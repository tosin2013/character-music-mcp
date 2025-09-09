#!/usr/bin/env python3
"""
Test meta tag page parsing functionality
"""

from wiki_content_parser import ContentParser


def test_metatag_parsing():
    """Test meta tag page parsing with sample HTML"""
    parser = ContentParser()

    # Sample HTML structure similar to Suno AI Wiki meta tags page
    sample_html = """
    <html>
        <head><title>List of Metatags</title></head>
        <body>
            <div class="sl-markdown-content">
                <h2>What are Meta Tags?</h2>
                <p>Meta tags in music AI are directives...</p>

                <h3>How to Use Meta Tags in Suno AI</h3>
                <p>Using meta tags can significantly enhance...</p>

                <h3>Sound Effects Meta Tags</h3>
                <ul>
                    <li><strong>Barking</strong> : Sound of a dog barking.</li>
                    <li><strong>Beeping</strong> : Beeping sound.</li>
                    <li><strong>Bell dings</strong> : Sound of a bell dinging.</li>
                    <li><strong>Birds chirping</strong> : Sound of birds chirping.</li>
                    <li><strong>Cheering</strong> : Sound of people cheering.</li>
                </ul>

                <h3>Vocal Expressions Meta Tags</h3>
                <ul>
                    <li><strong>Announcer</strong> : Voice of an announcer.</li>
                    <li><strong>Female narrator</strong> : Voice of a female narrator.</li>
                    <li><strong>Man</strong> : Voice of a man.</li>
                    <li><strong>Woman</strong> : Voice of a woman.</li>
                </ul>

                <h3>Structural Tags</h3>
                <ul>
                    <li><strong>Chorus</strong> : The chorus part of the song.</li>
                    <li><strong>Intro</strong> : Introduction part of the song.</li>
                    <li><strong>Outro</strong> : Ending part of the song.</li>
                    <li><strong>Verse</strong> : The verse sections of the song.</li>
                </ul>

                <h3>Styles and Genres Meta Tags</h3>
                <ul>
                    <li><strong>Acoustic</strong> : Acoustic style.</li>
                    <li><strong>Hip hop</strong> : Hip hop music.</li>
                    <li><strong>Jazz</strong> : Jazz music.</li>
                    <li><strong>Pop</strong> : Pop music.</li>
                    <li><strong>Rock</strong> : Rock music.</li>
                </ul>
            </div>
        </body>
    </html>
    """

    try:
        meta_tags = parser.parse_meta_tag_page(sample_html, "http://test.com/metatags")

        print(f"✓ Parsed {len(meta_tags)} meta tags")

        # Verify we got meta tags from different categories
        tag_names = [mt.tag for mt in meta_tags]

        # Check for sound effects tags
        assert "Barking" in tag_names, "Expected 'Barking' in parsed meta tags"
        assert "Beeping" in tag_names, "Expected 'Beeping' in parsed meta tags"

        # Check for vocal tags
        assert "Announcer" in tag_names, "Expected 'Announcer' in parsed meta tags"
        assert "Female narrator" in tag_names, "Expected 'Female narrator' in parsed meta tags"

        # Check for structural tags
        assert "Chorus" in tag_names, "Expected 'Chorus' in parsed meta tags"
        assert "Intro" in tag_names, "Expected 'Intro' in parsed meta tags"

        # Check for genre tags
        assert "Jazz" in tag_names, "Expected 'Jazz' in parsed meta tags"
        assert "Hip hop" in tag_names, "Expected 'Hip hop' in parsed meta tags"

        print("✓ All expected meta tags found")

        # Test meta tag object properties
        barking_tag = next((mt for mt in meta_tags if mt.tag == "Barking"), None)
        assert barking_tag is not None, "Barking meta tag not found"
        assert barking_tag.source_url == "http://test.com/metatags", "Source URL not set correctly"
        assert barking_tag.category == "sound_effects", f"Expected 'sound_effects', got '{barking_tag.category}'"
        assert "Sound of a dog barking" in barking_tag.description, "Description not parsed correctly"

        print("✓ Meta tag object properties validated")

        # Test category classification
        sound_effect_tags = [mt for mt in meta_tags if mt.category == "sound_effects"]
        vocal_tags = [mt for mt in meta_tags if mt.category == "vocal"]
        structural_tags = [mt for mt in meta_tags if mt.category == "structural"]
        genre_tags = [mt for mt in meta_tags if mt.category == "genre"]

        assert len(sound_effect_tags) >= 3, f"Expected at least 3 sound effect tags, got {len(sound_effect_tags)}"
        assert len(vocal_tags) >= 3, f"Expected at least 3 vocal tags, got {len(vocal_tags)}"
        assert len(structural_tags) >= 3, f"Expected at least 3 structural tags, got {len(structural_tags)}"
        assert len(genre_tags) >= 3, f"Expected at least 3 genre tags, got {len(genre_tags)}"

        print("✓ Category classification working")

        # Test compatible genres inference
        jazz_tag = next((mt for mt in meta_tags if mt.tag == "Jazz"), None)
        assert jazz_tag is not None, "Jazz meta tag not found"
        assert len(jazz_tag.compatible_genres) > 0, "Expected compatible genres for Jazz tag"
        assert "jazz" in jazz_tag.compatible_genres, "Expected 'jazz' in compatible genres"

        print("✓ Compatible genres inference working")

        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_metatag_item_parsing():
    """Test individual meta tag item parsing"""
    parser = ContentParser()

    # Test meta tag with description
    tag, desc, examples = parser._parse_meta_tag_item("**Barking** : Sound of a dog barking.")
    assert tag == "Barking", f"Expected 'Barking', got '{tag}'"
    assert "Sound of a dog barking" in desc, f"Expected description about barking, got '{desc}'"

    # Test meta tag without description
    tag, desc, examples = parser._parse_meta_tag_item("**Chorus**")
    assert tag == "Chorus", f"Expected 'Chorus', got '{tag}'"
    assert desc == "", f"Expected empty description, got '{desc}'"

    # Test meta tag with complex description
    tag, desc, examples = parser._parse_meta_tag_item("**Acoustic** : Acoustic style.")
    assert tag == "Acoustic", f"Expected 'Acoustic', got '{tag}'"
    assert "Acoustic style" in desc, f"Expected description about acoustic, got '{desc}'"

    print("✓ Meta tag item parsing tests passed")
    return True

def test_category_classification():
    """Test meta tag category classification"""
    parser = ContentParser()

    # Test sound effects
    category = parser._categorize_meta_tag("Sound Effects Meta Tags", "Barking")
    assert category == "sound_effects", f"Expected 'sound_effects', got '{category}'"

    # Test vocal
    category = parser._categorize_meta_tag("Vocal Expressions Meta Tags", "Announcer")
    assert category == "vocal", f"Expected 'vocal', got '{category}'"

    # Test structural
    category = parser._categorize_meta_tag("Structural Tags", "Chorus")
    assert category == "structural", f"Expected 'structural', got '{category}'"

    # Test genre
    category = parser._categorize_meta_tag("Styles and Genres Meta Tags", "Jazz")
    assert category == "genre", f"Expected 'genre', got '{category}'"

    print("✓ Category classification tests passed")
    return True

if __name__ == "__main__":
    print("Testing meta tag page parsing functionality...")

    success = True
    success &= test_metatag_item_parsing()
    success &= test_category_classification()
    success &= test_metatag_parsing()

    if success:
        print("\n✓ All meta tag parsing tests passed!")
    else:
        print("\n✗ Some tests failed!")
        exit(1)
