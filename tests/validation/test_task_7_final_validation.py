#!/usr/bin/env python3
"""
Final validation test for Task 7: Fix create_character_album tool for unique track generation
"""

import sys
import asyncio
import json
from working_universal_processor import WorkingUniversalProcessor
from server import _generate_unique_track_concepts, _extract_character_name, _extract_character_genre

def test_requirement_6_1_unique_lyrics():
    """Test Requirement 6.1: Each track SHALL have unique lyrics and content"""
    
    print("📝 TESTING REQUIREMENT 6.1: UNIQUE LYRICS FOR EACH TRACK")
    print("=" * 60)
    
    character_description = "Maya Chen is a 27-year-old indie folk singer from Portland, known for her introspective songwriting and acoustic guitar work."
    content = "A musician's journey of self-discovery through travel and meeting different people."
    
    processor = WorkingUniversalProcessor(character_description)
    
    # Generate 3 tracks
    tracks = []
    themes = ["personal_struggle", "hope_and_dreams", "artistic_beauty"]
    perspectives = [
        "Intimate examination of personal struggle",
        "Uplifting exploration of hope and dreams", 
        "Creative exploration of artistic beauty"
    ]
    
    for i in range(3):
        result = processor.process_track_content(
            content, f"Track {i+1}", themes[i], perspectives[i], i+1, 3
        )
        tracks.append(result)
    
    # Check lyrics uniqueness
    lyrics_sets = [set(track.formatted_lyrics.lower().split()) for track in tracks]
    
    print("Lyrics Uniqueness Analysis:")
    unique_tracks = 0
    for i in range(len(tracks)):
        for j in range(i+1, len(tracks)):
            common_words = lyrics_sets[i].intersection(lyrics_sets[j])
            total_words = len(lyrics_sets[i].union(lyrics_sets[j]))
            similarity = len(common_words) / total_words if total_words > 0 else 0
            
            print(f"  Track {i+1} vs Track {j+1} similarity: {similarity:.1%}")
            if similarity < 0.5:  # Less than 50% similarity means unique
                unique_tracks += 1
    
    requirement_6_1_pass = unique_tracks >= 2  # At least 2 pairs should be unique
    print(f"✅ Requirement 6.1: {'PASS' if requirement_6_1_pass else 'FAIL'} - Tracks have unique lyrics")
    
    return requirement_6_1_pass

def test_requirement_6_2_character_reflection():
    """Test Requirement 6.2: Album SHALL reflect the specified character, not hardcoded personas"""
    
    print(f"\n👤 TESTING REQUIREMENT 6.2: CHARACTER REFLECTION")
    print("=" * 60)
    
    # Test with very specific character
    character_description = "Kenji Nakamura is a 29-year-old Japanese jazz fusion guitarist from Tokyo, known for his technical precision and minimalist approach."
    content = "The beauty of simplicity in complex musical arrangements."
    
    processor = WorkingUniversalProcessor(character_description)
    
    result = processor.process_track_content(
        content, "Minimalist Complexity", "artistic_beauty", 
        "Technical exploration of artistic beauty", 1, 1
    )
    
    # Check for character-specific content
    full_output = f"{result.character_interpretation} {result.personal_story} {result.formatted_lyrics} {result.suno_command}".lower()
    
    character_terms = ["kenji", "nakamura", "japanese", "jazz fusion", "tokyo", "technical", "minimalist"]
    hardcoded_terms = ["marcus", "bristol", "warehouse", "liquid dnb"]
    
    character_found = sum(1 for term in character_terms if term in full_output)
    hardcoded_found = sum(1 for term in hardcoded_terms if term in full_output)
    
    print(f"Character-specific terms found: {character_found}/{len(character_terms)}")
    print(f"Hardcoded terms found: {hardcoded_found}/{len(hardcoded_terms)}")
    
    requirement_6_2_pass = character_found >= 3 and hardcoded_found == 0
    print(f"✅ Requirement 6.2: {'PASS' if requirement_6_2_pass else 'FAIL'} - Character reflected, no hardcoded personas")
    
    return requirement_6_2_pass

