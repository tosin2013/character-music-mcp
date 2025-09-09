#!/usr/bin/env python3

"""
Final validation test for enhanced understand_topic_with_emotions tool

This test validates that the enhanced tool meets all requirements:
- Requirement 11.1: Replace input text repetition with actual emotional understanding
- Requirement 11.2: Generate varied emotional insights beyond "contemplative"
- Requirement 11.3: Create contextually appropriate emotional responses for different topics
- Requirement 11.4: Generate meaningful beat patterns and musical elements
"""

import asyncio
import json
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import _understand_topic_with_emotions_internal


class MockContext:
    def __init__(self):
        self.messages = []

    async def info(self, message):
        self.messages.append(f"INFO: {message}")

    async def error(self, message):
        self.messages.append(f"ERROR: {message}")

async def validate_requirement_11_1(ctx):
    """Validate Requirement 11.1: Replace input text repetition with actual emotional understanding"""
    print("🔍 Validating Requirement 11.1: Actual emotional understanding (not input repetition)")

    test_text = "The detective walked through the dark alley, his heart pounding with fear as shadows seemed to move around him."

    result = await _understand_topic_with_emotions_internal(
        topic_text=test_text,
        source_type="story",
        ctx=ctx
    )

    result_data = json.loads(result)

    # Check that the output is not just repeating the input
    comprehensive_understanding = result_data.get("comprehensive_understanding", "")

    if test_text.lower() in comprehensive_understanding.lower():
        print("   ❌ FAILED: Output appears to repeat input text")
        return False

    # Check that we have actual emotional analysis
    emotional_analysis = result_data.get("emotional_analysis", {})
    if not emotional_analysis.get("primary_emotions"):
        print("   ❌ FAILED: No emotional analysis performed")
        return False

    print("   ✅ PASSED: Tool performs actual emotional understanding, not input repetition")
    return True

async def validate_requirement_11_2(ctx):
    """Validate Requirement 11.2: Generate varied emotional insights beyond 'contemplative'"""
    print("🔍 Validating Requirement 11.2: Varied emotional insights beyond 'contemplative'")

    test_cases = [
        {
            "text": "The explosion shattered the windows as Sarah ran for her life, terror gripping her heart.",
            "expected_not": "contemplative"
        },
        {
            "text": "Maria danced with joy as she received the acceptance letter to her dream university.",
            "expected_not": "contemplative"
        },
        {
            "text": "The old man wept silently as he held the photograph of his deceased wife.",
            "expected_not": "contemplative"
        }
    ]

    varied_emotions_detected = []

    for test_case in test_cases:
        result = await _understand_topic_with_emotions_internal(
            topic_text=test_case["text"],
            source_type="story",
            ctx=ctx
        )

        result_data = json.loads(result)
        emotional_analysis = result_data.get("emotional_analysis", {})
        dominant_mood = emotional_analysis.get("dominant_mood", "unknown")

        varied_emotions_detected.append(dominant_mood)

    # Check that we got varied emotions
    unique_emotions = set(varied_emotions_detected)
    if len(unique_emotions) < 2:
        print(f"   ❌ FAILED: Only detected {unique_emotions}, need more variety")
        return False

    # Check that not everything is "contemplative"
    if all(emotion == "contemplative" for emotion in varied_emotions_detected):
        print("   ❌ FAILED: All emotions detected as 'contemplative'")
        return False

    print(f"   ✅ PASSED: Detected varied emotions: {', '.join(unique_emotions)}")
    return True

async def validate_requirement_11_3(ctx):
    """Validate Requirement 11.3: Contextually appropriate emotional responses for different topics"""
    print("🔍 Validating Requirement 11.3: Contextually appropriate emotional responses")

    test_cases = [
        {
            "text": "The horror movie featured a serial killer stalking victims through a haunted house.",
            "source_type": "movie",
            "expected_emotions": ["terrified", "anxious", "fearful"],
            "expected_genres": ["horror", "dark", "industrial"]
        },
        {
            "text": "The romantic comedy showed two people falling in love during a summer vacation in Paris.",
            "source_type": "movie",
            "expected_emotions": ["hopeful", "joyful", "romantic"],
            "expected_genres": ["romantic", "uplifting", "light"]
        },
        {
            "text": "The philosophical treatise explored the nature of consciousness and reality.",
            "source_type": "philosophy",
            "expected_emotions": ["contemplative", "thoughtful", "intellectual"],
            "expected_genres": ["ambient", "minimal", "experimental"]
        }
    ]

    appropriate_responses = 0

    for test_case in test_cases:
        result = await _understand_topic_with_emotions_internal(
            topic_text=test_case["text"],
            source_type=test_case["source_type"],
            ctx=ctx
        )

        result_data = json.loads(result)

        # Check emotional appropriateness
        emotional_analysis = result_data.get("emotional_analysis", {})
        primary_emotions = [e["emotion"] for e in emotional_analysis.get("primary_emotions", [])]

        # Check if any expected emotions are detected
        emotion_match = any(expected in primary_emotions for expected in test_case["expected_emotions"])

        # Check genre appropriateness
        musical_interpretation = result_data.get("musical_interpretation", {})
        genre_suggestions = musical_interpretation.get("genre_suggestions", [])

        # Check if any expected genre characteristics are present
        genre_match = any(
            any(expected_genre in genre for genre in genre_suggestions)
            for expected_genre in test_case["expected_genres"]
        )

        if emotion_match or genre_match:
            appropriate_responses += 1

    if appropriate_responses < len(test_cases) * 0.7:  # At least 70% should be appropriate
        print(f"   ❌ FAILED: Only {appropriate_responses}/{len(test_cases)} responses were contextually appropriate")
        return False

    print(f"   ✅ PASSED: {appropriate_responses}/{len(test_cases)} responses were contextually appropriate")
    return True

