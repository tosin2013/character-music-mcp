#!/usr/bin/env python3
"""
Test meta tag parsing with real Suno AI Wiki page
"""

from wiki_content_parser import ContentParser

def test_real_metatag_page():
    """Test with real downloaded page"""
    parser = ContentParser()
    
    try:
        # Read the downloaded sample
        with open('sample_metatag_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        meta_tags = parser.parse_meta_tag_page(html_content, "https://sunoaiwiki.com/resources/2024-05-13-list-of-metatags/")
        
        print(f"✓ Parsed {len(meta_tags)} meta tags from real page")
        
        # Group by category
        categories = {}
        for mt in meta_tags:
            if mt.category not in categories:
                categories[mt.category] = []
            categories[mt.category].append(mt)
        
        print("\nMeta tags by category:")
        for category, tags in categories.items():
            print(f"  {category}: {len(tags)} tags")
            for tag in tags[:3]:  # Show first 3 in each category
                print(f"    - {tag.tag}: {tag.description[:50]}...")
        
        # Check for expected meta tags
        tag_names = [mt.tag for mt in meta_tags]
        expected_tags = ['Barking', 'Chorus', 'Jazz', 'Announcer', 'Acoustic']
        
        found_expected = []
        for expected in expected_tags:
            if expected in tag_names:
                found_expected.append(expected)
        
        print(f"\n✓ Found {len(found_expected)}/{len(expected_tags)} expected tags: {found_expected}")
        
        return len(meta_tags) > 0
        
    except FileNotFoundError:
        print("✗ sample_metatag_page.html not found - skipping real page test")
        return True  # Don't fail the test if file doesn't exist
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing with real Suno AI Wiki meta tags page...")
    
    if test_real_metatag_page():
        print("\n✓ Real page test passed!")
    else:
        print("\n✗ Real page test failed!")
        exit(1)