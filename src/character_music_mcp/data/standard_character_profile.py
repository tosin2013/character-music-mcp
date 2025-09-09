#!/usr/bin/env python3
"""
Standardized CharacterProfile data model for all MCP tools

This module provides a consistent CharacterProfile class that all MCP tools should use
to prevent format mismatches and initialization errors.
"""

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class StandardCharacterProfile:
    """
    Standardized character profile for all MCP tools
    
    This class implements the three-layer character analysis approach:
    - Skin Layer: Observable characteristics (physical, mannerisms, speech)
    - Flesh Layer: Background and relationships (backstory, connections)
    - Core Layer: Deep psychology (motivations, fears, desires)
    
    All fields have sensible defaults to handle missing data gracefully.
    """

    # Required fields
    name: str

    # Optional fields with defaults
    aliases: List[str] = field(default_factory=list)

    # Skin Layer - Observable characteristics
    physical_description: str = ""
    mannerisms: List[str] = field(default_factory=list)
    speech_patterns: List[str] = field(default_factory=list)
    behavioral_traits: List[str] = field(default_factory=list)

    # Flesh Layer - Background and relationships
    backstory: str = ""
    relationships: List[str] = field(default_factory=list)
    formative_experiences: List[str] = field(default_factory=list)
    social_connections: List[str] = field(default_factory=list)

    # Core Layer - Deep psychology
    motivations: List[str] = field(default_factory=list)
    fears: List[str] = field(default_factory=list)
    desires: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    personality_drivers: List[str] = field(default_factory=list)

    # Analysis metadata
    confidence_score: float = 1.0
    text_references: List[str] = field(default_factory=list)
    first_appearance: str = ""
    importance_score: float = 1.0

    # Optional conceptual fields (backward compatible)
    conceptual_basis: Optional[List[str]] = field(default_factory=list)
    content_type: Optional[str] = None  # "narrative", "conceptual", "descriptive"
    processing_notes: Optional[str] = None

    def __post_init__(self):
        """Validate and normalize data after initialization"""
        # Ensure name is not empty
        if not self.name or not self.name.strip():
            self.name = "Unknown Character"
            logger.warning("Character name was empty, set to 'Unknown Character'")

        # Normalize confidence and importance scores
        self.confidence_score = max(0.0, min(1.0, self.confidence_score))
        self.importance_score = max(0.0, min(1.0, self.importance_score))

        # Clean up string fields
        self.name = self.name.strip()
        self.physical_description = self.physical_description.strip()
        self.backstory = self.backstory.strip()
        self.first_appearance = self.first_appearance.strip()

        # Clean up optional conceptual fields
        if self.content_type:
            self.content_type = self.content_type.strip()
        if self.processing_notes:
            self.processing_notes = self.processing_notes.strip()
        if self.conceptual_basis:
            self.conceptual_basis = [item.strip() for item in self.conceptual_basis if item and item.strip()]

        # Remove empty strings from lists
        self.aliases = [alias.strip() for alias in self.aliases if alias and alias.strip()]
        self.mannerisms = [item.strip() for item in self.mannerisms if item and item.strip()]
        self.speech_patterns = [item.strip() for item in self.speech_patterns if item and item.strip()]
        self.behavioral_traits = [item.strip() for item in self.behavioral_traits if item and item.strip()]
        self.relationships = [item.strip() for item in self.relationships if item and item.strip()]
        self.formative_experiences = [item.strip() for item in self.formative_experiences if item and item.strip()]
        self.social_connections = [item.strip() for item in self.social_connections if item and item.strip()]
        self.motivations = [item.strip() for item in self.motivations if item and item.strip()]
        self.fears = [item.strip() for item in self.fears if item and item.strip()]
        self.desires = [item.strip() for item in self.desires if item and item.strip()]
        self.conflicts = [item.strip() for item in self.conflicts if item and item.strip()]
        self.personality_drivers = [item.strip() for item in self.personality_drivers if item and item.strip()]
        self.text_references = [item.strip() for item in self.text_references if item and item.strip()]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StandardCharacterProfile':
        """
        Create StandardCharacterProfile from dictionary, handling missing fields gracefully
        
        This method is essential for JSON deserialization and backward compatibility
        with existing character profile formats.
        
        Args:
            data: Dictionary containing character profile data
            
        Returns:
            StandardCharacterProfile instance with all fields properly initialized
        """
        if not isinstance(data, dict):
            logger.error(f"Expected dict, got {type(data)}: {data}")
            raise ValueError(f"Expected dictionary, got {type(data)}")

        # Handle the case where 'name' is missing
        if 'name' not in data or not data['name']:
            logger.warning("Character name missing from data, using 'Unknown Character'")
            data['name'] = "Unknown Character"

        # Create a new dict with only valid fields for this class
        valid_fields = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_data = {}

        for key, value in data.items():
            if key in valid_fields:
                # Handle type conversion for common mismatches
                field_type = cls.__dataclass_fields__[key].type

                # Handle list fields that might come as strings or None
                if hasattr(field_type, '__origin__') and field_type.__origin__ is list:
                    if value is None:
                        filtered_data[key] = []
                    elif isinstance(value, str):
                        # Split string into list if it contains separators
                        if ',' in value:
                            filtered_data[key] = [item.strip() for item in value.split(',') if item.strip()]
                        elif ';' in value:
                            filtered_data[key] = [item.strip() for item in value.split(';') if item.strip()]
                        else:
                            filtered_data[key] = [value] if value.strip() else []
                    elif isinstance(value, list):
                        filtered_data[key] = value
                    else:
                        logger.warning(f"Unexpected type for list field {key}: {type(value)}, converting to list")
                        filtered_data[key] = [str(value)] if value else []

                # Handle string fields that might be None
                elif field_type == str:
                    filtered_data[key] = str(value) if value is not None else ""

                # Handle float fields
                elif field_type == float:
                    try:
                        filtered_data[key] = float(value) if value is not None else 1.0
                    except (ValueError, TypeError):
                        logger.warning(f"Could not convert {key} value '{value}' to float, using 1.0")
                        filtered_data[key] = 1.0

                else:
                    filtered_data[key] = value
            else:
                logger.debug(f"Ignoring unknown field '{key}' with value '{value}'")

        try:
            return cls(**filtered_data)
        except TypeError as e:
            logger.error(f"Failed to create StandardCharacterProfile: {e}")
            logger.error(f"Filtered data: {filtered_data}")
            # Create minimal valid instance
            return cls(name=data.get('name', 'Unknown Character'))

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization
        
        Returns:
            Dictionary representation of the character profile
        """
        return asdict(self)

    def to_legacy_format(self, format_type: str = "simple") -> Dict[str, Any]:
        """
        Convert to legacy format for backward compatibility
        
        Args:
            format_type: Type of legacy format to generate
                - "simple": Just name and backstory (for old tests)
                - "minimal": Name, aliases, basic traits
                - "full": All fields (same as to_dict)
        
        Returns:
            Dictionary in the requested legacy format
        """
        if format_type == "simple":
            return {
                "name": self.name,
                "backstory": self.backstory,
                "conflicts": self.conflicts,
                "fears": self.fears
            }
        elif format_type == "minimal":
            return {
                "name": self.name,
                "aliases": self.aliases,
                "physical_description": self.physical_description,
                "backstory": self.backstory,
                "motivations": self.motivations,
                "fears": self.fears,
                "confidence_score": self.confidence_score
            }
        else:  # "full" or any other value
            return self.to_dict()

    @classmethod
    def from_legacy_format(cls, data: Dict[str, Any], format_type: str = "auto") -> 'StandardCharacterProfile':
        """
        Create StandardCharacterProfile from legacy format data
        
        Args:
            data: Legacy format data
            format_type: Type of legacy format ("auto" to detect automatically)
        
        Returns:
            StandardCharacterProfile instance
        """
        if format_type == "auto":
            # Auto-detect format based on available fields
            if len(data) <= 4 and "backstory" in data:
                format_type = "simple"
            elif len(data) <= 8:
                format_type = "minimal"
            else:
                format_type = "full"

        # Use from_dict which already handles missing fields gracefully
        return cls.from_dict(data)

    def merge_with(self, other: 'StandardCharacterProfile') -> 'StandardCharacterProfile':
        """
        Merge this character profile with another, combining information
        
        Args:
            other: Another StandardCharacterProfile to merge with
            
        Returns:
            New StandardCharacterProfile with merged information
        """
        if not isinstance(other, StandardCharacterProfile):
            raise ValueError("Can only merge with another StandardCharacterProfile")

        # Use the name from the profile with higher confidence
        name = self.name if self.confidence_score >= other.confidence_score else other.name

        # Merge lists by combining and deduplicating
        def merge_lists(list1: List[str], list2: List[str]) -> List[str]:
            combined = list1 + list2
            # Remove duplicates while preserving order
            seen = set()
            result = []
            for item in combined:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
            return result

        # Merge string fields by taking the longer/more detailed one
        def merge_strings(str1: str, str2: str) -> str:
            if not str1:
                return str2
            if not str2:
                return str1
            return str1 if len(str1) >= len(str2) else str2

        return StandardCharacterProfile(
            name=name,
            aliases=merge_lists(self.aliases, other.aliases),
            physical_description=merge_strings(self.physical_description, other.physical_description),
            mannerisms=merge_lists(self.mannerisms, other.mannerisms),
            speech_patterns=merge_lists(self.speech_patterns, other.speech_patterns),
            behavioral_traits=merge_lists(self.behavioral_traits, other.behavioral_traits),
            backstory=merge_strings(self.backstory, other.backstory),
            relationships=merge_lists(self.relationships, other.relationships),
            formative_experiences=merge_lists(self.formative_experiences, other.formative_experiences),
            social_connections=merge_lists(self.social_connections, other.social_connections),
            motivations=merge_lists(self.motivations, other.motivations),
            fears=merge_lists(self.fears, other.fears),
            desires=merge_lists(self.desires, other.desires),
            conflicts=merge_lists(self.conflicts, other.conflicts),
            personality_drivers=merge_lists(self.personality_drivers, other.personality_drivers),
            confidence_score=max(self.confidence_score, other.confidence_score),
            text_references=merge_lists(self.text_references, other.text_references),
            first_appearance=merge_strings(self.first_appearance, other.first_appearance),
            importance_score=max(self.importance_score, other.importance_score),
            conceptual_basis=merge_lists(self.conceptual_basis or [], other.conceptual_basis or []),
            content_type=merge_strings(self.content_type or "", other.content_type or ""),
            processing_notes=merge_strings(self.processing_notes or "", other.processing_notes or "")
        )

    def is_conceptual(self) -> bool:
        """
        Check if this is a conceptual character (created from abstract concepts)
        
        Returns:
            True if character is conceptual, False if narrative
        """
        return self.content_type in ["conceptual", "descriptive"]

    def is_narrative(self) -> bool:
        """
        Check if this is a narrative character (extracted from story)
        
        Returns:
            True if character is from narrative, False if conceptual
        """
        return self.content_type == "narrative"

    def get_processing_strategy(self) -> str:
        """
        Get the processing strategy used to create this character
        
        Returns:
            String indicating processing strategy
        """
        if self.is_conceptual():
            return "conceptual_creation"
        elif self.is_narrative():
            return "narrative_extraction"
        else:
            return "unknown"

    def is_complete(self) -> bool:
        """
        Check if the character profile has sufficient information for analysis
        
        Returns:
            True if profile has enough information, False otherwise
        """
        # Must have name
        if not self.name or self.name == "Unknown Character":
            return False

        # For conceptual characters, check if we have conceptual basis
        if self.is_conceptual():
            if not self.conceptual_basis:
                return False

        # Must have at least some information in each layer
        skin_layer_complete = (
            self.physical_description or
            self.mannerisms or
            self.speech_patterns or
            self.behavioral_traits
        )

        flesh_layer_complete = (
            self.backstory or
            self.relationships or
            self.formative_experiences or
            self.social_connections
        )

        core_layer_complete = (
            self.motivations or
            self.fears or
            self.desires or
            self.conflicts or
            self.personality_drivers
        )

        return skin_layer_complete and flesh_layer_complete and core_layer_complete

    def get_summary(self) -> str:
        """
        Get a brief summary of the character profile
        
        Returns:
            String summary of the character
        """
        summary_parts = [f"Character: {self.name}"]

        if self.aliases:
            summary_parts.append(f"Aliases: {', '.join(self.aliases[:3])}")

        if self.backstory:
            backstory_preview = self.backstory[:100] + "..." if len(self.backstory) > 100 else self.backstory
            summary_parts.append(f"Background: {backstory_preview}")

        if self.motivations:
            summary_parts.append(f"Key motivation: {self.motivations[0]}")

        if self.fears:
            summary_parts.append(f"Primary fear: {self.fears[0]}")

        summary_parts.append(f"Confidence: {self.confidence_score:.2f}")

        return " | ".join(summary_parts)

    def __str__(self) -> str:
        """String representation of the character profile"""
        return self.get_summary()

    def __repr__(self) -> str:
        """Detailed representation of the character profile"""
        return f"StandardCharacterProfile(name='{self.name}', confidence={self.confidence_score:.2f}, complete={self.is_complete()})"


# Utility functions for working with character profiles

def create_character_profile_from_text(text: str, name: str = None) -> StandardCharacterProfile:
    """
    Create a basic character profile from text description
    
    This is a simple utility function for quick character profile creation.
    For more sophisticated analysis, use the enhanced character analyzer.
    
    Args:
        text: Text containing character information
        name: Optional character name (will be extracted from text if not provided)
        
    Returns:
        StandardCharacterProfile instance
    """
    import re

    # Extract name if not provided
    if not name:
        # Look for name patterns in text
        name_patterns = [
            r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',  # First Last
            r'\b([A-Z][a-z]+)\b'  # Just first name
        ]

        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1)
                break

        if not name:
            name = "Character from Text"

    # Basic extraction of character information
    backstory = text[:500] if len(text) > 500 else text

    # Simple keyword-based trait extraction
    traits = []
    if re.search(r'\b(quiet|shy|introverted)\b', text, re.IGNORECASE):
        traits.append("introverted")
    if re.search(r'\b(loud|outgoing|extroverted)\b', text, re.IGNORECASE):
        traits.append("extroverted")
    if re.search(r'\b(creative|artistic|imaginative)\b', text, re.IGNORECASE):
        traits.append("creative")

    return StandardCharacterProfile(
        name=name,
        backstory=backstory,
        behavioral_traits=traits,
        text_references=[text[:200] + "..." if len(text) > 200 else text],
        confidence_score=0.7  # Lower confidence for simple extraction
    )


def validate_character_profile_data(data: Dict[str, Any]) -> List[str]:
    """
    Validate character profile data and return list of issues
    
    Args:
        data: Dictionary containing character profile data
        
    Returns:
        List of validation error messages (empty if valid)
    """
    issues = []

    if not isinstance(data, dict):
        issues.append(f"Expected dictionary, got {type(data)}")
        return issues

    # Check required fields
    if 'name' not in data or not data['name']:
        issues.append("Missing required field: 'name'")

    # Check field types
    expected_types = {
        'name': str,
        'aliases': list,
        'physical_description': str,
        'mannerisms': list,
        'speech_patterns': list,
        'behavioral_traits': list,
        'backstory': str,
        'relationships': list,
        'formative_experiences': list,
        'social_connections': list,
        'motivations': list,
        'fears': list,
        'desires': list,
        'conflicts': list,
        'personality_drivers': list,
        'confidence_score': (int, float),
        'text_references': list,
        'first_appearance': str,
        'importance_score': (int, float),
        'conceptual_basis': list,
        'content_type': str,
        'processing_notes': str
    }

    for field, expected_type in expected_types.items():
        if field in data:
            value = data[field]
            if value is not None and not isinstance(value, expected_type):
                issues.append(f"Field '{field}' should be {expected_type}, got {type(value)}")

    # Check score ranges
    for score_field in ['confidence_score', 'importance_score']:
        if score_field in data and data[score_field] is not None:
            score = data[score_field]
            if isinstance(score, (int, float)) and (score < 0 or score > 1):
                issues.append(f"Field '{score_field}' should be between 0 and 1, got {score}")

    return issues
