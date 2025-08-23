#!/usr/bin/env python3
"""
Unit Tests for Suno Command Generation Components

Tests command creation and optimization, different command formats (simple, custom, bracket notation),
meta tag strategy validation, and effectiveness scoring.
"""

import asyncio
import sys
import os
import json
from typing import Dict, List, Any, Optional
import pytest

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server import CharacterProfile, ArtistPersona, SunoCommand, SunoCommandGenerator
from enhanced_suno_generator import EnhancedSunoCommandGenerator, EnhancedSunoCommand
from tests.fixtures.test_data import TestDataManager, test_data_manager
from tests.fixtures.mock_contexts import MockContext, create_mock_context


class TestBasicCommandGeneration:
    """Test basic Suno command generation functionality"""
    
    async def test_simple_command_generation(self, ctx: MockContext, data_manager: TestDataManager):
        """Test generation of simple Suno commands"""
        expected_char = data_manager.get_expected_character("Sarah Chen")
        expected_persona = data_manager.get_expected_persona("Sarah Chen")
        generator = SunoCommandGenerator()
        
        await ctx.info("Testing simple command generation")
        
        # Generate simple command
        command = await generator.create_simple_command(
            character=expected_char,
            persona=expected_persona,
            track_title="Finding Myself",
            ctx=ctx
        )
        
        # Validate basic command structure
        assert command.title == "Finding Myself", "Should preserve track title"
        assert command.command_type == "simple", "Should be marked as simple command"
        assert len(command.formatted_command) > 0, "Should generate formatted command"
        
        # Should include basic elements
        assert expected_persona.primary_genre.lower() in command.formatted_command.lower(), \
            "Should include primary genre"
        assert any(trait in command.formatted_command.lower() for trait in expected_char.personality_drivers), \
            "Should reference character traits"
        
        await ctx.info(f"Simple command generated: {len(command.formatted_command)} characters")
    
    async def test_custom_command_generation(self, ctx: MockContext, data_manager: TestDataManager):
        """Test generation of custom Suno commands with detailed parameters"""
        expected_char = data_manager.get_expected_character("The Philosopher")
        expected_persona = data_manager.get_expected_persona("The Philosopher")
        generator = SunoCommandGenerator()
        
        await ctx.info("Testing custom command generation")
        
        # Generate custom command with specific parameters
        command = await generator.create_custom_command(
            character=expected_char,
            persona=expected_persona,
            track_title="Existential Questions",
            custom_params={
                "bpm": "120",
                "key": "D minor",
                "mood": "contemplative",
                "structure": "verse-chorus-bridge"
            },
            ctx=ctx
        )
        
        # Validate custom command structure
        assert command.command_type == "custom", "Should be marked as custom command"
        assert "120" in command.formatted_command, "Should include custom BPM"
        assert "D minor" in command.formatted_command, "Should include custom key"
        assert "contemplative" in command.formatted_command.lower(), "Should include custom mood"
        
        # Should be more detailed than simple command
        assert len(command.formatted_command) > 200, "Custom command should be detailed"
        
        await ctx.info(f"Custom command generated with {len(command.formatted_command)} characters")
    
    async def test_bracket_notation_command(self, ctx: MockContext, data_manager: TestDataManager):
        """Test generation of commands with proper bracket notation"""
        expected_char = data_manager.get_expected_character("Marcus")
        expected_persona = data_manager.get_expected_persona("Marcus")
        generator = SunoCommandGenerator()
        
        await ctx.info("Testing bracket notation command generation")
        
        command = await generator.create_bracket_notation_command(
            character=expected_char,
            persona=expected_persona,
            track_title="Memories of Love",
            ctx=ctx
        )
        
        # Validate bracket notation
        assert command.command_type == "bracket_notation", "Should be marked as bracket notation"
        
        # Should contain proper meta tags
        required_tags = ["[Intro]", "[Verse]", "[Chorus]", "[Outro]"]
        for tag in required_tags:
            assert tag in command.formatted_command, f"Should contain {tag} meta tag"
        
        # Should have structured sections
        sections = command.formatted_command.split('[')
        assert len(sections) >= 5, "Should have multiple structured sections"
        
        await ctx.info(f"Bracket notation command generated with {len(sections)} sections")


