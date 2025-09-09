#!/usr/bin/env python3

"""
Enhanced Beat Pattern Generator for understand_topic_with_emotions tool

This module provides sophisticated beat pattern generation that creates
genre-appropriate patterns based on emotional analysis instead of generic responses.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from enhanced_emotional_analyzer import EmotionalInsight, EmotionalProfile


@dataclass
class BeatPattern:
    """Represents a specific beat pattern with musical characteristics"""
    name: str
    time_signature: str
    tempo_range: Tuple[int, int]
    kick_pattern: List[int]  # Beat positions for kick drum
    snare_pattern: List[int]  # Beat positions for snare
    hihat_pattern: List[int]  # Beat positions for hi-hat
    complexity: float  # 0.0 to 1.0
    energy_level: str  # low, medium, high
    genre_associations: List[str]
    emotional_fit: List[str]  # Which emotions this pattern suits

@dataclass
class MusicalElement:
    """Represents a musical element with emotional context"""
    element_type: str  # rhythm, melody, harmony, texture
    description: str
    emotional_purpose: str
    implementation_notes: List[str]
    suno_commands: List[str]

class EnhancedBeatGenerator:
    """
    Advanced beat pattern generator that creates genre-appropriate patterns
    based on emotional analysis instead of generic responses.
    """

    def __init__(self):
        self.beat_patterns = self._initialize_beat_patterns()
        self.genre_characteristics = self._initialize_genre_characteristics()
        self.emotional_rhythms = self._initialize_emotional_rhythms()

    def _initialize_beat_patterns(self) -> Dict[str, BeatPattern]:
        """Initialize comprehensive beat pattern library"""
        return {
            # Electronic/Ambient Patterns
            "ambient_pulse": BeatPattern(
                name="Ambient Pulse",
                time_signature="4/4",
                tempo_range=(60, 80),
                kick_pattern=[1, 9],  # Sparse kick on 1 and 3
                snare_pattern=[5, 13],  # Snare on 2 and 4
                hihat_pattern=[1, 3, 5, 7, 9, 11, 13, 15],  # Eighth notes
                complexity=0.3,
                energy_level="low",
                genre_associations=["ambient", "chillout", "meditation"],
                emotional_fit=["contemplative", "peaceful", "melancholic"]
            ),

            "driving_electronic": BeatPattern(
                name="Driving Electronic",
                time_signature="4/4",
                tempo_range=(120, 140),
                kick_pattern=[1, 5, 9, 13],  # Four-on-the-floor
                snare_pattern=[5, 13],  # Snare on 2 and 4
                hihat_pattern=[3, 7, 11, 15],  # Off-beat hi-hats
                complexity=0.6,
                energy_level="high",
                genre_associations=["electronic", "dance", "synthwave"],
                emotional_fit=["energetic", "hopeful", "passionate"]
            ),

            # Rock/Alternative Patterns
            "alternative_rock": BeatPattern(
                name="Alternative Rock",
                time_signature="4/4",
                tempo_range=(90, 120),
                kick_pattern=[1, 7, 9, 15],  # Syncopated kick
                snare_pattern=[5, 13],  # Backbeat
                hihat_pattern=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],  # 16th notes
                complexity=0.7,
                energy_level="medium",
                genre_associations=["alternative", "indie_rock", "grunge"],
                emotional_fit=["frustrated", "conflicted", "passionate"]
            ),

            "heavy_rock": BeatPattern(
                name="Heavy Rock",
                time_signature="4/4",
                tempo_range=(100, 160),
                kick_pattern=[1, 3, 9, 11],  # Aggressive kick pattern
                snare_pattern=[5, 13],  # Strong backbeat
                hihat_pattern=[1, 3, 5, 7, 9, 11, 13, 15],  # Driving eighth notes
                complexity=0.8,
                energy_level="high",
                genre_associations=["metal", "hard_rock", "punk"],
                emotional_fit=["furious", "aggressive", "intense"]
            ),

            # Folk/Acoustic Patterns
            "folk_strum": BeatPattern(
                name="Folk Strum",
                time_signature="4/4",
                tempo_range=(70, 100),
                kick_pattern=[1, 9],  # Simple kick on 1 and 3
                snare_pattern=[5, 13],  # Light snare on 2 and 4
                hihat_pattern=[1, 3, 5, 7, 9, 11, 13, 15],  # Consistent strumming
                complexity=0.4,
                energy_level="low",
                genre_associations=["folk", "acoustic", "singer_songwriter"],
                emotional_fit=["melancholic", "hopeful", "contemplative"]
            ),

            "celtic_rhythm": BeatPattern(
                name="Celtic Rhythm",
                time_signature="6/8",
                tempo_range=(80, 120),
                kick_pattern=[1, 7],  # Strong beats in 6/8
                snare_pattern=[4, 10],  # Cross-rhythm snare
                hihat_pattern=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],  # Flowing eighth notes
                complexity=0.6,
                energy_level="medium",
                genre_associations=["celtic", "folk", "world"],
                emotional_fit=["mysterious", "nostalgic", "adventurous"]
            ),

            # Jazz/Complex Patterns
            "jazz_swing": BeatPattern(
                name="Jazz Swing",
                time_signature="4/4",
                tempo_range=(100, 140),
                kick_pattern=[1, 9],  # Walking bass feel
                snare_pattern=[5, 13],  # Swing snare
                hihat_pattern=[3, 7, 11, 15],  # Swing hi-hat
                complexity=0.8,
                energy_level="medium",
                genre_associations=["jazz", "swing", "blues"],
                emotional_fit=["sophisticated", "contemplative", "nostalgic"]
            ),

            # Cinematic/Orchestral Patterns
            "cinematic_build": BeatPattern(
                name="Cinematic Build",
                time_signature="4/4",
                tempo_range=(80, 120),
                kick_pattern=[1, 5, 9, 13, 15],  # Building intensity
                snare_pattern=[7, 15],  # Dramatic snare hits
                hihat_pattern=[1, 3, 5, 7, 9, 11, 13, 15],  # Consistent drive
                complexity=0.7,
                energy_level="high",
                genre_associations=["cinematic", "orchestral", "epic"],
                emotional_fit=["dramatic", "passionate", "heroic"]
            ),

            # Experimental/Irregular Patterns
            "irregular_complex": BeatPattern(
                name="Irregular Complex",
                time_signature="7/8",
                tempo_range=(90, 130),
                kick_pattern=[1, 6, 10],  # Odd meter kick
                snare_pattern=[4, 12],  # Displaced snare
                hihat_pattern=[1, 2, 4, 5, 6, 8, 9, 10, 12, 13],  # Complex hi-hat
                complexity=0.9,
                energy_level="medium",
                genre_associations=["progressive", "experimental", "art_rock"],
                emotional_fit=["conflicted", "complex", "intellectual"]
            ),

            # Minimal/Sparse Patterns
            "minimal_pulse": BeatPattern(
                name="Minimal Pulse",
                time_signature="4/4",
                tempo_range=(60, 90),
                kick_pattern=[1],  # Single kick per measure
                snare_pattern=[9],  # Single snare
                hihat_pattern=[5, 13],  # Minimal hi-hat
                complexity=0.2,
                energy_level="low",
                genre_associations=["minimal", "ambient", "drone"],
                emotional_fit=["meditative", "sparse", "introspective"]
            )
        }

    def _initialize_genre_characteristics(self) -> Dict[str, Dict[str, Any]]:
        """Initialize genre-specific musical characteristics"""
        return {
            "ambient": {
                "tempo_range": (60, 90),
                "typical_patterns": ["ambient_pulse", "minimal_pulse"],
                "key_elements": ["atmospheric_pads", "reverb_textures", "sparse_percussion"],
                "emotional_associations": ["contemplative", "peaceful", "mysterious"]
            },
            "electronic": {
                "tempo_range": (120, 140),
                "typical_patterns": ["driving_electronic"],
                "key_elements": ["synthesizers", "electronic_drums", "digital_effects"],
                "emotional_associations": ["energetic", "futuristic", "intense"]
            },
            "folk": {
                "tempo_range": (70, 110),
                "typical_patterns": ["folk_strum", "celtic_rhythm"],
                "key_elements": ["acoustic_guitar", "natural_percussion", "organic_textures"],
                "emotional_associations": ["nostalgic", "authentic", "melancholic"]
            },
            "rock": {
                "tempo_range": (90, 160),
                "typical_patterns": ["alternative_rock", "heavy_rock"],
                "key_elements": ["electric_guitar", "bass", "drums"],
                "emotional_associations": ["passionate", "rebellious", "energetic"]
            },
            "cinematic": {
                "tempo_range": (80, 120),
                "typical_patterns": ["cinematic_build"],
                "key_elements": ["orchestral_elements", "dynamic_builds", "emotional_swells"],
                "emotional_associations": ["dramatic", "epic", "emotional"]
            },
            "jazz": {
                "tempo_range": (100, 140),
                "typical_patterns": ["jazz_swing"],
                "key_elements": ["swing_rhythm", "complex_harmony", "improvisation"],
                "emotional_associations": ["sophisticated", "smooth", "contemplative"]
            }
        }

    def _initialize_emotional_rhythms(self) -> Dict[str, Dict[str, Any]]:
        """Initialize emotion-specific rhythm characteristics"""
        return {
            "anxious": {
                "rhythm_characteristics": ["irregular", "syncopated", "restless"],
                "tempo_modifier": 1.1,
                "complexity_boost": 0.2,
                "suggested_patterns": ["irregular_complex", "alternative_rock"]
            },
            "melancholic": {
                "rhythm_characteristics": ["slow", "flowing", "gentle"],
                "tempo_modifier": 0.8,
                "complexity_boost": -0.1,
                "suggested_patterns": ["folk_strum", "ambient_pulse"]
            },
            "furious": {
                "rhythm_characteristics": ["aggressive", "driving", "intense"],
                "tempo_modifier": 1.3,
                "complexity_boost": 0.3,
                "suggested_patterns": ["heavy_rock", "driving_electronic"]
            },
            "contemplative": {
                "rhythm_characteristics": ["steady", "meditative", "spacious"],
                "tempo_modifier": 0.9,
                "complexity_boost": -0.2,
                "suggested_patterns": ["ambient_pulse", "minimal_pulse"]
            },
            "hopeful": {
                "rhythm_characteristics": ["uplifting", "forward-moving", "bright"],
                "tempo_modifier": 1.1,
                "complexity_boost": 0.1,
                "suggested_patterns": ["folk_strum", "driving_electronic"]
            },
            "passionate": {
                "rhythm_characteristics": ["intense", "dynamic", "expressive"],
                "tempo_modifier": 1.2,
                "complexity_boost": 0.2,
                "suggested_patterns": ["cinematic_build", "alternative_rock"]
            }
        }

    def generate_beat_patterns(self, emotional_profile: EmotionalProfile, genre_preferences: List[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive beat patterns based on emotional analysis

        Args:
            emotional_profile: Emotional analysis results
            genre_preferences: Optional genre preferences

        Returns:
            Dictionary containing beat patterns and musical recommendations
        """
        if not emotional_profile.primary_emotions:
            # Generate default patterns when no emotions are detected
            return self._generate_default_patterns(genre_preferences)

        primary_emotion = emotional_profile.primary_emotions[0]

        # Select appropriate beat patterns
        selected_patterns = self._select_patterns_for_emotion(primary_emotion, genre_preferences)

        # Generate rhythm variations
        rhythm_variations = self._generate_rhythm_variations(emotional_profile)

        # Create musical elements
        musical_elements = self._create_musical_elements(emotional_profile, selected_patterns)

        # Generate Suno AI commands
        suno_commands = self._generate_suno_commands(selected_patterns, emotional_profile)

        return {
            "primary_emotion": primary_emotion.emotion,
            "emotional_intensity": primary_emotion.intensity,
            "selected_patterns": [pattern.name for pattern in selected_patterns],
            "rhythm_characteristics": self._get_rhythm_characteristics(primary_emotion),
            "tempo_recommendations": self._get_tempo_recommendations(emotional_profile),
            "beat_patterns": {
                pattern.name: {
                    "time_signature": pattern.time_signature,
                    "tempo_range": pattern.tempo_range,
                    "complexity": pattern.complexity,
                    "energy_level": pattern.energy_level,
                    "kick_pattern": pattern.kick_pattern,
                    "snare_pattern": pattern.snare_pattern,
                    "hihat_pattern": pattern.hihat_pattern,
                    "emotional_fit": pattern.emotional_fit
                }
                for pattern in selected_patterns
            },
            "rhythm_variations": rhythm_variations,
            "musical_elements": [
                {
                    "type": element.element_type,
                    "description": element.description,
                    "purpose": element.emotional_purpose,
                    "implementation": element.implementation_notes,
                    "suno_commands": element.suno_commands
                }
                for element in musical_elements
            ],
            "suno_commands": suno_commands,
            "production_notes": self._generate_production_notes(emotional_profile, selected_patterns)
        }

    def _select_patterns_for_emotion(self, emotion: EmotionalInsight, genre_preferences: List[str] = None) -> List[BeatPattern]:
        """Select appropriate beat patterns for the given emotion"""
        suitable_patterns = []

        # Find patterns that match the emotion
        for pattern in self.beat_patterns.values():
            if emotion.emotion in pattern.emotional_fit:
                suitable_patterns.append(pattern)

        # If genre preferences are specified, filter by genre
        if genre_preferences:
            genre_filtered = []
            for pattern in suitable_patterns:
                if any(genre in pattern.genre_associations for genre in genre_preferences):
                    genre_filtered.append(pattern)
            if genre_filtered:
                suitable_patterns = genre_filtered

        # If no suitable patterns found, use fallback based on emotion characteristics
        if not suitable_patterns:
            suitable_patterns = self._get_fallback_patterns(emotion)

        # Sort by emotional fit and complexity
        suitable_patterns.sort(key=lambda p: (
            emotion.emotion in p.emotional_fit,
            abs(p.complexity - emotion.intensity)
        ), reverse=True)

        return suitable_patterns[:3]  # Return top 3 patterns

    def _get_fallback_patterns(self, emotion: EmotionalInsight) -> List[BeatPattern]:
        """Get fallback patterns when no direct match is found"""
        if emotion.intensity > 0.7:
            # High intensity emotions
            return [self.beat_patterns["heavy_rock"], self.beat_patterns["driving_electronic"]]
        elif emotion.intensity < 0.3:
            # Low intensity emotions
            return [self.beat_patterns["ambient_pulse"], self.beat_patterns["minimal_pulse"]]
        else:
            # Medium intensity emotions
            return [self.beat_patterns["alternative_rock"], self.beat_patterns["folk_strum"]]

    def _generate_rhythm_variations(self, emotional_profile: EmotionalProfile) -> List[Dict[str, Any]]:
        """Generate rhythm variations based on emotional complexity"""
        variations = []

        # Base variation on emotional complexity
        if emotional_profile.emotional_complexity > 0.7:
            variations.append({
                "name": "Complex Polyrhythm",
                "description": "Layered rhythms reflecting emotional complexity",
                "implementation": "Multiple percussion layers with different time signatures"
            })

        # Variation based on emotional arc
        if emotional_profile.emotional_arc["beginning"] != emotional_profile.emotional_arc["end"]:
            variations.append({
                "name": "Progressive Rhythm",
                "description": f"Rhythm evolves from {emotional_profile.emotional_arc['beginning']} to {emotional_profile.emotional_arc['end']}",
                "implementation": "Gradual tempo and complexity changes throughout the piece"
            })

        # Variation based on dominant mood
        mood_variations = {
            "melancholic": {
                "name": "Rubato Timing",
                "description": "Flexible timing that breathes with emotion",
                "implementation": "Slight tempo variations and expressive timing"
            },
            "anxious": {
                "name": "Syncopated Tension",
                "description": "Off-beat accents creating rhythmic tension",
                "implementation": "Displaced beats and unexpected accents"
            },
            "passionate": {
                "name": "Dynamic Rhythm",
                "description": "Rhythm intensity matches emotional peaks",
                "implementation": "Dramatic tempo and volume changes"
            }
        }

        if emotional_profile.dominant_mood in mood_variations:
            variations.append(mood_variations[emotional_profile.dominant_mood])

        return variations

    def _create_musical_elements(self, emotional_profile: EmotionalProfile, patterns: List[BeatPattern]) -> List[MusicalElement]:
        """Create comprehensive musical elements based on emotional analysis"""
        elements = []

        # Rhythm element
        rhythm_element = MusicalElement(
            element_type="rhythm",
            description=f"Rhythm pattern reflecting {emotional_profile.dominant_mood} emotion",
            emotional_purpose=f"Convey the {emotional_profile.dominant_mood} feeling through rhythmic pulse",
            implementation_notes=[
                f"Use {patterns[0].name} as primary pattern",
                f"Tempo range: {patterns[0].tempo_range[0]}-{patterns[0].tempo_range[1]} BPM",
                f"Time signature: {patterns[0].time_signature}"
            ],
            suno_commands=[
                f"[{patterns[0].tempo_range[0]}bpm]",
                f"[{patterns[0].name.lower().replace(' ', '_')}_rhythm]"
            ]
        )
        elements.append(rhythm_element)

        # Melody element based on emotional themes
        melody_characteristics = self._get_melody_characteristics(emotional_profile)
        melody_element = MusicalElement(
            element_type="melody",
            description=melody_characteristics["description"],
            emotional_purpose=melody_characteristics["purpose"],
            implementation_notes=melody_characteristics["implementation"],
            suno_commands=melody_characteristics["suno_commands"]
        )
        elements.append(melody_element)

        # Harmony element
        harmony_characteristics = self._get_harmony_characteristics(emotional_profile)
        harmony_element = MusicalElement(
            element_type="harmony",
            description=harmony_characteristics["description"],
            emotional_purpose=harmony_characteristics["purpose"],
            implementation_notes=harmony_characteristics["implementation"],
            suno_commands=harmony_characteristics["suno_commands"]
        )
        elements.append(harmony_element)

        # Texture element
        texture_characteristics = self._get_texture_characteristics(emotional_profile)
        texture_element = MusicalElement(
            element_type="texture",
            description=texture_characteristics["description"],
            emotional_purpose=texture_characteristics["purpose"],
            implementation_notes=texture_characteristics["implementation"],
            suno_commands=texture_characteristics["suno_commands"]
        )
        elements.append(texture_element)

        return elements

    def _get_rhythm_characteristics(self, emotion: EmotionalInsight) -> Dict[str, Any]:
        """Get rhythm characteristics for the given emotion"""
        if emotion.emotion in self.emotional_rhythms:
            return self.emotional_rhythms[emotion.emotion]

        # Fallback based on intensity
        if emotion.intensity > 0.7:
            return {
                "rhythm_characteristics": ["intense", "driving", "complex"],
                "tempo_modifier": 1.2,
                "complexity_boost": 0.2
            }
        else:
            return {
                "rhythm_characteristics": ["gentle", "flowing", "simple"],
                "tempo_modifier": 0.9,
                "complexity_boost": -0.1
            }

    def _get_tempo_recommendations(self, emotional_profile: EmotionalProfile) -> Dict[str, Any]:
        """Get tempo recommendations based on emotional profile"""
        primary_emotion = emotional_profile.primary_emotions[0]
        base_tempo = 100  # Default tempo

        # Adjust based on emotion
        if primary_emotion.emotion in self.emotional_rhythms:
            modifier = self.emotional_rhythms[primary_emotion.emotion]["tempo_modifier"]
            base_tempo = int(base_tempo * modifier)

        # Adjust based on intensity
        intensity_adjustment = int((primary_emotion.intensity - 0.5) * 40)
        final_tempo = base_tempo + intensity_adjustment

        return {
            "recommended_tempo": final_tempo,
            "tempo_range": (final_tempo - 10, final_tempo + 10),
            "tempo_reasoning": f"Based on {primary_emotion.emotion} emotion with {primary_emotion.intensity:.1f} intensity"
        }

    def _get_melody_characteristics(self, emotional_profile: EmotionalProfile) -> Dict[str, Any]:
        """Get melody characteristics based on emotional profile"""
        primary_emotion = emotional_profile.primary_emotions[0].emotion

        melody_mappings = {
            "melancholic": {
                "description": "Descending melodic lines with minor intervals",
                "purpose": "Express sadness and longing through melodic contour",
                "implementation": ["Use minor scales", "Emphasize descending phrases", "Include expressive bends"],
                "suno_commands": ["[minor_melody]", "[descending_phrases]", "[expressive_vocals]"]
            },
            "hopeful": {
                "description": "Ascending melodic lines with major intervals",
                "purpose": "Convey optimism and forward momentum",
                "implementation": ["Use major scales", "Emphasize ascending phrases", "Bright vocal delivery"],
                "suno_commands": ["[major_melody]", "[uplifting_vocals]", "[ascending_phrases]"]
            },
            "anxious": {
                "description": "Irregular melodic patterns with tension",
                "purpose": "Create musical tension reflecting inner anxiety",
                "implementation": ["Use dissonant intervals", "Irregular phrase lengths", "Restless melodic motion"],
                "suno_commands": ["[tense_melody]", "[irregular_phrases]", "[anxious_vocals]"]
            },
            "passionate": {
                "description": "Wide melodic ranges with dramatic intervals",
                "purpose": "Express intense emotion through melodic extremes",
                "implementation": ["Large interval leaps", "Dynamic vocal delivery", "Emotional peaks"],
                "suno_commands": ["[dramatic_melody]", "[passionate_vocals]", "[wide_range]"]
            }
        }

        return melody_mappings.get(primary_emotion, {
            "description": "Balanced melodic lines",
            "purpose": "Provide melodic interest",
            "implementation": ["Standard melodic approach"],
            "suno_commands": ["[melodic_vocals]"]
        })

    def _get_harmony_characteristics(self, emotional_profile: EmotionalProfile) -> Dict[str, Any]:
        """Get harmony characteristics based on emotional profile"""
        primary_emotion = emotional_profile.primary_emotions[0].emotion

        harmony_mappings = {
            "melancholic": {
                "description": "Minor key harmonies with added tensions",
                "purpose": "Support melancholic mood with appropriate chord colors",
                "implementation": ["Minor key center", "Add9 and sus chords", "Gentle voice leading"],
                "suno_commands": ["[minor_key]", "[sad_chords]", "[gentle_harmony]"]
            },
            "hopeful": {
                "description": "Major key harmonies with bright extensions",
                "purpose": "Reinforce optimistic feeling with uplifting harmonies",
                "implementation": ["Major key center", "Add9 and maj7 chords", "Bright voicings"],
                "suno_commands": ["[major_key]", "[bright_chords]", "[uplifting_harmony]"]
            },
            "mysterious": {
                "description": "Modal harmonies with ambiguous tonality",
                "purpose": "Create sense of mystery through harmonic ambiguity",
                "implementation": ["Modal scales", "Suspended chords", "Ambiguous progressions"],
                "suno_commands": ["[modal_harmony]", "[mysterious_chords]", "[ambiguous_key]"]
            },
            "furious": {
                "description": "Dissonant harmonies with aggressive voicings",
                "purpose": "Express anger through harmonic tension",
                "implementation": ["Dissonant intervals", "Power chords", "Aggressive progressions"],
                "suno_commands": ["[aggressive_chords]", "[dissonant_harmony]", "[power_chords]"]
            }
        }

        return harmony_mappings.get(primary_emotion, {
            "description": "Standard harmonic progressions",
            "purpose": "Provide harmonic foundation",
            "implementation": ["Conventional chord progressions"],
            "suno_commands": ["[standard_harmony]"]
        })

    def _get_texture_characteristics(self, emotional_profile: EmotionalProfile) -> Dict[str, Any]:
        """Get texture characteristics based on emotional profile"""
        complexity = emotional_profile.emotional_complexity
        emotional_profile.primary_emotions[0].emotion

        if complexity > 0.7:
            return {
                "description": "Dense, layered texture with multiple elements",
                "purpose": "Reflect emotional complexity through musical density",
                "implementation": ["Multiple instrumental layers", "Countermelodies", "Rich arrangements"],
                "suno_commands": ["[layered_texture]", "[rich_arrangement]", "[multiple_voices]"]
            }
        elif complexity < 0.3:
            return {
                "description": "Sparse, minimal texture with space",
                "purpose": "Allow emotional content to breathe",
                "implementation": ["Minimal instrumentation", "Spacious arrangements", "Focus on essentials"],
                "suno_commands": ["[minimal_texture]", "[spacious_arrangement]", "[simple_instrumentation]"]
            }
        else:
            return {
                "description": "Balanced texture with moderate density",
                "purpose": "Support emotional content without overwhelming",
                "implementation": ["Balanced instrumentation", "Clear arrangements", "Appropriate density"],
                "suno_commands": ["[balanced_texture]", "[clear_arrangement]", "[moderate_instrumentation]"]
            }

    def _generate_suno_commands(self, patterns: List[BeatPattern], emotional_profile: EmotionalProfile) -> List[str]:
        """Generate practical Suno AI commands based on patterns and emotions"""
        commands = []

        if not patterns:
            return ["[standard_beat]"]

        primary_pattern = patterns[0]
        primary_emotion = emotional_profile.primary_emotions[0]

        # Tempo command
        tempo = int((primary_pattern.tempo_range[0] + primary_pattern.tempo_range[1]) / 2)
        commands.append(f"[{tempo}bpm]")

        # Genre/style command
        if primary_pattern.genre_associations:
            genre = primary_pattern.genre_associations[0]
            commands.append(f"[{genre}]")

        # Emotional directive
        commands.append(f"[{primary_emotion.emotion}_mood]")

        # Rhythm pattern command
        rhythm_name = primary_pattern.name.lower().replace(" ", "_")
        commands.append(f"[{rhythm_name}_beat]")

        # Energy level command
        commands.append(f"[{primary_pattern.energy_level}_energy]")

        # Complexity command based on emotional intensity
        if primary_emotion.intensity > 0.7:
            commands.append("[complex_arrangement]")
        elif primary_emotion.intensity < 0.3:
            commands.append("[simple_arrangement]")
        else:
            commands.append("[moderate_arrangement]")

        # Time signature if not 4/4
        if primary_pattern.time_signature != "4/4":
            commands.append(f"[{primary_pattern.time_signature}_time]")

        return commands

    def _generate_production_notes(self, emotional_profile: EmotionalProfile, patterns: List[BeatPattern]) -> List[str]:
        """Generate production notes based on emotional profile and patterns"""
        notes = []

        primary_emotion = emotional_profile.primary_emotions[0]

        # Notes based on emotion
        emotion_notes = {
            "melancholic": [
                "Use reverb to create spaciousness and reflection",
                "Keep dynamics subtle to maintain intimate feeling",
                "Consider tape saturation for warmth"
            ],
            "hopeful": [
                "Bright EQ to enhance optimistic feeling",
                "Moderate compression to maintain energy",
                "Add harmonic excitement in upper frequencies"
            ],
            "anxious": [
                "Use irregular panning to create restlessness",
                "Apply subtle distortion to increase tension",
                "Vary dynamics to maintain unease"
            ],
            "furious": [
                "Heavy compression for aggressive sound",
                "Boost midrange frequencies for punch",
                "Use parallel compression for intensity"
            ],
            "contemplative": [
                "Minimal processing to preserve natural sound",
                "Focus on clarity and space",
                "Use gentle EQ to enhance presence"
            ]
        }

        if primary_emotion.emotion in emotion_notes:
            notes.extend(emotion_notes[primary_emotion.emotion])

        # Notes based on complexity
        if emotional_profile.emotional_complexity > 0.7:
            notes.append("Balance multiple elements carefully to avoid muddiness")
            notes.append("Use frequency separation techniques for clarity")
        elif emotional_profile.emotional_complexity < 0.3:
            notes.append("Focus on perfecting fewer elements")
            notes.append("Use space as a compositional element")

        # Notes based on patterns
        if patterns:
            pattern = patterns[0]
            if pattern.energy_level == "high":
                notes.append("Maintain energy through consistent dynamics")
            elif pattern.energy_level == "low":
                notes.append("Preserve intimacy through gentle processing")

        return notes

    def _generate_default_patterns(self, genre_preferences: List[str] = None) -> Dict[str, Any]:
        """Generate default patterns when no emotions are detected"""
        # Use contemplative/neutral patterns as default
        default_pattern = self.beat_patterns["ambient_pulse"]

        # If genre preferences are provided, try to match them
        if genre_preferences:
            for genre in genre_preferences:
                for pattern in self.beat_patterns.values():
                    if genre in pattern.genre_associations:
                        default_pattern = pattern
                        break

        return {
            "primary_emotion": "neutral",
            "emotional_intensity": 0.5,
            "selected_patterns": [default_pattern.name],
            "rhythm_characteristics": {
                "rhythm_characteristics": ["steady", "balanced", "neutral"],
                "tempo_modifier": 1.0,
                "complexity_boost": 0.0
            },
            "tempo_recommendations": {
                "recommended_tempo": 90,
                "tempo_range": (80, 100),
                "tempo_reasoning": "Default tempo for neutral content"
            },
            "beat_patterns": {
                default_pattern.name: {
                    "time_signature": default_pattern.time_signature,
                    "tempo_range": default_pattern.tempo_range,
                    "complexity": default_pattern.complexity,
                    "energy_level": default_pattern.energy_level,
                    "kick_pattern": default_pattern.kick_pattern,
                    "snare_pattern": default_pattern.snare_pattern,
                    "hihat_pattern": default_pattern.hihat_pattern,
                    "emotional_fit": default_pattern.emotional_fit
                }
            },
            "rhythm_variations": [
                {
                    "name": "Neutral Variation",
                    "description": "Balanced rhythm for neutral content",
                    "implementation": "Standard rhythm patterns with moderate complexity"
                }
            ],
            "musical_elements": [
                {
                    "type": "rhythm",
                    "description": "Neutral rhythm pattern",
                    "purpose": "Provide steady rhythmic foundation",
                    "implementation": ["Use standard time signature", "Moderate tempo", "Balanced complexity"],
                    "suno_commands": ["[90bpm]", "[neutral_rhythm]"]
                },
                {
                    "type": "melody",
                    "description": "Balanced melodic approach",
                    "purpose": "Provide melodic interest without strong emotional direction",
                    "implementation": ["Use balanced intervals", "Moderate range", "Clear phrasing"],
                    "suno_commands": ["[balanced_melody]", "[clear_vocals]"]
                }
            ],
            "suno_commands": [
                "[90bpm]",
                "[neutral_mood]",
                f"[{default_pattern.name.lower().replace(' ', '_')}_beat]",
                "[balanced_arrangement]"
            ],
            "production_notes": [
                "Use balanced production approach for neutral content",
                "Focus on clarity and natural sound",
                "Maintain moderate dynamics throughout"
            ]
        }
