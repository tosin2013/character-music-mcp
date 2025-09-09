"""Unit tests for configuration management"""

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from character_music_mcp.config import (
    AgentConfig,
    DaggerConfig,
    DeepSeekConfig,
    GitHubConfig,
    create_default_config_file,
    get_config,
)


class TestDeepSeekConfig:
    """Test DeepSeekConfig class"""

    def test_from_env_with_all_values(self):
        """Test creating DeepSeekConfig from environment variables"""
        env_vars = {
            "DEEPSEEK_API_KEY": "test-api-key",
            "DEEPSEEK_MODEL": "deepseek-coder-v2",
            "DEEPSEEK_MAX_TOKENS": "8000",
            "DEEPSEEK_TEMPERATURE": "0.2",
            "DEEPSEEK_RATE_LIMIT": "120",
            "DEEPSEEK_TIMEOUT": "60"
        }

        with patch.dict(os.environ, env_vars):
            config = DeepSeekConfig.from_env()

        assert config.api_key == "test-api-key"
        assert config.model == "deepseek-coder-v2"
        assert config.max_tokens == 8000
        assert config.temperature == 0.2
        assert config.rate_limit == 120
        assert config.timeout == 60

    def test_from_env_with_defaults(self):
        """Test creating DeepSeekConfig with default values"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            config = DeepSeekConfig.from_env()

        assert config.api_key == "test-key"
        assert config.model == "deepseek-coder"
        assert config.max_tokens == 4000
        assert config.temperature == 0.1
        assert config.rate_limit == 60
        assert config.timeout == 30

    def test_from_env_missing_api_key(self):
        """Test that missing API key raises ValueError"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="DEEPSEEK_API_KEY environment variable is required"):
                DeepSeekConfig.from_env()

    def test_validate_success(self):
        """Test successful validation"""
        config = DeepSeekConfig(
            api_key="test-key",
            model="deepseek-coder",
            max_tokens=4000,
            temperature=0.1,
            rate_limit=60,
            timeout=30
        )

        # Should not raise any exception
        config.validate()

    def test_validate_failures(self):
        """Test validation failures"""
        # Test missing API key
        config = DeepSeekConfig(api_key="")
        with pytest.raises(ValueError, match="API key is required"):
            config.validate()

        # Test invalid max_tokens
        config = DeepSeekConfig(api_key="test", max_tokens=50)
        with pytest.raises(ValueError, match="max_tokens must be between 100 and 32000"):
            config.validate()

        # Test invalid temperature
        config = DeepSeekConfig(api_key="test", temperature=3.0)
        with pytest.raises(ValueError, match="temperature must be between 0.0 and 2.0"):
            config.validate()

        # Test invalid rate_limit
        config = DeepSeekConfig(api_key="test", rate_limit=0)
        with pytest.raises(ValueError, match="rate_limit must be at least 1"):
            config.validate()

        # Test invalid timeout
        config = DeepSeekConfig(api_key="test", timeout=0)
        with pytest.raises(ValueError, match="timeout must be at least 1 second"):
            config.validate()


