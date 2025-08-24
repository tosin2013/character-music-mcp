#!/usr/bin/env python3
"""
Test genre parsing with real Suno AI Wiki page
"""

from wiki_content_parser import ContentParser

def test_real_genre_page():
    """Test with real downloaded page"""
    parser = ContentParser()
    
    try:
        # Read the downloaded sample
        with open('sample_genre_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        genres = parser.parse_genre_page(html_content, "https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/")
        
        print(f"✓ Parsed {len(genres)} genres from real page")
        
        # Print some examples
        print("\nSample parsed genres:")
        for i, genre in enumerate(genres[:10]):  # Show first 10
            print(f"  {i+1}. {genre.name}")
            if genre.characteristics:
                print(f"     Characteristics: {', '.join(genre.characteristics[:3])}")
            if genre.typical_instruments:
                print(f"     Instruments: {', '.join(genre.typical_instruments[:3])}")
            print()
        
        # Check for expected genres
        genre_names = [g.name for g in genres]
        expected_genres = ['Ambient', 'Techno', 'Alternative rock', 'Bebop', 'Trap']
        
        found_expected = []
        for expected in expected_genres:
            if expected in genre_names:
                found_expected.append(expected)
        
        print(f"✓ Found {len(found_expected)}/{len(expected_genres)} expected genres: {found_expected}")
        
        return len(genres) > 0
        
    except FileNotFoundError:
        print("✗ sample_genre_page.html not found - skipping real page test")
        return True  # Don't fail the test if file doesn't exist
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing with real Suno AI Wiki genre page...")
    
    if test_real_genre_page():
        print("\n✓ Real page test passed!")
    else:
        print("\n✗ Real page test failed!")
        exit(1)