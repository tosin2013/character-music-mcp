#!/usr/bin/env python3
"""
Wiki Downloader for Dynamic Suno Data Integration

This module provides the WikiDownloader class for downloading and managing
wiki content with error handling, URL validation, and download tracking.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from urllib.parse import urlparse, urljoin
import aiohttp
import aiofiles

from wiki_cache_manager import WikiCacheManager
from performance_monitor import PerformanceMonitor

# Configure logging
logger = logging.getLogger(__name__)

# ================================================================================================
# DATA MODELS
# ================================================================================================

@dataclass
class DownloadResult:
    """Result of a download operation with metadata"""
    url: str
    success: bool
    local_path: Optional[str] = None
    status_code: Optional[int] = None
    content_length: Optional[int] = None
    download_time: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['download_time'] = self.download_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DownloadResult':
        """Create DownloadResult from dictionary"""
        if 'download_time' in data and isinstance(data['download_time'], str):
            data['download_time'] = datetime.fromisoformat(data['download_time'])
        return cls(**data)

@dataclass
class BatchDownloadResult:
    """Result of a batch download operation"""
    total_urls: int
    successful_downloads: int
    failed_downloads: int
    skipped_downloads: int
    results: List[DownloadResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration: Optional[timedelta] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        if self.total_duration:
            data['total_duration'] = self.total_duration.total_seconds()
        data['results'] = [result.to_dict() for result in self.results]
        return data

@dataclass
class DownloadProgress:
    """Progress information for batch downloads"""
    total_urls: int
    completed: int
    successful: int
    failed: int
    skipped: int
    current_url: Optional[str] = None
    
    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage"""
        if self.total_urls == 0:
            return 100.0
        return (self.completed / self.total_urls) * 100.0

# ================================================================================================
# WIKI DOWNLOADER
# ================================================================================================