class TestGitHubConfig:
    """Test GitHubConfig class"""

    def test_from_env_with_all_values(self):
        """Test creating GitHubConfig from environment variables"""
        env_vars = {
            "GITHUB_TOKEN": "test-token",
            "GITHUB_APP_ID": "12345",
            "GITHUB_PRIVATE_KEY": "test-private-key",
            "GITHUB_WEBHOOK_SECRET": "test-secret",
            "GITHUB_BASE_URL": "https://github.enterprise.com/api/v3",
            "GITHUB_TIMEOUT": "60",
            "GITHUB_MAX_RETRIES": "5"
        }

        with patch.dict(os.environ, env_vars):
            config = GitHubConfig.from_env()

        assert config.token == "test-token"
        assert config.app_id == "12345"
        assert config.private_key == "test-private-key"
        assert config.webhook_secret == "test-secret"
        assert config.base_url == "https://github.enterprise.com/api/v3"
        assert config.timeout == 60
        assert config.max_retries == 5

    def test_from_env_with_defaults(self):
        """Test creating GitHubConfig with default values"""
        with patch.dict(os.environ, {}, clear=True):
            config = GitHubConfig.from_env()

        assert config.token is None
        assert config.app_id is None
        assert config.private_key is None
        assert config.webhook_secret is None
        assert config.base_url == "https://api.github.com"
        assert config.timeout == 30
        assert config.max_retries == 3

    def test_validate_with_token_auth(self):
        """Test validation with token authentication"""
        config = GitHubConfig(token="test-token")
        config.validate(require_auth=True)  # Should not raise

    def test_validate_with_app_auth(self):
        """Test validation with GitHub App authentication"""
        config = GitHubConfig(app_id="12345", private_key="test-key")
        config.validate(require_auth=True)  # Should not raise

    def test_validate_missing_auth(self):
        """Test validation failure when authentication is required but missing"""
        config = GitHubConfig()
        with pytest.raises(ValueError, match="Either token or \\(app_id and private_key\\) must be provided"):
            config.validate(require_auth=True)

    def test_validate_invalid_timeout(self):
        """Test validation failure for invalid timeout"""
        config = GitHubConfig(timeout=0)
        with pytest.raises(ValueError, match="timeout must be at least 1 second"):
            config.validate()

    def test_validate_invalid_retries(self):
        """Test validation failure for invalid max_retries"""
        config = GitHubConfig(max_retries=-1)
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            config.validate()

    def test_has_token_auth(self):
        """Test has_token_auth property"""
        config = GitHubConfig(token="test-token")
        assert config.has_token_auth is True

        config = GitHubConfig()
        assert config.has_token_auth is False

    def test_has_app_auth(self):
        """Test has_app_auth property"""
        config = GitHubConfig(app_id="12345", private_key="test-key")
        assert config.has_app_auth is True

        config = GitHubConfig(app_id="12345")  # Missing private_key
        assert config.has_app_auth is False

        config = GitHubConfig()
        assert config.has_app_auth is False


class TestDaggerConfig:
    """Test DaggerConfig class"""

    def test_from_env_with_all_values(self):
        """Test creating DaggerConfig from environment variables"""
        env_vars = {
            "DAGGER_ENGINE_VERSION": "v0.9.0",
            "DAGGER_CACHE_ENABLED": "false",
            "DAGGER_PARALLEL_EXECUTION": "false",
            "DAGGER_CONTAINER_TIMEOUT": "1200",
            "DAGGER_MAX_CONCURRENT_CONTAINERS": "10"
        }

        with patch.dict(os.environ, env_vars):
            config = DaggerConfig.from_env()

        assert config.engine_version == "v0.9.0"
        assert config.cache_enabled is False
        assert config.parallel_execution is False
        assert config.container_timeout == 1200
        assert config.max_concurrent_containers == 10

    def test_from_env_with_defaults(self):
        """Test creating DaggerConfig with default values"""
        with patch.dict(os.environ, {}, clear=True):
            config = DaggerConfig.from_env()

        assert config.engine_version == "latest"
        assert config.cache_enabled is True
        assert config.parallel_execution is True
        assert config.container_timeout == 600
        assert config.max_concurrent_containers == 5

    def test_validate_success(self):
        """Test successful validation"""
        config = DaggerConfig()
        config.validate()  # Should not raise

    def test_validate_invalid_timeout(self):
        """Test validation failure for invalid container timeout"""
        config = DaggerConfig(container_timeout=30)
        with pytest.raises(ValueError, match="container_timeout must be at least 60 seconds"):
            config.validate()

    def test_validate_invalid_concurrent_containers(self):
        """Test validation failure for invalid max_concurrent_containers"""
        config = DaggerConfig(max_concurrent_containers=0)
        with pytest.raises(ValueError, match="max_concurrent_containers must be at least 1"):
            config.validate()


