#!/usr/bin/env python3
"""
Test genre page parsing functionality
"""

from wiki_content_parser import ContentParser


def test_genre_parsing():
    """Test genre page parsing with sample HTML"""
    parser = ContentParser()

    # Sample HTML structure similar to Suno AI Wiki
    sample_html = """
    <html>
        <head><title>List of Music Genres and Styles</title></head>
        <body>
            <div class="sl-markdown-content">
                <p>Here's a categorized selection of music genres and styles:</p>

                <h3 id="electronic">Electronic</h3>
                <ul>
                    <li>Ambient</li>
                    <li>Breakbeat</li>
                    <li>Disco</li>
                    <li>Drum and bass</li>
                    <li>House music</li>
                    <li>Techno</li>
                    <li>Trance music</li>
                </ul>

                <h3 id="rock">Rock</h3>
                <ul>
                    <li>Alternative rock</li>
                    <li>Classic rock</li>
                    <li>Hard rock</li>
                    <li>Indie rock</li>
                    <li>Punk rock</li>
                </ul>

                <h3 id="jazz">Jazz</h3>
                <ul>
                    <li>Bebop</li>
                    <li>Big band</li>
                    <li>Cool jazz</li>
                    <li>Jazz fusion</li>
                    <li>Smooth jazz</li>
                </ul>

                <h3 id="regional-music">Regional Music</h3>
                <ul>
                    <li>Brazilian music (e.g., Samba, Bossa nova)</li>
                    <li>Caribbean music (e.g., Reggae, Dancehall)</li>
                    <li>African music (e.g., Afrobeat, Highlife)</li>
                </ul>
            </div>
        </body>
    </html>
    """

    try:
        genres = parser.parse_genre_page(sample_html, "http://test.com/genres")

        print(f"✓ Parsed {len(genres)} genres")

        # Verify we got genres from different categories
        genre_names = [g.name for g in genres]

        # Check for electronic genres
        assert "Ambient" in genre_names, "Expected 'Ambient' in parsed genres"
        assert "Techno" in genre_names, "Expected 'Techno' in parsed genres"

        # Check for rock genres
        assert "Alternative rock" in genre_names, "Expected 'Alternative rock' in parsed genres"
        assert "Hard rock" in genre_names, "Expected 'Hard rock' in parsed genres"

        # Check for jazz genres
        assert "Bebop" in genre_names, "Expected 'Bebop' in parsed genres"
        assert "Jazz fusion" in genre_names, "Expected 'Jazz fusion' in parsed genres"

        # Check for regional music with descriptions
        regional_genres = [g for g in genres if "Brazilian music" in g.name or "Caribbean music" in g.name]
        assert len(regional_genres) >= 2, "Expected at least 2 regional music genres"

        print("✓ All expected genres found")

        # Test genre object properties
        ambient_genre = next((g for g in genres if g.name == "Ambient"), None)
        assert ambient_genre is not None, "Ambient genre not found"
        assert ambient_genre.source_url == "http://test.com/genres", "Source URL not set correctly"
        assert len(ambient_genre.characteristics) > 0, "Expected characteristics for Ambient genre"
        assert len(ambient_genre.typical_instruments) > 0, "Expected instruments for Ambient genre"
        assert len(ambient_genre.mood_associations) > 0, "Expected moods for Ambient genre"

        print("✓ Genre object properties validated")

        # Test characteristics inference
        electronic_genres = [g for g in genres if any(char in g.characteristics for char in ['synthesized sounds', 'electronic instruments'])]
        assert len(electronic_genres) > 0, "Expected electronic characteristics in electronic genres"

        rock_genres = [g for g in genres if any(char in g.characteristics for char in ['guitar-driven', 'amplified instruments'])]
        assert len(rock_genres) > 0, "Expected rock characteristics in rock genres"

        print("✓ Characteristics inference working")

        # Test instruments inference
        jazz_genres = [g for g in genres if 'saxophone' in g.typical_instruments or 'piano' in g.typical_instruments]
        assert len(jazz_genres) > 0, "Expected jazz instruments in jazz genres"

        print("✓ Instruments inference working")

        # Test mood inference
        ambient_moods = ambient_genre.mood_associations
        assert any(mood in ambient_moods for mood in ['atmospheric', 'meditative']), "Expected ambient-specific moods"

        print("✓ Mood inference working")

        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_genre_item_parsing():
    """Test individual genre item parsing"""
    parser = ContentParser()

    # Test simple genre name
    name, desc = parser._parse_genre_item("Ambient")
    assert name == "Ambient", f"Expected 'Ambient', got '{name}'"
    assert desc == "", f"Expected empty description, got '{desc}'"

    # Test genre with description
    name, desc = parser._parse_genre_item("Brazilian music (e.g., Samba, Bossa nova)")
    assert name == "Brazilian music", f"Expected 'Brazilian music', got '{name}'"
    assert "Samba, Bossa nova" in desc, f"Expected Samba and Bossa nova in description, got '{desc}'"

    # Test genre with parenthetical description
    name, desc = parser._parse_genre_item("Elevator music (muzak)")
    assert name == "Elevator music", f"Expected 'Elevator music', got '{name}'"
    assert desc == "muzak", f"Expected 'muzak', got '{desc}'"

    print("✓ Genre item parsing tests passed")
    return True

if __name__ == "__main__":
    print("Testing genre page parsing functionality...")

    success = True
    success &= test_genre_item_parsing()
    success &= test_genre_parsing()

    if success:
        print("\n✓ All genre parsing tests passed!")
    else:
        print("\n✗ Some tests failed!")
        exit(1)
