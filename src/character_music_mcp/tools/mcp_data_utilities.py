#!/usr/bin/env python3
"""
Comprehensive data utilities for MCP tools

This module provides high-level utility functions that combine validation, conversion,
and shared models to create a unified interface for all MCP tools.
"""

import logging
from typing import Any, Dict, List

from mcp_data_validation import (
    MCPDataValidator,
    ValidationError,
    ValidationResult,
    log_validation_issues,
    require_valid_data,
)
from mcp_format_conversion import (
    FormatConverter,
)
from mcp_shared_models import (
    ArtistPersona,
    CharacterAnalysisResult,
    SunoCommand,
    SunoCommandSet,
    calculate_data_quality_score,
    create_analysis_metadata,
    create_default_artist_persona,
    create_emotional_profile,
    create_genre_info,
    serialize_to_json,
)

# Import all the components we've created
from standard_character_profile import StandardCharacterProfile

logger = logging.getLogger(__name__)


class MCPDataManager:
    """
    Centralized data manager for all MCP tools

    This class provides a unified interface for data validation, conversion,
    and manipulation across all MCP tools.
    """

    def __init__(self):
        self.validator = MCPDataValidator()
        self.converter = FormatConverter()
        self._cache = {}

    # ================================================================================================
    # CHARACTER PROFILE OPERATIONS
    # ================================================================================================

    def process_character_input(self, data: Any, source_format: str = "auto") -> StandardCharacterProfile:
        """
        Process character input data and return validated StandardCharacterProfile

        Args:
            data: Character data in any supported format
            source_format: Source format hint

        Returns:
            StandardCharacterProfile instance

        Raises:
            ValidationError: If data is invalid
        """
        try:
            # Convert to standard format
            character_profile, validation_result = self.converter.convert_to_standard_character_profile(
                data, source_format
            )

            # Log any validation issues
            if validation_result.issues:
                log_validation_issues(validation_result, "character_input_processing")

            # Require valid data
            require_valid_data(validation_result)

            return character_profile

        except Exception as e:
            logger.error(f"Failed to process character input: {e}")
            raise ValidationError(ValidationResult()) from e

    def validate_character_completeness(self, character: StandardCharacterProfile) -> Dict[str, Any]:
        """
        Validate character profile completeness and provide improvement suggestions

        Args:
            character: Character profile to validate

        Returns:
            Dictionary with completeness analysis
        """
        completeness_info = {
            'is_complete': character.is_complete(),
            'quality_score': 0.0,
            'missing_layers': [],
            'suggestions': [],
            'strengths': []
        }

        # Calculate quality score
        character_dict = character.to_dict()
        required_fields = ['name', 'backstory', 'motivations', 'fears', 'conflicts']
        completeness_info['quality_score'] = calculate_data_quality_score(character_dict, required_fields)

        # Check three-layer completeness
        skin_fields = ['physical_description', 'mannerisms', 'speech_patterns', 'behavioral_traits']
        flesh_fields = ['backstory', 'relationships', 'formative_experiences', 'social_connections']
        core_fields = ['motivations', 'fears', 'desires', 'conflicts', 'personality_drivers']

        skin_complete = any(getattr(character, field) for field in skin_fields)
        flesh_complete = any(getattr(character, field) for field in flesh_fields)
        core_complete = any(getattr(character, field) for field in core_fields)

        if not skin_complete:
            completeness_info['missing_layers'].append('skin')
            completeness_info['suggestions'].append(
                'Add observable characteristics: physical description, mannerisms, or speech patterns'
            )
        else:
            completeness_info['strengths'].append('Good observable characteristics (skin layer)')

        if not flesh_complete:
            completeness_info['missing_layers'].append('flesh')
            completeness_info['suggestions'].append(
                'Add background information: backstory, relationships, or formative experiences'
            )
        else:
            completeness_info['strengths'].append('Good background information (flesh layer)')

        if not core_complete:
            completeness_info['missing_layers'].append('core')
            completeness_info['suggestions'].append(
                'Add psychological depth: motivations, fears, desires, or conflicts'
            )
        else:
            completeness_info['strengths'].append('Good psychological depth (core layer)')

        return completeness_info

    # ================================================================================================
    # PERSONA OPERATIONS
    # ================================================================================================

    def create_artist_persona(self, character: StandardCharacterProfile,
                            genre_hint: str = None,
                            style_preferences: Dict[str, Any] = None) -> ArtistPersona:
        """
        Create artist persona from character profile

        Args:
            character: Source character profile
            genre_hint: Optional genre hint
            style_preferences: Optional style preferences

        Returns:
            ArtistPersona instance
        """
        # Start with default persona
        persona = create_default_artist_persona(character)

        # Apply genre hint if provided
        if genre_hint:
            persona.genre_info = create_genre_info(genre_hint, confidence=0.8)

        # Apply style preferences if provided
        if style_preferences:
            if 'vocal_style' in style_preferences:
                from mcp_shared_models import VocalCharacteristics
                persona.vocal_characteristics = VocalCharacteristics(
                    style=style_preferences['vocal_style']
                )

            if 'lyrical_themes' in style_preferences:
                persona.lyrical_themes.extend(style_preferences['lyrical_themes'])

            if 'musical_influences' in style_preferences:
                persona.musical_influences = style_preferences['musical_influences']

        return persona

    def validate_persona_consistency(self, character: StandardCharacterProfile,
                                   persona: ArtistPersona) -> Dict[str, Any]:
        """
        Validate consistency between character and persona

        Args:
            character: Character profile
            persona: Artist persona

        Returns:
            Consistency analysis
        """
        from mcp_shared_models import validate_character_persona_alignment
        return validate_character_persona_alignment(character, persona)

    # ================================================================================================
    # SUNO COMMAND OPERATIONS
    # ================================================================================================

    def create_suno_commands(self, persona: ArtistPersona,
                           command_count: int = 3,
                           command_type: str = "generate") -> SunoCommandSet:
        """
        Create Suno commands from artist persona with genre-specific production intelligence

        Args:
            persona: Artist persona
            command_count: Number of commands to generate
            command_type: Type of commands to generate

        Returns:
            SunoCommandSet instance
        """
        commands = []

        # Try to use genre intelligence for enhanced commands
        try:
            from genre_production_intelligence import get_genre_intelligence
            genre_intelligence = get_genre_intelligence()
            use_enhanced = True
        except ImportError:
            logger.warning("Genre production intelligence not available, using basic command generation")
            use_enhanced = False

        # Generate commands based on persona
        for i in range(command_count):
            if use_enhanced and persona.genre_info:
                # Enhanced command generation with genre intelligence
                base_theme = "life"
                if persona.lyrical_themes and i < len(persona.lyrical_themes):
                    base_theme = persona.lyrical_themes[i]

                base_command = f"Create a song about {base_theme}"

                # Prepare character context
                character_context = {
                    "emotional_state": persona.emotional_profile.primary_emotion.value if persona.emotional_profile else "contemplative",
                    "character_name": persona.character_name,
                    "lyrical_themes": persona.lyrical_themes
                }

                # Enhance with genre intelligence
                enhanced_command = genre_intelligence.enhance_suno_command(
                    base_command, persona.genre_info.primary_genre, character_context
                )

                # Create enhanced SunoCommand
                command = SunoCommand(
                    command_text=enhanced_command["command_text"],
                    command_type=command_type,
                    tags=enhanced_command["style_tags"] + enhanced_command.get("meta_tags", []),
                    description=f"Enhanced {persona.genre_info.primary_genre} command {i+1} for {persona.character_name}",
                    parameters={
                        "tempo_bpm": enhanced_command.get("tempo_suggestion", 120),
                        "tempo_description": enhanced_command.get("tempo_description", "moderate"),
                        "instrumentation": enhanced_command.get("instrumentation", []),
                        "production_notes": enhanced_command.get("production_notes", []),
                        "vocal_direction": enhanced_command.get("vocal_direction", "expressive vocals"),
                        "genre_profile": enhanced_command.get("genre_profile", {})
                    }
                )
            else:
                # Basic command generation (fallback)
                command_parts = []

                # Add genre information
                if persona.genre_info:
                    command_parts.append(f"[{persona.genre_info.primary_genre}]")

                # Add vocal characteristics
                if persona.vocal_characteristics and persona.vocal_characteristics.style:
                    command_parts.append(f"[{persona.vocal_characteristics.style} vocals]")

                # Add emotional context
                if persona.emotional_profile:
                    command_parts.append(f"[{persona.emotional_profile.primary_emotion.value}]")

                # Add lyrical theme
                if persona.lyrical_themes and i < len(persona.lyrical_themes):
                    theme = persona.lyrical_themes[i]
                    command_parts.append(f"about {theme}")

                command_text = " ".join(command_parts) if command_parts else f"Generate music for {persona.character_name}"

                # Create tags
                tags = []
                if persona.genre_info:
                    tags.append(persona.genre_info.primary_genre)
                    tags.extend(persona.genre_info.sub_genres)

                if persona.lyrical_themes:
                    tags.extend(persona.lyrical_themes[:2])  # Limit to first 2 themes

                command = SunoCommand(
                    command_text=command_text,
                    command_type=command_type,
                    tags=tags,
                    description=f"Command {i+1} for {persona.character_name}"
                )

            commands.append(command)

        # Create metadata
        metadata = create_analysis_metadata(
            "enhanced_suno_command_generator" if use_enhanced else "suno_command_generator",
            confidence=persona.confidence_score
        )

        generation_notes = [f"Generated {command_count} {'enhanced' if use_enhanced else 'basic'} commands for {persona.character_name}"]
        if use_enhanced and persona.genre_info:
            generation_notes.append(f"Applied {persona.genre_info.primary_genre} genre-specific production intelligence")

        return SunoCommandSet(
            commands=commands,
            metadata=metadata,
            character_context=persona.source_character,
            artist_persona=persona,
            genre_info=persona.genre_info,
            generation_notes=generation_notes
        )

    # Note: Suno command validation is handled by mcp_data_validation.py
    # Use validator.validate_suno_command_data() directly

    # ================================================================================================
    # TEXT ANALYSIS OPERATIONS
    # ================================================================================================

    def analyze_text_for_characters(self, text: str) -> CharacterAnalysisResult:
        """
        Analyze text and extract character information

        Args:
            text: Text to analyze

        Returns:
            CharacterAnalysisResult
        """
        # Validate text input
        text_validation = self.validator.validate_text_input(text)
        if not text_validation.is_valid:
            logger.warning("Text validation issues found")
            log_validation_issues(text_validation, "text_analysis")

        # For now, create a basic analysis result
        # In a full implementation, this would use the enhanced character analyzer
        metadata = create_analysis_metadata(
            "text_analyzer",
            confidence=0.7,
            source_text_length=len(text)
        )

        # Create a basic character from text
        from standard_character_profile import create_character_profile_from_text
        character = create_character_profile_from_text(text)

        # Create basic emotional profile
        emotional_profile = create_emotional_profile("contemplative", intensity=0.6)

        return CharacterAnalysisResult(
            characters=[character],
            narrative_themes=["character development", "personal journey"],
            emotional_arc=emotional_profile,
            setting_info={"source": "text_analysis"},
            metadata=metadata
        )

    # ================================================================================================
    # WORKFLOW OPERATIONS
    # ================================================================================================

    def execute_complete_workflow(self, text: str, genre_hint: str = None) -> Dict[str, Any]:
        """
        Execute complete workflow from text to Suno commands

        Args:
            text: Input text for analysis
            genre_hint: Optional genre hint

        Returns:
            Complete workflow results
        """
        workflow_results = {
            'success': False,
            'steps_completed': [],
            'results': {},
            'errors': []
        }

        try:
            # Step 1: Analyze text for characters
            logger.info("Step 1: Analyzing text for characters")
            analysis_result = self.analyze_text_for_characters(text)
            workflow_results['steps_completed'].append('character_analysis')
            workflow_results['results']['character_analysis'] = analysis_result.to_dict()

            if not analysis_result.characters:
                workflow_results['errors'].append("No characters found in text")
                return workflow_results

            # Step 2: Create artist persona
            logger.info("Step 2: Creating artist persona")
            main_character = analysis_result.characters[0]  # Use first character
            persona = self.create_artist_persona(main_character, genre_hint)
            workflow_results['steps_completed'].append('persona_creation')
            workflow_results['results']['artist_persona'] = persona.to_dict()

            # Step 3: Generate Suno commands
            logger.info("Step 3: Generating Suno commands")
            command_set = self.create_suno_commands(persona)
            workflow_results['steps_completed'].append('command_generation')
            workflow_results['results']['suno_commands'] = command_set.to_dict()

            # Step 4: Validate results
            logger.info("Step 4: Validating results")
            command_validation = self.validate_suno_commands(command_set)
            workflow_results['steps_completed'].append('validation')
            workflow_results['results']['validation'] = command_validation.to_dict()

            workflow_results['success'] = True
            logger.info("Complete workflow executed successfully")

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            workflow_results['errors'].append(str(e))

        return workflow_results

    # ================================================================================================
    # UTILITY OPERATIONS
    # ================================================================================================

    def get_data_summary(self, data: Any) -> Dict[str, Any]:
        """
        Get summary information about any MCP data object

        Args:
            data: Data object to summarize

        Returns:
            Summary information
        """
        summary = {
            'type': type(data).__name__,
            'size': 0,
            'quality_score': 0.0,
            'completeness': 'unknown',
            'key_fields': []
        }

        try:
            if isinstance(data, StandardCharacterProfile):
                summary['size'] = len(data.to_dict())
                summary['completeness'] = 'complete' if data.is_complete() else 'incomplete'
                summary['key_fields'] = ['name', 'backstory', 'motivations', 'fears']
                summary['quality_score'] = calculate_data_quality_score(
                    data.to_dict(), summary['key_fields']
                )

            elif isinstance(data, ArtistPersona):
                summary['size'] = len(data.to_dict())
                summary['key_fields'] = ['character_name', 'genre_info', 'lyrical_themes']
                summary['quality_score'] = data.confidence_score

            elif isinstance(data, SunoCommandSet):
                summary['size'] = len(data.commands)
                summary['key_fields'] = ['commands', 'character_context', 'genre_info']
                summary['quality_score'] = data.quality_score

            elif isinstance(data, dict):
                summary['size'] = len(data)
                summary['key_fields'] = list(data.keys())[:5]  # First 5 keys
                summary['quality_score'] = calculate_data_quality_score(data, summary['key_fields'])

        except Exception as e:
            logger.warning(f"Failed to generate summary for {type(data)}: {e}")
            summary['error'] = str(e)

        return summary

    def export_data(self, data: Any, format_type: str = "json") -> str:
        """
        Export data in specified format

        Args:
            data: Data to export
            format_type: Export format ("json", "yaml", "dict")

        Returns:
            Exported data as string
        """
        try:
            if format_type == "json":
                return serialize_to_json(data)
            elif format_type == "dict":
                if hasattr(data, 'to_dict'):
                    return str(data.to_dict())
                else:
                    return str(data)
            else:
                return str(data)
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return f"Export failed: {e}"

    def clear_cache(self) -> None:
        """Clear internal cache"""
        self._cache.clear()
        logger.info("Data manager cache cleared")


