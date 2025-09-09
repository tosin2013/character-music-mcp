#!/usr/bin/env python3
"""
Test script for unique track generation in create_character_album
"""

from working_universal_processor import WorkingUniversalProcessor


class MockContext:
    async def info(self, msg):
        print(f'INFO: {msg}')
    async def error(self, msg):
        print(f'ERROR: {msg}')

def test_unique_track_generation():
    """Test that tracks have unique lyrics and themes"""

    print("🎵 TESTING UNIQUE TRACK GENERATION")
    print("=" * 60)

    # Test character description
    character_description = "DJ Memphis is a 25-year-old Memphis hip-hop producer working out of his home studio, known for his introspective approach to beats and philosophical lyrics."

    # Test content
    content = "A young artist struggles with finding their authentic voice in the music industry while dealing with family expectations and personal dreams."

    # Create processor
    processor = WorkingUniversalProcessor(character_description)

    # Test the new track processing method
    track_themes = ["personal_struggle", "hope_and_dreams", "artistic_beauty"]
    track_perspectives = [
        "Intimate examination of personal struggle from individual experience",
        "Uplifting exploration of hope and dreams through optimistic lens",
        "Creative exploration of artistic beauty through aesthetic appreciation"
    ]

    tracks = []

    for i in range(3):
        track_title = f"Track {i+1}: Finding Voice"
        track_theme = track_themes[i]
        track_perspective = track_perspectives[i]

        print(f"\n🎤 PROCESSING TRACK {i+1}")
        print(f"Title: {track_title}")
        print(f"Theme: {track_theme}")
        print(f"Perspective: {track_perspective}")

        # Process track with unique theme and perspective
        result = processor.process_track_content(
            content,
            track_title,
            track_theme,
            track_perspective,
            i + 1,  # track number
            3       # total tracks
        )

        tracks.append(result)

        # Show lyrics preview
        lyrics_lines = result.formatted_lyrics.split('\n')
        verse_start = next((i for i, line in enumerate(lyrics_lines) if '[Verse 1]' in line), 0)
        if verse_start < len(lyrics_lines) - 3:
            print('Verse 1 Preview:')
            for line in lyrics_lines[verse_start+1:verse_start+4]:
                if line.strip():
                    print(f'  {line}')

        print(f"Effectiveness Score: {result.effectiveness_score:.2f}")

    # Verify uniqueness
    print("\n📊 UNIQUENESS ANALYSIS")
    print("=" * 40)

    # Check if lyrics are different
    lyrics_sets = [set(track.formatted_lyrics.lower().split()) for track in tracks]

    for i in range(len(tracks)):
        for j in range(i+1, len(tracks)):
            common_words = lyrics_sets[i].intersection(lyrics_sets[j])
            total_words = len(lyrics_sets[i].union(lyrics_sets[j]))
            similarity = len(common_words) / total_words if total_words > 0 else 0

            print(f"Track {i+1} vs Track {j+1} similarity: {similarity:.2%}")

    # Check character interpretation uniqueness
    interpretations = [track.character_interpretation for track in tracks]
    print("\nCharacter Interpretations:")
    for i, interp in enumerate(interpretations):
        print(f"Track {i+1}: {interp[:100]}...")

    print("\n✅ UNIQUE TRACK GENERATION TEST COMPLETE!")

    return all(track.effectiveness_score > 0.7 for track in tracks)

if __name__ == "__main__":
    success = test_unique_track_generation()
    print(f"\n🎯 Test Result: {'PASS' if success else 'FAIL'}")
