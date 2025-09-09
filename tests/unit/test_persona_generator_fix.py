import pytest

#!/usr/bin/env python3
"""
Test script to verify the MusicPersonaGenerator format fix

This test verifies that the MusicPersonaGenerator can work with StandardCharacterProfile
without format errors.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from server import MusicPersonaGenerator
from standard_character_profile import StandardCharacterProfile
from tests.fixtures.mock_contexts import MockContext


@pytest.mark.asyncio
async def test_persona_generator_with_standard_profile():
    """Test that MusicPersonaGenerator works with StandardCharacterProfile"""
    print("Testing MusicPersonaGenerator with StandardCharacterProfile...")

    # Create a test character using StandardCharacterProfile
    test_character = StandardCharacterProfile(
        name="Test Character",
        aliases=["Tester"],
        physical_description="A thoughtful individual with expressive eyes",
        mannerisms=["taps fingers when thinking", "speaks softly"],
        speech_patterns=["uses metaphors", "pauses before important points"],
        behavioral_traits=["introspective", "creative", "empathetic"],
        backstory="A writer who discovered music as a form of emotional expression",
        relationships=["close friend Sarah", "mentor Professor Johnson"],
        formative_experiences=["first poetry reading", "loss of grandmother"],
        social_connections=["local writing group", "university alumni network"],
        motivations=["express authentic emotions", "connect with others"],
        fears=["being misunderstood", "creative failure"],
        desires=["artistic recognition", "meaningful relationships"],
        conflicts=["perfectionism vs. authenticity", "solitude vs. connection"],
        personality_drivers=["need for creative expression", "desire to help others"],
        confidence_score=0.85,
        text_references=["original character description"],
        first_appearance="Chapter 1",
        importance_score=0.9
    )

    # Create persona generator
    persona_generator = MusicPersonaGenerator()

    # Create mock context
    ctx = MockContext()

    try:
        # Generate artist persona
        persona = await persona_generator.generate_artist_persona(test_character, ctx)

        # Verify the persona was created successfully
        if not persona:
            print("❌ No persona generated")
            return False

        # Check required fields
        required_fields = [
            "character_name", "artist_name", "primary_genre", "secondary_genres",
            "vocal_style", "instrumental_preferences", "lyrical_themes",
            "emotional_palette", "artistic_influences", "collaboration_style",
            "character_mapping_confidence", "genre_justification", "persona_description"
        ]

        for field in required_fields:
            if not hasattr(persona, field):
                print(f"❌ Missing required field '{field}' in persona")
                return False

        print("✅ Successfully generated persona with StandardCharacterProfile")
        print(f"✅ Character: {persona.character_name}")
        print(f"✅ Artist: {persona.artist_name}")
        print(f"✅ Genre: {persona.primary_genre}")
        print(f"✅ Confidence: {persona.character_mapping_confidence}")

        return True

    except Exception as e:
        print(f"❌ Exception during persona generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


@pytest.mark.asyncio
async def test_minimal_character_profile():
    """Test with minimal character profile data"""
    print("\nTesting with minimal character profile...")

    # Create minimal character
    minimal_character = StandardCharacterProfile(
        name="Minimal Character",
        backstory="A character with minimal information"
    )

    # Create persona generator
    persona_generator = MusicPersonaGenerator()

    # Create mock context
    ctx = MockContext()

    try:
        # Generate artist persona
        persona = await persona_generator.generate_artist_persona(minimal_character, ctx)

        if not persona:
            print("❌ No persona generated for minimal character")
            return False

        print("✅ Successfully generated persona for minimal character")
        print(f"✅ Character: {persona.character_name}")
        print(f"✅ Artist: {persona.artist_name}")

        return True

    except Exception as e:
        print(f"❌ Exception with minimal character: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


@pytest.mark.asyncio
async def test_character_profile_from_dict():
    """Test StandardCharacterProfile.from_dict with various formats"""
    print("\nTesting StandardCharacterProfile.from_dict...")

    # Test with legacy format that might have caused errors
    legacy_data = {
        "name": "Legacy Character",
        "skin": "This field should be ignored",  # This was causing errors
        "age": 25,  # This was also causing errors
        "backstory": "A character from the old format",
        "conflicts": ["internal struggle"],
        "fears": ["failure"],
        "unknown_field": "This should be ignored"
    }

    try:
        # Create character from legacy data
        character = StandardCharacterProfile.from_dict(legacy_data)

        if not character:
            print("❌ Failed to create character from legacy data")
            return False

        if character.name != "Legacy Character":
            print(f"❌ Wrong character name: {character.name}")
            return False

        # Check that unknown fields were ignored
        if hasattr(character, 'skin') or hasattr(character, 'age') or hasattr(character, 'unknown_field'):
            print("❌ Unknown fields were not properly ignored")
            return False

        print("✅ Successfully created StandardCharacterProfile from legacy data")
        print(f"✅ Name: {character.name}")
        print(f"✅ Backstory: {character.backstory}")
        print(f"✅ Conflicts: {character.conflicts}")
        print(f"✅ Fears: {character.fears}")

        # Now test persona generation with this character
        persona_generator = MusicPersonaGenerator()
        ctx = MockContext()

        persona = await persona_generator.generate_artist_persona(character, ctx)

        if not persona:
            print("❌ Failed to generate persona from legacy character")
            return False

        print("✅ Successfully generated persona from legacy character data")

        return True

    except Exception as e:
        print(f"❌ Exception with legacy data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("🧪 Testing MusicPersonaGenerator format fixes\n")

    tests = [
        test_persona_generator_with_standard_profile,
        test_minimal_character_profile,
        test_character_profile_from_dict
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if await test():
                passed += 1
            else:
                print("❌ Test failed")
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The MusicPersonaGenerator format fix is working correctly.")
        return True
    else:
        print("❌ Some tests failed. The fix needs more work.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
