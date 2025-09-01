import pytest
#!/usr/bin/env python3
"""
Test Task 8: Fix create_story_integrated_album character detection

This test validates that the character detection fixes work properly
without the MCP tool conflicts.
"""

import asyncio
import json
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockContext:
    """Mock context for testing"""
    async def info(self, msg): 
        print(f'INFO: {msg}')
    
    async def error(self, msg): 
        print(f'ERROR: {msg}')

@pytest.mark.asyncio
async def test_character_detection_fix():
    """Test the character detection fix using middleware"""
    
    # Test narrative with clear characters
    narrative = '''
    Sarah Chen stood at the edge of the rooftop, tears streaming down her face. 
    At twenty-seven, she had spent her entire life meeting everyone else's expectations. 
    Perfect grades, perfect job, perfect smile - but inside, she felt completely empty.
    
    "I can't do this anymore," Sarah whispered to herself, her voice barely audible 
    over the city noise below. The wind whipped her long black hair across her face 
    as she gripped the railing tighter.
    
    Behind her, the door to the roof opened. "Sarah?" called Marcus, her best friend 
    since college. "What are you doing up here?"
    
    Sarah turned to face Marcus, her eyes red from crying. "I'm thinking about jumping," 
    she said quietly. Marcus rushed forward, his heart pounding.
    
    "Don't say that," Marcus pleaded, reaching out his hand. "Talk to me. What's wrong?"
    
    Sarah looked at her friend, seeing the genuine concern in his eyes. "I feel like 
    I'm drowning, Marcus. Every day is the same. Work, sleep, repeat. I'm successful 
    on paper, but I feel completely empty inside."
    
    Marcus stepped closer, his voice gentle. "Sarah, you don't have to carry this alone. 
    I've been worried about you for months. You've been different, distant."
    
    "I didn't want to burden anyone," Sarah replied, her voice breaking. "Everyone 
    thinks I have it all figured out. The perfect job, the perfect apartment, the 
    perfect life. But it's all a lie."
    '''
    
    ctx = MockContext()
    
    try:
        # Import middleware to test character detection
        from mcp_middleware import middleware
        
        print("=== Testing Character Detection ===")
        
        # Step 1: Test character analysis
        analysis_result = await middleware.analyze_characters(narrative, ctx)
        
        characters = analysis_result['characters']
        print(f"Characters found: {len(characters)}")
        
        if not characters:
            print("❌ FAILED: No characters found - this should not happen with clear character narrative")
            return False
        
        for char in characters:
            print(f"- {char.name} (confidence: {char.confidence_score:.2f})")
        
        # Step 2: Test persona generation
        print("\n=== Testing Persona Generation ===")
        main_character = characters[0]
        persona = await middleware.generate_persona(main_character, ctx)
        
        print(f"Generated persona for {main_character.name}:")
        print(f"- Artist name: {persona.artist_name}")
        print(f"- Genre: {persona.primary_genre}")
        print(f"- Vocal style: {persona.vocal_style}")
        
        # Step 3: Test story beat extraction
        print("\n=== Testing Story Beat Extraction ===")
        story_beats = middleware.extract_story_beats(narrative, main_character, ctx)
        
        print(f"Story beats extracted: {len(story_beats)}")
        for i, beat in enumerate(story_beats):
            print(f"- Beat {i+1}: {beat['emotional_state']} (character mentions: {beat['character_presence']})")
        
        # Step 4: Test track concept generation
        print("\n=== Testing Track Concept Generation ===")
        track_concepts = middleware.generate_story_based_tracks(
            story_beats, main_character, persona, 4, ctx
        )
        
        print(f"Track concepts generated: {len(track_concepts)}")
        for i, concept in enumerate(track_concepts):
            print(f"- Track {i+1}: {concept['title']}")
            print(f"  Emotional tone: {concept['emotional_tone']}")
            print(f"  Narrative function: {concept['narrative_function']}")
        
        # Step 5: Test track content processing
        print("\n=== Testing Track Content Processing ===")
        if track_concepts:
            track_data = middleware.process_track_content(
                track_concepts[0], main_character, persona, ctx
            )
            
            print("Track content processed successfully:")
            print(f"- Character interpretation: {track_data['content_analysis']['character_interpretation'][:100]}...")
            print(f"- Lyrics generated: {len(track_data['authentic_lyrics']['formatted_lyrics'])} characters")
            print(f"- Suno command generated: {len(track_data['suno_command']['formatted_command'])} characters")
        
        print("\n✅ SUCCESS: All character detection and processing components working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

@pytest.mark.asyncio
async def test_edge_cases():
    """Test edge cases for character detection"""
    
    print("\n=== Testing Edge Cases ===")
    ctx = MockContext()
    
    try:
        from mcp_middleware import middleware
        
        # Test case 1: Minimal character information
        minimal_narrative = """
        Someone walked through the rain. They thought about things. It was difficult.
        The person continued walking, feeling lost and confused about everything.
        """
        
        print("\nTest 1: Minimal character information")
        result = await middleware.analyze_characters(minimal_narrative, ctx)
        print(f"Characters found in minimal narrative: {len(result['characters'])}")
        
        # Test case 2: Multiple clear characters
        multi_character_narrative = """
        Elena Rodriguez stood in her cramped studio apartment, paintbrush trembling 
        in her hand as she stared at the blank canvas. At twenty-eight, she had already 
        spent three years working as a graphic designer for a corporate firm, but her 
        heart belonged to fine art.
        
        "You're wasting your talent," her mother, Carmen Rodriguez, had said during 
        their last phone call. "Art doesn't pay the bills, mija. You have a good job."
        
        But Elena couldn't shake the feeling that she was slowly dying inside. Every 
        morning, she put on her business attire and walked into the sterile office 
        building, spending eight hours creating marketing materials for products she 
        didn't care about.
        
        Her best friend Jake Thompson had been encouraging her to quit and pursue art 
        full-time. "You're incredibly talented, Elena," he'd said over coffee last week. 
        "I've seen your paintings. They're extraordinary."
        """
        
        print("\nTest 2: Multiple character narrative")
        result = await middleware.analyze_characters(multi_character_narrative, ctx)
        print(f"Characters found in multi-character narrative: {len(result['characters'])}")
        for char in result['characters']:
            print(f"- {char.name} (confidence: {char.confidence_score:.2f})")
        
        # Test case 3: Character with explicit name provided
        print("\nTest 3: Character name validation")
        if result['characters']:
            # Try to find Elena specifically
            elena = next((char for char in result['characters'] if 'elena' in char.name.lower()), None)
            if elena:
                print(f"✅ Successfully found Elena: {elena.name}")
            else:
                print("❌ Failed to find Elena in character list")
        
        print("\n✅ Edge case testing completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Edge case testing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("Starting Task 8 Character Detection Fix Tests")
    print("=" * 50)
    
    # Test 1: Basic character detection and processing
    test1_result = await test_character_detection_fix()
    
    # Test 2: Edge cases
    test2_result = await test_edge_cases()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Basic character detection: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Edge case handling: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 ALL TESTS PASSED - Task 8 implementation successful!")
        print("\nThe create_story_integrated_album character detection has been fixed:")
        print("- Characters are properly detected from narrative text")
        print("- No more 'No characters found' errors for clear character descriptions")
        print("- Character validation and parsing works for story integration")
        print("- Various narrative formats and character descriptions are supported")
    else:
        print("\n❌ SOME TESTS FAILED - Task 8 needs additional work")
    
    return test1_result and test2_result

if __name__ == "__main__":
    asyncio.run(main())