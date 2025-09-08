"""Failure Analyzer

This module implements the FailureAnalyzer class that uses DeepSeek API to analyze
test failures, extract code context, and provide AI-powered analysis with caching.
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime, UTC, timedelta
import structlog

from .models import (
    Failure, Analysis, CodeContext, FailureCategory, FixType,
    create_analysis
)
from .deepseek_client import DeepSeekClient, DeepSeekConfig, DeepSeekResponse

logger = structlog.get_logger(__name__)


class CodeContextExtractor:
    """Extracts code context for failure analysis"""
    
    def __init__(self, repository_path: str = "."):
        """
        Initialize code context extractor
        
        Args:
            repository_path: Path to the repository root
        """
        self.repository_path = Path(repository_path)
    
    async def extract_context(
        self,
        failure: Failure,
        context_lines: int = 10,
        max_file_size: int = 10000
    ) -> Optional[CodeContext]:
        """
        Extract code context for a failure
        
        Args:
            failure: The failure to extract context for
            context_lines: Number of lines to include around the error
            max_file_size: Maximum file size to read (in characters)
            
        Returns:
            CodeContext if file exists and is readable, None otherwise
        """
        if not failure.file_path:
            logger.warning("No file path in failure", failure_id=failure.id)
            return None
        
        file_path = self.repository_path / failure.file_path
        
        if not file_path.exists():
            logger.warning(
                "File not found for failure",
                failure_id=failure.id,
                file_path=str(file_path)
            )
            return None
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(max_file_size)
            
            lines = content.split('\n')
            total_lines = len(lines)
            
            # Determine line range
            if failure.line_number:
                center_line = failure.line_number
                start_line = max(1, center_line - context_lines)
                end_line = min(total_lines, center_line + context_lines)
            else:
                # If no specific line, include the whole file (up to max_file_size)
                start_line = 1
                end_line = total_lines
            
            # Extract the relevant content
            relevant_lines = lines[start_line-1:end_line]
            relevant_content = '\n'.join(relevant_lines)
            
            # Get surrounding files
            surrounding_files = await self._get_surrounding_files(
                failure, max_files=5, max_file_size=max_file_size // 5
            )
            
            return CodeContext(
                file_path=failure.file_path,
                content=relevant_content,
                start_line=start_line,
                end_line=end_line,
                surrounding_files=surrounding_files
            )
            
        except Exception as e:
            logger.error(
                "Failed to extract code context",
                failure_id=failure.id,
                file_path=str(file_path),
                error=str(e)
            )
            return None
    
    async def _get_surrounding_files(
        self,
        failure: Failure,
        max_files: int = 5,
        max_file_size: int = 2000
    ) -> Dict[str, str]:
        """Get content of related files for context"""
        surrounding_files = {}
        
        if not failure.file_path:
            return surrounding_files
        
        file_path = Path(failure.file_path)
        file_dir = file_path.parent
        
        # Files to look for based on failure type and location
        candidate_files = []
        
        # Always include pyproject.toml for dependency context
        candidate_files.append("pyproject.toml")
        
        # Include __init__.py files in the same directory
        init_file = file_dir / "__init__.py"
        if init_file != Path(failure.file_path):
            candidate_files.append(str(init_file))
        
        # For test files, include the corresponding source file
        if "test" in failure.file_path.lower():
            # Try to find corresponding source file
            source_candidates = [
                failure.file_path.replace("tests/", "src/").replace("test_", ""),
                failure.file_path.replace("tests/", "").replace("test_", ""),
                failure.file_path.replace("test_", "").replace("tests/", "src/"),
            ]
            candidate_files.extend(source_candidates)
        
        # For source files, include related test files
        else:
            test_candidates = [
                f"tests/test_{file_path.name}",
                f"tests/{file_path.parent}/test_{file_path.name}",
                f"test_{file_path.name}",
            ]
            candidate_files.extend(test_candidates)
        
        # Include configuration files
        config_files = [
            "setup.py",
            "setup.cfg", 
            "tox.ini",
            "pytest.ini",
            ".coveragerc",
            "mypy.ini",
            "ruff.toml",
            ".pre-commit-config.yaml"
        ]
        candidate_files.extend(config_files)
        
        # Read the files that exist
        files_added = 0
        for candidate in candidate_files:
            if files_added >= max_files:
                break
                
            candidate_path = self.repository_path / candidate
            
            if candidate_path.exists() and candidate_path.is_file():
                try:
                    with open(candidate_path, 'r', encoding='utf-8') as f:
                        content = f.read(max_file_size)
                    
                    surrounding_files[candidate] = content
                    files_added += 1
                    
                except Exception as e:
                    logger.debug(
                        "Could not read surrounding file",
                        file_path=str(candidate_path),
                        error=str(e)
                    )
        
        return surrounding_files


class AnalysisCache:
    """Cache for analysis results to reduce API usage"""
    
    def __init__(self, cache_dir: str = ".cache/analysis", ttl_hours: int = 24):
        """
        Initialize analysis cache
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time to live for cache entries in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_cache_key(self, failure: Failure, code_context: Optional[CodeContext]) -> str:
        """Generate cache key for a failure and context"""
        # Create a hash of the failure details and code context
        key_data = {
            "error_message": failure.error_message,
            "logs": failure.logs,
            "category": failure.category.value,
            "file_path": failure.file_path,
            "line_number": failure.line_number,
        }
        
        if code_context:
            key_data.update({
                "code_content": code_context.content,
                "start_line": code_context.start_line,
                "end_line": code_context.end_line,
            })
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get(self, failure: Failure, code_context: Optional[CodeContext]) -> Optional[Analysis]:
        """Get cached analysis if available and not expired"""
        cache_key = self._get_cache_key(failure, code_context)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached_data['cached_at'])
            if datetime.now(UTC) - cached_time > self.ttl:
                logger.debug("Cache entry expired", cache_key=cache_key)
                cache_file.unlink()  # Remove expired cache
                return None
            
            # Reconstruct Analysis object
            analysis_data = cached_data['analysis']
            
            # Reconstruct CodeContext if present
            code_context_data = analysis_data.get('code_context')
            if code_context_data:
                code_context_obj = CodeContext(**code_context_data)
            else:
                code_context_obj = code_context  # Use provided context
            
            analysis = Analysis(
                failure_id=analysis_data['failure_id'],
                root_cause=analysis_data['root_cause'],
                suggested_fix_type=FixType(analysis_data['suggested_fix_type']),
                confidence_score=analysis_data['confidence_score'],
                code_context=code_context_obj,
                deepseek_response=analysis_data['deepseek_response'],
                analysis_prompt=analysis_data['analysis_prompt'],
                tokens_used=analysis_data.get('tokens_used', 0),
                created_at=datetime.fromisoformat(analysis_data['created_at'])
            )
            
            logger.info("Using cached analysis", failure_id=failure.id, cache_key=cache_key)
            return analysis
            
        except Exception as e:
            logger.warning(
                "Failed to load cached analysis",
                cache_key=cache_key,
                error=str(e)
            )
            # Remove corrupted cache file
            if cache_file.exists():
                cache_file.unlink()
            return None
    
    def set(self, failure: Failure, analysis: Analysis, code_context: Optional[CodeContext]) -> None:
        """Cache analysis result"""
        cache_key = self._get_cache_key(failure, code_context)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            # Prepare data for caching
            cache_data = {
                "cached_at": datetime.now(UTC).isoformat(),
                "analysis": {
                    "failure_id": analysis.failure_id,
                    "root_cause": analysis.root_cause,
                    "suggested_fix_type": analysis.suggested_fix_type.value,
                    "confidence_score": analysis.confidence_score,
                    "code_context": {
                        "file_path": analysis.code_context.file_path,
                        "content": analysis.code_context.content,
                        "start_line": analysis.code_context.start_line,
                        "end_line": analysis.code_context.end_line,
                        "surrounding_files": analysis.code_context.surrounding_files,
                    } if analysis.code_context else None,
                    "deepseek_response": analysis.deepseek_response,
                    "analysis_prompt": analysis.analysis_prompt,
                    "tokens_used": analysis.tokens_used,
                    "created_at": analysis.created_at.isoformat(),
                }
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug("Cached analysis", failure_id=failure.id, cache_key=cache_key)
            
        except Exception as e:
            logger.warning(
                "Failed to cache analysis",
                failure_id=failure.id,
                error=str(e)
            )
    
    def clear_expired(self) -> int:
        """Clear expired cache entries and return count of removed entries"""
        removed_count = 0
        current_time = datetime.now(UTC)
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cached_data['cached_at'])
                if current_time - cached_time > self.ttl:
                    cache_file.unlink()
                    removed_count += 1
                    
            except Exception as e:
                logger.debug(
                    "Error checking cache file",
                    file=str(cache_file),
                    error=str(e)
                )
                # Remove corrupted cache files
                cache_file.unlink()
                removed_count += 1
        
        if removed_count > 0:
            logger.info("Cleared expired cache entries", count=removed_count)
        
        return removed_count


