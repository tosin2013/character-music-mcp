#!/usr/bin/env python3
"""
Error Recovery Manager for Dynamic Suno Data Integration

This module provides comprehensive error handling and fallback systems for the wiki
data integration system, implementing graceful degradation mechanisms and recovery strategies.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# ================================================================================================
# ENUMS AND DATA MODELS
# ================================================================================================

class ErrorType(Enum):
    """Types of errors that can occur in the system"""
    NETWORK_ERROR = "network_error"
    PARSE_ERROR = "parse_error"
    FILE_ERROR = "file_error"
    DATA_ERROR = "data_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN_ERROR = "unknown_error"

class RecoveryAction(Enum):
    """Types of recovery actions"""
    USE_CACHED_DATA = "use_cached_data"
    USE_FALLBACK_DATA = "use_fallback_data"
    RETRY_OPERATION = "retry_operation"
    SKIP_OPERATION = "skip_operation"
    PARTIAL_RECOVERY = "partial_recovery"
    FAIL_GRACEFULLY = "fail_gracefully"

class DataSource(Enum):
    """Types of data sources"""
    WIKI_FRESH = "wiki_fresh"
    WIKI_CACHED = "wiki_cached"
    HARDCODED_FALLBACK = "hardcoded_fallback"
    MIXED_SOURCES = "mixed_sources"

@dataclass
class ErrorRecord:
    """Record of an error occurrence"""
    error_type: ErrorType
    error_message: str
    operation: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_action: Optional[RecoveryAction] = None
    recovery_successful: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'error_type': self.error_type.value,
            'error_message': self.error_message,
            'operation': self.operation,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context,
            'recovery_action': self.recovery_action.value if self.recovery_action else None,
            'recovery_successful': self.recovery_successful
        }

@dataclass
class FallbackData:
    """Container for fallback data with metadata"""
    data: Any
    source: DataSource
    quality_score: float  # 0.0 to 1.0, where 1.0 is highest quality
    last_updated: datetime
    description: str = ""

    def is_stale(self, max_age_hours: int = 24) -> bool:
        """Check if fallback data is stale"""
        age = datetime.now() - self.last_updated
        return age > timedelta(hours=max_age_hours)

@dataclass
class RecoveryResult:
    """Result of a recovery operation"""
    success: bool
    data: Any = None
    source: DataSource = DataSource.HARDCODED_FALLBACK
    quality_score: float = 0.0
    error_message: Optional[str] = None
    recovery_action: Optional[RecoveryAction] = None
    partial_data: bool = False

# ================================================================================================
# ERROR RECOVERY MANAGER
# ================================================================================================

class ErrorRecoveryManager:
    """Manages error recovery and fallback systems for wiki data integration"""

    def __init__(self, storage_path: str = "./data/error_recovery"):
        self.storage_path = Path(storage_path)
        self.error_history: List[ErrorRecord] = []
        self.fallback_data_cache: Dict[str, FallbackData] = {}
        self.retry_policies: Dict[str, Dict[str, Any]] = {}
        self.initialized = False

        # Default retry policies
        self._setup_default_retry_policies()

        # Hardcoded fallback data
        self._setup_hardcoded_fallbacks()

    async def initialize(self) -> None:
        """Initialize the error recovery manager"""
        logger.info("Initializing ErrorRecoveryManager")

        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Load error history
        await self._load_error_history()

        self.initialized = True
        logger.info("ErrorRecoveryManager initialized successfully")

    async def handle_download_failure(self, url: str, error: Exception,
                                    operation_context: Dict[str, Any] = None) -> RecoveryResult:
        """
        Handle download failure with appropriate recovery strategy

        Args:
            url: URL that failed to download
            error: Exception that occurred
            operation_context: Additional context about the operation

        Returns:
            RecoveryResult with recovery data or fallback
        """
        logger.warning(f"Handling download failure for {url}: {error}")

        # Record the error
        error_record = ErrorRecord(
            error_type=self._classify_error(error),
            error_message=str(error),
            operation=f"download:{url}",
            context=operation_context or {}
        )

        # Determine recovery strategy
        recovery_action = await self._determine_recovery_action(url, error, "download")
        error_record.recovery_action = recovery_action

        # Execute recovery
        recovery_result = await self._execute_recovery(recovery_action, url, error, operation_context)
        error_record.recovery_successful = recovery_result.success

        # Store error record
        self.error_history.append(error_record)

        return recovery_result

    async def handle_parse_failure(self, content: str, error: Exception,
                                 content_type: str = "unknown",
                                 source_url: str = "") -> RecoveryResult:
        """
        Handle content parsing failure with fallback strategies

        Args:
            content: Content that failed to parse
            error: Exception that occurred
            content_type: Type of content being parsed
            source_url: Source URL of the content

        Returns:
            RecoveryResult with recovery data or fallback
        """
        logger.warning(f"Handling parse failure for {content_type} from {source_url}: {error}")

        # Record the error
        error_record = ErrorRecord(
            error_type=ErrorType.PARSE_ERROR,
            error_message=str(error),
            operation=f"parse:{content_type}",
            context={'source_url': source_url, 'content_length': len(content)}
        )

        # Determine recovery strategy
        recovery_action = await self._determine_recovery_action(source_url, error, "parse", content_type)
        error_record.recovery_action = recovery_action

        # Execute recovery
        recovery_result = await self._execute_recovery(recovery_action, source_url, error,
                                                     {'content_type': content_type, 'content': content})
        error_record.recovery_successful = recovery_result.success

        # Store error record
        self.error_history.append(error_record)

        return recovery_result

    def get_fallback_data(self, data_type: str, quality_threshold: float = 0.3) -> Optional[FallbackData]:
        """
        Get fallback data for a specific data type

        Args:
            data_type: Type of data needed ('genres', 'meta_tags', 'techniques')
            quality_threshold: Minimum quality score required

        Returns:
            FallbackData if available and meets quality threshold
        """
        if data_type in self.fallback_data_cache:
            fallback = self.fallback_data_cache[data_type]
            if fallback.quality_score >= quality_threshold:
                logger.info(f"Using fallback data for {data_type} (quality: {fallback.quality_score:.2f})")
                return fallback

        # Try to get hardcoded fallback
        hardcoded_fallback = self._get_hardcoded_fallback(data_type)
        if hardcoded_fallback:
            return hardcoded_fallback

        logger.warning(f"No suitable fallback data found for {data_type}")
        return None

    async def schedule_retry(self, operation: str, delay_minutes: int = 5,
                           max_retries: int = 3) -> None:
        """
        Schedule a retry operation for later execution

        Args:
            operation: Operation identifier
            delay_minutes: Delay before retry in minutes
            max_retries: Maximum number of retry attempts
        """
        logger.info(f"Scheduling retry for {operation} in {delay_minutes} minutes")

        # This would typically integrate with a task scheduler
        # For now, we'll use asyncio.sleep for demonstration
        await asyncio.sleep(delay_minutes * 60)

        # In a real implementation, this would trigger the retry
        logger.info(f"Retry scheduled for {operation} would execute now")

    def create_mixed_source_data(self, wiki_data: List[Any], fallback_data: List[Any],
                                data_type: str) -> FallbackData:
        """
        Create mixed source data combining wiki and fallback data

        Args:
            wiki_data: Data from wiki sources
            fallback_data: Fallback data
            data_type: Type of data being mixed

        Returns:
            FallbackData with mixed sources
        """
        # Combine data, preferring wiki data
        combined_data = []
        wiki_items = {self._get_item_key(item): item for item in wiki_data}
        fallback_items = {self._get_item_key(item): item for item in fallback_data}

        # Add all wiki items
        combined_data.extend(wiki_data)

        # Add fallback items that aren't in wiki data
        for key, item in fallback_items.items():
            if key not in wiki_items:
                combined_data.append(item)

        # Calculate quality score based on wiki vs fallback ratio
        wiki_ratio = len(wiki_data) / len(combined_data) if combined_data else 0
        quality_score = 0.5 + (wiki_ratio * 0.4)  # 0.5-0.9 range

        mixed_data = FallbackData(
            data=combined_data,
            source=DataSource.MIXED_SOURCES,
            quality_score=quality_score,
            last_updated=datetime.now(),
            description=f"Mixed {data_type} data: {len(wiki_data)} wiki + {len(fallback_data)} fallback items"
        )

        # Cache the mixed data
        self.fallback_data_cache[data_type] = mixed_data

        logger.info(f"Created mixed source data for {data_type}: {len(combined_data)} total items")
        return mixed_data

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics and recovery success rates"""
        if not self.error_history:
            return {'total_errors': 0}

        stats = {
            'total_errors': len(self.error_history),
            'errors_by_type': {},
            'recovery_success_rate': 0.0,
            'most_common_errors': [],
            'recent_errors': []
        }

        # Count errors by type
        for error in self.error_history:
            error_type = error.error_type.value
            if error_type not in stats['errors_by_type']:
                stats['errors_by_type'][error_type] = 0
            stats['errors_by_type'][error_type] += 1

        # Calculate recovery success rate
        successful_recoveries = sum(1 for error in self.error_history if error.recovery_successful)
        stats['recovery_success_rate'] = successful_recoveries / len(self.error_history)

        # Most common error messages
        error_messages = {}
        for error in self.error_history:
            msg = error.error_message[:100]  # Truncate long messages
            if msg not in error_messages:
                error_messages[msg] = 0
            error_messages[msg] += 1

        stats['most_common_errors'] = sorted(error_messages.items(),
                                           key=lambda x: x[1], reverse=True)[:10]

        # Recent errors
        recent_errors = sorted(self.error_history, key=lambda x: x.timestamp, reverse=True)[:10]
        stats['recent_errors'] = [
            {
                'timestamp': error.timestamp.isoformat(),
                'type': error.error_type.value,
                'operation': error.operation,
                'message': error.error_message[:200],
                'recovery_successful': error.recovery_successful
            }
            for error in recent_errors
        ]

        return stats

    # Private methods

    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify an error into appropriate error type"""
        error_str = str(error).lower()
        type(error).__name__.lower()

        if any(keyword in error_str for keyword in ['network', 'connection', 'timeout', 'dns']):
            return ErrorType.NETWORK_ERROR
        elif any(keyword in error_str for keyword in ['parse', 'html', 'xml', 'json']):
            return ErrorType.PARSE_ERROR
        elif any(keyword in error_str for keyword in ['file', 'directory', 'permission', 'disk']):
            return ErrorType.FILE_ERROR
        elif any(keyword in error_str for keyword in ['data', 'format', 'validation']):
            return ErrorType.DATA_ERROR
        elif any(keyword in error_str for keyword in ['config', 'setting', 'parameter']):
            return ErrorType.CONFIGURATION_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR

    async def _determine_recovery_action(self, resource_id: str, error: Exception,
                                       operation_type: str, content_type: str = None) -> RecoveryAction:
        """Determine the best recovery action for an error"""
        error_type = self._classify_error(error)

        # Check retry policy
        retry_key = f"{operation_type}:{error_type.value}"
        if retry_key in self.retry_policies:
            policy = self.retry_policies[retry_key]
            if policy['current_attempts'] < policy['max_attempts']:
                return RecoveryAction.RETRY_OPERATION

        # Network errors - try cached data first
        if error_type == ErrorType.NETWORK_ERROR:
            if await self._has_cached_data(resource_id):
                return RecoveryAction.USE_CACHED_DATA
            else:
                return RecoveryAction.USE_FALLBACK_DATA

        # Parse errors - try fallback data
        elif error_type == ErrorType.PARSE_ERROR:
            return RecoveryAction.USE_FALLBACK_DATA

        # File errors - try to recover or use fallback
        elif error_type == ErrorType.FILE_ERROR:
            return RecoveryAction.USE_FALLBACK_DATA

        # Data errors - try partial recovery
        elif error_type == ErrorType.DATA_ERROR:
            return RecoveryAction.PARTIAL_RECOVERY

        # Configuration errors - fail gracefully
        elif error_type == ErrorType.CONFIGURATION_ERROR:
            return RecoveryAction.FAIL_GRACEFULLY

        # Unknown errors - try fallback
        else:
            return RecoveryAction.USE_FALLBACK_DATA

    async def _execute_recovery(self, action: RecoveryAction, resource_id: str,
                              error: Exception, context: Dict[str, Any] = None) -> RecoveryResult:
        """Execute the determined recovery action"""
        context = context or {}

        try:
            if action == RecoveryAction.USE_CACHED_DATA:
                return await self._recover_with_cached_data(resource_id, context)

            elif action == RecoveryAction.USE_FALLBACK_DATA:
                return await self._recover_with_fallback_data(resource_id, context)

            elif action == RecoveryAction.RETRY_OPERATION:
                return await self._retry_operation(resource_id, context)

            elif action == RecoveryAction.PARTIAL_RECOVERY:
                return await self._attempt_partial_recovery(resource_id, context)

            elif action == RecoveryAction.SKIP_OPERATION:
                return RecoveryResult(
                    success=True,
                    data=None,
                    source=DataSource.HARDCODED_FALLBACK,
                    recovery_action=action
                )

            elif action == RecoveryAction.FAIL_GRACEFULLY:
                return RecoveryResult(
                    success=False,
                    error_message=f"Graceful failure: {str(error)}",
                    recovery_action=action
                )

            else:
                return RecoveryResult(
                    success=False,
                    error_message=f"Unknown recovery action: {action}",
                    recovery_action=action
                )

        except Exception as recovery_error:
            logger.error(f"Recovery action {action} failed: {recovery_error}")
            return RecoveryResult(
                success=False,
                error_message=f"Recovery failed: {str(recovery_error)}",
                recovery_action=action
            )

    async def _recover_with_cached_data(self, resource_id: str,
                                      context: Dict[str, Any]) -> RecoveryResult:
        """Recover using cached data"""
        # This would integrate with the cache manager
        # For now, simulate cached data recovery

        cached_data = await self._get_cached_data(resource_id)
        if cached_data:
            return RecoveryResult(
                success=True,
                data=cached_data,
                source=DataSource.WIKI_CACHED,
                quality_score=0.8,  # Cached data is high quality but not fresh
                recovery_action=RecoveryAction.USE_CACHED_DATA
            )
        else:
            # No cached data available, fall back to hardcoded
            return await self._recover_with_fallback_data(resource_id, context)

    async def _recover_with_fallback_data(self, resource_id: str,
                                        context: Dict[str, Any]) -> RecoveryResult:
        """Recover using fallback data"""
        content_type = context.get('content_type', 'unknown')

        # Map resource_id to data type
        if 'genre' in resource_id.lower() or content_type == 'genres':
            data_type = 'genres'
        elif 'meta' in resource_id.lower() or content_type == 'meta_tags':
            data_type = 'meta_tags'
        elif 'tip' in resource_id.lower() or content_type == 'techniques':
            data_type = 'techniques'
        else:
            data_type = 'general'

        fallback_data = self.get_fallback_data(data_type)
        if fallback_data:
            return RecoveryResult(
                success=True,
                data=fallback_data.data,
                source=fallback_data.source,
                quality_score=fallback_data.quality_score,
                recovery_action=RecoveryAction.USE_FALLBACK_DATA
            )
        else:
            return RecoveryResult(
                success=False,
                error_message=f"No fallback data available for {data_type}",
                recovery_action=RecoveryAction.USE_FALLBACK_DATA
            )

    async def _retry_operation(self, resource_id: str,
                             context: Dict[str, Any]) -> RecoveryResult:
        """Retry the failed operation"""
        # This would typically re-execute the original operation
        # For now, we'll simulate a retry

        logger.info(f"Retrying operation for {resource_id}")

        # Simulate retry delay
        await asyncio.sleep(1)

        # For demonstration, assume retry succeeds 50% of the time
        import random
        if random.random() > 0.5:
            return RecoveryResult(
                success=True,
                data=f"Retry successful for {resource_id}",
                source=DataSource.WIKI_FRESH,
                quality_score=1.0,
                recovery_action=RecoveryAction.RETRY_OPERATION
            )
        else:
            # Retry failed, fall back to cached/fallback data
            return await self._recover_with_fallback_data(resource_id, context)

    async def _attempt_partial_recovery(self, resource_id: str,
                                      context: Dict[str, Any]) -> RecoveryResult:
        """Attempt to recover partial data"""
        content = context.get('content', '')
        content_type = context.get('content_type', 'unknown')

        # Try to extract whatever data we can from the content
        partial_data = []

        if content and len(content) > 100:  # Only try if we have substantial content
            # Simple partial recovery - extract text that looks like data
            import re

            if content_type == 'genres':
                # Look for genre-like patterns
                genre_patterns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
                partial_data = [{'name': pattern, 'description': 'Partially recovered genre'}
                               for pattern in genre_patterns[:10]]

            elif content_type == 'meta_tags':
                # Look for meta tag patterns
                tag_patterns = re.findall(r'\[([^\]]+)\]', content)
                partial_data = [{'tag': tag, 'description': 'Partially recovered meta tag'}
                               for tag in tag_patterns[:20]]

        if partial_data:
            return RecoveryResult(
                success=True,
                data=partial_data,
                source=DataSource.MIXED_SOURCES,
                quality_score=0.3,  # Low quality due to partial recovery
                recovery_action=RecoveryAction.PARTIAL_RECOVERY,
                partial_data=True
            )
        else:
            # Partial recovery failed, use fallback
            return await self._recover_with_fallback_data(resource_id, context)

    async def _has_cached_data(self, resource_id: str) -> bool:
        """Check if cached data is available for a resource"""
        # This would integrate with the cache manager
        # For now, simulate cache availability
        return resource_id in ['genres', 'meta_tags', 'techniques']

    async def _get_cached_data(self, resource_id: str) -> Optional[Any]:
        """Get cached data for a resource"""
        # This would integrate with the cache manager
        # For now, return simulated cached data
        if resource_id == 'genres':
            return [{'name': 'Rock', 'description': 'Cached rock genre'}]
        elif resource_id == 'meta_tags':
            return [{'tag': '[rock]', 'description': 'Cached rock meta tag'}]
        elif resource_id == 'techniques':
            return [{'name': 'Basic Structure', 'description': 'Cached technique'}]
        return None

    def _get_item_key(self, item: Any) -> str:
        """Get a unique key for an item for deduplication"""
        if hasattr(item, 'name'):
            return item.name.lower()
        elif hasattr(item, 'tag'):
            return item.tag.lower()
        elif isinstance(item, dict):
            return item.get('name', item.get('tag', str(item))).lower()
        else:
            return str(item).lower()

    def _setup_default_retry_policies(self) -> None:
        """Setup default retry policies for different operations"""
        self.retry_policies = {
            'download:network_error': {
                'max_attempts': 3,
                'current_attempts': 0,
                'delay_seconds': [1, 5, 15],  # Exponential backoff
                'reset_after_hours': 1
            },
            'download:unknown_error': {
                'max_attempts': 2,
                'current_attempts': 0,
                'delay_seconds': [2, 10],
                'reset_after_hours': 2
            },
            'parse:parse_error': {
                'max_attempts': 1,  # Don't retry parse errors
                'current_attempts': 0,
                'delay_seconds': [0],
                'reset_after_hours': 24
            }
        }

    def _setup_hardcoded_fallbacks(self) -> None:
        """Setup hardcoded fallback data"""
        # Basic genre fallbacks
        hardcoded_genres = [
            {'name': 'Rock', 'description': 'Rock music genre', 'characteristics': ['guitar-driven', 'strong rhythm']},
            {'name': 'Pop', 'description': 'Popular music genre', 'characteristics': ['catchy', 'mainstream']},
            {'name': 'Jazz', 'description': 'Jazz music genre', 'characteristics': ['improvisation', 'complex harmonies']},
            {'name': 'Electronic', 'description': 'Electronic music genre', 'characteristics': ['synthesized', 'digital']},
            {'name': 'Folk', 'description': 'Folk music genre', 'characteristics': ['acoustic', 'traditional']},
            {'name': 'Hip Hop', 'description': 'Hip hop music genre', 'characteristics': ['rhythmic speech', 'beats']},
            {'name': 'Blues', 'description': 'Blues music genre', 'characteristics': ['twelve-bar', 'emotional']},
            {'name': 'Country', 'description': 'Country music genre', 'characteristics': ['storytelling', 'rural themes']}
        ]

        self.fallback_data_cache['genres'] = FallbackData(
            data=hardcoded_genres,
            source=DataSource.HARDCODED_FALLBACK,
            quality_score=0.6,
            last_updated=datetime.now(),
            description="Hardcoded genre fallback data"
        )

        # Basic meta tag fallbacks
        hardcoded_meta_tags = [
            {'tag': '[rock]', 'category': 'genre', 'description': 'Rock genre meta tag'},
            {'tag': '[pop]', 'category': 'genre', 'description': 'Pop genre meta tag'},
            {'tag': '[upbeat]', 'category': 'mood', 'description': 'Upbeat mood meta tag'},
            {'tag': '[melancholic]', 'category': 'mood', 'description': 'Melancholic mood meta tag'},
            {'tag': '[guitar]', 'category': 'instrument', 'description': 'Guitar instrument meta tag'},
            {'tag': '[piano]', 'category': 'instrument', 'description': 'Piano instrument meta tag'},
            {'tag': '[verse]', 'category': 'structure', 'description': 'Verse structure meta tag'},
            {'tag': '[chorus]', 'category': 'structure', 'description': 'Chorus structure meta tag'}
        ]

        self.fallback_data_cache['meta_tags'] = FallbackData(
            data=hardcoded_meta_tags,
            source=DataSource.HARDCODED_FALLBACK,
            quality_score=0.6,
            last_updated=datetime.now(),
            description="Hardcoded meta tag fallback data"
        )

        # Basic technique fallbacks
        hardcoded_techniques = [
            {'name': 'Basic Song Structure', 'description': 'Use verse-chorus-verse-chorus-bridge-chorus structure'},
            {'name': 'Genre Specification', 'description': 'Specify genre in meta tags for better results'},
            {'name': 'Mood Setting', 'description': 'Use mood-related meta tags to set the emotional tone'},
            {'name': 'Instrument Focus', 'description': 'Specify key instruments in meta tags'}
        ]

        self.fallback_data_cache['techniques'] = FallbackData(
            data=hardcoded_techniques,
            source=DataSource.HARDCODED_FALLBACK,
            quality_score=0.5,
            last_updated=datetime.now(),
            description="Hardcoded technique fallback data"
        )

    def _get_hardcoded_fallback(self, data_type: str) -> Optional[FallbackData]:
        """Get hardcoded fallback data for a specific type"""
        return self.fallback_data_cache.get(data_type)

    async def _load_error_history(self) -> None:
        """Load error history from disk"""
        error_file = self.storage_path / "error_history.json"
        if error_file.exists():
            try:
                with open(error_file, 'r') as f:
                    error_data = json.load(f)

                for record_data in error_data:
                    error_record = ErrorRecord(
                        error_type=ErrorType(record_data['error_type']),
                        error_message=record_data['error_message'],
                        operation=record_data['operation'],
                        timestamp=datetime.fromisoformat(record_data['timestamp']),
                        context=record_data.get('context', {}),
                        recovery_action=RecoveryAction(record_data['recovery_action']) if record_data.get('recovery_action') else None,
                        recovery_successful=record_data.get('recovery_successful', False)
                    )
                    self.error_history.append(error_record)

                logger.debug(f"Loaded {len(self.error_history)} error records from disk")
            except Exception as e:
                logger.warning(f"Failed to load error history: {e}")

    async def save_state(self) -> None:
        """Save current state to disk"""
        if not self.initialized:
            return

        # Save error history
        error_file = self.storage_path / "error_history.json"
        error_data = [record.to_dict() for record in self.error_history[-1000:]]  # Keep last 1000 records
        with open(error_file, 'w') as f:
            json.dump(error_data, f, indent=2)

        logger.debug("Saved error recovery state to disk")