class TestAgentConfig:
    """Test AgentConfig class"""

    def test_from_env_with_all_values(self):
        """Test creating AgentConfig from environment variables"""
        env_vars = {
            "DEEPSEEK_API_KEY": "test-api-key",
            "DEEPSEEK_MODEL": "deepseek-coder-v2",
            "GITHUB_TOKEN": "test-token",
            "ENABLED_FIX_TYPES": "syntax_fix,import_fix,test_fix,coverage_fix",
            "PYTHON_VERSIONS": "3.9,3.10,3.11",
            "MAX_CONCURRENT_FIXES": "5",
            "COVERAGE_THRESHOLD": "85.0",
            "FILE_PATTERNS_INCLUDE": "*.py,*.pyi,pyproject.toml",
            "FILE_PATTERNS_EXCLUDE": "__pycache__/*,*.pyc,.git/*",
            "LOG_LEVEL": "DEBUG",
            "LOG_FORMAT": "text",
            "DRY_RUN": "true",
            "CREATE_ISSUES_ON_FAILURE": "false",
            "AUTO_MERGE_SAFE_FIXES": "true"
        }

        with patch.dict(os.environ, env_vars):
            config = AgentConfig.from_env()

        assert config.deepseek_config.api_key == "test-api-key"
        assert config.deepseek_config.model == "deepseek-coder-v2"
        assert config.github_config.token == "test-token"
        assert config.enabled_fix_types == ["syntax_fix", "import_fix", "test_fix", "coverage_fix"]
        assert config.python_versions == ["3.9", "3.10", "3.11"]
        assert config.max_concurrent_fixes == 5
        assert config.coverage_threshold == 85.0
        assert config.file_patterns["include"] == ["*.py", "*.pyi", "pyproject.toml"]
        assert config.file_patterns["exclude"] == ["__pycache__/*", "*.pyc", ".git/*"]
        assert config.log_level == "DEBUG"
        assert config.log_format == "text"
        assert config.dry_run is True
        assert config.create_issues_on_failure is False
        assert config.auto_merge_safe_fixes is True

    def test_from_env_with_defaults(self):
        """Test creating AgentConfig with default values"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            config = AgentConfig.from_env()

        assert config.enabled_fix_types == ["syntax_fix", "import_fix", "quality_fix"]
        assert config.python_versions == ["3.10", "3.11", "3.12"]
        assert config.max_concurrent_fixes == 3
        assert config.coverage_threshold == 80.0
        assert config.log_level == "INFO"
        assert config.log_format == "json"
        assert config.dry_run is False
        assert config.create_issues_on_failure is True
        assert config.auto_merge_safe_fixes is False

    def test_from_file_success(self):
        """Test loading configuration from file"""
        config_data = {
            "deepseek": {
                "api_key": "file-api-key",
                "model": "deepseek-coder-v2",
                "max_tokens": 8000
            },
            "github": {
                "token": "file-token"
            },
            "dagger": {
                "engine_version": "v0.9.0"
            },
            "enabled_fix_types": ["syntax_fix", "import_fix"],
            "python_versions": ["3.11", "3.12"],
            "max_concurrent_fixes": 2,
            "coverage_threshold": 90.0
        }

        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            with open(config_path, 'w') as f:
                json.dump(config_data, f)

            config = AgentConfig.from_file(config_path)

        assert config.deepseek_config.api_key == "file-api-key"
        assert config.deepseek_config.model == "deepseek-coder-v2"
        assert config.deepseek_config.max_tokens == 8000
        assert config.github_config.token == "file-token"
        assert config.dagger_config.engine_version == "v0.9.0"
        assert config.enabled_fix_types == ["syntax_fix", "import_fix"]
        assert config.python_versions == ["3.11", "3.12"]
        assert config.max_concurrent_fixes == 2
        assert config.coverage_threshold == 90.0

    def test_from_file_not_found(self):
        """Test loading configuration from non-existent file"""
        with pytest.raises(FileNotFoundError):
            AgentConfig.from_file(Path("/non/existent/config.json"))

    def test_validate_success(self):
        """Test successful validation"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            config = AgentConfig.from_env()
            config.validate()  # Should not raise

    def test_validate_invalid_coverage_threshold(self):
        """Test validation failure for invalid coverage threshold"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            config = AgentConfig.from_env()
            config.coverage_threshold = 150.0

            with pytest.raises(ValueError, match="coverage_threshold must be between 0 and 100"):
                config.validate()

    def test_validate_invalid_max_concurrent_fixes(self):
        """Test validation failure for invalid max_concurrent_fixes"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            config = AgentConfig.from_env()
            config.max_concurrent_fixes = 0

            with pytest.raises(ValueError, match="max_concurrent_fixes must be at least 1"):
                config.validate()

    def test_validate_empty_fix_types(self):
        """Test validation failure for empty enabled_fix_types"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            config = AgentConfig.from_env()
            config.enabled_fix_types = []

            with pytest.raises(ValueError, match="at least one fix type must be enabled"):
                config.validate()

    def test_validate_empty_python_versions(self):
        """Test validation failure for empty python_versions"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            config = AgentConfig.from_env()
            config.python_versions = []

            with pytest.raises(ValueError, match="at least one Python version must be specified"):
                config.validate()

    def test_validate_invalid_python_version(self):
        """Test validation failure for invalid Python version format"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            config = AgentConfig.from_env()
            config.python_versions = ["3.10", "invalid-version"]

            with pytest.raises(ValueError, match="invalid Python version format: invalid-version"):
                config.validate()

    def test_validate_invalid_log_level(self):
        """Test validation failure for invalid log level"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            config = AgentConfig.from_env()
            config.log_level = "INVALID"

            with pytest.raises(ValueError, match="log_level must be one of"):
                config.validate()

    def test_to_dict(self):
        """Test converting configuration to dictionary"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key", "GITHUB_TOKEN": "test-token"}, clear=True):
            config = AgentConfig.from_env()
            config_dict = config.to_dict()

        assert config_dict["deepseek"]["api_key"] == "***"  # Masked
        assert config_dict["deepseek"]["model"] == "deepseek-coder"
        assert config_dict["github"]["token"] == "***"  # Masked
        assert config_dict["enabled_fix_types"] == ["syntax_fix", "import_fix", "quality_fix"]
        assert config_dict["python_versions"] == ["3.10", "3.11", "3.12"]

    def test_save_to_file(self):
        """Test saving configuration to file"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            config = AgentConfig.from_env()

        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "subdir" / "config.json"
            config.save_to_file(config_path)

            assert config_path.exists()

            with open(config_path) as f:
                saved_data = json.load(f)

            assert saved_data["deepseek"]["api_key"] == "***"  # Masked
            assert saved_data["deepseek"]["model"] == "deepseek-coder"


