#!/usr/bin/env python3
"""
Test Configuration for Character-Driven Music Generation

Centralized configuration for test execution, performance thresholds,
and test environment settings.
"""

import os
from pathlib import Path
from typing import Any, Dict, List


class TestConfig:
    """Test configuration management"""
    __test__ = False  # Prevent pytest from collecting this class

    def __init__(self):
        # Test execution settings
        self.PARALLEL_EXECUTION = False  # Set to True for parallel test execution
        self.MAX_CONCURRENT_TESTS = 5
        self.TEST_TIMEOUT = 30.0  # seconds
        self.VERBOSE_OUTPUT = True

        # Performance thresholds
        self.PERFORMANCE_THRESHOLDS = {
            "character_analysis_time": 5.0,  # seconds
            "persona_generation_time": 3.0,
            "command_generation_time": 2.0,
            "total_workflow_time": 10.0,
            "memory_usage_mb": 500,
            "large_text_processing_time": 15.0,  # for 10k+ word texts
            "concurrent_request_response_time": 8.0
        }

        # Test data settings
        self.TEST_DATA_SCENARIOS = [
            "single_character_simple",
            "multi_character_medium",
            "concept_album_complex",
            "minimal_character_edge",
            "emotional_intensity_high"
        ]

        # Coverage requirements
        self.MINIMUM_COVERAGE = {
            "overall": 0.85,  # 85% overall coverage
            "unit_tests": 0.90,  # 90% for unit tests
            "integration_tests": 0.80,  # 80% for integration tests
            "mcp_tools": 1.0  # 100% coverage for MCP tools
        }

        # Test suite configuration
        self.TEST_SUITES = {
            "unit": {
                "enabled": True,
                "path": "tests/unit",
                "pattern": "test_*.py",
                "timeout": 10.0
            },
            "integration": {
                "enabled": True,
                "path": "tests/integration",
                "pattern": "test_*.py",
                "timeout": 30.0
            },
            "performance": {
                "enabled": True,
                "path": "tests/performance",
                "pattern": "test_*.py",
                "timeout": 60.0
            },
            "existing": {
                "enabled": True,
                "path": "tests",
                "pattern": "test_*.py",
                "timeout": 20.0
            }
        }

        # Environment settings
        self.TEST_ENVIRONMENT = {
            "mock_mcp_server": True,
            "use_real_data": False,  # Use real vs mock data
            "log_level": "INFO",
            "save_test_artifacts": True,
            "cleanup_after_tests": True
        }

        # Reporting settings
        self.REPORTING = {
            "generate_html_report": True,
            "generate_json_report": True,
            "generate_coverage_report": True,
            "save_performance_metrics": True,
            "report_directory": "test_reports",
            "include_screenshots": False  # For future UI testing
        }

        # Load environment overrides
        self._load_environment_overrides()

    def _load_environment_overrides(self):
        """Load configuration overrides from environment variables"""
        # Performance thresholds
        for key in self.PERFORMANCE_THRESHOLDS:
            env_key = f"TEST_{key.upper()}"
            if env_key in os.environ:
                try:
                    self.PERFORMANCE_THRESHOLDS[key] = float(os.environ[env_key])
                except ValueError:
                    pass

        # Test execution settings
        if "TEST_PARALLEL" in os.environ:
            self.PARALLEL_EXECUTION = os.environ["TEST_PARALLEL"].lower() == "true"

        if "TEST_VERBOSE" in os.environ:
            self.VERBOSE_OUTPUT = os.environ["TEST_VERBOSE"].lower() == "true"

        if "TEST_TIMEOUT" in os.environ:
            try:
                self.TEST_TIMEOUT = float(os.environ["TEST_TIMEOUT"])
            except ValueError:
                pass

    def get_suite_config(self, suite_name: str) -> Dict[str, Any]:
        """Get configuration for specific test suite"""
        return self.TEST_SUITES.get(suite_name, {})

    def is_suite_enabled(self, suite_name: str) -> bool:
        """Check if test suite is enabled"""
        suite_config = self.get_suite_config(suite_name)
        return suite_config.get("enabled", False)

    def get_enabled_suites(self) -> List[str]:
        """Get list of enabled test suites"""
        return [name for name, config in self.TEST_SUITES.items()
                if config.get("enabled", False)]

    def get_performance_threshold(self, metric_name: str) -> float:
        """Get performance threshold for specific metric"""
        return self.PERFORMANCE_THRESHOLDS.get(metric_name, float('inf'))

    def should_run_performance_tests(self) -> bool:
        """Check if performance tests should be run"""
        return self.is_suite_enabled("performance")

    def get_report_directory(self) -> Path:
        """Get report directory path"""
        report_dir = Path(self.REPORTING["report_directory"])
        report_dir.mkdir(exist_ok=True)
        return report_dir

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "parallel_execution": self.PARALLEL_EXECUTION,
            "max_concurrent_tests": self.MAX_CONCURRENT_TESTS,
            "test_timeout": self.TEST_TIMEOUT,
            "verbose_output": self.VERBOSE_OUTPUT,
            "performance_thresholds": self.PERFORMANCE_THRESHOLDS,
            "test_data_scenarios": self.TEST_DATA_SCENARIOS,
            "minimum_coverage": self.MINIMUM_COVERAGE,
            "test_suites": self.TEST_SUITES,
            "test_environment": self.TEST_ENVIRONMENT,
            "reporting": self.REPORTING
        }


