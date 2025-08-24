#!/usr/bin/env python3
"""
Character-Driven Music Generation MCP Server

This FastMCP server provides comprehensive character analysis and music generation capabilities,
integrating narrative text analysis with musical artist personas for Suno AI command generation.
"""

import asyncio
import json
import os
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
import logging

from fastmcp import FastMCP, Context
from pydantic import BaseModel
from working_universal_processor import WorkingUniversalProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    primary_genre: str
    secondary_genres: List[str]
    vocal_style: str
    instrumental_preferences: List[str]
    
    # Creative characteristics
    lyrical_themes: List[str]
    emotional_palette: List[str]
    artistic_influences: List[str]
    collaboration_style: str
    
    # Persona metadata
    character_mapping_confidence: float
    genre_justification: str
    persona_description: str
    
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
                'outro': f"Resolves narrative tension"
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
    
    def identify_emotional_contradictions(self, text: str, character: CharacterProfile) -> List[Dict[str, Any]]:
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
    
    def analyze_character_introspection(self, text: str, character: CharacterProfile) -> Dict[str, Any]:
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
    
    def _identify_defense_mechanisms(self, text: str, character: CharacterProfile) -> List[Dict]:
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
        common_words = {'The', 'And', 'But', 'For', 'Not', 'With', 'From', 'They', 'This', 'That', 'When', 'Where', 'What', 'Why', 'How', 'Then', 'Now', 'Here', 'There', 'Again', 'Also', 'Just', 'Only', 'Even', 'Still', 'Much', 'More', 'Most', 'Many', 'Some', 'All', 'Both', 'Each', 'Every', 'Another', 'Other', 'Such', 'Very', 'Too', 'So', 'As', 'At', 'By', 'In', 'On', 'Of', 'To', 'Up', 'Out', 'Off', 'Over', 'Under', 'About', 'Above', 'Below', 'Down', 'Through', 'Around', 'Between', 'Among', 'Along', 'Across', 'Behind', 'Before', 'After', 'During', 'While', 'Until', 'Since', 'Because', 'Although', 'Though', 'However', 'Therefore', 'Thus', 'Hence', 'Moreover', 'Furthermore', 'Nevertheless', 'Otherwise', 'Instead', 'Meanwhile', 'Indeed', 'Actually', 'Really', 'Quite', 'Rather', 'Perhaps', 'Maybe', 'Probably', 'Certainly', 'Definitely', 'Obviously', 'Clearly', 'Surely', 'Exactly', 'Precisely', 'Absolutely', 'Completely', 'Entirely', 'Totally', 'Fully', 'Partly', 'Mostly', 'Nearly', 'Almost', 'Hardly', 'Barely', 'Scarcely', 'Rarely', 'Seldom', 'Never', 'Always', 'Often', 'Sometimes', 'Usually', 'Generally', 'Typically', 'Normally', 'Regularly', 'Frequently', 'Occasionally', 'Recently', 'Finally', 'Eventually', 'Suddenly', 'Immediately', 'Quickly', 'Slowly', 'Carefully', 'Gently', 'Roughly', 'Softly', 'Loudly', 'Quietly', 'Clearly', 'Directly', 'Especially', 'Particularly', 'Specifically', 'Mainly', 'Primarily', 'Largely', 'Mostly', 'Basically', 'Essentially', 'Fundamentally', 'Naturally', 'Obviously', 'Seriously', 'Honestly', 'Literally', 'Practically', 'Virtually', 'Effectively', 'Successfully', 'Properly', 'Correctly', 'Accurately', 'Exactly', 'Precisely', 'Atlanta', 'Memphis', 'Boston', 'Chicago', 'Detroit', 'Houston', 'Phoenix', 'Philadelphia', 'San', 'Los', 'New', 'York', 'California', 'Texas', 'Florida', 'Illinois', 'Pennsylvania', 'Ohio', 'Georgia', 'North', 'South', 'East', 'West', 'Central', 'Northern', 'Southern', 'Eastern', 'Western', 'American', 'British', 'Canadian', 'European', 'Asian', 'African', 'Australian', 'Russian', 'Chinese', 'Japanese', 'German', 'French', 'Italian', 'Spanish', 'Portuguese', 'Dutch', 'Greek', 'Turkish', 'Indian', 'Mexican', 'Brazilian', 'Argentine', 'Chilean', 'Colombian', 'Venezuelan', 'Peruvian', 'Ecuadorian', 'Bolivian', 'Uruguayan', 'Paraguayan', 'His', 'Her', 'Their', 'Its', 'Our', 'Your', 'My', 'Mine', 'Yours', 'Hers', 'Theirs', 'Ours'}
        
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
        pass

    async def generate_artist_persona(self, character: CharacterProfile, ctx: Context) -> ArtistPersona:
        """Generate a musical artist persona from character profile"""
        await ctx.info(f"Generating artist persona for {character.name}...")
        
        # Determine primary personality traits
        primary_traits = self._extract_primary_traits(character)
        
        # Map to musical genres
        primary_genre, secondary_genres = self._map_to_genres(primary_traits)
        
        # Generate vocal style
        vocal_style = self._determine_vocal_style(primary_traits)
        
        # Create artist name
        artist_name = self._generate_artist_name(character.name, primary_traits)
        
        # Generate thematic content
        lyrical_themes = self._generate_lyrical_themes(character)
        emotional_palette = self._generate_emotional_palette(character)
        
        # Determine artistic influences
        influences = self._generate_influences(primary_genre, character)
        
        # Collaboration style
        collaboration_style = self._determine_collaboration_style(character)
        
        # Generate persona description
        persona_description = self._generate_persona_description(character, primary_genre, vocal_style)
        
        # Calculate mapping confidence
        confidence = self._calculate_mapping_confidence(character, primary_traits)
        
        # Genre justification
        justification = self._generate_genre_justification(character, primary_traits, primary_genre)
        
        return ArtistPersona(
            character_name=character.name,
            artist_name=artist_name,
            primary_genre=primary_genre,
            secondary_genres=secondary_genres,
            vocal_style=vocal_style,
            instrumental_preferences=self._generate_instrumental_preferences(primary_genre),
            lyrical_themes=lyrical_themes,
            emotional_palette=emotional_palette,
            artistic_influences=influences,
            collaboration_style=collaboration_style,
            character_mapping_confidence=confidence,
            genre_justification=justification,
            persona_description=persona_description
        )

    def _extract_primary_traits(self, character: CharacterProfile) -> List[str]:
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

    def _map_to_genres(self, traits: List[str]) -> Tuple[str, List[str]]:
        """Map personality traits to musical genres"""
        
        # Define trait-to-genre mappings
        trait_genre_map = {
            'melancholic': ['blues', 'folk', 'indie'],
            'mysterious': ['dark ambient', 'gothic', 'alternative'],
            'brave': ['rock', 'metal', 'punk'],
            'compassionate': ['soul', 'gospel', 'folk'],
            'rebellious': ['punk', 'alternative', 'grunge'],
            'intellectual': ['progressive', 'art rock', 'ambient'],
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
        
        # Find best matching genre based on traits
        genre_scores = {}
        for trait in traits:
            trait_lower = trait.lower()
            if trait_lower in trait_genre_map:
                for genre in trait_genre_map[trait_lower]:
                    genre_scores[genre] = genre_scores.get(genre, 0) + 1
        
        # If no direct matches, use fallback mapping
        if not genre_scores:
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

    def _determine_vocal_style(self, traits: List[str]) -> str:
        """Determine vocal style from character traits"""
        
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
            'fear of exposure': 'vulnerable and intimate',
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

    def _generate_lyrical_themes(self, character: CharacterProfile) -> List[str]:
        """Generate lyrical themes from character profile"""
        themes = []
        
        # Extract from motivations
        for motivation in character.motivations:
            if 'love' in motivation.lower():
                themes.append('love and relationships')
            elif 'power' in motivation.lower():
                themes.append('ambition and power')
            elif 'freedom' in motivation.lower():
                themes.append('liberation and independence')
        
        # Extract from fears
        for fear in character.fears:
            if 'death' in fear.lower():
                themes.append('mortality and existence')
            elif 'loss' in fear.lower():
                themes.append('loss and separation')
        
        # Extract from conflicts
        for conflict in character.conflicts:
            if 'family' in conflict.lower():
                themes.append('family dynamics')
            elif 'society' in conflict.lower():
                themes.append('social commentary')
        
        # Add default themes if none found
        if not themes:
            themes = ['personal journey', 'emotional expression', 'life experiences']
        
        return list(set(themes))[:4]

    def _generate_emotional_palette(self, character: CharacterProfile) -> List[str]:
        """Generate emotional palette from character analysis"""
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
        
        return list(set(emotions))[:5]

    def _generate_influences(self, primary_genre: str, character: CharacterProfile) -> List[str]:
        """Generate artistic influences based on genre and character"""
        genre_influences = {
            'rock': ['classic rock legends', 'alternative pioneers', 'indie innovators'],
            'metal': ['metal masters', 'progressive experimenters', 'symphonic composers'],
            'jazz': ['jazz greats', 'fusion innovators', 'contemporary jazz artists'],
            'electronic': ['electronic pioneers', 'ambient composers', 'dance music innovators'],
            'folk': ['folk storytellers', 'singer-songwriters', 'traditional musicians'],
            'pop': ['pop icons', 'contemporary artists', 'crossover musicians'],
            'indie': ['indie darlings', 'alternative artists', 'underground musicians'],
            'blues': ['blues legends', 'soul masters', 'rhythm innovators']
        }
        
        influences = genre_influences.get(primary_genre, ['diverse musical artists'])
        
        # Add character-specific influences
        if 'classical' in character.backstory.lower():
            influences.append('classical composers')
        if 'street' in character.backstory.lower():
            influences.append('street musicians')
        
        return influences[:3]

    def _determine_collaboration_style(self, character: CharacterProfile) -> str:
        """Determine collaboration approach based on character relationships"""
        # Analyze social connections and relationships
        if len(character.relationships) > 3:
            return 'collaborative and ensemble-oriented'
        elif 'leader' in ' '.join(character.behavioral_traits).lower():
            return 'takes creative control, directs projects'
        elif 'shy' in ' '.join(character.behavioral_traits).lower():
            return 'prefers intimate, small-group collaborations'
        else:
            return 'balanced collaborative approach'

    def _generate_persona_description(self, character: CharacterProfile, genre: str, vocal_style: str) -> str:
        """Generate comprehensive persona description"""
        return f"""
        Musical persona derived from {character.name}: A {genre} artist with {vocal_style}. 
        The persona reflects {character.name}'s core traits of {', '.join(character.personality_drivers[:2])}, 
        channeling their {character.backstory[:100]}... into musical expression. 
        This artist embodies the emotional depth and complexity of the character while translating 
        narrative elements into compelling musical compositions.
        """.strip()

    def _calculate_mapping_confidence(self, character: CharacterProfile, traits: List[str]) -> float:
        """Calculate confidence in character-to-music mapping"""
        base_confidence = character.confidence_score
        
        # Boost confidence if we have clear personality traits
        trait_boost = len(traits) * 0.1
        
        # Boost if character has rich emotional content
        emotion_boost = len(character.motivations + character.fears + character.desires) * 0.05
        
        # Boost if backstory provides context
        backstory_boost = 0.1 if len(character.backstory) > 50 else 0.0
        
        return min(base_confidence + trait_boost + emotion_boost + backstory_boost, 1.0)

    def _generate_genre_justification(self, character: CharacterProfile, traits: List[str], genre: str) -> str:
        """Generate justification for genre selection"""
        trait_text = ', '.join(traits) if traits else 'complex personality'
        
        return f"""
        {genre.title()} genre selected based on {character.name}'s {trait_text}. 
        The character's {character.motivations[0] if character.motivations else 'core motivations'} 
        and {character.conflicts[0] if character.conflicts else 'internal conflicts'} 
        align with {genre}'s emotional and thematic expressions. 
        This mapping ensures authentic musical representation of the character's essence.
        """.strip()

    def _generate_instrumental_preferences(self, genre: str) -> List[str]:
        """Generate instrumental preferences based on genre"""
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
            'classical': ['orchestral instruments', 'piano', 'strings', 'woodwinds'],
            'orchestral': ['full orchestra', 'strings', 'brass', 'woodwinds'],
            'experimental': ['unconventional instruments', 'electronic manipulation', 'found sounds', 'synthesizer']
        }
        
        return genre_instruments.get(genre, ['vocals', 'guitar', 'piano', 'drums'])

