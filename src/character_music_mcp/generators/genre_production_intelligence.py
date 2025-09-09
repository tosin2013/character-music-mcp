#!/usr/bin/env python3
"""
Genre-Specific Production Intelligence for Suno Command Generation

This module provides comprehensive genre-specific production techniques, instrumentation,
tempo, and style recommendations for accurate Suno AI command generation.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ================================================================================================
# GENRE PRODUCTION DATA MODELS
# ================================================================================================

@dataclass
class TempoRange:
    """Tempo range for a genre"""
    min_bpm: int
    max_bpm: int
    typical_bpm: int

    def get_tempo_description(self) -> str:
        """Get human-readable tempo description"""
        if self.typical_bpm < 70:
            return "very slow"
        elif self.typical_bpm < 90:
            return "slow"
        elif self.typical_bpm < 110:
            return "moderate"
        elif self.typical_bpm < 130:
            return "medium"
        elif self.typical_bpm < 150:
            return "fast"
        else:
            return "very fast"

@dataclass
class ProductionTechniques:
    """Production techniques for a genre"""
    mixing_style: str
    effects: List[str] = field(default_factory=list)
    recording_approach: str = ""
    sound_characteristics: List[str] = field(default_factory=list)
    dynamics: str = ""

@dataclass
class VocalStyle:
    """Vocal style characteristics for a genre"""
    delivery_style: str
    techniques: List[str] = field(default_factory=list)
    range_preference: str = ""
    emotional_approach: str = ""

@dataclass
class GenreProfile:
    """Complete genre profile with production intelligence"""
    name: str
    category: str
    tempo_range: TempoRange
    instrumentation: List[str] = field(default_factory=list)
    production_techniques: ProductionTechniques = field(default_factory=ProductionTechniques)
    vocal_style: VocalStyle = field(default_factory=VocalStyle)
    style_tags: List[str] = field(default_factory=list)
    meta_tags: List[str] = field(default_factory=list)
    rhythm_patterns: List[str] = field(default_factory=list)
    harmonic_characteristics: List[str] = field(default_factory=list)

# ================================================================================================
# GENRE PRODUCTION INTELLIGENCE ENGINE
# ================================================================================================

class GenreProductionIntelligence:
    """Engine for genre-specific production intelligence and Suno command enhancement"""

    def __init__(self):
        """Initialize with comprehensive genre database"""
        self.genre_profiles = self._build_genre_database()
        self.fallback_profile = self._create_fallback_profile()

    def get_genre_profile(self, genre: str) -> GenreProfile:
        """Get comprehensive genre profile with production intelligence"""
        genre_key = self._normalize_genre_name(genre)

        # Direct match
        if genre_key in self.genre_profiles:
            return self.genre_profiles[genre_key]

        # Fuzzy match for common variations
        for profile_key, profile in self.genre_profiles.items():
            if genre_key in profile_key or profile_key in genre_key:
                return profile

        # Category-based fallback
        category_match = self._find_category_match(genre_key)
        if category_match:
            return category_match

        logger.warning(f"No genre profile found for '{genre}', using fallback")
        return self.fallback_profile

    def enhance_suno_command(self, base_command: str, genre: str,
                           character_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Enhance Suno command with genre-specific production intelligence"""
        profile = self.get_genre_profile(genre)

        # Build enhanced command structure
        enhanced_command = {
            "command_text": self._build_enhanced_command_text(base_command, profile, character_context),
            "style_tags": self._generate_style_tags(profile),
            "meta_tags": self._generate_meta_tags(profile, character_context),
            "tempo_suggestion": profile.tempo_range.typical_bpm,
            "tempo_description": profile.tempo_range.get_tempo_description(),
            "instrumentation": profile.instrumentation[:5],  # Limit to top 5
            "production_notes": self._generate_production_notes(profile),
            "vocal_direction": self._generate_vocal_direction(profile),
            "genre_profile": {
                "name": profile.name,
                "category": profile.category,
                "characteristics": profile.production_techniques.sound_characteristics
            }
        }

        return enhanced_command

    def _build_genre_database(self) -> Dict[str, GenreProfile]:
        """Build comprehensive genre database with production intelligence"""
        profiles = {}

        # Electronic genres
        profiles["electronic"] = GenreProfile(
            name="Electronic",
            category="electronic",
            tempo_range=TempoRange(120, 140, 128),
            instrumentation=["synthesizer", "drum machine", "digital effects", "sampler", "sequencer"],
            production_techniques=ProductionTechniques(
                mixing_style="digital precision",
                effects=["reverb", "delay", "filter sweeps", "compression", "sidechain"],
                recording_approach="digital/programmed",
                sound_characteristics=["crisp", "layered", "synthetic", "precise"],
                dynamics="controlled compression"
            ),
            vocal_style=VocalStyle(
                delivery_style="processed",
                techniques=["vocoder", "auto-tune", "harmonizer"],
                emotional_approach="ethereal"
            ),
            style_tags=["electronic", "synth", "digital"],
            meta_tags=["electronic beats", "synthesized", "programmed"],
            rhythm_patterns=["four-on-the-floor", "syncopated", "quantized"],
            harmonic_characteristics=["synthetic", "layered", "filtered"]
        )

        profiles["drum_and_bass"] = GenreProfile(
            name="Drum and Bass",
            category="electronic",
            tempo_range=TempoRange(160, 180, 174),
            instrumentation=["breakbeats", "sub bass", "synthesizer", "sampler", "drum machine"],
            production_techniques=ProductionTechniques(
                mixing_style="bass-heavy",
                effects=["low-pass filter", "reverb", "delay", "distortion", "compression"],
                recording_approach="sample-based",
                sound_characteristics=["fast", "energetic", "bass-heavy", "complex"],
                dynamics="dynamic range with heavy compression"
            ),
            vocal_style=VocalStyle(
                delivery_style="rhythmic",
                techniques=["chopped vocals", "time-stretched"],
                emotional_approach="energetic"
            ),
            style_tags=["drum and bass", "dnb", "breakbeat"],
            meta_tags=["fast breakbeats", "sub bass", "174 bpm"],
            rhythm_patterns=["amen break", "complex breakbeats", "syncopated"],
            harmonic_characteristics=["bass-focused", "minimal harmony", "rhythmic emphasis"]
        )

        profiles["liquid_drum_and_bass"] = GenreProfile(
            name="Liquid Drum and Bass",
            category="electronic",
            tempo_range=TempoRange(170, 180, 174),
            instrumentation=["smooth breakbeats", "jazz samples", "sub bass", "synthesizer", "piano"],
            production_techniques=ProductionTechniques(
                mixing_style="smooth and flowing",
                effects=["reverb", "chorus", "delay", "subtle compression"],
                recording_approach="sample-based with live elements",
                sound_characteristics=["smooth", "jazzy", "flowing", "melodic"],
                dynamics="gentle compression with natural flow"
            ),
            vocal_style=VocalStyle(
                delivery_style="smooth",
                techniques=["soulful", "jazzy phrasing"],
                emotional_approach="relaxed and soulful"
            ),
            style_tags=["liquid dnb", "liquid drum and bass", "smooth"],
            meta_tags=["liquid", "jazzy", "smooth breakbeats"],
            rhythm_patterns=["flowing breakbeats", "jazz-influenced"],
            harmonic_characteristics=["jazz harmony", "melodic", "smooth progressions"]
        )

        # Alternative and Rock
        profiles["alternative"] = GenreProfile(
            name="Alternative",
            category="rock",
            tempo_range=TempoRange(90, 140, 120),
            instrumentation=["electric guitar", "bass guitar", "drums", "vocals", "synthesizer"],
            production_techniques=ProductionTechniques(
                mixing_style="balanced with character",
                effects=["reverb", "delay", "distortion", "chorus"],
                recording_approach="live recording with overdubs",
                sound_characteristics=["authentic", "dynamic", "textured", "expressive"],
                dynamics="natural dynamics with selective compression"
            ),
            vocal_style=VocalStyle(
                delivery_style="expressive",
                techniques=["dynamic range", "emotional delivery"],
                emotional_approach="introspective and authentic"
            ),
            style_tags=["alternative", "indie", "modern rock"],
            meta_tags=["alternative rock", "indie", "expressive"],
            rhythm_patterns=["varied", "dynamic", "expressive"],
            harmonic_characteristics=["guitar-driven", "varied progressions", "melodic"]
        )

        # Hip-Hop and Trap
        profiles["hip_hop"] = GenreProfile(
            name="Hip-Hop",
            category="urban",
            tempo_range=TempoRange(70, 140, 95),
            instrumentation=["drum machine", "sampler", "turntables", "bass", "synthesizer"],
            production_techniques=ProductionTechniques(
                mixing_style="punchy and clear",
                effects=["compression", "EQ", "reverb", "delay"],
                recording_approach="sample-based with live elements",
                sound_characteristics=["punchy", "rhythmic", "bass-heavy", "clear"],
                dynamics="heavy compression with punch"
            ),
            vocal_style=VocalStyle(
                delivery_style="rhythmic rap",
                techniques=["flow", "wordplay", "rhythm"],
                emotional_approach="confident and expressive"
            ),
            style_tags=["hip-hop", "rap", "urban"],
            meta_tags=["hip hop beats", "rap", "urban"],
            rhythm_patterns=["boom-bap", "trap-influenced", "syncopated"],
            harmonic_characteristics=["sample-based", "minimal harmony", "rhythm-focused"]
        )

        profiles["trap"] = GenreProfile(
            name="Trap",
            category="urban",
            tempo_range=TempoRange(130, 170, 140),
            instrumentation=["808 drums", "hi-hats", "synthesizer", "sampler", "bass"],
            production_techniques=ProductionTechniques(
                mixing_style="hard-hitting",
                effects=["heavy compression", "distortion", "reverb", "delay"],
                recording_approach="digital production",
                sound_characteristics=["hard", "aggressive", "bass-heavy", "modern"],
                dynamics="heavy compression and limiting"
            ),
            vocal_style=VocalStyle(
                delivery_style="aggressive rap",
                techniques=["auto-tune", "ad-libs", "flow variations"],
                emotional_approach="aggressive and confident"
            ),
            style_tags=["trap", "hard", "aggressive"],
            meta_tags=["trap beats", "808s", "hard"],
            rhythm_patterns=["trap hi-hats", "808 patterns", "syncopated"],
            harmonic_characteristics=["minimal", "bass-focused", "modern"]
        )

        # Add more genres...
        profiles.update(self._add_additional_genres())

        return profiles

    def _add_additional_genres(self) -> Dict[str, GenreProfile]:
        """Add additional genre profiles"""
        additional = {}

        # Folk
        additional["folk"] = GenreProfile(
            name="Folk",
            category="acoustic",
            tempo_range=TempoRange(60, 120, 90),
            instrumentation=["acoustic guitar", "vocals", "harmonica", "fiddle", "banjo"],
            production_techniques=ProductionTechniques(
                mixing_style="natural and warm",
                effects=["subtle reverb", "compression"],
                recording_approach="live recording",
                sound_characteristics=["warm", "natural", "intimate", "organic"],
                dynamics="natural dynamics"
            ),
            vocal_style=VocalStyle(
                delivery_style="storytelling",
                techniques=["narrative", "emotional"],
                emotional_approach="authentic and heartfelt"
            ),
            style_tags=["folk", "acoustic", "storytelling"],
            meta_tags=["folk music", "acoustic", "storytelling"],
            rhythm_patterns=["simple", "natural", "varied"],
            harmonic_characteristics=["traditional", "simple", "melodic"]
        )

        # Jazz
        additional["jazz"] = GenreProfile(
            name="Jazz",
            category="jazz",
            tempo_range=TempoRange(60, 200, 120),
            instrumentation=["piano", "saxophone", "trumpet", "upright bass", "drums"],
            production_techniques=ProductionTechniques(
                mixing_style="spacious and natural",
                effects=["natural reverb", "minimal processing"],
                recording_approach="live recording",
                sound_characteristics=["sophisticated", "dynamic", "spacious", "natural"],
                dynamics="wide dynamic range"
            ),
            vocal_style=VocalStyle(
                delivery_style="sophisticated",
                techniques=["scat", "improvisation", "phrasing"],
                emotional_approach="sophisticated and expressive"
            ),
            style_tags=["jazz", "sophisticated", "improvised"],
            meta_tags=["jazz", "improvisation", "sophisticated"],
            rhythm_patterns=["swing", "complex", "improvised"],
            harmonic_characteristics=["complex", "sophisticated", "extended chords"]
        )

        return additional

    def _create_fallback_profile(self) -> GenreProfile:
        """Create fallback profile for unknown genres"""
        return GenreProfile(
            name="Alternative",
            category="general",
            tempo_range=TempoRange(90, 130, 110),
            instrumentation=["guitar", "bass", "drums", "vocals"],
            production_techniques=ProductionTechniques(
                mixing_style="balanced",
                effects=["reverb", "compression"],
                sound_characteristics=["balanced", "clear"]
            ),
            vocal_style=VocalStyle(
                delivery_style="expressive",
                emotional_approach="authentic"
            ),
            style_tags=["alternative", "indie"],
            meta_tags=["alternative", "indie"],
            rhythm_patterns=["standard"],
            harmonic_characteristics=["melodic"]
        )

    def _normalize_genre_name(self, genre: str) -> str:
        """Normalize genre name for matching"""
        return genre.lower().replace(" ", "_").replace("-", "_").replace("&", "and")

    def _find_category_match(self, genre_key: str) -> Optional[GenreProfile]:
        """Find genre by category matching"""
        category_keywords = {
            "electronic": ["electronic", "edm", "techno", "house", "trance"],
            "rock": ["rock", "alternative", "indie", "grunge"],
            "urban": ["hip_hop", "rap", "trap", "r&b"],
            "acoustic": ["folk", "country", "acoustic"],
            "jazz": ["jazz", "blues", "swing"]
        }

        for category, keywords in category_keywords.items():
            if any(keyword in genre_key for keyword in keywords):
                # Return first profile from this category
                for profile in self.genre_profiles.values():
                    if profile.category == category:
                        return profile

        return None

    def _build_enhanced_command_text(self, base_command: str, profile: GenreProfile,
                                   character_context: Optional[Dict] = None) -> str:
        """Build enhanced command text with genre-specific elements"""
        # Start with base command
        enhanced_parts = [base_command]

        # Add genre-specific style tags
        if profile.style_tags:
            style_tag = f"[{profile.style_tags[0]}]"
            if style_tag not in base_command:
                enhanced_parts.append(style_tag)

        # Add tempo indication if significantly different from default
        if profile.tempo_range.typical_bpm < 80 or profile.tempo_range.typical_bpm > 140:
            enhanced_parts.append(f"[{profile.tempo_range.get_tempo_description()} tempo]")

        # Add key instrumentation
        if profile.instrumentation:
            key_instrument = profile.instrumentation[0]
            if key_instrument not in base_command.lower():
                enhanced_parts.append(f"[{key_instrument}]")

        # Add production characteristic
        if profile.production_techniques.sound_characteristics:
            characteristic = profile.production_techniques.sound_characteristics[0]
            enhanced_parts.append(f"[{characteristic}]")

        return " ".join(enhanced_parts)

    def _generate_style_tags(self, profile: GenreProfile) -> List[str]:
        """Generate style tags for Suno command"""
        tags = profile.style_tags.copy()

        # Add tempo-based tags
        tempo_desc = profile.tempo_range.get_tempo_description()
        if tempo_desc not in ["moderate", "medium"]:
            tags.append(tempo_desc)

        # Add production style tags
        if profile.production_techniques.sound_characteristics:
            tags.extend(profile.production_techniques.sound_characteristics[:2])

        return tags[:6]  # Limit to 6 tags

    def _generate_meta_tags(self, profile: GenreProfile,
                          character_context: Optional[Dict] = None) -> List[str]:
        """Generate meta tags for enhanced command"""
        meta_tags = profile.meta_tags.copy()

        # Add BPM if specific
        if profile.tempo_range.typical_bpm != 120:  # 120 is default
            meta_tags.append(f"{profile.tempo_range.typical_bpm} bpm")

        # Add character-specific tags if available
        if character_context:
            if "emotional_state" in character_context:
                meta_tags.append(character_context["emotional_state"])

        return meta_tags[:5]  # Limit to 5 meta tags

    def _generate_production_notes(self, profile: GenreProfile) -> List[str]:
        """Generate production notes for the command"""
        notes = []

        # Mixing approach
        notes.append(f"Mix with {profile.production_techniques.mixing_style}")

        # Key effects
        if profile.production_techniques.effects:
            key_effects = profile.production_techniques.effects[:3]
            notes.append(f"Use {', '.join(key_effects)}")

        # Dynamics approach
        if profile.production_techniques.dynamics:
            notes.append(f"Apply {profile.production_techniques.dynamics}")

        return notes

    def _generate_vocal_direction(self, profile: GenreProfile) -> str:
        """Generate vocal direction for the command"""
        vocal = profile.vocal_style

        direction_parts = []

        if vocal.delivery_style:
            direction_parts.append(f"{vocal.delivery_style} delivery")

        if vocal.emotional_approach:
            direction_parts.append(f"{vocal.emotional_approach} approach")

        if vocal.techniques:
            direction_parts.append(f"using {vocal.techniques[0]}")

        return ", ".join(direction_parts) if direction_parts else "expressive vocals"