class TestCommandFormats:
    """Test different Suno command formats"""
    
    async def test_narrative_command_format(self, ctx: MockContext, data_manager: TestDataManager):
        """Test narrative-style command format with story integration"""
        enhanced_generator = EnhancedSunoCommandGenerator()
        
        await ctx.info("Testing narrative command format")
        
        # Create narrative command
        command = enhanced_generator.create_narrative_suno_command(
            main_story="A story of personal transformation through music",
            character_name="Sarah Chen",
            character_age=27,
            character_background="Young professional discovering her authentic self",
            track_title="Breaking Free",
            track_concept="Liberation from societal expectations",
            genre="indie"
        )
        
        # Validate narrative structure
        assert command.command_type == "narrative", "Should be narrative command type"
        assert len(command.main_story_context) > 0, "Should have main story context"
        assert len(command.character_story_context) > 0, "Should have character story context"
        assert len(command.song_story_context) > 0, "Should have song story context"
        
        # Should include all narrative layers
        assert "transformation" in command.main_story_context.lower(), "Should reference main story"
        assert "Sarah Chen" in command.character_story_context, "Should reference character"
        assert "Breaking Free" in command.song_story_context, "Should reference track"
        
        await ctx.info("Narrative command format validated")
    
    async def test_production_focused_format(self, ctx: MockContext, data_manager: TestDataManager):
        """Test production-focused command format with technical details"""
        expected_char = data_manager.get_expected_character("Captain Zara Okafor")
        expected_persona = data_manager.get_expected_persona("Captain Zara Okafor")
        generator = SunoCommandGenerator()
        
        await ctx.info("Testing production-focused format")
        
        command = await generator.create_production_command(
            character=expected_char,
            persona=expected_persona,
            track_title="Stellar Command",
            production_notes={
                "studio_type": "digital",
                "mixing_style": "cinematic",
                "effects": ["reverb", "delay", "compression"],
                "arrangement": "orchestral electronic"
            },
            ctx=ctx
        )
        
        # Should include production details
        assert "digital" in command.formatted_command.lower(), "Should reference studio type"
        assert "cinematic" in command.formatted_command.lower(), "Should reference mixing style"
        assert any(effect in command.formatted_command.lower() for effect in ["reverb", "delay"]), \
            "Should reference audio effects"
        
        # Should maintain character connection
        assert any(trait in command.formatted_command.lower() for trait in expected_char.personality_drivers), \
            "Should maintain character connection in production format"
        
        await ctx.info("Production-focused format validated")
    
    async def test_lyrical_focused_format(self, ctx: MockContext, data_manager: TestDataManager):
        """Test lyrical-focused command format emphasizing vocal content"""
        expected_char = data_manager.get_expected_character("Elena Rodriguez")
        expected_persona = data_manager.get_expected_persona("Elena Rodriguez")
        generator = SunoCommandGenerator()
        
        await ctx.info("Testing lyrical-focused format")
        
        command = await generator.create_lyrical_command(
            character=expected_char,
            persona=expected_persona,
            track_title="Canvas of Dreams",
            lyrical_themes=["artistic struggle", "creative authenticity", "fear of exposure"],
            ctx=ctx
        )
        
        # Should emphasize lyrical content
        assert "artistic" in command.formatted_command.lower(), "Should reference artistic themes"
        assert "creative" in command.formatted_command.lower(), "Should reference creativity"
        
        # Should include vocal direction
        vocal_directions = ["vocals", "singing", "voice", "delivery", "expression"]
        assert any(direction in command.formatted_command.lower() for direction in vocal_directions), \
            "Should include vocal direction"
        
        # Should reference character's emotional state
        assert any(emotion in command.formatted_command.lower() for emotion in ["fear", "vulnerable", "authentic"]), \
            "Should reference character's emotional state"
        
        await ctx.info("Lyrical-focused format validated")