class WikiDownloader:
    """Downloads and manages wiki page content with error handling and caching"""
    
    def __init__(self, 
                 cache_manager: Optional[WikiCacheManager] = None,
                 performance_monitor: Optional[PerformanceMonitor] = None,
                 request_timeout: int = 30,
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 user_agent: str = "WikiDownloader/1.0"):
        """
        Initialize WikiDownloader
        
        Args:
            cache_manager: WikiCacheManager instance for local file management
            performance_monitor: PerformanceMonitor instance for tracking metrics
            request_timeout: HTTP request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries in seconds
            user_agent: User agent string for HTTP requests
        """
        self.cache_manager = cache_manager
        self.performance_monitor = performance_monitor
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.user_agent = user_agent
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._download_history: List[DownloadResult] = []
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
    
    async def _ensure_session(self) -> None:
        """Ensure HTTP session is initialized"""
        if not self._session:
            timeout = aiohttp.ClientTimeout(total=self.request_timeout)
            headers = {'User-Agent': self.user_agent}
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers
            )
    
    async def cleanup(self) -> None:
        """Clean up HTTP session"""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def download_page(self, url: str, local_path: Optional[str] = None, 
                          content_type: str = "general") -> DownloadResult:
        """
        Download a single page with error handling and retry logic
        
        Args:
            url: URL to download
            local_path: Local file path to save content (auto-generated if None)
            content_type: Type of content for organized storage
            
        Returns:
            DownloadResult with download status and metadata
        """
        logger.info(f"Starting download: {url}")
        
        # Start performance monitoring
        start_time = datetime.now()
        
        # Validate URL
        if not self.validate_url(url):
            error_msg = f"Invalid URL: {url}"
            logger.error(error_msg)
            result = DownloadResult(
                url=url,
                success=False,
                error_message=error_msg
            )
            
            # Record performance metrics
            if self.performance_monitor:
                duration = (datetime.now() - start_time).total_seconds()
                await self.performance_monitor.record_download_metrics(
                    url=url,
                    duration=duration,
                    success=False,
                    file_size=0,
                    status_code=None
                )
            
            return result
        
        # Determine local path
        if local_path is None:
            if self.cache_manager:
                local_path = self.cache_manager.get_organized_path(url, content_type)
            else:
                local_path = self._generate_local_path(url, content_type)
        
        # Sanitize local path
        sanitized_path = self._sanitize_path(local_path)
        
        # Ensure session is ready
        await self._ensure_session()
        
        # Attempt download with retries
        last_error = None
        for attempt in range(self.max_retries):
            try:
                result = await self._attempt_download(url, sanitized_path, attempt)
                if result.success:
                    # Add to cache manager if available
                    if self.cache_manager:
                        await self.cache_manager.add_file(url, sanitized_path, result.download_time)
                    
                    self._download_history.append(result)
                    logger.info(f"Successfully downloaded {url} to {sanitized_path}")
                    
                    # Record performance metrics
                    if self.performance_monitor:
                        duration = (datetime.now() - start_time).total_seconds()
                        await self.performance_monitor.record_download_metrics(
                            url=url,
                            duration=duration,
                            success=True,
                            file_size=result.content_length or 0,
                            status_code=result.status_code
                        )
                    
                    return result
                else:
                    last_error = result.error_message
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Download attempt {attempt + 1} failed for {url}: {e}")
                
                # Wait before retry (exponential backoff)
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
        
        # All attempts failed
        error_msg = f"Failed to download after {self.max_retries} attempts: {last_error}"
        logger.error(f"Download failed for {url}: {error_msg}")
        
        result = DownloadResult(
            url=url,
            success=False,
            local_path=sanitized_path,
            error_message=error_msg,
            retry_count=self.max_retries
        )
        self._download_history.append(result)
        
        # Record performance metrics for failed download
        if self.performance_monitor:
            duration = (datetime.now() - start_time).total_seconds()
            await self.performance_monitor.record_download_metrics(
                url=url,
                duration=duration,
                success=False,
                file_size=0,
                status_code=None
            )
        
        return result
    
    async def _attempt_download(self, url: str, local_path: str, attempt: int) -> DownloadResult:
        """
        Single download attempt
        
        Args:
            url: URL to download
            local_path: Local file path to save content
            attempt: Current attempt number (0-based)
            
        Returns:
            DownloadResult with attempt status
        """
        if not self._session:
            raise RuntimeError("HTTP session not initialized")
        
        start_time = datetime.now()
        
        try:
            async with self._session.get(url) as response:
                status_code = response.status
                
                if status_code == 200:
                    content = await response.text()
                    content_length = len(content)
                    
                    # Ensure directory exists
                    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
                    
                    # Save content to file
                    async with aiofiles.open(local_path, 'w', encoding='utf-8') as f:
                        await f.write(content)
                    
                    # Save download metadata
                    await self._save_download_metadata(url, local_path, status_code, content_length, start_time)
                    
                    return DownloadResult(
                        url=url,
                        success=True,
                        local_path=local_path,
                        status_code=status_code,
                        content_length=content_length,
                        download_time=start_time,
                        retry_count=attempt
                    )
                else:
                    error_msg = f"HTTP {status_code}"
                    return DownloadResult(
                        url=url,
                        success=False,
                        local_path=local_path,
                        status_code=status_code,
                        download_time=start_time,
                        error_message=error_msg,
                        retry_count=attempt
                    )
                    
        except aiohttp.ClientError as e:
            error_msg = f"Client error: {str(e)}"
            return DownloadResult(
                url=url,
                success=False,
                local_path=local_path,
                download_time=start_time,
                error_message=error_msg,
                retry_count=attempt
            )
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            return DownloadResult(
                url=url,
                success=False,
                local_path=local_path,
                download_time=start_time,
                error_message=error_msg,
                retry_count=attempt
            )
    
    async def _save_download_metadata(self, url: str, local_path: str, status_code: int, 
                                    content_length: int, download_time: datetime) -> None:
        """Save download metadata to JSON file"""
        metadata = {
            'url': url,
            'download_date': download_time.isoformat(),
            'status_code': status_code,
            'content_length': content_length,
            'local_path': local_path
        }
        
        metadata_path = Path(local_path).with_suffix('.meta.json')
        try:
            async with aiofiles.open(metadata_path, 'w') as f:
                await f.write(json.dumps(metadata, indent=2))
        except Exception as e:
            logger.warning(f"Failed to save metadata for {url}: {e}")
    
    def validate_url(self, url: str) -> bool:
        """
        Validate and sanitize URL
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        try:
            parsed = urlparse(url.strip())
            
            # Check required components
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check scheme
            if parsed.scheme.lower() not in ['http', 'https']:
                return False
            
            # Check for suspicious characters
            suspicious_chars = ['<', '>', '"', '\'', '`', '{', '}']
            if any(char in url for char in suspicious_chars):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _sanitize_path(self, path: str) -> str:
        """
        Sanitize local file path
        
        Args:
            path: File path to sanitize
            
        Returns:
            Sanitized file path
        """
        # Convert to Path object for normalization
        path_obj = Path(path)
        
        # Remove any dangerous path components
        parts = []
        for part in path_obj.parts:
            # Skip dangerous parts
            if part in ['.', '..'] or part.startswith('.'):
                continue
            # Sanitize filename
            sanitized_part = "".join(c for c in part if c.isalnum() or c in '-_.')
            if sanitized_part:
                parts.append(sanitized_part)
        
        if not parts:
            parts = ['download']
        
        return str(Path(*parts))
    
    def get_download_history(self) -> List[DownloadResult]:
        """Get history of all download attempts"""
        return self._download_history.copy()
    
    def get_successful_downloads(self) -> List[DownloadResult]:
        """Get history of successful downloads only"""
        return [result for result in self._download_history if result.success]
    
    def get_failed_downloads(self) -> List[DownloadResult]:
        """Get history of failed downloads only"""
        return [result for result in self._download_history if not result.success]
    
    def clear_history(self) -> None:
        """Clear download history"""
        self._download_history.clear()
    
    async def is_refresh_needed(self, url: str, max_age_hours: int) -> bool:
        """
        Check if a file needs to be refreshed based on age
        
        Args:
            url: URL to check
            max_age_hours: Maximum age in hours before refresh is needed
            
        Returns:
            True if refresh is needed, False otherwise
        """
        if not self.cache_manager:
            # Without cache manager, always refresh
            return True
        
        # Check if file exists and is fresh
        return not await self.cache_manager.is_file_fresh(url, max_age_hours)
    
    async def get_cached_file_path(self, url: str) -> Optional[str]:
        """
        Get cached file path for a URL if it exists
        
        Args:
            url: URL to look up
            
        Returns:
            Local file path if cached, None otherwise
        """
        if not self.cache_manager:
            return None
        
        return await self.cache_manager.get_file_path(url)
    
    async def get_file_age(self, url: str) -> Optional[timedelta]:
        """
        Get age of a cached file
        
        Args:
            url: URL to check
            
        Returns:
            Age as timedelta, or None if not cached
        """
        if not self.cache_manager:
            return None
        
        return await self.cache_manager.get_file_age(url)
    
    def _generate_local_path(self, url: str, content_type: str = "general") -> str:
        """
        Generate local path when no cache manager is available
        
        Args:
            url: Source URL
            content_type: Type of content
            
        Returns:
            Generated local file path
        """
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        
        # Extract filename from URL
        path_parts = parsed.path.strip('/').split('/')
        filename = path_parts[-1] if path_parts else 'index'
        
        # Ensure .html extension
        if not filename.endswith('.html'):
            filename += '.html'
        
        # Simple path structure
        return f"./data/wiki/{content_type}/{filename}"
    
    async def download_all_configured_pages(self, 
                                          urls: List[str],
                                          max_age_hours: int = 24,
                                          max_concurrent: int = 5,
                                          progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> BatchDownloadResult:
        """
        Download all configured pages with progress tracking and concurrent handling
        
        Args:
            urls: List of URLs to download
            max_age_hours: Maximum age before refresh is needed
            max_concurrent: Maximum number of concurrent downloads
            progress_callback: Optional callback for progress updates
            
        Returns:
            BatchDownloadResult with overall status and individual results
        """
        logger.info(f"Starting batch download of {len(urls)} URLs")
        
        start_time = datetime.now()
        results = []
        
        # Initialize progress tracking
        progress = DownloadProgress(
            total_urls=len(urls),
            completed=0,
            successful=0,
            failed=0,
            skipped=0
        )
        
        # Create semaphore for concurrent downloads
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # Create download tasks
        tasks = []
        for url in urls:
            task = self._download_with_semaphore(
                semaphore, url, max_age_hours, progress, progress_callback
            )
            tasks.append(task)
        
        # Execute downloads concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        successful = 0
        failed = 0
        skipped = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Handle exception
                error_result = DownloadResult(
                    url=urls[i],
                    success=False,
                    error_message=str(result)
                )
                processed_results.append(error_result)
                failed += 1
            elif isinstance(result, DownloadResult):
                processed_results.append(result)
                if result.success:
                    successful += 1
                else:
                    failed += 1
            else:
                # Skipped download
                skipped += 1
        
        end_time = datetime.now()
        total_duration = end_time - start_time
        
        batch_result = BatchDownloadResult(
            total_urls=len(urls),
            successful_downloads=successful,
            failed_downloads=failed,
            skipped_downloads=skipped,
            results=processed_results,
            start_time=start_time,
            end_time=end_time,
            total_duration=total_duration
        )
        
        logger.info(f"Batch download completed: {successful} successful, {failed} failed, {skipped} skipped in {total_duration}")
        return batch_result
    
    async def _download_with_semaphore(self,
                                     semaphore: asyncio.Semaphore,
                                     url: str,
                                     max_age_hours: int,
                                     progress: DownloadProgress,
                                     progress_callback: Optional[Callable[[DownloadProgress], None]]) -> Optional[DownloadResult]:
        """
        Download a single URL with semaphore control and progress tracking
        
        Args:
            semaphore: Semaphore for controlling concurrency
            url: URL to download
            max_age_hours: Maximum age before refresh is needed
            progress: Progress tracking object
            progress_callback: Optional progress callback
            
        Returns:
            DownloadResult or None if skipped
        """
        async with semaphore:
            try:
                # Update progress
                progress.current_url = url
                if progress_callback:
                    progress_callback(progress)
                
                # Check if refresh is needed
                if not await self.is_refresh_needed(url, max_age_hours):
                    logger.info(f"Skipping {url} - file is still fresh")
                    progress.completed += 1
                    progress.skipped += 1
                    progress.current_url = None
                    if progress_callback:
                        progress_callback(progress)
                    return None
                
                # Determine content type from URL
                content_type = self._determine_content_type(url)
                
                # Download the page
                result = await self.download_page(url, content_type=content_type)
                
                # Update progress
                progress.completed += 1
                if result.success:
                    progress.successful += 1
                else:
                    progress.failed += 1
                
                progress.current_url = None
                if progress_callback:
                    progress_callback(progress)
                
                return result
                
            except Exception as e:
                logger.error(f"Error in batch download for {url}: {e}")
                progress.completed += 1
                progress.failed += 1
                progress.current_url = None
                if progress_callback:
                    progress_callback(progress)
                
                return DownloadResult(
                    url=url,
                    success=False,
                    error_message=str(e)
                )
    
    def _determine_content_type(self, url: str) -> str:
        """
        Determine content type from URL pattern
        
        Args:
            url: URL to analyze
            
        Returns:
            Content type string
        """
        url_lower = url.lower()
        
        if '/resources/' in url_lower and 'genres' in url_lower:
            return "genres"
        elif '/resources/' in url_lower and 'metatags' in url_lower:
            return "meta_tags"
        elif '/tips/' in url_lower:
            return "techniques"
        else:
            return "general"
    
    async def download_with_retry_logic(self, 
                                      urls: List[str],
                                      max_age_hours: int = 24,
                                      max_concurrent: int = 5,
                                      max_batch_retries: int = 2,
                                      progress_callback: Optional[Callable[[DownloadProgress], None]] = None) -> BatchDownloadResult:
        """
        Download URLs with retry logic for failed downloads
        
        Args:
            urls: List of URLs to download
            max_age_hours: Maximum age before refresh is needed
            max_concurrent: Maximum number of concurrent downloads
            max_batch_retries: Maximum number of retry attempts for failed downloads
            progress_callback: Optional callback for progress updates
            
        Returns:
            BatchDownloadResult with overall status
        """
        logger.info(f"Starting download with retry logic for {len(urls)} URLs")
        
        all_results = []
        remaining_urls = urls.copy()
        
        for retry_attempt in range(max_batch_retries + 1):
            if not remaining_urls:
                break
            
            if retry_attempt > 0:
                logger.info(f"Retry attempt {retry_attempt} for {len(remaining_urls)} failed URLs")
                # Wait before retry
                await asyncio.sleep(self.retry_delay * retry_attempt)
            
            # Download current batch
            batch_result = await self.download_all_configured_pages(
                remaining_urls, max_age_hours, max_concurrent, progress_callback
            )
            
            # Collect results
            all_results.extend(batch_result.results)
            
            # Prepare URLs for retry (only failed ones)
            if retry_attempt < max_batch_retries:
                remaining_urls = [
                    result.url for result in batch_result.results 
                    if not result.success and result.error_message and 'Invalid URL' not in result.error_message
                ]
            else:
                remaining_urls = []
        
        # Compile final results
        successful = sum(1 for result in all_results if result.success)
        failed = sum(1 for result in all_results if not result.success)
        
        final_result = BatchDownloadResult(
            total_urls=len(urls),
            successful_downloads=successful,
            failed_downloads=failed,
            skipped_downloads=0,  # Skipped downloads are not retried
            results=all_results
        )
        
        logger.info(f"Download with retry completed: {successful} successful, {failed} failed")
        return final_result