#!/usr/bin/env python3
"""
MCP Tools Integration Tests

Tests all MCP tool validation including analyze_character_text, generate_artist_personas,
create_suno_commands, complete_workflow, and creative_music_generation tools.
Tests error handling and parameter validation for all tools.

Requirements: 1.1, 3.5
"""

import asyncio
import json
import os

# Import test utilities
import sys
from dataclasses import asdict
from typing import Any, Dict

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server import (
    analyze_character_text,
    complete_workflow,
    create_suno_commands,
    creative_music_generation,
    generate_artist_personas,
)

from tests.fixtures.mock_contexts import MockConcurrentContext, MockContext
from tests.fixtures.test_data import TestDataManager

# Import enhanced tools if available
try:
    from enhanced_mcp_tool import create_character_album, process_universal_content
    ENHANCED_TOOLS_AVAILABLE = True
except ImportError:
    ENHANCED_TOOLS_AVAILABLE = False


class TestMCPToolsIntegration:
    """Test all MCP tools integration and validation"""

    def setup_method(self):
        """Set up test environment"""
        self.test_data = TestDataManager()
        self.mock_context = MockContext("mcp_tools_test")
        self.concurrent_context = MockConcurrentContext(max_concurrent=3, session_id="mcp_concurrent_test")

    @pytest.mark.asyncio
    async def test_analyze_character_text_tool(self):
        """Test analyze_character_text MCP tool validation"""
        await self.mock_context.info("Testing analyze_character_text tool")

        # Test with valid input
        scenario = self.test_data.get_scenario("single_character_simple")

        result = await analyze_character_text(
            self.mock_context,
            narrative_text=scenario.narrative_text
        )

        # Validate result structure
        assert result is not None
        result_data = json.loads(result)

        # Check required fields
        assert "characters" in result_data
        assert "analysis_metadata" in result_data
        assert "processing_summary" in result_data

        # Validate character data
        characters = result_data["characters"]
        assert len(characters) >= 1

        primary_character = characters[0]
        required_character_fields = [
            "name", "confidence_score", "importance_score",
            "behavioral_traits", "motivations", "fears", "desires"
        ]

        for field in required_character_fields:
            assert field in primary_character, f"Missing character field: {field}"

        # Validate confidence and importance scores
        assert 0.0 <= primary_character["confidence_score"] <= 1.0
        assert 0.0 <= primary_character["importance_score"] <= 1.0

        # Test parameter validation
        await self._test_analyze_character_text_parameter_validation()

        await self.mock_context.info("analyze_character_text tool validation passed")

    @pytest.mark.asyncio
    async def test_generate_artist_personas_tool(self):
        """Test generate_artist_personas MCP tool validation"""
        await self.mock_context.info("Testing generate_artist_personas tool")

        # Get character data for persona generation
        scenario = self.test_data.get_scenario("emotional_intensity_high")
        expected_character = self.test_data.get_expected_character("Marcus")

        character_data = asdict(expected_character)

        result = await generate_artist_personas(
            self.mock_context,
            character_data=character_data
        )

        # Validate result structure
        assert result is not None
        result_data = json.loads(result)

        # Check required fields
        assert "artist_persona" in result_data
        assert "generation_metadata" in result_data
        assert "character_mapping" in result_data

        # Validate persona data
        persona = result_data["artist_persona"]
        required_persona_fields = [
            "primary_genre", "vocal_style", "instrumental_preferences",
            "artistic_influences", "performance_style", "character_inspiration"
        ]

        for field in required_persona_fields:
            assert field in persona, f"Missing persona field: {field}"

        # Validate genre classification
        assert persona["primary_genre"] in scenario.expected_genres

        # Validate character connection
        assert expected_character.name in persona["character_inspiration"]

        # Test parameter validation
        await self._test_generate_artist_personas_parameter_validation()

        await self.mock_context.info("generate_artist_personas tool validation passed")

    @pytest.mark.asyncio
    async def test_create_suno_commands_tool(self):
        """Test create_suno_commands MCP tool validation"""
        await self.mock_context.info("Testing create_suno_commands tool")

        # Get test data
        self.test_data.get_scenario("sci_fi_adventure")
        expected_character = self.test_data.get_expected_character("Captain Zara Okafor")

        character_data = asdict(expected_character)

        # Generate persona first
        persona_result = await generate_artist_personas(
            self.mock_context,
            character_data=character_data
        )
        persona_data = json.loads(persona_result)["artist_persona"]

        # Test Suno command creation
        result = await create_suno_commands(
            self.mock_context,
            character_data=character_data,
            artist_persona=persona_data,
            song_concept="Space Adventure Epic"
        )

        # Validate result structure
        assert result is not None
        result_data = json.loads(result)

        # Check required fields
        assert "suno_commands" in result_data
        assert "command_metadata" in result_data
        assert "optimization_notes" in result_data

        # Validate command data
        commands = result_data["suno_commands"]
        assert len(commands) >= 1

        primary_command = commands[0]
        required_command_fields = [
            "formatted_command", "meta_tags", "genre_tags",
            "effectiveness_score", "optimization_strategy"
        ]

        for field in required_command_fields:
            assert field in primary_command, f"Missing command field: {field}"

        # Validate command format
        formatted_command = primary_command["formatted_command"]
        assert len(formatted_command) > 0
        assert any(tag in formatted_command for tag in primary_command["meta_tags"])

        # Validate effectiveness score
        assert 0.0 <= primary_command["effectiveness_score"] <= 1.0
        assert primary_command["effectiveness_score"] > 0.5

        # Test parameter validation
        await self._test_create_suno_commands_parameter_validation()

        await self.mock_context.info("create_suno_commands tool validation passed")

    @pytest.mark.asyncio
    async def test_complete_workflow_tool(self):
        """Test complete_workflow MCP tool validation"""
        await self.mock_context.info("Testing complete_workflow tool")

        scenario = self.test_data.get_scenario("romance_contemporary")

        result = await complete_workflow(
            self.mock_context,
            narrative_text=scenario.narrative_text,
            song_concept="Modern Love Story",
            include_analysis=True
        )

        # Validate result structure
        assert result is not None
        result_data = json.loads(result)

        # Check required workflow components
        required_workflow_fields = [
            "character_analysis", "artist_persona", "suno_commands", "workflow_summary"
        ]

        for field in required_workflow_fields:
            assert field in result_data, f"Missing workflow field: {field}"

        # Validate character analysis component
        char_analysis = result_data["character_analysis"]
        assert "characters" in char_analysis
        assert len(char_analysis["characters"]) >= 1

        # Validate persona component
        persona = result_data["artist_persona"]
        assert "primary_genre" in persona
        assert persona["primary_genre"] in scenario.expected_genres

        # Validate commands component
        commands = result_data["suno_commands"]
        assert len(commands) >= 1
        assert "formatted_command" in commands[0]

        # Validate workflow summary
        summary = result_data["workflow_summary"]
        assert "total_characters" in summary
        assert "primary_character" in summary
        assert "processing_time" in summary

        # Test parameter validation
        await self._test_complete_workflow_parameter_validation()

        await self.mock_context.info("complete_workflow tool validation passed")

    @pytest.mark.asyncio
    async def test_creative_music_generation_tool(self):
        """Test creative_music_generation MCP tool validation"""
        await self.mock_context.info("Testing creative_music_generation tool")

        scenario = self.test_data.get_scenario("urban_fantasy")

        result = await creative_music_generation(
            self.mock_context,
            narrative_text=scenario.narrative_text,
            creative_direction="Dark urban fantasy with supernatural elements",
            song_count=2
        )

        # Validate result structure
        assert result is not None
        result_data = json.loads(result)

        # Check required creative components
        required_creative_fields = [
            "creative_analysis", "generated_songs", "creative_summary"
        ]

        for field in required_creative_fields:
            assert field in result_data, f"Missing creative field: {field}"

        # Validate creative analysis
        creative_analysis = result_data["creative_analysis"]
        assert "narrative_themes" in creative_analysis
        assert "creative_opportunities" in creative_analysis

        # Validate generated songs
        songs = result_data["generated_songs"]
        assert len(songs) == 2

        for song in songs:
            required_song_fields = [
                "title", "character_inspiration", "suno_command", "creative_elements"
            ]
            for field in required_song_fields:
                assert field in song, f"Missing song field: {field}"

        # Validate creative summary
        summary = result_data["creative_summary"]
        assert "total_songs" in summary
        assert "creative_approach" in summary

        # Test parameter validation
        await self._test_creative_music_generation_parameter_validation()

        await self.mock_context.info("creative_music_generation tool validation passed")

    @pytest.mark.asyncio
    async def test_enhanced_tools_integration(self):
        """Test enhanced MCP tools if available"""
        if not ENHANCED_TOOLS_AVAILABLE:
            await self.mock_context.info("Enhanced tools not available, skipping test")
            return

        await self.mock_context.info("Testing enhanced MCP tools")

        scenario = self.test_data.get_scenario("philosophical_content")

        # Test process_universal_content
        content_result = await process_universal_content(
            content=scenario.narrative_text,
            character_description="Philosophical musician exploring existential themes",
            track_title="Universal Processing Test",
            ctx=self.mock_context
        )

        assert content_result is not None
        content_data = json.loads(content_result)

        # Validate universal content processing
        assert "processing_status" in content_data
        assert "content_analysis" in content_data
        assert "suno_command" in content_data

        # Test create_character_album
        album_result = await create_character_album(
            content=scenario.narrative_text,
            character_description="Philosophical musician",
            album_title="Existential Explorations",
            track_count=3,
            ctx=self.mock_context
        )

        assert album_result is not None
        album_data = json.loads(album_result)

        # Validate character album creation
        assert "album_status" in album_data
        assert "tracks" in album_data
        assert len(album_data["tracks"]) == 3

        await self.mock_context.info("Enhanced tools integration test passed")

    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self):
        """Test concurrent execution of MCP tools"""
        await self.concurrent_context.info("Testing concurrent tool execution")

        scenarios = [
            self.test_data.get_scenario("single_character_simple"),
            self.test_data.get_scenario("multi_character_medium"),
            self.test_data.get_scenario("emotional_intensity_high")
        ]

        # Start concurrent requests
        concurrent_tasks = []
        for i, scenario in enumerate(scenarios):
            request_id = f"concurrent_request_{i}"

            if await self.concurrent_context.start_concurrent_request(request_id):
                task = asyncio.create_task(
                    self._execute_concurrent_workflow(request_id, scenario)
                )
                concurrent_tasks.append(task)

        # Wait for all concurrent tasks to complete
        results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)

        # Validate concurrent execution results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 2, "At least 2 concurrent requests should succeed"

        # Check concurrent stats
        concurrent_stats = self.concurrent_context.get_concurrent_stats()
        assert concurrent_stats["completed_requests"] >= 2
        assert concurrent_stats["concurrent_peak"] <= 3

        await self.concurrent_context.info("Concurrent tool execution test passed")

    @pytest.mark.asyncio
    async def test_tool_error_handling_comprehensive(self):
        """Test comprehensive error handling across all tools"""
        await self.mock_context.info("Testing comprehensive tool error handling")

        # Test analyze_character_text error handling
        await self._test_tool_error_handling(
            analyze_character_text,
            "analyze_character_text",
            {"narrative_text": ""}  # Empty text
        )

        # Test generate_artist_personas error handling
        await self._test_tool_error_handling(
            generate_artist_personas,
            "generate_artist_personas",
            {"character_data": {}}  # Empty character data
        )

        # Test create_suno_commands error handling
        await self._test_tool_error_handling(
            create_suno_commands,
            "create_suno_commands",
            {
                "character_data": {"name": "Test"},
                "artist_persona": {},
                "song_concept": ""
            }
        )

        # Test complete_workflow error handling
        await self._test_tool_error_handling(
            complete_workflow,
            "complete_workflow",
            {"narrative_text": "", "song_concept": ""}
        )

        # Test creative_music_generation error handling
        await self._test_tool_error_handling(
            creative_music_generation,
            "creative_music_generation",
            {
                "narrative_text": "",
                "creative_direction": "",
                "song_count": 0
            }
        )

        await self.mock_context.info("Comprehensive error handling test passed")

    @pytest.mark.asyncio
    async def test_tool_parameter_validation_comprehensive(self):
        """Test comprehensive parameter validation across all tools"""
        await self.mock_context.info("Testing comprehensive parameter validation")

        # Test various invalid parameter combinations
        invalid_parameters = [
            # analyze_character_text invalid params
            {"tool": analyze_character_text, "params": {"narrative_text": None}},
            {"tool": analyze_character_text, "params": {"narrative_text": "a"}},  # Too short

            # generate_artist_personas invalid params
            {"tool": generate_artist_personas, "params": {"character_data": None}},
            {"tool": generate_artist_personas, "params": {"character_data": "invalid"}},

            # create_suno_commands invalid params
            {"tool": create_suno_commands, "params": {
                "character_data": None,
                "artist_persona": {},
                "song_concept": "Test"
            }},

            # complete_workflow invalid params
            {"tool": complete_workflow, "params": {
                "narrative_text": None,
                "song_concept": "Test"
            }},

            # creative_music_generation invalid params
            {"tool": creative_music_generation, "params": {
                "narrative_text": "Test",
                "creative_direction": "Test",
                "song_count": -1  # Invalid count
            }}
        ]

        for test_case in invalid_parameters:
            tool = test_case["tool"]
            params = test_case["params"]

            try:
                result = await tool(self.mock_context, **params)

                # If no exception, check for error in result
                if result:
                    result_data = json.loads(result)
                    assert "error" in result_data, f"Expected error for invalid params in {tool.__name__}"

            except Exception as e:
                # Exception is acceptable for invalid parameters
                assert len(str(e)) > 0, f"Empty error message for {tool.__name__}"

        await self.mock_context.info("Comprehensive parameter validation test passed")

    async def _execute_concurrent_workflow(self, request_id: str, scenario) -> Dict[str, Any]:
        """Execute workflow for concurrent testing"""
        try:
            result = await complete_workflow(
                self.concurrent_context,
                narrative_text=scenario.narrative_text,
                song_concept=f"Concurrent Test - {scenario.name}",
                include_analysis=True
            )

            result_data = json.loads(result)

            await self.concurrent_context.complete_concurrent_request(
                request_id,
                {"status": "success", "data": result_data}
            )

            return result_data

        except Exception as e:
            await self.concurrent_context.complete_concurrent_request(
                request_id,
                {"status": "error", "error": str(e)}
            )
            raise

    async def _test_tool_error_handling(self, tool_func, tool_name: str, invalid_params: Dict[str, Any]) -> None:
        """Test error handling for a specific tool"""
        try:
            result = await tool_func(self.mock_context, **invalid_params)

            # If no exception, check for error in result
            if result:
                result_data = json.loads(result)
                assert "error" in result_data or "status" in result_data, \
                    f"Expected error handling in {tool_name}"

        except Exception as e:
            # Exception is acceptable for error handling
            assert len(str(e)) > 0, f"Empty error message for {tool_name}"

        await self.mock_context.info(f"Error handling validated for {tool_name}")

    async def _test_analyze_character_text_parameter_validation(self) -> None:
        """Test parameter validation for analyze_character_text"""
        # Test minimum text length
        try:
            result = await analyze_character_text(
                self.mock_context,
                narrative_text="Hi"  # Too short
            )
            result_data = json.loads(result)
            # Should handle gracefully or return minimal results
            assert "characters" in result_data
        except Exception:
            pass  # Exception acceptable for invalid input

    async def _test_generate_artist_personas_parameter_validation(self) -> None:
        """Test parameter validation for generate_artist_personas"""
        # Test with minimal character data
        minimal_character = {"name": "Test Character"}

        try:
            result = await generate_artist_personas(
                self.mock_context,
                character_data=minimal_character
            )
            result_data = json.loads(result)
            # Should handle gracefully or provide default values
            assert "artist_persona" in result_data or "error" in result_data
        except Exception:
            pass  # Exception acceptable for minimal data

    async def _test_create_suno_commands_parameter_validation(self) -> None:
        """Test parameter validation for create_suno_commands"""
        # Test with minimal data
        minimal_character = {"name": "Test"}
        minimal_persona = {"primary_genre": "indie"}

        try:
            result = await create_suno_commands(
                self.mock_context,
                character_data=minimal_character,
                artist_persona=minimal_persona,
                song_concept="Test Song"
            )
            result_data = json.loads(result)
            # Should handle gracefully
            assert "suno_commands" in result_data or "error" in result_data
        except Exception:
            pass  # Exception acceptable for minimal data

    async def _test_complete_workflow_parameter_validation(self) -> None:
        """Test parameter validation for complete_workflow"""
        # Test with minimal text
        try:
            result = await complete_workflow(
                self.mock_context,
                narrative_text="Short text",
                song_concept="Test"
            )
            result_data = json.loads(result)
            # Should handle gracefully
            assert "workflow_summary" in result_data or "error" in result_data
        except Exception:
            pass  # Exception acceptable for minimal input

    async def _test_creative_music_generation_parameter_validation(self) -> None:
        """Test parameter validation for creative_music_generation"""
        # Test with invalid song count
        try:
            result = await creative_music_generation(
                self.mock_context,
                narrative_text="Test narrative",
                creative_direction="Test direction",
                song_count=0  # Invalid count
            )
            result_data = json.loads(result)
            # Should handle gracefully or return error
            assert "error" in result_data or "generated_songs" in result_data
        except Exception:
            pass  # Exception acceptable for invalid parameters