class TestMetaTagStrategy:
    """Test meta tag strategy and implementation"""
    
    async def test_structural_meta_tags(self, ctx: MockContext, data_manager: TestDataManager):
        """Test proper use of structural meta tags"""
        expected_char = data_manager.get_expected_character("Sarah Chen")
        expected_persona = data_manager.get_expected_persona("Sarah Chen")
        generator = SunoCommandGenerator()
        
        await ctx.info("Testing structural meta tags")
        
        command = await generator.create_bracket_notation_command(
            character=expected_char,
            persona=expected_persona,
            track_title="Journey Home",
            ctx=ctx
        )
        
        # Should include standard structural tags
        structural_tags = ["[Intro]", "[Verse]", "[Chorus]", "[Bridge]", "[Outro]"]
        found_tags = [tag for tag in structural_tags if tag in command.formatted_command]
        
        assert len(found_tags) >= 4, f"Should include most structural tags, found {found_tags}"
        
        # Tags should be in logical order
        tag_positions = {tag: command.formatted_command.find(tag) for tag in found_tags}
        sorted_tags = sorted(tag_positions.items(), key=lambda x: x[1])
        
        # Intro should come before Outro
        if "[Intro]" in found_tags and "[Outro]" in found_tags:
            assert tag_positions["[Intro]"] < tag_positions["[Outro]"], \
                "Intro should come before Outro"
        
        await ctx.info(f"Structural meta tags validated: {found_tags}")
    
    async def test_emotional_meta_tags(self, ctx: MockContext, data_manager: TestDataManager):
        """Test use of emotional meta tags based on character"""
        expected_char = data_manager.get_expected_character("Marcus")  # Grief-focused character
        expected_persona = data_manager.get_expected_persona("Marcus")
        generator = SunoCommandGenerator()
        
        await ctx.info("Testing emotional meta tags")
        
        command = await generator.create_bracket_notation_command(
            character=expected_char,
            persona=expected_persona,
            track_title="In Memory",
            ctx=ctx
        )
        
        # Should include emotion-appropriate meta tags
        emotional_tags = ["[Emotional]", "[Heartfelt]", "[Soulful]", "[Powerful]", "[Raw]"]
        found_emotional_tags = [tag for tag in emotional_tags if tag in command.formatted_command]
        
        assert len(found_emotional_tags) >= 1, \
            f"Should include emotional meta tags for emotional character, found {found_emotional_tags}"
        
        # Should avoid inappropriate emotional tags
        inappropriate_tags = ["[Upbeat]", "[Happy]", "[Cheerful]", "[Playful]"]
        found_inappropriate = [tag for tag in inappropriate_tags if tag in command.formatted_command]
        
        assert len(found_inappropriate) == 0, \
            f"Should not include inappropriate emotional tags, found {found_inappropriate}"
        
        await ctx.info(f"Emotional meta tags validated: {found_emotional_tags}")
    
    async def test_instrumental_meta_tags(self, ctx: MockContext, data_manager: TestDataManager):
        """Test instrumental meta tags based on persona preferences"""
        expected_char = data_manager.get_expected_character("The Philosopher")
        expected_persona = data_manager.get_expected_persona("The Philosopher")
        generator = SunoCommandGenerator()
        
        await ctx.info("Testing instrumental meta tags")
        
        command = await generator.create_bracket_notation_command(
            character=expected_char,
            persona=expected_persona,
            track_title="Contemplation",
            ctx=ctx
        )
        
        # Should include instrument-specific tags based on persona
        if expected_persona.instrumental_preferences:
            primary_instrument = expected_persona.instrumental_preferences[0].lower()
            
            # Look for instrument-related tags
            instrument_tags = ["[Guitar Solo]", "[Piano]", "[Strings]", "[Synthesizer]", "[Orchestral]"]
            found_instrument_tags = [tag for tag in instrument_tags if tag.lower().replace('[', '').replace(']', '') in primary_instrument]
            
            # Should reference preferred instruments in some way
            instrument_mentioned = any(instrument.lower() in command.formatted_command.lower() 
                                     for instrument in expected_persona.instrumental_preferences[:2])
            
            assert instrument_mentioned, \
                f"Should reference preferred instruments {expected_persona.instrumental_preferences[:2]}"
        
        await ctx.info("Instrumental meta tags validated")
    
    async def test_genre_specific_meta_tags(self, ctx: MockContext, data_manager: TestDataManager):
        """Test genre-specific meta tag usage"""
        expected_char = data_manager.get_expected_character("Captain Zara Okafor")  # Electronic genre
        expected_persona = data_manager.get_expected_persona("Captain Zara Okafor")
        generator = SunoCommandGenerator()
        
        await ctx.info("Testing genre-specific meta tags")
        
        command = await generator.create_bracket_notation_command(
            character=expected_char,
            persona=expected_persona,
            track_title="Digital Horizon",
            ctx=ctx
        )
        
        # Should include genre-appropriate tags
        if "electronic" in expected_persona.primary_genre.lower():
            electronic_tags = ["[Synthesized]", "[Digital]", "[Electronic]", "[Ambient]", "[Build]", "[Drop]"]
            found_electronic_tags = [tag for tag in electronic_tags if tag in command.formatted_command]
            
            assert len(found_electronic_tags) >= 1, \
                f"Should include electronic-specific tags, found {found_electronic_tags}"
        
        # Should avoid genre-inappropriate tags
        if "electronic" in expected_persona.primary_genre.lower():
            acoustic_tags = ["[Acoustic Guitar]", "[Harmonica]", "[Banjo]", "[Folk]"]
            found_acoustic_tags = [tag for tag in acoustic_tags if tag in command.formatted_command]
            
            assert len(found_acoustic_tags) == 0, \
                f"Should not include acoustic tags for electronic genre, found {found_acoustic_tags}"
        
        await ctx.info("Genre-specific meta tags validated")