# ================================================================================================
# CONVENIENCE FUNCTIONS
# ================================================================================================

# Global instance for convenience
_data_manager = None

def get_data_manager() -> MCPDataManager:
    """Get global data manager instance"""
    global _data_manager
    if _data_manager is None:
        _data_manager = MCPDataManager()
    return _data_manager


def quick_character_analysis(text: str) -> StandardCharacterProfile:
    """Quick character analysis from text"""
    manager = get_data_manager()
    result = manager.analyze_text_for_characters(text)
    return result.characters[0] if result.characters else StandardCharacterProfile(name="No Character Found")


def quick_persona_creation(character_data: Any, genre: str = None) -> ArtistPersona:
    """Quick persona creation from character data"""
    manager = get_data_manager()
    character = manager.process_character_input(character_data)
    return manager.create_artist_persona(character, genre)


def quick_suno_generation(persona_data: Any) -> List[str]:
    """Quick Suno command generation"""
    manager = get_data_manager()

    if isinstance(persona_data, ArtistPersona):
        persona = persona_data
    else:
        # Try to convert to persona
        character = manager.process_character_input(persona_data)
        persona = manager.create_artist_persona(character)

    command_set = manager.create_suno_commands(persona)
    return [cmd.command_text for cmd in command_set.commands]


