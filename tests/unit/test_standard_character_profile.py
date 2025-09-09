#!/usr/bin/env python3
"""
Tests for StandardCharacterProfile data model

This test suite validates that the StandardCharacterProfile class handles
all the format variations and edge cases identified in the diagnostic report.
"""


import pytest

from standard_character_profile import (
    StandardCharacterProfile,
    create_character_profile_from_text,
    validate_character_profile_data,
)


class TestStandardCharacterProfile:
    """Test the StandardCharacterProfile class"""

    def test_basic_initialization(self):
        """Test basic character profile creation"""
        profile = StandardCharacterProfile(name="Test Character")

        assert profile.name == "Test Character"
        assert profile.aliases == []
        assert profile.physical_description == ""
        assert profile.confidence_score == 1.0
        assert profile.importance_score == 1.0

    def test_full_initialization(self):
        """Test character profile with all fields"""
        profile = StandardCharacterProfile(
            name="Sarah Chen",
            aliases=["Sarah", "SC"],
            physical_description="Tall, dark hair",
            mannerisms=["fidgets with pen", "looks away when nervous"],
            speech_patterns=["speaks softly", "uses technical terms"],
            behavioral_traits=["perfectionist", "analytical"],
            backstory="Grew up in urban environment",
            relationships=["close to mother", "distant from father"],
            formative_experiences=["moved cities at age 12", "won science fair"],
            social_connections=["college friends", "work colleagues"],
            motivations=["prove herself", "help others"],
            fears=["failure", "disappointing others"],
            desires=["recognition", "stability"],
            conflicts=["perfectionism vs creativity", "family expectations vs personal goals"],
            personality_drivers=["need for control", "desire to belong"],
            confidence_score=0.85,
            text_references=["Chapter 1", "Page 45"],
            first_appearance="Opening scene",
            importance_score=0.9
        )

        assert profile.name == "Sarah Chen"
        assert len(profile.aliases) == 2
        assert len(profile.mannerisms) == 2
        assert len(profile.motivations) == 2
        assert profile.confidence_score == 0.85
        assert profile.importance_score == 0.9

    def test_post_init_validation(self):
        """Test that __post_init__ properly validates and normalizes data"""
        # Test empty name handling
        profile = StandardCharacterProfile(name="")
        assert profile.name == "Unknown Character"

        # Test score normalization
        profile = StandardCharacterProfile(
            name="Test",
            confidence_score=1.5,  # Above 1.0
            importance_score=-0.5  # Below 0.0
        )
        assert profile.confidence_score == 1.0
        assert profile.importance_score == 0.0

        # Test string cleaning
        profile = StandardCharacterProfile(
            name="  Test Character  ",
            physical_description="  Tall and thin  ",
            backstory="  Complex background  "
        )
        assert profile.name == "Test Character"
        assert profile.physical_description == "Tall and thin"
        assert profile.backstory == "Complex background"

        # Test list cleaning
        profile = StandardCharacterProfile(
            name="Test",
            aliases=["", "  Valid Alias  ", "", "Another"],
            mannerisms=["", "  fidgets  ", ""]
        )
        assert profile.aliases == ["Valid Alias", "Another"]
        assert profile.mannerisms == ["fidgets"]

    def test_from_dict_basic(self):
        """Test creating profile from dictionary"""
        data = {
            "name": "John Doe",
            "aliases": ["Johnny", "JD"],
            "backstory": "Interesting background",
            "confidence_score": 0.8
        }

        profile = StandardCharacterProfile.from_dict(data)
        assert profile.name == "John Doe"
        assert profile.aliases == ["Johnny", "JD"]
        assert profile.backstory == "Interesting background"
        assert profile.confidence_score == 0.8

    def test_from_dict_missing_fields(self):
        """Test from_dict handles missing fields gracefully"""
        data = {"name": "Minimal Character"}

        profile = StandardCharacterProfile.from_dict(data)
        assert profile.name == "Minimal Character"
        assert profile.aliases == []
        assert profile.backstory == ""
        assert profile.confidence_score == 1.0

    def test_from_dict_missing_name(self):
        """Test from_dict handles missing name"""
        data = {"backstory": "Some background"}

        profile = StandardCharacterProfile.from_dict(data)
        assert profile.name == "Unknown Character"
        assert profile.backstory == "Some background"

    def test_from_dict_type_conversion(self):
        """Test from_dict handles type conversions"""
        data = {
            "name": "Test Character",
            "aliases": "alias1,alias2,alias3",  # String instead of list
            "mannerisms": "fidgets;taps foot",  # String with semicolons
            "confidence_score": "0.75",  # String instead of float
            "importance_score": None  # None value
        }

        profile = StandardCharacterProfile.from_dict(data)
        assert profile.name == "Test Character"
        assert profile.aliases == ["alias1", "alias2", "alias3"]
        assert profile.mannerisms == ["fidgets", "taps foot"]
        assert profile.confidence_score == 0.75
        assert profile.importance_score == 1.0  # Default value

    def test_from_dict_invalid_data(self):
        """Test from_dict handles invalid data"""
        # Test non-dict input
        with pytest.raises(ValueError):
            StandardCharacterProfile.from_dict("not a dict")

        # Test invalid float conversion
        data = {
            "name": "Test",
            "confidence_score": "invalid_float"
        }
        profile = StandardCharacterProfile.from_dict(data)
        assert profile.confidence_score == 1.0  # Should use default

    def test_from_dict_unknown_fields(self):
        """Test from_dict ignores unknown fields"""
        data = {
            "name": "Test Character",
            "unknown_field": "should be ignored",
            "another_unknown": ["list", "of", "values"],
            "backstory": "Valid field"
        }

        profile = StandardCharacterProfile.from_dict(data)
        assert profile.name == "Test Character"
        assert profile.backstory == "Valid field"
        assert not hasattr(profile, "unknown_field")

    def test_to_dict(self):
        """Test converting profile to dictionary"""
        profile = StandardCharacterProfile(
            name="Test Character",
            aliases=["TC"],
            backstory="Test background",
            confidence_score=0.9
        )

        data = profile.to_dict()
        assert isinstance(data, dict)
        assert data["name"] == "Test Character"
        assert data["aliases"] == ["TC"]
        assert data["backstory"] == "Test background"
        assert data["confidence_score"] == 0.9

        # Should contain all fields including new conceptual fields
        expected_fields = {
            'name', 'aliases', 'physical_description', 'mannerisms', 'speech_patterns',
            'behavioral_traits', 'backstory', 'relationships', 'formative_experiences',
            'social_connections', 'motivations', 'fears', 'desires', 'conflicts',
            'personality_drivers', 'confidence_score', 'text_references',
            'first_appearance', 'importance_score', 'conceptual_basis', 'content_type',
            'processing_notes'
        }
        assert set(data.keys()) == expected_fields

    def test_to_legacy_format(self):
        """Test converting to legacy formats"""
        profile = StandardCharacterProfile(
            name="Test Character",
            aliases=["TC"],
            backstory="Test background",
            conflicts=["internal struggle"],
            fears=["failure"],
            physical_description="Tall",
            motivations=["success"],
            confidence_score=0.8
        )

        # Test simple format
        simple = profile.to_legacy_format("simple")
        expected_simple_keys = {"name", "backstory", "conflicts", "fears"}
        assert set(simple.keys()) == expected_simple_keys
        assert simple["name"] == "Test Character"

        # Test minimal format
        minimal = profile.to_legacy_format("minimal")
        expected_minimal_keys = {
            "name", "aliases", "physical_description", "backstory",
            "motivations", "fears", "confidence_score"
        }
        assert set(minimal.keys()) == expected_minimal_keys

        # Test full format
        full = profile.to_legacy_format("full")
        assert len(full.keys()) == 22  # All fields including new conceptual fields

    def test_from_legacy_format(self):
        """Test creating profile from legacy formats"""
        # Simple legacy format
        simple_data = {
            "name": "Legacy Character",
            "backstory": "Old format background",
            "conflicts": ["old conflict"],
            "fears": ["old fear"]
        }

        profile = StandardCharacterProfile.from_legacy_format(simple_data, "simple")
        assert profile.name == "Legacy Character"
        assert profile.backstory == "Old format background"
        assert profile.conflicts == ["old conflict"]
        assert profile.fears == ["old fear"]

        # Auto-detect format
        profile_auto = StandardCharacterProfile.from_legacy_format(simple_data, "auto")
        assert profile_auto.name == "Legacy Character"

    def test_merge_with(self):
        """Test merging two character profiles"""
        profile1 = StandardCharacterProfile(
            name="Character A",
            aliases=["A"],
            backstory="Background A",
            motivations=["motivation A"],
            confidence_score=0.8
        )

        profile2 = StandardCharacterProfile(
            name="Character B",
            aliases=["B"],
            backstory="Longer background B with more details",
            fears=["fear B"],
            confidence_score=0.6
        )

        merged = profile1.merge_with(profile2)

        # Should use name from higher confidence profile
        assert merged.name == "Character A"

        # Should merge lists
        assert set(merged.aliases) == {"A", "B"}

        # Should use longer backstory
        assert merged.backstory == "Longer background B with more details"

        # Should combine different fields
        assert merged.motivations == ["motivation A"]
        assert merged.fears == ["fear B"]

        # Should use higher confidence score
        assert merged.confidence_score == 0.8

    def test_merge_with_invalid_type(self):
        """Test merge_with with invalid input"""
        profile = StandardCharacterProfile(name="Test")

        with pytest.raises(ValueError):
            profile.merge_with("not a profile")

    def test_is_complete(self):
        """Test completeness checking"""
        # Incomplete profile (just name)
        incomplete = StandardCharacterProfile(name="Test")
        assert not incomplete.is_complete()

        # Unknown character is incomplete
        unknown = StandardCharacterProfile(name="Unknown Character")
        assert not unknown.is_complete()

        # Complete profile (has info in all layers)
        complete = StandardCharacterProfile(
            name="Complete Character",
            physical_description="Tall",  # Skin layer
            backstory="Rich background",  # Flesh layer
            motivations=["achieve goals"]  # Core layer
        )
        assert complete.is_complete()

        # Partially complete (missing core layer)
        partial = StandardCharacterProfile(
            name="Partial Character",
            mannerisms=["fidgets"],  # Skin layer
            relationships=["friend"]  # Flesh layer
            # Missing core layer
        )
        assert not partial.is_complete()

    def test_get_summary(self):
        """Test summary generation"""
        profile = StandardCharacterProfile(
            name="Summary Test",
            aliases=["ST", "Tester"],
            backstory="A character created for testing summary functionality",
            motivations=["test everything"],
            fears=["bugs in code"],
            confidence_score=0.95
        )

        summary = profile.get_summary()
        assert "Summary Test" in summary
        assert "ST, Tester" in summary
        assert "test everything" in summary
        assert "bugs in code" in summary
        assert "0.95" in summary

    def test_string_representations(self):
        """Test __str__ and __repr__ methods"""
        profile = StandardCharacterProfile(
            name="String Test",
            confidence_score=0.8
        )

        str_repr = str(profile)
        assert "String Test" in str_repr

        repr_str = repr(profile)
        assert "StandardCharacterProfile" in repr_str
        assert "String Test" in repr_str
        assert "0.80" in repr_str