# Global configuration instance
test_config = TestConfig()


# Utility functions for common configuration checks
def should_run_suite(suite_name: str) -> bool:
    """Check if a test suite should be run"""
    return test_config.is_suite_enabled(suite_name)


def get_timeout_for_suite(suite_name: str) -> float:
    """Get timeout for specific test suite"""
    suite_config = test_config.get_suite_config(suite_name)
    return suite_config.get("timeout", test_config.TEST_TIMEOUT)


def meets_performance_threshold(metric_name: str, actual_value: float) -> bool:
    """Check if actual performance meets threshold"""
    threshold = test_config.get_performance_threshold(metric_name)
    return actual_value <= threshold


def get_test_scenarios_for_complexity(complexity: str) -> List[str]:
    """Get test scenarios filtered by complexity"""
    # This would integrate with TestDataManager
    complexity_mapping = {
        "simple": ["single_character_simple", "minimal_character_edge"],
        "medium": ["multi_character_medium"],
        "complex": ["concept_album_complex", "emotional_intensity_high"]
    }
    return complexity_mapping.get(complexity, [])


# Environment-specific configurations
class DevelopmentTestConfig(TestConfig):
    """Configuration for development environment"""
    __test__ = False  # Prevent pytest from collecting this class

    def __init__(self):
        super().__init__()
        self.VERBOSE_OUTPUT = True
        self.TEST_ENVIRONMENT["log_level"] = "DEBUG"
        self.TEST_ENVIRONMENT["save_test_artifacts"] = True
        self.PERFORMANCE_THRESHOLDS = {k: v * 2 for k, v in self.PERFORMANCE_THRESHOLDS.items()}  # Relaxed thresholds


class CITestConfig(TestConfig):
    """Configuration for CI/CD environment"""
    __test__ = False  # Prevent pytest from collecting this class

    def __init__(self):
        super().__init__()
        self.PARALLEL_EXECUTION = True
        self.MAX_CONCURRENT_TESTS = 3  # Conservative for CI
        self.VERBOSE_OUTPUT = False
        self.TEST_ENVIRONMENT["cleanup_after_tests"] = True
        self.REPORTING["generate_html_report"] = False  # Save CI resources


class ProductionTestConfig(TestConfig):
    """Configuration for production-like testing"""
    __test__ = False  # Prevent pytest from collecting this class

    def __init__(self):
        super().__init__()
        self.PARALLEL_EXECUTION = True
        self.MAX_CONCURRENT_TESTS = 10
        self.TEST_ENVIRONMENT["use_real_data"] = True  # Use real data when available
        # Strict performance thresholds (use defaults)


def get_config_for_environment(env: str = None) -> TestConfig:
    """Get configuration for specific environment"""
    if env is None:
        env = os.environ.get("TEST_ENV", "development")

    if env == "ci":
        return CITestConfig()
    elif env == "production":
        return ProductionTestConfig()
    else:
        return DevelopmentTestConfig()


# Export the appropriate configuration
current_config = get_config_for_environment()
