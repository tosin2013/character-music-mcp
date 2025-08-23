#!/usr/bin/env python3
"""
Test the new artist description feature
Integrated with unified testing framework
"""

import asyncio
import sys
import os
from dataclasses import dataclass
from typing import Dict, List, Any

# Add paths for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests'))

from tests.fixtures.test_data import TestDataManager, test_data_manager
from tests.fixtures.mock_contexts import MockContext, create_mock_context

# Test data structures
@dataclass
class CharacterProfile:
    name: str
    backstory: str
    conflicts: List[str]
    fears: List[str]

@dataclass
class ArtistStory:
    introspective_themes: List[str]
    artistic_manifesto: str
    emotional_arc: str
    artistic_evolution: str

# Test the artist description logic
class TestArtistDescription:
    def _extract_origin_setting(self, character) -> str:
        backstory = character.backstory.lower()
        if "rooftop" in backstory or "city" in backstory:
            return "the urban landscape"
        elif "studio" in backstory or "apartment" in backstory:
            return "intimate creative spaces"
        elif "family" in backstory or "mother" in backstory:
            return "complex family dynamics"
        else:
            return "personal crossroads"
    
    def _extract_core_struggle(self, character, story) -> str:
        if character.conflicts:
            primary_conflict = character.conflicts[0]
            if "vs" in primary_conflict:
                parts = primary_conflict.split(" vs ")
                return f"the tension between {parts[0]} and {parts[1]}"
            else:
                return f"the weight of {primary_conflict}"
        elif character.fears:
            return f"the fear of {character.fears[0]}"
        else:
            return "internal battles"
    
    def _create_style_description(self, persona) -> str:
        vocal_style = persona.get("vocal_style", "")
        if "vulnerable" in vocal_style.lower():
            return "a vulnerable storyteller who crafts intimate confessions"
        elif "ethereal" in vocal_style.lower():
            return "an ethereal presence weaving atmospheric narratives"
        else:
            return "an authentic artist refusing to conform"
    
    def _extract_transformation(self, story) -> str:
        manifesto = story.artistic_manifesto.lower()
        evolution = story.artistic_evolution.lower()
        
        if "truth" in manifesto and "lies" in manifesto:
            return "raw truth over polished perfection"
        elif "facade" in evolution and "authentic" in evolution:
            return "authentic self-expression"
        else:
            return "honest emotional exploration"
    
    def _describe_emotional_impact(self, story) -> str:
        themes = story.introspective_themes
        arc = story.emotional_arc.lower()
        
        if any("confronting" in theme for theme in themes):
            return "confront listeners with uncomfortable truths"
        elif any("searching" in theme for theme in themes):
            return "guide others through their own searching"
        elif "isolation" in arc and "acceptance" in arc:
            return "transform isolation into shared understanding"
        else:
            return "invite deep introspection and healing"
    
    def create_artist_description(self, character, persona, story) -> str:
        # Extract key elements
        artist_name = persona.get("artist_name", character.name)
        origin_location = self._extract_origin_setting(character)
        core_struggle = self._extract_core_struggle(character, story)
        musical_style = self._create_style_description(persona)
        transformation = self._extract_transformation(story)
        
        # Create compelling narrative sentence
        description = (
            f"{artist_name} emerges from {origin_location} as {musical_style}, "
            f"channeling {core_struggle} into {transformation} through "
            f"{persona.get('primary_genre', 'indie')} soundscapes that "
            f"{self._describe_emotional_impact(story)}."
        )
        
        return description

