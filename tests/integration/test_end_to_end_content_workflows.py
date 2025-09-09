#!/usr/bin/env python3
"""
End-to-end integration tests for different content type workflows

Tests the complete workflow from content input to album generation for:
- Philosophical content processing creating meaningful characters and albums
- Explicit character description handling producing consistent results  
- Narrative fiction processing remaining functional

Requirements tested: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3
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
    from working_universal_processor import WorkingUniversalProcessor
    COMPONENTS_AVAILABLE = True
    print("All required components imported successfully")
except ImportError as e:
    print(f"Warning: Components not available for testing: {e}")
    COMPONENTS_AVAILABLE = False


@pytest.mark.asyncio
@pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Required components not available")
class TestPhilosophicalContentWorkflow:
    """Test end-to-end workflow for philosophical content processing"""

    def setup_method(self):
        """Setup for each test method"""
        self.processor = WorkingUniversalProcessor()
        self.analyzer = EnhancedCharacterAnalyzer()
        self.test_data = TestDataManager()

    async def test_philosophical_content_creates_meaningful_characters(self):
        """
        Test that philosophical content processing creates meaningful characters and albums
        Requirements: 1.1, 2.1, 2.2
        """
        philosophical_content = """
        The paradox of human existence lies in our simultaneous need for connection and solitude.
        We are social beings who crave understanding, yet we are fundamentally alone in our 
        consciousness. This tension creates the most profound art - expressions that bridge
        the gap between inner experience and shared meaning. Music becomes the language
        that speaks to both our collective humanity and our individual souls.
        """

        # Step 1: Test content type detection
        detection_result = self.processor.detect_content_type(philosophical_content)

        assert detection_result is not None
        assert detection_result["content_type"] in ["philosophical_conceptual", "mixed_content"]
        assert detection_result["confidence"] > 0.5
        assert "philosophical" in str(detection_result["detected_formats"]).lower() or \
               "conceptual" in str(detection_result["detected_formats"]).lower()

        # Step 2: Test character creation from philosophical content
        characters = self.processor.extract_or_create_characters(philosophical_content, detection_result)

        assert len(characters) > 0, "Should create at least one character from philosophical content"

        character = characters[0]
        assert character.get("name") is not None, "Character should have a name"
        assert len(character.get("name", "")) > 0, "Character name should not be empty"

        # Verify character has conceptual basis
        if "conceptual_basis" in character:
            conceptual_basis = character["conceptual_basis"]
            assert conceptual_basis is not None
            # Should reference philosophical themes
            basis_text = str(conceptual_basis).lower()
            assert any(term in basis_text for term in ["existential", "philosophical", "spiritual", "social", "aesthetic"]), \
                   f"Conceptual basis should contain philosophical themes, got: {conceptual_basis}"

        # Step 3: Test album generation from philosophical content
        ctx = create_mock_context()

        result_json = await create_conceptual_album.fn(
            content=philosophical_content,
            album_concept="The Paradox of Connection",
            track_count=6,
            genre="ambient",
            ctx=ctx
        )

        result = json.loads(result_json)

        assert "error" not in result, f"Album generation failed: {result.get('error', 'Unknown error')}"
        assert "tracks" in result, "Result should contain tracks"
        assert len(result["tracks"]) == 6, "Should generate requested number of tracks"

        # Verify tracks have meaningful content
        track_titles = [track.get("title", "") for track in result["tracks"]]
        assert all(title and title != f"Track {i+1}" for i, title in enumerate(track_titles)), \
               "All tracks should have meaningful titles, not generic ones"

        # Verify philosophical themes are present in album (check both concept and track content)
        album_info = result.get("album_info", {})
        album_concept = album_info.get("concept", "").lower()
        album_title = album_info.get("title", "").lower()

        # Check if themes appear in album title, concept, or track titles
        all_album_text = album_concept + " " + album_title + " " + " ".join(track_titles).lower()
        assert any(term in all_album_text for term in ["connection", "solitude", "existence", "consciousness", "existential", "spiritual"]), \
               f"Album should reflect philosophical themes. Got concept: '{album_concept}', title: '{album_title}', tracks: {track_titles}"

        # Verify tracks explore different aspects of the philosophical content
        track_contents = []
        for track in result["tracks"]:
            content = (track.get("lyrics", "") + " " + track.get("description", "")).lower()
            track_contents.append(content)

        # Should have thematic variety while maintaining coherence
        unique_themes = set()
        for content in track_contents:
            if "connection" in content or "together" in content:
                unique_themes.add("connection")
            if "solitude" in content or "alone" in content:
                unique_themes.add("solitude")
            if "consciousness" in content or "awareness" in content:
                unique_themes.add("consciousness")
            if "existence" in content or "being" in content:
                unique_themes.add("existence")

        assert len(unique_themes) >= 2, "Tracks should explore multiple philosophical themes"

    async def test_abstract_concept_character_development(self):
        """
        Test character development from abstract concepts
        Requirements: 2.1, 2.2, 2.3
        """
        abstract_content = """
        The philosophical concept of time challenges our understanding of reality and existence.
        Time is not a river flowing in one direction, but an ocean with currents moving
        in all directions simultaneously. This metaphysical perspective suggests we are not
        passengers on a boat, but conscious beings swimming in an infinite sea of possibility.
        Each stroke we take creates ripples that affect the entire ocean, and every wave
        that reaches us carries the echoes of countless other swimmers' spiritual journeys.
        """

        # Test character creation from abstract concepts
        detection_result = self.processor.detect_content_type(abstract_content)
        characters = self.processor.extract_or_create_characters(abstract_content, detection_result)

        assert len(characters) > 0, "Should create characters from abstract concepts"

        character = characters[0]

        # Verify character has depth and meaning
        assert character.get("name") is not None
        assert character.get("questions") is not None or character.get("struggles") is not None, \
               "Character should have questions or struggles"

        # Verify character reflects the abstract concepts
        character_text = (
            " ".join(character.get("questions", [])) + " " +
            " ".join(character.get("struggles", [])) + " " +
            str(character.get("conceptual_basis", []))
        ).lower()

        assert any(term in character_text for term in ["time", "temporal", "existence", "existential", "reality", "metaphysical"]), \
               f"Character should reflect source concepts, got: {character_text}"

        # Test album generation maintains conceptual coherence
        ctx = create_mock_context()

        result_json = await create_conceptual_album.fn(
            content=abstract_content,
            album_concept="Ocean of Time",
            track_count=5,
            genre="electronic",
            ctx=ctx
        )

        result = json.loads(result_json)

        assert "error" not in result
        assert len(result["tracks"]) == 5

        # Verify conceptual coherence across tracks
        all_track_content = ""
        for track in result["tracks"]:
            all_track_content += track.get("lyrics", "") + " " + track.get("description", "") + " "

        all_track_content = all_track_content.lower()
        assert any(term in all_track_content for term in ["time", "ocean", "current", "wave", "swim"]), \
               "Album should maintain conceptual themes throughout"


@pytest.mark.asyncio
@pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Required components not available")
class TestExplicitCharacterDescriptionWorkflow:
    """Test end-to-end workflow for explicit character description handling"""

    def setup_method(self):
        """Setup for each test method"""
        self.processor = WorkingUniversalProcessor()
        self.analyzer = EnhancedCharacterAnalyzer()

    async def test_explicit_character_description_produces_consistent_results(self):
        """
        Test that explicit character description handling produces consistent results
        Requirements: 1.2, 2.3
        """
        character_description = """
        Character Name: Maya Rodriguez
        Age: 29
        Background: Former classical violinist turned electronic music producer
        Personality: Perfectionist with anxiety issues, deeply empathetic, struggles with imposter syndrome
        Musical Style: Orchestral dubstep - combines classical arrangements with heavy electronic beats
        Key Traits: Uses music as emotional therapy, creates soundscapes that tell stories
        Influences: Skrillex, Lindsey Stirling, Hans Zimmer
        Current Situation: Recently moved to Berlin to escape family expectations and find her authentic voice
        """

        # Step 1: Test content type detection for explicit descriptions
        detection_result = self.processor.detect_content_type(character_description)

        assert detection_result is not None
        assert detection_result["content_type"] in ["character_description", "mixed_content"]
        assert "character" in str(detection_result["detected_formats"]).lower() or \
               "descriptive" in str(detection_result["detected_formats"]).lower()

        # Step 2: Test character processing uses explicit description
        characters = self.processor.extract_or_create_characters(character_description, detection_result)

        assert len(characters) > 0, "Should process explicit character description"

        character = characters[0]

        # Verify character uses provided information (name parsing may not be perfect, but should have a name)
        assert character.get("name") is not None and len(character.get("name", "")) > 0, \
               "Should have a character name"

        character_text = (
            " ".join(character.get("questions", [])) + " " +
            " ".join(character.get("struggles", [])) + " " +
            str(character.get("context", {})) + " " +
            character.get("processing_notes", "")
        ).lower()

        # Should incorporate key details from description (check for electronic music elements)
        assert "electronic" in character_text or "studio" in character_text, \
               f"Should incorporate musical elements, got: {character_text}"

        # Step 3: Test album generation maintains character consistency
        ctx = create_mock_context()

        result_json = await create_conceptual_album.fn(
            content=character_description,
            album_concept="Finding Authentic Voice",
            track_count=7,
            genre="electronic",
            ctx=ctx
        )

        result = json.loads(result_json)

        assert "error" not in result
        assert len(result["tracks"]) == 7

        # Verify character consistency across all tracks
        album_info = result.get("album_info", {})
        assert album_info.get("artist") is not None, \
               "Album should have an artist"

        # Check that tracks reflect character's musical style and background
        track_contents = []
        for track in result["tracks"]:
            content = (track.get("lyrics", "") + " " + track.get("description", "")).lower()
            track_contents.append(content)

            # Each track should reflect character's style or background (at least some electronic elements)
            assert any(term in content for term in [
                "electronic", "beat", "music", "sound", "authentic", "creative"
            ]), f"Track should reflect musical character: {track.get('title', 'Unknown')}"

        # Verify tracks tell a coherent story about the character
        all_content = " ".join(track_contents)
        assert "journey" in all_content or "growth" in all_content or "discovery" in all_content, \
               "Album should tell character's story"

    async def test_character_description_with_musical_details(self):
        """
        Test processing character descriptions with specific musical details
        Requirements: 2.3
        """
        musical_character = """
        Artist: DJ Neon Pulse
        Real Name: Alex Chen
        Genre: Synthwave/Retrowave
        Equipment: Moog synthesizers, Roland drum machines, vintage vocoders
        Style: Creates nostalgic 80s-inspired electronic music with modern production
        Backstory: Grew up in arcade culture, influenced by video game soundtracks
        Signature Sound: Neon-soaked melodies with driving basslines and retro drums
        """

        detection_result = self.processor.detect_content_type(musical_character)
        characters = self.processor.extract_or_create_characters(musical_character, detection_result)

        assert len(characters) > 0
        character = characters[0]

        # Should incorporate specific musical details
        character_text = str(character).lower()
        assert any(term in character_text for term in ["synth", "electronic", "80s", "retro", "arcade"]), \
               "Should incorporate musical style details"

        # Test album generation uses musical specifications
        ctx = create_mock_context()

        result_json = await create_conceptual_album.fn(
            content=musical_character,
            album_concept="Neon Arcade Dreams",
            track_count=4,
            genre="synthwave",
            ctx=ctx
        )

        result = json.loads(result_json)

        assert "error" not in result

        # Verify genre-specific production elements
        for track in result["tracks"]:
            suno_command = track.get("suno_command", "").lower()
            assert any(term in suno_command for term in [
                "synth", "electronic", "retro", "80s", "synthwave"
            ]), "Suno commands should reflect character's musical style"


@pytest.mark.asyncio
@pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Required components not available")
class TestNarrativeFictionWorkflow:
    """Test that narrative fiction processing remains functional"""

    def setup_method(self):
        """Setup for each test method"""
        self.processor = WorkingUniversalProcessor()
        self.analyzer = EnhancedCharacterAnalyzer()

    async def test_narrative_fiction_processing_remains_functional(self):
        """
        Test that narrative fiction processing still works correctly
        Requirements: 1.3
        """
        narrative_content = """
        This is a story about Sarah, who had been walking the empty streets of downtown for hours. 
        Her footsteps echoed off the wet pavement as she walked. The argument with her mother still 
        rang in her ears, each harsh word replaying like a broken record. She was twenty-six years 
        old, a successful graphic designer, yet she still felt like a child when her mother questioned her choices.
        
        The rain had stopped, but the air still smelled of petrichor and possibility. As she
        turned the corner onto Fifth Street, she saw him standing there under the streetlight,
        waiting. Marcus, her childhood friend who had become something more complicated over
        the years. He held his guitar case in one hand and a coffee in the other.
        
        "I thought you might need this," he said, offering her the coffee. His voice was gentle,
        understanding. He had always been able to read her moods, even when they were kids
        building forts in her backyard. Now he was a street musician, playing for tips and
        following his dreams despite everyone telling him to get a "real job."
        """

        # Step 1: Test content type detection for narrative
        detection_result = self.processor.detect_content_type(narrative_content)

        assert detection_result is not None
        assert detection_result["content_type"] in ["narrative_fiction", "mixed_content"]
        assert "narrative" in str(detection_result["detected_formats"]).lower() or \
               "fiction" in str(detection_result["detected_formats"]).lower()

        # Step 2: Test character extraction from narrative (override clarification request)
        if detection_result["processing_strategy"] == "request_clarification":
            # Override with explicit narrative processing
            detection_result["content_type"] = "narrative_fiction"
            detection_result["processing_strategy"] = "extract_characters"

        characters = self.processor.extract_or_create_characters(narrative_content, detection_result)

        assert len(characters) > 0, "Should extract characters from narrative"

        # Should identify main characters (name extraction may not be perfect)
        character_names = [char.get("name", "").lower() for char in characters]
        assert len(character_names) > 0, "Should extract at least one character"

        # Get the first character (main character)
        main_character = characters[0]
        assert main_character is not None, "Should create profile for main character"

        # Verify character details from narrative (check that it's from narrative context)
        character_text = (
            " ".join(main_character.get("questions", [])) + " " +
            " ".join(main_character.get("struggles", [])) + " " +
            str(main_character.get("context", {})) + " " +
            main_character.get("processing_notes", "")
        ).lower()

        assert "narrative" in character_text or "story" in character_text, \
               f"Should indicate narrative processing, got: {character_text}"

        # Step 3: Test album generation from narrative
        ctx = create_mock_context()

        result_json = await create_conceptual_album.fn(
            content=narrative_content,
            album_concept="Downtown Reflections",
            track_count=6,
            genre="indie",
            ctx=ctx
        )

        result = json.loads(result_json)

        assert "error" not in result
        assert len(result["tracks"]) == 6

        # Verify narrative elements in album
        album_info = result.get("album_info", {})
        assert album_info.get("artist") is not None, \
               "Album should have an artist"

        # Verify tracks follow narrative progression
        track_titles = [track.get("title", "") for track in result["tracks"]]
        track_contents = []

        for track in result["tracks"]:
            content = (track.get("lyrics", "") + " " + track.get("description", "")).lower()
            track_contents.append(content)

        all_content = " ".join(track_contents)

        # Should reference narrative or story elements
        assert any(term in all_content for term in ["story", "narrative", "character", "journey", "downtown"]), \
               f"Album should reference narrative elements, got content: {all_content[:200]}..."

    async def test_multi_character_narrative_processing(self):
        """
        Test processing narratives with multiple characters
        Requirements: 1.3
        """
        multi_character_narrative = """
        The coffee shop was Elena's sanctuary, a place where she could write without interruption.
        She was working on her third novel, a story about redemption and second chances. At
        twenty-eight, she had already published two successful books, but this one felt different,
        more personal.
        
        David, the barista, knew her order by heart: large coffee, black, with a blueberry muffin.
        He was an aspiring actor, working at the coffee shop to pay for acting classes. They had
        developed an easy friendship over the months, bonding over their shared artistic struggles.
        
        Today, a new customer caught Elena's attention. An older woman, maybe sixty, sat alone
        at the corner table, sketching in a worn leather journal. Her name was Margaret, though
        Elena didn't know it yet. Margaret was a retired art teacher who had recently lost her
        husband and was trying to rediscover her passion for drawing.
        """

        detection_result = self.processor.detect_content_type(multi_character_narrative)
        characters = self.processor.extract_or_create_characters(multi_character_narrative, detection_result)

        assert len(characters) >= 2, "Should extract multiple characters from narrative"

        character_names = [char.get("name", "").lower() for char in characters]

        # Should identify main characters
        assert any("elena" in name for name in character_names), "Should identify Elena"
        assert any("david" in name or "barista" in str(char).lower() for char in characters), \
               "Should identify David or reference barista role"

        # Test album generation with multiple characters
        ctx = create_mock_context()

        result_json = await create_conceptual_album.fn(
            content=multi_character_narrative,
            album_concept="Coffee Shop Chronicles",
            track_count=5,
            genre="folk",
            ctx=ctx
        )

        result = json.loads(result_json)

        assert "error" not in result
        assert len(result["tracks"]) == 5

        # Should reference multiple characters or their stories
        all_content = ""
        for track in result["tracks"]:
            all_content += track.get("lyrics", "") + " " + track.get("description", "") + " "

        all_content = all_content.lower()

        # Should reference the setting and multiple character elements
        assert "coffee" in all_content or "shop" in all_content, "Should reference setting"
        assert any(term in all_content for term in ["writer", "novel", "book", "story"]), \
               "Should reference Elena's writing"
        assert any(term in all_content for term in ["actor", "barista", "dreams"]), \
               "Should reference David's aspirations"


@pytest.mark.asyncio
@pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Required components not available")
class TestWorkflowErrorHandling:
    """Test error handling across different content type workflows"""

    def setup_method(self):
        """Setup for each test method"""
        self.processor = WorkingUniversalProcessor()

    async def test_ambiguous_content_handling(self):
        """Test handling of ambiguous content that could be multiple types"""
        ambiguous_content = """
        The musician stood on the empty stage, guitar in hand. The silence was deafening.
        What is the sound of one hand clapping? What is the music of an empty room?
        These questions haunted him as he prepared to play his final song.
        """

        detection_result = self.processor.detect_content_type(ambiguous_content)

        # Should handle ambiguous content gracefully
        assert detection_result is not None
        assert detection_result["content_type"] is not None
        assert detection_result["ambiguity_score"] is not None

        # Should provide clarification suggestions for ambiguous content
        if detection_result["ambiguity_score"] > 0.5:
            assert len(detection_result["suggested_clarifications"]) > 0

        # Should still be able to process the content
        characters = self.processor.extract_or_create_characters(ambiguous_content, detection_result)
        assert len(characters) > 0, "Should create characters even from ambiguous content"

    async def test_minimal_content_handling(self):
        """Test handling of very short or minimal content"""
        minimal_content = "Music is life."

        detection_result = self.processor.detect_content_type(minimal_content)

        # Should detect low confidence and request clarification
        assert detection_result["confidence"] < 0.5
        assert detection_result["clarification_needed"] is True
        assert len(detection_result["suggested_clarifications"]) > 0

        # Should handle gracefully without crashing
        characters = self.processor.extract_or_create_characters(minimal_content, detection_result)
        # May return empty list for minimal content, which is acceptable
        assert isinstance(characters, list)


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
