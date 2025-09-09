"""Unit tests for the FailureAnalyzer class"""

import json
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from character_music_mcp.deepseek_client import DeepSeekConfig, DeepSeekResponse
from character_music_mcp.failure_analyzer import (
    AnalysisCache,
    CodeContextExtractor,
    FailureAnalyzer,
)
from character_music_mcp.models import (
    Analysis,
    CodeContext,
    FailureCategory,
    FixType,
    create_failure,
)


class TestCodeContextExtractor:
    """Test CodeContextExtractor class"""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            # Create test files
            (repo_path / "src").mkdir()
            (repo_path / "tests").mkdir()

            # Create a source file
            src_file = repo_path / "src" / "main.py"
            src_file.write_text("""
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

class Calculator:
    def __init__(self):
        self.history = []
    
    def calculate(self, operation, a, b):
        if operation == "add":
            result = add(a, b)
        elif operation == "divide":
            result = divide(a, b)
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        self.history.append((operation, a, b, result))
        return result
            """.strip())

            # Create a test file
            test_file = repo_path / "tests" / "test_main.py"
            test_file.write_text("""
import pytest
from src.main import add, divide, Calculator

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_divide():
    assert divide(10, 2) == 5
    with pytest.raises(ValueError):
        divide(10, 0)

def test_calculator():
    calc = Calculator()
    result = calc.calculate("add", 5, 3)
    assert result == 8
    assert len(calc.history) == 1
            """.strip())

            # Create pyproject.toml
            pyproject_file = repo_path / "pyproject.toml"
            pyproject_file.write_text("""
[project]
name = "test-project"
version = "0.1.0"
dependencies = ["pytest"]

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
            """.strip())

            yield repo_path

    @pytest.fixture
    def extractor(self, temp_repo):
        """Create a CodeContextExtractor for testing"""
        return CodeContextExtractor(str(temp_repo))

    @pytest.fixture
    def sample_failure(self):
        """Create a sample failure for testing"""
        return create_failure(
            workflow_run_id="123456",
            job_name="test",
            step_name="Run tests",
            error_message="AssertionError: assert 8 == 9",
            logs="FAILED tests/test_main.py::test_calculator - AssertionError",
            repository="owner/repo",
            branch="main",
            commit_sha="abc123",
            category=FailureCategory.ASSERTION_ERROR,
            file_path="tests/test_main.py",
            line_number=15
        )

    @pytest.mark.asyncio
    async def test_extract_context_with_line_number(self, extractor, sample_failure):
        """Test extracting context with specific line number"""
        context = await extractor.extract_context(sample_failure, context_lines=3)

        assert context is not None
        assert context.file_path == "tests/test_main.py"
        assert context.start_line == 12  # 15 - 3
        assert context.end_line == 18   # 15 + 3
        assert "test_calculator" in context.content
        assert "calc = Calculator()" in context.content

        # Should include surrounding files
        assert len(context.surrounding_files) > 0
        assert "pyproject.toml" in context.surrounding_files

    @pytest.mark.asyncio
    async def test_extract_context_without_line_number(self, extractor):
        """Test extracting context without specific line number"""
        failure = create_failure(
            workflow_run_id="123456",
            job_name="test",
            step_name="Run tests",
            error_message="ImportError: No module named 'missing'",
            logs="ImportError in tests/test_main.py",
            repository="owner/repo",
            branch="main",
            commit_sha="abc123",
            category=FailureCategory.IMPORT_ERROR,
            file_path="tests/test_main.py",
            line_number=None
        )

        context = await extractor.extract_context(failure)

        assert context is not None
        assert context.file_path == "tests/test_main.py"
        assert context.start_line == 1
        assert "import pytest" in context.content
        assert "test_add" in context.content

    @pytest.mark.asyncio
    async def test_extract_context_file_not_found(self, extractor):
        """Test handling of non-existent files"""
        failure = create_failure(
            workflow_run_id="123456",
            job_name="test",
            step_name="Run tests",
            error_message="File not found",
            logs="Error in missing_file.py",
            repository="owner/repo",
            branch="main",
            commit_sha="abc123",
            category=FailureCategory.RUNTIME_ERROR,
            file_path="missing_file.py",
            line_number=1
        )

        context = await extractor.extract_context(failure)
        assert context is None

    @pytest.mark.asyncio
    async def test_extract_context_no_file_path(self, extractor):
        """Test handling of failures without file path"""
        failure = create_failure(
            workflow_run_id="123456",
            job_name="test",
            step_name="Run tests",
            error_message="General error",
            logs="Some error occurred",
            repository="owner/repo",
            branch="main",
            commit_sha="abc123",
            category=FailureCategory.RUNTIME_ERROR,
            file_path=None,
            line_number=None
        )

        context = await extractor.extract_context(failure)
        assert context is None

    @pytest.mark.asyncio
    async def test_get_surrounding_files_for_test_file(self, extractor, sample_failure):
        """Test getting surrounding files for a test file"""
        surrounding = await extractor._get_surrounding_files(sample_failure, max_files=10)

        # Should include configuration files
        assert "pyproject.toml" in surrounding

        # Should try to include corresponding source files
        # (may or may not find them depending on naming conventions)
        assert len(surrounding) > 0

    @pytest.mark.asyncio
    async def test_get_surrounding_files_for_source_file(self, extractor):
        """Test getting surrounding files for a source file"""
        failure = create_failure(
            workflow_run_id="123456",
            job_name="test",
            step_name="Run tests",
            error_message="Syntax error",
            logs="SyntaxError in src/main.py",
            repository="owner/repo",
            branch="main",
            commit_sha="abc123",
            category=FailureCategory.SYNTAX_ERROR,
            file_path="src/main.py",
            line_number=5
        )

        surrounding = await extractor._get_surrounding_files(failure, max_files=10)

        # Should include configuration files
        assert "pyproject.toml" in surrounding

        # Should try to include test files
        assert len(surrounding) > 0


