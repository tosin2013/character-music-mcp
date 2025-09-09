#!/usr/bin/env python3
"""
Shared data models and utilities for MCP tools

This module provides reusable data structures and utility functions that ensure
all MCP tools use compatible data formats and consistent interfaces.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from standard_character_profile import StandardCharacterProfile

logger = logging.getLogger(__name__)


# ================================================================================================
# ENUMS AND CONSTANTS
# ================================================================================================

class AnalysisConfidence(Enum):
    """Confidence levels for analysis results"""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95


class GenreCategory(Enum):
    """Major genre categories for music classification"""
    ROCK = "rock"
    POP = "pop"
    HIP_HOP = "hip-hop"
    ELECTRONIC = "electronic"
    FOLK = "folk"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    COUNTRY = "country"
    R_AND_B = "r&b"
    ALTERNATIVE = "alternative"
    EXPERIMENTAL = "experimental"
    OTHER = "other"


class EmotionalState(Enum):
    """Emotional states for character and music analysis"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    ANTICIPATION = "anticipation"
    TRUST = "trust"
    CONTEMPLATIVE = "contemplative"
    MELANCHOLIC = "melancholic"
    ENERGETIC = "energetic"
    PEACEFUL = "peaceful"


# ================================================================================================
# SHARED DATA MODELS
# ================================================================================================

