#!/usr/bin/env python3
"""
Unit Tests for Persona Generation Components

Tests artist persona creation logic, personality trait to genre mapping accuracy,
vocal style determination, and instrumental preference selection.
"""

import asyncio
import sys
import os
from typing import Dict, List, Any, Optional
import pytest

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server import CharacterProfile, ArtistPersona
# Use the actual MusicPersonaGenerator from server
from server import MusicPersonaGenerator as PersonaGenerator
from tests.fixtures.test_data import TestDataManager, test_data_manager
from tests.fixtures.mock_contexts import MockContext, create_mock_context


class TestPersonaCreation:
    """Test basic artist persona creation from character profiles"""
    
    async def test_persona_from_simple_character(self, ctx: MockContext, data_manager: TestDataManager):
        """Test persona generation from simple character profile"""
        expected_char = data_manager.get_expected_character("Sarah Chen")
        generator = PersonaGenerator()
        
        await ctx.info("Testing persona generation from simple character")
        
        # Generate persona
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Validate basic persona structure
        assert persona.artist_name is not None and len(persona.artist_name.strip()) > 0, \
            "Should generate artist name"
        assert persona.primary_genre is not None and len(persona.primary_genre.strip()) > 0, \
            "Should determine primary genre"
        assert len(persona.personality_traits) > 0, "Should extract personality traits"
        assert len(persona.artistic_influences) > 0, "Should identify artistic influences"
        
        # Persona should reflect character's core traits
        assert any(trait in persona.personality_traits for trait in ["perfectionist", "authentic", "introspective"]), \
            "Persona should reflect character's core personality traits"
        
        await ctx.info(f"Generated persona for {persona.artist_name} in {persona.primary_genre}")
    
    async def test_persona_from_complex_character(self, ctx: MockContext, data_manager: TestDataManager):
        """Test persona generation from complex character with rich psychology"""
        expected_char = data_manager.get_expected_character("The Philosopher")
        generator = PersonaGenerator()
        
        await ctx.info("Testing persona generation from complex character")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Complex character should generate rich persona
        assert len(persona.personality_traits) >= 5, "Complex character should have rich personality traits"
        assert len(persona.artistic_influences) >= 3, "Should identify multiple artistic influences"
        assert len(persona.lyrical_themes) >= 4, "Should extract multiple lyrical themes"
        
        # Should reflect philosophical nature
        philosophical_indicators = ["intellectual", "contemplative", "existential", "meaning", "purpose"]
        assert any(indicator in str(persona.personality_traits).lower() for indicator in philosophical_indicators), \
            "Should reflect philosophical character traits"
        
        # Genre should match character complexity
        complex_genres = ["progressive rock", "ambient", "post-rock", "experimental", "art rock"]
        assert any(genre in persona.primary_genre.lower() for genre in complex_genres), \
            "Complex character should map to sophisticated genres"
        
        await ctx.info(f"Complex persona generated: {len(persona.personality_traits)} traits, {persona.primary_genre}")
    
    async def test_persona_consistency(self, ctx: MockContext, data_manager: TestDataManager):
        """Test that persona generation is consistent for same character"""
        expected_char = data_manager.get_expected_character("Marcus")
        generator = PersonaGenerator()
        
        await ctx.info("Testing persona generation consistency")
        
        # Generate persona multiple times
        persona1 = await generator.generate_artist_persona(expected_char, ctx)
        persona2 = await generator.generate_artist_persona(expected_char, ctx)
        
        # Core elements should be consistent
        assert persona1.primary_genre == persona2.primary_genre, \
            "Primary genre should be consistent across generations"
        
        # Personality traits should have significant overlap
        common_traits = set(persona1.personality_traits) & set(persona2.personality_traits)
        assert len(common_traits) >= len(persona1.personality_traits) * 0.7, \
            "Should have consistent personality trait extraction"
        
        await ctx.info("Persona generation consistency validated")