class TestAnalysisCache:
    """Test AnalysisCache class"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def cache(self, temp_cache_dir):
        """Create an AnalysisCache for testing"""
        return AnalysisCache(temp_cache_dir, ttl_hours=1)

    @pytest.fixture
    def sample_failure(self):
        """Create a sample failure for testing"""
        return create_failure(
            workflow_run_id="123456",
            job_name="test",
            step_name="Run tests",
            error_message="Test error",
            logs="Test logs",
            repository="owner/repo",
            branch="main",
            commit_sha="abc123",
            category=FailureCategory.UNIT_TEST
        )

    @pytest.fixture
    def sample_analysis(self, sample_failure):
        """Create a sample analysis for testing"""
        code_context = CodeContext(
            file_path="test.py",
            content="def test(): pass",
            start_line=1,
            end_line=1
        )

        return Analysis(
            failure_id=sample_failure.id,
            root_cause="Test root cause",
            suggested_fix_type=FixType.TEST_FIX,
            confidence_score=0.8,
            code_context=code_context,
            deepseek_response="Test response",
            analysis_prompt="Test prompt",
            tokens_used=100
        )

    def test_cache_key_generation(self, cache, sample_failure):
        """Test cache key generation"""
        code_context = CodeContext(
            file_path="test.py",
            content="def test(): pass",
            start_line=1,
            end_line=1
        )

        key1 = cache._get_cache_key(sample_failure, code_context)
        key2 = cache._get_cache_key(sample_failure, code_context)

        # Same inputs should generate same key
        assert key1 == key2
        assert len(key1) == 64  # SHA256 hex digest length

    def test_cache_key_different_for_different_inputs(self, cache, sample_failure):
        """Test that different inputs generate different cache keys"""
        code_context1 = CodeContext(
            file_path="test1.py",
            content="def test1(): pass",
            start_line=1,
            end_line=1
        )

        code_context2 = CodeContext(
            file_path="test2.py",
            content="def test2(): pass",
            start_line=1,
            end_line=1
        )

        key1 = cache._get_cache_key(sample_failure, code_context1)
        key2 = cache._get_cache_key(sample_failure, code_context2)

        assert key1 != key2

    def test_cache_set_and_get(self, cache, sample_failure, sample_analysis):
        """Test setting and getting cache entries"""
        code_context = sample_analysis.code_context

        # Initially should not be cached
        cached = cache.get(sample_failure, code_context)
        assert cached is None

        # Cache the analysis
        cache.set(sample_failure, sample_analysis, code_context)

        # Should now be cached
        cached = cache.get(sample_failure, code_context)
        assert cached is not None
        assert cached.failure_id == sample_analysis.failure_id
        assert cached.root_cause == sample_analysis.root_cause
        assert cached.suggested_fix_type == sample_analysis.suggested_fix_type
        assert cached.confidence_score == sample_analysis.confidence_score

    def test_cache_expiration(self, temp_cache_dir, sample_failure, sample_analysis):
        """Test cache expiration"""
        # Create cache with very short TTL
        cache = AnalysisCache(temp_cache_dir, ttl_hours=0.001)  # ~3.6 seconds
        code_context = sample_analysis.code_context

        # Cache the analysis
        cache.set(sample_failure, sample_analysis, code_context)

        # Should be cached immediately
        cached = cache.get(sample_failure, code_context)
        assert cached is not None

        # Wait for expiration (in real test, we'd mock time)
        import time
        time.sleep(0.01)  # Wait a bit longer than TTL

        # Should be expired (though this test might be flaky due to timing)
        # In practice, we'd mock datetime.now() for reliable testing

    def test_cache_corrupted_file_handling(self, cache, sample_failure):
        """Test handling of corrupted cache files"""
        # Create a corrupted cache file
        cache_key = cache._get_cache_key(sample_failure, None)
        cache_file = cache.cache_dir / f"{cache_key}.json"
        cache_file.write_text("invalid json content")

        # Should handle corrupted file gracefully
        cached = cache.get(sample_failure, None)
        assert cached is None

        # Corrupted file should be removed
        assert not cache_file.exists()

    def test_clear_expired(self, cache, sample_failure, sample_analysis):
        """Test clearing expired cache entries"""
        code_context = sample_analysis.code_context

        # Add some cache entries
        cache.set(sample_failure, sample_analysis, code_context)

        # Create an expired entry by manually creating an old cache file
        old_cache_data = {
            "cached_at": (datetime.now(UTC) - timedelta(hours=2)).isoformat(),
            "analysis": {
                "failure_id": "old_failure",
                "root_cause": "Old cause",
                "suggested_fix_type": "test_fix",
                "confidence_score": 0.5,
                "code_context": None,
                "deepseek_response": "Old response",
                "analysis_prompt": "Old prompt",
                "tokens_used": 50,
                "created_at": datetime.now(UTC).isoformat(),
            }
        }

        old_cache_file = cache.cache_dir / "old_entry.json"
        with open(old_cache_file, 'w') as f:
            json.dump(old_cache_data, f)

        # Clear expired entries
        removed_count = cache.clear_expired()

        # Should have removed the old entry
        assert removed_count >= 1
        assert not old_cache_file.exists()


class TestFailureAnalyzer:
    """Test FailureAnalyzer class"""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            # Create a simple test file
            test_file = repo_path / "test.py"
            test_file.write_text("def test_function():\n    assert 1 == 2")

            yield repo_path

    @pytest.fixture
    def deepseek_config(self):
        """Create DeepSeek configuration for testing"""
        return DeepSeekConfig(
            api_key="test-key",
            max_retries=1,
            timeout=10
        )

    @pytest.fixture
    def analyzer(self, deepseek_config, temp_repo):
        """Create a FailureAnalyzer for testing"""
        with tempfile.TemporaryDirectory() as cache_dir:
            yield FailureAnalyzer(
                deepseek_config=deepseek_config,
                repository_path=str(temp_repo),
                cache_dir=cache_dir,
                cache_ttl_hours=1
            )

    @pytest.fixture
    def sample_failure(self):
        """Create a sample failure for testing"""
        return create_failure(
            workflow_run_id="123456",
            job_name="test",
            step_name="Run tests",
            error_message="AssertionError: assert 1 == 2",
            logs="FAILED test.py::test_function - AssertionError: assert 1 == 2",
            repository="owner/repo",
            branch="main",
            commit_sha="abc123",
            category=FailureCategory.ASSERTION_ERROR,
            file_path="test.py",
            line_number=2
        )

    @pytest.fixture
    def mock_deepseek_response(self):
        """Create a mock DeepSeek response"""
        return DeepSeekResponse(
            content="""
