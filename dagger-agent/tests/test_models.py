"""Unit tests for data models"""

import pytest
from datetime import datetime
from typing import Dict, Any
import json
import uuid

from character_music_mcp.models import (
    Failure, Analysis, Fix, ValidationResult, PullRequest,
    CodeContext, FileChange, TestResult, QualityResult,
    FailureCategory, FixType, ValidationStatus,
    serialize_model, deserialize_model, serialize_model_dict, deserialize_model_dict,
    create_failure, create_analysis, create_fix, create_validation_result
)


class TestFailureCategory:
    """Test FailureCategory enum"""
    
    def test_failure_category_values(self):
        """Test that all expected failure categories exist"""
        expected_categories = [
            "unit_test", "integration_test", "syntax_error", "import_error",
            "assertion_error", "runtime_error", "coverage_failure", "linting_error",
            "type_check_error", "security_scan_failure", "dependency_error",
            "documentation_error", "performance_failure", "unknown"
        ]
        
        for category in expected_categories:
            assert hasattr(FailureCategory, category.upper())
            assert FailureCategory[category.upper()].value == category


class TestFixType:
    """Test FixType enum"""
    
    def test_fix_type_values(self):
        """Test that all expected fix types exist"""
        expected_types = [
            "syntax_fix", "import_fix", "test_fix", "coverage_fix",
            "quality_fix", "dependency_fix", "security_fix",
            "documentation_fix", "configuration_fix"
        ]
        
        for fix_type in expected_types:
            assert hasattr(FixType, fix_type.upper())
            assert FixType[fix_type.upper()].value == fix_type


class TestValidationStatus:
    """Test ValidationStatus enum"""
    
    def test_validation_status_values(self):
        """Test that all expected validation statuses exist"""
        expected_statuses = ["passed", "failed", "skipped", "error"]
        
        for status in expected_statuses:
            assert hasattr(ValidationStatus, status.upper())
            assert ValidationStatus[status.upper()].value == status


class TestFailure:
    """Test Failure model"""
    
    def test_failure_creation(self):
        """Test creating a valid Failure instance"""
        failure = Failure(
            id="test-id",
            workflow_run_id="12345",
            job_name="test",
            step_name="run tests",
            error_message="Test failed",
            logs="Full logs here",
            category=FailureCategory.UNIT_TEST,
            repository="owner/repo",
            branch="main",
            commit_sha="abc123"
        )
        
        assert failure.id == "test-id"
        assert failure.workflow_run_id == "12345"
        assert failure.job_name == "test"
        assert failure.step_name == "run tests"
        assert failure.error_message == "Test failed"
        assert failure.logs == "Full logs here"
        assert failure.category == FailureCategory.UNIT_TEST
        assert failure.repository == "owner/repo"
        assert failure.branch == "main"
        assert failure.commit_sha == "abc123"
        assert isinstance(failure.created_at, datetime)
    
    def test_failure_with_optional_fields(self):
        """Test creating a Failure with optional fields"""
        failure = Failure(
            id="test-id",
            workflow_run_id="12345",
            job_name="test",
            step_name="run tests",
            error_message="Test failed",
            logs="Full logs here",
            category=FailureCategory.SYNTAX_ERROR,
            repository="owner/repo",
            branch="main",
            commit_sha="abc123",
            python_version="3.10",
            file_path="test_file.py",
            line_number=42
        )
        
        assert failure.python_version == "3.10"
        assert failure.file_path == "test_file.py"
        assert failure.line_number == 42
    
    def test_failure_line_number_validation(self):
        """Test that line number validation works"""
        with pytest.raises(ValueError, match="Line number must be positive"):
            Failure(
                id="test-id",
                workflow_run_id="12345",
                job_name="test",
                step_name="run tests",
                error_message="Test failed",
                logs="Full logs here",
                category=FailureCategory.SYNTAX_ERROR,
                repository="owner/repo",
                branch="main",
                commit_sha="abc123",
                line_number=0
            )
    
    def test_failure_serialization(self):
        """Test Failure serialization to JSON"""
        failure = Failure(
            id="test-id",
            workflow_run_id="12345",
            job_name="test",
            step_name="run tests",
            error_message="Test failed",
            logs="Full logs here",
            category=FailureCategory.UNIT_TEST,
            repository="owner/repo",
            branch="main",
            commit_sha="abc123"
        )
        
        json_str = serialize_model(failure)
        assert isinstance(json_str, str)
        
        # Parse JSON to verify it's valid
        data = json.loads(json_str)
        assert data["id"] == "test-id"
        assert data["category"] == "unit_test"
    
    def test_failure_deserialization(self):
        """Test Failure deserialization from JSON"""
        failure_data = {
            "id": "test-id",
            "workflow_run_id": "12345",
            "job_name": "test",
            "step_name": "run tests",
            "error_message": "Test failed",
            "logs": "Full logs here",
            "category": "unit_test",
            "repository": "owner/repo",
            "branch": "main",
            "commit_sha": "abc123",
            "created_at": "2023-01-01T00:00:00"
        }
        
        failure = deserialize_model_dict(Failure, failure_data)
        assert failure.id == "test-id"
        assert failure.category == FailureCategory.UNIT_TEST


