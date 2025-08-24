#!/usr/bin/env python3
"""
Wiki Cache Manager for Dynamic Suno Data Integration

This module provides local file management and caching functionality
for wiki content with age checking and metadata tracking.
"""

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import aiofiles

# Configure logging
logger = logging.getLogger(__name__)

# ================================================================================================
# DATA MODELS
# ================================================================================================

@dataclass
class CacheEntry:
    """Represents a cached file with metadata"""
    url: str
    local_path: str
    download_date: datetime
    file_size: int
    content_hash: Optional[str] = None
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['download_date'] = self.download_date.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create CacheEntry from dictionary"""
        if 'download_date' in data and isinstance(data['download_date'], str):
            data['download_date'] = datetime.fromisoformat(data['download_date'])
        if 'last_accessed' in data and isinstance(data['last_accessed'], str):
            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)

@dataclass
class CacheStats:
    """Cache statistics and metrics"""
    total_entries: int
    total_size_bytes: int
    oldest_entry: Optional[datetime] = None
    newest_entry: Optional[datetime] = None
    cache_hit_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        if self.oldest_entry:
            data['oldest_entry'] = self.oldest_entry.isoformat()
        if self.newest_entry:
            data['newest_entry'] = self.newest_entry.isoformat()
        return data

# ================================================================================================
# WIKI CACHE MANAGER
# ================================================================================================

class WikiCacheManager:
    """Manages local file storage and caching for wiki content"""
    
    def __init__(self, cache_root: str = "./data/wiki"):
        """
        Initialize WikiCacheManager
        
        Args:
            cache_root: Root directory for cache storage
        """
        self.cache_root = Path(cache_root)
        self.cache_index_file = self.cache_root / "cache_index.json"
        
        # Cache data
        self._cache_entries: Dict[str, CacheEntry] = {}
        self._cache_loaded = False
        
        # Statistics
        self._cache_hits = 0
        self._cache_misses = 0
    
    async def initialize(self) -> None:
        """Initialize cache manager and load existing cache index"""
        logger.info(f"Initializing WikiCacheManager with root: {self.cache_root}")
        
        # Create directory structure
        await self._setup_directory_structure()
        
        # Load existing cache index
        await self._load_cache_index()
        
        # Validate cache entries
        await self._validate_cache_entries()
        
        self._cache_loaded = True
        logger.info(f"Cache initialized with {len(self._cache_entries)} entries")
    
    async def get_file_path(self, url: str) -> Optional[str]:
        """
        Get local file path for a URL if it exists and is valid
        
        Args:
            url: URL to look up
            
        Returns:
            Local file path if exists, None otherwise
        """
        if not self._cache_loaded:
            await self.initialize()
        
        if url in self._cache_entries:
            entry = self._cache_entries[url]
            
            # Check if file still exists
            if Path(entry.local_path).exists():
                # Update access statistics
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                self._cache_hits += 1
                
                # Save updated index
                await self._save_cache_index()
                
                return entry.local_path
            else:
                # File was deleted, remove from cache
                logger.warning(f"Cached file missing, removing entry: {entry.local_path}")
                del self._cache_entries[url]
                await self._save_cache_index()
        
        self._cache_misses += 1
        return None
    
    async def add_file(self, url: str, local_path: str, download_date: Optional[datetime] = None) -> CacheEntry:
        """
        Add a file to the cache index
        
        Args:
            url: Source URL
            local_path: Local file path
            download_date: When file was downloaded (defaults to now)
            
        Returns:
            CacheEntry for the added file
        """
        if not self._cache_loaded:
            await self.initialize()
        
        if download_date is None:
            download_date = datetime.now()
        
        # Get file size
        file_path = Path(local_path)
        file_size = file_path.stat().st_size if file_path.exists() else 0
        
        # Create cache entry
        entry = CacheEntry(
            url=url,
            local_path=local_path,
            download_date=download_date,
            file_size=file_size
        )
        
        # Add to cache
        self._cache_entries[url] = entry
        
        # Save index
        await self._save_cache_index()
        
        logger.info(f"Added file to cache: {url} -> {local_path}")
        return entry
    
    async def is_file_fresh(self, url: str, max_age_hours: int) -> bool:
        """
        Check if a cached file is still fresh (within max age)
        
        Args:
            url: URL to check
            max_age_hours: Maximum age in hours
            
        Returns:
            True if file is fresh, False otherwise
        """
        if not self._cache_loaded:
            await self.initialize()
        
        if url not in self._cache_entries:
            return False
        
        entry = self._cache_entries[url]
        
        # Check if file exists
        if not Path(entry.local_path).exists():
            return False
        
        # Check age
        max_age = timedelta(hours=max_age_hours)
        age = datetime.now() - entry.download_date
        
        return age <= max_age
    
    async def get_file_age(self, url: str) -> Optional[timedelta]:
        """
        Get age of a cached file
        
        Args:
            url: URL to check
            
        Returns:
            Age as timedelta, or None if not cached
        """
        if not self._cache_loaded:
            await self.initialize()
        
        if url not in self._cache_entries:
            return None
        
        entry = self._cache_entries[url]
        return datetime.now() - entry.download_date
    
    async def remove_file(self, url: str) -> bool:
        """
        Remove a file from cache (both index and file)
        
        Args:
            url: URL to remove
            
        Returns:
            True if removed, False if not found
        """
        if not self._cache_loaded:
            await self.initialize()
        
        if url not in self._cache_entries:
            return False
        
        entry = self._cache_entries[url]
        
        # Remove physical file
        try:
            file_path = Path(entry.local_path)
            if file_path.exists():
                file_path.unlink()
            
            # Remove metadata file if exists
            metadata_path = file_path.with_suffix('.meta.json')
            if metadata_path.exists():
                metadata_path.unlink()
                
        except Exception as e:
            logger.warning(f"Error removing file {entry.local_path}: {e}")
        
        # Remove from index
        del self._cache_entries[url]
        await self._save_cache_index()
        
        logger.info(f"Removed file from cache: {url}")
        return True
    
    async def cleanup_old_files(self, max_age_hours: int) -> int:
        """
        Remove files older than specified age
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of files removed
        """
        if not self._cache_loaded:
            await self.initialize()
        
        max_age = timedelta(hours=max_age_hours)
        current_time = datetime.now()
        
        urls_to_remove = []
        for url, entry in self._cache_entries.items():
            age = current_time - entry.download_date
            if age > max_age:
                urls_to_remove.append(url)
        
        # Remove old files
        removed_count = 0
        for url in urls_to_remove:
            if await self.remove_file(url):
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old cache files")
        
        return removed_count
    
    async def get_cache_stats(self) -> CacheStats:
        """
        Get cache statistics
        
        Returns:
            CacheStats with current metrics
        """
        if not self._cache_loaded:
            await self.initialize()
        
        total_entries = len(self._cache_entries)
        total_size = sum(entry.file_size for entry in self._cache_entries.values())
        
        oldest_entry = None
        newest_entry = None
        
        if self._cache_entries:
            dates = [entry.download_date for entry in self._cache_entries.values()]
            oldest_entry = min(dates)
            newest_entry = max(dates)
        
        # Calculate hit rate
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total_requests if total_requests > 0 else 0.0
        
        return CacheStats(
            total_entries=total_entries,
            total_size_bytes=total_size,
            oldest_entry=oldest_entry,
            newest_entry=newest_entry,
            cache_hit_rate=hit_rate
        )
    
    async def list_cached_urls(self) -> List[str]:
        """
        Get list of all cached URLs
        
        Returns:
            List of cached URLs
        """
        if not self._cache_loaded:
            await self.initialize()
        
        return list(self._cache_entries.keys())
    
    async def get_cache_entry(self, url: str) -> Optional[CacheEntry]:
        """
        Get cache entry for a URL
        
        Args:
            url: URL to look up
            
        Returns:
            CacheEntry if found, None otherwise
        """
        if not self._cache_loaded:
            await self.initialize()
        
        return self._cache_entries.get(url)
    
    def get_organized_path(self, url: str, content_type: str = "general") -> str:
        """
        Generate organized local path for a URL
        
        Args:
            url: Source URL
            content_type: Type of content (genres, meta_tags, techniques)
            
        Returns:
            Organized local file path
        """
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        
        # Extract filename from URL
        path_parts = parsed.path.strip('/').split('/')
        filename = path_parts[-1] if path_parts else 'index'
        
        # Ensure .html extension
        if not filename.endswith('.html'):
            filename += '.html'
        
        # Determine subdirectory based on content type or URL pattern
        if content_type == "genres" or '/resources/' in url and 'genres' in url:
            subdir = "genres"
        elif content_type == "meta_tags" or '/resources/' in url and 'metatags' in url:
            subdir = "meta_tags"
        elif content_type == "techniques" or '/tips/' in url:
            subdir = "techniques"
        else:
            subdir = "general"
        
        return str(self.cache_root / subdir / filename)
    
    # Private methods
    
    async def _setup_directory_structure(self) -> None:
        """Set up cache directory structure"""
        directories = [
            self.cache_root,
            self.cache_root / "genres",
            self.cache_root / "meta_tags",
            self.cache_root / "techniques",
            self.cache_root / "general"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def _load_cache_index(self) -> None:
        """Load cache index from file"""
        if not self.cache_index_file.exists():
            logger.info("No existing cache index found, starting fresh")
            return
        
        try:
            async with aiofiles.open(self.cache_index_file, 'r') as f:
                content = await f.read()
                data = json.loads(content)
                
                # Load cache entries
                for url, entry_data in data.get('entries', {}).items():
                    try:
                        entry = CacheEntry.from_dict(entry_data)
                        self._cache_entries[url] = entry
                    except Exception as e:
                        logger.warning(f"Error loading cache entry for {url}: {e}")
                
                # Load statistics
                stats = data.get('stats', {})
                self._cache_hits = stats.get('cache_hits', 0)
                self._cache_misses = stats.get('cache_misses', 0)
                
                logger.info(f"Loaded cache index with {len(self._cache_entries)} entries")
                
        except Exception as e:
            logger.error(f"Error loading cache index: {e}")
            self._cache_entries = {}
    
    async def _save_cache_index(self) -> None:
        """Save cache index to file"""
        try:
            # Prepare data
            data = {
                'entries': {url: entry.to_dict() for url, entry in self._cache_entries.items()},
                'stats': {
                    'cache_hits': self._cache_hits,
                    'cache_misses': self._cache_misses,
                    'last_updated': datetime.now().isoformat()
                }
            }
            
            # Save to file
            async with aiofiles.open(self.cache_index_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
                
        except Exception as e:
            logger.error(f"Error saving cache index: {e}")
    
    async def _validate_cache_entries(self) -> None:
        """Validate existing cache entries and remove invalid ones"""
        invalid_urls = []
        
        for url, entry in self._cache_entries.items():
            file_path = Path(entry.local_path)
            
            # Check if file exists
            if not file_path.exists():
                logger.warning(f"Cache entry file missing: {entry.local_path}")
                invalid_urls.append(url)
                continue
            
            # Update file size if different
            actual_size = file_path.stat().st_size
            if actual_size != entry.file_size:
                logger.info(f"Updating file size for {url}: {entry.file_size} -> {actual_size}")
                entry.file_size = actual_size
        
        # Remove invalid entries
        for url in invalid_urls:
            del self._cache_entries[url]
        
        if invalid_urls:
            logger.info(f"Removed {len(invalid_urls)} invalid cache entries")
            await self._save_cache_index()