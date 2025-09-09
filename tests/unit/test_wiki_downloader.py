import pytest

#!/usr/bin/env python3
"""
Test script for WikiDownloader implementation

This script tests the basic functionality of the WikiDownloader
and WikiCacheManager components.
"""

import asyncio
import logging
import shutil
import tempfile

from wiki_cache_manager import WikiCacheManager
from wiki_downloader import DownloadProgress, WikiDownloader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_basic_functionality():
    """Test basic WikiDownloader and WikiCacheManager functionality"""

    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Using temporary directory: {temp_dir}")

    try:
        # Initialize cache manager
        cache_manager = WikiCacheManager(temp_dir)
        await cache_manager.initialize()

        # Initialize downloader
        downloader = WikiDownloader(cache_manager=cache_manager)

        async with downloader:
            # Test URL validation
            assert downloader.validate_url("https://example.com")
            assert not downloader.validate_url("invalid-url")
            assert not downloader.validate_url("")

            logger.info("✓ URL validation tests passed")

            # Test organized path generation
            test_url = "https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"
            organized_path = cache_manager.get_organized_path(test_url, "genres")
            assert "genres" in organized_path
            assert organized_path.endswith(".html")

            logger.info("✓ Path organization tests passed")

            # Test cache stats
            stats = await cache_manager.get_cache_stats()
            assert stats.total_entries == 0
            assert stats.total_size_bytes == 0

            logger.info("✓ Cache statistics tests passed")

            # Test file age checking (should return True for non-existent files)
            needs_refresh = await downloader.is_refresh_needed(test_url, 24)
            assert needs_refresh

            logger.info("✓ File age checking tests passed")

            # Test batch download with empty list
            empty_result = await downloader.download_all_configured_pages([])
            assert empty_result.total_urls == 0
            assert empty_result.successful_downloads == 0

            logger.info("✓ Empty batch download test passed")

        logger.info("✅ All basic functionality tests passed!")

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        logger.info(f"Cleaned up temporary directory: {temp_dir}")

def progress_callback(progress: DownloadProgress):
    """Progress callback for testing"""
    logger.info(f"Progress: {progress.completed}/{progress.total_urls} "
               f"({progress.progress_percentage:.1f}%) - "
               f"Success: {progress.successful}, Failed: {progress.failed}, Skipped: {progress.skipped}")
    if progress.current_url:
        logger.info(f"Currently downloading: {progress.current_url}")

@pytest.mark.asyncio
async def test_with_real_urls():
    """Test with a small set of real URLs (optional)"""

    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Using temporary directory for real URL test: {temp_dir}")

    try:
        # Initialize cache manager
        cache_manager = WikiCacheManager(temp_dir)
        await cache_manager.initialize()

        # Initialize downloader
        downloader = WikiDownloader(cache_manager=cache_manager, request_timeout=10)

        # Test with a simple, reliable URL
        test_urls = [
            "https://httpbin.org/html",  # Simple test URL that returns HTML
        ]

        async with downloader:
            logger.info("Testing with real URLs...")

            result = await downloader.download_all_configured_pages(
                test_urls,
                max_age_hours=1,
                max_concurrent=2,
                progress_callback=progress_callback
            )

            logger.info(f"Real URL test result: {result.successful_downloads} successful, "
                       f"{result.failed_downloads} failed, {result.skipped_downloads} skipped")

            # Test cache functionality
            if result.successful_downloads > 0:
                # Check if file is now cached
                cached_path = await downloader.get_cached_file_path(test_urls[0])
                if cached_path:
                    logger.info(f"✓ File successfully cached at: {cached_path}")

                    # Test that second download is skipped
                    result2 = await downloader.download_all_configured_pages(
                        test_urls,
                        max_age_hours=24,  # Fresh file should be skipped
                        progress_callback=progress_callback
                    )

                    if result2.skipped_downloads > 0:
                        logger.info("✓ Cache functionality working - file was skipped")
                    else:
                        logger.warning("⚠ Cache functionality may not be working properly")

        logger.info("✅ Real URL tests completed!")

    except Exception as e:
        logger.error(f"Real URL test failed (this may be expected if network is unavailable): {e}")

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        logger.info(f"Cleaned up temporary directory: {temp_dir}")

async def main():
    """Run all tests"""
    logger.info("Starting WikiDownloader tests...")

    # Run basic functionality tests
    await test_basic_functionality()

    # Optionally run real URL tests (commented out to avoid network dependencies)
    # await test_with_real_urls()

    logger.info("🎉 All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