class TestCodeContext:
    """Test CodeContext model"""
    
    def test_code_context_creation(self):
        """Test creating a valid CodeContext instance"""
        context = CodeContext(
            file_path="test.py",
            content="def test(): pass",
            start_line=1,
            end_line=1
        )
        
        assert context.file_path == "test.py"
        assert context.content == "def test(): pass"
        assert context.start_line == 1
        assert context.end_line == 1
        assert context.surrounding_files == {}
    
    def test_code_context_line_validation(self):
        """Test line number validation"""
        with pytest.raises(ValueError, match="Line numbers must be positive"):
            CodeContext(
                file_path="test.py",
                content="def test(): pass",
                start_line=0,
                end_line=1
            )
        
        with pytest.raises(ValueError, match="End line must be >= start line"):
            CodeContext(
                file_path="test.py",
                content="def test(): pass",
                start_line=5,
                end_line=3
            )


class TestAnalysis:
    """Test Analysis model"""
    
    def test_analysis_creation(self):
        """Test creating a valid Analysis instance"""
        context = CodeContext(
            file_path="test.py",
            content="def test(): pass",
            start_line=1,
            end_line=1
        )
        
        analysis = Analysis(
            failure_id="failure-123",
            root_cause="Missing import statement",
            suggested_fix_type=FixType.IMPORT_FIX,
            confidence_score=0.85,
            code_context=context,
            deepseek_response="Add import statement",
            analysis_prompt="Analyze this error"
        )
        
        assert analysis.failure_id == "failure-123"
        assert analysis.root_cause == "Missing import statement"
        assert analysis.suggested_fix_type == FixType.IMPORT_FIX
        assert analysis.confidence_score == 0.85
        assert analysis.code_context == context
        assert analysis.deepseek_response == "Add import statement"
        assert analysis.analysis_prompt == "Analyze this error"
        assert isinstance(analysis.created_at, datetime)
    
    def test_analysis_confidence_validation(self):
        """Test confidence score validation"""
        context = CodeContext(
            file_path="test.py",
            content="def test(): pass",
            start_line=1,
            end_line=1
        )
        
        with pytest.raises(ValueError):
            Analysis(
                failure_id="failure-123",
                root_cause="Missing import statement",
                suggested_fix_type=FixType.IMPORT_FIX,
                confidence_score=1.5,  # Invalid: > 1.0
                code_context=context,
                deepseek_response="Add import statement",
                analysis_prompt="Analyze this error"
            )


class TestFileChange:
    """Test FileChange model"""
    
    def test_file_change_creation(self):
        """Test creating a valid FileChange instance"""
        change = FileChange(
            file_path="test.py",
            original_content="old content",
            new_content="new content",
            change_type="modify"
        )
        
        assert change.file_path == "test.py"
        assert change.original_content == "old content"
        assert change.new_content == "new content"
        assert change.change_type == "modify"
        assert change.line_changes == {}
    
    def test_file_change_type_validation(self):
        """Test change type validation"""
        with pytest.raises(ValueError, match="Change type must be one of"):
            FileChange(
                file_path="test.py",
                original_content="old content",
                new_content="new content",
                change_type="invalid"
            )


class TestFix:
    """Test Fix model"""
    
    def test_fix_creation(self):
        """Test creating a valid Fix instance"""
        file_change = FileChange(
            file_path="test.py",
            original_content="old content",
            new_content="new content",
            change_type="modify"
        )
        
        fix = Fix(
            id="fix-123",
            analysis_id="analysis-123",
            fix_type=FixType.SYNTAX_FIX,
            file_changes=[file_change],
            description="Fix syntax error",
            estimated_impact="Low",
            branch_name="fix/syntax-error",
            pr_title="Fix syntax error in test.py",
            pr_description="This PR fixes a syntax error"
        )
        
        assert fix.id == "fix-123"
        assert fix.analysis_id == "analysis-123"
        assert fix.fix_type == FixType.SYNTAX_FIX
        assert len(fix.file_changes) == 1
        assert fix.file_changes[0] == file_change
        assert fix.description == "Fix syntax error"
        assert fix.estimated_impact == "Low"
        assert fix.branch_name == "fix/syntax-error"
        assert fix.pr_title == "Fix syntax error in test.py"
        assert fix.pr_description == "This PR fixes a syntax error"
        assert isinstance(fix.created_at, datetime)


