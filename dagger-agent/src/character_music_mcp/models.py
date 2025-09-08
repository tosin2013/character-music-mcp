"""Data models for the Dagger Test Repair Agent

This module contains all the data models used throughout the agent for representing
failures, analysis results, fixes, and validation results.
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, field_validator, ConfigDict
import json


class FailureCategory(str, Enum):
    """Categories of test failures that can be detected and fixed"""
    
    UNIT_TEST = "unit_test"
    INTEGRATION_TEST = "integration_test"
    SYNTAX_ERROR = "syntax_error"
    IMPORT_ERROR = "import_error"
    ASSERTION_ERROR = "assertion_error"
    RUNTIME_ERROR = "runtime_error"
    COVERAGE_FAILURE = "coverage_failure"
    LINTING_ERROR = "linting_error"
    TYPE_CHECK_ERROR = "type_check_error"
    SECURITY_SCAN_FAILURE = "security_scan_failure"
    DEPENDENCY_ERROR = "dependency_error"
    DOCUMENTATION_ERROR = "documentation_error"
    PERFORMANCE_FAILURE = "performance_failure"
    UNKNOWN = "unknown"


class FixType(str, Enum):
    """Types of fixes that can be generated"""
    
    SYNTAX_FIX = "syntax_fix"
    IMPORT_FIX = "import_fix"
    TEST_FIX = "test_fix"
    COVERAGE_FIX = "coverage_fix"
    QUALITY_FIX = "quality_fix"
    DEPENDENCY_FIX = "dependency_fix"
    SECURITY_FIX = "security_fix"
    DOCUMENTATION_FIX = "documentation_fix"
    CONFIGURATION_FIX = "configuration_fix"


class ValidationStatus(str, Enum):
    """Status of validation results"""
    
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class Failure(BaseModel):
    """Represents a test failure detected in GitHub Actions"""
    
    id: str = Field(..., description="Unique identifier for the failure")
    workflow_run_id: str = Field(..., description="GitHub workflow run ID")
    job_name: str = Field(..., description="Name of the failed job")
    step_name: str = Field(..., description="Name of the failed step")
    python_version: Optional[str] = Field(None, description="Python version if applicable")
    error_message: str = Field(..., description="Primary error message")
    logs: str = Field(..., description="Full logs from the failed step")
    file_path: Optional[str] = Field(None, description="File path where error occurred")
    line_number: Optional[int] = Field(None, description="Line number where error occurred")
    category: FailureCategory = Field(..., description="Category of the failure")
    repository: str = Field(..., description="Repository name (owner/repo)")
    branch: str = Field(..., description="Branch where failure occurred")
    commit_sha: str = Field(..., description="Commit SHA of the failure")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When failure was detected")
    
    @field_validator('line_number')
    @classmethod
    def validate_line_number(cls, v):
        if v is not None and v < 1:
            raise ValueError('Line number must be positive')
        return v
    
    model_config = ConfigDict(use_enum_values=True)


class CodeContext(BaseModel):
    """Code context for analysis"""
    
    file_path: str = Field(..., description="Path to the file")
    content: str = Field(..., description="File content")
    start_line: int = Field(..., description="Start line of relevant context")
    end_line: int = Field(..., description="End line of relevant context")
    surrounding_files: Dict[str, str] = Field(default_factory=dict, description="Related files and their content")
    
    @field_validator('start_line', 'end_line')
    @classmethod
    def validate_line_numbers(cls, v):
        if v < 1:
            raise ValueError('Line numbers must be positive')
        return v
    
    @field_validator('end_line')
    @classmethod
    def validate_end_after_start(cls, v, info):
        if info.data.get('start_line') and v < info.data['start_line']:
            raise ValueError('End line must be >= start line')
        return v


class Analysis(BaseModel):
    """Analysis result from DeepSeek API"""
    
    failure_id: str = Field(..., description="ID of the associated failure")
    root_cause: str = Field(..., description="Identified root cause of the failure")
    suggested_fix_type: FixType = Field(..., description="Suggested type of fix")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in the analysis (0-1)")
    code_context: CodeContext = Field(..., description="Code context used for analysis")
    deepseek_response: str = Field(..., description="Raw response from DeepSeek API")
    analysis_prompt: str = Field(..., description="Prompt sent to DeepSeek API")
    tokens_used: int = Field(default=0, description="Number of tokens used in API call")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When analysis was performed")
    
    model_config = ConfigDict(use_enum_values=True)


class FileChange(BaseModel):
    """Represents a change to a file"""
    
    file_path: str = Field(..., description="Path to the file being changed")
    original_content: str = Field(..., description="Original file content")
    new_content: str = Field(..., description="New file content after fix")
    change_type: str = Field(..., description="Type of change (create, modify, delete)")
    line_changes: Dict[str, Any] = Field(default_factory=dict, description="Specific line changes")
    
    @field_validator('change_type')
    @classmethod
    def validate_change_type(cls, v):
        valid_types = ['create', 'modify', 'delete']
        if v not in valid_types:
            raise ValueError(f'Change type must be one of: {valid_types}')
        return v


class Fix(BaseModel):
    """Represents a generated fix for a failure"""
    
    id: str = Field(..., description="Unique identifier for the fix")
    analysis_id: str = Field(..., description="ID of the associated analysis")
    fix_type: FixType = Field(..., description="Type of fix being applied")
    file_changes: List[FileChange] = Field(..., description="List of file changes")
    test_commands: List[str] = Field(default_factory=list, description="Commands to test the fix")
    description: str = Field(..., description="Human-readable description of the fix")
    estimated_impact: str = Field(..., description="Estimated impact of the fix")
    branch_name: str = Field(..., description="Git branch name for the fix")
    pr_title: str = Field(..., description="Proposed pull request title")
    pr_description: str = Field(..., description="Proposed pull request description")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When fix was generated")
    
    model_config = ConfigDict(use_enum_values=True)


class TestResult(BaseModel):
    """Result of running tests"""
    
    test_type: str = Field(..., description="Type of test (unit, integration, etc.)")
    status: ValidationStatus = Field(..., description="Test result status")
    output: str = Field(..., description="Test output/logs")
    duration: float = Field(..., description="Test execution time in seconds")
    coverage_percentage: Optional[float] = Field(None, description="Code coverage percentage")
    failed_tests: List[str] = Field(default_factory=list, description="List of failed test names")
    
    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v):
        if v < 0:
            raise ValueError('Duration must be non-negative')
        return v
    
    @field_validator('coverage_percentage')
    @classmethod
    def validate_coverage(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Coverage percentage must be between 0 and 100')
        return v
    
    model_config = ConfigDict(use_enum_values=True)


class QualityResult(BaseModel):
    """Result of quality checks (linting, type checking)"""
    
    tool: str = Field(..., description="Quality tool used (ruff, mypy, etc.)")
    status: ValidationStatus = Field(..., description="Quality check status")
    issues: List[Dict[str, Any]] = Field(default_factory=list, description="List of quality issues found")
    output: str = Field(..., description="Tool output")
    duration: float = Field(..., description="Check execution time in seconds")
    
    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v):
        if v < 0:
            raise ValueError('Duration must be non-negative')
        return v
    
    model_config = ConfigDict(use_enum_values=True)


class ValidationResult(BaseModel):
    """Result of validating a fix"""
    
    fix_id: str = Field(..., description="ID of the fix being validated")
    success: bool = Field(..., description="Whether validation passed overall")
    test_results: Dict[str, TestResult] = Field(default_factory=dict, description="Test results by type")
    quality_results: List[QualityResult] = Field(default_factory=list, description="Quality check results")
    logs: str = Field(..., description="Full validation logs")
    duration: float = Field(..., description="Total validation time in seconds")
    python_version: str = Field(..., description="Python version used for validation")
    container_id: Optional[str] = Field(None, description="Dagger container ID used")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When validation was performed")
    
    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v):
        if v < 0:
            raise ValueError('Duration must be non-negative')
        return v
    
    model_config = ConfigDict(use_enum_values=True)


class PullRequest(BaseModel):
    """Represents a pull request created for a fix"""
    
    fix_id: str = Field(..., description="ID of the associated fix")
    pr_number: int = Field(..., description="GitHub pull request number")
    title: str = Field(..., description="Pull request title")
    description: str = Field(..., description="Pull request description")
    branch_name: str = Field(..., description="Source branch name")
    base_branch: str = Field(..., description="Target branch name")
    repository: str = Field(..., description="Repository name (owner/repo)")
    url: str = Field(..., description="GitHub URL of the pull request")
    status: str = Field(..., description="Pull request status (open, closed, merged)")
    labels: List[str] = Field(default_factory=list, description="Labels applied to the PR")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When PR was created")
    updated_at: Optional[datetime] = Field(None, description="When PR was last updated")
    
    @field_validator('pr_number')
    @classmethod
    def validate_pr_number(cls, v):
        if v < 1:
            raise ValueError('PR number must be positive')
        return v


# Utility functions for serialization/deserialization

def serialize_model(model: BaseModel) -> str:
    """Serialize a Pydantic model to JSON string"""
    return model.model_dump_json()


def deserialize_model(model_class: type, json_str: str) -> BaseModel:
    """Deserialize a JSON string to a Pydantic model"""
    return model_class.model_validate_json(json_str)


def serialize_model_dict(model: BaseModel) -> Dict[str, Any]:
    """Serialize a Pydantic model to dictionary"""
    return model.model_dump()


def deserialize_model_dict(model_class: type, data: Dict[str, Any]) -> BaseModel:
    """Deserialize a dictionary to a Pydantic model"""
    return model_class.model_validate(data)


# Factory functions for creating models with defaults

def create_failure(
    workflow_run_id: str,
    job_name: str,
    step_name: str,
    error_message: str,
    logs: str,
    repository: str,
    branch: str,
    commit_sha: str,
    category: FailureCategory = FailureCategory.UNKNOWN,
    **kwargs
) -> Failure:
    """Create a Failure instance with required fields and optional overrides"""
    import uuid
    
    return Failure(
        id=str(uuid.uuid4()),
        workflow_run_id=workflow_run_id,
        job_name=job_name,
        step_name=step_name,
        error_message=error_message,
        logs=logs,
        repository=repository,
        branch=branch,
        commit_sha=commit_sha,
        category=category,
        **kwargs
    )


def create_analysis(
    failure_id: str,
    root_cause: str,
    suggested_fix_type: FixType,
    confidence_score: float,
    code_context: CodeContext,
    deepseek_response: str,
    analysis_prompt: str,
    **kwargs
) -> Analysis:
    """Create an Analysis instance with required fields and optional overrides"""
    return Analysis(
        failure_id=failure_id,
        root_cause=root_cause,
        suggested_fix_type=suggested_fix_type,
        confidence_score=confidence_score,
        code_context=code_context,
        deepseek_response=deepseek_response,
        analysis_prompt=analysis_prompt,
        **kwargs
    )


def create_fix(
    analysis_id: str,
    fix_type: FixType,
    file_changes: List[FileChange],
    description: str,
    estimated_impact: str,
    branch_name: str,
    pr_title: str,
    pr_description: str,
    **kwargs
) -> Fix:
    """Create a Fix instance with required fields and optional overrides"""
    import uuid
    
    return Fix(
        id=str(uuid.uuid4()),
        analysis_id=analysis_id,
        fix_type=fix_type,
        file_changes=file_changes,
        description=description,
        estimated_impact=estimated_impact,
        branch_name=branch_name,
        pr_title=pr_title,
        pr_description=pr_description,
        **kwargs
    )


def create_validation_result(
    fix_id: str,
    success: bool,
    logs: str,
    duration: float,
    python_version: str,
    **kwargs
) -> ValidationResult:
    """Create a ValidationResult instance with required fields and optional overrides"""
    return ValidationResult(
        fix_id=fix_id,
        success=success,
        logs=logs,
        duration=duration,
        python_version=python_version,
        **kwargs
    )