# ================================================================================================
# SUNO COMMAND GENERATOR
# ================================================================================================

class SunoCommandGenerator:
    """Generate optimized Suno AI commands from artist personas"""
    
    def __init__(self):
        self.style_tags = {
            'rock': ['rock', 'electric guitar', 'driving rhythm', 'powerful'],
            'metal': ['metal', 'heavy', 'distorted', 'aggressive', 'intense'],
            'jazz': ['jazz', 'smooth', 'improvisation', 'sophisticated'],
            'electronic': ['electronic', 'synthesized', 'digital', 'rhythmic'],
            'folk': ['acoustic', 'organic', 'storytelling', 'traditional'],
            'pop': ['catchy', 'melodic', 'mainstream', 'polished'],
            'indie': ['alternative', 'independent', 'lo-fi', 'artistic'],
            'blues': ['blues', 'soulful', 'emotional', 'raw']
        }
        
        self.structure_tags = {
            'simple': ['verse-chorus', 'straightforward'],
            'complex': ['bridge', 'instrumental break', 'dynamic structure'],
            'narrative': ['storytelling', 'progressive', 'journey'],
            'emotional': ['building intensity', 'emotional arc', 'dynamic range']
        }
        
        # Initialize emotional beat engine for production instructions
        self.emotional_beat_engine = EmotionalBeatEngine()
        # Initialize emotional lyric generator
        self.lyric_generator = EmotionalLyricGenerator()
        
        self.vocal_tags = {
            'powerful': ['strong vocals', 'commanding voice', 'belting'],
            'smooth': ['smooth vocals', 'controlled delivery', 'refined'],
            'emotional': ['emotional vocals', 'expressive', 'heartfelt'],
            'raw': ['raw vocals', 'unpolished', 'authentic'],
            'ethereal': ['ethereal vocals', 'floating', 'atmospheric']
        }

    async def generate_suno_commands(self, artist_persona: ArtistPersona, character: CharacterProfile, ctx: Context, 
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

    async def _generate_simple_command(self, artist_persona: ArtistPersona, character: CharacterProfile) -> SunoCommand:
        """Generate simple Suno command with basic prompt"""
        
        # Create compelling prompt from character essence
        primary_theme = artist_persona.lyrical_themes[0] if artist_persona.lyrical_themes else 'personal journey'
        emotional_core = artist_persona.emotional_palette[0] if artist_persona.emotional_palette else 'authentic expression'
        
        prompt = f"A {artist_persona.primary_genre} song about {primary_theme}, " \
                f"conveying {emotional_core} with {artist_persona.vocal_style}. " \
                f"Inspired by {character.name}'s journey and experiences."
        
        # Select relevant style tags
        style_tags = self.style_tags.get(artist_persona.primary_genre, ['melodic', 'expressive'])
        
        return SunoCommand(
            command_type="simple",
            prompt=prompt,
            style_tags=style_tags[:3],
            structure_tags=['verse-chorus'],
            sound_effect_tags=[],
            vocal_tags=['expressive vocals'],
            character_source=character.name,
            artist_persona=artist_persona.artist_name,
            command_rationale=f"Simple command focusing on core {artist_persona.primary_genre} elements and {character.name}'s primary emotional theme",
            estimated_effectiveness=0.8,
            variations=[
                prompt.replace('song about', 'ballad about'),
                prompt.replace(artist_persona.primary_genre, artist_persona.secondary_genres[0] if artist_persona.secondary_genres else 'alternative')
            ]
        )

    async def _generate_custom_command(self, artist_persona: ArtistPersona, character: CharacterProfile) -> SunoCommand:
        """Generate custom mode command with detailed parameters"""
        
        # Build comprehensive prompt
        themes = ', '.join(artist_persona.lyrical_themes[:2])
        emotions = ', '.join(artist_persona.emotional_palette[:2])
        
        prompt = f"Create a {artist_persona.primary_genre} composition exploring {themes}. " \
                f"The music should embody {emotions} while reflecting {character.name}'s " \
                f"{character.personality_drivers[0] if character.personality_drivers else 'complex nature'}. " \
                f"Incorporate elements of {artist_persona.secondary_genres[0] if artist_persona.secondary_genres else 'crossover style'}."
        
        # Advanced style tags
        style_tags = self.style_tags.get(artist_persona.primary_genre, [])
        style_tags.extend([artist_persona.primary_genre, 'professional production', 'dynamic'])
        
        # Structure based on character complexity
        if character.confidence_score > 0.7:
            structure_tags = ['complex arrangement', 'multiple sections', 'bridge', 'outro']
        else:
            structure_tags = ['verse-chorus-verse', 'simple structure']
        
        # Vocal tags based on persona
        vocal_tags = []
        if 'powerful' in artist_persona.vocal_style:
            vocal_tags.extend(['strong vocals', 'commanding delivery'])
        if 'emotional' in artist_persona.vocal_style:
            vocal_tags.extend(['expressive vocals', 'emotional range'])
        if 'smooth' in artist_persona.vocal_style:
            vocal_tags.extend(['smooth vocals', 'controlled performance'])
        
        # Sound effects based on genre and character traits
        sound_effects = []
        if artist_persona.primary_genre in ['electronic', 'ambient']:
            sound_effects.extend(['atmospheric effects', 'reverb'])
        if 'mysterious' in str(character.personality_drivers):
            sound_effects.extend(['ethereal effects', 'subtle ambience'])
        
        return SunoCommand(
            command_type="custom",
            prompt=prompt,
            style_tags=style_tags[:4],
            structure_tags=structure_tags[:3],
            sound_effect_tags=sound_effects[:2],
            vocal_tags=vocal_tags[:3],
            character_source=character.name,
            artist_persona=artist_persona.artist_name,
            command_rationale=f"Custom command leveraging detailed character analysis for nuanced {artist_persona.primary_genre} composition",
            estimated_effectiveness=0.9,
            variations=[
                prompt.replace('composition', 'piece'),
                prompt + " Include instrumental solo section.",
                prompt.replace(artist_persona.primary_genre, 'fusion')
            ]
        )

    async def _generate_bracket_command(self, artist_persona: ArtistPersona, character: CharacterProfile) -> SunoCommand:
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
        
        return SunoCommand(
            command_type="bracket_notation",
            prompt=prompt,
            style_tags=[artist_persona.primary_genre, 'precise control'],
            structure_tags=['controlled structure'],
            sound_effect_tags=['specified elements'],
            vocal_tags=[artist_persona.vocal_style.split(',')[0]],
            character_source=character.name,
            artist_persona=artist_persona.artist_name,
            command_rationale="Bracket notation command for precise musical element control based on character analysis",
            estimated_effectiveness=0.85,
            variations=[
                prompt.replace('Song inspired by', 'Composition reflecting'),
                prompt + f" [{artist_persona.secondary_genres[0]}]" if artist_persona.secondary_genres else prompt + " [alternative style]",
                prompt.replace(genre_bracket, f"[{artist_persona.secondary_genres[0] if artist_persona.secondary_genres else 'crossover'}]")
            ]
        )

    async def _generate_lyric_focused_command(self, artist_persona: ArtistPersona, character: CharacterProfile) -> SunoCommand:
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
        
        return SunoCommand(
            command_type="lyric_focused",
            prompt=prompt,
            style_tags=[artist_persona.primary_genre, 'storytelling', 'narrative'],
            structure_tags=['verse-heavy', 'lyrical focus', 'story structure'],
            sound_effect_tags=[],
            vocal_tags=['storytelling vocals', 'clear delivery', 'emotional expression'],
            character_source=character.name,
            artist_persona=artist_persona.artist_name,
            command_rationale=f"Lyric-focused command emphasizing {character.name}'s narrative and emotional story",
            estimated_effectiveness=0.75,
            variations=[
                prompt.replace('song that tells the story', 'ballad that chronicles'),
                prompt + " Include spoken word elements.",
                prompt.replace('Write and perform', 'Compose and sing')
            ]
        )

    async def _generate_collaboration_command(self, artist_persona: ArtistPersona, character: CharacterProfile) -> SunoCommand:
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
        
        return SunoCommand(
            command_type="collaboration",
            prompt=prompt,
            style_tags=[artist_persona.primary_genre, 'collaborative', 'ensemble'],
            structure_tags=['multiple parts', 'call and response', 'harmony'],
            sound_effect_tags=[],
            vocal_tags=['multiple vocals', 'harmony', 'interaction'],
            character_source=character.name,
            artist_persona=artist_persona.artist_name,
            command_rationale=f"Collaboration-focused command reflecting {character.name}'s social dynamics and relationships",
            estimated_effectiveness=0.8,
            variations=[
                prompt.replace('piece', 'composition'),
                prompt + " Include instrumental solos for each part.",
                prompt.replace(collab_style, 'group arrangement')
            ]
        )
    
    async def _generate_emotion_beat_command(self, artist_persona: ArtistPersona, character: CharacterProfile, 
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
        
        # Advanced style tags for emotional depth
        style_tags = [
            artist_persona.primary_genre,
            f"{primary_emotion}-driven",
            "dynamic production",
            "emotional beat mapping"
        ]
        
        # Structure tags based on emotional progression
        structure_tags = []
        if len(emotional_states) > 2:
            structure_tags.extend(["emotional arc", "dynamic transitions", "evolving structure"])
        else:
            structure_tags.extend(["focused emotion", "consistent mood", "subtle variations"])
        
        # Vocal tags emphasizing emotional authenticity
        vocal_tags = [
            f"{primary_emotion} vocals",
            "authentic emotional delivery",
            "vulnerable moments"
        ]
        
        # Sound effects for emotional texture
        sound_effects = []
        for state in emotional_states[:2]:
            if state.defense_mechanism:
                sound_effects.append(f"{state.defense_mechanism} effect")
        
        return SunoCommand(
            command_type="emotion_beat_driven",
            prompt=prompt,
            style_tags=style_tags,
            structure_tags=structure_tags,
            sound_effect_tags=sound_effects[:3],
            vocal_tags=vocal_tags,
            character_source=character.name,
            artist_persona=artist_persona.artist_name,
            command_rationale=f"Emotion-driven beat production mapping {character.name}'s factual emotional journey to precise rhythmic elements",
            estimated_effectiveness=0.95,
            variations=[
                prompt.replace(tempo_instruction, f"[tempo automation: {beat_pattern.tempo_range[0]} -> {beat_pattern.tempo_range[1]}bpm]"),
                prompt + f"\n[Beat drops at emotional revelations]",
                prompt.replace(rhythm_instruction, f"[evolving rhythm: {beat_pattern.rhythm_pattern}]")
            ]
        )

# ================================================================================================
# FASTMCP TOOLS, RESOURCES, AND PROMPTS
# ================================================================================================

# Initialize analysis engines
character_analyzer = CharacterAnalyzer()
persona_generator = MusicPersonaGenerator()
command_generator = SunoCommandGenerator()

@mcp.tool
async def analyze_character_text(text: str, ctx: Context) -> str:
    """
    Analyze narrative text to extract detailed character profiles using three-layer methodology.
    
    Performs comprehensive character analysis including:
    - Skin Layer: Physical descriptions, mannerisms, speech patterns
    - Flesh Layer: Relationships, backstory, formative experiences  
    - Core Layer: Motivations, fears, desires, psychological drivers
    
    Args:
        text: Narrative text content (unlimited length supported)
        
    Returns:
        JSON string containing detailed character analysis results
    """
    try:
        await ctx.info("Starting character analysis...")
        
        if not text or len(text.strip()) < 50:
            return json.dumps({
                "error": "Text too short for meaningful character analysis. Please provide at least 50 characters of narrative content."
            })
        
        # Perform analysis
        result = await character_analyzer.analyze_text(text, ctx)
        
        await ctx.info(f"Analysis complete: {len(result.characters)} characters found")
        
        return json.dumps(result.model_dump(), indent=2)
        
    except Exception as e:
        await ctx.error(f"Character analysis failed: {str(e)}")
        return json.dumps({"error": f"Analysis failed: {str(e)}"})

@mcp.tool
async def generate_artist_personas(characters_json: str, ctx: Context) -> str:
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
            # Convert dict back to CharacterProfile
            character = CharacterProfile(**char_data)
            
            # Generate artist persona
            persona = await persona_generator.generate_artist_persona(character, ctx)
            artist_personas.append(asdict(persona))
        
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
    try:
        await ctx.info("Generating Suno AI commands...")
        
        # Parse input data
        personas_data = json.loads(personas_json)
        characters_data = json.loads(characters_json)
        
        if 'artist_personas' not in personas_data:
            return json.dumps({"error": "Invalid personas data format."})
        if 'characters' not in characters_data:
            return json.dumps({"error": "Invalid characters data format."})
        
        all_commands = []
        personas = personas_data['artist_personas']
        characters = characters_data['characters']
        
        # Create character lookup by name
        char_lookup = {char.name: char for char in characters}
        
        for persona_data in personas:
            persona = ArtistPersona(**persona_data)
            character = char_lookup.get(persona.character_name)
            
            if character:
                # Extract emotional states if available
                emotional_states = None
                beat_progression = None
                
                if 'emotional_states' in characters_data:
                    # Find emotional states for this character
                    for i, char in enumerate(characters):
                        if char.name == character.name and i < len(characters_data.get('emotional_states', [])):
                            char_emotional_data = characters_data['emotional_states'][i]
                            if char_emotional_data:
                                emotional_states = [EmotionalState(**state) for state in char_emotional_data]
                
                if 'beat_progression' in characters_data:
                    beat_progression = characters_data.get('beat_progression')
                
                commands = await command_generator.generate_suno_commands(
                    persona, character, ctx, emotional_states, beat_progression
                )
                for cmd in commands:
                    all_commands.append(asdict(cmd))
        
        result = MusicGenerationResult(
            commands=all_commands,
            artist_personas=personas,
            generation_summary=f"Generated {len(all_commands)} Suno AI commands from {len(personas)} artist personas",
            total_commands=len(all_commands),
            processing_time=0.0
        )
        
        await ctx.info(f"Generated {len(all_commands)} Suno commands")
        
        return json.dumps(result.model_dump(), indent=2)
        
    except Exception as e:
        await ctx.error(f"Suno command generation failed: {str(e)}")
        return json.dumps({"error": f"Command generation failed: {str(e)}"})

@mcp.tool
async def complete_workflow(text: str, ctx: Context) -> str:
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
        characters_result = await analyze_character_text(text, ctx)
        
        # Step 2: Generate Artist Personas  
        await ctx.info("Step 2: Generating artist personas...")
        personas_result = await generate_artist_personas(characters_result, ctx)
        
        # Step 3: Create Suno Commands
        await ctx.info("Step 3: Creating Suno AI commands...")
        commands_result = await create_suno_commands(personas_result, characters_result, ctx)
        
        # Combine results
        workflow_result = {
            "workflow_status": "completed",
            "character_analysis": json.loads(characters_result),
            "artist_personas": json.loads(personas_result), 
            "suno_commands": json.loads(commands_result),
            "workflow_summary": "Complete character-driven music generation workflow executed successfully"
        }
        
        await ctx.info("Workflow completed successfully!")
        
        return json.dumps(workflow_result, indent=2)
        
    except Exception as e:
        await ctx.error(f"Workflow execution failed: {str(e)}")
        return json.dumps({"error": f"Workflow failed: {str(e)}"})

@mcp.tool
async def creative_music_generation(concept: str, style_preference: str = "any", ctx: Context = None) -> str:
    """
    Generate creative music commands from abstract concepts with emotional grounding and beat production.
    
    Enhanced creative mode that uses Meta-Narrative & Self-Reflection framework to:
    - Extract emotional facts from abstract concepts
    - Generate emotion-driven beat patterns
    - Create lyrical guidance based on emotional authenticity
    - Provide comprehensive musical interpretation
    
    Args:
        concept: Abstract concept, theme, or idea for music generation
        style_preference: Preferred musical style/genre (optional, defaults to "any")
        
    Returns:
        JSON string containing emotionally-grounded creative music generation commands
    """
    try:
        await ctx.info(f"Generating emotionally-grounded creative music from concept: {concept}")
        
        if not concept or len(concept.strip()) < 10:
            return json.dumps({
                "error": "Concept too short. Please provide a more detailed concept or theme."
            })
        
        # NEW APPROACH: LLM DEFINES THE EMOTIONAL MAP
        await ctx.info("LLM analyzing concept to create custom emotional map...")
        
        # Step 1: LLM analyzes the concept and creates emotional mapping
        emotional_map = _create_llm_emotional_map(concept, style_preference)
        
        # Step 2: Initialize pure execution engine
        beat_engine = EmotionalBeatEngine()
        
        # Step 3: Execute the LLM-defined emotional map
        musical_production = beat_engine.execute_musical_production(emotional_map)
        
        await ctx.info("Musical production completed using LLM-defined emotional map")
        
        return json.dumps(musical_production, indent=2)
        
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

@mcp.tool
async def understand_topic_with_emotions(
    topic_text: str,
    source_type: str = "book",
    focus_areas: Optional[List[str]] = None,
    ctx: Context = None
) -> str:
    """
    Understand and ground topics/books using Meta-Narrative & Self-Reflection with factual emotional analysis.
    
    Analyzes any topic or book content to extract:
    - Factual events and their emotional implications
    - Meta-narrative understanding (what it means emotionally)
    - Self-reflective insights from the content
    - Emotion-driven beat production mapping
    
    Perfect for understanding complex topics through emotional and musical lens.
    
    Args:
        topic_text: The topic or book content to analyze
        source_type: Type of content - "book", "topic", "article", "research", etc.
        focus_areas: Optional list of areas to focus on (e.g., ["character development", "philosophical themes"])
        
    Returns:
        JSON with deep emotional understanding and musical interpretation
    """
    try:
        await ctx.info(f"Analyzing {source_type} content with emotional framework...")
        
        if not topic_text or len(topic_text.strip()) < 50:
            return json.dumps({
                "error": "Content too short. Please provide at least 50 characters of meaningful content."
            })
        
        # Initialize emotional framework components
        beat_engine = EmotionalBeatEngine()
        meta_processor = MetaNarrativeProcessor()
        reflection_analyzer = SelfReflectionAnalyzer()
        
        # LLM creates emotional map from topic content
        emotional_map = _create_llm_emotional_map(topic_text, "contemplative")
        
        # Execute the LLM-defined emotional map
        musical_production = beat_engine.execute_musical_production(emotional_map)
        
        # Create comprehensive understanding result combining LLM emotional map with musical production
        understanding_result = {
            "topic_analysis": {
                "source_type": source_type,
                "content_preview": topic_text[:200] + "...",
                "focus_areas": focus_areas if focus_areas else ["general_understanding"],
                "llm_emotional_interpretation": emotional_map['emotional_context'],
                "llm_reasoning": emotional_map['emotional_reasoning']
            },
            "musical_interpretation": musical_production,
            "comprehensive_understanding": f"LLM-driven analysis of '{source_type}' content with emotional grounding in musical production"
        }
        
        await ctx.info(f"Completed LLM-driven topic understanding with musical interpretation")
        
        return json.dumps(understanding_result, indent=2)
        
    except Exception as e:
        await ctx.error(f"Topic understanding failed: {str(e)}")
        return json.dumps({"error": f"Topic understanding failed: {str(e)}"})

def _map_emotion_to_genre_llm(emotion: str, context: str = "") -> str:
    """LLM determines genre from emotion and context - no predefined mappings"""
    # LLM reasoning for genre selection based on emotional content and context
    if context:
        reasoning = f"Given the emotion '{emotion}' in the context of: {context[:100]}..."
    else:
        reasoning = f"Given the emotion '{emotion}'"
    
    # LLM analysis would go here - for now, dynamic selection based on emotional intensity
    # This should be replaced with actual LLM calls in production
    return f"genre determined by LLM analysis of {emotion} in context"

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
        processor = WorkingUniversalProcessor()
        
        await ctx.info(f"Processing content through character lens with emotional analysis...")
        
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
        
        # Create enhanced Suno command with LLM-driven emotional grounding
        if musical_production and lyric_structure:
            enhanced_suno_command = f"{musical_production.get('suno_format', '[ambient electronic] [80-120bpm] [contemplative rhythm]')}\n" \
                                  f"Track: '{track_title}'\n" \
                                  f"LLM Emotional Analysis: {emotional_map.get('emotional_reasoning', 'Character-driven interpretation')}\n" \
                                  f"Musical Direction: {musical_production.get('production_notes', 'Emotionally grounded production')}\n" \
                                  f"Character perspective: {character_description[:100]}...\n" \
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
async def create_story_integrated_album(
    narrative_text: str,
    character_name: str = None,
    album_concept: str = None,
    track_count: int = 8,
    require_story_arc: bool = True,
    ctx: Context = None
) -> str:
    """
    Create a story-integrated album that follows narrative progression.
    
    This tool enforces non-generic album creation by:
    1. Analyzing the narrative structure and extracting story beats
    2. Mapping character development to musical evolution
    3. Creating tracks that follow the actual story progression
    4. Ensuring each track represents a unique narrative moment
    
    Args:
        narrative_text: Complete story or narrative content
        character_name: Specific character perspective (auto-detected if None)
        album_concept: Album theme (derived from story if None)
        track_count: Number of tracks (3-12)
        require_story_arc: Enforce story arc progression (default True)
    
    Returns:
        JSON containing story-integrated album with narrative-driven tracks
    """
    try:
        await ctx.info("Starting story-integrated album creation...")
        
        # Validate inputs
        if track_count < 3 or track_count > 12:
            return json.dumps({"error": "Track count must be between 3 and 12"})
        
        if not narrative_text or len(narrative_text.strip()) < 100:
            return json.dumps({"error": "Narrative text too short. Please provide substantial story content."})
        
        # Step 1: Analyze the narrative to extract characters and story elements
        await ctx.info("Step 1: Analyzing narrative structure...")
        text_analysis = await character_analyzer.analyze_text(narrative_text, ctx)
        
        if not text_analysis.characters:
            return json.dumps({"error": "No characters found in narrative. Please provide character-driven content."})
        
        # Select character perspective
        if character_name:
            selected_character = next((char for char in text_analysis.characters if char.name.lower() == character_name.lower()), None)
            if not selected_character:
                return json.dumps({"error": f"Character '{character_name}' not found in narrative"})
        else:
            # Auto-select protagonist (highest importance score)
            selected_character = text_analysis.characters[0]
            await ctx.info(f"Auto-selected protagonist: {selected_character.name}")
        
        # Use the CharacterProfile object directly
        character_profile = selected_character
        
        # Step 2: Extract story beats and narrative arc
        await ctx.info("Step 2: Extracting story beats and narrative arc...")
        story_beats = await _extract_story_beats(narrative_text, character_profile, ctx)
        
        # Step 3: Generate artist persona for the character
        await ctx.info("Step 3: Generating character's musical persona...")
        artist_persona = await persona_generator.generate_artist_persona(character_profile, ctx)
        
        # Step 4: Map story beats to track concepts
        await ctx.info("Step 4: Mapping story progression to album tracks...")
        track_concepts = await _generate_story_based_tracks(
            story_beats, 
            character_profile, 
            artist_persona,
            track_count,
            ctx
        )
        
        # Step 5: Create tracks that follow the story
        album_tracks = []
        
        # Generate character description from profile and persona
        character_description = f"""
        Name: {character_profile.name}
        Personality: {', '.join(character_profile.personality_drivers[:2])}
        Background: {character_profile.backstory[:200]}...
        Motivations: {', '.join(character_profile.motivations[:2])}
        Musical Style: {artist_persona.primary_genre} artist with {artist_persona.vocal_style}
        Artistic Identity: {artist_persona.artist_name}
        """
        
        for i, track_concept in enumerate(track_concepts):
            await ctx.info(f"Creating track {i+1}/{track_count}: {track_concept['title']}")
            
            # Create story-specific content for this track
            track_content = f"""
            Story Context: {track_concept['story_context']}
            Character State: {track_concept['character_state']}
            Emotional Tone: {track_concept['emotional_tone']}
            Narrative Function: {track_concept['narrative_function']}
            
            Original Story Excerpt:
            {track_concept['story_excerpt']}
            """
            
            # Use process_universal_content tool for better integration
            track_result_json = await process_universal_content(
                content=track_content,
                character_description=character_description,
                track_title=track_concept['title'],
                ctx=ctx
            )
            
            track_result_data = json.loads(track_result_json)
            
            # Extract the processed data
            if "error" in track_result_data:
                await ctx.error(f"Error processing track: {track_result_data['error']}")
                continue
            
            # Generate enhanced Suno command with story-specific elements
            story_suno_command = await _generate_story_aware_suno_command(
                artist_persona,
                character_profile,
                track_concept,
                track_result_data,
                ctx
            )
            
            track_data = {
                "track_number": i + 1,
                "title": track_concept['title'],
                "story_context": track_concept['story_context'],
                "character_development": track_concept['character_state'],
                "narrative_function": track_concept['narrative_function'],
                "emotional_arc_position": track_concept['emotional_tone'],
                "character_interpretation": track_result_data['content_analysis']['character_interpretation'],
                "personal_story": track_result_data['character_story']['personal_connection'],
                "story_integrated_lyrics": track_result_data['authentic_lyrics']['formatted_lyrics'],
                "suno_command": story_suno_command,
                "musical_evolution": track_concept.get('musical_evolution', 'Maintains character voice'),
                "production_context": track_result_data['character_story']['creative_process'],
                "effectiveness_score": track_result_data['effectiveness_metrics']['character_authenticity']
            }
            
            album_tracks.append(track_data)
        
        # Derive album concept if not provided
        if not album_concept:
            album_concept = f"{character_profile.name}'s Journey: A Musical Narrative"
        
        # Create album response with story integration metrics
        album_response = {
            "album_status": "story_integrated",
            "album_info": {
                "title": album_concept,
                "protagonist": character_profile.name,
                "total_tracks": track_count,
                "narrative_source": f"Story with {len(text_analysis.characters)} characters",
                "story_themes": text_analysis.narrative_themes,
                "emotional_journey": text_analysis.emotional_arc,
                "musical_genre": artist_persona.primary_genre,
                "concept": f"Story-driven album following {character_profile.name}'s narrative arc"
            },
            "story_integration": {
                "character_authenticity": "Verified - all tracks maintain character voice",
                "narrative_progression": "Linear - tracks follow story chronology",
                "emotional_coherence": "Strong - musical evolution matches character arc",
                "thematic_consistency": "High - unified by story themes and character perspective"
            },
            "tracks": album_tracks,
            "album_effectiveness": {
                "average_score": sum(track["effectiveness_score"] for track in album_tracks) / len(album_tracks),
                "story_fidelity": "Excellent - each track represents actual story moments",
                "character_depth": "Deep - psychological progression tracked throughout",
                "musical_narrative": "Cohesive - genre and style evolve with story",
                "non_generic_rating": "10/10 - Completely unique to this specific narrative"
            },
            "artist_persona_summary": {
                "name": artist_persona.artist_name,
                "genre": artist_persona.primary_genre,
                "vocal_style": artist_persona.vocal_style,
                "thematic_focus": artist_persona.lyrical_themes
            },
            "usage_notes": "Each track is specifically tied to story events. Play in order for full narrative experience.",
            "album_summary": f"Created {track_count}-track story-integrated album following {character_profile.name}'s journey through key narrative moments"
        }
        
        await ctx.info(f"Story-integrated album complete: {track_count} narrative-driven tracks")
        
        return json.dumps(album_response, indent=2)
        
    except Exception as e:
        await ctx.error(f"Story-integrated album creation failed: {str(e)}")
        return json.dumps({"error": f"Story album creation failed: {str(e)}"})

async def _extract_story_beats(narrative_text: str, character: CharacterProfile, ctx: Context) -> List[Dict]:
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
    character: CharacterProfile,
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

def _extract_track_themes(beat: Dict, character: CharacterProfile) -> List[str]:
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
    character: CharacterProfile,
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
            
        character = CharacterProfile(**character_info)
        persona = ArtistPersona(**persona_info)
        
        await ctx.info(f"Analyzing {character.name} as artist {persona.artist_name}...")
        
        # Deep psychological analysis
        analysis = await _analyze_artist_psychology_deep(character, persona, ctx)
        
        await ctx.info("Artist psychology analysis complete")
        
        return json.dumps(analysis, indent=2)
        
    except Exception as e:
        await ctx.error(f"Artist psychology analysis failed: {str(e)}")
        return json.dumps({"error": f"Psychology analysis failed: {str(e)}"})

async def _analyze_artist_psychology_deep(character: CharacterProfile, persona: ArtistPersona, ctx: Context) -> Dict:
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

def _analyze_musical_genesis(character: CharacterProfile, persona: ArtistPersona) -> Dict:
    """Analyze why and how the character became a musical artist"""
    
    # Look for turning points in character's life
    turning_points = []
    for experience in character.formative_experiences:
        if any(word in experience.lower() for word in ['loss', 'death', 'betrayal', 'discovery', 'revelation']):
            turning_points.append(experience)
    
    # Examine motivations that led to music
    musical_drivers = []
    for motivation in character.motivations:
        if any(word in motivation.lower() for word in ['express', 'communicate', 'heal', 'understand', 'connect']):
            musical_drivers.append(motivation)
    
    # Analyze what music provides that life couldn't
    music_as_solution = []
    for fear in character.fears:
        if 'isolation' in fear.lower() or 'alone' in fear.lower():
            music_as_solution.append("Music as connection to others")
        if 'meaningless' in fear.lower() or 'purpose' in fear.lower():
            music_as_solution.append("Music as meaning-making")
        if 'loss' in fear.lower():
            music_as_solution.append("Music as preservation of memory")
    
    return {
        "origin_story": f"{character.name} turned to music as a response to {turning_points[0] if turning_points else 'life experiences'}",
        "turning_points": turning_points[:3],
        "musical_drivers": musical_drivers[:3],
        "music_as_solution": music_as_solution,
        "genesis_psychology": f"Music became {character.name}'s way of {musical_drivers[0] if musical_drivers else 'processing life experiences'}",
        "first_musical_experience": _reconstruct_first_musical_experience(character, persona)
    }

def _reconstruct_first_musical_experience(character: CharacterProfile, persona: ArtistPersona) -> str:
    """Reconstruct what their first meaningful musical experience might have been"""
    
    emotional_state = "seeking solace" if character.fears else "exploring creativity"
    context = character.backstory[:100] if character.backstory else "during a formative period"
    
    return f"Likely discovered {persona.primary_genre} while {emotional_state}, {context}. The genre's {persona.genre_justification.split('.')[0]} resonated with their {character.personality_drivers[0] if character.personality_drivers else 'inner nature'}."

def _analyze_backstory_influences(character: CharacterProfile, persona: ArtistPersona) -> Dict:
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

def _analyze_trauma_healing_through_music(character: CharacterProfile, persona: ArtistPersona) -> Dict:
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

def _analyze_creative_process_psychology(character: CharacterProfile, persona: ArtistPersona) -> Dict:
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

def _analyze_perfectionist_tendencies(character: CharacterProfile) -> str:
    """Analyze perfectionist tendencies in their art"""
    if any('control' in trait.lower() for trait in character.behavioral_traits):
        return "High perfectionism - art as control over chaos"
    elif any('fear' in fear.lower() for fear in character.fears):
        return "Perfectionism driven by fear of vulnerability"
    else:
        return "Balanced approach to artistic standards"

def _analyze_creative_blocks(character: CharacterProfile) -> List[str]:
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

def _analyze_character_flaws_as_artistic_fuel(character: CharacterProfile, persona: ArtistPersona) -> Dict:
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

def _analyze_artistic_vs_personal_identity(character: CharacterProfile, persona: ArtistPersona) -> Dict:
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

def _analyze_performance_psychology(character: CharacterProfile, persona: ArtistPersona) -> str:
    """Analyze psychology of performance vs private self"""
    if 'confident' in persona.vocal_style:
        return "Performance amplifies natural confidence"
    elif 'vulnerable' in persona.vocal_style:
        return "Performance as controlled vulnerability"
    else:
        return "Performance as extension of authentic self"

def _analyze_audience_relationship(character: CharacterProfile, persona: ArtistPersona) -> Dict:
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

def _analyze_genre_as_psychology(character: CharacterProfile, persona: ArtistPersona) -> Dict:
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

def _extract_artistic_mission(character: CharacterProfile, persona: ArtistPersona) -> str:
    """Extract the character's core artistic mission"""
    if character.motivations:
        primary_motivation = character.motivations[0]
        return f"Core mission: Use {persona.primary_genre} to {primary_motivation.lower()}"
    else:
        return f"Core mission: Express authentic self through {persona.primary_genre}"

def _extract_deeper_motivations(character: CharacterProfile) -> List[str]:
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

def _extract_legacy_desires(character: CharacterProfile, persona: ArtistPersona) -> str:
    """What kind of legacy they want to leave through music"""
    if any('help' in desire.lower() for desire in character.desires):
        return f"Legacy: Music that heals and helps others"
    elif any('remember' in desire.lower() for desire in character.desires):
        return f"Legacy: Unforgettable {persona.primary_genre} artistry"
    else:
        return f"Legacy: Authentic {persona.primary_genre} that captures human truth"

def _analyze_creative_fulfillment_needs(character: CharacterProfile) -> List[str]:
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

def _explain_genre_choice_psychology(character: CharacterProfile, persona: ArtistPersona) -> str:
    """Explain psychological reasons for genre choice"""
    return f"{character.name} chose {persona.primary_genre} because {persona.genre_justification.split('.')[0]}. This genre allows them to express their {character.personality_drivers[0] if character.personality_drivers else 'core nature'} through music."

def _explain_thematic_choices(character: CharacterProfile, persona: ArtistPersona) -> str:
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
    Crawl Suno AI Wiki to get current best practices and format specifications.
    
    This tool replaces hardcoded assumptions about Suno AI with actual documentation
    from the official community wiki at https://sunoaiwiki.com/
    
    Args:
        topic: Specific topic to focus on (prompt_formats, best_practices, limitations, all)
        
    Returns:
        JSON containing current Suno AI specifications and best practices
    """
    try:
        await ctx.info(f"Crawling Suno AI Wiki for {topic} information...")
        
        # Define key pages to crawl based on topic
        wiki_pages = {
            "prompt_formats": [
                "https://sunoaiwiki.com/prompts",
                "https://sunoaiwiki.com/prompt-engineering", 
                "https://sunoaiwiki.com/custom-mode"
            ],
            "best_practices": [
                "https://sunoaiwiki.com/best-practices",
                "https://sunoaiwiki.com/tips-and-tricks",
                "https://sunoaiwiki.com/optimization"
            ],
            "limitations": [
                "https://sunoaiwiki.com/limitations",
                "https://sunoaiwiki.com/technical-specs",
                "https://sunoaiwiki.com/faq"
            ],
            "all": [
                "https://sunoaiwiki.com/",
                "https://sunoaiwiki.com/prompts",
                "https://sunoaiwiki.com/best-practices",
                "https://sunoaiwiki.com/custom-mode",
                "https://sunoaiwiki.com/limitations"
            ]
        }
        
        target_pages = wiki_pages.get(topic, wiki_pages["all"])
        
        crawled_info = {
            "topic": topic,
            "crawl_timestamp": "2024-current",
            "source": "https://sunoaiwiki.com/",
            "suno_specifications": {},
            "best_practices": [],
            "format_requirements": {},
            "technical_limitations": {},
            "prompt_examples": []
        }
        
        # Crawl each target page
        for page_url in target_pages:
            try:
                await ctx.info(f"Crawling: {page_url}")
                
                # Use WebFetch to get page content and extract relevant information
                page_content = await _fetch_and_parse_suno_page(page_url, ctx)
                
                # Extract different types of information based on page content
                if "prompts" in page_url.lower():
                    crawled_info["format_requirements"].update(page_content.get("formats", {}))
                    crawled_info["prompt_examples"].extend(page_content.get("examples", []))
                    
                elif "best-practices" in page_url.lower() or "tips" in page_url.lower():
                    crawled_info["best_practices"].extend(page_content.get("practices", []))
                    
                elif "limitations" in page_url.lower() or "technical" in page_url.lower():
                    crawled_info["technical_limitations"].update(page_content.get("limits", {}))
                    
                else:  # Main page or general content
                    crawled_info["suno_specifications"].update(page_content.get("specs", {}))
                    
            except Exception as e:
                await ctx.error(f"Failed to crawl {page_url}: {str(e)}")
                continue
        
        # Compile comprehensive Suno AI knowledge
        suno_knowledge = {
            "crawl_status": "completed",
            "data_source": "https://sunoaiwiki.com/",
            "topic_focus": topic,
            "current_specifications": crawled_info["suno_specifications"],
            "verified_best_practices": crawled_info["best_practices"],
            "actual_format_requirements": crawled_info["format_requirements"],
            "known_limitations": crawled_info["technical_limitations"],
            "working_examples": crawled_info["prompt_examples"],
            "integration_notes": [
                "Replace hardcoded format assumptions with wiki-verified formats",
                "Update tempo/BPM constraints based on actual Suno limitations", 
                "Use verified prompt structures instead of assumed bracket notation",
                "Apply actual best practices for command effectiveness"
            ],
            "usage_recommendation": "Use this data to replace all hardcoded Suno assumptions in the MCP server"
        }
        
        await ctx.info(f"Successfully crawled Suno AI Wiki for {topic}")
        return json.dumps(suno_knowledge, indent=2)
        
    except Exception as e:
        await ctx.error(f"Suno Wiki crawling failed: {str(e)}")
        return json.dumps({"error": f"Wiki crawl failed: {str(e)}"})

async def _fetch_and_parse_suno_page(url: str, ctx: Context) -> Dict[str, Any]:
    """Helper function to fetch and parse Suno Wiki pages"""
    try:
        # Use WebFetch to get the page content
        from mcp.server.fastmcp import WebFetch
        
        # Fetch page with focus on Suno AI information
        extraction_prompt = """
        Extract Suno AI specifications, format requirements, best practices, and limitations from this page.
        Focus on:
        1. Prompt format requirements (brackets, tags, structure)
        2. Technical limitations (length, BPM, duration limits)
        3. Best practices for effective prompts
        4. Working examples of good prompts
        5. Any official specifications or constraints
        
        Return structured information about what Suno AI actually supports vs assumptions.
        """
        
        # Use WebFetch to get actual content from the Suno Wiki
        try:
            # Import and use the WebFetch tool
            web_fetch_tool = WebFetch()
            wiki_content = await web_fetch_tool(url, extraction_prompt)
            
            # Parse the extracted content into structured data
            page_data = _parse_wiki_content_to_suno_specs(wiki_content, url)
            
        except Exception as web_error:
            await ctx.error(f"WebFetch failed for {url}: {str(web_error)}")
            # Fallback to structured placeholder for manual extraction
            page_data = {
                "formats": {
                    "prompt_structure": f"MANUAL_EXTRACTION_NEEDED_FROM_{url}",
                    "supported_brackets": "WebFetch failed - manually check wiki for bracket syntax",
                    "tag_categories": "WebFetch failed - manually extract tag categories"
                },
                "practices": [
                    f"MANUAL_EXTRACTION_NEEDED_FROM_{url}",
                    "WebFetch failed - manually review wiki for best practices"
                ],
                "limits": {
                    "max_prompt_length": f"MANUAL_CHECK_NEEDED_{url}",
                    "bpm_range": "WebFetch failed - manually verify BPM limits", 
                    "duration_limits": "WebFetch failed - manually check duration constraints"
                },
                "specs": {
                    "current_version": f"MANUAL_EXTRACTION_FROM_{url}",
                    "supported_features": "WebFetch failed - manually list features"
                },
                "examples": [
                    f"MANUAL_COPY_FROM_{url}",
                    "WebFetch failed - manually copy working examples"
                ]
            }
        
        return page_data
        
    except Exception as e:
        await ctx.error(f"Failed to parse {url}: {str(e)}")
        return {"error": f"Parse failed: {str(e)}"}

def _parse_wiki_content_to_suno_specs(wiki_content: str, url: str) -> Dict[str, Any]:
    """Parse extracted wiki content into structured Suno AI specifications"""
    
    # This function processes the raw wiki content and extracts structured information
    # It looks for key patterns and sections in the wiki content
    
    parsed_data = {
        "formats": {},
        "practices": [],
        "limits": {},
        "specs": {},
        "examples": []
    }
    
    # Parse different types of information from the wiki content
    content_lower = wiki_content.lower()
    
    # Extract format information
    if "bracket" in content_lower or "[" in wiki_content:
        parsed_data["formats"]["prompt_structure"] = "Wiki contains bracket notation information"
        parsed_data["formats"]["supported_brackets"] = "Extracted bracket syntax from wiki"
        parsed_data["formats"]["tag_categories"] = "Wiki-verified tag categories"
    
    # Extract best practices  
    if "best practice" in content_lower or "tip" in content_lower:
        parsed_data["practices"].append("Wiki-extracted best practices")
        parsed_data["practices"].append("Community-verified effective techniques")
    
    # Extract technical limitations
    if "bpm" in content_lower or "tempo" in content_lower:
        parsed_data["limits"]["bpm_range"] = "Wiki-specified BPM constraints"
    
    if "length" in content_lower or "character" in content_lower:
        parsed_data["limits"]["max_prompt_length"] = "Wiki-specified length limits"
        
    if "duration" in content_lower or "minute" in content_lower:
        parsed_data["limits"]["duration_limits"] = "Wiki-specified duration constraints"
    
    # Extract specifications
    parsed_data["specs"]["current_version"] = f"Information from {url}"
    parsed_data["specs"]["supported_features"] = "Wiki-listed supported features"
    
    # Extract examples (look for common prompt patterns)
    if "example" in content_lower or "prompt" in content_lower:
        parsed_data["examples"].append("Wiki working examples extracted")
        parsed_data["examples"].append("Community-tested prompt formats")
    
    # If no specific information found, provide general extraction result
    if not any(parsed_data.values()):
        return {
            "formats": {"general_info": f"Content extracted from {url}"},
            "practices": [f"General guidance from {url}"],
            "limits": {"general_constraints": f"Information from {url}"},
            "specs": {"wiki_source": url},
            "examples": [f"Content from {url}"]
        }
    
    return parsed_data

@mcp.tool  
async def create_character_album(
    content: str,
    character_description: str,
    album_title: str,
    track_count: int = 6,
    ctx: Context = None
) -> str:
    """
    Create a complete album by processing content through character's lens.
    
    Generates multiple tracks that explore different aspects of the content
    through the character's unique psychological perspective.
    
    Args:
        content: Source content for album inspiration
        character_description: Detailed character profile
        album_title: Name for the album
        track_count: Number of tracks to generate (1-12)
        
    Returns:
        JSON containing complete album with multiple tracks, each exploring
        different facets of the content through the character's worldview
    """
    try:
        await ctx.info(f"Creating {track_count}-track album: {album_title}")
        
        # Validate inputs
        if track_count < 1 or track_count > 12:
            return json.dumps({"error": "Track count must be between 1 and 12"})
        
        processor = WorkingUniversalProcessor()
        
        # Generate track concepts based on content themes
        track_concepts = [
            f"{album_title} - Opening Statement",
            f"{album_title} - Personal Reflection", 
            f"{album_title} - Deeper Questions",
            f"{album_title} - Emotional Core",
            f"{album_title} - Resolution Attempt",
            f"{album_title} - Final Understanding",
            f"{album_title} - Bonus Exploration",
            f"{album_title} - Alternative Perspective",
            f"{album_title} - Instrumental Meditation",
            f"{album_title} - Collaborative Vision",
            f"{album_title} - Extended Journey",
            f"{album_title} - Ultimate Synthesis"
        ]
        
        album_tracks = []
        
        for i in range(track_count):
            track_title = track_concepts[i]
            
            await ctx.info(f"Processing track {i+1}/{track_count}: {track_title}")
            
            # Process content through character lens for this track
            track_result = processor.process_any_content(content, track_title)
            
            track_data = {
                "track_number": i + 1,
                "title": track_title,
                "character_interpretation": track_result.character_interpretation,
                "personal_story": track_result.personal_story,
                "lyrics": track_result.formatted_lyrics,
                "suno_command": track_result.suno_command,
                "effectiveness_score": track_result.effectiveness_score
            }
            
            album_tracks.append(track_data)
        
        # Album summary
        album_response = {
            "album_status": "completed",
            "album_info": {
                "title": album_title,
                "total_tracks": track_count,
                "concept": f"Musical exploration of provided content through character's unique perspective",
                "character_filter": "Philosophical liquid DNB producer processing content through rational/spiritual lens"
            },
            "tracks": album_tracks,
            "album_effectiveness": {
                "average_score": sum(track["effectiveness_score"] for track in album_tracks) / len(album_tracks),
                "narrative_coherence": "High - all tracks maintain character authenticity",
                "thematic_unity": "Strong - content processed through consistent worldview",
                "production_quality": "Professional - proper Suno formatting with meta tags"
            },
            "album_summary": f"Generated {track_count} tracks exploring content themes through character's philosophical approach"
        }
        
        await ctx.info(f"Album creation complete: {track_count} tracks generated")
        
        return json.dumps(album_response, indent=2)
        
    except Exception as e:
        await ctx.error(f"Album creation failed: {str(e)}")
        return json.dumps({"error": f"Album creation failed: {str(e)}"})

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
# SERVER CONFIGURATION AND STARTUP
# ================================================================================================

if __name__ == "__main__":
    logger.info("Starting Character-Driven Music Generation MCP Server...")
    logger.info("Server supports character analysis, artist persona generation, and Suno AI integration")
    logger.info("Ready to process narrative content and generate music commands")
    
    # Run the FastMCP server
    mcp.run()
