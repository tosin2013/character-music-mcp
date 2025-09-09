#!/usr/bin/env python3
"""
Format conversion utilities for MCP tools backward compatibility

This module provides utilities to convert between different data formats used
by MCP tools, ensuring backward compatibility while migrating to standardized formats.
"""

import json
import logging
from typing import Any, Dict, List, Tuple

from mcp_data_validation import MCPDataValidator, ValidationResult
from standard_character_profile import StandardCharacterProfile

logger = logging.getLogger(__name__)


class FormatConverter:
    """Utility class for converting between different MCP data formats"""

    def __init__(self):
        self.validator = MCPDataValidator()

    def convert_to_standard_character_profile(
        self,
        data: Any,
        source_format: str = "auto"
    ) -> Tuple[StandardCharacterProfile, ValidationResult]:
        """
        Convert various character profile formats to StandardCharacterProfile

        Args:
            data: Character profile data in any supported format
            source_format: Source format type ("auto", "legacy_simple", "legacy_full", "server_format")

        Returns:
            Tuple of (StandardCharacterProfile, ValidationResult)
        """
        validation_result = ValidationResult()

        try:
            # Handle different input types
            if isinstance(data, StandardCharacterProfile):
                return data, validation_result

            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    validation_result.add_error(
                        field="input",
                        message=f"Invalid JSON string: {e}",
                        suggestion="Ensure input is valid JSON or a dictionary"
                    )
                    return StandardCharacterProfile(name="Invalid Input"), validation_result

            if not isinstance(data, dict):
                validation_result.add_error(
                    field="input",
                    message=f"Expected dictionary or JSON string, got {type(data).__name__}",
                    suggestion="Provide character profile as dictionary or JSON"
                )
                return StandardCharacterProfile(name="Invalid Input"), validation_result

            # Auto-detect format if needed
            if source_format == "auto":
                source_format = self._detect_character_profile_format(data)
                validation_result.add_info(
                    field="format_detection",
                    message=f"Detected format: {source_format}"
                )

            # Convert based on detected/specified format
            if source_format == "legacy_simple":
                converted_data = self._convert_legacy_simple_character_profile(data)
            elif source_format == "legacy_full":
                converted_data = self._convert_legacy_full_character_profile(data)
            elif source_format == "server_format":
                converted_data = self._convert_server_character_profile(data)
            elif source_format == "test_format":
                converted_data = self._convert_test_character_profile(data)
            else:  # "standard" or unknown
                converted_data = data

            # Create StandardCharacterProfile
            character_profile = StandardCharacterProfile.from_dict(converted_data)

            # Validate the result
            profile_validation = self.validator.validate_character_profile(character_profile.to_dict())

            # Merge validation results
            validation_result.issues.extend(profile_validation.issues)
            if not profile_validation.is_valid:
                validation_result.is_valid = False

            return character_profile, validation_result

        except Exception as e:
            logger.error(f"Error converting character profile: {e}")
            validation_result.add_error(
                field="conversion",
                message=f"Conversion failed: {e}",
                suggestion="Check input data format and try again"
            )
            return StandardCharacterProfile(name="Conversion Failed"), validation_result

    def convert_persona_data_format(
        self,
        data: Any,
        target_format: str = "standard"
    ) -> Tuple[Dict[str, Any], ValidationResult]:
        """
        Convert persona data to specified format

        Args:
            data: Persona data in any supported format
            target_format: Target format ("standard", "legacy", "suno_compatible")

        Returns:
            Tuple of (converted_data, ValidationResult)
        """
        validation_result = ValidationResult()

        try:
            # Handle different input types
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    validation_result.add_error(
                        field="input",
                        message=f"Invalid JSON string: {e}",
                        suggestion="Ensure input is valid JSON"
                    )
                    return {}, validation_result

            if not isinstance(data, dict):
                validation_result.add_error(
                    field="input",
                    message=f"Expected dictionary or JSON string, got {type(data).__name__}",
                    suggestion="Provide persona data as dictionary or JSON"
                )
                return {}, validation_result

            # Convert to target format
            if target_format == "standard":
                converted_data = self._convert_to_standard_persona_format(data)
            elif target_format == "legacy":
                converted_data = self._convert_to_legacy_persona_format(data)
            elif target_format == "suno_compatible":
                converted_data = self._convert_to_suno_persona_format(data)
            else:
                converted_data = data
                validation_result.add_warning(
                    field="format",
                    message=f"Unknown target format '{target_format}', using input as-is"
                )

            # Validate the result
            persona_validation = self.validator.validate_persona_data(converted_data)

            # Merge validation results
            validation_result.issues.extend(persona_validation.issues)
            if not persona_validation.is_valid:
                validation_result.is_valid = False

            return converted_data, validation_result

        except Exception as e:
            logger.error(f"Error converting persona data: {e}")
            validation_result.add_error(
                field="conversion",
                message=f"Conversion failed: {e}",
                suggestion="Check input data format and try again"
            )
            return {}, validation_result

    def convert_suno_command_format(
        self,
        data: Any,
        target_format: str = "standard"
    ) -> Tuple[Dict[str, Any], ValidationResult]:
        """
        Convert Suno command data to specified format

        Args:
            data: Suno command data in any supported format
            target_format: Target format ("standard", "simple", "detailed")

        Returns:
            Tuple of (converted_data, ValidationResult)
        """
        validation_result = ValidationResult()

        try:
            # Handle different input types
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    validation_result.add_error(
                        field="input",
                        message=f"Invalid JSON string: {e}",
                        suggestion="Ensure input is valid JSON"
                    )
                    return {}, validation_result

            if isinstance(data, list):
                # Convert list of commands to standard format
                data = {
                    "commands": data,
                    "metadata": {},
                    "character_context": {},
                    "genre_info": {},
                    "generation_notes": []
                }

            if not isinstance(data, dict):
                validation_result.add_error(
                    field="input",
                    message=f"Expected dictionary, list, or JSON string, got {type(data).__name__}",
                    suggestion="Provide Suno command data as dictionary, list, or JSON"
                )
                return {}, validation_result

            # Convert to target format
            if target_format == "standard":
                converted_data = self._convert_to_standard_suno_format(data)
            elif target_format == "simple":
                converted_data = self._convert_to_simple_suno_format(data)
            elif target_format == "detailed":
                converted_data = self._convert_to_detailed_suno_format(data)
            else:
                converted_data = data
                validation_result.add_warning(
                    field="format",
                    message=f"Unknown target format '{target_format}', using input as-is"
                )

            # Validate the result
            suno_validation = self.validator.validate_suno_command_data(converted_data)

            # Merge validation results
            validation_result.issues.extend(suno_validation.issues)
            if not suno_validation.is_valid:
                validation_result.is_valid = False

            return converted_data, validation_result

        except Exception as e:
            logger.error(f"Error converting Suno command data: {e}")
            validation_result.add_error(
                field="conversion",
                message=f"Conversion failed: {e}",
                suggestion="Check input data format and try again"
            )
            return {}, validation_result

    def _detect_character_profile_format(self, data: Dict[str, Any]) -> str:
        """Detect the format of character profile data"""

        # Check for StandardCharacterProfile format
        standard_fields = {
            'name', 'aliases', 'physical_description', 'mannerisms', 'speech_patterns',
            'behavioral_traits', 'backstory', 'relationships', 'formative_experiences',
            'social_connections', 'motivations', 'fears', 'desires', 'conflicts',
            'personality_drivers', 'confidence_score', 'text_references',
            'first_appearance', 'importance_score'
        }

        data_fields = set(data.keys())

        # If most standard fields are present, it's likely standard format
        if len(data_fields.intersection(standard_fields)) >= 10:
            return "standard"

        # Check for server format (has to_dict method signature)
        if 'name' in data and 'aliases' in data and len(data_fields) > 10:
            return "server_format"

        # Check for legacy simple format (just name, backstory, conflicts, fears)
        legacy_simple_fields = {'name', 'backstory', 'conflicts', 'fears'}
        if data_fields.issubset(legacy_simple_fields.union({'aliases'})) and len(data_fields) <= 5:
            return "legacy_simple"

        # Check for test format
        if len(data_fields) <= 6 and 'name' in data:
            return "test_format"

        # Default to legacy full
        return "legacy_full"

    def _convert_legacy_simple_character_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert legacy simple format to standard format"""
        return {
            'name': data.get('name', 'Unknown Character'),
            'aliases': data.get('aliases', []),
            'backstory': data.get('backstory', ''),
            'conflicts': data.get('conflicts', []) if isinstance(data.get('conflicts'), list) else [data.get('conflicts', '')],
            'fears': data.get('fears', []) if isinstance(data.get('fears'), list) else [data.get('fears', '')],
            'confidence_score': 0.8,  # Lower confidence for legacy data
            'text_references': [],
            'first_appearance': '',
            'importance_score': 1.0,
            # Initialize other fields with defaults
            'physical_description': '',
            'mannerisms': [],
            'speech_patterns': [],
            'behavioral_traits': [],
            'relationships': [],
            'formative_experiences': [],
            'social_connections': [],
            'motivations': [],
            'desires': [],
            'personality_drivers': []
        }

    def _convert_legacy_full_character_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert legacy full format to standard format"""
        # Map legacy fields to standard fields
        field_mapping = {
            'character_name': 'name',
            'character_aliases': 'aliases',
            'physical_traits': 'physical_description',
            'behavior_patterns': 'behavioral_traits',
            'background': 'backstory',
            'character_relationships': 'relationships',
            'character_motivations': 'motivations',
            'character_fears': 'fears',
            'character_desires': 'desires',
            'character_conflicts': 'conflicts',
            'personality_traits': 'personality_drivers'
        }

        converted = {}

        # Map known fields
        for legacy_field, standard_field in field_mapping.items():
            if legacy_field in data:
                converted[standard_field] = data[legacy_field]

        # Copy fields that match standard format
        standard_fields = self.validator.character_profile_schema.keys()
        for field in standard_fields:
            if field in data:
                converted[field] = data[field]

        # Ensure required fields
        if 'name' not in converted:
            converted['name'] = data.get('character_name', 'Unknown Character')

        # Set defaults for missing fields
        for field, schema in self.validator.character_profile_schema.items():
            if field not in converted:
                converted[field] = schema.get('default', '' if schema['type'] == str else [])

        return converted

    def _convert_server_character_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert server format to standard format"""
        # Server format is very similar to standard, just ensure all fields are present
        converted = dict(data)  # Copy all existing fields

        # Set defaults for missing fields
        for field, schema in self.validator.character_profile_schema.items():
            if field not in converted:
                converted[field] = schema.get('default', '' if schema['type'] == str else [])

        return converted

    def _convert_test_character_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert test format to standard format"""
        return {
            'name': data.get('name', 'Test Character'),
            'aliases': data.get('aliases', []),
            'backstory': data.get('backstory', ''),
            'conflicts': [data.get('conflicts', '')] if data.get('conflicts') else [],
            'fears': [data.get('fears', '')] if data.get('fears') else [],
            'confidence_score': 0.7,  # Lower confidence for test data
            'text_references': [],
            'first_appearance': '',
            'importance_score': 1.0,
            # Initialize other fields with defaults
            'physical_description': '',
            'mannerisms': [],
            'speech_patterns': [],
            'behavioral_traits': [],
            'relationships': [],
            'formative_experiences': [],
            'social_connections': [],
            'motivations': [],
            'desires': [],
            'personality_drivers': []
        }

    def _convert_to_standard_persona_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert to standard persona format"""
        return {
            'character_name': data.get('character_name', data.get('name', 'Unknown')),
            'artist_persona': data.get('artist_persona', data.get('persona', {})),
            'musical_style': data.get('musical_style', data.get('style', '')),
            'genre_preferences': data.get('genre_preferences', data.get('genres', [])),
            'lyrical_themes': data.get('lyrical_themes', data.get('themes', [])),
            'vocal_characteristics': data.get('vocal_characteristics', data.get('vocals', {})),
            'production_style': data.get('production_style', data.get('production', {})),
            'confidence_score': data.get('confidence_score', data.get('confidence', 1.0))
        }

    def _convert_to_legacy_persona_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert to legacy persona format"""
        return {
            'name': data.get('character_name', 'Unknown'),
            'persona': data.get('artist_persona', {}),
            'style': data.get('musical_style', ''),
            'genres': data.get('genre_preferences', []),
            'themes': data.get('lyrical_themes', [])
        }

    def _convert_to_suno_persona_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert to Suno-compatible persona format"""
        return {
            'character_name': data.get('character_name', 'Unknown'),
            'artist_persona': data.get('artist_persona', {}),
            'musical_style': data.get('musical_style', ''),
            'genre_preferences': data.get('genre_preferences', []),
            'lyrical_themes': data.get('lyrical_themes', []),
            'vocal_characteristics': data.get('vocal_characteristics', {}),
            'production_style': data.get('production_style', {}),
            'suno_tags': self._extract_suno_tags(data),
            'confidence_score': data.get('confidence_score', 1.0)
        }

    def _convert_to_standard_suno_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert to standard Suno command format"""
        return {
            'commands': data.get('commands', data.get('suno_commands', [])),
            'metadata': data.get('metadata', {}),
            'character_context': data.get('character_context', data.get('character', {})),
            'genre_info': data.get('genre_info', data.get('genre', {})),
            'generation_notes': data.get('generation_notes', data.get('notes', []))
        }

    def _convert_to_simple_suno_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert to simple Suno command format"""
        return {
            'commands': data.get('commands', [])
        }

    def _convert_to_detailed_suno_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert to detailed Suno command format"""
        return {
            'commands': data.get('commands', []),
            'metadata': data.get('metadata', {}),
            'character_context': data.get('character_context', {}),
            'genre_info': data.get('genre_info', {}),
            'generation_notes': data.get('generation_notes', []),
            'technical_details': data.get('technical_details', {}),
            'quality_metrics': data.get('quality_metrics', {}),
            'source_attribution': data.get('source_attribution', {})
        }

    def _extract_suno_tags(self, data: Dict[str, Any]) -> List[str]:
        """Extract Suno-compatible tags from persona data"""
        tags = []

        # Extract from genre preferences
        genres = data.get('genre_preferences', [])
        if isinstance(genres, list):
            tags.extend(genres)

        # Extract from musical style
        style = data.get('musical_style', '')
        if style:
            tags.append(style)

        # Extract from vocal characteristics
        vocals = data.get('vocal_characteristics', {})
        if isinstance(vocals, dict):
            for key, value in vocals.items():
                if isinstance(value, str) and value:
                    tags.append(f"{key}:{value}")

        return list(set(tags))  # Remove duplicates


