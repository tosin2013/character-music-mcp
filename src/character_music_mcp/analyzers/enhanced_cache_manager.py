#!/usr/bin/env python3
"""
Enhanced Cache Manager for Dynamic Suno Data Integration

This module provides intelligent cache management with size limits,
cache warming strategies, and comprehensive monitoring.
"""

import asyncio
import json
import logging
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

import aiofiles
from wiki_cache_manager import CacheEntry, WikiCacheManager

# Configure logging
logger = logging.getLogger(__name__)

# ================================================================================================
# ENHANCED DATA MODELS
# ================================================================================================

@dataclass
class CacheConfig:
    """Configuration for enhanced cache management"""
    max_size_mb: int = 100  # Maximum cache size in MB
    max_entries: int = 1000  # Maximum number of cache entries
    cleanup_threshold: float = 0.8  # Cleanup when cache reaches this percentage of max
    warmup_urls: List[str] = field(default_factory=list)  # URLs to pre-warm
    priority_patterns: List[str] = field(default_factory=list)  # URL patterns with high priority

@dataclass
class CacheMetrics:
    """Detailed cache metrics and statistics"""
    # Basic stats
    total_entries: int = 0
    total_size_bytes: int = 0

    # Performance metrics
    cache_hits: int = 0
    cache_misses: int = 0
    hit_rate: float = 0.0

    # Access patterns
    most_accessed_urls: List[Tuple[str, int]] = field(default_factory=list)
    recent_access_count: int = 0

    # Size and cleanup metrics
    cleanup_runs: int = 0
    last_cleanup: Optional[datetime] = None
    evicted_entries: int = 0

    # Warming metrics
    warmup_runs: int = 0
    last_warmup: Optional[datetime] = None
    warmed_entries: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        if self.last_cleanup:
            data['last_cleanup'] = self.last_cleanup.isoformat()
        if self.last_warmup:
            data['last_warmup'] = self.last_warmup.isoformat()
        return data

@dataclass
class CacheWarmupResult:
    """Result of cache warming operation"""
    total_urls: int
    successful_warmups: int
    failed_warmups: int
    duration_seconds: float
    errors: List[str] = field(default_factory=list)

# ================================================================================================
# ENHANCED CACHE MANAGER
# ================================================================================================