class TestPersonalityTraitMapping:
    """Test mapping of character personality traits to musical elements"""
    
    async def test_emotional_trait_mapping(self, ctx: MockContext, data_manager: TestDataManager):
        """Test mapping of emotional traits to musical characteristics"""
        expected_char = data_manager.get_expected_character("Marcus")  # Grief-focused character
        generator = PersonaGenerator()
        
        await ctx.info("Testing emotional trait mapping")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Emotional traits should influence musical choices
        emotional_genres = ["blues", "soul", "gospel", "folk", "country"]
        assert any(genre in persona.primary_genre.lower() for genre in emotional_genres), \
            f"Emotional character should map to emotional genres, got {persona.primary_genre}"
        
        # Lyrical themes should reflect emotional content
        emotional_themes = ["loss", "grief", "love", "memory", "healing", "hope"]
        assert any(theme in str(persona.lyrical_themes).lower() for theme in emotional_themes), \
            "Lyrical themes should reflect emotional character traits"
        
        # Vocal style should match emotional intensity
        emotional_vocal_styles = ["soulful", "raw", "emotional", "powerful", "heartfelt"]
        assert any(style in persona.vocal_style.lower() for style in emotional_vocal_styles), \
            f"Vocal style should reflect emotional traits, got {persona.vocal_style}"
        
        await ctx.info("Emotional trait mapping validated")
    
    async def test_intellectual_trait_mapping(self, ctx: MockContext, data_manager: TestDataManager):
        """Test mapping of intellectual traits to musical characteristics"""
        expected_char = data_manager.get_expected_character("The Philosopher")
        generator = PersonaGenerator()
        
        await ctx.info("Testing intellectual trait mapping")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Intellectual traits should influence genre selection
        intellectual_genres = ["progressive", "art rock", "ambient", "experimental", "post-rock"]
        assert any(genre in persona.primary_genre.lower() for genre in intellectual_genres), \
            f"Intellectual character should map to complex genres, got {persona.primary_genre}"
        
        # Should have sophisticated lyrical themes
        intellectual_themes = ["philosophy", "existence", "meaning", "consciousness", "reality", "truth"]
        assert any(theme in str(persona.lyrical_themes).lower() for theme in intellectual_themes), \
            "Should have intellectually sophisticated lyrical themes"
        
        # Artistic influences should include thoughtful artists
        thoughtful_influences = ["radiohead", "pink floyd", "tool", "king crimson", "yes", "genesis"]
        persona_influences_lower = [inf.lower() for inf in persona.artistic_influences]
        assert any(influence in " ".join(persona_influences_lower) for influence in thoughtful_influences), \
            "Should reference intellectually sophisticated artists"
        
        await ctx.info("Intellectual trait mapping validated")
    
    async def test_creative_trait_mapping(self, ctx: MockContext, data_manager: TestDataManager):
        """Test mapping of creative traits to musical characteristics"""
        expected_char = data_manager.get_expected_character("Elena Rodriguez")  # Artist character
        generator = PersonaGenerator()
        
        await ctx.info("Testing creative trait mapping")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Creative traits should influence genre and style
        creative_genres = ["indie", "alternative", "art pop", "experimental", "singer-songwriter"]
        assert any(genre in persona.primary_genre.lower() for genre in creative_genres), \
            f"Creative character should map to artistic genres, got {persona.primary_genre}"
        
        # Should emphasize artistic expression
        creative_themes = ["art", "creativity", "expression", "authenticity", "vision", "inspiration"]
        assert any(theme in str(persona.lyrical_themes).lower() for theme in creative_themes), \
            "Should have creativity-focused lyrical themes"
        
        # Instrumental preferences should allow for artistic expression
        expressive_instruments = ["guitar", "piano", "synthesizer", "strings", "unconventional"]
        assert any(instrument in str(persona.instrumental_preferences).lower() for instrument in expressive_instruments), \
            "Should prefer expressive instruments"
        
        await ctx.info("Creative trait mapping validated")
    
    async def test_adventurous_trait_mapping(self, ctx: MockContext, data_manager: TestDataManager):
        """Test mapping of adventurous traits to musical characteristics"""
        expected_char = data_manager.get_expected_character("Captain Zara Okafor")  # Sci-fi adventure character
        generator = PersonaGenerator()
        
        await ctx.info("Testing adventurous trait mapping")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Adventurous traits should influence genre selection
        adventurous_genres = ["electronic", "synthwave", "space rock", "progressive", "cinematic"]
        assert any(genre in persona.primary_genre.lower() for genre in adventurous_genres), \
            f"Adventurous character should map to dynamic genres, got {persona.primary_genre}"
        
        # Themes should reflect adventure and exploration
        adventure_themes = ["exploration", "journey", "discovery", "courage", "unknown", "frontier"]
        assert any(theme in str(persona.lyrical_themes).lower() for theme in adventure_themes), \
            "Should have adventure-focused lyrical themes"
        
        # Should have dynamic vocal style
        dynamic_vocal_styles = ["powerful", "commanding", "confident", "soaring", "epic"]
        assert any(style in persona.vocal_style.lower() for style in dynamic_vocal_styles), \
            f"Should have dynamic vocal style, got {persona.vocal_style}"
        
        await ctx.info("Adventurous trait mapping validated")