# ================================================================================================
# CONVENIENCE FUNCTIONS
# ================================================================================================

def get_genre_intelligence() -> GenreProductionIntelligence:
    """Get singleton instance of genre production intelligence"""
    if not hasattr(get_genre_intelligence, '_instance'):
        get_genre_intelligence._instance = GenreProductionIntelligence()
    return get_genre_intelligence._instance

def enhance_suno_command_with_genre(command: str, genre: str,
                                  character_context: Optional[Dict] = None) -> Dict[str, Any]:
    """Convenience function to enhance Suno command with genre intelligence"""
    intelligence = get_genre_intelligence()
    return intelligence.enhance_suno_command(command, genre, character_context)

def get_genre_production_profile(genre: str) -> GenreProfile:
    """Convenience function to get genre production profile"""
    intelligence = get_genre_intelligence()
    return intelligence.get_genre_profile(genre)

def align_persona_with_genre(persona_data: Dict[str, Any], requested_genre: str) -> Dict[str, Any]:
    """Align artist persona characteristics with requested musical genre"""
    intelligence = get_genre_intelligence()
    genre_profile = intelligence.get_genre_profile(requested_genre)

    # Create aligned persona
    aligned_persona = persona_data.copy()

    # Update genre information
    aligned_persona["primary_genre"] = genre_profile.name.lower()
    aligned_persona["secondary_genres"] = [genre_profile.category, "alternative"]

    # Align vocal style with genre
    aligned_persona["vocal_style"] = _align_vocal_style_with_genre(
        persona_data.get("vocal_style", "expressive"), genre_profile
    )

    # Align instrumental preferences
    aligned_persona["instrumental_preferences"] = genre_profile.instrumentation[:5]

    # Update artistic influences based on genre
    aligned_persona["artistic_influences"] = _generate_genre_appropriate_influences(
        genre_profile, persona_data.get("character_name", "Artist")
    )

    # Align emotional palette with genre characteristics
    if genre_profile.production_techniques.sound_characteristics:
        aligned_persona["emotional_palette"] = _align_emotional_palette_with_genre(
            persona_data.get("emotional_palette", []), genre_profile
        )

    # Update collaboration style based on genre
    aligned_persona["collaboration_style"] = _align_collaboration_style_with_genre(
        persona_data.get("collaboration_style", "balanced"), genre_profile
    )

    # Add genre-specific persona description
    aligned_persona["persona_description"] = _generate_genre_aligned_description(
        persona_data, genre_profile
    )

    # Update confidence score (slightly lower due to forced alignment)
    original_confidence = persona_data.get("character_mapping_confidence", 0.8)
    aligned_persona["character_mapping_confidence"] = max(0.6, original_confidence * 0.9)

    # Add alignment notes
    aligned_persona["genre_alignment_notes"] = f"Persona aligned with {requested_genre} characteristics"

    return aligned_persona

