#!/usr/bin/env python3
"""
Standardized input validation system for MCP tools

This module provides consistent validation functions for character profiles, persona data,
and other data structures used across MCP tools. It ensures format consistency and provides
helpful error messages for debugging.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple, Type
from enum import Enum
import re

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    severity: ValidationSeverity
    field: str
    message: str
    expected_type: Optional[str] = None
    actual_type: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of data validation"""
    is_valid: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)
    
    def add_error(self, field: str, message: str, expected_type: str = None, 
                  actual_type: str = None, suggestion: str = None) -> None:
        """Add validation error"""
        self.issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR,
            field=field,
            message=message,
            expected_type=expected_type,
            actual_type=actual_type,
            suggestion=suggestion
        ))
        self.is_valid = False
    
    def add_warning(self, field: str, message: str, suggestion: str = None) -> None:
        """Add validation warning"""
        self.issues.append(ValidationIssue(
            severity=ValidationSeverity.WARNING,
            field=field,
            message=message,
            suggestion=suggestion
        ))
    
    def add_info(self, field: str, message: str) -> None:
        """Add validation info"""
        self.issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            field=field,
            message=message
        ))
    
    def get_errors(self) -> List[ValidationIssue]:
        """Get only error-level issues"""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.ERROR]
    
    def get_warnings(self) -> List[ValidationIssue]:
        """Get only warning-level issues"""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.WARNING]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'is_valid': self.is_valid,
            'error_count': len(self.get_errors()),
            'warning_count': len(self.get_warnings()),
            'issues': [
                {
                    'severity': issue.severity.value,
                    'field': issue.field,
                    'message': issue.message,
                    'expected_type': issue.expected_type,
                    'actual_type': issue.actual_type,
                    'suggestion': issue.suggestion
                }
                for issue in self.issues
            ]
        }
    
    def get_summary(self) -> str:
        """Get human-readable summary of validation results"""
        if self.is_valid:
            warning_count = len(self.get_warnings())
            if warning_count > 0:
                return f"Valid with {warning_count} warnings"
            return "Valid"
        
        error_count = len(self.get_errors())
        warning_count = len(self.get_warnings())
        return f"Invalid: {error_count} errors, {warning_count} warnings"