class TestEffectivenessScoring:
    """Test Suno command effectiveness scoring system"""
    
    async def test_narrative_coherence_scoring(self, ctx: MockContext, data_manager: TestDataManager):
        """Test narrative coherence scoring component"""
        enhanced_generator = EnhancedSunoCommandGenerator()
        
        await ctx.info("Testing narrative coherence scoring")
        
        # Create command with strong narrative coherence
        coherent_command = enhanced_generator.create_narrative_suno_command(
            main_story="A philosophical exploration of existence and meaning",
            character_name="Marcus Thompson",
            character_age=34,
            character_background="Philosophical liquid drum and bass producer exploring existential questions",
            track_title="Questions of Being",
            track_concept="Musical exploration of philosophical inquiry through electronic production",
            genre="liquid_dnb"
        )
        
        # Should have high narrative coherence
        assert coherent_command.narrative_coherence_score >= 0.7, \
            f"Coherent narrative should score highly, got {coherent_command.narrative_coherence_score}"
        
        # Create command with weak narrative coherence
        incoherent_command = enhanced_generator.create_narrative_suno_command(
            main_story="Random unrelated content",
            character_name="Bob",
            character_age=25,
            character_background="Generic person",
            track_title="Song",
            track_concept="Music",
            genre="pop"
        )
        
        # Should have lower narrative coherence
        assert incoherent_command.narrative_coherence_score < coherent_command.narrative_coherence_score, \
            "Incoherent narrative should score lower than coherent narrative"
        
        await ctx.info("Narrative coherence scoring validated")
    
    async def test_production_authenticity_scoring(self, ctx: MockContext, data_manager: TestDataManager):
        """Test production authenticity scoring component"""
        enhanced_generator = EnhancedSunoCommandGenerator()
        
        await ctx.info("Testing production authenticity scoring")
        
        # Create command with authentic production context
        authentic_command = enhanced_generator.create_narrative_suno_command(
            main_story="Professional music production story",
            character_name="Sarah Producer",
            character_age=35,
            character_background="Experienced music producer with 15 years in the industry, specializes in indie rock production",
            track_title="Studio Sessions",
            track_concept="Authentic studio production experience",
            genre="indie"
        )
        
        # Should have high production authenticity
        assert authentic_command.production_authenticity_score >= 0.7, \
            f"Authentic production should score highly, got {authentic_command.production_authenticity_score}"
        
        # Age and experience should contribute to score
        young_command = enhanced_generator.create_narrative_suno_command(
            main_story="Music story",
            character_name="Young Person",
            character_age=18,
            character_background="Just started making music",
            track_title="First Song",
            track_concept="Beginner music",
            genre="pop"
        )
        
        # Experienced producer should score higher than beginner
        assert authentic_command.production_authenticity_score > young_command.production_authenticity_score, \
            "Experienced producer should score higher than beginner"
        
        await ctx.info("Production authenticity scoring validated")
    
    async def test_suno_optimization_scoring(self, ctx: MockContext, data_manager: TestDataManager):
        """Test Suno AI optimization scoring component"""
        enhanced_generator = EnhancedSunoCommandGenerator()
        
        await ctx.info("Testing Suno optimization scoring")
        
        # Create well-optimized command
        optimized_command = enhanced_generator.create_narrative_suno_command(
            main_story="Well-structured musical narrative",
            character_name="Professional Artist",
            character_age=30,
            character_background="Professional musician with studio experience",
            track_title="Optimized Track",
            track_concept="Well-crafted musical composition",
            genre="electronic"
        )
        
        # Should have good Suno optimization
        assert optimized_command.suno_optimization_score >= 0.6, \
            f"Optimized command should score well, got {optimized_command.suno_optimization_score}"
        
        # Score should consider meta tags, BPM, and production details
        command_text = optimized_command.formatted_command
        
        # Check for optimization factors
        has_meta_tags = any(tag in command_text for tag in ["[Intro]", "[Verse]", "[Chorus]"])
        has_bpm = "BPM" in command_text or "bpm" in command_text
        has_production_details = any(detail in command_text.lower() for detail in ["studio", "production", "mixing"])
        
        optimization_factors = sum([has_meta_tags, has_bpm, has_production_details])
        assert optimization_factors >= 2, \
            f"Should include multiple optimization factors, found {optimization_factors}"
        
        await ctx.info("Suno optimization scoring validated")
    
    async def test_overall_effectiveness_calculation(self, ctx: MockContext, data_manager: TestDataManager):
        """Test overall effectiveness score calculation"""
        enhanced_generator = EnhancedSunoCommandGenerator()
        
        await ctx.info("Testing overall effectiveness calculation")
        
        command = enhanced_generator.create_narrative_suno_command(
            main_story="Comprehensive musical story with depth and meaning",
            character_name="Master Musician",
            character_age=40,
            character_background="Master musician and producer with decades of experience in multiple genres",
            track_title="Masterpiece",
            track_concept="Culmination of artistic vision and technical mastery",
            genre="progressive"
        )
        
        # Overall effectiveness should be average of component scores
        expected_overall = (
            command.narrative_coherence_score + 
            command.production_authenticity_score + 
            command.suno_optimization_score
        ) / 3
        
        assert abs(command.overall_effectiveness - expected_overall) < 0.01, \
            f"Overall effectiveness should be average of components, expected {expected_overall}, got {command.overall_effectiveness}"
        
        # All scores should be within valid range
        assert 0.0 <= command.narrative_coherence_score <= 1.0, "Narrative coherence should be 0-1"
        assert 0.0 <= command.production_authenticity_score <= 1.0, "Production authenticity should be 0-1"
        assert 0.0 <= command.suno_optimization_score <= 1.0, "Suno optimization should be 0-1"
        assert 0.0 <= command.overall_effectiveness <= 1.0, "Overall effectiveness should be 0-1"
        
        await ctx.info(f"Overall effectiveness validated: {command.overall_effectiveness:.3f}")


