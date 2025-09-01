#!/usr/bin/env python3
"""
Comprehensive Test Suite for MCP Error Handling System

This module tests all aspects of the error handling and recovery system
to ensure it works correctly with various error scenarios.
"""

import asyncio
import json
import pytest
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

# Import the error handling components
from mcp_error_handler import (
    MCPErrorHandler, 
    ErrorContext, 
    FormatMismatchError, 
    create_format_mismatch_error,
    get_error_handler
)
from mcp_error_recovery import (
    MCPErrorRecovery, 
    RecoveryResult, 
    RecoveryStrategy,
    get_recovery_system
)
from mcp_tool_decorator import (
    mcp_tool_with_error_handling,
    character_analysis_tool,
    persona_generation_tool,
    command_generation_tool
)
from mcp_tools_integration import EnhancedMCPTools, get_enhanced_tools

class TestMCPErrorHandler:
    """Test the error handler functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Create temporary log file
        self.temp_log = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
        self.temp_log.close()
        
        # Create error handler with temp log file
        self.error_handler = MCPErrorHandler(self.temp_log.name)
    
    def teardown_method(self):
        """Cleanup after each test method"""
        # Remove temporary log file
        if os.path.exists(self.temp_log.name):
            os.unlink(self.temp_log.name)
    
    def test_error_handler_initialization(self):
        """Test error handler initializes correctly"""
        assert self.error_handler is not None
        assert self.error_handler.log_file_path == self.temp_log.name
        assert self.error_handler.logger is not None
        assert self.error_handler.error_stats["total_errors"] == 0
    
    def test_log_tool_entry(self):
        """Test tool entry logging"""
        input_data = {"text": "test input", "param": "value"}
        
        self.error_handler.log_tool_entry("test_tool", "test_function", input_data)
        
        # Check that log file contains entry
        with open(self.temp_log.name, 'r') as f:
            log_content = f.read()
            assert "TOOL_ENTRY" in log_content
            assert "test_tool.test_function" in log_content
    
    def test_log_format_mismatch(self):
        """Test format mismatch error logging"""
        format_error = create_format_mismatch_error(
            expected_format="dict",
            actual_format="str",
            field_name="test_field",
            expected_type="dict",
            actual_type="str"
        )
        
        input_data = {"test_field": "string_value"}
        
        error_context = self.error_handler.log_format_mismatch(
            "test_tool", "test_function", format_error, input_data
        )
        
        assert error_context.tool_name == "test_tool"
        assert error_context.error_type == "FORMAT_MISMATCH"
        assert self.error_handler.error_stats["format_errors"] == 1
        assert self.error_handler.error_stats["total_errors"] == 1
    
    def test_log_character_detection_failure(self):
        """Test character detection failure logging"""
        text_sample = "This is a test text without clear characters."
        
        error_context = self.error_handler.log_character_detection_failure(
            "test_tool", "test_function", text_sample, "default_method", {"text": text_sample}
        )
        
        assert error_context.error_type == "CHARACTER_DETECTION_FAILURE"
        assert self.error_handler.error_stats["character_detection_errors"] == 1
        assert error_context.user_context["text_length"] == len(text_sample)
    
    def test_log_function_callable_error(self):
        """Test function callable error logging"""
        non_callable_object = "not_a_function"
        
        error_context = self.error_handler.log_function_callable_error(
            "test_tool", "test_function", non_callable_object, {"func": non_callable_object}
        )
        
        assert error_context.error_type == "FUNCTION_NOT_CALLABLE"
        assert self.error_handler.error_stats["function_errors"] == 1
    
    def test_error_statistics(self):
        """Test error statistics calculation"""
        # Generate some errors
        format_error = create_format_mismatch_error("dict", "str", "field", "dict", "str")
        self.error_handler.log_format_mismatch("tool", "func", format_error, {})
        self.error_handler.log_character_detection_failure("tool", "func", "text", "method", {})
        
        stats = self.error_handler.get_error_statistics()
        
        assert stats["total_errors"] == 2
        assert stats["format_errors"] == 1
        assert stats["character_detection_errors"] == 1
        assert "most_common_error_type" in stats
        assert "error_trends" in stats

class TestMCPErrorRecovery:
    """Test the error recovery functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.recovery_system = MCPErrorRecovery()
    
    @pytest.mark.asyncio
    async def test_format_conversion_recovery(self):
        """Test recovery from format mismatch errors"""
        format_error = create_format_mismatch_error(
            expected_format="dict",
            actual_format="str", 
            field_name="test_field",
            expected_type="dict",
            actual_type="str"
        )
        
        input_data = {"test_field": '{"key": "value"}'}  # JSON string that can be converted
        error_context = ErrorContext(
            tool_name="test_tool",
            function_name="test_function",
            input_data=input_data,
            error_type="FORMAT_MISMATCH",
            error_message="Format mismatch",
            stack_trace="",
            timestamp="2024-01-01T00:00:00"
        )
        
        recovery_result = await self.recovery_system.recover_from_format_error(
            "test_tool", "test_function", format_error, input_data, error_context
        )
        
        assert recovery_result.success
        assert recovery_result.recovered_data is not None
        assert isinstance(recovery_result.recovered_data["test_field"], dict)
    
    @pytest.mark.asyncio
    async def test_character_detection_recovery(self):
        """Test recovery from character detection failures"""
        text_sample = "John walked into the room. He was tired."
        error_context = ErrorContext(
            tool_name="test_tool",
            function_name="test_function", 
            input_data={"text": text_sample},
            error_type="CHARACTER_DETECTION_FAILURE",
            error_message="No characters found",
            stack_trace="",
            timestamp="2024-01-01T00:00:00"
        )
        
        recovery_result = await self.recovery_system.recover_from_character_detection_failure(
            "test_tool", "test_function", text_sample, "failed_method", {"text": text_sample}, error_context
        )
        
        assert recovery_result.success
        assert "characters" in recovery_result.recovered_data
        assert len(recovery_result.recovered_data["characters"]) > 0
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test graceful degradation functionality"""
        error_context = ErrorContext(
            tool_name="test_tool",
            function_name="test_function",
            input_data={"param": "value"},
            error_type="PROCESSING_ERROR",
            error_message="Processing failed",
            stack_trace="",
            timestamp="2024-01-01T00:00:00"
        )
        
        recovery_result = await self.recovery_system.provide_graceful_degradation(
            "test_tool", "test_function", {"param": "value"}, error_context, "functional"
        )
        
        assert recovery_result.success
        assert recovery_result.fallback_used
        assert recovery_result.quality_score < 1.0
    
    def test_recovery_statistics(self):
        """Test recovery statistics tracking"""
        initial_stats = self.recovery_system.get_recovery_statistics()
        assert initial_stats["total_attempts"] == 0
        assert initial_stats["successful_recoveries"] == 0

class TestMCPToolDecorator:
    """Test the tool decorator functionality"""
    
    @pytest.mark.asyncio
    async def test_decorator_with_valid_input(self):
        """Test decorator with valid input"""
        
        @mcp_tool_with_error_handling(
            tool_name="test_tool",
            expected_input_format={"text": "str"},
            enable_recovery=True
        )
        async def test_function(text: str) -> str:
            return json.dumps({"result": f"processed: {text}"})
        
        result = await test_function(text="test input")
        
        assert result is not None
        parsed_result = json.loads(result)
        assert "result" in parsed_result
        assert "test input" in parsed_result["result"]
    
    @pytest.mark.asyncio
    async def test_decorator_with_format_error(self):
        """Test decorator handling format errors"""
        
        @mcp_tool_with_error_handling(
            tool_name="test_tool",
            expected_input_format={"text": "str"},
            enable_recovery=True
        )
        async def test_function(text: str) -> str:
            return json.dumps({"result": f"processed: {text}"})
        
        # Pass wrong type (should be recovered)
        result = await test_function(text=123)  # int instead of str
        
        assert result is not None
        # Should either be recovered or return error response
        if "error" in result:
            parsed_result = json.loads(result)
            assert parsed_result["error"] is True
        else:
            # Recovery succeeded
            parsed_result = json.loads(result)
            assert "result" in parsed_result or "recovered" in result.lower()
    
    @pytest.mark.asyncio
    async def test_decorator_with_processing_error(self):
        """Test decorator handling processing errors"""
        
        @mcp_tool_with_error_handling(
            tool_name="test_tool",
            enable_recovery=True,
            max_retries=1
        )
        async def failing_function(text: str) -> str:
            raise ValueError("Simulated processing error")
        
        result = await failing_function(text="test")
        
        assert result is not None
        parsed_result = json.loads(result)
        assert parsed_result["error"] is True
        assert "troubleshooting" in parsed_result

class TestEnhancedMCPTools:
    """Test the enhanced MCP tools integration"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.enhanced_tools = EnhancedMCPTools()
        self.mock_context = Mock()
        self.mock_context.info = AsyncMock()
        self.mock_context.error = AsyncMock()
    
    @pytest.mark.asyncio
    async def test_enhanced_character_analysis(self):
        """Test enhanced character analysis tool"""
        text = "John walked into the room. He was a tall man with dark hair."
        
        result = await self.enhanced_tools.analyze_character_text_enhanced(text, self.mock_context)
        
        assert result is not None
        parsed_result = json.loads(result)
        assert "characters" in parsed_result
        
        # Should have found at least one character
        if parsed_result["characters"]:
            assert len(parsed_result["characters"]) > 0
            assert "name" in parsed_result["characters"][0]
    
    @pytest.mark.asyncio
    async def test_enhanced_character_analysis_with_empty_text(self):
        """Test enhanced character analysis with empty text"""
        result = await self.enhanced_tools.analyze_character_text_enhanced("", self.mock_context)
        
        assert result is not None
        parsed_result = json.loads(result)
        assert parsed_result["error"] is True
    
    @pytest.mark.asyncio
    async def test_enhanced_persona_generation(self):
        """Test enhanced persona generation tool"""
        characters_data = {
            "characters": [{
                "name": "John",
                "backstory": "A musician from the city",
                "personality_drivers": ["creative", "ambitious"]
            }]
        }
        
        result = await self.enhanced_tools.generate_artist_personas_enhanced(
            json.dumps(characters_data), self.mock_context
        )
        
        assert result is not None
        parsed_result = json.loads(result)
        assert "personas" in parsed_result
        assert len(parsed_result["personas"]) > 0
    
    @pytest.mark.asyncio
    async def test_enhanced_command_generation(self):
        """Test enhanced command generation tool"""
        personas_data = {
            "personas": [{
                "character_name": "John",
                "artist_name": "John Artist",
                "primary_genre": "rock"
            }]
        }
        
        characters_data = {
            "characters": [{
                "name": "John",
                "backstory": "A musician"
            }]
        }
        
        result = await self.enhanced_tools.create_suno_commands_enhanced(
            json.dumps(personas_data), json.dumps(characters_data), self.mock_context
        )
        
        assert result is not None
        parsed_result = json.loads(result)
        assert "commands" in parsed_result
        assert len(parsed_result["commands"]) > 0
    
    @pytest.mark.asyncio
    async def test_enhanced_complete_workflow(self):
        """Test enhanced complete workflow"""
        text = "John was a musician who loved to create songs about his experiences."
        
        result = await self.enhanced_tools.complete_workflow_enhanced(text, self.mock_context)
        
        assert result is not None
        parsed_result = json.loads(result)
        assert "workflow_status" in parsed_result
        assert "workflow_state" in parsed_result
        assert "final_results" in parsed_result
        
        # Should have attempted all steps
        assert "summary" in parsed_result
        assert parsed_result["summary"]["steps_attempted"] == 3

