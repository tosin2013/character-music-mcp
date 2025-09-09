#!/usr/bin/env python3
"""
MCP Tool Utilities

This module provides utilities for working with MCP tools and handling
the 'FunctionTool' object not callable errors.
"""

import asyncio
import logging
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPToolWrapper:
    """
    Wrapper for MCP tools that handles callable issues

    This class provides a way to call MCP tools that have been decorated
    with @mcp.tool and are not directly callable.
    """

    def __init__(self):
        self.tools = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize MCP tools with proper callable handling"""
        try:
            # Import the internal callable versions
            from server import (
                _analyze_character_text_internal,
                _complete_workflow_internal,
                _create_suno_commands_internal,
                _generate_artist_personas_internal,
            )

            # Register internal callable versions
            self.tools = {
                'analyze_character_text': _analyze_character_text_internal,
                'generate_artist_personas': _generate_artist_personas_internal,
                'create_suno_commands': _create_suno_commands_internal,
                'complete_workflow': _complete_workflow_internal
            }

            logger.info(f"Initialized {len(self.tools)} MCP tool wrappers")

        except ImportError as e:
            logger.error(f"Failed to import MCP tools: {e}")
            self.tools = {}

    async def call_tool(self, tool_name: str, *args, **kwargs) -> Any:
        """
        Call an MCP tool by name with proper error handling

        Args:
            tool_name: Name of the tool to call
            *args: Positional arguments for the tool
            **kwargs: Keyword arguments for the tool

        Returns:
            Result from the tool call

        Raises:
            ValueError: If tool is not found
            Exception: If tool execution fails
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}")

        tool_func = self.tools[tool_name]

        try:
            logger.info(f"Calling MCP tool: {tool_name}")
            result = await tool_func(*args, **kwargs)
            logger.info(f"MCP tool {tool_name} completed successfully")
            return result

        except Exception as e:
            logger.error(f"MCP tool {tool_name} failed: {e}")
            raise

    def get_available_tools(self) -> Dict[str, str]:
        """Get list of available tools"""
        return {
            name: f"Callable MCP tool: {name}"
            for name in self.tools.keys()
        }

    def is_tool_available(self, tool_name: str) -> bool:
        """Check if a tool is available"""
        return tool_name in self.tools


# Global wrapper instance
_mcp_wrapper = None

def get_mcp_wrapper() -> MCPToolWrapper:
    """Get or create the global MCP wrapper instance"""
    global _mcp_wrapper
    if _mcp_wrapper is None:
        _mcp_wrapper = MCPToolWrapper()
    return _mcp_wrapper


# Convenience functions for direct tool access
async def call_analyze_character_text(text: str, ctx) -> str:
    """Call analyze_character_text tool with proper handling"""
    wrapper = get_mcp_wrapper()
    return await wrapper.call_tool('analyze_character_text', text, ctx)

async def call_generate_artist_personas(characters_json: str, ctx) -> str:
    """Call generate_artist_personas tool with proper handling"""
    wrapper = get_mcp_wrapper()
    return await wrapper.call_tool('generate_artist_personas', characters_json, ctx)

async def call_create_suno_commands(personas_json: str, characters_json: str, ctx) -> str:
    """Call create_suno_commands tool with proper handling"""
    wrapper = get_mcp_wrapper()
    return await wrapper.call_tool('create_suno_commands', personas_json, characters_json, ctx)

async def call_complete_workflow(text: str, ctx) -> str:
    """Call complete_workflow tool with proper handling"""
    wrapper = get_mcp_wrapper()
    return await wrapper.call_tool('complete_workflow', text, ctx)


# Test function to validate MCP tool accessibility
async def test_mcp_tool_access():
    """Test that MCP tools can be accessed and called"""
    print("🔧 Testing MCP Tool Access")
    print("=" * 40)

    wrapper = get_mcp_wrapper()

    # Test tool availability
    available_tools = wrapper.get_available_tools()
    print(f"Available tools: {len(available_tools)}")
    for name, desc in available_tools.items():
        print(f"  ✅ {name}: {desc}")

    # Create mock context
    class MockContext:
        def __init__(self):
            self.messages = []

        async def info(self, message):
            self.messages.append(f"INFO: {message}")

        async def error(self, message):
            self.messages.append(f"ERROR: {message}")

    ctx = MockContext()

    # Test sample calls
    sample_text = "John was a musician who loved jazz and blues."

    try:
        # Test character analysis
        print("\nTesting character analysis...")
        result = await call_analyze_character_text(sample_text, ctx)
        assert result is not None
        print("✅ Character analysis works")

        # Test persona generation
        print("Testing persona generation...")
        persona_result = await call_generate_artist_personas(result, ctx)
        assert persona_result is not None
        print("✅ Persona generation works")

        # Test command generation
        print("Testing command generation...")
        command_result = await call_create_suno_commands(persona_result, result, ctx)
        assert command_result is not None
        print("✅ Command generation works")

        # Test complete workflow
        print("Testing complete workflow...")
        workflow_result = await call_complete_workflow(sample_text, ctx)
        assert workflow_result is not None
        print("✅ Complete workflow works")

        print("\n🎉 All MCP tool access tests passed!")
        return True

    except Exception as e:
        print(f"❌ MCP tool access test failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_mcp_tool_access())
