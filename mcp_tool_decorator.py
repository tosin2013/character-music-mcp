#!/usr/bin/env python3
"""
MCP Tool Decorator System with Comprehensive Error Handling

This module provides decorators that wrap MCP tools with comprehensive error handling,
logging, and recovery mechanisms.
"""

import asyncio
import json
import time
import functools
from typing import Dict, Any, Optional, Callable, Union
from datetime import datetime

from mcp_error_handler import get_error_handler, create_format_mismatch_error, ErrorContext
from mcp_error_recovery import get_recovery_system, RecoveryResult

def mcp_tool_with_error_handling(
    tool_name: str,
    expected_input_format: Optional[Dict[str, str]] = None,
    enable_recovery: bool = True,
    max_retries: int = 2
):
    """
    Decorator that adds comprehensive error handling to MCP tools
    
    Args:
        tool_name: Name of the tool for logging purposes
        expected_input_format: Dictionary mapping parameter names to expected types
        enable_recovery: Whether to attempt error recovery
        max_retries: Maximum number of retry attempts
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> str:
            error_handler = get_error_handler()
            recovery_system = get_recovery_system()
            function_name = func.__name__
            start_time = time.time()
            
            # Prepare input data for logging
            input_data = {
                "args": args,
                "kwargs": kwargs,
                "arg_count": len(args),
                "kwarg_keys": list(kwargs.keys())
            }
            
            # Log tool entry
            error_handler.log_tool_entry(tool_name, function_name, input_data)
            
            try:
                # Validate input format if specified
                if expected_input_format and enable_recovery:
                    validation_result = await _validate_input_format(
                        tool_name, function_name, kwargs, expected_input_format
                    )
                    
                    if not validation_result.success:
                        # Attempt format recovery
                        recovery_result = await recovery_system.recover_from_format_error(
                            tool_name, function_name, validation_result.format_error,
                            kwargs, validation_result.error_context
                        )
                        
                        if recovery_result.success:
                            # Use recovered data
                            kwargs.update(recovery_result.recovered_data)
                        else:
                            # Return error response
                            return _create_error_response(
                                tool_name, function_name, validation_result.error_context,
                                recovery_result.error_message
                            )
                
                # Execute the original function
                result = await func(*args, **kwargs)
                
                # Log successful execution
                execution_time = time.time() - start_time
                output_summary = _create_output_summary(result)
                error_handler.log_tool_success(tool_name, function_name, execution_time, output_summary)
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Log the error
                error_context = error_handler.log_processing_error(
                    tool_name, function_name, e, input_data, "main_execution"
                )
                
                if not enable_recovery:
                    return _create_error_response(tool_name, function_name, error_context, str(e))
                
                # Attempt recovery based on error type
                recovery_result = await _attempt_error_recovery(
                    e, tool_name, function_name, func, args, kwargs, 
                    error_context, recovery_system, max_retries
                )
                
                if recovery_result.success:
                    # Log recovery success and return recovered data
                    total_time = time.time() - start_time
                    error_handler.log_tool_success(
                        tool_name, function_name, total_time, 
                        f"Recovered: {_create_output_summary(recovery_result.recovered_data)}"
                    )
                    
                    # Return recovered data in proper format
                    if isinstance(recovery_result.recovered_data, dict):
                        if "result" in recovery_result.recovered_data:
                            return recovery_result.recovered_data["result"]
                        else:
                            return json.dumps(recovery_result.recovered_data, indent=2)
                    else:
                        return str(recovery_result.recovered_data)
                else:
                    # Recovery failed, return error response
                    return _create_error_response(
                        tool_name, function_name, error_context, 
                        recovery_result.error_message or str(e)
                    )
        
        return wrapper
    return decorator

async def _validate_input_format(
    tool_name: str, 
    function_name: str, 
    input_kwargs: Dict[str, Any], 
    expected_format: Dict[str, str]
) -> 'ValidationResult':
    """Validate input format against expected format"""
    
    for param_name, expected_type in expected_format.items():
        if param_name in input_kwargs:
            actual_value = input_kwargs[param_name]
            actual_type = type(actual_value).__name__
            
            # Check if types match
            if not _types_match(actual_type, expected_type):
                # Create format mismatch error
                format_error = create_format_mismatch_error(
                    expected_format=f"{param_name}: {expected_type}",
                    actual_format=f"{param_name}: {actual_type}",
                    field_name=param_name,
                    expected_type=expected_type,
                    actual_type=actual_type,
                    sample_expected=_get_sample_for_type(expected_type),
                    sample_actual=str(actual_value)[:100]
                )
                
                error_context = get_error_handler().log_format_mismatch(
                    tool_name, function_name, format_error, input_kwargs
                )
                
                return ValidationResult(
                    success=False,
                    format_error=format_error,
                    error_context=error_context
                )
    
    return ValidationResult(success=True)

def _types_match(actual_type: str, expected_type: str) -> bool:
    """Check if actual type matches expected type (with some flexibility)"""
    
    # Direct match
    if actual_type == expected_type:
        return True
    
    # Flexible matches
    type_equivalents = {
        "str": ["string", "text"],
        "dict": ["dictionary", "object", "mapping"],
        "list": ["array", "sequence"],
        "int": ["integer", "number"],
        "float": ["number", "decimal"],
        "bool": ["boolean"]
    }
    
    expected_variants = type_equivalents.get(expected_type, [expected_type])
    return actual_type.lower() in [t.lower() for t in expected_variants]

def _get_sample_for_type(type_name: str) -> str:
    """Get a sample value for a given type"""
    samples = {
        "str": '"example string"',
        "dict": '{"key": "value"}',
        "list": '["item1", "item2"]',
        "int": "42",
        "float": "3.14",
        "bool": "true"
    }
    return samples.get(type_name, f"<{type_name} value>")

async def _attempt_error_recovery(
    error: Exception,
    tool_name: str,
    function_name: str,
    original_function: Callable,
    args: tuple,
    kwargs: Dict[str, Any],
    error_context: ErrorContext,
    recovery_system,
    max_retries: int
) -> RecoveryResult:
    """Attempt to recover from various types of errors"""
    
    error_type = type(error).__name__
    
    # Character detection errors
    if "character" in str(error).lower() and "not found" in str(error).lower():
        text_param = _find_text_parameter(kwargs)
        if text_param:
            return await recovery_system.recover_from_character_detection_failure(
                tool_name, function_name, text_param, "default_method", kwargs, error_context
            )
    
    # Function callable errors
    elif "not callable" in str(error).lower() or "FunctionTool" in str(error):
        function_param = _find_function_parameter(kwargs)
        if function_param:
            return await recovery_system.recover_from_function_callable_error(
                tool_name, function_name, function_param, kwargs, error_context
            )
    
    # JSON/Format errors
    elif error_type in ["JSONDecodeError", "ValueError", "TypeError"]:
        # Try retry with backoff for transient errors
        if max_retries > 0:
            return await recovery_system.recover_with_retry(
                original_function, tool_name, function_name, kwargs, max_retries
            )
    
    # For all other errors, try graceful degradation
    return await recovery_system.provide_graceful_degradation(
        tool_name, function_name, kwargs, error_context, "functional"
    )

def _find_text_parameter(kwargs: Dict[str, Any]) -> Optional[str]:
    """Find text parameter in kwargs for character detection recovery"""
    text_param_names = ["text", "content", "narrative_text", "topic_text", "concept"]
    
    for param_name in text_param_names:
        if param_name in kwargs and isinstance(kwargs[param_name], str):
            return kwargs[param_name]
    
    return None

def _find_function_parameter(kwargs: Dict[str, Any]) -> Optional[Any]:
    """Find function parameter in kwargs for callable recovery"""
    function_param_names = ["function", "func", "tool", "callable"]
    
    for param_name in function_param_names:
        if param_name in kwargs:
            return kwargs[param_name]
    
    return None

def _create_output_summary(result: Any) -> str:
    """Create a summary of the output for logging"""
    if isinstance(result, str):
        try:
            # Try to parse as JSON for better summary
            parsed = json.loads(result)
            if isinstance(parsed, dict):
                keys = list(parsed.keys())[:3]  # First 3 keys
                return f"JSON with keys: {keys}"
            elif isinstance(parsed, list):
                return f"JSON array with {len(parsed)} items"
            else:
                return f"JSON value: {type(parsed).__name__}"
        except json.JSONDecodeError:
            # Not JSON, just return string info
            return f"String ({len(result)} chars)"
    elif isinstance(result, dict):
        keys = list(result.keys())[:3]
        return f"Dict with keys: {keys}"
    elif isinstance(result, list):
        return f"List with {len(result)} items"
    else:
        return f"{type(result).__name__}"

def _create_error_response(
    tool_name: str, 
    function_name: str, 
    error_context: ErrorContext, 
    error_message: str
) -> str:
    """Create a standardized error response"""
    
    error_response = {
        "error": True,
        "error_type": error_context.error_type,
        "error_message": error_message,
        "tool_name": tool_name,
        "function_name": function_name,
        "timestamp": error_context.timestamp,
        "troubleshooting": {
            "check_input_format": "Verify that input parameters match expected types",
            "check_data_structure": "Ensure data structures are properly formatted",
            "check_logs": f"Review logs for detailed error information: {get_error_handler().log_file_path}",
            "contact_support": "If error persists, check the error handling documentation"
        }
    }
    
    # Add specific troubleshooting based on error type
    if error_context.error_type == "FORMAT_MISMATCH":
        error_response["troubleshooting"]["format_help"] = "Check the expected input format in the tool documentation"
    elif error_context.error_type == "CHARACTER_DETECTION_FAILURE":
        error_response["troubleshooting"]["character_help"] = "Ensure text contains clear character descriptions or dialogue"
    elif error_context.error_type == "FUNCTION_NOT_CALLABLE":
        error_response["troubleshooting"]["function_help"] = "Check tool registration and function definition"
    
    return json.dumps(error_response, indent=2)

class ValidationResult:
    """Result of input validation"""
    def __init__(self, success: bool, format_error=None, error_context=None):
        self.success = success
        self.format_error = format_error
        self.error_context = error_context

# Convenience decorators for common MCP tools
def character_analysis_tool(func: Callable) -> Callable:
    """Decorator specifically for character analysis tools"""
    return mcp_tool_with_error_handling(
        tool_name="character_analysis",
        expected_input_format={
            "text": "str"
        },
        enable_recovery=True,
        max_retries=2
    )(func)

def persona_generation_tool(func: Callable) -> Callable:
    """Decorator specifically for persona generation tools"""
    return mcp_tool_with_error_handling(
        tool_name="persona_generation",
        expected_input_format={
            "characters_json": "str"
        },
        enable_recovery=True,
        max_retries=2
    )(func)

def command_generation_tool(func: Callable) -> Callable:
    """Decorator specifically for command generation tools"""
    return mcp_tool_with_error_handling(
        tool_name="command_generation",
        expected_input_format={
            "personas_json": "str",
            "characters_json": "str"
        },
        enable_recovery=True,
        max_retries=2
    )(func)

def creative_generation_tool(func: Callable) -> Callable:
    """Decorator specifically for creative generation tools"""
    return mcp_tool_with_error_handling(
        tool_name="creative_generation",
        expected_input_format={
            "concept": "str"
        },
        enable_recovery=True,
        max_retries=2
    )(func)

def workflow_tool(func: Callable) -> Callable:
    """Decorator specifically for workflow tools"""
    return mcp_tool_with_error_handling(
        tool_name="workflow",
        expected_input_format={
            "text": "str"
        },
        enable_recovery=True,
        max_retries=3  # More retries for complex workflows
    )(func)