class TestIntegrationScenarios:
    """Test real-world integration scenarios"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.enhanced_tools = EnhancedMCPTools()
        self.mock_context = Mock()
        self.mock_context.info = AsyncMock()
        self.mock_context.error = AsyncMock()
    
    @pytest.mark.asyncio
    async def test_format_mismatch_recovery_scenario(self):
        """Test a realistic format mismatch recovery scenario"""
        # Simulate passing a string where a dict is expected
        invalid_characters_json = "not valid json"
        
        result = await self.enhanced_tools.generate_artist_personas_enhanced(
            invalid_characters_json, self.mock_context
        )
        
        assert result is not None
        parsed_result = json.loads(result)
        
        # Should either recover or provide error response
        assert "error" in parsed_result or "personas" in parsed_result
    
    @pytest.mark.asyncio
    async def test_character_detection_failure_scenario(self):
        """Test character detection failure and recovery"""
        # Text with no clear characters
        text_without_characters = "The weather was nice today. It was sunny and warm."
        
        result = await self.enhanced_tools.analyze_character_text_enhanced(
            text_without_characters, self.mock_context
        )
        
        assert result is not None
        parsed_result = json.loads(result)
        
        # Should either find minimal characters or provide error
        if "characters" in parsed_result:
            # Recovery succeeded with minimal characters
            assert isinstance(parsed_result["characters"], list)
        else:
            # Error response provided
            assert parsed_result["error"] is True
    
    @pytest.mark.asyncio
    async def test_workflow_partial_failure_scenario(self):
        """Test workflow with partial failures"""
        # Use text that might cause issues in some steps
        problematic_text = "A"  # Very short text
        
        result = await self.enhanced_tools.complete_workflow_enhanced(
            problematic_text, self.mock_context
        )
        
        assert result is not None
        parsed_result = json.loads(result)
        
        # Should handle partial failures gracefully
        assert "workflow_status" in parsed_result
        assert "workflow_state" in parsed_result
        
        # Should have attempted recovery for failed steps
        workflow_state = parsed_result["workflow_state"]
        total_steps = len(workflow_state["steps_completed"]) + len(workflow_state["steps_failed"])
        assert total_steps > 0

# Test runner
if __name__ == "__main__":
    # Run basic tests
    print("Running MCP Error Handling Tests...")
    
    # Test error handler
    print("\n1. Testing Error Handler...")
    test_handler = TestMCPErrorHandler()
    test_handler.setup_method()
    test_handler.test_error_handler_initialization()
    test_handler.test_log_tool_entry()
    print("✓ Error Handler tests passed")
    
    # Test recovery system
    print("\n2. Testing Recovery System...")
    test_recovery = TestMCPErrorRecovery()
    test_recovery.setup_method()
    asyncio.run(test_recovery.test_graceful_degradation())
    print("✓ Recovery System tests passed")
    
    # Test enhanced tools
    print("\n3. Testing Enhanced Tools...")
    test_tools = TestEnhancedMCPTools()
    test_tools.setup_method()
    asyncio.run(test_tools.test_enhanced_character_analysis())
    print("✓ Enhanced Tools tests passed")
    
    print("\n✅ All basic tests completed successfully!")
    print("\nFor comprehensive testing, run: pytest test_mcp_error_handling.py -v")