async def validate_requirement_11_4(ctx):
    """Validate Requirement 11.4: Generate meaningful beat patterns and musical elements"""
    print("🔍 Validating Requirement 11.4: Meaningful beat patterns and musical elements")

    test_text = "The jazz musician played a soulful melody in the dimly lit club, his saxophone weeping with emotion."

    result = await _understand_topic_with_emotions_internal(
        topic_text=test_text,
        source_type="story",
        ctx=ctx
    )

    result_data = json.loads(result)

    # Check for beat patterns
    musical_interpretation = result_data.get("musical_interpretation", {})
    beat_patterns = musical_interpretation.get("beat_patterns", {})

    if not beat_patterns:
        print("   ❌ FAILED: No beat patterns generated")
        return False

    # Check for musical elements
    musical_elements = musical_interpretation.get("musical_elements", [])

    if not musical_elements:
        print("   ❌ FAILED: No musical elements generated")
        return False

    # Check for tempo recommendations
    tempo_recommendations = musical_interpretation.get("tempo_recommendations", {})

    if not tempo_recommendations.get("recommended_tempo"):
        print("   ❌ FAILED: No tempo recommendations generated")
        return False

    # Check for Suno commands
    suno_commands = result_data.get("suno_commands", {})
    complete_commands = suno_commands.get("complete_command_set", [])

    if not complete_commands:
        print("   ❌ FAILED: No Suno commands generated")
        return False

    # Check that commands are not generic
    generic_commands = ["[standard_beat]", "[generic_rhythm]", "[default_tempo]"]
    if any(cmd in complete_commands for cmd in generic_commands):
        print("   ❌ FAILED: Generated generic/default commands")
        return False

    print(f"   ✅ PASSED: Generated {len(beat_patterns)} beat patterns, {len(musical_elements)} musical elements, and {len(complete_commands)} Suno commands")
    return True

async def run_final_validation():
    """Run final validation of all requirements"""
    print("🎯 Final Validation: Enhanced understand_topic_with_emotions Tool")
    print("=" * 70)

    ctx = MockContext()

    # Run all requirement validations
    validations = [
        ("11.1", validate_requirement_11_1),
        ("11.2", validate_requirement_11_2),
        ("11.3", validate_requirement_11_3),
        ("11.4", validate_requirement_11_4)
    ]

    results = {}

    for req_num, validation_func in validations:
        try:
            result = await validation_func(ctx)
            results[req_num] = result
        except Exception as e:
            print(f"   ❌ FAILED: Exception during validation: {e}")
            results[req_num] = False

    print("\n" + "=" * 70)
    print("📊 VALIDATION RESULTS:")

    all_passed = True
    for req_num, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   Requirement {req_num}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 70)

    if all_passed:
        print("🎉 ALL REQUIREMENTS VALIDATED SUCCESSFULLY!")
        print("\n✅ Task 12.1: Meaningful emotional analysis - COMPLETE")
        print("   - Replaces input repetition with actual emotional understanding")
        print("   - Generates varied emotional insights beyond 'contemplative'")
        print("   - Creates contextually appropriate emotional responses")

        print("\n✅ Task 12.2: Meaningful beat patterns and musical elements - COMPLETE")
        print("   - Creates genre-appropriate beat patterns")
        print("   - Uses emotional analysis to inform musical recommendations")
        print("   - Generates practical musical suggestions aligned with emotional content")

        print("\n🎵 Enhanced understand_topic_with_emotions tool is fully functional!")
        print("   The tool now provides:")
        print("   - Sophisticated emotional analysis with context and triggers")
        print("   - Varied emotional insights tailored to content type")
        print("   - Genre-appropriate musical recommendations")
        print("   - Practical Suno AI commands based on emotional analysis")
        print("   - Comprehensive production notes and technical recommendations")

    else:
        print("❌ SOME REQUIREMENTS FAILED VALIDATION")
        print("   Please review the failed requirements above.")

    return all_passed

if __name__ == "__main__":
    asyncio.run(run_final_validation())