class TestGenreMapping:
    """Test accuracy of personality trait to genre mapping"""
    
    async def test_genre_mapping_accuracy(self, ctx: MockContext, data_manager: TestDataManager):
        """Test that genre mapping accurately reflects character traits"""
        generator = PersonaGenerator()
        
        await ctx.info("Testing genre mapping accuracy")
        
        # Test multiple character types
        test_cases = [
            ("Sarah Chen", ["indie", "alternative", "singer-songwriter"]),
            ("Marcus", ["blues", "soul", "gospel", "folk"]),
            ("The Philosopher", ["progressive", "ambient", "post-rock", "art rock"]),
            ("Captain Zara Okafor", ["electronic", "synthwave", "space rock"]),
            ("Maya Patel", ["indie pop", "folk", "singer-songwriter"])
        ]
        
        for char_name, expected_genres in test_cases:
            expected_char = data_manager.get_expected_character(char_name)
            persona = await generator.generate_artist_persona(expected_char, ctx)
            
            # Should map to one of the expected genres
            genre_match = any(expected_genre in persona.primary_genre.lower() 
                            for expected_genre in expected_genres)
            assert genre_match, \
                f"{char_name} should map to {expected_genres}, got {persona.primary_genre}"
        
        await ctx.info("Genre mapping accuracy validated")
    
    async def test_genre_consistency_with_traits(self, ctx: MockContext, data_manager: TestDataManager):
        """Test that selected genres are consistent with character traits"""
        expected_char = data_manager.get_expected_character("Detective Riley Santos")  # Urban fantasy
        generator = PersonaGenerator()
        
        await ctx.info("Testing genre consistency with traits")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Genre should match character's dark, mysterious nature
        dark_genres = ["dark electronic", "industrial", "gothic", "alternative", "dark ambient"]
        assert any(genre in persona.primary_genre.lower() for genre in dark_genres), \
            f"Dark character should map to dark genres, got {persona.primary_genre}"
        
        # Secondary genres should be complementary
        if hasattr(persona, 'secondary_genres') and persona.secondary_genres:
            complementary_genres = ["electronic", "ambient", "experimental", "cinematic"]
            assert any(genre in str(persona.secondary_genres).lower() for genre in complementary_genres), \
                "Secondary genres should complement primary genre"
        
        await ctx.info("Genre consistency validated")
    
    async def test_cross_genre_influences(self, ctx: MockContext, data_manager: TestDataManager):
        """Test handling of characters that could span multiple genres"""
        expected_char = data_manager.get_expected_character("Amelia Hartwell")  # Historical mathematician
        generator = PersonaGenerator()
        
        await ctx.info("Testing cross-genre influences")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Should handle the blend of historical and intellectual elements
        possible_genres = ["classical", "orchestral", "chamber", "neoclassical", "art pop", "progressive"]
        assert any(genre in persona.primary_genre.lower() for genre in possible_genres), \
            f"Historical intellectual should map to sophisticated genres, got {persona.primary_genre}"
        
        # Should reflect both historical and mathematical aspects
        historical_themes = ["history", "period", "classical", "tradition"]
        mathematical_themes = ["precision", "logic", "patterns", "structure"]
        
        themes_text = str(persona.lyrical_themes).lower()
        has_historical = any(theme in themes_text for theme in historical_themes)
        has_mathematical = any(theme in themes_text for theme in mathematical_themes)
        
        assert has_historical or has_mathematical, \
            "Should reflect either historical or mathematical aspects in themes"
        
        await ctx.info("Cross-genre influences validated")


