"""
Tests for dynamic configuration management system.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import aiofiles
import pytest

from dynamic_config_manager import (
    ConfigChangeHandler,
    DynamicConfigManager,
    add_wiki_urls_runtime,
    create_dynamic_config_manager,
    update_wiki_config_runtime,
)
from wiki_config_validator import ValidationResult
from wiki_data_system import WikiConfig


class TestConfigChangeHandler:
    """Test ConfigChangeHandler class"""

    def test_initialization(self):
        """Test handler initialization"""
        mock_manager = MagicMock()
        handler = ConfigChangeHandler(mock_manager)

        assert handler.config_manager == mock_manager
        assert handler.last_modified == {}

    def test_on_modified_debouncing(self):
        """Test file modification event debouncing"""
        mock_manager = MagicMock()
        handler = ConfigChangeHandler(mock_manager)

        # Mock event - need to import the actual event type
        from watchdog.events import FileModifiedEvent
        mock_event = FileModifiedEvent("/test/config.json")

        # Mock config file
        mock_manager.config_file.name = "config.json"

        # Mock event loop
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.time.return_value = 1000.0

            with patch('asyncio.create_task') as mock_create_task:
                handler.on_modified(mock_event)

                # Should create task for first modification
                mock_create_task.assert_called_once()

                # Reset mock
                mock_create_task.reset_mock()

                # Immediate second modification should be debounced
                mock_loop.return_value.time.return_value = 1000.5
                handler.on_modified(mock_event)

                # Should not create task (debounced)
                mock_create_task.assert_not_called()


class TestDynamicConfigManager:
    """Test DynamicConfigManager class"""

    def test_initialization(self):
        """Test manager initialization"""
        manager = DynamicConfigManager()

        assert manager.config_file.name == "wiki_config.json"
        assert manager.current_config is None
        assert manager.observer is None
        assert manager.watching == False
        assert manager.change_callbacks == []

    def test_initialization_with_custom_path(self):
        """Test manager initialization with custom config path"""
        custom_path = "/custom/path/config.json"
        manager = DynamicConfigManager(custom_path)

        assert str(manager.config_file) == custom_path

    @pytest.mark.asyncio
    async def test_initialize_success(self):
        """Test successful initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            # Create test config file
            test_config = WikiConfig(local_storage_path=temp_dir)
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(test_config.to_dict(), indent=2))

            manager = DynamicConfigManager(str(config_file))
            config = await manager.initialize()

            assert config is not None
            assert manager.current_config == config
            assert manager.last_validation_result is not None

    @pytest.mark.asyncio
    async def test_initialize_with_invalid_config(self):
        """Test initialization with invalid configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            # Create invalid config file
            invalid_config = WikiConfig(
                local_storage_path=temp_dir,
                refresh_interval_hours=-1  # Invalid
            )
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(invalid_config.to_dict(), indent=2))

            manager = DynamicConfigManager(str(config_file))
            config = await manager.initialize()

            assert config is not None
            assert manager.last_validation_result is not None
            assert not manager.last_validation_result.is_valid

    def test_start_stop_watching(self):
        """Test starting and stopping file watching"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"
            manager = DynamicConfigManager(str(config_file))

            # Start watching
            manager.start_watching()
            assert manager.watching == True
            assert manager.observer is not None
            assert manager.file_handler is not None

            # Stop watching
            manager.stop_watching()
            assert manager.watching == False
            assert manager.observer is None
            assert manager.file_handler is None

    def test_start_watching_already_active(self):
        """Test starting watching when already active"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"
            manager = DynamicConfigManager(str(config_file))

            manager.start_watching()
            assert manager.watching == True

            # Try to start again - should log warning but not fail
            manager.start_watching()
            assert manager.watching == True

            manager.stop_watching()

    def test_callback_management(self):
        """Test adding and removing change callbacks"""
        manager = DynamicConfigManager()

        def test_callback(old_config, new_config):
            pass

        # Add callback
        manager.add_change_callback(test_callback)
        assert test_callback in manager.change_callbacks

        # Remove callback
        manager.remove_change_callback(test_callback)
        assert test_callback not in manager.change_callbacks

    @pytest.mark.asyncio
    async def test_handle_config_change_success(self):
        """Test successful configuration change handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            # Create initial config
            initial_config = WikiConfig(
                local_storage_path=temp_dir,
                refresh_interval_hours=24
            )
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(initial_config.to_dict(), indent=2))

            manager = DynamicConfigManager(str(config_file))
            await manager.initialize()

            # Modify config file
            updated_config = WikiConfig(
                local_storage_path=temp_dir,
                refresh_interval_hours=48  # Changed
            )
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(updated_config.to_dict(), indent=2))

            # Handle change
            await manager._handle_config_change()

            assert manager.current_config.refresh_interval_hours == 48

    @pytest.mark.asyncio
    async def test_handle_config_change_invalid(self):
        """Test configuration change handling with invalid config"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            # Create initial config
            initial_config = WikiConfig(
                local_storage_path=temp_dir,
                refresh_interval_hours=24
            )
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(initial_config.to_dict(), indent=2))

            manager = DynamicConfigManager(str(config_file))
            await manager.initialize()

            # Modify config file with invalid data
            invalid_config = WikiConfig(
                local_storage_path=temp_dir,
                refresh_interval_hours=-1  # Invalid
            )
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(invalid_config.to_dict(), indent=2))

            # Handle change
            await manager._handle_config_change()

            # Should keep original config
            assert manager.current_config.refresh_interval_hours == 24

    @pytest.mark.asyncio
    async def test_notify_change_callbacks(self):
        """Test notification of change callbacks"""
        manager = DynamicConfigManager()

        callback_called = False
        old_config_received = None
        new_config_received = None

        def test_callback(old_config, new_config):
            nonlocal callback_called, old_config_received, new_config_received
            callback_called = True
            old_config_received = old_config
            new_config_received = new_config

        manager.add_change_callback(test_callback)

        old_config = WikiConfig(refresh_interval_hours=24)
        new_config = WikiConfig(refresh_interval_hours=48)

        await manager._notify_change_callbacks(old_config, new_config)

        assert callback_called == True
        assert old_config_received == old_config
        assert new_config_received == new_config

    @pytest.mark.asyncio
    async def test_notify_change_callbacks_async(self):
        """Test notification of async change callbacks"""
        manager = DynamicConfigManager()

        callback_called = False

        async def async_callback(old_config, new_config):
            nonlocal callback_called
            callback_called = True

        manager.add_change_callback(async_callback)

        old_config = WikiConfig(refresh_interval_hours=24)
        new_config = WikiConfig(refresh_interval_hours=48)

        await manager._notify_change_callbacks(old_config, new_config)

        assert callback_called == True

    @pytest.mark.asyncio
    async def test_update_config_success(self):
        """Test successful programmatic configuration update"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            manager = DynamicConfigManager(str(config_file))
            await manager.initialize()

            new_config = WikiConfig(
                local_storage_path=temp_dir,
                refresh_interval_hours=48
            )

            result = await manager.update_config(new_config, validate_urls=False)

            assert result.is_valid == True
            assert manager.current_config.refresh_interval_hours == 48

    @pytest.mark.asyncio
    async def test_update_config_invalid(self):
        """Test programmatic configuration update with invalid config"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            manager = DynamicConfigManager(str(config_file))
            await manager.initialize()

            invalid_config = WikiConfig(
                local_storage_path=temp_dir,
                refresh_interval_hours=-1  # Invalid
            )

            result = await manager.update_config(invalid_config, validate_urls=False)

            assert result.is_valid == False
            assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_add_urls_success(self):
        """Test successful URL addition"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            manager = DynamicConfigManager(str(config_file))
            await manager.initialize()

            new_urls = ["https://example.com/new-page"]

            with patch.object(manager.validator, 'validate_new_urls') as mock_validate:
                mock_validate.return_value = {"https://example.com/new-page": True}

                result = await manager.add_urls("genre_pages", new_urls, validate_urls=True)

                assert result.is_valid == True
                assert "https://example.com/new-page" in manager.current_config.genre_pages

    @pytest.mark.asyncio
    async def test_add_urls_invalid_type(self):
        """Test URL addition with invalid type"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            manager = DynamicConfigManager(str(config_file))
            await manager.initialize()

            result = await manager.add_urls("invalid_type", ["https://example.com"])

            assert result.is_valid == False
            assert any("Invalid URL type" in error for error in result.errors)

    @pytest.mark.asyncio
    async def test_add_urls_invalid_url(self):
        """Test URL addition with invalid URL"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            manager = DynamicConfigManager(str(config_file))
            await manager.initialize()

            invalid_urls = ["not-a-url"]

            with patch.object(manager.validator, 'validate_new_urls') as mock_validate:
                mock_validate.return_value = {"not-a-url": False}

                result = await manager.add_urls("genre_pages", invalid_urls, validate_urls=True)

                assert result.is_valid == False
                assert any("Invalid or inaccessible URL" in error for error in result.errors)

    @pytest.mark.asyncio
    async def test_remove_urls_success(self):
        """Test successful URL removal"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            # Create config with URLs to remove
            initial_config = WikiConfig(
                local_storage_path=temp_dir,
                genre_pages=["https://example.com/page1", "https://example.com/page2"]
            )
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(initial_config.to_dict(), indent=2))

            manager = DynamicConfigManager(str(config_file))
            await manager.initialize()

            urls_to_remove = ["https://example.com/page1"]
            result = await manager.remove_urls("genre_pages", urls_to_remove)

            assert result.is_valid == True
            assert "https://example.com/page1" not in manager.current_config.genre_pages
            assert "https://example.com/page2" in manager.current_config.genre_pages

    @pytest.mark.asyncio
    async def test_update_settings_success(self):
        """Test successful settings update"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            manager = DynamicConfigManager(str(config_file))
            await manager.initialize()

            result = await manager.update_settings(
                refresh_interval_hours=48,
                request_timeout=60
            )

            assert result.is_valid == True
            assert manager.current_config.refresh_interval_hours == 48
            assert manager.current_config.request_timeout == 60

    @pytest.mark.asyncio
    async def test_update_settings_unknown_setting(self):
        """Test settings update with unknown setting"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            manager = DynamicConfigManager(str(config_file))
            await manager.initialize()

            result = await manager.update_settings(unknown_setting="value")

            assert result.is_valid == False
            assert any("Unknown configuration setting" in error for error in result.errors)

    def test_get_current_config(self):
        """Test getting current configuration"""
        manager = DynamicConfigManager()

        assert manager.get_current_config() is None

        test_config = WikiConfig()
        manager.current_config = test_config

        assert manager.get_current_config() == test_config

    def test_get_last_validation_result(self):
        """Test getting last validation result"""
        manager = DynamicConfigManager()

        assert manager.get_last_validation_result() is None

        test_result = ValidationResult()
        manager.last_validation_result = test_result

        assert manager.get_last_validation_result() == test_result

    def test_is_watching(self):
        """Test watching status check"""
        manager = DynamicConfigManager()

        assert manager.is_watching() == False

        manager.watching = True
        assert manager.is_watching() == True

    @pytest.mark.asyncio
    async def test_reload_config(self):
        """Test manual configuration reload"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            manager = DynamicConfigManager(str(config_file))
            await manager.initialize()

            with patch.object(manager, '_handle_config_change') as mock_handle:
                result = await manager.reload_config()

                mock_handle.assert_called_once()
                assert isinstance(result, ValidationResult)

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            # Create test config file
            test_config = WikiConfig(local_storage_path=temp_dir)
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(test_config.to_dict(), indent=2))

            async with DynamicConfigManager(str(config_file)) as manager:
                assert manager.current_config is not None
                assert manager.is_watching() == True

            # Should have stopped watching after exit
            assert manager.is_watching() == False


