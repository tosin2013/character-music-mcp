#!/usr/bin/env python3
"""
Fixed Workflow Manager for MCP Tools

This module provides proper tool registration and callable function handling
to fix the 'FunctionTool' object not callable errors.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    name: str
    function: Callable
    description: str
    required_params: list
    optional_params: list = None

class FixedWorkflowManager:
    """
    Workflow manager with proper function tool handling

    This class ensures that all tool functions are properly callable
    and provides comprehensive error handling for workflow execution.
    """

    def __init__(self):
        self.tools = {}
        self.workflows = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize and register all available tools"""
        try:
            # Import internal callable versions from server
            from server import (
                _analyze_character_text_internal,
                _complete_workflow_internal,
                _create_suno_commands_internal,
                _generate_artist_personas_internal,
            )

            # Register tools with proper callable functions
            self.tools = {
                'analyze_character_text': WorkflowStep(
                    name='analyze_character_text',
                    function=_analyze_character_text_internal,
                    description='Analyze narrative text to extract character profiles',
                    required_params=['text', 'ctx']
                ),
                'generate_artist_personas': WorkflowStep(
                    name='generate_artist_personas',
                    function=_generate_artist_personas_internal,
                    description='Generate artist personas from character profiles',
                    required_params=['characters_json', 'ctx']
                ),
                'create_suno_commands': WorkflowStep(
                    name='create_suno_commands',
                    function=_create_suno_commands_internal,
                    description='Generate Suno AI commands from personas and characters',
                    required_params=['personas_json', 'characters_json', 'ctx']
                ),
                'complete_workflow': WorkflowStep(
                    name='complete_workflow',
                    function=_complete_workflow_internal,
                    description='Execute complete character-to-music workflow',
                    required_params=['text', 'ctx']
                )
            }

            logger.info(f"Initialized {len(self.tools)} workflow tools")

        except ImportError as e:
            logger.error(f"Failed to import workflow tools: {e}")
            self.tools = {}

    def _make_callable(self, tool_func):
        """Ensure tool functions are properly callable"""
        if callable(tool_func):
            return tool_func
        else:
            # Handle FunctionTool objects properly
            logger.warning(f"Tool function {tool_func} is not directly callable, creating wrapper")
            return lambda *args, **kwargs: tool_func(*args, **kwargs)

    async def execute_workflow_step(self, step_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute a single workflow step with proper error handling

        Args:
            step_name: Name of the workflow step to execute
            *args: Positional arguments for the step function
            **kwargs: Keyword arguments for the step function

        Returns:
            Dictionary containing step results or error information
        """
        if step_name not in self.tools:
            error_msg = f"Unknown workflow step: {step_name}"
            logger.error(error_msg)
            return {"error": error_msg, "available_steps": list(self.tools.keys())}

        step = self.tools[step_name]

        try:
            logger.info(f"Executing workflow step: {step.name}")

            # Validate required parameters
            if len(args) < len(step.required_params):
                error_msg = f"Missing required parameters for {step_name}. Required: {step.required_params}"
                logger.error(error_msg)
                return {"error": error_msg}

            # Execute the step function
            result = await step.function(*args, **kwargs)

            logger.info(f"Successfully completed workflow step: {step.name}")
            return {"success": True, "result": result, "step": step_name}

        except Exception as e:
            error_msg = f"Workflow step {step_name} failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "error": error_msg,
                "step": step_name,
                "exception_type": type(e).__name__
            }

    async def execute_complete_workflow(self, text: str, ctx) -> Dict[str, Any]:
        """
        Execute complete workflow with proper error handling and recovery

        Args:
            text: Input narrative text for analysis
            ctx: Context object for logging and communication

        Returns:
            Dictionary containing complete workflow results
        """
        workflow_results = {
            "workflow_status": "in_progress",
            "completed_steps": [],
            "failed_steps": [],
            "results": {}
        }

        try:
            await ctx.info("Starting complete character-to-music workflow...")

            # Step 1: Character Analysis
            await ctx.info("Step 1: Analyzing characters...")
            char_result = await self.execute_workflow_step('analyze_character_text', text, ctx)

            if "error" in char_result:
                workflow_results["failed_steps"].append("character_analysis")
                workflow_results["workflow_status"] = "failed"
                workflow_results["error"] = f"Character analysis failed: {char_result['error']}"
                return workflow_results

            workflow_results["completed_steps"].append("character_analysis")
            workflow_results["results"]["character_analysis"] = char_result["result"]
            characters_result = char_result["result"]

            # Step 2: Generate Artist Personas
            await ctx.info("Step 2: Generating artist personas...")
            persona_result = await self.execute_workflow_step('generate_artist_personas', characters_result, ctx)

            if "error" in persona_result:
                workflow_results["failed_steps"].append("persona_generation")
                workflow_results["workflow_status"] = "failed"
                workflow_results["error"] = f"Persona generation failed: {persona_result['error']}"
                return workflow_results

            workflow_results["completed_steps"].append("persona_generation")
            workflow_results["results"]["artist_personas"] = persona_result["result"]
            personas_result = persona_result["result"]

            # Step 3: Create Suno Commands
            await ctx.info("Step 3: Creating Suno AI commands...")
            command_result = await self.execute_workflow_step('create_suno_commands', personas_result, characters_result, ctx)

            if "error" in command_result:
                workflow_results["failed_steps"].append("command_generation")
                workflow_results["workflow_status"] = "failed"
                workflow_results["error"] = f"Command generation failed: {command_result['error']}"
                return workflow_results

            workflow_results["completed_steps"].append("command_generation")
            workflow_results["results"]["suno_commands"] = command_result["result"]

            # Workflow completed successfully
            workflow_results["workflow_status"] = "completed"
            workflow_results["workflow_summary"] = "Complete character-driven music generation workflow executed successfully"

            await ctx.info("Workflow completed successfully!")

            return workflow_results

        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            await ctx.error(error_msg)

            workflow_results["workflow_status"] = "failed"
            workflow_results["error"] = error_msg
            workflow_results["exception_type"] = type(e).__name__

            return workflow_results

    def get_tool_info(self, tool_name: str = None) -> Dict[str, Any]:
        """
        Get information about available tools

        Args:
            tool_name: Optional specific tool name to get info for

        Returns:
            Dictionary containing tool information
        """
        if tool_name:
            if tool_name in self.tools:
                step = self.tools[tool_name]
                return {
                    "name": step.name,
                    "description": step.description,
                    "required_params": step.required_params,
                    "optional_params": step.optional_params or [],
                    "callable": callable(step.function)
                }
            else:
                return {"error": f"Tool {tool_name} not found"}
        else:
            return {
                "available_tools": list(self.tools.keys()),
                "total_tools": len(self.tools),
                "tools_info": {
                    name: {
                        "description": step.description,
                        "required_params": step.required_params,
                        "callable": callable(step.function)
                    }
                    for name, step in self.tools.items()
                }
            }

    def validate_tool_callability(self) -> Dict[str, Any]:
        """
        Validate that all registered tools are properly callable

        Returns:
            Dictionary containing validation results
        """
        validation_results = {
            "total_tools": len(self.tools),
            "callable_tools": 0,
            "non_callable_tools": 0,
            "validation_details": {}
        }

        for name, step in self.tools.items():
            is_callable = callable(step.function)
            validation_results["validation_details"][name] = {
                "callable": is_callable,
                "function_type": type(step.function).__name__,
                "has_call_method": callable(step.function)
            }

            if is_callable:
                validation_results["callable_tools"] += 1
            else:
                validation_results["non_callable_tools"] += 1

        validation_results["all_tools_callable"] = validation_results["non_callable_tools"] == 0

        return validation_results


# Global workflow manager instance
workflow_manager = None

def get_workflow_manager() -> FixedWorkflowManager:
    """Get or create the global workflow manager instance"""
    global workflow_manager
    if workflow_manager is None:
        workflow_manager = FixedWorkflowManager()
    return workflow_manager


# Utility functions for testing and validation
async def test_workflow_callability():
    """Test that all workflow tools are properly callable"""
    manager = get_workflow_manager()

    print("🔧 Testing Workflow Tool Callability")
    print("=" * 50)

    validation = manager.validate_tool_callability()

    print(f"Total tools: {validation['total_tools']}")
    print(f"Callable tools: {validation['callable_tools']}")
    print(f"Non-callable tools: {validation['non_callable_tools']}")
    print(f"All tools callable: {validation['all_tools_callable']}")

    print("\nDetailed validation:")
    for tool_name, details in validation["validation_details"].items():
        status = "✅" if details["callable"] else "❌"
        print(f"  {status} {tool_name}: {details['function_type']}")

    return validation["all_tools_callable"]


async def test_complete_workflow_execution():
    """Test complete workflow execution with sample data"""
    manager = get_workflow_manager()

    # Create a mock context for testing
    class MockContext:
        def __init__(self):
            self.messages = []

        async def info(self, message):
            self.messages.append(f"INFO: {message}")
            print(f"INFO: {message}")

        async def error(self, message):
            self.messages.append(f"ERROR: {message}")
            print(f"ERROR: {message}")

    ctx = MockContext()

    # Test with sample narrative
    sample_text = """
    Sarah walked through the bustling city streets, her violin case clutched tightly in her hand.
    As a street musician, she had learned to read the crowd, to understand what music would touch their hearts.
    Her melancholy melodies often drew people in, reflecting her own struggles with loneliness and her deep
    desire to connect with others through her art.
    """

    print("🎵 Testing Complete Workflow Execution")
    print("=" * 50)

    try:
        result = await manager.execute_complete_workflow(sample_text, ctx)

        print(f"Workflow Status: {result['workflow_status']}")
        print(f"Completed Steps: {result['completed_steps']}")
        print(f"Failed Steps: {result['failed_steps']}")

        if result['workflow_status'] == 'completed':
            print("✅ Workflow executed successfully!")
            return True
        else:
            print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Workflow test failed with exception: {e}")
        return False


if __name__ == "__main__":
    async def main():
        # Test callability
        callability_ok = await test_workflow_callability()

        # Test execution if callability is OK
        if callability_ok:
            execution_ok = await test_complete_workflow_execution()

            if execution_ok:
                print("\n🎉 All workflow tests passed!")
            else:
                print("\n❌ Workflow execution test failed")
        else:
            print("\n❌ Tool callability test failed")

    asyncio.run(main())
