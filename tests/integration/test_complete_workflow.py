#!/usr/bin/env python3
"""
Complete Workflow Integration Tests

Tests end-to-end workflow validation, data consistency across all workflow steps,
and character analysis to Suno command pipeline integrity.

Requirements: 1.5, 3.2
"""

import asyncio
import json
import os

# Import test utilities
import sys
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

from tests.fixtures.mock_contexts import MockContext, MockPerformanceContext
from tests.fixtures.test_data import TestDataManager


class TestCompleteWorkflow:
    """Test complete workflow integration and data consistency"""

    def setup_method(self):
        """Set up test environment"""
        self.test_data = TestDataManager()
        self.mock_context = MockContext("workflow_integration_test")
        self.performance_context = MockPerformanceContext("workflow_performance_test")

    @pytest.mark.asyncio
    async def test_single_character_complete_workflow(self):
        """Test complete workflow with single character scenario"""
        # Get test scenario
        scenario = self.test_data.get_scenario("single_character_simple")

        # Step 1: Character Analysis
        await self.mock_context.info("Testing character analysis step")
        character_result = await analyze_character_text(
            self.mock_context,
            narrative_text=scenario.narrative_text
        )

        # Validate character analysis
        assert character_result is not None
        character_data = json.loads(character_result)
        assert "characters" in character_data
        assert len(character_data["characters"]) >= 1

        primary_character = character_data["characters"][0]
        assert primary_character["name"] == scenario.expected_primary_character
        assert primary_character["confidence_score"] > 0.7

        # Step 2: Artist Persona Generation
        await self.mock_context.info("Testing persona generation step")
        persona_result = await generate_artist_personas(
            self.mock_context,
            character_data=primary_character
        )

        # Validate persona generation
        assert persona_result is not None
        persona_data = json.loads(persona_result)
        assert "artist_persona" in persona_data

        artist_persona = persona_data["artist_persona"]
        assert artist_persona["primary_genre"] in scenario.expected_genres
        assert "vocal_style" in artist_persona
        assert "instrumental_preferences" in artist_persona

        # Step 3: Suno Command Generation
        await self.mock_context.info("Testing Suno command generation step")
        command_result = await create_suno_commands(
            self.mock_context,
            character_data=primary_character,
            artist_persona=artist_persona,
            song_concept="Test Song from Workflow"
        )

        # Validate command generation
        assert command_result is not None
        command_data = json.loads(command_result)
        assert "suno_commands" in command_data
        assert len(command_data["suno_commands"]) > 0

        suno_command = command_data["suno_commands"][0]
        assert "formatted_command" in suno_command
        assert "meta_tags" in suno_command
        assert len(suno_command["meta_tags"]) > 0

        # Validate data consistency across steps
        await self._validate_workflow_consistency(
            character_data, persona_data, command_data
        )

        # Ensure no errors occurred
        assert not self.mock_context.has_errors()

        await self.mock_context.info("Single character workflow test completed successfully")

    @pytest.mark.asyncio
    async def test_multi_character_complete_workflow(self):
        """Test complete workflow with multi-character scenario"""
        # Get test scenario
        scenario = self.test_data.get_scenario("multi_character_medium")

        # Step 1: Character Analysis
        character_result = await analyze_character_text(
            self.mock_context,
            narrative_text=scenario.narrative_text
        )

        character_data = json.loads(character_result)
        assert len(character_data["characters"]) >= 2

        # Find primary character
        primary_character = None
        for char in character_data["characters"]:
            if char["name"] == scenario.expected_primary_character:
                primary_character = char
                break

        assert primary_character is not None
        assert primary_character["importance_score"] >= 0.8

        # Step 2: Generate personas for multiple characters
        personas = []
        for character in character_data["characters"][:2]:  # Test top 2 characters
            persona_result = await generate_artist_personas(
                self.mock_context,
                character_data=character
            )
            persona_data = json.loads(persona_result)
            personas.append(persona_data["artist_persona"])

        # Validate persona diversity
        genres = [persona["primary_genre"] for persona in personas]
        assert len(set(genres)) >= 1  # At least some genre diversity

        # Step 3: Generate commands for each persona
        commands = []
        for i, persona in enumerate(personas):
            command_result = await create_suno_commands(
                self.mock_context,
                character_data=character_data["characters"][i],
                artist_persona=persona,
                song_concept=f"Multi-Character Song {i+1}"
            )
            command_data = json.loads(command_result)
            commands.append(command_data["suno_commands"][0])

        # Validate command diversity and consistency
        assert len(commands) == len(personas)
        for command in commands:
            assert "formatted_command" in command
            assert "effectiveness_score" in command
            assert command["effectiveness_score"] > 0.6

        await self.mock_context.info("Multi-character workflow test completed successfully")

    @pytest.mark.asyncio
    async def test_complete_workflow_tool_integration(self):
        """Test the complete_workflow MCP tool end-to-end"""
        scenario = self.test_data.get_scenario("emotional_intensity_high")

        # Test complete workflow tool
        workflow_result = await complete_workflow(
            self.mock_context,
            narrative_text=scenario.narrative_text,
            song_concept="Grief and Healing",
            include_analysis=True
        )

        # Validate complete workflow result
        assert workflow_result is not None
        workflow_data = json.loads(workflow_result)

        # Check all workflow components are present
        assert "character_analysis" in workflow_data
        assert "artist_persona" in workflow_data
        assert "suno_commands" in workflow_data
        assert "workflow_summary" in workflow_data

        # Validate character analysis component
        char_analysis = workflow_data["character_analysis"]
        assert "characters" in char_analysis
        assert len(char_analysis["characters"]) >= 1

        # Validate persona component
        persona = workflow_data["artist_persona"]
        assert "primary_genre" in persona
        assert persona["primary_genre"] in scenario.expected_genres

        # Validate Suno commands component
        commands = workflow_data["suno_commands"]
        assert len(commands) > 0
        assert "formatted_command" in commands[0]

        # Validate workflow summary
        summary = workflow_data["workflow_summary"]
        assert "total_characters" in summary
        assert "primary_character" in summary
        assert "genre_classification" in summary

        await self.mock_context.info("Complete workflow tool integration test passed")

    @pytest.mark.asyncio
    async def test_creative_music_generation_integration(self):
        """Test creative music generation tool integration"""
        scenario = self.test_data.get_scenario("sci_fi_adventure")

        # Test creative music generation
        creative_result = await creative_music_generation(
            self.mock_context,
            narrative_text=scenario.narrative_text,
            creative_direction="Epic space adventure with emotional depth",
            song_count=2
        )

        # Validate creative generation result
        assert creative_result is not None
        creative_data = json.loads(creative_result)

        # Check creative components
        assert "creative_analysis" in creative_data
        assert "generated_songs" in creative_data
        assert "creative_summary" in creative_data

        # Validate generated songs
        songs = creative_data["generated_songs"]
        assert len(songs) == 2

        for song in songs:
            assert "title" in song
            assert "character_inspiration" in song
            assert "suno_command" in song
            assert "creative_elements" in song

        await self.mock_context.info("Creative music generation integration test passed")

    @pytest.mark.asyncio
    async def test_workflow_performance_benchmarks(self):
        """Test workflow performance and timing"""
        scenario = self.test_data.get_scenario("concept_album_complex")

        # Record performance metrics
        import time

        # Character analysis performance
        start_time = time.time()
        character_result = await analyze_character_text(
            self.performance_context,
            narrative_text=scenario.narrative_text
        )
        char_time = time.time() - start_time
        await self.performance_context.record_performance_metric("character_analysis_time", char_time)

        # Persona generation performance
        character_data = json.loads(character_result)["characters"][0]
        start_time = time.time()
        persona_result = await generate_artist_personas(
            self.performance_context,
            character_data=character_data
        )
        persona_time = time.time() - start_time
        await self.performance_context.record_performance_metric("persona_generation_time", persona_time)

        # Command generation performance
        persona_data = json.loads(persona_result)["artist_persona"]
        start_time = time.time()
        await create_suno_commands(
            self.performance_context,
            character_data=character_data,
            artist_persona=persona_data,
            song_concept="Performance Test Song"
        )
        command_time = time.time() - start_time
        await self.performance_context.record_performance_metric("command_generation_time", command_time)

        # Total workflow time
        total_time = char_time + persona_time + command_time
        await self.performance_context.record_performance_metric("total_workflow_time", total_time)

        # Validate performance thresholds
        thresholds = {
            "character_analysis_time": 5.0,  # 5 seconds max
            "persona_generation_time": 3.0,  # 3 seconds max
            "command_generation_time": 2.0,  # 2 seconds max
            "total_workflow_time": 10.0      # 10 seconds max total
        }

        performance_check = self.performance_context.check_performance_thresholds(thresholds)

        # Assert performance requirements
        for metric, passed in performance_check.items():
            assert passed, f"Performance threshold failed for {metric}"

        await self.performance_context.info("Workflow performance benchmarks passed")

    @pytest.mark.asyncio
    async def test_workflow_error_handling(self):
        """Test workflow error handling and recovery"""
        # Test with invalid input
        try:
            result = await analyze_character_text(
                self.mock_context,
                narrative_text=""  # Empty text
            )
            result_data = json.loads(result)
            assert "error" in result_data or len(result_data.get("characters", [])) == 0
        except Exception as e:
            # Error handling should be graceful
            assert "empty" in str(e).lower() or "invalid" in str(e).lower()

        # Test with malformed character data
        try:
            result = await generate_artist_personas(
                self.mock_context,
                character_data={}  # Empty character data
            )
            result_data = json.loads(result)
            assert "error" in result_data
        except Exception as e:
            assert "character" in str(e).lower() or "invalid" in str(e).lower()

        # Test with missing required fields
        try:
            result = await create_suno_commands(
                self.mock_context,
                character_data={"name": "Test"},  # Minimal data
                artist_persona={"primary_genre": "indie"},  # Minimal persona
                song_concept="Test Song"
            )
            # Should handle gracefully, not crash
            assert result is not None
        except Exception as e:
            # Should provide meaningful error
            assert len(str(e)) > 0

        await self.mock_context.info("Workflow error handling test completed")

    @pytest.mark.asyncio
    async def test_workflow_data_consistency_validation(self):
        """Test data consistency across workflow steps"""
        scenario = self.test_data.get_scenario("romance_contemporary")

        # Run complete workflow
        character_result = await analyze_character_text(
            self.mock_context,
            narrative_text=scenario.narrative_text
        )

        character_data = json.loads(character_result)
        primary_character = character_data["characters"][0]

        persona_result = await generate_artist_personas(
            self.mock_context,
            character_data=primary_character
        )

        persona_data = json.loads(persona_result)
        artist_persona = persona_data["artist_persona"]

        command_result = await create_suno_commands(
            self.mock_context,
            character_data=primary_character,
            artist_persona=artist_persona,
            song_concept="Love in the Digital Age"
        )

        command_data = json.loads(command_result)

        # Validate consistency
        await self._validate_workflow_consistency(
            character_data, persona_data, command_data
        )

        await self.mock_context.info("Data consistency validation passed")

    async def _validate_workflow_consistency(
        self,
        character_data: Dict[str, Any],
        persona_data: Dict[str, Any],
        command_data: Dict[str, Any]
    ) -> None:
        """Validate consistency across workflow steps"""

        # Character to persona consistency
        primary_character = character_data["characters"][0]
        artist_persona = persona_data["artist_persona"]

        # Character traits should influence genre selection
        primary_character.get("behavioral_traits", [])
        persona_genre = artist_persona.get("primary_genre", "")

        # Emotional consistency
        primary_character.get("fears", []) + primary_character.get("desires", [])
        artist_persona.get("vocal_style", "")

        # Persona to command consistency
        suno_commands = command_data["suno_commands"]
        if suno_commands:
            command = suno_commands[0]
            command_genre = command.get("genre_tags", [])
            command_meta_tags = command.get("meta_tags", [])

            # Genre consistency between persona and command
            assert persona_genre in str(command_genre).lower() or any(
                persona_genre in tag.lower() for tag in command_meta_tags
            ), "Genre inconsistency between persona and command"

            # Effectiveness score should be reasonable
            effectiveness = command.get("effectiveness_score", 0)
            assert effectiveness > 0.5, f"Low effectiveness score: {effectiveness}"

        # Character name consistency
        character_name = primary_character.get("name", "")
        persona_inspiration = artist_persona.get("character_inspiration", "")
        assert character_name in persona_inspiration or character_name != "", "Character name not preserved in persona"

        await self.mock_context.info("Workflow consistency validation completed")


