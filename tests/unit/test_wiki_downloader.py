#!/usr/bin/env python3
"""
Unit Tests for WikiDownloader

Tests the WikiDownloader class with mocked HTTP responses to verify
download functionality, error handling, and retry logic.
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import json

# Import the module under test
from wiki_downloader import WikiDownloader, DownloadResult, BatchDownloadResult, DownloadProgress
from wiki_cache_manager import WikiCacheManager


class TestWikiDownloader:
    """Test suite for WikiDownloader class"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def mock_cache_manager(self):
        """Create mock cache manager"""
        cache_manager = Mock(spec=WikiCacheManager)
        cache_manager.get_organized_path = Mock(return_value="test/path/file.html")
        cache_manager.add_file = AsyncMock()
        cache_manager.is_file_fresh = AsyncMock(return_value=False)
        cache_manager.get_file_path = AsyncMock(return_value=None)
        cache_manager.get_file_age = AsyncMock(return_value=None)
        return cache_manager
    
    @pytest.fixture
    def downloader(self, mock_cache_manager):
        """Create WikiDownloader instance with mock cache manager"""
        return WikiDownloader(
            cache_manager=mock_cache_manager,
            request_timeout=5,
            max_retries=2,
            retry_delay=0.1
        )
    
    @pytest.fixture
    def downloader_no_cache(self):
        """Create WikiDownloader instance without cache manager"""
        return WikiDownloader(
            cache_manager=None,
            request_timeout=5,
            max_retries=2,
            retry_delay=0.1
        )
    
    def test_init_with_cache_manager(self, mock_cache_manager):
        """Test initialization with cache manager"""
        downloader = WikiDownloader(cache_manager=mock_cache_manager)
        
        assert downloader.cache_manager == mock_cache_manager
        assert downloader.request_timeout == 30  # default
        assert downloader.max_retries == 3  # default
        assert downloader.retry_delay == 1.0  # default
        assert downloader.user_agent == "WikiDownloader/1.0"
        assert downloader._session is None
        assert downloader._download_history == []
    
    def test_init_without_cache_manager(self):
        """Test initialization without cache manager"""
        downloader = WikiDownloader()
        
        assert downloader.cache_manager is None
        assert downloader.request_timeout == 30
        assert downloader.max_retries == 3
        assert downloader.retry_delay == 1.0
    
    def test_init_with_custom_params(self):
        """Test initialization with custom parameters"""
        downloader = WikiDownloader(
            request_timeout=10,
            max_retries=5,
            retry_delay=2.0,
            user_agent="TestAgent/1.0"
        )
        
        assert downloader.request_timeout == 10
        assert downloader.max_retries == 5
        assert downloader.retry_delay == 2.0
        assert downloader.user_agent == "TestAgent/1.0"
    
    @pytest.mark.asyncio
    async def test_context_manager(self, downloader):
        """Test async context manager functionality"""
        async with downloader as d:
            assert d._session is not None
            assert isinstance(d._session, aiohttp.ClientSession)
        
        # Session should be closed after context exit
        assert d._session is None
    
    @pytest.mark.asyncio
    async def test_ensure_session(self, downloader):
        """Test session initialization"""
        assert downloader._session is None
        
        await downloader._ensure_session()
        
        assert downloader._session is not None
        assert isinstance(downloader._session, aiohttp.ClientSession)
        
        # Cleanup
        await downloader.cleanup()
    
    @pytest.mark.asyncio
    async def test_cleanup(self, downloader):
        """Test session cleanup"""
        await downloader._ensure_session()
        assert downloader._session is not None
        
        await downloader.cleanup()
        assert downloader._session is None
    
    def test_validate_url_valid_urls(self, downloader):
        """Test URL validation with valid URLs"""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://sunoaiwiki.com/resources/genres",
            "http://localhost:8080/test",
            "https://example.com/path/to/resource?param=value"
        ]
        
        for url in valid_urls:
            assert downloader.validate_url(url), f"URL should be valid: {url}"
    
    def test_validate_url_invalid_urls(self, downloader):
        """Test URL validation with invalid URLs"""
        invalid_urls = [
            "",
            None,
            "not-a-url",
            "ftp://example.com",
            "javascript:alert('xss')",
            "https://example.com<script>",
            "https://example.com\"malicious",
            "   ",
            123,
            []
        ]
        
        for url in invalid_urls:
            assert not downloader.validate_url(url), f"URL should be invalid: {url}"
    
    def test_sanitize_path(self, downloader):
        """Test path sanitization"""
        test_cases = [
            ("normal/path/file.html", "normal/path/file.html"),
            ("../../../etc/passwd", "etc/passwd"),
            ("./file.html", "file.html"),
            ("path/with spaces/file.html", "path/with spaces/file.html"),
            ("path/with-dashes/file.html", "path/with-dashes/file.html"),
            ("path/with_underscores/file.html", "path/with_underscores/file.html"),
            ("", "download"),
            ("///", "download"),
            ("path/with/../../traversal", "path/with/traversal")
        ]
        
        for input_path, expected in test_cases:
            result = downloader._sanitize_path(input_path)
            assert str(Path(result)) == str(Path(expected)), f"Path sanitization failed for {input_path}"
    
    def test_generate_local_path(self, downloader_no_cache):
        """Test local path generation without cache manager"""
        test_cases = [
            ("https://example.com/page.html", "general", "./data/wiki/general/page.html"),
            ("https://example.com/path/to/resource", "genres", "./data/wiki/genres/resource.html"),
            ("https://example.com/", "meta_tags", "./data/wiki/meta_tags/index.html")
        ]
        
        for url, content_type, expected in test_cases:
            result = downloader_no_cache._generate_local_path(url, content_type)
            assert result == expected, f"Path generation failed for {url}"
    
    def test_determine_content_type(self, downloader):
        """Test content type determination from URL"""
        test_cases = [
            ("https://sunoaiwiki.com/resources/genres", "genres"),
            ("https://sunoaiwiki.com/resources/metatags", "meta_tags"),
            ("https://sunoaiwiki.com/tips/how-to-use", "techniques"),
            ("https://example.com/other", "general")
        ]
        
        for url, expected in test_cases:
            result = downloader._determine_content_type(url)
            assert result == expected, f"Content type determination failed for {url}"
    
    @pytest.mark.asyncio
    async def test_download_page_success(self, downloader, temp_dir):
        """Test successful page download"""
        url = "https://example.com/test.html"
        content = "<html><body>Test content</body></html>"
        local_path = str(temp_dir / "test.html")
        
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=content)
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with downloader:
                result = await downloader.download_page(url, local_path)
        
        assert result.success
        assert result.url == url
        assert result.local_path == local_path
        assert result.status_code == 200
        assert result.content_length == len(content)
        assert result.error_message is None
        
        # Verify file was written
        assert Path(local_path).exists()
        with open(local_path, 'r') as f:
            assert f.read() == content
    
    @pytest.mark.asyncio
    async def test_download_page_http_error(self, downloader, temp_dir):
        """Test download with HTTP error response"""
        url = "https://example.com/notfound.html"
        local_path = str(temp_dir / "notfound.html")
        
        # Mock HTTP response with 404 error
        mock_response = AsyncMock()
        mock_response.status = 404
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with downloader:
                result = await downloader.download_page(url, local_path)
        
        assert not result.success
        assert result.url == url
        assert result.local_path == local_path
        assert result.status_code == 404
        assert "HTTP 404" in result.error_message
        assert result.retry_count == 2  # max_retries
    
    @pytest.mark.asyncio
    async def test_download_page_network_error(self, downloader, temp_dir):
        """Test download with network error"""
        url = "https://example.com/test.html"
        local_path = str(temp_dir / "test.html")
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = aiohttp.ClientError("Network error")
            
            async with downloader:
                result = await downloader.download_page(url, local_path)
        
        assert not result.success
        assert result.url == url
        assert "Network error" in result.error_message
        assert result.retry_count == 2  # max_retries
    
    @pytest.mark.asyncio
    async def test_download_page_invalid_url(self, downloader):
        """Test download with invalid URL"""
        url = "invalid-url"
        
        async with downloader:
            result = await downloader.download_page(url)
        
        assert not result.success
        assert result.url == url
        assert "Invalid URL" in result.error_message
        assert result.retry_count == 0  # No retries for invalid URL
    
    @pytest.mark.asyncio
    async def test_download_page_with_cache_manager(self, downloader, temp_dir):
        """Test download with cache manager integration"""
        url = "https://example.com/test.html"
        content = "<html><body>Test content</body></html>"
        
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=content)
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with downloader:
                result = await downloader.download_page(url, content_type="genres")
        
        assert result.success
        
        # Verify cache manager was called
        downloader.cache_manager.get_organized_path.assert_called_once_with(url, "genres")
        downloader.cache_manager.add_file.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_is_refresh_needed_with_cache(self, downloader):
        """Test refresh check with cache manager"""
        url = "https://example.com/test.html"
        max_age_hours = 24
        
        # Test when refresh is needed
        downloader.cache_manager.is_file_fresh.return_value = False
        result = await downloader.is_refresh_needed(url, max_age_hours)
        assert result is True
        
        # Test when refresh is not needed
        downloader.cache_manager.is_file_fresh.return_value = True
        result = await downloader.is_refresh_needed(url, max_age_hours)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_is_refresh_needed_without_cache(self, downloader_no_cache):
        """Test refresh check without cache manager"""
        url = "https://example.com/test.html"
        max_age_hours = 24
        
        # Without cache manager, always refresh
        result = await downloader_no_cache.is_refresh_needed(url, max_age_hours)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_cached_file_path(self, downloader):
        """Test getting cached file path"""
        url = "https://example.com/test.html"
        expected_path = "/path/to/cached/file.html"
        
        downloader.cache_manager.get_file_path.return_value = expected_path
        result = await downloader.get_cached_file_path(url)
        
        assert result == expected_path
        downloader.cache_manager.get_file_path.assert_called_once_with(url)
    
    @pytest.mark.asyncio
    async def test_get_file_age(self, downloader):
        """Test getting file age"""
        url = "https://example.com/test.html"
        expected_age = timedelta(hours=12)
        
        downloader.cache_manager.get_file_age.return_value = expected_age
        result = await downloader.get_file_age(url)
        
        assert result == expected_age
        downloader.cache_manager.get_file_age.assert_called_once_with(url)
    
    def test_download_history_management(self, downloader):
        """Test download history management"""
        # Initially empty
        assert downloader.get_download_history() == []
        assert downloader.get_successful_downloads() == []
        assert downloader.get_failed_downloads() == []
        
        # Add some mock results
        success_result = DownloadResult(url="https://example.com/success", success=True)
        failure_result = DownloadResult(url="https://example.com/failure", success=False)
        
        downloader._download_history.extend([success_result, failure_result])
        
        # Test history retrieval
        history = downloader.get_download_history()
        assert len(history) == 2
        assert success_result in history
        assert failure_result in history
        
        # Test successful downloads
        successful = downloader.get_successful_downloads()
        assert len(successful) == 1
        assert successful[0] == success_result
        
        # Test failed downloads
        failed = downloader.get_failed_downloads()
        assert len(failed) == 1
        assert failed[0] == failure_result
        
        # Test clear history
        downloader.clear_history()
        assert downloader.get_download_history() == []
    
    @pytest.mark.asyncio
    async def test_batch_download_all_successful(self, downloader, temp_dir):
        """Test batch download with all successful downloads"""
        urls = [
            "https://example.com/page1.html",
            "https://example.com/page2.html",
            "https://example.com/page3.html"
        ]
        content = "<html><body>Test content</body></html>"
        
        # Mock HTTP responses
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=content)
        
        # Mock refresh check to always need refresh
        downloader.cache_manager.is_file_fresh.return_value = False
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with downloader:
                result = await downloader.download_all_configured_pages(
                    urls, max_age_hours=24, max_concurrent=2
                )
        
        assert result.total_urls == 3
        assert result.successful_downloads == 3
        assert result.failed_downloads == 0
        assert result.skipped_downloads == 0
        assert len(result.results) == 3
        assert result.end_time is not None
        assert result.total_duration is not None
    
    @pytest.mark.asyncio
    async def test_batch_download_with_failures(self, downloader):
        """Test batch download with some failures"""
        urls = [
            "https://example.com/success.html",
            "https://example.com/failure.html"
        ]
        
        # Mock refresh check
        downloader.cache_manager.is_file_fresh.return_value = False
        
        async def mock_get_side_effect(url):
            mock_response = AsyncMock()
            if "success" in str(url):
                mock_response.status = 200
                mock_response.text = AsyncMock(return_value="<html>Success</html>")
            else:
                mock_response.status = 404
            return mock_response
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = lambda url: mock_get_side_effect(url)
            mock_get.return_value.__aenter__ = lambda self: mock_get_side_effect(None)
            
            # Simplified mock for testing
            with patch.object(downloader, 'download_page') as mock_download:
                mock_download.side_effect = [
                    DownloadResult(url=urls[0], success=True),
                    DownloadResult(url=urls[1], success=False, error_message="HTTP 404")
                ]
                
                async with downloader:
                    result = await downloader.download_all_configured_pages(urls)
        
        assert result.total_urls == 2
        assert result.successful_downloads == 1
        assert result.failed_downloads == 1
        assert result.skipped_downloads == 0
    
    @pytest.mark.asyncio
    async def test_batch_download_with_skipped(self, downloader):
        """Test batch download with skipped files"""
        urls = ["https://example.com/fresh.html"]
        
        # Mock refresh check to indicate file is fresh (no refresh needed)
        downloader.cache_manager.is_file_fresh.return_value = True
        
        async with downloader:
            result = await downloader.download_all_configured_pages(urls)
        
        assert result.total_urls == 1
        assert result.successful_downloads == 0
        assert result.failed_downloads == 0
        assert result.skipped_downloads == 1
    
    @pytest.mark.asyncio
    async def test_batch_download_progress_callback(self, downloader):
        """Test batch download with progress callback"""
        urls = ["https://example.com/test.html"]
        progress_updates = []
        
        def progress_callback(progress: DownloadProgress):
            progress_updates.append({
                'completed': progress.completed,
                'total': progress.total_urls,
                'percentage': progress.progress_percentage,
                'current_url': progress.current_url
            })
        
        # Mock refresh check and download
        downloader.cache_manager.is_file_fresh.return_value = False
        
        with patch.object(downloader, 'download_page') as mock_download:
            mock_download.return_value = DownloadResult(url=urls[0], success=True)
            
            async with downloader:
                result = await downloader.download_all_configured_pages(
                    urls, progress_callback=progress_callback
                )
        
        assert len(progress_updates) >= 2  # At least start and end updates
        assert progress_updates[-1]['completed'] == 1
        assert progress_updates[-1]['percentage'] == 100.0
    
    @pytest.mark.asyncio
    async def test_download_with_retry_logic(self, downloader):
        """Test download with retry logic for failed downloads"""
        urls = [
            "https://example.com/retry-success.html",
            "https://example.com/permanent-failure.html"
        ]
        
        call_count = 0
        
        def mock_download_side_effect(url, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if "retry-success" in url:
                if call_count == 1:
                    # Fail first time
                    return DownloadResult(url=url, success=False, error_message="Temporary error")
                else:
                    # Succeed on retry
                    return DownloadResult(url=url, success=True)
            else:
                # Always fail
                return DownloadResult(url=url, success=False, error_message="Permanent error")
        
        with patch.object(downloader, 'download_all_configured_pages') as mock_batch:
            # Mock the batch download to simulate retry behavior
            mock_batch.side_effect = [
                # First attempt
                BatchDownloadResult(
                    total_urls=2,
                    successful_downloads=0,
                    failed_downloads=2,
                    skipped_downloads=0,
                    results=[
                        DownloadResult(url=urls[0], success=False, error_message="Temporary error"),
                        DownloadResult(url=urls[1], success=False, error_message="Permanent error")
                    ]
                ),
                # Retry attempt
                BatchDownloadResult(
                    total_urls=1,  # Only retry the temporary failure
                    successful_downloads=1,
                    failed_downloads=0,
                    skipped_downloads=0,
                    results=[
                        DownloadResult(url=urls[0], success=True)
                    ]
                )
            ]
            
            async with downloader:
                result = await downloader.download_with_retry_logic(
                    urls, max_batch_retries=1
                )
        
        # Should have results from both attempts
        assert len(result.results) == 3  # 2 from first attempt + 1 from retry
        assert result.successful_downloads == 1
        assert result.failed_downloads == 2


class TestDownloadResult:
    """Test suite for DownloadResult data model"""
    
    def test_download_result_creation(self):
        """Test DownloadResult creation and basic properties"""
        result = DownloadResult(
            url="https://example.com/test.html",
            success=True,
            local_path="/path/to/file.html",
            status_code=200,
            content_length=1024
        )
        
        assert result.url == "https://example.com/test.html"
        assert result.success is True
        assert result.local_path == "/path/to/file.html"
        assert result.status_code == 200
        assert result.content_length == 1024
        assert result.error_message is None
        assert result.retry_count == 0
        assert isinstance(result.download_time, datetime)
    
    def test_download_result_serialization(self):
        """Test DownloadResult to_dict and from_dict methods"""
        original = DownloadResult(
            url="https://example.com/test.html",
            success=False,
            error_message="Test error",
            retry_count=2
        )
        
        # Test serialization
        data = original.to_dict()
        assert isinstance(data, dict)
        assert data['url'] == original.url
        assert data['success'] == original.success
        assert data['error_message'] == original.error_message
        assert data['retry_count'] == original.retry_count
        assert isinstance(data['download_time'], str)  # Should be ISO format
        
        # Test deserialization
        restored = DownloadResult.from_dict(data)
        assert restored.url == original.url
        assert restored.success == original.success
        assert restored.error_message == original.error_message
        assert restored.retry_count == original.retry_count
        assert isinstance(restored.download_time, datetime)


class TestBatchDownloadResult:
    """Test suite for BatchDownloadResult data model"""
    
    def test_batch_download_result_creation(self):
        """Test BatchDownloadResult creation"""
        results = [
            DownloadResult(url="https://example.com/1.html", success=True),
            DownloadResult(url="https://example.com/2.html", success=False)
        ]
        
        batch_result = BatchDownloadResult(
            total_urls=2,
            successful_downloads=1,
            failed_downloads=1,
            skipped_downloads=0,
            results=results
        )
        
        assert batch_result.total_urls == 2
        assert batch_result.successful_downloads == 1
        assert batch_result.failed_downloads == 1
        assert batch_result.skipped_downloads == 0
        assert len(batch_result.results) == 2
        assert isinstance(batch_result.start_time, datetime)
    
    def test_batch_download_result_serialization(self):
        """Test BatchDownloadResult serialization"""
        results = [
            DownloadResult(url="https://example.com/1.html", success=True)
        ]
        
        batch_result = BatchDownloadResult(
            total_urls=1,
            successful_downloads=1,
            failed_downloads=0,
            skipped_downloads=0,
            results=results,
            end_time=datetime.now(),
            total_duration=timedelta(seconds=30)
        )
        
        data = batch_result.to_dict()
        
        assert isinstance(data, dict)
        assert data['total_urls'] == 1
        assert data['successful_downloads'] == 1
        assert isinstance(data['start_time'], str)
        assert isinstance(data['end_time'], str)
        assert isinstance(data['total_duration'], float)
        assert isinstance(data['results'], list)
        assert len(data['results']) == 1


class TestDownloadProgress:
    """Test suite for DownloadProgress data model"""
    
    def test_download_progress_creation(self):
        """Test DownloadProgress creation and properties"""
        progress = DownloadProgress(
            total_urls=10,
            completed=3,
            successful=2,
            failed=1,
            skipped=0,
            current_url="https://example.com/current.html"
        )
        
        assert progress.total_urls == 10
        assert progress.completed == 3
        assert progress.successful == 2
        assert progress.failed == 1
        assert progress.skipped == 0
        assert progress.current_url == "https://example.com/current.html"
    
    def test_progress_percentage_calculation(self):
        """Test progress percentage calculation"""
        # Normal case
        progress = DownloadProgress(total_urls=10, completed=3, successful=2, failed=1, skipped=0)
        assert progress.progress_percentage == 30.0
        
        # Complete case
        progress = DownloadProgress(total_urls=5, completed=5, successful=4, failed=1, skipped=0)
        assert progress.progress_percentage == 100.0
        
        # Zero total case
        progress = DownloadProgress(total_urls=0, completed=0, successful=0, failed=0, skipped=0)
        assert progress.progress_percentage == 100.0
        
        # Not started case
        progress = DownloadProgress(total_urls=10, completed=0, successful=0, failed=0, skipped=0)
        assert progress.progress_percentage == 0.0


if __name__ == "__main__":
    pytest.main([__file__])