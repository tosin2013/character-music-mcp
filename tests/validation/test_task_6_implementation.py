#!/usr/bin/env python3
"""
Test implementation of Task 6: Remove hardcoded content from process_universal_content tool

This test verifies that:
- 6.1: Hardcoded Bristol backstory is replaced with dynamic content
- 6.2: Genre-aware content generation is implemented

Requirements tested:
- 5.1: Character descriptions are used instead of hardcoded "Marcus" or Bristol references
- 5.2: Genre specifications generate content in requested genre, not always alternative/philosophical  
- 5.3: Output reflects input parameters, not predetermined backstories
- 5.4: Different characters generate unique content for each character
"""

from working_universal_processor import WorkingUniversalProcessor


def test_hardcoded_content_removal():
    """Test that hardcoded Bristol/Marcus content is replaced with dynamic content"""
    print("🧪 Testing hardcoded content removal...")

    # Test with different character descriptions
    test_cases = [
        {
            "description": "Marcus Thompson, 34-year-old liquid drum and bass producer from Bristol warehouse studio",
            "expected_name": "Marcus Thompson",
            "expected_location": "warehouse studio",  # Should not be hardcoded Bristol
            "expected_genre": "liquid drum and bass"
        },
        {
            "description": "Sarah Chen, 28-year-old neo-soul artist from Los Angeles home studio",
            "expected_name": "Sarah Chen",
            "expected_location": "Los Angeles home studio",
            "expected_genre": "neo-soul"
        },
        {
            "description": "DJ Memphis, 25-year-old Memphis hip-hop producer from basement studio",
            "expected_name": "DJ Memphis",
            "expected_location": "Memphis basement studio",
            "expected_genre": "memphis hip-hop"
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n  Test Case {i}: {case['description'][:50]}...")

        processor = WorkingUniversalProcessor(case["description"])
        result = processor.process_any_content("Love and loss", f"Test Track {i}")

        # Verify character extraction
        assert processor.character_worldview["name"] == case["expected_name"], \
            f"Expected name {case['expected_name']}, got {processor.character_worldview['name']}"

        # Verify location extraction (not hardcoded)
        actual_location = processor.character_worldview["context"]["location"]
        assert case["expected_location"] in actual_location, \
            f"Expected location to contain {case['expected_location']}, got {actual_location}"

        # Verify genre detection
        assert processor.character_worldview["context"]["genre"] == case["expected_genre"], \
            f"Expected genre {case['expected_genre']}, got {processor.character_worldview['context']['genre']}"

        # Verify no hardcoded Bristol/Marcus content in personal story
        personal_story = result.personal_story.lower()
        hardcoded_terms = ["bristol warehouse studio", "dad died", "theological disagreements", "3am in my bristol"]

        for term in hardcoded_terms:
            assert term not in personal_story, \
                f"Found hardcoded content '{term}' in personal story: {personal_story}"

        print(f"    ✅ Character: {processor.character_worldview['name']}")
        print(f"    ✅ Genre: {processor.character_worldview['context']['genre']}")
        print(f"    ✅ Location: {processor.character_worldview['context']['location']}")
        print("    ✅ No hardcoded content found")

def test_genre_aware_content_generation():
    """Test that content generation is genre-aware"""
    print("\n🎵 Testing genre-aware content generation...")

    genre_tests = [
        {
            "description": "Trap King, 24-year-old trap producer from Atlanta",
            "expected_genre": "trap",
            "expected_production_keywords": ["808", "hi-hat", "trap"]
        },
        {
            "description": "Jazz Cat, 35-year-old jazz fusion artist from New York",
            "expected_genre": "jazz fusion",
            "expected_production_keywords": ["acoustic", "electric", "complex"]
        },
        {
            "description": "Folk Singer, 29-year-old indie folk artist from Nashville",
            "expected_genre": "indie folk",
            "expected_production_keywords": ["acoustic", "creative", "intimate"]
        },
        {
            "description": "Techno Master, 31-year-old techno producer from Detroit warehouse",
            "expected_genre": "techno",
            "expected_production_keywords": ["driving", "4/4", "industrial"]
        }
    ]

    for i, case in enumerate(genre_tests, 1):
        print(f"\n  Genre Test {i}: {case['expected_genre']}")

        processor = WorkingUniversalProcessor(case["description"])

        # Verify genre detection
        actual_genre = processor.character_worldview["context"]["genre"]
        assert actual_genre == case["expected_genre"], \
            f"Expected genre {case['expected_genre']}, got {actual_genre}"

        # Verify genre-specific production characteristics
        production_style = processor._get_production_style().lower()
        production_notes = processor._get_production_notes().lower()
        vocal_style = processor._get_vocal_style().lower()

        # Check that genre-specific keywords appear in production content
        found_keywords = []
        all_content = f"{production_style} {production_notes} {vocal_style}"

        for keyword in case["expected_production_keywords"]:
            if keyword.lower() in all_content:
                found_keywords.append(keyword)

        assert len(found_keywords) > 0, \
            f"No genre-specific keywords {case['expected_production_keywords']} found in production content"

        print(f"    ✅ Genre detected: {actual_genre}")
        print(f"    ✅ Genre-specific keywords found: {found_keywords}")
        print(f"    ✅ Production style: {production_style[:60]}...")

def test_dynamic_vs_hardcoded_comparison():
    """Test that different characters produce different content (not hardcoded)"""
    print("\n🔄 Testing dynamic content generation...")

    # Create two very different characters
    character1 = WorkingUniversalProcessor("Spiritual Sam, 40-year-old ambient electronic artist from Seattle home studio, spiritual approach")
    character2 = WorkingUniversalProcessor("Gangsta G, 22-year-old trap rapper from Atlanta basement studio, social conscious approach")

    # Process same content through both characters
    content = "The struggle for justice in modern society"
    result1 = character1.process_any_content(content, "Justice Track 1")
    result2 = character2.process_any_content(content, "Justice Track 2")

    # Verify they produce different results
    assert result1.character_interpretation != result2.character_interpretation, \
        "Different characters should produce different interpretations"

    assert result1.personal_story != result2.personal_story, \
        "Different characters should produce different personal stories"

    # Verify genre-specific differences
    assert character1.character_worldview["context"]["genre"] != character2.character_worldview["context"]["genre"], \
        "Different characters should have different genres"

    print(f"    ✅ Character 1 ({character1.character_worldview['name']}): {character1.character_worldview['context']['genre']}")
    print(f"    ✅ Character 2 ({character2.character_worldview['name']}): {character2.character_worldview['context']['genre']}")
    print("    ✅ Different interpretations generated")
    print("    ✅ Different personal stories generated")

def main():
    """Run all tests for Task 6 implementation"""
    print("🚀 TESTING TASK 6: REMOVE HARDCODED CONTENT FROM PROCESS_UNIVERSAL_CONTENT TOOL")
    print("=" * 80)

    try:
        test_hardcoded_content_removal()
        test_genre_aware_content_generation()
        test_dynamic_vs_hardcoded_comparison()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("\nTask 6 Requirements Verified:")
        print("  ✅ 6.1: Hardcoded Bristol backstory replaced with dynamic content")
        print("  ✅ 6.2: Genre-aware content generation implemented")
        print("\nRequirements 5.1-5.4 Satisfied:")
        print("  ✅ 5.1: Uses provided character descriptions, not hardcoded Marcus/Bristol")
        print("  ✅ 5.2: Generates content in requested genre, not always alternative")
        print("  ✅ 5.3: Output reflects input parameters, not predetermined backstories")
        print("  ✅ 5.4: Different characters generate unique content")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        return False

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
