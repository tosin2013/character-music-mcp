#!/usr/bin/env python3
"""
Test script to verify character and genre specifications are respected
"""

from working_universal_processor import WorkingUniversalProcessor


def test_character_genre_respect():
    """Test that different characters and genres produce different results"""

    print("🎭 TESTING CHARACTER AND GENRE RESPECT")
    print("=" * 60)

    # Test cases with different characters and genres
    test_cases = [
        {
            "name": "Memphis Hip-Hop Producer",
            "description": "DJ Memphis is a 25-year-old Memphis hip-hop producer working out of his home studio, known for his introspective approach to beats and philosophical lyrics.",
            "expected_genre": "memphis hip-hop",
            "expected_name": "DJ Memphis"
        },
        {
            "name": "Neo-Soul Singer",
            "description": "Sarah Johnson is a 28-year-old neo-soul singer from Atlanta, known for her powerful vocals and socially conscious lyrics about community empowerment.",
            "expected_genre": "neo-soul",
            "expected_name": "Sarah Johnson"
        },
        {
            "name": "Electronic Producer",
            "description": "Alex Chen is a 30-year-old electronic music producer from Los Angeles, specializing in ambient soundscapes and experimental beats.",
            "expected_genre": "electronic",
            "expected_name": "Alex Chen"
        }
    ]

    content = "A young artist struggles with finding their authentic voice in the music industry."

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎤 TEST CASE {i}: {test_case['name']}")
        print("=" * 40)
        print(f"Description: {test_case['description']}")

        # Create processor with specific character
        processor = WorkingUniversalProcessor(test_case['description'])

        # Check character parsing
        character = processor.character_worldview
        print(f"Parsed Name: {character['name']}")
        print(f"Parsed Genre: {character['context']['genre']}")
        print(f"Parsed Location: {character['context']['location']}")
        print(f"Character Filter: {character['filter']}")

        # Verify expectations
        name_match = test_case['expected_name'] in character['name']
        genre_match = test_case['expected_genre'] == character['context']['genre']

        print(f"✅ Name Match: {name_match} ({'PASS' if name_match else 'FAIL'})")
        print(f"✅ Genre Match: {genre_match} ({'PASS' if genre_match else 'FAIL'})")

        # Test track generation with this character
        result = processor.process_track_content(
            content,
            "Authentic Voice",
            "personal_struggle",
            "Intimate examination of finding authentic voice",
            1, 1
        )

        # Check if character details appear in output
        character_in_interpretation = character['name'].split()[0] in result.character_interpretation
        genre_in_command = character['context']['genre'] in result.suno_command.lower()

        print(f"✅ Character in Interpretation: {character_in_interpretation} ({'PASS' if character_in_interpretation else 'FAIL'})")
        print(f"✅ Genre in Suno Command: {genre_in_command} ({'PASS' if genre_in_command else 'FAIL'})")

        # Show sample output
        print("\nSample Character Interpretation:")
        print(f"  {result.character_interpretation[:150]}...")

        print("\nSample Suno Command (first few lines):")
        command_lines = result.suno_command.split('\n')[:5]
        for line in command_lines:
            if line.strip():
                print(f"  {line}")

    print("\n🎯 CHARACTER AND GENRE RESPECT TEST COMPLETE!")

def test_hardcoded_content_removal():
    """Test that hardcoded Bristol/Marcus content is not present"""

    print("\n🚫 TESTING HARDCODED CONTENT REMOVAL")
    print("=" * 60)

    # Test with completely different character
    character_description = "Luna Rodriguez is a 22-year-old folk singer from Seattle, known for her acoustic guitar work and environmental activism themes."

    processor = WorkingUniversalProcessor(character_description)

    result = processor.process_track_content(
        "Environmental destruction threatens our planet's future.",
        "Earth's Song",
        "environmental_concern",
        "Passionate exploration of environmental themes",
        1, 1
    )

    # Check for hardcoded content
    hardcoded_terms = ["marcus", "bristol", "warehouse studio", "philosophical liquid dnb"]

    full_output = f"{result.character_interpretation} {result.personal_story} {result.formatted_lyrics} {result.suno_command}".lower()

    print("Checking for hardcoded content:")
    for term in hardcoded_terms:
        found = term in full_output
        print(f"  '{term}': {'FOUND (BAD)' if found else 'NOT FOUND (GOOD)'}")

    # Check for expected character content
    expected_terms = ["luna", "seattle", "folk", "acoustic", "environmental"]

    print("\nChecking for character-specific content:")
    for term in expected_terms:
        found = term in full_output
        print(f"  '{term}': {'FOUND (GOOD)' if found else 'NOT FOUND (BAD)'}")

    print("\nSample output with Luna character:")
    print(f"Character Interpretation: {result.character_interpretation[:200]}...")

if __name__ == "__main__":
    test_character_genre_respect()
    test_hardcoded_content_removal()