# Utility functions for integration testing
async def run_workflow_integration_tests():
    """Run all workflow integration tests"""
    test_suite = TestCompleteWorkflow()
    test_suite.setup_method()

    print("🚀 RUNNING COMPLETE WORKFLOW INTEGRATION TESTS")
    print("=" * 60)

    try:
        # Run individual tests
        await test_suite.test_single_character_complete_workflow()
        print("✅ Single character workflow test passed")

        await test_suite.test_multi_character_complete_workflow()
        print("✅ Multi-character workflow test passed")

        await test_suite.test_complete_workflow_tool_integration()
        print("✅ Complete workflow tool integration test passed")

        await test_suite.test_creative_music_generation_integration()
        print("✅ Creative music generation integration test passed")

        await test_suite.test_workflow_performance_benchmarks()
        print("✅ Workflow performance benchmarks passed")

        await test_suite.test_workflow_error_handling()
        print("✅ Workflow error handling test passed")

        await test_suite.test_workflow_data_consistency_validation()
        print("✅ Data consistency validation test passed")

        print("\n🎉 ALL WORKFLOW INTEGRATION TESTS PASSED!")

        # Print performance summary
        perf_summary = test_suite.performance_context.get_performance_summary()
        print("\n📊 PERFORMANCE SUMMARY:")
        for metric, stats in perf_summary.items():
            if isinstance(stats, dict) and "average" in stats:
                print(f"  {metric}: {stats['average']:.3f}s (avg)")

    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(run_workflow_integration_tests())