class TestTestResult:
    """Test TestResult model"""
    
    def test_test_result_creation(self):
        """Test creating a valid TestResult instance"""
        result = TestResult(
            test_type="unit",
            status=ValidationStatus.PASSED,
            output="All tests passed",
            duration=10.5
        )
        
        assert result.test_type == "unit"
        assert result.status == ValidationStatus.PASSED
        assert result.output == "All tests passed"
        assert result.duration == 10.5
        assert result.coverage_percentage is None
        assert result.failed_tests == []
    
    def test_test_result_with_coverage(self):
        """Test TestResult with coverage information"""
        result = TestResult(
            test_type="unit",
            status=ValidationStatus.PASSED,
            output="All tests passed",
            duration=10.5,
            coverage_percentage=85.5,
            failed_tests=[]
        )
        
        assert result.coverage_percentage == 85.5
    
    def test_test_result_validation(self):
        """Test TestResult validation"""
        with pytest.raises(ValueError, match="Duration must be non-negative"):
            TestResult(
                test_type="unit",
                status=ValidationStatus.PASSED,
                output="All tests passed",
                duration=-1.0
            )
        
        with pytest.raises(ValueError, match="Coverage percentage must be between 0 and 100"):
            TestResult(
                test_type="unit",
                status=ValidationStatus.PASSED,
                output="All tests passed",
                duration=10.5,
                coverage_percentage=150.0
            )


class TestQualityResult:
    """Test QualityResult model"""
    
    def test_quality_result_creation(self):
        """Test creating a valid QualityResult instance"""
        result = QualityResult(
            tool="ruff",
            status=ValidationStatus.PASSED,
            output="No issues found",
            duration=2.5
        )
        
        assert result.tool == "ruff"
        assert result.status == ValidationStatus.PASSED
        assert result.output == "No issues found"
        assert result.duration == 2.5
        assert result.issues == []


class TestValidationResult:
    """Test ValidationResult model"""
    
    def test_validation_result_creation(self):
        """Test creating a valid ValidationResult instance"""
        test_result = TestResult(
            test_type="unit",
            status=ValidationStatus.PASSED,
            output="All tests passed",
            duration=10.5
        )
        
        quality_result = QualityResult(
            tool="ruff",
            status=ValidationStatus.PASSED,
            output="No issues found",
            duration=2.5
        )
        
        validation = ValidationResult(
            fix_id="fix-123",
            success=True,
            test_results={"unit": test_result},
            quality_results=[quality_result],
            logs="Validation logs",
            duration=15.0,
            python_version="3.10"
        )
        
        assert validation.fix_id == "fix-123"
        assert validation.success is True
        assert "unit" in validation.test_results
        assert validation.test_results["unit"] == test_result
        assert len(validation.quality_results) == 1
        assert validation.quality_results[0] == quality_result
        assert validation.logs == "Validation logs"
        assert validation.duration == 15.0
        assert validation.python_version == "3.10"
        assert isinstance(validation.created_at, datetime)


class TestPullRequest:
    """Test PullRequest model"""
    
    def test_pull_request_creation(self):
        """Test creating a valid PullRequest instance"""
        pr = PullRequest(
            fix_id="fix-123",
            pr_number=42,
            title="Fix syntax error",
            description="This PR fixes a syntax error",
            branch_name="fix/syntax-error",
            base_branch="main",
            repository="owner/repo",
            url="https://github.com/owner/repo/pull/42",
            status="open"
        )
        
        assert pr.fix_id == "fix-123"
        assert pr.pr_number == 42
        assert pr.title == "Fix syntax error"
        assert pr.description == "This PR fixes a syntax error"
        assert pr.branch_name == "fix/syntax-error"
        assert pr.base_branch == "main"
        assert pr.repository == "owner/repo"
        assert pr.url == "https://github.com/owner/repo/pull/42"
        assert pr.status == "open"
        assert pr.labels == []
        assert isinstance(pr.created_at, datetime)
    
    def test_pull_request_validation(self):
        """Test PullRequest validation"""
        with pytest.raises(ValueError, match="PR number must be positive"):
            PullRequest(
                fix_id="fix-123",
                pr_number=0,
                title="Fix syntax error",
                description="This PR fixes a syntax error",
                branch_name="fix/syntax-error",
                base_branch="main",
                repository="owner/repo",
                url="https://github.com/owner/repo/pull/42",
                status="open"
            )