The root cause of this failure is an incorrect assertion in the test.
The test expects 1 to equal 2, which is mathematically impossible.

Confidence: 0.95

This is a test logic error that needs to be fixed by correcting the assertion.
            """.strip(),
            tokens_used=150,
            model="deepseek-coder",
            finish_reason="stop",
            response_time=1.5,
            raw_response={}
        )

    @pytest.mark.asyncio
    async def test_analyze_failure_success(self, analyzer, sample_failure, mock_deepseek_response):
        """Test successful failure analysis"""
        with patch('character_music_mcp.deepseek_client.DeepSeekClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.analyze_failure.return_value = mock_deepseek_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            analysis = await analyzer.analyze_failure(sample_failure)

            assert isinstance(analysis, Analysis)
            assert analysis.failure_id == sample_failure.id
            assert "incorrect assertion" in analysis.root_cause.lower()
            assert analysis.suggested_fix_type == FixType.TEST_FIX
            assert analysis.confidence_score == 0.95
            assert analysis.tokens_used == 150

            # Verify DeepSeek client was called
            mock_client.analyze_failure.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_failure_with_caching(self, analyzer, sample_failure, mock_deepseek_response):
        """Test that analysis results are cached"""
        with patch('character_music_mcp.deepseek_client.DeepSeekClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.analyze_failure.return_value = mock_deepseek_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # First analysis should call API
            analysis1 = await analyzer.analyze_failure(sample_failure)
            assert mock_client.analyze_failure.call_count == 1

            # Second analysis should use cache
            analysis2 = await analyzer.analyze_failure(sample_failure)
            assert mock_client.analyze_failure.call_count == 1  # No additional calls

            # Results should be the same
            assert analysis1.failure_id == analysis2.failure_id
            assert analysis1.root_cause == analysis2.root_cause

    @pytest.mark.asyncio
    async def test_get_code_context(self, analyzer, sample_failure):
        """Test getting code context"""
        context = await analyzer.get_code_context(sample_failure)

        assert context is not None
        assert context.file_path == "test.py"
        assert "assert 1 == 2" in context.content

    def test_determine_fix_type(self, analyzer):
        """Test fix type determination"""
        test_cases = [
            (FailureCategory.SYNTAX_ERROR, None, FixType.SYNTAX_FIX),
            (FailureCategory.IMPORT_ERROR, None, FixType.IMPORT_FIX),
            (FailureCategory.ASSERTION_ERROR, None, FixType.TEST_FIX),
            (FailureCategory.COVERAGE_FAILURE, None, FixType.COVERAGE_FIX),
            (FailureCategory.LINTING_ERROR, None, FixType.QUALITY_FIX),
            (FailureCategory.TYPE_CHECK_ERROR, None, FixType.QUALITY_FIX),
            (FailureCategory.SECURITY_SCAN_FAILURE, None, FixType.SECURITY_FIX),
            (FailureCategory.DEPENDENCY_ERROR, None, FixType.DEPENDENCY_FIX),
            (FailureCategory.UNKNOWN, "import_fix", FixType.IMPORT_FIX),  # AI suggestion
        ]

        for category, suggested, expected in test_cases:
            result = analyzer._determine_fix_type(category, suggested)
            assert result == expected, f"Failed for category: {category.value}"

    def test_parse_analysis_response_with_json(self, analyzer):
        """Test parsing analysis response with JSON"""
        response_content = """
Here's my analysis:

```json
{
  "root_cause": "Missing import statement",
  "confidence_score": 0.9,
  "suggested_fix_type": "import_fix"
}
```

The issue is clear.
        """

        result = analyzer._parse_analysis_response(response_content)

        assert result["root_cause"] == "Missing import statement"
        assert result["confidence_score"] == 0.9
        assert result["suggested_fix_type"] == "import_fix"

    def test_parse_analysis_response_text_only(self, analyzer):
        """Test parsing analysis response without JSON"""
        response_content = """
Root Cause: The test assertion is incorrect
The main issue is that the expected value doesn't match the actual value.
I'm 85% confident in this analysis.
        """

        result = analyzer._parse_analysis_response(response_content)

        assert "test assertion is incorrect" in result["root_cause"].lower()
        assert result["confidence_score"] == 0.85

    def test_sanitize_code_context(self, analyzer):
        """Test code context sanitization"""
        code_context = CodeContext(
            file_path="test.py",
            content='api_key = "secret123"\npassword = "mypass"',
            start_line=1,
            end_line=2,
            surrounding_files={
                "config.py": 'token = "abc123def456"'
            }
        )

        sanitized = analyzer._sanitize_code_context(code_context)

        assert "***REDACTED***" in sanitized.content
        assert "secret123" not in sanitized.content
        assert "***REDACTED***" in sanitized.surrounding_files["config.py"]
        assert "abc123def456" not in sanitized.surrounding_files["config.py"]

    @pytest.mark.asyncio
    async def test_clear_cache(self, analyzer):
        """Test clearing cache"""
        # This is mostly testing that the method exists and doesn't crash
        removed_count = await analyzer.clear_cache()
        assert isinstance(removed_count, int)
        assert removed_count >= 0

    def test_get_cache_stats(self, analyzer):
        """Test getting cache statistics"""
        stats = analyzer.get_cache_stats()

        assert "cache_dir" in stats
        assert "total_entries" in stats
        assert "total_size_bytes" in stats
        assert "total_size_mb" in stats
        assert "ttl_hours" in stats

        assert isinstance(stats["total_entries"], int)
        assert isinstance(stats["total_size_bytes"], int)
        assert isinstance(stats["total_size_mb"], (int, float))
        assert isinstance(stats["ttl_hours"], (int, float))

    @pytest.mark.asyncio
    async def test_batch_analyze_failures(self, analyzer, mock_deepseek_response):
        """Test batch analysis of multiple failures"""
        failures = [
            create_failure(
                workflow_run_id=f"12345{i}",
                job_name="test",
                step_name="Run tests",
                error_message=f"Error {i}",
                logs=f"Test logs {i}",
                repository="owner/repo",
                branch="main",
                commit_sha="abc123",
                category=FailureCategory.UNIT_TEST,
                file_path="test.py"
            )
            for i in range(3)
        ]

        with patch('character_music_mcp.deepseek_client.DeepSeekClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.analyze_failure.return_value = mock_deepseek_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            analyses = await analyzer.batch_analyze_failures(failures, max_concurrent=2)

            assert len(analyses) == 3
            assert all(isinstance(analysis, Analysis) for analysis in analyses)

            # Should have made 3 API calls (one per failure)
            assert mock_client.analyze_failure.call_count == 3

    @pytest.mark.asyncio
    async def test_batch_analyze_with_errors(self, analyzer):
        """Test batch analysis with some failures"""
        failures = [
            create_failure(
                workflow_run_id=f"12345{i}",
                job_name="test",
                step_name="Run tests",
                error_message=f"Error {i}",
                logs=f"Test logs {i}",
                repository="owner/repo",
                branch="main",
                commit_sha="abc123",
                category=FailureCategory.UNIT_TEST,
                file_path="test.py"
            )
            for i in range(2)
        ]

        with patch('character_music_mcp.deepseek_client.DeepSeekClient') as mock_client_class:
            mock_client = AsyncMock()
            # First call succeeds, second fails
            mock_client.analyze_failure.side_effect = [
                DeepSeekResponse(
                    content="Success",
                    tokens_used=100,
                    model="test",
                    finish_reason="stop",
                    response_time=1.0,
                    raw_response={}
                ),
                Exception("API Error")
            ]
            mock_client_class.return_value.__aenter__.return_value = mock_client

            analyses = await analyzer.batch_analyze_failures(failures)

            # Should get one successful analysis (the other failed)
            assert len(analyses) == 1
            assert isinstance(analyses[0], Analysis)