class TestConvenienceFunctions:
    """Test convenience functions"""

    @pytest.mark.asyncio
    async def test_create_dynamic_config_manager(self):
        """Test dynamic config manager creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            # Create test config file
            test_config = WikiConfig(local_storage_path=temp_dir)
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(test_config.to_dict(), indent=2))

            manager = await create_dynamic_config_manager(str(config_file))

            assert isinstance(manager, DynamicConfigManager)
            assert manager.current_config is not None

    @pytest.mark.asyncio
    async def test_update_wiki_config_runtime(self):
        """Test runtime configuration update function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            # Create test config file
            test_config = WikiConfig(local_storage_path=temp_dir)
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(test_config.to_dict(), indent=2))

            result = await update_wiki_config_runtime(
                config_path=str(config_file),
                refresh_interval_hours=48
            )

            assert isinstance(result, ValidationResult)
            assert result.is_valid == True

    @pytest.mark.asyncio
    async def test_add_wiki_urls_runtime(self):
        """Test runtime URL addition function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"

            # Create test config file
            test_config = WikiConfig(local_storage_path=temp_dir)
            async with aiofiles.open(config_file, 'w') as f:
                await f.write(json.dumps(test_config.to_dict(), indent=2))

            with patch('dynamic_config_manager.WikiConfigValidator.validate_new_urls') as mock_validate:
                mock_validate.return_value = {"https://example.com": True}

                result = await add_wiki_urls_runtime(
                    "genre_pages",
                    ["https://example.com"],
                    config_path=str(config_file),
                    validate_urls=True
                )

                assert isinstance(result, ValidationResult)
                assert result.is_valid == True


if __name__ == "__main__":
    pytest.main([__file__])
