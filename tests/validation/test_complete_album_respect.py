#!/usr/bin/env python3
"""
Test complete album creation to verify character and genre respect
"""

import sys
import asyncio
import json
from working_universal_processor import WorkingUniversalProcessor
from server import _generate_unique_track_concepts, _extract_character_name, _extract_character_genre

class MockContext:
    async def info(self, msg): 
        print(f'INFO: {msg}')
    async def error(self, msg): 
        print(f'ERROR: {msg}')

def test_complete_album_character_respect():
    """Test complete album creation with different characters"""
    
    print("🎵 TESTING COMPLETE ALBUM CHARACTER RESPECT")
    print("=" * 60)
    
    # Test case: Reggaeton artist (very different from any hardcoded content)
    character_description = "Carlos Rivera is a 24-year-old reggaeton producer from Puerto Rico, known for his innovative trap-reggaeton fusion and socially conscious lyrics about island life."
    content = "The struggles of island youth trying to make it in the music industry while staying true to their cultural roots."
    album_title = "Isla Dreams"
    
    print(f"Character: {character_description}")
    print(f"Content: {content}")
    print(f"Album: {album_title}")
    
    # Test character extraction
    character_name = _extract_character_name(character_description)
    character_genre = _extract_character_genre(character_description)
    
    print(f"\nExtracted Name: {character_name}")
    print(f"Extracted Genre: {character_genre}")
    
    # Test track concept generation
    track_concepts = _generate_unique_track_concepts(content, album_title, character_description, 3)
    
    print(f"\nGenerated Track Concepts:")
    for i, concept in enumerate(track_concepts, 1):
        print(f"  Track {i}: {concept['title']}")
        print(f"    Theme: {concept['theme']}")
        print(f"    Perspective: {concept['perspective'][:80]}...")
    
    # Test processor with this character
    processor = WorkingUniversalProcessor(character_description)
    
    print(f"\nProcessor Character Analysis:")
    character = processor.character_worldview
    print(f"  Name: {character['name']}")
    print(f"  Genre: {character['context']['genre']}")
    print(f"  Location: {character['context']['location']}")
    print(f"  Filter: {character['filter']}")
    
    # Test track processing
    track_result = processor.process_track_content(
        content,
        track_concepts[0]['title'],
        track_concepts[0]['theme'],
        track_concepts[0]['perspective'],
        1, 3
    )
    
    print(f"\nTrack Processing Results:")
    print(f"  Title: {track_result.title}")
    print(f"  Character Interpretation: {track_result.character_interpretation[:150]}...")
    
    # Check Suno command for character-specific content
    suno_lines = track_result.suno_command.split('\n')[:8]
    print(f"\nSuno Command (first 8 lines):")
    for line in suno_lines:
        if line.strip():
            print(f"  {line}")
    
    # Verify no hardcoded content
    full_output = f"{track_result.character_interpretation} {track_result.personal_story} {track_result.formatted_lyrics} {track_result.suno_command}".lower()
    
    hardcoded_terms = ["marcus", "bristol", "warehouse", "liquid dnb", "philosophical"]
    character_terms = ["carlos", "rivera", "puerto rico", "reggaeton", "island"]
    
    print(f"\nHardcoded Content Check:")
    hardcoded_found = False
    for term in hardcoded_terms:
        found = term in full_output
        if found:
            hardcoded_found = True
        print(f"  '{term}': {'❌ FOUND (BAD)' if found else '✅ NOT FOUND (GOOD)'}")
    
    print(f"\nCharacter-Specific Content Check:")
    character_found = 0
    for term in character_terms:
        found = term in full_output
        if found:
            character_found += 1
        print(f"  '{term}': {'✅ FOUND (GOOD)' if found else '❌ NOT FOUND (BAD)'}")
    
    # Overall assessment
    print(f"\n📊 ASSESSMENT:")
    print(f"  Character Name Extracted: {'✅ PASS' if character_name == 'Carlos Rivera' else '❌ FAIL'}")
    print(f"  Genre Detected: {'✅ PASS' if 'reggaeton' in character_genre else '❌ FAIL'}")
    print(f"  No Hardcoded Content: {'✅ PASS' if not hardcoded_found else '❌ FAIL'}")
    print(f"  Character Content Present: {'✅ PASS' if character_found >= 2 else '❌ FAIL'}")
    
    return not hardcoded_found and character_found >= 2

if __name__ == "__main__":
    success = test_complete_album_character_respect()
    print(f"\n🎯 Overall Test Result: {'✅ PASS' if success else '❌ FAIL'}")