class TestUtilityFunctions:
    """Test utility functions"""

    def test_create_character_profile_from_text(self):
        """Test creating profile from text"""
        text = "John Smith is a creative and quiet person who loves art."

        profile = create_character_profile_from_text(text)
        assert profile.name == "John Smith"
        assert "creative" in profile.behavioral_traits
        assert profile.confidence_score == 0.7
        assert len(profile.text_references) == 1

    def test_create_character_profile_from_text_with_name(self):
        """Test creating profile from text with provided name"""
        text = "A creative person who loves music."

        profile = create_character_profile_from_text(text, name="Custom Name")
        assert profile.name == "Custom Name"
        assert "creative" in profile.behavioral_traits

    def test_create_character_profile_from_text_no_name_found(self):
        """Test creating profile when no name can be extracted"""
        text = "someone who is very creative and artistic"

        profile = create_character_profile_from_text(text)
        assert profile.name == "Character from Text"
        assert "creative" in profile.behavioral_traits

    def test_validate_character_profile_data_valid(self):
        """Test validation with valid data"""
        data = {
            "name": "Valid Character",
            "aliases": ["VC"],
            "confidence_score": 0.8
        }

        issues = validate_character_profile_data(data)
        assert len(issues) == 0

    def test_validate_character_profile_data_invalid(self):
        """Test validation with invalid data"""
        # Test non-dict input
        issues = validate_character_profile_data("not a dict")
        assert len(issues) == 1
        assert "Expected dictionary" in issues[0]

        # Test missing name
        data = {"backstory": "No name provided"}
        issues = validate_character_profile_data(data)
        assert len(issues) == 1
        assert "Missing required field: 'name'" in issues[0]

        # Test wrong types
        data = {
            "name": "Test",
            "aliases": "should be list",
            "confidence_score": "should be number"
        }
        issues = validate_character_profile_data(data)
        assert len(issues) == 2
        assert any("aliases" in issue for issue in issues)
        assert any("confidence_score" in issue for issue in issues)

        # Test score out of range
        data = {
            "name": "Test",
            "confidence_score": 1.5
        }
        issues = validate_character_profile_data(data)
        assert len(issues) == 1
        assert "between 0 and 1" in issues[0]