@dataclass
class AnalysisMetadata:
    """Metadata for analysis operations"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tool_name: str = ""
    version: str = "1.0"
    confidence_score: float = 1.0
    processing_time_ms: Optional[int] = None
    source_text_length: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class GenreInfo:
    """Information about musical genre"""
    primary_genre: str
    sub_genres: List[str] = field(default_factory=list)
    category: GenreCategory = GenreCategory.OTHER
    confidence_score: float = 1.0
    characteristics: List[str] = field(default_factory=list)
    typical_instruments: List[str] = field(default_factory=list)
    tempo_range: Optional[Tuple[int, int]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['category'] = self.category.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GenreInfo':
        """Create from dictionary"""
        if 'category' in data and isinstance(data['category'], str):
            try:
                data['category'] = GenreCategory(data['category'])
            except ValueError:
                data['category'] = GenreCategory.OTHER
        return cls(**data)


@dataclass
class EmotionalProfile:
    """Emotional profile for characters or music"""
    primary_emotion: EmotionalState
    secondary_emotions: List[EmotionalState] = field(default_factory=list)
    intensity: float = 0.5  # 0.0 to 1.0
    stability: float = 0.5  # How stable/consistent the emotion is
    progression: List[EmotionalState] = field(default_factory=list)  # Emotional arc

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'primary_emotion': self.primary_emotion.value,
            'secondary_emotions': [e.value for e in self.secondary_emotions],
            'intensity': self.intensity,
            'stability': self.stability,
            'progression': [e.value for e in self.progression]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionalProfile':
        """Create from dictionary"""
        primary = EmotionalState(data.get('primary_emotion', 'contemplative'))
        secondary = [EmotionalState(e) for e in data.get('secondary_emotions', [])]
        progression = [EmotionalState(e) for e in data.get('progression', [])]

        return cls(
            primary_emotion=primary,
            secondary_emotions=secondary,
            intensity=data.get('intensity', 0.5),
            stability=data.get('stability', 0.5),
            progression=progression
        )


@dataclass
class VocalCharacteristics:
    """Vocal characteristics for music generation"""
    voice_type: str = ""  # tenor, soprano, baritone, etc.
    style: str = ""  # smooth, raspy, powerful, etc.
    range_description: str = ""
    techniques: List[str] = field(default_factory=list)  # vibrato, falsetto, etc.
    emotional_delivery: str = ""
    accent_or_dialect: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VocalCharacteristics':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ProductionStyle:
    """Production style information"""
    instrumentation: List[str] = field(default_factory=list)
    production_techniques: List[str] = field(default_factory=list)
    sound_characteristics: List[str] = field(default_factory=list)
    mixing_style: str = ""
    effects_usage: List[str] = field(default_factory=list)
    recording_approach: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductionStyle':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ArtistPersona:
    """Complete artist persona for music generation"""
    character_name: str
    stage_name: str = ""
    artistic_identity: str = ""
    musical_influences: List[str] = field(default_factory=list)
    lyrical_themes: List[str] = field(default_factory=list)
    performance_style: str = ""
    target_audience: str = ""
    brand_personality: List[str] = field(default_factory=list)

    # Musical characteristics
    genre_info: Optional[GenreInfo] = None
    vocal_characteristics: Optional[VocalCharacteristics] = None
    production_style: Optional[ProductionStyle] = None
    emotional_profile: Optional[EmotionalProfile] = None

    # Metadata
    confidence_score: float = 1.0
    source_character: Optional[StandardCharacterProfile] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)

        # Handle nested objects
        if self.genre_info:
            data['genre_info'] = self.genre_info.to_dict()
        if self.vocal_characteristics:
            data['vocal_characteristics'] = self.vocal_characteristics.to_dict()
        if self.production_style:
            data['production_style'] = self.production_style.to_dict()
        if self.emotional_profile:
            data['emotional_profile'] = self.emotional_profile.to_dict()
        if self.source_character:
            data['source_character'] = self.source_character.to_dict()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArtistPersona':
        """Create from dictionary"""
        # Handle nested objects
        genre_info = None
        if 'genre_info' in data and data['genre_info']:
            genre_info = GenreInfo.from_dict(data['genre_info'])

        vocal_characteristics = None
        if 'vocal_characteristics' in data and data['vocal_characteristics']:
            vocal_characteristics = VocalCharacteristics.from_dict(data['vocal_characteristics'])

        production_style = None
        if 'production_style' in data and data['production_style']:
            production_style = ProductionStyle.from_dict(data['production_style'])

        emotional_profile = None
        if 'emotional_profile' in data and data['emotional_profile']:
            emotional_profile = EmotionalProfile.from_dict(data['emotional_profile'])

        source_character = None
        if 'source_character' in data and data['source_character']:
            source_character = StandardCharacterProfile.from_dict(data['source_character'])

        # Create instance with basic fields
        basic_fields = {k: v for k, v in data.items()
                       if k in cls.__dataclass_fields__ and k not in
                       ['genre_info', 'vocal_characteristics', 'production_style',
                        'emotional_profile', 'source_character']}

        return cls(
            **basic_fields,
            genre_info=genre_info,
            vocal_characteristics=vocal_characteristics,
            production_style=production_style,
            emotional_profile=emotional_profile,
            source_character=source_character
        )


@dataclass
class SunoCommand:
    """Individual Suno AI command"""
    command_text: str
    command_type: str = "generate"  # generate, extend, remix, etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    description: str = ""
    expected_duration: Optional[int] = None  # seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SunoCommand':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class SunoCommandSet:
    """Set of Suno AI commands with context"""
    commands: List[SunoCommand]
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)
    character_context: Optional[StandardCharacterProfile] = None
    artist_persona: Optional[ArtistPersona] = None
    genre_info: Optional[GenreInfo] = None
    generation_notes: List[str] = field(default_factory=list)
    quality_score: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            'commands': [cmd.to_dict() for cmd in self.commands],
            'metadata': self.metadata.to_dict(),
            'generation_notes': self.generation_notes,
            'quality_score': self.quality_score
        }

        if self.character_context:
            data['character_context'] = self.character_context.to_dict()
        if self.artist_persona:
            data['artist_persona'] = self.artist_persona.to_dict()
        if self.genre_info:
            data['genre_info'] = self.genre_info.to_dict()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SunoCommandSet':
        """Create from dictionary"""
        commands = [SunoCommand.from_dict(cmd) for cmd in data.get('commands', [])]

        metadata = AnalysisMetadata()
        if 'metadata' in data:
            metadata = AnalysisMetadata(**data['metadata'])

        character_context = None
        if 'character_context' in data and data['character_context']:
            character_context = StandardCharacterProfile.from_dict(data['character_context'])

        artist_persona = None
        if 'artist_persona' in data and data['artist_persona']:
            artist_persona = ArtistPersona.from_dict(data['artist_persona'])

        genre_info = None
        if 'genre_info' in data and data['genre_info']:
            genre_info = GenreInfo.from_dict(data['genre_info'])

        return cls(
            commands=commands,
            metadata=metadata,
            character_context=character_context,
            artist_persona=artist_persona,
            genre_info=genre_info,
            generation_notes=data.get('generation_notes', []),
            quality_score=data.get('quality_score', 1.0)
        )


@dataclass
class CharacterAnalysisResult:
    """Result of character analysis operations"""
    characters: List[StandardCharacterProfile]
    narrative_themes: List[str] = field(default_factory=list)
    emotional_arc: Optional[EmotionalProfile] = None
    setting_info: Dict[str, Any] = field(default_factory=dict)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            'characters': [char.to_dict() for char in self.characters],
            'narrative_themes': self.narrative_themes,
            'setting_info': self.setting_info,
            'relationships': self.relationships,
            'metadata': self.metadata.to_dict()
        }

        if self.emotional_arc:
            data['emotional_arc'] = self.emotional_arc.to_dict()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterAnalysisResult':
        """Create from dictionary"""
        characters = [StandardCharacterProfile.from_dict(char) for char in data.get('characters', [])]

        metadata = AnalysisMetadata()
        if 'metadata' in data:
            metadata = AnalysisMetadata(**data['metadata'])

        emotional_arc = None
        if 'emotional_arc' in data and data['emotional_arc']:
            emotional_arc = EmotionalProfile.from_dict(data['emotional_arc'])

        return cls(
            characters=characters,
            narrative_themes=data.get('narrative_themes', []),
            emotional_arc=emotional_arc,
            setting_info=data.get('setting_info', {}),
            relationships=data.get('relationships', []),
            metadata=metadata
        )


# ================================================================================================
# UTILITY FUNCTIONS
# ================================================================================================

def create_analysis_metadata(tool_name: str, confidence: float = 1.0,
                           processing_time_ms: int = None,
                           source_text_length: int = None) -> AnalysisMetadata:
    """Create analysis metadata with current timestamp"""
    return AnalysisMetadata(
        tool_name=tool_name,
        confidence_score=confidence,
        processing_time_ms=processing_time_ms,
        source_text_length=source_text_length
    )


def create_genre_info(primary_genre: str, sub_genres: List[str] = None,
                     confidence: float = 1.0) -> GenreInfo:
    """Create genre info with automatic category detection"""
    if sub_genres is None:
        sub_genres = []

    # Auto-detect category
    genre_lower = primary_genre.lower()
    category = GenreCategory.OTHER

    for cat in GenreCategory:
        if cat.value in genre_lower or genre_lower in cat.value:
            category = cat
            break

    return GenreInfo(
        primary_genre=primary_genre,
        sub_genres=sub_genres,
        category=category,
        confidence_score=confidence
    )


def create_emotional_profile(primary_emotion: str, intensity: float = 0.5,
                           secondary_emotions: List[str] = None) -> EmotionalProfile:
    """Create emotional profile with validation"""
    if secondary_emotions is None:
        secondary_emotions = []

    try:
        primary = EmotionalState(primary_emotion.lower())
    except ValueError:
        primary = EmotionalState.CONTEMPLATIVE

    secondary = []
    for emotion in secondary_emotions:
        try:
            secondary.append(EmotionalState(emotion.lower()))
        except ValueError:
            continue

    return EmotionalProfile(
        primary_emotion=primary,
        secondary_emotions=secondary,
        intensity=max(0.0, min(1.0, intensity))
    )


def create_suno_command(command_text: str, tags: List[str] = None,
                       description: str = "", command_type: str = "generate") -> SunoCommand:
    """Create a Suno command with validation"""
    if tags is None:
        tags = []

    return SunoCommand(
        command_text=command_text.strip(),
        command_type=command_type,
        tags=tags,
        description=description
    )


def merge_character_profiles(profiles: List[StandardCharacterProfile]) -> StandardCharacterProfile:
    """Merge multiple character profiles into one comprehensive profile"""
    if not profiles:
        return StandardCharacterProfile(name="Empty Profile")

    if len(profiles) == 1:
        return profiles[0]

    # Start with the profile with highest confidence
    base_profile = max(profiles, key=lambda p: p.confidence_score)

    # Merge with others
    for profile in profiles:
        if profile != base_profile:
            base_profile = base_profile.merge_with(profile)

    return base_profile


def extract_genre_from_text(text: str) -> Optional[GenreInfo]:
    """Extract genre information from text description"""
    text_lower = text.lower()

    # Common genre keywords
    genre_keywords = {
        'rock': ['rock', 'guitar', 'drums', 'electric'],
        'pop': ['pop', 'catchy', 'mainstream', 'radio'],
        'hip-hop': ['hip-hop', 'rap', 'beats', 'rhyme', 'flow'],
        'electronic': ['electronic', 'synth', 'edm', 'techno', 'house'],
        'folk': ['folk', 'acoustic', 'traditional', 'storytelling'],
        'jazz': ['jazz', 'improvisation', 'swing', 'blues'],
        'country': ['country', 'twang', 'rural', 'americana'],
        'r&b': ['r&b', 'soul', 'groove', 'rhythm']
    }

    detected_genres = []
    for genre, keywords in genre_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_genres.append(genre)

    if detected_genres:
        primary = detected_genres[0]
        sub_genres = detected_genres[1:] if len(detected_genres) > 1 else []
        return create_genre_info(primary, sub_genres, confidence=0.7)

    return None


def validate_data_consistency(character: StandardCharacterProfile,
                            persona: ArtistPersona) -> List[str]:
    """Validate consistency between character profile and artist persona"""
    issues = []

    # Check name consistency
    if character.name != persona.character_name:
        issues.append(f"Character name mismatch: '{character.name}' vs '{persona.character_name}'")

    # Check emotional consistency
    if persona.emotional_profile and character.fears:
        # Ensure fears are reflected in emotional profile
        fear_emotions = [EmotionalState.FEAR, EmotionalState.SADNESS, EmotionalState.ANGER]
        if persona.emotional_profile.primary_emotion not in fear_emotions and character.fears:
            issues.append("Character fears not reflected in emotional profile")

    # Check thematic consistency
    if persona.lyrical_themes and character.motivations:
        # Basic check for thematic alignment
        motivation_words = ' '.join(character.motivations).lower()
        theme_words = ' '.join(persona.lyrical_themes).lower()

        # Simple word overlap check
        motivation_set = set(motivation_words.split())
        theme_set = set(theme_words.split())

        if len(motivation_set.intersection(theme_set)) == 0:
            issues.append("Character motivations and lyrical themes show no overlap")

    return issues


def create_default_artist_persona(character: StandardCharacterProfile) -> ArtistPersona:
    """Create a default artist persona from a character profile"""

    # Extract basic info
    stage_name = character.name
    if character.aliases:
        stage_name = character.aliases[0]

    # Create emotional profile from character traits
    primary_emotion = EmotionalState.CONTEMPLATIVE
    if character.fears and "anger" in ' '.join(character.fears).lower():
        primary_emotion = EmotionalState.ANGER
    elif character.desires and "joy" in ' '.join(character.desires).lower():
        primary_emotion = EmotionalState.JOY

    emotional_profile = EmotionalProfile(primary_emotion=primary_emotion)

    # Extract lyrical themes from character elements
    lyrical_themes = []
    if character.conflicts:
        lyrical_themes.extend(character.conflicts[:3])  # Limit to first 3
    if character.motivations:
        lyrical_themes.extend(character.motivations[:2])  # Limit to first 2

    # Create basic genre info
    genre_info = create_genre_info("alternative", confidence=0.5)

    return ArtistPersona(
        character_name=character.name,
        stage_name=stage_name,
        artistic_identity=character.backstory[:200] if character.backstory else "",
        lyrical_themes=lyrical_themes,
        emotional_profile=emotional_profile,
        genre_info=genre_info,
        confidence_score=character.confidence_score * 0.8,  # Lower confidence for derived data
        source_character=character
    )


# ================================================================================================
# DATA CONVERSION UTILITIES
# ================================================================================================

def convert_legacy_persona_to_artist_persona(legacy_data: Dict[str, Any]) -> ArtistPersona:
    """Convert legacy persona format to ArtistPersona"""

    character_name = legacy_data.get('name', legacy_data.get('character_name', 'Unknown'))

    # Extract genre info
    genre_info = None
    if 'style' in legacy_data or 'genres' in legacy_data:
        primary_genre = legacy_data.get('style', 'alternative')
        sub_genres = legacy_data.get('genres', [])
        genre_info = create_genre_info(primary_genre, sub_genres)

    # Extract vocal characteristics
    vocal_characteristics = None
    if 'vocals' in legacy_data:
        vocal_characteristics = VocalCharacteristics.from_dict(legacy_data['vocals'])

    return ArtistPersona(
        character_name=character_name,
        stage_name=legacy_data.get('stage_name', character_name),
        lyrical_themes=legacy_data.get('themes', []),
        genre_info=genre_info,
        vocal_characteristics=vocal_characteristics,
        confidence_score=legacy_data.get('confidence', 1.0)
    )


def convert_simple_commands_to_command_set(commands: List[str],
                                         character: StandardCharacterProfile = None,
                                         genre: str = None) -> SunoCommandSet:
    """Convert simple command list to SunoCommandSet"""

    suno_commands = []
    for cmd_text in commands:
        suno_commands.append(create_suno_command(cmd_text))

    genre_info = None
    if genre:
        genre_info = create_genre_info(genre)

    metadata = create_analysis_metadata("command_converter")

    return SunoCommandSet(
        commands=suno_commands,
        metadata=metadata,
        character_context=character,
        genre_info=genre_info
    )


# ================================================================================================
# SERIALIZATION UTILITIES
# ================================================================================================

def serialize_to_json(obj: Any, indent: int = 2) -> str:
    """Serialize any MCP data object to JSON"""
    if hasattr(obj, 'to_dict'):
        data = obj.to_dict()
    else:
        data = obj

    return json.dumps(data, indent=indent, ensure_ascii=False)


def deserialize_from_json(json_str: str, target_class: type) -> Any:
    """Deserialize JSON to MCP data object"""
    try:
        data = json.loads(json_str)
        if hasattr(target_class, 'from_dict'):
            return target_class.from_dict(data)
        else:
            return target_class(**data)
    except Exception as e:
        logger.error(f"Failed to deserialize JSON to {target_class.__name__}: {e}")
        raise ValueError(f"Deserialization failed: {e}")


def safe_serialize(obj: Any) -> Dict[str, Any]:
    """Safely serialize object to dictionary, handling errors gracefully"""
    try:
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif isinstance(obj, dict):
            return obj
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return {'value': str(obj), 'type': type(obj).__name__}
    except Exception as e:
        logger.warning(f"Failed to serialize object: {e}")
        return {'error': str(e), 'type': type(obj).__name__}


# ================================================================================================
# QUALITY ASSURANCE UTILITIES
# ================================================================================================

def calculate_data_quality_score(data: Dict[str, Any], required_fields: List[str]) -> float:
    """Calculate quality score for data based on completeness and content"""
    if not isinstance(data, dict):
        return 0.0

    # Check field completeness
    present_fields = sum(1 for field in required_fields if field in data and data[field])
    completeness_score = present_fields / len(required_fields) if required_fields else 1.0

    # Check content quality (non-empty strings, non-empty lists)
    content_quality = 0.0
    content_count = 0

    for key, value in data.items():
        content_count += 1
        if isinstance(value, str) and len(value.strip()) > 0:
            content_quality += 1.0
        elif isinstance(value, list) and len(value) > 0:
            content_quality += 1.0
        elif isinstance(value, dict) and len(value) > 0:
            content_quality += 1.0
        elif isinstance(value, (int, float)) and value != 0:
            content_quality += 1.0

    content_score = content_quality / content_count if content_count > 0 else 0.0

    # Weighted average
    return (completeness_score * 0.7) + (content_score * 0.3)


def validate_character_persona_alignment(character: StandardCharacterProfile,
                                       persona: ArtistPersona) -> Dict[str, Any]:
    """Validate alignment between character and persona"""
    alignment_score = 1.0
    issues = []
    suggestions = []

    # Name consistency
    if character.name != persona.character_name:
        alignment_score -= 0.2
        issues.append("Name mismatch between character and persona")
        suggestions.append("Ensure character name matches persona character_name")

    # Emotional consistency
    if persona.emotional_profile:
        character_emotions = []
        if character.fears:
            character_emotions.extend(['fear', 'anxiety'])
        if character.motivations:
            character_emotions.extend(['determination', 'hope'])

        if character_emotions and persona.emotional_profile.primary_emotion.value not in character_emotions:
            alignment_score -= 0.1
            issues.append("Emotional profile doesn't align with character traits")

    # Thematic consistency
    if persona.lyrical_themes and character.motivations:
        theme_overlap = set(' '.join(persona.lyrical_themes).lower().split())
        motivation_overlap = set(' '.join(character.motivations).lower().split())

        if not theme_overlap.intersection(motivation_overlap):
            alignment_score -= 0.1
            issues.append("Lyrical themes don't reflect character motivations")
            suggestions.append("Align lyrical themes with character motivations and conflicts")

    return {
        'alignment_score': max(0.0, alignment_score),
        'issues': issues,
        'suggestions': suggestions,
        'is_aligned': alignment_score >= 0.8
    }