class TestUtilityFunctions:
    """Test utility functions"""

    def test_get_config_from_env(self):
        """Test get_config function with environment variables"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            config = get_config()
            assert config.deepseek_config.api_key == "test-key"

    def test_get_config_from_file(self):
        """Test get_config function with configuration file"""
        config_data = {
            "deepseek": {"api_key": "file-key"},
            "github": {},
            "dagger": {}
        }

        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            with open(config_path, 'w') as f:
                json.dump(config_data, f)

            config = get_config(config_file=config_path)
            assert config.deepseek_config.api_key == "file-key"

    def test_get_config_validation_error(self):
        """Test get_config function with validation error"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                get_config()

    def test_create_default_config_file(self):
        """Test creating default configuration file"""
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "subdir" / "config.json"
            create_default_config_file(config_path)

            assert config_path.exists()

            with open(config_path) as f:
                config_data = json.load(f)

            assert config_data["deepseek"]["api_key"] == "${DEEPSEEK_API_KEY}"
            assert config_data["github"]["token"] == "${GITHUB_TOKEN}"
            assert config_data["enabled_fix_types"] == ["syntax_fix", "import_fix", "quality_fix"]
            assert config_data["python_versions"] == ["3.10", "3.11", "3.12"]


class TestConfigIntegration:
    """Integration tests for configuration system"""

    def test_full_configuration_cycle(self):
        """Test complete configuration lifecycle"""
        # Create configuration from environment
        env_vars = {
            "DEEPSEEK_API_KEY": "test-api-key",
            "GITHUB_TOKEN": "test-token",
            "ENABLED_FIX_TYPES": "syntax_fix,import_fix",
            "PYTHON_VERSIONS": "3.11,3.12",
            "MAX_CONCURRENT_FIXES": "2",
            "COVERAGE_THRESHOLD": "85.0"
        }

        with patch.dict(os.environ, env_vars):
            config = AgentConfig.from_env()

        # Validate configuration
        config.validate(require_github_auth=True)

        # Save to file
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config.save_to_file(config_path)

            # Load from file
            loaded_config = AgentConfig.from_file(config_path)

            # Validate loaded configuration
            loaded_config.validate(require_github_auth=True)

            # Compare key values (note: sensitive data is masked in saved file)
            assert loaded_config.enabled_fix_types == config.enabled_fix_types
            assert loaded_config.python_versions == config.python_versions
            assert loaded_config.max_concurrent_fixes == config.max_concurrent_fixes
            assert loaded_config.coverage_threshold == config.coverage_threshold

    def test_configuration_with_missing_optional_auth(self):
        """Test configuration without GitHub authentication"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            config = AgentConfig.from_env()

            # Should validate without requiring GitHub auth
            config.validate(require_github_auth=False)

            # Should fail when GitHub auth is required
            with pytest.raises(ValueError):
                config.validate(require_github_auth=True)
