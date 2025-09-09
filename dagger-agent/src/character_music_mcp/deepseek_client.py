"""DeepSeek API Client

This module implements the DeepSeekClient class for interacting with the DeepSeek API
to analyze test failures and generate fixes using AI-powered analysis.
"""

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any

import httpx
import structlog
from httpx import AsyncClient, Response

from .models import CodeContext, Failure

logger = structlog.get_logger(__name__)


@dataclass
class DeepSeekConfig:
    """Configuration for DeepSeek API client"""
    api_key: str
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-coder"
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout: int = 60
    max_retries: int = 3
    rate_limit_requests_per_minute: int = 60
    rate_limit_tokens_per_minute: int = 100000


@dataclass
class DeepSeekResponse:
    """Response from DeepSeek API"""
    content: str
    tokens_used: int
    model: str
    finish_reason: str
    response_time: float
    raw_response: dict[str, Any]


class DeepSeekRateLimiter:
    """Rate limiter for DeepSeek API calls"""

    def __init__(self, requests_per_minute: int, tokens_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        self.request_times: list[float] = []
        self.token_usage: list[tuple[float, int]] = []  # (timestamp, tokens)
        self._lock = asyncio.Lock()

    async def wait_if_needed(self, estimated_tokens: int = 1000) -> None:
        """Wait if rate limits would be exceeded"""
        async with self._lock:
            now = time.time()

            # Clean old entries (older than 1 minute)
            cutoff = now - 60
            self.request_times = [t for t in self.request_times if t > cutoff]
            self.token_usage = [(t, tokens) for t, tokens in self.token_usage if t > cutoff]

            # Check request rate limit
            if len(self.request_times) >= self.requests_per_minute:
                wait_time = 60 - (now - self.request_times[0])
                if wait_time > 0:
                    logger.info("Rate limit reached, waiting", wait_time=wait_time)
                    await asyncio.sleep(wait_time)

            # Check token rate limit
            current_tokens = sum(tokens for _, tokens in self.token_usage)
            if current_tokens + estimated_tokens > self.tokens_per_minute:
                # Find when we can make the request
                tokens_needed = current_tokens + estimated_tokens - self.tokens_per_minute
                for timestamp, tokens in sorted(self.token_usage):
                    tokens_needed -= tokens
                    if tokens_needed <= 0:
                        wait_time = 60 - (now - timestamp)
                        if wait_time > 0:
                            logger.info("Token rate limit reached, waiting", wait_time=wait_time)
                            await asyncio.sleep(wait_time)
                        break

            # Record this request
            self.request_times.append(now)

    def record_usage(self, tokens_used: int) -> None:
        """Record token usage for rate limiting"""
        self.token_usage.append((time.time(), tokens_used))


class DeepSeekAPIError(Exception):
    """Base exception for DeepSeek API errors"""
    pass


class DeepSeekRateLimitError(DeepSeekAPIError):
    """Rate limit exceeded error"""
    pass


class DeepSeekAuthenticationError(DeepSeekAPIError):
    """Authentication error"""
    pass


class DeepSeekClient:
    """Client for interacting with DeepSeek API"""

    def __init__(self, config: DeepSeekConfig):
        """Initialize the DeepSeek client"""
        self.config = config
        self.rate_limiter = DeepSeekRateLimiter(
            config.rate_limit_requests_per_minute,
            config.rate_limit_tokens_per_minute
        )
        self._client: AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry"""
        self._client = AsyncClient(
            timeout=httpx.Timeout(self.config.timeout),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._client:
            await self._client.aclose()

    async def analyze_failure(
        self,
        failure: Failure,
        code_context: CodeContext | None = None
    ) -> DeepSeekResponse:
        """
        Analyze a test failure using DeepSeek API
        
        Args:
            failure: The failure to analyze
            code_context: Optional code context for better analysis
            
        Returns:
            DeepSeek API response with analysis
        """
        prompt = self._generate_analysis_prompt(failure, code_context)

        logger.info(
            "Analyzing failure with DeepSeek",
            failure_id=failure.id,
            category=failure.category.value if hasattr(failure.category, 'value') else failure.category,
            prompt_length=len(prompt)
        )

        return await self._make_api_call(prompt, "analyze_failure")

    async def generate_fix(
        self,
        failure: Failure,
        analysis: str,
        code_context: CodeContext | None = None
    ) -> DeepSeekResponse:
        """
        Generate a fix for a failure using DeepSeek API
        
        Args:
            failure: The failure to fix
            analysis: Previous analysis of the failure
            code_context: Code context for generating the fix
            
        Returns:
            DeepSeek API response with fix suggestion
        """
        prompt = self._generate_fix_prompt(failure, analysis, code_context)

        logger.info(
            "Generating fix with DeepSeek",
            failure_id=failure.id,
            category=failure.category.value if hasattr(failure.category, 'value') else failure.category,
            prompt_length=len(prompt)
        )

        return await self._make_api_call(prompt, "generate_fix")

    async def validate_code(self, code: str, language: str = "python") -> DeepSeekResponse:
        """
        Validate code syntax and quality using DeepSeek API
        
        Args:
            code: Code to validate
            language: Programming language (default: python)
            
        Returns:
            DeepSeek API response with validation results
        """
        prompt = self._generate_validation_prompt(code, language)

        logger.info(
            "Validating code with DeepSeek",
            language=language,
            code_length=len(code)
        )

        return await self._make_api_call(prompt, "validate_code")

    async def _make_api_call(
        self,
        prompt: str,
        operation: str,
        max_retries: int | None = None
    ) -> DeepSeekResponse:
        """
        Make an API call to DeepSeek with retry logic
        
        Args:
            prompt: The prompt to send
            operation: Operation name for logging
            max_retries: Maximum number of retries (uses config default if None)
            
        Returns:
            DeepSeek API response
        """
        if not self._client:
            raise DeepSeekAPIError("Client not initialized. Use async context manager.")

        max_retries = max_retries or self.config.max_retries
        estimated_tokens = len(prompt.split()) * 2  # Rough estimate

        for attempt in range(max_retries + 1):
            try:
                # Wait for rate limiting
                await self.rate_limiter.wait_if_needed(estimated_tokens)

                # Prepare request
                payload = {
                    "model": self.config.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert Python developer and test automation specialist. Analyze the provided information carefully and provide precise, actionable solutions."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "stream": False
                }

                start_time = time.time()

                # Make the API call
                response = await self._client.post(
                    f"{self.config.base_url}/chat/completions",
                    json=payload
                )

                response_time = time.time() - start_time

                # Handle response
                if response.status_code == 200:
                    return self._parse_response(response, response_time, operation)
                elif response.status_code == 429:
                    # Rate limit exceeded
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(
                        "Rate limit exceeded",
                        operation=operation,
                        attempt=attempt + 1,
                        retry_after=retry_after
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(retry_after)
                        continue
                    else:
                        raise DeepSeekRateLimitError(f"Rate limit exceeded after {max_retries} retries")
                elif response.status_code == 401:
                    raise DeepSeekAuthenticationError("Invalid API key")
                else:
                    error_msg = f"API call failed with status {response.status_code}: {response.text}"
                    logger.error(
                        "API call failed",
                        operation=operation,
                        status_code=response.status_code,
                        response_text=response.text
                    )
                    if attempt < max_retries:
                        wait_time = 2 ** attempt  # Exponential backoff
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise DeepSeekAPIError(error_msg)

            except httpx.TimeoutException:
                logger.warning(
                    "API call timeout",
                    operation=operation,
                    attempt=attempt + 1,
                    timeout=self.config.timeout
                )
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise DeepSeekAPIError(f"API call timed out after {max_retries} retries")

            except Exception as e:
                logger.error(
                    "Unexpected error in API call",
                    operation=operation,
                    attempt=attempt + 1,
                    error=str(e)
                )
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise DeepSeekAPIError(f"Unexpected error: {str(e)}")

        raise DeepSeekAPIError(f"Failed to complete API call after {max_retries} retries")

    def _parse_response(self, response: Response, response_time: float, operation: str) -> DeepSeekResponse:
        """Parse DeepSeek API response"""
        try:
            data = response.json()

            if "choices" not in data or not data["choices"]:
                raise DeepSeekAPIError("Invalid response format: no choices")

            choice = data["choices"][0]
            content = choice.get("message", {}).get("content", "")
            finish_reason = choice.get("finish_reason", "unknown")

            usage = data.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)

            # Record token usage for rate limiting
            self.rate_limiter.record_usage(tokens_used)

            logger.info(
                "API call successful",
                operation=operation,
                tokens_used=tokens_used,
                response_time=response_time,
                finish_reason=finish_reason
            )

            return DeepSeekResponse(
                content=content,
                tokens_used=tokens_used,
                model=data.get("model", self.config.model),
                finish_reason=finish_reason,
                response_time=response_time,
                raw_response=data
            )

        except json.JSONDecodeError as e:
            raise DeepSeekAPIError(f"Failed to parse JSON response: {str(e)}")
        except KeyError as e:
            raise DeepSeekAPIError(f"Missing key in response: {str(e)}")

    def _generate_analysis_prompt(
        self,
        failure: Failure,
        code_context: CodeContext | None = None
    ) -> str:
        """Generate prompt for failure analysis"""
        prompt = f"""
Analyze the following test failure and provide a detailed analysis:

## Failure Information
- **Repository**: {failure.repository}
- **Branch**: {failure.branch}
- **Commit**: {failure.commit_sha}
- **Workflow Run**: {failure.workflow_run_id}
- **Job**: {failure.job_name}
- **Step**: {failure.step_name}
- **Python Version**: {failure.python_version or 'Unknown'}
- **Category**: {failure.category.value if hasattr(failure.category, 'value') else failure.category}
- **File**: {failure.file_path or 'Unknown'}
- **Line**: {failure.line_number or 'Unknown'}

## Error Message
```
{failure.error_message}
```

## Logs
```
{failure.logs}
```
"""

        if code_context:
            prompt += f"""
## Code Context
**File**: {code_context.file_path}
**Lines**: {code_context.start_line}-{code_context.end_line}

```python
{code_context.content}
```
"""

            if code_context.surrounding_files:
                prompt += "\n## Related Files\n"
                for file_path, content in code_context.surrounding_files.items():
                    prompt += f"\n**{file_path}**:\n```python\n{content[:1000]}...\n```\n"

        prompt += """
## Analysis Required
Please provide:

1. **Root Cause**: What is the primary cause of this failure?
2. **Category Verification**: Is the failure category correct? If not, what should it be?
3. **Impact Assessment**: How severe is this issue?
4. **Fix Strategy**: What approach should be taken to fix this?
5. **Dependencies**: Are there any dependencies or prerequisites for the fix?
6. **Risk Assessment**: What are the risks of applying a fix?

Please be specific and actionable in your analysis. Focus on Python best practices and testing standards.
"""

        return prompt

    def _generate_fix_prompt(
        self,
        failure: Failure,
        analysis: str,
        code_context: CodeContext | None = None
    ) -> str:
        """Generate prompt for fix generation"""
        prompt = f"""
Generate a fix for the following test failure based on the analysis provided:

## Failure Information
- **Repository**: {failure.repository}
- **Category**: {failure.category.value if hasattr(failure.category, 'value') else failure.category}
- **File**: {failure.file_path or 'Unknown'}
- **Line**: {failure.line_number or 'Unknown'}
- **Error**: {failure.error_message}

## Previous Analysis
{analysis}

## Current Code
"""

        if code_context:
            prompt += f"""
**File**: {code_context.file_path}
**Lines**: {code_context.start_line}-{code_context.end_line}

```python
{code_context.content}
```
"""

            if code_context.surrounding_files:
                prompt += "\n## Related Files\n"
                for file_path, content in code_context.surrounding_files.items():
                    prompt += f"\n**{file_path}**:\n```python\n{content[:500]}...\n```\n"

        prompt += """
## Fix Requirements
Please provide a complete fix that includes:

1. **Modified Code**: The exact code changes needed
2. **File Changes**: List all files that need to be modified
3. **New Files**: Any new files that need to be created
4. **Dependencies**: Any new dependencies to add to pyproject.toml
5. **Test Commands**: Commands to verify the fix works
6. **Validation Steps**: How to validate the fix doesn't break anything else

## Output Format
Please structure your response as JSON:

```json
{
  "fix_type": "syntax_fix|import_fix|test_fix|coverage_fix|quality_fix|dependency_fix|security_fix",
  "confidence": 0.95,
  "description": "Brief description of the fix",
  "file_changes": [
    {
      "file_path": "path/to/file.py",
      "change_type": "modify|create|delete",
      "original_content": "original code if modifying",
      "new_content": "new code content",
      "line_start": 10,
      "line_end": 15
    }
  ],
  "dependencies": [
    {
      "name": "package-name",
      "version": ">=1.0.0",
      "dev": false
    }
  ],
  "test_commands": [
    "pytest tests/test_specific.py -v",
    "ruff check ."
  ],
  "validation_notes": "Additional notes about validating the fix"
}
```

Focus on minimal, safe changes that directly address the root cause.
"""

        return prompt

    def _generate_validation_prompt(self, code: str, language: str) -> str:
        """Generate prompt for code validation"""
        return f"""
Validate the following {language} code for syntax errors, potential issues, and best practices:

```{language}
{code}
```

Please check for:
1. Syntax errors
2. Import issues
3. Type hints (if applicable)
4. Code style issues
5. Potential runtime errors
6. Security concerns
7. Performance issues

Provide a JSON response with:
```json
{{
  "valid": true/false,
  "issues": [
    {{
      "type": "syntax|import|style|security|performance",
      "severity": "error|warning|info",
      "line": 10,
      "message": "Description of the issue",
      "suggestion": "How to fix it"
    }}
  ],
  "overall_quality": "excellent|good|fair|poor",
  "suggestions": ["List of general improvements"]
}}
```
"""

    def sanitize_code_for_api(self, code: str) -> str:
        """
        Sanitize code before sending to API to remove sensitive information
        
        Args:
            code: Code to sanitize
            
        Returns:
            Sanitized code
        """
        import re

        # Patterns for sensitive information
        sensitive_patterns = [
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'api_key = "***REDACTED***"'),
            (r'password\s*=\s*["\'][^"\']+["\']', 'password = "***REDACTED***"'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'token = "***REDACTED***"'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'secret = "***REDACTED***"'),
            (r'key\s*=\s*["\'][^"\']+["\']', 'key = "***REDACTED***"'),
            (r'["\'][A-Za-z0-9+/]{16,}={0,2}["\']', '"***BASE64_REDACTED***"'),  # Base64 encoded
            (r'["\'][0-9a-fA-F]{32,}["\']', '"***HEX_REDACTED***"'),  # Hex strings (likely keys)
            (r'https?://[^/]+:[^@]+@', 'https://***REDACTED***@'),  # URLs with credentials
        ]

        sanitized = code
        for pattern, replacement in sensitive_patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        return sanitized

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation)
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters for English text
        # For code, it's often closer to 1 token ≈ 3 characters
        return len(text) // 3
