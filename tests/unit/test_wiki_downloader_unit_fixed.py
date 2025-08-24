#!/usr/bin/env python3
"""
Unit tests for WikiDownloader

Tests the WikiDownloader class with mocked HTTP responses to ensure
proper functionality without network dependencies.
"""

import pytest
import pytest_asyncio
import asyncio
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta
import aiohttp

from wiki_downloader import (
    WikiDownloader, 
    DownloadResult, 
    BatchDownloadResult, 
    DownloadProgress
)
from wiki_cache_manager import WikiCacheManager

class TestWikiDownloader:
    """Unit tests for WikiDownloader class"""
    
    @pytest_asyncio.fixture
    async def temp_cache_manager(self):
        """Create a temporary cache manager for testing"""
        temp_dir = tempfile.mkdtemp()
        cache_manager = WikiCacheManager(temp_dir)
        await cache_manager.initialize()
        yield cache_manager
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest_asyncio.fixture
    async def downloader(self, temp_cache_manager):
        """Create a WikiDownloader instance for testing"""
        downloader = WikiDownloader(
            cache_manager=temp_cache_manager,
            request_timeout=5,
            max_retries=2
        )
        yield downloader
    
    def test_url_validation(self, downloader):
        """Test URL validation functionality"""
        # Valid URLs
        assert downloader.validate_url("https://example.com") == True
        assert downloader.validate_url("http://example.com") == True
        assert downloader.validate_url("https://sunoaiwiki.com/resources/genres") == True
        
        # Invalid URLs
        assert downloader.validate_url("") == False
        assert downloader.validate_url("not-a-url") == False
        assert downloader.validate_url("ftp://example.com") == False
        assert downloader.validate_url("javascript:alert('xss')") == False
        assert downloader.validate_url(None) == False
    
    @pytest.mark.asyncio
    async def test_download_page_success(self, downloader, temp_cache_manager):
        """Test successful page download"""
        test_url = "https://example.com/test"
        test_html = "<html><body><h1>Test Page</h1></body></html>"
        
        # Mock the HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=test_html)
        mock_response.headers = {'content-type': 'text/html'}
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with downloader:
                result = await downloader.download_page(test_url)
            
            assert result.success == True
            assert result.url == test_url
            assert result.status_code == 200
            assert result.local_path != ""
            
            # Verify file was cached
            cached_path = await temp_cache_manager.get_cached_file_path(test_url)
            assert cached_path is not None
            assert Path(cached_path).exists()
    
    @pytest.mark.asyncio
    async def test_download_page_http_error(self, downloader):
        """Test download with HTTP error response"""
        test_url = "https://example.com/notfound"
        
        # Mock 404 response
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value="Not Found")
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with downloader:
                result = await downloader.download_page(test_url)
            
            assert result.success == False
            assert "404" in result.error_message
    
    @pytest.mark.asyncio
    async def test_download_page_network_error(self, downloader):
        """Test download with network error"""
        test_url = "https://example.com/timeout"
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = aiohttp.ClientError("Connection timeout")
            
            async with downloader:
                result = await downloader.download_page(test_url)
            
            assert result.success == False
            assert "Connection timeout" in result.error_message
    
    @pytest.mark.asyncio
    async def test_download_page_invalid_url(self, downloader):
        """Test download with invalid URL"""
        invalid_url = "not-a-url"
        
        async with downloader:
            result = await downloader.download_page(invalid_url)
        
        assert result.success == False
        assert "Invalid URL" in result.error_message
    
    @pytest.mark.asyncio
    async def test_is_refresh_needed(self, downloader, temp_cache_manager):
        """Test refresh need detection"""
        test_url = "https://example.com/test"
        
        # Non-existent file should need refresh
        needs_refresh = await downloader.is_refresh_needed(test_url, 24)
        assert needs_refresh == True
        
        # Create a fresh file by adding it to cache
        test_html = "<html><body>Test</body></html>"
        temp_file = temp_cache_manager.cache_root / "general" / "test.html"
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file.write_text(test_html)
        
        # Add to cache index
        await temp_cache_manager.add_file(test_url, str(temp_file))
        
        # Fresh file should not need refresh
        needs_refresh = await downloader.is_refresh_needed(test_url, 24)
        assert needs_refresh == False
        
        # Test with old file (mock old timestamp)
        old_time = datetime.now() - timedelta(days=2)
        temp_file.touch(times=(old_time.timestamp(), old_time.timestamp()))
        
        needs_refresh = await downloader.is_refresh_needed(test_url, 24)
        assert needs_refresh == True
    
    @pytest.mark.asyncio
    async def test_batch_download_success(self, downloader):
        """Test successful batch download"""
        test_urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        # Mock successful responses
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")
        mock_response.headers = {'content-type': 'text/html'}
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            progress_updates = []
            def progress_callback(progress: DownloadProgress):
                progress_updates.append(progress)
            
            async with downloader:
                result = await downloader.download_all_configured_pages(
                    test_urls,
                    max_age_hours=24,
                    max_concurrent=2,
                    progress_callback=progress_callback
                )
            
            assert result.total_urls == 3
            assert result.successful_downloads == 3
            assert result.failed_downloads == 0
            assert result.skipped_downloads == 0
            assert len(result.results) == 3
            
            # Check progress updates
            assert len(progress_updates) > 0
            final_progress = progress_updates[-1]
            assert final_progress.completed == 3
            assert final_progress.successful == 3
    
    @pytest.mark.asyncio
    async def test_batch_download_empty_list(self, downloader):
        """Test batch download with empty URL list"""
        async with downloader:
            result = await downloader.download_all_configured_pages([])
        
        assert result.total_urls == 0
        assert result.successful_downloads == 0
        assert result.failed_downloads == 0
        assert result.skipped_downloads == 0
        assert len(result.results) == 0
    
    @pytest.mark.asyncio
    async def test_get_cached_file_path(self, downloader, temp_cache_manager):
        """Test getting cached file path"""
        test_url = "https://example.com/test"
        
        # No cached file initially
        cached_path = await downloader.get_cached_file_path(test_url)
        assert cached_path is None
        
        # Create and cache a file
        test_html = "<html>Test</html>"
        temp_file = temp_cache_manager.cache_root / "general" / "test.html"
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file.write_text(test_html)
        
        # Add to cache index
        await temp_cache_manager.add_file(test_url, str(temp_file))
        
        # Should now return cached path
        cached_path = await downloader.get_cached_file_path(test_url)
        assert cached_path is not None
        assert Path(cached_path).exists()
    
    @pytest.mark.asyncio
    async def test_context_manager(self, temp_cache_manager):
        """Test WikiDownloader as context manager"""
        downloader = WikiDownloader(cache_manager=temp_cache_manager)
        
        # Test async context manager
        async with downloader:
            assert downloader._session is not None
            assert not downloader._session.closed
        
        # Session should be closed after context
        assert downloader._session.closed
    
    @pytest.mark.asyncio
    async def test_cleanup(self, temp_cache_manager):
        """Test manual cleanup"""
        downloader = WikiDownloader(cache_manager=temp_cache_manager)
        
        # Initialize session
        await downloader._ensure_session()
        assert downloader._session is not None
        
        # Cleanup
        await downloader.cleanup()
        assert downloader._session is None

if __name__ == "__main__":
    # Run basic tests
    async def run_basic_tests():
        temp_dir = tempfile.mkdtemp()
        try:
            cache_manager = WikiCacheManager(temp_dir)
            await cache_manager.initialize()
            
            downloader = WikiDownloader(cache_manager=cache_manager)
            
            # Test URL validation
            assert downloader.validate_url("https://example.com") == True
            assert downloader.validate_url("invalid") == False
            print("✓ URL validation tests passed")
            
            # Test refresh need detection
            needs_refresh = await downloader.is_refresh_needed("https://example.com", 24)
            assert needs_refresh == True
            print("✓ Refresh detection tests passed")
            
            print("Basic WikiDownloader unit tests passed!")
            
        finally:
            shutil.rmtree(temp_dir)
    
    asyncio.run(run_basic_tests())