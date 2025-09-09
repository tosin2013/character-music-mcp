#!/usr/bin/env python3
"""
Integration tests for conceptual album generation functionality

Tests the refactored functionality from the conceptual-album-generation-fixes spec:
- Content type detection logic
- Conceptual character creation from abstract content
- Album generation with meaningful track progression
- Validation that existing narrative fiction processing still works
"""

import json
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import test fixtures
from tests.fixtures.mock_contexts import create_mock_context
from tests.fixtures.test_data import TestDataManager

# Import components to test
try:
    from enhanced_character_analyzer import EnhancedCharacterAnalyzer
    from server import create_conceptual_album
    from standard_character_profile import StandardCharacterProfile
    from working_universal_processor import WorkingUniversalProcessor
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Components not available for testing: {e}")
    COMPONENTS_AVAILABLE = False


@pytest.mark.asyncio
@pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Required components not available")
class TestConceptualAlbumGeneration:
    """Test conceptual album generation functionality"""

    def setup_method(self):
        """Setup for each test method"""
        self.processor = WorkingUniversalProcessor()
        self.analyzer = EnhancedCharacterAnalyzer()
        self.test_data = TestDataManager()

    async def test_content_type_detection_philosophical(self):
        """Test content type detection for philosophical content"""
        philosophical_content = """
        The nature of existence is a question that has plagued humanity since the dawn of consciousness.
        What does it mean to be? To exist in a universe that seems indifferent to our struggles and aspirations?
        These questions form the foundation of existential philosophy, challenging us to find meaning in apparent meaninglessness.
        """

        # Test that philosophical content is detected as conceptual
        result = self.processor.detect_content_type(philosophical_content)

        assert result is not None
        assert "content_type" in result
        # Should detect as conceptual rather than narrative
        content_type = result.get("content_type", "")
        assert any(term in content_type.lower() for term in ["conceptual", "philosophical"])

    async def test_content_type_detection_narrative(self):
        """Test content type detection for narrative fiction"""
        narrative_content = """
        Sarah walked through the empty streets of downtown, her footsteps echoing off the wet pavement.
        She had been walking for hours, trying to clear her head after the argument with her mother.
        The rain had stopped, but the air still smelled of petrichor and possibility.
        As she turned the corner, she saw him standing there under the streetlight, waiting.
        """

        # Test that narrative content is detected correctly
        result = self.processor.detect_content_type(narrative_content)

        assert result is not None
        assert "content_type" in result
        # Should detect as narrative or mixed
        content_type = result.get("content_type", "")
        assert any(term in content_type.lower() for term in ["narrative", "story", "mixed"])

    async def test_content_type_detection_character_description(self):
        """Test content type detection for explicit character descriptions"""
        character_description = """
        Character Name: Marcus Chen
        Age: 34
        Background: A former software engineer turned street musician
        Personality: Introspective, passionate about social justice, struggles with anxiety
        Musical Style: Folk-punk with electronic elements
        Key Traits: Uses music as therapy, writes songs about urban alienation
        """

        # Test that character descriptions are detected correctly
        result = self.processor.detect_content_type(character_description)

        assert result is not None
        assert "content_type" in result
        # Should detect as character description
        content_type = result.get("content_type", "")
        assert any(term in content_type.lower() for term in ["character", "descriptive", "mixed"])

    async def test_conceptual_character_creation(self):
        """Test creation of characters from conceptual/philosophical content"""
        conceptual_content = """
        The concept of time as a river flowing in one direction is fundamentally flawed.
        Time is more like an ocean - vast, deep, with currents that flow in all directions.
        We are not passengers on a boat moving downstream, but swimmers in an infinite sea,
        capable of diving deep into the past or surfacing into possible futures.
        """

        ctx = create_mock_context()

        # Test conceptual character creation
        result = await self.analyzer.analyze_character_text(ctx, conceptual_content)

        assert result is not None
        characters = result.get("characters", [])
        assert len(characters) > 0

        # Verify character was created from concepts rather than extracted
        character = characters[0]
        assert character.get("name") is not None
        assert character.get("conceptual_basis") is not None
        assert "time" in str(character.get("conceptual_basis", "")).lower()

    async def test_album_generation_conceptual_content(self):
        """Test album generation from conceptual content"""
        conceptual_content = """
        The architecture of loneliness is built from silence and empty spaces.
        Each room represents a different type of solitude - the crowded loneliness of cities,
        the peaceful solitude of nature, the aching isolation of misunderstanding.
        These spaces shape us, define us, and ultimately teach us about connection.
        """

        ctx = create_mock_context()

        # Test album generation from conceptual content
        result_json = await create_conceptual_album(
            ctx=ctx,
            content=conceptual_content,
            album_concept="Architecture of Loneliness",
            track_count=5,
            genre="ambient"
        )

        result = json.loads(result_json)

        assert "error" not in result
        assert "tracks" in result
        assert len(result["tracks"]) == 5

        # Verify tracks have meaningful, unique titles
        track_titles = [track.get("title", "") for track in result["tracks"]]
        assert all(title and title != f"Track {i+1}" for i, title in enumerate(track_titles))
        assert len(set(track_titles)) == len(track_titles)  # All titles unique

        # Verify thematic coherence
        assert "album_info" in result
        assert "concept" in result["album_info"]
        assert "loneliness" in result["album_info"]["concept"].lower()

    async def test_album_generation_narrative_content(self):
        """Test that narrative fiction processing still works correctly"""
        narrative_content = """
        Elena had always been drawn to the old lighthouse on the cliff. As a child, she would climb
        the rocky path every summer evening, watching the beacon sweep across the dark ocean.
        Now, twenty years later, she stood at the same spot as the lighthouse keeper's daughter,
        responsible for maintaining the light that had guided her through so many storms.
        The weight of tradition and the pull of the modern world created a constant tension in her heart.
        """

        ctx = create_mock_context()

        # Test album generation from narrative content
        result_json = await create_conceptual_album(
            ctx=ctx,
            content=narrative_content,
            album_concept="The Lighthouse Keeper's Daughter",
            track_count=6,
            genre="folk"
        )

        result = json.loads(result_json)

        assert "error" not in result
        assert "tracks" in result
        assert len(result["tracks"]) == 6

        # Verify character-driven narrative progression
        assert "album_info" in result
        assert "protagonist" in result["album_info"]
        assert result["album_info"]["protagonist"] == "Elena"

        # Verify tracks follow narrative progression
        track_titles = [track.get("title", "") for track in result["tracks"]]
        assert any("lighthouse" in title.lower() for title in track_titles)

    async def test_track_content_uniqueness(self):
        """Test that generated tracks have unique content and avoid repetition"""
        content = """
        The journey of self-discovery begins with a single question: Who am I?
        This question leads to others: What do I value? What brings me joy?
        What are my fears? How do I relate to others? Each answer reveals new questions,
        creating an endless spiral of growth and understanding.
        """

        ctx = create_mock_context()

        result_json = await create_conceptual_album(
            ctx=ctx,
            content=content,
            album_concept="Questions of Self",
            track_count=7,
            genre="indie"
        )

        result = json.loads(result_json)

        assert "error" not in result
        assert "tracks" in result

        # Verify each track has unique content
        track_contents = []
        for track in result["tracks"]:
            track_content = track.get("lyrics", "") + track.get("description", "")
            track_contents.append(track_content.lower())

        # Check for excessive repetition (allowing some thematic consistency)
        for i, content1 in enumerate(track_contents):
            for j, content2 in enumerate(track_contents[i+1:], i+1):
                # Calculate similarity (simple word overlap check)
                words1 = set(content1.split())
                words2 = set(content2.split())
                if len(words1) > 0 and len(words2) > 0:
                    overlap = len(words1.intersection(words2))
                    similarity = overlap / min(len(words1), len(words2))
                    # Tracks shouldn't be more than 70% similar
                    assert similarity < 0.7, f"Tracks {i+1} and {j+1} are too similar"

    async def test_genre_specific_production_intelligence(self):
        """Test that genre-specific production techniques are applied correctly"""
        content = """
        The pulse of the city never stops. Concrete and steel create rhythms that echo
        through subway tunnels and bounce off skyscrapers. This urban symphony needs
        electronic interpretation - synthesized beats that match the mechanical heartbeat
        of metropolitan life.
        """

        ctx = create_mock_context()

        # Test with electronic genre
        result_json = await create_conceptual_album(
            ctx=ctx,
            content=content,
            album_concept="Urban Pulse",
            track_count=4,
            genre="electronic"
        )

        result = json.loads(result_json)

        assert "error" not in result
        assert "tracks" in result

        # Verify genre-appropriate elements are present
        album_info = result.get("album_info", {})
        assert album_info.get("genre") == "electronic"

        # Check that tracks contain genre-appropriate production notes
        for track in result["tracks"]:
            suno_command = track.get("suno_command", "").lower()
            # Should contain electronic-specific elements
            assert any(term in suno_command for term in [
                "electronic", "synth", "beat", "digital", "electronic drums"
            ])

    async def test_error_handling_and_fallbacks(self):
        """Test error handling and fallback strategies"""
        # Test with very short content (should trigger error handling)
        short_content = "Music."

        ctx = create_mock_context()

        result_json = await create_conceptual_album(
            ctx=ctx,
            content=short_content,
            album_concept="Test",
            track_count=3,
            genre="alternative"
        )

        result = json.loads(result_json)

        # Should handle gracefully with error message
        assert "error" in result
        assert "too short" in result["error"].lower()

    async def test_character_consistency_across_tracks(self):
        """Test that character voice and perspective remain consistent across album tracks"""
        content = """
        I am a night shift nurse in a city hospital. Every evening, I witness the full spectrum
        of human experience - birth, death, healing, suffering. The fluorescent lights and
        beeping machines create a strange lullaby that has become the soundtrack to my life.
        I find beauty in the small moments of care and connection that happen in the darkness.
        """

        ctx = create_mock_context()

        result_json = await create_conceptual_album(
            ctx=ctx,
            content=content,
            album_concept="Night Shift Chronicles",
            track_count=5,
            genre="alternative"
        )

        result = json.loads(result_json)

        assert "error" not in result
        assert "tracks" in result

        # Verify character consistency
        album_info = result.get("album_info", {})
        album_info.get("protagonist", "")

        # All tracks should maintain the nurse perspective
        for track in result["tracks"]:
            track_content = (track.get("lyrics", "") + " " + track.get("description", "")).lower()
            # Should contain nursing/medical references
            assert any(term in track_content for term in [
                "nurse", "hospital", "patient", "night", "shift", "medical", "care"
            ])