class TestCommandOptimization:
    """Test command optimization features"""
    
    async def test_length_optimization(self, ctx: MockContext, data_manager: TestDataManager):
        """Test command length optimization for Suno AI limits"""
        expected_char = data_manager.get_expected_character("The Philosopher")
        expected_persona = data_manager.get_expected_persona("The Philosopher")
        generator = SunoCommandGenerator()
        
        await ctx.info("Testing command length optimization")
        
        # Generate command and check length
        command = await generator.create_optimized_command(
            character=expected_char,
            persona=expected_persona,
            track_title="Philosophical Inquiry",
            max_length=2000,  # Typical Suno limit
            ctx=ctx
        )
        
        # Should respect length limits
        assert len(command.formatted_command) <= 2000, \
            f"Command should respect length limit, got {len(command.formatted_command)} characters"
        
        # Should still include essential elements
        assert command.title in command.formatted_command, "Should include track title"
        assert expected_persona.primary_genre.lower() in command.formatted_command.lower(), \
            "Should include genre information"
        
        # Should prioritize most important information
        essential_elements = [
            expected_char.name,
            expected_persona.primary_genre,
            command.title
        ]
        
        for element in essential_elements:
            assert element.lower() in command.formatted_command.lower(), \
                f"Should include essential element: {element}"
        
        await ctx.info(f"Length optimization validated: {len(command.formatted_command)} characters")
    
    async def test_clarity_optimization(self, ctx: MockContext, data_manager: TestDataManager):
        """Test command clarity optimization for better Suno AI understanding"""
        expected_char = data_manager.get_expected_character("Maya Patel")
        expected_persona = data_manager.get_expected_persona("Maya Patel")
        generator = SunoCommandGenerator()
        
        await ctx.info("Testing command clarity optimization")
        
        command = await generator.create_clear_command(
            character=expected_char,
            persona=expected_persona,
            track_title="Connection",
            ctx=ctx
        )
        
        # Should use clear, direct language
        unclear_phrases = ["perhaps", "maybe", "might be", "could be", "somewhat"]
        found_unclear = [phrase for phrase in unclear_phrases if phrase in command.formatted_command.lower()]
        
        assert len(found_unclear) <= 1, \
            f"Should minimize unclear language, found {found_unclear}"
        
        # Should have clear structure
        sentences = command.formatted_command.split('.')
        long_sentences = [s for s in sentences if len(s.strip()) > 150]
        
        assert len(long_sentences) <= 2, \
            f"Should avoid overly long sentences, found {len(long_sentences)}"
        
        # Should use specific rather than generic terms
        specific_terms = [expected_char.name, expected_persona.primary_genre, command.title]
        for term in specific_terms:
            assert term in command.formatted_command, \
                f"Should use specific term: {term}"
        
        await ctx.info("Command clarity optimization validated")
    
    async def test_genre_optimization(self, ctx: MockContext, data_manager: TestDataManager):
        """Test genre-specific command optimization"""
        expected_char = data_manager.get_expected_character("Captain Zara Okafor")
        expected_persona = data_manager.get_expected_persona("Captain Zara Okafor")
        generator = SunoCommandGenerator()
        
        await ctx.info("Testing genre-specific optimization")
        
        command = await generator.create_genre_optimized_command(
            character=expected_char,
            persona=expected_persona,
            track_title="Stellar Navigation",
            ctx=ctx
        )
        
        # Should optimize for the specific genre
        genre = expected_persona.primary_genre.lower()
        
        if "electronic" in genre:
            # Electronic music optimization
            electronic_terms = ["synthesizer", "digital", "electronic", "beats", "production"]
            found_electronic = [term for term in electronic_terms if term in command.formatted_command.lower()]
            assert len(found_electronic) >= 2, \
                f"Electronic genre should include electronic terms, found {found_electronic}"
        
        elif "rock" in genre:
            # Rock music optimization
            rock_terms = ["guitar", "drums", "bass", "power", "energy"]
            found_rock = [term for term in rock_terms if term in command.formatted_command.lower()]
            assert len(found_rock) >= 2, \
                f"Rock genre should include rock terms, found {found_rock}"
        
        # Should avoid genre-inappropriate terms
        if "electronic" in genre:
            acoustic_terms = ["acoustic guitar", "harmonica", "banjo", "folk"]
            found_acoustic = [term for term in acoustic_terms if term in command.formatted_command.lower()]
            assert len(found_acoustic) == 0, \
                f"Electronic genre should avoid acoustic terms, found {found_acoustic}"
        
        await ctx.info(f"Genre optimization validated for {genre}")


# Test runner integration
async def run_suno_command_tests():
    """Run all Suno command generation tests"""
    print("🎵 Running Suno Command Generation Unit Tests")
    print("=" * 50)
    
    ctx = create_mock_context("basic", session_id="suno_command_tests")
    data_manager = test_data_manager
    
    test_classes = [
        TestBasicCommandGeneration(),
        TestCommandFormats(),
        TestMetaTagStrategy(),
        TestEffectivenessScoring(),
        TestCommandOptimization()
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
    
    print(f"\n🎯 Suno Command Tests Complete")
    print(f"   Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = asyncio.run(run_suno_command_tests())
    sys.exit(0 if success else 1)