class TestBackwardCompatibility:
    """Test backward compatibility with existing formats"""

    def test_server_format_compatibility(self):
        """Test compatibility with server.py CharacterProfile format"""
        # This is the format from server.py
        server_data = {
            'name': 'Server Character',
            'aliases': ['SC'],
            'physical_description': 'Tall and lean',
            'mannerisms': ['taps fingers'],
            'speech_patterns': ['speaks quickly'],
            'behavioral_traits': ['analytical'],
            'backstory': 'Complex background',
            'relationships': ['colleague'],
            'formative_experiences': ['childhood event'],
            'social_connections': ['work friends'],
            'motivations': ['success'],
            'fears': ['failure'],
            'desires': ['recognition'],
            'conflicts': ['work vs life'],
            'personality_drivers': ['perfectionism'],
            'confidence_score': 0.9,
            'text_references': ['page 1'],
            'first_appearance': 'chapter 1',
            'importance_score': 0.8
        }

        profile = StandardCharacterProfile.from_dict(server_data)
        assert profile.name == 'Server Character'
        assert profile.confidence_score == 0.9

        # Should be able to convert back
        converted = profile.to_dict()
        assert converted['name'] == 'Server Character'

    def test_test_core_classes_format_compatibility(self):
        """Test compatibility with tests/test_core_classes.py format"""
        # This format has all the same fields as server.py
        test_data = {
            'name': 'Test Character',
            'aliases': ['TC'],
            'physical_description': 'Average height',
            'backstory': 'Test background',
            'motivations': ['test goals'],
            'fears': ['test fears'],
            'confidence_score': 0.7
        }

        profile = StandardCharacterProfile.from_dict(test_data)
        assert profile.name == 'Test Character'
        assert profile.is_complete()  # Should have enough info

    def test_legacy_simple_format_compatibility(self):
        """Test compatibility with legacy simple format"""
        # This is the format from tests/legacy/test_artist_description.py
        legacy_data = {
            'name': 'Legacy Character',
            'backstory': 'Legacy background',
            'conflicts': ['legacy conflict'],
            'fears': ['legacy fear']
        }

        profile = StandardCharacterProfile.from_dict(legacy_data)
        assert profile.name == 'Legacy Character'
        assert profile.backstory == 'Legacy background'
        assert profile.conflicts == ['legacy conflict']
        assert profile.fears == ['legacy fear']

        # Should be able to convert to legacy format
        legacy_format = profile.to_legacy_format('simple')
        assert legacy_format['name'] == 'Legacy Character'
        assert legacy_format['backstory'] == 'Legacy background'


if __name__ == "__main__":
    # Run basic tests if executed directly
    test_instance = TestStandardCharacterProfile()

    print("Running basic StandardCharacterProfile tests...")

    try:
        test_instance.test_basic_initialization()
        print("✓ Basic initialization test passed")

        test_instance.test_from_dict_basic()
        print("✓ from_dict basic test passed")

        test_instance.test_to_dict()
        print("✓ to_dict test passed")

        test_instance.test_is_complete()
        print("✓ Completeness check test passed")

        print("\nAll basic tests passed! Run with pytest for full test suite.")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise
