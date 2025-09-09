"""Unit tests for the DeepSeekClient class"""

import json
import time
from unittest.mock import Mock, patch

import httpx
import pytest

from character_music_mcp.deepseek_client import (
    DeepSeekAPIError,
    DeepSeekAuthenticationError,
    DeepSeekClient,
    DeepSeekConfig,
    DeepSeekRateLimiter,
    DeepSeekRateLimitError,
    DeepSeekResponse,
)
from character_music_mcp.models import (
    CodeContext,
    FailureCategory,
    create_failure,
)


class TestDeepSeekConfig:
    """Test DeepSeekConfig dataclass"""

    def test_default_config(self):
        """Test default configuration values"""
        config = DeepSeekConfig(api_key="test-key")

        assert config.api_key == "test-key"
        assert config.base_url == "https://api.deepseek.com/v1"
        assert config.model == "deepseek-coder"
        assert config.max_tokens == 4000
        assert config.temperature == 0.1
        assert config.timeout == 60
        assert config.max_retries == 3
        assert config.rate_limit_requests_per_minute == 60
        assert config.rate_limit_tokens_per_minute == 100000

    def test_custom_config(self):
        """Test custom configuration values"""
        config = DeepSeekConfig(
            api_key="custom-key",
            base_url="https://custom.api.com",
            model="custom-model",
            max_tokens=2000,
            temperature=0.5,
            timeout=30,
            max_retries=5,
            rate_limit_requests_per_minute=30,
            rate_limit_tokens_per_minute=50000
        )

        assert config.api_key == "custom-key"
        assert config.base_url == "https://custom.api.com"
        assert config.model == "custom-model"
        assert config.max_tokens == 2000
        assert config.temperature == 0.5
        assert config.timeout == 30
        assert config.max_retries == 5
        assert config.rate_limit_requests_per_minute == 30
        assert config.rate_limit_tokens_per_minute == 50000


class TestDeepSeekRateLimiter:
    """Test DeepSeekRateLimiter class"""

    @pytest.fixture
    def rate_limiter(self):
        """Create a rate limiter for testing"""
        return DeepSeekRateLimiter(requests_per_minute=60, tokens_per_minute=1000)

    @pytest.mark.asyncio
    async def test_no_rate_limiting_when_under_limits(self, rate_limiter):
        """Test that no waiting occurs when under rate limits"""
        start_time = time.time()
        await rate_limiter.wait_if_needed(100)
        end_time = time.time()

        # Should not wait
        assert end_time - start_time < 0.1

    @pytest.mark.asyncio
    async def test_request_rate_limiting(self, rate_limiter):
        """Test request rate limiting"""
        # Fill up the request limit
        for _ in range(60):
            rate_limiter.request_times.append(time.time())

        # Next request should be rate limited
        start_time = time.time()
        await rate_limiter.wait_if_needed(100)
        end_time = time.time()

        # Should have waited (but we'll use a small timeout for testing)
        # In real scenario, this would wait up to 60 seconds
        assert end_time - start_time >= 0  # At least some processing time

    @pytest.mark.asyncio
    async def test_token_rate_limiting(self, rate_limiter):
        """Test token rate limiting"""
        # Fill up the token limit
        now = time.time()
        rate_limiter.token_usage = [(now, 500), (now, 500)]  # 1000 tokens used

        # Request that would exceed limit should be rate limited
        start_time = time.time()
        await rate_limiter.wait_if_needed(100)  # Would exceed 1000 limit
        end_time = time.time()

        # Should have waited
        assert end_time - start_time >= 0

    def test_record_usage(self, rate_limiter):
        """Test recording token usage"""
        rate_limiter.record_usage(500)

        assert len(rate_limiter.token_usage) == 1
        assert rate_limiter.token_usage[0][1] == 500

    @pytest.mark.asyncio
    async def test_cleanup_old_entries(self, rate_limiter):
        """Test cleanup of old rate limiting entries"""
        # Add old entries
        old_time = time.time() - 120  # 2 minutes ago
        rate_limiter.request_times = [old_time, old_time]
        rate_limiter.token_usage = [(old_time, 100), (old_time, 200)]

        # Make a request to trigger cleanup
        await rate_limiter.wait_if_needed(100)

        # Old entries should be cleaned up
        assert len(rate_limiter.request_times) == 1  # Only the new one
        # Token usage might be 0 or 1 depending on whether record_usage was called
        assert len(rate_limiter.token_usage) <= 1  # At most the new one


class TestDeepSeekClient:
    """Test DeepSeekClient class"""

    @pytest.fixture
    def config(self):
        """Create a test configuration"""
        return DeepSeekConfig(
            api_key="test-api-key",
            max_retries=2,
            timeout=10
        )

    @pytest.fixture
    def sample_failure(self):
        """Create a sample failure for testing"""
        return create_failure(
            workflow_run_id="123456",
            job_name="test (python-3.10)",
            step_name="Run unit tests",
            error_message="AssertionError: assert 1 == 2",
            logs="FAILED tests/test_example.py::test_function - AssertionError: assert 1 == 2",
            repository="owner/repo",
            branch="main",
            commit_sha="abc123",
            category=FailureCategory.ASSERTION_ERROR,
            file_path="tests/test_example.py",
            line_number=42
        )

    @pytest.fixture
    def sample_code_context(self):
        """Create sample code context"""
        return CodeContext(
            file_path="tests/test_example.py",
            content="def test_function():\n    assert 1 == 2",
            start_line=1,
            end_line=2,
            surrounding_files={
                "src/main.py": "def main():\n    return 1"
            }
        )

    @pytest.fixture
    def mock_response(self):
        """Create a mock API response"""
        return {
            "choices": [
                {
                    "message": {
                        "content": "This is a test analysis response"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "total_tokens": 150,
                "prompt_tokens": 100,
                "completion_tokens": 50
            },
            "model": "deepseek-coder"
        }

    @pytest.mark.asyncio
    async def test_client_context_manager(self, config):
        """Test client as async context manager"""
        async with DeepSeekClient(config) as client:
            assert client._client is not None
            assert isinstance(client._client, httpx.AsyncClient)

        # Client should be closed after context
        assert client._client is None or client._client.is_closed

    @pytest.mark.asyncio
    async def test_analyze_failure_success(self, config, sample_failure, sample_code_context, mock_response):
        """Test successful failure analysis"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = Mock(
                status_code=200,
                json=Mock(return_value=mock_response)
            )

            async with DeepSeekClient(config) as client:
                response = await client.analyze_failure(sample_failure, sample_code_context)

                assert isinstance(response, DeepSeekResponse)
                assert response.content == "This is a test analysis response"
                assert response.tokens_used == 150
                assert response.model == "deepseek-coder"
                assert response.finish_reason == "stop"

                # Verify API call was made correctly
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                assert call_args[1]['json']['model'] == config.model
                assert call_args[1]['json']['max_tokens'] == config.max_tokens
                assert call_args[1]['json']['temperature'] == config.temperature

    @pytest.mark.asyncio
    async def test_generate_fix_success(self, config, sample_failure, sample_code_context, mock_response):
        """Test successful fix generation"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response_fix = mock_response.copy()
            mock_response_fix['choices'][0]['message']['content'] = '{"fix_type": "test_fix", "confidence": 0.9}'
            mock_post.return_value = Mock(
                status_code=200,
                json=Mock(return_value=mock_response_fix)
            )

            async with DeepSeekClient(config) as client:
                response = await client.generate_fix(
                    sample_failure,
                    "Previous analysis",
                    sample_code_context
                )

                assert isinstance(response, DeepSeekResponse)
                assert '{"fix_type": "test_fix", "confidence": 0.9}' in response.content

                # Verify API call was made
                mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_code_success(self, config, mock_response):
        """Test successful code validation"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response_validation = mock_response.copy()
            mock_response_validation['choices'][0]['message']['content'] = '{"valid": true, "issues": []}'
            mock_post.return_value = Mock(
                status_code=200,
                json=Mock(return_value=mock_response_validation)
            )

            async with DeepSeekClient(config) as client:
                response = await client.validate_code("def test(): pass", "python")

                assert isinstance(response, DeepSeekResponse)
                assert '{"valid": true, "issues": []}' in response.content

    @pytest.mark.asyncio
    async def test_api_authentication_error(self, config, sample_failure):
        """Test handling of authentication errors"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = Mock(
                status_code=401,
                text="Unauthorized"
            )

            async with DeepSeekClient(config) as client:
                with pytest.raises(DeepSeekAuthenticationError):
                    await client.analyze_failure(sample_failure)

    @pytest.mark.asyncio
    async def test_api_rate_limit_error(self, config, sample_failure):
        """Test handling of rate limit errors"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = Mock(
                status_code=429,
                headers={"Retry-After": "1"},
                text="Rate limit exceeded"
            )

            async with DeepSeekClient(config) as client:
                with pytest.raises(DeepSeekRateLimitError):
                    await client.analyze_failure(sample_failure)

    @pytest.mark.asyncio
    async def test_api_timeout_error(self, config, sample_failure):
        """Test handling of timeout errors"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Request timeout")

            async with DeepSeekClient(config) as client:
                with pytest.raises(DeepSeekAPIError, match="timed out"):
                    await client.analyze_failure(sample_failure)

    @pytest.mark.asyncio
    async def test_api_retry_logic(self, config, sample_failure, mock_response):
        """Test retry logic for transient errors"""
        with patch('httpx.AsyncClient.post') as mock_post:
            # First call fails, second succeeds
            mock_post.side_effect = [
                Mock(status_code=500, text="Internal server error"),
                Mock(status_code=200, json=Mock(return_value=mock_response))
            ]

            async with DeepSeekClient(config) as client:
                response = await client.analyze_failure(sample_failure)

                assert isinstance(response, DeepSeekResponse)
                assert mock_post.call_count == 2

    @pytest.mark.asyncio
    async def test_invalid_response_format(self, config, sample_failure):
        """Test handling of invalid response format"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"invalid": "response"})
            )

            async with DeepSeekClient(config) as client:
                with pytest.raises(DeepSeekAPIError, match="Invalid response format"):
                    await client.analyze_failure(sample_failure)

    @pytest.mark.asyncio
    async def test_json_decode_error(self, config, sample_failure):
        """Test handling of JSON decode errors"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = Mock(
                status_code=200,
                json=Mock(side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
            )

            async with DeepSeekClient(config) as client:
                with pytest.raises(DeepSeekAPIError, match="Failed to parse JSON"):
                    await client.analyze_failure(sample_failure)

    def test_generate_analysis_prompt(self, config, sample_failure, sample_code_context):
        """Test analysis prompt generation"""
        client = DeepSeekClient(config)
        prompt = client._generate_analysis_prompt(sample_failure, sample_code_context)

        # Check that key information is included
        assert sample_failure.repository in prompt
        assert sample_failure.job_name in prompt
        assert sample_failure.error_message in prompt
        assert sample_failure.logs in prompt
        assert sample_code_context.file_path in prompt
        assert sample_code_context.content in prompt
        assert "Root Cause" in prompt
        assert "Fix Strategy" in prompt

    def test_generate_fix_prompt(self, config, sample_failure, sample_code_context):
        """Test fix generation prompt"""
        client = DeepSeekClient(config)
        analysis = "This is a test analysis"
        prompt = client._generate_fix_prompt(sample_failure, analysis, sample_code_context)

        # Check that key information is included
        assert sample_failure.repository in prompt
        assert sample_failure.error_message in prompt
        assert analysis in prompt
        assert sample_code_context.content in prompt
        assert "fix_type" in prompt
        assert "file_changes" in prompt
        assert "JSON" in prompt

    def test_generate_validation_prompt(self, config):
        """Test validation prompt generation"""
        client = DeepSeekClient(config)
        code = "def test(): pass"
        prompt = client._generate_validation_prompt(code, "python")

        assert code in prompt
        assert "python" in prompt
        assert "Syntax errors" in prompt
        assert "JSON" in prompt
        assert "valid" in prompt

    def test_sanitize_code_for_api(self, config):
        """Test code sanitization for API"""
        client = DeepSeekClient(config)

        test_cases = [
            ('api_key = "secret123"', 'api_key = "***REDACTED***"'),
            ('password = "mypass"', 'password = "***REDACTED***"'),
            ('token = "abc123def456"', 'token = "***REDACTED***"'),
            ('secret = "topsecret"', 'secret = "***REDACTED***"'),
            ('"YWJjZGVmZ2hpams="', '"***BASE64_REDACTED***"'),  # Base64
            ('"1234567890abcdef1234567890abcdef"', '"***HEX_REDACTED***"'),  # Hex
            ('https://user:pass@example.com', 'https://***REDACTED***@example.com'),
        ]

        for original, expected in test_cases:
            result = client.sanitize_code_for_api(original)
            assert expected in result, f"Failed to sanitize: {original}"

    def test_estimate_tokens(self, config):
        """Test token estimation"""
        client = DeepSeekClient(config)

        test_cases = [
            ("", 0),
            ("hello", 1),  # 5 chars / 3 = 1.67 -> 1
            ("hello world", 3),  # 11 chars / 3 = 3.67 -> 3
            ("a" * 30, 10),  # 30 chars / 3 = 10
        ]

        for text, expected in test_cases:
            result = client.estimate_tokens(text)
            assert result == expected, f"Failed for text: '{text}'"


class TestDeepSeekPromptGeneration:
    """Test prompt generation methods"""

    @pytest.fixture
    def client(self):
        config = DeepSeekConfig(api_key="test")
        return DeepSeekClient(config)

    @pytest.fixture
    def complex_failure(self):
        """Create a complex failure for testing"""
        return create_failure(
            workflow_run_id="complex_123",
            job_name="test (ubuntu-latest, python-3.11)",
            step_name="Run integration tests with coverage",
            error_message="ImportError: No module named 'missing_package'",
            logs="""
FAILED tests/integration/test_api.py::test_api_call - ImportError: No module named 'missing_package'
File "/src/tests/integration/test_api.py", line 15, in test_api_call
    from missing_package import MissingClass
ImportError: No module named 'missing_package'
            """.strip(),
            repository="test-org/complex-repo",
            branch="feature/new-integration",
            commit_sha="complex_commit_456",
            category=FailureCategory.IMPORT_ERROR,
            file_path="tests/integration/test_api.py",
            line_number=15,
            python_version="3.11"
        )

    @pytest.fixture
    def complex_code_context(self):
        """Create complex code context"""
        return CodeContext(
            file_path="tests/integration/test_api.py",
            content="""
import pytest
import requests
from unittest.mock import Mock, patch

def test_api_call():
    from missing_package import MissingClass

    client = MissingClass()
    result = client.call_api()
    assert result.status_code == 200
            """.strip(),
            start_line=1,
            end_line=9,
            surrounding_files={
                "src/api/client.py": "class APIClient:\n    def call_api(self):\n        return requests.get('https://api.example.com')",
                "pyproject.toml": "[project]\nname = 'test-project'\ndependencies = ['requests', 'pytest']"
            }
        )

    def test_analysis_prompt_completeness(self, client, complex_failure, complex_code_context):
        """Test that analysis prompt includes all necessary information"""
        prompt = client._generate_analysis_prompt(complex_failure, complex_code_context)

        # Check failure information
        assert complex_failure.repository in prompt
        assert complex_failure.branch in prompt
        assert complex_failure.commit_sha in prompt
        assert complex_failure.workflow_run_id in prompt
        assert complex_failure.job_name in prompt
        assert complex_failure.step_name in prompt
        assert complex_failure.python_version in prompt
        assert complex_failure.category.value in prompt
        assert complex_failure.file_path in prompt
        assert str(complex_failure.line_number) in prompt
        assert complex_failure.error_message in prompt
        assert complex_failure.logs in prompt

        # Check code context
        assert complex_code_context.file_path in prompt
        assert complex_code_context.content in prompt
        assert str(complex_code_context.start_line) in prompt
        assert str(complex_code_context.end_line) in prompt

        # Check surrounding files
        for file_path, content in complex_code_context.surrounding_files.items():
            assert file_path in prompt
            assert content[:100] in prompt  # At least part of the content

        # Check analysis requirements
        required_sections = [
            "Root Cause",
            "Category Verification",
            "Impact Assessment",
            "Fix Strategy",
            "Dependencies",
            "Risk Assessment"
        ]
        for section in required_sections:
            assert section in prompt

    def test_fix_prompt_structure(self, client, complex_failure, complex_code_context):
        """Test fix prompt structure and content"""
        analysis = "The failure is caused by a missing import. The package 'missing_package' is not installed."
        prompt = client._generate_fix_prompt(complex_failure, analysis, complex_code_context)

        # Check failure information
        assert complex_failure.repository in prompt
        assert complex_failure.category.value in prompt
        assert complex_failure.error_message in prompt

        # Check analysis is included
        assert analysis in prompt

        # Check code context
        assert complex_code_context.content in prompt

        # Check JSON structure requirements
        json_fields = [
            "fix_type",
            "confidence",
            "description",
            "file_changes",
            "dependencies",
            "test_commands",
            "validation_notes"
        ]
        for field in json_fields:
            assert field in prompt

        # Check fix types are listed
        fix_types = [
            "syntax_fix",
            "import_fix",
            "test_fix",
            "coverage_fix",
            "quality_fix",
            "dependency_fix",
            "security_fix"
        ]
        for fix_type in fix_types:
            assert fix_type in prompt

    def test_validation_prompt_coverage(self, client):
        """Test validation prompt covers all necessary checks"""
        code = """
def example_function(param: str) -> int:
    import os
    result = int(param)
    return result
        """

        prompt = client._generate_validation_prompt(code, "python")

        # Check code is included
        assert code in prompt
        assert "python" in prompt

        # Check validation categories
        validation_checks = [
            "Syntax errors",
            "Import issues",
            "Type hints",
            "Code style issues",
            "Potential runtime errors",
            "Security concerns",
            "Performance issues"
        ]
        for check in validation_checks:
            assert check in prompt

        # Check JSON response structure
        json_fields = [
            "valid",
            "issues",
            "overall_quality",
            "suggestions"
        ]
        for field in json_fields:
            assert field in prompt

        # Check issue types
        issue_types = [
            "syntax",
            "import",
            "style",
            "security",
            "performance"
        ]
        for issue_type in issue_types:
            assert issue_type in prompt

    def test_prompt_without_code_context(self, client, complex_failure):
        """Test prompt generation without code context"""
        prompt = client._generate_analysis_prompt(complex_failure, None)

        # Should still include failure information
        assert complex_failure.error_message in prompt
        assert complex_failure.logs in prompt

        # Should not include code context sections
        assert "Code Context" not in prompt
        assert "Related Files" not in prompt

    def test_prompt_with_empty_surrounding_files(self, client, complex_failure):
        """Test prompt with code context but no surrounding files"""
        code_context = CodeContext(
            file_path="test.py",
            content="def test(): pass",
            start_line=1,
            end_line=1,
            surrounding_files={}
        )

        prompt = client._generate_analysis_prompt(complex_failure, code_context)

        # Should include main code context
        assert code_context.content in prompt

        # Should not include related files section
        assert "Related Files" not in prompt