# Note: Workflow validation is handled by mcp_data_validation.py
# Use MCPDataValidator methods directly for individual validations


def get_workflow_summary(workflow_results: Dict[str, Any]) -> str:
    """Get human-readable summary of workflow results"""
    if not workflow_results.get('success', False):
        errors = workflow_results.get('errors', [])
        return f"Workflow failed. Errors: {'; '.join(errors)}"

    steps = workflow_results.get('steps_completed', [])
    results = workflow_results.get('results', {})

    summary_parts = [f"Workflow completed successfully ({len(steps)} steps)"]

    if 'character_analysis' in results:
        char_count = len(results['character_analysis'].get('characters', []))
        summary_parts.append(f"Found {char_count} character(s)")

    if 'suno_commands' in results:
        cmd_count = len(results['suno_commands'].get('commands', []))
        summary_parts.append(f"Generated {cmd_count} Suno command(s)")

    return ". ".join(summary_parts)


# ================================================================================================
# ERROR HANDLING DECORATORS
# ================================================================================================

def handle_mcp_errors(func):
    """Decorator to handle common MCP data errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.error(f"Validation error in {func.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise ValidationError(ValidationResult()) from e
    return wrapper


def log_mcp_operation(operation_name: str):
    """Decorator to log MCP operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"Starting {operation_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed {operation_name} successfully")
                return result
            except Exception as e:
                logger.error(f"Failed {operation_name}: {e}")
                raise
        return wrapper
    return decorator
