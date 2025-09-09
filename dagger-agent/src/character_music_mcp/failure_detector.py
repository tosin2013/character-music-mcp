"""Failure Detection System

This module implements the FailureDetector class that parses GitHub workflow logs,
categorizes different failure types, and extracts error messages for analysis.
"""

import re
from typing import Any

import structlog

from .models import Failure, FailureCategory, create_failure

logger = structlog.get_logger(__name__)


class FailureDetector:
    """Detects and categorizes test failures from GitHub workflow logs"""

    def __init__(self):
        """Initialize the failure detector with pattern matchers"""
        self.failure_patterns = self._initialize_failure_patterns()
        self.job_type_patterns = self._initialize_job_type_patterns()

    def _initialize_failure_patterns(self) -> dict[FailureCategory, list[str]]:
        """Initialize regex patterns for different failure types"""
        return {
            FailureCategory.SYNTAX_ERROR: [
                r"SyntaxError:",
                r"IndentationError:",
                r"TabError:",
                r"invalid syntax",
                r"unexpected EOF while parsing",
                r"unmatched '\)'",
                r"unmatched '\]'",
                r"unmatched '\}'"
            ],
            FailureCategory.IMPORT_ERROR: [
                r"ImportError:",
                r"ModuleNotFoundError:",
                r"No module named",
                r"cannot import name",
                r"attempted relative import",
                r"PYTHONPATH",
                r"sys\.path"
            ],
            FailureCategory.ASSERTION_ERROR: [
                r"AssertionError:",
                r"assert .+ == .+",
                r"assert .+ != .+",
                r"assert .+ is .+",
                r"assert .+ in .+",
                r"Expected .+ but got .+",
                r"FAILED.*assert"
            ],
            FailureCategory.RUNTIME_ERROR: [
                r"RuntimeError:",
                r"ValueError:",
                r"TypeError:",
                r"AttributeError:",
                r"KeyError:",
                r"IndexError:",
                r"NameError:",
                r"UnboundLocalError:",
                r"ZeroDivisionError:",
                r"FileNotFoundError:",
                r"PermissionError:"
            ],
            FailureCategory.COVERAGE_FAILURE: [
                r"TOTAL.*\d+%.*FAIL",
                r"coverage.*below.*threshold",
                r"--cov-fail-under",
                r"Required test coverage of \d+% not reached",
                r"Coverage check failed",
                r"FAIL Required test coverage"
            ],
            FailureCategory.LINTING_ERROR: [
                r"ruff.*error",
                r"ruff.*failed",
                r"E\d{3}.*",  # PEP8 error codes
                r"W\d{3}.*",  # PEP8 warning codes
                r"F\d{3}.*",  # Pyflakes codes
                r"C\d{3}.*",  # McCabe complexity
                r"N\d{3}.*",  # Naming conventions
                r"D\d{3}.*",  # Docstring conventions
                r"S\d{3}.*",  # Security issues
                r"B\d{3}.*",  # Bugbear issues
                r"A\d{3}.*",  # Built-in shadowing
                r"COM\d{3}.*", # Comma issues
                r"ISC\d{3}.*", # String concatenation
                r"ICN\d{3}.*", # Import conventions
                r"PIE\d{3}.*", # Pie issues
                r"T\d{3}.*",   # Print statements
                r"RET\d{3}.*", # Return issues
                r"SIM\d{3}.*", # Simplification
                r"ARG\d{3}.*", # Unused arguments
                r"PTH\d{3}.*", # Path issues
                r"ERA\d{3}.*", # Commented code
                r"PD\d{3}.*",  # Pandas issues
                r"PGH\d{3}.*", # Pygrep hooks
                r"PL\d{3}.*",  # Pylint
                r"TRY\d{3}.*", # Try/except issues
                r"FLY\d{3}.*", # Flynt issues
                r"PERF\d{3}.*", # Performance issues
                r"FURB\d{3}.*", # Refurb issues
                r"LOG\d{3}.*", # Logging issues
                r"RUF\d{3}.*"  # Ruff-specific rules
            ],
            FailureCategory.TYPE_CHECK_ERROR: [
                r"mypy.*error",
                r"error:.*\[.*\]",
                r"Incompatible types",
                r"Cannot determine type",
                r"has no attribute",
                r"Argument \d+ to .* has incompatible type",
                r"Incompatible return value type",
                r"Need type annotation",
                r"Variable .* is not valid as a type",
                r"Cannot infer type"
            ],
            FailureCategory.SECURITY_SCAN_FAILURE: [
                r"safety.*error",
                r"bandit.*error",
                r"Security issue found",
                r"Vulnerability found",
                r"High severity",
                r"Medium severity",
                r"B\d{3}.*",  # Bandit issue codes
                r"CWE-\d+",   # Common Weakness Enumeration
                r"CVE-\d{4}-\d+"  # Common Vulnerabilities and Exposures
            ],
            FailureCategory.DEPENDENCY_ERROR: [
                r"pip.*error",
                r"uv.*error",
                r"Could not find a version",
                r"No matching distribution found",
                r"Package .* not found",
                r"Dependency resolution failed",
                r"Requirements conflict",
                r"Version conflict",
                r"pyproject\.toml.*error",
                r"uv\.lock.*error"
            ],
            FailureCategory.DOCUMENTATION_ERROR: [
                r"sphinx.*error",
                r"Documentation build failed",
                r"rst.*error",
                r"markdown.*error",
                r"Missing docstring",
                r"Invalid cross-reference",
                r"Unknown directive",
                r"Malformed table"
            ],
            FailureCategory.PERFORMANCE_FAILURE: [
                r"Performance test failed",
                r"Benchmark.*failed",
                r"Timeout.*exceeded",
                r"Memory limit exceeded",
                r"CPU limit exceeded",
                r"Response time.*exceeded"
            ]
        }

    def _initialize_job_type_patterns(self) -> dict[str, FailureCategory]:
        """Initialize patterns to map job names to failure categories"""
        # Order matters - more specific patterns should come first
        return {
            r".*performance.*test.*": FailureCategory.PERFORMANCE_FAILURE,
            r".*performance.*": FailureCategory.PERFORMANCE_FAILURE,
            r".*benchmark.*": FailureCategory.PERFORMANCE_FAILURE,
            r".*unit.*test.*": FailureCategory.UNIT_TEST,
            r".*integration.*test.*": FailureCategory.INTEGRATION_TEST,
            r".*test.*unit.*": FailureCategory.UNIT_TEST,
            r".*test.*integration.*": FailureCategory.INTEGRATION_TEST,
            r".*quality.*check.*": FailureCategory.LINTING_ERROR,
            r".*lint.*": FailureCategory.LINTING_ERROR,
            r".*ruff.*": FailureCategory.LINTING_ERROR,
            r".*mypy.*": FailureCategory.TYPE_CHECK_ERROR,
            r".*type.*check.*": FailureCategory.TYPE_CHECK_ERROR,
            r".*security.*scan.*": FailureCategory.SECURITY_SCAN_FAILURE,
            r".*security.*": FailureCategory.SECURITY_SCAN_FAILURE,
            r".*safety.*": FailureCategory.SECURITY_SCAN_FAILURE,
            r".*bandit.*": FailureCategory.SECURITY_SCAN_FAILURE,
            r".*documentation.*": FailureCategory.DOCUMENTATION_ERROR,
            r".*docs.*": FailureCategory.DOCUMENTATION_ERROR,
            r".*coverage.*": FailureCategory.COVERAGE_FAILURE,
            r".*test.*": FailureCategory.UNIT_TEST,  # Default test jobs to unit tests (must be last)
        }

    async def detect_failures(
        self,
        workflow_run_id: str,
        jobs_data: dict[str, Any],
        repository: str,
        branch: str,
        commit_sha: str
    ) -> list[Failure]:
        """
        Detect failures from GitHub workflow jobs data

        Args:
            workflow_run_id: GitHub workflow run ID
            jobs_data: Jobs data from GitHub API
            repository: Repository name (owner/repo)
            branch: Branch name
            commit_sha: Commit SHA

        Returns:
            List of detected failures
        """
        logger.info(
            "Detecting failures in workflow run",
            workflow_run_id=workflow_run_id,
            repository=repository
        )

        failures = []

        jobs = jobs_data.get("jobs", [])
        if jobs is None:
            jobs = []

        for job in jobs:
            if job.get("conclusion") == "failure":
                job_failures = await self._analyze_job_failure(
                    job, workflow_run_id, repository, branch, commit_sha
                )
                failures.extend(job_failures)

        logger.info(
            "Failure detection completed",
            workflow_run_id=workflow_run_id,
            total_failures=len(failures)
        )

        return failures

    async def _analyze_job_failure(
        self,
        job: dict[str, Any],
        workflow_run_id: str,
        repository: str,
        branch: str,
        commit_sha: str
    ) -> list[Failure]:
        """Analyze a single failed job to extract failures"""
        job_name = job.get("name", "unknown")
        job_id = job.get("id")

        logger.info("Analyzing failed job", job_name=job_name, job_id=job_id)

        failures = []

        # Analyze each failed step
        for step in job.get("steps", []):
            if step.get("conclusion") == "failure":
                step_failures = await self._analyze_step_failure(
                    step, job, workflow_run_id, repository, branch, commit_sha
                )
                failures.extend(step_failures)

        # If no step-level failures found but job failed, create a job-level failure
        if not failures:
            job_failure = await self._create_job_level_failure(
                job, workflow_run_id, repository, branch, commit_sha
            )
            if job_failure:
                failures.append(job_failure)

        return failures

    async def _analyze_step_failure(
        self,
        step: dict[str, Any],
        job: dict[str, Any],
        workflow_run_id: str,
        repository: str,
        branch: str,
        commit_sha: str
    ) -> list[Failure]:
        """Analyze a single failed step"""
        step_name = step.get("name", "unknown")
        job_name = job.get("name", "unknown")

        # For now, we'll create a placeholder failure since we don't have logs
        # In a real implementation, this would fetch and parse the actual logs
        logs = f"Step '{step_name}' in job '{job_name}' failed"
        error_message = f"Step failure in {step_name}"

        # Categorize based on job and step names
        category = self._categorize_failure_by_name(job_name, step_name)

        # Extract Python version if available
        python_version = self._extract_python_version(job_name)

        failure = create_failure(
            workflow_run_id=workflow_run_id,
            job_name=job_name,
            step_name=step_name,
            error_message=error_message,
            logs=logs,
            repository=repository,
            branch=branch,
            commit_sha=commit_sha,
            category=category,
            python_version=python_version
        )

        return [failure]

    async def _create_job_level_failure(
        self,
        job: dict[str, Any],
        workflow_run_id: str,
        repository: str,
        branch: str,
        commit_sha: str
    ) -> Failure | None:
        """Create a job-level failure when no step-level failures are found"""
        job_name = job.get("name", "unknown")

        # Skip if job didn't actually fail
        if job.get("conclusion") != "failure":
            return None

        logs = f"Job '{job_name}' failed without specific step failures"
        error_message = f"Job failure: {job_name}"

        category = self._categorize_failure_by_name(job_name, "")
        python_version = self._extract_python_version(job_name)

        return create_failure(
            workflow_run_id=workflow_run_id,
            job_name=job_name,
            step_name="job-level",
            error_message=error_message,
            logs=logs,
            repository=repository,
            branch=branch,
            commit_sha=commit_sha,
            category=category,
            python_version=python_version
        )

    def _categorize_failure_by_name(self, job_name: str, step_name: str) -> FailureCategory:
        """Categorize failure based on job and step names"""
        full_name = f"{job_name} {step_name}".lower()

        # Check job type patterns
        for pattern, category in self.job_type_patterns.items():
            if re.search(pattern, full_name, re.IGNORECASE):
                return category

        return FailureCategory.UNKNOWN

    def _extract_python_version(self, job_name: str) -> str | None:
        """Extract Python version from job name"""
        # Look for patterns like "python-3.10", "py310", "3.11", etc.
        patterns = [
            r"python[_-]?(\d+\.\d+)",
            r"py(\d)(\d+)",
            r"(\d+\.\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, job_name.lower())
            if match:
                if len(match.groups()) == 1:
                    return match.group(1)
                elif len(match.groups()) == 2:
                    # Handle py310 format
                    return f"{match.group(1)}.{match.group(2)}"

        return None

    async def categorize_failure(self, failure: Failure) -> FailureCategory:
        """
        Categorize a failure based on its logs and error message

        Args:
            failure: The failure to categorize

        Returns:
            The categorized failure type
        """
        logs = failure.logs.lower()
        error_message = failure.error_message.lower()
        combined_text = f"{logs} {error_message}"

        # Check each category's patterns
        for category, patterns in self.failure_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    logger.info(
                        "Failure categorized",
                        failure_id=failure.id,
                        category=category.value,
                        matched_pattern=pattern
                    )
                    return category

        # If no pattern matches, try to infer from job/step names
        name_category = self._categorize_failure_by_name(failure.job_name, failure.step_name)
        if name_category != FailureCategory.UNKNOWN:
            return name_category

        logger.warning(
            "Could not categorize failure",
            failure_id=failure.id,
            job_name=failure.job_name,
            step_name=failure.step_name
        )

        return FailureCategory.UNKNOWN

    async def extract_logs(self, job_data: dict[str, Any]) -> str:
        """
        Extract logs from job data (placeholder implementation)

        In a real implementation, this would make API calls to fetch actual logs

        Args:
            job_data: Job data from GitHub API

        Returns:
            Extracted logs as string
        """
        job_name = job_data.get("name", "unknown")
        job_id = job_data.get("id", "unknown")
        conclusion = job_data.get("conclusion", "unknown")

        # Placeholder log extraction
        logs = f"""
Job: {job_name}
Job ID: {job_id}
Conclusion: {conclusion}
Started: {job_data.get('started_at', 'unknown')}
Completed: {job_data.get('completed_at', 'unknown')}

Steps:
"""

        for step in job_data.get("steps", []):
            step_name = step.get("name", "unknown")
            step_conclusion = step.get("conclusion", "unknown")
            logs += f"  - {step_name}: {step_conclusion}\n"

            if step_conclusion == "failure":
                logs += f"    Error: Step '{step_name}' failed\n"

        return logs

    def extract_error_details(self, logs: str) -> tuple[str | None, int | None]:
        """
        Extract file path and line number from error logs

        Args:
            logs: The log content to analyze

        Returns:
            Tuple of (file_path, line_number) or (None, None) if not found
        """
        # Common patterns for file paths and line numbers in Python tracebacks
        patterns = [
            r'File "([^"]+)", line (\d+)',
            r'([^\s]+\.py):(\d+):',
            r'([^\s]+\.py)\((\d+)\)',
            r'in ([^\s]+\.py) line (\d+)',
            r'([^\s]+\.py) at line (\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, logs)
            if match:
                file_path = match.group(1)
                line_number = int(match.group(2))

                # Clean up file path (remove leading ./ or absolute paths)
                if file_path.startswith('./'):
                    file_path = file_path[2:]
                elif file_path.startswith('/'):
                    # Try to extract relative path from absolute path
                    parts = file_path.split('/')
                    if 'src' in parts:
                        src_index = parts.index('src')
                        file_path = '/'.join(parts[src_index:])
                    elif any(part.endswith('.py') for part in parts):
                        # Find the first Python file and take from there
                        for i, part in enumerate(parts):
                            if part.endswith('.py') or part in ['tests', 'src']:
                                file_path = '/'.join(parts[i:])
                                break

                return file_path, line_number

        return None, None

    def extract_specific_error_message(self, logs: str, category: FailureCategory) -> str:
        """
        Extract specific error message based on failure category

        Args:
            logs: The log content to analyze
            category: The failure category

        Returns:
            Extracted specific error message
        """
        if category == FailureCategory.SYNTAX_ERROR:
            return self._extract_syntax_error(logs)
        elif category == FailureCategory.IMPORT_ERROR:
            return self._extract_import_error(logs)
        elif category == FailureCategory.ASSERTION_ERROR:
            return self._extract_assertion_error(logs)
        elif category == FailureCategory.COVERAGE_FAILURE:
            return self._extract_coverage_error(logs)
        elif category == FailureCategory.LINTING_ERROR:
            return self._extract_linting_error(logs)
        elif category == FailureCategory.TYPE_CHECK_ERROR:
            return self._extract_type_error(logs)
        else:
            return self._extract_generic_error(logs)

    def _extract_syntax_error(self, logs: str) -> str:
        """Extract syntax error details"""
        patterns = [
            r'SyntaxError: (.+)',
            r'IndentationError: (.+)',
            r'TabError: (.+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, logs)
            if match:
                return match.group(1).strip()

        return "Syntax error detected"

    def _extract_import_error(self, logs: str) -> str:
        """Extract import error details"""
        patterns = [
            r'ImportError: (.+)',
            r'ModuleNotFoundError: (.+)',
            r'No module named [\'"]([^\'"]+)[\'"]',
        ]

        for pattern in patterns:
            match = re.search(pattern, logs)
            if match:
                return match.group(1).strip()

        return "Import error detected"

    def _extract_assertion_error(self, logs: str) -> str:
        """Extract assertion error details"""
        patterns = [
            r'AssertionError: (.+)',
            r'assert (.+)',
            r'Expected (.+) but got (.+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, logs)
            if match:
                return match.group(0).strip()

        return "Assertion error detected"

    def _extract_coverage_error(self, logs: str) -> str:
        """Extract coverage error details"""
        patterns = [
            r'TOTAL.*(\d+)%.*FAIL',
            r'Required test coverage of (\d+)% not reached.*Total coverage: (\d+\.\d+)%',
            r'Coverage check failed.*(\d+\.\d+)%',
        ]

        for pattern in patterns:
            match = re.search(pattern, logs)
            if match:
                return match.group(0).strip()

        return "Coverage threshold not met"

    def _extract_linting_error(self, logs: str) -> str:
        """Extract linting error details"""
        patterns = [
            r'([A-Z]\d{3}.*)',
            r'ruff.*: (.+)',
            r'(\w+:\d+:\d+: [A-Z]\d{3} .+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, logs)
            if match:
                return match.group(1).strip()

        return "Linting error detected"

    def _extract_type_error(self, logs: str) -> str:
        """Extract type checking error details"""
        patterns = [
            r'error: (.+)',  # Capture everything after "error:"
            r'mypy.*: (.+)',
            r'(Incompatible types .+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, logs)
            if match:
                return match.group(1).strip()

        return "Type checking error detected"

    def _extract_generic_error(self, logs: str) -> str:
        """Extract generic error message"""
        # Look for common error patterns
        patterns = [
            r'Error: (.+)',
            r'Exception: (.+)',
            r'Failed: (.+)',
            r'(\w+Error: .+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, logs)
            if match:
                return match.group(1).strip()

        # If no specific pattern found, return first line that looks like an error
        lines = logs.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
                return line

        return "Unknown error detected"
