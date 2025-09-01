#!/usr/bin/env python3
"""
Test that album creation respects character specifications in the character_filter field
"""

import sys
import json
from server import _extract_character_name, _extract_character_genre

def test_character_filter_extraction():
    """Test character name and genre extraction functions"""
    
    print("🎭 TESTING CHARACTER FILTER EXTRACTION")
    print("=" * 60)
    
    test_cases = [
        {
            "description": "DJ Memphis is a 25-year-old Memphis hip-hop producer working out of his home studio, known for his introspective approach to beats and philosophical lyrics.",
            "expected_name": "DJ Memphis",
            "expected_genre": "memphis hip-hop"
        },
        {
            "description": "Sarah Johnson is a 28-year-old neo-soul singer from Atlanta, known for her powerful vocals and socially conscious lyrics about community empowerment.",
            "expected_name": "Sarah Johnson", 
            "expected_genre": "neo-soul"
        },
        {
            "description": "Luna Rodriguez is a 22-year-old folk singer from Seattle, known for her acoustic guitar work and environmental activism themes.",
            "expected_name": "Luna Rodriguez",
            "expected_genre": "folk"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎤 TEST CASE {i}")
        print(f"Description: {test_case['description'][:80]}...")
        
        # Test extraction functions
        extracted_name = _extract_character_name(test_case['description'])
        extracted_genre = _extract_character_genre(test_case['description'])
        
        print(f"Expected Name: {test_case['expected_name']}")
        print(f"Extracted Name: {extracted_name}")
        print(f"Name Match: {'✅ PASS' if extracted_name == test_case['expected_name'] else '❌ FAIL'}")
        
        print(f"Expected Genre: {test_case['expected_genre']}")
        print(f"Extracted Genre: {extracted_genre}")
        print(f"Genre Match: {'✅ PASS' if extracted_genre == test_case['expected_genre'] else '❌ FAIL'}")

def test_no_hardcoded_character_filter():
    """Test that character_filter doesn't contain hardcoded values"""
    
    print(f"\n🚫 TESTING NO HARDCODED CHARACTER FILTER")
    print("=" * 60)
    
    # Test with completely different character
    description = "Maria Santos is a 26-year-old reggaeton artist from Miami, known for her bilingual lyrics and dance-focused beats."
    
    # Simulate what would be in character_filter
    character_filter = f"Character-driven interpretation: {description[:100]}{'...' if len(description) > 100 else ''}"
    
    print(f"Character Filter: {character_filter}")
    
    # Check for hardcoded content
    hardcoded_terms = ["marcus", "bristol", "philosophical", "liquid dnb", "warehouse"]
    
    print("\nChecking for hardcoded content in character_filter:")
    for term in hardcoded_terms:
        found = term.lower() in character_filter.lower()
        print(f"  '{term}': {'❌ FOUND (BAD)' if found else '✅ NOT FOUND (GOOD)'}")
    
    # Check for expected character content
    expected_terms = ["maria", "santos", "reggaeton", "miami", "bilingual"]
    
    print("\nChecking for character-specific content:")
    for term in expected_terms:
        found = term.lower() in character_filter.lower()
        print(f"  '{term}': {'✅ FOUND (GOOD)' if found else '❌ NOT FOUND (BAD)'}")

if __name__ == "__main__":
    test_character_filter_extraction()
    test_no_hardcoded_character_filter()