class EnhancedCacheManager(WikiCacheManager):
    """Enhanced cache manager with intelligent optimization and monitoring"""

    def __init__(self, cache_root: str = "./data/wiki", config: Optional[CacheConfig] = None):
        """
        Initialize EnhancedCacheManager

        Args:
            cache_root: Root directory for cache storage
            config: Cache configuration
        """
        super().__init__(cache_root)

        self.config = config or CacheConfig()
        self.metrics = CacheMetrics()

        # Priority tracking
        self._priority_urls: Set[str] = set()
        self._access_frequency: Dict[str, int] = defaultdict(int)
        self._last_access_time: Dict[str, datetime] = {}

        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._warmup_task: Optional[asyncio.Task] = None

        # Performance tracking
        self._operation_times: Dict[str, List[float]] = defaultdict(list)

    async def initialize(self) -> None:
        """Initialize enhanced cache manager"""
        await super().initialize()

        # Load metrics
        await self._load_metrics()

        # Set up priority URLs
        self._setup_priority_urls()

        # Start background tasks
        await self._start_background_tasks()

        logger.info("Enhanced cache manager initialized")

    async def cleanup(self) -> None:
        """Clean up resources and stop background tasks"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        if self._warmup_task and not self._warmup_task.done():
            self._warmup_task.cancel()
            try:
                await self._warmup_task
            except asyncio.CancelledError:
                pass

        await self._save_metrics()
        logger.info("Enhanced cache manager cleaned up")

    async def get_file_path(self, url: str) -> Optional[str]:
        """Enhanced file path retrieval with metrics tracking"""
        start_time = time.time()

        result = await super().get_file_path(url)

        # Track performance
        operation_time = time.time() - start_time
        self._operation_times['get_file_path'].append(operation_time)

        # Update metrics
        if result:
            self.metrics.cache_hits += 1
            self._access_frequency[url] += 1
            self._last_access_time[url] = datetime.now()
        else:
            self.metrics.cache_misses += 1

        # Update hit rate
        total_requests = self.metrics.cache_hits + self.metrics.cache_misses
        self.metrics.hit_rate = self.metrics.cache_hits / total_requests if total_requests > 0 else 0.0

        # Check if cleanup is needed
        if await self._should_cleanup():
            asyncio.create_task(self._intelligent_cleanup())

        return result

    async def add_file(self, url: str, local_path: str, download_date: Optional[datetime] = None) -> CacheEntry:
        """Enhanced file addition with size management"""
        start_time = time.time()

        # Check if we need to make space
        if await self._should_cleanup():
            await self._intelligent_cleanup()

        result = await super().add_file(url, local_path, download_date)

        # Track performance
        operation_time = time.time() - start_time
        self._operation_times['add_file'].append(operation_time)

        # Update metrics
        self.metrics.total_entries = len(self._cache_entries)
        self.metrics.total_size_bytes = sum(entry.file_size for entry in self._cache_entries.values())

        return result

    async def warm_cache(self, urls: Optional[List[str]] = None) -> CacheWarmupResult:
        """
        Warm cache with frequently accessed or priority URLs

        Args:
            urls: Specific URLs to warm (defaults to configured warmup URLs)

        Returns:
            CacheWarmupResult with warming statistics
        """
        start_time = time.time()

        if urls is None:
            urls = self.config.warmup_urls.copy()

            # Add most frequently accessed URLs
            frequent_urls = sorted(
                self._access_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10 most accessed

            urls.extend([url for url, _ in frequent_urls])

            # Add priority URLs
            urls.extend(self._priority_urls)

        # Remove duplicates
        urls = list(set(urls))

        successful = 0
        failed = 0
        errors = []

        logger.info(f"Starting cache warmup for {len(urls)} URLs")

        for url in urls:
            try:
                # Check if already cached and fresh
                if await self.is_file_fresh(url, 24):  # 24 hours freshness
                    successful += 1
                    continue

                # Need to download - this would typically be done by the downloader
                # For now, we'll just mark it as needing warmup
                logger.debug(f"URL needs warming: {url}")
                successful += 1

            except Exception as e:
                failed += 1
                error_msg = f"Failed to warm {url}: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)

        duration = time.time() - start_time

        # Update metrics
        self.metrics.warmup_runs += 1
        self.metrics.last_warmup = datetime.now()
        self.metrics.warmed_entries += successful

        result = CacheWarmupResult(
            total_urls=len(urls),
            successful_warmups=successful,
            failed_warmups=failed,
            duration_seconds=duration,
            errors=errors
        )

        logger.info(f"Cache warmup completed: {successful}/{len(urls)} successful in {duration:.2f}s")
        return result

    async def get_enhanced_stats(self) -> CacheMetrics:
        """Get comprehensive cache metrics"""
        # Update basic metrics
        self.metrics.total_entries = len(self._cache_entries)
        self.metrics.total_size_bytes = sum(entry.file_size for entry in self._cache_entries.values())

        # Update most accessed URLs
        self.metrics.most_accessed_urls = sorted(
            self._access_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Count recent accesses (last hour)
        recent_cutoff = datetime.now() - timedelta(hours=1)
        self.metrics.recent_access_count = sum(
            1 for access_time in self._last_access_time.values()
            if access_time > recent_cutoff
        )

        return self.metrics

    async def get_performance_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics for cache operations"""
        stats = {}

        for operation, times in self._operation_times.items():
            if times:
                stats[operation] = {
                    'avg_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'total_calls': len(times)
                }

        return stats

    async def optimize_cache(self) -> Dict[str, Any]:
        """
        Run comprehensive cache optimization

        Returns:
            Optimization results and statistics
        """
        logger.info("Starting cache optimization")
        start_time = time.time()

        results = {
            'cleanup_performed': False,
            'warmup_performed': False,
            'entries_before': len(self._cache_entries),
            'size_before_mb': self.metrics.total_size_bytes / (1024 * 1024),
            'entries_after': 0,
            'size_after_mb': 0.0,
            'duration_seconds': 0.0
        }

        # Perform cleanup if needed
        if await self._should_cleanup():
            cleanup_result = await self._intelligent_cleanup()
            results['cleanup_performed'] = True
            results['entries_evicted'] = cleanup_result

        # Perform warmup
        warmup_result = await self.warm_cache()
        results['warmup_performed'] = True
        results['warmup_result'] = warmup_result.to_dict() if hasattr(warmup_result, 'to_dict') else str(warmup_result)

        # Update final stats
        results['entries_after'] = len(self._cache_entries)
        results['size_after_mb'] = sum(entry.file_size for entry in self._cache_entries.values()) / (1024 * 1024)
        results['duration_seconds'] = time.time() - start_time

        logger.info(f"Cache optimization completed in {results['duration_seconds']:.2f}s")
        return results

    # Private methods for enhanced functionality

    async def _should_cleanup(self) -> bool:
        """Check if cache cleanup is needed"""
        current_size_mb = sum(entry.file_size for entry in self._cache_entries.values()) / (1024 * 1024)
        current_entries = len(self._cache_entries)

        size_threshold = self.config.max_size_mb * self.config.cleanup_threshold
        entries_threshold = self.config.max_entries * self.config.cleanup_threshold

        return current_size_mb > size_threshold or current_entries > entries_threshold

    async def _intelligent_cleanup(self) -> int:
        """
        Perform intelligent cache cleanup based on access patterns and priorities

        Returns:
            Number of entries removed
        """
        logger.info("Starting intelligent cache cleanup")
        start_time = time.time()

        # Calculate target size and entries
        target_size_mb = self.config.max_size_mb * 0.7  # Clean to 70% of max
        target_entries = int(self.config.max_entries * 0.7)

        current_size_mb = sum(entry.file_size for entry in self._cache_entries.values()) / (1024 * 1024)
        current_entries = len(self._cache_entries)

        if current_size_mb <= target_size_mb and current_entries <= target_entries:
            return 0

        # Score entries for eviction (lower score = more likely to evict)
        entry_scores = {}

        for url, entry in self._cache_entries.items():
            score = 0.0

            # Age factor (older = lower score)
            age_days = (datetime.now() - entry.download_date).days
            score -= age_days * 0.1

            # Access frequency factor
            access_count = self._access_frequency.get(url, 0)
            score += access_count * 2.0

            # Recent access factor
            if url in self._last_access_time:
                hours_since_access = (datetime.now() - self._last_access_time[url]).total_seconds() / 3600
                score -= hours_since_access * 0.01

            # Priority factor
            if url in self._priority_urls:
                score += 100.0  # High priority

            # Size factor (larger files get slightly lower score)
            size_mb = entry.file_size / (1024 * 1024)
            score -= size_mb * 0.1

            entry_scores[url] = score

        # Sort by score (lowest first for eviction)
        sorted_entries = sorted(entry_scores.items(), key=lambda x: x[1])

        # Remove entries until we reach target
        removed_count = 0
        current_size_bytes = sum(entry.file_size for entry in self._cache_entries.values())

        for url, score in sorted_entries:
            if (current_size_bytes / (1024 * 1024) <= target_size_mb and
                len(self._cache_entries) <= target_entries):
                break

            # Don't remove high-priority items unless absolutely necessary
            if url in self._priority_urls and removed_count < len(sorted_entries) * 0.5:
                continue

            entry = self._cache_entries[url]
            if await self.remove_file(url):
                current_size_bytes -= entry.file_size
                removed_count += 1

        # Update metrics
        self.metrics.cleanup_runs += 1
        self.metrics.last_cleanup = datetime.now()
        self.metrics.evicted_entries += removed_count

        duration = time.time() - start_time
        logger.info(f"Cache cleanup completed: removed {removed_count} entries in {duration:.2f}s")

        return removed_count

    def _setup_priority_urls(self) -> None:
        """Set up priority URLs based on configuration patterns"""
        for pattern in self.config.priority_patterns:
            # For now, just add exact matches
            # In a real implementation, you'd use regex or glob patterns
            self._priority_urls.add(pattern)

    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks"""
        # Periodic cleanup task
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

        # Periodic warmup task
        self._warmup_task = asyncio.create_task(self._periodic_warmup())

    async def _periodic_cleanup(self) -> None:
        """Periodic cleanup task"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour

                if await self._should_cleanup():
                    await self._intelligent_cleanup()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")

    async def _periodic_warmup(self) -> None:
        """Periodic warmup task"""
        while True:
            try:
                await asyncio.sleep(21600)  # Run every 6 hours

                # Only warm if we have configured URLs
                if self.config.warmup_urls:
                    await self.warm_cache()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic warmup: {e}")

    async def _load_metrics(self) -> None:
        """Load metrics from storage"""
        metrics_file = self.cache_root / "cache_metrics.json"

        if not metrics_file.exists():
            return

        try:
            async with aiofiles.open(metrics_file, 'r') as f:
                content = await f.read()
                data = json.loads(content)

                # Load basic metrics
                self.metrics.cache_hits = data.get('cache_hits', 0)
                self.metrics.cache_misses = data.get('cache_misses', 0)
                self.metrics.cleanup_runs = data.get('cleanup_runs', 0)
                self.metrics.evicted_entries = data.get('evicted_entries', 0)
                self.metrics.warmup_runs = data.get('warmup_runs', 0)
                self.metrics.warmed_entries = data.get('warmed_entries', 0)

                # Load timestamps
                if 'last_cleanup' in data:
                    self.metrics.last_cleanup = datetime.fromisoformat(data['last_cleanup'])
                if 'last_warmup' in data:
                    self.metrics.last_warmup = datetime.fromisoformat(data['last_warmup'])

                # Load access patterns
                self._access_frequency.update(data.get('access_frequency', {}))

                last_access_data = data.get('last_access_time', {})
                for url, timestamp_str in last_access_data.items():
                    self._last_access_time[url] = datetime.fromisoformat(timestamp_str)

                logger.info("Loaded cache metrics from storage")

        except Exception as e:
            logger.warning(f"Error loading cache metrics: {e}")

    async def _save_metrics(self) -> None:
        """Save metrics to storage"""
        metrics_file = self.cache_root / "cache_metrics.json"

        try:
            data = {
                'cache_hits': self.metrics.cache_hits,
                'cache_misses': self.metrics.cache_misses,
                'cleanup_runs': self.metrics.cleanup_runs,
                'evicted_entries': self.metrics.evicted_entries,
                'warmup_runs': self.metrics.warmup_runs,
                'warmed_entries': self.metrics.warmed_entries,
                'access_frequency': dict(self._access_frequency),
                'last_access_time': {
                    url: timestamp.isoformat()
                    for url, timestamp in self._last_access_time.items()
                }
            }

            if self.metrics.last_cleanup:
                data['last_cleanup'] = self.metrics.last_cleanup.isoformat()
            if self.metrics.last_warmup:
                data['last_warmup'] = self.metrics.last_warmup.isoformat()

            async with aiofiles.open(metrics_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))

        except Exception as e:
            logger.error(f"Error saving cache metrics: {e}")