def _align_vocal_style_with_genre(original_vocal_style: str, genre_profile: GenreProfile) -> str:
    """Align vocal style with genre characteristics"""
    genre_vocal_mappings = {
        "electronic": "processed and ethereal",
        "drum_and_bass": "rhythmic and energetic",
        "liquid_drum_and_bass": "smooth and soulful",
        "hip_hop": "rhythmic and confident",
        "trap": "aggressive and modern",
        "alternative": "expressive and authentic",
        "folk": "storytelling and heartfelt",
        "jazz": "sophisticated and improvisational",
        "rock": "powerful and dynamic"
    }

    genre_key = genre_profile.name.lower().replace(" ", "_")
    if genre_key in genre_vocal_mappings:
        return genre_vocal_mappings[genre_key]

    # Use genre's vocal style if available
    if genre_profile.vocal_style.delivery_style:
        return f"{genre_profile.vocal_style.delivery_style} and {genre_profile.vocal_style.emotional_approach}"

    return original_vocal_style

def _generate_genre_appropriate_influences(genre_profile: GenreProfile, character_name: str) -> List[str]:
    """Generate genre-appropriate artistic influences"""
    genre_influences = {
        "electronic": ["Aphex Twin", "Boards of Canada", "Burial", "Four Tet"],
        "drum_and_bass": ["LTJ Bukem", "Goldie", "Roni Size", "Netsky"],
        "liquid_drum_and_bass": ["LTJ Bukem", "Calibre", "High Contrast", "London Elektricity"],
        "hip_hop": ["J Dilla", "Madlib", "The Alchemist", "9th Wonder"],
        "trap": ["Metro Boomin", "Southside", "TM88", "Zaytoven"],
        "alternative": ["Radiohead", "Arcade Fire", "The National", "Bon Iver"],
        "folk": ["Bob Dylan", "Joni Mitchell", "Nick Drake", "Fleet Foxes"],
        "jazz": ["Miles Davis", "John Coltrane", "Bill Evans", "Herbie Hancock"],
        "rock": ["Led Zeppelin", "Pink Floyd", "The Beatles", "Queens of the Stone Age"]
    }

    genre_key = genre_profile.name.lower().replace(" ", "_")
    if genre_key in genre_influences:
        return genre_influences[genre_key][:3]  # Return top 3

    # Fallback to category-based influences
    category_influences = {
        "electronic": ["Kraftwerk", "Daft Punk", "Aphex Twin"],
        "urban": ["Kanye West", "Dr. Dre", "Timbaland"],
        "rock": ["The Beatles", "Led Zeppelin", "Nirvana"],
        "acoustic": ["Bob Dylan", "Johnny Cash", "Neil Young"],
        "jazz": ["Miles Davis", "Duke Ellington", "Ella Fitzgerald"]
    }

    return category_influences.get(genre_profile.category, ["Various Artists", "Independent Musicians", "Genre Pioneers"])