class FailureAnalyzer:
    """Analyzes test failures using AI-powered analysis"""
    
    def __init__(
        self,
        deepseek_config: DeepSeekConfig,
        repository_path: str = ".",
        cache_dir: str = ".cache/analysis",
        cache_ttl_hours: int = 24
    ):
        """
        Initialize the failure analyzer
        
        Args:
            deepseek_config: Configuration for DeepSeek API
            repository_path: Path to the repository root
            cache_dir: Directory for analysis cache
            cache_ttl_hours: Cache time-to-live in hours
        """
        self.deepseek_config = deepseek_config
        self.code_extractor = CodeContextExtractor(repository_path)
        self.cache = AnalysisCache(cache_dir, cache_ttl_hours)
        
        # Mapping of failure categories to fix types
        self.category_to_fix_type = {
            FailureCategory.SYNTAX_ERROR: FixType.SYNTAX_FIX,
            FailureCategory.IMPORT_ERROR: FixType.IMPORT_FIX,
            FailureCategory.ASSERTION_ERROR: FixType.TEST_FIX,
            FailureCategory.RUNTIME_ERROR: FixType.TEST_FIX,
            FailureCategory.COVERAGE_FAILURE: FixType.COVERAGE_FIX,
            FailureCategory.LINTING_ERROR: FixType.QUALITY_FIX,
            FailureCategory.TYPE_CHECK_ERROR: FixType.QUALITY_FIX,
            FailureCategory.SECURITY_SCAN_FAILURE: FixType.SECURITY_FIX,
            FailureCategory.DEPENDENCY_ERROR: FixType.DEPENDENCY_FIX,
            FailureCategory.DOCUMENTATION_ERROR: FixType.DOCUMENTATION_FIX,
            FailureCategory.UNIT_TEST: FixType.TEST_FIX,
            FailureCategory.INTEGRATION_TEST: FixType.TEST_FIX,
            FailureCategory.PERFORMANCE_FAILURE: FixType.TEST_FIX,
        }
    
    async def analyze_failure(self, failure: Failure) -> Analysis:
        """
        Analyze a test failure using AI-powered analysis
        
        Args:
            failure: The failure to analyze
            
        Returns:
            Analysis result
        """
        logger.info(
            "Starting failure analysis",
            failure_id=failure.id,
            category=failure.category.value
        )
        
        # Extract code context
        code_context = await self.code_extractor.extract_context(failure)
        
        # Check cache first
        cached_analysis = self.cache.get(failure, code_context)
        if cached_analysis:
            return cached_analysis
        
        # Perform AI analysis
        analysis = await self._perform_ai_analysis(failure, code_context)
        
        # Cache the result
        self.cache.set(failure, analysis, code_context)
        
        logger.info(
            "Failure analysis completed",
            failure_id=failure.id,
            confidence=analysis.confidence_score,
            suggested_fix=analysis.suggested_fix_type.value
        )
        
        return analysis
    
    async def _perform_ai_analysis(
        self,
        failure: Failure,
        code_context: Optional[CodeContext]
    ) -> Analysis:
        """Perform AI analysis using DeepSeek API"""
        async with DeepSeekClient(self.deepseek_config) as client:
            # Sanitize code context before sending to API
            if code_context:
                sanitized_context = self._sanitize_code_context(code_context)
            else:
                sanitized_context = code_context
            
            # Get AI analysis
            response = await client.analyze_failure(failure, sanitized_context)
            
            # Parse the response to extract structured information
            analysis_result = self._parse_analysis_response(response.content)
            
            # Determine suggested fix type
            suggested_fix_type = self._determine_fix_type(
                failure.category,
                analysis_result.get('suggested_fix_type')
            )
            
            # Create analysis object
            analysis = create_analysis(
                failure_id=failure.id,
                root_cause=analysis_result.get('root_cause', 'Unknown root cause'),
                suggested_fix_type=suggested_fix_type,
                confidence_score=analysis_result.get('confidence_score', 0.5),
                code_context=code_context or CodeContext(
                    file_path=failure.file_path or "unknown",
                    content="",
                    start_line=1,
                    end_line=1
                ),
                deepseek_response=response.content,
                analysis_prompt=self._generate_analysis_summary(failure, code_context),
                tokens_used=response.tokens_used
            )
            
            return analysis
    
    def _sanitize_code_context(self, code_context: CodeContext) -> CodeContext:
        """Sanitize code context before sending to API"""
        # Create a new DeepSeek client instance for sanitization
        temp_client = DeepSeekClient(self.deepseek_config)
        
        sanitized_content = temp_client.sanitize_code_for_api(code_context.content)
        
        sanitized_surrounding = {}
        for file_path, content in code_context.surrounding_files.items():
            sanitized_surrounding[file_path] = temp_client.sanitize_code_for_api(content)
        
        return CodeContext(
            file_path=code_context.file_path,
            content=sanitized_content,
            start_line=code_context.start_line,
            end_line=code_context.end_line,
            surrounding_files=sanitized_surrounding
        )
    
    def _parse_analysis_response(self, response_content: str) -> Dict[str, Any]:
        """Parse AI analysis response to extract structured information"""
        # Try to extract JSON if present
        try:
            # Look for JSON blocks in the response
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Fallback to text parsing
        result = {
            'root_cause': 'Unknown',
            'confidence_score': 0.5,
            'suggested_fix_type': None
        }
        
        # Extract root cause
        root_cause_patterns = [
            r'Root Cause[:\s]*(.+?)(?:\n|$)',
            r'Primary cause[:\s]*(.+?)(?:\n|$)',
            r'The (?:main )?(?:root )?cause is[:\s]*(.+?)(?:\n|$)',
        ]
        
        for pattern in root_cause_patterns:
            match = re.search(pattern, response_content, re.IGNORECASE | re.MULTILINE)
            if match:
                result['root_cause'] = match.group(1).strip()
                break
        
        # Extract confidence if mentioned
        confidence_patterns = [
            r'confidence[:\s]*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)%?\s*confident',
        ]
        
        for pattern in confidence_patterns:
            match = re.search(pattern, response_content, re.IGNORECASE)
            if match:
                confidence = float(match.group(1))
                if confidence > 1:  # Assume percentage
                    confidence /= 100
                result['confidence_score'] = min(1.0, max(0.0, confidence))
                break
        
        return result
    
    def _determine_fix_type(
        self,
        failure_category: FailureCategory,
        suggested_fix_type: Optional[str]
    ) -> FixType:
        """Determine the appropriate fix type"""
        # If AI suggested a specific fix type, try to use it
        if suggested_fix_type:
            try:
                return FixType(suggested_fix_type.lower())
            except ValueError:
                pass
        
        # Fall back to category mapping
        return self.category_to_fix_type.get(failure_category, FixType.TEST_FIX)
    
    def _generate_analysis_summary(
        self,
        failure: Failure,
        code_context: Optional[CodeContext]
    ) -> str:
        """Generate a summary of the analysis for logging/debugging"""
        summary = f"Analysis for {failure.category.value} in {failure.file_path or 'unknown file'}"
        
        if failure.line_number:
            summary += f" at line {failure.line_number}"
        
        if code_context:
            summary += f" (context: lines {code_context.start_line}-{code_context.end_line})"
        
        return summary
    
    async def get_code_context(self, failure: Failure) -> Optional[CodeContext]:
        """
        Get code context for a failure (public method for external use)
        
        Args:
            failure: The failure to get context for
            
        Returns:
            CodeContext if available, None otherwise
        """
        return await self.code_extractor.extract_context(failure)
    
    async def clear_cache(self) -> int:
        """
        Clear expired cache entries
        
        Returns:
            Number of entries removed
        """
        return self.cache.clear_expired()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cache_files = list(self.cache.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files if f.exists())
        
        return {
            "cache_dir": str(self.cache.cache_dir),
            "total_entries": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "ttl_hours": self.cache.ttl.total_seconds() / 3600
        }
    
    async def batch_analyze_failures(
        self,
        failures: List[Failure],
        max_concurrent: int = 3
    ) -> List[Analysis]:
        """
        Analyze multiple failures concurrently
        
        Args:
            failures: List of failures to analyze
            max_concurrent: Maximum number of concurrent analyses
            
        Returns:
            List of analysis results
        """
        import asyncio
        
        logger.info(
            "Starting batch failure analysis",
            total_failures=len(failures),
            max_concurrent=max_concurrent
        )
        
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_semaphore(failure: Failure) -> Analysis:
            async with semaphore:
                return await self.analyze_failure(failure)
        
        # Run analyses concurrently
        tasks = [analyze_with_semaphore(failure) for failure in failures]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Separate successful results from exceptions
        analyses = []
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    "Failed to analyze failure",
                    failure_id=failures[i].id,
                    error=str(result)
                )
                errors.append((failures[i], result))
            else:
                analyses.append(result)
        
        logger.info(
            "Batch failure analysis completed",
            successful=len(analyses),
            failed=len(errors),
            total=len(failures)
        )
        
        return analyses