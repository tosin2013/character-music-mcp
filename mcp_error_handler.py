#!/usr/bin/env python3
"""
Comprehensive Error Handling and Logging System for MCP Tools

This module provides structured error handling, detailed logging, and recovery mechanisms
for all MCP tools in the character-driven music generation system.
"""

import logging
import sys
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


# Configure structured logging
class MCPLogLevel(Enum):
    """Custom log levels for MCP tools"""
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    TOOL_ERROR = 45  # Custom level for tool-specific errors

@dataclass
class ErrorContext:
    """Structured error context for detailed logging"""
    tool_name: str
    function_name: str
    input_data: Dict[str, Any]
    error_type: str
    error_message: str
    stack_trace: str
    timestamp: str
    user_context: Optional[Dict[str, Any]] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class FormatMismatchError:
    """Detailed format mismatch error information"""
    expected_format: str
    actual_format: str
    field_name: str
    expected_type: str
    actual_type: str
    sample_expected: str
    sample_actual: str
    conversion_suggestion: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class MCPErrorHandler:
    """Centralized error handling system for all MCP tools"""

    def __init__(self, log_file_path: str = "mcp_tools_errors.log"):
        self.log_file_path = log_file_path
        self.logger = self._setup_logger()
        self.error_stats = {
            "total_errors": 0,
            "format_errors": 0,
            "function_errors": 0,
            "character_detection_errors": 0,
            "processing_errors": 0,
            "recovery_attempts": 0,
            "recovery_successes": 0
        }

    def _setup_logger(self) -> logging.Logger:
        """Setup structured logger with detailed formatting"""
        logger = logging.getLogger("mcp_tools")
        logger.setLevel(logging.DEBUG)

        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # File handler for detailed logs
        file_handler = logging.FileHandler(self.log_file_path, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Console handler for important messages
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)

        # Detailed formatter for file logs
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Simple formatter for console
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def log_tool_entry(self, tool_name: str, function_name: str, input_data: Dict[str, Any]) -> None:
        """Log tool entry with input data"""
        self.logger.info(
            f"TOOL_ENTRY | {tool_name}.{function_name} | Input: {self._sanitize_input_for_log(input_data)}"
        )

    def log_tool_success(self, tool_name: str, function_name: str, execution_time: float, output_summary: str) -> None:
        """Log successful tool execution"""
        self.logger.info(
            f"TOOL_SUCCESS | {tool_name}.{function_name} | Time: {execution_time:.3f}s | Output: {output_summary}"
        )

    def log_format_mismatch(
        self,
        tool_name: str,
        function_name: str,
        format_error: FormatMismatchError,
        input_data: Dict[str, Any]
    ) -> ErrorContext:
        """Log detailed format mismatch errors"""
        self.error_stats["format_errors"] += 1
        self.error_stats["total_errors"] += 1

        error_context = ErrorContext(
            tool_name=tool_name,
            function_name=function_name,
            input_data=self._sanitize_input_for_log(input_data),
            error_type="FORMAT_MISMATCH",
            error_message=f"Format mismatch in field '{format_error.field_name}': expected {format_error.expected_type}, got {format_error.actual_type}",
            stack_trace=traceback.format_exc(),
            timestamp=datetime.now().isoformat()
        )

        self.logger.error(
            f"FORMAT_MISMATCH | {tool_name}.{function_name} | "
            f"Field: {format_error.field_name} | "
            f"Expected: {format_error.expected_format} | "
            f"Actual: {format_error.actual_format} | "
            f"Suggestion: {format_error.conversion_suggestion}"
        )

        # Log detailed format comparison
        self.logger.debug(
            f"FORMAT_DETAILS | {tool_name}.{function_name} | "
            f"Expected sample: {format_error.sample_expected} | "
            f"Actual sample: {format_error.sample_actual}"
        )

        return error_context

    def log_character_detection_failure(
        self,
        tool_name: str,
        function_name: str,
        text_sample: str,
        detection_method: str,
        input_data: Dict[str, Any]
    ) -> ErrorContext:
        """Log character detection failures with analysis"""
        self.error_stats["character_detection_errors"] += 1
        self.error_stats["total_errors"] += 1

        # Analyze text for debugging
        text_analysis = self._analyze_text_for_debugging(text_sample)

        error_context = ErrorContext(
            tool_name=tool_name,
            function_name=function_name,
            input_data=self._sanitize_input_for_log(input_data),
            error_type="CHARACTER_DETECTION_FAILURE",
            error_message=f"No characters detected using method '{detection_method}'",
            stack_trace=traceback.format_exc(),
            timestamp=datetime.now().isoformat(),
            user_context={
                "text_length": len(text_sample),
                "text_analysis": text_analysis,
                "detection_method": detection_method
            }
        )

        self.logger.error(
            f"CHARACTER_DETECTION_FAILURE | {tool_name}.{function_name} | "
            f"Method: {detection_method} | "
            f"Text length: {len(text_sample)} | "
            f"Analysis: {text_analysis}"
        )

        # Log text sample for debugging
        self.logger.debug(
            f"TEXT_SAMPLE | {tool_name}.{function_name} | "
            f"Sample: {text_sample[:200]}{'...' if len(text_sample) > 200 else ''}"
        )

        return error_context

    def log_function_callable_error(
        self,
        tool_name: str,
        function_name: str,
        function_object: Any,
        input_data: Dict[str, Any]
    ) -> ErrorContext:
        """Log function callable errors with detailed analysis"""
        self.error_stats["function_errors"] += 1
        self.error_stats["total_errors"] += 1

        # Analyze function object
        function_analysis = self._analyze_function_object(function_object)

        error_context = ErrorContext(
            tool_name=tool_name,
            function_name=function_name,
            input_data=self._sanitize_input_for_log(input_data),
            error_type="FUNCTION_NOT_CALLABLE",
            error_message=f"Function object is not callable: {type(function_object)}",
            stack_trace=traceback.format_exc(),
            timestamp=datetime.now().isoformat(),
            user_context={
                "function_type": str(type(function_object)),
                "function_analysis": function_analysis
            }
        )

        self.logger.error(
            f"FUNCTION_NOT_CALLABLE | {tool_name}.{function_name} | "
            f"Type: {type(function_object)} | "
            f"Analysis: {function_analysis}"
        )

        return error_context

    def log_processing_error(
        self,
        tool_name: str,
        function_name: str,
        error: Exception,
        input_data: Dict[str, Any],
        processing_stage: str = "unknown"
    ) -> ErrorContext:
        """Log general processing errors with context"""
        self.error_stats["processing_errors"] += 1
        self.error_stats["total_errors"] += 1

        error_context = ErrorContext(
            tool_name=tool_name,
            function_name=function_name,
            input_data=self._sanitize_input_for_log(input_data),
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            timestamp=datetime.now().isoformat(),
            user_context={
                "processing_stage": processing_stage,
                "error_class": error.__class__.__module__ + "." + error.__class__.__name__
            }
        )

        self.logger.error(
            f"PROCESSING_ERROR | {tool_name}.{function_name} | "
            f"Stage: {processing_stage} | "
            f"Error: {type(error).__name__}: {str(error)}"
        )

        return error_context

    def log_recovery_attempt(
        self,
        error_context: ErrorContext,
        recovery_method: str,
        recovery_data: Dict[str, Any]
    ) -> None:
        """Log error recovery attempts"""
        self.error_stats["recovery_attempts"] += 1

        error_context.recovery_attempted = True

        self.logger.warning(
            f"RECOVERY_ATTEMPT | {error_context.tool_name}.{error_context.function_name} | "
            f"Method: {recovery_method} | "
            f"Original error: {error_context.error_type}"
        )

        self.logger.debug(
            f"RECOVERY_DATA | {error_context.tool_name}.{error_context.function_name} | "
            f"Data: {self._sanitize_input_for_log(recovery_data)}"
        )

    def log_recovery_success(
        self,
        error_context: ErrorContext,
        recovery_method: str,
        recovered_data: Dict[str, Any]
    ) -> None:
        """Log successful error recovery"""
        self.error_stats["recovery_successes"] += 1

        error_context.recovery_successful = True

        self.logger.info(
            f"RECOVERY_SUCCESS | {error_context.tool_name}.{error_context.function_name} | "
            f"Method: {recovery_method} | "
            f"Original error: {error_context.error_type}"
        )

        self.logger.debug(
            f"RECOVERED_DATA | {error_context.tool_name}.{error_context.function_name} | "
            f"Data: {self._sanitize_input_for_log(recovered_data)}"
        )

    def log_recovery_failure(
        self,
        error_context: ErrorContext,
        recovery_method: str,
        recovery_error: Exception
    ) -> None:
        """Log failed error recovery attempts"""
        self.logger.error(
            f"RECOVERY_FAILURE | {error_context.tool_name}.{error_context.function_name} | "
            f"Method: {recovery_method} | "
            f"Recovery error: {type(recovery_error).__name__}: {str(recovery_error)}"
        )

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        recovery_rate = (
            self.error_stats["recovery_successes"] / max(self.error_stats["recovery_attempts"], 1)
        ) * 100

        return {
            **self.error_stats,
            "recovery_rate_percent": round(recovery_rate, 2),
            "most_common_error_type": self._get_most_common_error_type(),
            "error_trends": self._get_error_trends()
        }

    def _sanitize_input_for_log(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input data for logging (remove sensitive info, truncate large data)"""
        sanitized = {}

        for key, value in input_data.items():
            if isinstance(value, str):
                # Truncate long strings
                if len(value) > 200:
                    sanitized[key] = value[:200] + "... [truncated]"
                else:
                    sanitized[key] = value
            elif isinstance(value, (dict, list)):
                # Truncate large structures
                value_str = str(value)
                if len(value_str) > 300:
                    sanitized[key] = value_str[:300] + "... [truncated]"
                else:
                    sanitized[key] = value
            else:
                sanitized[key] = value

        return sanitized

    def _analyze_text_for_debugging(self, text: str) -> Dict[str, Any]:
        """Analyze text to help debug character detection issues"""
        import re

        # Basic text analysis
        words = text.split()
        sentences = text.split('.')

        # Look for potential character indicators
        potential_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        quoted_speech = re.findall(r'"[^"]*"', text)
        pronouns = re.findall(r'\b(?:he|she|they|him|her|them|his|hers|their)\b', text.lower())

        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "potential_names": potential_names[:5],  # First 5 potential names
            "quoted_speech_count": len(quoted_speech),
            "pronoun_count": len(pronouns),
            "has_dialogue": len(quoted_speech) > 0,
            "has_proper_nouns": len(potential_names) > 0
        }

    def _analyze_function_object(self, function_object: Any) -> Dict[str, Any]:
        """Analyze function object to help debug callable issues"""
        analysis = {
            "type": str(type(function_object)),
            "is_callable": callable(function_object),
            "has_call_method": callable(function_object),
            "attributes": []
        }

        # Get relevant attributes
        for attr in dir(function_object):
            if not attr.startswith('_'):
                analysis["attributes"].append(attr)

        # Limit attributes list
        analysis["attributes"] = analysis["attributes"][:10]

        return analysis

    def _get_most_common_error_type(self) -> str:
        """Determine the most common error type"""
        error_types = {
            "format_errors": self.error_stats["format_errors"],
            "function_errors": self.error_stats["function_errors"],
            "character_detection_errors": self.error_stats["character_detection_errors"],
            "processing_errors": self.error_stats["processing_errors"]
        }

        if not any(error_types.values()):
            return "none"

        return max(error_types.items(), key=lambda x: x[1])[0]

    def _get_error_trends(self) -> Dict[str, str]:
        """Get error trend analysis"""
        total = self.error_stats["total_errors"]

        if total == 0:
            return {"trend": "no_errors", "recommendation": "system_healthy"}

        format_rate = (self.error_stats["format_errors"] / total) * 100
        function_rate = (self.error_stats["function_errors"] / total) * 100
        detection_rate = (self.error_stats["character_detection_errors"] / total) * 100

        if format_rate > 50:
            return {
                "trend": "high_format_errors",
                "recommendation": "review_data_model_consistency"
            }
        elif function_rate > 30:
            return {
                "trend": "high_function_errors",
                "recommendation": "review_tool_registration_and_callability"
            }
        elif detection_rate > 40:
            return {
                "trend": "high_detection_errors",
                "recommendation": "improve_character_detection_algorithms"
            }
        else:
            return {
                "trend": "mixed_errors",
                "recommendation": "general_system_review"
            }

# Global error handler instance
_error_handler = None

def get_error_handler() -> MCPErrorHandler:
    """Get or create the global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = MCPErrorHandler()
    return _error_handler

def create_format_mismatch_error(
    expected_format: str,
    actual_format: str,
    field_name: str,
    expected_type: str,
    actual_type: str,
    sample_expected: str = "",
    sample_actual: str = ""
) -> FormatMismatchError:
    """Create a detailed format mismatch error"""

    # Generate conversion suggestion
    conversion_suggestions = {
        ("str", "dict"): "Use json.loads() to parse JSON string",
        ("dict", "str"): "Use json.dumps() to serialize dictionary",
        ("list", "str"): "Split string by delimiter or parse JSON array",
        ("str", "list"): "Join list elements or serialize as JSON",
        ("int", "str"): "Use int() to convert string to integer",
        ("float", "str"): "Use float() to convert string to number",
        ("bool", "str"): "Use bool() or check for 'true'/'false' strings"
    }

    suggestion = conversion_suggestions.get(
        (expected_type, actual_type),
        f"Convert {actual_type} to {expected_type} using appropriate method"
    )

    return FormatMismatchError(
        expected_format=expected_format,
        actual_format=actual_format,
        field_name=field_name,
        expected_type=expected_type,
        actual_type=actual_type,
        sample_expected=sample_expected,
        sample_actual=sample_actual,
        conversion_suggestion=suggestion
    )
