"""Configuration management for the Dagger Test Repair Agent"""

import os
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


@dataclass
class DeepSeekConfig:
    """Configuration for DeepSeek API integration"""
    
    api_key: str
    model: str = "deepseek-coder"
    max_tokens: int = 4000
    temperature: float = 0.1
    rate_limit: int = 60  # requests per minute
    timeout: int = 30  # seconds
    
    @classmethod
    def from_env(cls) -> "DeepSeekConfig":
        """Create DeepSeekConfig from environment variables"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is required")
        
        return cls(
            api_key=api_key,
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-coder"),
            max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", "0.1")),
            rate_limit=int(os.getenv("DEEPSEEK_RATE_LIMIT", "60")),
            timeout=int(os.getenv("DEEPSEEK_TIMEOUT", "30"))
        )
    
    def validate(self) -> None:
        """Validate DeepSeek configuration"""
        errors = []
        
        if not self.api_key:
            errors.append("API key is required")
        
        if self.max_tokens < 100 or self.max_tokens > 32000:
            errors.append("max_tokens must be between 100 and 32000")
        
        if self.temperature < 0.0 or self.temperature > 2.0:
            errors.append("temperature must be between 0.0 and 2.0")
        
        if self.rate_limit < 1:
            errors.append("rate_limit must be at least 1")
        
        if self.timeout < 1:
            errors.append("timeout must be at least 1 second")
        
        if errors:
            raise ValueError(f"DeepSeek configuration validation failed: {'; '.join(errors)}")


@dataclass
class GitHubConfig:
    """Configuration for GitHub integration"""
    
    token: Optional[str] = None
    app_id: Optional[str] = None
    private_key: Optional[str] = None
    webhook_secret: Optional[str] = None
    base_url: str = "https://api.github.com"
    timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> "GitHubConfig":
        """Create GitHubConfig from environment variables"""
        return cls(
            token=os.getenv("GITHUB_TOKEN"),
            app_id=os.getenv("GITHUB_APP_ID"),
            private_key=os.getenv("GITHUB_PRIVATE_KEY"),
            webhook_secret=os.getenv("GITHUB_WEBHOOK_SECRET"),
            base_url=os.getenv("GITHUB_BASE_URL", "https://api.github.com"),
            timeout=int(os.getenv("GITHUB_TIMEOUT", "30")),
            max_retries=int(os.getenv("GITHUB_MAX_RETRIES", "3"))
        )
    
    def validate(self, require_auth: bool = False) -> None:
        """Validate GitHub configuration"""
        errors = []
        
        if require_auth and not self.token and not (self.app_id and self.private_key):
            errors.append("Either token or (app_id and private_key) must be provided")
        
        if self.timeout < 1:
            errors.append("timeout must be at least 1 second")
        
        if self.max_retries < 0:
            errors.append("max_retries must be non-negative")
        
        if errors:
            raise ValueError(f"GitHub configuration validation failed: {'; '.join(errors)}")
    
    @property
    def has_token_auth(self) -> bool:
        """Check if token authentication is configured"""
        return bool(self.token)
    
    @property
    def has_app_auth(self) -> bool:
        """Check if GitHub App authentication is configured"""
        return bool(self.app_id and self.private_key)


@dataclass
class DaggerConfig:
    """Configuration for Dagger operations"""
    
    engine_version: str = "latest"
    cache_enabled: bool = True
    parallel_execution: bool = True
    container_timeout: int = 600  # 10 minutes
    max_concurrent_containers: int = 5
    
    @classmethod
    def from_env(cls) -> "DaggerConfig":
        """Create DaggerConfig from environment variables"""
        return cls(
            engine_version=os.getenv("DAGGER_ENGINE_VERSION", "latest"),
            cache_enabled=os.getenv("DAGGER_CACHE_ENABLED", "true").lower() == "true",
            parallel_execution=os.getenv("DAGGER_PARALLEL_EXECUTION", "true").lower() == "true",
            container_timeout=int(os.getenv("DAGGER_CONTAINER_TIMEOUT", "600")),
            max_concurrent_containers=int(os.getenv("DAGGER_MAX_CONCURRENT_CONTAINERS", "5"))
        )
    
    def validate(self) -> None:
        """Validate Dagger configuration"""
        errors = []
        
        if self.container_timeout < 60:
            errors.append("container_timeout must be at least 60 seconds")
        
        if self.max_concurrent_containers < 1:
            errors.append("max_concurrent_containers must be at least 1")
        
        if errors:
            raise ValueError(f"Dagger configuration validation failed: {'; '.join(errors)}")


@dataclass
class AgentConfig:
    """Main configuration for the test repair agent"""
    
    # Sub-configurations
    deepseek_config: DeepSeekConfig
    github_config: GitHubConfig
    dagger_config: DaggerConfig
    
    # Agent behavior configuration
    enabled_fix_types: List[str] = field(default_factory=lambda: ["syntax_fix", "import_fix", "quality_fix"])
    python_versions: List[str] = field(default_factory=lambda: ["3.10", "3.11", "3.12"])
    max_concurrent_fixes: int = 3
    coverage_threshold: float = 80.0
    
    # File pattern configuration
    file_patterns: Dict[str, List[str]] = field(default_factory=lambda: {
        "include": ["*.py", "pyproject.toml", "requirements*.txt"],
        "exclude": ["__pycache__/*", "*.pyc", ".git/*", ".venv/*", "node_modules/*"]
    })
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Feature flags
    dry_run: bool = False
    create_issues_on_failure: bool = True
    auto_merge_safe_fixes: bool = False
    
    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Create AgentConfig from environment variables"""
        deepseek_config = DeepSeekConfig.from_env()
        github_config = GitHubConfig.from_env()
        dagger_config = DaggerConfig.from_env()
        
        # Parse enabled fix types
        enabled_fix_types = os.getenv("ENABLED_FIX_TYPES", "syntax_fix,import_fix,quality_fix").split(",")
        enabled_fix_types = [fix_type.strip() for fix_type in enabled_fix_types if fix_type.strip()]
        
        # Parse Python versions
        python_versions = os.getenv("PYTHON_VERSIONS", "3.10,3.11,3.12").split(",")
        python_versions = [version.strip() for version in python_versions if version.strip()]
        
        # Parse file patterns
        file_patterns = {
            "include": os.getenv("FILE_PATTERNS_INCLUDE", "*.py,pyproject.toml,requirements*.txt").split(","),
            "exclude": os.getenv("FILE_PATTERNS_EXCLUDE", "__pycache__/*,*.pyc,.git/*,.venv/*,node_modules/*").split(",")
        }
        
        return cls(
            deepseek_config=deepseek_config,
            github_config=github_config,
            dagger_config=dagger_config,
            enabled_fix_types=enabled_fix_types,
            python_versions=python_versions,
            max_concurrent_fixes=int(os.getenv("MAX_CONCURRENT_FIXES", "3")),
            coverage_threshold=float(os.getenv("COVERAGE_THRESHOLD", "80.0")),
            file_patterns=file_patterns,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "json"),
            dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
            create_issues_on_failure=os.getenv("CREATE_ISSUES_ON_FAILURE", "true").lower() == "true",
            auto_merge_safe_fixes=os.getenv("AUTO_MERGE_SAFE_FIXES", "false").lower() == "true"
        )
    
    @classmethod
    def from_file(cls, config_path: Path) -> "AgentConfig":
        """Load configuration from a JSON file"""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        # Create sub-configurations
        deepseek_data = data.get("deepseek", {})
        deepseek_config = DeepSeekConfig(
            api_key=deepseek_data.get("api_key", os.getenv("DEEPSEEK_API_KEY", "")),
            model=deepseek_data.get("model", "deepseek-coder"),
            max_tokens=deepseek_data.get("max_tokens", 4000),
            temperature=deepseek_data.get("temperature", 0.1),
            rate_limit=deepseek_data.get("rate_limit", 60),
            timeout=deepseek_data.get("timeout", 30)
        )
        
        github_data = data.get("github", {})
        github_config = GitHubConfig(
            token=github_data.get("token", os.getenv("GITHUB_TOKEN")),
            app_id=github_data.get("app_id", os.getenv("GITHUB_APP_ID")),
            private_key=github_data.get("private_key", os.getenv("GITHUB_PRIVATE_KEY")),
            webhook_secret=github_data.get("webhook_secret", os.getenv("GITHUB_WEBHOOK_SECRET")),
            base_url=github_data.get("base_url", "https://api.github.com"),
            timeout=github_data.get("timeout", 30),
            max_retries=github_data.get("max_retries", 3)
        )
        
        dagger_data = data.get("dagger", {})
        dagger_config = DaggerConfig(
            engine_version=dagger_data.get("engine_version", "latest"),
            cache_enabled=dagger_data.get("cache_enabled", True),
            parallel_execution=dagger_data.get("parallel_execution", True),
            container_timeout=dagger_data.get("container_timeout", 600),
            max_concurrent_containers=dagger_data.get("max_concurrent_containers", 5)
        )
        
        return cls(
            deepseek_config=deepseek_config,
            github_config=github_config,
            dagger_config=dagger_config,
            enabled_fix_types=data.get("enabled_fix_types", ["syntax_fix", "import_fix", "quality_fix"]),
            python_versions=data.get("python_versions", ["3.10", "3.11", "3.12"]),
            max_concurrent_fixes=data.get("max_concurrent_fixes", 3),
            coverage_threshold=data.get("coverage_threshold", 80.0),
            file_patterns=data.get("file_patterns", {
                "include": ["*.py", "pyproject.toml", "requirements*.txt"],
                "exclude": ["__pycache__/*", "*.pyc", ".git/*", ".venv/*", "node_modules/*"]
            }),
            log_level=data.get("log_level", "INFO"),
            log_format=data.get("log_format", "json"),
            dry_run=data.get("dry_run", False),
            create_issues_on_failure=data.get("create_issues_on_failure", True),
            auto_merge_safe_fixes=data.get("auto_merge_safe_fixes", False)
        )
    
    def validate(self, require_github_auth: bool = False) -> None:
        """Validate the entire configuration"""
        errors = []
        
        # Validate sub-configurations
        try:
            self.deepseek_config.validate()
        except ValueError as e:
            errors.append(f"DeepSeek config: {e}")
        
        try:
            self.github_config.validate(require_auth=require_github_auth)
        except ValueError as e:
            errors.append(f"GitHub config: {e}")
        
        try:
            self.dagger_config.validate()
        except ValueError as e:
            errors.append(f"Dagger config: {e}")
        
        # Validate agent-specific settings
        if self.coverage_threshold < 0 or self.coverage_threshold > 100:
            errors.append("coverage_threshold must be between 0 and 100")
        
        if self.max_concurrent_fixes < 1:
            errors.append("max_concurrent_fixes must be at least 1")
        
        if not self.enabled_fix_types:
            errors.append("at least one fix type must be enabled")
        
        if not self.python_versions:
            errors.append("at least one Python version must be specified")
        
        # Validate Python versions format
        for version in self.python_versions:
            if not version.replace(".", "").isdigit():
                errors.append(f"invalid Python version format: {version}")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"log_level must be one of: {valid_log_levels}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "deepseek": {
                "api_key": "***" if self.deepseek_config.api_key else None,  # Mask sensitive data
                "model": self.deepseek_config.model,
                "max_tokens": self.deepseek_config.max_tokens,
                "temperature": self.deepseek_config.temperature,
                "rate_limit": self.deepseek_config.rate_limit,
                "timeout": self.deepseek_config.timeout
            },
            "github": {
                "token": "***" if self.github_config.token else None,  # Mask sensitive data
                "app_id": self.github_config.app_id,
                "private_key": "***" if self.github_config.private_key else None,  # Mask sensitive data
                "webhook_secret": "***" if self.github_config.webhook_secret else None,  # Mask sensitive data
                "base_url": self.github_config.base_url,
                "timeout": self.github_config.timeout,
                "max_retries": self.github_config.max_retries
            },
            "dagger": {
                "engine_version": self.dagger_config.engine_version,
                "cache_enabled": self.dagger_config.cache_enabled,
                "parallel_execution": self.dagger_config.parallel_execution,
                "container_timeout": self.dagger_config.container_timeout,
                "max_concurrent_containers": self.dagger_config.max_concurrent_containers
            },
            "enabled_fix_types": self.enabled_fix_types,
            "python_versions": self.python_versions,
            "max_concurrent_fixes": self.max_concurrent_fixes,
            "coverage_threshold": self.coverage_threshold,
            "file_patterns": self.file_patterns,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "dry_run": self.dry_run,
            "create_issues_on_failure": self.create_issues_on_failure,
            "auto_merge_safe_fixes": self.auto_merge_safe_fixes
        }
    
    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to a JSON file"""
        config_dict = self.to_dict()
        
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)


def get_config(
    config_file: Optional[Path] = None,
    require_github_auth: bool = False
) -> AgentConfig:
    """Get the agent configuration with validation
    
    Args:
        config_file: Optional path to configuration file
        require_github_auth: Whether GitHub authentication is required
    
    Returns:
        Validated AgentConfig instance
    """
    if config_file and config_file.exists():
        config = AgentConfig.from_file(config_file)
    else:
        config = AgentConfig.from_env()
    
    config.validate(require_github_auth=require_github_auth)
    return config


def create_default_config_file(config_path: Path) -> None:
    """Create a default configuration file template
    
    Args:
        config_path: Path where to create the configuration file
    """
    default_config = {
        "deepseek": {
            "api_key": "${DEEPSEEK_API_KEY}",
            "model": "deepseek-coder",
            "max_tokens": 4000,
            "temperature": 0.1,
            "rate_limit": 60,
            "timeout": 30
        },
        "github": {
            "token": "${GITHUB_TOKEN}",
            "app_id": "${GITHUB_APP_ID}",
            "private_key": "${GITHUB_PRIVATE_KEY}",
            "webhook_secret": "${GITHUB_WEBHOOK_SECRET}",
            "base_url": "https://api.github.com",
            "timeout": 30,
            "max_retries": 3
        },
        "dagger": {
            "engine_version": "latest",
            "cache_enabled": True,
            "parallel_execution": True,
            "container_timeout": 600,
            "max_concurrent_containers": 5
        },
        "enabled_fix_types": [
            "syntax_fix",
            "import_fix",
            "quality_fix"
        ],
        "python_versions": [
            "3.10",
            "3.11",
            "3.12"
        ],
        "max_concurrent_fixes": 3,
        "coverage_threshold": 80.0,
        "file_patterns": {
            "include": [
                "*.py",
                "pyproject.toml",
                "requirements*.txt"
            ],
            "exclude": [
                "__pycache__/*",
                "*.pyc",
                ".git/*",
                ".venv/*",
                "node_modules/*"
            ]
        },
        "log_level": "INFO",
        "log_format": "json",
        "dry_run": False,
        "create_issues_on_failure": True,
        "auto_merge_safe_fixes": False
    }
    
    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(default_config, f, indent=2)