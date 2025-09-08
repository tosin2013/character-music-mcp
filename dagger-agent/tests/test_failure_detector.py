"""Unit tests for the FailureDetector class"""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, patch

from character_music_mcp.failure_detector import FailureDetector
from character_music_mcp.models import FailureCategory, Failure


class TestFailureDetector:
    """Test cases for FailureDetector"""
    
    @pytest.fixture
    def detector(self):
        """Create a FailureDetector instance for testing"""
        return FailureDetector()
    
    @pytest.fixture
    def sample_workflow_data(self):
        """Sample workflow data for testing"""
        return {
            "jobs": [
                {
                    "id": 12345,
                    "name": "test (python-3.10)",
                    "conclusion": "failure",
                    "started_at": "2024-01-01T10:00:00Z",
                    "completed_at": "2024-01-01T10:05:00Z",
                    "steps": [
                        {
                            "name": "Run unit tests",
                            "conclusion": "failure"
                        },
                        {
                            "name": "Setup Python",
                            "conclusion": "success"
                        }
                    ]
                },
                {
                    "id": 12346,
                    "name": "quality-checks",
                    "conclusion": "failure",
                    "started_at": "2024-01-01T10:00:00Z",
                    "completed_at": "2024-01-01T10:03:00Z",
                    "steps": [
                        {
                            "name": "Run ruff",
                            "conclusion": "failure"
                        }
                    ]
                },
                {
                    "id": 12347,
                    "name": "security-scan",
                    "conclusion": "success",
                    "steps": [
                        {
                            "name": "Run bandit",
                            "conclusion": "success"
                        }
                    ]
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_detect_failures_basic(self, detector, sample_workflow_data):
        """Test basic failure detection"""
        failures = await detector.detect_failures(
            workflow_run_id="123456",
            jobs_data=sample_workflow_data,
            repository="owner/repo",
            branch="main",
            commit_sha="abc123"
        )
        
        assert len(failures) == 2  # Two failed jobs
        
        # Check first failure (unit test)
        unit_test_failure = failures[0]
        assert unit_test_failure.workflow_run_id == "123456"
        assert unit_test_failure.job_name == "test (python-3.10)"
        assert unit_test_failure.step_name == "Run unit tests"
        assert unit_test_failure.python_version == "3.10"
        assert unit_test_failure.repository == "owner/repo"
        assert unit_test_failure.branch == "main"
        assert unit_test_failure.commit_sha == "abc123"
        assert unit_test_failure.category == FailureCategory.UNIT_TEST
        
        # Check second failure (quality checks)
        quality_failure = failures[1]
        assert quality_failure.job_name == "quality-checks"
        assert quality_failure.step_name == "Run ruff"
        assert quality_failure.category == FailureCategory.LINTING_ERROR
    
    @pytest.mark.asyncio
    async def test_detect_failures_no_failures(self, detector):
        """Test detection when no failures exist"""
        jobs_data = {
            "jobs": [
                {
                    "id": 12345,
                    "name": "test",
                    "conclusion": "success",
                    "steps": [
                        {
                            "name": "Run tests",
                            "conclusion": "success"
                        }
                    ]
                }
            ]
        }
        
        failures = await detector.detect_failures(
            workflow_run_id="123456",
            jobs_data=jobs_data,
            repository="owner/repo",
            branch="main",
            commit_sha="abc123"
        )
        
        assert len(failures) == 0
    
    @pytest.mark.asyncio
    async def test_detect_failures_job_level_failure(self, detector):
        """Test detection of job-level failures without step failures"""
        jobs_data = {
            "jobs": [
                {
                    "id": 12345,
                    "name": "integration-tests",
                    "conclusion": "failure",
                    "steps": [
                        {
                            "name": "Setup",
                            "conclusion": "success"
                        },
                        {
                            "name": "Run tests",
                            "conclusion": "success"
                        }
                    ]
                }
            ]
        }
        
        failures = await detector.detect_failures(
            workflow_run_id="123456",
            jobs_data=jobs_data,
            repository="owner/repo",
            branch="main",
            commit_sha="abc123"
        )
        
        assert len(failures) == 1
        failure = failures[0]
        assert failure.job_name == "integration-tests"
        assert failure.step_name == "job-level"
        assert failure.category == FailureCategory.INTEGRATION_TEST
    
    def test_categorize_failure_by_name(self, detector):
        """Test failure categorization by job/step names"""
        test_cases = [
            ("unit-test", "", FailureCategory.UNIT_TEST),
            ("integration-test", "", FailureCategory.INTEGRATION_TEST),
            ("test-python-3.10", "", FailureCategory.UNIT_TEST),
            ("quality-checks", "", FailureCategory.LINTING_ERROR),
            ("ruff-check", "", FailureCategory.LINTING_ERROR),
            ("mypy-check", "", FailureCategory.TYPE_CHECK_ERROR),
            ("security-scan", "", FailureCategory.SECURITY_SCAN_FAILURE),
            ("documentation-build", "", FailureCategory.DOCUMENTATION_ERROR),
            ("coverage-check", "", FailureCategory.COVERAGE_FAILURE),
            ("performance-test", "", FailureCategory.PERFORMANCE_FAILURE),
            ("unknown-job", "", FailureCategory.UNKNOWN),
        ]
        
        for job_name, step_name, expected_category in test_cases:
            category = detector._categorize_failure_by_name(job_name, step_name)
            assert category == expected_category, f"Failed for job: {job_name}"
    
    def test_extract_python_version(self, detector):
        """Test Python version extraction from job names"""
        test_cases = [
            ("test (python-3.10)", "3.10"),
            ("test-python-3.11", "3.11"),
            ("test_python_3.12", "3.12"),
            ("test-py310", "3.10"),
            ("test-py311", "3.11"),
            ("test-3.10", "3.10"),
            ("test-matrix-3.11", "3.11"),
            ("test-no-version", None),
            ("quality-checks", None),
        ]
        
        for job_name, expected_version in test_cases:
            version = detector._extract_python_version(job_name)
            assert version == expected_version, f"Failed for job: {job_name}"
    
    @pytest.mark.asyncio
    async def test_categorize_failure_by_logs(self, detector):
        """Test failure categorization by log content"""
        test_cases = [
            ("SyntaxError: invalid syntax", FailureCategory.SYNTAX_ERROR),
            ("ImportError: No module named 'missing_module'", FailureCategory.IMPORT_ERROR),
            ("AssertionError: assert 1 == 2", FailureCategory.ASSERTION_ERROR),
            ("ValueError: invalid literal", FailureCategory.RUNTIME_ERROR),
            ("TOTAL 75% FAIL Required test coverage", FailureCategory.COVERAGE_FAILURE),
            ("E501 line too long", FailureCategory.LINTING_ERROR),
            ("mypy error: Incompatible types", FailureCategory.TYPE_CHECK_ERROR),
            ("bandit error: High severity issue", FailureCategory.SECURITY_SCAN_FAILURE),
            ("pip error: Could not find version", FailureCategory.DEPENDENCY_ERROR),
            ("sphinx error: Documentation build failed", FailureCategory.DOCUMENTATION_ERROR),
            ("Performance test failed", FailureCategory.PERFORMANCE_FAILURE),
        ]
        
        for logs, expected_category in test_cases:
            # Create a mock failure with the test logs
            failure = Failure(
                id="test",
                workflow_run_id="123",
                job_name="test",
                step_name="test",
                error_message="test error",
                logs=logs,
                repository="owner/repo",
                branch="main",
                commit_sha="abc123",
                category=FailureCategory.UNKNOWN
            )
            
            category = await detector.categorize_failure(failure)
            assert category == expected_category, f"Failed for logs: {logs}"
    
    def test_extract_error_details(self, detector):
        """Test extraction of file path and line number from logs"""
        test_cases = [
            ('File "src/main.py", line 42', ("src/main.py", 42)),
            ('src/test.py:123: error message', ("src/test.py", 123)),
            ('main.py(456)', ("main.py", 456)),
            ('in utils.py line 789', ("utils.py", 789)),
            ('config.py at line 101', ("config.py", 101)),
            ('./src/module.py:55: warning', ("src/module.py", 55)),
            ('/absolute/path/src/file.py:99: error', ("src/file.py", 99)),
            ('no file info here', (None, None)),
        ]
        
        for logs, expected_result in test_cases:
            result = detector.extract_error_details(logs)
            assert result == expected_result, f"Failed for logs: {logs}"
    
    def test_extract_specific_error_messages(self, detector):
        """Test extraction of specific error messages by category"""
        test_cases = [
            (FailureCategory.SYNTAX_ERROR, "SyntaxError: invalid syntax", "invalid syntax"),
            (FailureCategory.IMPORT_ERROR, "ImportError: No module named 'test'", "No module named 'test'"),
            (FailureCategory.ASSERTION_ERROR, "AssertionError: 1 != 2", "1 != 2"),
            (FailureCategory.COVERAGE_FAILURE, "TOTAL 75% FAIL", "TOTAL 75% FAIL"),
            (FailureCategory.LINTING_ERROR, "E501 line too long (82 > 79)", "E501 line too long (82 > 79)"),
            (FailureCategory.TYPE_CHECK_ERROR, "error: Incompatible types [assignment]", "Incompatible types [assignment]"),
        ]
        
        for category, logs, expected_message in test_cases:
            message = detector.extract_specific_error_message(logs, category)
            assert expected_message in message, f"Failed for category: {category.value}"
    
    @pytest.mark.asyncio
    async def test_extract_logs(self, detector):
        """Test log extraction from job data"""
        job_data = {
            "name": "test-job",
            "id": 12345,
            "conclusion": "failure",
            "started_at": "2024-01-01T10:00:00Z",
            "completed_at": "2024-01-01T10:05:00Z",
            "steps": [
                {
                    "name": "Setup",
                    "conclusion": "success"
                },
                {
                    "name": "Run tests",
                    "conclusion": "failure"
                }
            ]
        }
        
        logs = await detector.extract_logs(job_data)
        
        assert "Job: test-job" in logs
        assert "Job ID: 12345" in logs
        assert "Conclusion: failure" in logs
        assert "Setup: success" in logs
        assert "Run tests: failure" in logs
        assert "Error: Step 'Run tests' failed" in logs


class TestFailureDetectorPatterns:
    """Test failure detection patterns"""
    
    @pytest.fixture
    def detector(self):
        return FailureDetector()
    
    def test_syntax_error_patterns(self, detector):
        """Test syntax error pattern matching"""
        patterns = detector.failure_patterns[FailureCategory.SYNTAX_ERROR]
        test_logs = [
            "SyntaxError: invalid syntax",
            "IndentationError: expected an indented block",
            "TabError: inconsistent use of tabs and spaces",
            "unexpected EOF while parsing",
            "unmatched ')'",
        ]
        
        for logs in test_logs:
            assert any(
                __import__('re').search(pattern, logs, __import__('re').IGNORECASE)
                for pattern in patterns
            ), f"Pattern not matched for: {logs}"
    
    def test_import_error_patterns(self, detector):
        """Test import error pattern matching"""
        patterns = detector.failure_patterns[FailureCategory.IMPORT_ERROR]
        test_logs = [
            "ImportError: cannot import name 'missing'",
            "ModuleNotFoundError: No module named 'test'",
            "No module named 'missing_package'",
            "cannot import name 'function' from 'module'",
            "attempted relative import with no known parent package",
        ]
        
        for logs in test_logs:
            assert any(
                __import__('re').search(pattern, logs, __import__('re').IGNORECASE)
                for pattern in patterns
            ), f"Pattern not matched for: {logs}"
    
    def test_coverage_failure_patterns(self, detector):
        """Test coverage failure pattern matching"""
        patterns = detector.failure_patterns[FailureCategory.COVERAGE_FAILURE]
        test_logs = [
            "TOTAL 75% FAIL",
            "coverage below threshold",
            "--cov-fail-under=80",
            "Required test coverage of 80% not reached",
            "Coverage check failed",
            "FAIL Required test coverage",
        ]
        
        for logs in test_logs:
            assert any(
                __import__('re').search(pattern, logs, __import__('re').IGNORECASE)
                for pattern in patterns
            ), f"Pattern not matched for: {logs}"
    
    def test_linting_error_patterns(self, detector):
        """Test linting error pattern matching"""
        patterns = detector.failure_patterns[FailureCategory.LINTING_ERROR]
        test_logs = [
            "E501 line too long",
            "W292 no newline at end of file",
            "F401 'os' imported but unused",
            "C901 'function' is too complex",
            "N806 variable in function should be lowercase",
            "D100 Missing docstring in public module",
            "S101 Use of assert detected",
            "B008 Do not perform function calls in argument defaults",
            "RUF001 String contains ambiguous character",
        ]
        
        for logs in test_logs:
            assert any(
                __import__('re').search(pattern, logs, __import__('re').IGNORECASE)
                for pattern in patterns
            ), f"Pattern not matched for: {logs}"
    
    def test_type_check_error_patterns(self, detector):
        """Test type checking error pattern matching"""
        patterns = detector.failure_patterns[FailureCategory.TYPE_CHECK_ERROR]
        test_logs = [
            "mypy error: Incompatible types",
            "error: Cannot determine type [misc]",
            "Incompatible types in assignment",
            "has no attribute 'missing'",
            "Argument 1 to 'func' has incompatible type",
            "Incompatible return value type",
            "Need type annotation for variable",
        ]
        
        for logs in test_logs:
            assert any(
                __import__('re').search(pattern, logs, __import__('re').IGNORECASE)
                for pattern in patterns
            ), f"Pattern not matched for: {logs}"


class TestFailureDetectorIntegration:
    """Integration tests for FailureDetector"""
    
    @pytest.fixture
    def detector(self):
        return FailureDetector()
    
    @pytest.mark.asyncio
    async def test_real_workflow_failure_scenario(self, detector):
        """Test with realistic workflow failure data"""
        workflow_data = {
            "jobs": [
                {
                    "id": 1001,
                    "name": "test (ubuntu-latest, python-3.10)",
                    "conclusion": "failure",
                    "started_at": "2024-01-01T10:00:00Z",
                    "completed_at": "2024-01-01T10:15:00Z",
                    "steps": [
                        {
                            "name": "Set up Python 3.10",
                            "conclusion": "success"
                        },
                        {
                            "name": "Install dependencies",
                            "conclusion": "success"
                        },
                        {
                            "name": "Run unit tests with coverage",
                            "conclusion": "failure"
                        }
                    ]
                },
                {
                    "id": 1002,
                    "name": "quality-checks",
                    "conclusion": "failure",
                    "started_at": "2024-01-01T10:00:00Z",
                    "completed_at": "2024-01-01T10:05:00Z",
                    "steps": [
                        {
                            "name": "Run ruff linting",
                            "conclusion": "failure"
                        },
                        {
                            "name": "Run mypy type checking",
                            "conclusion": "success"
                        }
                    ]
                },
                {
                    "id": 1003,
                    "name": "security-scan",
                    "conclusion": "failure",
                    "started_at": "2024-01-01T10:00:00Z",
                    "completed_at": "2024-01-01T10:02:00Z",
                    "steps": [
                        {
                            "name": "Run safety check",
                            "conclusion": "failure"
                        }
                    ]
                }
            ]
        }
        
        failures = await detector.detect_failures(
            workflow_run_id="workflow_123",
            jobs_data=workflow_data,
            repository="test-org/test-repo",
            branch="feature/test-fix",
            commit_sha="commit_abc123"
        )
        
        assert len(failures) == 3
        
        # Verify unit test failure
        unit_failure = next(f for f in failures if f.job_name.startswith("test"))
        assert unit_failure.category == FailureCategory.UNIT_TEST
        assert unit_failure.python_version == "3.10"
        assert unit_failure.step_name == "Run unit tests with coverage"
        
        # Verify quality check failure
        quality_failure = next(f for f in failures if f.job_name == "quality-checks")
        assert quality_failure.category == FailureCategory.LINTING_ERROR
        assert quality_failure.step_name == "Run ruff linting"
        
        # Verify security scan failure
        security_failure = next(f for f in failures if f.job_name == "security-scan")
        assert security_failure.category == FailureCategory.SECURITY_SCAN_FAILURE
        assert security_failure.step_name == "Run safety check"
    
    @pytest.mark.asyncio
    async def test_matrix_job_failures(self, detector):
        """Test detection of failures in matrix jobs"""
        workflow_data = {
            "jobs": [
                {
                    "id": 2001,
                    "name": "test (ubuntu-latest, python-3.10)",
                    "conclusion": "success",
                    "steps": [{"name": "Run tests", "conclusion": "success"}]
                },
                {
                    "id": 2002,
                    "name": "test (ubuntu-latest, python-3.11)",
                    "conclusion": "failure",
                    "steps": [{"name": "Run tests", "conclusion": "failure"}]
                },
                {
                    "id": 2003,
                    "name": "test (ubuntu-latest, python-3.12)",
                    "conclusion": "success",
                    "steps": [{"name": "Run tests", "conclusion": "success"}]
                }
            ]
        }
        
        failures = await detector.detect_failures(
            workflow_run_id="matrix_test_123",
            jobs_data=workflow_data,
            repository="test-org/matrix-repo",
            branch="main",
            commit_sha="matrix_commit_456"
        )
        
        assert len(failures) == 1
        failure = failures[0]
        assert failure.python_version == "3.11"
        assert failure.category == FailureCategory.UNIT_TEST
        assert "python-3.11" in failure.job_name
    
    @pytest.mark.asyncio
    async def test_empty_workflow_data(self, detector):
        """Test handling of empty or malformed workflow data"""
        test_cases = [
            {},  # Empty dict
            {"jobs": []},  # No jobs
            {"jobs": None},  # None jobs
            {"jobs": [{}]},  # Empty job
            {"jobs": [{"conclusion": "success"}]},  # Job without failure
        ]
        
        for workflow_data in test_cases:
            failures = await detector.detect_failures(
                workflow_run_id="empty_test",
                jobs_data=workflow_data,
                repository="test-org/empty-repo",
                branch="main",
                commit_sha="empty_commit"
            )
            assert len(failures) == 0