class TestVocalStyleDetermination:
    """Test vocal style determination based on character traits"""
    
    async def test_emotional_vocal_styles(self, ctx: MockContext, data_manager: TestDataManager):
        """Test vocal style determination for emotional characters"""
        expected_char = data_manager.get_expected_character("Marcus")  # Grief-focused
        generator = PersonaGenerator()
        
        await ctx.info("Testing emotional vocal styles")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Emotional character should have emotionally expressive vocal style
        emotional_descriptors = ["soulful", "raw", "emotional", "powerful", "heartfelt", "vulnerable", "passionate"]
        assert any(descriptor in persona.vocal_style.lower() for descriptor in emotional_descriptors), \
            f"Emotional character should have expressive vocal style, got {persona.vocal_style}"
        
        # Should not have overly technical or cold descriptions
        technical_descriptors = ["technical", "precise", "mechanical", "cold", "detached"]
        assert not any(descriptor in persona.vocal_style.lower() for descriptor in technical_descriptors), \
            "Emotional character should not have technical vocal style"
        
        await ctx.info(f"Emotional vocal style validated: {persona.vocal_style}")
    
    async def test_intellectual_vocal_styles(self, ctx: MockContext, data_manager: TestDataManager):
        """Test vocal style determination for intellectual characters"""
        expected_char = data_manager.get_expected_character("The Philosopher")
        generator = PersonaGenerator()
        
        await ctx.info("Testing intellectual vocal styles")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Intellectual character should have thoughtful vocal style
        intellectual_descriptors = ["contemplative", "thoughtful", "measured", "articulate", "profound", "reflective"]
        assert any(descriptor in persona.vocal_style.lower() for descriptor in intellectual_descriptors), \
            f"Intellectual character should have thoughtful vocal style, got {persona.vocal_style}"
        
        # May include spoken word elements
        spoken_elements = ["spoken", "narrative", "storytelling", "conversational"]
        has_spoken_elements = any(element in persona.vocal_style.lower() for element in spoken_elements)
        
        # Either thoughtful singing or spoken elements should be present
        assert has_spoken_elements or any(desc in persona.vocal_style.lower() for desc in intellectual_descriptors), \
            "Intellectual character should have either thoughtful or spoken vocal elements"
        
        await ctx.info(f"Intellectual vocal style validated: {persona.vocal_style}")
    
    async def test_confident_vocal_styles(self, ctx: MockContext, data_manager: TestDataManager):
        """Test vocal style determination for confident characters"""
        expected_char = data_manager.get_expected_character("Captain Zara Okafor")  # Leadership character
        generator = PersonaGenerator()
        
        await ctx.info("Testing confident vocal styles")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Confident character should have strong vocal style
        confident_descriptors = ["powerful", "commanding", "strong", "confident", "authoritative", "bold", "soaring"]
        assert any(descriptor in persona.vocal_style.lower() for descriptor in confident_descriptors), \
            f"Confident character should have strong vocal style, got {persona.vocal_style}"
        
        # Should not be described as weak or hesitant
        weak_descriptors = ["weak", "hesitant", "timid", "uncertain", "fragile"]
        assert not any(descriptor in persona.vocal_style.lower() for descriptor in weak_descriptors), \
            "Confident character should not have weak vocal descriptors"
        
        await ctx.info(f"Confident vocal style validated: {persona.vocal_style}")
    
    async def test_vulnerable_vocal_styles(self, ctx: MockContext, data_manager: TestDataManager):
        """Test vocal style determination for vulnerable characters"""
        expected_char = data_manager.get_expected_character("Elena Rodriguez")  # Fearful artist
        generator = PersonaGenerator()
        
        await ctx.info("Testing vulnerable vocal styles")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Vulnerable character should have intimate vocal style
        vulnerable_descriptors = ["intimate", "vulnerable", "delicate", "tender", "soft", "whispered", "fragile", "honest"]
        assert any(descriptor in persona.vocal_style.lower() for descriptor in vulnerable_descriptors), \
            f"Vulnerable character should have intimate vocal style, got {persona.vocal_style}"
        
        # Should emphasize emotional authenticity
        authentic_descriptors = ["authentic", "honest", "genuine", "real", "true"]
        assert any(descriptor in persona.vocal_style.lower() for descriptor in authentic_descriptors), \
            "Vulnerable character should emphasize vocal authenticity"
        
        await ctx.info(f"Vulnerable vocal style validated: {persona.vocal_style}")


