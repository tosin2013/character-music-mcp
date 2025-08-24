#!/usr/bin/env python3
"""
Integration test for WikiDataManager with new WikiDownloader

This script tests the integration between WikiDataManager,
WikiDownloader, and WikiCacheManager components.
"""

import asyncio
import logging
import tempfile
import shutil
from pathlib import Path

from wiki_data_system import WikiDataManager, WikiConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_wiki_data_manager_integration():
    """Test WikiDataManager with new downloader integration"""
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Using temporary directory: {temp_dir}")
    
    try:
        # Create test configuration
        config = WikiConfig(
            enabled=True,
            local_storage_path=temp_dir,
            refresh_interval_hours=1,
            fallback_to_hardcoded=True,
            genre_pages=[],  # Empty for testing
            meta_tag_pages=[],
            tip_pages=[],
            request_timeout=10,
            max_retries=2,
            retry_delay=0.5
        )
        
        # Validate configuration
        errors = config.validate()
        assert len(errors) == 0, f"Configuration validation failed: {errors}"
        logger.info("✓ Configuration validation passed")
        
        # Initialize WikiDataManager
        manager = WikiDataManager()
        await manager.initialize(config)
        
        # Test that components are initialized
        assert manager.cache_manager is not None, "Cache manager not initialized"
        assert manager.downloader is not None, "Downloader not initialized"
        logger.info("✓ WikiDataManager components initialized")
        
        # Test empty refresh (no URLs configured)
        result = await manager.refresh_data(force=True)
        assert result.success == True, "Empty refresh should succeed"
        assert result.pages_downloaded == 0, "No pages should be downloaded"
        logger.info("✓ Empty refresh test passed")
        
        # Test data retrieval (should return empty lists)
        genres = await manager.get_genres()
        meta_tags = await manager.get_meta_tags()
        techniques = await manager.get_techniques()
        
        assert isinstance(genres, list), "Genres should be a list"
        assert isinstance(meta_tags, list), "Meta tags should be a list"
        assert isinstance(techniques, list), "Techniques should be a list"
        logger.info("✓ Data retrieval tests passed")
        
        # Test source URL retrieval
        genre_urls = manager.get_source_urls("genres")
        meta_tag_urls = manager.get_source_urls("meta_tags")
        technique_urls = manager.get_source_urls("techniques")
        
        assert isinstance(genre_urls, list), "Genre URLs should be a list"
        assert isinstance(meta_tag_urls, list), "Meta tag URLs should be a list"
        assert isinstance(technique_urls, list), "Technique URLs should be a list"
        logger.info("✓ Source URL retrieval tests passed")
        
        # Test cache statistics
        if manager.cache_manager:
            stats = await manager.cache_manager.get_cache_stats()
            assert stats.total_entries == 0, "Cache should be empty"
            assert stats.total_size_bytes == 0, "Cache size should be zero"
            logger.info("✓ Cache statistics tests passed")
        
        # Clean up
        await manager.cleanup()
        logger.info("✓ Manager cleanup completed")
        
        logger.info("✅ All integration tests passed!")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        logger.info(f"Cleaned up temporary directory: {temp_dir}")

async def test_configuration_management():
    """Test configuration loading and saving"""
    
    # Create temporary directory for config
    temp_dir = tempfile.mkdtemp()
    config_path = Path(temp_dir) / "test_config.json"
    
    try:
        from wiki_data_system import ConfigurationManager
        
        # Test default configuration
        default_config = WikiConfig()
        assert default_config.enabled == True
        assert default_config.refresh_interval_hours == 24
        logger.info("✓ Default configuration test passed")
        
        # Test configuration saving and loading
        await ConfigurationManager.save_config(default_config, str(config_path))
        assert config_path.exists(), "Config file should be created"
        
        loaded_config = await ConfigurationManager.load_config(str(config_path))
        assert loaded_config.enabled == default_config.enabled
        assert loaded_config.refresh_interval_hours == default_config.refresh_interval_hours
        logger.info("✓ Configuration save/load tests passed")
        
        # Test configuration validation
        invalid_config = WikiConfig(
            refresh_interval_hours=0,  # Invalid
            request_timeout=-1,        # Invalid
            local_storage_path=""      # Invalid
        )
        
        errors = ConfigurationManager.validate_config(invalid_config)
        assert len(errors) > 0, "Invalid configuration should have errors"
        logger.info("✓ Configuration validation tests passed")
        
        logger.info("✅ All configuration tests passed!")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        logger.info(f"Cleaned up temporary directory: {temp_dir}")

async def main():
    """Run all integration tests"""
    logger.info("Starting WikiDataManager integration tests...")
    
    # Run integration tests
    await test_wiki_data_manager_integration()
    
    # Run configuration tests
    await test_configuration_management()
    
    logger.info("🎉 All integration tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())