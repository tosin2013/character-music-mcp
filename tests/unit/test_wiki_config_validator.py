"""
Tests for wiki configuration validation system.
"""

import pytest
import tempfile
import asyncio
import aiofiles
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
import aiohttp

from wiki_config_validator import (
    WikiConfigValidator, ValidationResult, 
    validate_config_quick, validate_config_full,
    validate_storage_only, check_urls_accessibility
)
from wiki_data_system import WikiConfig


class TestValidationResult:
    """Test ValidationResult class"""
    
    def test_initialization(self):
        """Test ValidationResult initialization"""
        result = ValidationResult()
        assert result.is_valid == True
        assert result.errors == []
        assert result.warnings == []
        assert result.url_checks == {}
        assert result.storage_info == {}
    
    def test_add_error(self):
        """Test adding errors"""
        result = ValidationResult()
        result.add_error("Test error")
        
        assert result.is_valid == False
        assert "Test error" in result.errors
    
    def test_add_warning(self):
        """Test adding warnings"""
        result = ValidationResult()
        result.add_warning("Test warning")
        
        assert result.is_valid == True  # Warnings don't affect validity
        assert "Test warning" in result.warnings
    
    def test_to_dict(self):
        """Test dictionary conversion"""
        result = ValidationResult()
        result.add_error("Error")
        result.add_warning("Warning")
        result.url_checks["http://test.com"] = True
        result.storage_info["writable"] = True
        
        data = result.to_dict()
        assert data['is_valid'] == False
        assert data['errors'] == ["Error"]
        assert data['warnings'] == ["Warning"]
        assert data['url_checks'] == {"http://test.com": True}
        assert data['storage_info'] == {"writable": True}


