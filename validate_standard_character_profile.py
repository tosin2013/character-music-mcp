#!/usr/bin/env python3
"""
Validation script for StandardCharacterProfile implementation

This script validates that the StandardCharacterProfile implementation
correctly addresses all the issues identified in the diagnostic report.
"""

import json
import traceback
from typing import Dict, Any, List
from standard_character_profile import (
    StandardCharacterProfile, 
    validate_character_profile_data,
    create_character_profile_from_text
)


class StandardCharacterProfileValidator:
    """Validator for StandardCharacterProfile implementation"""
    
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and record results"""
        try:
            test_func()
            self.test_results.append({"name": test_name, "status": "PASSED", "error": None})
            self.passed_tests += 1
            print(f"✓ {test_name}")
        except Exception as e:
            self.test_results.append({"name": test_name, "status": "FAILED", "error": str(e)})
            self.failed_tests += 1
            print(f"✗ {test_name}: {e}")
    
    def validate_requirement_2_1(self):
        """Validate Requirement 2.1: No 'skin' parameter errors"""
        # Test data with problematic 'skin' parameter
        data_with_skin = {
            "name": "Test Character",
            "skin": "This parameter should be ignored",
            "physical_description": "Valid description",
            "backstory": "Valid backstory"
        }
        
        # Should create without errors
        profile = StandardCharacterProfile.from_dict(data_with_skin)
        assert profile.name == "Test Character"
        assert profile.physical_description == "Valid description"
        assert not hasattr(profile, 'skin')
        
        # Should not include 'skin' in output
        output_dict = profile.to_dict()
        assert 'skin' not in output_dict
    
    def validate_requirement_2_2(self):
        """Validate Requirement 2.2: Correct parameter names and structure"""
        # Test with all expected parameter names
        expected_data = {
            'name': 'Test Character',
            'aliases': ['TC'],
            'physical_description': 'Test description',
            'mannerisms': ['test mannerism'],
            'speech_patterns': ['test pattern'],
            'behavioral_traits': ['test trait'],
            'backstory': 'Test backstory',
            'relationships': ['test relationship'],
            'formative_experiences': ['test experience'],
            'social_connections': ['test connection'],
            'motivations': ['test motivation'],
            'fears': ['test fear'],
            'desires': ['test desire'],
            'conflicts': ['test conflict'],
            'personality_drivers': ['test driver'],
            'confidence_score': 0.8,
            'text_references': ['test reference'],
            'first_appearance': 'test appearance',
            'importance_score': 0.9
        }
        
        profile = StandardCharacterProfile.from_dict(expected_data)
        
        # Verify all fields are correctly set
        assert profile.name == 'Test Character'
        assert profile.aliases == ['TC']
        assert profile.confidence_score == 0.8
        assert profile.importance_score == 0.9
        assert len(profile.motivations) == 1
    
    def validate_requirement_8_1(self):
        """Validate Requirement 8.1: No 'age' parameter errors"""
        # Test data with problematic 'age' parameter
        data_with_age = {
            "name": "Test Character",
            "age": 25,
            "backstory": "Young professional",
            "motivations": ["career success"]
        }
        
        # Should create without errors
        profile = StandardCharacterProfile.from_dict(data_with_age)
        assert profile.name == "Test Character"
        assert profile.backstory == "Young professional"
        assert not hasattr(profile, 'age')
        
        # Should not include 'age' in output
        output_dict = profile.to_dict()
        assert 'age' not in output_dict
    
    def validate_requirement_8_2(self):
        """Validate Requirement 8.2: Correct initialization parameters"""
        # Test direct initialization with correct parameters
        profile = StandardCharacterProfile(
            name="Direct Init Test",
            aliases=["DIT"],
            physical_description="Test description",
            backstory="Test backstory",
            motivations=["test goal"],
            confidence_score=0.75
        )
        
        assert profile.name == "Direct Init Test"
        assert profile.aliases == ["DIT"]
        assert profile.confidence_score == 0.75
    
    def validate_requirement_13_1(self):
        """Validate Requirement 13.1: Consistent character profile formats"""
        # Test multiple format inputs produce consistent output structure
        formats = [
            # Server.py format
            {
                'name': 'Server Format',
                'aliases': ['SF'],
                'physical_description': 'Server description',
                'backstory': 'Server backstory',
                'motivations': ['server goal'],
                'confidence_score': 0.8
            },
            # Legacy simple format
            {
                'name': 'Legacy Format',
                'backstory': 'Legacy backstory',
                'conflicts': ['legacy conflict'],
                'fears': ['legacy fear']
            },
            # Minimal format
            {
                'name': 'Minimal Format'
            }
        ]
        
        profiles = []
        for format_data in formats:
            profile = StandardCharacterProfile.from_dict(format_data)
            profiles.append(profile)
        
        # All profiles should have consistent structure
        for profile in profiles:
            output_dict = profile.to_dict()
            # Should have all expected fields
            expected_fields = {
                'name', 'aliases', 'physical_description', 'mannerisms', 'speech_patterns',
                'behavioral_traits', 'backstory', 'relationships', 'formative_experiences',
                'social_connections', 'motivations', 'fears', 'desires', 'conflicts',
                'personality_drivers', 'confidence_score', 'text_references',
                'first_appearance', 'importance_score'
            }
            assert set(output_dict.keys()) == expected_fields
    
    def validate_requirement_13_2(self):
        """Validate Requirement 13.2: Shared data models prevent format mismatches"""
        # Test that different input formats can be converted to each other
        server_format = {
            'name': 'Conversion Test',
            'aliases': ['CT'],
            'physical_description': 'Test description',
            'backstory': 'Test backstory',
            'motivations': ['test goal'],
            'fears': ['test fear'],
            'confidence_score': 0.8
        }
        
        profile = StandardCharacterProfile.from_dict(server_format)
        
        # Should convert to different legacy formats without errors
        simple_format = profile.to_legacy_format('simple')
        minimal_format = profile.to_legacy_format('minimal')
        full_format = profile.to_legacy_format('full')
        
        # All formats should be valid
        assert simple_format['name'] == 'Conversion Test'
        assert minimal_format['name'] == 'Conversion Test'
        assert full_format['name'] == 'Conversion Test'
        
        # Should be able to recreate profile from any format
        profile_from_simple = StandardCharacterProfile.from_legacy_format(simple_format)
        profile_from_minimal = StandardCharacterProfile.from_legacy_format(minimal_format)
        profile_from_full = StandardCharacterProfile.from_legacy_format(full_format)
        
        assert profile_from_simple.name == 'Conversion Test'
        assert profile_from_minimal.name == 'Conversion Test'
        assert profile_from_full.name == 'Conversion Test'
    
    def validate_json_serialization(self):
        """Validate JSON serialization compatibility"""
        profile = StandardCharacterProfile(
            name="JSON Test",
            aliases=["JT"],
            backstory="JSON test backstory",
            motivations=["test JSON"],
            confidence_score=0.85
        )
        
        # Should serialize to JSON without errors
        profile_dict = profile.to_dict()
        json_string = json.dumps(profile_dict)
        
        # Should deserialize from JSON without errors
        deserialized_dict = json.loads(json_string)
        new_profile = StandardCharacterProfile.from_dict(deserialized_dict)
        
        # Should be identical
        assert new_profile.name == profile.name
        assert new_profile.aliases == profile.aliases
        assert new_profile.backstory == profile.backstory
        assert new_profile.confidence_score == profile.confidence_score
    
    def validate_error_handling(self):
        """Validate robust error handling"""
        # Test with invalid data types
        invalid_data = {
            "name": "Error Test",
            "aliases": "should_be_list",
            "confidence_score": "should_be_float",
            "motivations": None
        }
        
        # Should handle gracefully
        profile = StandardCharacterProfile.from_dict(invalid_data)
        assert profile.name == "Error Test"
        assert isinstance(profile.aliases, list)
        assert isinstance(profile.confidence_score, float)
        assert isinstance(profile.motivations, list)
    
    def validate_three_layer_analysis(self):
        """Validate three-layer analysis support"""
        profile = StandardCharacterProfile(
            name="Three Layer Test",
            # Skin layer
            physical_description="Observable traits",
            mannerisms=["observable behavior"],
            # Flesh layer
            backstory="Background information",
            relationships=["relationship info"],
            # Core layer
            motivations=["deep motivation"],
            fears=["deep fear"]
        )
        
        # Should be complete with all three layers
        assert profile.is_complete()
        
        # Should have information in each layer
        assert profile.physical_description or profile.mannerisms  # Skin layer
        assert profile.backstory or profile.relationships  # Flesh layer
        assert profile.motivations or profile.fears  # Core layer
    
    def validate_backward_compatibility(self):
        """Validate backward compatibility with existing formats"""
        # Test compatibility with various existing formats
        test_formats = [
            # Format from server.py
            {
                'name': 'Server Character',
                'aliases': ['SC'],
                'physical_description': 'Server description',
                'backstory': 'Server backstory',
                'motivations': ['server goal'],
                'confidence_score': 0.8
            },
            # Format from test files
            {
                'name': 'Test Character',
                'backstory': 'Test backstory',
                'conflicts': ['test conflict'],
                'fears': ['test fear']
            }
        ]
        
        for format_data in test_formats:
            profile = StandardCharacterProfile.from_dict(format_data)
            assert profile.name is not None
            assert len(profile.name) > 0
    
    def validate_utility_functions(self):
        """Validate utility functions"""
        # Test create_character_profile_from_text
        text = "John Smith is a creative and quiet person who loves art."
        profile = create_character_profile_from_text(text)
        assert profile.name == "John Smith"
        assert "creative" in profile.behavioral_traits
        
        # Test validation function
        valid_data = {"name": "Valid", "confidence_score": 0.8}
        issues = validate_character_profile_data(valid_data)
        assert len(issues) == 0
        
        invalid_data = {"backstory": "No name"}
        issues = validate_character_profile_data(invalid_data)
        assert len(issues) > 0
    
    def run_all_validations(self):
        """Run all validation tests"""
        print("Validating StandardCharacterProfile Implementation")
        print("=" * 60)
        
        # Run requirement validations
        self.run_test("Requirement 2.1: No 'skin' parameter errors", self.validate_requirement_2_1)
        self.run_test("Requirement 2.2: Correct parameter names", self.validate_requirement_2_2)
        self.run_test("Requirement 8.1: No 'age' parameter errors", self.validate_requirement_8_1)
        self.run_test("Requirement 8.2: Correct initialization", self.validate_requirement_8_2)
        self.run_test("Requirement 13.1: Consistent formats", self.validate_requirement_13_1)
        self.run_test("Requirement 13.2: Shared data models", self.validate_requirement_13_2)
        
        # Run additional validations
        self.run_test("JSON serialization compatibility", self.validate_json_serialization)
        self.run_test("Robust error handling", self.validate_error_handling)
        self.run_test("Three-layer analysis support", self.validate_three_layer_analysis)
        self.run_test("Backward compatibility", self.validate_backward_compatibility)
        self.run_test("Utility functions", self.validate_utility_functions)
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"Validation Summary:")
        print(f"  Passed: {self.passed_tests}")
        print(f"  Failed: {self.failed_tests}")
        print(f"  Total:  {self.passed_tests + self.failed_tests}")
        
        if self.failed_tests == 0:
            print("\n🎉 All validations passed! StandardCharacterProfile is ready for use.")
            return True
        else:
            print(f"\n❌ {self.failed_tests} validations failed. See details above.")
            return False
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate a detailed validation report"""
        return {
            "validation_summary": {
                "total_tests": len(self.test_results),
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": self.passed_tests / len(self.test_results) if self.test_results else 0
            },
            "test_results": self.test_results,
            "requirements_addressed": [
                "2.1: Character profiles accept expected JSON format without 'skin' parameter errors",
                "2.2: CharacterProfile uses correct parameter names and structure",
                "8.1: Character profiles accept profiles without 'age' parameter errors",
                "8.2: CharacterProfile objects use correct initialization parameters",
                "13.1: Consistent character profile formats across all tools",
                "13.2: Shared and reused data models to prevent format mismatches"
            ],
            "features_validated": [
                "JSON serialization/deserialization",
                "Robust error handling and type conversion",
                "Three-layer character analysis support",
                "Backward compatibility with existing formats",
                "Utility functions for common operations",
                "Data validation and completeness checking"
            ]
        }


def main():
    """Main validation function"""
    validator = StandardCharacterProfileValidator()
    success = validator.run_all_validations()
    
    # Generate and save validation report
    report = validator.generate_validation_report()
    
    with open('standard_character_profile_validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nValidation report saved to: standard_character_profile_validation_report.json")
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)