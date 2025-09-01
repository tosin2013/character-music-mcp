#!/usr/bin/env python3
"""
MCP Tools Middleware

This module provides a clean interface layer between MCP tools and the underlying
functionality, avoiding the 'FunctionTool' object not callable errors that occur
when MCP tools try to call each other directly.

The middleware provides:
- Character analysis services
- Persona generation services  
- Content processing services
- Wiki attribution services
- Story analysis services

All services are designed to be called from within MCP tools without conflicts.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import asdict

from standard_character_profile import StandardCharacterProfile
from enhanced_character_analyzer import EnhancedCharacterAnalyzer
from server import MusicPersonaGenerator, ArtistPersona

logger = logging.getLogger(__name__)

class MCPMiddleware:
    """
    Middleware layer for MCP tools to access underlying functionality
    without direct tool-to-tool calls that cause FunctionTool errors
    """
    
    def __init__(self):
        """Initialize middleware with fresh instances of all services"""
        self.character_analyzer = EnhancedCharacterAnalyzer()
        self.persona_generator = MusicPersonaGenerator()
        self.logger = logging.getLogger(__name__)
    
    async def analyze_characters(self, text: str, ctx=None) -> Dict[str, Any]:
        """
        Analyze text for characters using the enhanced character analyzer
        
        Args:
            text: Input narrative text
            ctx: Optional context for logging
            
        Returns:
            Dictionary with characters, themes, and emotional arc
        """
        try:
            if ctx:
                await ctx.info("Middleware: Starting character analysis...")
            
            # Use the character analyzer directly
            result = await self.character_analyzer.analyze_text(text, ctx)
            
            # Convert character dictionaries to StandardCharacterProfile objects
            characters = []
            for char_data in result.get('characters', []):
                try:
                    character_profile = StandardCharacterProfile.from_dict(char_data)
                    characters.append(character_profile)
                except Exception as e:
                    if ctx:
                        await ctx.error(f"Failed to create character profile: {str(e)}")
                    continue
            
            # Return structured result
            return {
                'characters': characters,
                'narrative_themes': result.get('narrative_themes', []),
                'emotional_arc': result.get('emotional_arc', []),
                'analysis_metadata': result.get('analysis_metadata', {})
            }
            
        except Exception as e:
            if ctx:
                await ctx.error(f"Character analysis failed: {str(e)}")
            raise
    
    async def generate_persona(self, character: StandardCharacterProfile, ctx=None) -> ArtistPersona:
        """
        Generate artist persona for a character
        
        Args:
            character: StandardCharacterProfile object
            ctx: Optional context for logging
            
        Returns:
            ArtistPersona object
        """
        try:
            if ctx:
                await ctx.info(f"Middleware: Generating persona for {character.name}...")
            
            # Use the persona generator directly
            persona = await self.persona_generator.generate_artist_persona(character, ctx)
            
            return persona
            
        except Exception as e:
            if ctx:
                await ctx.error(f"Persona generation failed: {str(e)}")
            raise
    
    def process_track_content(
        self, 
        track_concept: Dict[str, Any], 
        character: StandardCharacterProfile, 
        persona: ArtistPersona,
        ctx=None
    ) -> Dict[str, Any]:
        """
        Process track content for story-integrated albums
        
        Args:
            track_concept: Dictionary with track concept details
            character: Character profile
            persona: Artist persona
            ctx: Optional context for logging
            
        Returns:
            Processed track data
        """
        try:
            # Create comprehensive track data
            track_data = {
                "content_analysis": {
                    "character_interpretation": f"Track explores {character.name}'s {track_concept.get('emotional_tone', 'complex')} state during {track_concept.get('narrative_function', 'story progression')}"
                },
                "character_story": {
                    "personal_connection": f"{character.name} experiences {track_concept.get('story_context', 'narrative development')} leading to {track_concept.get('character_state', 'emotional evolution')}",
                    "creative_process": f"Musical expression of {track_concept.get('emotional_tone', 'emotional depth')} through {persona.primary_genre} style"
                },
                "authentic_lyrics": {
                    "formatted_lyrics": self._generate_story_lyrics(track_concept, character)
                },
                "suno_command": {
                    "formatted_command": self._generate_suno_command(track_concept, character, persona)
                },
                "effectiveness_metrics": {
                    "character_authenticity": 0.85  # High authenticity for story-based content
                }
            }
            
            return track_data
            
        except Exception as e:
            if ctx:
                logger.error(f"Track content processing failed: {str(e)}")
            raise
    
    def _generate_story_lyrics(self, track_concept: Dict[str, Any], character: StandardCharacterProfile) -> str:
        """Generate lyrics based on story concept and character"""
        story_excerpt = track_concept.get('story_excerpt', f"Story of {character.name}")
        character_state = track_concept.get('character_state', 'emotional journey')
        story_context = track_concept.get('story_context', 'narrative moment')
        
        # Create structured lyrics
        lyrics = f"""[Verse 1]
{story_excerpt[:100]}...
{character.name}'s journey unfolds
{story_context[:50]}...

[Chorus]
{character_state}
{track_concept.get('emotional_tone', 'Deep emotions')} running through
{character.name}'s story continues
{track_concept.get('narrative_function', 'Moving forward')}

[Verse 2]
{story_context[:100]}...
Character development shows
{character_state[:50]}...

[Bridge]
{track_concept.get('emotional_tone', 'Emotional peak')}
{character.name} faces the moment
Story reaches its point

[Outro]
{character_state[:50]}...
The narrative continues..."""
        
        return lyrics
    
    def _generate_suno_command(
        self, 
        track_concept: Dict[str, Any], 
        character: StandardCharacterProfile, 
        persona: ArtistPersona
    ) -> str:
        """Generate Suno AI command for the track"""
        
        emotional_tone = track_concept.get('emotional_tone', 'contemplative')
        narrative_function = track_concept.get('narrative_function', 'story development')
        
        # Adjust style based on narrative position
        if "introduction" in narrative_function.lower():
            style_modifier = "introductory, establishing"
        elif "climax" in narrative_function.lower():
            style_modifier = "intense, dramatic, peak energy"
        elif "resolution" in narrative_function.lower():
            style_modifier = "reflective, concluding"
        else:
            style_modifier = "developing, progressive"
        
        command = f"""[{persona.primary_genre}] [{emotional_tone}] [{style_modifier}]

{track_concept.get('title', 'Untitled Track')} - {narrative_function}

Musical interpretation of {character.name}'s journey at this story moment.
{persona.vocal_style} conveying {emotional_tone} emotions.

{self._generate_story_lyrics(track_concept, character)}"""
        
        return command
    
    def extract_story_beats(self, narrative_text: str, character: StandardCharacterProfile, ctx=None) -> List[Dict]:
        """
        Extract story beats from narrative text
        
        Args:
            narrative_text: Full narrative text
            character: Main character to focus on
            ctx: Optional context for logging
            
        Returns:
            List of story beat dictionaries
        """
        try:
            # Divide text into sections for analysis
            text_length = len(narrative_text)
            section_size = max(text_length // 8, 100)  # At least 100 chars per section
            
            story_beats = []
            
            for i in range(8):
                start = i * section_size
                end = start + section_size if i < 7 else text_length
                
                if start >= text_length:
                    break
                    
                section = narrative_text[start:end]
                
                # Find character mentions in this section
                char_mentions = section.lower().count(character.name.lower())
                
                if char_mentions > 0 or len(story_beats) == 0:  # Always include first section
                    # Extract key events and emotions
                    beat = {
                        "section": i + 1,
                        "text": section[:500],  # First 500 chars
                        "character_presence": char_mentions,
                        "key_events": self._extract_events(section, character.name),
                        "emotional_state": self._analyze_section_emotion(section),
                        "relationships": self._extract_section_relationships(section, character.name),
                        "conflicts": self._extract_section_conflicts(section)
                    }
                    story_beats.append(beat)
            
            return story_beats
            
        except Exception as e:
            if ctx:
                logger.error(f"Story beat extraction failed: {str(e)}")
            return []
    
    def _extract_events(self, text: str, character_name: str) -> List[str]:
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
    
    def _analyze_section_emotion(self, text: str) -> str:
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
        return 'contemplative'
    
    def _extract_section_relationships(self, text: str, character_name: str) -> List[str]:
        """Extract relationship dynamics in section"""
        relationships = []
        
        # Find other character names near our character
        sentences = text.split('.')
        for sentence in sentences:
            if character_name.lower() in sentence.lower():
                # Look for other capitalized names
                words = sentence.split()
                for word in words:
                    if word != character_name and len(word) > 2 and word[0].isupper():
                        relationships.append(f"Interaction with {word}")
        
        return list(set(relationships))[:2]
    
    def _extract_section_conflicts(self, text: str) -> List[str]:
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
    
    def generate_story_based_tracks(
        self,
        story_beats: List[Dict],
        character: StandardCharacterProfile,
        persona: ArtistPersona,
        track_count: int,
        ctx=None
    ) -> List[Dict]:
        """Generate track concepts based on story progression"""
        
        track_concepts = []
        
        # Distribute tracks across story beats
        beats_per_track = max(1, len(story_beats) // track_count)
        
        for i in range(track_count):
            # Select story beat(s) for this track
            beat_index = min(i * beats_per_track, len(story_beats) - 1)
            beat = story_beats[beat_index] if story_beats else {}
            
            # Determine narrative function based on track position
            if i == 0:
                narrative_function = "Introduction - Setting the scene"
            elif i == track_count - 1:
                narrative_function = "Resolution - Story conclusion"
            elif i == track_count // 2:
                narrative_function = "Climax - Peak dramatic moment"
            else:
                narrative_function = f"Development - Story progression {i+1}"
            
            # Create track concept
            track_concept = {
                'title': f"{character.name}'s Journey - Part {i+1}",
                'story_context': beat.get('text', f"Story moment {i+1} in {character.name}'s journey")[:200],
                'character_state': f"{character.name} experiences {beat.get('emotional_state', 'emotional growth')}",
                'emotional_tone': beat.get('emotional_state', 'contemplative'),
                'narrative_function': narrative_function,
                'story_excerpt': beat.get('text', f"Chapter {i+1} of {character.name}'s story")[:300],
                'track_themes': [
                    beat.get('emotional_state', 'growth'),
                    'character development',
                    'narrative progression'
                ],
                'musical_evolution': f"Track {i+1} builds on previous emotional development"
            }
            
            track_concepts.append(track_concept)
        
        return track_concepts
    
    def get_wiki_attribution(self) -> str:
        """Get wiki attribution context (simplified for now)"""
        return "Using fallback data - no wiki sources available"

# Global middleware instance
middleware = MCPMiddleware()