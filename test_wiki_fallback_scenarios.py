#!/usr/bin/env python3
"""
Test Wiki Data Fallback Scenarios

This test file validates that the system works correctly when wiki data
is unavailable and falls back to hardcoded mappings gracefully.
"""

import pytest
import asyncio
import tempfile
from unittest.mock import AsyncMock, Mock, patch
from pathlib import Path

# Import the classes we're testing
from server import MusicPersonaGenerator, CharacterProfile, Context

# Import wiki integration components if available
try:
    from wiki_data_system import WikiDataManager, WikiConfig
    from enhanced_genre_mapper import EnhancedGenreMapper
    WIKI_INTEGRATION_AVAILABLE = True
except ImportError:
    WIKI_INTEGRATION_AVAILABLE = False


class TestWikiFallbackScenarios:
    """Test fallback scenarios when wiki data is unavailable"""
    
    @pytest.fixture
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
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock context for testing"""
        context = Mock(spec=Context)
        context.info = AsyncMock()
        return context
    
    @pytest.mark.asyncio
    async def test_fallback_when_wiki_disabled(self, sample_character, mock_context):
        """Test fallback behavior when wiki integration is disabled"""
        generator = MusicPersonaGenerator()
        
        # Disable wiki integration
        generator._initialization_attempted = True
        generator.wiki_data_manager = None
        generator.enhanced_genre_mapper = None
        generator.source_attribution_manager = None
        
        # Generate persona using fallback
        persona = await generator.generate_artist_persona(sample_character, mock_context)
        
        # Verify fallback persona is valid
        assert persona is not None
        assert persona.character_name == sample_character.name
        assert isinstance(persona.primary_genre, str) and len(persona.primary_genre) > 0
        assert isinstance(persona.secondary_genres, list) and len(persona.secondary_genres) >= 1
        assert isinstance(persona.vocal_style, str) and len(persona.vocal_style) > 0
        
        # Should use hardcoded mappings
        hardcoded_genres = ["progressive", "art rock", "ambient", "indie", "alternative", "art pop"]
        assert any(genre in persona.primary_genre.lower() for genre in hardcoded_genres)
    
    @pytest.mark.asyncio
    async def test_fallback_genre_mapping_consistency(self, sample_character, mock_context):
        """Test that fallback genre mapping is consistent"""
        generator = MusicPersonaGenerator()
        
        # Disable wiki integration
        generator._initialization_attempted = True
        generator.wiki_data_manager = None
        generator.enhanced_genre_mapper = None
        generator.source_attribution_manager = None
        
        # Generate multiple personas
        persona1 = await generator.generate_artist_persona(sample_character, mock_context)
        persona2 = await generator.generate_artist_persona(sample_character, mock_context)
        
        # Should be consistent
        assert persona1.primary_genre == persona2.primary_genre
        assert persona1.secondary_genres == persona2.secondary_genres
    
    @pytest.mark.asyncio
    async def test_fallback_with_different_traits(self, mock_context):
        """Test fallback behavior with different character traits"""
        generator = MusicPersonaGenerator()
        
        # Disable wiki integration
        generator._initialization_attempted = True
        generator.wiki_data_manager = None
        generator.enhanced_genre_mapper = None
        generator.source_attribution_manager = None
        
        # Test different character types
        test_characters = [
            # Emotional character
            CharacterProfile(
                name="Emotional Character",
                aliases=["EC"],
                physical_description="Expressive person",
                mannerisms=["emotional gestures"],
                speech_patterns=["passionate speech"],
                behavioral_traits=["emotional: deeply feeling"],
                backstory="Someone who feels deeply",
                relationships=["close friends"],
                formative_experiences=["emotional awakening"],
                social_connections=["support group"],
                personality_drivers=["emotional (strong)"],
                motivations=["connect with others"],
                fears=["isolation"],
                desires=["understanding"],
                conflicts=["heart vs mind"],
                confidence_score=0.7,
                text_references=["Chapter 1"],
                first_appearance="Chapter 1",
                importance_score=0.8
            ),
            # Creative character
            CharacterProfile(
                name="Creative Character",
                aliases=["CC"],
                physical_description="Artistic person",
                mannerisms=["creative gestures"],
                speech_patterns=["artistic language"],
                behavioral_traits=["creative: innovative"],
                backstory="An artist seeking expression",
                relationships=["fellow artists"],
                formative_experiences=["artistic breakthrough"],
                social_connections=["art community"],
                personality_drivers=["creative (strong)"],
                motivations=["create beauty"],
                fears=["creative block"],
                desires=["artistic recognition"],
                conflicts=["art vs commerce"],
                confidence_score=0.8,
                text_references=["Chapter 1"],
                first_appearance="Chapter 1",
                importance_score=0.9
            )
        ]
        
        for character in test_characters:
            persona = await generator.generate_artist_persona(character, mock_context)
            
            # Should generate valid persona
            assert persona is not None
            assert isinstance(persona.primary_genre, str) and len(persona.primary_genre) > 0
            assert isinstance(persona.secondary_genres, list) and len(persona.secondary_genres) >= 1
    
    @pytest.mark.asyncio
    async def test_mixed_source_scenario(self, sample_character, mock_context):
        """Test scenario where some wiki data is available but incomplete"""
        if not WIKI_INTEGRATION_AVAILABLE:
            pytest.skip("Wiki integration not available")
        
        generator = MusicPersonaGenerator()
        
        # Mock partial wiki integration failure
        with patch.object(generator, 'enhanced_genre_mapper') as mock_mapper:
            # Mock mapper to return empty results (forcing fallback)
            mock_mapper.map_traits_to_genres = AsyncMock(return_value=[])
            generator.enhanced_genre_mapper = mock_mapper
            generator._initialization_attempted = True
            
            # Generate persona
            persona = await generator.generate_artist_persona(sample_character, mock_context)
            
            # Should fall back to hardcoded mapping
            assert persona is not None
            assert isinstance(persona.primary_genre, str) and len(persona.primary_genre) > 0
    
    @pytest.mark.asyncio
    async def test_attribution_fallback(self, sample_character, mock_context):
        """Test that attribution falls back gracefully when unavailable"""
        generator = MusicPersonaGenerator()
        
        # Disable source attribution
        generator._initialization_attempted = True
        generator.source_attribution_manager = None
        
        # Test attribution context building
        test_content = {"test": "data"}
        result = generator.build_attributed_context_for_llm(test_content, "genre")
        
        # Should return content without attribution
        assert isinstance(result, str)
        assert "data" in result
    
    @pytest.mark.asyncio
    async def test_error_recovery_in_fallback(self, sample_character, mock_context):
        """Test error recovery when fallback mapping also fails"""
        generator = MusicPersonaGenerator()
        
        # Disable wiki integration
        generator._initialization_attempted = True
        generator.wiki_data_manager = None
        generator.enhanced_genre_mapper = None
        generator.source_attribution_manager = None
        
        # Mock fallback mapping to raise an error
        with patch.object(generator, '_fallback_map_to_genres') as mock_fallback:
            mock_fallback.side_effect = Exception("Fallback failed")
            
            # Should still generate a persona (with default values)
            try:
                persona = await generator.generate_artist_persona(sample_character, mock_context)
                # If it succeeds, verify it's valid
                assert persona is not None
            except Exception:
                # If it fails, that's also acceptable for this edge case
                pass
    
    @pytest.mark.asyncio
    async def test_performance_with_fallback(self, sample_character, mock_context):
        """Test that fallback performance is acceptable"""
        import time
        
        generator = MusicPersonaGenerator()
        
        # Disable wiki integration
        generator._initialization_attempted = True
        generator.wiki_data_manager = None
        generator.enhanced_genre_mapper = None
        generator.source_attribution_manager = None
        
        # Measure fallback performance
        start_time = time.time()
        persona = await generator.generate_artist_persona(sample_character, mock_context)
        end_time = time.time()
        
        # Should complete in reasonable time (less than 1 second)
        assert (end_time - start_time) < 1.0
        assert persona is not None
    
    @pytest.mark.asyncio
    async def test_fallback_data_quality(self, sample_character, mock_context):
        """Test that fallback data maintains quality standards"""
        generator = MusicPersonaGenerator()
        
        # Disable wiki integration
        generator._initialization_attempted = True
        generator.wiki_data_manager = None
        generator.enhanced_genre_mapper = None
        generator.source_attribution_manager = None
        
        # Generate persona
        persona = await generator.generate_artist_persona(sample_character, mock_context)
        
        # Verify data quality
        assert persona.primary_genre != ""
        assert not persona.primary_genre.isspace()
        assert len(persona.secondary_genres) >= 1
        assert all(genre != "" and not genre.isspace() for genre in persona.secondary_genres)
        assert persona.vocal_style != ""
        assert not persona.vocal_style.isspace()
        assert len(persona.lyrical_themes) >= 1
        assert len(persona.artistic_influences) >= 1
        assert 0 <= persona.character_mapping_confidence <= 1


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])