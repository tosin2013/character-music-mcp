import pytest

#!/usr/bin/env python3
"""
Test script to verify the generate_artist_personas tool format fix

This test verifies that:
1. The tool accepts StandardCharacterProfile format without 'skin' parameter errors
2. CharacterProfile initialization uses correct parameter names
3. Input validation handles various character profile formats gracefully
4. Persona generation works with corrected character profile structure
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from server import generate_artist_personas
from standard_character_profile import StandardCharacterProfile

from tests.fixtures.mock_contexts import MockContext


@pytest.mark.asyncio
async def test_standard_character_profile_format():
    """Test that the tool accepts StandardCharacterProfile format correctly"""
    print("Testing StandardCharacterProfile format acceptance...")

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

    # Create test input in the expected format
    test_input = {
        "characters": [test_character.to_dict()],
        "narrative_themes": ["self-discovery", "artistic growth"],
        "emotional_arc": ["uncertainty", "exploration", "acceptance"]
    }

    # Convert to JSON string as expected by the tool
    characters_json = json.dumps(test_input)

    # Create mock context
    ctx = MockContext()

    try:
        # Call the generate_artist_personas tool
        result = await generate_artist_personas(characters_json, ctx)

        # Parse the result
        result_data = json.loads(result)

        # Check for errors
        if "error" in result_data:
            print(f"❌ Error in persona generation: {result_data['error']}")
            return False

        # Verify the result structure
        if "artist_personas" not in result_data:
            print("❌ Missing 'artist_personas' in result")
            return False

        personas = result_data["artist_personas"]
        if not personas:
            print("❌ No personas generated")
            return False

        # Verify persona structure
        persona = personas[0]
        required_fields = [
            "character_name", "artist_name", "primary_genre", "secondary_genres",
            "vocal_style", "instrumental_preferences", "lyrical_themes",
            "emotional_palette", "artistic_influences", "collaboration_style",
            "character_mapping_confidence", "genre_justification", "persona_description"
        ]

        for field in required_fields:
            if field not in persona:
                print(f"❌ Missing required field '{field}' in persona")
                return False

        print("✅ StandardCharacterProfile format accepted successfully")
        print(f"✅ Generated persona for: {persona['character_name']}")
        print(f"✅ Artist name: {persona['artist_name']}")
        print(f"✅ Primary genre: {persona['primary_genre']}")
        print(f"✅ Confidence: {persona['character_mapping_confidence']}")

        return True

    except Exception as e:
        print(f"❌ Exception during persona generation: {str(e)}")
        return False


@pytest.mark.asyncio
async def test_input_validation():
    """Test input validation with various character profile formats"""
    print("\nTesting input validation with various formats...")

    ctx = MockContext()

    # Test 1: Invalid JSON
    try:
        result = await generate_artist_personas("invalid json", ctx)
        result_data = json.loads(result)
        if "error" not in result_data:
            print("❌ Should have failed with invalid JSON")
            return False
        print("✅ Correctly handled invalid JSON")
    except Exception as e:
        print(f"❌ Unexpected exception with invalid JSON: {e}")
        return False

    # Test 2: Missing 'characters' field
    try:
        test_input = {"invalid": "format"}
        result = await generate_artist_personas(json.dumps(test_input), ctx)
        result_data = json.loads(result)
        if "error" not in result_data:
            print("❌ Should have failed with missing 'characters' field")
            return False
        print("✅ Correctly handled missing 'characters' field")
    except Exception as e:
        print(f"❌ Unexpected exception with missing 'characters': {e}")
        return False

    # Test 3: Empty characters array
    try:
        test_input = {"characters": []}
        result = await generate_artist_personas(json.dumps(test_input), ctx)
        result_data = json.loads(result)
        if "error" not in result_data:
            print("❌ Should have failed with empty characters array")
            return False
        print("✅ Correctly handled empty characters array")
    except Exception as e:
        print(f"❌ Unexpected exception with empty characters: {e}")
        return False

    # Test 4: Character with missing name
    try:
        test_character = {"backstory": "A character without a name"}
        test_input = {"characters": [test_character]}
        result = await generate_artist_personas(json.dumps(test_input), ctx)
        result_data = json.loads(result)

        # Should still work but with default name
        if "error" in result_data:
            print("✅ Correctly handled character with missing name")
        else:
            # Check if it created a character with default name
            personas = result_data.get("artist_personas", [])
            if personas and personas[0]["character_name"] == "Unknown Character":
                print("✅ Correctly handled character with missing name (created default)")
            else:
                print("❌ Did not handle missing name correctly")
                return False
    except Exception as e:
        print(f"❌ Unexpected exception with missing name: {e}")
        return False

    # Test 5: Character with minimal valid data
    try:
        test_character = {
            "name": "Minimal Character",
            "backstory": "A character with minimal information"
        }
        test_input = {"characters": [test_character]}
        result = await generate_artist_personas(json.dumps(test_input), ctx)
        result_data = json.loads(result)

        if "error" in result_data:
            print(f"❌ Failed with minimal valid character: {result_data['error']}")
            return False

        personas = result_data.get("artist_personas", [])
        if not personas:
            print("❌ No personas generated for minimal character")
            return False

        print("✅ Correctly handled character with minimal data")
    except Exception as e:
        print(f"❌ Unexpected exception with minimal character: {e}")
        return False

    return True


@pytest.mark.asyncio
async def test_legacy_format_compatibility():
    """Test compatibility with legacy character profile formats"""
    print("\nTesting legacy format compatibility...")

    ctx = MockContext()

    # Test with old format that might have caused 'skin' parameter errors
    legacy_character = {
        "name": "Legacy Character",
        "skin": "This field should be ignored",  # This was causing errors
        "age": 25,  # This was also causing errors
        "backstory": "A character from the old format",
        "conflicts": ["internal struggle"],
        "fears": ["failure"],
        "unknown_field": "This should be ignored"
    }

    test_input = {"characters": [legacy_character]}

    try:
        result = await generate_artist_personas(json.dumps(test_input), ctx)
        result_data = json.loads(result)

        if "error" in result_data:
            print(f"❌ Failed with legacy format: {result_data['error']}")
            return False

        personas = result_data.get("artist_personas", [])
        if not personas:
            print("❌ No personas generated for legacy character")
            return False

        persona = personas[0]
        if persona["character_name"] != "Legacy Character":
            print(f"❌ Wrong character name: {persona['character_name']}")
            return False

        print("✅ Successfully handled legacy format with unknown fields")
        print(f"✅ Generated persona: {persona['artist_name']}")

        return True

    except Exception as e:
        print(f"❌ Exception with legacy format: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("🧪 Testing generate_artist_personas tool format fixes\n")

    tests = [
        test_standard_character_profile_format,
        test_input_validation,
        test_legacy_format_compatibility
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
        print("🎉 All tests passed! The generate_artist_personas tool format fix is working correctly.")
        return True
    else:
        print("❌ Some tests failed. The fix needs more work.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
