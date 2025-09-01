#!/usr/bin/env python3
"""
Integration tests for StandardCharacterProfile with existing MCP tools

This test suite verifies that the StandardCharacterProfile works correctly
with the existing MCP tools and resolves the format mismatch issues.
"""

import pytest
import json
from typing import Dict, Any
from standard_character_profile import StandardCharacterProfile, validate_character_profile_data


class TestStandardCharacterProfileIntegration:
    """Test StandardCharacterProfile integration with MCP tools"""
    
    def test_format_compatibility_with_server_py(self):
        """Test that StandardCharacterProfile is compatible with server.py format"""
        # This is the exact format used in server.py
        server_format_data = {
            'name': 'Sarah Chen',
            'aliases': ['Sarah', 'SC'],
            'physical_description': 'Tall, dark hair, expressive eyes',
            'mannerisms': ['fidgets with pen when thinking', 'looks away when nervous'],
            'speech_patterns': ['speaks softly', 'uses precise language'],
            'behavioral_traits': ['perfectionist', 'analytical', 'empathetic'],
            'backstory': 'Grew up in urban environment, high achiever',
            'relationships': ['close to mother', 'distant from father'],
            'formative_experiences': ['moved cities at age 12', 'won science fair'],
            'social_connections': ['college friends', 'work colleagues'],
            'motivations': ['prove herself', 'help others succeed'],
            'fears': ['failure', 'disappointing others'],
            'desires': ['recognition', 'meaningful work'],
            'conflicts': ['perfectionism vs creativity', 'family expectations vs personal goals'],
            'personality_drivers': ['need for control', 'desire to belong'],
            'confidence_score': 0.85,
            'text_references': ['Chapter 1: Introduction', 'Page 45-67'],
            'first_appearance': 'Opening scene at coffee shop',
            'importance_score': 0.9
        }
        
        # Should create without errors
        profile = StandardCharacterProfile.from_dict(server_format_data)
        
        # Verify all fields are preserved
        assert profile.name == 'Sarah Chen'
        assert profile.aliases == ['Sarah', 'SC']
        assert profile.confidence_score == 0.85
        assert profile.importance_score == 0.9
        assert len(profile.motivations) == 2
        assert len(profile.fears) == 2
        
        # Should be complete
        assert profile.is_complete()
        
        # Should convert back to dict correctly
        converted = profile.to_dict()
        assert converted['name'] == 'Sarah Chen'
        assert len(converted.keys()) == 19  # All fields present
    
    def test_legacy_simple_format_compatibility(self):
        """Test compatibility with legacy simple format from test files"""
        # This is the format used in tests/legacy/test_artist_description.py
        legacy_format_data = {
            'name': 'Marcus Rivera',
            'backstory': 'father\'s abandonment, grandmother\'s wisdom, family traditions vs innovation',
            'conflicts': ['tradition vs innovation', 'family loyalty vs personal growth'],
            'fears': ['abandoning family', 'losing cultural identity']
        }
        
        # Should create without errors
        profile = StandardCharacterProfile.from_dict(legacy_format_data)
        
        # Verify fields are preserved
        assert profile.name == 'Marcus Rivera'
        assert 'grandmother\'s wisdom' in profile.backstory
        assert len(profile.conflicts) == 2
        assert len(profile.fears) == 2
        
        # Should fill in missing fields with defaults
        assert profile.aliases == []
        assert profile.physical_description == ""
        assert profile.confidence_score == 1.0
        
        # Should be able to convert to legacy format
        legacy_converted = profile.to_legacy_format('simple')
        assert legacy_converted['name'] == 'Marcus Rivera'
        assert legacy_converted['backstory'] == legacy_format_data['backstory']
        assert legacy_converted['conflicts'] == legacy_format_data['conflicts']
        assert legacy_converted['fears'] == legacy_format_data['fears']
    
    def test_problematic_skin_parameter_handling(self):
        """Test handling of problematic 'skin' parameter that causes errors"""
        # This simulates the problematic format that causes 'skin' parameter errors
        problematic_data = {
            'name': 'Test Character',
            'skin': 'This parameter should be ignored',  # This causes errors in current tools
            'physical_description': 'Tall and lean',
            'backstory': 'Complex background',
            'confidence_score': 0.8
        }
        
        # Should create without errors, ignoring the 'skin' parameter
        profile = StandardCharacterProfile.from_dict(problematic_data)
        
        # Should use valid fields
        assert profile.name == 'Test Character'
        assert profile.physical_description == 'Tall and lean'
        assert profile.backstory == 'Complex background'
        assert profile.confidence_score == 0.8
        
        # Should not have 'skin' attribute
        assert not hasattr(profile, 'skin')
        
        # Converted dict should not contain 'skin'
        converted = profile.to_dict()
        assert 'skin' not in converted
    
    def test_problematic_age_parameter_handling(self):
        """Test handling of problematic 'age' parameter that causes errors"""
        # This simulates the problematic format that causes 'age' parameter errors
        problematic_data = {
            'name': 'Test Character',
            'age': 25,  # This parameter doesn't exist in StandardCharacterProfile
            'backstory': 'Young professional',
            'motivations': ['career success']
        }
        
        # Should create without errors, ignoring the 'age' parameter
        profile = StandardCharacterProfile.from_dict(problematic_data)
        
        # Should use valid fields
        assert profile.name == 'Test Character'
        assert profile.backstory == 'Young professional'
        assert profile.motivations == ['career success']
        
        # Should not have 'age' attribute
        assert not hasattr(profile, 'age')
        
        # Age information can be included in backstory or physical_description
        assert 'Young' in profile.backstory
    
    def test_type_conversion_robustness(self):
        """Test robust type conversion for common format mismatches"""
        # Test various type mismatches that occur in real usage
        mismatched_data = {
            'name': 'Type Test Character',
            'aliases': 'single_alias',  # String instead of list
            'mannerisms': 'fidgets,taps,looks_around',  # Comma-separated string
            'speech_patterns': 'quiet;thoughtful;precise',  # Semicolon-separated
            'motivations': None,  # None instead of list
            'confidence_score': '0.75',  # String instead of float
            'importance_score': None,  # None instead of float
            'behavioral_traits': ['trait1', 'trait2', '', 'trait3']  # List with empty strings
        }
        
        profile = StandardCharacterProfile.from_dict(mismatched_data)
        
        # Should handle string-to-list conversion
        assert profile.aliases == ['single_alias']
        assert profile.mannerisms == ['fidgets', 'taps', 'looks_around']
        assert profile.speech_patterns == ['quiet', 'thoughtful', 'precise']
        
        # Should handle None-to-list conversion
        assert profile.motivations == []
        
        # Should handle string-to-float conversion
        assert profile.confidence_score == 0.75
        
        # Should handle None-to-float conversion with default
        assert profile.importance_score == 1.0
        
        # Should clean empty strings from lists
        assert profile.behavioral_traits == ['trait1', 'trait2', 'trait3']
    
    def test_json_serialization_compatibility(self):
        """Test JSON serialization/deserialization compatibility"""
        # Create a profile with various data types
        original_profile = StandardCharacterProfile(
            name='JSON Test Character',
            aliases=['JTC', 'Tester'],
            physical_description='Average height, brown hair',
            mannerisms=['gestures while talking'],
            backstory='Created for JSON testing',
            motivations=['test compatibility'],
            fears=['serialization errors'],
            confidence_score=0.88,
            importance_score=0.92
        )
        
        # Convert to dict and serialize to JSON
        profile_dict = original_profile.to_dict()
        json_string = json.dumps(profile_dict)
        
        # Deserialize from JSON and create new profile
        deserialized_dict = json.loads(json_string)
        new_profile = StandardCharacterProfile.from_dict(deserialized_dict)
        
        # Should be identical
        assert new_profile.name == original_profile.name
        assert new_profile.aliases == original_profile.aliases
        assert new_profile.physical_description == original_profile.physical_description
        assert new_profile.mannerisms == original_profile.mannerisms
        assert new_profile.backstory == original_profile.backstory
        assert new_profile.motivations == original_profile.motivations
        assert new_profile.fears == original_profile.fears
        assert new_profile.confidence_score == original_profile.confidence_score
        assert new_profile.importance_score == original_profile.importance_score
    
    def test_empty_and_minimal_data_handling(self):
        """Test handling of empty and minimal data scenarios"""
        # Test completely empty data (except name)
        minimal_data = {'name': 'Minimal Character'}
        profile = StandardCharacterProfile.from_dict(minimal_data)
        
        assert profile.name == 'Minimal Character'
        assert profile.aliases == []
        assert profile.backstory == ""
        assert profile.confidence_score == 1.0
        assert not profile.is_complete()  # Should not be complete with minimal data
        
        # Test with some empty fields
        partial_data = {
            'name': 'Partial Character',
            'aliases': [],
            'physical_description': '',
            'backstory': 'Some background',
            'motivations': ['goal'],
            'mannerisms': ['habit']
        }
        
        profile = StandardCharacterProfile.from_dict(partial_data)
        assert profile.name == 'Partial Character'
        assert profile.backstory == 'Some background'
        assert profile.motivations == ['goal']
        assert profile.mannerisms == ['habit']
        assert profile.is_complete()  # Should be complete with info in all layers
    
    def test_validation_function_integration(self):
        """Test the validation function with various data scenarios"""
        # Valid data
        valid_data = {
            'name': 'Valid Character',
            'aliases': ['VC'],
            'confidence_score': 0.8
        }
        issues = validate_character_profile_data(valid_data)
        assert len(issues) == 0
        
        # Invalid data - missing name
        invalid_data = {'backstory': 'No name'}
        issues = validate_character_profile_data(invalid_data)
        assert len(issues) == 1
        assert 'name' in issues[0]
        
        # Invalid data - wrong types
        wrong_types_data = {
            'name': 'Test',
            'aliases': 'should be list',
            'confidence_score': 'should be number'
        }
        issues = validate_character_profile_data(wrong_types_data)
        assert len(issues) == 2
        
        # Invalid data - score out of range
        out_of_range_data = {
            'name': 'Test',
            'confidence_score': 1.5
        }
        issues = validate_character_profile_data(out_of_range_data)
        assert len(issues) == 1
        assert 'between 0 and 1' in issues[0]
    
    def test_merge_functionality_for_character_detection(self):
        """Test merge functionality that could be useful for character detection"""
        # Simulate two partial character detections that need to be merged
        detection1 = StandardCharacterProfile(
            name='Sarah',
            physical_description='Tall woman',
            mannerisms=['fidgets with pen'],
            confidence_score=0.7
        )
        
        detection2 = StandardCharacterProfile(
            name='Sarah Chen',  # More complete name
            aliases=['Sarah'],
            backstory='Works in tech industry',
            motivations=['career advancement'],
            confidence_score=0.8
        )
        
        merged = detection1.merge_with(detection2)
        
        # Should use more confident name
        assert merged.name == 'Sarah Chen'
        
        # Should combine information
        assert merged.physical_description == 'Tall woman'
        assert merged.mannerisms == ['fidgets with pen']
        assert merged.aliases == ['Sarah']
        assert merged.backstory == 'Works in tech industry'
        assert merged.motivations == ['career advancement']
        
        # Should use higher confidence
        assert merged.confidence_score == 0.8
        
        # Should be more complete than individual parts
        assert merged.is_complete()
    
    def test_three_layer_analysis_structure(self):
        """Test that the three-layer analysis structure is properly supported"""
        profile = StandardCharacterProfile(
            name='Three Layer Test',
            
            # Skin Layer - Observable characteristics
            physical_description='Medium height, athletic build',
            mannerisms=['taps foot when thinking', 'maintains eye contact'],
            speech_patterns=['speaks clearly', 'uses technical terms'],
            behavioral_traits=['punctual', 'organized', 'detail-oriented'],
            
            # Flesh Layer - Background and relationships
            backstory='Grew up in small town, moved to city for college',
            relationships=['close to sister', 'mentor relationship with professor'],
            formative_experiences=['parents\' divorce at age 10', 'first job at startup'],
            social_connections=['college alumni network', 'professional associations'],
            
            # Core Layer - Deep psychology
            motivations=['prove independence', 'make meaningful impact'],
            fears=['being seen as incompetent', 'losing control'],
            desires=['recognition for expertise', 'work-life balance'],
            conflicts=['ambition vs family time', 'perfectionism vs efficiency'],
            personality_drivers=['need for achievement', 'desire for stability']
        )
        
        # Should be complete with all three layers
        assert profile.is_complete()
        
        # Should have information in each layer
        skin_layer_info = (
            profile.physical_description or 
            profile.mannerisms or 
            profile.speech_patterns or 
            profile.behavioral_traits
        )
        assert skin_layer_info
        
        flesh_layer_info = (
            profile.backstory or 
            profile.relationships or 
            profile.formative_experiences or 
            profile.social_connections
        )
        assert flesh_layer_info
        
        core_layer_info = (
            profile.motivations or 
            profile.fears or 
            profile.desires or 
            profile.conflicts or 
            profile.personality_drivers
        )
        assert core_layer_info
        
        # Summary should include key information
        summary = profile.get_summary()
        assert 'Three Layer Test' in summary
        assert 'prove independence' in summary  # First motivation
        assert 'being seen as incompetent' in summary  # First fear


