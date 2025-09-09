"""
Dynamic configuration management system for wiki data integration.

This module provides runtime configuration updates, file watching, and
configuration reloading without system restart.
"""

import asyncio
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Callable, List, Optional

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from wiki_config_validator import ValidationResult, WikiConfigValidator
from wiki_data_system import ConfigurationManager, WikiConfig

logger = logging.getLogger(__name__)


class ConfigChangeHandler(FileSystemEventHandler):
    """File system event handler for configuration changes"""

    def __init__(self, config_manager: 'DynamicConfigManager'):
        self.config_manager = config_manager
        self.last_modified = {}

    def on_modified(self, event):
        """Handle file modification events"""
        if isinstance(event, FileModifiedEvent) and not event.is_directory:
            file_path = Path(event.src_path)

            # Check if this is our config file
            if file_path.name == self.config_manager.config_file.name:
                # Debounce rapid file changes
                current_time = asyncio.get_event_loop().time()
                last_time = self.last_modified.get(str(file_path), 0)

                if current_time - last_time > 1.0:  # 1 second debounce
                    self.last_modified[str(file_path)] = current_time

                    # Schedule config reload
                    asyncio.create_task(self.config_manager._handle_config_change())


class DynamicConfigManager:
    """
    Dynamic configuration manager with file watching and runtime updates
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_file = Path(config_path or ConfigurationManager.DEFAULT_CONFIG_PATH)
        self.current_config: Optional[WikiConfig] = None
        self.validator = WikiConfigValidator()

        # File watching
        self.observer: Optional[Observer] = None
        self.file_handler: Optional[ConfigChangeHandler] = None

        # Callbacks for configuration changes
        self.change_callbacks: List[Callable[[WikiConfig, WikiConfig], None]] = []

        # State tracking
        self.watching = False
        self.last_validation_result: Optional[ValidationResult] = None

    async def initialize(self) -> WikiConfig:
        """
        Initialize the configuration manager and load initial config
        
        Returns:
            Loaded WikiConfig
        """
        logger.info("Initializing dynamic configuration manager")

        # Load initial configuration
        self.current_config = await ConfigurationManager.load_config(str(self.config_file))

        # Validate initial configuration
        self.last_validation_result = await self.validator.validate_config(
            self.current_config, check_urls=False
        )

        if not self.last_validation_result.is_valid:
            logger.warning(f"Initial configuration has validation errors: {self.last_validation_result.errors}")

        logger.info(f"Loaded configuration from {self.config_file}")
        return self.current_config

    def start_watching(self) -> None:
        """Start watching the configuration file for changes"""
        if self.watching:
            logger.warning("Configuration file watching is already active")
            return

        try:
            # Ensure config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # Set up file system observer
            self.observer = Observer()
            self.file_handler = ConfigChangeHandler(self)

            # Watch the directory containing the config file
            self.observer.schedule(
                self.file_handler,
                str(self.config_file.parent),
                recursive=False
            )

            self.observer.start()
            self.watching = True

            logger.info(f"Started watching configuration file: {self.config_file}")

        except Exception as e:
            logger.error(f"Failed to start configuration file watching: {e}")
            raise

    def stop_watching(self) -> None:
        """Stop watching the configuration file"""
        if not self.watching:
            return

        try:
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5.0)
                self.observer = None

            self.file_handler = None
            self.watching = False

            logger.info("Stopped watching configuration file")

        except Exception as e:
            logger.error(f"Error stopping configuration file watching: {e}")

    async def _handle_config_change(self) -> None:
        """Handle configuration file changes"""
        try:
            logger.info("Configuration file changed, reloading...")

            # Load new configuration
            new_config = await ConfigurationManager.load_config(str(self.config_file))

            # Validate new configuration
            validation_result = await self.validator.validate_config(
                new_config, check_urls=False
            )

            if not validation_result.is_valid:
                logger.error(f"New configuration is invalid: {validation_result.errors}")
                logger.info("Keeping current configuration")
                return

            # Store old config for callbacks
            old_config = self.current_config

            # Update current configuration
            self.current_config = new_config
            self.last_validation_result = validation_result

            logger.info("Configuration reloaded successfully")

            # Notify callbacks
            await self._notify_change_callbacks(old_config, new_config)

        except Exception as e:
            logger.error(f"Error handling configuration change: {e}")

    async def _notify_change_callbacks(self, old_config: WikiConfig, new_config: WikiConfig) -> None:
        """Notify registered callbacks about configuration changes"""
        for callback in self.change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(old_config, new_config)
                else:
                    callback(old_config, new_config)
            except Exception as e:
                logger.error(f"Error in configuration change callback: {e}")

    def add_change_callback(self, callback: Callable[[WikiConfig, WikiConfig], None]) -> None:
        """
        Add a callback to be notified when configuration changes
        
        Args:
            callback: Function to call with (old_config, new_config)
        """
        self.change_callbacks.append(callback)
        logger.debug(f"Added configuration change callback: {callback.__name__}")

    def remove_change_callback(self, callback: Callable[[WikiConfig, WikiConfig], None]) -> None:
        """Remove a configuration change callback"""
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
            logger.debug(f"Removed configuration change callback: {callback.__name__}")

    async def update_config(self, new_config: WikiConfig, validate_urls: bool = True) -> ValidationResult:
        """
        Update configuration programmatically
        
        Args:
            new_config: New configuration to apply
            validate_urls: Whether to validate URL accessibility
            
        Returns:
            ValidationResult indicating success/failure
        """
        logger.info("Updating configuration programmatically")

        # Validate new configuration
        validation_result = await self.validator.validate_config(
            new_config, check_urls=validate_urls
        )

        if not validation_result.is_valid:
            logger.error(f"New configuration is invalid: {validation_result.errors}")
            return validation_result

        # Store old config for callbacks
        old_config = self.current_config

        # Save new configuration to file
        await ConfigurationManager.save_config(new_config, str(self.config_file))

        # Update current configuration
        self.current_config = new_config
        self.last_validation_result = validation_result

        logger.info("Configuration updated successfully")

        # Notify callbacks
        await self._notify_change_callbacks(old_config, new_config)

        return validation_result

    async def add_urls(self, url_type: str, urls: List[str], validate_urls: bool = True) -> ValidationResult:
        """
        Add new URLs to configuration
        
        Args:
            url_type: Type of URLs ('genre_pages', 'meta_tag_pages', 'tip_pages')
            urls: List of URLs to add
            validate_urls: Whether to validate URL accessibility
            
        Returns:
            ValidationResult indicating success/failure
        """
        if not self.current_config:
            raise RuntimeError("Configuration not initialized")

        # Validate URL type
        if url_type not in ['genre_pages', 'meta_tag_pages', 'tip_pages']:
            result = ValidationResult()
            result.add_error(f"Invalid URL type: {url_type}")
            return result

        # Validate new URLs if requested
        if validate_urls:
            url_validation = await self.validator.validate_new_urls(urls)
            invalid_urls = [url for url, valid in url_validation.items() if not valid]

            if invalid_urls:
                result = ValidationResult()
                for url in invalid_urls:
                    result.add_error(f"Invalid or inaccessible URL: {url}")
                return result

        # Create new configuration with added URLs
        config_dict = asdict(self.current_config)
        current_urls = config_dict[url_type]

        # Add new URLs (avoid duplicates)
        for url in urls:
            if url not in current_urls:
                current_urls.append(url)

        new_config = WikiConfig.from_dict(config_dict)

        # Update configuration
        return await self.update_config(new_config, validate_urls=False)

    async def remove_urls(self, url_type: str, urls: List[str]) -> ValidationResult:
        """
        Remove URLs from configuration
        
        Args:
            url_type: Type of URLs ('genre_pages', 'meta_tag_pages', 'tip_pages')
            urls: List of URLs to remove
            
        Returns:
            ValidationResult indicating success/failure
        """
        if not self.current_config:
            raise RuntimeError("Configuration not initialized")

        # Validate URL type
        if url_type not in ['genre_pages', 'meta_tag_pages', 'tip_pages']:
            result = ValidationResult()
            result.add_error(f"Invalid URL type: {url_type}")
            return result

        # Create new configuration with removed URLs
        config_dict = asdict(self.current_config)
        current_urls = config_dict[url_type]

        # Remove URLs
        for url in urls:
            if url in current_urls:
                current_urls.remove(url)

        new_config = WikiConfig.from_dict(config_dict)

        # Update configuration
        return await self.update_config(new_config, validate_urls=False)

    async def update_settings(self, **settings) -> ValidationResult:
        """
        Update specific configuration settings
        
        Args:
            **settings: Settings to update (e.g., refresh_interval_hours=48)
            
        Returns:
            ValidationResult indicating success/failure
        """
        if not self.current_config:
            raise RuntimeError("Configuration not initialized")

        # Create new configuration with updated settings
        config_dict = asdict(self.current_config)

        # Update provided settings
        for key, value in settings.items():
            if key in config_dict:
                config_dict[key] = value
            else:
                result = ValidationResult()
                result.add_error(f"Unknown configuration setting: {key}")
                return result

        new_config = WikiConfig.from_dict(config_dict)

        # Update configuration
        return await self.update_config(new_config, validate_urls=False)

    def get_current_config(self) -> Optional[WikiConfig]:
        """Get the current configuration"""
        return self.current_config

    def get_last_validation_result(self) -> Optional[ValidationResult]:
        """Get the last validation result"""
        return self.last_validation_result

    def is_watching(self) -> bool:
        """Check if file watching is active"""
        return self.watching

    async def reload_config(self) -> ValidationResult:
        """
        Manually reload configuration from file
        
        Returns:
            ValidationResult indicating success/failure
        """
        await self._handle_config_change()
        return self.last_validation_result or ValidationResult()

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        self.start_watching()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self.stop_watching()


# Convenience functions for common operations

async def create_dynamic_config_manager(config_path: Optional[str] = None) -> DynamicConfigManager:
    """Create and initialize a dynamic configuration manager"""
    manager = DynamicConfigManager(config_path)
    await manager.initialize()
    return manager


async def update_wiki_config_runtime(
    config_path: Optional[str] = None,
    **settings
) -> ValidationResult:
    """Update wiki configuration at runtime"""
    manager = DynamicConfigManager(config_path)
    await manager.initialize()
    return await manager.update_settings(**settings)


async def add_wiki_urls_runtime(
    url_type: str,
    urls: List[str],
    config_path: Optional[str] = None,
    validate_urls: bool = True
) -> ValidationResult:
    """Add URLs to wiki configuration at runtime"""
    manager = DynamicConfigManager(config_path)
    await manager.initialize()
    return await manager.add_urls(url_type, urls, validate_urls)
