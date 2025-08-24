#!/usr/bin/env python3
"""
Test Wiki Data Integration with Persona Generation

This test file validates that the persona generation system works correctly
with wiki data integration, focusing on compatibility and fallback behavior.
"""

import pytest
import asyncio
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


class TestWikiPersonaIntegration:
    """Test persona generation with wiki data integration"""
    
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
    async def test_persona_generation_with_wiki_integration(self, sample_character, mock_context):
        """Test that persona generation works with wiki integration enabled"""
        if not WIKI_INTEGRATION_AVAILABLE:
            pytest.skip("Wiki integration not available")
        
        generator = MusicPersonaGenerator()
        
        # Generate persona with wiki integration
        persona = await generator.generate_artist_persona(sample_character, mock_context)
        
        # Verify basic persona structure is maintained
        assert persona is not None
        assert persona.character_name == sample_character.name
        assert isinstance(persona.artist_name, str) and len(persona.artist_name) > 0
        assert isinstance(persona.primary_genre, str) and len(persona.primary_genre) > 0
        assert isinstance(persona.secondary_genres, list) and len(persona.secondary_genres) >= 1
        assert isinstance(persona.vocal_style, str) and len(persona.vocal_style) > 0
        assert isinstance(persona.lyrical_themes, list) and len(persona.lyrical_themes) > 0
        assert isinstance(persona.artistic_influences, list) and len(persona.artistic_influences) > 0
        assert isinstance(persona.character_mapping_confidence, float)
        assert 0 <= persona.character_mapping_confidence <= 1
    
    @pytest.mark.asyncio
    async def test_persona_generation_fallback_behavior(self, sample_character, mock_context):
        """Test that persona generation falls back gracefully when wiki integration fails"""
        generator = MusicPersonaGenerator()
        
        # Mock wiki integration to fail after initialization
        if WIKI_INTEGRATION_AVAILABLE:
            # Set the initialization flag to avoid the mock being called during _map_to_genres
            generator._initialization_attempted = True
            generator.enhanced_genre_mapper = None
            generator.wiki_data_manager = None
            generator.source_attribution_manager = None
            
            # Should still generate persona using fallback
            persona = await generator.generate_artist_persona(sample_character, mock_context)
            
            # Verify fallback persona is valid
            assert persona is not None
            assert persona.character_name == sample_character.name
            assert isinstance(persona.primary_genre, str) and len(persona.primary_genre) > 0
    
    @pytest.mark.asyncio
    async def test_genre_mapping_produces_valid_results(self, sample_character, mock_context):
        """Test that genre mapping produces valid results regardless of source"""
        generator = MusicPersonaGenerator()
        
        # Generate persona
        persona = await generator.generate_artist_persona(sample_character, mock_context)
        
        # Verify genre mapping produces reasonable results
        assert isinstance(persona.primary_genre, str)
        assert len(persona.primary_genre.strip()) > 0
        assert not persona.primary_genre.isspace()
        
        # Secondary genres should be different from primary
        for secondary_genre in persona.secondary_genres:
            assert isinstance(secondary_genre, str)
            assert len(secondary_genre.strip()) > 0
            assert secondary_genre != persona.primary_genre
    
    @pytest.mark.asyncio
    async def test_source_attribution_integration(self, sample_character, mock_context):
        """Test that source attribution works when available"""
        generator = MusicPersonaGenerator()
        
        # Generate persona
        persona = await generator.generate_artist_persona(sample_character, mock_context)
        
        # If source attribution is available, it should be working
        if hasattr(generator, 'source_attribution_manager') and generator.source_attribution_manager:
            # Test that attribution context can be built
            test_content = {"test": "data"}
            attributed_context = generator.build_attributed_context_for_llm(test_content, "genre")
            assert isinstance(attributed_context, str)
            assert len(attributed_context) > 0
    
    @pytest.mark.asyncio
    async def test_enhanced_genre_mapping_error_handling(self, sample_character, mock_context):
        """Test that enhanced genre mapping handles errors gracefully"""
        generator = MusicPersonaGenerator()
        
        if WIKI_INTEGRATION_AVAILABLE:
            # Mock enhanced genre mapper to raise an error
            with patch.object(generator, 'enhanced_genre_mapper') as mock_mapper:
                mock_mapper.map_traits_to_genres = AsyncMock(side_effect=Exception("Mapping failed"))
                
                # Should fall back to hardcoded mapping
                persona = await generator.generate_artist_persona(sample_character, mock_context)
                
                # Verify fallback worked
                assert persona is not None
                assert isinstance(persona.primary_genre, str)
                assert len(persona.primary_genre) > 0
    
    @pytest.mark.asyncio
    async def test_wiki_vs_fallback_consistency(self, sample_character, mock_context):
        """Test that wiki and fallback mappings produce consistent persona structure"""
        generator = MusicPersonaGenerator()
        
        # Generate persona with current configuration
        persona1 = await generator.generate_artist_persona(sample_character, mock_context)
        
        # Generate another persona (should be consistent in structure)
        persona2 = await generator.generate_artist_persona(sample_character, mock_context)
        
        # Structure should be consistent
        assert type(persona1.primary_genre) == type(persona2.primary_genre)
        assert type(persona1.secondary_genres) == type(persona2.secondary_genres)
        assert type(persona1.vocal_style) == type(persona2.vocal_style)
        assert type(persona1.lyrical_themes) == type(persona2.lyrical_themes)
        assert type(persona1.artistic_influences) == type(persona2.artistic_influences)
        
        # Both should have valid confidence scores
        assert 0 <= persona1.character_mapping_confidence <= 1
        assert 0 <= persona2.character_mapping_confidence <= 1
    
    @pytest.mark.asyncio
    async def test_trait_extraction_consistency(self, sample_character, mock_context):
        """Test that trait extraction works consistently with wiki integration"""
        generator = MusicPersonaGenerator()
        
        # Extract traits directly
        traits = generator._extract_primary_traits(sample_character)
        
        # Should extract meaningful traits
        assert isinstance(traits, list)
        assert len(traits) > 0
        assert all(isinstance(trait, str) for trait in traits)
        assert all(len(trait.strip()) > 0 for trait in traits)
        
        # Should not exceed expected limit
        assert len(traits) <= 3
    
    @pytest.mark.asyncio
    async def test_vocal_style_determination(self, sample_character, mock_context):
        """Test that vocal style determination works with wiki integration"""
        generator = MusicPersonaGenerator()
        
        # Generate persona
        persona = await generator.generate_artist_persona(sample_character, mock_context)
        
        # Vocal style should be meaningful
        assert isinstance(persona.vocal_style, str)
        assert len(persona.vocal_style.strip()) > 0
        assert not persona.vocal_style.isspace()
        
        # Should contain meaningful descriptive words (not just conjunctions)
        meaningful_words = [word for word in persona.vocal_style.split() 
                           if word.lower() not in ["and", "or", "with", "but", "yet", "so", "the", "a", "an"]]
        assert len(meaningful_words) >= 2, f"Vocal style should have meaningful descriptive content: {persona.vocal_style}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])