class TestRealWorldScenarios:
    """Test real-world scenarios that caused issues in the diagnostic report"""
    
    def test_analyze_character_text_tool_format(self):
        """Test format expected by analyze_character_text tool"""
        # This simulates the format that should be returned by analyze_character_text
        analysis_result = {
            "characters": [
                {
                    "name": "Elena Rodriguez",
                    "aliases": ["Elena", "El"],
                    "physical_description": "Petite, dark curly hair, paint-stained fingers",
                    "mannerisms": ["bites lip when concentrating", "gestures expressively"],
                    "speech_patterns": ["speaks passionately about art", "uses visual metaphors"],
                    "behavioral_traits": ["creative", "self-critical", "passionate"],
                    "backstory": "Art school graduate struggling with self-doubt",
                    "relationships": ["supportive roommate", "critical art professor"],
                    "formative_experiences": ["harsh critique in art school", "first gallery showing"],
                    "social_connections": ["local art community", "online artist groups"],
                    "motivations": ["create meaningful art", "overcome self-doubt"],
                    "fears": ["artistic failure", "being judged"],
                    "desires": ["recognition", "artistic fulfillment"],
                    "conflicts": ["perfectionism vs expression", "commercial vs artistic success"],
                    "personality_drivers": ["need for creative expression", "fear of mediocrity"],
                    "confidence_score": 0.85,
                    "text_references": ["paragraph 1-3", "character introduction"],
                    "first_appearance": "studio apartment scene",
                    "importance_score": 0.9
                }
            ],
            "narrative_themes": ["artistic struggle", "self-discovery", "creative growth"],
            "emotional_arc": ["self-doubt", "determination", "breakthrough"]
        }
        
        # Should be able to create StandardCharacterProfile from this data
        character_data = analysis_result["characters"][0]
        profile = StandardCharacterProfile.from_dict(character_data)
        
        assert profile.name == "Elena Rodriguez"
        assert profile.is_complete()
        assert len(profile.aliases) == 2
        assert len(profile.motivations) == 2
        assert len(profile.fears) == 2
    
    def test_generate_artist_personas_tool_format(self):
        """Test format expected by generate_artist_personas tool"""
        # This simulates input to generate_artist_personas tool
        character_profile_data = {
            "name": "Marcus Thompson",
            "aliases": ["Marcus", "MT"],
            "backstory": "Hip-hop producer from Memphis with deep roots in the community",
            "motivations": ["represent Memphis culture", "support local artists"],
            "fears": ["losing authenticity", "commercialization"],
            "behavioral_traits": ["collaborative", "community-focused", "authentic"],
            "confidence_score": 0.9
        }
        
        # Should create profile without errors
        profile = StandardCharacterProfile.from_dict(character_profile_data)
        
        assert profile.name == "Marcus Thompson"
        assert "Memphis" in profile.backstory
        assert "represent Memphis culture" in profile.motivations
        assert profile.confidence_score == 0.9
        
        # Should be able to convert back for tool usage
        tool_format = profile.to_dict()
        assert tool_format["name"] == "Marcus Thompson"
        assert "Memphis" in tool_format["backstory"]
    
    def test_create_suno_commands_tool_format(self):
        """Test format expected by create_suno_commands tool"""
        # This simulates persona data input to create_suno_commands tool
        persona_data = {
            "character_name": "Sarah Chen",
            "artist_name": "Sarah C",
            "primary_genre": "indie folk",
            "secondary_genres": ["acoustic", "singer-songwriter"],
            "vocal_style": "soft and introspective",
            "lyrical_themes": ["urban isolation", "personal growth"],
            "emotional_palette": ["melancholy", "hope", "introspection"]
        }
        
        # The tool should also receive character profile data
        character_data = {
            "name": "Sarah Chen",
            "backstory": "Urban professional seeking authenticity",
            "motivations": ["find genuine connections", "express inner truth"],
            "fears": ["superficial relationships", "losing herself"],
            "confidence_score": 0.8
        }
        
        # Should create profile without format errors
        profile = StandardCharacterProfile.from_dict(character_data)
        
        assert profile.name == "Sarah Chen"
        assert profile.name == persona_data["character_name"]  # Names should match
        assert profile.confidence_score == 0.8
    
    def test_hardcoded_content_replacement(self):
        """Test that hardcoded content can be replaced with dynamic content"""
        # This simulates the problematic hardcoded Bristol content
        hardcoded_data = {
            "name": "Marcus Thompson",  # This was hardcoded
            "backstory": "Bristol warehouse studio, underground music scene",  # This was hardcoded
            "location": "Bristol",  # This was hardcoded
            "motivations": ["create authentic music"],
            "confidence_score": 0.8
        }
        
        # Should create profile (the hardcoded content is just data now)
        profile = StandardCharacterProfile.from_dict(hardcoded_data)
        
        assert profile.name == "Marcus Thompson"
        assert "Bristol" in profile.backstory
        
        # But now we can easily create dynamic content
        dynamic_data = {
            "name": "Elena Rodriguez",  # Dynamic name
            "backstory": "Los Angeles art studio, creative community",  # Dynamic location
            "motivations": ["express artistic vision"],
            "confidence_score": 0.85
        }
        
        dynamic_profile = StandardCharacterProfile.from_dict(dynamic_data)
        
        assert dynamic_profile.name == "Elena Rodriguez"
        assert "Los Angeles" in dynamic_profile.backstory
        assert dynamic_profile.name != profile.name  # Different characters
        assert dynamic_profile.backstory != profile.backstory  # Different backgrounds


if __name__ == "__main__":
    # Run basic integration tests if executed directly
    test_instance = TestStandardCharacterProfileIntegration()
    
    print("Running StandardCharacterProfile integration tests...")
    
    try:
        test_instance.test_format_compatibility_with_server_py()
        print("✓ Server.py format compatibility test passed")
        
        test_instance.test_legacy_simple_format_compatibility()
        print("✓ Legacy format compatibility test passed")
        
        test_instance.test_problematic_skin_parameter_handling()
        print("✓ Problematic 'skin' parameter handling test passed")
        
        test_instance.test_problematic_age_parameter_handling()
        print("✓ Problematic 'age' parameter handling test passed")
        
        test_instance.test_type_conversion_robustness()
        print("✓ Type conversion robustness test passed")
        
        test_instance.test_json_serialization_compatibility()
        print("✓ JSON serialization compatibility test passed")
        
        test_instance.test_three_layer_analysis_structure()
        print("✓ Three-layer analysis structure test passed")
        
        print("\nAll integration tests passed! StandardCharacterProfile is ready for use.")
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        raise