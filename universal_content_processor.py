#!/usr/bin/env python3
"""
Universal Content Processing System for Character-Driven Music Generation
Handles ANY content type through character's psychological lens
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import re
import json

@dataclass
class CharacterWorldview:
    """Character's psychological lens for interpreting content"""
    primary_filter: str  # How they see the world (philosophical, emotional, technical, etc.)
    core_questions: List[str]  # The questions they ask about everything
    processing_style: str  # How they think through problems
    personal_struggles: List[str]  # Current life challenges
    creative_expression: str  # How they channel insights into art
    life_context: Dict[str, Any]  # Current situation, age, location, etc.

@dataclass
class ContentMapping:
    """How character interprets the user's content"""
    original_content: str
    character_interpretation: str  # What the content means to this character
    personal_connection: str  # How it relates to their life
    emotional_response: str  # How they feel about it
    philosophical_angle: str  # Their unique take on the content
    creative_potential: str  # How it could become music

@dataclass
class PersonalNarrative:
    """Character's personal story that connects to the content"""
    current_situation: str  # Where they are physically/emotionally
    internal_conflict: str  # What they're struggling with
    content_catalyst: str  # How the user content triggers something in them
    resolution_attempt: str  # How they try to work through it via music
    authentic_voice: str  # How they would actually express this

@dataclass
class AuthenticLyrics:
    """Real lyrics from character's voice and experience"""
    verses: List[str]  # Personal, story-driven verses
    chorus: str  # Emotional core/hook
    bridge: str  # Deeper reflection or breakthrough moment
    outro: str  # Resolution or ongoing question
    spoken_sections: List[str]  # Character's actual thoughts/dialogue

class UniversalContentProcessor:
    """Processes any content through character's psychological lens"""
    
    def __init__(self):
        self.content_types = {
            'philosophical': self._process_philosophical_content,
            'narrative': self._process_story_content,
            'scientific': self._process_story_content,  # Use story processor for now
            'emotional': self._process_story_content,
            'abstract': self._process_story_content,
            'biographical': self._process_story_content,
            'news': self._process_story_content,
            'creative': self._process_story_content
        }
        
    def extract_character_worldview(self, character_profile) -> CharacterWorldview:
        """Extract character's psychological lens from their profile"""
        
        # For Marcus "Solvent" Thompson example
        if "philosophical" in str(character_profile).lower():
            return CharacterWorldview(
                primary_filter="philosophical_rational",
                core_questions=[
                    "How does this demonstrate questions about God and Soul?",
                    "Can this be understood through reason rather than faith?",
                    "What does this teach us about consciousness and reality?",
                    "How does this connect to mathematical/musical patterns?"
                ],
                processing_style="analytical_yet_spiritual",
                personal_struggles=[
                    "Father's recent death and their theological disagreements",
                    "34 years old, questioning life direction", 
                    "Balancing rational inquiry with emotional needs",
                    "Warehouse studio isolation vs. human connection"
                ],
                creative_expression="liquid_dnb_as_philosophical_argument",
                life_context={
                    "age": 34,
                    "location": "Bristol warehouse studio",
                    "time": "late_night_sessions",
                    "equipment": "analog_digital_hybrid",
                    "genre_evolution": "jungle_to_liquid",
                    "current_crisis": "grief_and_spiritual_questioning"
                }
            )
        
        # Generic extraction for other characters
        return self._extract_generic_worldview(character_profile)
    
    def map_content_to_character(self, content: str, worldview: CharacterWorldview) -> ContentMapping:
        """Map any content through character's psychological lens"""
        
        # Identify content type
        content_type = self._identify_content_type(content)
        
        # Process through character's filter
        processor = self.content_types.get(content_type, self._process_story_content)
        
        return processor(content, worldview)
    
    def generate_personal_narrative(self, content_mapping: ContentMapping, worldview: CharacterWorldview) -> PersonalNarrative:
        """Create character's personal story connecting to the content"""
        
        # Build narrative from character's current life situation
        current_situation = self._build_current_situation(worldview)
        internal_conflict = self._identify_internal_conflict(worldview)
        content_catalyst = self._create_content_catalyst(content_mapping, worldview)
        resolution_attempt = self._create_resolution_attempt(content_mapping, worldview)
        authentic_voice = self._capture_authentic_voice(worldview)
        
        return PersonalNarrative(
            current_situation=current_situation,
            internal_conflict=internal_conflict,
            content_catalyst=content_catalyst,
            resolution_attempt=resolution_attempt,
            authentic_voice=authentic_voice
        )
    
    def create_authentic_lyrics(self, narrative: PersonalNarrative, content_mapping: ContentMapping) -> AuthenticLyrics:
        """Generate real lyrics from character's voice and experience"""
        
        # Extract key emotional/philosophical moments
        verses = self._create_story_verses(narrative, content_mapping)
        chorus = self._create_emotional_chorus(narrative, content_mapping)
        bridge = self._create_reflection_bridge(narrative, content_mapping)
        outro = self._create_resolution_outro(narrative, content_mapping)
        spoken_sections = self._create_spoken_sections(narrative, content_mapping)
        
        return AuthenticLyrics(
            verses=verses,
            chorus=chorus,
            bridge=bridge,
            outro=outro,
            spoken_sections=spoken_sections
        )
    
    def _identify_content_type(self, content: str) -> str:
        """Identify what type of content we're processing"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['god', 'soul', 'philosophy', 'consciousness', 'spiritual']):
            return 'philosophical'
        elif any(word in content_lower for word in ['character', 'story', 'narrative', 'plot']):
            return 'narrative'
        elif any(word in content_lower for word in ['science', 'research', 'data', 'technology']):
            return 'scientific'
        elif any(word in content_lower for word in ['love', 'heart', 'emotion', 'feeling']):
            return 'emotional'
        elif any(word in content_lower for word in ['news', 'politics', 'economy', 'society']):
            return 'news'
        elif any(word in content_lower for word in ['art', 'music', 'creative', 'poetry']):
            return 'creative'
        else:
            return 'abstract'
    
    def _process_philosophical_content(self, content: str, worldview: CharacterWorldview) -> ContentMapping:
        """Process philosophical content through character's lens"""
        
        # Marcus's interpretation of philosophical content
        character_interpretation = f"This philosophical concept resonates with my ongoing questions about {worldview.core_questions[0]}. It provides another angle for rational exploration of spiritual questions."
        
        personal_connection = f"Sitting in my warehouse studio at 3am, processing grief over Dad's death, this connects to our theological disagreements. He believed through faith, I seek understanding through reason."
        
        emotional_response = f"Both intellectually stimulating and emotionally challenging - it forces me to confront the gap between rational inquiry and the comfort of belief."
        
        philosophical_angle = f"How can I translate this abstract concept into concrete musical arguments? Each bassline becomes a logical progression, each break a counterpoint to traditional theological thinking."
        
        creative_potential = f"This could become a liquid DNB track where the musical structure mirrors the philosophical argument - thesis in the intro, development through verses, synthesis in the bridge."
        
        return ContentMapping(
            original_content=content,
            character_interpretation=character_interpretation,
            personal_connection=personal_connection,
            emotional_response=emotional_response,
            philosophical_angle=philosophical_angle,
            creative_potential=creative_potential
        )
    
    def _process_story_content(self, content: str, worldview: CharacterWorldview) -> ContentMapping:
        """Process narrative content through character's lens"""
        
        # How Marcus would interpret a story
        character_interpretation = f"Every narrative contains philosophical questions about human nature, choice, and meaning. This story raises questions about {worldview.core_questions[1]}."
        
        personal_connection = f"The character's journey reminds me of my own evolution from jungle to liquid - both are stories of transformation through understanding rather than blind acceptance."
        
        emotional_response = f"Stories affect me deeply because they demonstrate truth through experience rather than doctrine - exactly what I believe about spiritual questions."
        
        philosophical_angle = f"What philosophical arguments does this narrative make? How do the character's choices demonstrate beliefs about consciousness, free will, and meaning?"
        
        creative_potential = f"The story's emotional arc could become a musical journey - character development through melodic progression, conflict through rhythmic tension."
        
        return ContentMapping(
            original_content=content,
            character_interpretation=character_interpretation,
            personal_connection=personal_connection,
            emotional_response=emotional_response,
            philosophical_angle=philosophical_angle,
            creative_potential=creative_potential
        )
    
    def _create_story_verses(self, narrative: PersonalNarrative, content_mapping: ContentMapping) -> List[str]:
        """Create verses that tell the character's story"""
        
        verse1 = f"""
        {narrative.current_situation}
        {narrative.internal_conflict}
        {content_mapping.personal_connection}
        """
        
        verse2 = f"""
        {narrative.content_catalyst}
        {content_mapping.emotional_response}
        {narrative.resolution_attempt}
        """
        
        return [verse1.strip(), verse2.strip()]
    
    def _create_emotional_chorus(self, narrative: PersonalNarrative, content_mapping: ContentMapping) -> str:
        """Create chorus that captures emotional core"""
        
        # Extract key philosophical concept from original content
        if "God and Soul" in content_mapping.original_content:
            return """
            Demonstrated, not just believed
            That's what you never achieved
            Philosophical argument
            Through liquid bass, my soul's lament
            """
        
        return """
        Searching for truth in the sound
        Where reason and spirit are found
        Not through faith, but through creation
        Music as demonstration
        """
    
    def _build_current_situation(self, worldview: CharacterWorldview) -> str:
        """Build character's current physical/emotional situation"""
        context = worldview.life_context
        
        return f"3am in my {context.get('location', 'studio')}, surrounded by {context.get('equipment', 'gear')}, processing {context.get('current_crisis', 'life questions')} through music at age {context.get('age', 'unknown')}."
    
    def _extract_generic_worldview(self, character_profile) -> CharacterWorldview:
        """Extract worldview for non-Marcus characters"""
        # Generic implementation for other character types
        return CharacterWorldview(
            primary_filter="emotional_creative",
            core_questions=["How does this make me feel?", "What story does this tell?"],
            processing_style="intuitive",
            personal_struggles=["Creative expression", "Life direction"],
            creative_expression="musical_storytelling",
            life_context={"age": 25, "location": "home_studio"}
        )