def _align_emotional_palette_with_genre(original_palette: List[str], genre_profile: GenreProfile) -> List[str]:
    """Align emotional palette with genre characteristics"""
    genre_emotions = {
        "electronic": ["ethereal", "futuristic", "contemplative", "energetic"],
        "drum_and_bass": ["energetic", "intense", "dynamic", "powerful"],
        "liquid_drum_and_bass": ["smooth", "soulful", "flowing", "jazzy"],
        "hip_hop": ["confident", "expressive", "rhythmic", "authentic"],
        "trap": ["aggressive", "modern", "intense", "bold"],
        "alternative": ["introspective", "authentic", "expressive", "dynamic"],
        "folk": ["heartfelt", "storytelling", "authentic", "peaceful"],
        "jazz": ["sophisticated", "improvisational", "expressive", "complex"],
        "rock": ["powerful", "dynamic", "energetic", "rebellious"]
    }

    genre_key = genre_profile.name.lower().replace(" ", "_")
    if genre_key in genre_emotions:
        # Blend original palette with genre-appropriate emotions
        genre_specific = genre_emotions[genre_key]
        # Keep some original emotions, add genre-specific ones
        combined = original_palette[:2] + genre_specific[:3]
        return list(dict.fromkeys(combined))  # Remove duplicates while preserving order

    return original_palette