# Convenience functions

def convert_character_profile(data: Any, source_format: str = "auto") -> Tuple[StandardCharacterProfile, ValidationResult]:
    """Quick character profile conversion"""
    converter = FormatConverter()
    return converter.convert_to_standard_character_profile(data, source_format)


def convert_persona_data(data: Any, target_format: str = "standard") -> Tuple[Dict[str, Any], ValidationResult]:
    """Quick persona data conversion"""
    converter = FormatConverter()
    return converter.convert_persona_data_format(data, target_format)


def convert_suno_commands(data: Any, target_format: str = "standard") -> Tuple[Dict[str, Any], ValidationResult]:
    """Quick Suno command conversion"""
    converter = FormatConverter()
    return converter.convert_suno_command_format(data, target_format)


def ensure_standard_character_profile(data: Any) -> StandardCharacterProfile:
    """
    Ensure data is converted to StandardCharacterProfile, raising exception on failure

    Args:
        data: Character profile data in any format

    Returns:
        StandardCharacterProfile instance

    Raises:
        ValueError: If conversion fails
    """
    profile, validation_result = convert_character_profile(data)

    if not validation_result.is_valid:
        error_messages = [issue.message for issue in validation_result.get_errors()]
        raise ValueError(f"Character profile conversion failed: {'; '.join(error_messages)}")

    return profile


def ensure_valid_persona_data(data: Any) -> Dict[str, Any]:
    """
    Ensure data is converted to valid persona format, raising exception on failure

    Args:
        data: Persona data in any format

    Returns:
        Valid persona data dictionary

    Raises:
        ValueError: If conversion fails
    """
    persona_data, validation_result = convert_persona_data(data)

    if not validation_result.is_valid:
        error_messages = [issue.message for issue in validation_result.get_errors()]
        raise ValueError(f"Persona data conversion failed: {'; '.join(error_messages)}")

    return persona_data


def ensure_valid_suno_commands(data: Any) -> Dict[str, Any]:
    """
    Ensure data is converted to valid Suno command format, raising exception on failure

    Args:
        data: Suno command data in any format

    Returns:
        Valid Suno command data dictionary

    Raises:
        ValueError: If conversion fails
    """
    suno_data, validation_result = convert_suno_commands(data)

    if not validation_result.is_valid:
        error_messages = [issue.message for issue in validation_result.get_errors()]
        raise ValueError(f"Suno command conversion failed: {'; '.join(error_messages)}")

    return suno_data