class TestSerializationFunctions:
    """Test serialization/deserialization utility functions"""
    
    def test_serialize_deserialize_model(self):
        """Test model serialization and deserialization"""
        failure = Failure(
            id="test-id",
            workflow_run_id="12345",
            job_name="test",
            step_name="run tests",
            error_message="Test failed",
            logs="Full logs here",
            category=FailureCategory.UNIT_TEST,
            repository="owner/repo",
            branch="main",
            commit_sha="abc123"
        )
        
        # Serialize to JSON string
        json_str = serialize_model(failure)
        assert isinstance(json_str, str)
        
        # Deserialize back to model
        deserialized = deserialize_model(Failure, json_str)
        assert deserialized.id == failure.id
        assert deserialized.category == failure.category
    
    def test_serialize_deserialize_model_dict(self):
        """Test model dictionary serialization and deserialization"""
        failure = Failure(
            id="test-id",
            workflow_run_id="12345",
            job_name="test",
            step_name="run tests",
            error_message="Test failed",
            logs="Full logs here",
            category=FailureCategory.UNIT_TEST,
            repository="owner/repo",
            branch="main",
            commit_sha="abc123"
        )
        
        # Serialize to dictionary
        data_dict = serialize_model_dict(failure)
        assert isinstance(data_dict, dict)
        assert data_dict["id"] == "test-id"
        
        # Deserialize back to model
        deserialized = deserialize_model_dict(Failure, data_dict)
        assert deserialized.id == failure.id
        assert deserialized.category == failure.category


class TestFactoryFunctions:
    """Test factory functions for creating models"""
    
    def test_create_failure(self):
        """Test create_failure factory function"""
        failure = create_failure(
            workflow_run_id="12345",
            job_name="test",
            step_name="run tests",
            error_message="Test failed",
            logs="Full logs here",
            repository="owner/repo",
            branch="main",
            commit_sha="abc123",
            category=FailureCategory.UNIT_TEST
        )
        
        assert failure.workflow_run_id == "12345"
        assert failure.job_name == "test"
        assert failure.category == FailureCategory.UNIT_TEST
        assert isinstance(failure.id, str)
        assert len(failure.id) > 0  # UUID should be generated
    
    def test_create_analysis(self):
        """Test create_analysis factory function"""
        context = CodeContext(
            file_path="test.py",
            content="def test(): pass",
            start_line=1,
            end_line=1
        )
        
        analysis = create_analysis(
            failure_id="failure-123",
            root_cause="Missing import statement",
            suggested_fix_type=FixType.IMPORT_FIX,
            confidence_score=0.85,
            code_context=context,
            deepseek_response="Add import statement",
            analysis_prompt="Analyze this error"
        )
        
        assert analysis.failure_id == "failure-123"
        assert analysis.root_cause == "Missing import statement"
        assert analysis.suggested_fix_type == FixType.IMPORT_FIX
        assert analysis.confidence_score == 0.85
    
    def test_create_fix(self):
        """Test create_fix factory function"""
        file_change = FileChange(
            file_path="test.py",
            original_content="old content",
            new_content="new content",
            change_type="modify"
        )
        
        fix = create_fix(
            analysis_id="analysis-123",
            fix_type=FixType.SYNTAX_FIX,
            file_changes=[file_change],
            description="Fix syntax error",
            estimated_impact="Low",
            branch_name="fix/syntax-error",
            pr_title="Fix syntax error in test.py",
            pr_description="This PR fixes a syntax error"
        )
        
        assert fix.analysis_id == "analysis-123"
        assert fix.fix_type == FixType.SYNTAX_FIX
        assert len(fix.file_changes) == 1
        assert isinstance(fix.id, str)
        assert len(fix.id) > 0  # UUID should be generated
    
    def test_create_validation_result(self):
        """Test create_validation_result factory function"""
        validation = create_validation_result(
            fix_id="fix-123",
            success=True,
            logs="Validation logs",
            duration=15.0,
            python_version="3.10"
        )
        
        assert validation.fix_id == "fix-123"
        assert validation.success is True
        assert validation.logs == "Validation logs"
        assert validation.duration == 15.0
        assert validation.python_version == "3.10"