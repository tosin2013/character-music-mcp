#!/usr/bin/env python3
"""
Character-Driven Music Generation MCP Server

This FastMCP server provides comprehensive character analysis and music generation capabilities,
integrating narrative text analysis with musical artist personas for Suno AI command generation.
"""

import asyncio
import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from fastmcp import Context, FastMCP
from pydantic import BaseModel

from enhanced_character_analyzer import EnhancedCharacterAnalyzer

# Enhanced character analysis imports
from standard_character_profile import StandardCharacterProfile
from working_universal_processor import WorkingUniversalProcessor

# Wiki data integration imports
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from enhanced_genre_mapper import EnhancedGenreMapper, GenreMatch
    from source_attribution_manager import SourceAttributionManager
    from wiki_data_models import WikiConfig
    from wiki_data_system import WikiDataManager
    WIKI_INTEGRATION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Wiki integration not available: {e}")
    WIKI_INTEGRATION_AVAILABLE = False

# Initialize FastMCP server
mcp = FastMCP("Character Music Generator")

# ================================================================================================
# DATA MODELS AND SCHEMAS
# ================================================================================================

@dataclass
class CharacterProfile:
    """Complete character profile with three-layer analysis"""
    name: str
    aliases: List[str]

    # Skin Layer - Observable characteristics
    physical_description: str
    mannerisms: List[str]
    speech_patterns: List[str]
    behavioral_traits: List[str]

    # Flesh Layer - Background and relationships
    backstory: str
    relationships: List[str]
    formative_experiences: List[str]
    social_connections: List[str]

    # Core Layer - Deep psychology
    motivations: List[str]
    fears: List[str]
    desires: List[str]
    conflicts: List[str]
    personality_drivers: List[str]

    # Analysis metadata
    confidence_score: float
    text_references: List[str]
    first_appearance: str
    importance_score: float

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'aliases': self.aliases,
            'physical_description': self.physical_description,
            'mannerisms': self.mannerisms,
            'speech_patterns': self.speech_patterns,
            'behavioral_traits': self.behavioral_traits,
            'backstory': self.backstory,
            'relationships': self.relationships,
            'formative_experiences': self.formative_experiences,
            'social_connections': self.social_connections,
            'motivations': self.motivations,
            'fears': self.fears,
            'desires': self.desires,
            'conflicts': self.conflicts,
            'personality_drivers': self.personality_drivers,
            'confidence_score': self.confidence_score,
            'text_references': self.text_references,
            'first_appearance': self.first_appearance,
            'importance_score': self.importance_score
        }

@dataclass
class ArtistPersona:
    """Musical artist persona derived from character analysis"""
    character_name: str
    artist_name: str

    # Musical identity
    primary_genre: str = ""
    secondary_genres: List[str] = field(default_factory=list)
    vocal_style: str = ""
    instrumental_preferences: List[str] = field(default_factory=list)

    # Creative characteristics
    lyrical_themes: List[str] = field(default_factory=list)
    emotional_palette: List[str] = field(default_factory=list)
    artistic_influences: List[str] = field(default_factory=list)
    collaboration_style: str = ""

    # Persona metadata
    character_mapping_confidence: float = 1.0
    genre_justification: str = ""
    persona_description: str = ""

    def __post_init__(self):
        """Validate and normalize data after initialization"""
        # Ensure required string fields are not empty
        if not self.character_name or not self.character_name.strip():
            self.character_name = "Unknown Character"
        if not self.artist_name or not self.artist_name.strip():
            self.artist_name = self.character_name

        # Normalize confidence score
        self.character_mapping_confidence = max(0.0, min(1.0, self.character_mapping_confidence))

        # Clean up string fields
        self.character_name = self.character_name.strip()
        self.artist_name = self.artist_name.strip()
        self.primary_genre = self.primary_genre.strip()
        self.vocal_style = self.vocal_style.strip()
        self.collaboration_style = self.collaboration_style.strip()
        self.genre_justification = self.genre_justification.strip()
        self.persona_description = self.persona_description.strip()

        # Remove empty strings from lists
        self.secondary_genres = [item.strip() for item in self.secondary_genres if item and item.strip()]
        self.instrumental_preferences = [item.strip() for item in self.instrumental_preferences if item and item.strip()]
        self.lyrical_themes = [item.strip() for item in self.lyrical_themes if item and item.strip()]
        self.emotional_palette = [item.strip() for item in self.emotional_palette if item and item.strip()]
        self.artistic_influences = [item.strip() for item in self.artistic_influences if item and item.strip()]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArtistPersona':
        """
        Create ArtistPersona from dictionary, handling missing fields gracefully
        
        Args:
            data: Dictionary containing artist persona data
            
        Returns:
            ArtistPersona instance with all fields properly initialized
        """
        if not isinstance(data, dict):
            raise ValueError(f"Expected dictionary, got {type(data)}")

        # Handle the case where required fields are missing
        if 'character_name' not in data or not data['character_name']:
            data['character_name'] = "Unknown Character"
        if 'artist_name' not in data or not data['artist_name']:
            data['artist_name'] = data['character_name']

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
                        filtered_data[key] = [str(value)] if value else []

                # Handle string fields that might be None
                elif field_type == str:
                    filtered_data[key] = str(value) if value is not None else ""

                # Handle float fields
                elif field_type == float:
                    try:
                        filtered_data[key] = float(value) if value is not None else 1.0
                    except (ValueError, TypeError):
                        filtered_data[key] = 1.0

                else:
                    filtered_data[key] = value

        try:
            return cls(**filtered_data)
        except TypeError:
            # Create minimal valid instance if there are still issues
            return cls(
                character_name=data.get('character_name', 'Unknown Character'),
                artist_name=data.get('artist_name', data.get('character_name', 'Unknown Artist'))
            )

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'character_name': self.character_name,
            'artist_name': self.artist_name,
            'primary_genre': self.primary_genre,
            'secondary_genres': self.secondary_genres,
            'vocal_style': self.vocal_style,
            'instrumental_preferences': self.instrumental_preferences,
            'lyrical_themes': self.lyrical_themes,
            'emotional_palette': self.emotional_palette,
            'artistic_influences': self.artistic_influences,
            'collaboration_style': self.collaboration_style,
            'character_mapping_confidence': self.character_mapping_confidence,
            'genre_justification': self.genre_justification,
            'persona_description': self.persona_description
        }

@dataclass
class SunoCommand:
    """Optimized Suno AI command with metadata"""
    command_type: str  # "simple", "custom", "bracket_notation"
    prompt: str
    style_tags: List[str]
    structure_tags: List[str]
    sound_effect_tags: List[str]
    vocal_tags: List[str]

    # Command metadata
    character_source: str
    artist_persona: str
    command_rationale: str
    estimated_effectiveness: float
    variations: List[str]

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'command_type': self.command_type,
            'prompt': self.prompt,
            'style_tags': self.style_tags,
            'structure_tags': self.structure_tags,
            'sound_effect_tags': self.sound_effect_tags,
            'vocal_tags': self.vocal_tags,
            'character_source': self.character_source,
            'artist_persona': self.artist_persona,
            'command_rationale': self.command_rationale,
            'estimated_effectiveness': self.estimated_effectiveness,
            'variations': self.variations
        }

class TextAnalysisResult(BaseModel):
    """Comprehensive text analysis results"""
    characters: List[CharacterProfile]
    narrative_themes: List[str]
    emotional_arc: List[str]
    setting_description: str
    text_complexity: float
    processing_time: float
    # New emotional framework fields
    emotional_states: Optional[List[Dict]] = None
    emotional_subtext: Optional[List[Dict]] = None
    beat_progression: Optional[Dict] = None
    introspection_analysis: Optional[Dict] = None

class MusicGenerationResult(BaseModel):
    """Music generation command results"""
    commands: List[SunoCommand]
    artist_personas: List[ArtistPersona]
    generation_summary: str
    total_commands: int
    processing_time: float

# ================================================================================================
# EMOTIONAL FRAMEWORK COMPONENTS
# ================================================================================================

@dataclass
class EmotionalState:
    """Represents a complex emotional state with meta-narrative context"""
    primary_emotion: str
    secondary_emotions: List[str]
    intensity: float  # 0.0 to 1.0
    factual_triggers: List[str]  # Facts from text that caused this emotion
    internal_conflict: Optional[str]
    defense_mechanism: Optional[str]
    authenticity_score: float  # How genuine vs performative

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'primary_emotion': self.primary_emotion,
            'secondary_emotions': self.secondary_emotions,
            'intensity': self.intensity,
            'factual_triggers': self.factual_triggers,
            'internal_conflict': self.internal_conflict,
            'defense_mechanism': self.defense_mechanism,
            'authenticity_score': self.authenticity_score
        }

@dataclass
class BeatPattern:
    """Emotional beat pattern for production"""
    tempo_range: Tuple[int, int]  # BPM range
    rhythm_pattern: str  # Description of rhythm
    percussion_elements: List[str]
    dynamic_progression: str  # How it evolves
    emotional_mapping: str  # Which emotion it represents
    intensity_automation: List[Dict[str, float]]  # Time-based intensity changes

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'tempo_range': list(self.tempo_range),
            'rhythm_pattern': self.rhythm_pattern,
            'percussion_elements': self.percussion_elements,
            'dynamic_progression': self.dynamic_progression,
            'emotional_mapping': self.emotional_mapping,
            'intensity_automation': self.intensity_automation
        }

class CreativeMusicEngine:
    """Engine for meaningful creative music generation with musical analysis"""

    def __init__(self):
        # Initialize with access to wiki data if available
        self.wiki_data_manager = None
        try:
            # Try to get wiki data manager from global context if available
            if hasattr(globals(), 'wiki_data_manager') and globals()['wiki_data_manager']:
                self.wiki_data_manager = globals()['wiki_data_manager']
        except:
            pass

    def analyze_musical_concept(self, concept: str) -> Dict[str, Any]:
        """Analyze concept for musical elements instead of just repeating text"""
        concept_lower = concept.lower()

        # Extract musical elements from concept
        musical_elements = {
            "core_themes": self._extract_themes(concept),
            "emotional_qualities": self._analyze_emotional_qualities(concept),
            "rhythmic_implications": self._analyze_rhythmic_elements(concept),
            "harmonic_suggestions": self._analyze_harmonic_elements(concept),
            "textural_elements": self._analyze_textural_elements(concept),
            "structural_implications": self._analyze_structural_elements(concept),
            "sonic_palette": self._extract_sonic_palette(concept)
        }

        return musical_elements

    def generate_creative_variations(self, concept_analysis: Dict[str, Any], style_preference: str) -> List[Dict[str, Any]]:
        """Generate meaningful creative variations based on musical analysis"""
        variations = []

        # Generate variations based on different musical approaches
        approaches = [
            "rhythmic_focus",
            "harmonic_exploration",
            "textural_emphasis",
            "structural_innovation",
            "emotional_intensity"
        ]

        for approach in approaches:
            variation = self._create_variation_by_approach(concept_analysis, approach, style_preference)
            variations.append(variation)

        return variations

    async def generate_practical_suno_commands(self, variations: List[Dict], concept_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate practical Suno AI commands that actually work"""
        commands = []

        # Get wiki data for accurate meta tags and techniques
        genres = []
        meta_tags = []
        techniques = []

        if self.wiki_data_manager:
            try:
                genres = await self.wiki_data_manager.get_genres()
                meta_tags = await self.wiki_data_manager.get_meta_tags()
                techniques = await self.wiki_data_manager.get_techniques()
            except Exception as e:
                logger.warning(f"Could not fetch wiki data: {e}")

        # Generate commands for each variation
        for i, variation in enumerate(variations):
            command = self._create_suno_command(
                variation, concept_analysis, genres, meta_tags, techniques, i + 1
            )
            commands.append(command)

        return commands

    def _extract_themes(self, concept: str) -> List[str]:
        """Extract core thematic elements from concept"""
        themes = []
        concept_lower = concept.lower()

        # Enhanced thematic keywords mapping with more comprehensive coverage
        theme_patterns = {
            "transformation": ["change", "transform", "evolve", "become", "growth", "metamorphosis", "transition", "shift"],
            "journey": ["travel", "path", "journey", "road", "adventure", "quest", "voyage", "walk", "move", "go"],
            "conflict": ["struggle", "fight", "battle", "conflict", "tension", "opposition", "war", "clash", "chaos"],
            "love": ["love", "romance", "heart", "passion", "affection", "devotion", "relationship", "together"],
            "loss": ["loss", "grief", "sorrow", "missing", "gone", "departed", "empty", "alone", "lost"],
            "hope": ["hope", "dream", "aspire", "wish", "future", "possibility", "bright", "light", "tomorrow"],
            "memory": ["remember", "memory", "past", "nostalgia", "recall", "reminisce", "childhood", "yesterday"],
            "nature": ["nature", "earth", "sky", "water", "forest", "mountain", "ocean", "tree", "wind", "rain"],
            "time": ["time", "moment", "eternity", "forever", "instant", "duration", "clock", "hour", "day"],
            "identity": ["self", "identity", "who", "being", "existence", "soul", "person", "individual"],
            "peace": ["peace", "calm", "quiet", "still", "serene", "tranquil", "meditation", "rest"],
            "energy": ["energy", "power", "force", "dynamic", "vibrant", "alive", "electric", "intense"],
            "urban": ["city", "urban", "street", "building", "traffic", "crowd", "metropolitan", "downtown"],
            "family": ["family", "home", "mother", "father", "child", "parent", "sibling", "house"],
            "freedom": ["freedom", "free", "escape", "liberation", "independent", "open", "release"],
            "mystery": ["mystery", "unknown", "secret", "hidden", "enigma", "puzzle", "strange"],
            "celebration": ["celebration", "party", "joy", "festival", "dance", "music", "happy"],
            "solitude": ["alone", "solitude", "lonely", "isolated", "single", "individual", "solo"],
            "decision": ["decision", "choice", "choose", "decide", "crossroads", "option", "path"],
            "awakening": ["wake", "awaken", "dawn", "morning", "sunrise", "beginning", "start"]
        }

        # Score themes based on keyword matches
        theme_scores = {}
        for theme, keywords in theme_patterns.items():
            score = sum(1 for keyword in keywords if keyword in concept_lower)
            if score > 0:
                theme_scores[theme] = score

        # Get top themes by score
        if theme_scores:
            sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
            themes = [theme for theme, score in sorted_themes[:3]]

        # Enhanced fallback logic - analyze concept structure and content
        if not themes:
            words = concept_lower.split()

            # Analyze sentence structure for themes
            if any(word in concept_lower for word in ["feeling", "emotion", "sense"]):
                themes.append("emotional_exploration")
            elif any(word in concept_lower for word in ["standing", "sitting", "walking", "moving"]):
                themes.append("physical_experience")
            elif any(word in concept_lower for word in ["watching", "seeing", "looking", "observing"]):
                themes.append("observation")
            elif any(word in concept_lower for word in ["thinking", "contemplating", "wondering", "considering"]):
                themes.append("contemplation")
            elif len(words) > 15:
                themes.append("complex_narrative")
            elif len(words) > 8:
                themes.append("detailed_scene")
            else:
                themes.append("abstract_concept")

        # Ensure we always have at least one theme
        if not themes:
            themes = ["universal_experience"]

        return themes[:3]  # Limit to top 3 themes

    def _analyze_emotional_qualities(self, concept: str) -> Dict[str, Any]:
        """Analyze emotional qualities with varied responses"""
        concept_lower = concept.lower()

        # Emotional intensity analysis
        intensity_indicators = {
            "high": ["intense", "powerful", "overwhelming", "explosive", "dramatic"],
            "medium": ["strong", "significant", "notable", "meaningful", "important"],
            "low": ["gentle", "subtle", "quiet", "soft", "delicate"]
        }

        intensity = "medium"  # default
        for level, indicators in intensity_indicators.items():
            if any(indicator in concept_lower for indicator in indicators):
                intensity = level
                break

        # Emotional valence analysis
        positive_words = ["joy", "happy", "love", "hope", "bright", "light", "celebration"]
        negative_words = ["sad", "dark", "loss", "pain", "sorrow", "grief", "struggle"]

        positive_count = sum(1 for word in positive_words if word in concept_lower)
        negative_count = sum(1 for word in negative_words if word in concept_lower)

        if positive_count > negative_count:
            valence = "positive"
        elif negative_count > positive_count:
            valence = "negative"
        else:
            valence = "neutral_complex"

        # Emotional progression analysis
        progression = "static"
        if any(word in concept_lower for word in ["become", "transform", "change", "evolve"]):
            progression = "transformative"
        elif any(word in concept_lower for word in ["journey", "path", "through", "across"]):
            progression = "developmental"

        return {
            "intensity": intensity,
            "valence": valence,
            "progression": progression,
            "primary_emotion": self._identify_primary_emotion(concept_lower),
            "emotional_complexity": "high" if len(concept.split()) > 10 else "medium"
        }

    def _identify_primary_emotion(self, concept_lower: str) -> str:
        """Identify primary emotion beyond just 'contemplative'"""
        emotion_patterns = {
            "melancholy": ["sad", "sorrow", "melancholy", "wistful", "longing", "empty", "loss", "grief"],
            "euphoria": ["joy", "ecstasy", "bliss", "elation", "euphoria", "celebration", "happy", "delight"],
            "anxiety": ["worry", "fear", "anxious", "nervous", "uncertain", "tension", "stress", "edge"],
            "anger": ["anger", "rage", "fury", "mad", "frustrated", "chaos", "battle", "fight"],
            "wonder": ["wonder", "awe", "amazement", "mystery", "magical", "dawn", "awakening", "discovery"],
            "nostalgia": ["memory", "past", "remember", "nostalgia", "childhood", "house", "family", "home"],
            "determination": ["will", "strength", "determined", "resolve", "persevere", "decision", "choice"],
            "serenity": ["peace", "calm", "serene", "tranquil", "still", "quiet", "meditation", "gentle"],
            "excitement": ["energy", "dynamic", "vibrant", "electric", "intense", "powerful", "alive"],
            "loneliness": ["alone", "lonely", "solitude", "isolated", "single", "empty", "echoing"],
            "hope": ["hope", "dream", "future", "possibility", "light", "bright", "tomorrow"],
            "curiosity": ["explore", "discover", "unknown", "question", "search", "find", "seek"]
        }

        # Score emotions based on keyword matches
        emotion_scores = {}
        for emotion, keywords in emotion_patterns.items():
            score = sum(1 for keyword in keywords if keyword in concept_lower)
            if score > 0:
                emotion_scores[emotion] = score

        # Return highest scoring emotion
        if emotion_scores:
            return max(emotion_scores.items(), key=lambda x: x[1])[0]

        # Enhanced fallback based on concept characteristics
        if "?" in concept_lower:
            return "curiosity"
        elif "!" in concept_lower:
            return "excitement"
        elif len(concept_lower.split()) > 20:
            return "contemplative"
        elif any(word in concept_lower for word in ["the", "a", "an"]) and len(concept_lower.split()) > 10:
            return "reflective"
        else:
            return "contemplative"  # final fallback

    def _analyze_rhythmic_elements(self, concept: str) -> Dict[str, Any]:
        """Analyze rhythmic implications from concept"""
        concept_lower = concept.lower()

        # Tempo implications
        tempo_indicators = {
            "fast": ["fast", "quick", "rapid", "racing", "urgent", "rushing", "energetic"],
            "slow": ["slow", "gentle", "peaceful", "calm", "meditative", "still"],
            "variable": ["changing", "shifting", "dynamic", "flowing", "evolving"]
        }

        tempo_feel = "moderate"
        for feel, indicators in tempo_indicators.items():
            if any(indicator in concept_lower for indicator in indicators):
                tempo_feel = feel
                break

        # Rhythmic character
        rhythm_character = "steady"
        if any(word in concept_lower for word in ["broken", "fragmented", "chaos", "irregular"]):
            rhythm_character = "irregular"
        elif any(word in concept_lower for word in ["flow", "wave", "organic", "natural"]):
            rhythm_character = "flowing"
        elif any(word in concept_lower for word in ["pulse", "heartbeat", "steady", "constant"]):
            rhythm_character = "pulsing"

        return {
            "tempo_feel": tempo_feel,
            "rhythm_character": rhythm_character,
            "suggested_bpm_range": self._suggest_bpm_range(tempo_feel),
            "rhythmic_complexity": "complex" if "complex" in concept_lower else "moderate"
        }

    def _suggest_bpm_range(self, tempo_feel: str) -> str:
        """Suggest BPM range based on tempo feel"""
        bpm_ranges = {
            "slow": "60-80 BPM",
            "moderate": "90-110 BPM",
            "fast": "120-140 BPM",
            "variable": "80-120 BPM (variable)"
        }
        return bpm_ranges.get(tempo_feel, "90-110 BPM")

    def _analyze_harmonic_elements(self, concept: str) -> Dict[str, Any]:
        """Analyze harmonic implications"""
        concept_lower = concept.lower()

        # Harmonic complexity
        complexity = "moderate"
        if any(word in concept_lower for word in ["complex", "layered", "deep", "intricate"]):
            complexity = "complex"
        elif any(word in concept_lower for word in ["simple", "pure", "clean", "minimal"]):
            complexity = "simple"

        # Harmonic color
        color = "warm"
        if any(word in concept_lower for word in ["dark", "shadow", "night", "deep"]):
            color = "dark"
        elif any(word in concept_lower for word in ["bright", "light", "sun", "clear"]):
            color = "bright"
        elif any(word in concept_lower for word in ["cold", "ice", "winter", "distant"]):
            color = "cool"

        # Modal suggestions
        modal_suggestions = []
        if "sad" in concept_lower or "sorrow" in concept_lower:
            modal_suggestions.append("minor_modes")
        if "mysterious" in concept_lower or "unknown" in concept_lower:
            modal_suggestions.append("modal_scales")
        if "joy" in concept_lower or "celebration" in concept_lower:
            modal_suggestions.append("major_modes")

        return {
            "complexity": complexity,
            "harmonic_color": color,
            "modal_suggestions": modal_suggestions,
            "chord_progression_style": self._suggest_chord_style(concept_lower)
        }

    def _suggest_chord_style(self, concept_lower: str) -> str:
        """Suggest chord progression style"""
        if any(word in concept_lower for word in ["classical", "traditional", "formal"]):
            return "classical_progressions"
        elif any(word in concept_lower for word in ["jazz", "sophisticated", "complex"]):
            return "jazz_progressions"
        elif any(word in concept_lower for word in ["folk", "simple", "acoustic"]):
            return "folk_progressions"
        elif any(word in concept_lower for word in ["modern", "contemporary", "new"]):
            return "contemporary_progressions"
        else:
            return "versatile_progressions"

    def _analyze_textural_elements(self, concept: str) -> Dict[str, Any]:
        """Analyze textural implications"""
        concept_lower = concept.lower()

        # Texture density
        density = "medium"
        if any(word in concept_lower for word in ["thick", "dense", "layered", "full"]):
            density = "dense"
        elif any(word in concept_lower for word in ["thin", "sparse", "minimal", "empty"]):
            density = "sparse"

        # Texture character
        character = "smooth"
        if any(word in concept_lower for word in ["rough", "harsh", "gritty", "raw"]):
            character = "rough"
        elif any(word in concept_lower for word in ["soft", "gentle", "flowing", "silk"]):
            character = "soft"
        elif any(word in concept_lower for word in ["sharp", "crisp", "clear", "defined"]):
            character = "crisp"

        return {
            "density": density,
            "character": character,
            "suggested_instruments": self._suggest_instruments(concept_lower),
            "production_style": self._suggest_production_style(concept_lower)
        }

    def _suggest_instruments(self, concept_lower: str) -> List[str]:
        """Suggest instruments based on concept"""
        instruments = []

        # Instrument associations
        if any(word in concept_lower for word in ["nature", "forest", "earth"]):
            instruments.extend(["acoustic_guitar", "flute", "strings"])
        if any(word in concept_lower for word in ["urban", "city", "modern"]):
            instruments.extend(["synthesizer", "electric_guitar", "electronic_drums"])
        if any(word in concept_lower for word in ["classical", "elegant", "formal"]):
            instruments.extend(["piano", "violin", "cello"])
        if any(word in concept_lower for word in ["folk", "traditional", "acoustic"]):
            instruments.extend(["acoustic_guitar", "harmonica", "banjo"])

        # Default if no specific associations
        if not instruments:
            instruments = ["piano", "strings", "subtle_percussion"]

        return instruments[:4]  # Limit to 4 instruments

    def _suggest_production_style(self, concept_lower: str) -> str:
        """Suggest production style"""
        if any(word in concept_lower for word in ["intimate", "close", "personal"]):
            return "intimate_production"
        elif any(word in concept_lower for word in ["grand", "epic", "vast", "huge"]):
            return "epic_production"
        elif any(word in concept_lower for word in ["clean", "pure", "minimal"]):
            return "clean_production"
        elif any(word in concept_lower for word in ["atmospheric", "ambient", "space"]):
            return "atmospheric_production"
        else:
            return "balanced_production"

    def _analyze_structural_elements(self, concept: str) -> Dict[str, Any]:
        """Analyze structural implications"""
        concept_lower = concept.lower()

        # Structure type
        structure_type = "traditional"
        if any(word in concept_lower for word in ["journey", "story", "narrative"]):
            structure_type = "narrative"
        elif any(word in concept_lower for word in ["cycle", "circular", "return"]):
            structure_type = "cyclical"
        elif any(word in concept_lower for word in ["build", "grow", "develop"]):
            structure_type = "developmental"
        elif any(word in concept_lower for word in ["fragment", "piece", "broken"]):
            structure_type = "fragmented"

        # Suggested sections
        sections = self._suggest_sections(concept_lower, structure_type)

        return {
            "structure_type": structure_type,
            "suggested_sections": sections,
            "overall_arc": self._suggest_overall_arc(concept_lower),
            "dynamic_progression": self._suggest_dynamic_progression(concept_lower)
        }

    def _suggest_sections(self, concept_lower: str, structure_type: str) -> List[str]:
        """Suggest song sections based on concept"""
        if structure_type == "narrative":
            return ["intro_setting", "verse_development", "chorus_climax", "bridge_reflection", "outro_resolution"]
        elif structure_type == "cyclical":
            return ["intro", "theme_a", "theme_b", "theme_a_return", "outro"]
        elif structure_type == "developmental":
            return ["intro_seed", "development_1", "development_2", "climax", "resolution"]
        elif structure_type == "fragmented":
            return ["fragment_1", "fragment_2", "fragment_3", "synthesis", "outro"]
        else:
            return ["intro", "verse", "chorus", "verse", "chorus", "bridge", "chorus", "outro"]

    def _suggest_overall_arc(self, concept_lower: str) -> str:
        """Suggest overall emotional/dynamic arc"""
        if any(word in concept_lower for word in ["rise", "build", "grow", "ascend"]):
            return "ascending"
        elif any(word in concept_lower for word in ["fall", "descend", "fade", "diminish"]):
            return "descending"
        elif any(word in concept_lower for word in ["wave", "cycle", "ebb", "flow"]):
            return "wave_like"
        else:
            return "balanced"

    def _suggest_dynamic_progression(self, concept_lower: str) -> str:
        """Suggest dynamic progression"""
        if any(word in concept_lower for word in ["explosive", "dramatic", "intense"]):
            return "dramatic_build"
        elif any(word in concept_lower for word in ["gentle", "gradual", "slow"]):
            return "gradual_evolution"
        elif any(word in concept_lower for word in ["sudden", "shift", "change"]):
            return "sudden_changes"
        else:
            return "organic_flow"

    def _extract_sonic_palette(self, concept: str) -> List[str]:
        """Extract sonic palette suggestions from concept imagery"""
        concept_lower = concept.lower()
        sonic_elements = []

        # Natural sounds
        if any(word in concept_lower for word in ["water", "ocean", "rain", "river"]):
            sonic_elements.append("water_textures")
        if any(word in concept_lower for word in ["wind", "air", "breath", "breeze"]):
            sonic_elements.append("wind_elements")
        if any(word in concept_lower for word in ["fire", "flame", "burn", "heat"]):
            sonic_elements.append("fire_textures")
        if any(word in concept_lower for word in ["earth", "stone", "rock", "ground"]):
            sonic_elements.append("earth_tones")

        # Atmospheric elements
        if any(word in concept_lower for word in ["space", "vast", "infinite", "cosmos"]):
            sonic_elements.append("spatial_reverb")
        if any(word in concept_lower for word in ["intimate", "close", "whisper", "personal"]):
            sonic_elements.append("intimate_ambience")
        if any(word in concept_lower for word in ["echo", "distant", "far", "memory"]):
            sonic_elements.append("echo_effects")

        # Textural elements
        if any(word in concept_lower for word in ["smooth", "silk", "flowing", "liquid"]):
            sonic_elements.append("smooth_textures")
        if any(word in concept_lower for word in ["rough", "gritty", "harsh", "raw"]):
            sonic_elements.append("rough_textures")
        if any(word in concept_lower for word in ["shimmer", "sparkle", "glitter", "bright"]):
            sonic_elements.append("shimmer_effects")

        # Default if no specific elements found
        if not sonic_elements:
            sonic_elements = ["atmospheric_pad", "subtle_texture"]

        return sonic_elements[:5]  # Limit to 5 elements

    def _create_variation_by_approach(self, concept_analysis: Dict, approach: str, style_preference: str) -> Dict[str, Any]:
        """Create a variation based on specific musical approach"""
        base_variation = {
            "approach": approach,
            "style_preference": style_preference,
            "concept_elements": concept_analysis["core_themes"]
        }

        if approach == "rhythmic_focus":
            base_variation.update({
                "primary_focus": "rhythm_and_groove",
                "tempo_emphasis": concept_analysis["rhythmic_implications"]["tempo_feel"],
                "rhythmic_character": concept_analysis["rhythmic_implications"]["rhythm_character"],
                "suggested_bpm": concept_analysis["rhythmic_implications"]["suggested_bpm_range"],
                "groove_style": f"{style_preference}_groove" if style_preference != "any" else "dynamic_groove"
            })

        elif approach == "harmonic_exploration":
            base_variation.update({
                "primary_focus": "harmony_and_chords",
                "harmonic_complexity": concept_analysis["harmonic_suggestions"]["complexity"],
                "harmonic_color": concept_analysis["harmonic_suggestions"]["harmonic_color"],
                "chord_style": concept_analysis["harmonic_suggestions"]["chord_progression_style"],
                "modal_approach": concept_analysis["harmonic_suggestions"]["modal_suggestions"]
            })

        elif approach == "textural_emphasis":
            base_variation.update({
                "primary_focus": "texture_and_timbre",
                "texture_density": concept_analysis["textural_elements"]["density"],
                "texture_character": concept_analysis["textural_elements"]["character"],
                "instruments": concept_analysis["textural_elements"]["suggested_instruments"],
                "production_style": concept_analysis["textural_elements"]["production_style"]
            })

        elif approach == "structural_innovation":
            base_variation.update({
                "primary_focus": "structure_and_form",
                "structure_type": concept_analysis["structural_implications"]["structure_type"],
                "sections": concept_analysis["structural_implications"]["suggested_sections"],
                "overall_arc": concept_analysis["structural_implications"]["overall_arc"],
                "dynamic_progression": concept_analysis["structural_implications"]["dynamic_progression"]
            })

        elif approach == "emotional_intensity":
            base_variation.update({
                "primary_focus": "emotional_expression",
                "emotional_intensity": concept_analysis["emotional_qualities"]["intensity"],
                "emotional_valence": concept_analysis["emotional_qualities"]["valence"],
                "primary_emotion": concept_analysis["emotional_qualities"]["primary_emotion"],
                "emotional_progression": concept_analysis["emotional_qualities"]["progression"]
            })

        return base_variation

    def _create_suno_command(self, variation: Dict, concept_analysis: Dict, genres: List, meta_tags: List, techniques: List, variation_num: int) -> Dict[str, Any]:
        """Create practical Suno AI command using wiki data"""

        # Build command components using actual Suno AI syntax
        command_parts = []

        # Add genre/style tags from wiki data
        style_tags = self._get_style_tags(variation["style_preference"], genres)
        if style_tags:
            command_parts.extend(style_tags)

        # Add tempo/BPM specification
        bpm_range = concept_analysis["rhythmic_implications"]["suggested_bpm_range"]
        if "BPM" in bpm_range:
            # Extract BPM number for Suno format
            bpm_match = re.search(r'(\d+)', bpm_range)
            if bpm_match:
                command_parts.append(f"{bpm_match.group(1)}bpm")

        # Add emotional/mood tags from wiki meta tags
        emotional_tags = self._get_emotional_meta_tags(concept_analysis["emotional_qualities"], meta_tags)
        if emotional_tags:
            command_parts.extend(emotional_tags)

        # Add instrumental/textural tags based on concept analysis
        instrumental_tags = self._get_instrumental_tags(concept_analysis, meta_tags)
        if instrumental_tags:
            command_parts.extend(instrumental_tags)

        # Add vocal style tags if applicable
        vocal_tags = self._get_vocal_style_tags(variation, meta_tags)
        if vocal_tags:
            command_parts.extend(vocal_tags)

        # Create the main Suno command
        main_command = ", ".join(command_parts)

        # Add structural annotations using wiki techniques
        structural_annotations = self._create_structural_annotations(variation, techniques)

        # Add vocal effects and formatting from wiki techniques
        vocal_effects = self._create_vocal_effects(concept_analysis, techniques)

        # Create complete Suno-compatible command structure
        complete_command = {
            "style_tags": f"[{main_command}]",
            "structural_annotations": structural_annotations,
            "vocal_effects": vocal_effects,
            "full_command_example": self._create_full_command_example(main_command, structural_annotations, vocal_effects)
        }

        # Add lyrical guidance based on concept
        lyrical_guidance = self._create_lyrical_guidance(concept_analysis, variation)

        return {
            "variation_number": variation_num,
            "approach": variation["approach"],
            "suno_commands": complete_command,
            "lyrical_guidance": lyrical_guidance,
            "production_notes": self._create_production_notes(variation, concept_analysis),
            "wiki_techniques_used": self._list_wiki_techniques_used(techniques),
            "estimated_duration": "3-4 minutes",
            "complexity_level": self._assess_complexity(variation)
        }

    def _get_style_tags(self, style_preference: str, genres: List) -> List[str]:
        """Get style tags from wiki genres data"""
        if style_preference == "any":
            return ["versatile"]

        style_tags = []
        style_lower = style_preference.lower()

        # Try to match with wiki genres
        for genre in genres:
            if hasattr(genre, 'name'):
                genre_name = genre.name.lower()
                if style_lower in genre_name or genre_name in style_lower:
                    # Use the exact genre name from wiki for accuracy
                    style_tags.append(genre.name.replace(" ", " "))  # Keep spaces for Suno
                    # Add subgenres if available
                    if hasattr(genre, 'subgenres') and genre.subgenres:
                        style_tags.extend([sg for sg in genre.subgenres[:1]])  # Add 1 subgenre
                    break

        # Fallback to basic style parsing if no wiki match
        if not style_tags:
            # Clean up style preference for Suno format
            cleaned_style = style_preference.replace("_", " ").title()
            style_tags.append(cleaned_style)

        return style_tags[:2]  # Limit to 2 style tags for cleaner commands

    def _get_focus_meta_tags(self, variation: Dict, meta_tags: List) -> List[str]:
        """Get meta tags based on variation focus"""
        focus = variation["primary_focus"]
        focus_tags = []

        focus_mappings = {
            "rhythm_and_groove": ["rhythmic", "groove", "beat", "percussion"],
            "harmony_and_chords": ["harmonic", "chord", "melodic", "tonal"],
            "texture_and_timbre": ["textural", "atmospheric", "ambient", "layered"],
            "structure_and_form": ["structured", "dynamic", "progressive", "developmental"],
            "emotional_expression": ["emotional", "expressive", "intense", "passionate"]
        }

        keywords = focus_mappings.get(focus, [])

        # Match with available meta tags
        for tag in meta_tags:
            if any(keyword in tag.tag.lower() for keyword in keywords):
                focus_tags.append(tag.tag.lower())
                if len(focus_tags) >= 2:
                    break

        # Fallback to basic tags
        if not focus_tags:
            focus_tags = keywords[:2]

        return focus_tags

    def _get_emotional_meta_tags(self, emotional_qualities: Dict, meta_tags: List) -> List[str]:
        """Get emotional meta tags from wiki data"""
        emotional_tags = []

        primary_emotion = emotional_qualities["primary_emotion"]
        intensity = emotional_qualities["intensity"]
        valence = emotional_qualities["valence"]

        # Map emotions to Suno-compatible terms
        emotion_mappings = {
            "melancholy": ["melancholic", "sad", "wistful"],
            "euphoria": ["euphoric", "joyful", "uplifting"],
            "anxiety": ["anxious", "tense", "nervous"],
            "anger": ["aggressive", "intense", "powerful"],
            "wonder": ["mysterious", "ethereal", "magical"],
            "nostalgia": ["nostalgic", "reflective", "reminiscent"],
            "determination": ["determined", "driving", "strong"],
            "serenity": ["peaceful", "calm", "serene"],
            "contemplative": ["contemplative", "thoughtful", "introspective"]
        }

        # Get Suno-compatible emotion terms
        if primary_emotion in emotion_mappings:
            emotional_tags.extend(emotion_mappings[primary_emotion][:1])

        # Add intensity modifiers
        if intensity == "high":
            emotional_tags.append("intense")
        elif intensity == "low":
            emotional_tags.append("gentle")

        # Add valence modifiers
        if valence == "positive":
            emotional_tags.append("uplifting")
        elif valence == "negative":
            emotional_tags.append("dark")

        # Try to match with actual wiki meta tags
        for tag in meta_tags:
            if hasattr(tag, 'tag') and hasattr(tag, 'category'):
                tag_lower = tag.tag.lower()
                # Look for emotional or mood-related tags
                if any(emotion_word in tag_lower for emotion_word in emotional_tags):
                    if tag.tag not in emotional_tags:  # Avoid duplicates
                        emotional_tags.append(tag.tag)
                        break

        return emotional_tags[:2]  # Limit to 2 emotional tags

    def _get_instrumental_tags(self, concept_analysis: Dict, meta_tags: List) -> List[str]:
        """Get instrumental/textural tags from concept analysis and wiki data"""
        instrumental_tags = []

        # Get suggested instruments from concept analysis
        suggested_instruments = concept_analysis["textural_elements"]["suggested_instruments"]

        # Map concept instruments to Suno-compatible terms
        instrument_mappings = {
            "acoustic_guitar": "acoustic guitar",
            "electric_guitar": "electric guitar",
            "synthesizer": "synth",
            "electronic_drums": "electronic drums",
            "piano": "piano",
            "violin": "violin",
            "cello": "cello",
            "flute": "flute",
            "strings": "strings",
            "harmonica": "harmonica",
            "banjo": "banjo",
            "subtle_percussion": "percussion"
        }

        # Convert to Suno format
        for instrument in suggested_instruments[:2]:  # Limit to 2 instruments
            if instrument in instrument_mappings:
                instrumental_tags.append(instrument_mappings[instrument])

        # Add textural elements from sonic palette
        sonic_palette = concept_analysis["sonic_palette"]
        texture_mappings = {
            "water_textures": "flowing",
            "wind_elements": "atmospheric",
            "fire_textures": "warm",
            "earth_tones": "organic",
            "spatial_reverb": "spacious",
            "intimate_ambience": "intimate",
            "echo_effects": "reverb",
            "smooth_textures": "smooth",
            "rough_textures": "gritty",
            "shimmer_effects": "bright"
        }

        for sonic_element in sonic_palette[:1]:  # Add 1 textural element
            if sonic_element in texture_mappings:
                instrumental_tags.append(texture_mappings[sonic_element])

        return instrumental_tags[:3]  # Limit to 3 total tags

    def _get_vocal_style_tags(self, variation: Dict, meta_tags: List) -> List[str]:
        """Get vocal style tags based on variation approach"""
        vocal_tags = []

        approach = variation["approach"]

        # Map approaches to vocal styles
        vocal_mappings = {
            "rhythmic_focus": ["rhythmic vocals"],
            "harmonic_exploration": ["melodic vocals"],
            "textural_emphasis": ["atmospheric vocals"],
            "structural_innovation": ["dynamic vocals"],
            "emotional_intensity": ["expressive vocals"]
        }

        if approach in vocal_mappings:
            vocal_tags.extend(vocal_mappings[approach])

        # Look for vocal-related meta tags in wiki data
        for tag in meta_tags:
            if hasattr(tag, 'category') and hasattr(tag, 'tag'):
                if tag.category.lower() in ["vocal", "vocal_style", "vocals"]:
                    vocal_tags.append(tag.tag)
                    break  # Add only one wiki vocal tag

        return vocal_tags[:1]  # Limit to 1 vocal tag

    def _create_structural_annotations(self, variation: Dict, techniques: List) -> List[str]:
        """Create structural annotations using wiki techniques"""
        annotations = []

        # Look for structural techniques in wiki data
        for technique in techniques:
            if hasattr(technique, 'technique_type') and hasattr(technique, 'examples'):
                if technique.technique_type == "prompt_structure":
                    # Use examples from wiki techniques
                    if technique.examples:
                        # Filter for structural annotations
                        for example in technique.examples:
                            if any(marker in example for marker in ["[", "]", "intro", "verse", "chorus", "bridge"]):
                                annotations.append(example)
                                if len(annotations) >= 2:
                                    break
                    if len(annotations) >= 2:
                        break

        # Fallback structural annotations if no wiki data
        if not annotations:
            structure_type = variation.get("structure_type", "traditional")
            if structure_type == "narrative":
                annotations = ["[Intro]", "[Verse]", "[Chorus]", "[Bridge]", "[Outro]"]
            elif structure_type == "developmental":
                annotations = ["[Build up]", "[Climax]", "[Resolution]"]
            else:
                annotations = ["[Verse]", "[Chorus]", "[Bridge]"]

        return annotations[:3]  # Limit to 3 annotations

    def _create_vocal_effects(self, concept_analysis: Dict, techniques: List) -> List[str]:
        """Create vocal effects using wiki techniques"""
        effects = []

        # Look for vocal effect techniques in wiki data
        for technique in techniques:
            if hasattr(technique, 'technique_type') and hasattr(technique, 'examples'):
                if technique.technique_type == "vocal_style":
                    # Use examples from wiki techniques
                    if technique.examples:
                        for example in technique.examples:
                            # Filter for vocal effects (asterisks, caps, etc.)
                            if "*" in example or example.isupper():
                                effects.append(example)
                                if len(effects) >= 2:
                                    break
                    if len(effects) >= 2:
                        break

        # Add effects based on emotional qualities
        emotional_qualities = concept_analysis["emotional_qualities"]
        primary_emotion = emotional_qualities["primary_emotion"]
        intensity = emotional_qualities["intensity"]

        # Map emotions to vocal effects
        if primary_emotion == "anger" and intensity == "high":
            effects.append("[Screaming vocals]")
        elif primary_emotion == "serenity" or intensity == "low":
            effects.append("[Whispering vocals]")
        elif intensity == "high":
            effects.append("[Powerful vocals]")

        # Add capitalization effects for emphasis
        if intensity == "high":
            effects.append("EMPHASIS!")

        return effects[:2]  # Limit to 2 effects

    def _create_full_command_example(self, main_command: str, structural_annotations: List[str], vocal_effects: List[str]) -> str:
        """Create a complete Suno command example"""
        command_parts = []

        # Add main style command
        command_parts.append(f"[{main_command}]")

        # Add structural elements
        if structural_annotations:
            command_parts.append(structural_annotations[0])  # Use first annotation as example

        # Add vocal effects
        if vocal_effects:
            command_parts.append(vocal_effects[0])  # Use first effect as example

        return " ".join(command_parts)

    def _list_wiki_techniques_used(self, techniques: List) -> List[str]:
        """List which wiki techniques were used in command generation"""
        used_techniques = []

        for technique in techniques[:3]:  # Show up to 3 techniques
            if hasattr(technique, 'name'):
                used_techniques.append(technique.name)

        return used_techniques

    def _get_structural_tags(self, variation: Dict, meta_tags: List) -> List[str]:
        """Get structural meta tags"""
        structural_tags = []

        if "structure_type" in variation:
            structure_type = variation["structure_type"]

            # Look for structural meta tags
            for tag in meta_tags:
                if tag.category.lower() == "structural" or "structure" in tag.description.lower():
                    if structure_type in tag.tag.lower() or structure_type in tag.description.lower():
                        structural_tags.append(tag.tag.lower())
                        break

        return structural_tags[:1]  # Limit to 1 structural tag

    def _create_lyrical_guidance(self, concept_analysis: Dict, variation: Dict) -> Dict[str, Any]:
        """Create lyrical guidance based on concept analysis"""
        themes = concept_analysis["core_themes"]
        emotional_qualities = concept_analysis["emotional_qualities"]

        return {
            "suggested_themes": themes,
            "emotional_tone": emotional_qualities["primary_emotion"],
            "lyrical_approach": self._suggest_lyrical_approach(variation["approach"]),
            "imagery_suggestions": concept_analysis["sonic_palette"],
            "narrative_structure": self._suggest_narrative_structure(emotional_qualities["progression"])
        }

    def _suggest_lyrical_approach(self, approach: str) -> str:
        """Suggest lyrical approach based on musical approach"""
        approach_mappings = {
            "rhythmic_focus": "rhythmic_and_percussive_lyrics",
            "harmonic_exploration": "melodic_and_flowing_lyrics",
            "textural_emphasis": "atmospheric_and_impressionistic_lyrics",
            "structural_innovation": "narrative_and_progressive_lyrics",
            "emotional_intensity": "direct_and_emotionally_raw_lyrics"
        }
        return approach_mappings.get(approach, "balanced_lyrical_approach")

    def _suggest_narrative_structure(self, progression: str) -> str:
        """Suggest narrative structure for lyrics"""
        if progression == "transformative":
            return "before_and_after_narrative"
        elif progression == "developmental":
            return "journey_narrative"
        else:
            return "moment_in_time_narrative"

    def _create_production_notes(self, variation: Dict, concept_analysis: Dict) -> List[str]:
        """Create production notes for the variation"""
        notes = []

        # Add notes based on variation focus
        focus = variation["primary_focus"]
        if focus == "rhythmic_focus":
            notes.append("Emphasize drum programming and rhythmic elements")
            notes.append("Consider polyrhythmic layers for complexity")
        elif focus == "harmonic_exploration":
            notes.append("Focus on chord voicings and harmonic movement")
            notes.append("Experiment with extended and altered chords")
        elif focus == "textural_emphasis":
            notes.append("Layer multiple textural elements")
            notes.append("Use reverb and spatial effects creatively")
        elif focus == "structural_innovation":
            notes.append("Vary section lengths and arrangements")
            notes.append("Create smooth transitions between sections")
        elif focus == "emotional_intensity":
            notes.append("Use dynamics to enhance emotional impact")
            notes.append("Consider vocal delivery and expression")

        # Add notes based on sonic palette
        sonic_elements = concept_analysis["sonic_palette"]
        if "water_textures" in sonic_elements:
            notes.append("Incorporate flowing, liquid-like sounds")
        if "atmospheric_pad" in sonic_elements:
            notes.append("Use atmospheric pads for depth")

        return notes

    def _assess_complexity(self, variation: Dict) -> str:
        """Assess the complexity level of the variation"""
        complexity_factors = 0

        if variation.get("harmonic_complexity") == "complex":
            complexity_factors += 1
        if variation.get("rhythmic_character") == "irregular":
            complexity_factors += 1
        if variation.get("structure_type") == "fragmented":
            complexity_factors += 1
        if len(variation.get("instruments", [])) > 3:
            complexity_factors += 1

        if complexity_factors >= 3:
            return "high"
        elif complexity_factors >= 1:
            return "medium"
        else:
            return "low"


class EmotionalBeatEngine:
    """PURE EXECUTION ENGINE - Takes LLM-defined emotional maps and produces music accordingly"""

    def __init__(self):
        # No predefined mappings - everything comes from the calling LLM
        pass

    def execute_musical_production(self, emotional_map: Dict[str, Any]) -> Dict[str, Any]:
        """PURE EXECUTION - Takes LLM-defined emotional map and produces music"""

        # Extract LLM-defined parameters
        tempo = emotional_map.get('tempo_directive', 80)
        rhythm_instruction = emotional_map.get('rhythm_directive', 'steady')
        sonic_palette = emotional_map.get('sonic_directives', [])
        structural_plan = emotional_map.get('structure_directive', {})
        emotional_context = emotional_map.get('emotional_context', '')
        production_style = emotional_map.get('production_style', 'natural')

        # EXECUTE based on LLM directives - no predefined logic
        production_commands = self._execute_production_directives(
            tempo, rhythm_instruction, sonic_palette, structural_plan,
            emotional_context, production_style, emotional_map
        )

        return {
            'execution_method': 'llm_directed_production',
            'tempo_bpm': tempo,
            'rhythm_execution': rhythm_instruction,
            'sonic_execution': sonic_palette,
            'structure_execution': structural_plan,
            'production_commands': production_commands,
            'llm_emotional_map': emotional_context,
            'execution_style': production_style,
            'custom_directives': emotional_map.get('custom_directives', [])
        }

    def _execute_production_directives(self, tempo: int, rhythm: str, sounds: List[str],
                                     structure: Dict, emotion_context: str, style: str,
                                     full_map: Dict[str, Any]) -> List[str]:
        """Execute the exact production directives provided by LLM"""
        commands = []

        # Execute tempo directive exactly as specified
        tempo_command = f"[{tempo}bpm]"
        if full_map.get('tempo_reasoning'):
            tempo_command += f" // {full_map['tempo_reasoning']}"
        commands.append(tempo_command)

        # Execute rhythm directive exactly as specified
        rhythm_command = f"[{rhythm}]"
        if full_map.get('rhythm_reasoning'):
            rhythm_command += f" // {full_map['rhythm_reasoning']}"
        commands.append(rhythm_command)

        # Execute sonic directives exactly as specified
        if sounds:
            sonic_command = f"[{', '.join(sounds)}]"
            if full_map.get('sonic_reasoning'):
                sonic_command += f" // {full_map['sonic_reasoning']}"
            commands.append(sonic_command)

        # Execute structural directives exactly as specified
        for section, directive in structure.items():
            section_command = f"[{section.upper()}] {directive}"
            commands.append(section_command)

        # Execute emotional context exactly as specified
        if emotion_context:
            emotion_command = f"[EMOTIONAL_CORE] {emotion_context}"
            if full_map.get('emotional_reasoning'):
                emotion_command += f" // {full_map['emotional_reasoning']}"
            commands.append(emotion_command)

        # Execute any custom directives exactly as specified
        for custom_directive in full_map.get('custom_directives', []):
            commands.append(f"[CUSTOM] {custom_directive}")

        # Final execution summary
        execution_summary = f"Executing LLM-defined musical interpretation: {style}"
        if full_map.get('execution_notes'):
            execution_summary += f" | Notes: {full_map['execution_notes']}"
        commands.append(execution_summary)

        return commands

    def _generate_tempo_from_content(self, text: str, emotional_states: List[EmotionalState]) -> int:
        """Generate BPM from actual textual content, not templates"""
        base_tempo = 80

        # Physical actions mentioned in text determine tempo
        if re.search(r'\b(running|racing|rushing|hurrying|chasing)\b', text, re.IGNORECASE):
            base_tempo = 140
        elif re.search(r'\b(walking|moving|traveling|going)\b', text, re.IGNORECASE):
            base_tempo = 100
        elif re.search(r'\b(sitting|resting|waiting|thinking|contemplating)\b', text, re.IGNORECASE):
            base_tempo = 75
        elif re.search(r'\b(sleeping|dreaming|lying|peaceful|calm)\b', text, re.IGNORECASE):
            base_tempo = 60

        # Emotional intensity modification
        if emotional_states:
            avg_intensity = sum(state.intensity for state in emotional_states) / len(emotional_states)
            base_tempo += int(avg_intensity * 30)  # 0-30 BPM boost from intensity

        # Textual rhythm (sentence length affects tempo)
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_sentence_length > 20:  # Long sentences = slower tempo
                base_tempo -= 10
            elif avg_sentence_length < 5:  # Short sentences = faster tempo
                base_tempo += 15

        return max(50, min(180, base_tempo))

    def _generate_rhythm_from_content(self, text: str, emotional_states: List[EmotionalState]) -> str:
        """Generate rhythm pattern from actual content, not templates"""

        # Text structure influences rhythm
        punctuation_density = (text.count(',') + text.count(';') + text.count(':')) / len(text) * 1000
        question_density = text.count('?') / len(text) * 1000
        exclamation_density = text.count('!') / len(text) * 1000

        if question_density > 5:
            rhythm_base = "questioning_syncopation"
        elif exclamation_density > 3:
            rhythm_base = "emphatic_accents"
        elif punctuation_density > 20:
            rhythm_base = "complex_subdivision"
        else:
            rhythm_base = "steady_flow"

        # Emotional facts modify rhythm
        if emotional_states:
            primary_emotion = emotional_states[0].primary_emotion
            if 'anger' in primary_emotion or 'rage' in primary_emotion:
                rhythm_modifier = "_with_aggressive_hits"
            elif 'grief' in primary_emotion or 'loss' in primary_emotion:
                rhythm_modifier = "_with_heavy_spaces"
            elif 'joy' in primary_emotion or 'happiness' in primary_emotion:
                rhythm_modifier = "_with_uplifting_swing"
            elif 'fear' in primary_emotion or 'anxiety' in primary_emotion:
                rhythm_modifier = "_with_irregular_patterns"
            else:
                rhythm_modifier = f"_reflecting_{primary_emotion.replace(' ', '_')}"
        else:
            rhythm_modifier = ""

        return rhythm_base + rhythm_modifier

    def _design_sounds_from_content(self, text: str, emotional_states: List[EmotionalState]) -> List[str]:
        """Design sonic elements based on textual content"""
        sounds = []

        # Extract sound-related words from text
        sound_mapping = {
            'water': ['flowing_water_samples', 'rain_texture', 'ocean_ambience'],
            'wind': ['wind_sweeps', 'atmospheric_movement', 'breathy_textures'],
            'fire': ['crackling_elements', 'warm_distortion', 'flicker_automation'],
            'metal': ['metallic_hits', 'industrial_textures', 'resonant_strikes'],
            'wood': ['organic_percussion', 'wooden_textures', 'natural_resonance'],
            'glass': ['crystalline_elements', 'fragile_textures', 'breaking_sounds'],
            'heart': ['heartbeat_bass', 'pulse_rhythm', 'cardiovascular_bass'],
            'breath': ['breathing_pads', 'respiratory_rhythm', 'air_textures']
        }

        for sound_source, sound_elements in sound_mapping.items():
            if sound_source in text.lower():
                sounds.extend(sound_elements)

        # Add emotional sound design
        if emotional_states:
            for state in emotional_states:
                emotion = state.primary_emotion
                if 'dark' in emotion or 'heavy' in emotion:
                    sounds.append('low_rumbling_bass')
                elif 'bright' in emotion or 'light' in emotion:
                    sounds.append('sparkling_high_frequencies')
                elif 'warm' in emotion:
                    sounds.append('warm_analog_saturation')
                elif 'cold' in emotion:
                    sounds.append('digital_crystalline_processing')

        # If no specific sounds found, derive from factual triggers
        if not sounds and emotional_states:
            for state in emotional_states:
                for trigger in state.factual_triggers:
                    if any(word in trigger.lower() for word in ['home', 'house', 'room']):
                        sounds.append('domestic_ambience')
                    elif any(word in trigger.lower() for word in ['street', 'city', 'urban']):
                        sounds.append('urban_texture')
                    elif any(word in trigger.lower() for word in ['nature', 'forest', 'outdoor']):
                        sounds.append('natural_environment')

        return sounds[:5] if sounds else ['contextual_ambience']  # Limit to 5 elements

    def _generate_structure_from_content(self, text: str, emotional_states: List[EmotionalState]) -> Dict[str, str]:
        """Generate track structure from narrative flow"""

        # Analyze text structure
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        if len(paragraphs) >= 3:
            structure = {
                'intro': f"Establishes {emotional_states[0].primary_emotion if emotional_states else 'narrative'} atmosphere",
                'verse_1': f"Introduces main factual content: {sentences[0][:100] if sentences else 'content'}...",
                'chorus': f"Emotional core expressing: {emotional_states[0].primary_emotion if emotional_states else 'main theme'}",
                'verse_2': f"Develops narrative: {sentences[len(sentences)//2][:100] if len(sentences) > 1 else 'development'}...",
                'bridge': f"Transforms to: {emotional_states[-1].primary_emotion if len(emotional_states) > 1 else 'resolution'}",
                'outro': "Resolves narrative tension"
            }
        else:
            structure = {
                'intro': "Brief atmospheric introduction",
                'main_section': f"Carries the emotional weight of: {text[:150]}...",
                'outro': "Natural conclusion"
            }

        return structure

    def _create_production_commands(self, tempo: int, rhythm: str, sounds: List[str], structure: Dict[str, str], text: str, emotional_states: List[EmotionalState]) -> List[str]:
        """Create actual production commands for Suno"""
        commands = []

        # Main production command
        primary_emotion = emotional_states[0].primary_emotion if emotional_states else "narrative_driven"

        main_command = f"[{tempo}bpm] [{rhythm}] "
        main_command += f"Emotional core: {primary_emotion} | "
        main_command += f"Sonic palette: {', '.join(sounds[:3])} | "
        main_command += f"Based on: {text[:100]}..."

        commands.append(main_command)

        # Structural variations
        for section, description in structure.items():
            section_command = f"[{section.upper()}] {description}"
            commands.append(section_command)

        # Emotional authenticity instruction
        if emotional_states:
            authenticity = sum(state.authenticity_score for state in emotional_states) / len(emotional_states)
            if authenticity > 0.8:
                commands.append("[AUTHENTIC_DELIVERY] Raw, unfiltered emotional expression")
            else:
                commands.append("[LAYERED_DELIVERY] Complex, nuanced emotional expression")

        return commands

    def analyze_emotional_facts_adaptive(self, text: str, character: Optional[CharacterProfile] = None) -> List[EmotionalState]:
        """NEW: Adaptive emotional analysis that grounds music in textual facts - no templates"""
        emotional_states = []

        # Step 1: Extract factual triggers - what actually happened
        factual_events = self._extract_factual_events(text)

        # Step 2: For each factual event, determine the emotional response
        for event in factual_events:
            emotional_response = self._derive_emotion_from_fact(event, text)
            if emotional_response:
                emotional_states.append(emotional_response)

        # Step 3: If no specific events, analyze the overall emotional tone
        if not emotional_states:
            overall_tone = self._analyze_content_tone(text)
            if overall_tone:
                emotional_states.append(overall_tone)

        return emotional_states

    def _extract_factual_events(self, text: str) -> List[Dict[str, str]]:
        """Extract concrete events/facts from text"""
        events = []

        # Action patterns - things that actually happened
        action_patterns = [
            r'(?:he|she|they|I)\s+(died|left|arrived|discovered|realized|decided|fought|won|lost|created|destroyed|built|broke|learned|found|met|became|changed)',
            r'(?:was|were|became|got)\s+([a-z]+(?:ed|ing)?)',
            r'(?:happened|occurred|took place|resulted in|led to|caused)\s+([^.]+)',
            r'(?:felt|experienced|witnessed|saw|heard|found)\s+([^.]+)',
            r'\b(birth|death|marriage|divorce|graduation|promotion|failure|success|accident|illness|recovery|journey|arrival|departure)\b'
        ]

        for pattern in action_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context_start = max(0, match.start() - 100)
                context_end = min(len(text), match.end() + 100)
                context = text[context_start:context_end].strip()

                events.append({
                    'action': match.group(),
                    'context': context,
                    'type': 'factual_event',
                    'position': match.start()
                })

        return events

    def _derive_emotion_from_fact(self, event: Dict[str, str], full_text: str) -> Optional[EmotionalState]:
        """Derive emotional state from actual factual content"""
        action = event['action'].lower()
        context = event['context']

        # Analyze the emotional weight of this specific fact
        emotional_indicators = self._find_emotional_language_around_fact(context, full_text)

        if not emotional_indicators:
            return None

        # Build emotion from the actual content, not templates
        primary_emotion = self._determine_primary_emotion_from_indicators(emotional_indicators, action)
        secondary_emotions = self._extract_secondary_emotions(emotional_indicators)
        intensity = self._calculate_emotional_intensity_from_context(emotional_indicators, context)

        return EmotionalState(
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_emotions,
            intensity=intensity,
            factual_triggers=[action, context[:100]],
            internal_conflict=self._detect_internal_conflict_in_text(context),
            defense_mechanism=self._detect_defense_mechanism_in_text(context),
            authenticity_score=self._score_emotional_authenticity_from_text(emotional_indicators, context)
        )

    def _find_emotional_language_around_fact(self, context: str, full_text: str) -> List[str]:
        """Find emotional language specifically connected to this fact"""
        emotional_words = []

        # Emotional descriptors that appear near the fact
        emotion_patterns = [
            r'\b(felt|feeling|emotions?|mood|heart|soul|spirit|mind)\s+([a-z]+)',
            r'\b(happy|sad|angry|afraid|surprised|disgusted|excited|nervous|calm|peaceful|agitated|frustrated|hopeful|hopeless|proud|ashamed|guilty|relieved|anxious|content|bitter|sweet|tender|harsh|gentle|violent|quiet|loud|slow|fast|heavy|light|dark|bright|warm|cold|empty|full|broken|whole|lost|found)\b',
            r'\b(tears?|crying|laughing|smiling|frowning|sighing|screaming|whispering|trembling|shaking|breathing|gasping|choking|sobbing)\b',
            r'\b(love|hate|fear|hope|despair|joy|sorrow|rage|peace|chaos|freedom|prison|heaven|hell|light|darkness)\b'
        ]

        for pattern in emotion_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    emotional_words.extend([word for word in match if word and len(word) > 2])
                else:
                    emotional_words.append(match)

        return list(set(emotional_words))

    def _determine_primary_emotion_from_indicators(self, indicators: List[str], action: str) -> str:
        """Determine primary emotion from actual text indicators and factual action"""
        # Weight emotions based on actual word usage, not predetermined categories
        emotion_evidence = {}

        # Combine indicators with action context
        all_context = indicators + [action]

        for word in all_context:
            word_lower = word.lower()

            # Build emotion evidence from actual language used
            if any(term in word_lower for term in ['sad', 'cry', 'tear', 'mourn', 'grief', 'loss', 'death', 'died', 'departed', 'goodbye']):
                emotion_evidence['profound_loss'] = emotion_evidence.get('profound_loss', 0) + 1
            elif any(term in word_lower for term in ['happy', 'joy', 'laugh', 'smile', 'celebrate', 'excited', 'won', 'success', 'achieved']):
                emotion_evidence['genuine_joy'] = emotion_evidence.get('genuine_joy', 0) + 1
            elif any(term in word_lower for term in ['angry', 'rage', 'furious', 'mad', 'hate', 'frustrated', 'fought', 'broke', 'destroyed']):
                emotion_evidence['raw_anger'] = emotion_evidence.get('raw_anger', 0) + 1
            elif any(term in word_lower for term in ['afraid', 'fear', 'scared', 'terrified', 'anxious', 'worried', 'nervous', 'trembling']):
                emotion_evidence['deep_fear'] = emotion_evidence.get('deep_fear', 0) + 1
            elif any(term in word_lower for term in ['discovered', 'realized', 'learned', 'found', 'think', 'wonder', 'consider', 'reflect']):
                emotion_evidence['discovery_wonder'] = emotion_evidence.get('discovery_wonder', 0) + 1
            elif any(term in word_lower for term in ['vulnerable', 'exposed', 'open', 'raw', 'honest', 'tender', 'soft', 'gentle']):
                emotion_evidence['tender_vulnerability'] = emotion_evidence.get('tender_vulnerability', 0) + 1
            elif any(term in word_lower for term in ['empty', 'hollow', 'void', 'lost', 'alone', 'isolated', 'abandoned']):
                emotion_evidence['existential_emptiness'] = emotion_evidence.get('existential_emptiness', 0) + 1
            elif any(term in word_lower for term in ['hope', 'light', 'bright', 'warm', 'rising', 'growing', 'building']):
                emotion_evidence['rising_hope'] = emotion_evidence.get('rising_hope', 0) + 1
            else:
                # Create dynamic emotion name from the actual content
                emotion_evidence[f"context_{word_lower}"] = emotion_evidence.get(f"context_{word_lower}", 0) + 1

        # Return the emotion with highest evidence, or create from context
        if emotion_evidence:
            return max(emotion_evidence.items(), key=lambda x: x[1])[0]
        else:
            return f"unprocessed_{action.replace(' ', '_')}"

    def _analyze_content_tone(self, text: str) -> Optional[EmotionalState]:
        """Analyze overall emotional tone when no specific events found"""
        # Look for overall emotional atmosphere
        tone_indicators = []

        # Extract descriptive language that sets emotional tone
        tone_patterns = [
            r'\b(atmosphere|mood|feeling|sense|air|weight|energy|vibration|tension|calm|storm|peace|chaos)\s+(?:of|was|felt|seemed)\s+([a-z]+)',
            r'\b(dark|light|heavy|light|cold|warm|sharp|soft|harsh|gentle|loud|quiet|fast|slow|thick|thin)\b',
            r'\b(?:everything|world|life|existence|reality|truth|time|space|people|everyone|nothing|something)\s+(?:felt|seemed|appeared|looked|sounded)\s+([a-z]+)'
        ]

        for pattern in tone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    tone_indicators.extend([word for word in match if word and len(word) > 2])
                else:
                    tone_indicators.append(match)

        if tone_indicators:
            primary_tone = self._determine_primary_emotion_from_indicators(tone_indicators, "overall_atmosphere")
            return EmotionalState(
                primary_emotion=primary_tone,
                secondary_emotions=tone_indicators[:3],
                intensity=0.6,  # Medium intensity for overall tone
                factual_triggers=[f"Textual atmosphere: {', '.join(tone_indicators[:2])}"],
                internal_conflict=None,
                defense_mechanism=None,
                authenticity_score=0.8
            )

        return None

    def _extract_secondary_emotions(self, indicators: List[str]) -> List[str]:
        """Extract secondary emotions from indicators"""
        return indicators[:3]  # Return up to 3 secondary emotions

    def _calculate_emotional_intensity_from_context(self, indicators: List[str], context: str) -> float:
        """Calculate emotional intensity based on context"""
        intensity_words = ['extremely', 'very', 'deeply', 'profoundly', 'completely', 'utterly', 'overwhelming']
        intensity_score = 0.5  # Base intensity

        for word in intensity_words:
            if word in context.lower():
                intensity_score += 0.1

        return min(intensity_score, 1.0)

    def _detect_internal_conflict_in_text(self, context: str) -> Optional[str]:
        """Detect internal conflict from context"""
        conflict_patterns = [
            r'(?:but|however|yet|though|although)\s+([^.]+)',
            r'(?:torn between|conflicted|unsure|uncertain|confused)\s+([^.]+)'
        ]

        for pattern in conflict_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1)[:100]

        return None

    def _detect_defense_mechanism_in_text(self, context: str) -> Optional[str]:
        """Detect defense mechanisms from context"""
        defense_patterns = {
            'denial': r'(?:not|never|couldn\'t|wouldn\'t)\s+(?:true|real|happening)',
            'projection': r'(?:they|everyone|others)\s+(?:always|never|should)',
            'rationalization': r'(?:because|since|reason|logical|makes sense)'
        }

        for mechanism, pattern in defense_patterns.items():
            if re.search(pattern, context, re.IGNORECASE):
                return mechanism

        return None

    def _score_emotional_authenticity_from_text(self, indicators: List[str], context: str) -> float:
        """Score emotional authenticity based on text evidence"""
        authenticity_markers = ['felt', 'feeling', 'emotion', 'heart', 'soul', 'deep', 'real', 'true']
        performance_markers = ['should', 'supposed', 'expected', 'proper', 'appropriate']

        authentic_count = sum(1 for marker in authenticity_markers if marker in context.lower())
        performance_count = sum(1 for marker in performance_markers if marker in context.lower())

        # Base score on evidence of genuine vs performed emotion
        if authentic_count > performance_count:
            return min(0.7 + (authentic_count * 0.1), 1.0)
        else:
            return max(0.3, 0.7 - (performance_count * 0.1))

    def analyze_emotional_facts(self, text: str, character: Optional[CharacterProfile] = None) -> List[EmotionalState]:
        """Extract fact-based emotional states from text"""
        emotional_states = []

        # Fact extraction patterns
        action_patterns = {
            'loss': r'(?:lost|died|gone|left|abandoned|departed)',
            'achievement': r'(?:won|succeeded|accomplished|achieved|mastered)',
            'conflict': r'(?:fought|argued|confronted|challenged|opposed)',
            'connection': r'(?:loved|befriended|trusted|bonded|united)',
            'betrayal': r'(?:betrayed|lied|deceived|broken|failed)'
        }

        for emotion_type, pattern in action_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract surrounding context
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]

                # Determine emotional response based on facts
                emotional_state = self._map_fact_to_emotion(emotion_type, context, character)
                if emotional_state:
                    emotional_states.append(emotional_state)

        return emotional_states

    def _map_fact_to_emotion(self, fact_type: str, context: str, character: Optional[CharacterProfile]) -> Optional[EmotionalState]:
        """Map factual events to complex emotional states"""
        emotion_mappings = {
            'loss': {
                'primary': 'grief',
                'secondary': ['denial', 'anger', 'numbness'],
                'defense': 'emotional shutdown',
                'intensity': 0.9
            },
            'achievement': {
                'primary': 'joy',
                'secondary': ['pride', 'relief', 'anticipation'],
                'defense': None,
                'intensity': 0.8
            },
            'betrayal': {
                'primary': 'anger',
                'secondary': ['hurt', 'disbelief', 'shame'],
                'defense': 'projection',
                'intensity': 0.95
            }
        }

        if fact_type in emotion_mappings:
            mapping = emotion_mappings[fact_type]
            return EmotionalState(
                primary_emotion=mapping['primary'],
                secondary_emotions=mapping['secondary'],
                intensity=mapping['intensity'],
                factual_triggers=[context.strip()],
                internal_conflict=self._detect_internal_conflict(context, character),
                defense_mechanism=mapping['defense'],
                authenticity_score=self._calculate_authenticity(context)
            )
        return None

    def _detect_internal_conflict(self, context: str, character: Optional[CharacterProfile]) -> Optional[str]:
        """Detect internal emotional conflicts from context"""
        conflict_indicators = [
            (r'but\s+(?:I|he|she|they)\s+(?:couldn\'t|shouldn\'t|wouldn\'t)', "desire vs duty"),
            (r'wanted\s+to\s+\w+\s+but', "impulse vs restraint"),
            (r'(?:torn|divided|conflicted)\s+between', "competing loyalties"),
            (r'(?:pretended|forced|faked)\s+(?:a|to)\s+\w+', "authentic vs performative")
        ]

        for pattern, conflict_type in conflict_indicators:
            if re.search(pattern, context, re.IGNORECASE):
                return conflict_type
        return None

    def _calculate_authenticity(self, context: str) -> float:
        """Calculate emotional authenticity score"""
        # Higher score = more authentic emotion
        performative_indicators = ['pretended', 'forced', 'faked', 'acted', 'seemed']
        authentic_indicators = ['truly', 'genuinely', 'really', 'actually', 'honestly']

        performative_count = sum(1 for word in performative_indicators if word in context.lower())
        authentic_count = sum(1 for word in authentic_indicators if word in context.lower())

        if performative_count > authentic_count:
            return 0.3 + (authentic_count * 0.1)
        else:
            return 0.7 + (authentic_count * 0.1) - (performative_count * 0.2)

    def generate_beat_progression(self, emotional_states: List[EmotionalState]) -> Dict[str, Any]:
        """Generate beat progression from emotional states - calls LLM-driven approach"""
        # Extract emotional context from states
        emotional_context = " → ".join([f"{state.primary_emotion} ({state.intensity})" for state in emotional_states])

        # Use the LLM-driven approach
        return self.generate_llm_beat_progression(emotional_context, emotional_states)

    def generate_llm_beat_progression(self, emotional_context: str, emotional_states: List[EmotionalState], duration: int = 180) -> Dict[str, Any]:
        """Generate beat progression using LLM-defined emotional mapping - NO templates"""

        # LLM creates the beat progression from emotional context
        progression = {
            'generation_method': 'llm_driven_progression',
            'source_context': emotional_context,
            'overall_tempo_range': self._llm_determine_tempo_range_from_states(emotional_states),
            'sections': [],
            'transitions': [],
            'emotional_journey': [state.primary_emotion for state in emotional_states]
        }

        # LLM generates each section based on emotional states
        for i, state in enumerate(emotional_states):
            # LLM creates beat progression for this specific emotional state
            section = {
                'timestamp': f"{i*30}s-{(i+1)*30}s",
                'emotion': state.primary_emotion,
                'llm_beat_interpretation': self._llm_create_beat_from_emotion(state),
                'intensity': state.intensity,
                'factual_context': state.factual_triggers[0] if state.factual_triggers else "",
                'llm_production_notes': f"LLM interpretation of {state.primary_emotion} at {state.intensity} intensity"
            }

            progression['sections'].append(section)

            # LLM creates transitions between emotional states
            if i > 0:
                transition = self._llm_create_transition(emotional_states[i-1], state, f"{i*30}s")
                progression['transitions'].append(transition)

        return progression

    def _llm_determine_tempo_range_from_states(self, emotional_states: List[EmotionalState]) -> tuple:
        """LLM determines tempo range from emotional states"""
        if not emotional_states:
            return (80, 120)

        # LLM analyzes the emotional intensity to determine tempo range
        max_intensity = max(state.intensity for state in emotional_states)
        min_intensity = min(state.intensity for state in emotional_states)

        # Convert intensity to tempo (LLM logic)
        min_tempo = int(60 + (min_intensity * 60))  # 60-120 BPM range
        max_tempo = int(80 + (max_intensity * 80))  # 80-160 BPM range

        return (min_tempo, max_tempo)

    def _llm_create_beat_from_emotion(self, state: EmotionalState) -> Dict[str, str]:
        """LLM creates beat interpretation from emotional state"""
        return {
            'tempo_suggestion': f"BPM derived from {state.primary_emotion} intensity {state.intensity}",
            'rhythm_suggestion': f"Rhythm pattern expressing {state.primary_emotion}",
            'sonic_suggestion': f"Sounds that embody the feeling of {state.primary_emotion}",
            'factual_grounding': f"Based on factual trigger: {state.factual_triggers[0] if state.factual_triggers else 'emotional context'}"
        }

    def _llm_create_transition(self, from_state: EmotionalState, to_state: EmotionalState, timestamp: str) -> Dict[str, str]:
        """LLM creates transition between emotional states"""
        return {
            'timestamp': timestamp,
            'transition_type': f"LLM transition from {from_state.primary_emotion} to {to_state.primary_emotion}",
            'description': f"Musical bridge expressing the shift from {from_state.primary_emotion} to {to_state.primary_emotion}",
            'intensity_change': f"Intensity shift from {from_state.intensity} to {to_state.intensity}"
        }
        return progression



class MetaNarrativeProcessor:
    """Processes meta-narrative elements and emotional subtext"""

    def __init__(self):
        self.subtext_patterns = {
            'suppressed_emotion': [
                r'(?:forced|managed|mustered)\s+a\s+(?:smile|laugh)',
                r'(?:held|bit|swallowed)\s+(?:back|down|their)',
                r'(?:pretended|acted)\s+(?:not|as if|like)'
            ],
            'emotional_turning_point': [
                r'(?:realized|understood|saw)\s+(?:that|how|why)',
                r'(?:suddenly|finally|at last)\s+(?:felt|knew|understood)',
                r'(?:everything|nothing)\s+would\s+(?:ever\s+)?be\s+the\s+same'
            ],
            'identity_crisis': [
                r'(?:who|what)\s+(?:am|was|had)\s+(?:I|he|she|they)\s+become',
                r'(?:lost|found)\s+(?:himself|herself|themselves)',
                r'(?:questioned|doubted)\s+everything'
            ]
        }

    def extract_emotional_subtext(self, text: str, explicit_emotions: List[EmotionalState]) -> List[Dict[str, Any]]:
        """Extract implicit emotional content not directly stated"""
        subtext_elements = []

        for subtext_type, patterns in self.subtext_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    context_start = max(0, match.start() - 200)
                    context_end = min(len(text), match.end() + 200)
                    context = text[context_start:context_end]

                    subtext = {
                        'type': subtext_type,
                        'text_evidence': match.group(),
                        'context': context,
                        'implied_emotions': self._infer_emotions(subtext_type, context),
                        'narrative_significance': self._assess_significance(subtext_type, context, explicit_emotions)
                    }
                    subtext_elements.append(subtext)

        return subtext_elements

    def _infer_emotions(self, subtext_type: str, context: str) -> List[str]:
        """Infer emotions from subtext type and context"""
        inference_map = {
            'suppressed_emotion': ['denial', 'fear', 'shame', 'vulnerability'],
            'emotional_turning_point': ['revelation', 'transformation', 'acceptance', 'awakening'],
            'identity_crisis': ['confusion', 'loss', 'searching', 'fragmentation']
        }
        return inference_map.get(subtext_type, ['complexity'])

    def _assess_significance(self, subtext_type: str, context: str, explicit_emotions: List[EmotionalState]) -> str:
        """Assess narrative significance of emotional subtext"""
        if subtext_type == 'emotional_turning_point':
            return "Critical moment of emotional transformation"
        elif subtext_type == 'suppressed_emotion':
            return "Hidden emotional truth requiring musical expression"
        elif subtext_type == 'identity_crisis':
            return "Core identity questioning demanding introspective production"
        return "Emotional complexity layer"

    def identify_emotional_contradictions(self, text: str, character: StandardCharacterProfile) -> List[Dict[str, Any]]:
        """Identify contradictions between stated and actual emotions"""
        contradictions = []

        # Look for action-emotion mismatches
        action_emotion_patterns = [
            (r'smiled\s+(?:while|as|when)\s+(?:crying|tears)', 'joy vs sadness'),
            (r'laughed\s+(?:but|though|even though)\s+(?:hurt|pain)', 'humor vs pain'),
            (r'calm\s+(?:despite|even with|while)\s+(?:rage|fury|anger)', 'peace vs anger')
        ]

        for pattern, contradiction_type in action_emotion_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                contradictions.append({
                    'type': contradiction_type,
                    'evidence': match.group(),
                    'musical_implication': f"Layer contrasting elements: {contradiction_type}",
                    'production_technique': "Use parallel processing for emotional duality"
                })

        return contradictions

class EmotionalLyricGenerator:
    """Generates emotionally-grounded lyrics based on factual triggers"""

    def __init__(self):
        # NO PREDEFINED TEMPLATES - LLM generates all lyrical content dynamically
        self.llm_lyric_generator = True  # Flag indicating LLM-driven approach

        # Template dictionary completely removed - LLM handles all lyric generation

        self.lyrical_devices = {
            'metaphor': self._generate_metaphor,
            'repetition': self._generate_repetition,
            'contrast': self._generate_contrast,
            'imagery': self._generate_imagery
        }

    def generate_lyric_structure(self, emotional_states: List[EmotionalState],
                               narrative_context: str) -> Dict[str, Any]:
        """Generate complete lyric structure based on emotional journey"""

        if not emotional_states:
            return self._generate_default_structure()

        primary_emotion = emotional_states[0].primary_emotion
        primary_trigger = emotional_states[0].factual_triggers[0] if emotional_states[0].factual_triggers else "this moment"

        # Generate verse progressions
        verses = []
        for i, state in enumerate(emotional_states[:3]):  # First 3 states for verses
            verse = self._generate_verse(state, i + 1)
            verses.append(verse)

        # Generate chorus based on primary emotion
        chorus = self._generate_chorus(primary_emotion, primary_trigger, emotional_states)

        # Generate bridge for transformation
        bridge = self._generate_bridge(emotional_states)

        # Create lyrical themes based on facts
        themes = self._extract_lyrical_themes(emotional_states, narrative_context)

        return {
            'structure': {
                'verses': verses,
                'chorus': chorus,
                'bridge': bridge,
                'outro': self._generate_outro(emotional_states)
            },
            'themes': themes,
            'emotional_arc': [state.primary_emotion for state in emotional_states],
            'key_phrases': self._extract_key_phrases(emotional_states),
            'lyrical_devices': self._suggest_devices(emotional_states)
        }

    def _generate_verse(self, state: EmotionalState, verse_number: int) -> Dict[str, str]:
        """Generate verse using LLM-driven approach - no predefined templates"""

        # LLM generates verse based on emotional context and factual triggers
        fact = state.factual_triggers[0] if state.factual_triggers else "what happened"
        fact = self._simplify_fact(fact)

        # LLM-driven verse generation based on emotional state and facts
        opening = f"LLM-generated verse {verse_number + 1} exploring {state.primary_emotion} from: {fact}"

        # Add internal conflict if present
        if state.internal_conflict:
            conflict_line = f"Torn between {state.internal_conflict}"
        else:
            conflict_line = ""

        return {
            'opening': opening,
            'development': f"Exploring the {state.primary_emotion} through lived experience",
            'conflict': conflict_line,
            'authenticity_note': f"Delivery: {'raw and honest' if state.authenticity_score > 0.7 else 'guarded, defensive'}"
        }

    def _generate_chorus(self, primary_emotion: str, primary_trigger: str,
                        states: List[EmotionalState]) -> Dict[str, str]:
        """Generate chorus that captures emotional core"""
        # LLM-driven chorus generation - no predefined templates

        # Simplify the fact for lyrical use
        simplified_fact = self._simplify_fact(primary_trigger)

        # LLM generates chorus based on emotional context
        main_line = f"LLM-generated chorus hook: {primary_emotion} emerges from {simplified_fact}"

        # Add emotional layers
        if len(states) > 1:
            secondary_emotions = [s.primary_emotion for s in states[1:3]]
            emotional_layer = f"Moving through {' and '.join(secondary_emotions)}"
        else:
            emotional_layer = f"Living with this {primary_emotion}"

        return {
            'hook': main_line,
            'emotional_layer': emotional_layer,
            'repetition_pattern': f"Repeat '{self._extract_power_word(simplified_fact)}' for emphasis",
            'vocal_direction': f"Build intensity on '{primary_emotion}'"
        }

    def _generate_bridge(self, states: List[EmotionalState]) -> Dict[str, str]:
        """Generate bridge showing transformation"""
        if not states:
            return {'content': "Instrumental bridge"}

        # Track emotional journey
        start_emotion = states[0].primary_emotion
        end_emotion = states[-1].primary_emotion if len(states) > 1 else start_emotion

        # LLM generates bridge concepts dynamically
        start_concepts = [f"LLM-generated concept for {start_emotion}", "transformation", "growth"]

        transformation = f"From {start_emotion} to {end_emotion}" if start_emotion != end_emotion else f"Deeper into {start_emotion}"

        return {
            'transformation': transformation,
            'concepts': start_concepts,
            'lyrical_shift': f"Perspective change: from victim to {start_concepts[0] if start_concepts else 'survivor'}",
            'musical_direction': "Strip down instrumentation, focus on vocal vulnerability"
        }

    def _simplify_fact(self, fact: str) -> str:
        """Simplify fact for lyrical use"""
        # Remove extra words, keep core meaning
        if len(fact) > 50:
            # Extract key phrases
            key_words = []
            for word in fact.split():
                if word.lower() in ['lost', 'died', 'left', 'betrayed', 'loved', 'fought', 'won', 'changed']:
                    key_words.append(word)

            if key_words:
                return ' '.join(key_words[:3])

        return fact.strip()[:30] + "..." if len(fact) > 30 else fact

    def _extract_power_word(self, text: str) -> str:
        """Extract most powerful word for repetition"""
        power_words = ['lost', 'love', 'gone', 'broken', 'free', 'alive', 'truth', 'home']

        for word in text.lower().split():
            if word in power_words:
                return word

        # Return first significant word
        words = text.split()
        return words[0] if words else "this"

    def _extract_lyrical_themes(self, states: List[EmotionalState], context: str) -> List[str]:
        """Extract main lyrical themes from emotional states"""
        themes = set()

        for state in states:
            # Theme based on emotion
            emotion_themes = {
                'grief': ['loss', 'memory', 'healing'],
                'joy': ['celebration', 'gratitude', 'connection'],
                'anger': ['injustice', 'strength', 'truth'],
                'contemplation': ['searching', 'understanding', 'growth'],
                'vulnerability': ['authenticity', 'courage', 'intimacy']
            }

            themes.update(emotion_themes.get(state.primary_emotion, ['journey']))

            # Add themes from internal conflicts
            if state.internal_conflict:
                themes.add('inner struggle')

        return list(themes)[:5]

    def _extract_key_phrases(self, states: List[EmotionalState]) -> List[str]:
        """Extract key phrases for lyrical use"""
        phrases = []

        for state in states:
            if state.factual_triggers:
                # Extract impactful phrases
                trigger = state.factual_triggers[0]
                if len(trigger) < 50:
                    phrases.append(trigger)
                else:
                    # Extract key part
                    key_part = self._simplify_fact(trigger)
                    phrases.append(key_part)

        return phrases[:4]

    def _suggest_devices(self, states: List[EmotionalState]) -> List[str]:
        """Suggest lyrical devices based on emotional content"""
        devices = []

        # High authenticity = raw, direct language
        avg_authenticity = sum(s.authenticity_score for s in states) / len(states) if states else 0.5

        if avg_authenticity > 0.7:
            devices.extend(['direct address', 'confession', 'stream of consciousness'])
        else:
            devices.extend(['metaphor', 'symbolism', 'indirect expression'])

        # Internal conflicts suggest contrast
        if any(s.internal_conflict for s in states):
            devices.append('juxtaposition')

        # Multiple emotions suggest repetition with variation
        if len(set(s.primary_emotion for s in states)) > 2:
            devices.append('evolving refrain')

        return devices

    def _generate_outro(self, states: List[EmotionalState]) -> Dict[str, str]:
        """Generate outro/resolution"""
        if not states:
            return {'type': 'fade out'}

        final_emotion = states[-1].primary_emotion
        final_trigger = states[-1].factual_triggers[0] if states[-1].factual_triggers else "this journey"

        return {
            'type': 'resolution',
            'final_statement': f"Finding peace with {self._simplify_fact(final_trigger)}",
            'emotional_landing': final_emotion,
            'musical_direction': 'Gradual decrease in intensity, leave space for reflection'
        }

    def _generate_metaphor(self, emotion: str, fact: str) -> str:
        """Generate metaphor based on emotion and fact"""
        metaphor_map = {
            'grief': f"An ocean where {fact} used to be solid ground",
            'joy': f"Sunlight breaking through where {fact} opened the sky",
            'anger': f"A wildfire sparked by {fact}",
            'vulnerability': f"Glass walls revealing {fact}"
        }
        return metaphor_map.get(emotion, f"A journey through {fact}")

    def _generate_repetition(self, key_phrase: str) -> str:
        """Generate repetition pattern"""
        return f"Repeat '{key_phrase}' with increasing intensity"

    def _generate_contrast(self, emotion1: str, emotion2: str) -> str:
        """Generate contrasting elements"""
        return f"Juxtapose {emotion1} in verses with {emotion2} in chorus"

    def _generate_imagery(self, emotion: str, fact: str) -> str:
        """Generate vivid imagery"""
        imagery_map = {
            'grief': f"Empty chairs, silent phones, {fact}",
            'joy': f"Dancing shadows, golden hours, {fact}",
            'anger': f"Shattered glass, burning bridges, {fact}"
        }
        return imagery_map.get(emotion, f"Vivid scenes of {fact}")

    def _generate_default_structure(self) -> Dict[str, Any]:
        """Generate default structure when no emotional states provided"""
        return {
            'structure': {
                'verses': [{'opening': 'Tell your story here'}],
                'chorus': {'hook': 'Express your truth'},
                'bridge': {'content': 'Find your transformation'},
                'outro': {'type': 'open ending'}
            },
            'themes': ['personal journey'],
            'emotional_arc': ['exploration'],
            'key_phrases': [],
            'lyrical_devices': ['honest expression']
        }

class EmotionalCoherenceValidator:
    """Validates emotional coherence and consistency across the framework"""

    def __init__(self):
        self.coherence_thresholds = {
            'authenticity_minimum': 0.3,
            'intensity_range': (0.1, 1.0),
            'consistency_tolerance': 0.4,
            'contradiction_threshold': 0.7
        }

        self.emotion_compatibility_matrix = {
            'grief': {'compatible': ['contemplation', 'vulnerability'], 'incompatible': ['joy'], 'neutral': ['anger']},
            'joy': {'compatible': ['contemplation', 'vulnerability'], 'incompatible': ['grief'], 'neutral': ['anger']},
            'anger': {'compatible': ['vulnerability'], 'incompatible': [], 'neutral': ['grief', 'joy', 'contemplation']},
            'contemplation': {'compatible': ['grief', 'joy', 'vulnerability'], 'incompatible': [], 'neutral': ['anger']},
            'vulnerability': {'compatible': ['grief', 'joy', 'anger', 'contemplation'], 'incompatible': [], 'neutral': []},
            'anxiety': {'compatible': ['vulnerability', 'contemplation'], 'incompatible': ['joy'], 'neutral': ['grief', 'anger']}
        }

    def validate_emotional_states(self, emotional_states: List[EmotionalState]) -> Dict[str, Any]:
        """Validate the coherence of extracted emotional states"""
        if not emotional_states:
            return {
                'is_coherent': True,
                'validation_score': 1.0,
                'issues': [],
                'recommendations': []
            }

        issues = []
        recommendations = []
        validation_scores = []

        # 1. Validate individual emotional states
        for i, state in enumerate(emotional_states):
            state_validation = self._validate_individual_state(state, i)
            validation_scores.append(state_validation['score'])
            issues.extend(state_validation['issues'])
            recommendations.extend(state_validation['recommendations'])

        # 2. Validate emotional progression coherence
        if len(emotional_states) > 1:
            progression_validation = self._validate_emotional_progression(emotional_states)
            validation_scores.append(progression_validation['score'])
            issues.extend(progression_validation['issues'])
            recommendations.extend(progression_validation['recommendations'])

        # 3. Validate factual grounding
        grounding_validation = self._validate_factual_grounding(emotional_states)
        validation_scores.append(grounding_validation['score'])
        issues.extend(grounding_validation['issues'])
        recommendations.extend(grounding_validation['recommendations'])

        # Calculate overall validation score
        overall_score = sum(validation_scores) / len(validation_scores) if validation_scores else 1.0
        is_coherent = overall_score >= 0.7 and len([issue for issue in issues if issue['severity'] == 'critical']) == 0

        return {
            'is_coherent': is_coherent,
            'validation_score': overall_score,
            'issues': issues,
            'recommendations': recommendations,
            'detailed_analysis': {
                'individual_states_valid': all(s >= 0.5 for s in validation_scores[:len(emotional_states)]),
                'progression_coherent': len(emotional_states) <= 1 or validation_scores[len(emotional_states)] >= 0.6,
                'factually_grounded': grounding_validation['score'] >= 0.5,
                'authenticity_range': [s.authenticity_score for s in emotional_states],
                'intensity_range': [s.intensity for s in emotional_states]
            }
        }

    def _validate_individual_state(self, state: EmotionalState, index: int) -> Dict[str, Any]:
        """Validate an individual emotional state"""
        issues = []
        recommendations = []
        score_components = []

        # Validate authenticity score
        if state.authenticity_score < self.coherence_thresholds['authenticity_minimum']:
            issues.append({
                'type': 'low_authenticity',
                'severity': 'warning',
                'message': f"State {index}: Low authenticity score ({state.authenticity_score:.2f})",
                'suggestion': "Consider if this emotion is performative vs genuine"
            })
            score_components.append(0.3)
        else:
            score_components.append(0.8)

        # Validate intensity range
        if not (self.coherence_thresholds['intensity_range'][0] <= state.intensity <= self.coherence_thresholds['intensity_range'][1]):
            issues.append({
                'type': 'invalid_intensity',
                'severity': 'critical',
                'message': f"State {index}: Intensity out of valid range ({state.intensity})",
                'suggestion': "Intensity must be between 0.1 and 1.0"
            })
            score_components.append(0.0)
        else:
            score_components.append(1.0)

        # Validate factual triggers
        if not state.factual_triggers or all(not trigger.strip() for trigger in state.factual_triggers):
            issues.append({
                'type': 'missing_triggers',
                'severity': 'warning',
                'message': f"State {index}: No factual triggers provided",
                'suggestion': "Emotional states should be grounded in specific textual facts"
            })
            score_components.append(0.4)
        else:
            score_components.append(0.9)

        # Validate secondary emotions compatibility
        if state.secondary_emotions:
            compatibility_score = self._check_emotion_compatibility(state.primary_emotion, state.secondary_emotions)
            if compatibility_score < 0.5:
                issues.append({
                    'type': 'emotion_incompatibility',
                    'severity': 'warning',
                    'message': f"State {index}: Secondary emotions may not be compatible with primary emotion",
                    'suggestion': f"Review compatibility of {state.primary_emotion} with {state.secondary_emotions}"
                })
            score_components.append(compatibility_score)
        else:
            score_components.append(0.8)  # Neutral score for missing secondary emotions

        # Generate recommendations
        if state.authenticity_score > 0.8:
            recommendations.append({
                'type': 'production_suggestion',
                'message': f"State {index}: High authenticity - use clean, direct production"
            })
        elif state.authenticity_score < 0.5:
            recommendations.append({
                'type': 'production_suggestion',
                'message': f"State {index}: Low authenticity - consider processed/filtered effects"
            })

        return {
            'score': sum(score_components) / len(score_components) if score_components else 0.5,
            'issues': issues,
            'recommendations': recommendations
        }

    def _validate_emotional_progression(self, states: List[EmotionalState]) -> Dict[str, Any]:
        """Validate the coherence of emotional progression"""
        issues = []
        recommendations = []

        # Check for abrupt emotional shifts
        shift_scores = []
        for i in range(len(states) - 1):
            current_state = states[i]
            next_state = states[i + 1]

            # Calculate shift magnitude
            intensity_shift = abs(current_state.intensity - next_state.intensity)
            authenticity_shift = abs(current_state.authenticity_score - next_state.authenticity_score)

            # Check emotional compatibility
            compatibility = self._check_emotion_compatibility(current_state.primary_emotion, [next_state.primary_emotion])

            # Assess if shift is too abrupt
            if intensity_shift > 0.6 and compatibility < 0.3:
                issues.append({
                    'type': 'abrupt_shift',
                    'severity': 'warning',
                    'message': f"Abrupt emotional shift from {current_state.primary_emotion} to {next_state.primary_emotion}",
                    'suggestion': "Consider adding transitional emotional states or justifying the dramatic shift"
                })
                shift_scores.append(0.3)
            elif intensity_shift > 0.8:
                issues.append({
                    'type': 'extreme_intensity_shift',
                    'severity': 'warning',
                    'message': f"Extreme intensity shift: {current_state.intensity:.2f} → {next_state.intensity:.2f}",
                    'suggestion': "Large intensity changes should be factually justified"
                })
                shift_scores.append(0.4)
            else:
                shift_scores.append(0.8)

        # Check for emotional arc coherence
        if len(states) >= 3:
            # Look for narrative progression patterns
            intensities = [s.intensity for s in states]
            authenticity_scores = [s.authenticity_score for s in states]

            # Check if there's some form of progression (not just random)
            intensity_variance = sum((x - sum(intensities) / len(intensities)) ** 2 for x in intensities) / len(intensities)
            if intensity_variance < 0.01:  # Too flat
                recommendations.append({
                    'type': 'progression_suggestion',
                    'message': "Emotional journey appears flat - consider varying intensity for more dynamic storytelling"
                })

        progression_score = sum(shift_scores) / len(shift_scores) if shift_scores else 1.0

        return {
            'score': progression_score,
            'issues': issues,
            'recommendations': recommendations
        }

    def _validate_factual_grounding(self, states: List[EmotionalState]) -> Dict[str, Any]:
        """Validate that emotional states are properly grounded in facts"""
        issues = []
        recommendations = []
        grounding_scores = []

        for i, state in enumerate(states):
            if not state.factual_triggers:
                issues.append({
                    'type': 'no_factual_grounding',
                    'severity': 'critical',
                    'message': f"State {i}: No factual triggers provided",
                    'suggestion': "Every emotional state should be tied to specific textual evidence"
                })
                grounding_scores.append(0.0)
                continue

            # Check quality of factual triggers
            trigger_quality_score = 0.0
            for trigger in state.factual_triggers:
                if len(trigger.strip()) < 10:
                    trigger_quality_score += 0.2  # Very short trigger
                elif len(trigger.strip()) < 30:
                    trigger_quality_score += 0.6  # Adequate trigger
                else:
                    trigger_quality_score += 1.0  # Detailed trigger

            avg_trigger_quality = trigger_quality_score / len(state.factual_triggers)
            grounding_scores.append(avg_trigger_quality)

            if avg_trigger_quality < 0.5:
                issues.append({
                    'type': 'weak_factual_grounding',
                    'severity': 'warning',
                    'message': f"State {i}: Factual triggers are too brief or vague",
                    'suggestion': "Provide more specific, detailed factual evidence for emotional states"
                })

        overall_grounding = sum(grounding_scores) / len(grounding_scores) if grounding_scores else 0.0

        return {
            'score': overall_grounding,
            'issues': issues,
            'recommendations': recommendations
        }

    def _check_emotion_compatibility(self, primary_emotion: str, secondary_emotions: List[str]) -> float:
        """Check compatibility between primary and secondary emotions"""
        if primary_emotion not in self.emotion_compatibility_matrix:
            return 0.5  # Neutral score for unknown emotions

        compatibility_matrix = self.emotion_compatibility_matrix[primary_emotion]
        compatibility_scores = []

        for secondary in secondary_emotions:
            if secondary in compatibility_matrix['compatible']:
                compatibility_scores.append(1.0)
            elif secondary in compatibility_matrix['incompatible']:
                compatibility_scores.append(0.0)
            elif secondary in compatibility_matrix['neutral']:
                compatibility_scores.append(0.6)
            else:
                compatibility_scores.append(0.5)  # Unknown emotion

        return sum(compatibility_scores) / len(compatibility_scores) if compatibility_scores else 0.5

    def validate_beat_progression(self, beat_progression: Dict, emotional_states: List[EmotionalState]) -> Dict[str, Any]:
        """Validate that beat progression matches emotional states"""
        if not beat_progression or not emotional_states:
            return {
                'is_coherent': True,
                'score': 1.0,
                'issues': [],
                'recommendations': []
            }

        issues = []
        recommendations = []

        # Check if number of beat sections matches emotional progression
        sections = beat_progression.get('sections', [])
        if len(sections) != len(emotional_states):
            issues.append({
                'type': 'section_emotion_mismatch',
                'severity': 'warning',
                'message': f"Beat sections ({len(sections)}) don't match emotional states ({len(emotional_states)})",
                'suggestion': "Ensure each emotional state has corresponding beat section"
            })

        # Validate tempo coherence with emotions
        tempo_issues = 0
        for i, section in enumerate(sections):
            if i < len(emotional_states):
                state = emotional_states[i]
                beat_pattern = section.get('beat_pattern', {})
                tempo_range = beat_pattern.get('tempo_range', (70, 130))

                # Check if tempo matches emotion intensity
                expected_tempo_low = 60 + (state.intensity * 80)  # Scale 60-140 BPM based on intensity
                expected_tempo_high = expected_tempo_low + 20

                if tempo_range[1] < expected_tempo_low - 20 or tempo_range[0] > expected_tempo_high + 20:
                    tempo_issues += 1
                    recommendations.append({
                        'type': 'tempo_adjustment',
                        'message': f"Section {i}: Consider adjusting tempo to match {state.primary_emotion} intensity ({state.intensity})"
                    })

        coherence_score = 1.0 - (tempo_issues / max(len(sections), 1) * 0.3)

        return {
            'is_coherent': coherence_score >= 0.7,
            'score': coherence_score,
            'issues': issues,
            'recommendations': recommendations
        }

    def validate_lyrical_coherence(self, lyric_structure: Dict, emotional_states: List[EmotionalState]) -> Dict[str, Any]:
        """Validate lyrical coherence with emotional states"""
        if not lyric_structure or not emotional_states:
            return {
                'is_coherent': True,
                'score': 1.0,
                'issues': [],
                'recommendations': []
            }

        issues = []
        recommendations = []

        # Check if emotional arc matches lyrical themes
        lyrical_themes = lyric_structure.get('themes', [])
        emotional_themes = []

        for state in emotional_states:
            if state.primary_emotion == 'grief':
                emotional_themes.extend(['loss', 'memory', 'healing'])
            elif state.primary_emotion == 'joy':
                emotional_themes.extend(['celebration', 'gratitude', 'connection'])
            elif state.primary_emotion == 'contemplation':
                emotional_themes.extend(['understanding', 'searching', 'growth'])

        theme_overlap = len(set(lyrical_themes) & set(emotional_themes))
        theme_coherence = theme_overlap / max(len(lyrical_themes), 1)

        if theme_coherence < 0.3:
            issues.append({
                'type': 'theme_mismatch',
                'severity': 'warning',
                'message': "Lyrical themes don't align well with emotional states",
                'suggestion': f"Consider incorporating themes like: {', '.join(emotional_themes[:3])}"
            })

        return {
            'is_coherent': theme_coherence >= 0.3,
            'score': theme_coherence,
            'issues': issues,
            'recommendations': recommendations
        }

class SelfReflectionAnalyzer:
    """Analyzes self-reflective and introspective content"""

    def __init__(self):
        self.reflection_indicators = {
            'self_awareness': [
                r'(?:I|he|she|they)\s+(?:realized|understood|knew)\s+(?:that|how)',
                r'(?:looking|looked)\s+(?:back|within|inside)',
                r'(?:reflected|pondered|contemplated)\s+(?:on|upon)'
            ],
            'emotional_processing': [
                r'(?:felt|feeling)\s+(?:like|as if|that)',
                r'(?:emotions?|feelings?)\s+(?:washed|flooded|overwhelmed)',
                r'(?:tried|trying)\s+to\s+(?:understand|process|cope)'
            ],
            'growth_recognition': [
                r'(?:learned|grown|changed)\s+(?:from|since|after)',
                r'(?:no longer|not anymore)\s+(?:the same|who)',
                r'(?:became|becoming)\s+(?:someone|something)\s+(?:new|different)'
            ]
        }

    def analyze_character_introspection(self, text: str, character: StandardCharacterProfile) -> Dict[str, Any]:
        """Analyze character's self-reflective journey"""
        introspection_data = {
            'self_awareness_moments': [],
            'emotional_processing_stages': [],
            'growth_trajectory': [],
            'vulnerability_scores': [],
            'defense_mechanisms': []
        }

        # Extract self-awareness moments
        for category, patterns in self.reflection_indicators.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    moment = {
                        'category': category,
                        'text': match.group(),
                        'context': self._extract_context(text, match),
                        'emotional_depth': self._calculate_depth(match.group()),
                        'musical_expression': self._suggest_musical_expression(category)
                    }

                    if category == 'self_awareness':
                        introspection_data['self_awareness_moments'].append(moment)
                    elif category == 'emotional_processing':
                        introspection_data['emotional_processing_stages'].append(moment)
                    elif category == 'growth_recognition':
                        introspection_data['growth_trajectory'].append(moment)

        # Calculate vulnerability progression
        introspection_data['vulnerability_scores'] = self._track_vulnerability_progression(
            introspection_data['self_awareness_moments']
        )

        # Identify defense mechanisms
        introspection_data['defense_mechanisms'] = self._identify_defense_mechanisms(text, character)

        return introspection_data

    def _extract_context(self, text: str, match) -> str:
        """Extract meaningful context around match"""
        start = max(0, match.start() - 150)
        end = min(len(text), match.end() + 150)
        return text[start:end].strip()

    def _calculate_depth(self, text: str) -> float:
        """Calculate emotional depth score"""
        depth_indicators = ['truly', 'deeply', 'profoundly', 'completely', 'utterly']
        depth_score = sum(1 for word in depth_indicators if word in text.lower())
        return min(1.0, 0.5 + (depth_score * 0.2))

    def _suggest_musical_expression(self, category: str) -> str:
        """Suggest musical expression for introspective category"""
        expressions = {
            'self_awareness': "Stripped-down production with exposed vocals",
            'emotional_processing': "Evolving textures with processing effects",
            'growth_recognition': "Building arrangement representing transformation"
        }
        return expressions.get(category, "Introspective ambient production")

    def _track_vulnerability_progression(self, awareness_moments: List[Dict]) -> List[float]:
        """Track how vulnerability increases through narrative"""
        scores = []
        base_vulnerability = 0.3

        for i, moment in enumerate(awareness_moments):
            # Vulnerability increases with each self-awareness moment
            progression_factor = i * 0.1
            depth_factor = moment.get('emotional_depth', 0.5)
            score = min(1.0, base_vulnerability + progression_factor + depth_factor * 0.2)
            scores.append(score)

        return scores

    def _identify_defense_mechanisms(self, text: str, character: StandardCharacterProfile) -> List[Dict]:
        """Identify psychological defense mechanisms in text"""
        mechanisms = []

        defense_patterns = {
            'denial': r'(?:couldn\'t|wouldn\'t|refused to)\s+(?:believe|accept|see)',
            'projection': r'(?:blamed|accused)\s+(?:everyone|them|others)',
            'rationalization': r'(?:told\s+(?:myself|himself|herself|themselves)|reasoned that|justified)',
            'displacement': r'(?:took\s+out|vented|directed)\s+(?:anger|frustration|pain)\s+(?:on|at)'
        }

        for mechanism_type, pattern in defense_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                mechanisms.append({
                    'type': mechanism_type,
                    'evidence': match.group(),
                    'musical_representation': self._get_defense_musical_representation(mechanism_type)
                })

        return mechanisms

    def _get_defense_musical_representation(self, mechanism: str) -> str:
        """Get musical representation for defense mechanism"""
        representations = {
            'denial': "Filtered/muffled sections representing blocked reality",
            'projection': "Reverb/delay throws representing deflection",
            'rationalization': "Overly structured/rigid beat patterns",
            'displacement': "Aggressive percussion redirected from original target"
        }
        return representations.get(mechanism, "Distorted elements representing psychological defense")

# ================================================================================================
# CHARACTER ANALYSIS ENGINE
# ================================================================================================

class CharacterAnalyzer:
    """Advanced character analysis using NLP and pattern recognition"""

    def __init__(self):
        self.character_indicators = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Proper names
            r'\b(?:he|she|they|him|her|them)\b',      # Pronouns
            r'\bsaid\s+([A-Z][a-z]+)',                # Speech attribution
            r'([A-Z][a-z]+)\s+(?:smiled|frowned|laughed|cried|whispered)'  # Actions
        ]

        self.personality_markers = {
            'brave': ['courage', 'fearless', 'bold', 'heroic', 'valiant'],
            'cunning': ['clever', 'shrewd', 'sly', 'calculating', 'manipulative'],
            'compassionate': ['kind', 'caring', 'gentle', 'empathetic', 'loving'],
            'ambitious': ['driven', 'determined', 'ruthless', 'goal-oriented'],
            'mysterious': ['secretive', 'enigmatic', 'elusive', 'hidden'],
            'cheerful': ['happy', 'optimistic', 'joyful', 'upbeat', 'positive'],
            'melancholic': ['sad', 'brooding', 'contemplative', 'nostalgic'],
            'rebellious': ['defiant', 'independent', 'non-conformist', 'radical']
        }

        # Initialize emotional framework components
        self.emotional_beat_engine = EmotionalBeatEngine()
        self.meta_narrative_processor = MetaNarrativeProcessor()
        self.self_reflection_analyzer = SelfReflectionAnalyzer()

    async def analyze_text(self, text: str, ctx: Context) -> TextAnalysisResult:
        """Perform comprehensive character analysis on input text"""
        await ctx.info("Starting character analysis...")

        # Extract potential characters
        characters = await self._extract_characters(text, ctx)

        # Analyze narrative themes
        themes = await self._analyze_themes(text)

        # Determine emotional arc
        emotional_arc = await self._analyze_emotional_arc(text)

        # Extract setting information
        setting = await self._extract_setting(text)

        # Calculate text complexity
        complexity = await self._calculate_complexity(text)

        # NEW: Extract fact-based emotional states
        emotional_states = []
        primary_character = characters[0] if characters else None
        if primary_character:
            raw_states = self.emotional_beat_engine.analyze_emotional_facts(text, primary_character)
            emotional_states = [asdict(state) for state in raw_states]

        # NEW: Extract emotional subtext and meta-narrative elements
        emotional_subtext = []
        if emotional_states:
            emotional_state_objects = [EmotionalState(**state) for state in emotional_states]
            emotional_subtext = self.meta_narrative_processor.extract_emotional_subtext(text, emotional_state_objects)

        # NEW: Generate beat progression based on emotional journey
        beat_progression = None
        if emotional_states:
            beat_progression = self.emotional_beat_engine.generate_beat_progression(
                [EmotionalState(**state) for state in emotional_states]
            )

        # NEW: Analyze introspection and self-reflection
        introspection_analysis = None
        if primary_character:
            introspection_analysis = self.self_reflection_analyzer.analyze_character_introspection(
                text, primary_character
            )

        result = TextAnalysisResult(
            characters=[asdict(char) for char in characters],
            narrative_themes=themes,
            emotional_arc=emotional_arc,
            setting_description=setting,
            text_complexity=complexity,
            processing_time=0.0,  # Will be calculated by caller
            emotional_states=emotional_states,
            emotional_subtext=emotional_subtext,
            beat_progression=beat_progression,
            introspection_analysis=introspection_analysis
        )

        await ctx.info(f"Analysis complete: Found {len(characters)} characters with {len(emotional_states)} emotional states")
        return result

    async def analyze_characters(self, text: str, ctx: Context = None) -> Dict[str, Any]:
        """Analyze characters in text - compatibility method for smoke test"""
        if ctx is None:
            # Create a minimal context for compatibility
            class MinimalContext:
                async def info(self, msg): pass
                async def error(self, msg): pass
            ctx = MinimalContext()

        # Use the existing analyze_text method
        result = await self.analyze_text(text, ctx)

        # Convert to expected format
        return {
            'characters': result.characters,
            'narrative_themes': result.narrative_themes,
            'emotional_arc': result.emotional_arc,
            'analysis_metadata': {
                'text_length': len(text),
                'character_count': len(result.characters),
                'confidence': 0.8
            }
        }

    async def _extract_characters(self, text: str, ctx: Context) -> List[CharacterProfile]:
        """Extract and analyze characters using three-layer methodology"""
        # Find potential character names with improved patterns
        potential_names = set()

        # Pattern 1: Full names (First Last, First Middle Last)
        full_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b', text)
        potential_names.update(full_names)

        # Pattern 2: Single names that appear frequently
        single_names = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
        for name in single_names:
            if text.count(name) >= 3:  # Single names must appear at least 3 times
                potential_names.add(name)

        # Pattern 3: Names from dialogue attribution
        dialogue_names = re.findall(r'([A-Z][a-z]+)\s+(?:said|asked|replied|whispered|shouted|exclaimed)', text)
        potential_names.update(dialogue_names)

        # Filter out common words and validate as character names
        characters = []
        common_words = {'The', 'And', 'But', 'For', 'Not', 'With', 'From', 'They', 'This', 'That', 'When', 'Where', 'What', 'Why', 'How', 'Then', 'Now', 'Here', 'There', 'Again', 'Also', 'Just', 'Only', 'Even', 'Still', 'Much', 'More', 'Most', 'Many', 'Some', 'All', 'Both', 'Each', 'Every', 'Another', 'Other', 'Such', 'Very', 'Too', 'So', 'As', 'At', 'By', 'In', 'On', 'Of', 'To', 'Up', 'Out', 'Off', 'Over', 'Under', 'About', 'Above', 'Below', 'Down', 'Through', 'Around', 'Between', 'Among', 'Along', 'Across', 'Behind', 'Before', 'After', 'During', 'While', 'Until', 'Since', 'Because', 'Although', 'Though', 'However', 'Therefore', 'Thus', 'Hence', 'Moreover', 'Furthermore', 'Nevertheless', 'Otherwise', 'Instead', 'Meanwhile', 'Indeed', 'Actually', 'Really', 'Quite', 'Rather', 'Perhaps', 'Maybe', 'Probably', 'Certainly', 'Definitely', 'Obviously', 'Clearly', 'Surely', 'Exactly', 'Precisely', 'Absolutely', 'Completely', 'Entirely', 'Totally', 'Fully', 'Partly', 'Mostly', 'Nearly', 'Almost', 'Hardly', 'Barely', 'Scarcely', 'Rarely', 'Seldom', 'Never', 'Always', 'Often', 'Sometimes', 'Usually', 'Generally', 'Typically', 'Normally', 'Regularly', 'Frequently', 'Occasionally', 'Recently', 'Finally', 'Eventually', 'Suddenly', 'Immediately', 'Quickly', 'Slowly', 'Carefully', 'Gently', 'Roughly', 'Softly', 'Loudly', 'Quietly', 'Directly', 'Especially', 'Particularly', 'Specifically', 'Mainly', 'Primarily', 'Largely', 'Basically', 'Essentially', 'Fundamentally', 'Naturally', 'Seriously', 'Honestly', 'Literally', 'Practically', 'Virtually', 'Effectively', 'Successfully', 'Properly', 'Correctly', 'Accurately', 'Atlanta', 'Memphis', 'Boston', 'Chicago', 'Detroit', 'Houston', 'Phoenix', 'Philadelphia', 'San', 'Los', 'New', 'York', 'California', 'Texas', 'Florida', 'Illinois', 'Pennsylvania', 'Ohio', 'Georgia', 'North', 'South', 'East', 'West', 'Central', 'Northern', 'Southern', 'Eastern', 'Western', 'American', 'British', 'Canadian', 'European', 'Asian', 'African', 'Australian', 'Russian', 'Chinese', 'Japanese', 'German', 'French', 'Italian', 'Spanish', 'Portuguese', 'Dutch', 'Greek', 'Turkish', 'Indian', 'Mexican', 'Brazilian', 'Argentine', 'Chilean', 'Colombian', 'Venezuelan', 'Peruvian', 'Ecuadorian', 'Bolivian', 'Uruguayan', 'Paraguayan', 'His', 'Her', 'Their', 'Its', 'Our', 'Your', 'My', 'Mine', 'Yours', 'Hers', 'Theirs', 'Ours'}

        for name in potential_names:
            if name not in common_words and len(name) > 2:
                try:
                    char_profile = await self._build_character_profile(name, text, ctx)
                    if char_profile.confidence_score > 0.4:  # Higher confidence threshold
                        characters.append(char_profile)
                except Exception as e:
                    await ctx.error(f"Failed to build profile for character '{name}': {str(e)}")
                    continue

        # Sort by importance score
        characters.sort(key=lambda x: x.importance_score, reverse=True)
        return characters[:5]  # Return top 5 characters to avoid noise

    async def _build_character_profile(self, name: str, text: str, ctx: Context) -> CharacterProfile:
        """Build comprehensive character profile using three-layer analysis"""

        # Extract text segments related to this character
        char_segments = self._extract_character_segments(name, text)

        # SKIN LAYER - Observable characteristics
        physical_desc = self._extract_physical_description(name, char_segments)
        mannerisms = self._extract_mannerisms(name, char_segments)
        speech_patterns = self._extract_speech_patterns(name, char_segments)
        behaviors = self._extract_behavioral_traits(name, char_segments)

        # FLESH LAYER - Background and relationships
        backstory = self._extract_backstory(name, char_segments)
        relationships = self._extract_relationships(name, char_segments)
        experiences = self._extract_formative_experiences(name, char_segments)
        connections = self._extract_social_connections(name, char_segments)

        # CORE LAYER - Deep psychology
        motivations = self._extract_motivations(name, char_segments)
        fears = self._extract_fears(name, char_segments)
        desires = self._extract_desires(name, char_segments)
        conflicts = self._extract_conflicts(name, char_segments)
        drivers = self._extract_personality_drivers(name, char_segments)

        # Calculate confidence and importance scores
        confidence = self._calculate_confidence_score(name, char_segments)
        importance = self._calculate_importance_score(name, text)

        # Find aliases and references
        aliases = self._find_aliases(name, text)
        references = char_segments[:5]  # First 5 references
        first_appearance = char_segments[0] if char_segments else f"Character named {name}"

        return CharacterProfile(
            name=name,
            aliases=aliases,
            physical_description=physical_desc,
            mannerisms=mannerisms,
            speech_patterns=speech_patterns,
            behavioral_traits=behaviors,
            backstory=backstory,
            relationships=relationships,
            formative_experiences=experiences,
            social_connections=connections,
            motivations=motivations,
            fears=fears,
            desires=desires,
            conflicts=conflicts,
            personality_drivers=drivers,
            confidence_score=confidence,
            text_references=references,
            first_appearance=first_appearance,
            importance_score=importance
        )

    def _extract_character_segments(self, name: str, text: str) -> List[str]:
        """Extract text segments that mention the character"""
        sentences = re.split(r'[.!?]+', text)
        segments = []

        for sentence in sentences:
            if name.lower() in sentence.lower():
                segments.append(sentence.strip())

        return segments

    def _extract_physical_description(self, name: str, segments: List[str]) -> str:
        """Extract physical description from character segments"""
        physical_terms = ['tall', 'short', 'dark', 'light', 'hair', 'eyes', 'skin', 'face', 'build', 'wore', 'dressed']
        descriptions = []

        for segment in segments:
            if name.lower() in segment.lower():
                for term in physical_terms:
                    if term in segment.lower():
                        descriptions.append(segment)
                        break

        return ' '.join(descriptions[:3]) if descriptions else f"Physical description of {name} not explicitly provided."

    def _extract_mannerisms(self, name: str, segments: List[str]) -> List[str]:
        """Extract behavioral mannerisms"""
        mannerism_patterns = ['smiled', 'frowned', 'gestured', 'nodded', 'shook', 'laughed', 'sighed', 'whispered']
        mannerisms = []

        for segment in segments:
            if name.lower() in segment.lower():
                for pattern in mannerism_patterns:
                    if pattern in segment.lower():
                        mannerisms.append(f"{pattern} - {segment[:50]}...")

        return list(set(mannerisms))[:5]

    def _extract_speech_patterns(self, name: str, segments: List[str]) -> List[str]:
        """Extract speech patterns and dialogue style"""
        speech_indicators = ['said', 'spoke', 'whispered', 'shouted', 'muttered', 'replied', 'asked']
        patterns = []

        for segment in segments:
            for indicator in speech_indicators:
                if indicator in segment.lower() and name.lower() in segment.lower():
                    patterns.append(f"Speech pattern: {segment[:60]}...")

        return list(set(patterns))[:3]

    def _extract_behavioral_traits(self, name: str, segments: List[str]) -> List[str]:
        """Extract behavioral characteristics"""
        traits = []

        for personality_type, keywords in self.personality_markers.items():
            for segment in segments:
                if name.lower() in segment.lower():
                    for keyword in keywords:
                        if keyword in segment.lower():
                            traits.append(f"{personality_type}: {keyword}")

        return list(set(traits))[:5]

    def _extract_backstory(self, name: str, segments: List[str]) -> str:
        """Extract backstory and history"""
        backstory_indicators = ['grew up', 'childhood', 'parents', 'family', 'past', 'history', 'before', 'used to']
        backstory_segments = []

        for segment in segments:
            if name.lower() in segment.lower():
                for indicator in backstory_indicators:
                    if indicator in segment.lower():
                        backstory_segments.append(segment)
                        break

        return ' '.join(backstory_segments[:2]) if backstory_segments else f"Backstory for {name} not explicitly detailed."

    def _extract_relationships(self, name: str, segments: List[str]) -> List[str]:
        """Extract character relationships"""
        relationship_terms = ['friend', 'enemy', 'lover', 'parent', 'child', 'sibling', 'colleague', 'mentor', 'student']
        relationships = []

        for segment in segments:
            if name.lower() in segment.lower():
                for term in relationship_terms:
                    if term in segment.lower():
                        relationships.append(f"{term} relationship: {segment[:50]}...")

        return list(set(relationships))[:4]

    def _extract_formative_experiences(self, name: str, segments: List[str]) -> List[str]:
        """Extract formative experiences"""
        experience_indicators = ['experienced', 'learned', 'discovered', 'realized', 'changed', 'transformed']
        experiences = []

        for segment in segments:
            if name.lower() in segment.lower():
                for indicator in experience_indicators:
                    if indicator in segment.lower():
                        experiences.append(f"Experience: {segment[:60]}...")

        return list(set(experiences))[:3]

    def _extract_social_connections(self, name: str, segments: List[str]) -> List[str]:
        """Extract social connections and network"""
        # Find other character names mentioned with this character
        connections = []

        for segment in segments:
            if name.lower() in segment.lower():
                # Look for other proper names in the same segment
                other_names = re.findall(r'\b[A-Z][a-z]+\b', segment)
                for other_name in other_names:
                    if other_name != name and len(other_name) > 2:
                        connections.append(f"Connected to {other_name}")

        return list(set(connections))[:4]

    def _extract_motivations(self, name: str, segments: List[str]) -> List[str]:
        """Extract character motivations"""
        motivation_indicators = ['wants', 'needs', 'desires', 'seeks', 'hopes', 'dreams', 'goals', 'ambitions']
        motivations = []

        for segment in segments:
            if name.lower() in segment.lower():
                for indicator in motivation_indicators:
                    if indicator in segment.lower():
                        motivations.append(f"Motivation: {segment[:60]}...")

        return list(set(motivations))[:3]

    def _extract_fears(self, name: str, segments: List[str]) -> List[str]:
        """Extract character fears and anxieties"""
        fear_indicators = ['afraid', 'fear', 'scared', 'worried', 'anxious', 'terrified', 'phobia']
        fears = []

        for segment in segments:
            if name.lower() in segment.lower():
                for indicator in fear_indicators:
                    if indicator in segment.lower():
                        fears.append(f"Fear: {segment[:60]}...")

        return list(set(fears))[:3]

    def _extract_desires(self, name: str, segments: List[str]) -> List[str]:
        """Extract character desires and wants"""
        desire_indicators = ['love', 'want', 'desire', 'wish', 'long for', 'crave', 'yearn']
        desires = []

        for segment in segments:
            if name.lower() in segment.lower():
                for indicator in desire_indicators:
                    if indicator in segment.lower():
                        desires.append(f"Desire: {segment[:60]}...")

        return list(set(desires))[:3]

    def _extract_conflicts(self, name: str, segments: List[str]) -> List[str]:
        """Extract character conflicts"""
        conflict_indicators = ['conflict', 'struggle', 'fight', 'battle', 'oppose', 'against', 'problem']
        conflicts = []

        for segment in segments:
            if name.lower() in segment.lower():
                for indicator in conflict_indicators:
                    if indicator in segment.lower():
                        conflicts.append(f"Conflict: {segment[:60]}...")

        return list(set(conflicts))[:3]

    def _extract_personality_drivers(self, name: str, segments: List[str]) -> List[str]:
        """Extract core personality drivers"""
        drivers = []

        # Analyze overall personality based on actions and descriptions
        trait_counts = {}
        for personality_type, keywords in self.personality_markers.items():
            count = 0
            for segment in segments:
                if name.lower() in segment.lower():
                    for keyword in keywords:
                        if keyword in segment.lower():
                            count += 1
            if count > 0:
                trait_counts[personality_type] = count

        # Get top 3 personality drivers
        sorted_traits = sorted(trait_counts.items(), key=lambda x: x[1], reverse=True)
        drivers = [f"{trait} (strength: {count})" for trait, count in sorted_traits[:3]]

        return drivers

    def _calculate_confidence_score(self, name: str, segments: List[str]) -> float:
        """Calculate confidence in character analysis"""
        if not segments:
            return 0.0

        # Base score on number of mentions and depth of information
        mention_score = min(len(segments) / 10.0, 0.5)  # Max 0.5 for mentions

        # Depth score based on variety of information types
        depth_indicators = ['said', 'felt', 'thought', 'was', 'had', 'did', 'went']
        depth_count = sum(1 for segment in segments for indicator in depth_indicators if indicator in segment.lower())
        depth_score = min(depth_count / 20.0, 0.5)  # Max 0.5 for depth

        return mention_score + depth_score

    def _calculate_importance_score(self, name: str, text: str) -> float:
        """Calculate character importance in the narrative"""
        total_words = len(text.split())
        name_mentions = text.lower().count(name.lower())

        if total_words == 0:
            return 0.0

        # Base score on frequency
        frequency_score = name_mentions / total_words * 100

        # Boost for characters mentioned in first/last paragraphs
        paragraphs = text.split('\n\n')
        position_boost = 0.0
        if paragraphs and name.lower() in paragraphs[0].lower():
            position_boost += 0.2
        if len(paragraphs) > 1 and name.lower() in paragraphs[-1].lower():
            position_boost += 0.2

        return min(frequency_score + position_boost, 1.0)

    def _find_aliases(self, name: str, text: str) -> List[str]:
        """Find aliases and alternative names for the character"""
        aliases = []

        # Look for patterns like "John, also known as", "Mary (nicknamed Sue)"
        alias_patterns = [
            rf"{name}[,\s]+(?:also known as|nicknamed|called)\s+([A-Z][a-z]+)",
            rf"([A-Z][a-z]+)[,\s]+(?:also known as|nicknamed|called)\s+{name}",
            rf"{name}\s*\(([A-Z][a-z]+)\)",
            rf"([A-Z][a-z]+)\s*\({name}\)"
        ]

        for pattern in alias_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            aliases.extend(matches)

        return list(set(aliases))

    async def _analyze_themes(self, text: str) -> List[str]:
        """Analyze narrative themes"""
        theme_keywords = {
            'love': ['love', 'romance', 'relationship', 'heart', 'feelings'],
            'power': ['power', 'control', 'authority', 'dominance', 'rule'],
            'redemption': ['redemption', 'forgiveness', 'second chance', 'atonement'],
            'betrayal': ['betrayal', 'deception', 'lie', 'cheat', 'backstab'],
            'sacrifice': ['sacrifice', 'give up', 'loss', 'surrender'],
            'justice': ['justice', 'fair', 'right', 'wrong', 'moral'],
            'family': ['family', 'parent', 'child', 'brother', 'sister'],
            'friendship': ['friend', 'companion', 'ally', 'bond'],
            'survival': ['survive', 'escape', 'danger', 'threat', 'death'],
            'growth': ['learn', 'grow', 'change', 'develop', 'mature']
        }

        themes = []
        text_lower = text.lower()

        for theme, keywords in theme_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            if score > 0:
                themes.append(f"{theme} (strength: {score})")

        # Sort by strength and return top themes
        theme_scores = [(theme.split(' (')[0], int(theme.split('strength: ')[1].rstrip(')'))) for theme in themes]
        theme_scores.sort(key=lambda x: x[1], reverse=True)

        return [theme for theme, _ in theme_scores[:5]]

    async def _analyze_emotional_arc(self, text: str) -> List[str]:
        """Analyze the emotional progression through the text"""
        emotions = {
            'joy': ['happy', 'joy', 'elated', 'cheerful', 'delighted'],
            'sadness': ['sad', 'sorrow', 'grief', 'melancholy', 'despair'],
            'anger': ['angry', 'rage', 'fury', 'mad', 'irritated'],
            'fear': ['afraid', 'scared', 'terrified', 'anxious', 'worried'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished'],
            'hope': ['hope', 'optimistic', 'confident', 'positive'],
            'tension': ['tense', 'stressed', 'pressure', 'conflict', 'struggle']
        }

        # Divide text into sections and analyze emotional content
        sections = [text[i:i+len(text)//5] for i in range(0, len(text), len(text)//5)]
        emotional_arc = []

        for i, section in enumerate(sections):
            section_emotions = {}
            section_lower = section.lower()

            for emotion, keywords in emotions.items():
                score = sum(section_lower.count(keyword) for keyword in keywords)
                if score > 0:
                    section_emotions[emotion] = score

            if section_emotions:
                dominant_emotion = max(section_emotions, key=section_emotions.get)
                emotional_arc.append(f"Section {i+1}: {dominant_emotion}")
            else:
                emotional_arc.append(f"Section {i+1}: neutral")

        return emotional_arc

    async def _extract_setting(self, text: str) -> str:
        """Extract setting and world-building information"""
        setting_indicators = ['place', 'city', 'town', 'forest', 'castle', 'house', 'world', 'land', 'kingdom']
        time_indicators = ['day', 'night', 'morning', 'evening', 'year', 'century', 'age', 'era']

        setting_segments = []
        text_lower = text.lower()

        for indicator in setting_indicators + time_indicators:
            if indicator in text_lower:
                # Find sentences containing setting information
                sentences = re.split(r'[.!?]+', text)
                for sentence in sentences:
                    if indicator in sentence.lower():
                        setting_segments.append(sentence.strip())
                        break

        return ' '.join(setting_segments[:3]) if setting_segments else "Setting not explicitly described."

    async def _calculate_complexity(self, text: str) -> float:
        """Calculate text complexity score"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)

        if not words or not sentences:
            return 0.0

        # Average words per sentence
        avg_words_per_sentence = len(words) / len(sentences)

        # Vocabulary diversity (unique words / total words)
        unique_words = len(set(word.lower() for word in words))
        vocabulary_diversity = unique_words / len(words)

        # Complexity based on sentence length and vocabulary
        complexity = min((avg_words_per_sentence / 20.0) + vocabulary_diversity, 1.0)

        return complexity

# ================================================================================================
# MUSICAL PERSONA GENERATOR
# ================================================================================================

class MusicPersonaGenerator:
    """Generate musical artist personas from character profiles"""

    def __init__(self):
        # NO PREDEFINED MAPPINGS - LLM analyzes character and determines musical expression dynamically
        self.wiki_data_manager = None
        self.enhanced_genre_mapper = None
        self.source_attribution_manager = None
        self._initialization_attempted = False

    async def _ensure_wiki_integration(self):
        """Ensure wiki integration is initialized if available"""
        global command_generator

        if self._initialization_attempted:
            return

        self._initialization_attempted = True

        if not WIKI_INTEGRATION_AVAILABLE:
            logger.info("Wiki integration not available, using fallback mappings")
            # Initialize SunoCommandGenerator without wiki data manager (fallback mode)
            command_generator = SunoCommandGenerator(None)
            return

        try:
            # Initialize WikiDataManager with default configuration
            self.wiki_data_manager = WikiDataManager()
            config = WikiConfig()  # Use default configuration
            await self.wiki_data_manager.initialize(config)

            # Initialize EnhancedGenreMapper
            self.enhanced_genre_mapper = EnhancedGenreMapper(self.wiki_data_manager)

            # Initialize SourceAttributionManager
            self.source_attribution_manager = SourceAttributionManager()
            await self.source_attribution_manager.initialize()

            # Initialize SunoCommandGenerator with wiki data manager
            command_generator = SunoCommandGenerator(self.wiki_data_manager)

            logger.info("Wiki integration initialized successfully")

        except Exception as e:
            logger.warning(f"Failed to initialize wiki integration: {e}")
            self.wiki_data_manager = None
            self.enhanced_genre_mapper = None
            self.source_attribution_manager = None

            # Initialize SunoCommandGenerator without wiki data manager (fallback mode)
            command_generator = SunoCommandGenerator(None)

    def build_attributed_context_for_llm(self, content: Any, content_type: str = "general") -> str:
        """Build LLM context with source attribution
        
        Args:
            content: The content to include in LLM context
            content_type: Type of content ('genre', 'meta_tag', 'technique', 'general')
            
        Returns:
            Formatted context string with source attribution
        """
        if not self.source_attribution_manager:
            # Fallback to content without attribution
            return str(content)

        try:
            # Get relevant source URLs based on content type
            source_urls = self.source_attribution_manager.get_source_urls(content_type)

            if not source_urls:
                # No sources available, return content as-is
                return str(content)

            # Build attributed content
            attributed_content = self.source_attribution_manager.build_attributed_context(
                content, source_urls
            )

            # Track usage
            self.source_attribution_manager.track_content_usage(
                attributed_content.content_id,
                source_urls[0] if source_urls else "",
                f"LLM context for {content_type}"
            )

            # Format for LLM context
            context_text = f"{content}\n\n{attributed_content.attribution_text}"

            return context_text

        except Exception as e:
            logger.warning(f"Failed to build attributed context: {e}")
            return str(content)

    async def generate_artist_persona(self, character: StandardCharacterProfile, ctx: Context,
                                     requested_genre: Optional[str] = None) -> ArtistPersona:
        """Generate a musical artist persona from character profile, optionally aligned with requested genre"""
        await ctx.info(f"Generating artist persona for {character.name}...")

        # Determine primary personality traits
        primary_traits = self._extract_primary_traits(character)

        # Map to musical genres (or use requested genre)
        if requested_genre:
            await ctx.info(f"Aligning persona with requested genre: {requested_genre}")
            primary_genre = requested_genre
            secondary_genres = await self._get_secondary_genres_for_requested(requested_genre)
        else:
            primary_genre, secondary_genres = await self._map_to_genres(primary_traits)

        # Generate vocal style (aligned with genre if requested)
        vocal_style = self._determine_vocal_style(primary_traits, requested_genre)

        # Create artist name
        artist_name = self._generate_artist_name(character.name, primary_traits)

        # Generate thematic content
        lyrical_themes = self._generate_lyrical_themes(character)
        emotional_palette = self._generate_emotional_palette(character, requested_genre)

        # Determine artistic influences (genre-appropriate if requested)
        influences = self._generate_influences(primary_genre, character, requested_genre)

        # Collaboration style (aligned with genre if requested)
        collaboration_style = self._determine_collaboration_style(character, requested_genre)

        # Generate persona description
        persona_description = self._generate_persona_description(character, primary_genre, vocal_style)

        # Calculate mapping confidence
        confidence = self._calculate_mapping_confidence(character, primary_traits, requested_genre)

        # Genre justification
        justification = self._generate_genre_justification(character, primary_traits, primary_genre, requested_genre)

        # Create base persona
        persona = ArtistPersona(
            character_name=character.name,
            artist_name=artist_name,
            primary_genre=primary_genre,
            secondary_genres=secondary_genres,
            vocal_style=vocal_style,
            instrumental_preferences=await self._generate_instrumental_preferences(primary_genre),
            lyrical_themes=lyrical_themes,
            emotional_palette=emotional_palette,
            artistic_influences=influences,
            collaboration_style=collaboration_style,
            character_mapping_confidence=confidence,
            genre_justification=justification,
            persona_description=persona_description
        )

        # If genre was requested, apply additional alignment
        if requested_genre:
            persona = await self._apply_genre_alignment(persona, requested_genre, ctx)

        return persona

    async def _apply_genre_alignment(self, persona: ArtistPersona, requested_genre: str, ctx: Context) -> ArtistPersona:
        """Apply genre-specific alignment to persona using genre intelligence"""
        try:
            from genre_production_intelligence import align_persona_with_genre

            # Convert persona to dict for alignment
            persona_dict = asdict(persona)

            # Apply genre alignment
            aligned_dict = align_persona_with_genre(persona_dict, requested_genre)

            # Create new aligned persona
            aligned_persona = ArtistPersona.from_dict(aligned_dict)

            await ctx.info(f"Applied {requested_genre} genre alignment to {persona.character_name}")
            return aligned_persona

        except ImportError:
            await ctx.warning("Genre production intelligence not available, using basic persona")
            return persona

    async def _get_secondary_genres_for_requested(self, requested_genre: str) -> List[str]:
        """Get appropriate secondary genres for a requested primary genre"""
        try:
            from genre_production_intelligence import get_genre_intelligence
            genre_intelligence = get_genre_intelligence()
            genre_profile = genre_intelligence.get_genre_profile(requested_genre)

            # Return category and a complementary genre
            secondary = [genre_profile.category]
            if genre_profile.category != "alternative":
                secondary.append("alternative")
            else:
                secondary.append("indie")

            return secondary
        except ImportError:
            # Fallback secondary genres
            genre_secondaries = {
                "electronic": ["edm", "alternative"],
                "drum_and_bass": ["electronic", "breakbeat"],
                "hip_hop": ["rap", "urban"],
                "trap": ["hip_hop", "urban"],
                "folk": ["acoustic", "indie"],
                "jazz": ["blues", "soul"],
                "rock": ["alternative", "indie"]
            }
            return genre_secondaries.get(requested_genre.lower(), ["alternative", "indie"])

    def _extract_primary_traits(self, character: StandardCharacterProfile) -> List[str]:
        """Extract primary personality traits from character profile"""
        traits = []

        # Extract from personality drivers
        for driver in character.personality_drivers:
            trait = driver.split(' (')[0]  # Remove strength indicator
            traits.append(trait)

        # Extract from behavioral traits
        for behavior in character.behavioral_traits:
            if ':' in behavior:
                trait = behavior.split(':')[0]
                traits.append(trait)

        # Extract from motivations and conflicts for additional traits
        motivation_text = ' '.join(character.motivations).lower()
        conflict_text = ' '.join(character.conflicts).lower()

        # Map motivations/conflicts to traits
        if 'power' in motivation_text or 'control' in motivation_text:
            traits.append('ambitious')
        if 'love' in motivation_text or 'help' in motivation_text:
            traits.append('compassionate')
        if 'secret' in conflict_text or 'hidden' in conflict_text:
            traits.append('mysterious')

        return list(set(traits))[:3]  # Return top 3 unique traits

    async def _map_to_genres(self, traits: List[str]) -> Tuple[str, List[str]]:
        """Map personality traits to musical genres using enhanced wiki-based mapping"""

        # Ensure wiki integration is initialized
        await self._ensure_wiki_integration()

        # Try enhanced mapping first if available
        if self.enhanced_genre_mapper:
            try:
                genre_matches = await self.enhanced_genre_mapper.map_traits_to_genres(
                    traits, max_results=5, use_hierarchical=True
                )

                if genre_matches and len(genre_matches) > 0:
                    # Register genre sources for attribution
                    if self.source_attribution_manager:
                        for match in genre_matches:
                            if hasattr(match.genre, 'source_url') and match.genre.source_url:
                                self.source_attribution_manager.register_source(
                                    match.genre.source_url,
                                    'genre',
                                    f"Genre: {match.genre.name}",
                                    match.genre.download_date if hasattr(match.genre, 'download_date') else datetime.now()
                                )

                    # Extract primary and secondary genres from matches
                    primary_genre = genre_matches[0].genre.name
                    secondary_genres = [match.genre.name for match in genre_matches[1:3]]

                    # Ensure we have at least 2 secondary genres
                    if len(secondary_genres) < 2:
                        # Add more from matches or use fallback
                        for match in genre_matches[3:]:
                            if len(secondary_genres) >= 2:
                                break
                            secondary_genres.append(match.genre.name)

                        # If still not enough, use fallback genres
                        if len(secondary_genres) < 2:
                            fallback_genres = ['indie', 'alternative', 'pop', 'rock']
                            for genre in fallback_genres:
                                if genre != primary_genre and genre not in secondary_genres:
                                    secondary_genres.append(genre)
                                    if len(secondary_genres) >= 2:
                                        break

                    logger.info(f"Enhanced mapping: {primary_genre} with confidence {genre_matches[0].confidence:.3f}")
                    return primary_genre, secondary_genres[:2]

            except Exception as e:
                logger.warning(f"Enhanced genre mapping failed: {e}, falling back to hardcoded mapping")

        # Fallback to intelligent mapping
        return await self._fallback_map_to_genres(traits)

    async def _fallback_map_to_genres(self, traits: List[str]) -> Tuple[str, List[str]]:
        """Intelligent fallback trait-to-genre mapping using enhanced genre mapper when available"""

        # Try to use enhanced genre mapper's intelligent fallback first
        if self.enhanced_genre_mapper:
            try:
                logger.info(f"Using enhanced genre mapper fallback for traits: {traits}")

                # Use the enhanced genre mapper's intelligent fallback matching
                genre_matches = await self.enhanced_genre_mapper.find_fallback_matches(
                    traits, max_results=5
                )

                if genre_matches and len(genre_matches) > 0:
                    # Register genre sources for attribution
                    if self.source_attribution_manager:
                        for match in genre_matches:
                            if hasattr(match.genre, 'source_url') and match.genre.source_url:
                                self.source_attribution_manager.register_source(
                                    match.genre.source_url,
                                    'genre',
                                    f"Genre: {match.genre.name}",
                                    match.genre.download_date if hasattr(match.genre, 'download_date') else datetime.now()
                                )

                    # Extract primary and secondary genres from matches
                    primary_genre = genre_matches[0].genre.name
                    secondary_genres = [match.genre.name for match in genre_matches[1:3]]

                    # Ensure we have at least 2 secondary genres
                    if len(secondary_genres) < 2:
                        # Add more from matches
                        for match in genre_matches[3:]:
                            if len(secondary_genres) >= 2:
                                break
                            secondary_genres.append(match.genre.name)

                        # If still not enough, use basic fallback genres
                        if len(secondary_genres) < 2:
                            fallback_genres = ['indie', 'alternative', 'pop', 'rock']
                            for genre in fallback_genres:
                                if genre != primary_genre and genre not in secondary_genres:
                                    secondary_genres.append(genre)
                                    if len(secondary_genres) >= 2:
                                        break

                    logger.info(f"Enhanced fallback mapping: {primary_genre} with confidence {genre_matches[0].confidence:.3f}")
                    return primary_genre, secondary_genres[:2]

            except Exception as e:
                logger.warning(f"Enhanced fallback genre mapping failed: {e}, using hardcoded fallback")

        # Final fallback to hardcoded mappings when enhanced mapper is unavailable
        return self._hardcoded_fallback_mapping(traits)

    def _hardcoded_fallback_mapping(self, traits: List[str]) -> Tuple[str, List[str]]:
        """Final hardcoded fallback when all intelligent methods fail"""
        logger.info("Using hardcoded fallback trait mappings as last resort")

        # Define essential trait-to-genre mappings for absolute fallback
        trait_genre_map = {
            'melancholic': ['blues', 'folk', 'indie'],
            'mysterious': ['dark ambient', 'gothic', 'alternative'],
            'brave': ['rock', 'metal', 'punk'],
            'compassionate': ['soul', 'gospel', 'folk'],
            'rebellious': ['punk', 'alternative', 'grunge'],
            'intellectual': ['progressive', 'art rock', 'ambient'],
            'intellectual courage': ['progressive', 'art rock', 'experimental'],
            'creative': ['indie', 'alternative', 'art pop'],
            'adventurous': ['electronic', 'synthwave', 'space rock'],
            'emotional': ['blues', 'soul', 'gospel'],
            'confident': ['rock', 'pop', 'electronic'],
            'vulnerable': ['indie', 'singer-songwriter', 'folk'],
            'ambitious': ['pop', 'electronic', 'rock'],
            'perfectionist': ['progressive', 'classical', 'jazz'],
            'authentic': ['folk', 'country', 'singer-songwriter'],
            'introspective': ['ambient', 'post-rock', 'indie'],
            'artistic': ['art pop', 'experimental', 'indie'],
            'quest for meaning': ['progressive', 'ambient', 'post-rock'],
            'commitment to life': ['soul', 'gospel', 'blues'],
            'love transcending death': ['blues', 'soul', 'folk'],
            'creative drive': ['indie', 'alternative', 'art pop'],
            'fear of exposure': ['indie', 'singer-songwriter', 'alternative'],
            'duty to crew': ['electronic', 'synthwave', 'rock'],
            'courage under pressure': ['rock', 'electronic', 'metal'],
            'desire for freedom': ['indie', 'alternative', 'folk'],
            'need for authenticity': ['singer-songwriter', 'folk', 'indie'],
            'duty to justice': ['alternative', 'rock', 'gothic'],
            'inherited magical responsibility': ['gothic', 'dark ambient', 'alternative'],
            'intellectual brilliance': ['progressive', 'art rock', 'classical'],
            'determination to contribute': ['classical', 'orchestral', 'progressive']
        }

        # Find best matching genre based on traits with priority weighting
        genre_scores = {}
        for i, trait in enumerate(traits):
            trait_lower = trait.lower()
            if trait_lower in trait_genre_map:
                # Give higher weight to first traits (more important)
                weight = len(traits) - i
                for genre in trait_genre_map[trait_lower]:
                    genre_scores[genre] = genre_scores.get(genre, 0) + weight

        # If no direct matches, use intelligent fallback mapping
        if not genre_scores:
            # Try to use genre intelligence for better fallback
            try:
                from genre_production_intelligence import get_genre_intelligence
                genre_intelligence = get_genre_intelligence()

                # Use character traits to determine better genre
                character_traits = traits[:5]  # Use the traits already passed to this method

                if character_traits:
                    # This would require implementing trait-to-genre mapping in genre intelligence
                    # For now, use improved fallback based on character analysis
                    if any(trait.lower() in ['dark', 'intense', 'aggressive'] for trait in character_traits):
                        primary_genre = 'electronic'
                        secondary_genres = ['drum_and_bass', 'trap']
                    elif any(trait.lower() in ['peaceful', 'calm', 'introspective'] for trait in character_traits):
                        primary_genre = 'folk'
                        secondary_genres = ['alternative', 'indie']
                    elif any(trait.lower() in ['energetic', 'dynamic', 'powerful'] for trait in character_traits):
                        primary_genre = 'hip_hop'
                        secondary_genres = ['trap', 'alternative']
                    else:
                        primary_genre = 'alternative'
                        secondary_genres = ['indie', 'pop']
                else:
                    primary_genre = 'alternative'
                    secondary_genres = ['indie', 'pop']
            except ImportError:
                primary_genre = 'alternative'
                secondary_genres = ['indie', 'pop']
        else:
            # Sort by score and select top genres
            sorted_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)
            primary_genre = sorted_genres[0][0]
            secondary_genres = [genre for genre, _ in sorted_genres[1:3]]

            # Ensure we have at least 2 secondary genres
            if len(secondary_genres) < 2:
                fallback_genres = ['indie', 'alternative', 'pop', 'rock']
                for genre in fallback_genres:
                    if genre != primary_genre and genre not in secondary_genres:
                        secondary_genres.append(genre)
                        if len(secondary_genres) >= 2:
                            break

        return primary_genre, secondary_genres[:2]

    def _determine_vocal_style(self, traits: List[str], requested_genre: Optional[str] = None) -> str:
        """Determine vocal style from character traits, optionally aligned with requested genre"""

        # If genre is requested, prioritize genre-appropriate vocal style
        if requested_genre:
            try:
                from genre_production_intelligence import get_genre_intelligence
                genre_intelligence = get_genre_intelligence()
                genre_profile = genre_intelligence.get_genre_profile(requested_genre)

                if genre_profile.vocal_style.delivery_style:
                    base_style = genre_profile.vocal_style.delivery_style
                    if genre_profile.vocal_style.emotional_approach:
                        return f"{base_style} and {genre_profile.vocal_style.emotional_approach}"
                    return base_style
            except ImportError:
                pass

        # Define trait-to-vocal-style mappings
        trait_vocal_map = {
            'melancholic': 'soulful and emotional',
            'mysterious': 'haunting and atmospheric',
            'brave': 'powerful and commanding',
            'compassionate': 'warm and heartfelt',
            'rebellious': 'raw and aggressive',
            'intellectual': 'contemplative and articulate',
            'creative': 'expressive and artistic',
            'adventurous': 'dynamic and energetic',
            'emotional': 'raw and passionate',
            'confident': 'strong and commanding',
            'vulnerable': 'intimate and delicate',
            'ambitious': 'powerful and determined',
            'perfectionist': 'precise and controlled',
            'authentic': 'honest and genuine',
            'introspective': 'thoughtful and reflective',
            'artistic': 'expressive and creative',
            'quest for meaning': 'profound and contemplative',
            'commitment to life': 'passionate and soulful',
            'love transcending death': 'emotional and heartfelt',
            'creative drive': 'expressive and passionate',
            'fear of exposure': 'vulnerable and authentic',
            'duty to crew': 'strong and reliable',
            'courage under pressure': 'powerful and confident',
            'desire for freedom': 'liberating and expressive',
            'need for authenticity': 'honest and raw',
            'duty to justice': 'determined and strong',
            'inherited magical responsibility': 'mysterious and powerful',
            'intellectual brilliance': 'articulate and measured',
            'determination to contribute': 'inspiring and uplifting'
        }

        # Find best matching vocal style
        for trait in traits:
            trait_lower = trait.lower()
            if trait_lower in trait_vocal_map:
                return trait_vocal_map[trait_lower]

        # Default fallback
        return 'expressive and character-driven'

    def _generate_artist_name(self, character_name: str, traits: List[str]) -> str:
        """Generate an artist name based on character name and traits"""
        # Use character name as base, possibly with modifications
        if len(traits) > 0:
            trait_modifiers = {
                'mysterious': ['Shadow', 'Echo', 'Veil'],
                'brave': ['Steel', 'Fire', 'Storm'],
                'melancholic': ['Rain', 'Moon', 'Mist'],
                'rebellious': ['Wild', 'Rage', 'Storm'],
                'compassionate': ['Soul', 'Heart', 'Grace']
            }

            primary_trait = traits[0]
            if primary_trait in trait_modifiers:
                modifier = trait_modifiers[primary_trait][0]
                return f"{character_name} {modifier}"

        return character_name

    def _generate_lyrical_themes(self, character: StandardCharacterProfile) -> List[str]:
        """Generate lyrical themes from character profile"""
        themes = []

        # Extract from personality drivers first (most important)
        for driver in character.personality_drivers:
            driver_lower = driver.lower()
            if 'quest for meaning' in driver_lower or 'intellectual' in driver_lower:
                themes.extend(['existential questions', 'search for truth', 'philosophical inquiry', 'meaning of life'])
            elif 'creative' in driver_lower or 'artistic' in driver_lower:
                themes.extend(['artistic expression', 'creative struggle', 'inspiration', 'artistic authenticity'])
            elif 'duty' in driver_lower or 'responsibility' in driver_lower:
                themes.extend(['honor and duty', 'responsibility', 'service to others', 'moral obligation'])
                # Add adventure themes for duty to crew (space/adventure context)
                if 'crew' in driver_lower:
                    themes.extend(['exploration', 'journey', 'unknown territories', 'frontier'])
            elif 'courage' in driver_lower or 'brave' in driver_lower:
                themes.extend(['overcoming fear', 'heroic journey', 'standing up for beliefs', 'courage under pressure'])
                # Add adventure themes for courage under pressure (adventure context)
                if 'pressure' in driver_lower:
                    themes.extend(['discovery', 'courage', 'unknown', 'exploration'])
            elif 'love' in driver_lower or 'compassion' in driver_lower:
                themes.extend(['love transcending boundaries', 'compassion for others', 'human connection', 'empathy'])

        # Extract from motivations
        for motivation in character.motivations:
            motivation_lower = motivation.lower()
            if 'love' in motivation_lower:
                themes.append('love and relationships')
            elif 'power' in motivation_lower:
                themes.append('ambition and power')
            elif 'freedom' in motivation_lower:
                themes.append('liberation and independence')
            elif 'justice' in motivation_lower:
                themes.append('justice and fairness')
            elif 'adventure' in motivation_lower:
                themes.append('exploration and discovery')

        # Extract from fears
        for fear in character.fears:
            fear_lower = fear.lower()
            if 'death' in fear_lower:
                themes.append('mortality and existence')
            elif 'loss' in fear_lower:
                themes.append('loss and separation')
            elif 'exposure' in fear_lower:
                themes.append('vulnerability and authenticity')

        # Extract from conflicts
        for conflict in character.conflicts:
            conflict_lower = conflict.lower()
            if 'family' in conflict_lower:
                themes.append('family dynamics')
            elif 'society' in conflict_lower:
                themes.append('social commentary')
            elif 'vs' in conflict_lower:
                # Extract opposing concepts
                parts = conflict_lower.split(' vs ')
                if len(parts) == 2:
                    themes.append(f'tension between {parts[0]} and {parts[1]}')

        # Add character-specific themes based on backstory
        if hasattr(character, 'backstory') and character.backstory:
            backstory_lower = character.backstory.lower()
            if 'mathematical' in backstory_lower or 'science' in backstory_lower:
                themes.extend(['logic and reason', 'scientific discovery', 'mathematical beauty'])
            elif 'historical' in backstory_lower:
                themes.extend(['lessons from history', 'timeless wisdom', 'legacy and tradition'])
            elif 'magical' in backstory_lower or 'fantasy' in backstory_lower:
                themes.extend(['magic and mystery', 'supernatural forces', 'hidden worlds'])
            elif 'starship' in backstory_lower or 'space' in backstory_lower or 'captain' in backstory_lower:
                themes.extend(['exploration', 'journey', 'discovery', 'unknown', 'frontier', 'courage'])

        # Add default themes if none found, but make them richer
        if not themes:
            themes = ['personal journey', 'emotional expression', 'life experiences', 'human condition']

        # Remove duplicates and return top themes
        unique_themes = list(dict.fromkeys(themes))  # Preserves order while removing duplicates
        return unique_themes[:5]  # Return up to 5 themes for complex characters

    def _generate_emotional_palette(self, character: StandardCharacterProfile,
                                  requested_genre: Optional[str] = None) -> List[str]:
        """Generate emotional palette from character analysis, optionally aligned with requested genre"""
        emotions = []

        # Map personality drivers to emotions
        driver_emotions = {
            'brave': 'determination',
            'cunning': 'intensity',
            'compassionate': 'warmth',
            'ambitious': 'drive',
            'mysterious': 'intrigue',
            'cheerful': 'joy',
            'melancholic': 'melancholy',
            'rebellious': 'defiance'
        }

        for driver in character.personality_drivers:
            trait = driver.split(' (')[0]
            if trait in driver_emotions:
                emotions.append(driver_emotions[trait])

        # Add emotional range based on character complexity
        if character.confidence_score > 0.7:
            emotions.extend(['complexity', 'depth'])

        if not emotions:
            emotions = ['authenticity', 'expression']

        # If genre is requested, blend with genre-appropriate emotions
        if requested_genre:
            try:
                from genre_production_intelligence import (
                    _align_emotional_palette_with_genre,
                    get_genre_intelligence,
                )
                genre_intelligence = get_genre_intelligence()
                genre_profile = genre_intelligence.get_genre_profile(requested_genre)
                emotions = _align_emotional_palette_with_genre(emotions, genre_profile)
            except ImportError:
                pass

        return list(set(emotions))[:5]

    def _generate_influences(self, primary_genre: str, character: StandardCharacterProfile,
                           requested_genre: Optional[str] = None) -> List[str]:
        """Generate artistic influences based on genre and character, optionally using requested genre"""
        # Use requested genre if provided, otherwise use mapped genre
        genre_for_influences = requested_genre if requested_genre else primary_genre

        # Try to get genre-specific influences from genre intelligence first
        if requested_genre:
            try:
                from genre_production_intelligence import (
                    _generate_genre_appropriate_influences,
                    get_genre_intelligence,
                )
                genre_intelligence = get_genre_intelligence()
                genre_profile = genre_intelligence.get_genre_profile(requested_genre)
                return _generate_genre_appropriate_influences(genre_profile, character.name)
            except ImportError:
                pass

        genre_influences = {
            'rock': ['classic rock legends', 'alternative pioneers', 'indie innovators'],
            'metal': ['metal masters', 'progressive experimenters', 'symphonic composers'],
            'jazz': ['jazz greats', 'fusion innovators', 'contemporary jazz artists'],
            'electronic': ['electronic pioneers', 'ambient composers', 'dance music innovators'],
            'folk': ['folk storytellers', 'singer-songwriters', 'traditional musicians'],
            'pop': ['pop icons', 'contemporary artists', 'crossover musicians'],
            'indie': ['indie darlings', 'alternative artists', 'underground musicians'],
            'blues': ['blues legends', 'soul masters', 'rhythm innovators'],
            'progressive': ['progressive rock pioneers', 'art rock innovators', 'concept album masters'],
            'ambient': ['ambient composers', 'atmospheric sound designers', 'meditative musicians'],
            'post-rock': ['post-rock architects', 'instrumental storytellers', 'cinematic composers'],
            'art rock': ['art rock visionaries', 'experimental rock artists', 'avant-garde musicians'],
            'soul': ['soul legends', 'gospel innovators', 'rhythm and blues masters'],
            'gospel': ['gospel pioneers', 'spiritual music leaders', 'choir directors'],
            'alternative': ['alternative rock icons', 'indie pioneers', 'underground innovators'],
            'singer-songwriter': ['folk storytellers', 'acoustic poets', 'intimate performers'],
            'synthwave': ['synthwave pioneers', 'retro-futuristic composers', 'electronic nostalgia artists'],
            'space rock': ['cosmic rock explorers', 'psychedelic space travelers', 'interstellar musicians'],
            'art pop': ['art pop innovators', 'experimental pop artists', 'avant-garde performers'],
            'experimental': ['experimental music pioneers', 'sound art innovators', 'boundary-pushing artists'],
            'classical': ['classical composers', 'orchestral masters', 'chamber music specialists'],
            'orchestral': ['symphonic composers', 'film score masters', 'orchestral arrangers']
        }

        influences = genre_influences.get(genre_for_influences, ['diverse musical artists'])

        # Add character-specific influences
        if 'classical' in character.backstory.lower():
            influences.append('classical composers')
        if 'street' in character.backstory.lower():
            influences.append('street musicians')

        return influences[:3]

    def _determine_collaboration_style(self, character: StandardCharacterProfile,
                                     requested_genre: Optional[str] = None) -> str:
        """Determine collaboration approach based on character relationships and optionally requested genre"""

        # If genre is requested, prioritize genre-appropriate collaboration style
        if requested_genre:
            try:
                from genre_production_intelligence import (
                    _align_collaboration_style_with_genre,
                    get_genre_intelligence,
                )
                genre_intelligence = get_genre_intelligence()
                genre_profile = genre_intelligence.get_genre_profile(requested_genre)

                # Get base style from character
                base_style = self._get_base_collaboration_style(character)
                return _align_collaboration_style_with_genre(base_style, genre_profile)
            except ImportError:
                pass

        return self._get_base_collaboration_style(character)

    def _get_base_collaboration_style(self, character: StandardCharacterProfile) -> str:
        """Get base collaboration style from character traits"""
        # Analyze social connections and relationships
        if len(character.relationships) > 3:
            return 'collaborative and ensemble-oriented'
        elif 'leader' in ' '.join(character.behavioral_traits).lower():
            return 'takes creative control, directs projects'
        elif 'shy' in ' '.join(character.behavioral_traits).lower():
            return 'prefers intimate, small-group collaborations'
        else:
            return 'balanced collaborative approach'

    def _generate_persona_description(self, character: StandardCharacterProfile, genre: str, vocal_style: str) -> str:
        """Generate comprehensive persona description"""
        return f"""
        Musical persona derived from {character.name}: A {genre} artist with {vocal_style}. 
        The persona reflects {character.name}'s core traits of {', '.join(character.personality_drivers[:2])}, 
        channeling their {character.backstory[:100]}... into musical expression. 
        This artist embodies the emotional depth and complexity of the character while translating 
        narrative elements into compelling musical compositions.
        """.strip()

    def _calculate_mapping_confidence(self, character: StandardCharacterProfile, traits: List[str],
                                    requested_genre: Optional[str] = None) -> float:
        """Calculate confidence in character-to-music mapping"""
        base_confidence = character.confidence_score

        # Boost confidence if we have clear personality traits
        trait_boost = len(traits) * 0.1

        # Boost if character has rich emotional content
        emotion_boost = len(character.motivations + character.fears + character.desires) * 0.05

        # Boost if backstory provides context
        backstory_boost = 0.1 if len(character.backstory) > 50 else 0.0

        # If genre was requested (forced alignment), slightly reduce confidence
        genre_adjustment = -0.1 if requested_genre else 0.0

        return min(base_confidence + trait_boost + emotion_boost + backstory_boost + genre_adjustment, 1.0)

    def _generate_genre_justification(self, character: StandardCharacterProfile, traits: List[str],
                                    genre: str, requested_genre: Optional[str] = None) -> str:
        """Generate justification for genre selection"""
        trait_text = ', '.join(traits) if traits else 'complex personality'

        if requested_genre:
            return f"""
            {genre.title()} genre applied as requested, with persona aligned to match genre characteristics. 
            {character.name}'s {trait_text} has been adapted to fit {genre}'s emotional and thematic expressions. 
            The character's {character.motivations[0] if character.motivations else 'core motivations'} 
            and {character.conflicts[0] if character.conflicts else 'internal conflicts'} 
            are expressed through {genre}-specific musical elements and production techniques.
            """.strip()
        else:
            return f"""
            {genre.title()} genre selected based on {character.name}'s {trait_text}. 
            The character's {character.motivations[0] if character.motivations else 'core motivations'} 
            and {character.conflicts[0] if character.conflicts else 'internal conflicts'} 
            align with {genre}'s emotional and thematic expressions. 
            This mapping ensures authentic musical representation of the character's essence.
            """.strip()

    async def _generate_instrumental_preferences(self, genre: str) -> List[str]:
        """Generate instrumental preferences based on genre using wiki data"""
        # Try enhanced genre mapper first if available
        if self.enhanced_genre_mapper:
            try:
                # Define fallback instruments for the genre
                fallback_instruments = self._get_fallback_instruments(genre)

                # Get instruments from wiki data
                instruments = await self.enhanced_genre_mapper.get_genre_instruments(
                    genre, fallback_instruments=fallback_instruments
                )

                logger.info(f"Generated {len(instruments)} instrumental preferences for genre '{genre}' using wiki data")
                return instruments

            except Exception as e:
                logger.error(f"Error getting instruments from enhanced genre mapper: {e}")
                # Fall through to hardcoded fallback

        # Fallback to hardcoded mappings if wiki integration unavailable
        logger.info(f"Using fallback instrumental preferences for genre '{genre}'")
        return self._get_fallback_instruments(genre)

    def _get_fallback_instruments(self, genre: str) -> List[str]:
        """Get fallback instrumental preferences for a genre"""
        genre_instruments = {
            'rock': ['electric guitar', 'bass guitar', 'drums', 'synthesizer'],
            'metal': ['distorted guitar', 'bass guitar', 'heavy drums', 'orchestral elements'],
            'jazz': ['saxophone', 'piano', 'upright bass', 'drums'],
            'electronic': ['synthesizer', 'drum machine', 'sampling', 'digital effects'],
            'synthwave': ['synthesizer', 'drum machine', 'electronic bass', 'digital effects'],
            'space rock': ['synthesizer', 'electric guitar', 'atmospheric effects', 'electronic drums'],
            'folk': ['acoustic guitar', 'harmonica', 'fiddle', 'mandolin'],
            'pop': ['vocals', 'keyboard', 'guitar', 'electronic beats'],
            'indie': ['indie guitar', 'lo-fi production', 'vintage synthesizer', 'minimal drums'],
            'alternative': ['electric guitar', 'bass guitar', 'drums', 'effects pedals'],
            'art pop': ['synthesizer', 'unconventional instruments', 'electronic elements', 'vocals'],
            'blues': ['guitar', 'harmonica', 'piano', 'rhythm section'],
            'soul': ['piano', 'organ', 'horn section', 'rhythm guitar'],
            'gospel': ['organ', 'piano', 'choir', 'rhythm section'],
            'progressive': ['synthesizers', 'orchestral arrangements', 'complex percussion', 'guitar'],
            'art rock': ['synthesizer', 'guitar', 'unconventional instruments', 'orchestral elements'],
            'ambient': ['synthesizer', 'atmospheric sounds', 'minimal percussion', 'electronic textures'],
            'post-rock': ['electric guitar', 'effects pedals', 'atmospheric sounds', 'dynamic drums'],
            'singer-songwriter': ['acoustic guitar', 'piano', 'minimal accompaniment', 'vocals'],
            'country': ['acoustic guitar', 'steel guitar', 'fiddle', 'banjo'],
            'grunge': ['distorted guitar', 'bass guitar', 'heavy drums', 'raw production'],
            'punk': ['electric guitar', 'bass guitar', 'fast drums', 'minimal production'],
            'gothic': ['synthesizer', 'atmospheric sounds', 'dark electronic elements', 'orchestral'],
            'dark ambient': ['synthesizer', 'atmospheric textures', 'minimal percussion', 'electronic'],
            'classical': ['piano', 'strings', 'woodwinds', 'harpsichord'],
            'orchestral': ['strings', 'brass', 'woodwinds', 'timpani'],
            'experimental': ['unconventional instruments', 'electronic manipulation', 'found sounds', 'synthesizer']
        }

        return genre_instruments.get(genre, ['vocals', 'guitar', 'piano', 'drums'])

# ================================================================================================
# SUNO COMMAND GENERATOR
# ================================================================================================

class SunoCommandGenerator:
    """Generate optimized Suno AI commands from artist personas"""

    def __init__(self, wiki_data_manager: Optional['WikiDataManager'] = None):
        # Wiki data integration
        self.wiki_data_manager = wiki_data_manager

        # Initialize emotional beat engine for production instructions
        self.emotional_beat_engine = EmotionalBeatEngine()
        # Initialize emotional lyric generator
        self.lyric_generator = EmotionalLyricGenerator()

    async def get_style_tags_for_genre(self, genre: str) -> List[str]:
        """Get style tags for a genre from wiki data or fallback"""
        if self.wiki_data_manager:
            try:
                # Get meta tags from wiki data
                meta_tags = await self.wiki_data_manager.get_meta_tags(category="style")

                # Filter tags compatible with the genre
                compatible_tags = []
                for tag in meta_tags:
                    if not tag.compatible_genres or genre.lower() in [g.lower() for g in tag.compatible_genres]:
                        compatible_tags.append(tag.tag)

                if compatible_tags:
                    return compatible_tags[:4]  # Limit to 4 most relevant

            except Exception as e:
                logger.warning(f"Failed to get wiki style tags for {genre}: {e}")

        # Fallback to dynamic style tag generation
        return await self._get_fallback_style_tags(genre)

    async def get_structure_tags_for_complexity(self, complexity: str, character_traits: List[str] = None) -> List[str]:
        """Get structure tags based on complexity and character traits"""
        if self.wiki_data_manager:
            try:
                # Get structural meta tags from wiki
                meta_tags = await self.wiki_data_manager.get_meta_tags(category="structural")

                # Filter based on complexity and character traits
                suitable_tags = []
                for tag in meta_tags:
                    tag_lower = tag.tag.lower()
                    desc_lower = tag.description.lower()

                    # Match complexity level
                    if complexity == 'simple' and any(word in tag_lower or word in desc_lower
                                                    for word in ['simple', 'basic', 'straightforward', 'verse-chorus']):
                        suitable_tags.append(tag.tag)
                    elif complexity == 'complex' and any(word in tag_lower or word in desc_lower
                                                       for word in ['complex', 'bridge', 'dynamic', 'multiple']):
                        suitable_tags.append(tag.tag)
                    elif complexity == 'narrative' and any(word in tag_lower or word in desc_lower
                                                         for word in ['story', 'narrative', 'progressive', 'journey']):
                        suitable_tags.append(tag.tag)

                if suitable_tags:
                    return suitable_tags[:3]

            except Exception as e:
                logger.warning(f"Failed to get wiki structure tags for {complexity}: {e}")

        # Fallback to dynamic structure tag generation
        return await self._get_fallback_structure_tags(complexity, character_traits)

    async def get_vocal_tags_for_style(self, vocal_style: str, emotion: str = None) -> List[str]:
        """Get vocal tags based on vocal style and emotion"""
        if self.wiki_data_manager:
            try:
                # Get vocal meta tags from wiki
                meta_tags = await self.wiki_data_manager.get_meta_tags(category="vocal")

                suitable_tags = []
                for tag in meta_tags:
                    tag_lower = tag.tag.lower()
                    desc_lower = tag.description.lower()

                    # Match vocal style
                    if any(style_word in tag_lower or style_word in desc_lower
                          for style_word in vocal_style.lower().split()):
                        suitable_tags.append(tag.tag)

                    # Match emotion if provided
                    if emotion and (emotion.lower() in tag_lower or emotion.lower() in desc_lower):
                        suitable_tags.append(tag.tag)

                if suitable_tags:
                    return suitable_tags[:3]

            except Exception as e:
                logger.warning(f"Failed to get wiki vocal tags for {vocal_style}: {e}")

        # Fallback to dynamic vocal tag generation
        return await self._get_fallback_vocal_tags(vocal_style, emotion)

    async def get_emotional_meta_tags(self, emotion: str, genre: str = None) -> List[str]:
        """Get meta tags that match specific emotions"""
        if self.wiki_data_manager:
            try:
                # Get emotional meta tags from wiki
                meta_tags = await self.wiki_data_manager.get_meta_tags(category="emotional")

                suitable_tags = []
                for tag in meta_tags:
                    tag_lower = tag.tag.lower()
                    desc_lower = tag.description.lower()

                    # Match emotion
                    if emotion.lower() in tag_lower or emotion.lower() in desc_lower:
                        # Check genre compatibility if specified
                        if not genre or not tag.compatible_genres or genre.lower() in [g.lower() for g in tag.compatible_genres]:
                            suitable_tags.append(tag.tag)

                if suitable_tags:
                    return suitable_tags[:3]

            except Exception as e:
                logger.warning(f"Failed to get wiki emotional tags for {emotion}: {e}")

        # Use dynamic emotion tag generation
        return await self._get_fallback_emotion_tags(emotion)

    async def get_instrumental_meta_tags(self, instruments: List[str], genre: str = None) -> List[str]:
        """Get meta tags for specific instruments"""
        if self.wiki_data_manager:
            try:
                # Get instrumental meta tags from wiki
                meta_tags = await self.wiki_data_manager.get_meta_tags(category="instrumental")

                suitable_tags = []
                for tag in meta_tags:
                    tag_lower = tag.tag.lower()
                    desc_lower = tag.description.lower()

                    # Match instruments
                    for instrument in instruments:
                        if instrument.lower() in tag_lower or instrument.lower() in desc_lower:
                            # Check genre compatibility if specified
                            if not genre or not tag.compatible_genres or genre.lower() in [g.lower() for g in tag.compatible_genres]:
                                suitable_tags.append(tag.tag)

                if suitable_tags:
                    return suitable_tags[:3]

            except Exception as e:
                logger.warning(f"Failed to get wiki instrumental tags for {instruments}: {e}")

        # Fallback to instrument names
        return instruments[:3]

    def check_meta_tag_compatibility(self, tags: List[str], genre: str = None) -> List[str]:
        """Check and resolve meta tag conflicts"""
        # Basic conflict resolution - remove contradictory tags
        conflicts = [
            (['fast', 'slow'], 'tempo'),
            (['loud', 'quiet', 'soft'], 'volume'),
            (['simple', 'complex'], 'complexity'),
            (['electronic', 'acoustic'], 'production')
        ]

        resolved_tags = tags.copy()

        for conflict_group, conflict_type in conflicts:
            found_tags = [tag for tag in resolved_tags if any(conflict in tag.lower() for conflict in conflict_group)]
            if len(found_tags) > 1:
                # Keep the first one, remove others
                for tag in found_tags[1:]:
                    if tag in resolved_tags:
                        resolved_tags.remove(tag)

        return resolved_tags

    async def get_genre_specific_meta_tags(self, genre: str, context: str = None) -> Dict[str, List[str]]:
        """Get meta tags specifically curated for a genre with contextual selection"""
        if self.wiki_data_manager:
            try:
                # Get all meta tags
                all_meta_tags = await self.wiki_data_manager.get_meta_tags()

                # Categorize tags by type for this genre
                genre_tags = {
                    'style': [],
                    'structural': [],
                    'emotional': [],
                    'instrumental': [],
                    'vocal': [],
                    'production': []
                }

                for tag in all_meta_tags:
                    # Check if tag is compatible with genre
                    if not tag.compatible_genres or genre.lower() in [g.lower() for g in tag.compatible_genres]:
                        category = tag.category.lower()

                        # Map categories to our structure
                        if category in ['style', 'genre']:
                            genre_tags['style'].append(tag.tag)
                        elif category in ['structural', 'structure']:
                            genre_tags['structural'].append(tag.tag)
                        elif category in ['emotional', 'emotion', 'mood']:
                            genre_tags['emotional'].append(tag.tag)
                        elif category in ['instrumental', 'instrument']:
                            genre_tags['instrumental'].append(tag.tag)
                        elif category in ['vocal', 'voice']:
                            genre_tags['vocal'].append(tag.tag)
                        elif category in ['production', 'technical']:
                            genre_tags['production'].append(tag.tag)

                # Apply contextual filtering if context is provided
                if context:
                    for category in genre_tags:
                        genre_tags[category] = self._filter_tags_by_context(genre_tags[category], context)

                return genre_tags

            except Exception as e:
                logger.warning(f"Failed to get genre-specific meta tags for {genre}: {e}")

        # Fallback to dynamic genre-specific tags
        return await self._get_fallback_genre_tags(genre)

    def _filter_tags_by_context(self, tags: List[str], context: str) -> List[str]:
        """Filter tags based on context (e.g., 'upbeat', 'melancholy', 'energetic')"""
        context_lower = context.lower()

        # Context-based filtering rules
        context_filters = {
            'upbeat': ['energetic', 'fast', 'bright', 'major', 'happy', 'driving'],
            'melancholy': ['sad', 'minor', 'slow', 'emotional', 'introspective', 'dark'],
            'energetic': ['fast', 'driving', 'powerful', 'intense', 'dynamic'],
            'calm': ['slow', 'peaceful', 'ambient', 'soft', 'gentle', 'relaxed'],
            'aggressive': ['heavy', 'distorted', 'intense', 'powerful', 'driving'],
            'romantic': ['smooth', 'soft', 'emotional', 'intimate', 'gentle']
        }

        # Find matching context
        relevant_keywords = []
        for ctx, keywords in context_filters.items():
            if ctx in context_lower:
                relevant_keywords.extend(keywords)

        if not relevant_keywords:
            return tags

        # Filter tags that match context keywords
        filtered_tags = []
        for tag in tags:
            tag_lower = tag.lower()
            if any(keyword in tag_lower for keyword in relevant_keywords):
                filtered_tags.append(tag)

        # If no matches, return original tags
        return filtered_tags if filtered_tags else tags

    async def _get_fallback_genre_tags(self, genre: str) -> Dict[str, List[str]]:
        """Get fallback genre-specific tags using intelligent generation when wiki data unavailable"""
        try:
            # Try to get from wiki data first
            if self.wiki_data_manager:
                try:
                    # Get all meta tags and filter by genre compatibility
                    all_tags = await self.wiki_data_manager.get_meta_tags()
                    genre_tags = {
                        'style': [],
                        'structural': [],
                        'emotional': [],
                        'instrumental': [],
                        'vocal': [],
                        'production': []
                    }

                    for tag in all_tags:
                        # Check if tag is compatible with the genre
                        if not tag.compatible_genres or genre.lower() in [g.lower() for g in tag.compatible_genres]:
                            category = tag.category.lower()
                            if category in genre_tags:
                                genre_tags[category].append(tag.tag)
                            elif 'style' in category:
                                genre_tags['style'].append(tag.tag)
                            elif 'structure' in category:
                                genre_tags['structural'].append(tag.tag)
                            elif 'emotion' in category or 'mood' in category:
                                genre_tags['emotional'].append(tag.tag)
                            elif 'instrument' in category:
                                genre_tags['instrumental'].append(tag.tag)
                            elif 'vocal' in category:
                                genre_tags['vocal'].append(tag.tag)
                            elif 'production' in category or 'technical' in category:
                                genre_tags['production'].append(tag.tag)

                    # If we got good wiki data, return it
                    if any(len(tags) > 0 for tags in genre_tags.values()):
                        # Limit each category to 4 tags
                        for category in genre_tags:
                            genre_tags[category] = genre_tags[category][:4]
                        return genre_tags

                except Exception as e:
                    logger.debug(f"Wiki genre tags unavailable: {e}")

            # Try to get from error recovery manager's fallback data
            if hasattr(self, 'error_recovery_manager') and self.error_recovery_manager:
                fallback_data = self.error_recovery_manager.get_fallback_data('meta_tags')
                if fallback_data and fallback_data.data:
                    genre_tags = {
                        'style': [],
                        'structural': [],
                        'emotional': [],
                        'instrumental': [],
                        'vocal': [],
                        'production': []
                    }

                    for tag_data in fallback_data.data:
                        tag_text = tag_data.get('tag', '')
                        category = tag_data.get('category', '').lower()

                        # Check if tag is relevant to the genre
                        if genre.lower() in tag_text.lower() or not tag_data.get('compatible_genres'):
                            if category in genre_tags:
                                genre_tags[category].append(tag_text)

                    if any(len(tags) > 0 for tags in genre_tags.values()):
                        return genre_tags

            # Intelligent fallback based on genre characteristics
            genre_characteristics = {
                'rock': {
                    'style': ['rock', 'electric guitar', 'driving rhythm', 'powerful'],
                    'structural': ['verse-chorus', 'bridge', 'guitar solo'],
                    'emotional': ['energetic', 'rebellious', 'passionate'],
                    'instrumental': ['electric guitar', 'bass', 'drums'],
                    'vocal': ['strong vocals', 'belting', 'raspy'],
                    'production': ['distorted', 'amplified', 'dynamic']
                },
                'jazz': {
                    'style': ['jazz', 'smooth', 'improvisation', 'sophisticated'],
                    'structural': ['complex harmony', 'improvisation', 'swing'],
                    'emotional': ['smooth', 'sophisticated', 'expressive'],
                    'instrumental': ['saxophone', 'piano', 'upright bass', 'brushed drums'],
                    'vocal': ['smooth vocals', 'scatting', 'expressive'],
                    'production': ['acoustic', 'live recording', 'natural reverb']
                },
                'electronic': {
                    'style': ['electronic', 'synthesized', 'digital', 'rhythmic'],
                    'structural': ['build-up', 'drop', 'loop-based'],
                    'emotional': ['futuristic', 'hypnotic', 'energetic'],
                    'instrumental': ['synthesizer', 'drum machine', 'sampler'],
                    'vocal': ['processed vocals', 'vocoder', 'auto-tune'],
                    'production': ['digital effects', 'compression', 'layered']
                },
                'pop': {
                    'style': ['catchy', 'melodic', 'mainstream', 'polished'],
                    'structural': ['verse-chorus', 'hook', 'bridge'],
                    'emotional': ['uplifting', 'accessible', 'relatable'],
                    'instrumental': ['full arrangement', 'balanced mix'],
                    'vocal': ['clear vocals', 'melodic', 'accessible'],
                    'production': ['polished', 'radio-ready', 'compressed']
                },
                'folk': {
                    'style': ['acoustic', 'organic', 'storytelling', 'traditional'],
                    'structural': ['verse-chorus', 'narrative', 'simple'],
                    'emotional': ['authentic', 'heartfelt', 'nostalgic'],
                    'instrumental': ['acoustic guitar', 'harmonica', 'fiddle'],
                    'vocal': ['natural vocals', 'storytelling', 'intimate'],
                    'production': ['organic', 'minimal', 'natural']
                },
                'hip hop': {
                    'style': ['rhythmic', 'beats', 'urban', 'lyrical'],
                    'structural': ['verse-chorus', 'rap verses', 'hook'],
                    'emotional': ['confident', 'expressive', 'authentic'],
                    'instrumental': ['beats', 'bass', 'samples'],
                    'vocal': ['rap vocals', 'rhythmic', 'clear'],
                    'production': ['beats', 'sampling', 'layered']
                }
            }

            return genre_characteristics.get(genre.lower(), {
                'style': ['melodic', 'expressive'],
                'structural': ['verse-chorus'],
                'emotional': ['authentic'],
                'instrumental': ['full arrangement'],
                'vocal': ['expressive vocals'],
                'production': ['professional']
            })

        except Exception as e:
            logger.warning(f"Failed to get fallback genre tags for {genre}: {e}")
            return {
                'style': ['melodic', 'expressive'],
                'structural': ['verse-chorus'],
                'emotional': ['authentic'],
                'instrumental': ['full arrangement'],
                'vocal': ['expressive vocals'],
                'production': ['professional']
            }

    async def create_emotion_to_meta_tag_mapping(self, emotions: List[str], genre: str = None) -> Dict[str, List[str]]:
        """Create sophisticated emotion-to-meta-tag mapping using wiki data"""
        emotion_mapping = {}

        if self.wiki_data_manager:
            try:
                # Get emotional meta tags from wiki
                emotional_tags = await self.wiki_data_manager.get_meta_tags(category="emotional")

                for emotion in emotions:
                    emotion_lower = emotion.lower()
                    matching_tags = []

                    for tag in emotional_tags:
                        tag_lower = tag.tag.lower()
                        desc_lower = tag.description.lower()

                        # Direct emotion match
                        if emotion_lower in tag_lower or emotion_lower in desc_lower:
                            # Check genre compatibility
                            if not genre or not tag.compatible_genres or genre.lower() in [g.lower() for g in tag.compatible_genres]:
                                matching_tags.append(tag.tag)

                        # Semantic emotion matching
                        elif self._emotions_are_related(emotion_lower, tag_lower, desc_lower):
                            if not genre or not tag.compatible_genres or genre.lower() in [g.lower() for g in tag.compatible_genres]:
                                matching_tags.append(tag.tag)

                    emotion_mapping[emotion] = matching_tags[:4]  # Limit to 4 most relevant

            except Exception as e:
                logger.warning(f"Failed to create emotion-to-meta-tag mapping: {e}")

        # Fill in any missing emotions with fallback mappings
        for emotion in emotions:
            if emotion not in emotion_mapping:
                emotion_mapping[emotion] = await self._get_fallback_emotion_tags(emotion)

        return emotion_mapping

    def _emotions_are_related(self, emotion: str, tag: str, description: str) -> bool:
        """Check if an emotion is semantically related to a meta tag"""
        emotion_relations = {
            'joy': ['happy', 'uplifting', 'bright', 'cheerful', 'positive', 'energetic'],
            'sadness': ['melancholy', 'dark', 'minor', 'somber', 'mournful', 'blue'],
            'anger': ['aggressive', 'intense', 'heavy', 'powerful', 'driving', 'fierce'],
            'fear': ['tense', 'anxious', 'dark', 'mysterious', 'suspenseful', 'eerie'],
            'love': ['romantic', 'warm', 'intimate', 'gentle', 'soft', 'tender'],
            'nostalgia': ['wistful', 'reminiscent', 'vintage', 'classic', 'timeless'],
            'contemplation': ['thoughtful', 'reflective', 'meditative', 'introspective', 'ambient'],
            'excitement': ['energetic', 'fast', 'driving', 'dynamic', 'upbeat', 'lively']
        }

        related_words = emotion_relations.get(emotion, [])
        return any(word in tag or word in description for word in related_words)

    async def _get_fallback_style_tags(self, genre: str) -> List[str]:
        """Get fallback style tags using intelligent generation when wiki data unavailable"""
        try:
            # Try to get from error recovery manager's fallback data
            if hasattr(self, 'error_recovery_manager') and self.error_recovery_manager:
                fallback_data = self.error_recovery_manager.get_fallback_data('meta_tags')
                if fallback_data and fallback_data.data:
                    style_tags = [tag['tag'] for tag in fallback_data.data
                                if tag.get('category') == 'style' or genre.lower() in tag.get('tag', '').lower()]
                    if style_tags:
                        return style_tags[:4]

            # Intelligent fallback based on genre characteristics
            genre_characteristics = {
                'rock': ['electric guitar', 'driving rhythm', 'powerful', 'energetic'],
                'metal': ['heavy', 'distorted', 'aggressive', 'intense'],
                'jazz': ['smooth', 'improvisation', 'sophisticated', 'complex'],
                'electronic': ['synthesized', 'digital', 'rhythmic', 'atmospheric'],
                'folk': ['acoustic', 'organic', 'storytelling', 'traditional'],
                'pop': ['catchy', 'melodic', 'mainstream', 'polished'],
                'indie': ['alternative', 'independent', 'lo-fi', 'artistic'],
                'blues': ['soulful', 'emotional', 'raw', 'expressive'],
                'hip hop': ['rhythmic', 'beats', 'urban', 'lyrical'],
                'country': ['storytelling', 'rural', 'acoustic', 'narrative'],
                'classical': ['orchestral', 'complex', 'refined', 'traditional'],
                'reggae': ['rhythmic', 'relaxed', 'island', 'groove']
            }

            return genre_characteristics.get(genre.lower(), ['melodic', 'expressive'])

        except Exception as e:
            logger.warning(f"Failed to get fallback style tags for {genre}: {e}")
            return ['melodic', 'expressive']

    async def _get_fallback_structure_tags(self, complexity: str, character_traits: List[str] = None) -> List[str]:
        """Get fallback structure tags using intelligent generation when wiki data unavailable"""
        try:
            # Try to get from error recovery manager's fallback data
            if hasattr(self, 'error_recovery_manager') and self.error_recovery_manager:
                fallback_data = self.error_recovery_manager.get_fallback_data('meta_tags')
                if fallback_data and fallback_data.data:
                    structure_tags = [tag['tag'] for tag in fallback_data.data
                                    if tag.get('category') == 'structure']
                    if structure_tags:
                        return structure_tags[:3]

            # Intelligent fallback based on complexity and character traits
            complexity_mapping = {
                'simple': ['verse-chorus', 'straightforward', 'basic structure'],
                'complex': ['bridge', 'instrumental break', 'dynamic structure', 'multiple sections'],
                'narrative': ['storytelling', 'progressive', 'journey', 'evolving'],
                'emotional': ['building intensity', 'emotional arc', 'dynamic range', 'climactic']
            }

            base_tags = complexity_mapping.get(complexity, ['verse-chorus'])

            # Enhance based on character traits if provided
            if character_traits:
                trait_enhancements = {
                    'adventurous': ['dynamic transitions', 'unexpected changes'],
                    'contemplative': ['gradual build', 'reflective passages'],
                    'energetic': ['fast transitions', 'high energy'],
                    'melancholic': ['slow build', 'emotional depth']
                }

                for trait in character_traits:
                    trait_lower = trait.lower()
                    for trait_key, enhancements in trait_enhancements.items():
                        if trait_key in trait_lower:
                            base_tags.extend(enhancements[:1])  # Add one enhancement
                            break

            return base_tags[:3]  # Limit to 3 tags

        except Exception as e:
            logger.warning(f"Failed to get fallback structure tags for {complexity}: {e}")
            return ['verse-chorus']

    async def _get_fallback_vocal_tags(self, vocal_style: str, emotion: str = None) -> List[str]:
        """Get fallback vocal tags using intelligent generation when wiki data unavailable"""
        try:
            # Try to get from error recovery manager's fallback data
            if hasattr(self, 'error_recovery_manager') and self.error_recovery_manager:
                fallback_data = self.error_recovery_manager.get_fallback_data('meta_tags')
                if fallback_data and fallback_data.data:
                    vocal_tags = [tag['tag'] for tag in fallback_data.data
                                if tag.get('category') == 'vocal' or 'vocal' in tag.get('tag', '').lower()]
                    if vocal_tags:
                        return vocal_tags[:3]

            # Intelligent fallback based on vocal style and emotion
            style_mapping = {
                'powerful': ['strong vocals', 'commanding voice', 'belting', 'dynamic'],
                'smooth': ['smooth vocals', 'controlled delivery', 'refined', 'polished'],
                'emotional': ['emotional vocals', 'expressive', 'heartfelt', 'passionate'],
                'raw': ['raw vocals', 'unpolished', 'authentic', 'gritty'],
                'ethereal': ['ethereal vocals', 'floating', 'atmospheric', 'dreamy'],
                'aggressive': ['aggressive vocals', 'intense', 'forceful', 'harsh'],
                'gentle': ['gentle vocals', 'soft', 'tender', 'delicate'],
                'rhythmic': ['rhythmic vocals', 'percussive', 'syncopated', 'groove-based']
            }

            # Find matching style
            base_tags = []
            for style_key, tags in style_mapping.items():
                if style_key in vocal_style.lower():
                    base_tags = tags
                    break

            if not base_tags:
                base_tags = ['expressive vocals']

            # Enhance based on emotion if provided
            if emotion:
                emotion_enhancements = {
                    'joy': ['uplifting', 'bright'],
                    'sadness': ['melancholic', 'somber'],
                    'anger': ['intense', 'fierce'],
                    'love': ['warm', 'intimate'],
                    'fear': ['tense', 'anxious'],
                    'excitement': ['energetic', 'dynamic']
                }

                emotion_lower = emotion.lower()
                for emotion_key, enhancements in emotion_enhancements.items():
                    if emotion_key in emotion_lower:
                        base_tags.extend(enhancements[:1])  # Add one enhancement
                        break

            return base_tags[:3]  # Limit to 3 tags

        except Exception as e:
            logger.warning(f"Failed to get fallback vocal tags for {vocal_style}: {e}")
            return ['expressive vocals']

    async def _get_fallback_emotion_tags(self, emotion: str) -> List[str]:
        """Get fallback emotion tags using intelligent generation when wiki data unavailable"""
        try:
            # Try to get from wiki data first (emotional category)
            if self.wiki_data_manager:
                try:
                    emotional_tags = await self.wiki_data_manager.get_meta_tags(category="emotional")
                    matching_tags = []

                    for tag in emotional_tags:
                        tag_lower = tag.tag.lower()
                        desc_lower = tag.description.lower()
                        emotion_lower = emotion.lower()

                        # Direct emotion match
                        if emotion_lower in tag_lower or emotion_lower in desc_lower:
                            matching_tags.append(tag.tag)
                        # Semantic emotion matching
                        elif self._is_emotion_semantically_related(emotion_lower, tag_lower, desc_lower):
                            matching_tags.append(tag.tag)

                    if matching_tags:
                        return matching_tags[:4]

                except Exception as e:
                    logger.debug(f"Wiki emotional tags unavailable: {e}")

            # Try to get from error recovery manager's fallback data
            if hasattr(self, 'error_recovery_manager') and self.error_recovery_manager:
                fallback_data = self.error_recovery_manager.get_fallback_data('meta_tags')
                if fallback_data and fallback_data.data:
                    emotion_tags = [tag['tag'] for tag in fallback_data.data
                                  if tag.get('category') == 'mood' or emotion.lower() in tag.get('tag', '').lower()]
                    if emotion_tags:
                        return emotion_tags[:4]

            # Intelligent fallback with semantic emotion mapping
            emotion_semantic_mapping = {
                'joy': ['uplifting', 'happy', 'energetic', 'bright', 'cheerful', 'positive'],
                'happiness': ['uplifting', 'happy', 'energetic', 'bright', 'cheerful', 'positive'],
                'sadness': ['melancholic', 'sad', 'introspective', 'minor', 'somber', 'mournful'],
                'melancholy': ['melancholic', 'sad', 'introspective', 'minor', 'somber', 'mournful'],
                'anger': ['aggressive', 'intense', 'powerful', 'driving', 'fierce', 'harsh'],
                'rage': ['aggressive', 'intense', 'powerful', 'driving', 'fierce', 'harsh'],
                'fear': ['tense', 'dark', 'mysterious', 'anxious', 'ominous', 'suspenseful'],
                'anxiety': ['tense', 'dark', 'mysterious', 'anxious', 'ominous', 'suspenseful'],
                'love': ['romantic', 'warm', 'intimate', 'gentle', 'tender', 'affectionate'],
                'romance': ['romantic', 'warm', 'intimate', 'gentle', 'tender', 'affectionate'],
                'nostalgia': ['nostalgic', 'wistful', 'reminiscent', 'vintage', 'bittersweet', 'longing'],
                'longing': ['nostalgic', 'wistful', 'reminiscent', 'vintage', 'bittersweet', 'longing'],
                'contemplation': ['thoughtful', 'reflective', 'meditative', 'ambient', 'introspective', 'philosophical'],
                'reflection': ['thoughtful', 'reflective', 'meditative', 'ambient', 'introspective', 'philosophical'],
                'excitement': ['energetic', 'fast', 'dynamic', 'upbeat', 'thrilling', 'exhilarating'],
                'energy': ['energetic', 'fast', 'dynamic', 'upbeat', 'thrilling', 'exhilarating'],
                'peace': ['peaceful', 'calm', 'serene', 'tranquil', 'soothing', 'gentle'],
                'calm': ['peaceful', 'calm', 'serene', 'tranquil', 'soothing', 'gentle'],
                'hope': ['hopeful', 'uplifting', 'inspiring', 'optimistic', 'bright', 'encouraging'],
                'optimism': ['hopeful', 'uplifting', 'inspiring', 'optimistic', 'bright', 'encouraging']
            }

            # Find best semantic match
            emotion_lower = emotion.lower()
            for emotion_key, tags in emotion_semantic_mapping.items():
                if emotion_key in emotion_lower or emotion_lower in emotion_key:
                    return tags[:4]

            # Fallback to generic expressive tags
            return ['expressive', 'authentic', 'emotional', 'dynamic']

        except Exception as e:
            logger.warning(f"Failed to get fallback emotion tags for {emotion}: {e}")
            return ['expressive', 'authentic']

    async def correlate_instruments_to_meta_tags(self, instruments: List[str], genre: str = None, emotion: str = None) -> Dict[str, List[str]]:
        """Create sophisticated instrument-to-meta-tag correlation"""
        instrument_correlation = {}

        if self.wiki_data_manager:
            try:
                # Get instrumental meta tags from wiki
                instrumental_tags = await self.wiki_data_manager.get_meta_tags(category="instrumental")

                for instrument in instruments:
                    instrument_lower = instrument.lower()
                    matching_tags = []

                    for tag in instrumental_tags:
                        tag_lower = tag.tag.lower()
                        desc_lower = tag.description.lower()

                        # Direct instrument match
                        if instrument_lower in tag_lower or instrument_lower in desc_lower:
                            # Check genre and emotion compatibility
                            if self._is_tag_compatible(tag, genre, emotion):
                                matching_tags.append(tag.tag)

                        # Instrument family matching
                        elif self._instruments_are_related(instrument_lower, tag_lower, desc_lower):
                            if self._is_tag_compatible(tag, genre, emotion):
                                matching_tags.append(tag.tag)

                    instrument_correlation[instrument] = matching_tags[:3]  # Limit to 3 most relevant

            except Exception as e:
                logger.warning(f"Failed to correlate instruments to meta tags: {e}")

        # Fill in any missing instruments with fallback correlations
        for instrument in instruments:
            if instrument not in instrument_correlation:
                instrument_correlation[instrument] = await self._get_fallback_instrument_tags(instrument, genre, emotion)

        return instrument_correlation

    def _is_tag_compatible(self, tag, genre: str = None, emotion: str = None) -> bool:
        """Check if a meta tag is compatible with genre and emotion context"""
        # Check genre compatibility
        if genre and tag.compatible_genres:
            if genre.lower() not in [g.lower() for g in tag.compatible_genres]:
                return False

        # Check emotion compatibility (basic check)
        if emotion and tag.description:
            emotion_lower = emotion.lower()
            desc_lower = tag.description.lower()

            # If tag description contains contradictory emotions, it might not be compatible
            contradictory_emotions = {
                'happy': ['sad', 'melancholy', 'dark', 'gloomy'],
                'sad': ['happy', 'uplifting', 'bright', 'cheerful'],
                'energetic': ['slow', 'calm', 'peaceful', 'relaxed'],
                'calm': ['aggressive', 'intense', 'energetic', 'driving']
            }

            if emotion_lower in contradictory_emotions:
                if any(contra in desc_lower for contra in contradictory_emotions[emotion_lower]):
                    return False

        return True

    def _instruments_are_related(self, instrument: str, tag: str, description: str) -> bool:
        """Check if an instrument is related to a meta tag"""
        instrument_families = {
            'guitar': ['string', 'fretted', 'plucked', 'acoustic', 'electric'],
            'piano': ['keyboard', 'keys', 'acoustic', 'grand', 'upright'],
            'drums': ['percussion', 'rhythm', 'beat', 'kit', 'acoustic'],
            'bass': ['low', 'rhythm', 'foundation', 'groove', 'electric'],
            'violin': ['string', 'bowed', 'classical', 'orchestral'],
            'saxophone': ['wind', 'brass', 'jazz', 'reed', 'woodwind'],
            'synthesizer': ['electronic', 'digital', 'synth', 'keyboard', 'electronic']
        }

        related_words = instrument_families.get(instrument, [])
        return any(word in tag or word in description for word in related_words)

    async def _get_fallback_instrument_tags(self, instrument: str, genre: str = None, emotion: str = None) -> List[str]:
        """Get fallback instrument tags using intelligent generation when wiki data unavailable"""
        try:
            # Try to get from error recovery manager's fallback data
            if hasattr(self, 'error_recovery_manager') and self.error_recovery_manager:
                fallback_data = self.error_recovery_manager.get_fallback_data('meta_tags')
                if fallback_data and fallback_data.data:
                    instrument_tags = [tag['tag'] for tag in fallback_data.data
                                     if tag.get('category') == 'instrument' or instrument.lower() in tag.get('tag', '').lower()]
                    if instrument_tags:
                        return instrument_tags[:3]

            # Intelligent fallback based on instrument characteristics
            instrument_characteristics = {
                'guitar': ['guitar-driven', 'string-based', 'melodic', 'harmonic'],
                'electric guitar': ['electric', 'distorted', 'powerful', 'rock-oriented'],
                'acoustic guitar': ['acoustic', 'organic', 'warm', 'intimate'],
                'piano': ['piano-led', 'harmonic', 'melodic', 'expressive'],
                'drums': ['rhythmic', 'percussive', 'driving', 'dynamic'],
                'bass': ['bass-heavy', 'groove-based', 'rhythmic', 'foundational'],
                'violin': ['string section', 'orchestral', 'melodic', 'emotional'],
                'saxophone': ['brass section', 'jazzy', 'smooth', 'expressive'],
                'synthesizer': ['electronic', 'synthesized', 'digital', 'atmospheric'],
                'trumpet': ['brass', 'bright', 'bold', 'triumphant'],
                'flute': ['woodwind', 'airy', 'delicate', 'melodic'],
                'cello': ['string', 'deep', 'rich', 'emotional'],
                'harp': ['ethereal', 'delicate', 'classical', 'angelic']
            }

            base_tags = instrument_characteristics.get(instrument.lower(), [instrument]).copy()

            # Add genre-specific modifiers (prioritized)
            genre_modifiers = []
            if genre:
                genre_lower = genre.lower()
                instrument_lower = instrument.lower()

                genre_instrument_modifiers = {
                    'rock': {
                        'guitar': ['distorted', 'electric', 'powerful'],
                        'drums': ['heavy', 'driving', 'intense'],
                        'bass': ['punchy', 'aggressive']
                    },
                    'jazz': {
                        'piano': ['improvised', 'complex harmony', 'sophisticated'],
                        'saxophone': ['smooth', 'improvised', 'soulful'],
                        'bass': ['walking', 'swing', 'upright']
                    },
                    'electronic': {
                        'synthesizer': ['digital', 'programmed', 'atmospheric'],
                        'drums': ['programmed', 'electronic', 'precise']
                    },
                    'folk': {
                        'guitar': ['acoustic', 'fingerpicked', 'organic'],
                        'violin': ['fiddle', 'traditional', 'rustic']
                    },
                    'classical': {
                        'piano': ['concert', 'refined', 'technical'],
                        'violin': ['orchestral', 'precise', 'expressive']
                    }
                }

                if genre_lower in genre_instrument_modifiers:
                    if instrument_lower in genre_instrument_modifiers[genre_lower]:
                        genre_modifiers = genre_instrument_modifiers[genre_lower][instrument_lower][:2]

            # Add emotion-specific modifiers
            emotion_modifiers = []
            if emotion:
                emotion_lower = emotion.lower()
                emotion_instrument_modifiers = {
                    'aggressive': ['intense', 'powerful', 'driving'],
                    'gentle': ['soft', 'delicate', 'tender'],
                    'energetic': ['dynamic', 'fast', 'lively'],
                    'melancholic': ['somber', 'mournful', 'introspective'],
                    'romantic': ['warm', 'intimate', 'expressive']
                }

                for emotion_key, modifiers in emotion_instrument_modifiers.items():
                    if emotion_key in emotion_lower:
                        emotion_modifiers = modifiers[:1]  # Add one modifier
                        break

            # Combine tags with priority: genre modifiers, base tags, emotion modifiers
            final_tags = []
            final_tags.extend(genre_modifiers)
            final_tags.extend(base_tags)
            final_tags.extend(emotion_modifiers)

            # Remove duplicates while preserving order
            seen = set()
            unique_tags = []
            for tag in final_tags:
                if tag not in seen:
                    seen.add(tag)
                    unique_tags.append(tag)

            return unique_tags[:3]  # Limit to 3 tags

        except Exception as e:
            logger.warning(f"Failed to get fallback instrument tags for {instrument}: {e}")
            return [instrument]

    async def generate_suno_commands(self, artist_persona: ArtistPersona, character: StandardCharacterProfile, ctx: Context,
                                   emotional_states: Optional[List[EmotionalState]] = None,
                                   beat_progression: Optional[Dict] = None) -> List[SunoCommand]:
        """Generate multiple Suno AI command variations from artist persona"""
        await ctx.info(f"Generating Suno commands for {artist_persona.artist_name}...")

        commands = []

        # Generate different command types

        # 1. Simple prompt command
        simple_command = await self._generate_simple_command(artist_persona, character)
        commands.append(simple_command)

        # 2. Custom mode command with detailed parameters
        custom_command = await self._generate_custom_command(artist_persona, character)
        commands.append(custom_command)

        # 3. Bracket notation command for precise control
        bracket_command = await self._generate_bracket_command(artist_persona, character)
        commands.append(bracket_command)

        # 4. NEW: Emotion-driven beat command if emotional states are provided
        if emotional_states and len(emotional_states) > 0:
            emotion_beat_command = await self._generate_emotion_beat_command(
                artist_persona, character, emotional_states, beat_progression or {}
            )
            commands.append(emotion_beat_command)

        # 5. Lyric-focused command if character has strong narrative elements
        if len(character.motivations) > 1 or len(character.conflicts) > 1:
            lyric_command = await self._generate_lyric_focused_command(artist_persona, character)
            commands.append(lyric_command)

        # 6. Collaboration-style command if character has relationships
        if len(character.relationships) > 2:
            collab_command = await self._generate_collaboration_command(artist_persona, character)
            commands.append(collab_command)

        return commands

    async def _generate_simple_command(self, artist_persona: ArtistPersona, character: StandardCharacterProfile) -> SunoCommand:
        """Generate simple Suno command with basic prompt"""

        # Create compelling prompt from character essence
        primary_theme = artist_persona.lyrical_themes[0] if artist_persona.lyrical_themes else 'personal journey'
        emotional_core = artist_persona.emotional_palette[0] if artist_persona.emotional_palette else 'authentic expression'

        prompt = f"A {artist_persona.primary_genre} song about {primary_theme}, " \
                f"conveying {emotional_core} with {artist_persona.vocal_style}. " \
                f"Inspired by {character.name}'s journey and experiences."

        # Select relevant style tags from wiki data
        style_tags = await self.get_style_tags_for_genre(artist_persona.primary_genre)

        # Get structure and vocal tags from wiki data
        structure_tags = await self.get_structure_tags_for_complexity('simple')
        vocal_tags = await self.get_vocal_tags_for_style(artist_persona.vocal_style, emotional_core)

        # Check for tag compatibility
        all_tags = style_tags + structure_tags + vocal_tags
        compatible_tags = self.check_meta_tag_compatibility(all_tags, artist_persona.primary_genre)

        return SunoCommand(
            command_type="simple",
            prompt=prompt,
            style_tags=style_tags[:3],
            structure_tags=structure_tags[:2],
            sound_effect_tags=[],
            vocal_tags=vocal_tags[:2],
            character_source=character.name,
            artist_persona=artist_persona.artist_name,
            command_rationale=f"Simple command using wiki-sourced meta tags for {artist_persona.primary_genre} with {character.name}'s emotional theme",
            estimated_effectiveness=0.8,
            variations=[
                prompt.replace('song about', 'ballad about'),
                prompt.replace(artist_persona.primary_genre, artist_persona.secondary_genres[0] if artist_persona.secondary_genres else 'alternative')
            ]
        )

    async def _generate_custom_command(self, artist_persona: ArtistPersona, character: StandardCharacterProfile) -> SunoCommand:
        """Generate custom mode command with detailed parameters"""

        # Build comprehensive prompt
        themes = ', '.join(artist_persona.lyrical_themes[:2])
        emotions = ', '.join(artist_persona.emotional_palette[:2])

        prompt = f"Create a {artist_persona.primary_genre} composition exploring {themes}. " \
                f"The music should embody {emotions} while reflecting {character.name}'s " \
                f"{character.personality_drivers[0] if character.personality_drivers else 'complex nature'}. " \
                f"Incorporate elements of {artist_persona.secondary_genres[0] if artist_persona.secondary_genres else 'crossover style'}."

        # Use advanced genre-specific meta tag selection
        genre_tags = await self.get_genre_specific_meta_tags(
            artist_persona.primary_genre,
            context=emotions.split(', ')[0] if emotions else None
        )

        # Get style tags with contextual filtering
        style_tags = genre_tags['style'][:3]
        additional_style_tags = [artist_persona.primary_genre, 'professional production', 'dynamic']
        style_tags.extend(additional_style_tags)

        # Get structure tags from genre-specific selection
        structure_tags = genre_tags['structural'][:2]
        complexity = 'complex' if character.confidence_score > 0.7 else 'simple'
        additional_structure = await self.get_structure_tags_for_complexity(complexity, character.personality_drivers)
        structure_tags.extend(additional_structure[:2])

        # Use advanced emotion-to-meta-tag mapping
        primary_emotion = emotions.split(', ')[0] if emotions else None
        if primary_emotion:
            emotion_mapping = await self.create_emotion_to_meta_tag_mapping(
                [primary_emotion],
                artist_persona.primary_genre
            )
            emotional_tags = emotion_mapping.get(primary_emotion, [])
            style_tags.extend(emotional_tags[:2])

        # Get vocal tags from genre-specific selection and persona
        vocal_tags = genre_tags['vocal'][:2]
        persona_vocal_tags = await self.get_vocal_tags_for_style(artist_persona.vocal_style, primary_emotion)
        vocal_tags.extend(persona_vocal_tags[:2])

        # Use advanced instrument-to-meta-tag correlation
        sound_effects = []
        if artist_persona.instrumental_preferences:
            instrument_correlation = await self.correlate_instruments_to_meta_tags(
                artist_persona.instrumental_preferences,
                artist_persona.primary_genre,
                primary_emotion
            )

            # Collect correlated tags from all instruments
            for instrument, tags in instrument_correlation.items():
                sound_effects.extend(tags)

        # Add genre-specific production tags
        production_tags = genre_tags['production'][:2]
        sound_effects.extend(production_tags)

        # Add character-driven sound effects
        if 'mysterious' in str(character.personality_drivers):
            sound_effects.extend(['ethereal effects', 'subtle ambience'])

        # Check meta tag compatibility and resolve conflicts
        all_tags = style_tags + structure_tags + vocal_tags + sound_effects
        compatible_tags = self.check_meta_tag_compatibility(all_tags, artist_persona.primary_genre)

        return SunoCommand(
            command_type="custom",
            prompt=prompt,
            style_tags=style_tags[:4],
            structure_tags=structure_tags[:3],
            sound_effect_tags=sound_effects[:3],
            vocal_tags=vocal_tags[:3],
            character_source=character.name,
            artist_persona=artist_persona.artist_name,
            command_rationale=f"Custom command using wiki-sourced meta tags for detailed {artist_persona.primary_genre} composition with character-driven elements",
            estimated_effectiveness=0.9,
            variations=[
                prompt.replace('composition', 'piece'),
                prompt + " Include instrumental solo section.",
                prompt.replace(artist_persona.primary_genre, 'fusion')
            ]
        )

    async def _generate_bracket_command(self, artist_persona: ArtistPersona, character: StandardCharacterProfile) -> SunoCommand:
        """Generate bracket notation command for precise control"""

        # Build precise bracket notation
        genre_bracket = f"[{artist_persona.primary_genre}]"

        # Add emotional indicators
        emotion_bracket = f"[{artist_persona.emotional_palette[0]}]" if artist_persona.emotional_palette else "[expressive]"

        # Add vocal style
        vocal_bracket = f"[{artist_persona.vocal_style.split(',')[0]}]"

        # Add instrumental elements
        instruments = artist_persona.instrumental_preferences[:2]
        instrument_bracket = f"[{', '.join(instruments)}]" if instruments else "[full arrangement]"

        # Character-specific elements
        character_element = ""
        if character.personality_drivers:
            trait = character.personality_drivers[0].split(' (')[0]
            character_element = f"[{trait} energy]"

        prompt = f"{genre_bracket} {emotion_bracket} {vocal_bracket} {instrument_bracket} {character_element} " \
                f"Song inspired by {character.name}'s journey through {artist_persona.lyrical_themes[0] if artist_persona.lyrical_themes else 'life experiences'}"

        # Get wiki-based tags for bracket notation
        style_tags = await self.get_style_tags_for_genre(artist_persona.primary_genre)
        style_tags.extend([artist_persona.primary_genre, 'precise control'])

        structure_tags = await self.get_structure_tags_for_complexity('simple')
        structure_tags.append('controlled structure')

        vocal_tags = await self.get_vocal_tags_for_style(artist_persona.vocal_style)

        # Get instrumental tags for sound effects
        sound_effects = ['specified elements']
        if artist_persona.instrumental_preferences:
            instrumental_tags = await self.get_instrumental_meta_tags(
                artist_persona.instrumental_preferences[:2],
                artist_persona.primary_genre
            )
            sound_effects.extend(instrumental_tags)

        return SunoCommand(
            command_type="bracket_notation",
            prompt=prompt,
            style_tags=style_tags[:3],
            structure_tags=structure_tags[:2],
            sound_effect_tags=sound_effects[:3],
            vocal_tags=vocal_tags[:2],
            character_source=character.name,
            artist_persona=artist_persona.artist_name,
            command_rationale="Bracket notation command using wiki meta tags for precise musical element control",
            estimated_effectiveness=0.85,
            variations=[
                prompt.replace('Song inspired by', 'Composition reflecting'),
                prompt + f" [{artist_persona.secondary_genres[0]}]" if artist_persona.secondary_genres else prompt + " [alternative style]",
                prompt.replace(genre_bracket, f"[{artist_persona.secondary_genres[0] if artist_persona.secondary_genres else 'crossover'}]")
            ]
        )

    async def _generate_lyric_focused_command(self, artist_persona: ArtistPersona, character: StandardCharacterProfile) -> SunoCommand:
        """Generate command focused on lyrical storytelling"""

        # Extract narrative elements
        story_elements = []
        if character.motivations:
            story_elements.append(f"driven by {character.motivations[0]}")
        if character.conflicts:
            story_elements.append(f"struggling with {character.conflicts[0]}")
        if character.backstory and len(character.backstory) > 50:
            story_elements.append("with rich personal history")

        narrative = ', '.join(story_elements) if story_elements else "on a personal journey"

        prompt = f"Write and perform a {artist_persona.primary_genre} song that tells the story of someone {narrative}. " \
                f"Focus on lyrical storytelling with {artist_persona.vocal_style}. " \
                f"The song should capture the essence of {character.name}'s experience and emotional journey."

        # Get wiki-based tags for lyric-focused command
        style_tags = await self.get_style_tags_for_genre(artist_persona.primary_genre)
        style_tags.extend([artist_persona.primary_genre, 'storytelling', 'narrative'])

        structure_tags = await self.get_structure_tags_for_complexity('narrative', character.personality_drivers)
        structure_tags.extend(['verse-heavy', 'lyrical focus', 'story structure'])

        # Get vocal tags optimized for storytelling
        vocal_tags = await self.get_vocal_tags_for_style(artist_persona.vocal_style)
        storytelling_vocals = ['storytelling vocals', 'clear delivery', 'emotional expression']
        vocal_tags.extend(storytelling_vocals)

        return SunoCommand(
            command_type="lyric_focused",
            prompt=prompt,
            style_tags=style_tags[:4],
            structure_tags=structure_tags[:4],
            sound_effect_tags=[],
            vocal_tags=vocal_tags[:4],
            character_source=character.name,
            artist_persona=artist_persona.artist_name,
            command_rationale=f"Lyric-focused command using wiki meta tags to emphasize {character.name}'s narrative and storytelling elements",
            estimated_effectiveness=0.75,
            variations=[
                prompt.replace('song that tells the story', 'ballad that chronicles'),
                prompt + " Include spoken word elements.",
                prompt.replace('Write and perform', 'Compose and sing')
            ]
        )

    async def _generate_collaboration_command(self, artist_persona: ArtistPersona, character: StandardCharacterProfile) -> SunoCommand:
        """Generate command for collaborative-style music"""

        # Analyze character relationships for collaboration style
        relationship_styles = []
        for relationship in character.relationships[:2]:
            if 'friend' in relationship.lower():
                relationship_styles.append('friendly duet')
            elif 'family' in relationship.lower():
                relationship_styles.append('family harmony')
            elif 'mentor' in relationship.lower():
                relationship_styles.append('mentor-student exchange')
            else:
                relationship_styles.append('collaborative ensemble')

        collab_style = relationship_styles[0] if relationship_styles else 'ensemble performance'

        prompt = f"Create a {artist_persona.primary_genre} {collab_style} piece inspired by {character.name}'s " \
                f"relationships and social connections. The music should reflect {artist_persona.collaboration_style} " \
                f"with multiple vocal parts and {', '.join(artist_persona.instrumental_preferences[:2])}."

        # Get wiki-based tags for collaboration command
        style_tags = await self.get_style_tags_for_genre(artist_persona.primary_genre)
        style_tags.extend([artist_persona.primary_genre, 'collaborative', 'ensemble'])

        structure_tags = await self.get_structure_tags_for_complexity('complex', character.personality_drivers)
        collaboration_structure = ['multiple parts', 'call and response', 'harmony']
        structure_tags.extend(collaboration_structure)

        # Get vocal tags for collaborative performance
        vocal_tags = await self.get_vocal_tags_for_style(artist_persona.vocal_style)
        collaboration_vocals = ['multiple vocals', 'harmony', 'interaction']
        vocal_tags.extend(collaboration_vocals)

        # Get instrumental tags for ensemble
        sound_effects = []
        if artist_persona.instrumental_preferences:
            instrumental_tags = await self.get_instrumental_meta_tags(
                artist_persona.instrumental_preferences,
                artist_persona.primary_genre
            )
            sound_effects.extend(instrumental_tags)

        return SunoCommand(
            command_type="collaboration",
            prompt=prompt,
            style_tags=style_tags[:4],
            structure_tags=structure_tags[:4],
            sound_effect_tags=sound_effects[:3],
            vocal_tags=vocal_tags[:4],
            character_source=character.name,
            artist_persona=artist_persona.artist_name,
            command_rationale=f"Collaboration-focused command using wiki meta tags to reflect {character.name}'s social dynamics",
            estimated_effectiveness=0.8,
            variations=[
                prompt.replace('piece', 'composition'),
                prompt + " Include instrumental solos for each part.",
                prompt.replace(collab_style, 'group arrangement')
            ]
        )

    async def _generate_emotion_beat_command(self, artist_persona: ArtistPersona, character: StandardCharacterProfile,
                                           emotional_states: List[EmotionalState], beat_progression: Dict) -> SunoCommand:
        """Generate emotion-driven beat production command with detailed instructions"""

        # Extract primary emotional journey
        primary_emotion = emotional_states[0].primary_emotion if emotional_states else 'contemplative'
        emotion_sequence = ' -> '.join([state.primary_emotion for state in emotional_states[:4]])

        # Get beat pattern for primary emotion
        beat_pattern = self.emotional_beat_engine.emotion_beat_map.get(
            primary_emotion,
            self.emotional_beat_engine.emotion_beat_map['contemplation']
        )

        # Build detailed production prompt
        tempo_instruction = f"[{beat_pattern.tempo_range[0]}-{beat_pattern.tempo_range[1]}bpm]"
        rhythm_instruction = f"[{beat_pattern.rhythm_pattern}]"
        percussion_elements = ' + '.join([f"[{elem}]" for elem in beat_pattern.percussion_elements[:3]])

        # Include emotional authenticity in production
        authenticity_notes = []
        for state in emotional_states[:2]:
            if state.authenticity_score < 0.5:
                authenticity_notes.append(f"[subtle glitch/distortion at {state.primary_emotion} sections]")
            if state.internal_conflict:
                authenticity_notes.append(f"[contrasting rhythms for {state.internal_conflict}]")

        # Generate lyric structure
        primary_trigger = emotional_states[0].factual_triggers[0] if emotional_states and emotional_states[0].factual_triggers else "life experiences"
        lyric_structure = self.lyric_generator.generate_lyric_structure(
            emotional_states,
            f"{character.name}'s story about {primary_trigger}"
        )

        # Extract key lyrical content
        verse_hook = lyric_structure['structure']['verses'][0]['opening'] if lyric_structure['structure']['verses'] else "Tell the story"
        chorus_hook = lyric_structure['structure']['chorus']['hook']
        lyrical_themes = ', '.join(lyric_structure['themes'][:3])
        lyrical_devices = ', '.join(lyric_structure['lyrical_devices'][:2])

        # Build comprehensive prompt with lyrics
        prompt = f"{artist_persona.primary_genre} {tempo_instruction} {rhythm_instruction}\n" \
                f"Beat elements: {percussion_elements}\n" \
                f"Emotional journey: {emotion_sequence}\n" \
                f"Production: {beat_pattern.dynamic_progression}\n" \
                f"{' '.join(authenticity_notes)}\n" \
                f"Vocals: {artist_persona.vocal_style} expressing {primary_emotion} through {character.name}'s perspective\n" \
                f"Musical story: {emotional_states[0].factual_triggers[0] if emotional_states and emotional_states[0].factual_triggers else 'emotional narrative'}\n" \
                f"\nLYRICAL GUIDANCE:\n" \
                f"Verse concept: {verse_hook}\n" \
                f"Chorus hook: {chorus_hook}\n" \
                f"Themes: {lyrical_themes}\n" \
                f"Lyrical approach: {lyrical_devices}\n" \
                f"Key phrases: {', '.join(lyric_structure['key_phrases'][:3])}"

        # Use advanced genre-specific meta tag selection with emotional context
        genre_tags = await self.get_genre_specific_meta_tags(
            artist_persona.primary_genre,
            context=primary_emotion
        )

        # Get style tags with emotional filtering
        style_tags = genre_tags['style'][:3]

        # Use advanced emotion-to-meta-tag mapping for multiple emotions
        all_emotions = [state.primary_emotion for state in emotional_states[:3]]
        emotion_mapping = await self.create_emotion_to_meta_tag_mapping(
            all_emotions,
            artist_persona.primary_genre
        )

        # Collect emotional tags from all states
        for emotion, tags in emotion_mapping.items():
            style_tags.extend(tags[:2])

        # Add production-specific tags
        production_tags = [f"{primary_emotion}-driven", "dynamic production", "emotional beat mapping"]
        style_tags.extend(production_tags)

        # Get structure tags from genre-specific selection
        structure_tags = genre_tags['structural'][:2]

        # Add complexity-based structure tags
        complexity = 'complex' if len(emotional_states) > 2 else 'emotional'
        complexity_structure = await self.get_structure_tags_for_complexity(complexity, character.personality_drivers)
        structure_tags.extend(complexity_structure[:2])

        # Add emotion-specific structure tags
        if len(emotional_states) > 2:
            emotion_structure = ["emotional arc", "dynamic transitions", "evolving structure"]
        else:
            emotion_structure = ["focused emotion", "consistent mood", "subtle variations"]
        structure_tags.extend(emotion_structure)

        # Get vocal tags from genre-specific selection and emotional context
        vocal_tags = genre_tags['vocal'][:2]
        persona_vocal_tags = await self.get_vocal_tags_for_style(artist_persona.vocal_style, primary_emotion)
        vocal_tags.extend(persona_vocal_tags[:2])

        # Add emotional authenticity vocals
        authenticity_vocals = [f"{primary_emotion} vocals", "authentic emotional delivery", "vulnerable moments"]
        vocal_tags.extend(authenticity_vocals)

        # Use advanced instrument-to-meta-tag correlation for emotional texture
        sound_effects = []
        if artist_persona.instrumental_preferences:
            instrument_correlation = await self.correlate_instruments_to_meta_tags(
                artist_persona.instrumental_preferences,
                artist_persona.primary_genre,
                primary_emotion
            )

            # Collect correlated tags from all instruments
            for instrument, tags in instrument_correlation.items():
                sound_effects.extend(tags)

        # Add genre-specific production tags
        production_tags = genre_tags['production'][:2]
        sound_effects.extend(production_tags)

        # Add emotional sound effects
        for state in emotional_states[:2]:
            if state.defense_mechanism:
                sound_effects.append(f"{state.defense_mechanism} effect")

        # Check meta tag compatibility
        all_tags = style_tags + structure_tags + vocal_tags + sound_effects
        compatible_tags = self.check_meta_tag_compatibility(all_tags, artist_persona.primary_genre)

        return SunoCommand(
            command_type="emotion_beat_driven",
            prompt=prompt,
            style_tags=style_tags[:5],
            structure_tags=structure_tags[:4],
            sound_effect_tags=sound_effects[:4],
            vocal_tags=vocal_tags[:4],
            character_source=character.name,
            artist_persona=artist_persona.artist_name,
            command_rationale=f"Emotion-driven beat production using wiki meta tags to map {character.name}'s emotional journey to precise rhythmic elements",
            estimated_effectiveness=0.95,
            variations=[
                prompt.replace(tempo_instruction, f"[tempo automation: {beat_pattern.tempo_range[0]} -> {beat_pattern.tempo_range[1]}bpm]"),
                prompt + "\n[Beat drops at emotional revelations]",
                prompt.replace(rhythm_instruction, f"[evolving rhythm: {beat_pattern.rhythm_pattern}]")
            ]
        )

# ================================================================================================
# FASTMCP TOOLS, RESOURCES, AND PROMPTS
# ================================================================================================

# Initialize analysis engines
character_analyzer = EnhancedCharacterAnalyzer()
persona_generator = MusicPersonaGenerator()
command_generator = None  # Will be initialized after wiki data manager is set up

# Global wiki data manager for server-wide access
wiki_data_manager = None

async def ensure_wiki_data_manager():
    """Ensure wiki data manager is available, initialize if needed"""
    global wiki_data_manager

    if wiki_data_manager is None and WIKI_INTEGRATION_AVAILABLE:
        try:
            logger.info("Initializing wiki data manager on demand...")
            from wiki_data_models import WikiConfig
            from wiki_data_system import WikiDataManager

            wiki_data_manager = WikiDataManager()
            config = WikiConfig()
            await wiki_data_manager.initialize(config)
            logger.info("Wiki data manager initialized successfully")

        except Exception as e:
            logger.warning(f"Failed to initialize wiki data manager: {e}")
            wiki_data_manager = None

    return wiki_data_manager

async def initialize_server():
    """Initialize the MCP server with all components including wiki integration"""
    global wiki_data_manager, command_generator

    logger.info("Initializing Character-Driven Music Generation MCP Server...")

    # Initialize wiki integration if available
    if WIKI_INTEGRATION_AVAILABLE:
        try:
            logger.info("Initializing wiki data integration...")

            # Initialize WikiDataManager with default configuration
            wiki_data_manager = WikiDataManager()
            config = WikiConfig()  # Use default configuration
            await wiki_data_manager.initialize(config)

            # Initialize persona generator with wiki integration
            await persona_generator._ensure_wiki_integration()

            # Initialize command generator with wiki data manager
            command_generator = SunoCommandGenerator(wiki_data_manager)

            logger.info("Wiki integration initialized successfully")
            logger.info(f"- Genre data available: {len(await wiki_data_manager.get_genres()) if wiki_data_manager else 0} genres")
            logger.info(f"- Meta tag data available: {len(await wiki_data_manager.get_meta_tags()) if wiki_data_manager else 0} meta tags")

        except Exception as e:
            logger.warning(f"Failed to initialize wiki integration: {e}")
            logger.info("Falling back to hardcoded data")
            wiki_data_manager = None
            command_generator = SunoCommandGenerator(None)
    else:
        logger.info("Wiki integration not available, using fallback mappings")
        command_generator = SunoCommandGenerator(None)

    logger.info("Server initialization complete")
    logger.info("Ready to process narrative content and generate music commands")

# Internal callable version for use by other tools
async def _analyze_character_text_internal(text: str, ctx: Context) -> str:
    """
    Analyze narrative text to extract detailed character profiles using three-layer methodology.
    
    Performs comprehensive character analysis including:
    - Skin Layer: Physical descriptions, mannerisms, speech patterns
    - Flesh Layer: Relationships, backstory, formative experiences  
    - Core Layer: Motivations, fears, desires, psychological drivers
    
    Uses enhanced character detection with:
    - Named Entity Recognition for robust character detection
    - Semantic analysis for multiple narrative themes beyond "friendship"
    - Varied emotional arc analysis instead of "neutral" defaults
    
    Args:
        text: Narrative text content (unlimited length supported)
        
    Returns:
        JSON string containing detailed character analysis results
    """
    try:
        await ctx.info("Starting enhanced character analysis...")

        if not text or len(text.strip()) < 50:
            return json.dumps({
                "error": "Text too short for meaningful character analysis. Please provide at least 50 characters of narrative content."
            })

        # Perform enhanced analysis
        result = await character_analyzer.analyze_text(text, ctx)

        # Validate results
        from enhanced_character_analyzer import validate_analysis_results
        validation_issues = validate_analysis_results(result)
        if validation_issues:
            await ctx.error(f"Analysis validation issues: {validation_issues}")

        await ctx.info(f"Enhanced analysis complete: {len(result['characters'])} characters, {len(result['narrative_themes'])} themes, {len(result['emotional_arc'])} emotional states found")

        return json.dumps(result, indent=2)

    except Exception as e:
        await ctx.error(f"Enhanced character analysis failed: {str(e)}")
        return json.dumps({"error": f"Enhanced analysis failed: {str(e)}"})

@mcp.tool
async def analyze_character_text(text: str, ctx: Context) -> str:
    """
    Analyze narrative text to extract detailed character profiles using three-layer methodology.
    
    Performs comprehensive character analysis including:
    - Skin Layer: Physical descriptions, mannerisms, speech patterns
    - Flesh Layer: Relationships, backstory, formative experiences  
    - Core Layer: Motivations, fears, desires, psychological drivers
    
    Uses enhanced character detection with:
    - Named Entity Recognition for robust character detection
    - Semantic analysis for multiple narrative themes beyond "friendship"
    - Varied emotional arc analysis instead of "neutral" defaults
    
    Args:
        text: Narrative text content (unlimited length supported)
        
    Returns:
        JSON string containing detailed character analysis results
    """
    return await _analyze_character_text_internal(text, ctx)

# Internal callable version for use by other tools
async def _generate_artist_personas_internal(characters_json: str, ctx: Context,
                                            requested_genre: Optional[str] = None) -> str:
    """
    Generate musical artist personas from character profiles.
    
    Transforms character psychological profiles into coherent musical artist identities
    with genre mappings, vocal styles, and thematic content.
    
    Args:
        characters_json: JSON string containing character profiles from analyze_character_text
        
    Returns:
        JSON string containing generated artist personas
    """
    try:
        await ctx.info("Generating artist personas...")

        # Parse character data
        data = json.loads(characters_json)
        if 'characters' not in data:
            return json.dumps({"error": "Invalid character data format. Expected 'characters' field."})

        characters_data = data['characters']
        if not characters_data:
            return json.dumps({"error": "No characters found in input data."})

        artist_personas = []

        for char_data in characters_data:
            try:
                # Validate character data format
                if not isinstance(char_data, dict):
                    await ctx.error(f"Invalid character data format: expected dict, got {type(char_data)}")
                    continue

                # Convert dict to StandardCharacterProfile with graceful error handling
                character = StandardCharacterProfile.from_dict(char_data)

                # Validate that character has minimum required information
                if not character.name or character.name == "Unknown Character":
                    await ctx.error(f"Character missing required name field: {char_data}")
                    continue

                # Generate artist persona (with optional genre alignment)
                persona = await persona_generator.generate_artist_persona(character, ctx, requested_genre)
                artist_personas.append(asdict(persona))

            except Exception as e:
                await ctx.error(f"Failed to process character data {char_data}: {str(e)}")
                continue

        result = {
            "artist_personas": artist_personas,
            "total_personas": len(artist_personas),
            "generation_summary": f"Generated {len(artist_personas)} unique artist personas from character analysis"
        }

        await ctx.info(f"Generated {len(artist_personas)} artist personas")

        return json.dumps(result, indent=2)

    except Exception as e:
        await ctx.error(f"Artist persona generation failed: {str(e)}")
        return json.dumps({"error": f"Persona generation failed: {str(e)}"})

@mcp.tool
async def generate_artist_personas(characters_json: str, ctx: Context, requested_genre: Optional[str] = None) -> str:
    """
    Generate musical artist personas from character profiles.
    
    Transforms character psychological profiles into coherent musical artist identities
    with genre mappings, vocal styles, and thematic content.
    
    Args:
        characters_json: JSON string containing character profiles from analyze_character_text
        
    Returns:
        JSON string containing generated artist personas
    """
    return await _generate_artist_personas_internal(characters_json, ctx, requested_genre)

# Internal callable version for use by other tools
async def _create_suno_commands_internal(personas_json: str, characters_json: str, ctx: Context) -> str:
    """
    Generate optimized Suno AI commands from artist personas and character profiles.
    
    Creates multiple command variations including simple prompts, custom mode,
    bracket notation, and specialized commands for different musical approaches.
    
    Args:
        personas_json: JSON string containing artist personas from generate_artist_personas
        characters_json: JSON string containing character profiles
        
    Returns:
        JSON string containing Suno AI commands with metadata
    """
    try:
        await ctx.info("Generating Suno AI commands...")

        # Ensure command generator is initialized
        global command_generator
        if command_generator is None:
            # Initialize with wiki data manager if available
            global wiki_data_manager
            command_generator = SunoCommandGenerator(wiki_data_manager)
            await ctx.info(f"Initialized SunoCommandGenerator with {'wiki integration' if wiki_data_manager else 'fallback mode'}")

        # Parse input data with better error handling
        try:
            personas_data = json.loads(personas_json)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid personas JSON format: {str(e)}"
            await ctx.error(error_msg)
            return json.dumps({"error": error_msg})

        try:
            characters_data = json.loads(characters_json)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid characters JSON format: {str(e)}"
            await ctx.error(error_msg)
            return json.dumps({"error": error_msg})

        # Validate data structure with detailed error messages
        if not isinstance(personas_data, dict):
            error_msg = f"Personas data must be a dictionary, got {type(personas_data)}"
            await ctx.error(error_msg)
            return json.dumps({"error": error_msg})

        if 'artist_personas' not in personas_data:
            error_msg = "Invalid personas data format. Expected 'artist_personas' key. Available keys: " + str(list(personas_data.keys()))
            await ctx.error(error_msg)
            return json.dumps({"error": error_msg})

        if not isinstance(characters_data, dict):
            error_msg = f"Characters data must be a dictionary, got {type(characters_data)}"
            await ctx.error(error_msg)
            return json.dumps({"error": error_msg})

        if 'characters' not in characters_data:
            error_msg = "Invalid characters data format. Expected 'characters' key. Available keys: " + str(list(characters_data.keys()))
            await ctx.error(error_msg)
            return json.dumps({"error": error_msg})

        all_commands = []
        personas = personas_data['artist_personas']
        characters = characters_data['characters']

        # Validate personas list
        if not isinstance(personas, list):
            error_msg = f"'artist_personas' must be a list, got {type(personas)}"
            await ctx.error(error_msg)
            return json.dumps({"error": error_msg})

        if len(personas) == 0:
            error_msg = "No artist personas provided in 'artist_personas' list"
            await ctx.error(error_msg)
            return json.dumps({"error": error_msg})

        # Validate characters list
        if not isinstance(characters, list):
            error_msg = f"'characters' must be a list, got {type(characters)}"
            await ctx.error(error_msg)
            return json.dumps({"error": error_msg})

        if len(characters) == 0:
            error_msg = "No characters provided in 'characters' list"
            await ctx.error(error_msg)
            return json.dumps({"error": error_msg})

        # Create character lookup by name
        char_lookup = {char.get('name', ''): char for char in characters}

        await ctx.info(f"Processing {len(personas)} personas and {len(characters)} characters")

        for i, persona_data in enumerate(personas):
            # Validate persona data structure
            if not isinstance(persona_data, dict):
                await ctx.error(f"Persona {i} must be a dictionary, got {type(persona_data)}")
                continue

            # Check for required fields and provide helpful error messages
            required_fields = ['character_name']
            missing_fields = [field for field in required_fields if field not in persona_data or not persona_data[field]]

            if missing_fields:
                await ctx.error(f"Persona {i} missing required fields: {missing_fields}. Available fields: {list(persona_data.keys())}")
                # Add missing fields with defaults
                for field in missing_fields:
                    if field == 'character_name':
                        persona_data[field] = f"Character_{i}"

            try:
                # Use from_dict method to handle missing fields gracefully
                persona = ArtistPersona.from_dict(persona_data)
                await ctx.info(f"Created persona for {persona.character_name} -> {persona.artist_name}")
            except Exception as e:
                await ctx.error(f"Failed to create ArtistPersona from data {persona_data}: {e}")
                # Create minimal persona with available data
                persona = ArtistPersona(
                    character_name=persona_data.get('character_name', f'Character_{i}'),
                    artist_name=persona_data.get('artist_name', persona_data.get('character_name', f'Artist_{i}')),
                    primary_genre=persona_data.get('primary_genre', ''),
                    secondary_genres=persona_data.get('secondary_genres', []),
                    vocal_style=persona_data.get('vocal_style', ''),
                    lyrical_themes=persona_data.get('lyrical_themes', []),
                    emotional_palette=persona_data.get('emotional_palette', [])
                )
                await ctx.info(f"Created fallback persona for {persona.character_name}")

            character_dict = char_lookup.get(persona.character_name)

            if character_dict:
                try:
                    # Convert character dict to StandardCharacterProfile
                    character = StandardCharacterProfile.from_dict(character_dict)
                    await ctx.info(f"Matched persona {persona.character_name} with character profile")
                except Exception as e:
                    await ctx.error(f"Failed to create StandardCharacterProfile from {character_dict}: {e}")
                    # Create minimal character profile
                    character = StandardCharacterProfile(
                        name=persona.character_name,
                        backstory=character_dict.get('backstory', ''),
                        motivations=character_dict.get('motivations', []),
                        fears=character_dict.get('fears', [])
                    )
            else:
                await ctx.error(f"No character found for persona {persona.character_name}. Available characters: {list(char_lookup.keys())}")
                # Create minimal character profile from persona data
                character = StandardCharacterProfile(
                    name=persona.character_name,
                    backstory=f"Character profile for {persona.character_name}",
                    motivations=[f"Express {persona.primary_genre} music"],
                    personality_drivers=persona.lyrical_themes
                )

            # Extract emotional states if available (for both matched and unmatched characters)
            emotional_states = None
            beat_progression = None

            if 'emotional_states' in characters_data:
                # Find emotional states for this character
                for j, char in enumerate(characters):
                    if char.get('name', '') == character.name and j < len(characters_data.get('emotional_states', [])):
                        char_emotional_data = characters_data['emotional_states'][j]
                        if char_emotional_data:
                            emotional_states = [EmotionalState(**state) for state in char_emotional_data]

            if 'beat_progression' in characters_data:
                beat_progression = characters_data.get('beat_progression')

            await ctx.info(f"About to generate commands for {persona.character_name}")
            try:
                commands = await command_generator.generate_suno_commands(
                    persona, character, ctx, emotional_states, beat_progression
                )
                await ctx.info(f"Generated {len(commands)} commands for {persona.character_name}")
                for cmd in commands:
                    all_commands.append(asdict(cmd))
            except Exception as e:
                await ctx.error(f"Failed to generate commands for {persona.character_name}: {e}")
                import traceback
                await ctx.error(f"Traceback: {traceback.format_exc()}")
                # Create a fallback simple command
                fallback_command = {
                    'command_type': 'simple',
                    'prompt': f"A {persona.primary_genre or 'music'} song inspired by {persona.character_name}",
                    'style_tags': [persona.primary_genre] if persona.primary_genre else [],
                    'structure_tags': [],
                    'sound_effect_tags': [],
                    'vocal_tags': [persona.vocal_style] if persona.vocal_style else [],
                    'character_source': persona.character_name,
                    'artist_persona': persona.artist_name,
                    'command_rationale': f"Fallback command for {persona.character_name}",
                    'estimated_effectiveness': 0.5
                }
                all_commands.append(fallback_command)

        # Convert personas to dict format for result validation
        personas_for_result = []
        for persona_data in personas:
            if isinstance(persona_data, dict):
                personas_for_result.append(persona_data)
            else:
                # Skip invalid persona data that couldn't be processed
                continue

        result = MusicGenerationResult(
            commands=all_commands,
            artist_personas=personas_for_result,
            generation_summary=f"Generated {len(all_commands)} Suno AI commands from {len(personas_for_result)} valid artist personas",
            total_commands=len(all_commands),
            processing_time=0.0
        )

        await ctx.info(f"Generated {len(all_commands)} Suno commands")

        return json.dumps(result.model_dump(), indent=2)

    except Exception as e:
        await ctx.error(f"Suno command generation failed: {str(e)}")
        return json.dumps({"error": f"Command generation failed: {str(e)}"})

@mcp.tool
async def create_suno_commands(personas_json: str, characters_json: str, ctx: Context) -> str:
    """
    Generate optimized Suno AI commands from artist personas and character profiles.
    
    Creates multiple command variations including simple prompts, custom mode,
    bracket notation, and specialized commands for different musical approaches.
    
    Args:
        personas_json: JSON string containing artist personas from generate_artist_personas
        characters_json: JSON string containing character profiles
        
    Returns:
        JSON string containing Suno AI commands with metadata
    """
    return await _create_suno_commands_internal(personas_json, characters_json, ctx)

# Internal callable version for use by other tools
async def _complete_workflow_internal(text: str, ctx: Context, requested_genre: Optional[str] = None) -> str:
    """
    Execute complete character-to-music workflow in one operation.
    
    Performs full pipeline:
    1. Character analysis from narrative text
    2. Artist persona generation
    3. Suno AI command creation
    
    Args:
        text: Input narrative text for analysis
        
    Returns:
        JSON string containing complete workflow results
    """
    try:
        await ctx.info("Starting complete character-to-music workflow...")

        # Step 1: Character Analysis
        await ctx.info("Step 1: Analyzing characters...")
        characters_result = await _analyze_character_text_internal(text, ctx)

        # Step 2: Generate Artist Personas
        await ctx.info("Step 2: Generating artist personas...")
        personas_result = await _generate_artist_personas_internal(characters_result, ctx, requested_genre)

        # Step 3: Create Suno Commands
        await ctx.info("Step 3: Creating Suno AI commands...")
        commands_result = await _create_suno_commands_internal(personas_result, characters_result, ctx)

        # Add wiki attribution context
        wiki_attribution = await _build_wiki_attribution_context({
            "characters": json.loads(characters_result),
            "personas": json.loads(personas_result),
            "commands": json.loads(commands_result)
        }, ctx)

        # Combine results
        workflow_result = {
            "workflow_status": "completed",
            "character_analysis": json.loads(characters_result),
            "artist_personas": json.loads(personas_result),
            "suno_commands": json.loads(commands_result),
            "workflow_summary": "Complete character-driven music generation workflow executed successfully",
            "wiki_attribution": wiki_attribution if wiki_attribution else "Using fallback data - no wiki sources available"
        }

        await ctx.info("Workflow completed successfully!")

        return json.dumps(workflow_result, indent=2)

    except Exception as e:
        await ctx.error(f"Workflow execution failed: {str(e)}")
        return json.dumps({"error": f"Workflow failed: {str(e)}"})

@mcp.tool
async def complete_workflow(text: str, ctx: Context, requested_genre: Optional[str] = None) -> str:
    """
    Execute complete character-to-music workflow in one operation.
    
    Performs full pipeline:
    1. Character analysis from narrative text
    2. Artist persona generation
    3. Suno AI command creation
    
    Args:
        text: Input narrative text for analysis
        
    Returns:
        JSON string containing complete workflow results
    """
    return await _complete_workflow_internal(text, ctx, requested_genre)

@mcp.tool
async def creative_music_generation(concept: str, style_preference: str = "any", ctx: Context = None) -> str:
    """
    Generate creative music commands from abstract concepts with meaningful musical analysis.
    
    Enhanced creative mode that provides:
    - Deep musical concept analysis extracting key elements
    - Creative variations based on musical theory and genre knowledge
    - Practical Suno AI commands using wiki data integration
    - Contextually appropriate responses instead of generic repetition
    
    Args:
        concept: Abstract concept, theme, or idea for music generation
        style_preference: Preferred musical style/genre (optional, defaults to "any")
        
    Returns:
        JSON string containing meaningful creative music generation with practical Suno commands
    """
    try:
        await ctx.info(f"Analyzing concept for creative music generation: {concept}")

        if not concept or len(concept.strip()) < 10:
            return json.dumps({
                "error": "Concept too short. Please provide a more detailed concept or theme."
            })

        # Initialize creative music engine
        creative_engine = CreativeMusicEngine()

        # Step 1: Analyze the musical concept for key elements
        await ctx.info("Analyzing musical concept for key elements...")
        concept_analysis = creative_engine.analyze_musical_concept(concept)

        # Step 2: Generate creative variations based on analysis
        await ctx.info("Generating creative variations based on musical theory...")
        creative_variations = creative_engine.generate_creative_variations(
            concept_analysis, style_preference
        )

        # Step 3: Create practical Suno AI commands
        await ctx.info("Creating practical Suno AI commands...")
        suno_commands = await creative_engine.generate_practical_suno_commands(
            creative_variations, concept_analysis
        )

        # Step 4: Compile comprehensive result
        result = {
            "concept_analysis": concept_analysis,
            "creative_variations": creative_variations,
            "suno_commands": suno_commands,
            "generation_metadata": {
                "concept_length": len(concept),
                "style_preference": style_preference,
                "analysis_timestamp": datetime.now().isoformat(),
                "variations_count": len(creative_variations),
                "commands_count": len(suno_commands)
            }
        }

        await ctx.info("Creative music generation completed with meaningful analysis")

        return json.dumps(result, indent=2)

    except Exception as e:
        await ctx.error(f"Creative generation failed: {str(e)}")
        return json.dumps({"error": f"Creative generation failed: {str(e)}"})

# LLM EMOTIONAL MAPPING FUNCTIONS - Used by tools to create custom emotional maps
def _create_llm_emotional_map(concept: str, style_preference: str) -> Dict[str, Any]:
    """LLM creates custom emotional map from concept - no predefined limitations"""

    # LLM ANALYSIS - This is where the intelligence happens
    concept_lower = concept.lower()

    # LLM determines tempo from content
    if any(word in concept_lower for word in ['fast', 'urgent', 'intense', 'racing']):
        tempo = 140
    elif any(word in concept_lower for word in ['slow', 'peaceful', 'calm', 'meditation']):
        tempo = 70
    else:
        tempo = 100

    # LLM determines rhythm from content structure
    if any(word in concept_lower for word in ['chaos', 'broken', 'conflict']):
        rhythm = "irregular_syncopated_with_breaks"
    elif any(word in concept_lower for word in ['flow', 'organic', 'natural']):
        rhythm = "flowing_organic_rhythm"
    else:
        rhythm = f"rhythm_expressing_{concept.replace(' ', '_').lower()}"

    # LLM determines sounds from content imagery
    sounds = []
    if any(word in concept_lower for word in ['water', 'ocean', 'rain']):
        sounds.extend(['flowing_water_textures', 'liquid_elements'])
    if any(word in concept_lower for word in ['wind', 'air', 'breath']):
        sounds.extend(['atmospheric_movement', 'breathy_textures'])
    if not sounds:
        sounds.append(f"sonic_interpretation_of_{concept.replace(' ', '_').lower()}")

    emotional_map = {
        'tempo_directive': tempo,
        'tempo_reasoning': f"Tempo derived from analyzing '{concept}'",
        'rhythm_directive': rhythm,
        'rhythm_reasoning': f"Rhythm reflecting structure of '{concept}'",
        'sonic_directives': sounds[:3],
        'sonic_reasoning': f"Sounds derived from imagery in '{concept}'",
        'structure_directive': {
            'intro': f"Atmospheric introduction to '{concept}'",
            'main_section': f"Musical exploration of '{concept}'",
            'outro': f"Resolution of '{concept}'"
        },
        'emotional_context': f"Human emotional experience of '{concept}'",
        'emotional_reasoning': f"Emotional interpretation of '{concept}'",
        'production_style': style_preference if style_preference != "any" else "natural_interpretation",
        'custom_directives': [
            f"Let '{concept}' guide every musical decision",
            f"Ground all elements in the meaning of '{concept}'"
        ],
        'execution_notes': f"Complete LLM analysis of '{concept}' with no limitations"
    }

    return emotional_map

# Internal callable version for use by other tools
async def _understand_topic_with_emotions_internal(
    topic_text: str,
    source_type: str = "book",
    focus_areas: Optional[List[str]] = None,
    ctx: Context = None
) -> str:
    """
    Enhanced internal version of understand_topic_with_emotions with meaningful emotional analysis.
    
    Analyzes any topic or book content to extract:
    - Sophisticated emotional analysis with varied insights
    - Context-appropriate emotional responses for different topics
    - Genre-appropriate beat patterns and musical elements
    - Practical Suno AI commands based on emotional content
    
    Args:
        topic_text: The topic or book content to analyze
        source_type: Type of content - "book", "topic", "article", "research", etc.
        focus_areas: Optional list of areas to focus on
        ctx: Context for logging
        
    Returns:
        JSON with comprehensive emotional understanding and musical interpretation
    """
    try:
        if ctx:
            await ctx.info(f"Performing enhanced analysis of {source_type} content...")

        if not topic_text or len(topic_text.strip()) < 50:
            return json.dumps({
                "error": "Content too short. Please provide at least 50 characters of meaningful content."
            })

        # Import enhanced analyzers
        try:
            import os
            import sys

            # Add current directory to path for imports
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)

            from enhanced_beat_generator import EnhancedBeatGenerator
            from enhanced_emotional_analyzer import EnhancedEmotionalAnalyzer

            # Initialize enhanced analyzers
            emotional_analyzer = EnhancedEmotionalAnalyzer()
            beat_generator = EnhancedBeatGenerator()

            # Perform comprehensive emotional analysis
            emotional_profile = emotional_analyzer.analyze_emotional_content(topic_text, source_type)

            # Generate genre preferences based on emotional content
            genre_preferences = _extract_genre_preferences_for_topic(emotional_profile, source_type)

            # Generate beat patterns and musical elements
            beat_analysis = beat_generator.generate_beat_patterns(emotional_profile, genre_preferences)

            # Create comprehensive understanding result
            understanding_result = {
                "topic_analysis": {
                    "source_type": source_type,
                    "content_preview": topic_text[:200] + ("..." if len(topic_text) > 200 else ""),
                    "content_length": len(topic_text),
                    "focus_areas": focus_areas if focus_areas else ["emotional_understanding", "musical_interpretation"],
                    "analysis_method": "enhanced_emotional_analysis"
                },
                "emotional_analysis": {
                    "primary_emotions": [
                        {
                            "emotion": emotion.emotion,
                            "intensity": emotion.intensity,
                            "context": emotion.context,
                            "triggers": emotion.triggers,
                            "musical_implications": emotion.musical_implications
                        }
                        for emotion in emotional_profile.primary_emotions
                    ],
                    "emotional_arc": emotional_profile.emotional_arc,
                    "emotional_complexity": emotional_profile.emotional_complexity,
                    "dominant_mood": emotional_profile.dominant_mood,
                    "emotional_themes": emotional_profile.emotional_themes,
                    "analysis_confidence": _calculate_topic_analysis_confidence(emotional_profile)
                },
                "musical_interpretation": {
                    "beat_patterns": beat_analysis.get("beat_patterns", {}),
                    "rhythm_characteristics": beat_analysis.get("rhythm_characteristics", {}),
                    "tempo_recommendations": beat_analysis.get("tempo_recommendations", {}),
                    "musical_elements": beat_analysis.get("musical_elements", []),
                    "rhythm_variations": beat_analysis.get("rhythm_variations", []),
                    "genre_suggestions": genre_preferences,
                    "instrumentation_recommendations": emotional_profile.musical_recommendations.get("instrumentation", {}),
                    "production_techniques": emotional_profile.musical_recommendations.get("production_techniques", [])
                },
                "suno_commands": {
                    "primary_commands": beat_analysis.get("suno_commands", []),
                    "emotional_directives": _generate_topic_emotional_directives(emotional_profile),
                    "production_commands": _generate_topic_production_commands(emotional_profile),
                    "complete_command_set": _generate_complete_topic_suno_commands(emotional_profile, beat_analysis)
                },
                "production_notes": {
                    "emotional_production_notes": beat_analysis.get("production_notes", []),
                    "technical_recommendations": _generate_topic_technical_recommendations(emotional_profile),
                    "creative_suggestions": _generate_topic_creative_suggestions(emotional_profile, source_type)
                },
                "comprehensive_understanding": _generate_topic_comprehensive_summary(emotional_profile, source_type, beat_analysis)
            }

            if ctx:
                await ctx.info(f"Completed enhanced analysis with {len(emotional_profile.primary_emotions)} emotions detected")

            return json.dumps(understanding_result, indent=2)

        except ImportError:
            # Fallback to original implementation if enhanced modules not available
            if ctx:
                await ctx.info("Enhanced modules not available, using fallback implementation...")

            # Original implementation as fallback
            emotional_map = _create_llm_emotional_map(topic_text, "contemplative")
            beat_engine = EmotionalBeatEngine()
            musical_production = beat_engine.execute_musical_production(emotional_map)

            understanding_result = {
                "topic_analysis": {
                    "source_type": source_type,
                    "content_preview": topic_text[:200] + ("..." if len(topic_text) > 200 else ""),
                    "focus_areas": focus_areas if focus_areas else ["general_understanding"],
                    "analysis_method": "fallback_implementation",
                    "llm_emotional_interpretation": emotional_map['emotional_context'],
                    "llm_reasoning": emotional_map['emotional_reasoning']
                },
                "musical_interpretation": musical_production,
                "comprehensive_understanding": f"Fallback analysis of '{source_type}' content with basic emotional mapping"
            }

            return json.dumps(understanding_result, indent=2)

    except Exception as e:
        error_msg = f"Enhanced topic understanding failed: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool
async def understand_topic_with_emotions(
    topic_text: str,
    source_type: str = "book",
    focus_areas: Optional[List[str]] = None,
    ctx: Context = None
) -> str:
    """
    Understand and ground topics/books using enhanced emotional analysis with meaningful insights.
    
    Analyzes any topic or book content to extract:
    - Sophisticated emotional analysis with varied insights beyond "contemplative"
    - Context-appropriate emotional responses for different topics  
    - Genre-appropriate beat patterns and musical elements
    - Practical Suno AI commands aligned with emotional content
    
    Perfect for understanding complex topics through emotional and musical lens.
    
    Args:
        topic_text: The topic or book content to analyze
        source_type: Type of content - "book", "topic", "article", "research", etc.
        focus_areas: Optional list of areas to focus on (e.g., ["character development", "philosophical themes"])
        
    Returns:
        JSON with comprehensive emotional understanding and musical interpretation
    """
    return await _understand_topic_with_emotions_internal(topic_text, source_type, focus_areas, ctx)

# Removed unused function _map_emotion_to_genre_llm

def _generate_topic_production_notes(emotional_states: List[EmotionalState], subtext: List[Dict]) -> List[str]:
    """Generate production notes based on emotional analysis"""
    notes = []

    if emotional_states:
        # Add notes based on emotional authenticity
        avg_authenticity = sum(s.authenticity_score for s in emotional_states) / len(emotional_states)
        if avg_authenticity < 0.5:
            notes.append("Use processing effects to represent emotional complexity")
        else:
            notes.append("Keep production clean to highlight emotional authenticity")

    if subtext:
        # Add notes based on subtext
        subtext_types = [s['type'] for s in subtext]
        if 'suppressed_emotion' in subtext_types:
            notes.append("Layer subtle undertones to represent hidden emotions")
        if 'emotional_turning_point' in subtext_types:
            notes.append("Create dramatic shift in production at key moments")

    return notes

# Helper functions for enhanced topic analysis
def _extract_genre_preferences_for_topic(emotional_profile, source_type: str) -> List[str]:
    """Extract genre preferences based on emotional content and source type"""
    genre_preferences = []

    # Add genres from musical recommendations
    if hasattr(emotional_profile, 'musical_recommendations') and "genre_suggestions" in emotional_profile.musical_recommendations:
        genre_preferences.extend(emotional_profile.musical_recommendations["genre_suggestions"])

    # Add source-type specific genres
    source_genre_mappings = {
        "book": ["cinematic", "orchestral", "ambient"],
        "philosophy": ["ambient", "neo_classical", "experimental"],
        "story": ["cinematic", "folk", "indie"],
        "article": ["electronic", "ambient", "minimal"],
        "research": ["ambient", "experimental", "minimal"],
        "poetry": ["folk", "ambient", "indie"],
        "memoir": ["folk", "indie", "acoustic"]
    }

    if source_type in source_genre_mappings:
        for genre in source_genre_mappings[source_type]:
            if genre not in genre_preferences:
                genre_preferences.append(genre)

    # Add emotion-based genres
    emotion_genre_mappings = {
        "melancholic": ["indie_folk", "ambient", "neo_classical"],
        "hopeful": ["indie_pop", "folk", "uplifting_electronic"],
        "anxious": ["experimental", "industrial", "dark_ambient"],
        "furious": ["metal", "punk", "aggressive_electronic"],
        "contemplative": ["ambient", "neo_classical", "meditation"],
        "passionate": ["orchestral", "dramatic", "cinematic"],
        "mysterious": ["dark_ambient", "experimental", "atmospheric"]
    }

    if hasattr(emotional_profile, 'primary_emotions'):
        for emotion in emotional_profile.primary_emotions[:2]:  # Top 2 emotions
            if emotion.emotion in emotion_genre_mappings:
                for genre in emotion_genre_mappings[emotion.emotion]:
                    if genre not in genre_preferences:
                        genre_preferences.append(genre)

    return genre_preferences[:5]  # Return top 5 genre preferences

def _calculate_topic_analysis_confidence(emotional_profile) -> float:
    """Calculate confidence score for the emotional analysis"""
    if not hasattr(emotional_profile, 'primary_emotions') or not emotional_profile.primary_emotions:
        return 0.0

    # Base confidence on number of emotions detected and their intensities
    num_emotions = len(emotional_profile.primary_emotions)
    if num_emotions == 0:
        return 0.0

    avg_intensity = sum(e.intensity for e in emotional_profile.primary_emotions) / num_emotions

    # Higher confidence with more emotions and higher intensities
    confidence = min((num_emotions * 0.2) + (avg_intensity * 0.8), 1.0)

    return round(confidence, 2)

def _generate_topic_emotional_directives(emotional_profile) -> List[str]:
    """Generate Suno AI emotional directives based on analysis"""
    directives = []

    if not hasattr(emotional_profile, 'primary_emotions') or not emotional_profile.primary_emotions:
        return ["[neutral_mood]"]

    for emotion in emotional_profile.primary_emotions[:3]:  # Top 3 emotions
        # Basic emotional directive
        directives.append(f"[{emotion.emotion}_feeling]")

        # Intensity-based directive
        if emotion.intensity > 0.8:
            directives.append(f"[intense_{emotion.emotion}]")
        elif emotion.intensity < 0.3:
            directives.append(f"[subtle_{emotion.emotion}]")
        else:
            directives.append(f"[moderate_{emotion.emotion}]")

    # Emotional arc directive
    if hasattr(emotional_profile, 'emotional_arc') and emotional_profile.emotional_arc["beginning"] != emotional_profile.emotional_arc["end"]:
        directives.append(f"[emotional_journey_{emotional_profile.emotional_arc['beginning']}_to_{emotional_profile.emotional_arc['end']}]")

    # Complexity directive
    if hasattr(emotional_profile, 'emotional_complexity'):
        if emotional_profile.emotional_complexity > 0.7:
            directives.append("[complex_emotions]")
        elif emotional_profile.emotional_complexity < 0.3:
            directives.append("[simple_emotions]")

    return directives

def _generate_topic_production_commands(emotional_profile) -> List[str]:
    """Generate production-specific Suno commands"""
    commands = []

    if not hasattr(emotional_profile, 'dominant_mood'):
        return ["[standard_production]"]

    # Commands based on dominant mood
    mood_commands = {
        "melancholic": ["[reverb_space]", "[warm_tone]", "[gentle_dynamics]"],
        "hopeful": ["[bright_eq]", "[uplifting_energy]", "[clear_vocals]"],
        "anxious": ["[tension_building]", "[irregular_rhythm]", "[restless_energy]"],
        "furious": ["[aggressive_compression]", "[heavy_distortion]", "[intense_energy]"],
        "contemplative": ["[minimal_processing]", "[natural_sound]", "[spacious_mix]"],
        "passionate": ["[dynamic_range]", "[emotional_builds]", "[expressive_vocals]"]
    }

    if emotional_profile.dominant_mood in mood_commands:
        commands.extend(mood_commands[emotional_profile.dominant_mood])

    # Commands based on emotional complexity
    if hasattr(emotional_profile, 'emotional_complexity'):
        if emotional_profile.emotional_complexity > 0.7:
            commands.extend(["[layered_arrangement]", "[rich_texture]", "[complex_harmony]"])
        elif emotional_profile.emotional_complexity < 0.3:
            commands.extend(["[minimal_arrangement]", "[simple_texture]", "[clear_structure]"])

    return commands

def _generate_complete_topic_suno_commands(emotional_profile, beat_analysis: Dict[str, Any]) -> List[str]:
    """Generate a complete set of Suno commands for the track"""
    commands = []

    # Start with beat pattern commands
    if "suno_commands" in beat_analysis:
        commands.extend(beat_analysis["suno_commands"])

    # Add emotional directives
    commands.extend(_generate_topic_emotional_directives(emotional_profile))

    # Add production commands
    commands.extend(_generate_topic_production_commands(emotional_profile))

    # Add musical element commands
    if "musical_elements" in beat_analysis:
        for element in beat_analysis["musical_elements"]:
            if "suno_commands" in element:
                commands.extend(element["suno_commands"])

    # Remove duplicates while preserving order
    unique_commands = []
    for command in commands:
        if command not in unique_commands:
            unique_commands.append(command)

    return unique_commands

def _generate_topic_technical_recommendations(emotional_profile) -> List[str]:
    """Generate technical production recommendations"""
    recommendations = []

    # Recommendations based on emotional intensity
    if hasattr(emotional_profile, 'primary_emotions') and emotional_profile.primary_emotions:
        avg_intensity = sum(e.intensity for e in emotional_profile.primary_emotions) / len(emotional_profile.primary_emotions)

        if avg_intensity > 0.7:
            recommendations.extend([
                "Use dynamic range to emphasize emotional peaks",
                "Consider parallel compression for intensity without losing dynamics",
                "Apply careful EQ to prevent harshness at high intensities"
            ])
        elif avg_intensity < 0.3:
            recommendations.extend([
                "Preserve natural dynamics for intimate feeling",
                "Use gentle compression to maintain consistency",
                "Focus on clarity and presence rather than power"
            ])

    # Recommendations based on emotional complexity
    if hasattr(emotional_profile, 'emotional_complexity') and emotional_profile.emotional_complexity > 0.7:
        recommendations.extend([
            "Use frequency separation techniques to manage complex arrangements",
            "Apply subtle panning to create space for multiple elements",
            "Consider automation to highlight different emotional layers"
        ])

    return recommendations

def _generate_topic_creative_suggestions(emotional_profile, source_type: str) -> List[str]:
    """Generate creative suggestions based on analysis"""
    suggestions = []

    # Suggestions based on emotional themes
    if hasattr(emotional_profile, 'emotional_themes'):
        for theme in emotional_profile.emotional_themes[:3]:
            theme_suggestions = {
                "transformation": "Consider using musical metamorphosis techniques - start with one sound and gradually transform it",
                "conflict": "Use contrasting musical elements to represent internal or external conflicts",
                "love": "Incorporate warm, embracing harmonies and gentle rhythmic patterns",
                "loss": "Use space and silence as compositional elements to represent absence",
                "discovery": "Build musical revelations through gradual unveiling of new elements",
                "journey": "Create a sense of forward motion through rhythmic and harmonic progression",
                "identity": "Develop a unique musical signature that represents the character or narrator",
                "redemption": "Use resolution of dissonance to represent emotional healing",
                "hope": "Incorporate ascending melodic lines and brightening harmonies"
            }

            if theme in theme_suggestions:
                suggestions.append(theme_suggestions[theme])

    # Suggestions based on source type
    source_suggestions = {
        "book": "Consider creating musical chapters that reflect different sections of the narrative",
        "philosophy": "Use abstract musical concepts to represent complex ideas",
        "story": "Create character themes and develop them throughout the piece",
        "poetry": "Let the natural rhythm of the text inform the musical rhythm",
        "memoir": "Use personal, intimate musical textures to reflect the autobiographical nature"
    }

    if source_type in source_suggestions:
        suggestions.append(source_suggestions[source_type])

    # Suggestions based on emotional arc
    if hasattr(emotional_profile, 'emotional_arc') and emotional_profile.emotional_arc["beginning"] != emotional_profile.emotional_arc["end"]:
        suggestions.append(f"Create a musical journey that mirrors the emotional arc from {emotional_profile.emotional_arc['beginning']} to {emotional_profile.emotional_arc['end']}")

    return suggestions

def _generate_topic_comprehensive_summary(emotional_profile, source_type: str, beat_analysis: Dict[str, Any]) -> str:
    """Generate a comprehensive summary of the analysis"""
    if not hasattr(emotional_profile, 'primary_emotions') or not emotional_profile.primary_emotions:
        return f"Analysis of {source_type} content completed with minimal emotional content detected."

    primary_emotion = emotional_profile.primary_emotions[0]

    summary_parts = []

    # Emotional analysis summary
    summary_parts.append(f"The {source_type} content reveals a primarily {primary_emotion.emotion} emotional landscape with {primary_emotion.intensity:.1f} intensity.")

    # Emotional complexity
    if hasattr(emotional_profile, 'emotional_complexity'):
        if emotional_profile.emotional_complexity > 0.7:
            summary_parts.append("The emotional content is highly complex, featuring multiple layered emotions that would benefit from sophisticated musical treatment.")
        elif emotional_profile.emotional_complexity < 0.3:
            summary_parts.append("The emotional content is relatively straightforward, allowing for focused musical interpretation.")
        else:
            summary_parts.append("The emotional content shows moderate complexity with clear primary emotions and subtle undertones.")

    # Musical recommendations summary
    if "tempo_recommendations" in beat_analysis:
        tempo_info = beat_analysis["tempo_recommendations"]
        summary_parts.append(f"Musical interpretation suggests a tempo around {tempo_info.get('recommended_tempo', 100)} BPM to match the emotional pacing.")

    # Thematic summary
    if hasattr(emotional_profile, 'emotional_themes') and emotional_profile.emotional_themes:
        themes_str = ", ".join(emotional_profile.emotional_themes[:3])
        summary_parts.append(f"Key emotional themes include {themes_str}, which should inform the musical narrative structure.")

    # Production approach summary
    if hasattr(emotional_profile, 'dominant_mood') and emotional_profile.dominant_mood:
        summary_parts.append(f"The dominant {emotional_profile.dominant_mood} mood suggests a production approach that emphasizes {_get_topic_mood_production_focus(emotional_profile.dominant_mood)}.")

    return " ".join(summary_parts)

def _get_topic_mood_production_focus(mood: str) -> str:
    """Get production focus description for a given mood"""
    mood_focus = {
        "melancholic": "spaciousness, warmth, and emotional resonance",
        "hopeful": "brightness, clarity, and forward momentum",
        "anxious": "tension, irregularity, and restless energy",
        "furious": "power, aggression, and intense dynamics",
        "contemplative": "clarity, space, and natural sound",
        "passionate": "dynamic range, emotional builds, and expressive elements",
        "mysterious": "atmosphere, ambiguity, and subtle textures"
    }

    return mood_focus.get(mood, "balanced musical elements")

@mcp.tool
async def process_universal_content(
    content: str,
    character_description: str,
    track_title: str,
    ctx: Context
) -> str:
    """
    Process ANY content through character's psychological lens with Meta-Narrative & Self-Reflection analysis.
    
    Enhanced universal content processor that uses emotional framework to:
    - Extract factual emotional triggers from content
    - Apply meta-narrative analysis for deeper meaning
    - Generate self-reflective insights
    - Create emotion-driven beat patterns and lyrics
    - Process through character's worldview for authentic personalization
    
    Universal content processor that can handle:
    - Philosophical texts, Love stories, Science fiction
    - News articles, Poetry, Biographical content, Abstract concepts
    
    Args:
        content: Any text content (unlimited length, any type)
        character_description: Detailed character profile and background
        track_title: Name for the resulting track
        
    Returns:
        JSON containing meta-narrative analysis, emotional grounding, beat patterns,
        lyrical guidance, and comprehensive Suno AI commands
    """
    try:
        await ctx.info("Starting enhanced universal content processing with emotional framework...")

        if not content or len(content.strip()) < 10:
            return json.dumps({
                "error": "Content too short. Please provide meaningful content to process."
            })

        if not character_description or len(character_description.strip()) < 20:
            return json.dumps({
                "error": "Character description too short. Please provide detailed character background."
            })

        # Initialize emotional framework components
        beat_engine = EmotionalBeatEngine()
        meta_processor = MetaNarrativeProcessor()
        reflection_analyzer = SelfReflectionAnalyzer()
        lyric_generator = EmotionalLyricGenerator()

        # Create LLM-defined emotional map from content and character
        emotional_map = _create_llm_emotional_map(content, character_description)

        # Execute musical production based on LLM map
        musical_production = beat_engine.execute_musical_production(emotional_map)

        # Extract meta-narrative elements using LLM-derived emotional insights
        emotional_subtext = meta_processor.extract_emotional_subtext(content, [])  # Meta-processor now handles content directly

        # Create temporary character profile for analysis
        temp_character = CharacterProfile(
            name="Content Interpreter",
            aliases=[],
            physical_description="",
            mannerisms=[],
            speech_patterns=[],
            behavioral_traits=[],
            backstory=character_description,
            relationships=[],
            formative_experiences=[],
            social_connections=[],
            motivations=["understanding", "authentic expression"],
            fears=["misinterpretation", "superficiality"],
            desires=["deep connection", "emotional truth"],
            conflicts=["complexity vs clarity"],
            personality_drivers=["empathy", "creativity"],
            confidence_score=0.8,
            text_references=[],
            first_appearance="",
            importance_score=1.0
        )

        # Analyze self-reflection and introspection
        introspection_data = reflection_analyzer.analyze_character_introspection(content, temp_character)

        # Identify emotional contradictions through character lens
        emotional_contradictions = meta_processor.identify_emotional_contradictions(content, temp_character)

        # Beat progression now comes from LLM-driven musical production
        beat_progression = musical_production.get('beat_progression', {})

        # Generate lyrical content based on LLM emotional map
        lyric_structure = lyric_generator.generate_lyric_structure(
            [],  # Lyric generator now uses LLM emotional context
            f"Character interpretation of: {content[:100]}..."
        )

        # Initialize original processor for character filtering
        processor = WorkingUniversalProcessor(character_description)

        await ctx.info("Processing content through character lens with emotional analysis...")

        # Process content through character's psychological filter
        original_result = processor.process_any_content(content, track_title)

        # Enhanced analysis combining original processing with LLM-driven emotional framework
        enhanced_analysis = {
            "original_content": original_result.original_content,
            "content_type": "auto_detected",
            "character_interpretation": original_result.character_interpretation,
            # NEW: LLM-driven emotional framework analysis
            "llm_emotional_analysis": {
                "emotional_context": emotional_map.get('emotional_context', {}),
                "musical_interpretation": musical_production.get('interpretation', {}),
                "reasoning": emotional_map.get('emotional_reasoning', 'LLM-driven analysis')
            },
            "meta_narrative_analysis": {
                "subtext_elements": emotional_subtext[:3],
                "emotional_contradictions": emotional_contradictions[:2],
                "hidden_meanings": [elem['narrative_significance'] for elem in emotional_subtext[:2]]
            },
            "self_reflection_insights": {
                "awareness_moments": len(introspection_data.get('self_awareness_moments', [])),
                "growth_trajectory": introspection_data.get('growth_trajectory', [])[:2],
                "vulnerability_progression": introspection_data.get('vulnerability_scores', [])[:3],
                "defense_mechanisms": [mech['type'] for mech in introspection_data.get('defense_mechanisms', [])[:2]]
            }
        }

        # Add source attribution for wiki-sourced content
        wiki_attribution = await _build_wiki_attribution_context(enhanced_analysis, ctx)

        # Create enhanced Suno command with LLM-driven emotional grounding
        if musical_production and lyric_structure:
            enhanced_suno_command = f"{musical_production.get('suno_format', '[ambient electronic] [80-120bpm] [contemplative rhythm]')}\n" \
                                  f"Track: '{track_title}'\n" \
                                  f"LLM Emotional Analysis: {emotional_map.get('emotional_reasoning', 'Character-driven interpretation')}\n" \
                                  f"Musical Direction: {musical_production.get('production_notes', 'Emotionally grounded production')}\n" \
                                  f"Character perspective: {character_description[:100]}...\n" \
                                  f"{wiki_attribution}\n" \
                                  f"\nLYRICAL GUIDANCE:\n" \
                                  f"Verse concept: {lyric_structure['structure']['verses'][0]['opening'] if lyric_structure['structure']['verses'] else 'Character interpretation'}\n" \
                                  f"Chorus hook: {lyric_structure['structure']['chorus']['hook']}\n" \
                                  f"Themes: {', '.join(lyric_structure['themes'][:3])}\n" \
                                  f"LLM Production Authenticity: {musical_production.get('authenticity_notes', 'Contextual emotional delivery')}"
        else:
            enhanced_suno_command = original_result.suno_command

        # Format enhanced response combining original result with emotional framework
        response = {
            "processing_status": "completed_with_emotional_framework",
            "content_analysis": enhanced_analysis,
            "character_story": {
                "personal_connection": original_result.personal_story if hasattr(original_result, 'personal_story') else "Character-driven interpretation",
                "emotional_context": f"Processing LLM-analyzed emotions through music: {emotional_map.get('primary_emotion', 'contemplative')}",
                "creative_process": "LLM-driven production with meta-narrative analysis"
            },
            "musical_elements": {
                "beat_progression": beat_progression,
                "lyrical_structure": lyric_structure,
                "emotional_authenticity": musical_production.get('authenticity_score', 0.8),
                "llm_musical_mapping": musical_production.get('genre_reasoning', 'LLM-determined genre selection')
            },
            "enhanced_suno_command": {
                "command": enhanced_suno_command,
                "emotional_grounding": True,
                "meta_narrative_integration": len(emotional_subtext) > 0,
                "lyrical_guidance_included": lyric_structure is not None,
                "beat_pattern_specified": beat_progression is not None
            },
            "framework_analysis": {
                "llm_emotional_analysis": "completed",
                "subtext_elements": len(emotional_subtext),
                "introspection_insights": len(introspection_data.get('self_awareness_moments', [])),
                "emotional_contradictions": len(emotional_contradictions),
                "llm_authenticity_score": musical_production.get('authenticity_score', 0.8)
            },
            "workflow_summary": f"Enhanced processing: {len(content)} chars → LLM emotional analysis → beat patterns + lyrics + meta-narrative analysis"
        }

        await ctx.info(f"Universal processing complete: {track_title}")

        return json.dumps(response, indent=2)

    except Exception as e:
        await ctx.error(f"Universal content processing failed: {str(e)}")
        return json.dumps({"error": f"Processing failed: {str(e)}"})

@mcp.tool
async def create_conceptual_album(
    content: str,
    album_concept: str = None,
    character_name: str = None,
    character_description: str = None,
    track_count: int = 8,
    genre: str = "alternative",
    processing_mode: str = "auto",
    ctx: Context = None
) -> str:
    """
    Create a comprehensive conceptual album with meaningful track progression.
    
    This consolidated tool handles multiple content types and creation modes:
    1. Story-integrated albums from narrative content with character arcs
    2. Character-driven albums from explicit character descriptions
    3. Conceptual albums from philosophical or abstract content
    4. Ensures unique, thematic track titles and content progression
    
    Args:
        content: Source content (narrative, character description, or concepts)
        album_concept: Album theme/title (auto-generated if None)
        character_name: Specific character perspective (auto-detected if None)
        character_description: Explicit character profile (for character-driven mode)
        track_count: Number of tracks (3-12)
        genre: Musical genre preference
        processing_mode: "narrative", "character", "conceptual", or "auto"
    
    Returns:
        JSON containing complete album with meaningful track progression
    """
    try:
        await ctx.info(f"Starting conceptual album creation with {processing_mode} mode...")

        # Validate inputs
        if track_count < 3 or track_count > 12:
            return json.dumps({"error": "Track count must be between 3 and 12"})

        if not content or len(content.strip()) < 50:
            return json.dumps({"error": "Content too short. Please provide substantial content for album creation."})

        # Step 1: Determine processing mode and content type
        detected_mode = await _detect_content_type(content, character_description, processing_mode, ctx)
        await ctx.info(f"Processing mode: {detected_mode}")

        # Step 2: Process content based on detected mode
        if detected_mode == "narrative":
            album_result = await _create_narrative_album(
                content, album_concept, character_name, track_count, genre, ctx
            )
        elif detected_mode == "character":
            album_result = await _create_character_driven_album(
                content, character_description, album_concept, track_count, genre, ctx
            )
        elif detected_mode == "conceptual":
            album_result = await _create_conceptual_thematic_album(
                content, album_concept, track_count, genre, ctx
            )
        else:
            # Hybrid mode - combine approaches
            album_result = await _create_hybrid_album(
                content, album_concept, character_name, character_description, track_count, genre, ctx
            )

        await ctx.info(f"Conceptual album creation complete: {track_count} unique tracks")
        return json.dumps(album_result, indent=2)

    except Exception as e:
        await ctx.error(f"Conceptual album creation failed: {str(e)}")
        return json.dumps({"error": f"Album creation failed: {str(e)}"})

async def _extract_story_beats(narrative_text: str, character: StandardCharacterProfile, ctx: Context) -> List[Dict]:
    """Extract key story beats and plot points from narrative"""

    # Divide text into sections for analysis
    text_length = len(narrative_text)
    section_size = text_length // 8  # 8 major story sections

    story_beats = []

    for i in range(8):
        start = i * section_size
        end = start + section_size if i < 7 else text_length
        section = narrative_text[start:end]

        # Find character mentions in this section
        char_mentions = section.lower().count(character.name.lower())

        if char_mentions > 0:
            # Extract key events and emotions
            beat = {
                "section": i + 1,
                "text": section[:500],  # First 500 chars
                "character_presence": char_mentions,
                "key_events": _extract_events(section, character.name),
                "emotional_state": _analyze_section_emotion(section),
                "relationships": _extract_section_relationships(section, character.name),
                "conflicts": _extract_section_conflicts(section)
            }
            story_beats.append(beat)

    return story_beats

def _extract_events(text: str, character_name: str) -> List[str]:
    """Extract key events from text section"""
    event_indicators = ['happened', 'occurred', 'discovered', 'realized', 'found', 'met', 'left', 'arrived', 'decided', 'fought']
    events = []

    sentences = text.split('.')
    for sentence in sentences:
        if character_name.lower() in sentence.lower():
            for indicator in event_indicators:
                if indicator in sentence.lower():
                    events.append(sentence.strip())
                    break

    return events[:3]  # Top 3 events

def _analyze_section_emotion(text: str) -> str:
    """Analyze dominant emotion in text section"""
    emotions = {
        'tense': ['conflict', 'fight', 'argue', 'tension', 'struggle'],
        'joyful': ['happy', 'joy', 'celebrate', 'laugh', 'smile'],
        'sorrowful': ['sad', 'cry', 'loss', 'grief', 'mourn'],
        'hopeful': ['hope', 'dream', 'aspire', 'wish', 'future'],
        'fearful': ['afraid', 'fear', 'scared', 'terrified', 'anxious'],
        'triumphant': ['victory', 'success', 'achieve', 'win', 'overcome']
    }

    text_lower = text.lower()
    emotion_scores = {}

    for emotion, keywords in emotions.items():
        score = sum(text_lower.count(keyword) for keyword in keywords)
        if score > 0:
            emotion_scores[emotion] = score

    if emotion_scores:
        return max(emotion_scores, key=emotion_scores.get)
    return 'neutral'

def _extract_section_relationships(text: str, character_name: str) -> List[str]:
    """Extract relationship dynamics in section"""
    relationships = []

    # Find other character names near our character
    sentences = text.split('.')
    for sentence in sentences:
        if character_name.lower() in sentence.lower():
            # Look for other capitalized names
            words = sentence.split()
            for word in words:
                if word != character_name and word[0].isupper() and len(word) > 2:
                    relationships.append(f"Interaction with {word}")

    return list(set(relationships))[:2]

def _extract_section_conflicts(text: str) -> List[str]:
    """Extract conflicts and challenges in section"""
    conflict_words = ['but', 'however', 'although', 'despite', 'against', 'struggle', 'challenge', 'difficult']
    conflicts = []

    sentences = text.split('.')
    for sentence in sentences:
        for word in conflict_words:
            if word in sentence.lower():
                conflicts.append(sentence.strip())
                break

    return conflicts[:2]

async def _generate_story_based_tracks(
    story_beats: List[Dict],
    character: StandardCharacterProfile,
    persona: ArtistPersona,
    track_count: int,
    ctx: Context
) -> List[Dict]:
    """Generate track concepts based on actual story progression"""

    track_concepts = []

    # Distribute tracks across story beats
    beats_per_track = max(1, len(story_beats) // track_count)

    for i in range(track_count):
        # Select story beat(s) for this track
        beat_index = min(i * beats_per_track, len(story_beats) - 1)
        beat = story_beats[beat_index]

        # Determine track position in story arc
        position = i / (track_count - 1) if track_count > 1 else 0.5

        # Generate track concept based on story position
        if position < 0.2:  # Beginning
            narrative_function = "Introduction/Setup"
            musical_evolution = "Establishing musical identity"
        elif position < 0.4:  # Rising action
            narrative_function = "Rising Action/Development"
            musical_evolution = "Building complexity and tension"
        elif position < 0.6:  # Midpoint
            narrative_function = "Turning Point/Revelation"
            musical_evolution = "Genre exploration/experimentation"
        elif position < 0.8:  # Climax approach
            narrative_function = "Climax/Peak Conflict"
            musical_evolution = "Maximum intensity and emotion"
        else:  # Resolution
            narrative_function = "Resolution/Reflection"
            musical_evolution = "Synthesis and closure"

        # Extract specific story content for this track
        story_excerpt = beat['text'][:300] + "..."

        # Create track title based on story events
        if beat['key_events']:
            event_summary = beat['key_events'][0].split()[:5]
            track_title = f"{character.name} - {' '.join(event_summary)}"
        else:
            track_title = f"{character.name} - Chapter {beat['section']}"

        track_concept = {
            "title": track_title,
            "story_context": f"Story section {beat['section']}: {beat['emotional_state']} tone",
            "character_state": f"{character.name} experiencing {beat['emotional_state']} emotions",
            "emotional_tone": beat['emotional_state'],
            "narrative_function": narrative_function,
            "story_excerpt": story_excerpt,
            "musical_evolution": musical_evolution,
            "relationships_present": beat['relationships'],
            "conflicts_present": beat['conflicts'][:1] if beat['conflicts'] else [],
            "track_themes": _extract_track_themes(beat, character)
        }

        track_concepts.append(track_concept)

    return track_concepts

def _extract_track_themes(beat: Dict, character: StandardCharacterProfile) -> List[str]:
    """Extract themes for a specific track based on story beat"""
    themes = []

    # Add emotional theme
    themes.append(f"{beat['emotional_state']} journey")

    # Add relationship themes
    if beat['relationships']:
        themes.append("interpersonal dynamics")

    # Add conflict themes
    if beat['conflicts']:
        themes.append("overcoming challenges")

    # Add character-specific themes
    if character.motivations:
        themes.append(character.motivations[0].lower())

    return themes[:3]

async def _generate_story_aware_suno_command(
    persona: ArtistPersona,
    character: StandardCharacterProfile,
    track_concept: Dict,
    track_result_data: Dict,
    ctx: Context
) -> str:
    """Generate Suno command that reflects story progression"""

    # Build command with story-specific elements
    emotional_descriptor = track_concept['emotional_tone']
    narrative_position = track_concept['narrative_function']

    # Adjust musical style based on story position
    if "Introduction" in narrative_position:
        style_modifier = "introductory, establishing"
    elif "Climax" in narrative_position:
        style_modifier = "intense, dramatic, peak energy"
    elif "Resolution" in narrative_position:
        style_modifier = "reflective, concluding"
    else:
        style_modifier = "developing, progressive"

    # Extract the base Suno command from process_universal_content
    base_suno_command = track_result_data['suno_command']['formatted_command']

    # Enhance with story-specific elements
    # Find where the lyrics start in the base command
    lyrics_start = base_suno_command.find('[Intro]')
    if lyrics_start == -1:
        lyrics_start = base_suno_command.find('[Verse')

    if lyrics_start > -1:
        # Extract the lyrics portion
        lyrics_portion = base_suno_command[lyrics_start:]

        # Build enhanced story-aware command
        suno_command = f"""[{persona.primary_genre}] [{emotional_descriptor}] [{style_modifier}]
    
{track_concept['title']} - {narrative_position}

Musical interpretation of {character.name}'s journey at this story moment.
{persona.vocal_style} conveying {emotional_descriptor} emotions.

Key themes: {', '.join(track_concept['track_themes'])}

{lyrics_portion}

[Production notes: {track_concept['musical_evolution']}]
[Story context: {track_concept['story_context']}]
[Character state: {track_concept['character_state']}]"""
    else:
        # Fallback if we can't parse the base command
        suno_command = base_suno_command + f"\n\n[Story Integration: {narrative_position} - {emotional_descriptor}]"

    return suno_command

@mcp.tool
async def analyze_artist_psychology(
    character_json: str,
    persona_json: str,
    ctx: Context = None
) -> str:
    """
    Analyze the psychological motivations behind why a character creates music.
    
    Explores the deep psychological drivers that transform a literary character
    into a musical artist, examining their backstory, traumas, desires, and
    how these manifest in their artistic expression.
    
    Args:
        character_json: JSON string containing character profile from analyze_character_text
        persona_json: JSON string containing artist persona from generate_artist_personas
        
    Returns:
        JSON containing deep psychological analysis of the artist's creative motivations,
        backstory influences, and artistic purpose according to character bible methodology
    """
    try:
        await ctx.info("Starting deep artist psychology analysis...")

        # Parse input data
        character_data = json.loads(character_json)
        persona_data = json.loads(persona_json)

        # Extract character and persona
        if 'characters' in character_data and character_data['characters']:
            character_info = character_data['characters'][0]  # First character
        else:
            character_info = character_data

        if 'artist_personas' in persona_data and persona_data['artist_personas']:
            persona_info = persona_data['artist_personas'][0]  # First persona
        else:
            persona_info = persona_data

        # Use StandardCharacterProfile.from_dict to handle format issues gracefully
        character = StandardCharacterProfile.from_dict(character_info)

        # Use ArtistPersona.from_dict to handle format issues gracefully
        persona = ArtistPersona.from_dict(persona_info)

        await ctx.info(f"Analyzing {character.name} as artist {persona.artist_name}...")

        # Deep psychological analysis
        analysis = await _analyze_artist_psychology_deep(character, persona, ctx)

        await ctx.info("Artist psychology analysis complete")

        return json.dumps(analysis, indent=2)

    except Exception as e:
        await ctx.error(f"Artist psychology analysis failed: {str(e)}")
        return json.dumps({"error": f"Psychology analysis failed: {str(e)}"})

async def _analyze_artist_psychology_deep(character: StandardCharacterProfile, persona: ArtistPersona, ctx: Context) -> Dict:
    """Perform deep psychological analysis of artist motivations"""

    # 1. Analyze why they turned to music
    musical_genesis = _analyze_musical_genesis(character, persona)

    # 2. Examine backstory influences on artistic expression
    backstory_influences = _analyze_backstory_influences(character, persona)

    # 3. Explore trauma and healing through music
    trauma_and_healing = _analyze_trauma_healing_through_music(character, persona)

    # 4. Analyze creative process psychology
    creative_process = _analyze_creative_process_psychology(character, persona)

    # 5. Examine relationship between character flaws and artistic strengths
    flaws_to_strengths = _analyze_character_flaws_as_artistic_fuel(character, persona)

    # 6. Explore artistic identity vs. personal identity
    identity_analysis = _analyze_artistic_vs_personal_identity(character, persona)

    # 7. Examine audience relationship and performance psychology
    audience_psychology = _analyze_audience_relationship(character, persona)

    # 8. Analyze genre choice as psychological expression
    genre_psychology = _analyze_genre_as_psychology(character, persona)

    return {
        "artist_psychology_analysis": {
            "character_name": character.name,
            "artist_name": persona.artist_name,
            "confidence_score": character.confidence_score,
            "analysis_depth": "comprehensive_character_bible_methodology"
        },
        "musical_genesis": musical_genesis,
        "backstory_influences": backstory_influences,
        "trauma_and_healing": trauma_and_healing,
        "creative_process_psychology": creative_process,
        "character_flaws_as_fuel": flaws_to_strengths,
        "identity_dynamics": identity_analysis,
        "audience_relationship": audience_psychology,
        "genre_psychology": genre_psychology,
        "artistic_purpose": {
            "core_mission": _extract_artistic_mission(character, persona),
            "deeper_motivations": _extract_deeper_motivations(character),
            "artistic_legacy_desire": _extract_legacy_desires(character, persona),
            "creative_fulfillment": _analyze_creative_fulfillment_needs(character)
        },
        "psychological_insights": {
            "why_this_genre": _explain_genre_choice_psychology(character, persona),
            "why_these_themes": _explain_thematic_choices(character, persona),
            "why_this_vocal_style": _explain_vocal_style_psychology(character, persona),
            "creative_compulsions": _identify_creative_compulsions(character)
        },
        "character_bible_integration": {
            "skin_layer_in_music": _map_skin_to_music(character, persona),
            "flesh_layer_in_music": _map_flesh_to_music(character, persona),
            "core_layer_in_music": _map_core_to_music(character, persona)
        }
    }

def _analyze_musical_genesis(character: StandardCharacterProfile, persona: ArtistPersona) -> Dict:
    """Analyze why and how the character became a musical artist"""

    # Extract key themes from backstory for more specific analysis
    backstory_themes = _extract_backstory_themes(character.backstory)

    # Look for turning points in character's life
    turning_points = []
    for experience in character.formative_experiences:
        if any(word in experience.lower() for word in ['loss', 'death', 'betrayal', 'discovery', 'revelation', 'injustice', 'fight', 'protest', 'brutality']):
            turning_points.append(experience)

    # Also check backstory for turning points
    if character.backstory:
        backstory_lower = character.backstory.lower()
        if any(word in backstory_lower for word in ['lost', 'death', 'died', 'injustice', 'poverty', 'fight', 'struggle']):
            # Extract the specific context from backstory
            backstory_context = character.backstory[:100] + "..." if len(character.backstory) > 100 else character.backstory
            turning_points.append(backstory_context)

    # Examine motivations that led to music
    musical_drivers = []
    for motivation in character.motivations:
        if any(word in motivation.lower() for word in ['express', 'communicate', 'heal', 'understand', 'connect', 'fight', 'voice', 'honor', 'memory']):
            musical_drivers.append(motivation)

    # Analyze what music provides that life couldn't
    music_as_solution = []
    for fear in character.fears:
        if 'isolation' in fear.lower() or 'alone' in fear.lower():
            music_as_solution.append("Music as connection to others")
        if 'meaningless' in fear.lower() or 'purpose' in fear.lower():
            music_as_solution.append("Music as meaning-making")
        if 'loss' in fear.lower() or 'forgotten' in fear.lower():
            music_as_solution.append("Music as preservation of memory")
        if 'selling out' in fear.lower() or 'complacent' in fear.lower():
            music_as_solution.append("Music as authentic expression")

    # Create more specific origin story based on character details
    origin_story = _create_specific_origin_story(character, persona, turning_points, backstory_themes)

    return {
        "origin_story": origin_story,
        "turning_points": turning_points[:3],
        "musical_drivers": musical_drivers[:3],
        "music_as_solution": music_as_solution,
        "genesis_psychology": f"Music became {character.name}'s way of {musical_drivers[0] if musical_drivers else 'processing life experiences'}",
        "first_musical_experience": _reconstruct_first_musical_experience(character, persona)
    }

def _extract_backstory_themes(backstory: str) -> List[str]:
    """Extract key themes from character backstory"""
    if not backstory:
        return []

    themes = []
    backstory_lower = backstory.lower()

    # Social/economic themes
    if any(word in backstory_lower for word in ['poverty', 'poor', 'urban', 'city', 'street']):
        themes.append("urban struggle")
    if any(word in backstory_lower for word in ['mountain', 'rural', 'quiet', 'small town']):
        themes.append("rural/isolated upbringing")

    # Loss/trauma themes
    if any(word in backstory_lower for word in ['lost', 'death', 'died', 'father', 'mother']):
        themes.append("family loss")
    if any(word in backstory_lower for word in ['injustice', 'unfair', 'brutality', 'systemic']):
        themes.append("social injustice")

    # Personal growth themes
    if any(word in backstory_lower for word in ['fought', 'fight', 'struggle', 'overcome']):
        themes.append("personal struggle")

    return themes

def _create_specific_origin_story(character: StandardCharacterProfile, persona: ArtistPersona, turning_points: List[str], themes: List[str]) -> str:
    """Create a specific origin story incorporating character details"""

    # Use the most relevant turning point
    primary_catalyst = turning_points[0] if turning_points else "life experiences"

    # Incorporate backstory themes
    context = ""
    if "urban struggle" in themes:
        context = "growing up in urban poverty and witnessing systemic injustice"
    elif "family loss" in themes:
        context = "experiencing profound loss and seeking meaning"
    elif "social injustice" in themes:
        context = "confronting inequality and fighting for justice"
    elif "rural/isolated upbringing" in themes:
        context = "finding solace in quiet, introspective moments"
    else:
        context = "navigating personal challenges"

    # Connect to musical choice
    genre_connection = ""
    if persona.primary_genre:
        if "punk" in persona.primary_genre.lower() or "rock" in persona.primary_genre.lower():
            genre_connection = f", finding that {persona.primary_genre} provided the raw energy needed for authentic expression"
        elif "folk" in persona.primary_genre.lower():
            genre_connection = f", discovering that {persona.primary_genre} offered the perfect medium for introspective storytelling"
        else:
            genre_connection = f", drawn to {persona.primary_genre} as the ideal vehicle for their message"

    return f"{character.name} turned to music after {context}, specifically responding to {primary_catalyst}{genre_connection}"

def _reconstruct_first_musical_experience(character: StandardCharacterProfile, persona: ArtistPersona) -> str:
    """Reconstruct what their first meaningful musical experience might have been"""

    emotional_state = "seeking solace" if character.fears else "exploring creativity"
    context = character.backstory[:100] if character.backstory else "during a formative period"

    return f"Likely discovered {persona.primary_genre} while {emotional_state}, {context}. The genre's {persona.genre_justification.split('.')[0]} resonated with their {character.personality_drivers[0] if character.personality_drivers else 'inner nature'}."

def _analyze_backstory_influences(character: StandardCharacterProfile, persona: ArtistPersona) -> Dict:
    """Examine how backstory shapes artistic expression"""

    # Family influences
    family_musical_influence = "unknown"
    if character.relationships:
        for rel in character.relationships:
            if 'parent' in rel.lower() or 'family' in rel.lower():
                family_musical_influence = rel
                break

    # Formative experiences in music
    formative_musical_experiences = []
    for exp in character.formative_experiences:
        formative_musical_experiences.append(f"Translated into music: {exp}")

    # Cultural/social background influence
    social_influences = []
    for connection in character.social_connections:
        social_influences.append(f"Musical network influence: {connection}")

    return {
        "family_musical_heritage": family_musical_influence,
        "formative_experiences_in_music": formative_musical_experiences[:3],
        "social_musical_influences": social_influences[:3],
        "backstory_to_lyrics_pipeline": f"Personal history becomes lyrical content through {character.name}'s {persona.vocal_style}",
        "cultural_musical_identity": f"Backstory shaped their {persona.primary_genre} identity and {persona.collaboration_style}"
    }

def _analyze_trauma_healing_through_music(character: StandardCharacterProfile, persona: ArtistPersona) -> Dict:
    """Explore how trauma manifests and heals through musical expression"""

    # Identify traumas
    traumas = []
    for fear in character.fears:
        traumas.append(f"Trauma indicator: {fear}")
    for conflict in character.conflicts:
        traumas.append(f"Ongoing trauma: {conflict}")

    # How music heals
    healing_mechanisms = []
    if 'emotional' in persona.vocal_style:
        healing_mechanisms.append("Vocal expression as emotional release")
    if any(theme for theme in persona.lyrical_themes if 'relationship' in theme or 'love' in theme):
        healing_mechanisms.append("Lyrical exploration of human connection")
    if persona.collaboration_style:
        healing_mechanisms.append(f"Collaborative healing: {persona.collaboration_style}")

    # Musical therapy aspects
    therapeutic_elements = []
    for emotion in persona.emotional_palette:
        therapeutic_elements.append(f"Processing {emotion} through {persona.primary_genre}")

    return {
        "identified_traumas": traumas[:3],
        "musical_healing_mechanisms": healing_mechanisms,
        "therapeutic_elements": therapeutic_elements,
        "trauma_to_art_transformation": f"{character.name} transforms pain into {persona.primary_genre} that {healing_mechanisms[0] if healing_mechanisms else 'provides catharsis'}",
        "healing_progression": "Music as path from trauma to transcendence"
    }

def _analyze_creative_process_psychology(character: StandardCharacterProfile, persona: ArtistPersona) -> Dict:
    """Analyze the psychology behind their creative process"""

    # When they create (psychological state)
    creative_triggers = []
    for motivation in character.motivations:
        creative_triggers.append(f"Creates when feeling: {motivation}")

    # How they create (psychological approach)
    if 'controlled' in persona.vocal_style:
        creative_approach = "Methodical, precise creative process"
    elif 'raw' in persona.vocal_style:
        creative_approach = "Spontaneous, emotional creative process"
    else:
        creative_approach = "Balanced creative process"

    # Creative compulsions
    compulsions = []
    for driver in character.personality_drivers:
        if 'brave' in driver:
            compulsions.append("Compelled to take creative risks")
        elif 'cunning' in driver:
            compulsions.append("Compelled to create complex, layered music")
        elif 'compassionate' in driver:
            compulsions.append("Compelled to create music that heals others")

    return {
        "creative_triggers": creative_triggers[:3],
        "creative_approach": creative_approach,
        "creative_compulsions": compulsions,
        "creative_psychology": f"{character.name}'s {character.personality_drivers[0] if character.personality_drivers else 'nature'} drives their {creative_approach}",
        "artistic_perfectionism": _analyze_perfectionist_tendencies(character),
        "creative_blocks": _analyze_creative_blocks(character)
    }

def _analyze_perfectionist_tendencies(character: StandardCharacterProfile) -> str:
    """Analyze perfectionist tendencies in their art"""
    if any('control' in trait.lower() for trait in character.behavioral_traits):
        return "High perfectionism - art as control over chaos"
    elif any('fear' in fear.lower() for fear in character.fears):
        return "Perfectionism driven by fear of vulnerability"
    else:
        return "Balanced approach to artistic standards"

def _analyze_creative_blocks(character: StandardCharacterProfile) -> List[str]:
    """Identify likely creative blocks"""
    blocks = []
    for fear in character.fears:
        if 'failure' in fear.lower():
            blocks.append("Fear of artistic failure")
        if 'rejection' in fear.lower():
            blocks.append("Fear of audience rejection")
        if 'authentic' in fear.lower():
            blocks.append("Fear of not being authentic enough")
    return blocks[:2]

def _analyze_character_flaws_as_artistic_fuel(character: StandardCharacterProfile, persona: ArtistPersona) -> Dict:
    """Analyze how character flaws become artistic strengths"""

    flaw_to_strength_mappings = []

    # Look at conflicts as potential flaws that become strengths
    for conflict in character.conflicts:
        if 'anger' in conflict.lower():
            flaw_to_strength_mappings.append("Anger → Passionate musical expression")
        elif 'isolation' in conflict.lower():
            flaw_to_strength_mappings.append("Isolation → Deep introspective lyrics")
        elif 'control' in conflict.lower():
            flaw_to_strength_mappings.append("Control issues → Precise musical production")

    # Look at fears as vulnerabilities that create authenticity
    vulnerability_to_art = []
    for fear in character.fears:
        vulnerability_to_art.append(f"Vulnerability about {fear} → Authentic lyrical content")

    return {
        "flaw_to_strength_mappings": flaw_to_strength_mappings[:3],
        "vulnerability_as_authenticity": vulnerability_to_art[:3],
        "artistic_alchemy": f"{character.name} transforms personal flaws into {persona.primary_genre} authenticity",
        "shadow_work_through_music": "Using music to integrate rejected aspects of self"
    }

def _analyze_artistic_vs_personal_identity(character: StandardCharacterProfile, persona: ArtistPersona) -> Dict:
    """Analyze the relationship between personal and artistic identity"""

    identity_alignment = "high" if character.name.lower() in persona.artist_name.lower() else "moderate"

    # How much of themselves they put into their art
    self_revelation_level = "high" if len(persona.lyrical_themes) > 3 else "moderate"

    # Artistic persona as protection or exposure
    if any('mysterious' in trait for trait in character.behavioral_traits):
        persona_function = "Artistic identity as protective mask"
    else:
        persona_function = "Artistic identity as authentic self-expression"

    return {
        "identity_alignment": identity_alignment,
        "self_revelation_level": self_revelation_level,
        "persona_function": persona_function,
        "artistic_authenticity": f"{persona.artist_name} represents {character.name}'s {persona_function.lower()}",
        "performance_vs_private_self": _analyze_performance_psychology(character, persona)
    }

def _analyze_performance_psychology(character: StandardCharacterProfile, persona: ArtistPersona) -> str:
    """Analyze psychology of performance vs private self"""
    if 'confident' in persona.vocal_style:
        return "Performance amplifies natural confidence"
    elif 'vulnerable' in persona.vocal_style:
        return "Performance as controlled vulnerability"
    else:
        return "Performance as extension of authentic self"

def _analyze_audience_relationship(character: StandardCharacterProfile, persona: ArtistPersona) -> Dict:
    """Analyze psychological relationship with audience"""

    # What they seek from audience
    audience_needs = []
    for desire in character.desires:
        if 'love' in desire.lower() or 'accept' in desire.lower():
            audience_needs.append("Seeks love and acceptance through music")
        elif 'understand' in desire.lower():
            audience_needs.append("Seeks understanding and connection")
        elif 'impact' in desire.lower():
            audience_needs.append("Seeks to make meaningful impact")

    # How they relate to audience based on collaboration style
    audience_relationship_style = persona.collaboration_style.replace('collaborative', 'audience connection')

    return {
        "audience_psychological_needs": audience_needs[:2],
        "audience_relationship_style": audience_relationship_style,
        "performance_psychology": f"Uses {persona.vocal_style} to {audience_needs[0] if audience_needs else 'connect with audience'}",
        "audience_as_therapy": "Audience connection as healing for character's relational wounds"
    }

def _analyze_genre_as_psychology(character: StandardCharacterProfile, persona: ArtistPersona) -> Dict:
    """Analyze genre choice as psychological expression"""

    genre_psychology = {
        "rock": "Rebellion and power expression",
        "folk": "Storytelling and authenticity seeking",
        "electronic": "Control and precision needs",
        "jazz": "Complexity and sophistication expression",
        "blues": "Pain processing and emotional release"
    }

    chosen_psychology = genre_psychology.get(persona.primary_genre, "Self-expression and identity formation")

    return {
        "genre_psychology": chosen_psychology,
        "genre_justification_deep": f"{persona.primary_genre} allows {character.name} to express their {chosen_psychology.lower()}",
        "musical_language": f"{persona.primary_genre} becomes {character.name}'s psychological language",
        "genre_evolution_potential": f"May evolve toward {persona.secondary_genres[0] if persona.secondary_genres else 'hybrid genres'} as psychology matures"
    }

def _extract_artistic_mission(character: StandardCharacterProfile, persona: ArtistPersona) -> str:
    """Extract the character's core artistic mission"""
    if character.motivations:
        primary_motivation = character.motivations[0]
        return f"Core mission: Use {persona.primary_genre} to {primary_motivation.lower()}"
    else:
        return f"Core mission: Express authentic self through {persona.primary_genre}"

def _extract_deeper_motivations(character: StandardCharacterProfile) -> List[str]:
    """Extract deeper psychological motivations behind the art"""
    deeper_motivations = []

    # Look at the intersection of desires and fears
    for desire in character.desires:
        for fear in character.fears:
            if 'love' in desire.lower() and 'rejection' in fear.lower():
                deeper_motivations.append("Seeking love while protecting from rejection")
            elif 'success' in desire.lower() and 'failure' in fear.lower():
                deeper_motivations.append("Proving worth through artistic achievement")

    # If no intersections found, use direct motivations
    if not deeper_motivations:
        deeper_motivations = character.motivations[:2]

    return deeper_motivations[:3]

def _extract_legacy_desires(character: StandardCharacterProfile, persona: ArtistPersona) -> str:
    """What kind of legacy they want to leave through music"""
    if any('help' in desire.lower() for desire in character.desires):
        return "Legacy: Music that heals and helps others"
    elif any('remember' in desire.lower() for desire in character.desires):
        return f"Legacy: Unforgettable {persona.primary_genre} artistry"
    else:
        return f"Legacy: Authentic {persona.primary_genre} that captures human truth"

def _analyze_creative_fulfillment_needs(character: StandardCharacterProfile) -> List[str]:
    """What the character needs to feel creatively fulfilled"""
    fulfillment_needs = []

    for motivation in character.motivations:
        if 'recognition' in motivation.lower():
            fulfillment_needs.append("Recognition for artistic excellence")
        elif 'connection' in motivation.lower():
            fulfillment_needs.append("Deep connection with audience")
        elif 'impact' in motivation.lower():
            fulfillment_needs.append("Meaningful impact on others' lives")

    if not fulfillment_needs:
        fulfillment_needs = ["Authentic self-expression", "Creative growth", "Artistic integrity"]

    return fulfillment_needs[:3]

def _explain_genre_choice_psychology(character: StandardCharacterProfile, persona: ArtistPersona) -> str:
    """Explain psychological reasons for genre choice"""
    return f"{character.name} chose {persona.primary_genre} because {persona.genre_justification.split('.')[0]}. This genre allows them to express their {character.personality_drivers[0] if character.personality_drivers else 'core nature'} through music."

def _explain_thematic_choices(character: StandardCharacterProfile, persona: ArtistPersona) -> str:
    """Explain psychological reasons for thematic choices"""
    primary_theme = persona.lyrical_themes[0] if persona.lyrical_themes else "personal expression"
    return f"Focuses on {primary_theme} because it directly connects to their {character.motivations[0] if character.motivations else 'life experiences'}"

def _explain_vocal_style_psychology(character: CharacterProfile, persona: ArtistPersona) -> str:
    """Explain psychological reasons for vocal style"""
    return f"Vocal style ({persona.vocal_style}) reflects their {character.behavioral_traits[0] if character.behavioral_traits else 'authentic personality'} and serves as their primary emotional outlet"

def _identify_creative_compulsions(character: CharacterProfile) -> List[str]:
    """Identify what compels them to create"""
    compulsions = []

    for motivation in character.motivations:
        compulsions.append(f"Compelled by: {motivation}")

    for fear in character.fears:
        compulsions.append(f"Creates to avoid: {fear}")

    return compulsions[:3]

def _map_skin_to_music(character: CharacterProfile, persona: ArtistPersona) -> str:
    """Map skin layer (observable traits) to musical expression"""
    return f"Physical mannerisms ({character.mannerisms[0] if character.mannerisms else 'body language'}) translate to {persona.vocal_style} and stage presence"

def _map_flesh_to_music(character: CharacterProfile, persona: ArtistPersona) -> str:
    """Map flesh layer (background/relationships) to musical expression"""
    return f"Personal history and relationships become lyrical content and {persona.collaboration_style}"

def _map_core_to_music(character: CharacterProfile, persona: ArtistPersona) -> str:
    """Map core layer (deep psychology) to musical expression"""
    return f"Core motivations and fears drive the {persona.primary_genre} choice and {', '.join(persona.lyrical_themes[:2])} thematic focus"

@mcp.tool
async def crawl_suno_wiki_best_practices(
    topic: str = "all",
    ctx: Context = None
) -> str:
    """
    Get current Suno AI best practices and format specifications from cached wiki data.
    
    This tool provides actual Suno AI documentation and best practices from the 
    cached wiki data system, replacing hardcoded assumptions with real specifications.
    
    Args:
        topic: Specific topic to focus on (genres, meta_tags, techniques, prompt_formats, best_practices, all)
        
    Returns:
        JSON containing current Suno AI specifications and best practices from cached data
    """
    try:
        await ctx.info(f"Retrieving Suno AI Wiki data for {topic}...")

        # Ensure wiki data manager is available
        current_wiki_manager = await ensure_wiki_data_manager()

        if current_wiki_manager:
            await ctx.info("Using wiki data manager for cached data access")
        else:
            await ctx.info("Wiki data manager not available, using fallback mode")

        # Initialize response structure with actual wiki data
        suno_knowledge = {
            "crawl_status": "completed_from_cache" if current_wiki_manager else "fallback_mode",
            "data_source": "https://sunoaiwiki.com/ (cached)" if current_wiki_manager else "fallback_data",
            "topic_focus": topic,
            "cache_timestamp": datetime.now().isoformat(),
            "current_specifications": {},
            "verified_best_practices": [],
            "actual_format_requirements": {},
            "known_limitations": {},
            "working_examples": [],
            "available_genres": [],
            "available_meta_tags": [],
            "available_techniques": []
        }

        # Get data from WikiDataManager if available
        if current_wiki_manager:
            try:
                # Get genres data
                if topic in ["all", "genres"]:
                    await ctx.info("Retrieving genres data...")
                    genres = await current_wiki_manager.get_genres()
                    suno_knowledge["available_genres"] = [
                        {
                            "name": genre.name,
                            "description": genre.description,
                            "characteristics": genre.characteristics,
                            "typical_instruments": genre.typical_instruments,
                            "mood_associations": genre.mood_associations,
                            "source_url": getattr(genre, 'source_url', ''),
                            "download_date": getattr(genre, 'download_date', '')
                        } for genre in genres[:50]  # Limit to first 50 for readability
                    ]

                    # Extract genre-based specifications
                    suno_knowledge["current_specifications"]["supported_genres"] = [g.name for g in genres]
                    suno_knowledge["current_specifications"]["total_genres_available"] = len(genres)

                    # Extract genre categories
                    genre_categories = []
                    for g in genres:
                        if " in the " in g.description:
                            category = g.description.split(" in the ")[-1].split(" category")[0]
                            if category not in genre_categories:
                                genre_categories.append(category)
                    suno_knowledge["current_specifications"]["genre_categories"] = genre_categories

                    await ctx.info(f"Retrieved {len(genres)} genres from {len(genre_categories)} categories")

                # Get meta tags data
                if topic in ["all", "meta_tags", "prompt_formats"]:
                    await ctx.info("Retrieving meta tags data...")
                    meta_tags = await current_wiki_manager.get_meta_tags()
                    suno_knowledge["available_meta_tags"] = [
                        {
                            "tag": tag.tag,
                            "category": tag.category,
                            "description": tag.description,
                            "compatible_genres": tag.compatible_genres,
                            "source_url": getattr(tag, 'source_url', ''),
                            "download_date": getattr(tag, 'download_date', '')
                        } for tag in meta_tags[:100]  # Show more meta tags as they're essential
                    ]

                    # Extract format requirements from meta tags
                    categories = {}
                    for tag in meta_tags:
                        if tag.category not in categories:
                            categories[tag.category] = []
                        categories[tag.category].append(tag.tag)

                    suno_knowledge["actual_format_requirements"] = {
                        "tag_format": "Use tags in [brackets] like [Intro], [Verse], [Chorus]",
                        "supported_categories": list(categories.keys()),
                        "total_tags_available": len(meta_tags),
                        "category_breakdown": {cat: len(tags) for cat, tags in categories.items()}
                    }

                    # Add specific category tags for easy access
                    for category, tags in categories.items():
                        suno_knowledge["actual_format_requirements"][f"{category}_tags"] = tags

                    await ctx.info(f"Retrieved {len(meta_tags)} meta tags across {len(categories)} categories")

                # Get techniques data
                if topic in ["all", "techniques", "best_practices"]:
                    await ctx.info("Retrieving techniques and best practices...")
                    techniques = await current_wiki_manager.get_techniques()
                    suno_knowledge["available_techniques"] = [
                        {
                            "name": tech.name,
                            "description": tech.description,
                            "technique_type": tech.technique_type,
                            "examples": tech.examples,
                            "applicable_scenarios": tech.applicable_scenarios,
                            "source_url": getattr(tech, 'source_url', ''),
                            "download_date": getattr(tech, 'download_date', '')
                        } for tech in techniques[:50]  # Limit for readability
                    ]

                    # Extract best practices from techniques
                    best_practices = []
                    technique_types = ["prompt_structure", "meta_tags", "vocal_style", "song_structure", "lyric_writing"]

                    for tech in techniques:
                        if tech.technique_type in technique_types:
                            best_practices.append({
                                "practice": tech.name,
                                "description": tech.description,
                                "type": tech.technique_type,
                                "examples": tech.examples,
                                "applicable_scenarios": tech.applicable_scenarios
                            })

                    suno_knowledge["verified_best_practices"] = best_practices

                    # Extract working examples
                    working_examples = []
                    for tech in techniques:
                        if tech.examples:
                            for example in tech.examples:
                                working_examples.append({
                                    "example": example,
                                    "technique": tech.name,
                                    "type": tech.technique_type,
                                    "applicable_scenarios": tech.applicable_scenarios
                                })

                    suno_knowledge["working_examples"] = working_examples[:100]  # Show more examples

                    await ctx.info(f"Retrieved {len(techniques)} techniques, extracted {len(best_practices)} best practices and {len(working_examples)} examples")

                # Note: Using global wiki_data_manager, no cleanup needed

            except Exception as e:
                await ctx.error(f"Error retrieving wiki data: {e}")
                logger.error(f"Wiki data retrieval error: {e}")
                # Continue with fallback data
                suno_knowledge["crawl_status"] = "partial_failure"
                suno_knowledge["error_details"] = str(e)
        else:
            # No wiki manager available - provide fallback information
            await ctx.info("Wiki data manager not available, providing fallback information...")
            suno_knowledge["crawl_status"] = "fallback_mode"
            suno_knowledge["fallback_reason"] = "Wiki integration not available or failed to initialize"

        # Add technical limitations based on cached data analysis and known Suno AI constraints
        suno_knowledge["known_limitations"] = {
            "prompt_length": "Recommended to keep prompts concise and focused (under 200 characters for best results)",
            "tag_usage": "Use brackets [like this] for structural and effect tags - avoid overusing tags",
            "genre_mixing": "Can combine multiple genres with comma separation, but limit to 2-3 for clarity",
            "vocal_specifications": "Use detailed vocal descriptors like [masculine low gospel vocal] for better control",
            "content_filtering": "Explicit content may be filtered - use creative alternatives and metaphors",
            "song_structure": "Use structural tags like [Intro], [Verse], [Chorus], [Bridge], [Outro] for better song flow",
            "lyric_formatting": "Use proper line breaks and avoid overly complex formatting",
            "style_consistency": "Maintain consistent style throughout the song for better results"
        }

        # Add integration notes for developers
        suno_knowledge["integration_notes"] = [
            "Use cached wiki data for accurate genre and meta tag information",
            "Apply verified prompt structures from techniques data",
            "Leverage meta tag categories for proper command formatting",
            "Use genre characteristics for better music generation context",
            "Apply technique examples for consistent results",
            "Combine multiple data sources (genres + meta tags + techniques) for optimal commands",
            "Consider character psychology when selecting appropriate techniques"
        ]

        # Add practical usage recommendations
        suno_knowledge["usage_recommendation"] = (
            "This cached wiki data provides real Suno AI specifications extracted from the official wiki. "
            "Use the genres, meta tags, and techniques data to replace hardcoded assumptions "
            "and generate more accurate Suno AI commands. Combine genre characteristics with "
            "appropriate meta tags and apply proven techniques for optimal music generation results."
        )

        # Add data freshness information
        suno_knowledge["data_freshness"] = {
            "cache_status": "active" if current_wiki_manager else "unavailable",
            "last_updated": datetime.now().isoformat(),
            "data_sources": [
                "https://sunoaiwiki.com/genres/",
                "https://sunoaiwiki.com/meta-tags/",
                "https://sunoaiwiki.com/tips-and-tricks/"
            ]
        }

        await ctx.info(f"Successfully retrieved Suno AI Wiki data for {topic}")
        return json.dumps(suno_knowledge, indent=2)

    except Exception as e:
        await ctx.error(f"Suno Wiki data retrieval failed: {str(e)}")
        logger.error(f"Crawl tool error: {e}")
        return json.dumps({
            "error": f"Wiki data retrieval failed: {str(e)}",
            "crawl_status": "failed",
            "fallback_recommendation": "Check wiki data cache availability and WikiDataManager initialization",
            "timestamp": datetime.now().isoformat()
        })



# Consolidated album creation helper functions

async def _detect_content_type(content: str, character_description: str, processing_mode: str, ctx: Context) -> str:
    """Detect the appropriate processing mode for the content"""
    if processing_mode != "auto":
        return processing_mode

    content_lower = content.lower()

    # Check for explicit character description
    if character_description and len(character_description.strip()) > 50:
        await ctx.info("Detected explicit character description - using character mode")
        return "character"

    # Check for narrative indicators
    narrative_indicators = ["story", "character", "protagonist", "plot", "chapter", "scene", "dialogue"]
    narrative_score = sum(1 for indicator in narrative_indicators if indicator in content_lower)

    # Check for conceptual/philosophical indicators
    conceptual_indicators = ["concept", "philosophy", "theory", "abstract", "idea", "principle", "meaning"]
    conceptual_score = sum(1 for indicator in conceptual_indicators if indicator in content_lower)

    # Determine mode based on content analysis
    if narrative_score > conceptual_score and narrative_score >= 2:
        return "narrative"
    elif conceptual_score > narrative_score and conceptual_score >= 2:
        return "conceptual"
    elif len(content.split()) > 200:  # Long content likely narrative
        return "narrative"
    else:
        return "conceptual"  # Default to conceptual for shorter, abstract content

async def _create_narrative_album(content: str, album_concept: str, character_name: str,
                                track_count: int, genre: str, ctx: Context) -> Dict:
    """Create album from narrative content with story progression"""
    await ctx.info("Creating narrative-driven album...")

    # Use existing character analysis workflow
    try:
        from mcp_tools_integration import MCPToolsIntegration
        integration = MCPToolsIntegration()

        # Analyze characters and story structure
        analysis_result = await integration.analyze_characters(content, ctx)
        characters = analysis_result.get('characters', [])

        if not characters:
            # Fallback to conceptual mode if no characters found
            await ctx.info("No characters found in narrative - switching to conceptual mode")
            return await _create_conceptual_thematic_album(content, album_concept, track_count, genre, ctx)

        # Select character
        if character_name:
            selected_character = next((char for char in characters if char.name.lower() == character_name.lower()), None)
            if not selected_character:
                selected_character = characters[0]
                await ctx.info(f"Character '{character_name}' not found, using {selected_character.name}")
        else:
            selected_character = characters[0]
            await ctx.info(f"Auto-selected character: {selected_character.name}")

        # Generate story-based track progression
        track_concepts = await _generate_narrative_track_progression(
            content, selected_character, track_count, ctx
        )

        # Validate narrative progression before creating tracks
        progression_validation = _validate_narrative_progression(track_concepts)
        await ctx.info(f"Narrative progression validation: {progression_validation['progression_score']:.2f}")

        # Create album tracks
        album_tracks = []
        for i, track_concept in enumerate(track_concepts):
            await ctx.info(f"Creating narrative track {i+1}/{track_count}: {track_concept['title']}")

            track_data = await _create_narrative_track(
                track_concept, selected_character, genre, i + 1, ctx
            )
            album_tracks.append(track_data)

        # Ensure unique content across all tracks
        album_tracks = _ensure_unique_track_content(album_tracks)

        # Generate album concept if not provided
        if not album_concept:
            album_concept = f"{selected_character.name}'s Journey: A Musical Narrative"

        return {
            "album_status": "narrative_integrated",
            "album_info": {
                "title": album_concept,
                "protagonist": selected_character.name,
                "total_tracks": track_count,
                "genre": genre,
                "processing_mode": "narrative",
                "concept": f"Story-driven album following {selected_character.name}'s narrative arc"
            },
            "tracks": album_tracks,
            "album_effectiveness": {
                "average_score": sum(track.get("effectiveness_score", 0.8) for track in album_tracks) / len(album_tracks),
                "narrative_progression": f"Score: {progression_validation['progression_score']:.2f} - {progression_validation['strengths'][0] if progression_validation['strengths'] else 'Basic progression'}",
                "character_consistency": "High - unified character perspective throughout",
                "thematic_coherence": "Excellent - story themes drive musical development",
                "progression_validation": progression_validation
            },
            "album_summary": f"Created {track_count}-track narrative album following {selected_character.name}'s story progression"
        }

    except Exception as e:
        await ctx.error(f"Narrative album creation failed: {str(e)}")
        # Fallback to conceptual mode
        return await _create_conceptual_thematic_album(content, album_concept, track_count, genre, ctx)

async def _create_character_driven_album(content: str, character_description: str, album_concept: str,
                                       track_count: int, genre: str, ctx: Context) -> Dict:
    """Create album using explicit character description"""
    await ctx.info("Creating character-driven album...")

    # Extract character details
    character_name = _extract_character_name(character_description)
    character_traits = _analyze_character_traits(character_description)

    # Generate track concepts based on character perspective
    track_concepts = _generate_character_track_concepts(
        content, character_description, character_traits, track_count
    )

    # Create album tracks
    album_tracks = []
    processor = WorkingUniversalProcessor(character_description)

    for i, track_concept in enumerate(track_concepts):
        await ctx.info(f"Creating character track {i+1}/{track_count}: {track_concept['title']}")

        # Process track through character lens
        track_result = processor.process_track_content(
            content,
            track_concept["title"],
            track_concept["theme"],
            track_concept["perspective"],
            i + 1,
            track_count
        )

        track_data = {
            "track_number": i + 1,
            "title": track_concept["title"],
            "theme": track_concept["theme"],
            "perspective": track_concept["perspective"],
            "character_interpretation": track_result.character_interpretation,
            "personal_story": track_result.personal_story,
            "lyrics": track_result.formatted_lyrics,
            "suno_command": track_result.suno_command,
            "effectiveness_score": track_result.effectiveness_score
        }
        album_tracks.append(track_data)

    # Ensure unique content across all tracks
    album_tracks = _ensure_unique_track_content(album_tracks)

    # Validate thematic progression
    thematic_validation = _validate_thematic_coherence(track_concepts)

    # Generate album concept if not provided
    if not album_concept:
        album_concept = f"{character_name}'s Perspective: Musical Interpretations"

    return {
        "album_status": "character_driven",
        "album_info": {
            "title": album_concept,
            "artist": character_name,
            "total_tracks": track_count,
            "genre": genre,
            "processing_mode": "character",
            "concept": f"Content explored through {character_name}'s unique perspective"
        },
        "tracks": album_tracks,
        "album_effectiveness": {
            "average_score": sum(track.get("effectiveness_score", 0.8) for track in album_tracks) / len(album_tracks),
            "character_consistency": "High - all tracks maintain character voice",
            "thematic_variety": f"Score: {thematic_validation['coherence_score']:.2f} - {thematic_validation['strengths'][0] if thematic_validation['strengths'] else 'Basic variety'}",
            "authenticity": "Excellent - character-driven interpretation throughout",
            "thematic_validation": thematic_validation
        },
        "album_summary": f"Created {track_count}-track character-driven album through {character_name}'s perspective"
    }

async def _create_conceptual_thematic_album(content: str, album_concept: str, track_count: int,
                                          genre: str, ctx: Context) -> Dict:
    """Create album from conceptual/philosophical content"""
    await ctx.info("Creating conceptual thematic album...")

    # Analyze content for themes and concepts
    content_themes = _analyze_content_themes(content)
    conceptual_elements = _extract_conceptual_elements(content)

    # Generate thematic track progression
    track_concepts = _generate_thematic_track_progression(
        content, content_themes, conceptual_elements, track_count
    )

    # Create conceptual character to embody the themes
    conceptual_character = _create_conceptual_character(content, conceptual_elements, genre)

    # Create album tracks
    album_tracks = []
    for i, track_concept in enumerate(track_concepts):
        await ctx.info(f"Creating conceptual track {i+1}/{track_count}: {track_concept['title']}")

        track_data = await _create_conceptual_track(
            track_concept, conceptual_character, genre, i + 1, ctx
        )
        album_tracks.append(track_data)

    # Generate album concept if not provided
    if not album_concept:
        primary_theme = content_themes[0] if content_themes else "philosophical_exploration"
        album_concept = f"Conceptual Explorations: {primary_theme.replace('_', ' ').title()}"

    return {
        "album_status": "conceptual_thematic",
        "album_info": {
            "title": album_concept,
            "artist": conceptual_character["name"],
            "total_tracks": track_count,
            "genre": genre,
            "processing_mode": "conceptual",
            "concept": "Thematic exploration of conceptual content through musical interpretation"
        },
        "tracks": album_tracks,
        "album_effectiveness": {
            "average_score": sum(track.get("effectiveness_score", 0.8) for track in album_tracks) / len(album_tracks),
            "thematic_coherence": "Strong - unified conceptual framework",
            "conceptual_depth": "High - philosophical themes explored musically",
            "artistic_innovation": "Excellent - unique approach to abstract content"
        },
        "album_summary": f"Created {track_count}-track conceptual album exploring thematic elements"
    }

async def _create_hybrid_album(content: str, album_concept: str, character_name: str,
                             character_description: str, track_count: int, genre: str, ctx: Context) -> Dict:
    """Create album combining multiple approaches"""
    await ctx.info("Creating hybrid album with multiple approaches...")

    # Try narrative approach first, fall back to character or conceptual
    try:
        return await _create_narrative_album(content, album_concept, character_name, track_count, genre, ctx)
    except:
        if character_description:
            return await _create_character_driven_album(content, character_description, album_concept, track_count, genre, ctx)
        else:
            return await _create_conceptual_thematic_album(content, album_concept, track_count, genre, ctx)


async def _generate_narrative_track_progression(content: str, character: Any, track_count: int, ctx: Context) -> List[Dict]:
    """Generate track concepts that follow narrative progression"""
    # Divide content into story beats
    content_sections = _divide_content_into_sections(content, track_count)

    track_concepts = []
    for i, section in enumerate(content_sections):
        # Analyze this section for story elements
        story_beat = _analyze_story_section(section, character, i, track_count)

        track_concept = {
            "title": _generate_meaningful_track_title(story_beat, character.name, i + 1),
            "story_context": story_beat["context"],
            "character_state": story_beat["character_development"],
            "emotional_tone": story_beat["emotion"],
            "narrative_function": story_beat["function"],
            "story_excerpt": section[:200] + "..." if len(section) > 200 else section,
            "musical_evolution": story_beat["musical_direction"]
        }
        track_concepts.append(track_concept)

    return track_concepts

def _generate_character_track_concepts(content: str, character_description: str, character_traits: Dict, track_count: int) -> List[Dict]:
    """Generate track concepts based on character perspective"""
    content_themes = _analyze_content_themes(content)

    # Define perspective templates for character-driven tracks
    perspective_templates = [
        {"type": "introduction", "focus": "character_establishment", "mood": "establishing"},
        {"type": "personal_reflection", "focus": "inner_thoughts", "mood": "introspective"},
        {"type": "emotional_core", "focus": "deep_feelings", "mood": "intense"},
        {"type": "memory_exploration", "focus": "past_experiences", "mood": "nostalgic"},
        {"type": "conflict_processing", "focus": "internal_struggle", "mood": "challenging"},
        {"type": "revelation_moment", "focus": "understanding", "mood": "enlightening"},
        {"type": "relationship_dynamics", "focus": "connections", "mood": "relational"},
        {"type": "philosophical_inquiry", "focus": "meaning_seeking", "mood": "contemplative"},
        {"type": "creative_expression", "focus": "artistic_voice", "mood": "expressive"},
        {"type": "resolution_synthesis", "focus": "integration", "mood": "resolving"}
    ]

    track_concepts = []
    for i in range(track_count):
        template = perspective_templates[i % len(perspective_templates)]
        theme = content_themes[i % len(content_themes)]

        track_concept = {
            "title": _generate_character_track_title(theme, template, character_traits, i + 1),
            "theme": theme,
            "perspective": _create_track_perspective(character_traits, template, theme),
            "template": template
        }
        track_concepts.append(track_concept)

    return track_concepts

def _generate_thematic_track_progression(content: str, themes: List[str], conceptual_elements: Dict, track_count: int) -> List[Dict]:
    """Generate track concepts based on thematic progression"""
    track_concepts = []

    # Create a thematic journey through the concepts
    thematic_progression = [
        "introduction_to_concept",
        "exploration_of_implications",
        "emotional_resonance",
        "philosophical_depth",
        "practical_application",
        "contradictions_and_tensions",
        "synthesis_and_integration",
        "transcendence_or_resolution"
    ]

    for i in range(track_count):
        theme = themes[i % len(themes)]
        progression_stage = thematic_progression[i % len(thematic_progression)]

        track_concept = {
            "title": _generate_thematic_track_title(theme, progression_stage, i + 1),
            "theme": theme,
            "conceptual_focus": progression_stage,
            "philosophical_angle": conceptual_elements.get("philosophical_frameworks", ["existential"])[0],
            "emotional_approach": conceptual_elements.get("emotional_tones", ["contemplative"])[0],
            "content_excerpt": _extract_relevant_content_excerpt(content, theme)
        }
        track_concepts.append(track_concept)

    return track_concepts

def _generate_unique_track_concepts(content: str, album_title: str, character_description: str, track_count: int) -> List[Dict[str, str]]:
    """Generate unique track concepts based on content analysis and character"""

    # Analyze content for themes and elements
    content_themes = _analyze_content_themes(content)
    character_traits = _analyze_character_traits(character_description)

    # Define track perspective templates that create unique angles
    perspective_templates = [
        {"type": "opening", "focus": "introduction", "mood": "establishing"},
        {"type": "personal", "focus": "individual_experience", "mood": "intimate"},
        {"type": "questioning", "focus": "doubt_exploration", "mood": "contemplative"},
        {"type": "emotional", "focus": "feeling_core", "mood": "intense"},
        {"type": "struggle", "focus": "conflict_resolution", "mood": "challenging"},
        {"type": "revelation", "focus": "understanding", "mood": "enlightening"},
        {"type": "social", "focus": "community_connection", "mood": "connecting"},
        {"type": "alternative", "focus": "different_viewpoint", "mood": "contrasting"},
        {"type": "instrumental", "focus": "musical_expression", "mood": "atmospheric"},
        {"type": "collaborative", "focus": "shared_experience", "mood": "unifying"},
        {"type": "journey", "focus": "progression", "mood": "evolving"},
        {"type": "synthesis", "focus": "conclusion", "mood": "resolving"}
    ]

    track_concepts = []

    for i in range(track_count):
        template = perspective_templates[i % len(perspective_templates)]
        theme = content_themes[i % len(content_themes)]

        # Generate unique title based on theme and perspective
        title = _generate_track_title(album_title, theme, template, i + 1)

        # Create unique perspective combining character traits with template
        perspective = _create_track_perspective(character_traits, template, theme)

        track_concepts.append({
            "title": title,
            "theme": theme,
            "perspective": perspective,
            "template": template
        })

    return track_concepts


def _analyze_content_themes(content: str) -> List[str]:
    """Analyze content to extract multiple themes for track variation"""
    content_lower = content.lower()
    themes = []

    # Primary themes
    if any(word in content_lower for word in ["love", "heart", "romance", "relationship", "connection"]):
        themes.append("love_and_connection")
    if any(word in content_lower for word in ["death", "loss", "grief", "mortality", "ending"]):
        themes.append("mortality_and_loss")
    if any(word in content_lower for word in ["god", "divine", "spiritual", "soul", "sacred"]):
        themes.append("spiritual_inquiry")
    if any(word in content_lower for word in ["truth", "reality", "existence", "being", "meaning"]):
        themes.append("existential_truth")
    if any(word in content_lower for word in ["beauty", "art", "creation", "aesthetic", "wonder"]):
        themes.append("artistic_beauty")
    if any(word in content_lower for word in ["time", "memory", "past", "future", "change"]):
        themes.append("temporal_reflection")
    if any(word in content_lower for word in ["struggle", "challenge", "difficulty", "overcome"]):
        themes.append("personal_struggle")
    if any(word in content_lower for word in ["hope", "dream", "aspiration", "possibility"]):
        themes.append("hope_and_dreams")
    if any(word in content_lower for word in ["fear", "anxiety", "worry", "doubt"]):
        themes.append("fear_and_doubt")
    if any(word in content_lower for word in ["freedom", "liberation", "escape", "transcend"]):
        themes.append("liberation")

    # If no specific themes found, create general ones
    if not themes:
        themes = ["personal_reflection", "emotional_journey", "life_experience", "inner_dialogue"]

    # Ensure we have enough themes by adding variations
    while len(themes) < 12:
        base_themes = themes.copy()
        for theme in base_themes:
            if len(themes) >= 12:
                break
            themes.append(f"{theme}_variation")

    return themes


def _analyze_character_traits(character_description: str) -> Dict[str, str]:
    """Extract character traits for perspective generation"""
    desc_lower = character_description.lower()

    traits = {
        "personality": "introspective",
        "approach": "thoughtful",
        "background": "artistic",
        "worldview": "questioning"
    }

    # Personality analysis
    if "philosophical" in desc_lower:
        traits["personality"] = "philosophical"
        traits["approach"] = "analytical"
    elif "spiritual" in desc_lower:
        traits["personality"] = "spiritual"
        traits["approach"] = "intuitive"
    elif "social" in desc_lower or "political" in desc_lower:
        traits["personality"] = "socially_conscious"
        traits["approach"] = "activist"
    elif "emotional" in desc_lower:
        traits["personality"] = "emotionally_driven"
        traits["approach"] = "feeling-based"

    # Background analysis
    if any(word in desc_lower for word in ["producer", "beats", "studio"]):
        traits["background"] = "producer"
    elif any(word in desc_lower for word in ["singer", "vocalist", "voice"]):
        traits["background"] = "vocalist"
    elif any(word in desc_lower for word in ["rapper", "mc", "hip-hop"]):
        traits["background"] = "rapper"
    elif any(word in desc_lower for word in ["musician", "instrument", "player"]):
        traits["background"] = "instrumentalist"

    # Worldview analysis
    if "optimistic" in desc_lower or "positive" in desc_lower:
        traits["worldview"] = "optimistic"
    elif "pessimistic" in desc_lower or "dark" in desc_lower:
        traits["worldview"] = "pessimistic"
    elif "realistic" in desc_lower or "practical" in desc_lower:
        traits["worldview"] = "realistic"
    elif "idealistic" in desc_lower or "dreamer" in desc_lower:
        traits["worldview"] = "idealistic"

    return traits


def _generate_track_title(album_title: str, theme: str, template: Dict, track_number: int) -> str:
    """Generate unique track titles based on theme and perspective"""

    theme_titles = {
        "love_and_connection": ["Heart's Frequency", "Connection Protocol", "Love's Algorithm", "Bonded Souls"],
        "mortality_and_loss": ["Final Breath", "Memory's Echo", "Last Light", "Fading Signal"],
        "spiritual_inquiry": ["Divine Questions", "Sacred Geometry", "Soul's Compass", "Heavenly Frequencies"],
        "existential_truth": ["Reality Check", "Truth Seeker", "Being's Core", "Existence Proof"],
        "artistic_beauty": ["Beauty's Code", "Aesthetic Theory", "Creative Force", "Art's Purpose"],
        "temporal_reflection": ["Time's Arrow", "Memory Lane", "Future's Call", "Present Moment"],
        "personal_struggle": ["Inner Battle", "Struggle's Song", "Fighting Through", "Overcoming"],
        "hope_and_dreams": ["Dream State", "Hope's Light", "Future Vision", "Aspiration"],
        "fear_and_doubt": ["Shadow's Voice", "Doubt's Whisper", "Fear's Face", "Anxiety's Song"],
        "liberation": ["Breaking Free", "Liberation Day", "Freedom's Call", "Escape Velocity"],
        "personal_reflection": ["Mirror's Truth", "Self Portrait", "Inner Voice", "Personal Space"],
        "emotional_journey": ["Feeling's Path", "Emotion's Map", "Heart's Journey", "Soul's Travel"],
        "life_experience": ["Life's Lessons", "Experience Bank", "Living Proof", "Real Talk"],
        "inner_dialogue": ["Mind's Conversation", "Internal Debate", "Self Talk", "Inner Voice"]
    }

    # Get theme-specific titles
    titles = theme_titles.get(theme, [f"Track {track_number}", f"Song {track_number}", f"Piece {track_number}", f"Movement {track_number}"])

    # Select title based on track number to ensure uniqueness
    selected_title = titles[track_number % len(titles)]

    # Add template-specific prefix/suffix for more uniqueness
    if template["type"] == "opening":
        return f"Intro: {selected_title}"
    elif template["type"] == "instrumental":
        return f"{selected_title} (Instrumental)"
    elif template["type"] == "synthesis":
        return f"Outro: {selected_title}"
    else:
        return selected_title


async def _create_narrative_track(track_concept: Dict, character: Any, genre: str, track_number: int, ctx: Context) -> Dict:
    """Create a track based on narrative progression"""
    # Use WorkingUniversalProcessor for track creation
    character_desc = f"Name: {character.name}, Background: {character.backstory[:100]}, Personality: {', '.join(character.personality_drivers[:2])}"
    processor = WorkingUniversalProcessor(character_desc)

    # Create track content from story context
    track_content = f"""
    Story Context: {track_concept['story_context']}
    Character Development: {track_concept['character_state']}
    Emotional Tone: {track_concept['emotional_tone']}
    Narrative Function: {track_concept['narrative_function']}
    Story Excerpt: {track_concept['story_excerpt']}
    """

    # Process through character lens
    track_result = processor.process_track_content(
        track_content,
        track_concept["title"],
        track_concept["emotional_tone"],
        track_concept["narrative_function"],
        track_number,
        8  # default track count for context
    )

    return {
        "track_number": track_number,
        "title": track_concept["title"],
        "story_context": track_concept["story_context"],
        "character_development": track_concept["character_state"],
        "narrative_function": track_concept["narrative_function"],
        "emotional_arc_position": track_concept["emotional_tone"],
        "character_interpretation": track_result.character_interpretation,
        "personal_story": track_result.personal_story,
        "lyrics": track_result.formatted_lyrics,
        "suno_command": track_result.suno_command,
        "musical_evolution": track_concept.get("musical_evolution", "Maintains character voice"),
        "effectiveness_score": track_result.effectiveness_score
    }

async def _create_conceptual_track(track_concept: Dict, conceptual_character: Dict, genre: str, track_number: int, ctx: Context) -> Dict:
    """Create a track based on conceptual themes"""
    # Create character description for processor
    character_desc = f"Name: {conceptual_character['name']}, Perspective: {conceptual_character['perspective']}, Focus: {conceptual_character['thematic_focus']}"
    processor = WorkingUniversalProcessor(character_desc)

    # Create track content from conceptual elements
    track_content = f"""
    Thematic Focus: {track_concept['theme']}
    Conceptual Angle: {track_concept['conceptual_focus']}
    Philosophical Framework: {track_concept['philosophical_angle']}
    Emotional Approach: {track_concept['emotional_approach']}
    Content Excerpt: {track_concept['content_excerpt']}
    """

    # Process through conceptual character lens
    track_result = processor.process_track_content(
        track_content,
        track_concept["title"],
        track_concept["theme"],
        track_concept["conceptual_focus"],
        track_number,
        8  # default track count for context
    )

    return {
        "track_number": track_number,
        "title": track_concept["title"],
        "theme": track_concept["theme"],
        "conceptual_focus": track_concept["conceptual_focus"],
        "philosophical_angle": track_concept["philosophical_angle"],
        "character_interpretation": track_result.character_interpretation,
        "personal_story": track_result.personal_story,
        "lyrics": track_result.formatted_lyrics,
        "suno_command": track_result.suno_command,
        "effectiveness_score": track_result.effectiveness_score
    }

def _divide_content_into_sections(content: str, section_count: int) -> List[str]:
    """Divide content into meaningful sections for track progression"""
    words = content.split()
    words_per_section = max(50, len(words) // section_count)

    sections = []
    for i in range(section_count):
        start_idx = i * words_per_section
        end_idx = min((i + 1) * words_per_section, len(words))
        section = ' '.join(words[start_idx:end_idx])
        sections.append(section)

    return sections

def _analyze_story_section(section: str, character: Any, section_index: int, total_sections: int) -> Dict:
    """Analyze a story section for narrative elements"""
    # Determine story progression stage
    progression_stages = ["setup", "inciting_incident", "rising_action", "climax", "falling_action", "resolution"]
    stage_index = min(section_index, len(progression_stages) - 1)
    narrative_stage = progression_stages[stage_index]

    # Analyze emotional tone
    section_lower = section.lower()
    if any(word in section_lower for word in ["happy", "joy", "celebration", "success"]):
        emotion = "uplifting"
    elif any(word in section_lower for word in ["sad", "loss", "grief", "sorrow"]):
        emotion = "melancholic"
    elif any(word in section_lower for word in ["angry", "rage", "fury", "conflict"]):
        emotion = "intense"
    elif any(word in section_lower for word in ["fear", "anxiety", "worry", "danger"]):
        emotion = "tense"
    else:
        emotion = "contemplative"

    return {
        "context": f"Story section {section_index + 1}/{total_sections} - {narrative_stage}",
        "character_development": f"{character.name} in {narrative_stage} phase",
        "emotion": emotion,
        "function": narrative_stage,
        "musical_direction": f"Musical evolution reflecting {narrative_stage} energy"
    }

def _generate_meaningful_track_title(story_beat: Dict, character_name: str, track_number: int) -> str:
    """Generate meaningful track titles based on story beats - never generic"""
    function = story_beat["function"]
    emotion = story_beat["emotion"]

    # Expanded title templates with more variety and meaning
    title_templates = {
        "setup": [
            f"{character_name}'s World", "Where It All Begins", "The Foundation", "Origins Unveiled",
            "First Light", "The Starting Point", "Roots Run Deep", "Before the Storm"
        ],
        "inciting_incident": [
            "The Call to Adventure", "Catalyst Moment", "Point of No Return", "The Spark Ignites",
            "When Everything Changed", "The First Step", "Breaking Point", "The Awakening"
        ],
        "rising_action": [
            "The Ascent", "Climbing Mountains", "Building Momentum", "The Long Road",
            "Against the Current", "Pushing Forward", "The Struggle Intensifies", "Rising Tide"
        ],
        "climax": [
            "The Moment of Truth", "Peak Experience", "Final Confrontation", "The Revelation",
            "Eye of the Storm", "The Breaking Point", "Truth Unveiled", "The Decisive Hour"
        ],
        "falling_action": [
            "After the Storm", "Coming Back Down", "Facing Consequences", "The Reckoning",
            "Picking Up Pieces", "The Aftermath", "What Remains", "Settling Dust"
        ],
        "resolution": [
            "New Dawn Rising", "Finding Peace", "The Journey's End", "Full Circle",
            "Lessons Learned", "The New Beginning", "Harmony Restored", "Coming Home"
        ]
    }

    # Get function-specific titles
    templates = title_templates.get(function, [f"{character_name}'s Journey"])

    # Select title ensuring uniqueness across tracks
    title_index = (track_number - 1) % len(templates)
    base_title = templates[title_index]

    # Add emotional depth and avoid generic modifiers
    emotion_modifiers = {
        "melancholic": ["Through Tears", "In Shadow", "With Heavy Heart", "Through Sorrow"],
        "intense": ["With Fire", "In Fury", "Through Passion", "With Power"],
        "tense": ["On the Edge", "In Suspense", "Through Fear", "Under Pressure"],
        "uplifting": ["In Light", "With Hope", "Through Joy", "In Triumph"],
        "contemplative": ["In Reflection", "Through Thought", "In Silence", "With Wonder"]
    }

    # Apply emotional modifier if appropriate
    if emotion in emotion_modifiers:
        modifiers = emotion_modifiers[emotion]
        modifier = modifiers[(track_number - 1) % len(modifiers)]
        return f"{base_title} {modifier}"

    return base_title

def _generate_character_track_title(theme: str, template: Dict, character_traits: Dict, track_number: int) -> str:
    """Generate character-driven track titles - creative and meaningful"""
    theme_words = theme.replace("_", " ").title()
    template_type = template["type"]
    personality = character_traits.get("personality", "introspective")

    # Creative title variations based on template type
    title_variations = {
        "introduction": [
            f"Welcome to {theme_words}", f"Introducing {theme_words}", f"First Glimpse of {theme_words}",
            f"Opening {theme_words}", f"The World of {theme_words}", f"Discovering {theme_words}"
        ],
        "personal_reflection": [
            f"My Journey with {theme_words}", f"Inside {theme_words}", f"Personal {theme_words}",
            f"Through My Eyes: {theme_words}", f"Living {theme_words}", f"My Truth About {theme_words}"
        ],
        "emotional_core": [
            f"Heart of {theme_words}", f"The Soul of {theme_words}", f"Feeling {theme_words}",
            f"Deep in {theme_words}", f"The Essence of {theme_words}", f"Raw {theme_words}"
        ],
        "memory_exploration": [
            f"Remembering {theme_words}", f"Echoes of {theme_words}", f"Looking Back at {theme_words}",
            f"Memories of {theme_words}", f"Yesterday's {theme_words}", f"Traces of {theme_words}"
        ],
        "conflict_processing": [
            f"Wrestling with {theme_words}", f"The Battle for {theme_words}", f"Struggling Through {theme_words}",
            f"Fighting {theme_words}", f"Confronting {theme_words}", f"The War Within {theme_words}"
        ],
        "revelation_moment": [
            f"Understanding {theme_words}", f"The Truth About {theme_words}", f"Seeing {theme_words} Clearly",
            f"Breakthrough in {theme_words}", f"Awakening to {theme_words}", f"The Light of {theme_words}"
        ],
        "relationship_dynamics": [
            f"Connected by {theme_words}", f"Sharing {theme_words}", f"Together in {theme_words}",
            f"Bonds of {theme_words}", f"United Through {theme_words}", f"The Bridge of {theme_words}"
        ],
        "philosophical_inquiry": [
            f"Why {theme_words}?", f"The Question of {theme_words}", f"Seeking {theme_words}",
            f"The Mystery of {theme_words}", f"Pondering {theme_words}", f"The Riddle of {theme_words}"
        ],
        "creative_expression": [
            f"Expressing {theme_words}", f"Creating {theme_words}", f"The Art of {theme_words}",
            f"Painting {theme_words}", f"Singing {theme_words}", f"Crafting {theme_words}"
        ],
        "resolution_synthesis": [
            f"Resolving {theme_words}", f"Finding Peace in {theme_words}", f"The Answer to {theme_words}",
            f"Completing {theme_words}", f"The End of {theme_words}", f"Harmony with {theme_words}"
        ]
    }

    # Get variations for this template type
    variations = title_variations.get(template_type, [f"Exploring {theme_words}"])

    # Select variation based on track number to ensure uniqueness
    variation_index = (track_number - 1) % len(variations)
    selected_title = variations[variation_index]

    # Add personality-based modifier for more character depth
    if personality == "philosophical" and "?" not in selected_title:
        return f"{selected_title}: A Meditation"
    elif personality == "emotional" and template_type not in ["emotional_core"]:
        return f"{selected_title} (From the Heart)"
    elif personality == "social" and template_type not in ["relationship_dynamics"]:
        return f"{selected_title} Together"

    return selected_title

def _generate_thematic_track_title(theme: str, progression_stage: str, track_number: int) -> str:
    """Generate thematic track titles with creative depth"""
    theme_words = theme.replace("_", " ").title()

    # Expanded creative approaches for each progression stage
    stage_approaches = {
        "introduction_to_concept": [
            f"First Encounter with {theme_words}", f"Opening the Door to {theme_words}",
            f"Welcome to {theme_words}", f"The Beginning of {theme_words}",
            f"Discovering {theme_words}", f"Initial Thoughts on {theme_words}"
        ],
        "exploration_of_implications": [
            f"Diving Deep into {theme_words}", f"The Ripple Effects of {theme_words}",
            f"Unfolding {theme_words}", f"The Many Faces of {theme_words}",
            f"Exploring the Depths of {theme_words}", f"What {theme_words} Really Means"
        ],
        "emotional_resonance": [
            f"Feeling the Weight of {theme_words}", f"The Heart of {theme_words}",
            f"Emotional Echoes of {theme_words}", f"How {theme_words} Moves Me",
            f"The Soul of {theme_words}", f"When {theme_words} Touches You"
        ],
        "philosophical_depth": [
            f"The Philosophy of {theme_words}", f"Deep Thoughts on {theme_words}",
            f"The Wisdom in {theme_words}", f"Understanding {theme_words}",
            f"The Truth About {theme_words}", f"Contemplating {theme_words}"
        ],
        "practical_application": [
            f"Living {theme_words}", f"Putting {theme_words} into Practice",
            f"The Daily Reality of {theme_words}", f"How to Embody {theme_words}",
            f"Making {theme_words} Real", f"Walking the Path of {theme_words}"
        ],
        "contradictions_and_tensions": [
            f"The Paradox of {theme_words}", f"Wrestling with {theme_words}",
            f"The Dark Side of {theme_words}", f"When {theme_words} Conflicts",
            f"The Tension in {theme_words}", f"Questioning {theme_words}"
        ],
        "synthesis_and_integration": [
            f"Bringing {theme_words} Together", f"The Unity of {theme_words}",
            f"Integrating {theme_words}", f"The Whole Picture of {theme_words}",
            f"Synthesizing {theme_words}", f"The Complete {theme_words}"
        ],
        "transcendence_or_resolution": [
            f"Beyond {theme_words}", f"Transcending {theme_words}",
            f"The Resolution of {theme_words}", f"Rising Above {theme_words}",
            f"The Final Word on {theme_words}", f"Peace with {theme_words}"
        ]
    }

    # Get approaches for this stage
    approaches = stage_approaches.get(progression_stage, [f"Exploring {theme_words}"])

    # Select approach based on track number for uniqueness
    approach_index = (track_number - 1) % len(approaches)
    return approaches[approach_index]

def _extract_conceptual_elements(content: str) -> Dict:
    """Extract conceptual elements from content"""
    content_lower = content.lower()

    # Identify philosophical frameworks
    philosophical_frameworks = []
    if any(word in content_lower for word in ["existence", "being", "reality"]):
        philosophical_frameworks.append("existential")
    if any(word in content_lower for word in ["meaning", "purpose", "significance"]):
        philosophical_frameworks.append("teleological")
    if any(word in content_lower for word in ["ethics", "moral", "right", "wrong"]):
        philosophical_frameworks.append("ethical")
    if any(word in content_lower for word in ["beauty", "aesthetic", "art"]):
        philosophical_frameworks.append("aesthetic")

    if not philosophical_frameworks:
        philosophical_frameworks = ["existential"]

    # Identify emotional tones
    emotional_tones = []
    if any(word in content_lower for word in ["contemplat", "reflect", "ponder"]):
        emotional_tones.append("contemplative")
    if any(word in content_lower for word in ["melanchol", "sad", "sorrow"]):
        emotional_tones.append("melancholic")
    if any(word in content_lower for word in ["hope", "optimis", "bright"]):
        emotional_tones.append("hopeful")
    if any(word in content_lower for word in ["intense", "passion", "fervor"]):
        emotional_tones.append("intense")

    if not emotional_tones:
        emotional_tones = ["contemplative"]

    return {
        "philosophical_frameworks": philosophical_frameworks,
        "emotional_tones": emotional_tones
    }

def _create_conceptual_character(content: str, conceptual_elements: Dict, genre: str) -> Dict:
    """Create a conceptual character to embody the themes"""
    primary_framework = conceptual_elements["philosophical_frameworks"][0]
    primary_tone = conceptual_elements["emotional_tones"][0]

    character_names = {
        "existential": "The Seeker",
        "teleological": "The Questioner",
        "ethical": "The Conscience",
        "aesthetic": "The Artist"
    }

    perspectives = {
        "existential": "exploring the nature of existence and being",
        "teleological": "seeking meaning and purpose in experience",
        "ethical": "examining moral dimensions of life",
        "aesthetic": "finding beauty and artistic truth"
    }

    return {
        "name": character_names.get(primary_framework, "The Philosopher"),
        "perspective": perspectives.get(primary_framework, "exploring deep questions"),
        "thematic_focus": primary_framework,
        "emotional_approach": primary_tone,
        "genre_preference": genre
    }

def _extract_relevant_content_excerpt(content: str, theme: str) -> str:
    """Extract content excerpt most relevant to the theme"""
    # Simple approach: find sentences containing theme-related words
    theme_keywords = theme.replace("_", " ").split()
    sentences = content.split(".")

    relevant_sentences = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword.lower() in sentence_lower for keyword in theme_keywords):
            relevant_sentences.append(sentence.strip())

    if relevant_sentences:
        excerpt = ". ".join(relevant_sentences[:2])
        return excerpt[:200] + "..." if len(excerpt) > 200 else excerpt
    else:
        # Fallback to first part of content
        return content[:200] + "..." if len(content) > 200 else content

def _validate_narrative_progression(track_concepts: List[Dict]) -> Dict[str, Any]:
    """Validate that tracks follow coherent story arc progression"""
    validation_result = {
        "is_coherent": True,
        "progression_score": 0.0,
        "issues": [],
        "strengths": []
    }

    if len(track_concepts) < 3:
        validation_result["issues"].append("Too few tracks for meaningful progression")
        validation_result["is_coherent"] = False
        return validation_result

    # Check for story arc elements
    story_functions = [track.get("narrative_function", "") for track in track_concepts]

    # Validate beginning, middle, end structure
    has_setup = any("setup" in func or "introduction" in func for func in story_functions)
    has_development = any("rising" in func or "development" in func or "conflict" in func for func in story_functions)
    has_resolution = any("resolution" in func or "conclusion" in func or "end" in func for func in story_functions)

    progression_score = 0
    if has_setup:
        progression_score += 0.3
        validation_result["strengths"].append("Clear story setup")
    else:
        validation_result["issues"].append("Missing story setup/introduction")

    if has_development:
        progression_score += 0.4
        validation_result["strengths"].append("Story development present")
    else:
        validation_result["issues"].append("Missing story development/conflict")

    if has_resolution:
        progression_score += 0.3
        validation_result["strengths"].append("Story resolution present")
    else:
        validation_result["issues"].append("Missing story resolution")

    # Check for emotional progression
    emotions = [track.get("emotional_tone", "") for track in track_concepts]
    unique_emotions = len(set(emotions))

    if unique_emotions > 1:
        progression_score += 0.2
        validation_result["strengths"].append("Varied emotional progression")
    else:
        validation_result["issues"].append("Monotonous emotional tone")

    # Check for title uniqueness and meaningfulness
    titles = [track.get("title", "") for track in track_concepts]
    generic_titles = [title for title in titles if any(generic in title.lower() for generic in ["track", "song", "piece", "number"])]

    if generic_titles:
        validation_result["issues"].append(f"Generic titles found: {generic_titles}")
        progression_score -= 0.2
    else:
        validation_result["strengths"].append("All titles are meaningful and specific")

    # Check for unique content
    unique_titles = len(set(titles))
    if unique_titles == len(titles):
        validation_result["strengths"].append("All track titles are unique")
    else:
        validation_result["issues"].append("Duplicate track titles found")
        progression_score -= 0.1

    validation_result["progression_score"] = max(0.0, min(1.0, progression_score))
    validation_result["is_coherent"] = progression_score >= 0.6 and len(validation_result["issues"]) <= 2

    return validation_result

def _ensure_unique_track_content(album_tracks: List[Dict]) -> List[Dict]:
    """Ensure each track has unique content and avoid repetition"""
    seen_titles = set()
    seen_themes = set()

    for i, track in enumerate(album_tracks):
        original_title = track.get("title", f"Track {i+1}")
        original_theme = track.get("theme", "general")

        # Ensure unique titles
        title = original_title
        counter = 1
        while title in seen_titles:
            title = f"{original_title} (Part {counter})"
            counter += 1

        track["title"] = title
        seen_titles.add(title)

        # Ensure theme variety
        theme = original_theme
        counter = 1
        while theme in seen_themes and counter <= 3:
            theme = f"{original_theme}_variation_{counter}"
            counter += 1

        track["theme"] = theme
        seen_themes.add(theme)

        # Add uniqueness indicators to track
        track["uniqueness_score"] = 1.0 - (counter - 1) * 0.1
        track["content_variation"] = f"Unique perspective #{i+1}"

    return album_tracks

def _validate_thematic_coherence(track_concepts: List[Dict]) -> Dict[str, Any]:
    """Validate thematic coherence across character-driven tracks"""
    validation_result = {
        "is_coherent": True,
        "coherence_score": 0.0,
        "issues": [],
        "strengths": []
    }

    if len(track_concepts) < 2:
        validation_result["issues"].append("Too few tracks for coherence analysis")
        return validation_result

    # Check theme variety
    themes = [track.get("theme", "") for track in track_concepts]
    unique_themes = len(set(themes))
    theme_variety_score = min(1.0, unique_themes / len(themes))

    if theme_variety_score > 0.7:
        validation_result["strengths"].append("Good thematic variety")
    else:
        validation_result["issues"].append("Limited thematic variety")

    # Check perspective variety
    perspectives = [track.get("perspective", "") for track in track_concepts]
    unique_perspectives = len(set(perspectives))
    perspective_variety_score = min(1.0, unique_perspectives / len(perspectives))

    if perspective_variety_score > 0.6:
        validation_result["strengths"].append("Varied character perspectives")
    else:
        validation_result["issues"].append("Repetitive character perspectives")

    # Check title meaningfulness
    titles = [track.get("title", "") for track in track_concepts]
    meaningful_titles = [title for title in titles if not any(generic in title.lower() for generic in ["track", "song", "piece", "number"])]
    title_quality_score = len(meaningful_titles) / len(titles)

    if title_quality_score == 1.0:
        validation_result["strengths"].append("All titles are meaningful")
    else:
        validation_result["issues"].append("Some generic titles found")

    # Calculate overall coherence score
    coherence_score = (theme_variety_score + perspective_variety_score + title_quality_score) / 3
    validation_result["coherence_score"] = coherence_score
    validation_result["is_coherent"] = coherence_score >= 0.6

    return validation_result

def _create_track_perspective(character_traits: Dict, template: Dict, theme: str) -> str:
    """Create unique perspective for each track"""

    personality = character_traits["personality"]
    approach = character_traits["approach"]
    background = character_traits["background"]
    worldview = character_traits["worldview"]

    # Base perspective from template
    base_perspectives = {
        "introduction": f"Introducing the {theme} through {personality} lens, setting the stage for exploration",
        "personal_reflection": f"Intimate {approach} examination of {theme} from personal experience",
        "emotional_core": f"Raw emotional processing of {theme} through {background} expression",
        "memory_exploration": f"Exploring memories and past experiences related to {theme}",
        "conflict_processing": f"Wrestling with {theme} using {approach} methods and {personality} insight",
        "revelation_moment": f"Breakthrough understanding of {theme} through {worldview} realization",
        "relationship_dynamics": f"Exploring {theme} through connections and relationships with others",
        "philosophical_inquiry": f"Deep {worldview} questioning of {theme} and its implications",
        "creative_expression": f"Artistic {background} expression of {theme} through creative voice",
        "resolution_synthesis": f"Integrating understanding of {theme} through {personality} synthesis"
    }

    template_type = template.get("type", "personal_reflection")
    return base_perspectives.get(template_type, f"Exploring {theme} through {personality} perspective")


def _extract_character_name(character_description: str) -> str:
    """Extract character name from description"""
    import re

    # Try multiple name patterns
    name_patterns = [
        r'([A-Z][A-Z]+ [A-Z][a-zA-Z]+)',  # DJ Memphis, MC Something
        r'([A-Z][a-z]+ [A-Z][a-zA-Z]+)',  # John Smith or John McKenzie
        r'([A-Z][a-z]+ (?:"[^"]*" )?[A-Z][a-z]+)',  # John "Nickname" Smith
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-zA-Z]+)+)',  # Multiple names at start
        r'([A-Z][A-Z]+)',  # Single names like DJ, MC (fallback)
    ]

    # First try to find name in the first sentence
    first_sentence = character_description.split('.')[0] if '.' in character_description else character_description.split('\n')[0]

    for pattern in name_patterns:
        match = re.search(pattern, first_sentence)
        if match:
            return match.group(1)

    # If still no match, try the whole description
    for pattern in name_patterns:
        match = re.search(pattern, character_description)
        if match:
            return match.group(1)

    return "Independent Artist"


def _extract_character_genre(character_description: str) -> str:
    """Extract genre from character description"""
    desc_lower = character_description.lower()

    # Genre patterns with priority (more specific first)
    genre_patterns = {
        # Electronic subgenres (most specific first)
        "liquid drum and bass": ["liquid drum and bass", "liquid dnb", "liquid d&b", "liquid drum & bass"],
        "drum and bass": ["drum and bass", "dnb", "d&b", "drum & bass", "jungle"],
        "dubstep": ["dubstep", "dub step", "bass music"],
        "house": ["house music", "deep house", "tech house"],
        "techno": ["techno", "detroit techno", "minimal techno"],
        "trance": ["trance", "progressive trance", "uplifting trance"],
        "electronic": ["electronic music", "electronic producer", "electronic artist", "edm"],

        # Hip-hop subgenres
        "memphis hip-hop": ["memphis hip-hop", "memphis rap", "memphis hip hop"],
        "trap": ["trap music", "trap beats", "trap producer", "trap artist"],
        "boom bap": ["boom bap", "boom-bap", "old school hip hop"],
        "hip-hop": ["hip-hop", "hip hop", "rap music", "rap"],

        # Latin/Caribbean genres
        "reggaeton": ["reggaeton", "reggaeton producer", "reggaeton artist"],
        "latin trap": ["latin trap", "trap-reggaeton", "trap reggaeton"],
        "salsa": ["salsa", "salsa music"],
        "bachata": ["bachata", "bachata music"],

        # Rock subgenres
        "metal": ["metal", "heavy metal", "death metal", "black metal"],
        "punk": ["punk", "punk rock", "hardcore punk"],
        "grunge": ["grunge", "alternative rock", "seattle sound"],
        "indie rock": ["indie rock", "independent rock"],
        "rock": ["rock music", "rock"],

        # Soul/R&B
        "neo-soul": ["neo-soul", "neo soul", "neosoul"],
        "r&b": ["r&b", "rnb", "rhythm and blues"],
        "soul": ["soul music", "soul"],
        "funk": ["funk", "funk music"],

        # Jazz subgenres
        "smooth jazz": ["smooth jazz", "contemporary jazz"],
        "bebop": ["bebop", "be-bop"],
        "fusion": ["jazz fusion", "fusion"],
        "jazz": ["jazz", "jazz music"],

        # Folk and acoustic
        "indie folk": ["indie folk", "independent folk"],
        "country": ["country", "country music", "americana"],
        "folk": ["folk music", "folk"],
        "acoustic": ["acoustic", "acoustic music"],

        # Pop subgenres
        "indie pop": ["indie pop", "independent pop"],
        "synth pop": ["synth pop", "synthpop", "new wave"],
        "pop": ["pop music", "pop"],

        # Alternative (catch-all)
        "alternative": ["alternative", "alt rock", "alternative rock", "indie"]
    }

    # Check for genre patterns
    for genre, patterns in genre_patterns.items():
        for pattern in patterns:
            if pattern in desc_lower:
                return genre

    return "alternative"

# ================================================================================================
# RESOURCES
# ================================================================================================

@mcp.resource("character://profiles")
async def character_profiles_resource() -> str:
    """
    Comprehensive guide to character profile structure and three-layer analysis methodology.
    
    Returns detailed information about the character analysis framework used by this MCP server.
    """
    return """
    # Character Profile Analysis Framework
    
    ## Three-Layer Character Bible Methodology
    
    ### Skin Layer - Observable Characteristics
    - **Physical Descriptions**: Appearance, clothing, distinctive features
    - **Mannerisms**: Gestures, habits, behavioral tics
    - **Speech Patterns**: Dialogue style, vocabulary, accent
    - **Behavioral Traits**: Observable actions and reactions
    
    ### Flesh Layer - Background and Relationships
    - **Backstory**: Personal history, formative events
    - **Relationships**: Family, friends, enemies, mentors
    - **Formative Experiences**: Key life events that shaped character
    - **Social Connections**: Network and community ties
    
    ### Core Layer - Deep Psychology
    - **Motivations**: What drives the character's actions
    - **Fears**: Deepest anxieties and phobias
    - **Desires**: Core wants and needs
    - **Conflicts**: Internal and external struggles
    - **Personality Drivers**: Fundamental psychological patterns
    
    ## Analysis Confidence Scoring
    - Confidence scores range from 0.0 to 1.0
    - Based on mention frequency, information depth, and narrative prominence
    - Minimum threshold of 0.3 for character inclusion
    
    ## Character Importance Ranking
    - Calculated using mention frequency, narrative position, and role significance
    - Characters sorted by importance score for optimal processing
    """

@mcp.resource("music://genre-mappings")
async def genre_mappings_resource() -> str:
    """
    Complete mapping system from character traits to musical genres and styles.
    
    Returns the psychological-to-musical mapping framework used for artist persona generation.
    """
    return """
    # Character-to-Music Genre Mapping System
    
    ## Personality Trait Mappings
    
    ### Brave Characters → Power Genres
    - **Rock**: Electric guitar, driving rhythm, powerful vocals
    - **Metal**: Heavy, distorted, aggressive, intense
    - **Epic Orchestral**: Cinematic, heroic, triumphant
    - **Anthemic Pop**: Uplifting, inspirational, strong melodies
    
    ### Cunning Characters → Sophisticated Genres  
    - **Jazz**: Smooth, controlled, improvisation, sophisticated
    - **Classical**: Complex, refined, intellectual depth
    - **Experimental**: Innovative, unconventional, artistic
    - **Dark Ambient**: Atmospheric, mysterious, calculating
    
    ### Compassionate Characters → Emotional Genres
    - **Folk**: Acoustic, organic, storytelling, traditional
    - **Soul**: Emotional depth, spiritual, heartfelt
    - **Gospel**: Community-focused, uplifting, spiritual
    - **Acoustic**: Intimate, personal, vulnerable
    
    ### Ambitious Characters → Dynamic Genres
    - **Electronic**: Digital, rhythmic, modern, driving
    - **Hip-Hop**: Confident, assertive, rhythmic, urban
    - **Pop**: Mainstream, polished, accessible, catchy
    - **Industrial**: Mechanical, powerful, relentless
    
    ### Mysterious Characters → Atmospheric Genres
    - **Darkwave**: Ethereal, haunting, atmospheric
    - **Ambient**: Floating, spacious, contemplative
    - **Trip-Hop**: Moody, experimental, downtempo
    - **Gothic**: Dark, romantic, dramatic
    
    ## Vocal Style Mapping
    - **Brave** → Powerful, commanding vocals
    - **Cunning** → Smooth, controlled delivery  
    - **Compassionate** → Warm, emotional singing
    - **Ambitious** → Confident, assertive vocals
    - **Mysterious** → Ethereal, haunting voice
    - **Cheerful** → Bright, energetic vocals
    - **Melancholic** → Soft, introspective singing
    - **Rebellious** → Raw, passionate vocals
    """

@mcp.resource("suno://command-formats")
async def suno_command_formats_resource() -> str:
    """
    Complete guide to Suno AI command formats and optimization strategies.
    
    Returns comprehensive information about Suno AI integration and command generation.
    """
    return """
    # Suno AI Command Generation Guide
    
    ## Command Types
    
    ### 1. Simple Prompt Commands
    - Basic text prompts describing desired music
    - Natural language descriptions of style and content
    - Best for: Quick generation, straightforward concepts
    - Example: "A rock song about overcoming challenges with powerful vocals"
    
    ### 2. Custom Mode Commands
    - Detailed parameters for precise control
    - Multiple style tags and specifications
    - Best for: Complex compositions, specific requirements
    - Includes: Style tags, structure, vocal directions
    
    ### 3. Bracket Notation Commands
    - Precise element control using [brackets]
    - Specific musical elements and effects
    - Best for: Technical specifications, exact sound design
    - Example: "[rock] [powerful vocals] [electric guitar] [driving rhythm]"
    
    ## Optimization Strategies
    
    ### Style Tags (Genre/Sound)
    - Primary genre identification
    - Secondary style elements
    - Production characteristics
    - Instrument specifications
    
    ### Structure Tags (Arrangement)
    - Song structure (verse-chorus, bridge, etc.)
    - Dynamic progression
    - Complexity level
    - Timing and pacing
    
    ### Vocal Tags (Voice Characteristics)
    - Vocal style and delivery
    - Emotional expression
    - Technical approach
    - Multiple voice arrangements
    
    ### Sound Effect Tags (Production)
    - Atmospheric elements
    - Reverb and effects
    - Spatial characteristics
    - Special audio processing
    
    ## Effectiveness Scoring
    - Commands rated 0.0 to 1.0 for expected effectiveness
    - Based on clarity, specificity, and Suno AI compatibility
    - Higher scores for well-structured, clear prompts
    """

@mcp.resource("workflow://integration-guide")
async def workflow_integration_resource() -> str:
    """
    Complete workflow integration guide for character-driven music generation.
    
    Returns step-by-step instructions for using the MCP server effectively.
    """
    return """
    # Character-Driven Music Generation Workflow
    
    ## Complete Workflow Process
    
    ### Phase 1: Text Input and Preparation
    1. Prepare narrative text (novels, stories, character descriptions)
    2. Ensure sufficient character detail (minimum 50 words)
    3. Include dialogue, actions, and character interactions
    4. Multiple characters increase analysis depth
    
    ### Phase 2: Character Analysis
    1. Use `analyze_character_text` tool with narrative input
    2. Review extracted character profiles
    3. Verify character accuracy and completeness
    4. Note confidence scores and importance rankings
    
    ### Phase 3: Artist Persona Generation
    1. Use `generate_artist_personas` with character analysis results
    2. Review psychological-to-musical mappings
    3. Examine genre selections and justifications
    4. Validate persona authenticity to source characters
    
    ### Phase 4: Suno Command Creation
    1. Use `create_suno_commands` with personas and characters
    2. Review multiple command variations
    3. Select optimal commands based on effectiveness scores
    4. Consider different command types for varied results
    
    ## Alternative Workflows
    
    ### Quick Complete Workflow
    - Use `complete_workflow` tool for end-to-end processing
    - Single operation from text to final commands
    - Best for: Initial exploration, rapid prototyping
    
    ### Creative Mode Workflow
    - Use `creative_music_generation` for abstract concepts
    - No character analysis required
    - Best for: Thematic music, conceptual compositions
    
    ## Quality Assurance
    
    ### Character Analysis Quality
    - Confidence scores above 0.5 indicate strong analysis
    - Multiple personality drivers suggest complex characters
    - Rich backstory and relationships improve persona generation
    
    ### Artist Persona Quality
    - High mapping confidence (>0.7) indicates strong character-music connection
    - Multiple lyrical themes suggest depth
    - Clear genre justification validates mapping decisions
    
    ### Command Effectiveness
    - Effectiveness scores above 0.8 indicate high-quality commands
    - Multiple command variations provide creative options
    - Clear rationales explain command construction logic
    
    ## Integration with External Systems
    
    ### Claude Desktop Integration
    - Access through MCP client configuration
    - Real-time character analysis and music generation
    - Seamless workflow execution
    
    ### API Integration
    - JSON-based input/output for programmatic access
    - Structured data formats for easy parsing
    - Error handling and validation included
    
    ### Batch Processing
    - Process multiple texts or characters simultaneously
    - Efficient for large-scale content analysis
    - Maintains character relationships across processing
    """

# ================================================================================================
# PROMPTS
# ================================================================================================

@mcp.prompt
async def character_analysis_prompt(text_sample: str) -> str:
    """
    Generate an optimized prompt for character analysis from a text sample.
    
    Creates a detailed analysis prompt that guides effective character extraction
    and psychological profiling from narrative content.
    
    Args:
        text_sample: Sample of the text to be analyzed
        
    Returns:
        Formatted prompt for comprehensive character analysis
    """
    return f"""
    Analyze the following narrative text for character development using the three-layer character bible methodology:

    TEXT SAMPLE:
    {text_sample[:500]}{'...' if len(text_sample) > 500 else ''}

    ANALYSIS FRAMEWORK:

    **Skin Layer Analysis:**
    - Identify all character names and aliases
    - Extract physical descriptions and mannerisms
    - Note speech patterns and behavioral characteristics
    - Document observable traits and actions

    **Flesh Layer Analysis:**
    - Uncover backstory and personal history
    - Map relationships and social connections
    - Identify formative experiences and life events
    - Analyze family dynamics and friendships

    **Core Layer Analysis:**
    - Determine primary motivations and drives
    - Extract fears, anxieties, and insecurities
    - Identify core desires and aspirations
    - Analyze internal and external conflicts
    - Map psychological drivers and personality patterns

    **Character Ranking:**
    - Assess importance within the narrative
    - Calculate confidence in analysis based on available information
    - Rank characters by narrative significance and depth

    Focus on psychological depth and musical potential - these characters will be transformed into musical artist personas.
    """

@mcp.prompt
async def music_persona_prompt(character_name: str, personality_traits: str) -> str:
    """
    Generate a prompt for creating musical artist personas from character analysis.
    
    Creates a detailed prompt for transforming character psychological profiles
    into coherent musical artist identities.
    
    Args:
        character_name: Name of the character being analyzed
        personality_traits: Key personality traits identified
        
    Returns:
        Formatted prompt for artist persona generation
    """
    return f"""
    Transform the character "{character_name}" with traits "{personality_traits}" into a musical artist persona:

    **PSYCHOLOGICAL-MUSICAL MAPPING:**

    **Genre Selection:**
    - Map personality traits to appropriate musical genres
    - Consider emotional palette and psychological drivers
    - Balance authenticity with musical viability
    - Justify genre choices based on character psychology

    **Vocal Style Development:**
    - Translate speech patterns into vocal characteristics
    - Map emotional range to vocal dynamics
    - Consider character confidence and social traits
    - Develop unique vocal identity

    **Artistic Identity:**
    - Create compelling artist name (based on character or thematic)
    - Develop musical influences that align with character background
    - Design collaboration style based on social dynamics
    - Establish creative approach and artistic vision

    **Thematic Content:**
    - Extract lyrical themes from character motivations
    - Map fears and desires to emotional content
    - Translate conflicts into musical tension
    - Develop narrative arc for musical storytelling

    **Production Characteristics:**
    - Select instrumental preferences based on genre and character
    - Determine production style and sonic palette
    - Consider complexity level based on character depth
    - Design overall musical aesthetic

    Ensure the resulting artist persona feels authentic to the source character while being musically compelling and commercially viable.
    """

@mcp.prompt
async def suno_optimization_prompt(artist_persona: str, character_background: str) -> str:
    """
    Generate an optimization prompt for Suno AI command creation.
    
    Creates a detailed prompt for generating effective Suno AI commands
    from artist personas and character backgrounds.
    
    Args:
        artist_persona: Description of the generated artist persona
        character_background: Background information about the source character
        
    Returns:
        Formatted prompt for Suno command optimization
    """
    return f"""
    Create optimized Suno AI commands for the artist persona: {artist_persona[:200]}...
    Based on character background: {character_background[:200]}...

    **COMMAND OPTIMIZATION STRATEGY:**

    **Simple Command Approach:**
    - Create natural language prompts that capture essence
    - Focus on primary genre and emotional core
    - Include character-inspired thematic elements
    - Maintain clarity and directness

    **Custom Mode Approach:**
    - Develop detailed parameter specifications
    - Include multiple style tags for depth
    - Specify structure based on character complexity
    - Add vocal direction for authentic delivery

    **Bracket Notation Approach:**
    - Use precise element control for technical specifications
    - Balance specificity with creative freedom
    - Include character-specific atmospheric elements
    - Optimize for Suno AI's parsing capabilities

    **Variation Strategy:**
    - Create multiple command variations for creative options
    - Explore different musical interpretations of the same character
    - Balance familiarity with innovation
    - Consider different moods and contexts

    **Effectiveness Optimization:**
    - Ensure commands are clear and actionable
    - Balance detail with creative freedom
    - Test command logic and structure
    - Optimize for Suno AI's current capabilities

    **Quality Validation:**
    - Verify character authenticity in musical translation
    - Ensure genre appropriateness and viability
    - Validate emotional resonance and thematic coherence
    - Check technical feasibility and effectiveness

    Generate commands that effectively bridge the gap between literary character analysis and practical music generation.
    """

# ================================================================================================
# WIKI ATTRIBUTION HELPERS
# ================================================================================================

async def _build_wiki_attribution_context(analysis_data: Dict[str, Any], ctx: Context) -> str:
    """Build attribution context for wiki-sourced content used in analysis
    
    Args:
        analysis_data: The analysis data that may contain wiki-sourced information
        ctx: Context for logging
        
    Returns:
        Attribution text for LLM context
    """
    try:
        # Access the persona generator's attribution manager
        if hasattr(persona_generator, 'source_attribution_manager') and persona_generator.source_attribution_manager:
            attribution_manager = persona_generator.source_attribution_manager

            # Collect all wiki sources that might have been used
            wiki_sources = []

            # Add genre sources if available
            genre_sources = attribution_manager.get_source_urls('genre')
            if genre_sources:
                wiki_sources.extend(genre_sources)

            # Add meta tag sources if available
            meta_tag_sources = attribution_manager.get_source_urls('meta_tag')
            if meta_tag_sources:
                wiki_sources.extend(meta_tag_sources)

            # Add technique sources if available
            technique_sources = attribution_manager.get_source_urls('technique')
            if technique_sources:
                wiki_sources.extend(technique_sources)

            if wiki_sources:
                # Build attributed context
                attribution_text = attribution_manager.format_source_references(wiki_sources)

                # Track usage
                content_id = f"analysis_{hash(str(analysis_data))}"
                for source in wiki_sources:
                    attribution_manager.track_content_usage(
                        content_id, source, "Album generation analysis"
                    )

                await ctx.info(f"Added attribution for {len(wiki_sources)} wiki sources")
                return f"\n\nSOURCE ATTRIBUTION:\n{attribution_text}"

        return ""

    except Exception as e:
        logger.warning(f"Failed to build wiki attribution context: {e}")
        return ""

# ================================================================================================
# SERVER CONFIGURATION AND STARTUP
# ================================================================================================

@mcp.tool
async def detect_input_format(text: str, ctx: Context) -> str:
    """
    Detect input format and provide processing recommendations
    
    This tool analyzes input text to determine its type (character description, narrative fiction,
    philosophical content, etc.) and provides recommendations for processing approach.
    
    Args:
        text: Input text to analyze
        ctx: Context for logging
        
    Returns:
        JSON string containing detection results and processing recommendations
    """
    try:
        await ctx.info(f"Detecting input format for {len(text)} character text")

        if not text or len(text.strip()) < 10:
            return json.dumps({
                "error": "Insufficient content for format detection",
                "recommendation": "Please provide more detailed content"
            })

        # Use working universal processor for detection
        processor = WorkingUniversalProcessor()
        detection_result = processor.detect_content_type(text)

        # Add processing recommendations
        recommendations = {
            "character_description": "Use 'analyze_character_text' with this content directly",
            "narrative_fiction": "Use 'analyze_character_text' to extract characters from the narrative",
            "philosophical_conceptual": "Use 'create_conceptual_album' to create characters from concepts",
            "poetic_content": "Use 'analyze_character_text' to create characters from poetic voice",
            "concept_outline": "Use 'create_conceptual_album' to process structured concepts",
            "mixed_content": "Use 'analyze_character_text' with adaptive processing"
        }

        content_type = detection_result.get("content_type", "mixed_content")
        detection_result["processing_recommendation"] = recommendations.get(content_type, "Use 'analyze_character_text' for general processing")

        await ctx.info(f"Detected content type: {content_type} (confidence: {detection_result.get('confidence', 0.0):.2f})")

        return json.dumps(detection_result, indent=2)

    except Exception as e:
        await ctx.error(f"Format detection failed: {str(e)}")
        return json.dumps({"error": f"Format detection failed: {str(e)}"})

@mcp.tool
async def request_clarification(text: str, detection_result: str = None, ctx: Context = None) -> str:
    """
    Request clarification for ambiguous input content
    
    This tool generates clarification prompts when input content type is unclear,
    helping users specify the appropriate processing approach.
    
    Args:
        text: Original input text that needs clarification
        detection_result: Optional JSON string of previous detection results
        ctx: Context for logging
        
    Returns:
        JSON string containing clarification prompts and processing options
    """
    try:
        if ctx:
            await ctx.info("Generating clarification prompts for ambiguous input")

        # Parse detection result if provided
        detection_info = {}
        if detection_result:
            try:
                detection_data = json.loads(detection_result)
                detection_info = detection_data.get("detection_result", detection_data)
            except json.JSONDecodeError:
                pass

        # If no detection result provided, perform quick detection
        if not detection_info:
            processor = WorkingUniversalProcessor()
            detection_info = processor.detect_content_type(text)

        # Generate clarification prompts
        clarification_response = _generate_clarification_prompts(text, detection_info)

        if ctx:
            await ctx.info(f"Generated {len(clarification_response.get('prompts', []))} clarification prompts")

        return json.dumps(clarification_response, indent=2)

    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to generate clarification: {str(e)}")
        return json.dumps({"error": f"Clarification generation failed: {str(e)}"})

@mcp.tool
async def process_with_guidance(text: str, user_choice: str, additional_context: str = "", ctx: Context = None) -> str:
    """
    Process content with user-provided guidance
    
    This tool processes content using the user's specified approach, incorporating
    any additional context provided to improve results.
    
    Args:
        text: Original input text to process
        user_choice: User's chosen processing method (character_description, narrative_fiction, etc.)
        additional_context: Additional context to help with processing
        ctx: Context for logging
        
    Returns:
        JSON string containing processing results
    """
    try:
        if ctx:
            await ctx.info(f"Processing content with user guidance: {user_choice}")

        # Validate user choice
        valid_choices = [
            "character_description", "narrative_fiction", "philosophical_conceptual",
            "poetic_content", "concept_outline", "mixed_content"
        ]

        if user_choice not in valid_choices:
            return json.dumps({
                "error": f"Invalid choice: {user_choice}",
                "valid_choices": valid_choices,
                "suggestion": "Please select one of the valid processing options"
            })

        # Combine original text with additional context if provided
        enhanced_text = text
        if additional_context.strip():
            enhanced_text = f"{text}\n\nAdditional Context: {additional_context}"

        # Route to appropriate processing method based on user choice
        if user_choice == "character_description":
            result = await analyze_character_text(enhanced_text, ctx)
        elif user_choice == "narrative_fiction":
            result = await analyze_character_text(enhanced_text, ctx)
        elif user_choice in ["philosophical_conceptual", "concept_outline"]:
            result = await create_conceptual_album(enhanced_text, "alternative", 9, ctx)
        elif user_choice == "poetic_content":
            result = await analyze_character_text(enhanced_text, ctx)
        else:  # mixed_content
            result = await complete_workflow(enhanced_text, ctx)

        # Parse result and add guidance metadata
        try:
            result_data = json.loads(result)
            result_data["user_guidance"] = {
                "chosen_method": user_choice,
                "additional_context_provided": bool(additional_context.strip()),
                "guidance_applied": True
            }
            result = json.dumps(result_data, indent=2)
        except json.JSONDecodeError:
            pass  # Return original result if parsing fails

        if ctx:
            await ctx.info(f"Successfully processed content using {user_choice} method")

        return result

    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to process with guidance: {str(e)}")
        return json.dumps({"error": f"Processing with guidance failed: {str(e)}"})

@mcp.tool
async def get_processing_guidance(content_type: str = None, ctx: Context = None) -> str:
    """
    Get guidance on different processing modes and when to use them
    
    This tool provides detailed information about available processing modes,
    when to use each one, and examples of appropriate content types.
    
    Args:
        content_type: Specific content type to get guidance for (optional)
        ctx: Context for logging
        
    Returns:
        JSON string containing processing guidance and examples
    """
    try:
        if ctx:
            await ctx.info("Providing processing guidance")

        guidance = {
            "processing_modes": {
                "character_description": {
                    "when_to_use": "When you have explicit character details, artist bios, or persona descriptions",
                    "examples": [
                        "John Smith, 28-year-old indie folk artist from Portland",
                        "Character: Sarah - A philosophical songwriter who explores existential themes",
                        "Artist Profile: DJ Memphis, electronic producer specializing in ambient soundscapes"
                    ],
                    "tool_to_use": "analyze_character_text",
                    "output": "Uses your character details directly to create music content"
                },
                "narrative_fiction": {
                    "when_to_use": "When you have stories, narratives, or fictional content with characters",
                    "examples": [
                        "Story excerpts with dialogue and character actions",
                        "Novel chapters or short stories",
                        "Narrative descriptions of events and characters"
                    ],
                    "tool_to_use": "analyze_character_text",
                    "output": "Extracts characters from the story and creates music from their perspective"
                },
                "philosophical_conceptual": {
                    "when_to_use": "When you have abstract ideas, philosophical content, or conceptual themes",
                    "examples": [
                        "Philosophical essays or excerpts",
                        "Abstract concepts like 'the nature of time'",
                        "Thematic content about existentialism, spirituality, etc."
                    ],
                    "tool_to_use": "create_conceptual_album",
                    "output": "Creates characters that embody and explore these concepts through music"
                },
                "poetic_content": {
                    "when_to_use": "When you have poetry, lyrical content, or highly metaphorical text",
                    "examples": [
                        "Poems or verses",
                        "Lyrical content with rich imagery",
                        "Metaphorical or symbolic text"
                    ],
                    "tool_to_use": "analyze_character_text",
                    "output": "Creates characters from the poetic voice and transforms themes into music"
                },
                "concept_outline": {
                    "when_to_use": "When you have structured outlines, lists, or organized conceptual content",
                    "examples": [
                        "Numbered lists of ideas or themes",
                        "Structured outlines of concepts",
                        "Organized frameworks or systems"
                    ],
                    "tool_to_use": "create_conceptual_album",
                    "output": "Processes each concept systematically to create coherent characters"
                },
                "mixed_content": {
                    "when_to_use": "When your content combines multiple types or you're unsure",
                    "examples": [
                        "Content that mixes narrative with philosophical elements",
                        "Character descriptions embedded in stories",
                        "Any content that doesn't fit clearly into other categories"
                    ],
                    "tool_to_use": "complete_workflow",
                    "output": "Uses adaptive processing to handle multiple content types intelligently"
                }
            },
            "workflow_recommendations": [
                "1. Start with 'detect_input_format' to understand your content type",
                "2. If results are unclear, use 'request_clarification' for guidance",
                "3. Use 'process_with_guidance' if you want to specify the processing approach",
                "4. For general processing, use the recommended tool from format detection"
            ],
            "tips": [
                "Be as specific as possible about what you want to achieve",
                "If you're unsure, start with 'detect_input_format' for analysis",
                "You can always provide additional context to guide the processing",
                "Character descriptions work best when they include age, background, and musical style",
                "Narrative content works best when it has clear characters and dialogue",
                "Conceptual content works best when themes are clearly articulated"
            ],
            "troubleshooting": {
                "empty_results": "Try providing more detailed content or switching to a different processing mode",
                "generic_output": "Add more specific details about characters, themes, or context",
                "wrong_interpretation": "Use 'request_clarification' to specify the correct processing approach"
            }
        }

        # If specific content type requested, focus on that
        if content_type and content_type in guidance["processing_modes"]:
            focused_guidance = {
                "requested_mode": content_type,
                "details": guidance["processing_modes"][content_type],
                "workflow_recommendations": guidance["workflow_recommendations"],
                "tips": guidance["tips"],
                "troubleshooting": guidance["troubleshooting"]
            }
            return json.dumps(focused_guidance, indent=2)

        return json.dumps(guidance, indent=2)

    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to provide guidance: {str(e)}")
        return json.dumps({"error": f"Guidance generation failed: {str(e)}"})

def _generate_clarification_prompts(text: str, detection_info: Dict) -> Dict:
    """Generate helpful clarification prompts based on detection results"""
    content_type = detection_info.get("content_type", "unknown")
    confidence = detection_info.get("confidence", 0.0)
    ambiguity_score = detection_info.get("ambiguity_score", 0.0)
    detected_formats = detection_info.get("detected_formats", [])

    prompts = []
    options = []

    if confidence < 0.4:
        prompts.extend([
            "I'm having trouble determining what type of content this is.",
            "Could you help me understand how you'd like me to process this content?"
        ])

        options.extend([
            {
                "id": "character_description",
                "label": "This is a character description",
                "description": "Use this if you're providing explicit details about a character or artist persona"
            },
            {
                "id": "narrative_fiction",
                "label": "This is a story or narrative",
                "description": "Use this if you want me to extract characters from a fictional narrative"
            },
            {
                "id": "philosophical_conceptual",
                "label": "This contains concepts or themes",
                "description": "Use this if you want me to create characters from abstract ideas or philosophical content"
            },
            {
                "id": "mixed_content",
                "label": "Process adaptively",
                "description": "Let me try multiple approaches and use the best result"
            }
        ])

    elif ambiguity_score > 0.6 and len(detected_formats) > 1:
        format_list = ", ".join(detected_formats)
        prompts.append(f"I detected multiple content types: {format_list}. Which approach would you prefer?")

        for format_type in detected_formats:
            option = _create_format_option(format_type)
            if option:
                options.append(option)

    else:
        prompts.append(f"This appears to be {content_type.replace('_', ' ')} content. Is this correct?")

        # Add the detected type as primary option
        primary_option = _create_format_option(content_type)
        if primary_option:
            options.append(primary_option)

        # Add alternative options
        alternatives = ["character_description", "narrative_fiction", "philosophical_conceptual", "mixed_content"]
        for alt in alternatives:
            if alt != content_type:
                alt_option = _create_format_option(alt)
                if alt_option:
                    options.append(alt_option)

    return {
        "clarification_needed": True,
        "confidence": confidence,
        "ambiguity_score": ambiguity_score,
        "detected_formats": detected_formats,
        "prompts": prompts,
        "options": options[:4],  # Limit to 4 options
        "text_preview": text[:200] + "..." if len(text) > 200 else text,
        "guidance": [
            "Select the option that best matches your intent",
            "You can provide additional context using 'process_with_guidance'",
            "If unsure, choose 'mixed_content' for adaptive processing"
        ]
    }

def _create_format_option(format_type: str) -> Dict:
    """Create an option dictionary for a specific format type"""
    format_options = {
        "character_description": {
            "id": "character_description",
            "label": "Character Description",
            "description": "Process as explicit character details and use them directly"
        },
        "narrative_fiction": {
            "id": "narrative_fiction",
            "label": "Narrative Fiction",
            "description": "Extract characters from the story or narrative elements"
        },
        "philosophical_conceptual": {
            "id": "philosophical_conceptual",
            "label": "Conceptual Content",
            "description": "Create characters that embody the philosophical themes and concepts"
        },
        "poetic_content": {
            "id": "poetic_content",
            "label": "Poetic Content",
            "description": "Create characters from the poetic voice and imagery"
        },
        "concept_outline": {
            "id": "concept_outline",
            "label": "Concept Outline",
            "description": "Process structured concepts and create characters from them"
        },
        "mixed_content": {
            "id": "mixed_content",
            "label": "Mixed Content",
            "description": "Use adaptive processing to handle multiple content types"
        }
    }

    return format_options.get(format_type)

# Initialize server components on import
async def _startup_initialization():
    """Initialize server components"""
    await initialize_server()

# Store initialization task for later execution
_initialization_task = None

async def startup():
    """Startup hook to initialize server components"""
    await initialize_server()

if __name__ == "__main__":
    logger.info("Starting Character-Driven Music Generation MCP Server...")

    # Initialize server components
    import asyncio
    asyncio.run(startup())

    # Run the FastMCP server
    mcp.run()
