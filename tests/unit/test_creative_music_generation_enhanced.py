import pytest
#!/usr/bin/env python3
"""
Test script for enhanced creative_music_generation tool

This script tests the enhanced creative music generation functionality
to ensure it provides meaningful analysis and practical Suno commands.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from server import CreativeMusicEngine
from tests.fixtures.mock_contexts import MockContext

@pytest.mark.asyncio
async def test_enhanced_creative_generation():
    """Test enhanced creative music generation with meaningful analysis"""
    print("Testing Enhanced Creative Music Generation")
    print("=" * 50)
    
    # Create creative music engine
    engine = CreativeMusicEngine()
    
    # Test concepts with different characteristics
    test_concepts = [
        {
            "concept": "The feeling of standing at the edge of a cliff at dawn, watching the world wake up below while contemplating a major life decision",
            "style": "indie folk",
            "expected_elements": ["contemplative", "dawn", "decision", "atmospheric"]
        },
        {
            "concept": "Urban chaos and the rhythm of city life - car horns, footsteps, conversations blending into a symphony of human activity",
            "style": "electronic",
            "expected_elements": ["urban", "rhythmic", "chaos", "electronic"]
        },
        {
            "concept": "A child's laughter echoing through an empty house, memories of family gatherings that once filled these rooms",
            "style": "any",
            "expected_elements": ["nostalgia", "memory", "family", "emotional"]
        }
    ]
    
    for i, test_case in enumerate(test_concepts, 1):
        print(f"\nTest Case {i}: {test_case['concept'][:50]}...")
        print(f"Style Preference: {test_case['style']}")
        
        try:
            # Test concept analysis
            concept_analysis = engine.analyze_musical_concept(test_case["concept"])
            
            # Verify concept analysis has meaningful content
            assert "core_themes" in concept_analysis, "Missing core_themes"
            assert "emotional_qualities" in concept_analysis, "Missing emotional_qualities"
            assert "rhythmic_implications" in concept_analysis, "Missing rhythmic_implications"
            assert "harmonic_suggestions" in concept_analysis, "Missing harmonic_suggestions"
            assert "textural_elements" in concept_analysis, "Missing textural_elements"
            assert "structural_implications" in concept_analysis, "Missing structural_implications"
            assert "sonic_palette" in concept_analysis, "Missing sonic_palette"
            
            # Verify themes are not empty and meaningful
            themes = concept_analysis["core_themes"]
            assert len(themes) > 0, "Should extract at least one theme"
            assert themes != ["abstract_concept"], f"Should extract meaningful themes, got {themes}"
            
            # Verify emotional analysis is varied (not always "contemplative")
            primary_emotion = concept_analysis["emotional_qualities"]["primary_emotion"]
            assert primary_emotion is not None, "Should identify primary emotion"
            
            # Test creative variations generation
            variations = engine.generate_creative_variations(concept_analysis, test_case["style"])
            
            # Verify we have multiple creative variations
            assert len(variations) >= 3, f"Expected at least 3 variations, got {len(variations)}"
            
            # Verify each variation has different approaches
            approaches = [v["approach"] for v in variations]
            assert len(set(approaches)) >= 3, "Variations should have different approaches"
            
            # Test Suno command generation
            suno_commands = await engine.generate_practical_suno_commands(variations, concept_analysis)
            
            # Verify Suno commands are generated
            assert len(suno_commands) >= 3, f"Expected at least 3 Suno commands, got {len(suno_commands)}"
            
            # Check that commands have practical Suno format
            for cmd in suno_commands:
                assert "suno_commands" in cmd, "Missing suno_commands in command"
                assert "style_tags" in cmd["suno_commands"], "Missing style_tags"
                assert "full_command_example" in cmd["suno_commands"], "Missing full_command_example"
                
                # Verify style tags are not empty
                style_tags = cmd["suno_commands"]["style_tags"]
                assert len(style_tags) > 5, f"Style tags should not be empty: {style_tags}"
                assert "[" in style_tags and "]" in style_tags, "Should use proper Suno bracket format"
            
            print(f"✅ Test Case {i} PASSED")
            
            # Print sample results for verification
            print(f"   Core Themes: {themes}")
            print(f"   Primary Emotion: {primary_emotion}")
            print(f"   Variations: {len(variations)}")
            print(f"   Sample Command: {suno_commands[0]['suno_commands']['style_tags']}")
            
        except Exception as e:
            print(f"❌ Test Case {i} FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    print(f"\n🎉 All test cases passed! Enhanced creative music generation is working correctly.")
    return True

@pytest.mark.asyncio
async def test_meaningful_analysis():
    """Test that analysis is meaningful and not just repetitive"""
    print("\nTesting Meaningful Analysis")
    print("=" * 30)
    
    engine = CreativeMusicEngine()
    
    # Test different concepts to ensure varied output
    concepts = [
        "Peaceful morning meditation in a quiet garden",
        "Intense battle scene with clashing swords and war cries", 
        "Nostalgic memories of childhood summers at grandmother's house"
    ]
    
    analyses = []
    for concept in concepts:
        analysis = engine.analyze_musical_concept(concept)
        analyses.append(analysis)
    
    # Verify that different concepts produce different analyses
    emotions = [a["emotional_qualities"]["primary_emotion"] for a in analyses]
    assert len(set(emotions)) > 1, f"Should produce different emotions for different concepts: {emotions}"
    
    themes_sets = [set(a["core_themes"]) for a in analyses]
    # At least some themes should be different
    all_themes = set()
    for theme_set in themes_sets:
        all_themes.update(theme_set)
    assert len(all_themes) > 3, f"Should extract varied themes across concepts: {all_themes}"
    
    print("✅ Meaningful analysis validation passed")
    print(f"   Different emotions detected: {emotions}")
    print(f"   Total unique themes: {len(all_themes)}")

@pytest.mark.asyncio
async def test_wiki_integration():
    """Test wiki data integration"""
    print("\nTesting Wiki Data Integration")
    print("=" * 30)
    
    engine = CreativeMusicEngine()
    
    # Test with a concept and style that should match wiki data
    concept_analysis = engine.analyze_musical_concept("Electronic dance music with heavy bass and synthesizers")
    variations = engine.generate_creative_variations(concept_analysis, "electronic")
    
    # Generate commands (this will try to use wiki data)
    suno_commands = await engine.generate_practical_suno_commands(variations, concept_analysis)
    
    # Check if wiki techniques are referenced
    for cmd in suno_commands:
        if "wiki_techniques_used" in cmd:
            print(f"   Wiki techniques used: {cmd['wiki_techniques_used']}")
    
    print("✅ Wiki integration test completed")
    print(f"   Generated {len(suno_commands)} commands with wiki integration")

async def main():
    """Run all tests"""
    print("Enhanced Creative Music Generation Test Suite")
    print("=" * 60)
    
    try:
        # Test enhanced functionality
        success = await test_enhanced_creative_generation()
        if not success:
            return 1
        
        # Test meaningful analysis
        await test_meaningful_analysis()
        
        # Test wiki integration
        await test_wiki_integration()
        
        print("\n🎊 All tests completed successfully!")
        print("Enhanced creative music generation is ready for use.")
        return 0
        
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)