class MCPDataValidator:
    """Centralized validator for all MCP tool data structures"""
    
    def __init__(self):
        self.character_profile_schema = self._get_character_profile_schema()
        self.persona_data_schema = self._get_persona_data_schema()
        self.suno_command_schema = self._get_suno_command_schema()
    
    def validate_character_profile(self, data: Any) -> ValidationResult:
        """
        Validate character profile data structure
        
        Args:
            data: Character profile data to validate
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult()
        
        # Basic type check
        if not isinstance(data, dict):
            result.add_error(
                field="root",
                message=f"Character profile must be a dictionary, got {type(data).__name__}",
                expected_type="dict",
                actual_type=type(data).__name__,
                suggestion="Ensure character profile is passed as a dictionary/JSON object"
            )
            return result
        
        # Validate against schema
        self._validate_against_schema(data, self.character_profile_schema, result, "character_profile")
        
        # Additional character-specific validations
        self._validate_character_profile_content(data, result)
        
        return result
    
    def validate_persona_data(self, data: Any) -> ValidationResult:
        """
        Validate persona data structure
        
        Args:
            data: Persona data to validate
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult()
        
        # Basic type check
        if not isinstance(data, dict):
            result.add_error(
                field="root",
                message=f"Persona data must be a dictionary, got {type(data).__name__}",
                expected_type="dict",
                actual_type=type(data).__name__,
                suggestion="Ensure persona data is passed as a dictionary/JSON object"
            )
            return result
        
        # Validate against schema
        self._validate_against_schema(data, self.persona_data_schema, result, "persona_data")
        
        # Additional persona-specific validations
        self._validate_persona_data_content(data, result)
        
        return result
    
    def validate_suno_command_data(self, data: Any) -> ValidationResult:
        """
        Validate Suno command data structure
        
        Args:
            data: Suno command data to validate
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult()
        
        # Basic type check
        if not isinstance(data, dict):
            result.add_error(
                field="root",
                message=f"Suno command data must be a dictionary, got {type(data).__name__}",
                expected_type="dict",
                actual_type=type(data).__name__,
                suggestion="Ensure Suno command data is passed as a dictionary/JSON object"
            )
            return result
        
        # Validate against schema
        self._validate_against_schema(data, self.suno_command_schema, result, "suno_command")
        
        # Additional Suno-specific validations
        self._validate_suno_command_content(data, result)
        
        return result
    
    def validate_text_input(self, text: Any, min_length: int = 10, max_length: int = 50000) -> ValidationResult:
        """
        Validate text input for analysis tools
        
        Args:
            text: Text to validate
            min_length: Minimum required text length
            max_length: Maximum allowed text length
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult()
        
        # Type check
        if not isinstance(text, str):
            result.add_error(
                field="text",
                message=f"Text input must be a string, got {type(text).__name__}",
                expected_type="str",
                actual_type=type(text).__name__,
                suggestion="Ensure text is passed as a string"
            )
            return result
        
        # Length checks
        text_length = len(text.strip())
        
        if text_length == 0:
            result.add_error(
                field="text",
                message="Text input cannot be empty",
                suggestion="Provide meaningful text content for analysis"
            )
        elif text_length < min_length:
            result.add_warning(
                field="text",
                message=f"Text is very short ({text_length} characters, minimum recommended: {min_length})",
                suggestion="Consider providing more detailed text for better analysis"
            )
        elif text_length > max_length:
            result.add_error(
                field="text",
                message=f"Text is too long ({text_length} characters, maximum: {max_length})",
                suggestion="Consider breaking text into smaller chunks"
            )
        
        # Content quality checks
        if text.strip().count(' ') < 5:
            result.add_warning(
                field="text",
                message="Text appears to be very short or single words",
                suggestion="Provide complete sentences or paragraphs for better analysis"
            )
        
        return result
    
    def validate_genre_specification(self, genre: Any) -> ValidationResult:
        """
        Validate genre specification
        
        Args:
            genre: Genre specification to validate
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult()
        
        if genre is None:
            result.add_info("genre", "No genre specified, will use default/inferred genre")
            return result
        
        if not isinstance(genre, str):
            result.add_error(
                field="genre",
                message=f"Genre must be a string, got {type(genre).__name__}",
                expected_type="str",
                actual_type=type(genre).__name__,
                suggestion="Provide genre as a string (e.g., 'hip-hop', 'folk', 'electronic')"
            )
            return result
        
        genre = genre.strip().lower()
        
        if not genre:
            result.add_warning(
                field="genre",
                message="Genre specification is empty",
                suggestion="Provide a specific genre for better results"
            )
        elif len(genre) < 3:
            result.add_warning(
                field="genre",
                message="Genre specification is very short",
                suggestion="Provide a more specific genre description"
            )
        
        return result
    
    def validate_content_type_detection(self, content: str, detected_type: str) -> ValidationResult:
        """
        Validate content type detection results
        
        Args:
            content: Original content that was analyzed
            detected_type: The detected content type
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult()
        
        # Validate detected type is one of the known types
        known_types = {
            "narrative_fiction", "character_description", "philosophical_conceptual",
            "poetic_content", "mixed_content", "unknown"
        }
        
        if detected_type not in known_types:
            result.add_error(
                field="detected_type",
                message=f"Unknown content type detected: {detected_type}",
                suggestion=f"Content type should be one of: {', '.join(known_types)}"
            )
        
        # Validate content length for type detection reliability
        content_length = len(content.strip()) if content else 0
        
        if content_length < 50:
            result.add_warning(
                field="content_length",
                message="Content is very short for reliable type detection",
                suggestion="Provide more content for better type detection accuracy"
            )
        
        # Type-specific validations
        if detected_type == "character_description":
            if not any(indicator in content.lower() for indicator in 
                      ["character:", "protagonist:", "artist:", "musician:", "year-old", "born in"]):
                result.add_warning(
                    field="character_indicators",
                    message="Content detected as character description but lacks clear character indicators",
                    suggestion="Verify content actually contains character descriptions"
                )
        
        elif detected_type == "narrative_fiction":
            if not any(indicator in content.lower() for indicator in 
                      ["story", "character", "protagonist", "narrative", "plot"]):
                result.add_warning(
                    field="narrative_indicators",
                    message="Content detected as narrative fiction but lacks clear narrative indicators",
                    suggestion="Verify content actually contains narrative elements"
                )
        
        elif detected_type == "philosophical_conceptual":
            if not any(indicator in content.lower() for indicator in 
                      ["philosophy", "concept", "theory", "abstract", "meaning", "existence"]):
                result.add_warning(
                    field="philosophical_indicators",
                    message="Content detected as philosophical but lacks clear philosophical indicators",
                    suggestion="Verify content actually contains philosophical concepts"
                )
        
        return result
    
    def validate_workflow_state(self, workflow_state: Dict[str, Any]) -> ValidationResult:
        """
        Validate workflow state structure and completeness
        
        Args:
            workflow_state: Workflow state dictionary to validate
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult()
        
        # Check required workflow state fields
        required_fields = ["steps_completed", "steps_failed", "partial_results", "overall_success"]
        
        for field in required_fields:
            if field not in workflow_state:
                result.add_error(
                    field=field,
                    message=f"Required workflow state field '{field}' is missing",
                    suggestion=f"Add '{field}' to workflow state"
                )
        
        # Validate steps_completed
        if "steps_completed" in workflow_state:
            steps_completed = workflow_state["steps_completed"]
            if not isinstance(steps_completed, list):
                result.add_error(
                    field="steps_completed",
                    message="steps_completed must be a list",
                    expected_type="list",
                    actual_type=type(steps_completed).__name__
                )
            else:
                valid_steps = {
                    "content_detection", "character_analysis", "persona_generation", 
                    "album_generation", "command_generation"
                }
                for step in steps_completed:
                    if step not in valid_steps:
                        result.add_warning(
                            field="steps_completed",
                            message=f"Unknown step '{step}' in completed steps",
                            suggestion=f"Valid steps are: {', '.join(valid_steps)}"
                        )
        
        # Validate partial_results structure
        if "partial_results" in workflow_state:
            partial_results = workflow_state["partial_results"]
            if not isinstance(partial_results, dict):
                result.add_error(
                    field="partial_results",
                    message="partial_results must be a dictionary",
                    expected_type="dict",
                    actual_type=type(partial_results).__name__
                )
            else:
                # Check for expected result types
                expected_results = ["analysis", "personas", "album", "commands"]
                for result_type in expected_results:
                    if result_type in partial_results:
                        if not isinstance(partial_results[result_type], dict):
                            result.add_warning(
                                field=f"partial_results.{result_type}",
                                message=f"{result_type} result should be a dictionary",
                                suggestion=f"Ensure {result_type} result is properly structured"
                            )
        
        return result
    
    def validate_processing_strategy(self, content_type: str, strategy_name: str) -> ValidationResult:
        """
        Validate that processing strategy matches content type
        
        Args:
            content_type: Detected content type
            strategy_name: Name of processing strategy being used
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult()
        
        # Define expected strategies for each content type
        strategy_mapping = {
            "narrative_fiction": "_process_narrative_content",
            "character_description": "_process_character_description", 
            "philosophical_conceptual": "_process_conceptual_content",
            "poetic_content": "_process_poetic_content",
            "mixed_content": "_process_mixed_content"
        }
        
        expected_strategy = strategy_mapping.get(content_type)
        
        if expected_strategy and strategy_name != expected_strategy:
            result.add_warning(
                field="strategy_alignment",
                message=f"Strategy '{strategy_name}' may not be optimal for content type '{content_type}'",
                suggestion=f"Consider using '{expected_strategy}' for {content_type} content"
            )
        
        if not strategy_name.startswith("_process_"):
            result.add_warning(
                field="strategy_naming",
                message=f"Strategy name '{strategy_name}' doesn't follow expected naming convention",
                suggestion="Strategy names should start with '_process_'"
            )
        
        return result
    
    def _get_character_profile_schema(self) -> Dict[str, Any]:
        """Get character profile validation schema"""
        return {
            'name': {'type': str, 'required': True, 'min_length': 1},
            'aliases': {'type': list, 'required': False, 'default': []},
            'physical_description': {'type': str, 'required': False, 'default': ''},
            'mannerisms': {'type': list, 'required': False, 'default': []},
            'speech_patterns': {'type': list, 'required': False, 'default': []},
            'behavioral_traits': {'type': list, 'required': False, 'default': []},
            'backstory': {'type': str, 'required': False, 'default': ''},
            'relationships': {'type': list, 'required': False, 'default': []},
            'formative_experiences': {'type': list, 'required': False, 'default': []},
            'social_connections': {'type': list, 'required': False, 'default': []},
            'motivations': {'type': list, 'required': False, 'default': []},
            'fears': {'type': list, 'required': False, 'default': []},
            'desires': {'type': list, 'required': False, 'default': []},
            'conflicts': {'type': list, 'required': False, 'default': []},
            'personality_drivers': {'type': list, 'required': False, 'default': []},
            'confidence_score': {'type': (int, float), 'required': False, 'default': 1.0, 'min': 0.0, 'max': 1.0},
            'text_references': {'type': list, 'required': False, 'default': []},
            'first_appearance': {'type': str, 'required': False, 'default': ''},
            'importance_score': {'type': (int, float), 'required': False, 'default': 1.0, 'min': 0.0, 'max': 1.0}
        }
    
    def _get_persona_data_schema(self) -> Dict[str, Any]:
        """Get persona data validation schema"""
        return {
            'character_name': {'type': str, 'required': True, 'min_length': 1},
            'artist_persona': {'type': dict, 'required': True},
            'musical_style': {'type': str, 'required': False, 'default': ''},
            'genre_preferences': {'type': list, 'required': False, 'default': []},
            'lyrical_themes': {'type': list, 'required': False, 'default': []},
            'vocal_characteristics': {'type': dict, 'required': False, 'default': {}},
            'production_style': {'type': dict, 'required': False, 'default': {}},
            'confidence_score': {'type': (int, float), 'required': False, 'default': 1.0, 'min': 0.0, 'max': 1.0}
        }
    
    def _get_suno_command_schema(self) -> Dict[str, Any]:
        """Get Suno command validation schema"""
        return {
            'commands': {'type': list, 'required': True, 'min_length': 1},
            'metadata': {'type': dict, 'required': False, 'default': {}},
            'character_context': {'type': dict, 'required': False, 'default': {}},
            'genre_info': {'type': dict, 'required': False, 'default': {}},
            'generation_notes': {'type': list, 'required': False, 'default': []}
        }
    
    def _validate_against_schema(self, data: Dict[str, Any], schema: Dict[str, Any], 
                                result: ValidationResult, context: str) -> None:
        """Validate data against schema definition"""
        
        # Check required fields
        for field_name, field_schema in schema.items():
            if field_schema.get('required', False) and field_name not in data:
                result.add_error(
                    field=field_name,
                    message=f"Required field '{field_name}' is missing",
                    suggestion=f"Add '{field_name}' field to {context}"
                )
                continue
            
            if field_name not in data:
                continue  # Optional field not present
            
            value = data[field_name]
            expected_type = field_schema['type']
            
            # Type validation
            if not isinstance(value, expected_type):
                result.add_error(
                    field=field_name,
                    message=f"Field '{field_name}' has incorrect type",
                    expected_type=str(expected_type),
                    actual_type=type(value).__name__,
                    suggestion=f"Ensure '{field_name}' is of type {expected_type}"
                )
                continue
            
            # Additional validations based on type
            if isinstance(value, str):
                min_length = field_schema.get('min_length', 0)
                if len(value.strip()) < min_length:
                    if min_length > 0:
                        result.add_error(
                            field=field_name,
                            message=f"Field '{field_name}' is too short (minimum length: {min_length})",
                            suggestion=f"Provide meaningful content for '{field_name}'"
                        )
            
            elif isinstance(value, list):
                min_length = field_schema.get('min_length', 0)
                if len(value) < min_length:
                    result.add_error(
                        field=field_name,
                        message=f"Field '{field_name}' has too few items (minimum: {min_length})",
                        suggestion=f"Provide at least {min_length} items for '{field_name}'"
                    )
            
            elif isinstance(value, (int, float)):
                min_val = field_schema.get('min')
                max_val = field_schema.get('max')
                
                if min_val is not None and value < min_val:
                    result.add_error(
                        field=field_name,
                        message=f"Field '{field_name}' is below minimum value ({min_val})",
                        suggestion=f"Set '{field_name}' to at least {min_val}"
                    )
                
                if max_val is not None and value > max_val:
                    result.add_error(
                        field=field_name,
                        message=f"Field '{field_name}' exceeds maximum value ({max_val})",
                        suggestion=f"Set '{field_name}' to at most {max_val}"
                    )
    
    def _validate_character_profile_content(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Additional content validation for character profiles"""
        
        # Check for meaningful character information
        name = data.get('name', '').strip()
        if name.lower() in ['unknown', 'character', 'unknown character', 'test', 'example']:
            result.add_warning(
                field="name",
                message="Character name appears to be a placeholder",
                suggestion="Provide a specific character name for better analysis"
            )
        
        # Check for three-layer completeness
        skin_fields = ['physical_description', 'mannerisms', 'speech_patterns', 'behavioral_traits']
        flesh_fields = ['backstory', 'relationships', 'formative_experiences', 'social_connections']
        core_fields = ['motivations', 'fears', 'desires', 'conflicts', 'personality_drivers']
        
        skin_complete = any(data.get(field) for field in skin_fields)
        flesh_complete = any(data.get(field) for field in flesh_fields)
        core_complete = any(data.get(field) for field in core_fields)
        
        if not skin_complete:
            result.add_warning(
                field="skin_layer",
                message="Skin layer (observable characteristics) is incomplete",
                suggestion="Add physical description, mannerisms, speech patterns, or behavioral traits"
            )
        
        if not flesh_complete:
            result.add_warning(
                field="flesh_layer",
                message="Flesh layer (background/relationships) is incomplete",
                suggestion="Add backstory, relationships, formative experiences, or social connections"
            )
        
        if not core_complete:
            result.add_warning(
                field="core_layer",
                message="Core layer (psychology) is incomplete",
                suggestion="Add motivations, fears, desires, conflicts, or personality drivers"
            )
    
    def _validate_persona_data_content(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Additional content validation for persona data"""
        
        # Check artist persona structure
        artist_persona = data.get('artist_persona', {})
        if not isinstance(artist_persona, dict):
            result.add_error(
                field="artist_persona",
                message="Artist persona must be a dictionary",
                expected_type="dict",
                actual_type=type(artist_persona).__name__
            )
        elif not artist_persona:
            result.add_warning(
                field="artist_persona",
                message="Artist persona is empty",
                suggestion="Provide artist persona details for better music generation"
            )
        
        # Check for meaningful musical information
        musical_style = data.get('musical_style', '').strip()
        if not musical_style:
            result.add_warning(
                field="musical_style",
                message="No musical style specified",
                suggestion="Specify musical style for better genre matching"
            )
    
    def _validate_suno_command_content(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Additional content validation for Suno commands"""
        
        commands = data.get('commands', [])
        if not commands:
            result.add_error(
                field="commands",
                message="No Suno commands provided",
                suggestion="Generate at least one Suno command"
            )
        else:
            # Validate individual commands
            for i, command in enumerate(commands):
                if not isinstance(command, str):
                    result.add_error(
                        field=f"commands[{i}]",
                        message=f"Command {i} must be a string",
                        expected_type="str",
                        actual_type=type(command).__name__
                    )
                elif not command.strip():
                    result.add_error(
                        field=f"commands[{i}]",
                        message=f"Command {i} is empty",
                        suggestion="Provide meaningful Suno command content"
                    )


# Convenience functions for common validation scenarios

def validate_character_profile(data: Any) -> ValidationResult:
    """Quick character profile validation"""
    validator = MCPDataValidator()
    return validator.validate_character_profile(data)


def validate_persona_data(data: Any) -> ValidationResult:
    """Quick persona data validation"""
    validator = MCPDataValidator()
    return validator.validate_persona_data(data)


def validate_text_input(text: Any, min_length: int = 10) -> ValidationResult:
    """Quick text input validation"""
    validator = MCPDataValidator()
    return validator.validate_text_input(text, min_length=min_length)


def validate_suno_commands(data: Any) -> ValidationResult:
    """Quick Suno command validation"""
    validator = MCPDataValidator()
    return validator.validate_suno_command_data(data)


def validate_content_type_detection(content: str, detected_type: str) -> ValidationResult:
    """Quick content type detection validation"""
    validator = MCPDataValidator()
    return validator.validate_content_type_detection(content, detected_type)


def validate_workflow_state(workflow_state: Dict[str, Any]) -> ValidationResult:
    """Quick workflow state validation"""
    validator = MCPDataValidator()
    return validator.validate_workflow_state(workflow_state)


def validate_processing_strategy(content_type: str, strategy_name: str) -> ValidationResult:
    """Quick processing strategy validation"""
    validator = MCPDataValidator()
    return validator.validate_processing_strategy(content_type, strategy_name)


# Error handling utilities

class ValidationError(Exception):
    """Exception raised for validation errors"""
    
    def __init__(self, validation_result: ValidationResult):
        self.validation_result = validation_result
        super().__init__(validation_result.get_summary())


def require_valid_data(validation_result: ValidationResult) -> None:
    """Raise ValidationError if data is not valid"""
    if not validation_result.is_valid:
        raise ValidationError(validation_result)


def log_validation_issues(validation_result: ValidationResult, context: str = "") -> None:
    """Log validation issues with appropriate levels"""
    context_prefix = f"[{context}] " if context else ""
    
    for issue in validation_result.issues:
        message = f"{context_prefix}{issue.field}: {issue.message}"
        if issue.suggestion:
            message += f" (Suggestion: {issue.suggestion})"
        
        if issue.severity == ValidationSeverity.ERROR:
            logger.error(message)
        elif issue.severity == ValidationSeverity.WARNING:
            logger.warning(message)
        else:
            logger.info(message)