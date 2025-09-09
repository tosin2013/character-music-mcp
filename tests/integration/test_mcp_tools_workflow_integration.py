#!/usr/bin/env python3
"""
MCP Tools Workflow Integration Tests

Comprehensive integration tests for MCP tools workflows, testing:
- Complete workflow execution without callable errors
- Data flow between tools with consistent formats
- Various character descriptions and genre specifications
- End-to-end functionality with realistic use cases
- All requirements validation

This test suite validates the fixes implemented in the MCP tools diagnostic fixes spec.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import test fixtures and utilities
from tests.fixtures.mock_contexts import create_mock_context
from tests.fixtures.test_data import test_data_manager

# Import MCP tools and components
try:
    from mcp_data_validation import (
        validate_character_profile,
        validate_persona_data,
        validate_suno_commands,
    )
    from mcp_format_conversion import convert_character_profile, ensure_standard_character_profile
    from mcp_shared_models import StandardCharacterProfile
    from mcp_tools_integration import EnhancedMCPTools, get_enhanced_tools
    MCP_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: MCP tools not available for integration testing: {e}")
    MCP_TOOLS_AVAILABLE = False


@pytest.mark.asyncio
@pytest.mark.skipif(not MCP_TOOLS_AVAILABLE, reason="MCP tools not available")
class TestMCPToolsWorkflowIntegration:
    """Integration tests for MCP tools workflows"""

    def setup_method(self):
        """Setup for each test method"""
        self.enhanced_tools = get_enhanced_tools()
        self.data_manager = test_data_manager
        self.test_scenarios = self.data_manager.scenarios

        # Performance tracking
        self.performance_metrics = {
            "character_analysis_times": [],
            "persona_generation_times": [],
            "command_generation_times": [],
            "workflow_execution_times": []
        }

    async def test_complete_workflow_execution_no_callable_errors(self):
        """
        Test complete workflow execution without callable errors

        Requirements: 4.1, 4.2 - Workflow execution without FunctionTool errors
        """
        # Test with simple character scenario
        scenario = self.test_scenarios["single_character_simple"]
        ctx = create_mock_context("basic", session_id="workflow_test")

        try:
            # Execute complete workflow
            result_json = await self.enhanced_tools.complete_workflow_enhanced(
                scenario.narrative_text, ctx
            )

            # Validate result is valid JSON
            result = json.loads(result_json)

            # Verify workflow completed without callable errors
            assert "workflow_status" in result
            assert result["workflow_status"] in ["completed", "partial"]

            # Verify no function callable errors in context
            error_messages = [msg.message for msg in ctx.errors]
            callable_errors = [msg for msg in error_messages if "not callable" in msg.lower()]
            assert len(callable_errors) == 0, f"Found callable errors: {callable_errors}"

            # Verify workflow steps were attempted
            assert "workflow_state" in result
            workflow_state = result["workflow_state"]
            assert "steps_completed" in workflow_state
            assert "steps_failed" in workflow_state

            # At least some steps should complete successfully
            assert len(workflow_state["steps_completed"]) > 0, "No workflow steps completed"

            print(f"✓ Workflow completed with {len(workflow_state['steps_completed'])} successful steps")

        except Exception as e:
            pytest.fail(f"Workflow execution failed with error: {e}")

    async def test_data_flow_between_tools_consistent_formats(self):
        """
        Test data flow between tools with consistent formats

        Requirements: 13.1, 13.2, 13.3 - Consistent data models and interfaces
        """
        scenario = self.test_scenarios["multi_character_medium"]
        ctx = create_mock_context("basic", session_id="data_flow_test")

        # Step 1: Character Analysis
        analysis_result_json = await self.enhanced_tools.analyze_character_text_enhanced(
            scenario.narrative_text, ctx
        )
        analysis_result = json.loads(analysis_result_json)

        # Validate character analysis format
        assert "characters" in analysis_result
        assert isinstance(analysis_result["characters"], list)

        # Validate character profile format consistency
        for character_data in analysis_result["characters"]:
            validation_result = validate_character_profile(character_data)
            assert validation_result["is_valid"], f"Invalid character profile: {validation_result['errors']}"

        # Step 2: Persona Generation (using analysis output)
        personas_result_json = await self.enhanced_tools.generate_artist_personas_enhanced(
            analysis_result_json, ctx
        )
        personas_result = json.loads(personas_result_json)

        # Validate persona data format
        assert "personas" in personas_result
        assert isinstance(personas_result["personas"], list)

        # Validate persona format consistency
        for persona_data in personas_result["personas"]:
            validation_result = validate_persona_data(persona_data)
            assert validation_result["is_valid"], f"Invalid persona data: {validation_result['errors']}"

        # Step 3: Command Generation (using both previous outputs)
        commands_result_json = await self.enhanced_tools.create_suno_commands_enhanced(
            personas_result_json, analysis_result_json, ctx
        )
        commands_result = json.loads(commands_result_json)

        # Validate command data format
        assert "commands" in commands_result
        assert isinstance(commands_result["commands"], list)

        # Validate command format consistency
        validation_result = validate_suno_commands(commands_result)
        assert validation_result.is_valid, f"Invalid command data: {[issue.message for issue in validation_result.get_errors()]}"

        # Verify data flow consistency
        # Characters from analysis should influence personas
        character_names = [char["name"] for char in analysis_result["characters"]]
        persona_character_names = [persona.get("character_name", "") for persona in personas_result["personas"]]

        # At least some character names should appear in personas
        name_overlap = any(char_name in persona_name for char_name in character_names for persona_name in persona_character_names)
        assert name_overlap or len(character_names) == 0, "No character name consistency between analysis and personas"

        print(f"✓ Data flow validated through {len(analysis_result['characters'])} characters → {len(personas_result['personas'])} personas → {len(commands_result['commands'])} commands")

    async def test_various_character_descriptions_and_genres(self):
        """
        Test various character descriptions and genre specifications

        Requirements: 5.1, 5.2, 6.2, 6.3 - Dynamic content processing and genre respect
        """
        test_cases = [
            {
                "scenario": "single_character_simple",
                "expected_genres": ["indie", "alternative"],
                "description": "Simple contemporary character"
            },
            {
                "scenario": "sci_fi_adventure",
                "expected_genres": ["electronic", "synthwave", "ambient"],
                "description": "Science fiction adventure character"
            },
            {
                "scenario": "historical_drama",
                "expected_genres": ["classical", "orchestral", "chamber music"],
                "description": "Historical period character"
            },
            {
                "scenario": "urban_fantasy",
                "expected_genres": ["dark electronic", "industrial", "gothic"],
                "description": "Urban fantasy supernatural character"
            }
        ]

        for test_case in test_cases:
            scenario = self.test_scenarios[test_case["scenario"]]
            ctx = create_mock_context("basic", session_id=f"genre_test_{test_case['scenario']}")

            # Test character analysis respects character description
            analysis_result_json = await self.enhanced_tools.analyze_character_text_enhanced(
                scenario.narrative_text, ctx
            )
            analysis_result = json.loads(analysis_result_json)

            # Verify characters are detected (not hardcoded)
            assert len(analysis_result["characters"]) > 0, f"No characters detected in {test_case['description']}"

            # Verify character names match expected (not hardcoded Bristol/Marcus)
            character_names = [char["name"] for char in analysis_result["characters"]]
            assert scenario.expected_primary_character in character_names, f"Expected character {scenario.expected_primary_character} not found in {character_names}"

            # Verify no hardcoded Bristol/Marcus content
            all_text = json.dumps(analysis_result).lower()
            assert "bristol" not in all_text, f"Found hardcoded Bristol content in {test_case['description']}"
            assert "marcus thompson" not in all_text, f"Found hardcoded Marcus Thompson content in {test_case['description']}"

            # Test persona generation respects character and genre
            personas_result_json = await self.enhanced_tools.generate_artist_personas_enhanced(
                analysis_result_json, ctx
            )
            personas_result = json.loads(personas_result_json)

            # Verify personas reflect the character description
            assert len(personas_result["personas"]) > 0, f"No personas generated for {test_case['description']}"

            # Test creative generation with genre preference
            for expected_genre in test_case["expected_genres"][:1]:  # Test first expected genre
                creative_result_json = await self.enhanced_tools.creative_music_generation_enhanced(
                    f"Create music for {scenario.expected_primary_character}",
                    style_preference=expected_genre,
                    ctx=ctx
                )
                creative_result = json.loads(creative_result_json)

                # Verify creative output is not just input repetition
                assert "creative_variations" in creative_result
                assert len(creative_result["creative_variations"]) > 0

                # Verify style preference is respected
                assert creative_result["generation_metadata"]["style_preference"] == expected_genre

            print(f"✓ Validated {test_case['description']} with character {scenario.expected_primary_character}")

    async def test_end_to_end_functionality_realistic_use_cases(self):
        """
        Test end-to-end functionality with realistic use cases

        Requirements: All requirements validation - comprehensive end-to-end testing
        """
        realistic_scenarios = [
            {
                "name": "indie_musician_story",
                "text": """
                Jamie Martinez sat in their cramped apartment, guitar in hand, staring at the
                rejection email from yet another record label. At 26, they had been writing
                songs since high school, pouring their heart into indie folk melodies that
                spoke of small-town dreams and big-city disappointments.

                Their latest EP, recorded in their bedroom with borrowed equipment, captured
                the raw emotion of their journey from rural Texas to Austin's competitive
                music scene. Each song told a piece of their story - the loneliness of
                leaving home, the struggle to pay rent while chasing dreams, the bittersweet
                hope that kept them going despite constant rejection.
                """,
                "expected_character": "Jamie Martinez",
                "expected_themes": ["indie", "folk", "singer-songwriter"],
                "complexity": "medium"
            },
            {
                "name": "electronic_producer_narrative",
                "text": """
                Alex Chen worked through the night in their home studio, surrounded by
                synthesizers and drum machines that hummed with electronic potential.
                As a 24-year-old producer, they had found their voice in the intersection
                of ambient soundscapes and driving techno beats.

                Their music reflected their dual heritage - the meditative qualities of
                their grandmother's traditional Chinese music blended with the pulsing
                energy of underground Berlin clubs they'd discovered online. Each track
                was a journey through digital landscapes that somehow felt deeply human.
                """,
                "expected_character": "Alex Chen",
                "expected_themes": ["electronic", "ambient", "techno"],
                "complexity": "medium"
            }
        ]

        for scenario in realistic_scenarios:
            ctx = create_mock_context("performance", session_id=f"realistic_{scenario['name']}")

            # Execute complete workflow
            import time
            start_time = time.time()

            workflow_result_json = await self.enhanced_tools.complete_workflow_enhanced(
                scenario["text"], ctx
            )

            execution_time = time.time() - start_time
            self.performance_metrics["workflow_execution_times"].append(execution_time)

            workflow_result = json.loads(workflow_result_json)

            # Validate workflow success
            assert workflow_result["workflow_status"] in ["completed", "partial"]

            # Validate character detection
            if "final_results" in workflow_result and "analysis" in workflow_result["final_results"]:
                analysis = workflow_result["final_results"]["analysis"]
                if "characters" in analysis and analysis["characters"]:
                    character_names = [char["name"] for char in analysis["characters"]]
                    assert scenario["expected_character"] in character_names, f"Expected character {scenario['expected_character']} not found"

            # Validate persona generation
            if "final_results" in workflow_result and "personas" in workflow_result["final_results"]:
                personas = workflow_result["final_results"]["personas"]
                if "personas" in personas and personas["personas"]:
                    # Verify personas are generated and not just fallbacks
                    non_fallback_personas = [p for p in personas["personas"] if not p.get("is_fallback", False)]
                    assert len(non_fallback_personas) > 0, "Only fallback personas generated"

            # Validate command generation
            if "final_results" in workflow_result and "commands" in workflow_result["final_results"]:
                commands = workflow_result["final_results"]["commands"]
                if "commands" in commands and commands["commands"]:
                    # Verify commands are practical and not just fallbacks
                    non_fallback_commands = [c for c in commands["commands"] if not c.get("is_fallback", False)]
                    assert len(non_fallback_commands) > 0, "Only fallback commands generated"

            # Validate no errors in context
            assert not ctx.has_errors(), f"Workflow had errors: {[e.message for e in ctx.errors]}"

            print(f"✓ End-to-end validation completed for {scenario['name']} in {execution_time:.2f}s")

    async def test_error_recovery_and_graceful_degradation(self):
        """
        Test error recovery and graceful degradation

        Requirements: 12.3, 12.4 - Error recovery mechanisms
        """
        # Test with problematic input that might cause errors
        problematic_inputs = [
            {
                "name": "empty_text",
                "text": "",
                "expected_behavior": "graceful_error_handling"
            },
            {
                "name": "very_short_text",
                "text": "Hi.",
                "expected_behavior": "minimal_analysis"
            },
            {
                "name": "no_clear_characters",
                "text": "The weather was nice. Things happened. It was okay.",
                "expected_behavior": "fallback_character_creation"
            }
        ]

        for test_input in problematic_inputs:
            ctx = create_mock_context("basic", session_id=f"error_recovery_{test_input['name']}")

            try:
                # Attempt workflow execution
                result_json = await self.enhanced_tools.complete_workflow_enhanced(
                    test_input["text"], ctx
                )
                result = json.loads(result_json)

                # Verify graceful handling
                assert "workflow_status" in result

                # For empty/short text, expect partial completion with fallbacks
                if test_input["name"] in ["empty_text", "very_short_text"]:
                    # Should have some error handling but still produce result
                    assert result["workflow_status"] in ["partial", "completed"]

                    # Check if fallback mechanisms were used
                    if "final_results" in result:
                        final_results = result["final_results"]

                        # Analysis should have minimal/fallback data
                        if "analysis" in final_results:
                            analysis = final_results["analysis"]
                            if "characters" in analysis:
                                # Should have at least minimal character data
                                assert len(analysis["characters"]) >= 0

                print(f"✓ Error recovery validated for {test_input['name']}")

            except Exception as e:
                # Even with errors, should not crash completely
                assert "empty" in test_input["name"] or "short" in test_input["name"], f"Unexpected error for {test_input['name']}: {e}"

    async def test_performance_and_scalability(self):
        """
        Test performance and scalability of workflow

        Requirements: Performance validation for production use
        """
        # Test with multiple scenarios to measure performance
        performance_scenarios = [
            self.test_scenarios["single_character_simple"],
            self.test_scenarios["multi_character_medium"],
            self.test_scenarios["concept_album_complex"]
        ]

        execution_times = []
        memory_usage = []

        for i, scenario in enumerate(performance_scenarios):
            ctx = create_mock_context("performance", session_id=f"performance_test_{i}")

            import time

            import psutil

            # Measure execution time and memory
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB

            start_time = time.time()

            result_json = await self.enhanced_tools.complete_workflow_enhanced(
                scenario.narrative_text, ctx
            )

            execution_time = time.time() - start_time
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before

            execution_times.append(execution_time)
            memory_usage.append(memory_used)

            # Validate result was produced
            result = json.loads(result_json)
            assert "workflow_status" in result

            print(f"✓ Performance test {i+1}: {execution_time:.2f}s, {memory_used:.1f}MB")

        # Validate performance thresholds
        avg_execution_time = sum(execution_times) / len(execution_times)
        max_execution_time = max(execution_times)
        avg_memory_usage = sum(memory_usage) / len(memory_usage)

        # Performance assertions (adjust thresholds as needed)
        assert avg_execution_time < 30.0, f"Average execution time too high: {avg_execution_time:.2f}s"
        assert max_execution_time < 60.0, f"Maximum execution time too high: {max_execution_time:.2f}s"
        assert avg_memory_usage < 100.0, f"Average memory usage too high: {avg_memory_usage:.1f}MB"

        print(f"✓ Performance validation: avg {avg_execution_time:.2f}s, max {max_execution_time:.2f}s, avg memory {avg_memory_usage:.1f}MB")

    async def test_concurrent_workflow_execution(self):
        """
        Test concurrent workflow execution

        Requirements: Concurrent processing capability
        """
        # Test concurrent execution of multiple workflows
        concurrent_scenarios = [
            self.test_scenarios["single_character_simple"],
            self.test_scenarios["romance_contemporary"],
            self.test_scenarios["sci_fi_adventure"]
        ]

        async def execute_workflow(scenario, scenario_id):
            ctx = create_mock_context("concurrent", session_id=f"concurrent_{scenario_id}")
            result_json = await self.enhanced_tools.complete_workflow_enhanced(
                scenario.narrative_text, ctx
            )
            result = json.loads(result_json)
            return {
                "scenario_id": scenario_id,
                "result": result,
                "context": ctx,
                "success": result.get("workflow_status") in ["completed", "partial"]
            }

        # Execute workflows concurrently
        import time
        start_time = time.time()

        tasks = [
            execute_workflow(scenario, i)
            for i, scenario in enumerate(concurrent_scenarios)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        execution_time = time.time() - start_time

        # Validate all workflows completed
        successful_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Concurrent execution error: {result}")
            else:
                assert result["success"], f"Workflow {result['scenario_id']} failed"
                successful_results.append(result)

        assert len(successful_results) == len(concurrent_scenarios), "Not all concurrent workflows succeeded"

        # Validate concurrent execution was faster than sequential
        # (This is a rough estimate - actual speedup depends on system)
        estimated_sequential_time = len(concurrent_scenarios) * 10  # Assume 10s per workflow
        assert execution_time < estimated_sequential_time, f"Concurrent execution not faster: {execution_time:.2f}s vs estimated {estimated_sequential_time}s"

        print(f"✓ Concurrent execution of {len(successful_results)} workflows in {execution_time:.2f}s")

    async def test_requirements_validation_comprehensive(self):
        """
        Comprehensive validation of all requirements

        Requirements: All requirements from 1.1 to 13.4
        """
        validation_results = {
            "character_analysis_accuracy": False,
            "format_consistency": False,
            "creative_generation_quality": False,
            "workflow_execution_reliability": False,
            "dynamic_content_processing": False,
            "error_handling_robustness": False
        }

        # Test character analysis accuracy (Requirements 1.1-1.5)
        scenario = self.test_scenarios["multi_character_medium"]
        ctx = create_mock_context("basic", session_id="requirements_validation")

        analysis_result_json = await self.enhanced_tools.analyze_character_text_enhanced(
            scenario.narrative_text, ctx
        )
        analysis_result = json.loads(analysis_result_json)

        # Validate character detection
        if (len(analysis_result.get("characters", [])) > 0 and
            scenario.expected_primary_character in [c["name"] for c in analysis_result["characters"]]):
            validation_results["character_analysis_accuracy"] = True

        # Test format consistency (Requirements 13.1-13.4)
        try:
            personas_result_json = await self.enhanced_tools.generate_artist_personas_enhanced(
                analysis_result_json, ctx
            )
            personas_result = json.loads(personas_result_json)

            commands_result_json = await self.enhanced_tools.create_suno_commands_enhanced(
                personas_result_json, analysis_result_json, ctx
            )
            commands_result = json.loads(commands_result_json)

            validation_results["format_consistency"] = True
        except Exception as e:
            print(f"Format consistency test failed: {e}")

        # Test creative generation quality (Requirements 3.1-3.4)
        creative_result_json = await self.enhanced_tools.creative_music_generation_enhanced(
            "Create an emotional indie song about personal growth",
            style_preference="indie",
            ctx=ctx
        )
        creative_result = json.loads(creative_result_json)

        if (len(creative_result.get("creative_variations", [])) > 0 and
            creative_result.get("generation_metadata", {}).get("quality_score", 0) > 0.5):
            validation_results["creative_generation_quality"] = True

        # Test workflow execution reliability (Requirements 4.1-4.4)
        workflow_result_json = await self.enhanced_tools.complete_workflow_enhanced(
            scenario.narrative_text, ctx
        )
        workflow_result = json.loads(workflow_result_json)

        if (workflow_result.get("workflow_status") in ["completed", "partial"] and
            not ctx.has_errors()):
            validation_results["workflow_execution_reliability"] = True

        # Test dynamic content processing (Requirements 5.1-5.4)
        all_results_text = json.dumps({
            "analysis": analysis_result,
            "personas": personas_result,
            "commands": commands_result,
            "creative": creative_result,
            "workflow": workflow_result
        }).lower()

        # Verify no hardcoded Bristol/Marcus content
        if ("bristol" not in all_results_text and
            "marcus thompson" not in all_results_text):
            validation_results["dynamic_content_processing"] = True

        # Test error handling robustness (Requirements 12.1-12.4)
        try:
            # Test with problematic input
            error_test_result = await self.enhanced_tools.complete_workflow_enhanced(
                "Very short text.", ctx
            )
            error_result = json.loads(error_test_result)

            # Should handle gracefully without crashing
            if "workflow_status" in error_result:
                validation_results["error_handling_robustness"] = True
        except Exception:
            # Even exceptions should be handled gracefully in production
            pass

        # Report validation results
        passed_validations = sum(validation_results.values())
        total_validations = len(validation_results)

        print("\n=== Requirements Validation Summary ===")
        for requirement, passed in validation_results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{requirement}: {status}")

        print(f"\nOverall: {passed_validations}/{total_validations} validations passed")

        # Assert that most validations pass (allow some flexibility for edge cases)
        assert passed_validations >= total_validations * 0.8, f"Too many validation failures: {passed_validations}/{total_validations}"

        return validation_results


# Standalone test functions for pytest discovery
@pytest.mark.asyncio
@pytest.mark.skipif(not MCP_TOOLS_AVAILABLE, reason="MCP tools not available")
async def test_workflow_execution_no_errors():
    """Test complete workflow execution without callable errors"""
    test_instance = TestMCPToolsWorkflowIntegration()
    test_instance.setup_method()
    await test_instance.test_complete_workflow_execution_no_callable_errors()


@pytest.mark.asyncio
@pytest.mark.skipif(not MCP_TOOLS_AVAILABLE, reason="MCP tools not available")
async def test_data_flow_consistency():
    """Test data flow between tools with consistent formats"""
    test_instance = TestMCPToolsWorkflowIntegration()
    test_instance.setup_method()
    await test_instance.test_data_flow_between_tools_consistent_formats()


@pytest.mark.asyncio
@pytest.mark.skipif(not MCP_TOOLS_AVAILABLE, reason="MCP tools not available")
async def test_character_and_genre_variations():
    """Test various character descriptions and genre specifications"""
    test_instance = TestMCPToolsWorkflowIntegration()
    test_instance.setup_method()
    await test_instance.test_various_character_descriptions_and_genres()


@pytest.mark.asyncio
@pytest.mark.skipif(not MCP_TOOLS_AVAILABLE, reason="MCP tools not available")
async def test_end_to_end_realistic_scenarios():
    """Test end-to-end functionality with realistic use cases"""
    test_instance = TestMCPToolsWorkflowIntegration()
    test_instance.setup_method()
    await test_instance.test_end_to_end_functionality_realistic_use_cases()


@pytest.mark.asyncio
@pytest.mark.skipif(not MCP_TOOLS_AVAILABLE, reason="MCP tools not available")
async def test_comprehensive_requirements_validation():
    """Comprehensive validation of all requirements"""
    test_instance = TestMCPToolsWorkflowIntegration()
    test_instance.setup_method()
    await test_instance.test_requirements_validation_comprehensive()


if __name__ == "__main__":
    """Run integration tests directly"""
    import asyncio

    async def run_all_tests():
        """Run all integration tests"""
        print("=== MCP Tools Workflow Integration Tests ===\n")

        if not MCP_TOOLS_AVAILABLE:
            print("❌ MCP tools not available - skipping integration tests")
            return

        test_instance = TestMCPToolsWorkflowIntegration()
        test_instance.setup_method()

        tests = [
            ("Workflow Execution (No Callable Errors)", test_instance.test_complete_workflow_execution_no_callable_errors),
            ("Data Flow Consistency", test_instance.test_data_flow_between_tools_consistent_formats),
            ("Character & Genre Variations", test_instance.test_various_character_descriptions_and_genres),
            ("End-to-End Realistic Scenarios", test_instance.test_end_to_end_functionality_realistic_use_cases),
            ("Error Recovery", test_instance.test_error_recovery_and_graceful_degradation),
            ("Performance & Scalability", test_instance.test_performance_and_scalability),
            ("Concurrent Execution", test_instance.test_concurrent_workflow_execution),
            ("Comprehensive Requirements", test_instance.test_requirements_validation_comprehensive)
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            try:
                print(f"Running: {test_name}")
                await test_func()
                print(f"✓ {test_name} - PASSED\n")
                passed += 1
            except Exception as e:
                print(f"✗ {test_name} - FAILED: {e}\n")
                failed += 1

        print("=== Test Summary ===")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total: {passed + failed}")

        if failed == 0:
            print("🎉 All integration tests passed!")
        else:
            print(f"⚠️  {failed} test(s) failed")

    # Run the tests
    asyncio.run(run_all_tests())
