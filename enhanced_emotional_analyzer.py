#!/usr/bin/env python3

"""
Enhanced Emotional Analyzer for understand_topic_with_emotions tool

This module provides sophisticated emotional analysis capabilities that replace
the generic "contemplative" responses with meaningful, varied emotional insights.
"""

import re
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from collections import Counter

@dataclass
class EmotionalInsight:
    """Represents a specific emotional insight from text analysis"""
    emotion: str
    intensity: float  # 0.0 to 1.0
    context: str
    triggers: List[str]
    musical_implications: Dict[str, Any]

@dataclass
class EmotionalProfile:
    """Complete emotional profile of analyzed content"""
    primary_emotions: List[EmotionalInsight]
    emotional_arc: Dict[str, str]  # beginning, middle, end
    emotional_complexity: float
    dominant_mood: str
    emotional_themes: List[str]
    musical_recommendations: Dict[str, Any]

class EnhancedEmotionalAnalyzer:
    """
    Advanced emotional analysis engine that provides meaningful, varied insights
    instead of generic "contemplative" responses.
    """
    
    def __init__(self):
        self.emotion_patterns = self._initialize_emotion_patterns()
        self.musical_mappings = self._initialize_musical_mappings()
        self.contextual_modifiers = self._initialize_contextual_modifiers()
    
    def _initialize_emotion_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize sophisticated emotion detection patterns"""
        return {
            # Joy and Positive Emotions
            "euphoric": {
                "keywords": ["triumph", "victory", "celebration", "ecstatic", "blissful", "radiant"],
                "intensity_base": 0.9,
                "musical_tempo": 130,
                "musical_key": "major",
                "energy": "high"
            },
            "hopeful": {
                "keywords": ["hope", "optimism", "bright", "dawn", "possibility", "future", "dream", "love", "falling in love", "romance", "vacation", "summer", "joy", "happy"],
                "intensity_base": 0.7,
                "musical_tempo": 100,
                "musical_key": "major",
                "energy": "medium"
            },
            "content": {
                "keywords": ["peaceful", "satisfied", "calm", "serene", "balanced", "harmony"],
                "intensity_base": 0.5,
                "musical_tempo": 80,
                "musical_key": "major",
                "energy": "low"
            },
            
            # Sadness and Melancholy
            "melancholic": {
                "keywords": ["melancholy", "wistful", "bittersweet", "nostalgic", "longing", "yearning", "soulful", "weeping", "mournful", "sad", "sorrowful", "blue", "somber"],
                "intensity_base": 0.6,
                "musical_tempo": 70,
                "musical_key": "minor",
                "energy": "low"
            },
            "sorrowful": {
                "keywords": ["grief", "loss", "mourning", "despair", "heartbreak", "anguish"],
                "intensity_base": 0.8,
                "musical_tempo": 60,
                "musical_key": "minor",
                "energy": "low"
            },
            "lonely": {
                "keywords": ["alone", "isolated", "abandoned", "solitude", "empty", "void"],
                "intensity_base": 0.7,
                "musical_tempo": 75,
                "musical_key": "minor",
                "energy": "low"
            },
            
            # Fear and Anxiety
            "anxious": {
                "keywords": ["worry", "nervous", "tension", "stress", "uncertain", "restless"],
                "intensity_base": 0.6,
                "musical_tempo": 110,
                "musical_key": "minor",
                "energy": "medium"
            },
            "terrified": {
                "keywords": ["terror", "horror", "panic", "dread", "nightmare", "fear"],
                "intensity_base": 0.9,
                "musical_tempo": 140,
                "musical_key": "diminished",
                "energy": "high"
            },
            "apprehensive": {
                "keywords": ["cautious", "wary", "hesitant", "doubtful", "suspicious"],
                "intensity_base": 0.5,
                "musical_tempo": 90,
                "musical_key": "minor",
                "energy": "medium"
            },
            
            # Anger and Intensity
            "furious": {
                "keywords": ["rage", "fury", "anger", "wrath", "outrage", "indignation"],
                "intensity_base": 0.9,
                "musical_tempo": 150,
                "musical_key": "minor",
                "energy": "high"
            },
            "frustrated": {
                "keywords": ["frustration", "irritation", "annoyance", "impatience", "exasperation"],
                "intensity_base": 0.6,
                "musical_tempo": 120,
                "musical_key": "minor",
                "energy": "medium"
            },
            
            # Complex Emotions
            "conflicted": {
                "keywords": ["torn", "divided", "conflicted", "ambivalent", "uncertain", "dilemma"],
                "intensity_base": 0.7,
                "musical_tempo": 95,
                "musical_key": "modal",
                "energy": "medium"
            },
            "passionate": {
                "keywords": ["passion", "intense", "fervent", "ardent", "burning", "consuming", "fierce", "determination", "courage", "battle", "charged"],
                "intensity_base": 0.8,
                "musical_tempo": 125,
                "musical_key": "major",
                "energy": "high"
            },
            "contemplative": {
                "keywords": ["thoughtful", "reflective", "pensive", "meditative", "introspective"],
                "intensity_base": 0.4,
                "musical_tempo": 85,
                "musical_key": "modal",
                "energy": "low"
            },
            "mysterious": {
                "keywords": ["mystery", "enigma", "unknown", "hidden", "secret", "cryptic"],
                "intensity_base": 0.6,
                "musical_tempo": 95,
                "musical_key": "minor",
                "energy": "medium"
            }
        }
    
    def _initialize_musical_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize mappings from emotions to musical elements"""
        return {
            "tempo_modifiers": {
                "urgent": 1.3,
                "rushed": 1.4,
                "slow": 0.7,
                "dragging": 0.6,
                "steady": 1.0,
                "building": 1.2
            },
            "rhythm_patterns": {
                "chaotic": "irregular_syncopated_with_breaks",
                "flowing": "flowing_organic_rhythm",
                "driving": "steady_driving_beat",
                "broken": "fragmented_rhythm_with_pauses",
                "pulsing": "rhythmic_pulse_emphasis",
                "floating": "ethereal_rhythm_patterns"
            },
            "sonic_textures": {
                "water": ["flowing_water_textures", "liquid_elements"],
                "air": ["atmospheric_movement", "breathy_textures"],
                "earth": ["grounded_bass_elements", "organic_textures"],
                "fire": ["intense_energy_bursts", "crackling_elements"],
                "metal": ["sharp_metallic_textures", "industrial_elements"],
                "nature": ["organic_environmental_sounds", "natural_textures"]
            }
        }
    
    def _initialize_contextual_modifiers(self) -> Dict[str, float]:
        """Initialize contextual modifiers that affect emotional intensity"""
        return {
            "death": 1.3,
            "love": 1.2,
            "war": 1.4,
            "childhood": 0.8,
            "memory": 0.9,
            "future": 1.1,
            "family": 1.1,
            "betrayal": 1.3,
            "discovery": 1.2,
            "loss": 1.3
        }
    
    def analyze_emotional_content(self, text: str, source_type: str = "general") -> EmotionalProfile:
        """
        Perform comprehensive emotional analysis of text content
        
        Args:
            text: The text content to analyze
            source_type: Type of source material (book, article, etc.)
            
        Returns:
            EmotionalProfile with detailed emotional insights
        """
        # Detect primary emotions
        primary_emotions = self._detect_emotions(text)
        
        # Analyze emotional arc
        emotional_arc = self._analyze_emotional_arc(text)
        
        # Calculate emotional complexity
        emotional_complexity = self._calculate_emotional_complexity(primary_emotions)
        
        # Determine dominant mood
        dominant_mood = self._determine_dominant_mood(primary_emotions)
        
        # Extract emotional themes
        emotional_themes = self._extract_emotional_themes(text, primary_emotions)
        
        # Generate musical recommendations
        musical_recommendations = self._generate_musical_recommendations(
            primary_emotions, emotional_arc, source_type
        )
        
        return EmotionalProfile(
            primary_emotions=primary_emotions,
            emotional_arc=emotional_arc,
            emotional_complexity=emotional_complexity,
            dominant_mood=dominant_mood,
            emotional_themes=emotional_themes,
            musical_recommendations=musical_recommendations
        )
    
    def _detect_emotions(self, text: str) -> List[EmotionalInsight]:
        """Detect emotions in text using sophisticated pattern matching"""
        text_lower = text.lower()
        detected_emotions = []
        
        for emotion_name, emotion_data in self.emotion_patterns.items():
            # Count keyword matches
            matches = []
            for keyword in emotion_data["keywords"]:
                if keyword in text_lower:
                    matches.append(keyword)
            
            if matches:
                # Calculate intensity based on matches and context
                base_intensity = emotion_data["intensity_base"]
                match_boost = min(len(matches) * 0.1, 0.3)
                context_modifier = self._get_context_modifier(text_lower)
                
                intensity = min(base_intensity + match_boost + context_modifier, 1.0)
                
                # Generate musical implications
                musical_implications = {
                    "tempo": emotion_data["musical_tempo"],
                    "key": emotion_data["musical_key"],
                    "energy": emotion_data["energy"],
                    "suggested_instruments": self._suggest_instruments(emotion_name),
                    "production_notes": self._generate_production_notes(emotion_name, intensity)
                }
                
                # Extract context around matches
                context = self._extract_context(text, matches[0])
                
                emotion_insight = EmotionalInsight(
                    emotion=emotion_name,
                    intensity=intensity,
                    context=context,
                    triggers=matches,
                    musical_implications=musical_implications
                )
                
                detected_emotions.append(emotion_insight)
        
        # Sort by intensity and return top emotions
        detected_emotions.sort(key=lambda x: x.intensity, reverse=True)
        return detected_emotions[:5]  # Return top 5 emotions
    
    def _get_context_modifier(self, text: str) -> float:
        """Get contextual modifier based on text content"""
        modifier = 0.0
        for context, value in self.contextual_modifiers.items():
            if context in text:
                modifier += (value - 1.0) * 0.1  # Scale down the modifier
        return min(modifier, 0.3)  # Cap the modifier
    
    def _extract_context(self, text: str, keyword: str) -> str:
        """Extract context around a keyword match"""
        text_lower = text.lower()
        keyword_pos = text_lower.find(keyword)
        if keyword_pos == -1:
            return ""
        
        # Extract 50 characters before and after
        start = max(0, keyword_pos - 50)
        end = min(len(text), keyword_pos + len(keyword) + 50)
        context = text[start:end].strip()
        
        return context
    
    def _analyze_emotional_arc(self, text: str) -> Dict[str, str]:
        """Analyze the emotional progression through the text"""
        # Split text into three parts
        text_length = len(text)
        part_size = text_length // 3
        
        beginning = text[:part_size]
        middle = text[part_size:2*part_size]
        end = text[2*part_size:]
        
        # Analyze each part
        beginning_emotions = self._detect_emotions(beginning)
        middle_emotions = self._detect_emotions(middle)
        end_emotions = self._detect_emotions(end)
        
        return {
            "beginning": beginning_emotions[0].emotion if beginning_emotions else "neutral",
            "middle": middle_emotions[0].emotion if middle_emotions else "neutral",
            "end": end_emotions[0].emotion if end_emotions else "neutral"
        }
    
    def _calculate_emotional_complexity(self, emotions: List[EmotionalInsight]) -> float:
        """Calculate the emotional complexity of the content"""
        if not emotions:
            return 0.0
        
        # Complexity based on number of emotions and intensity variation
        num_emotions = len(emotions)
        intensity_variance = self._calculate_variance([e.intensity for e in emotions])
        
        # Normalize complexity score
        complexity = (num_emotions * 0.2) + (intensity_variance * 0.8)
        return min(complexity, 1.0)
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _determine_dominant_mood(self, emotions: List[EmotionalInsight]) -> str:
        """Determine the overall dominant mood"""
        if not emotions:
            return "neutral"
        
        # Weight emotions by intensity
        weighted_emotions = {}
        for emotion in emotions:
            if emotion.emotion not in weighted_emotions:
                weighted_emotions[emotion.emotion] = 0
            weighted_emotions[emotion.emotion] += emotion.intensity
        
        # Return the emotion with highest weighted score
        return max(weighted_emotions.items(), key=lambda x: x[1])[0]
    
    def _extract_emotional_themes(self, text: str, emotions: List[EmotionalInsight]) -> List[str]:
        """Extract high-level emotional themes from the content"""
        themes = []
        text_lower = text.lower()
        
        # Theme detection based on content and emotions
        theme_patterns = {
            "transformation": ["change", "growth", "evolution", "becoming", "transformation"],
            "conflict": ["struggle", "fight", "battle", "conflict", "opposition"],
            "love": ["love", "romance", "affection", "devotion", "heart"],
            "loss": ["loss", "death", "ending", "goodbye", "farewell"],
            "discovery": ["discovery", "revelation", "truth", "understanding", "realization"],
            "journey": ["journey", "path", "travel", "quest", "adventure"],
            "identity": ["identity", "self", "who am i", "purpose", "meaning"],
            "redemption": ["redemption", "forgiveness", "second chance", "atonement"],
            "sacrifice": ["sacrifice", "giving up", "cost", "price", "trade-off"],
            "hope": ["hope", "future", "possibility", "dream", "aspiration"]
        }
        
        for theme, keywords in theme_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        # Add themes based on detected emotions
        emotion_themes = {
            "melancholic": "nostalgia",
            "hopeful": "optimism",
            "terrified": "survival",
            "passionate": "intensity",
            "conflicted": "inner_struggle"
        }
        
        for emotion in emotions:
            if emotion.emotion in emotion_themes:
                theme = emotion_themes[emotion.emotion]
                if theme not in themes:
                    themes.append(theme)
        
        return themes[:5]  # Return top 5 themes
    
    def _generate_musical_recommendations(
        self, 
        emotions: List[EmotionalInsight], 
        emotional_arc: Dict[str, str],
        source_type: str
    ) -> Dict[str, Any]:
        """Generate comprehensive musical recommendations based on emotional analysis"""
        if not emotions:
            return {"error": "No emotions detected for musical recommendations"}
        
        primary_emotion = emotions[0]
        
        # Base recommendations from primary emotion
        recommendations = {
            "tempo": primary_emotion.musical_implications["tempo"],
            "key_signature": primary_emotion.musical_implications["key"],
            "energy_level": primary_emotion.musical_implications["energy"],
            "primary_emotion": primary_emotion.emotion,
            "emotional_intensity": primary_emotion.intensity
        }
        
        # Adjust based on emotional arc
        if emotional_arc["beginning"] != emotional_arc["end"]:
            recommendations["structure_suggestion"] = "dynamic_progression"
            recommendations["arc_description"] = f"Evolves from {emotional_arc['beginning']} to {emotional_arc['end']}"
        else:
            recommendations["structure_suggestion"] = "consistent_mood"
            recommendations["arc_description"] = f"Maintains {emotional_arc['beginning']} throughout"
        
        # Genre suggestions based on emotions and source type
        recommendations["genre_suggestions"] = self._suggest_genres(emotions, source_type)
        
        # Instrumentation suggestions
        recommendations["instrumentation"] = self._suggest_comprehensive_instrumentation(emotions)
        
        # Production techniques
        recommendations["production_techniques"] = self._suggest_production_techniques(emotions)
        
        return recommendations
    
    def _suggest_instruments(self, emotion: str) -> List[str]:
        """Suggest instruments based on emotion"""
        instrument_mappings = {
            "melancholic": ["piano", "strings", "acoustic_guitar", "cello"],
            "hopeful": ["acoustic_guitar", "piano", "light_percussion", "flute"],
            "terrified": ["dissonant_strings", "heavy_percussion", "distorted_synths"],
            "furious": ["electric_guitar", "heavy_drums", "bass", "aggressive_synths"],
            "contemplative": ["piano", "ambient_pads", "soft_strings", "acoustic_guitar"],
            "passionate": ["strings", "piano", "dynamic_percussion", "brass"],
            "mysterious": ["ambient_textures", "subtle_percussion", "ethereal_pads"]
        }
        
        return instrument_mappings.get(emotion, ["piano", "strings", "light_percussion"])
    
    def _generate_production_notes(self, emotion: str, intensity: float) -> List[str]:
        """Generate production notes based on emotion and intensity"""
        base_notes = {
            "melancholic": ["Use reverb for spaciousness", "Keep dynamics subtle"],
            "hopeful": ["Bright EQ", "Uplifting chord progressions"],
            "terrified": ["Dissonant harmonies", "Sudden dynamic changes"],
            "furious": ["Heavy compression", "Aggressive EQ"],
            "contemplative": ["Minimal processing", "Focus on clarity"],
            "passionate": ["Dynamic range", "Emotional builds"]
        }
        
        notes = base_notes.get(emotion, ["Standard production"])
        
        # Add intensity-based notes
        if intensity > 0.8:
            notes.append("High emotional intensity - emphasize dynamics")
        elif intensity < 0.3:
            notes.append("Subtle emotional content - focus on nuance")
        
        return notes
    
    def _suggest_genres(self, emotions: List[EmotionalInsight], source_type: str) -> List[str]:
        """Suggest musical genres based on emotions and source type"""
        genre_mappings = {
            "melancholic": ["indie_folk", "ambient", "neo_classical"],
            "hopeful": ["indie_pop", "folk", "uplifting_electronic"],
            "terrified": ["dark_ambient", "industrial", "horror_soundtrack"],
            "furious": ["metal", "punk", "aggressive_electronic"],
            "contemplative": ["ambient", "neo_classical", "meditation"],
            "passionate": ["orchestral", "dramatic", "cinematic"],
            "mysterious": ["dark_ambient", "experimental", "atmospheric"]
        }
        
        suggested_genres = []
        for emotion in emotions[:3]:  # Top 3 emotions
            genres = genre_mappings.get(emotion.emotion, [])
            suggested_genres.extend(genres)
        
        # Remove duplicates while preserving order
        unique_genres = []
        for genre in suggested_genres:
            if genre not in unique_genres:
                unique_genres.append(genre)
        
        return unique_genres[:5]  # Return top 5 genre suggestions
    
    def _suggest_comprehensive_instrumentation(self, emotions: List[EmotionalInsight]) -> Dict[str, List[str]]:
        """Suggest comprehensive instrumentation based on emotional profile"""
        instrumentation = {
            "primary": [],
            "secondary": [],
            "texture": [],
            "rhythm": []
        }
        
        for emotion in emotions[:3]:  # Top 3 emotions
            instruments = self._suggest_instruments(emotion.emotion)
            
            # Categorize instruments
            if not instrumentation["primary"]:
                instrumentation["primary"] = instruments[:2]
            
            instrumentation["secondary"].extend(instruments[2:])
            
            # Add texture elements based on emotion
            if emotion.emotion in ["mysterious", "contemplative"]:
                instrumentation["texture"].extend(["ambient_pads", "ethereal_textures"])
            elif emotion.emotion in ["furious", "passionate"]:
                instrumentation["texture"].extend(["dynamic_elements", "intensity_builders"])
        
        # Remove duplicates
        for category in instrumentation:
            instrumentation[category] = list(set(instrumentation[category]))
        
        return instrumentation
    
    def _suggest_production_techniques(self, emotions: List[EmotionalInsight]) -> List[str]:
        """Suggest production techniques based on emotional profile"""
        techniques = []
        
        for emotion in emotions[:3]:
            emotion_techniques = {
                "melancholic": ["reverb_for_space", "subtle_compression", "warm_eq"],
                "hopeful": ["bright_eq", "moderate_compression", "uplifting_harmonies"],
                "terrified": ["dissonant_processing", "sudden_cuts", "tension_building"],
                "furious": ["heavy_compression", "aggressive_eq", "distortion"],
                "contemplative": ["minimal_processing", "natural_dynamics", "clarity_focus"],
                "passionate": ["dynamic_processing", "emotional_automation", "build_techniques"]
            }
            
            emotion_specific = emotion_techniques.get(emotion.emotion, [])
            techniques.extend(emotion_specific)
        
        # Remove duplicates while preserving order
        unique_techniques = []
        for technique in techniques:
            if technique not in unique_techniques:
                unique_techniques.append(technique)
        
        return unique_techniques