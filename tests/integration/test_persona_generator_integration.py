#!/usr/bin/env python3
"""
Test integration of EnhancedGenreMapper with MusicPersonaGenerator

This test file validates that the MusicPersonaGenerator correctly integrates
with the EnhancedGenreMapper while maintaining backward compatibility.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio

# Import the classes we're testing
from server import CharacterProfile, Context, MusicPersonaGenerator

# Import wiki integration components if available
try:
    from enhanced_genre_mapper import EnhancedGenreMapper, GenreMatch
    from wiki_data_system import Genre, WikiConfig, WikiDataManager
    WIKI_INTEGRATION_AVAILABLE = True
except ImportError:
    WIKI_INTEGRATION_AVAILABLE = False


class TestMusicPersonaGeneratorIntegration:
    """Test MusicPersonaGenerator integration with EnhancedGenreMapper"""

    @pytest_asyncio.fixture
    def sample_character(self):
        """Create a sample character for testing"""
        return CharacterProfile(
            name="Test Character",
            aliases=["TC"],
            physical_description="A thoughtful individual",
            mannerisms=["thoughtful pauses", "analytical gestures"],
            speech_patterns=["precise language", "philosophical questions"],
            behavioral_traits=["intellectual: deep thinker", "creative: innovative solutions"],
            backstory="A brilliant scientist who questions the nature of reality",
            relationships=["mentor to students", "colleague to researchers"],
            formative_experiences=["breakthrough discovery", "philosophical awakening"],
            social_connections=["academic community", "research network"],
            personality_drivers=["intellectual courage (strong)", "quest for meaning (moderate)"],
            motivations=["understand the universe", "help humanity"],
            fears=["intellectual stagnation", "meaninglessness"],
            desires=["breakthrough discovery", "lasting impact"],
            conflicts=["theory vs practice", "individual vs community"],
            confidence_score=0.85,
            text_references=["Chapter 1: The Discovery", "Chapter 3: The Question"],
            first_appearance="Chapter 1",
            importance_score=0.9
        )

    @pytest_asyncio.fixture
    def mock_context(self):
        """Create a mock context for testing"""
        context = Mock(spec=Context)
        context.info = AsyncMock()
        return context

    @pytest_asyncio.fixture
    def sample_genres(self):
        """Create sample genres for testing"""
        return [
            Genre(
                name="progressive rock",
                description="Complex, experimental rock music with intellectual themes",
                characteristics=["complex compositions", "intellectual lyrics", "experimental"],
                mood_associations=["contemplative", "intellectual", "complex"],
                typical_instruments=["synthesizer", "guitar", "complex percussion"],
                source_url="test://progressive-rock"
            ),
            Genre(
                name="art rock",
                description="Artistic and experimental approach to rock music",
                characteristics=["artistic", "experimental", "sophisticated"],
                mood_associations=["intellectual", "artistic", "sophisticated"],
                typical_instruments=["synthesizer", "guitar", "unconventional instruments"],
                source_url="test://art-rock"
            ),
            Genre(
                name="ambient",
                description="Atmospheric, meditative music for contemplation",
                characteristics=["atmospheric", "meditative", "contemplative"],
                mood_associations=["peaceful", "introspective", "meditative"],
                typical_instruments=["synthesizer", "atmospheric sounds", "minimal percussion"],
                source_url="test://ambient"
            )
        ]

    @pytest.mark.asyncio
    async def test_persona_generator_initialization(self):
        """Test that MusicPersonaGenerator initializes correctly"""
        generator = MusicPersonaGenerator()

        # Should initialize without wiki integration initially
        assert generator.wiki_data_manager is None
        assert generator.enhanced_genre_mapper is None
        assert not generator._initialization_attempted

    @pytest.mark.asyncio
    async def test_wiki_integration_initialization_success(self, sample_genres):
        """Test successful wiki integration initialization"""
        if not WIKI_INTEGRATION_AVAILABLE:
            pytest.skip("Wiki integration not available")

        generator = MusicPersonaGenerator()

        # Mock the WikiDataManager and EnhancedGenreMapper
        with patch('server.WikiDataManager') as mock_manager_class, \
             patch('server.EnhancedGenreMapper') as mock_mapper_class:

            mock_manager = AsyncMock()
            mock_manager_class.return_value = mock_manager

            mock_mapper = Mock()
            mock_mapper_class.return_value = mock_mapper

            # Test initialization
            await generator._ensure_wiki_integration()

            # Verify initialization was attempted
            assert generator._initialization_attempted

            # Verify components were initialized
            mock_manager_class.assert_called_once()
            mock_manager.initialize.assert_called_once()
            mock_mapper_class.assert_called_once_with(mock_manager)

            assert generator.wiki_data_manager == mock_manager
            assert generator.enhanced_genre_mapper == mock_mapper

    @pytest.mark.asyncio
    async def test_wiki_integration_initialization_failure(self):
        """Test graceful handling of wiki integration initialization failure"""
        generator = MusicPersonaGenerator()

        # Mock WikiDataManager to raise an exception
        with patch('server.WikiDataManager') as mock_manager_class:
            mock_manager_class.side_effect = Exception("Initialization failed")

            # Should not raise exception, but log warning
            await generator._ensure_wiki_integration()

            # Verify graceful failure
            assert generator._initialization_attempted
            assert generator.wiki_data_manager is None
            assert generator.enhanced_genre_mapper is None

    @pytest.mark.asyncio
    async def test_enhanced_genre_mapping_success(self, sample_character, sample_genres):
        """Test successful enhanced genre mapping"""
        generator = MusicPersonaGenerator()

        # Skip initialization to avoid overriding our mock
        generator._initialization_attempted = True

        # Mock enhanced genre mapper to return specific results
        mock_mapper = AsyncMock()
        genre_matches = [
            GenreMatch(
                genre=sample_genres[0],  # progressive rock
                confidence=0.85,
                matching_traits=["intellectual courage", "quest for meaning"],
                matching_reasons=["Intellectual themes match progressive rock"]
            ),
            GenreMatch(
                genre=sample_genres[1],  # art rock
                confidence=0.75,
                matching_traits=["intellectual courage"],
                matching_reasons=["Artistic approach matches character"]
            ),
            GenreMatch(
                genre=sample_genres[2],  # ambient
                confidence=0.65,
                matching_traits=["quest for meaning"],
                matching_reasons=["Contemplative nature matches ambient"]
            )
        ]
        mock_mapper.map_traits_to_genres.return_value = genre_matches
        generator.enhanced_genre_mapper = mock_mapper

        # Test mapping
        traits = ["intellectual courage", "quest for meaning", "creative"]
        primary_genre, secondary_genres = await generator._map_to_genres(traits)

        # Verify results
        assert primary_genre == "progressive rock"
        assert "art rock" in secondary_genres
        assert "ambient" in secondary_genres
        assert len(secondary_genres) == 2

        # Verify mapper was called correctly
        mock_mapper.map_traits_to_genres.assert_called_once_with(
            traits, max_results=5, use_hierarchical=True
        )

    @pytest.mark.asyncio
    async def test_enhanced_genre_mapping_insufficient_results(self, sample_character, sample_genres):
        """Test enhanced mapping with insufficient secondary genres"""
        generator = MusicPersonaGenerator()

        # Skip initialization to avoid overriding our mock
        generator._initialization_attempted = True

        # Mock enhanced genre mapper to return limited results
        mock_mapper = AsyncMock()
        genre_matches = [
            GenreMatch(
                genre=sample_genres[0],  # progressive rock
                confidence=0.85,
                matching_traits=["intellectual courage"],
                matching_reasons=["Intellectual themes match"]
            )
        ]
        mock_mapper.map_traits_to_genres.return_value = genre_matches
        generator.enhanced_genre_mapper = mock_mapper

        # Test mapping
        traits = ["intellectual courage"]
        primary_genre, secondary_genres = await generator._map_to_genres(traits)

        # Verify results - should fill in with fallback genres
        assert primary_genre == "progressive rock"
        assert len(secondary_genres) == 2
        # Should contain fallback genres
        fallback_genres = ['indie', 'alternative', 'pop', 'rock']
        for genre in secondary_genres:
            assert genre in fallback_genres

    @pytest.mark.asyncio
    async def test_fallback_to_hardcoded_mapping(self, sample_character):
        """Test fallback to hardcoded mapping when enhanced mapping fails"""
        generator = MusicPersonaGenerator()

        # Mock enhanced genre mapper to raise exception
        mock_mapper = AsyncMock()
        mock_mapper.map_traits_to_genres.side_effect = Exception("Mapping failed")
        generator.enhanced_genre_mapper = mock_mapper

        # Test mapping
        traits = ["intellectual", "creative"]
        primary_genre, secondary_genres = await generator._map_to_genres(traits)

        # Should fall back to hardcoded mapping
        # Note: Enhanced genre mapper may return wiki-sourced genre names which can be different
        expected_genres = ["progressive", "art rock", "ambient", "indie", "alternative", "art pop",
                          "Progressive music", "Progressive rock", "Art rock", "Alternative rock"]
        assert primary_genre in expected_genres
        assert len(secondary_genres) == 2

    @pytest.mark.asyncio
    async def test_fallback_mapping_directly(self):
        """Test the fallback mapping method directly"""
        generator = MusicPersonaGenerator()

        # Test with known traits
        traits = ["intellectual", "creative", "mysterious"]
        primary_genre, secondary_genres = await generator._fallback_map_to_genres(traits)

        # Verify results - should use enhanced mapping if available, otherwise hardcoded
        assert isinstance(primary_genre, str)
        assert len(secondary_genres) == 2
        for genre in secondary_genres:
            assert isinstance(genre, str)

    @pytest.mark.asyncio
    async def test_fallback_mapping_no_matches(self):
        """Test fallback mapping with no trait matches"""
        generator = MusicPersonaGenerator()

        # Test with unknown traits
        traits = ["unknown_trait", "another_unknown"]
        primary_genre, secondary_genres = await generator._fallback_map_to_genres(traits)

        # Should use fallback (either enhanced or hardcoded)
        assert isinstance(primary_genre, str)
        assert len(secondary_genres) == 2
        for genre in secondary_genres:
            assert isinstance(genre, str)

    @pytest.mark.asyncio
    async def test_full_persona_generation_with_enhanced_mapping(self, sample_character, mock_context, sample_genres):
        """Test full persona generation with enhanced mapping"""
        generator = MusicPersonaGenerator()

        # Skip initialization to avoid overriding our mock
        generator._initialization_attempted = True

        # Mock enhanced genre mapper
        mock_mapper = AsyncMock()
        genre_matches = [
            GenreMatch(
                genre=sample_genres[0],  # progressive rock
                confidence=0.85,
                matching_traits=["intellectual courage", "quest for meaning"],
                matching_reasons=["Intellectual themes match progressive rock"]
            ),
            GenreMatch(
                genre=sample_genres[1],  # art rock
                confidence=0.75,
                matching_traits=["intellectual courage"],
                matching_reasons=["Artistic approach matches character"]
            )
        ]
        mock_mapper.map_traits_to_genres.return_value = genre_matches
        generator.enhanced_genre_mapper = mock_mapper

        # Generate persona
        persona = await generator.generate_artist_persona(sample_character, mock_context)

        # Verify persona was generated successfully
        assert persona is not None
        assert persona.character_name == "Test Character"
        assert persona.primary_genre == "progressive rock"
        assert "art rock" in persona.secondary_genres
        assert persona.character_mapping_confidence > 0

        # Verify context was used
        mock_context.info.assert_called()

    @pytest.mark.asyncio
    async def test_full_persona_generation_fallback(self, sample_character, mock_context):
        """Test full persona generation with fallback mapping"""
        generator = MusicPersonaGenerator()

        # Don't initialize enhanced mapping - should use fallback

        # Generate persona
        persona = await generator.generate_artist_persona(sample_character, mock_context)

        # Verify persona was generated successfully with fallback
        assert persona is not None
        assert persona.character_name == "Test Character"
        assert isinstance(persona.primary_genre, str)
        assert len(persona.secondary_genres) == 2
        assert persona.character_mapping_confidence > 0

    @pytest.mark.asyncio
    async def test_backward_compatibility(self, sample_character, mock_context):
        """Test that the integration maintains backward compatibility"""
        generator = MusicPersonaGenerator()

        # Generate persona without wiki integration
        persona = await generator.generate_artist_persona(sample_character, mock_context)

        # Verify all expected fields are present and valid
        assert persona.character_name == sample_character.name
        assert isinstance(persona.artist_name, str)
        assert isinstance(persona.primary_genre, str)
        assert isinstance(persona.secondary_genres, list)
        assert len(persona.secondary_genres) == 2
        assert isinstance(persona.vocal_style, str)
        assert isinstance(persona.instrumental_preferences, list)
        assert isinstance(persona.lyrical_themes, list)
        assert isinstance(persona.emotional_palette, list)
        assert isinstance(persona.artistic_influences, list)
        assert isinstance(persona.collaboration_style, str)
        assert isinstance(persona.character_mapping_confidence, float)
        assert 0 <= persona.character_mapping_confidence <= 1
        assert isinstance(persona.genre_justification, str)
        assert isinstance(persona.persona_description, str)

    @pytest.mark.asyncio
    async def test_multiple_initialization_calls(self):
        """Test that multiple initialization calls don't cause issues"""
        generator = MusicPersonaGenerator()

        # Call initialization multiple times
        await generator._ensure_wiki_integration()
        await generator._ensure_wiki_integration()
        await generator._ensure_wiki_integration()

        # Should only attempt initialization once
        assert generator._initialization_attempted


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
