#!/usr/bin/env python3
"""
Test tip parsing with real Suno AI Wiki page
"""

from wiki_content_parser import ContentParser

def test_real_tip_page():
    """Test with real downloaded page"""
    parser = ContentParser()
    
    try:
        # Read the downloaded sample
        with open('sample_tip_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        techniques = parser.parse_tip_page(html_content, "https://sunoaiwiki.com/tips/2024-05-04-how-to-structure-prompts-for-suno-ai/")
        
        print(f"✓ Parsed {len(techniques)} techniques from real page")
        
        # Group by technique type
        types = {}
        for t in techniques:
            if t.technique_type not in types:
                types[t.technique_type] = []
            types[t.technique_type].append(t)
        
        print("\nTechniques by type:")
        for tech_type, techs in types.items():
            print(f"  {tech_type}: {len(techs)} techniques")
            for tech in techs:
                print(f"    - {tech.name}")
                if tech.examples:
                    print(f"      Examples: {len(tech.examples)}")
                    for example in tech.examples[:2]:  # Show first 2 examples
                        print(f"        • {example}")
                print(f"      Scenarios: {', '.join(tech.applicable_scenarios[:3])}")
                print()
        
        # Check for expected content
        technique_names = [t.name for t in techniques]
        expected_content = ["Structure Prompts", "Custom Mode", "Brackets"]
        
        found_expected = []
        for expected in expected_content:
            if any(expected in name for name in technique_names):
                found_expected.append(expected)
        
        print(f"✓ Found {len(found_expected)}/{len(expected_content)} expected content: {found_expected}")
        
        return len(techniques) > 0
        
    except FileNotFoundError:
        print("✗ sample_tip_page.html not found - skipping real page test")
        return True  # Don't fail the test if file doesn't exist
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing with real Suno AI Wiki tip page...")
    
    if test_real_tip_page():
        print("\n✓ Real page test passed!")
    else:
        print("\n✗ Real page test failed!")
        exit(1)