async def test_artist_descriptions():
    print("🎨 Testing Artist Description Generation (Unified Framework)")
    print("=" * 60)
    
    # Test data
    test_cases = [
        {
            "name": "Sarah Chen - Urban Perfectionist",
            "character": CharacterProfile(
                name="Sarah Chen",
                backstory="rooftop confession, city lights, perfect daughter role, mother's expectations",
                conflicts=["perfection vs authenticity", "others' dreams vs own dreams"],
                fears=["disappointing others", "vulnerability"]
            ),
            "persona": {
                "artist_name": "Fragile Freedom",
                "primary_genre": "indie",
                "vocal_style": "vulnerable and raw emotional delivery",
                "collaboration_style": "intimate and selective"
            },
            "story": ArtistStory(
                introspective_themes=["confronting disappointing others", "searching for authentic self-expression"],
                artistic_manifesto="Music as a weapon against disappointing others, every note a declaration of authenticity. Raw truth over polished lies.",
                emotional_arc="From isolation through struggle to acceptance",
                artistic_evolution="From perfectionist facade observer to bold storyteller, driven by need for truth"
            )
        },
        {
            "name": "Marcus Rivera - Generational Trauma",
            "character": CharacterProfile(
                name="Marcus Rivera",
                backstory="father's abandonment, grandmother's wisdom, family traditions vs innovation",
                conflicts=["loyalty vs self-preservation", "tradition vs innovation"],
                fears=["abandonment", "losing himself in others' needs"]
            ),
            "persona": {
                "artist_name": "Echo Bloodlines",
                "primary_genre": "folk",
                "vocal_style": "powerful and storytelling",
                "collaboration_style": "community-focused"
            },
            "story": ArtistStory(
                introspective_themes=["confronting abandonment", "searching for unconditional acceptance"],
                artistic_manifesto="Music as healing for generational wounds, breaking cycles through understanding",
                emotional_arc="From inherited pain through confrontation to liberation",
                artistic_evolution="From wounded observer to healing storyteller"
            )
        },
        {
            "name": "Elena Rodriguez - Creative Self-Sabotage",
            "character": CharacterProfile(
                name="Elena Rodriguez",
                backstory="studio apartment, paintbrush trembling, art school struggles, gallery opening fears",
                conflicts=["success vs self-sabotage", "visibility vs hiding"],
                fears=["failure", "success", "judgment"]
            ),
            "persona": {
                "artist_name": "Hidden Canvas",
                "primary_genre": "electronic",
                "vocal_style": "ethereal and atmospheric",
                "collaboration_style": "experimental partnerships"
            },
            "story": ArtistStory(
                introspective_themes=["confronting fear of success", "searching for artistic courage"],
                artistic_manifesto="Art as courage, every creation a step toward visibility",
                emotional_arc="From hiding through exposure to artistic freedom",
                artistic_evolution="From hidden creator to bold artist"
            )
        }
    ]
    
    generator = TestArtistDescription()
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['name']}")
        print("-" * 40)
        
        description = generator.create_artist_description(
            case["character"],
            case["persona"], 
            case["story"]
        )
        
        print(f"Artist Description:")
        print(f"'{description}'")
        print()
        
        # Validate description elements
        assert case["persona"]["artist_name"] in description, "Should include artist name"
        assert case["persona"]["primary_genre"] in description, "Should include genre"
        
        # Check for story integration
        has_story_element = any(
            theme_word in description.lower() 
            for theme in case["story"].introspective_themes 
            for theme_word in theme.split()
        )
        
        print("✅ Description generated successfully")
        if has_story_element:
            print("✅ Story themes integrated")
        else:
            print("⚠️ Story integration could be stronger")
    
    print("\n" + "=" * 60)
    print("🎉 Artist Description Testing Complete!")
    print("\nExample Output Formats:")
    print("• Origin setting contextualizes the artist's background")
    print("• Core struggle shows what drives their music") 
    print("• Musical style describes their artistic approach")
    print("• Transformation reveals their artistic mission")
    print("• Emotional impact explains how they affect listeners")
    
    return True


# Test function for unified framework integration
async def test_artist_description_integration(ctx: MockContext, test_manager: TestDataManager) -> None:
    """Test function compatible with unified test runner"""
    # Use test data from unified framework
    scenario = test_manager.get_test_scenario("single_character_simple")
    expected_char = test_manager.get_expected_character("Sarah Chen")
    
    generator = TestArtistDescription()
    
    # Create test persona and story
    test_persona = {
        "artist_name": "Fragile Freedom",
        "primary_genre": "indie",
        "vocal_style": "vulnerable and raw emotional delivery"
    }
    
    test_story = ArtistStory(
        introspective_themes=["confronting disappointing others", "searching for authentic self-expression"],
        artistic_manifesto="Music as a weapon against disappointing others, every note a declaration of authenticity",
        emotional_arc="From isolation through struggle to acceptance",
        artistic_evolution="From perfectionist facade observer to bold storyteller"
    )
    
    # Test character profile conversion
    test_character = CharacterProfile(
        name=expected_char.name,
        backstory=expected_char.backstory,
        conflicts=expected_char.conflicts,
        fears=expected_char.fears
    )
    
    # Generate description
    description = generator.create_artist_description(test_character, test_persona, test_story)
    
    # Validate description
    assert len(description) > 50, "Description should be substantial"
    assert test_persona["artist_name"] in description, "Should include artist name"
    assert test_persona["primary_genre"] in description, "Should include genre"
    
    await ctx.info(f"Generated artist description: {description[:100]}...")


if __name__ == "__main__":
    asyncio.run(test_artist_descriptions())