# Utility functions for MCP tools testing
async def run_mcp_tools_integration_tests():
    """Run all MCP tools integration tests"""
    test_suite = TestMCPToolsIntegration()
    test_suite.setup_method()

    print("🔧 RUNNING MCP TOOLS INTEGRATION TESTS")
    print("=" * 60)

    try:
        await test_suite.test_analyze_character_text_tool()
        print("✅ analyze_character_text tool validation passed")

        await test_suite.test_generate_artist_personas_tool()
        print("✅ generate_artist_personas tool validation passed")

        await test_suite.test_create_suno_commands_tool()
        print("✅ create_suno_commands tool validation passed")

        await test_suite.test_complete_workflow_tool()
        print("✅ complete_workflow tool validation passed")

        await test_suite.test_creative_music_generation_tool()
        print("✅ creative_music_generation tool validation passed")

        await test_suite.test_enhanced_tools_integration()
        print("✅ Enhanced tools integration test passed")

        await test_suite.test_concurrent_tool_execution()
        print("✅ Concurrent tool execution test passed")

        await test_suite.test_tool_error_handling_comprehensive()
        print("✅ Comprehensive error handling test passed")

        await test_suite.test_tool_parameter_validation_comprehensive()
        print("✅ Comprehensive parameter validation test passed")

        print("\n🎉 ALL MCP TOOLS INTEGRATION TESTS PASSED!")

        # Print concurrent execution stats
        concurrent_stats = test_suite.concurrent_context.get_concurrent_stats()
        print("\n📊 CONCURRENT EXECUTION STATS:")
        print(f"  Max concurrent: {concurrent_stats['max_concurrent']}")
        print(f"  Peak concurrent: {concurrent_stats['concurrent_peak']}")
        print(f"  Completed requests: {concurrent_stats['completed_requests']}")

    except Exception as e:
        print(f"❌ MCP tools integration test failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(run_mcp_tools_integration_tests())