class TestInstrumentalPreferences:
    """Test instrumental preference selection based on character traits"""
    
    async def test_emotional_instrumental_preferences(self, ctx: MockContext, data_manager: TestDataManager):
        """Test instrumental preferences for emotional characters"""
        expected_char = data_manager.get_expected_character("Marcus")  # Grief-focused
        generator = PersonaGenerator()
        
        await ctx.info("Testing emotional instrumental preferences")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Emotional character should prefer expressive instruments
        emotional_instruments = ["piano", "guitar", "strings", "organ", "harmonica", "saxophone", "violin"]
        assert any(instrument in str(persona.instrumental_preferences).lower() for instrument in emotional_instruments), \
            f"Emotional character should prefer expressive instruments, got {persona.instrumental_preferences}"
        
        # Should avoid overly electronic or mechanical instruments as primary
        mechanical_instruments = ["drum machine", "synthesizer", "sampler", "sequencer"]
        primary_instruments = persona.instrumental_preferences[:2] if len(persona.instrumental_preferences) >= 2 else persona.instrumental_preferences
        
        mechanical_count = sum(1 for instrument in primary_instruments 
                             if any(mech in instrument.lower() for mech in mechanical_instruments))
        assert mechanical_count <= 1, "Emotional character should not be primarily mechanical instruments"
        
        await ctx.info(f"Emotional instrumental preferences validated: {persona.instrumental_preferences[:3]}")
    
    async def test_electronic_instrumental_preferences(self, ctx: MockContext, data_manager: TestDataManager):
        """Test instrumental preferences for electronic/futuristic characters"""
        expected_char = data_manager.get_expected_character("Captain Zara Okafor")  # Sci-fi character
        generator = PersonaGenerator()
        
        await ctx.info("Testing electronic instrumental preferences")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Sci-fi character should prefer electronic instruments
        electronic_instruments = ["synthesizer", "electronic", "digital", "sampler", "drum machine", "sequencer"]
        assert any(instrument in str(persona.instrumental_preferences).lower() for instrument in electronic_instruments), \
            f"Sci-fi character should prefer electronic instruments, got {persona.instrumental_preferences}"
        
        # May also include cinematic elements
        cinematic_instruments = ["orchestral", "strings", "brass", "cinematic", "ambient"]
        has_cinematic = any(instrument in str(persona.instrumental_preferences).lower() for instrument in cinematic_instruments)
        
        # Should have either electronic or cinematic elements (or both)
        has_electronic = any(instrument in str(persona.instrumental_preferences).lower() for instrument in electronic_instruments)
        assert has_electronic or has_cinematic, "Sci-fi character should have electronic or cinematic elements"
        
        await ctx.info(f"Electronic instrumental preferences validated: {persona.instrumental_preferences[:3]}")
    
    async def test_traditional_instrumental_preferences(self, ctx: MockContext, data_manager: TestDataManager):
        """Test instrumental preferences for traditional/historical characters"""
        expected_char = data_manager.get_expected_character("Amelia Hartwell")  # Victorian mathematician
        generator = PersonaGenerator()
        
        await ctx.info("Testing traditional instrumental preferences")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Historical character should prefer classical instruments
        classical_instruments = ["piano", "violin", "cello", "harpsichord", "chamber", "orchestral", "strings", "woodwinds"]
        assert any(instrument in str(persona.instrumental_preferences).lower() for instrument in classical_instruments), \
            f"Historical character should prefer classical instruments, got {persona.instrumental_preferences}"
        
        # Should avoid modern electronic instruments as primary choices
        modern_instruments = ["synthesizer", "electric guitar", "drum machine", "sampler"]
        primary_instruments = persona.instrumental_preferences[:2] if len(persona.instrumental_preferences) >= 2 else persona.instrumental_preferences
        
        modern_count = sum(1 for instrument in primary_instruments 
                          if any(modern in instrument.lower() for modern in modern_instruments))
        assert modern_count == 0, "Historical character should not primarily use modern instruments"
        
        await ctx.info(f"Traditional instrumental preferences validated: {persona.instrumental_preferences[:3]}")
    
    async def test_versatile_instrumental_preferences(self, ctx: MockContext, data_manager: TestDataManager):
        """Test instrumental preferences for versatile/creative characters"""
        expected_char = data_manager.get_expected_character("Elena Rodriguez")  # Artist character
        generator = PersonaGenerator()
        
        await ctx.info("Testing versatile instrumental preferences")
        
        persona = await generator.generate_artist_persona(expected_char, ctx)
        
        # Creative character should have diverse instrumental preferences
        assert len(persona.instrumental_preferences) >= 3, \
            "Creative character should have diverse instrumental preferences"
        
        # Should include both traditional and modern elements
        traditional_instruments = ["guitar", "piano", "violin", "drums"]
        modern_instruments = ["synthesizer", "electronic", "sampler", "effects"]
        
        has_traditional = any(instrument in str(persona.instrumental_preferences).lower() for instrument in traditional_instruments)
        has_modern = any(instrument in str(persona.instrumental_preferences).lower() for instrument in modern_instruments)
        
        # Should have variety (either traditional + modern, or multiple traditional, etc.)
        instrument_variety = len(set(persona.instrumental_preferences))
        assert instrument_variety >= 3 or (has_traditional and has_modern), \
            "Creative character should have instrumental variety"
        
        await ctx.info(f"Versatile instrumental preferences validated: {persona.instrumental_preferences}")


# Test runner integration
async def run_persona_generation_tests():
    """Run all persona generation tests"""
    print("🎭 Running Persona Generation Unit Tests")
    print("=" * 50)
    
    ctx = create_mock_context("basic", session_id="persona_generation_tests")
    data_manager = test_data_manager
    
    test_classes = [
        TestPersonaCreation(),
        TestPersonalityTraitMapping(),
        TestGenreMapping(),
        TestVocalStyleDetermination(),
        TestInstrumentalPreferences()
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n📋 {class_name}")
        print("-" * 30)
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) 
                       if method.startswith('test_') and callable(getattr(test_class, method))]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                test_method = getattr(test_class, method_name)
                await test_method(ctx, data_manager)
                print(f"  ✅ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  ❌ {method_name}: {str(e)}")
    
    print(f"\n🎯 Persona Generation Tests Complete")
    print(f"   Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = asyncio.run(run_persona_generation_tests())
    sys.exit(0 if success else 1)