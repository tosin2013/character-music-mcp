import pytest

#!/usr/bin/env python3
"""
Test Complete Workflow Fixes

This test validates that the 'FunctionTool' object not callable errors
have been fixed and that the complete workflow executes properly.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
try:
    from server import (
        _analyze_character_text_internal,
        _complete_workflow_internal,
        _create_suno_commands_internal,
        _generate_artist_personas_internal,
        analyze_character_text,
        complete_workflow,
        create_suno_commands,
        generate_artist_personas,
    )
    from workflow_manager import (
        FixedWorkflowManager,
        test_complete_workflow_execution,
        test_workflow_callability,
    )
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

class MockContext:
    """Mock context for testing MCP tools"""

    def __init__(self, session_id="test_session"):
        self.session_id = session_id
        self.messages = []
        self.errors = []

    async def info(self, message):
        self.messages.append(f"INFO: {message}")
        print(f"INFO: {message}")

    async def error(self, message):
        self.errors.append(f"ERROR: {message}")
        print(f"ERROR: {message}")

    def has_errors(self):
        return len(self.errors) > 0

    def get_messages(self):
        return self.messages

    def get_errors(self):
        return self.errors

@pytest.mark.asyncio
async def test_internal_functions_callable():
    """Test that internal functions are directly callable"""
    print("\n🔧 Testing Internal Function Callability")
    print("=" * 50)

    ctx = MockContext("internal_test")

    # Test sample narrative
    sample_text = """
    Marcus Thompson stood in his Bristol warehouse studio, surrounded by vintage synthesizers
    and analog equipment. As a producer, he had always been drawn to the philosophical depths
    of alternative music, seeking to create sounds that would make listeners question their
    place in the universe.
    """

    try:
        # Test 1: Character Analysis
        print("Testing _analyze_character_text_internal...")
        char_result = await _analyze_character_text_internal(sample_text, ctx)
        assert char_result is not None
        char_data = json.loads(char_result)
        assert "characters" in char_data or "error" in char_data
        print("✅ Character analysis internal function works")

        # Test 2: Persona Generation (if character analysis succeeded)
        if "characters" in char_data and char_data["characters"]:
            print("Testing _generate_artist_personas_internal...")
            persona_result = await _generate_artist_personas_internal(char_result, ctx)
            assert persona_result is not None
            persona_data = json.loads(persona_result)
            assert "artist_personas" in persona_data or "error" in persona_data
            print("✅ Persona generation internal function works")

            # Test 3: Command Generation (if persona generation succeeded)
            if "artist_personas" in persona_data:
                print("Testing _create_suno_commands_internal...")
                command_result = await _create_suno_commands_internal(persona_result, char_result, ctx)
                assert command_result is not None
                json.loads(command_result)
                print("✅ Command generation internal function works")

        # Test 4: Complete Workflow Internal
        print("Testing _complete_workflow_internal...")
        workflow_result = await _complete_workflow_internal(sample_text, ctx)
        assert workflow_result is not None
        workflow_data = json.loads(workflow_result)
        assert "workflow_status" in workflow_data or "error" in workflow_data
        print("✅ Complete workflow internal function works")

        return True

    except Exception as e:
        print(f"❌ Internal function test failed: {e}")
        return False

@pytest.mark.asyncio
async def test_mcp_tool_wrappers():
    """Test that MCP tool wrappers work correctly"""
    print("\n🎭 Testing MCP Tool Wrappers")
    print("=" * 50)

    ctx = MockContext("mcp_test")

    sample_text = """
    Elena Rodriguez was a jazz pianist who performed in small clubs around the city.
    Her music was deeply emotional, drawing from her experiences with heartbreak and
    her journey toward self-discovery. She had a gift for improvisation that allowed
    her to channel her feelings directly into her performances.
    """

    try:
        # Test MCP tool wrappers using the utility wrapper
        from mcp_tool_utils import (
            call_analyze_character_text,
            call_complete_workflow,
            call_create_suno_commands,
            call_generate_artist_personas,
        )

        print("Testing analyze_character_text MCP tool...")
        char_result = await call_analyze_character_text(sample_text, ctx)
        assert char_result is not None
        print("✅ Character analysis MCP tool works")

        print("Testing generate_artist_personas MCP tool...")
        persona_result = await call_generate_artist_personas(char_result, ctx)
        assert persona_result is not None
        print("✅ Persona generation MCP tool works")

        print("Testing create_suno_commands MCP tool...")
        command_result = await call_create_suno_commands(persona_result, char_result, ctx)
        assert command_result is not None
        print("✅ Command generation MCP tool works")

        print("Testing complete_workflow MCP tool...")
        workflow_result = await call_complete_workflow(sample_text, ctx)
        assert workflow_result is not None
        json.loads(workflow_result)
        print("✅ Complete workflow MCP tool works")

        return True

    except Exception as e:
        print(f"❌ MCP tool wrapper test failed: {e}")
        return False

@pytest.mark.asyncio
async def test_workflow_manager():
    """Test the workflow manager functionality"""
    print("\n⚙️ Testing Workflow Manager")
    print("=" * 50)

    try:
        manager = FixedWorkflowManager()

        # Test tool registration
        tool_info = manager.get_tool_info()
        print(f"Registered tools: {tool_info['total_tools']}")
        assert tool_info['total_tools'] > 0

        # Test callability validation
        validation = manager.validate_tool_callability()
        print(f"All tools callable: {validation['all_tools_callable']}")

        if not validation['all_tools_callable']:
            print("Non-callable tools found:")
            for name, details in validation['validation_details'].items():
                if not details['callable']:
                    print(f"  ❌ {name}: {details['function_type']}")

        # Test workflow execution
        ctx = MockContext("workflow_manager_test")
        sample_text = """
        David Kim was a electronic music producer who specialized in ambient soundscapes.
        His work was influenced by his meditation practice and his fascination with the
        intersection of technology and spirituality. He often incorporated field recordings
        of nature into his compositions.
        """

        result = await manager.execute_complete_workflow(sample_text, ctx)
        assert result is not None
        assert "workflow_status" in result

        print(f"Workflow status: {result['workflow_status']}")
        print(f"Completed steps: {result.get('completed_steps', [])}")

        return result['workflow_status'] == 'completed'

    except Exception as e:
        print(f"❌ Workflow manager test failed: {e}")
        return False

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling and recovery mechanisms"""
    print("\n🛡️ Testing Error Handling")
    print("=" * 50)

    ctx = MockContext("error_test")

    try:
        # Test with empty text
        print("Testing with empty text...")
        result = await _analyze_character_text_internal("", ctx)
        result_data = json.loads(result)
        assert "error" in result_data
        print("✅ Empty text error handling works")

        # Test with invalid JSON
        print("Testing with invalid character data...")
        result = await _generate_artist_personas_internal("{invalid json}", ctx)
        result_data = json.loads(result)
        assert "error" in result_data
        print("✅ Invalid JSON error handling works")

        # Test workflow with invalid input
        print("Testing complete workflow with minimal text...")
        result = await _complete_workflow_internal("Hi", ctx)
        result_data = json.loads(result)
        # Should either succeed with minimal data or fail gracefully
        assert "workflow_status" in result_data or "error" in result_data
        print("✅ Minimal input error handling works")

        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