def test_requirement_6_3_genre_matching():
    """Test Requirement 6.3: Music SHALL match the requested genre"""
    
    print(f"\n🎵 TESTING REQUIREMENT 6.3: GENRE MATCHING")
    print("=" * 60)
    
    test_cases = [
        {
            "description": "Rico Martinez is a 26-year-old reggaeton producer from San Juan, known for his heavy bass lines and party anthems.",
            "expected_genre": "reggaeton"
        },
        {
            "description": "Emma Thompson is a 24-year-old neo-soul singer from Detroit, known for her powerful vocals and R&B influences.",
            "expected_genre": "neo-soul"
        }
    ]
    
    genre_matches = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        
        # Test extraction
        extracted_genre = _extract_character_genre(test_case['description'])
        print(f"  Expected: {test_case['expected_genre']}")
        print(f"  Extracted: {extracted_genre}")
        
        # Test processor
        processor = WorkingUniversalProcessor(test_case['description'])
        character_genre = processor.character_worldview['context']['genre']
        print(f"  Processor: {character_genre}")
        
        # Test in output
        result = processor.process_track_content(
            "Music industry challenges", "Genre Test", "personal_struggle",
            "Genre-specific exploration", 1, 1
        )
        
        genre_in_output = test_case['expected_genre'] in result.suno_command.lower()
        print(f"  In Suno Command: {'✅' if genre_in_output else '❌'}")
        
        if extracted_genre == test_case['expected_genre'] and genre_in_output:
            genre_matches += 1
    
    requirement_6_3_pass = genre_matches == len(test_cases)
    print(f"\n✅ Requirement 6.3: {'PASS' if requirement_6_3_pass else 'FAIL'} - Genres match specifications")
    
    return requirement_6_3_pass

def test_requirement_6_4_consistent_character_usage():
    """Test Requirement 6.4: Character description SHALL be used throughout, not ignored"""
    
    print(f"\n🔄 TESTING REQUIREMENT 6.4: CONSISTENT CHARACTER USAGE")
    print("=" * 60)
    
    character_description = "Zara Ahmed is a 25-year-old Afrobeat drummer from Lagos, known for her polyrhythmic patterns and cultural fusion approach."
    content = "Celebrating cultural heritage through modern music."
    
    processor = WorkingUniversalProcessor(character_description)
    
    # Generate multiple tracks to test consistency
    tracks = []
    for i in range(3):
        result = processor.process_track_content(
            content, f"Heritage Track {i+1}", "artistic_beauty",
            f"Cultural exploration perspective {i+1}", i+1, 3
        )
        tracks.append(result)
    
    # Check character consistency across tracks
    character_terms = ["zara", "ahmed", "afrobeat", "lagos", "polyrhythmic", "cultural"]
    
    consistent_usage = 0
    for i, track in enumerate(tracks, 1):
        full_output = f"{track.character_interpretation} {track.personal_story} {track.suno_command}".lower()
        terms_found = sum(1 for term in character_terms if term in full_output)
        
        print(f"Track {i}: {terms_found}/{len(character_terms)} character terms found")
        if terms_found >= 3:  # At least half the character terms should appear
            consistent_usage += 1
    
    requirement_6_4_pass = consistent_usage == len(tracks)
    print(f"\n✅ Requirement 6.4: {'PASS' if requirement_6_4_pass else 'FAIL'} - Character used consistently throughout")
    
    return requirement_6_4_pass

def main():
    """Run all requirement tests"""
    
    print("🎯 TASK 7 FINAL VALIDATION: CREATE_CHARACTER_ALBUM TOOL")
    print("=" * 80)
    
    # Test all requirements
    req_6_1 = test_requirement_6_1_unique_lyrics()
    req_6_2 = test_requirement_6_2_character_reflection()
    req_6_3 = test_requirement_6_3_genre_matching()
    req_6_4 = test_requirement_6_4_consistent_character_usage()
    
    # Overall assessment
    all_passed = all([req_6_1, req_6_2, req_6_3, req_6_4])
    
    print(f"\n📊 FINAL ASSESSMENT")
    print("=" * 40)
    print(f"Requirement 6.1 (Unique Lyrics): {'✅ PASS' if req_6_1 else '❌ FAIL'}")
    print(f"Requirement 6.2 (Character Reflection): {'✅ PASS' if req_6_2 else '❌ FAIL'}")
    print(f"Requirement 6.3 (Genre Matching): {'✅ PASS' if req_6_3 else '❌ FAIL'}")
    print(f"Requirement 6.4 (Consistent Usage): {'✅ PASS' if req_6_4 else '❌ FAIL'}")
    
    print(f"\n🎯 TASK 7 OVERALL RESULT: {'✅ SUCCESS' if all_passed else '❌ FAILURE'}")
    
    if all_passed:
        print("\n🎉 All requirements met! The create_character_album tool now:")
        print("   • Generates unique lyrics for each track")
        print("   • Respects character specifications instead of using hardcoded personas")
        print("   • Matches requested genres accurately")
        print("   • Uses character descriptions consistently throughout")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)