import pytest

#!/usr/bin/env python3
"""
Comprehensive test for the analyze_artist_psychology tool format fixes

This test verifies all the requirements for task 9:
- Update tool to accept correct CharacterProfile format without 'age' parameter errors
- Fix CharacterProfile object creation to use proper initialization parameters
- Add meaningful psychological analysis instead of format error responses
- Test psychology analysis with various character profiles
"""

import asyncio
import sys


# Mock the MCP context
class MockContext:
    def __init__(self):
        self.info_messages = []
        self.error_messages = []

    async def info(self, message):
        self.info_messages.append(message)
        print(f"INFO: {message}")

    async def error(self, message):
        self.error_messages.append(message)
        print(f"ERROR: {message}")

@pytest.mark.asyncio
async def test_comprehensive_format_fixes():
    """Test all aspects of the format fixes"""

    print("Testing comprehensive analyze_artist_psychology format fixes...")

    # Import the function logic
    from server import ArtistPersona, _analyze_artist_psychology_deep
    from standard_character_profile import StandardCharacterProfile

    # Create mock context
    ctx = MockContext()

    # Test Case 1: Character data with problematic 'age' parameter
    print("\n1. Testing 'age' parameter handling...")
    character_with_age = {
        "name": "Test Character",
        "age": 25,  # Should be ignored
        "backstory": "A musician with a story",
        "motivations": ["create music"],
        "fears": ["failure"],
        "confidence_score": 0.8
    }

    persona_minimal = {
        "character_name": "Test Character",
        "artist_name": "Test Artist",
        "primary_genre": "indie"
    }

    try:
        character = StandardCharacterProfile.from_dict(character_with_age)
        persona = ArtistPersona.from_dict(persona_minimal)
        analysis = await _analyze_artist_psychology_deep(character, persona, ctx)

        if not analysis or not isinstance(analysis, dict):
            print("❌ Failed to generate analysis with 'age' parameter")
            return False

        print("✅ Successfully handled 'age' parameter")
    except Exception as e:
        print(f"❌ Failed with 'age' parameter: {e}")
        return False

    # Test Case 2: Minimal character data
    print("\n2. Testing minimal character data...")
    minimal_character = {
        "name": "Minimal Character"
    }

    minimal_persona = {
        "character_name": "Minimal Character",
        "artist_name": "Minimal"
    }

    try:
        character = StandardCharacterProfile.from_dict(minimal_character)
        persona = ArtistPersona.from_dict(minimal_persona)
        analysis = await _analyze_artist_psychology_deep(character, persona, ctx)

        if not analysis or not isinstance(analysis, dict):
            print("❌ Failed to generate analysis with minimal data")
            return False

        print("✅ Successfully handled minimal character data")
    except Exception as e:
        print(f"❌ Failed with minimal data: {e}")
        return False

    # Test Case 3: Character data with extra unknown fields
    print("\n3. Testing unknown fields handling...")
    character_with_extras = {
        "name": "Extra Fields Character",
        "unknown_field": "should be ignored",
        "skin": "should be ignored",
        "random_data": {"nested": "data"},
        "backstory": "Character with extra fields",
        "motivations": ["test unknown field handling"],
        "confidence_score": 0.7
    }

    persona_with_extras = {
        "character_name": "Extra Fields Character",
        "artist_name": "Extra",
        "primary_genre": "test",
        "unknown_persona_field": "ignore me",
        "extra_data": [1, 2, 3]
    }

    try:
        character = StandardCharacterProfile.from_dict(character_with_extras)
        persona = ArtistPersona.from_dict(persona_with_extras)
        analysis = await _analyze_artist_psychology_deep(character, persona, ctx)

        if not analysis or not isinstance(analysis, dict):
            print("❌ Failed to generate analysis with extra fields")
            return False

        print("✅ Successfully handled unknown fields")
    except Exception as e:
        print(f"❌ Failed with extra fields: {e}")
        return False

    # Test Case 4: Verify meaningful analysis content
    print("\n4. Testing meaningful analysis generation...")
    rich_character = {
        "name": "Rich Character",
        "backstory": "Grew up in a musical family but faced tragedy",
        "motivations": ["honor family legacy", "heal through music"],
        "fears": ["not being good enough", "losing inspiration"],
        "desires": ["create lasting art", "connect with audiences"],
        "conflicts": ["perfectionism vs authenticity"],
        "personality_drivers": ["passion", "dedication"],
        "formative_experiences": ["first piano lesson", "family tragedy"],
        "confidence_score": 0.9
    }

    rich_persona = {
        "character_name": "Rich Character",
        "artist_name": "Rich",
        "primary_genre": "classical crossover",
        "vocal_style": "emotional and powerful",
        "lyrical_themes": ["family", "loss", "hope"],
        "genre_justification": "Classical crossover allows for emotional depth and technical skill"
    }

    try:
        character = StandardCharacterProfile.from_dict(rich_character)
        persona = ArtistPersona.from_dict(rich_persona)
        analysis = await _analyze_artist_psychology_deep(character, persona, ctx)

        # Check for meaningful content
        if not analysis.get("musical_genesis", {}).get("origin_story"):
            print("❌ No meaningful origin story generated")
            return False

        if not analysis.get("backstory_influences", {}).get("backstory_to_lyrics_pipeline"):
            print("❌ No meaningful backstory analysis generated")
            return False

        # Check that analysis incorporates character-specific details
        origin_story = analysis.get("musical_genesis", {}).get("origin_story", "").lower()
        if "rich character" not in origin_story:
            print("❌ Analysis doesn't incorporate character name")
            return False

        print("✅ Generated meaningful, character-specific analysis")
        print(f"   Origin story: {analysis.get('musical_genesis', {}).get('origin_story', '')[:100]}...")

    except Exception as e:
        print(f"❌ Failed to generate meaningful analysis: {e}")
        return False

    # Test Case 5: Test with nested JSON format (as would come from MCP tool)
    print("\n5. Testing nested JSON format...")
    nested_data = {
        "characters": [rich_character],
        "metadata": {"source": "test"}
    }

    nested_persona_data = {
        "artist_personas": [rich_persona],
        "generation_info": {"version": "1.0"}
    }

    try:
        # Simulate MCP tool extraction logic
        character_info = nested_data['characters'][0]
        persona_info = nested_persona_data['artist_personas'][0]

        character = StandardCharacterProfile.from_dict(character_info)
        persona = ArtistPersona.from_dict(persona_info)
        analysis = await _analyze_artist_psychology_deep(character, persona, ctx)

        if not analysis or not isinstance(analysis, dict):
            print("❌ Failed to handle nested JSON format")
            return False

        print("✅ Successfully handled nested JSON format")

    except Exception as e:
        print(f"❌ Failed with nested format: {e}")
        return False

    return True

async def main():
    """Run the comprehensive test"""
    success = await test_comprehensive_format_fixes()

    if success:
        print("\n🎉 All comprehensive tests passed!")
        print("   ✅ Handles 'age' parameter errors gracefully")
        print("   ✅ Handles unknown/extra fields gracefully")
        print("   ✅ Works with minimal character data")
        print("   ✅ Generates meaningful psychological analysis")
        print("   ✅ Incorporates character-specific details")
        print("   ✅ Works with nested JSON formats")
        print("   ✅ Uses StandardCharacterProfile.from_dict() correctly")
        print("   ✅ Uses ArtistPersona.from_dict() correctly")
        sys.exit(0)
    else:
        print("\n💥 Comprehensive tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