def _align_collaboration_style_with_genre(original_style: str, genre_profile: GenreProfile) -> str:
    """Align collaboration style with genre characteristics"""
    genre_collaboration = {
        "electronic": "producer-focused with featured vocalists",
        "drum_and_bass": "DJ/producer collaborative approach",
        "liquid_drum_and_bass": "smooth collaborative flow with jazz musicians",
        "hip_hop": "producer-rapper collaborative dynamic",
        "trap": "hard-hitting producer-artist collaboration",
        "alternative": "band-oriented collaborative approach",
        "folk": "intimate acoustic collaboration",
        "jazz": "improvisational ensemble collaboration",
        "rock": "full band collaborative energy"
    }

    genre_key = genre_profile.name.lower().replace(" ", "_")
    return genre_collaboration.get(genre_key, original_style)

def _generate_genre_aligned_description(persona_data: Dict[str, Any], genre_profile: GenreProfile) -> str:
    """Generate persona description aligned with genre characteristics"""
    character_name = persona_data.get("character_name", "Artist")
    genre_name = genre_profile.name

    # Get key characteristics
    sound_chars = genre_profile.production_techniques.sound_characteristics
    vocal_style = genre_profile.vocal_style.delivery_style

    description = f"""
    Musical persona derived from {character_name}: A {genre_name.lower()} artist with {vocal_style} delivery.
    
    This artist embodies the {genre_name.lower()} aesthetic through {', '.join(sound_chars[:2]) if sound_chars else 'expressive'} 
    soundscapes and {genre_profile.vocal_style.emotional_approach} vocal approach. 
    
    Production style focuses on {genre_profile.production_techniques.mixing_style} with 
    {', '.join(genre_profile.instrumentation[:3]) if genre_profile.instrumentation else 'varied instrumentation'}.
    
    Tempo typically ranges from {genre_profile.tempo_range.min_bpm} to {genre_profile.tempo_range.max_bpm} BPM, 
    creating {genre_profile.tempo_range.get_tempo_description()} energy that matches the character's essence.
    """

    return description.strip()
