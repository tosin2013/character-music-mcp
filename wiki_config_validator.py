"""
Configuration validation system for wiki data integration.

This module provides comprehensive validation for WikiConfig including:
- URL accessibility validation
- Local storage permissions and space checks
- Configuration parameter validation
- Network connectivity testing
"""

import asyncio
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import aiofiles
import aiohttp

from wiki_data_system import WikiConfig

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of configuration validation"""

    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.url_checks: Dict[str, bool] = {}
        self.storage_info: Dict[str, Any] = {}

    def add_error(self, message: str) -> None:
        """Add validation error"""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add validation warning"""
        self.warnings.append(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'url_checks': self.url_checks,
            'storage_info': self.storage_info
        }


class WikiConfigValidator:
    """Comprehensive configuration validator for wiki data integration"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    async def validate_config(self, config: WikiConfig, check_urls: bool = True) -> ValidationResult:
        """
        Perform comprehensive configuration validation
        
        Args:
            config: WikiConfig to validate
            check_urls: Whether to perform network checks on URLs
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult()

        # Basic parameter validation
        self._validate_basic_parameters(config, result)

        # Storage validation
        await self._validate_storage(config, result)

        # URL validation
        if check_urls:
            await self._validate_urls(config, result)
        else:
            self._validate_url_format(config, result)

        return result

    def _validate_basic_parameters(self, config: WikiConfig, result: ValidationResult) -> None:
        """Validate basic configuration parameters"""

        # Validate refresh interval
        if config.refresh_interval_hours < 1:
            result.add_error("refresh_interval_hours must be at least 1")
        elif config.refresh_interval_hours > 8760:  # 1 year
            result.add_warning("refresh_interval_hours is very large (>1 year)")

        # Validate request timeout
        if config.request_timeout < 1:
            result.add_error("request_timeout must be at least 1 second")
        elif config.request_timeout > 300:  # 5 minutes
            result.add_warning("request_timeout is very large (>5 minutes)")

        # Validate retry settings
        if config.max_retries < 0:
            result.add_error("max_retries cannot be negative")
        elif config.max_retries > 10:
            result.add_warning("max_retries is very high (>10)")

        if config.retry_delay < 0:
            result.add_error("retry_delay cannot be negative")
        elif config.retry_delay > 60:
            result.add_warning("retry_delay is very large (>60 seconds)")

        # Validate page lists
        if not config.genre_pages and not config.meta_tag_pages and not config.tip_pages:
            result.add_warning("No wiki pages configured - system will only use hardcoded data")

        # Check for duplicate URLs
        all_urls = config.genre_pages + config.meta_tag_pages + config.tip_pages
        unique_urls = set(all_urls)
        if len(all_urls) != len(unique_urls):
            result.add_warning("Duplicate URLs found in configuration")

    async def _validate_storage(self, config: WikiConfig, result: ValidationResult) -> None:
        """Validate local storage configuration"""

        if not config.local_storage_path:
            result.add_error("local_storage_path cannot be empty")
            return

        storage_path = Path(config.local_storage_path)

        try:
            # Check if path exists or can be created
            if not storage_path.exists():
                try:
                    storage_path.mkdir(parents=True, exist_ok=True)
                    result.storage_info['path_created'] = True
                except PermissionError:
                    result.add_error(f"Cannot create storage directory: {storage_path} (Permission denied)")
                    return
                except Exception as e:
                    result.add_error(f"Cannot create storage directory: {storage_path} ({e})")
                    return

            # Check write permissions
            test_file = storage_path / ".write_test"
            try:
                async with aiofiles.open(test_file, 'w') as f:
                    await f.write("test")
                test_file.unlink()  # Clean up
                result.storage_info['writable'] = True
            except PermissionError:
                result.add_error(f"No write permission for storage directory: {storage_path}")
                return
            except Exception as e:
                result.add_error(f"Cannot write to storage directory: {storage_path} ({e})")
                return

            # Check available space
            try:
                stat = shutil.disk_usage(storage_path)
                available_gb = stat.free / (1024**3)
                result.storage_info['available_space_gb'] = round(available_gb, 2)

                if available_gb < 0.1:  # Less than 100MB
                    result.add_error(f"Insufficient disk space: {available_gb:.2f}GB available")
                elif available_gb < 1.0:  # Less than 1GB
                    result.add_warning(f"Low disk space: {available_gb:.2f}GB available")

            except Exception as e:
                result.add_warning(f"Could not check disk space: {e}")

            # Check if path is absolute or relative
            if not storage_path.is_absolute():
                result.add_warning("Using relative path for storage - consider using absolute path")

        except Exception as e:
            result.add_error(f"Storage validation failed: {e}")

    def _validate_url_format(self, config: WikiConfig, result: ValidationResult) -> None:
        """Validate URL formats without network checks"""

        all_urls = config.genre_pages + config.meta_tag_pages + config.tip_pages

        for url in all_urls:
            if not self._is_valid_url_format(url):
                result.add_error(f"Invalid URL format: {url}")
            else:
                result.url_checks[url] = None  # Format valid, accessibility unknown

    async def _validate_urls(self, config: WikiConfig, result: ValidationResult) -> None:
        """Validate URL accessibility with network checks"""

        all_urls = config.genre_pages + config.meta_tag_pages + config.tip_pages

        if not all_urls:
            return

        # Check URLs concurrently
        tasks = []
        for url in all_urls:
            if self._is_valid_url_format(url):
                tasks.append(self._check_url_accessibility(url))
            else:
                result.add_error(f"Invalid URL format: {url}")
                result.url_checks[url] = False

        if tasks:
            url_results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, url_result in enumerate(url_results):
                url = all_urls[i] if i < len(all_urls) else "unknown"

                if isinstance(url_result, Exception):
                    result.add_warning(f"Could not check URL accessibility: {url} ({url_result})")
                    result.url_checks[url] = False
                else:
                    accessible, status_code, error = url_result
                    result.url_checks[url] = accessible

                    if not accessible:
                        if status_code:
                            result.add_warning(f"URL not accessible: {url} (HTTP {status_code})")
                        else:
                            result.add_warning(f"URL not accessible: {url} ({error})")

    def _is_valid_url_format(self, url: str) -> bool:
        """Check if URL format is valid"""
        try:
            parsed = urlparse(url)
            return all([
                parsed.scheme in ('http', 'https'),
                parsed.netloc,
                len(url.strip()) > 0
            ])
        except Exception:
            return False

    async def _check_url_accessibility(self, url: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Check if URL is accessible
        
        Returns:
            Tuple of (accessible, status_code, error_message)
        """
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.head(url) as response:
                    accessible = response.status < 400
                    return accessible, response.status, None

        except aiohttp.ClientError as e:
            return False, None, str(e)
        except asyncio.TimeoutError:
            return False, None, "Request timeout"
        except Exception as e:
            return False, None, str(e)

    async def validate_new_urls(self, urls: List[str]) -> Dict[str, bool]:
        """
        Validate a list of new URLs for accessibility
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            Dictionary mapping URLs to accessibility status
        """
        results = {}

        tasks = []
        valid_urls = []

        for url in urls:
            if self._is_valid_url_format(url):
                tasks.append(self._check_url_accessibility(url))
                valid_urls.append(url)
            else:
                results[url] = False

        if tasks:
            url_results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, url_result in enumerate(url_results):
                url = valid_urls[i]

                if isinstance(url_result, Exception):
                    results[url] = False
                else:
                    accessible, _, _ = url_result
                    results[url] = accessible

        return results


# Convenience functions for common validation scenarios

async def validate_config_quick(config: WikiConfig) -> ValidationResult:
    """Quick validation without network checks"""
    validator = WikiConfigValidator()
    return await validator.validate_config(config, check_urls=False)


async def validate_config_full(config: WikiConfig, timeout: int = 10) -> ValidationResult:
    """Full validation including network checks"""
    validator = WikiConfigValidator(timeout=timeout)
    return await validator.validate_config(config, check_urls=True)


async def validate_storage_only(config: WikiConfig) -> ValidationResult:
    """Validate only storage-related configuration"""
    validator = WikiConfigValidator()
    result = ValidationResult()
    await validator._validate_storage(config, result)
    return result


async def check_urls_accessibility(urls: List[str], timeout: int = 10) -> Dict[str, bool]:
    """Check accessibility of a list of URLs"""
    validator = WikiConfigValidator(timeout=timeout)
    return await validator.validate_new_urls(urls)