@pytest.mark.asyncio
@pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Required components not available")
class TestContentTypeDetectionEdgeCases:
    """Test edge cases for content type detection"""

    def setup_method(self):
        """Setup for each test method"""
        self.processor = WorkingUniversalProcessor()

    async def test_mixed_content_detection(self):
        """Test detection of mixed content types"""
        mixed_content = """
        Character: Dr. Sarah Chen, a philosopher who works nights as a taxi driver.

        Sarah often contemplates the nature of human connection while driving through
        the empty city streets. She believes that every passenger carries a universe
        of stories, and her job is to provide safe passage not just through the city,
        but through the moments of vulnerability that occur in the back seat of a cab.

        The existential weight of these encounters shapes her understanding of what
        it means to be truly present for another human being.
        """

        result = await self.processor.process_content(mixed_content)

        assert result is not None
        # Should detect as mixed or hybrid content
        content_type = result.get("content_type", "")
        assert content_type in ["mixed", "hybrid", "character_description", "narrative"]

    async def test_ambiguous_content_handling(self):
        """Test handling of ambiguous content that's hard to classify"""
        ambiguous_content = """
        Rain. Always rain in this place. The sound becomes part of you after a while,
        like breathing or heartbeat. Some days it's gentle, other days it pounds
        against the windows like it's trying to get in. Or maybe trying to get out.
        """

        result = await self.processor.process_content(ambiguous_content)

        assert result is not None
        # Should handle gracefully without crashing
        assert "content_type" in result
        # Should not be empty or None
        assert result.get("content_type") is not None
        assert result.get("content_type") != ""


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