class TestWikiConfigValidator:
    """Test WikiConfigValidator class"""
    
    def test_initialization(self):
        """Test validator initialization"""
        validator = WikiConfigValidator()
        assert validator.timeout == 10
        
        validator = WikiConfigValidator(timeout=30)
        assert validator.timeout == 30
    
    def test_url_format_validation(self):
        """Test URL format validation"""
        validator = WikiConfigValidator()
        
        # Valid URLs
        assert validator._is_valid_url_format("https://example.com") == True
        assert validator._is_valid_url_format("http://test.org/path") == True
        
        # Invalid URLs
        assert validator._is_valid_url_format("not-a-url") == False
        assert validator._is_valid_url_format("ftp://example.com") == False
        assert validator._is_valid_url_format("") == False
        assert validator._is_valid_url_format("https://") == False
    
    def test_basic_parameter_validation(self):
        """Test basic parameter validation"""
        validator = WikiConfigValidator()
        
        # Valid config
        config = WikiConfig()
        result = ValidationResult()
        validator._validate_basic_parameters(config, result)
        assert result.is_valid == True
        
        # Invalid refresh interval
        config = WikiConfig(refresh_interval_hours=0)
        result = ValidationResult()
        validator._validate_basic_parameters(config, result)
        assert result.is_valid == False
        assert any("refresh_interval_hours" in error for error in result.errors)
        
        # Invalid timeout
        config = WikiConfig(request_timeout=0)
        result = ValidationResult()
        validator._validate_basic_parameters(config, result)
        assert result.is_valid == False
        assert any("request_timeout" in error for error in result.errors)
        
        # Invalid retries
        config = WikiConfig(max_retries=-1)
        result = ValidationResult()
        validator._validate_basic_parameters(config, result)
        assert result.is_valid == False
        assert any("max_retries" in error for error in result.errors)
        
        # Invalid retry delay
        config = WikiConfig(retry_delay=-1)
        result = ValidationResult()
        validator._validate_basic_parameters(config, result)
        assert result.is_valid == False
        assert any("retry_delay" in error for error in result.errors)
    
    def test_basic_parameter_warnings(self):
        """Test basic parameter warnings"""
        validator = WikiConfigValidator()
        
        # Large refresh interval
        config = WikiConfig(refresh_interval_hours=10000)
        result = ValidationResult()
        validator._validate_basic_parameters(config, result)
        assert result.is_valid == True
        assert any("very large" in warning for warning in result.warnings)
        
        # Large timeout
        config = WikiConfig(request_timeout=400)
        result = ValidationResult()
        validator._validate_basic_parameters(config, result)
        assert result.is_valid == True
        assert any("very large" in warning for warning in result.warnings)
        
        # High retries
        config = WikiConfig(max_retries=15)
        result = ValidationResult()
        validator._validate_basic_parameters(config, result)
        assert result.is_valid == True
        assert any("very high" in warning for warning in result.warnings)
        
        # Large retry delay
        config = WikiConfig(retry_delay=100)
        result = ValidationResult()
        validator._validate_basic_parameters(config, result)
        assert result.is_valid == True
        assert any("very large" in warning for warning in result.warnings)
    
    def test_empty_page_lists_warning(self):
        """Test warning for empty page lists"""
        validator = WikiConfigValidator()
        
        config = WikiConfig(
            genre_pages=[],
            meta_tag_pages=[],
            tip_pages=[]
        )
        result = ValidationResult()
        validator._validate_basic_parameters(config, result)
        
        assert result.is_valid == True
        assert any("No wiki pages configured" in warning for warning in result.warnings)
    
    def test_duplicate_urls_warning(self):
        """Test warning for duplicate URLs"""
        validator = WikiConfigValidator()
        
        duplicate_url = "https://example.com"
        config = WikiConfig(
            genre_pages=[duplicate_url],
            meta_tag_pages=[duplicate_url],
            tip_pages=[]
        )
        result = ValidationResult()
        validator._validate_basic_parameters(config, result)
        
        assert result.is_valid == True
        assert any("Duplicate URLs" in warning for warning in result.warnings)
    
    @pytest.mark.asyncio
    async def test_storage_validation_success(self):
        """Test successful storage validation"""
        validator = WikiConfigValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = WikiConfig(local_storage_path=temp_dir)
            result = ValidationResult()
            
            await validator._validate_storage(config, result)
            
            assert result.is_valid == True
            assert result.storage_info['writable'] == True
            assert 'available_space_gb' in result.storage_info
    
    @pytest.mark.asyncio
    async def test_storage_validation_empty_path(self):
        """Test storage validation with empty path"""
        validator = WikiConfigValidator()
        
        config = WikiConfig(local_storage_path="")
        result = ValidationResult()
        
        await validator._validate_storage(config, result)
        
        assert result.is_valid == False
        assert any("cannot be empty" in error for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_storage_validation_create_directory(self):
        """Test storage validation with directory creation"""
        validator = WikiConfigValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "new_wiki_storage"
            config = WikiConfig(local_storage_path=str(new_dir))
            result = ValidationResult()
            
            await validator._validate_storage(config, result)
            
            assert result.is_valid == True
            assert result.storage_info['path_created'] == True
            assert new_dir.exists()
    
    @pytest.mark.asyncio
    async def test_storage_validation_permission_error(self):
        """Test storage validation with permission error"""
        validator = WikiConfigValidator()
        
        # Try to use a path that should cause permission error
        config = WikiConfig(local_storage_path="/root/wiki_storage")
        result = ValidationResult()
        
        await validator._validate_storage(config, result)
        
        # Should either succeed (if running as root) or fail with permission error
        if not result.is_valid:
            assert any("Permission denied" in error or "Cannot create" in error 
                      for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_storage_validation_relative_path_warning(self):
        """Test warning for relative storage path"""
        validator = WikiConfigValidator()
        
        config = WikiConfig(local_storage_path="./relative/path")
        result = ValidationResult()
        
        await validator._validate_storage(config, result)
        
        # Should have warning about relative path
        assert any("relative path" in warning for warning in result.warnings)
    
    def test_url_format_validation_only(self):
        """Test URL format validation without network checks"""
        validator = WikiConfigValidator()
        
        config = WikiConfig(
            genre_pages=["https://valid.com", "invalid-url"],
            meta_tag_pages=["https://another-valid.com"],
            tip_pages=[]
        )
        result = ValidationResult()
        
        validator._validate_url_format(config, result)
        
        assert result.is_valid == False
        assert any("Invalid URL format: invalid-url" in error for error in result.errors)
        assert result.url_checks["https://valid.com"] is None
        assert result.url_checks["https://another-valid.com"] is None
    
    @pytest.mark.asyncio
    async def test_url_accessibility_check_success(self):
        """Test successful URL accessibility check"""
        validator = WikiConfigValidator()
        
        # Mock the _check_url_accessibility method directly
        with patch.object(validator, '_check_url_accessibility') as mock_check:
            mock_check.return_value = (True, 200, None)
            
            accessible, status_code, error = await validator._check_url_accessibility("https://example.com")
            
            assert accessible == True
            assert status_code == 200
            assert error is None
    
    @pytest.mark.asyncio
    async def test_url_accessibility_check_failure(self):
        """Test failed URL accessibility check"""
        validator = WikiConfigValidator()
        
        # Mock the _check_url_accessibility method directly
        with patch.object(validator, '_check_url_accessibility') as mock_check:
            mock_check.return_value = (False, 404, None)
            
            accessible, status_code, error = await validator._check_url_accessibility("https://example.com")
            
            assert accessible == False
            assert status_code == 404
            assert error is None
    
    @pytest.mark.asyncio
    async def test_url_accessibility_check_exception(self):
        """Test URL accessibility check with exception"""
        validator = WikiConfigValidator()
        
        # Mock the _check_url_accessibility method directly
        with patch.object(validator, '_check_url_accessibility') as mock_check:
            mock_check.return_value = (False, None, "Network error")
            
            accessible, status_code, error = await validator._check_url_accessibility("https://example.com")
            
            assert accessible == False
            assert status_code is None
            assert "Network error" in error
    
    @pytest.mark.asyncio
    async def test_validate_new_urls(self):
        """Test validation of new URLs"""
        validator = WikiConfigValidator()
        
        urls = [
            "https://valid.com",
            "invalid-url",
            "https://another-valid.com"
        ]
        
        # Mock the _check_url_accessibility method
        with patch.object(validator, '_check_url_accessibility') as mock_check:
            mock_check.return_value = (True, 200, None)
            
            results = await validator.validate_new_urls(urls)
            
            assert results["https://valid.com"] == True
            assert results["invalid-url"] == False  # Invalid format
            assert results["https://another-valid.com"] == True
    
    @pytest.mark.asyncio
    async def test_full_config_validation(self):
        """Test full configuration validation"""
        validator = WikiConfigValidator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = WikiConfig(local_storage_path=temp_dir)
            
            # Mock URL accessibility checks
            with patch.object(validator, '_check_url_accessibility') as mock_check:
                mock_check.return_value = (True, 200, None)
                
                result = await validator.validate_config(config, check_urls=True)
                
                assert result.is_valid == True
                assert result.storage_info['writable'] == True
                # Should have checked all URLs
                all_urls = config.genre_pages + config.meta_tag_pages + config.tip_pages
                for url in all_urls:
                    assert url in result.url_checks
                    assert result.url_checks[url] == True


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    @pytest.mark.asyncio
    async def test_validate_config_quick(self):
        """Test quick validation function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = WikiConfig(local_storage_path=temp_dir)
            result = await validate_config_quick(config)
            
            assert isinstance(result, ValidationResult)
            # Should not have checked URL accessibility
            for url_status in result.url_checks.values():
                assert url_status is None
    
    @pytest.mark.asyncio
    async def test_validate_config_full(self):
        """Test full validation function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = WikiConfig(local_storage_path=temp_dir)
            
            # Mock URL checks
            with patch('wiki_config_validator.WikiConfigValidator._check_url_accessibility') as mock_check:
                mock_check.return_value = (True, 200, None)
                
                result = await validate_config_full(config, timeout=5)
                
                assert isinstance(result, ValidationResult)
                # Should have checked URL accessibility
                for url_status in result.url_checks.values():
                    assert url_status == True
    
    @pytest.mark.asyncio
    async def test_validate_storage_only(self):
        """Test storage-only validation function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = WikiConfig(local_storage_path=temp_dir)
            result = await validate_storage_only(config)
            
            assert isinstance(result, ValidationResult)
            assert result.storage_info['writable'] == True
            assert result.url_checks == {}  # No URL checks
    
    @pytest.mark.asyncio
    async def test_check_urls_accessibility(self):
        """Test URL accessibility checking function"""
        urls = ["https://example.com", "https://test.org"]
        
        # Mock the WikiConfigValidator._check_url_accessibility method
        with patch('wiki_config_validator.WikiConfigValidator._check_url_accessibility') as mock_check:
            mock_check.return_value = (True, 200, None)
            
            results = await check_urls_accessibility(urls, timeout=5)
            
            assert isinstance(results, dict)
            assert results["https://example.com"] == True
            assert results["https://test.org"] == True


if __name__ == "__main__":
    pytest.main([__file__])