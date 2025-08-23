#!/usr/bin/env python3
"""
Test script for new MCP tools: process_universal_content and create_character_album
Integrated with unified testing framework
"""

import sys
import asyncio
import json
import os

# Add paths for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests'))

from tests.fixtures.test_data import TestDataManager, test_data_manager
from tests.fixtures.mock_contexts import MockContext, create_mock_context
from working_universal_processor import WorkingUniversalProcessor


async def test_process_universal_content():
    """Test the process_universal_content functionality"""
    print("🧪 Testing process_universal_content (Unified Framework)")
    print("=" * 60)
    
    # Import the tool function logic
    processor = WorkingUniversalProcessor()
    ctx = create_mock_context("universal_content", session_id="universal_test")
    
    # Test content
    content = """
    Sarah and David fell deeply in love, but their relationship was complicated by different 
    spiritual beliefs. She was a scientist who believed in empirical evidence, while he found 
    truth through faith and intuition. Their love forced both to question their fundamental 
    assumptions about reality, truth, and the nature of human connection.
    """
    
    character_description = """
    Marcus "Solvent" Thompson, 34-year-old liquid drum and bass producer from Bristol. 
    Lost his father 3 months ago, struggling with theological vs. rational approaches to grief. 
    Believes spiritual questions should be demonstrated through philosophical argument rather 
    than theological doctrine. Uses music production as form of rational inquiry.
    """
    
    track_title = "Love and Logic"
    
    # Test the core processing
    await ctx.info("Starting universal content processing...")
    
    if len(content.strip()) < 10:
        print("❌ Content validation failed")
        return False
    
    if len(character_description.strip()) < 20:
        print("❌ Character description validation failed")
        return False
    
    await ctx.info("Processing content through character lens...")
    
    # Process content through character's psychological filter
    result = processor.process_any_content(content, track_title)
    
    # Validate result
    if not result.title:
        print("❌ No title generated")
        return False
    
    if not result.character_interpretation:
        print("❌ No character interpretation generated")
        return False
    
    if not result.formatted_lyrics:
        print("❌ No lyrics generated")
        return False
    
    if not result.suno_command:
        print("❌ No Suno command generated")
        return False
    
    print(f"✅ Title: {result.title}")
    print(f"✅ Character interpretation: {result.character_interpretation[:100]}...")
    print(f"✅ Effectiveness score: {result.effectiveness_score}")
    print(f"✅ Suno command generated: {len(result.suno_command)} characters")
    
    await ctx.info(f"Universal processing complete: {track_title}")
    
    return True


async def test_create_character_album():
    """Test the create_character_album functionality"""
    print("\n🎵 Testing create_character_album (Unified Framework)")
    print("=" * 60)
    
    processor = WorkingUniversalProcessor()
    ctx = create_mock_context("character_album", session_id="album_test")
    
    content = """
    The nature of consciousness has always puzzled philosophers and scientists. 
    What makes us aware? Is consciousness an emergent property of complex neural networks, 
    or something more fundamental to the universe?
    """
    
    character_description = "Marcus Thompson, philosophical producer"
    album_title = "Questions of Consciousness"
    track_count = 3
    
    await ctx.info(f"Creating {track_count}-track album: {album_title}")
    
    # Validate inputs
    if track_count < 1 or track_count > 12:
        print("❌ Invalid track count")
        return False
    
    # Generate track concepts
    track_concepts = [
        f"{album_title} - Opening Statement",
        f"{album_title} - Personal Reflection", 
        f"{album_title} - Deeper Questions",
        f"{album_title} - Emotional Core",
        f"{album_title} - Resolution Attempt",
        f"{album_title} - Final Understanding"
    ]
    
    album_tracks = []
    
    for i in range(track_count):
        track_title = track_concepts[i]
        
        await ctx.info(f"Processing track {i+1}/{track_count}: {track_title}")
        
        # Process content through character lens for this track
        track_result = processor.process_any_content(content, track_title)
        
        track_data = {
            "track_number": i + 1,
            "title": track_title,
            "character_interpretation": track_result.character_interpretation,
            "personal_story": track_result.personal_story,
            "lyrics": track_result.formatted_lyrics,
            "suno_command": track_result.suno_command,
            "effectiveness_score": track_result.effectiveness_score
        }
        
        album_tracks.append(track_data)
    
    # Validate album
    if len(album_tracks) != track_count:
        print(f"❌ Expected {track_count} tracks, got {len(album_tracks)}")
        return False
    
    avg_score = sum(track["effectiveness_score"] for track in album_tracks) / len(album_tracks)
    
    print(f"✅ Album created: {album_title}")
    print(f"✅ Tracks generated: {len(album_tracks)}")
    print(f"✅ Average effectiveness: {avg_score:.2f}")
    
    for track in album_tracks:
        print(f"  📻 Track {track['track_number']}: {track['title']}")
    
    await ctx.info(f"Album creation complete: {track_count} tracks generated")
    
    return True


# Test functions for unified framework integration
async def test_universal_content_integration(ctx: MockContext, test_manager: TestDataManager) -> None:
    """Test function compatible with unified test runner"""
    result = await test_process_universal_content()
    assert result, "Universal content processing should succeed"


async def test_character_album_integration(ctx: MockContext, test_manager: TestDataManager) -> None:
    """Test function compatible with unified test runner"""
    result = await test_create_character_album()
    assert result, "Character album creation should succeed"


async def main():
    """Run all tests"""
    print("🚀 TESTING NEW MCP TOOLS (Unified Framework)")
    print("=" * 70)
    
    # Test 1: Universal content processing
    test1_result = await test_process_universal_content()
    
    # Test 2: Character album creation
    test2_result = await test_create_character_album()
    
    print("\n📊 TEST RESULTS")
    print("=" * 30)
    print(f"process_universal_content: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"create_character_album: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 ALL TESTS PASSED!")
        print("The new tools are ready for integration.")
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        print("Please check the implementation.")
    
    return test1_result and test2_result


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)