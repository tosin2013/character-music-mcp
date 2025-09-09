"""
Integration tests for configuration management and validation system.
"""

import json
import tempfile
from pathlib import Path

import aiofiles
import pytest

from wiki_config_validator import validate_config_full, validate_config_quick
from wiki_data_system import WikiConfig, WikiDataManager


class TestConfigurationIntegration:
    """Test integration between configuration validation and wiki data system"""

    @pytest.mark.asyncio
    async def test_wiki_data_manager_with_validation(self):
        """Test WikiDataManager with configuration validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create valid configuration
            config = WikiConfig(
                enabled=True,
                local_storage_path=temp_dir,
                refresh_interval_hours=24,
                genre_pages=["https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"],
                meta_tag_pages=["https://sunoaiwiki.com/resources/2024-05-13-list-of-metatags/"],
                tip_pages=["https://sunoaiwiki.com/tips/2024-05-02-how-to-enhance-song-production-using-suno-ai/"]
            )

            # Validate configuration
            validation_result = await validate_config_quick(config)
            assert validation_result.is_valid == True

            # Initialize WikiDataManager
            manager = WikiDataManager()
            await manager.initialize(config)

            assert manager.initialized == True
            assert manager.config == config

    @pytest.mark.asyncio
    async def test_wiki_data_manager_with_invalid_config(self):
        """Test WikiDataManager with invalid configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid configuration
            invalid_config = WikiConfig(
                enabled=True,
                local_storage_path=temp_dir,
                refresh_interval_hours=-1,  # Invalid
                request_timeout=0,          # Invalid
                max_retries=-1             # Invalid
            )

            # Validate configuration
            validation_result = await validate_config_quick(invalid_config)
            assert validation_result.is_valid == False
            assert len(validation_result.errors) >= 3

            # WikiDataManager should reject invalid config
            manager = WikiDataManager()

            with pytest.raises(ValueError, match="Invalid configuration"):
                await manager.initialize(invalid_config)

    @pytest.mark.asyncio
    async def test_dynamic_config_with_wiki_data_manager(self):
        """Test dynamic configuration management with WikiDataManager"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            # Create initial configuration
            initial_config = WikiConfig(
                enabled=True,
                local_storage_path=temp_dir,
                refresh_interval_hours=24
            )

            # Save configuration to file
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(initial_config.to_dict(), indent=2))

            # Initialize WikiDataManager
            manager = WikiDataManager()
            await manager.initialize(initial_config)

            # Enable dynamic configuration
            await manager.enable_dynamic_config(str(config_file))

            assert manager.dynamic_config_manager is not None
            assert manager.dynamic_config_manager.is_watching() == True

            # Test runtime configuration update
            success = await manager.update_config_runtime(refresh_interval_hours=48)
            assert success == True
            assert manager.config.refresh_interval_hours == 48

            # Test adding URLs at runtime
            success = await manager.add_wiki_urls_runtime(
                "genre_pages",
                ["https://example.com/new-genre-page"],
                validate_urls=False
            )
            assert success == True
            assert "https://example.com/new-genre-page" in manager.config.genre_pages

            # Test removing URLs at runtime
            success = await manager.remove_wiki_urls_runtime(
                "genre_pages",
                ["https://example.com/new-genre-page"]
            )
            assert success == True
            assert "https://example.com/new-genre-page" not in manager.config.genre_pages

            # Get dynamic config status
            status = manager.get_dynamic_config_status()
            assert status['enabled'] == True
            assert status['watching'] == True

            # Disable dynamic configuration
            manager.disable_dynamic_config()

            status = manager.get_dynamic_config_status()
            assert status['enabled'] == False
            assert status['watching'] == False

    @pytest.mark.asyncio
    async def test_config_change_handling(self):
        """Test configuration change handling in WikiDataManager"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            # Create initial configuration
            initial_config = WikiConfig(
                enabled=True,
                local_storage_path=temp_dir,
                refresh_interval_hours=24,
                genre_pages=["https://example.com/page1"]
            )

            # Save configuration to file
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(initial_config.to_dict(), indent=2))

            # Initialize WikiDataManager
            manager = WikiDataManager()
            await manager.initialize(initial_config)
            await manager.enable_dynamic_config(str(config_file))

            # Simulate configuration change
            new_config = WikiConfig(
                enabled=True,
                local_storage_path=temp_dir,
                refresh_interval_hours=48,  # Changed
                genre_pages=["https://example.com/page1", "https://example.com/page2"]  # Added URL
            )

            # Handle configuration change
            await manager._handle_config_change(initial_config, new_config)

            # Verify changes were applied
            assert manager.config.refresh_interval_hours == 48
            assert len(manager.config.genre_pages) == 2
            assert "https://example.com/page2" in manager.config.genre_pages

            manager.disable_dynamic_config()

    @pytest.mark.asyncio
    async def test_storage_path_change_handling(self):
        """Test handling of storage path changes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            old_storage = Path(temp_dir) / "old_storage"
            new_storage = Path(temp_dir) / "new_storage"

            # Create initial configuration
            initial_config = WikiConfig(
                enabled=True,
                local_storage_path=str(old_storage),
                refresh_interval_hours=24
            )

            # Initialize WikiDataManager
            manager = WikiDataManager()
            await manager.initialize(initial_config)

            assert manager.storage_path == old_storage

            # Simulate storage path change
            new_config = WikiConfig(
                enabled=True,
                local_storage_path=str(new_storage),
                refresh_interval_hours=24
            )

            # Handle configuration change
            await manager._handle_config_change(initial_config, new_config)

            # Verify storage path was updated
            assert manager.storage_path == new_storage
            assert new_storage.exists()

    @pytest.mark.asyncio
    async def test_url_change_cache_invalidation(self):
        """Test cache invalidation when URLs change"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create initial configuration
            initial_config = WikiConfig(
                enabled=True,
                local_storage_path=temp_dir,
                refresh_interval_hours=24,
                genre_pages=["https://example.com/page1"]
            )

            # Initialize WikiDataManager
            manager = WikiDataManager()
            await manager.initialize(initial_config)

            # Set cache as valid
            manager._cache_valid = True

            # Simulate URL change
            new_config = WikiConfig(
                enabled=True,
                local_storage_path=temp_dir,
                refresh_interval_hours=24,
                genre_pages=["https://example.com/page1", "https://example.com/page2"]  # Added URL
            )

            # Handle configuration change
            await manager._handle_config_change(initial_config, new_config)

            # Verify cache was invalidated
            assert manager._cache_valid == False

    @pytest.mark.asyncio
    async def test_runtime_operations_without_dynamic_config(self):
        """Test runtime operations when dynamic config is not enabled"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = WikiConfig(
                enabled=True,
                local_storage_path=temp_dir,
                refresh_interval_hours=24
            )

            # Initialize WikiDataManager without dynamic config
            manager = WikiDataManager()
            await manager.initialize(config)

            # Runtime operations should fail gracefully
            success = await manager.update_config_runtime(refresh_interval_hours=48)
            assert success == False

            success = await manager.add_wiki_urls_runtime("genre_pages", ["https://example.com"])
            assert success == False

            success = await manager.remove_wiki_urls_runtime("genre_pages", ["https://example.com"])
            assert success == False

            # Status should indicate dynamic config is disabled
            status = manager.get_dynamic_config_status()
            assert status['enabled'] == False

    @pytest.mark.asyncio
    async def test_full_validation_with_url_checks(self):
        """Test full configuration validation with URL accessibility checks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = WikiConfig(
                enabled=True,
                local_storage_path=temp_dir,
                refresh_interval_hours=24,
                genre_pages=["https://httpbin.org/status/200"],  # Should be accessible
                meta_tag_pages=["https://httpbin.org/status/404"],  # Should return 404
                tip_pages=["https://invalid-domain-that-does-not-exist.com"]  # Should be inaccessible
            )

            # Perform full validation with URL checks
            validation_result = await validate_config_full(config, timeout=5)

            # Should be valid overall (warnings don't make it invalid)
            assert validation_result.is_valid == True

            # Should have warnings about inaccessible URLs
            assert len(validation_result.warnings) > 0

            # Check URL accessibility results
            assert "https://httpbin.org/status/200" in validation_result.url_checks
            assert "https://httpbin.org/status/404" in validation_result.url_checks
            assert "https://invalid-domain-that-does-not-exist.com" in validation_result.url_checks

            # Storage should be validated successfully
            assert validation_result.storage_info['writable'] == True
            assert 'available_space_gb' in validation_result.storage_info


if __name__ == "__main__":
    pytest.main([__file__])