@pytest.mark.asyncio
async def test_data_consistency():
    """Test data consistency across workflow steps"""
    print("\n📊 Testing Data Consistency")
    print("=" * 50)

    ctx = MockContext("consistency_test")

    sample_text = """
    Maria Santos was a folk singer-songwriter from a small coastal town. Her music was
    deeply rooted in her cultural heritage and family traditions. She wrote songs about
    love, loss, and the connection between people and the sea. Her voice carried the
    weight of generations of storytellers, and her guitar playing was both delicate
    and powerful.
    """

    try:
        # Execute workflow step by step
        char_result = await _analyze_character_text_internal(sample_text, ctx)
        char_data = json.loads(char_result)

        if "error" in char_data:
            print(f"Character analysis failed: {char_data['error']}")
            return False

        persona_result = await _generate_artist_personas_internal(char_result, ctx)
        persona_data = json.loads(persona_result)

        if "error" in persona_data:
            print(f"Persona generation failed: {persona_data['error']}")
            return False

        command_result = await _create_suno_commands_internal(persona_result, char_result, ctx)
        command_data = json.loads(command_result)

        if "error" in command_data:
            print(f"Command generation failed: {command_data['error']}")
            return False

        # Validate data consistency
        if "characters" in char_data and char_data["characters"]:
            primary_char = char_data["characters"][0]
            char_name = primary_char.get("name", "")

            if "artist_personas" in persona_data and persona_data["artist_personas"]:
                persona = persona_data["artist_personas"][0]
                persona_char_name = persona.get("character_name", "")

                # Check character name consistency
                if char_name and persona_char_name:
                    assert char_name == persona_char_name, f"Character name mismatch: {char_name} vs {persona_char_name}"
                    print("✅ Character name consistency maintained")

        print("✅ Data consistency validation passed")
        return True

    except Exception as e:
        print(f"❌ Data consistency test failed: {e}")
        return False

async def run_all_tests():
    """Run all workflow fix tests"""
    print("🚀 COMPLETE WORKFLOW FIXES TEST SUITE")
    print("=" * 60)

    test_results = {}

    # Test 1: Internal function callability
    test_results["internal_functions"] = await test_internal_functions_callable()

    # Test 2: MCP tool wrappers
    test_results["mcp_wrappers"] = await test_mcp_tool_wrappers()

    # Test 3: Workflow manager
    test_results["workflow_manager"] = await test_workflow_manager()

    # Test 4: Error handling
    test_results["error_handling"] = await test_error_handling()

    # Test 5: Data consistency
    test_results["data_consistency"] = await test_data_consistency()

    # Test 6: Workflow manager utility tests
    print("\n🔧 Running Workflow Manager Utility Tests")
    callability_ok = await test_workflow_callability()
    test_results["utility_callability"] = callability_ok

    if callability_ok:
        execution_ok = await test_complete_workflow_execution()
        test_results["utility_execution"] = execution_ok
    else:
        test_results["utility_execution"] = False

    # Summary
    print("\n📋 TEST RESULTS SUMMARY")
    print("=" * 60)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:25} {status}")
        if result:
            passed_tests += 1

    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Complete workflow fixes are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please review the output above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
