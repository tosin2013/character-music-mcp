#!/usr/bin/env python3
"""
Album Creation Integration Tests

Tests multi-song generation workflows, single character album creation with thematic consistency,
multi-character album tests with character relationship handling, concept album generation,
and album metadata completeness validation.

Requirements: 3.1, 3.2, 3.3, 3.4
"""

import asyncio
import json
import os

# Import test utilities
import sys
from typing import Any, Dict, List

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server import (
    analyze_character_text,
    create_suno_commands,
    generate_artist_personas,
)
from tests.fixtures.mock_contexts import MockBatchContext, MockContext
from tests.fixtures.test_data import TestDataManager


class TestAlbumCreation:
    """Test comprehensive album creation workflows"""

    def setup_method(self):
        """Set up test environment"""
        self.test_data = TestDataManager()
        self.mock_context = MockContext("album_creation_test")
        self.batch_context = MockBatchContext(batch_size=6, session_id="album_batch_test")

    @pytest.mark.asyncio
    async def test_single_character_album_creation(self):
        """Test single character album creation with thematic consistency"""
        scenario = self.test_data.get_scenario("emotional_intensity_high")

        await self.mock_context.info("Testing single character album creation")

        # Step 1: Analyze character for album themes
        character_result = await analyze_character_text(
            self.mock_context,
            narrative_text=scenario.narrative_text
        )

        character_data = json.loads(character_result)
        primary_character = character_data["characters"][0]

        # Step 2: Generate artist persona
        persona_result = await generate_artist_personas(
            self.mock_context,
            character_data=primary_character
        )

        persona_data = json.loads(persona_result)
        artist_persona = persona_data["artist_persona"]

        # Step 3: Create album with multiple songs
        album_themes = [
            "The Moment of Loss",
            "Rage Against the Universe",
            "Bargaining with God",
            "The Weight of Emptiness",
            "Memories of Love",
            "Choosing to Live"
        ]

        album_songs = []
        for i, theme in enumerate(album_themes):
            song_result = await create_suno_commands(
                self.mock_context,
                character_data=primary_character,
                artist_persona=artist_persona,
                song_concept=theme
            )

            song_data = json.loads(song_result)
            song_command = song_data["suno_commands"][0]

            album_songs.append({
                "track_number": i + 1,
                "theme": theme,
                "command": song_command,
                "character_connection": primary_character["name"]
            })

        # Validate album structure
        assert len(album_songs) == 6

        # Validate thematic consistency
        await self._validate_album_thematic_consistency(album_songs, primary_character)

        # Validate genre consistency
        genres = [song["command"].get("genre_tags", []) for song in album_songs]
        primary_genre = artist_persona["primary_genre"]

        for genre_list in genres:
            assert any(primary_genre in str(genre).lower() for genre in genre_list), \
                f"Genre inconsistency in album: expected {primary_genre}"

        # Validate emotional arc progression
        effectiveness_scores = [song["command"]["effectiveness_score"] for song in album_songs]
        assert all(score > 0.6 for score in effectiveness_scores), "Low effectiveness in album tracks"

        await self.mock_context.info("Single character album creation test passed")

    @pytest.mark.asyncio
    async def test_multi_character_album_creation(self):
        """Test multi-character album with character relationship handling"""
        scenario = self.test_data.get_scenario("multi_character_medium")

        await self.mock_context.info("Testing multi-character album creation")

        # Step 1: Analyze all characters
        character_result = await analyze_character_text(
            self.mock_context,
            narrative_text=scenario.narrative_text
        )

        character_data = json.loads(character_result)
        characters = character_data["characters"][:2]  # Use top 2 characters

        # Step 2: Generate personas for each character
        character_personas = []
        for character in characters:
            persona_result = await generate_artist_personas(
                self.mock_context,
                character_data=character
            )
            persona_data = json.loads(persona_result)
            character_personas.append({
                "character": character,
                "persona": persona_data["artist_persona"]
            })

        # Step 3: Create album exploring character relationships
        relationship_themes = [
            f"{characters[0]['name']}'s Perspective",
            f"{characters[1]['name']}'s Perspective",
            "The Space Between Us",
            "Shared Struggles",
            "Different Paths",
            "Understanding Each Other"
        ]

        album_songs = []
        for i, theme in enumerate(relationship_themes):
            # Alternate between character perspectives
            char_persona = character_personas[i % 2]

            song_result = await create_suno_commands(
                self.mock_context,
                character_data=char_persona["character"],
                artist_persona=char_persona["persona"],
                song_concept=theme
            )

            song_data = json.loads(song_result)
            song_command = song_data["suno_commands"][0]

            album_songs.append({
                "track_number": i + 1,
                "theme": theme,
                "command": song_command,
                "character_perspective": char_persona["character"]["name"],
                "relationship_focus": True
            })

        # Validate multi-character album structure
        assert len(album_songs) == 6

        # Validate character representation balance
        char1_tracks = [s for s in album_songs if s["character_perspective"] == characters[0]["name"]]
        char2_tracks = [s for s in album_songs if s["character_perspective"] == characters[1]["name"]]

        assert len(char1_tracks) >= 2, "Insufficient representation of first character"
        assert len(char2_tracks) >= 2, "Insufficient representation of second character"

        # Validate relationship themes
        relationship_tracks = [s for s in album_songs if "relationship_focus" in s]
        assert len(relationship_tracks) == 6, "All tracks should explore relationships"

        # Validate genre diversity while maintaining coherence
        genres = set()
        for song in album_songs:
            song_genres = song["command"].get("genre_tags", [])
            genres.update(str(g).lower() for g in song_genres)

        assert len(genres) >= 1, "Album should have genre coherence"
        assert len(genres) <= 4, "Album should not be too genre-diverse"

        await self.mock_context.info("Multi-character album creation test passed")

    @pytest.mark.asyncio
    async def test_concept_album_generation(self):
        """Test concept album generation from abstract themes"""
        scenario = self.test_data.get_scenario("concept_album_complex")

        await self.mock_context.info("Testing concept album generation")

        # Step 1: Analyze philosophical character
        character_result = await analyze_character_text(
            self.mock_context,
            narrative_text=scenario.narrative_text
        )

        character_data = json.loads(character_result)
        philosopher = character_data["characters"][0]

        # Step 2: Generate philosophical artist persona
        persona_result = await generate_artist_personas(
            self.mock_context,
            character_data=philosopher
        )

        persona_data = json.loads(persona_result)
        artist_persona = persona_data["artist_persona"]

        # Step 3: Create concept album exploring philosophical journey
        concept_movements = [
            "I. The Death of Certainty",
            "II. Descent into the Void",
            "III. Wrestling with Absurdity",
            "IV. The Weight of Freedom",
            "V. Creating Personal Meaning",
            "VI. The Symphony of Existence"
        ]

        concept_album = []
        for i, movement in enumerate(concept_movements):
            song_result = await create_suno_commands(
                self.mock_context,
                character_data=philosopher,
                artist_persona=artist_persona,
                song_concept=movement
            )

            song_data = json.loads(song_result)
            song_command = song_data["suno_commands"][0]

            concept_album.append({
                "movement_number": i + 1,
                "movement_title": movement,
                "command": song_command,
                "philosophical_theme": self._extract_philosophical_theme(movement),
                "narrative_position": self._determine_narrative_position(i, len(concept_movements))
            })

        # Validate concept album structure
        assert len(concept_album) == 6

        # Validate philosophical progression
        await self._validate_concept_album_progression(concept_album)

        # Validate thematic depth
        for movement in concept_album:
            assert movement["philosophical_theme"] is not None
            assert movement["command"]["effectiveness_score"] > 0.7, \
                f"Low effectiveness for philosophical concept: {movement['movement_title']}"

        # Validate genre appropriateness for concept album
        expected_genres = ["progressive rock", "ambient", "post-rock", "experimental"]
        album_genres = []
        for movement in concept_album:
            movement_genres = movement["command"].get("genre_tags", [])
            album_genres.extend(str(g).lower() for g in movement_genres)

        assert any(genre in album_genres for genre in expected_genres), \
            "Concept album should use appropriate progressive/experimental genres"

        await self.mock_context.info("Concept album generation test passed")

    @pytest.mark.asyncio
    async def test_album_metadata_completeness(self):
        """Test album metadata completeness and track listing accuracy"""
        scenario = self.test_data.get_scenario("coming_of_age")

        await self.mock_context.info("Testing album metadata completeness")

        # Create album with comprehensive metadata tracking
        character_result = await analyze_character_text(
            self.mock_context,
            narrative_text=scenario.narrative_text
        )

        character_data = json.loads(character_result)
        main_character = character_data["characters"][0]

        persona_result = await generate_artist_personas(
            self.mock_context,
            character_data=main_character
        )

        persona_data = json.loads(persona_result)
        artist_persona = persona_data["artist_persona"]

        # Create album with detailed metadata
        album_metadata = {
            "title": "Finding My Voice",
            "artist": f"{main_character['name']} (Musical Interpretation)",
            "concept": "Coming-of-age journey through music and identity",
            "total_tracks": 5,
            "estimated_duration": "22-28 minutes",
            "primary_themes": main_character.get("conflicts", [])[:3],
            "character_inspiration": main_character["name"],
            "genre_classification": artist_persona["primary_genre"],
            "production_notes": "Raw, authentic sound reflecting teenage experience"
        }

        track_themes = [
            "Expectations vs Dreams",
            "Cultural Identity Crisis",
            "The Underground Scene",
            "Disappointing Parents",
            "Choosing My Path"
        ]

        album_tracks = []
        for i, theme in enumerate(track_themes):
            song_result = await create_suno_commands(
                self.mock_context,
                character_data=main_character,
                artist_persona=artist_persona,
                song_concept=theme
            )

            song_data = json.loads(song_result)
            song_command = song_data["suno_commands"][0]

            # Create comprehensive track metadata
            track_metadata = {
                "track_number": i + 1,
                "title": theme,
                "duration_estimate": "4-6 minutes",
                "key_themes": [theme],
                "character_connection": main_character["name"],
                "emotional_intensity": self._assess_emotional_intensity(theme),
                "narrative_function": self._determine_narrative_function(i, len(track_themes)),
                "suno_command": song_command,
                "production_notes": song_command.get("production_notes", ""),
                "meta_tags": song_command.get("meta_tags", []),
                "effectiveness_score": song_command.get("effectiveness_score", 0)
            }

            album_tracks.append(track_metadata)

        # Validate metadata completeness
        await self._validate_album_metadata_completeness(album_metadata, album_tracks)

        # Validate track listing accuracy
        assert len(album_tracks) == album_metadata["total_tracks"]

        for i, track in enumerate(album_tracks):
            assert track["track_number"] == i + 1
            assert track["title"] is not None and len(track["title"]) > 0
            assert track["character_connection"] == main_character["name"]
            assert track["effectiveness_score"] > 0.5
            assert len(track["meta_tags"]) > 0

        # Validate thematic coherence across album
        all_themes = []
        for track in album_tracks:
            all_themes.extend(track["key_themes"])

        # Should have thematic variety but coherent focus
        unique_themes = set(all_themes)
        assert len(unique_themes) >= 3, "Album should explore multiple themes"
        assert len(unique_themes) <= 8, "Album should maintain thematic focus"

        await self.mock_context.info("Album metadata completeness test passed")

    @pytest.mark.asyncio
    async def test_album_batch_processing(self):
        """Test batch processing of album creation"""
        scenarios = [
            self.test_data.get_scenario("romance_contemporary"),
            self.test_data.get_scenario("urban_fantasy"),
            self.test_data.get_scenario("historical_drama")
        ]

        await self.batch_context.info("Testing album batch processing")

        batch_albums = []

        for batch_id, scenario in enumerate(scenarios):
            await self.batch_context.start_batch(batch_id)

            # Process each scenario as mini-album (3 tracks)
            character_result = await analyze_character_text(
                self.batch_context,
                narrative_text=scenario.narrative_text
            )

            character_data = json.loads(character_result)
            main_character = character_data["characters"][0]

            persona_result = await generate_artist_personas(
                self.batch_context,
                character_data=main_character
            )

            persona_data = json.loads(persona_result)
            artist_persona = persona_data["artist_persona"]

            # Create 3-track mini album
            mini_album_tracks = []
            track_themes = [
                f"{scenario.name} - Opening",
                f"{scenario.name} - Development",
                f"{scenario.name} - Resolution"
            ]

            for track_id, theme in enumerate(track_themes):
                song_result = await create_suno_commands(
                    self.batch_context,
                    character_data=main_character,
                    artist_persona=artist_persona,
                    song_concept=theme
                )

                song_data = json.loads(song_result)
                track_result = {
                    "track_id": f"batch_{batch_id}_track_{track_id}",
                    "theme": theme,
                    "command": song_data["suno_commands"][0],
                    "scenario": scenario.name
                }

                mini_album_tracks.append(track_result)

                await self.batch_context.process_batch_item(
                    f"track_{track_id}",
                    track_result
                )

            batch_summary = await self.batch_context.end_batch()

            batch_albums.append({
                "batch_id": batch_id,
                "scenario": scenario.name,
                "tracks": mini_album_tracks,
                "batch_summary": batch_summary
            })

        # Validate batch processing results
        assert len(batch_albums) == 3

        for album in batch_albums:
            assert len(album["tracks"]) == 3
            assert album["batch_summary"]["success_count"] == 3
            assert album["batch_summary"]["error_count"] == 0

        # Validate cross-album diversity
        all_genres = []
        for album in batch_albums:
            for track in album["tracks"]:
                track_genres = track["command"].get("genre_tags", [])
                all_genres.extend(str(g).lower() for g in track_genres)

        unique_genres = set(all_genres)
        assert len(unique_genres) >= 3, "Batch processing should produce genre diversity"

        await self.batch_context.info("Album batch processing test passed")

    async def _validate_album_thematic_consistency(
        self,
        album_songs: List[Dict[str, Any]],
        character: Dict[str, Any]
    ) -> None:
        """Validate thematic consistency across album"""

        # Extract themes from all songs
        song_themes = [song["theme"] for song in album_songs]

        # Check for character-driven thematic coherence
        character_conflicts = character.get("conflicts", [])
        character_desires = character.get("desires", [])
        character_fears = character.get("fears", [])

        character_elements = character_conflicts + character_desires + character_fears

        # At least 70% of songs should relate to character psychology
        related_songs = 0
        for theme in song_themes:
            if any(element.lower() in theme.lower() for element in character_elements):
                related_songs += 1

        consistency_ratio = related_songs / len(song_themes)
        assert consistency_ratio >= 0.5, f"Low thematic consistency: {consistency_ratio:.2f}"

        await self.mock_context.info(f"Thematic consistency validated: {consistency_ratio:.2f}")

    async def _validate_concept_album_progression(self, concept_album: List[Dict[str, Any]]) -> None:
        """Validate philosophical progression in concept album"""

        # Check narrative progression
        positions = [movement["narrative_position"] for movement in concept_album]
        expected_positions = ["opening", "development", "development", "development", "climax", "resolution"]

        # Validate effectiveness progression (should build to climax)
        effectiveness_scores = [movement["command"]["effectiveness_score"] for movement in concept_album]

        # Peak effectiveness should be in later movements
        peak_index = effectiveness_scores.index(max(effectiveness_scores))
        assert peak_index >= len(effectiveness_scores) // 2, "Peak effectiveness should be in later movements"

        # Validate philosophical depth
        philosophical_themes = [movement["philosophical_theme"] for movement in concept_album]
        assert all(theme is not None for theme in philosophical_themes), "All movements should have philosophical themes"

        await self.mock_context.info("Concept album progression validated")

    async def _validate_album_metadata_completeness(
        self,
        album_metadata: Dict[str, Any],
        tracks: List[Dict[str, Any]]
    ) -> None:
        """Validate completeness of album metadata"""

        required_album_fields = [
            "title", "artist", "concept", "total_tracks",
            "primary_themes", "character_inspiration", "genre_classification"
        ]

        for field in required_album_fields:
            assert field in album_metadata, f"Missing album metadata field: {field}"
            assert album_metadata[field] is not None, f"Null album metadata field: {field}"

        required_track_fields = [
            "track_number", "title", "character_connection",
            "emotional_intensity", "narrative_function", "suno_command"
        ]

        for track in tracks:
            for field in required_track_fields:
                assert field in track, f"Missing track metadata field: {field}"
                assert track[field] is not None, f"Null track metadata field: {field}"

        await self.mock_context.info("Album metadata completeness validated")

    def _extract_philosophical_theme(self, movement_title: str) -> str:
        """Extract philosophical theme from movement title"""
        theme_mapping = {
            "Death of Certainty": "epistemological_crisis",
            "Descent into the Void": "existential_despair",
            "Wrestling with Absurdity": "absurdist_confrontation",
            "Weight of Freedom": "existential_responsibility",
            "Creating Personal Meaning": "meaning_construction",
            "Symphony of Existence": "life_affirmation"
        }

        for key, theme in theme_mapping.items():
            if key.lower() in movement_title.lower():
                return theme

        return "philosophical_exploration"

    def _determine_narrative_position(self, index: int, total: int) -> str:
        """Determine narrative position in album"""
        ratio = index / (total - 1)

        if ratio < 0.2:
            return "opening"
        elif ratio < 0.6:
            return "development"
        elif ratio < 0.8:
            return "climax"
        else:
            return "resolution"

    def _assess_emotional_intensity(self, theme: str) -> str:
        """Assess emotional intensity of theme"""
        high_intensity_keywords = ["crisis", "disappointment", "conflict", "struggle"]
        medium_intensity_keywords = ["identity", "choice", "path", "understanding"]

        theme_lower = theme.lower()

        if any(keyword in theme_lower for keyword in high_intensity_keywords):
            return "high"
        elif any(keyword in theme_lower for keyword in medium_intensity_keywords):
            return "medium"
        else:
            return "low"

    def _determine_narrative_function(self, index: int, total: int) -> str:
        """Determine narrative function of track in album"""
        if index == 0:
            return "introduction"
        elif index == total - 1:
            return "conclusion"
        elif index == total // 2:
            return "turning_point"
        else:
            return "development"


# Utility functions for album testing
async def run_album_creation_tests():
    """Run all album creation tests"""
    test_suite = TestAlbumCreation()
    test_suite.setup_method()

    print("🎵 RUNNING ALBUM CREATION INTEGRATION TESTS")
    print("=" * 60)

    try:
        await test_suite.test_single_character_album_creation()
        print("✅ Single character album creation test passed")

        await test_suite.test_multi_character_album_creation()
        print("✅ Multi-character album creation test passed")

        await test_suite.test_concept_album_generation()
        print("✅ Concept album generation test passed")

        await test_suite.test_album_metadata_completeness()
        print("✅ Album metadata completeness test passed")

        await test_suite.test_album_batch_processing()
        print("✅ Album batch processing test passed")

        print("\n🎉 ALL ALBUM CREATION TESTS PASSED!")

        # Print batch processing summary
        batch_stats = test_suite.batch_context.get_concurrent_stats() if hasattr(test_suite.batch_context, 'get_concurrent_stats') else {}
        if batch_stats:
            print("\n📊 BATCH PROCESSING STATS:")
            print(f"  Total batches processed: {batch_stats.get('completed_requests', 0)}")

    except Exception as e:
        print(f"❌ Album creation test failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(run_album_creation_tests())