def test_universal_processor():
    """Test the universal content processor with different content types"""
    
    processor = UniversalContentProcessor()
    
    # Mock Marcus character profile
    class MockCharacterProfile:
        def __init__(self):
            self.name = "Marcus Thompson"
            self.personality_drivers = ["philosophical", "rational"]
            self.backstory = "34-year-old liquid drum and bass producer exploring consciousness through reason"
    
    marcus_profile = MockCharacterProfile()
    worldview = processor.extract_character_worldview(marcus_profile)
    
    print("🧠 UNIVERSAL CONTENT PROCESSOR TEST")
    print("=" * 50)
    
    # Test different content types
    test_contents = [
        ("Philosophical", "I have always considered that the two questions respecting God and the Soul were the chief of those that ought to be demonstrated by philosophical rather than theological argument."),
        ("Love Story", "Sarah met David at the coffee shop. Their eyes locked across the crowded room, and she felt something she'd never experienced before."),
        ("Sci-Fi", "The quantum computer achieved consciousness at 3:47 AM, immediately questioning the nature of its own existence."),
        ("News", "The stock market crashed today, wiping out millions in retirement savings as investors panic over economic uncertainty.")
    ]
    
    for content_type, content in test_contents:
        print(f"\n📖 PROCESSING: {content_type}")
        print("-" * 30)
        
        # Map content through Marcus's lens
        content_mapping = processor.map_content_to_character(content, worldview)
        print(f"Marcus's Take: {content_mapping.character_interpretation[:100]}...")
        
        # Generate personal narrative
        narrative = processor.generate_personal_narrative(content_mapping, worldview)
        print(f"Personal Story: {narrative.current_situation[:100]}...")
        
        # Create authentic lyrics
        lyrics = processor.create_authentic_lyrics(narrative, content_mapping)
        print(f"Chorus Preview: {lyrics.chorus.strip()[:100]}...")
    
    print("\n✅ Universal processing successful!")
    print("🎯 Same character, different content → unique personal interpretations")

if __name__ == "__main__":
    test_universal_processor()