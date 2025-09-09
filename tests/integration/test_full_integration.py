import pytest

#!/usr/bin/env python3
"""
Test script to verify the full integration of the generate_artist_personas fix

This test simulates the actual MCP tool call by directly calling the underlying function logic.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from dataclasses import asdict

from server import persona_generator
from standard_character_profile import StandardCharacterProfile
from tests.fixtures.mock_contexts import MockContext


@pytest.mark.asyncio
async def test_full_integration():
    """Test the full integration by simulating the generate_artist_personas tool logic"""
    print("Testing full integration of generate_artist_personas fix...")

    # Create test characters using StandardCharacterProfile
    test_characters = [
        StandardCharacterProfile(
            name="Alice Writer",
            aliases=["A.W.", "The Wordsmith"],
            physical_description="Tall with thoughtful eyes and ink-stained fingers",
            mannerisms=["adjusts glasses when thinking", "taps pen rhythmically"],
            speech_patterns=["uses literary references", "speaks in measured tones"],
            behavioral_traits=["introspective", "creative", "perfectionist"],
            backstory="A novelist who turned to music to express emotions that words couldn't capture",
            relationships=["mentor Professor Davis", "writing group friends"],
            formative_experiences=["first published story", "writer's block crisis"],
            social_connections=["literary community", "local coffee shop regulars"],
            motivations=["express deep emotions", "connect with readers"],
            fears=["creative failure", "being misunderstood"],
            desires=["artistic recognition", "emotional authenticity"],
            conflicts=["perfectionism vs. spontaneity", "solitude vs. connection"],
            personality_drivers=["need for creative expression", "desire to touch hearts"],
            confidence_score=0.8,
            text_references=["character analysis from novel"],
            first_appearance="Chapter 1",
            importance_score=0.9
        ),
        StandardCharacterProfile(
            name="Bob Mechanic",
            backstory="A car mechanic who finds rhythm in the sounds of his workshop",
            motivations=["fix things", "create order from chaos"],
            fears=["things breaking down"],
            personality_drivers=["practical problem-solving"],
            confidence_score=0.7,
            importance_score=0.6
        )
    ]

    # Create test input in the expected format
    test_input = {
        "characters": [char.to_dict() for char in test_characters],
        "narrative_themes": ["self-discovery", "artistic growth", "blue-collar dreams"],
        "emotional_arc": ["uncertainty", "exploration", "acceptance"]
    }

    # Convert to JSON string as expected by the tool
    characters_json = json.dumps(test_input)

    # Create mock context
    ctx = MockContext()

    try:
        # Simulate the generate_artist_personas tool logic
        await ctx.info("Generating artist personas...")

        # Parse character data (same as in the actual tool)
        data = json.loads(characters_json)
        if 'characters' not in data:
            print("❌ Invalid character data format. Expected 'characters' field.")
            return False

        characters_data = data['characters']
        if not characters_data:
            print("❌ No characters found in input data.")
            return False

        artist_personas = []

        for char_data in characters_data:
            try:
                # Validate character data format
                if not isinstance(char_data, dict):
                    await ctx.error(f"Invalid character data format: expected dict, got {type(char_data)}")
                    continue

                # Convert dict to StandardCharacterProfile with graceful error handling
                character = StandardCharacterProfile.from_dict(char_data)

                # Validate that character has minimum required information
                if not character.name or character.name == "Unknown Character":
                    await ctx.error(f"Character missing required name field: {char_data}")
                    continue

                # Generate artist persona
                persona = await persona_generator.generate_artist_persona(character, ctx)
                artist_personas.append(asdict(persona))

            except Exception as e:
                await ctx.error(f"Failed to process character data {char_data}: {str(e)}")
                continue

        result = {
            "artist_personas": artist_personas,
            "total_personas": len(artist_personas),
            "generation_summary": f"Generated {len(artist_personas)} unique artist personas from character analysis"
        }

        await ctx.info(f"Generated {len(artist_personas)} artist personas")

        # Verify the results
        if not artist_personas:
            print("❌ No personas generated")
            return False

        if len(artist_personas) != 2:
            print(f"❌ Expected 2 personas, got {len(artist_personas)}")
            return False

        # Check each persona
        for i, persona in enumerate(artist_personas):
            character_name = test_characters[i].name

            # Verify required fields
            required_fields = [
                "character_name", "artist_name", "primary_genre", "secondary_genres",
                "vocal_style", "instrumental_preferences", "lyrical_themes",
                "emotional_palette", "artistic_influences", "collaboration_style",
                "character_mapping_confidence", "genre_justification", "persona_description"
            ]

            for field in required_fields:
                if field not in persona:
                    print(f"❌ Missing required field '{field}' in persona for {character_name}")
                    return False

            if persona["character_name"] != character_name:
                print(f"❌ Wrong character name: expected {character_name}, got {persona['character_name']}")
                return False

            print(f"✅ Generated persona for {character_name}:")
            print(f"   Artist: {persona['artist_name']}")
            print(f"   Genre: {persona['primary_genre']}")
            print(f"   Confidence: {persona['character_mapping_confidence']}")

        print("✅ Full integration test passed!")
        print(f"✅ Successfully processed {len(artist_personas)} characters")
        print("✅ All personas have required fields")
        print("✅ Input validation worked correctly")

        return True

    except Exception as e:
        print(f"❌ Exception during full integration test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling with problematic inputs"""
    print("\nTesting error handling...")

    ctx = MockContext()

    # Test with character that has problematic legacy fields
    problematic_character = {
        "name": "Problematic Character",
        "skin": "This should be ignored",  # This was causing 'skin' parameter errors
        "age": 30,  # This was causing 'age' parameter errors
        "invalid_list_field": "should be list but is string",
        "backstory": "A character with problematic fields",
        "confidence_score": 1.5,  # Invalid score (should be 0-1)
        "importance_score": -0.5   # Invalid score (should be 0-1)
    }

    test_input = {"characters": [problematic_character]}
    characters_json = json.dumps(test_input)

    try:
        # Parse and process
        data = json.loads(characters_json)
        characters_data = data['characters']

        char_data = characters_data[0]

        # This should not fail even with problematic fields
        character = StandardCharacterProfile.from_dict(char_data)

        # Check that problematic fields were handled
        if hasattr(character, 'skin') or hasattr(character, 'age'):
            print("❌ Problematic fields were not filtered out")
            return False

        # Check that scores were normalized
        if character.confidence_score > 1.0 or character.confidence_score < 0.0:
            print(f"❌ Confidence score not normalized: {character.confidence_score}")
            return False

        if character.importance_score > 1.0 or character.importance_score < 0.0:
            print(f"❌ Importance score not normalized: {character.importance_score}")
            return False

        # Generate persona - this should work
        persona = await persona_generator.generate_artist_persona(character, ctx)

        if not persona:
            print("❌ Failed to generate persona from problematic character")
            return False

        print("✅ Successfully handled problematic character fields")
        print(f"✅ Generated persona: {persona.artist_name}")
        print(f"✅ Normalized confidence: {character.confidence_score}")
        print(f"✅ Normalized importance: {character.importance_score}")

        return True

    except Exception as e:
        print(f"❌ Failed to handle problematic character: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all integration tests"""
    print("🧪 Testing full integration of generate_artist_personas fix\n")

    tests = [
        test_full_integration,
        test_error_handling
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

    print(f"\n📊 Integration Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed! The generate_artist_personas tool fix is working correctly.")
        return True
    else:
        print("❌ Some integration tests failed. The fix needs more work.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
