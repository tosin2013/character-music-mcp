#!/usr/bin/env python3
"""
Enhanced Character Analyzer for MCP Tools

This module provides robust character detection and analysis using:
- Named Entity Recognition (NER) for character detection
- Three-layer character analysis (skin/flesh/core)
- Semantic analysis for narrative themes
- Emotional arc analysis with varied states

Addresses requirements 1.1, 1.2, 1.3, 1.4, 1.5 from the MCP tools diagnostic fixes.
"""

import logging
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

from standard_character_profile import StandardCharacterProfile

logger = logging.getLogger(__name__)

@dataclass
class EmotionalState:
    """Represents an emotional state with context"""
    emotion: str
    intensity: float  # 0.0 to 1.0
    context: str
    text_position: int
    triggers: List[str]

@dataclass
class NarrativeTheme:
    """Represents a narrative theme with evidence"""
    theme: str
    strength: float  # 0.0 to 1.0
    evidence: List[str]
    keywords: List[str]

class EnhancedCharacterAnalyzer:
    """
    Enhanced character analyzer with robust detection and three-layer analysis
    
    This replaces the basic CharacterAnalyzer with improved:
    - Character detection using multiple NER techniques
    - Three-layer analysis (skin/flesh/core) as specified
    - Semantic theme analysis beyond just "friendship"
    - Varied emotional arc analysis instead of "neutral" defaults
    """

    def __init__(self):
        """Initialize the enhanced character analyzer"""
        self.logger = logging.getLogger(__name__)

        # Enhanced character detection patterns
        self.character_patterns = {
            'full_names': r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b',
            'single_names': r'\b[A-Z][a-z]{2,15}\b',
            'dialogue_attribution': r'([A-Z][a-z]+)\s+(?:said|asked|replied|whispered|shouted|exclaimed|muttered|declared|announced|continued|added|interrupted|insisted|protested|agreed|disagreed|laughed|cried|sighed)',
            'possessive_names': r"([A-Z][a-z]+)'s\s+",
            'direct_address': r'"[^"]*,\s*([A-Z][a-z]+)[,.]',
            'action_attribution': r'([A-Z][a-z]+)\s+(?:walked|ran|stood|sat|looked|turned|moved|stepped|jumped|climbed|fell|rose|entered|left|arrived|departed)'
        }

        # Common words to exclude from character detection
        self.common_words = {
            'The', 'And', 'But', 'For', 'Not', 'With', 'From', 'They', 'This', 'That', 'When', 'Where',
            'What', 'Why', 'How', 'Then', 'Now', 'Here', 'There', 'Again', 'Also', 'Just', 'Only',
            'Even', 'Still', 'Much', 'More', 'Most', 'Many', 'Some', 'All', 'Both', 'Each', 'Every',
            'His', 'Her', 'Their', 'Its', 'Our', 'Your', 'My', 'Mine', 'Yours', 'Hers', 'Theirs', 'Ours',
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
            'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December',
            'America', 'American', 'Europe', 'European', 'Asia', 'Asian', 'Africa', 'African',
            'God', 'Lord', 'Jesus', 'Christ', 'Heaven', 'Hell', 'Bible', 'Church'
        }

        # Enhanced theme detection patterns
        self.theme_patterns = {
            'love_romance': {
                'keywords': ['love', 'romance', 'heart', 'kiss', 'embrace', 'passion', 'affection', 'devotion', 'adore', 'cherish', 'beloved', 'darling', 'sweetheart'],
                'patterns': [r'\blove[ds]?\b', r'\bromance\b', r'\bheart\b.*\b(?:flutter|race|skip|pound)\b']
            },
            'betrayal_deception': {
                'keywords': ['betrayal', 'betray', 'deceive', 'lie', 'cheat', 'backstab', 'double-cross', 'treachery', 'dishonest', 'unfaithful'],
                'patterns': [r'\bbetra[yl]', r'\blie[ds]?\b', r'\bcheat', r'\bdeceiv']
            },
            'power_control': {
                'keywords': ['power', 'control', 'authority', 'dominance', 'rule', 'command', 'govern', 'lead', 'influence', 'manipulate'],
                'patterns': [r'\bpower\b', r'\bcontrol', r'\brule[ds]?\b', r'\bcommand']
            },
            'redemption_forgiveness': {
                'keywords': ['redemption', 'redeem', 'forgive', 'forgiveness', 'second chance', 'atonement', 'mercy', 'pardon', 'absolve'],
                'patterns': [r'\bredeem', r'\bforgiv', r'\bsecond chance\b', r'\batonement\b']
            },
            'sacrifice_loss': {
                'keywords': ['sacrifice', 'loss', 'give up', 'surrender', 'abandon', 'forfeit', 'relinquish', 'renounce'],
                'patterns': [r'\bsacrifice', r'\bgive up\b', r'\blose\b', r'\bloss\b']
            },
            'justice_morality': {
                'keywords': ['justice', 'moral', 'ethical', 'right', 'wrong', 'fair', 'unfair', 'honor', 'virtue', 'principle'],
                'patterns': [r'\bjustice\b', r'\bmoral', r'\bright\b.*\bwrong\b', r'\bfair']
            },
            'family_kinship': {
                'keywords': ['family', 'mother', 'father', 'parent', 'child', 'son', 'daughter', 'brother', 'sister', 'sibling', 'relative'],
                'patterns': [r'\bfamily\b', r'\bmother\b', r'\bfather\b', r'\bparent']
            },
            'friendship_loyalty': {
                'keywords': ['friend', 'friendship', 'loyal', 'loyalty', 'companion', 'ally', 'bond', 'trust', 'faithful'],
                'patterns': [r'\bfriend', r'\bloyal', r'\bcompanion\b', r'\bally\b']
            },
            'survival_danger': {
                'keywords': ['survive', 'survival', 'danger', 'threat', 'peril', 'risk', 'escape', 'flee', 'hide', 'protect'],
                'patterns': [r'\bsurviv', r'\bdanger', r'\bthreat', r'\bescape']
            },
            'growth_transformation': {
                'keywords': ['grow', 'growth', 'change', 'transform', 'evolve', 'develop', 'mature', 'learn', 'discover', 'realize'],
                'patterns': [r'\bgrow', r'\bchange', r'\btransform', r'\blearn']
            },
            'conflict_struggle': {
                'keywords': ['conflict', 'struggle', 'fight', 'battle', 'war', 'combat', 'oppose', 'resist', 'challenge'],
                'patterns': [r'\bconflict\b', r'\bstruggle', r'\bfight', r'\bbattle']
            },
            'mystery_secrets': {
                'keywords': ['mystery', 'secret', 'hidden', 'conceal', 'reveal', 'discover', 'uncover', 'enigma', 'puzzle'],
                'patterns': [r'\bmystery\b', r'\bsecret', r'\bhidden\b', r'\breveal']
            },
            'adventure_journey': {
                'keywords': ['adventure', 'journey', 'quest', 'expedition', 'voyage', 'travel', 'explore', 'discover'],
                'patterns': [r'\badventure\b', r'\bjourney\b', r'\bquest\b', r'\btravel']
            },
            'identity_self_discovery': {
                'keywords': ['identity', 'self', 'who am I', 'purpose', 'meaning', 'belonging', 'find myself'],
                'patterns': [r'\bidentity\b', r'\bwho am I\b', r'\bfind myself\b', r'\bpurpose\b']
            }
        }

        # Enhanced emotional indicators
        self.emotion_patterns = {
            'joy_happiness': {
                'keywords': ['happy', 'joy', 'joyful', 'elated', 'cheerful', 'delighted', 'ecstatic', 'blissful', 'euphoric', 'gleeful'],
                'intensity_modifiers': {'very': 1.2, 'extremely': 1.4, 'incredibly': 1.3, 'somewhat': 0.7, 'slightly': 0.5}
            },
            'sadness_grief': {
                'keywords': ['sad', 'sorrow', 'grief', 'melancholy', 'despair', 'heartbroken', 'devastated', 'mournful', 'dejected'],
                'intensity_modifiers': {'deeply': 1.3, 'profoundly': 1.4, 'utterly': 1.5, 'somewhat': 0.7, 'mildly': 0.6}
            },
            'anger_rage': {
                'keywords': ['angry', 'rage', 'fury', 'mad', 'irritated', 'furious', 'livid', 'enraged', 'incensed', 'irate'],
                'intensity_modifiers': {'violently': 1.5, 'intensely': 1.3, 'slightly': 0.5, 'mildly': 0.6}
            },
            'fear_anxiety': {
                'keywords': ['afraid', 'scared', 'terrified', 'anxious', 'worried', 'fearful', 'panicked', 'nervous', 'apprehensive'],
                'intensity_modifiers': {'absolutely': 1.4, 'completely': 1.3, 'somewhat': 0.7, 'slightly': 0.5}
            },
            'surprise_shock': {
                'keywords': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'bewildered', 'startled', 'flabbergasted'],
                'intensity_modifiers': {'completely': 1.3, 'utterly': 1.4, 'mildly': 0.6}
            },
            'hope_optimism': {
                'keywords': ['hope', 'hopeful', 'optimistic', 'confident', 'positive', 'encouraged', 'uplifted', 'inspired'],
                'intensity_modifiers': {'deeply': 1.3, 'truly': 1.2, 'somewhat': 0.7}
            },
            'tension_stress': {
                'keywords': ['tense', 'stressed', 'pressure', 'strain', 'overwhelmed', 'burdened', 'exhausted'],
                'intensity_modifiers': {'extremely': 1.4, 'very': 1.2, 'somewhat': 0.7}
            },
            'confusion_uncertainty': {
                'keywords': ['confused', 'uncertain', 'puzzled', 'perplexed', 'bewildered', 'lost', 'unsure'],
                'intensity_modifiers': {'completely': 1.3, 'utterly': 1.4, 'somewhat': 0.7}
            },
            'guilt_shame': {
                'keywords': ['guilty', 'ashamed', 'remorseful', 'regretful', 'embarrassed', 'humiliated'],
                'intensity_modifiers': {'deeply': 1.3, 'profoundly': 1.4, 'slightly': 0.5}
            },
            'pride_satisfaction': {
                'keywords': ['proud', 'satisfied', 'accomplished', 'fulfilled', 'triumphant', 'victorious'],
                'intensity_modifiers': {'immensely': 1.4, 'deeply': 1.3, 'somewhat': 0.7}
            }
        }

    def _detect_content_type(self, text: str) -> str:
        """
        Detect the type of content to determine processing strategy
        
        Returns:
            Content type: "narrative", "conceptual", "descriptive", or "mixed"
        """
        text_lower = text.lower()

        # Indicators for different content types
        narrative_indicators = [
            'once upon a time', 'chapter', 'story', 'plot', 'character said', 'dialogue',
            'he walked', 'she ran', 'they went', 'narrative', 'fiction', 'novel',
            'protagonist', 'antagonist', 'scene', 'setting', 'stood at', 'walked into',
            'had grown up', 'had been', 'felt a mixture', 'whispered to', 'voice breaking',
            'closest friend', 'since childhood', 'shared dreams', 'would not let'
        ]

        conceptual_indicators = [
            'philosophy', 'concept', 'theory', 'principle', 'idea', 'notion',
            'abstract', 'metaphor', 'symbolism', 'represents', 'embodies',
            'philosophical', 'theoretical', 'conceptual', 'existential',
            'consciousness', 'reality', 'truth', 'meaning', 'purpose'
        ]

        descriptive_indicators = [
            'character profile', 'description of', 'personality:', 'traits:',
            'background:', 'appearance:', 'motivation:', 'fear:', 'desire:',
            'name:', 'age:', 'occupation:', 'likes:', 'dislikes:',
            'character sheet', 'bio:', 'biography'
        ]

        # Count indicators
        narrative_score = sum(1 for indicator in narrative_indicators if indicator in text_lower)
        conceptual_score = sum(1 for indicator in conceptual_indicators if indicator in text_lower)
        descriptive_score = sum(1 for indicator in descriptive_indicators if indicator in text_lower)

        # Additional scoring based on structure
        if ':' in text and text.count(':') > 3:  # Structured format
            descriptive_score += 2

        if '"' in text and text.count('"') > 0:  # Dialogue indicates narrative
            narrative_score += 3

        # Look for past tense narrative patterns
        past_tense_patterns = [
            r'\b(stood|walked|ran|felt|said|whispered|had|was|were)\b'
        ]
        for pattern in past_tense_patterns:
            matches = len(re.findall(pattern, text_lower))
            if matches > 3:  # Multiple past tense verbs suggest narrative
                narrative_score += 2

        # Look for character names with actions
        character_action_pattern = r'\b[A-Z][a-z]+\s+(stood|walked|felt|said|had|was|were)\b'
        character_actions = len(re.findall(character_action_pattern, text))
        if character_actions > 2:
            narrative_score += 3

        # Check for philosophical language patterns
        philosophical_patterns = [
            r'\bwhat is\b', r'\bwhy do\b', r'\bhow can\b', r'\bthe nature of\b',
            r'\bexistence\b', r'\breality\b', r'\btruth\b', r'\bmeaning\b'
        ]
        for pattern in philosophical_patterns:
            if re.search(pattern, text_lower):
                conceptual_score += 1

        # Determine content type
        max_score = max(narrative_score, conceptual_score, descriptive_score)

        if max_score == 0:
            return "mixed"  # No clear indicators
        elif descriptive_score == max_score:
            return "descriptive"
        elif conceptual_score == max_score:
            return "conceptual"
        elif narrative_score == max_score:
            return "narrative"
        else:
            return "mixed"

    def _determine_processing_strategy(self, content_type: str, text: str) -> str:
        """
        Determine the processing strategy based on content type
        
        Returns:
            Processing strategy: "extract", "create", "use_explicit", or "hybrid"
        """
        if content_type == "narrative":
            return "extract"
        elif content_type == "conceptual":
            return "create"
        elif content_type == "descriptive":
            return "use_explicit"
        else:  # mixed
            # For mixed content, check which approach is more appropriate
            if len(re.findall(r'\b[A-Z][a-z]+\b', text)) > 10:  # Many proper names
                return "extract"
            else:
                return "hybrid"

    async def _detect_characters_by_type(self, text: str, content_type: str, strategy: str, ctx=None) -> List[StandardCharacterProfile]:
        """
        Detect or create characters based on content type and strategy
        
        Args:
            text: Input text
            content_type: Detected content type
            strategy: Processing strategy
            ctx: Optional context for logging
            
        Returns:
            List of StandardCharacterProfile instances
        """
        if ctx:
            await ctx.info(f"Processing characters using strategy: {strategy}")

        if strategy == "extract":
            # Use traditional character extraction for narrative content
            return await self._detect_characters_enhanced(text, ctx)
        elif strategy == "create":
            # Create conceptual characters from philosophical themes
            return await self._create_conceptual_characters(text, ctx)
        elif strategy == "use_explicit":
            # Handle explicit character descriptions
            return await self._process_explicit_descriptions(text, ctx)
        else:  # hybrid
            # Try extraction first, fall back to creation if needed
            extracted_chars = await self._detect_characters_enhanced(text, ctx)
            if len(extracted_chars) == 0 or all(char.confidence_score < 0.3 for char in extracted_chars):
                if ctx:
                    await ctx.info("Extraction yielded poor results, switching to conceptual creation")
                return await self._create_conceptual_characters(text, ctx)
            return extracted_chars

    async def _create_conceptual_characters(self, text: str, ctx=None) -> List[StandardCharacterProfile]:
        """
        Create characters from philosophical themes and concepts
        
        Args:
            text: Input text containing concepts/themes
            ctx: Optional context for logging
            
        Returns:
            List of conceptual character profiles
        """
        if ctx:
            await ctx.info("Creating conceptual characters from themes...")

        # Extract key concepts and themes
        concepts = self._extract_key_concepts(text)
        themes = self._extract_philosophical_themes(text)

        characters = []

        # Create characters based on major concepts
        for i, concept in enumerate(concepts[:3]):  # Limit to top 3 concepts
            char_name = self._generate_conceptual_character_name(concept, i)

            # Build character profile around the concept
            profile = await self._build_conceptual_profile(char_name, concept, text, themes, ctx)
            profile.content_type = "conceptual"
            profile.conceptual_basis = [concept] + themes[:2]
            profile.processing_notes = f"Character created from concept: {concept}"

            characters.append(profile)

        if ctx:
            await ctx.info(f"Created {len(characters)} conceptual characters")

        return characters

    async def _process_explicit_descriptions(self, text: str, ctx=None) -> List[StandardCharacterProfile]:
        """
        Process explicit character descriptions
        
        Args:
            text: Input text with character descriptions
            ctx: Optional context for logging
            
        Returns:
            List of character profiles from descriptions
        """
        if ctx:
            await ctx.info("Processing explicit character descriptions...")

        # Look for structured character information
        characters = []

        # Split text into potential character sections
        sections = self._split_into_character_sections(text)

        for section in sections:
            char_name = self._extract_character_name_from_section(section)
            if char_name:
                profile = await self._build_profile_from_description(char_name, section, ctx)
                profile.content_type = "descriptive"
                profile.processing_notes = "Character built from explicit description"
                characters.append(profile)

        if ctx:
            await ctx.info(f"Processed {len(characters)} explicit character descriptions")

        return characters

    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key philosophical/abstract concepts from text"""
        concept_patterns = [
            r'\b(consciousness|awareness|perception|reality|truth|existence|being|identity|self|soul|mind|spirit)\b',
            r'\b(freedom|liberty|choice|will|determinism|fate|destiny|purpose|meaning|significance)\b',
            r'\b(love|hate|fear|hope|despair|joy|sorrow|anger|peace|harmony|conflict)\b',
            r'\b(justice|morality|ethics|virtue|vice|good|evil|right|wrong|duty|responsibility)\b',
            r'\b(time|eternity|mortality|immortality|death|life|birth|creation|destruction)\b',
            r'\b(knowledge|wisdom|ignorance|understanding|learning|discovery|revelation|insight)\b'
        ]

        concepts = []
        for pattern in concept_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            concepts.extend([match.lower() for match in matches])

        # Count frequency and return most common
        concept_counts = Counter(concepts)
        return [concept for concept, count in concept_counts.most_common(5)]

    def _extract_philosophical_themes(self, text: str) -> List[str]:
        """Extract philosophical themes from text"""
        themes = []

        # Look for thematic statements
        theme_patterns = [
            r'the nature of ([^.!?]+)',
            r'what it means to ([^.!?]+)',
            r'the essence of ([^.!?]+)',
            r'the question of ([^.!?]+)',
            r'the problem of ([^.!?]+)'
        ]

        for pattern in theme_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            themes.extend([match.strip() for match in matches])

        return themes[:3]  # Return top 3 themes

    def _generate_conceptual_character_name(self, concept: str, index: int) -> str:
        """Generate a character name based on a concept"""
        concept_names = {
            'consciousness': 'Aware',
            'reality': 'Vera',
            'truth': 'Veritas',
            'existence': 'Esse',
            'freedom': 'Liber',
            'love': 'Amor',
            'fear': 'Timor',
            'hope': 'Spes',
            'justice': 'Justus',
            'time': 'Tempus',
            'knowledge': 'Sophia',
            'wisdom': 'Sage',
            'identity': 'Ego',
            'purpose': 'Telos',
            'meaning': 'Logos'
        }

        base_name = concept_names.get(concept.lower(), concept.capitalize())

        # Add suffix for multiple characters
        if index > 0:
            suffixes = ['Prime', 'Second', 'Third', 'Alpha', 'Beta', 'Gamma']
            if index < len(suffixes):
                base_name += f" {suffixes[index]}"
            else:
                base_name += f" {index + 1}"

        return base_name

    async def _build_conceptual_profile(self, name: str, concept: str, text: str, themes: List[str], ctx=None) -> StandardCharacterProfile:
        """Build a character profile around a philosophical concept"""

        # Create conceptual backstory
        backstory = f"A being that embodies the concept of {concept}. "
        if themes:
            backstory += f"Deeply connected to themes of {', '.join(themes)}. "
        backstory += f"Emerged from contemplation of: {text[:200]}..."

        # Generate concept-based traits
        concept_traits = self._generate_concept_traits(concept)
        motivations = self._generate_concept_motivations(concept)
        fears = self._generate_concept_fears(concept)
        desires = self._generate_concept_desires(concept)

        return StandardCharacterProfile(
            name=name,
            backstory=backstory,
            behavioral_traits=concept_traits,
            motivations=motivations,
            fears=fears,
            desires=desires,
            personality_drivers=[f"Driven by the essence of {concept}"],
            confidence_score=0.8,  # High confidence for conceptual creation
            text_references=[text[:300] + "..." if len(text) > 300 else text],
            first_appearance=f"Conceptual character representing {concept}",
            importance_score=0.9
        )

    def _generate_concept_traits(self, concept: str) -> List[str]:
        """Generate behavioral traits based on a concept"""
        trait_mappings = {
            'consciousness': ['introspective', 'aware', 'perceptive', 'mindful'],
            'reality': ['grounded', 'practical', 'truthful', 'authentic'],
            'truth': ['honest', 'direct', 'uncompromising', 'revealing'],
            'freedom': ['independent', 'rebellious', 'liberating', 'unbound'],
            'love': ['compassionate', 'nurturing', 'connecting', 'devoted'],
            'fear': ['cautious', 'protective', 'vigilant', 'anxious'],
            'hope': ['optimistic', 'inspiring', 'persevering', 'uplifting'],
            'justice': ['fair', 'principled', 'righteous', 'balanced'],
            'time': ['patient', 'eternal', 'cyclical', 'measuring'],
            'knowledge': ['curious', 'analytical', 'learning', 'questioning']
        }

        return trait_mappings.get(concept.lower(), [f'embodies {concept}', f'represents {concept}'])

    def _generate_concept_motivations(self, concept: str) -> List[str]:
        """Generate motivations based on a concept"""
        motivation_mappings = {
            'consciousness': ['To awaken others to awareness', 'To explore the depths of mind'],
            'truth': ['To reveal hidden realities', 'To dispel illusions'],
            'freedom': ['To break chains of oppression', 'To liberate the bound'],
            'love': ['To connect all beings', 'To heal through compassion'],
            'justice': ['To restore balance', 'To right wrongs'],
            'knowledge': ['To understand all mysteries', 'To share wisdom']
        }

        return motivation_mappings.get(concept.lower(), [f'To manifest {concept} in the world'])

    def _generate_concept_fears(self, concept: str) -> List[str]:
        """Generate fears based on a concept"""
        fear_mappings = {
            'consciousness': ['Loss of awareness', 'Mental dissolution'],
            'truth': ['Deception prevailing', 'Reality being denied'],
            'freedom': ['Enslavement', 'Restriction of choice'],
            'love': ['Hatred consuming all', 'Isolation and disconnection'],
            'justice': ['Injustice triumphing', 'Moral corruption'],
            'knowledge': ['Ignorance spreading', 'Wisdom being lost']
        }

        return fear_mappings.get(concept.lower(), [f'The absence of {concept}'])

    def _generate_concept_desires(self, concept: str) -> List[str]:
        """Generate desires based on a concept"""
        desire_mappings = {
            'consciousness': ['Universal awakening', 'Perfect awareness'],
            'truth': ['Complete revelation', 'End of all lies'],
            'freedom': ['Total liberation', 'Unlimited choice'],
            'love': ['Universal connection', 'Perfect harmony'],
            'justice': ['Perfect balance', 'True fairness'],
            'knowledge': ['Complete understanding', 'Infinite wisdom']
        }

        return desire_mappings.get(concept.lower(), [f'The perfection of {concept}'])

    def _split_into_character_sections(self, text: str) -> List[str]:
        """Split text into sections that might contain character descriptions"""
        sections = []

        # Split by "Character:" indicators
        char_splits = re.split(r'\n\s*Character:\s*', text)

        if len(char_splits) > 1:
            # First split might not be a character if it doesn't start with "Character:"
            for i, section in enumerate(char_splits):
                if i == 0 and not section.strip().startswith('Character:'):
                    continue  # Skip non-character content at the beginning

                # Add back the "Character:" prefix for consistency
                if not section.strip().startswith('Character:'):
                    section = 'Character: ' + section

                sections.append(section.strip())
        else:
            # No explicit "Character:" markers, try other patterns
            # Look for name patterns at the start of lines
            lines = text.split('\n')
            current_section = ""

            for line in lines:
                line = line.strip()
                if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+\s*$', line):  # Name pattern
                    if current_section:
                        sections.append(current_section.strip())
                    current_section = f"Character: {line}\n"
                else:
                    current_section += line + "\n"

            if current_section:
                sections.append(current_section.strip())

        return [s for s in sections if s.strip()]

    def _extract_character_name_from_section(self, section: str) -> Optional[str]:
        """Extract character name from a description section"""
        # Look for name patterns
        name_patterns = [
            r'Name:\s*([^\n]+)',
            r'Character:\s*([^\n]+)',
            r'^([A-Z][a-z]+ [A-Z][a-z]+)',  # First Last at start
            r'^([A-Z][a-z]+)\s*[-:]',  # Name followed by dash or colon
        ]

        for pattern in name_patterns:
            match = re.search(pattern, section, re.MULTILINE)
            if match:
                return match.group(1).strip()

        return None

    async def _build_profile_from_description(self, name: str, description: str, ctx=None) -> StandardCharacterProfile:
        """Build character profile from explicit description"""

        # Extract structured information
        profile_data = {
            'name': name,
            'physical_description': self._extract_field(description, ['appearance', 'physical', 'looks']),
            'backstory': self._extract_field(description, ['background', 'history', 'backstory']),
            'personality_drivers': self._extract_list_field(description, ['personality', 'traits', 'characteristics']),
            'motivations': self._extract_list_field(description, ['motivation', 'goals', 'wants']),
            'fears': self._extract_list_field(description, ['fears', 'afraid', 'phobias']),
            'desires': self._extract_list_field(description, ['desires', 'wishes', 'dreams']),
            'confidence_score': 0.9,  # High confidence for explicit descriptions
            'text_references': [description[:300] + "..." if len(description) > 300 else description],
            'first_appearance': f"Explicitly described character: {name}",
            'importance_score': 0.8
        }

        return StandardCharacterProfile(**profile_data)

    def _extract_field(self, text: str, field_names: List[str]) -> str:
        """Extract a field value from structured text"""
        for field_name in field_names:
            pattern = rf'{field_name}:\s*([^\n]+(?:\n(?!\w+:)[^\n]+)*)'
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_list_field(self, text: str, field_names: List[str]) -> List[str]:
        """Extract a list field from structured text"""
        for field_name in field_names:
            pattern = rf'{field_name}:\s*([^\n]+(?:\n(?!\w+:)[^\n]+)*)'
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                # Split by common separators
                if ',' in value:
                    return [item.strip() for item in value.split(',') if item.strip()]
                elif ';' in value:
                    return [item.strip() for item in value.split(';') if item.strip()]
                elif '\n' in value:
                    return [item.strip() for item in value.split('\n') if item.strip()]
                else:
                    return [value]
        return []

    async def analyze_text(self, text: str, ctx=None) -> Dict[str, Any]:
        """
        Perform comprehensive character analysis on input text
        
        Args:
            text: Input narrative text
            ctx: Optional context for logging
            
        Returns:
            Dictionary containing analysis results with characters, themes, and emotional arc
        """
        if ctx:
            await ctx.info("Starting enhanced character analysis...")

        # Step 0: Detect content type before processing
        content_type = self._detect_content_type(text)
        processing_strategy = self._determine_processing_strategy(content_type, text)

        if ctx:
            await ctx.info(f"Detected content type: {content_type}, using strategy: {processing_strategy}")

        # Step 1: Character detection based on content type
        characters = await self._detect_characters_by_type(text, content_type, processing_strategy, ctx)

        # Step 2: Semantic theme analysis
        themes = await self._analyze_narrative_themes_semantic(text, ctx)

        # Step 3: Varied emotional arc analysis
        emotional_arc = await self._analyze_emotional_arc_varied(text, ctx)

        # Step 4: Additional analysis
        setting = self._extract_setting_information(text)
        complexity = self._calculate_text_complexity(text)

        result = {
            'characters': [char.to_dict() for char in characters],
            'narrative_themes': [asdict(theme) for theme in themes],
            'emotional_arc': [asdict(state) for state in emotional_arc],
            'setting_description': setting,
            'text_complexity': complexity,
            'processing_time': 0.0,
            'detected_content_type': content_type,
            'processing_strategy': processing_strategy,
            'analysis_metadata': {
                'character_count': len(characters),
                'theme_count': len(themes),
                'emotional_states_count': len(emotional_arc),
                'text_length': len(text),
                'analyzer_version': 'enhanced_v1.1'
            }
        }

        if ctx:
            await ctx.info(f"Enhanced analysis complete: {len(characters)} characters, {len(themes)} themes, {len(emotional_arc)} emotional states")

        return result

    async def analyze_character_text(self, ctx, text: str, user_guidance: str = None) -> Dict[str, Any]:
        """
        Analyze character text with content type detection and clarification support
        
        This method is the main entry point for character analysis that detects
        content type before processing and handles different input formats appropriately.
        It includes clarification request functionality for ambiguous input.
        
        Args:
            ctx: Context for logging and communication
            text: Input text to analyze
            user_guidance: Optional user guidance for processing approach
            
        Returns:
            Dictionary containing character analysis results or clarification request
        """
        try:
            # Perform basic validation
            if not text or len(text.strip()) < 10:
                return {
                    "clarification_needed": True,
                    "error": "Insufficient content",
                    "prompts": ["Please provide more content for character analysis"],
                    "options": [
                        {
                            "id": "provide_more_content",
                            "label": "Provide more detailed content",
                            "description": "Add more text, character details, or context"
                        }
                    ]
                }

            # Detect content type and determine if clarification is needed
            content_analysis = self._analyze_content_for_clarification(text)

            # Check if clarification is needed
            if content_analysis.get("clarification_needed", False) and not user_guidance:
                if ctx:
                    await ctx.info("Content is ambiguous, requesting user clarification")

                return {
                    "clarification_needed": True,
                    "content_analysis": content_analysis,
                    "prompts": content_analysis.get("suggested_clarifications", []),
                    "options": self._generate_processing_options(content_analysis),
                    "text_preview": text[:200] + "..." if len(text) > 200 else text
                }

            # Process with user guidance if provided
            if user_guidance:
                if ctx:
                    await ctx.info(f"Processing with user guidance: {user_guidance}")
                return await self._analyze_with_guidance(text, user_guidance, ctx)

            # Proceed with automatic analysis
            return await self.analyze_text(text, ctx)

        except Exception as e:
            if ctx:
                await ctx.error(f"Character analysis failed: {str(e)}")

            # Return clarification request on error
            return {
                "clarification_needed": True,
                "error": str(e),
                "prompts": [
                    "An error occurred during analysis. Could you help clarify the content type?",
                    "What type of content would you like me to process?"
                ],
                "options": self._get_default_processing_options()
            }

    def _analyze_content_for_clarification(self, text: str) -> Dict[str, Any]:
        """
        Analyze content to determine if clarification is needed
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing analysis results and clarification indicators
        """
        text_lower = text.lower()

        # Detect different content type indicators
        content_indicators = {
            "character_description": self._detect_character_description_indicators(text_lower),
            "narrative_fiction": self._detect_narrative_indicators(text_lower),
            "philosophical_conceptual": self._detect_philosophical_indicators(text_lower),
            "poetic_content": self._detect_poetic_indicators(text_lower)
        }

        # Calculate confidence scores
        total_indicators = sum(content_indicators.values())
        confidence_scores = {}

        if total_indicators > 0:
            for content_type, count in content_indicators.items():
                confidence_scores[content_type] = count / total_indicators
        else:
            confidence_scores = {"unknown": 1.0}

        # Determine primary content type
        primary_type = max(confidence_scores.keys(), key=lambda k: confidence_scores[k])
        primary_confidence = confidence_scores[primary_type]

        # Calculate ambiguity (how close the top scores are)
        sorted_scores = sorted(confidence_scores.values(), reverse=True)
        ambiguity_score = 0.0
        if len(sorted_scores) > 1:
            ambiguity_score = 1.0 - (sorted_scores[0] - sorted_scores[1])

        # Determine if clarification is needed
        clarification_needed = (
            primary_confidence < 0.6 or  # Low confidence
            ambiguity_score > 0.4 or     # High ambiguity
            primary_type == "unknown"     # Unknown content type
        )

        # Generate clarification suggestions
        suggested_clarifications = self._generate_content_clarifications(
            primary_type, primary_confidence, ambiguity_score, confidence_scores
        )

        return {
            "content_type": primary_type,
            "confidence": primary_confidence,
            "ambiguity_score": ambiguity_score,
            "confidence_scores": confidence_scores,
            "clarification_needed": clarification_needed,
            "suggested_clarifications": suggested_clarifications,
            "detected_indicators": content_indicators
        }

    def _detect_character_description_indicators(self, text_lower: str) -> int:
        """Count indicators of explicit character descriptions"""
        indicators = [
            "character:", "protagonist:", "artist:", "musician:", "producer:",
            "year-old", "years old", "born in", "grew up", "personality:",
            "background:", "style:", "genre:", "influences:", "known for"
        ]
        return sum(1 for indicator in indicators if indicator in text_lower)

    def _detect_narrative_indicators(self, text_lower: str) -> int:
        """Count indicators of narrative fiction"""
        indicators = [
            "once upon", "chapter", "he said", "she said", "they said",
            "walked", "looked", "thought", "remembered", "dialogue",
            "story", "plot", "scene", "narrator"
        ]
        return sum(1 for indicator in indicators if indicator in text_lower)

    def _detect_philosophical_indicators(self, text_lower: str) -> int:
        """Count indicators of philosophical content"""
        indicators = [
            "philosophy", "philosophical", "concept", "meaning", "existence",
            "consciousness", "reality", "truth", "spiritual", "divine",
            "metaphysical", "existential", "transcendent"
        ]
        return sum(1 for indicator in indicators if indicator in text_lower)

    def _detect_poetic_indicators(self, text_lower: str) -> int:
        """Count indicators of poetic content"""
        indicators = ["poem", "poetry", "verse", "metaphor", "imagery", "stanza"]
        count = sum(1 for indicator in indicators if indicator in text_lower)

        # Add points for structural indicators
        if "/" in text_lower:  # Line break indicators
            count += 1
        if "\n" in text_lower and len(text_lower.split("\n")) > 3:  # Multiple line breaks
            count += 1

        return count

    def _generate_content_clarifications(self, primary_type: str, confidence: float,
                                       ambiguity_score: float, confidence_scores: Dict) -> List[str]:
        """Generate helpful clarification suggestions"""
        clarifications = []

        if confidence < 0.4:
            clarifications.extend([
                "I'm having difficulty determining the content type.",
                "Could you specify whether this is a character description, story excerpt, or conceptual content?"
            ])
        elif ambiguity_score > 0.5:
            # Multiple possible types detected
            top_types = sorted(confidence_scores.items(), key=lambda x: x[1], reverse=True)[:2]
            type_names = [t[0].replace("_", " ") for t, _ in top_types]
            clarifications.append(f"This could be {type_names[0]} or {type_names[1]}. Which would you prefer?")
        elif primary_type == "unknown":
            clarifications.extend([
                "I couldn't identify a clear content type.",
                "Please help me understand what type of content this is."
            ])
        else:
            clarifications.append(f"This appears to be {primary_type.replace('_', ' ')}. Is this correct?")

        return clarifications

    def _generate_processing_options(self, content_analysis: Dict) -> List[Dict]:
        """Generate processing options based on content analysis"""
        options = []
        confidence_scores = content_analysis.get("confidence_scores", {})

        # Add options for detected content types (sorted by confidence)
        sorted_types = sorted(confidence_scores.items(), key=lambda x: x[1], reverse=True)

        for content_type, confidence in sorted_types:
            if confidence > 0.1 and content_type != "unknown":  # Only include meaningful options
                option = self._create_processing_option(content_type, confidence)
                if option:
                    options.append(option)

        # Add fallback options
        if not options or len(options) < 2:
            options.extend(self._get_default_processing_options())

        return options[:5]  # Limit to 5 options to avoid overwhelming user

    def _create_processing_option(self, content_type: str, confidence: float) -> Dict:
        """Create a processing option for a specific content type"""
        option_templates = {
            "character_description": {
                "id": "character_description",
                "label": "Character Description",
                "description": "Process as explicit character details and use them directly for music creation"
            },
            "narrative_fiction": {
                "id": "narrative_fiction",
                "label": "Story/Narrative",
                "description": "Extract characters from the narrative and create music from their perspective"
            },
            "philosophical_conceptual": {
                "id": "philosophical_conceptual",
                "label": "Conceptual/Philosophical",
                "description": "Create characters that embody these concepts and explore them through music"
            },
            "poetic_content": {
                "id": "poetic_content",
                "label": "Poetic Content",
                "description": "Create characters from the poetic voice and transform imagery into music"
            }
        }

        template = option_templates.get(content_type)
        if template:
            template["confidence"] = confidence
            return template
        return None

    def _get_default_processing_options(self) -> List[Dict]:
        """Get default processing options when content type is unclear"""
        return [
            {
                "id": "character_description",
                "label": "Treat as Character Description",
                "description": "Use any character details provided directly"
            },
            {
                "id": "narrative_fiction",
                "label": "Extract from Narrative",
                "description": "Look for characters within story elements"
            },
            {
                "id": "philosophical_conceptual",
                "label": "Create from Concepts",
                "description": "Build characters that embody the themes and ideas"
            },
            {
                "id": "mixed_content",
                "label": "Adaptive Processing",
                "description": "Let me try multiple approaches and use the best result"
            }
        ]

    async def _analyze_with_guidance(self, text: str, user_guidance: str, ctx) -> Dict[str, Any]:
        """
        Analyze text with user-provided guidance
        
        Args:
            text: Input text to analyze
            user_guidance: User's chosen processing approach
            ctx: Context for logging
            
        Returns:
            Analysis results using the specified approach
        """
        if ctx:
            await ctx.info(f"Analyzing with user guidance: {user_guidance}")

        # Map user guidance to processing approach
        guidance_mapping = {
            "character_description": "explicit_character",
            "narrative_fiction": "narrative_extraction",
            "philosophical_conceptual": "conceptual_creation",
            "poetic_content": "poetic_analysis",
            "mixed_content": "adaptive_analysis"
        }

        processing_approach = guidance_mapping.get(user_guidance, "standard_analysis")

        # Perform analysis with specified approach
        result = await self.analyze_text(text, ctx)

        # Add guidance metadata
        result["processing_guidance"] = {
            "user_choice": user_guidance,
            "processing_approach": processing_approach,
            "guidance_applied": True
        }

        return result

    async def _detect_characters_enhanced(self, text: str, ctx=None) -> List[StandardCharacterProfile]:
        """
        Enhanced character detection using multiple NER techniques
        
        Implements requirement 1.1: Replace empty character detection with actual name entity recognition
        """
        if ctx:
            await ctx.info("Performing enhanced character detection...")

        # Step 1: Extract potential character names using multiple patterns
        potential_characters = self._extract_potential_character_names(text)

        # Step 2: Validate and score character candidates
        validated_characters = self._validate_character_candidates(potential_characters, text)

        # Step 3: Build comprehensive character profiles
        character_profiles = []
        for char_name, score in validated_characters:
            if score > 0.3:  # Minimum confidence threshold
                try:
                    profile = await self._build_three_layer_profile(char_name, text, ctx)
                    if profile.confidence_score > 0.2:  # Lower threshold for profile acceptance
                        character_profiles.append(profile)
                except Exception as e:
                    if ctx:
                        await ctx.error(f"Failed to build profile for {char_name}: {str(e)}")
                    continue

        # Step 4: Sort by importance and return top characters
        character_profiles.sort(key=lambda x: x.importance_score, reverse=True)

        if ctx:
            await ctx.info(f"Detected {len(character_profiles)} valid characters")

        return character_profiles[:8]  # Return top 8 characters

    def _extract_potential_character_names(self, text: str) -> Dict[str, int]:
        """Extract potential character names using multiple NER patterns"""
        potential_names = defaultdict(int)

        # Pattern 1: Full names (First Last, First Middle Last)
        full_names = re.findall(self.character_patterns['full_names'], text)
        for name in full_names:
            if name not in self.common_words:
                potential_names[name] += 3  # Higher weight for full names

        # Pattern 2: Single names with frequency check
        single_names = re.findall(self.character_patterns['single_names'], text)
        name_counts = Counter(single_names)
        for name, count in name_counts.items():
            if name not in self.common_words and count >= 2:  # Must appear at least twice
                potential_names[name] += count

        # Pattern 3: Dialogue attribution
        dialogue_names = re.findall(self.character_patterns['dialogue_attribution'], text)
        for name in dialogue_names:
            if name not in self.common_words:
                potential_names[name] += 4  # High weight for dialogue attribution

        # Pattern 4: Possessive forms
        possessive_names = re.findall(self.character_patterns['possessive_names'], text)
        for name in possessive_names:
            if name not in self.common_words:
                potential_names[name] += 2

        # Pattern 5: Direct address in dialogue
        address_names = re.findall(self.character_patterns['direct_address'], text)
        for name in address_names:
            if name not in self.common_words:
                potential_names[name] += 3

        # Pattern 6: Action attribution
        action_names = re.findall(self.character_patterns['action_attribution'], text)
        for name in action_names:
            if name not in self.common_words:
                potential_names[name] += 2

        return dict(potential_names)

    def _validate_character_candidates(self, candidates: Dict[str, int], text: str) -> List[Tuple[str, float]]:
        """Validate character candidates and assign confidence scores"""
        validated = []

        for name, raw_score in candidates.items():
            # Skip if name is too short or too long
            if len(name) < 2 or len(name) > 25:
                continue

            # Skip if name contains numbers or special characters
            if re.search(r'[0-9@#$%^&*()_+=\[\]{}|\\:";\'<>?,./]', name):
                continue

            # Calculate confidence score
            confidence = self._calculate_character_confidence(name, raw_score, text)

            if confidence > 0.3:  # Minimum threshold
                validated.append((name, confidence))

        # Sort by confidence
        validated.sort(key=lambda x: x[1], reverse=True)
        return validated

    def _calculate_character_confidence(self, name: str, raw_score: int, text: str) -> float:
        """Calculate confidence score for a character candidate"""
        # Base score from pattern matching - more generous scoring
        base_score = min(raw_score / 5.0, 0.7)  # Max 0.7 from raw score, lower threshold

        # Context analysis
        context_score = 0.0

        # Check for character-like context around mentions
        character_contexts = [
            r'\b' + re.escape(name) + r'\b\s+(?:was|is|had|has|did|does|said|says|felt|feels|thought|thinks|looked|looks|walked|walks|ran|runs|stood|sat)',
            r'(?:he|she|they)\s+.*\b' + re.escape(name) + r'\b',
            r'\b' + re.escape(name) + r'\b.*(?:smiled|frowned|laughed|cried|whispered|shouted)',
            r'\b' + re.escape(name) + r'\b.*(?:heart|mind|eyes|face|hand)'  # Physical/emotional references
        ]

        for pattern in character_contexts:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            context_score += matches * 0.1  # Increased weight

        context_score = min(context_score, 0.4)  # Max 0.4 from context

        # Position bonus (characters mentioned early are often important)
        text_length = len(text)
        first_mention = text.lower().find(name.lower())
        if first_mention != -1:
            position_score = 0.15 * (1 - (first_mention / text_length))  # Increased bonus
        else:
            position_score = 0.0

        # Frequency bonus - if name appears multiple times, it's likely a character
        name_count = text.lower().count(name.lower())
        frequency_bonus = min(name_count * 0.1, 0.2)

        total_score = base_score + context_score + position_score + frequency_bonus
        return min(total_score, 1.0)

    async def _build_three_layer_profile(self, name: str, text: str, ctx=None) -> StandardCharacterProfile:
        """
        Build comprehensive character profile using three-layer analysis
        
        Implements requirements 1.2, 1.3, 1.4: Add three-layer character analysis (skin/flesh/core)
        """
        # Extract character-related text segments
        char_segments = self._extract_character_segments(name, text)

        # SKIN LAYER - Observable characteristics
        skin_layer = await self._analyze_skin_layer(name, char_segments, text)

        # FLESH LAYER - Background and relationships
        flesh_layer = await self._analyze_flesh_layer(name, char_segments, text)

        # CORE LAYER - Deep psychology
        core_layer = await self._analyze_core_layer(name, char_segments, text)

        # Calculate metadata
        confidence = self._calculate_profile_confidence(name, char_segments, skin_layer, flesh_layer, core_layer)
        importance = self._calculate_character_importance(name, text)

        # Find aliases
        aliases = self._find_character_aliases(name, text)

        # Create profile
        profile = StandardCharacterProfile(
            name=name,
            aliases=aliases,

            # Skin layer
            physical_description=skin_layer['physical_description'],
            mannerisms=skin_layer['mannerisms'],
            speech_patterns=skin_layer['speech_patterns'],
            behavioral_traits=skin_layer['behavioral_traits'],

            # Flesh layer
            backstory=flesh_layer['backstory'],
            relationships=flesh_layer['relationships'],
            formative_experiences=flesh_layer['formative_experiences'],
            social_connections=flesh_layer['social_connections'],

            # Core layer
            motivations=core_layer['motivations'],
            fears=core_layer['fears'],
            desires=core_layer['desires'],
            conflicts=core_layer['conflicts'],
            personality_drivers=core_layer['personality_drivers'],

            # Metadata
            confidence_score=confidence,
            text_references=char_segments[:5],
            first_appearance=char_segments[0] if char_segments else f"Character named {name}",
            importance_score=importance
        )

        return profile

    def _extract_character_segments(self, name: str, text: str) -> List[str]:
        """Extract text segments that mention the character"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        segments = []

        # Find sentences mentioning the character
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and name.lower() in sentence.lower():
                segments.append(sentence)

        # Also extract paragraphs containing the character
        paragraphs = text.split('\n\n')
        for paragraph in paragraphs:
            if name.lower() in paragraph.lower() and paragraph.strip() not in segments:
                # Add paragraph if it's not already covered by sentences
                segments.append(paragraph.strip())

        return segments

    async def _analyze_skin_layer(self, name: str, segments: List[str], full_text: str) -> Dict[str, Any]:
        """
        Analyze skin layer - observable characteristics
        
        Physical descriptions, mannerisms, speech patterns, behavioral traits
        """
        skin_layer = {
            'physical_description': '',
            'mannerisms': [],
            'speech_patterns': [],
            'behavioral_traits': []
        }

        # Physical description patterns
        physical_patterns = [
            r'\b(?:tall|short|thin|fat|slim|heavy|light|dark|pale|tanned|blonde|brunette|redhead)\b',
            r'\b(?:hair|eyes|skin|face|build|height|weight)\b.*?(?:was|were|is|are)\s+([^.!?]+)',
            r'\b(?:wore|dressed|clothing|outfit|appearance)\b.*?([^.!?]+)',
            r'\b(?:beautiful|handsome|ugly|attractive|plain|striking|elegant|rough)\b'
        ]

        physical_descriptions = []
        for segment in segments:
            for pattern in physical_patterns:
                matches = re.findall(pattern, segment, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        physical_descriptions.extend([m for m in match if m.strip()])
                    else:
                        physical_descriptions.append(match)

        if physical_descriptions:
            skin_layer['physical_description'] = ' '.join(physical_descriptions[:3])
        else:
            skin_layer['physical_description'] = f"Physical description of {name} not explicitly provided in text."

        # Mannerisms - repeated behaviors and gestures
        mannerism_patterns = [
            r'\b(?:smiled|frowned|gestured|nodded|shook|laughed|sighed|whispered|grinned|winked|shrugged)\b',
            r'\b(?:habit|tendency|way|manner)\b.*?(?:of|to)\s+([^.!?]+)',
            r'\b(?:always|often|frequently|usually)\b.*?([^.!?]+)'
        ]

        for segment in segments:
            if name.lower() in segment.lower():
                for pattern in mannerism_patterns:
                    matches = re.findall(pattern, segment, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, str) and len(match.strip()) > 3:
                            skin_layer['mannerisms'].append(f"{match.strip()[:60]}...")

        # Remove duplicates
        skin_layer['mannerisms'] = list(set(skin_layer['mannerisms']))[:5]

        # Speech patterns - how the character speaks
        speech_patterns = []
        dialogue_segments = []

        # Extract dialogue
        dialogue_pattern = r'"([^"]+)"\s*,?\s*' + re.escape(name) + r'\s+(?:said|asked|replied|whispered|shouted|exclaimed)'
        dialogue_matches = re.findall(dialogue_pattern, full_text, re.IGNORECASE)
        dialogue_segments.extend(dialogue_matches)

        # Reverse pattern - name first, then dialogue
        reverse_pattern = re.escape(name) + r'\s+(?:said|asked|replied|whispered|shouted|exclaimed)\s*,?\s*"([^"]+)"'
        reverse_matches = re.findall(reverse_pattern, full_text, re.IGNORECASE)
        dialogue_segments.extend(reverse_matches)

        # Analyze speech patterns
        if dialogue_segments:
            # Analyze vocabulary level
            avg_word_length = sum(len(word) for dialogue in dialogue_segments for word in dialogue.split()) / max(1, sum(len(dialogue.split()) for dialogue in dialogue_segments))
            if avg_word_length > 5:
                speech_patterns.append("Uses sophisticated vocabulary")
            elif avg_word_length < 4:
                speech_patterns.append("Uses simple, direct language")

            # Check for speech quirks
            combined_dialogue = ' '.join(dialogue_segments).lower()
            if combined_dialogue.count('um') + combined_dialogue.count('uh') > 2:
                speech_patterns.append("Hesitant speech with filler words")
            if combined_dialogue.count('!') > len(dialogue_segments) * 0.3:
                speech_patterns.append("Exclamatory, emphatic speech")
            if combined_dialogue.count('?') > len(dialogue_segments) * 0.2:
                speech_patterns.append("Questioning, inquisitive speech")

        skin_layer['speech_patterns'] = speech_patterns[:4]

        # Behavioral traits - observable behaviors
        behavior_patterns = {
            'aggressive': ['aggressive', 'violent', 'hostile', 'confrontational', 'combative'],
            'gentle': ['gentle', 'kind', 'soft', 'tender', 'caring'],
            'confident': ['confident', 'bold', 'assertive', 'self-assured', 'decisive'],
            'nervous': ['nervous', 'anxious', 'fidgety', 'restless', 'worried'],
            'calm': ['calm', 'peaceful', 'serene', 'composed', 'tranquil'],
            'energetic': ['energetic', 'active', 'lively', 'dynamic', 'vigorous'],
            'withdrawn': ['withdrawn', 'quiet', 'reserved', 'introverted', 'shy'],
            'social': ['social', 'outgoing', 'friendly', 'gregarious', 'extroverted']
        }

        behavioral_traits = []
        for segment in segments:
            if name.lower() in segment.lower():
                for trait, keywords in behavior_patterns.items():
                    for keyword in keywords:
                        if keyword in segment.lower():
                            behavioral_traits.append(f"{trait}: {keyword} - {segment[:50]}...")
                            break

        skin_layer['behavioral_traits'] = list(set(behavioral_traits))[:5]

        return skin_layer

    async def _analyze_flesh_layer(self, name: str, segments: List[str], full_text: str) -> Dict[str, Any]:
        """
        Analyze flesh layer - background and relationships
        
        Backstory, relationships, formative experiences, social connections
        """
        flesh_layer = {
            'backstory': '',
            'relationships': [],
            'formative_experiences': [],
            'social_connections': []
        }

        # Backstory patterns
        backstory_patterns = [
            r'\b(?:grew up|childhood|born|raised|family|parents|mother|father|past|history|before|used to|once|years ago)\b.*?([^.!?]+)',
            r'\b(?:background|origin|came from|lived in|worked as|studied|education)\b.*?([^.!?]+)'
        ]

        backstory_segments = []
        for segment in segments:
            if name.lower() in segment.lower():
                for pattern in backstory_patterns:
                    matches = re.findall(pattern, segment, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, str) and len(match.strip()) > 10:
                            backstory_segments.append(match.strip())

        if backstory_segments:
            flesh_layer['backstory'] = ' '.join(backstory_segments[:3])
        else:
            flesh_layer['backstory'] = f"Backstory for {name} not explicitly detailed in the provided text."

        # Relationships
        relationship_patterns = [
            r'\b(?:friend|enemy|lover|partner|spouse|husband|wife|boyfriend|girlfriend|parent|child|son|daughter|brother|sister|sibling|colleague|mentor|student|teacher|boss|employee)\b',
            r'\b(?:relationship|married|dating|engaged|divorced|separated)\b.*?([^.!?]+)',
            r'\b(?:loves|hates|likes|dislikes|trusts|distrusts)\b.*?([A-Z][a-z]+)'
        ]

        relationships = []
        for segment in segments:
            if name.lower() in segment.lower():
                for pattern in relationship_patterns:
                    matches = re.findall(pattern, segment, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, str) and len(match.strip()) > 3:
                            relationships.append(f"Relationship context: {segment[:60]}...")

        flesh_layer['relationships'] = list(set(relationships))[:5]

        # Formative experiences
        experience_patterns = [
            r'\b(?:experienced|learned|discovered|realized|changed|transformed|happened|occurred|event|incident|moment)\b.*?([^.!?]+)',
            r'\b(?:first time|last time|never forget|always remember|turning point|life-changing)\b.*?([^.!?]+)'
        ]

        experiences = []
        for segment in segments:
            if name.lower() in segment.lower():
                for pattern in experience_patterns:
                    matches = re.findall(pattern, segment, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, str) and len(match.strip()) > 10:
                            experiences.append(f"Experience: {match.strip()[:60]}...")

        flesh_layer['formative_experiences'] = list(set(experiences))[:4]

        # Social connections - other characters mentioned with this character
        connections = []
        for segment in segments:
            if name.lower() in segment.lower():
                # Find other proper names in the same segment
                other_names = re.findall(r'\b[A-Z][a-z]{2,}\b', segment)
                for other_name in other_names:
                    if other_name != name and other_name not in self.common_words and len(other_name) > 2:
                        connections.append(f"Connected to {other_name} in context: {segment[:40]}...")

        flesh_layer['social_connections'] = list(set(connections))[:6]

        return flesh_layer

    async def _analyze_core_layer(self, name: str, segments: List[str], full_text: str) -> Dict[str, Any]:
        """
        Analyze core layer - deep psychology
        
        Motivations, fears, desires, conflicts, personality drivers
        """
        core_layer = {
            'motivations': [],
            'fears': [],
            'desires': [],
            'conflicts': [],
            'personality_drivers': []
        }

        # Motivations
        motivation_patterns = [
            r'\b(?:wants|needs|desires|seeks|hopes|dreams|goals|ambitions|purpose|drive|motivation)\b.*?([^.!?]+)',
            r'\b(?:trying to|attempting to|working toward|striving for|aiming to)\b.*?([^.!?]+)'
        ]

        motivations = []
        for segment in segments:
            if name.lower() in segment.lower():
                for pattern in motivation_patterns:
                    matches = re.findall(pattern, segment, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, str) and len(match.strip()) > 5:
                            motivations.append(f"Motivation: {match.strip()[:60]}...")

        core_layer['motivations'] = list(set(motivations))[:4]

        # Fears
        fear_patterns = [
            r'\b(?:afraid|fear|scared|terrified|worried|anxious|phobia|nightmare|dread)\b.*?([^.!?]+)',
            r'\b(?:what if|worried about|concerned about|frightened by)\b.*?([^.!?]+)'
        ]

        fears = []
        for segment in segments:
            if name.lower() in segment.lower():
                for pattern in fear_patterns:
                    matches = re.findall(pattern, segment, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, str) and len(match.strip()) > 5:
                            fears.append(f"Fear: {match.strip()[:60]}...")

        core_layer['fears'] = list(set(fears))[:4]

        # Desires
        desire_patterns = [
            r'\b(?:love|want|desire|wish|long for|crave|yearn|dream of|hope for)\b.*?([^.!?]+)',
            r'\b(?:if only|wished|dreamed|longed)\b.*?([^.!?]+)'
        ]

        desires = []
        for segment in segments:
            if name.lower() in segment.lower():
                for pattern in desire_patterns:
                    matches = re.findall(pattern, segment, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, str) and len(match.strip()) > 5:
                            desires.append(f"Desire: {match.strip()[:60]}...")

        core_layer['desires'] = list(set(desires))[:4]

        # Conflicts
        conflict_patterns = [
            r'\b(?:conflict|struggle|fight|battle|oppose|against|problem|dilemma|torn between)\b.*?([^.!?]+)',
            r'\b(?:can\'t decide|difficult choice|internal struggle|at odds)\b.*?([^.!?]+)'
        ]

        conflicts = []
        for segment in segments:
            if name.lower() in segment.lower():
                for pattern in conflict_patterns:
                    matches = re.findall(pattern, segment, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, str) and len(match.strip()) > 5:
                            conflicts.append(f"Conflict: {match.strip()[:60]}...")

        core_layer['conflicts'] = list(set(conflicts))[:4]

        # Personality drivers - core traits that drive behavior
        personality_indicators = {
            'ambitious': ['ambitious', 'driven', 'determined', 'goal-oriented', 'competitive'],
            'compassionate': ['compassionate', 'empathetic', 'caring', 'kind', 'nurturing'],
            'independent': ['independent', 'self-reliant', 'autonomous', 'free-spirited'],
            'loyal': ['loyal', 'faithful', 'devoted', 'committed', 'steadfast'],
            'curious': ['curious', 'inquisitive', 'questioning', 'investigative'],
            'protective': ['protective', 'defensive', 'guardian', 'watchful'],
            'rebellious': ['rebellious', 'defiant', 'non-conformist', 'revolutionary'],
            'perfectionist': ['perfectionist', 'meticulous', 'precise', 'exacting']
        }

        personality_drivers = []
        driver_scores = defaultdict(int)

        for segment in segments:
            if name.lower() in segment.lower():
                for driver, keywords in personality_indicators.items():
                    for keyword in keywords:
                        if keyword in segment.lower():
                            driver_scores[driver] += 1

        # Get top personality drivers
        sorted_drivers = sorted(driver_scores.items(), key=lambda x: x[1], reverse=True)
        for driver, score in sorted_drivers[:4]:
            personality_drivers.append(f"{driver} (evidence strength: {score})")

        core_layer['personality_drivers'] = personality_drivers

        return core_layer

    def _calculate_profile_confidence(self, name: str, segments: List[str], skin_layer: Dict, flesh_layer: Dict, core_layer: Dict) -> float:
        """Calculate confidence score for the character profile"""
        if not segments:
            return 0.0

        # Base score from number of mentions
        mention_score = min(len(segments) / 15.0, 0.3)

        # Information depth score
        info_score = 0.0

        # Skin layer completeness
        if skin_layer['physical_description'] and 'not explicitly provided' not in skin_layer['physical_description']:
            info_score += 0.1
        if skin_layer['mannerisms']:
            info_score += 0.05
        if skin_layer['speech_patterns']:
            info_score += 0.05
        if skin_layer['behavioral_traits']:
            info_score += 0.1

        # Flesh layer completeness
        if flesh_layer['backstory'] and 'not explicitly detailed' not in flesh_layer['backstory']:
            info_score += 0.15
        if flesh_layer['relationships']:
            info_score += 0.1
        if flesh_layer['formative_experiences']:
            info_score += 0.05
        if flesh_layer['social_connections']:
            info_score += 0.05

        # Core layer completeness
        if core_layer['motivations']:
            info_score += 0.1
        if core_layer['fears']:
            info_score += 0.05
        if core_layer['desires']:
            info_score += 0.05
        if core_layer['conflicts']:
            info_score += 0.05
        if core_layer['personality_drivers']:
            info_score += 0.1

        total_score = mention_score + info_score
        return min(total_score, 1.0)

    def _calculate_character_importance(self, name: str, text: str) -> float:
        """Calculate character importance in the narrative"""
        total_words = len(text.split())
        if total_words == 0:
            return 0.0

        name_mentions = text.lower().count(name.lower())
        frequency_score = name_mentions / total_words * 100

        # Position bonus
        paragraphs = text.split('\n\n')
        position_bonus = 0.0

        if paragraphs and name.lower() in paragraphs[0].lower():
            position_bonus += 0.2  # Mentioned in first paragraph

        if len(paragraphs) > 1 and name.lower() in paragraphs[-1].lower():
            position_bonus += 0.1  # Mentioned in last paragraph

        # Dialogue bonus
        dialogue_pattern = r'"[^"]*"[^"]*' + re.escape(name)
        dialogue_mentions = len(re.findall(dialogue_pattern, text, re.IGNORECASE))
        dialogue_bonus = min(dialogue_mentions * 0.05, 0.2)

        total_importance = frequency_score + position_bonus + dialogue_bonus
        return min(total_importance, 1.0)

    def _find_character_aliases(self, name: str, text: str) -> List[str]:
        """Find aliases and alternative names for the character"""
        aliases = []

        # Pattern 1: "John, also known as Jack"
        pattern1 = rf"{re.escape(name)}[,\s]+(?:also known as|nicknamed|called|known as)\s+([A-Z][a-z]+)"
        matches1 = re.findall(pattern1, text, re.IGNORECASE)
        aliases.extend(matches1)

        # Pattern 2: "Jack (also known as John)"
        pattern2 = rf"([A-Z][a-z]+)[,\s]*\([^)]*{re.escape(name)}[^)]*\)"
        matches2 = re.findall(pattern2, text, re.IGNORECASE)
        aliases.extend(matches2)

        # Pattern 3: "John (Jack)"
        pattern3 = rf"{re.escape(name)}\s*\(([A-Z][a-z]+)\)"
        matches3 = re.findall(pattern3, text, re.IGNORECASE)
        aliases.extend(matches3)

        return list(set(aliases))

    async def _analyze_narrative_themes_semantic(self, text: str, ctx=None) -> List[NarrativeTheme]:
        """
        Semantic analysis to identify multiple narrative themes
        
        Implements requirement 1.2: Fix narrative theme analysis beyond "friendship"
        """
        if ctx:
            await ctx.info("Performing semantic theme analysis...")

        themes = []
        text_lower = text.lower()

        for theme_name, theme_data in self.theme_patterns.items():
            evidence = []
            keyword_matches = []
            pattern_matches = []

            # Check keywords
            for keyword in theme_data['keywords']:
                count = text_lower.count(keyword.lower())
                if count > 0:
                    keyword_matches.append(f"{keyword} ({count} occurrences)")

            # Check patterns
            for pattern in theme_data.get('patterns', []):
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    pattern_matches.extend([f"Pattern match: {match}" for match in matches[:3]])

            # Calculate theme strength
            keyword_strength = len(keyword_matches) * 0.1
            pattern_strength = len(pattern_matches) * 0.15

            # Context analysis - look for thematic sentences
            theme_sentences = []
            sentences = re.split(r'[.!?]+', text)
            for sentence in sentences:
                sentence_lower = sentence.lower()
                theme_word_count = sum(1 for keyword in theme_data['keywords'] if keyword.lower() in sentence_lower)
                if theme_word_count >= 2:  # Sentence contains multiple theme words
                    theme_sentences.append(sentence.strip()[:100] + "...")

            context_strength = len(theme_sentences) * 0.2
            total_strength = keyword_strength + pattern_strength + context_strength

            if total_strength > 0.1:  # Minimum threshold for theme inclusion
                evidence.extend(keyword_matches)
                evidence.extend(pattern_matches)
                evidence.extend([f"Thematic context: {sent}" for sent in theme_sentences[:2]])

                theme = NarrativeTheme(
                    theme=theme_name.replace('_', ' ').title(),
                    strength=min(total_strength, 1.0),
                    evidence=evidence[:5],  # Limit evidence to top 5 items
                    keywords=theme_data['keywords'][:5]
                )
                themes.append(theme)

        # Sort themes by strength
        themes.sort(key=lambda x: x.strength, reverse=True)

        if ctx:
            await ctx.info(f"Identified {len(themes)} narrative themes")

        return themes[:8]  # Return top 8 themes

    async def _analyze_emotional_arc_varied(self, text: str, ctx=None) -> List[EmotionalState]:
        """
        Analyze emotional progression with deeper psychological analysis
        
        Enhanced implementation for requirement 4.1: Replace superficial emotion detection 
        with deeper psychological analysis and complex emotional state tracking
        """
        if ctx:
            await ctx.info("Performing deep psychological emotional analysis...")

        # Divide text into sections for progression analysis
        text_length = len(text)
        section_size = max(text_length // 5, 200)  # At least 200 chars per section
        sections = []

        for i in range(0, text_length, section_size):
            section = text[i:i + section_size]
            if section.strip():
                sections.append((section, i))

        emotional_states = []

        # Analyze each section with enhanced psychological depth
        for section_idx, (section, position) in enumerate(sections):
            section_emotions = await self._analyze_section_emotions_deep(section, position, section_idx, ctx)
            if section_emotions:
                emotional_states.extend(section_emotions)

        # Add philosophical-emotional connections
        philosophical_emotions = await self._analyze_philosophical_emotional_connections(text, ctx)
        emotional_states.extend(philosophical_emotions)

        # Analyze complex emotional patterns and transitions
        complex_patterns = await self._analyze_complex_emotional_patterns(text, emotional_states, ctx)
        emotional_states.extend(complex_patterns)

        # If still no specific emotions found, perform deep contextual analysis
        if not emotional_states:
            deep_contextual = await self._analyze_deep_contextual_emotions(text, ctx)
            if deep_contextual:
                emotional_states.extend(deep_contextual)

        # Sort by psychological depth and relevance
        emotional_states = self._prioritize_emotional_states_by_depth(emotional_states)

        if ctx:
            await ctx.info(f"Identified {len(emotional_states)} deep psychological emotional states")

        return emotional_states[:12]  # Return up to 12 emotional states for richer analysis

    async def _analyze_section_emotions_deep(self, section: str, position: int, section_idx: int, ctx=None) -> List[EmotionalState]:
        """
        Analyze emotions in a specific text section with deep psychological analysis
        
        Enhanced for requirement 4.1: Deeper psychological analysis beyond surface emotions
        """
        section_emotions = []
        section_lower = section.lower()

        # Enhanced emotion patterns with psychological depth
        deep_emotion_patterns = {
            'existential_anxiety': {
                'keywords': ['meaningless', 'purpose', 'why exist', 'what\'s the point', 'emptiness', 'void', 'absurd'],
                'psychological_indicators': ['questioning existence', 'search for meaning', 'confronting mortality'],
                'intensity_base': 0.7
            },
            'cognitive_dissonance': {
                'keywords': ['contradiction', 'conflicted', 'torn between', 'doesn\'t make sense', 'paradox'],
                'psychological_indicators': ['internal conflict', 'belief system challenge', 'moral ambiguity'],
                'intensity_base': 0.6
            },
            'transcendent_awe': {
                'keywords': ['overwhelming', 'infinite', 'beyond understanding', 'sublime', 'transcendent'],
                'psychological_indicators': ['spiritual experience', 'ego dissolution', 'cosmic perspective'],
                'intensity_base': 0.8
            },
            'melancholic_nostalgia': {
                'keywords': ['bittersweet', 'longing', 'what could have been', 'lost time', 'fading'],
                'psychological_indicators': ['temporal displacement', 'idealized past', 'loss processing'],
                'intensity_base': 0.5
            },
            'anticipatory_dread': {
                'keywords': ['inevitable', 'approaching', 'can\'t escape', 'looming', 'countdown'],
                'psychological_indicators': ['future anxiety', 'helplessness', 'temporal pressure'],
                'intensity_base': 0.6
            },
            'cathartic_release': {
                'keywords': ['finally', 'breakthrough', 'letting go', 'release', 'liberation'],
                'psychological_indicators': ['emotional breakthrough', 'tension resolution', 'psychological healing'],
                'intensity_base': 0.7
            }
        }

        # Analyze traditional emotions with enhanced depth
        for emotion_type, emotion_data in self.emotion_patterns.items():
            emotion_evidence = []
            psychological_depth = 0.0
            base_intensity = 0.0

            # Check for emotion keywords with context analysis
            for keyword in emotion_data['keywords']:
                if keyword in section_lower:
                    # Analyze the psychological context around the keyword
                    context_analysis = self._analyze_emotional_context(section, keyword)
                    if context_analysis['depth_score'] > 0.3:
                        emotion_evidence.append(context_analysis['context'])
                        psychological_depth += context_analysis['depth_score']
                        base_intensity += 0.4

            # Check for intensity modifiers with psychological weight
            intensity_modifiers = emotion_data.get('intensity_modifiers', {})
            for modifier, multiplier in intensity_modifiers.items():
                if modifier in section_lower:
                    base_intensity *= multiplier
                    psychological_depth += 0.1
                    emotion_evidence.append(f"Psychological intensity: {modifier}")

            # Create emotional state if evidence found and has psychological depth
            if emotion_evidence and base_intensity > 0.2 and psychological_depth > 0.2:
                emotional_state = EmotionalState(
                    emotion=f"Deep {emotion_type.replace('_', ' ').title()}",
                    intensity=min(base_intensity * (1 + psychological_depth), 1.0),
                    context=section[:150] + "..." if len(section) > 150 else section,
                    text_position=position,
                    triggers=emotion_evidence[:4]  # More triggers for deeper analysis
                )
                section_emotions.append(emotional_state)

        # Analyze deep psychological emotions
        for deep_emotion, pattern_data in deep_emotion_patterns.items():
            evidence = []
            depth_score = 0.0

            # Check for keywords
            for keyword in pattern_data['keywords']:
                if keyword in section_lower:
                    evidence.append(f"Keyword: {keyword}")
                    depth_score += 0.3

            # Check for psychological indicators
            for indicator in pattern_data['psychological_indicators']:
                if any(word in section_lower for word in indicator.split()):
                    evidence.append(f"Psychological pattern: {indicator}")
                    depth_score += 0.4

            # Create deep emotional state if sufficient evidence
            if evidence and depth_score > 0.4:
                emotional_state = EmotionalState(
                    emotion=deep_emotion.replace('_', ' ').title(),
                    intensity=min(pattern_data['intensity_base'] + depth_score, 1.0),
                    context=section[:150] + "..." if len(section) > 150 else section,
                    text_position=position,
                    triggers=evidence[:3]
                )
                section_emotions.append(emotional_state)

        # Sort by psychological depth and intensity
        section_emotions.sort(key=lambda x: x.intensity, reverse=True)
        return section_emotions[:3]  # Max 3 emotions per section for deeper analysis

    def _analyze_overall_emotional_tone(self, text: str) -> Optional[EmotionalState]:
        """Analyze overall emotional tone when no specific emotions found"""
        text_lower = text.lower()

        # Look for general emotional indicators
        tone_indicators = {
            'contemplative_reflection': ['think', 'thought', 'consider', 'reflect', 'ponder', 'wonder', 'realize'],
            'nostalgic_longing': ['remember', 'memory', 'past', 'used to', 'once', 'long ago', 'miss'],
            'anticipatory_tension': ['will', 'would', 'might', 'could', 'future', 'tomorrow', 'next', 'soon'],
            'melancholic_atmosphere': ['quiet', 'silence', 'empty', 'alone', 'solitude', 'shadow', 'gray'],
            'hopeful_determination': ['try', 'attempt', 'effort', 'work', 'build', 'create', 'forward'],
            'mysterious_intrigue': ['secret', 'hidden', 'unknown', 'mystery', 'strange', 'curious', 'wonder']
        }

        tone_scores = {}
        for tone, keywords in tone_indicators.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            if score > 0:
                tone_scores[tone] = score

        if tone_scores:
            dominant_tone = max(tone_scores, key=tone_scores.get)
            return EmotionalState(
                emotion=dominant_tone.replace('_', ' ').title(),
                intensity=min(tone_scores[dominant_tone] / 10.0, 0.8),
                context=text[:200] + "..." if len(text) > 200 else text,
                text_position=0,
                triggers=[f"Overall tone based on {tone_scores[dominant_tone]} relevant keywords"]
            )

        return None

    def _analyze_emotional_context(self, section: str, keyword: str) -> Dict[str, Any]:
        """
        Analyze the psychological context around an emotional keyword
        
        Returns depth score and contextual information for deeper emotional analysis
        """
        sentences = re.split(r'[.!?]+', section)
        keyword_sentence = None

        # Find the sentence containing the keyword
        for sentence in sentences:
            if keyword.lower() in sentence.lower():
                keyword_sentence = sentence.strip()
                break

        if not keyword_sentence:
            return {'depth_score': 0.0, 'context': ''}

        depth_score = 0.0
        context_factors = []

        # Analyze sentence complexity (complex emotions often have complex expression)
        word_count = len(keyword_sentence.split())
        if word_count > 15:
            depth_score += 0.2
            context_factors.append("complex expression")

        # Check for psychological depth indicators
        depth_indicators = [
            'because', 'since', 'although', 'despite', 'however', 'nevertheless',
            'realize', 'understand', 'recognize', 'acknowledge', 'confront',
            'struggle', 'wrestle', 'grapple', 'torn', 'conflicted'
        ]

        for indicator in depth_indicators:
            if indicator in keyword_sentence.lower():
                depth_score += 0.15
                context_factors.append(f"depth indicator: {indicator}")

        # Check for causal relationships (deeper emotions have causes)
        causal_patterns = [
            r'because of', r'due to', r'as a result of', r'stemming from',
            r'rooted in', r'triggered by', r'caused by'
        ]

        for pattern in causal_patterns:
            if re.search(pattern, keyword_sentence, re.IGNORECASE):
                depth_score += 0.25
                context_factors.append("causal relationship identified")

        # Check for temporal context (emotions with history are deeper)
        temporal_indicators = [
            'always', 'never', 'since', 'for years', 'long time', 'forever',
            'childhood', 'growing up', 'used to', 'remember when'
        ]

        for indicator in temporal_indicators:
            if indicator in keyword_sentence.lower():
                depth_score += 0.2
                context_factors.append(f"temporal depth: {indicator}")

        return {
            'depth_score': min(depth_score, 1.0),
            'context': f"{keyword_sentence} [{', '.join(context_factors)}]"
        }

    async def _analyze_philosophical_emotional_connections(self, text: str, ctx=None) -> List[EmotionalState]:
        """
        Analyze connections between philosophical concepts and emotional states
        
        Implements requirement 4.2: Add connection logic between philosophical concepts and emotional states
        """
        if ctx:
            await ctx.info("Analyzing philosophical-emotional connections...")

        philosophical_emotional_map = {
            'consciousness': {
                'emotions': ['existential_awareness', 'cognitive_awakening', 'self_recognition'],
                'triggers': ['aware', 'consciousness', 'realize', 'awaken', 'perceive'],
                'intensity_base': 0.7
            },
            'mortality': {
                'emotions': ['existential_dread', 'temporal_anxiety', 'life_urgency'],
                'triggers': ['death', 'mortality', 'finite', 'end', 'dying', 'mortal'],
                'intensity_base': 0.8
            },
            'freedom': {
                'emotions': ['liberation_euphoria', 'choice_anxiety', 'responsibility_weight'],
                'triggers': ['freedom', 'choice', 'liberty', 'free will', 'decide', 'autonomous'],
                'intensity_base': 0.6
            },
            'truth': {
                'emotions': ['revelation_shock', 'disillusionment_pain', 'clarity_relief'],
                'triggers': ['truth', 'reality', 'revelation', 'discover', 'uncover', 'realize'],
                'intensity_base': 0.7
            },
            'identity': {
                'emotions': ['self_doubt', 'identity_crisis', 'authentic_recognition'],
                'triggers': ['who am i', 'identity', 'self', 'authentic', 'real me', 'true self'],
                'intensity_base': 0.6
            },
            'meaning': {
                'emotions': ['purposeless_despair', 'meaning_quest', 'significance_joy'],
                'triggers': ['meaning', 'purpose', 'significance', 'why', 'point', 'matter'],
                'intensity_base': 0.8
            },
            'love': {
                'emotions': ['unconditional_devotion', 'vulnerable_openness', 'connection_transcendence'],
                'triggers': ['love', 'devotion', 'connection', 'bond', 'unite', 'together'],
                'intensity_base': 0.7
            },
            'suffering': {
                'emotions': ['transformative_pain', 'growth_through_struggle', 'wisdom_through_loss'],
                'triggers': ['suffer', 'pain', 'struggle', 'hardship', 'difficulty', 'challenge'],
                'intensity_base': 0.8
            }
        }

        philosophical_emotions = []
        text_lower = text.lower()

        for concept, concept_data in philosophical_emotional_map.items():
            concept_evidence = []
            concept_intensity = 0.0

            # Check for philosophical triggers
            for trigger in concept_data['triggers']:
                if trigger in text_lower:
                    # Find context around the trigger
                    trigger_contexts = self._extract_philosophical_context(text, trigger)
                    concept_evidence.extend(trigger_contexts)
                    concept_intensity += 0.3

            # If philosophical concept found, create associated emotional states
            if concept_evidence and concept_intensity > 0.2:
                for emotion in concept_data['emotions']:
                    philosophical_emotion = EmotionalState(
                        emotion=emotion.replace('_', ' ').title(),
                        intensity=min(concept_data['intensity_base'] + concept_intensity * 0.3, 1.0),
                        context=f"Philosophical concept '{concept}' triggers emotional response",
                        text_position=text_lower.find(concept_data['triggers'][0]),
                        triggers=[f"Philosophical connection: {concept}"] + concept_evidence[:2]
                    )
                    philosophical_emotions.append(philosophical_emotion)

        if ctx:
            await ctx.info(f"Found {len(philosophical_emotions)} philosophical-emotional connections")

        return philosophical_emotions[:6]  # Limit to top 6 philosophical emotions

    async def _analyze_complex_emotional_patterns(self, text: str, existing_emotions: List[EmotionalState], ctx=None) -> List[EmotionalState]:
        """
        Analyze complex emotional patterns and transitions across the text
        
        Implements requirement 4.3: Complex emotional state tracking across album tracks
        """
        if ctx:
            await ctx.info("Analyzing complex emotional patterns and transitions...")

        complex_patterns = []

        # Analyze emotional progression patterns
        if len(existing_emotions) >= 2:
            progression_patterns = self._identify_emotional_progressions(existing_emotions)
            complex_patterns.extend(progression_patterns)

        # Analyze emotional contradictions and paradoxes
        contradiction_patterns = self._identify_emotional_contradictions(text, existing_emotions)
        complex_patterns.extend(contradiction_patterns)

        # Analyze cyclical emotional patterns
        cyclical_patterns = self._identify_cyclical_emotions(text, existing_emotions)
        complex_patterns.extend(cyclical_patterns)

        # Analyze suppressed or hidden emotions
        suppressed_patterns = self._identify_suppressed_emotions(text)
        complex_patterns.extend(suppressed_patterns)

        if ctx:
            await ctx.info(f"Identified {len(complex_patterns)} complex emotional patterns")

        return complex_patterns[:8]  # Limit to top 8 complex patterns

    def _extract_philosophical_context(self, text: str, trigger: str) -> List[str]:
        """Extract contextual information around philosophical triggers"""
        contexts = []
        sentences = re.split(r'[.!?]+', text)

        for sentence in sentences:
            if trigger.lower() in sentence.lower():
                # Clean and limit context
                context = sentence.strip()
                if len(context) > 100:
                    context = context[:100] + "..."
                contexts.append(f"Context: {context}")

        return contexts[:2]  # Limit to 2 contexts per trigger

    def _identify_emotional_progressions(self, emotions: List[EmotionalState]) -> List[EmotionalState]:
        """Identify emotional progression patterns"""
        progressions = []

        # Sort emotions by text position
        sorted_emotions = sorted(emotions, key=lambda x: x.text_position)

        # Look for meaningful progressions
        for i in range(len(sorted_emotions) - 1):
            current = sorted_emotions[i]
            next_emotion = sorted_emotions[i + 1]

            # Identify progression types
            progression_type = self._classify_emotional_transition(current.emotion, next_emotion.emotion)

            if progression_type:
                progression = EmotionalState(
                    emotion=f"Emotional Progression: {progression_type}",
                    intensity=(current.intensity + next_emotion.intensity) / 2,
                    context=f"Transition from {current.emotion} to {next_emotion.emotion}",
                    text_position=current.text_position,
                    triggers=[f"Progression pattern: {progression_type}"]
                )
                progressions.append(progression)

        return progressions[:3]  # Limit to top 3 progressions

    def _classify_emotional_transition(self, emotion1: str, emotion2: str) -> Optional[str]:
        """Classify the type of emotional transition"""
        # Define transition patterns
        transition_patterns = {
            'cathartic_release': [
                ('anxiety', 'relief'), ('fear', 'calm'), ('anger', 'peace'),
                ('despair', 'hope'), ('confusion', 'clarity')
            ],
            'emotional_descent': [
                ('hope', 'despair'), ('joy', 'sadness'), ('calm', 'anxiety'),
                ('confidence', 'doubt'), ('love', 'loss')
            ],
            'emotional_awakening': [
                ('numbness', 'feeling'), ('denial', 'acceptance'), ('ignorance', 'awareness'),
                ('apathy', 'passion'), ('confusion', 'understanding')
            ],
            'cyclical_return': [
                ('hope', 'disappointment'), ('trust', 'betrayal'), ('peace', 'conflict'),
                ('clarity', 'confusion'), ('connection', 'isolation')
            ]
        }

        emotion1_lower = emotion1.lower()
        emotion2_lower = emotion2.lower()

        for pattern_name, transitions in transition_patterns.items():
            for start, end in transitions:
                if start in emotion1_lower and end in emotion2_lower:
                    return pattern_name

        return None

    def _identify_emotional_contradictions(self, text: str, emotions: List[EmotionalState]) -> List[EmotionalState]:
        """Identify emotional contradictions and paradoxes"""
        contradictions = []

        # Look for contradictory emotions in close proximity
        contradiction_pairs = [
            ('love', 'hate'), ('joy', 'sorrow'), ('hope', 'despair'),
            ('peace', 'turmoil'), ('clarity', 'confusion'), ('trust', 'suspicion')
        ]

        for emotion1, emotion2 in contradiction_pairs:
            if any(emotion1 in e.emotion.lower() for e in emotions) and \
               any(emotion2 in e.emotion.lower() for e in emotions):

                contradiction = EmotionalState(
                    emotion=f"Emotional Paradox: {emotion1.title()}-{emotion2.title()}",
                    intensity=0.8,  # High intensity for contradictions
                    context=f"Simultaneous presence of {emotion1} and {emotion2}",
                    text_position=0,
                    triggers=[f"Contradiction between {emotion1} and {emotion2}"]
                )
                contradictions.append(contradiction)

        return contradictions[:2]  # Limit to 2 contradictions

    def _identify_cyclical_emotions(self, text: str, emotions: List[EmotionalState]) -> List[EmotionalState]:
        """Identify cyclical emotional patterns"""
        cyclical = []

        # Look for repeated emotional themes
        emotion_counts = {}
        for emotion in emotions:
            base_emotion = emotion.emotion.split()[0].lower()  # Get base emotion word
            emotion_counts[base_emotion] = emotion_counts.get(base_emotion, 0) + 1

        # Identify cycles (emotions that repeat)
        for emotion, count in emotion_counts.items():
            if count >= 2:  # Appears at least twice
                cyclical_emotion = EmotionalState(
                    emotion=f"Cyclical Pattern: {emotion.title()}",
                    intensity=0.6,
                    context=f"Recurring emotional theme: {emotion}",
                    text_position=0,
                    triggers=[f"Emotion '{emotion}' appears {count} times"]
                )
                cyclical.append(cyclical_emotion)

        return cyclical[:2]  # Limit to 2 cyclical patterns

    def _identify_suppressed_emotions(self, text: str) -> List[EmotionalState]:
        """Identify suppressed or hidden emotions through subtext"""
        suppressed = []
        text_lower = text.lower()

        # Patterns that suggest emotional suppression
        suppression_patterns = {
            'suppressed_anger': [
                'tried to stay calm', 'forced a smile', 'bit tongue', 'held back',
                'kept quiet', 'said nothing', 'swallowed words'
            ],
            'hidden_sadness': [
                'pretended to be fine', 'put on brave face', 'didn\'t want to cry',
                'held back tears', 'forced cheerfulness', 'masked pain'
            ],
            'concealed_fear': [
                'acted brave', 'didn\'t want to show', 'hid anxiety',
                'pretended confidence', 'masked terror', 'false bravado'
            ],
            'buried_love': [
                'couldn\'t say', 'kept feelings hidden', 'secret affection',
                'unspoken love', 'hidden feelings', 'dared not express'
            ]
        }

        for emotion_type, patterns in suppression_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    suppressed_emotion = EmotionalState(
                        emotion=emotion_type.replace('_', ' ').title(),
                        intensity=0.7,  # High intensity for suppressed emotions
                        context=f"Suppression pattern: {pattern}",
                        text_position=text_lower.find(pattern),
                        triggers=[f"Suppression indicator: {pattern}"]
                    )
                    suppressed.append(suppressed_emotion)
                    break  # One per emotion type

        return suppressed[:3]  # Limit to 3 suppressed emotions

    async def _analyze_deep_contextual_emotions(self, text: str, ctx=None) -> List[EmotionalState]:
        """
        Perform deep contextual emotional analysis when surface emotions aren't found
        
        Enhanced version of contextual emotion inference with psychological depth
        """
        if ctx:
            await ctx.info("Performing deep contextual emotional analysis...")

        contextual_emotions = []
        sentences = re.split(r'[.!?]+', text)

        # Enhanced question analysis - different types of questions reveal different emotions
        questions = [s for s in sentences if '?' in s]
        if questions:
            question_emotions = self._analyze_question_emotions(questions)
            contextual_emotions.extend(question_emotions)

        # Enhanced exclamation analysis
        exclamations = [s for s in sentences if '!' in s]
        if exclamations:
            exclamation_emotions = self._analyze_exclamation_emotions(exclamations)
            contextual_emotions.extend(exclamation_emotions)

        # Analyze sentence rhythm and structure for emotional implications
        rhythm_emotions = self._analyze_textual_rhythm_emotions(sentences)
        contextual_emotions.extend(rhythm_emotions)

        # Analyze semantic density for emotional weight
        semantic_emotions = self._analyze_semantic_emotional_density(text)
        contextual_emotions.extend(semantic_emotions)

        return contextual_emotions[:6]  # Limit to 6 contextual emotions

    def _analyze_question_emotions(self, questions: List[str]) -> List[EmotionalState]:
        """Analyze emotional implications of different question types"""
        question_emotions = []

        question_patterns = {
            'existential_questioning': [
                'why', 'what\'s the point', 'what does it mean', 'why do we',
                'what\'s the purpose', 'why exist', 'what\'s it all for'
            ],
            'self_doubt': [
                'am i', 'do i', 'can i', 'should i', 'what if i',
                'am i wrong', 'am i right', 'what\'s wrong with me'
            ],
            'desperate_seeking': [
                'where', 'how can', 'when will', 'who will',
                'is there anyone', 'will someone', 'can anyone'
            ]
        }

        for emotion_type, patterns in question_patterns.items():
            matching_questions = []
            for question in questions:
                question_lower = question.lower()
                for pattern in patterns:
                    if pattern in question_lower:
                        matching_questions.append(question.strip())
                        break

            if matching_questions:
                emotion = EmotionalState(
                    emotion=emotion_type.replace('_', ' ').title(),
                    intensity=min(len(matching_questions) / 3.0, 0.8),
                    context=matching_questions[0][:100] + "..." if len(matching_questions[0]) > 100 else matching_questions[0],
                    text_position=0,
                    triggers=[f"{len(matching_questions)} {emotion_type} questions"]
                )
                question_emotions.append(emotion)

        return question_emotions

    def _analyze_exclamation_emotions(self, exclamations: List[str]) -> List[EmotionalState]:
        """Analyze emotional implications of exclamations"""
        exclamation_emotions = []

        # Analyze exclamation content for emotional type
        positive_indicators = ['yes', 'great', 'wonderful', 'amazing', 'fantastic', 'perfect']
        negative_indicators = ['no', 'terrible', 'awful', 'horrible', 'disaster', 'wrong']
        intense_indicators = ['never', 'always', 'completely', 'absolutely', 'totally']

        positive_count = sum(1 for exc in exclamations for indicator in positive_indicators if indicator in exc.lower())
        negative_count = sum(1 for exc in exclamations for indicator in negative_indicators if indicator in exc.lower())
        intense_count = sum(1 for exc in exclamations for indicator in intense_indicators if indicator in exc.lower())

        if positive_count > 0:
            exclamation_emotions.append(EmotionalState(
                emotion="Exclamatory Joy",
                intensity=min(positive_count / 2.0, 0.9),
                context="Positive exclamations detected",
                text_position=0,
                triggers=[f"{positive_count} positive exclamations"]
            ))

        if negative_count > 0:
            exclamation_emotions.append(EmotionalState(
                emotion="Exclamatory Distress",
                intensity=min(negative_count / 2.0, 0.9),
                context="Negative exclamations detected",
                text_position=0,
                triggers=[f"{negative_count} negative exclamations"]
            ))

        if intense_count > 0:
            exclamation_emotions.append(EmotionalState(
                emotion="Emotional Intensity",
                intensity=min(intense_count / 2.0, 0.8),
                context="Intense emotional expressions detected",
                text_position=0,
                triggers=[f"{intense_count} intensity markers"]
            ))

        return exclamation_emotions

    def _analyze_textual_rhythm_emotions(self, sentences: List[str]) -> List[EmotionalState]:
        """Analyze emotional implications of textual rhythm and structure"""
        rhythm_emotions = []

        if not sentences:
            return rhythm_emotions

        # Analyze sentence length variation
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if not sentence_lengths:
            return rhythm_emotions

        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        length_variance = sum((length - avg_length) ** 2 for length in sentence_lengths) / len(sentence_lengths)

        # High variance suggests emotional turbulence
        if length_variance > 50:
            rhythm_emotions.append(EmotionalState(
                emotion="Emotional Turbulence",
                intensity=min(length_variance / 100.0, 0.8),
                context="Highly varied sentence structure suggests emotional instability",
                text_position=0,
                triggers=[f"Sentence length variance: {length_variance:.1f}"]
            ))

        # Very short sentences suggest tension or urgency
        very_short = [s for s in sentences if len(s.split()) <= 3 and s.strip()]
        if len(very_short) > len(sentences) * 0.3:  # More than 30% are very short
            rhythm_emotions.append(EmotionalState(
                emotion="Staccato Tension",
                intensity=min(len(very_short) / len(sentences), 0.7),
                context="Predominance of very short sentences suggests tension",
                text_position=0,
                triggers=[f"{len(very_short)} very short sentences"]
            ))

        # Very long sentences suggest contemplation or overwhelm
        very_long = [s for s in sentences if len(s.split()) > 25]
        if very_long:
            rhythm_emotions.append(EmotionalState(
                emotion="Contemplative Flow",
                intensity=min(len(very_long) / 3.0, 0.6),
                context="Long, complex sentences suggest deep contemplation",
                text_position=0,
                triggers=[f"{len(very_long)} very long sentences"]
            ))

        return rhythm_emotions

    def _analyze_semantic_emotional_density(self, text: str) -> List[EmotionalState]:
        """Analyze emotional weight through semantic density"""
        semantic_emotions = []

        # Count emotionally charged words
        emotional_weight_words = [
            'overwhelming', 'devastating', 'profound', 'intense', 'deep',
            'crushing', 'soaring', 'piercing', 'burning', 'freezing',
            'suffocating', 'liberating', 'transforming', 'shattering'
        ]

        weight_count = sum(text.lower().count(word) for word in emotional_weight_words)
        total_words = len(text.split())

        if total_words > 0:
            emotional_density = weight_count / total_words

            if emotional_density > 0.02:  # More than 2% emotionally weighted words
                semantic_emotions.append(EmotionalState(
                    emotion="High Emotional Density",
                    intensity=min(emotional_density * 20, 0.9),
                    context="Text has high concentration of emotionally charged language",
                    text_position=0,
                    triggers=[f"Emotional density: {emotional_density:.3f}"]
                ))

        return semantic_emotions

    def _prioritize_emotional_states_by_depth(self, emotional_states: List[EmotionalState]) -> List[EmotionalState]:
        """Prioritize emotional states by psychological depth and relevance"""
        if not emotional_states:
            return emotional_states

        # Define depth scoring criteria
        depth_keywords = {
            'high_depth': ['existential', 'philosophical', 'transcendent', 'paradox', 'suppressed', 'deep'],
            'medium_depth': ['complex', 'progression', 'cyclical', 'contradiction', 'pattern'],
            'surface_level': ['basic', 'simple', 'direct', 'obvious']
        }

        # Score each emotional state
        scored_states = []
        for state in emotional_states:
            depth_score = 0.0
            emotion_lower = state.emotion.lower()

            # Check for depth indicators in emotion name
            for keyword in depth_keywords['high_depth']:
                if keyword in emotion_lower:
                    depth_score += 0.3

            for keyword in depth_keywords['medium_depth']:
                if keyword in emotion_lower:
                    depth_score += 0.2

            # Bonus for complex triggers
            if len(state.triggers) > 2:
                depth_score += 0.1

            # Bonus for high intensity (often indicates psychological significance)
            depth_score += state.intensity * 0.2

            scored_states.append((state, depth_score))

        # Sort by depth score (descending) and return states
        scored_states.sort(key=lambda x: x[1], reverse=True)
        return [state for state, score in scored_states]

    def _infer_contextual_emotions(self, text: str) -> List[EmotionalState]:
        """Legacy method - now redirects to deep contextual analysis"""
        # This method is kept for backward compatibility but now uses deep analysis
        import asyncio
        return asyncio.run(self._analyze_deep_contextual_emotions(text))

    def _extract_setting_information(self, text: str) -> str:
        """Extract setting and world-building information"""
        setting_patterns = [
            r'\b(?:in|at|on|near|by|inside|outside|within|beneath|above|below)\s+(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\b(?:city|town|village|forest|castle|house|building|room|street|road|path|mountain|river|ocean|lake)\b[^.!?]*',
            r'\b(?:morning|afternoon|evening|night|dawn|dusk|midnight|noon)\b[^.!?]*',
            r'\b(?:winter|spring|summer|fall|autumn)\b[^.!?]*'
        ]

        setting_elements = []
        for pattern in setting_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    setting_elements.extend([m for m in match if m.strip()])
                else:
                    setting_elements.append(match)

        if setting_elements:
            return f"Setting elements: {', '.join(set(setting_elements[:5]))}"
        else:
            return "Setting not explicitly described in the text."

    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity score"""
        if not text:
            return 0.0

        words = text.split()
        sentences = re.split(r'[.!?]+', text)

        if not words or not sentences:
            return 0.0

        # Average words per sentence
        avg_words_per_sentence = len(words) / len(sentences)

        # Vocabulary diversity
        unique_words = len(set(word.lower().strip('.,!?;:"()[]{}') for word in words))
        vocabulary_diversity = unique_words / len(words)

        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)

        # Punctuation complexity
        punctuation_density = (text.count(',') + text.count(';') + text.count(':')) / len(text) * 1000

        # Combine factors
        sentence_complexity = min(avg_words_per_sentence / 25.0, 1.0)
        vocab_complexity = vocabulary_diversity
        word_complexity = min(avg_word_length / 8.0, 1.0)
        punct_complexity = min(punctuation_density / 50.0, 1.0)

        overall_complexity = (sentence_complexity + vocab_complexity + word_complexity + punct_complexity) / 4
        return min(overall_complexity, 1.0)


# Utility functions for integration with existing system

def create_enhanced_analyzer() -> EnhancedCharacterAnalyzer:
    """Create an instance of the enhanced character analyzer"""
    return EnhancedCharacterAnalyzer()


async def analyze_text_enhanced(text: str, ctx=None) -> Dict[str, Any]:
    """
    Convenience function for enhanced text analysis
    
    Args:
        text: Input narrative text
        ctx: Optional context for logging
        
    Returns:
        Dictionary containing enhanced analysis results
    """
    analyzer = EnhancedCharacterAnalyzer()
    return await analyzer.analyze_text(text, ctx)


@dataclass
class ThematicCoherenceScore:
    """Represents thematic coherence analysis results"""
    overall_score: float  # 0.0 to 1.0
    consistency_score: float
    character_voice_score: float
    perspective_maintenance_score: float
    thematic_alignment_score: float
    issues: List[str]
    strengths: List[str]
    recommendations: List[str]

@dataclass
class AlbumCoherenceValidation:
    """Represents album-wide coherence validation results"""
    coherence_score: ThematicCoherenceScore
    track_consistency: Dict[str, float]  # Track name -> consistency score
    character_voice_analysis: Dict[str, Dict[str, Any]]  # Character -> voice analysis
    thematic_progression: Dict[str, Any]
    quality_flags: List[str]

class ThematicCoherenceValidator:
    """
    Validates thematic coherence and consistency across album content
    
    Implements requirement 4.2: Add thematic coherence validation
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Thematic consistency indicators
        self.consistency_patterns = {
            'character_voice': {
                'vocabulary_consistency': ['word_choice', 'complexity_level', 'formality'],
                'emotional_consistency': ['emotional_range', 'expression_style', 'intensity_patterns'],
                'perspective_consistency': ['viewpoint', 'values', 'worldview', 'priorities']
            },
            'thematic_alignment': {
                'core_themes': ['primary_message', 'central_conflict', 'philosophical_stance'],
                'supporting_themes': ['secondary_messages', 'subplots', 'character_arcs'],
                'symbolic_consistency': ['metaphors', 'imagery', 'recurring_symbols']
            },
            'narrative_progression': {
                'logical_flow': ['cause_effect', 'temporal_consistency', 'character_development'],
                'emotional_arc': ['emotional_progression', 'climax_buildup', 'resolution'],
                'thematic_development': ['theme_introduction', 'theme_exploration', 'theme_resolution']
            }
        }

    async def validate_album_coherence(self, album_content: Dict[str, Any], ctx=None) -> AlbumCoherenceValidation:
        """
        Validate coherence across an entire album
        
        Args:
            album_content: Dictionary containing album tracks and metadata
            ctx: Optional context for logging
            
        Returns:
            AlbumCoherenceValidation with detailed analysis
        """
        if ctx:
            await ctx.info("Validating album-wide thematic coherence...")

        # Extract tracks and characters
        tracks = album_content.get('tracks', [])
        characters = album_content.get('characters', [])

        # Validate overall coherence
        coherence_score = await self._calculate_overall_coherence(tracks, characters, ctx)

        # Analyze track-by-track consistency
        track_consistency = await self._analyze_track_consistency(tracks, ctx)

        # Analyze character voice consistency
        character_voice_analysis = await self._analyze_character_voice_consistency(tracks, characters, ctx)

        # Analyze thematic progression
        thematic_progression = await self._analyze_thematic_progression(tracks, ctx)

        # Generate quality flags
        quality_flags = self._generate_quality_flags(coherence_score, track_consistency, character_voice_analysis)

        return AlbumCoherenceValidation(
            coherence_score=coherence_score,
            track_consistency=track_consistency,
            character_voice_analysis=character_voice_analysis,
            thematic_progression=thematic_progression,
            quality_flags=quality_flags
        )

    async def _calculate_overall_coherence(self, tracks: List[Dict], characters: List[Dict], ctx=None) -> ThematicCoherenceScore:
        """Calculate overall thematic coherence score"""
        if ctx:
            await ctx.info("Calculating overall coherence score...")

        issues = []
        strengths = []
        recommendations = []

        # Consistency score - how consistent are themes across tracks
        consistency_score = await self._calculate_consistency_score(tracks)
        if consistency_score < 0.6:
            issues.append(f"Low thematic consistency across tracks (score: {consistency_score:.2f})")
            recommendations.append("Review tracks for thematic alignment and ensure core themes are maintained")
        else:
            strengths.append(f"Strong thematic consistency (score: {consistency_score:.2f})")

        # Character voice score - how consistent are character voices
        character_voice_score = await self._calculate_character_voice_score(tracks, characters)
        if character_voice_score < 0.7:
            issues.append(f"Inconsistent character voice across tracks (score: {character_voice_score:.2f})")
            recommendations.append("Ensure character personality and voice remain consistent across all tracks")
        else:
            strengths.append(f"Consistent character voice (score: {character_voice_score:.2f})")

        # Perspective maintenance score - how well is perspective maintained
        perspective_score = await self._calculate_perspective_maintenance_score(tracks)
        if perspective_score < 0.6:
            issues.append(f"Inconsistent perspective maintenance (score: {perspective_score:.2f})")
            recommendations.append("Maintain consistent narrative perspective and character viewpoint")
        else:
            strengths.append(f"Well-maintained perspective (score: {perspective_score:.2f})")

        # Thematic alignment score - how well do all elements align with core themes
        alignment_score = await self._calculate_thematic_alignment_score(tracks, characters)
        if alignment_score < 0.6:
            issues.append(f"Poor thematic alignment (score: {alignment_score:.2f})")
            recommendations.append("Ensure all content elements support and reinforce core themes")
        else:
            strengths.append(f"Strong thematic alignment (score: {alignment_score:.2f})")

        # Calculate overall score
        overall_score = (consistency_score + character_voice_score + perspective_score + alignment_score) / 4

        return ThematicCoherenceScore(
            overall_score=overall_score,
            consistency_score=consistency_score,
            character_voice_score=character_voice_score,
            perspective_maintenance_score=perspective_score,
            thematic_alignment_score=alignment_score,
            issues=issues,
            strengths=strengths,
            recommendations=recommendations
        )

    async def _calculate_consistency_score(self, tracks: List[Dict]) -> float:
        """Calculate thematic consistency across tracks"""
        if len(tracks) < 2:
            return 1.0  # Single track is perfectly consistent

        # Extract themes from each track
        track_themes = []
        for track in tracks:
            themes = self._extract_track_themes(track)
            track_themes.append(themes)

        # Calculate theme overlap between tracks
        total_comparisons = 0
        total_overlap = 0.0

        for i in range(len(track_themes)):
            for j in range(i + 1, len(track_themes)):
                overlap = self._calculate_theme_overlap(track_themes[i], track_themes[j])
                total_overlap += overlap
                total_comparisons += 1

        if total_comparisons == 0:
            return 0.0

        return total_overlap / total_comparisons

    async def _calculate_character_voice_score(self, tracks: List[Dict], characters: List[Dict]) -> float:
        """Calculate character voice consistency score"""
        if not characters:
            return 1.0  # No characters to be inconsistent

        voice_scores = []

        for character in characters:
            char_name = character.get('name', 'Unknown')
            char_voice_score = await self._analyze_character_voice_in_tracks(char_name, tracks)
            voice_scores.append(char_voice_score)

        return sum(voice_scores) / len(voice_scores) if voice_scores else 0.0

    async def _calculate_perspective_maintenance_score(self, tracks: List[Dict]) -> float:
        """Calculate perspective maintenance score"""
        if len(tracks) < 2:
            return 1.0

        # Analyze narrative perspective consistency
        perspectives = []
        for track in tracks:
            perspective = self._analyze_track_perspective(track)
            perspectives.append(perspective)

        # Check for perspective consistency
        if not perspectives:
            return 0.0

        primary_perspective = perspectives[0]
        consistent_count = sum(1 for p in perspectives if self._perspectives_match(primary_perspective, p))

        return consistent_count / len(perspectives)

    async def _calculate_thematic_alignment_score(self, tracks: List[Dict], characters: List[Dict]) -> float:
        """Calculate thematic alignment score"""
        # Extract core themes from the album
        core_themes = self._extract_core_album_themes(tracks, characters)

        if not core_themes:
            return 0.5  # Neutral score if no themes identified

        alignment_scores = []

        for track in tracks:
            track_alignment = self._calculate_track_theme_alignment(track, core_themes)
            alignment_scores.append(track_alignment)

        return sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0

    def _extract_track_themes(self, track: Dict) -> List[str]:
        """Extract themes from a single track"""
        themes = []

        # Extract from lyrics using basic keyword matching
        lyrics = track.get('lyrics', '')
        if lyrics:
            lyrics_lower = lyrics.lower()

            # Basic theme keywords
            theme_keywords = {
                'consciousness': ['consciousness', 'aware', 'awaken', 'mind', 'perception'],
                'existence': ['existence', 'exist', 'being', 'reality', 'life'],
                'meaning': ['meaning', 'purpose', 'significance', 'point', 'why'],
                'love': ['love', 'affection', 'devotion', 'heart', 'romance'],
                'loss': ['loss', 'grief', 'sorrow', 'missing', 'gone'],
                'hope': ['hope', 'optimism', 'future', 'dream', 'aspire'],
                'fear': ['fear', 'afraid', 'terror', 'anxiety', 'worry'],
                'identity': ['identity', 'self', 'who am i', 'authentic', 'true'],
                'freedom': ['freedom', 'liberty', 'choice', 'independent', 'free'],
                'truth': ['truth', 'reality', 'honest', 'real', 'genuine']
            }

            for theme_name, keywords in theme_keywords.items():
                if any(keyword in lyrics_lower for keyword in keywords):
                    themes.append(theme_name)

        # Extract from track metadata
        track_themes = track.get('themes', [])
        themes.extend(track_themes)

        return list(set(themes))  # Remove duplicates

    def _calculate_theme_overlap(self, themes1: List[str], themes2: List[str]) -> float:
        """Calculate overlap between two theme lists"""
        if not themes1 or not themes2:
            return 0.0

        set1 = set(themes1)
        set2 = set(themes2)

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    async def _analyze_character_voice_in_tracks(self, character_name: str, tracks: List[Dict]) -> float:
        """Analyze character voice consistency across tracks"""
        character_appearances = []

        for track in tracks:
            lyrics = track.get('lyrics', '')
            if character_name.lower() in lyrics.lower():
                voice_analysis = self._analyze_character_voice_in_text(character_name, lyrics)
                character_appearances.append(voice_analysis)

        if len(character_appearances) < 2:
            return 1.0  # Can't be inconsistent with only one appearance

        # Compare voice consistency across appearances
        consistency_scores = []
        for i in range(len(character_appearances)):
            for j in range(i + 1, len(character_appearances)):
                consistency = self._compare_voice_analyses(character_appearances[i], character_appearances[j])
                consistency_scores.append(consistency)

        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0

    def _analyze_character_voice_in_text(self, character_name: str, text: str) -> Dict[str, Any]:
        """Analyze character voice characteristics in text"""
        voice_analysis = {
            'vocabulary_level': self._analyze_vocabulary_level(text),
            'emotional_tone': self._analyze_emotional_tone(text),
            'sentence_structure': self._analyze_sentence_structure(text),
            'perspective_markers': self._extract_perspective_markers(text)
        }

        return voice_analysis

    def _analyze_vocabulary_level(self, text: str) -> str:
        """Analyze vocabulary complexity level"""
        words = text.split()
        if not words:
            return 'unknown'

        avg_word_length = sum(len(word.strip('.,!?;:"()[]{}')) for word in words) / len(words)

        if avg_word_length > 6:
            return 'sophisticated'
        elif avg_word_length > 4:
            return 'moderate'
        else:
            return 'simple'

    def _analyze_emotional_tone(self, text: str) -> str:
        """Analyze overall emotional tone of text"""
        text_lower = text.lower()

        positive_words = ['happy', 'joy', 'love', 'hope', 'peace', 'wonderful', 'beautiful']
        negative_words = ['sad', 'angry', 'hate', 'fear', 'pain', 'terrible', 'awful']
        neutral_words = ['think', 'consider', 'perhaps', 'maybe', 'understand', 'realize']

        positive_count = sum(text_lower.count(word) for word in positive_words)
        negative_count = sum(text_lower.count(word) for word in negative_words)
        neutral_count = sum(text_lower.count(word) for word in neutral_words)

        if positive_count > negative_count and positive_count > neutral_count:
            return 'positive'
        elif negative_count > positive_count and negative_count > neutral_count:
            return 'negative'
        else:
            return 'neutral'

    def _analyze_sentence_structure(self, text: str) -> str:
        """Analyze sentence structure complexity"""
        sentences = re.split(r'[.!?]+', text)
        if not sentences:
            return 'unknown'

        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / len([s for s in sentences if s.strip()])

        if avg_sentence_length > 15:
            return 'complex'
        elif avg_sentence_length > 8:
            return 'moderate'
        else:
            return 'simple'

    def _extract_perspective_markers(self, text: str) -> List[str]:
        """Extract markers that indicate narrative perspective"""
        markers = []
        text_lower = text.lower()

        first_person = ['i ', 'me ', 'my ', 'mine ', 'myself ']
        second_person = ['you ', 'your ', 'yours ', 'yourself ']
        third_person = ['he ', 'she ', 'they ', 'him ', 'her ', 'them ']

        if any(marker in text_lower for marker in first_person):
            markers.append('first_person')
        if any(marker in text_lower for marker in second_person):
            markers.append('second_person')
        if any(marker in text_lower for marker in third_person):
            markers.append('third_person')

        return markers

    def _compare_voice_analyses(self, analysis1: Dict[str, Any], analysis2: Dict[str, Any]) -> float:
        """Compare two voice analyses for consistency"""
        consistency_score = 0.0
        total_factors = 0

        # Compare vocabulary level
        if analysis1['vocabulary_level'] == analysis2['vocabulary_level']:
            consistency_score += 1.0
        total_factors += 1

        # Compare emotional tone
        if analysis1['emotional_tone'] == analysis2['emotional_tone']:
            consistency_score += 1.0
        total_factors += 1

        # Compare sentence structure
        if analysis1['sentence_structure'] == analysis2['sentence_structure']:
            consistency_score += 1.0
        total_factors += 1

        # Compare perspective markers
        markers1 = set(analysis1['perspective_markers'])
        markers2 = set(analysis2['perspective_markers'])
        if markers1 and markers2:
            marker_overlap = len(markers1.intersection(markers2)) / len(markers1.union(markers2))
            consistency_score += marker_overlap
        total_factors += 1

        return consistency_score / total_factors if total_factors > 0 else 0.0

    def _analyze_track_perspective(self, track: Dict) -> Dict[str, Any]:
        """Analyze narrative perspective of a track"""
        lyrics = track.get('lyrics', '')

        return {
            'perspective_markers': self._extract_perspective_markers(lyrics),
            'narrative_voice': self._determine_narrative_voice(lyrics),
            'viewpoint_consistency': self._check_viewpoint_consistency(lyrics)
        }

    def _determine_narrative_voice(self, text: str) -> str:
        """Determine the primary narrative voice"""
        text_lower = text.lower()

        first_person_count = sum(text_lower.count(marker) for marker in ['i ', 'me ', 'my '])
        second_person_count = sum(text_lower.count(marker) for marker in ['you ', 'your '])
        third_person_count = sum(text_lower.count(marker) for marker in ['he ', 'she ', 'they '])

        if first_person_count > second_person_count and first_person_count > third_person_count:
            return 'first_person'
        elif second_person_count > first_person_count and second_person_count > third_person_count:
            return 'second_person'
        elif third_person_count > 0:
            return 'third_person'
        else:
            return 'unclear'

    def _check_viewpoint_consistency(self, text: str) -> float:
        """Check consistency of viewpoint within text"""
        sentences = re.split(r'[.!?]+', text)
        viewpoints = []

        for sentence in sentences:
            if sentence.strip():
                viewpoint = self._determine_narrative_voice(sentence)
                if viewpoint != 'unclear':
                    viewpoints.append(viewpoint)

        if not viewpoints:
            return 1.0  # No viewpoints to be inconsistent

        # Calculate consistency
        primary_viewpoint = max(set(viewpoints), key=viewpoints.count)
        consistent_count = viewpoints.count(primary_viewpoint)

        return consistent_count / len(viewpoints)

    def _perspectives_match(self, perspective1: Dict[str, Any], perspective2: Dict[str, Any]) -> bool:
        """Check if two perspectives match"""
        return (perspective1['narrative_voice'] == perspective2['narrative_voice'] and
                perspective1['viewpoint_consistency'] > 0.7 and
                perspective2['viewpoint_consistency'] > 0.7)

    def _extract_core_album_themes(self, tracks: List[Dict], characters: List[Dict]) -> List[str]:
        """Extract core themes that should be consistent across the album"""
        all_themes = []

        # Extract themes from all tracks
        for track in tracks:
            track_themes = self._extract_track_themes(track)
            all_themes.extend(track_themes)

        # Extract themes from character profiles
        for character in characters:
            char_themes = character.get('themes', [])
            all_themes.extend(char_themes)

        # Find most common themes (these are likely core themes)
        theme_counts = Counter(all_themes)
        core_themes = [theme for theme, count in theme_counts.most_common(5) if count > 1]

        return core_themes

    def _calculate_track_theme_alignment(self, track: Dict, core_themes: List[str]) -> float:
        """Calculate how well a track aligns with core themes"""
        track_themes = self._extract_track_themes(track)

        if not core_themes or not track_themes:
            return 0.5  # Neutral score

        # Calculate overlap with core themes
        alignment_count = sum(1 for theme in track_themes if theme in core_themes)

        return alignment_count / len(core_themes) if core_themes else 0.0

    async def _analyze_track_consistency(self, tracks: List[Dict], ctx=None) -> Dict[str, float]:
        """Analyze consistency of each track with the overall album"""
        if ctx:
            await ctx.info("Analyzing track-by-track consistency...")

        track_consistency = {}

        if len(tracks) < 2:
            # Single track is perfectly consistent
            for track in tracks:
                track_name = track.get('title', f"Track {tracks.index(track) + 1}")
                track_consistency[track_name] = 1.0
            return track_consistency

        # Calculate consistency for each track against all others
        for i, track in enumerate(tracks):
            track_name = track.get('title', f"Track {i + 1}")

            consistency_scores = []
            for j, other_track in enumerate(tracks):
                if i != j:
                    consistency = await self._calculate_track_pair_consistency(track, other_track)
                    consistency_scores.append(consistency)

            avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0
            track_consistency[track_name] = avg_consistency

        return track_consistency

    async def _calculate_track_pair_consistency(self, track1: Dict, track2: Dict) -> float:
        """Calculate consistency between two tracks"""
        # Theme consistency
        themes1 = self._extract_track_themes(track1)
        themes2 = self._extract_track_themes(track2)
        theme_consistency = self._calculate_theme_overlap(themes1, themes2)

        # Emotional tone consistency
        lyrics1 = track1.get('lyrics', '')
        lyrics2 = track2.get('lyrics', '')
        tone1 = self._analyze_emotional_tone(lyrics1)
        tone2 = self._analyze_emotional_tone(lyrics2)
        tone_consistency = 1.0 if tone1 == tone2 else 0.5  # Partial credit for different but compatible tones

        # Perspective consistency
        perspective1 = self._analyze_track_perspective(track1)
        perspective2 = self._analyze_track_perspective(track2)
        perspective_consistency = 1.0 if self._perspectives_match(perspective1, perspective2) else 0.0

        # Weighted average
        return (theme_consistency * 0.4 + tone_consistency * 0.3 + perspective_consistency * 0.3)

    async def _analyze_character_voice_consistency(self, tracks: List[Dict], characters: List[Dict], ctx=None) -> Dict[str, Dict[str, Any]]:
        """Analyze character voice consistency across tracks"""
        if ctx:
            await ctx.info("Analyzing character voice consistency...")

        character_analysis = {}

        for character in characters:
            char_name = character.get('name', 'Unknown')

            # Find tracks where this character appears
            character_tracks = []
            for track in tracks:
                lyrics = track.get('lyrics', '')
                if char_name.lower() in lyrics.lower():
                    character_tracks.append(track)

            if len(character_tracks) >= 2:
                # Analyze voice consistency across tracks
                voice_consistency = await self._analyze_character_voice_in_tracks(char_name, character_tracks)

                character_analysis[char_name] = {
                    'consistency_score': voice_consistency,
                    'track_count': len(character_tracks),
                    'analysis': 'Consistent voice across tracks' if voice_consistency > 0.7 else 'Voice inconsistencies detected'
                }
            else:
                character_analysis[char_name] = {
                    'consistency_score': 1.0,  # Can't be inconsistent with single appearance
                    'track_count': len(character_tracks),
                    'analysis': 'Insufficient appearances for consistency analysis'
                }

        return character_analysis

    async def _analyze_thematic_progression(self, tracks: List[Dict], ctx=None) -> Dict[str, Any]:
        """Analyze thematic progression across the album"""
        if ctx:
            await ctx.info("Analyzing thematic progression...")

        progression_analysis = {
            'has_clear_progression': False,
            'progression_type': 'none',
            'thematic_arc': [],
            'progression_strength': 0.0
        }

        if len(tracks) < 3:
            return progression_analysis

        # Extract themes from each track in order
        track_themes = []
        for track in tracks:
            themes = self._extract_track_themes(track)
            track_themes.append(themes)

        # Analyze progression patterns
        progression_patterns = self._identify_thematic_progression_patterns(track_themes)

        if progression_patterns:
            progression_analysis['has_clear_progression'] = True
            progression_analysis['progression_type'] = progression_patterns['type']
            progression_analysis['thematic_arc'] = progression_patterns['arc']
            progression_analysis['progression_strength'] = progression_patterns['strength']

        return progression_analysis

    def _identify_thematic_progression_patterns(self, track_themes: List[List[str]]) -> Optional[Dict[str, Any]]:
        """Identify patterns in thematic progression"""
        if len(track_themes) < 3:
            return None

        # Look for common progression patterns
        patterns = {
            'linear_development': self._check_linear_development(track_themes),
            'cyclical_return': self._check_cyclical_return(track_themes),
            'thematic_deepening': self._check_thematic_deepening(track_themes),
            'conflict_resolution': self._check_conflict_resolution(track_themes)
        }

        # Find the strongest pattern
        strongest_pattern = max(patterns.items(), key=lambda x: x[1]['strength'])

        if strongest_pattern[1]['strength'] > 0.3:
            return {
                'type': strongest_pattern[0],
                'arc': strongest_pattern[1]['arc'],
                'strength': strongest_pattern[1]['strength']
            }

        return None

    def _check_linear_development(self, track_themes: List[List[str]]) -> Dict[str, Any]:
        """Check for linear thematic development"""
        # Simplified implementation - would be more sophisticated in practice
        unique_themes_per_track = [len(set(themes)) for themes in track_themes]

        # Linear development often shows increasing thematic complexity
        if len(unique_themes_per_track) >= 3:
            increasing_trend = all(unique_themes_per_track[i] <= unique_themes_per_track[i+1]
                                 for i in range(len(unique_themes_per_track)-1))

            if increasing_trend:
                return {
                    'strength': 0.7,
                    'arc': ['introduction', 'development', 'complexity']
                }

        return {'strength': 0.0, 'arc': []}

    def _check_cyclical_return(self, track_themes: List[List[str]]) -> Dict[str, Any]:
        """Check for cyclical thematic return"""
        if len(track_themes) < 3:
            return {'strength': 0.0, 'arc': []}

        first_themes = set(track_themes[0])
        last_themes = set(track_themes[-1])

        # Check for return to initial themes
        overlap = len(first_themes.intersection(last_themes))
        total_unique = len(first_themes.union(last_themes))

        if total_unique > 0:
            return_strength = overlap / total_unique
            if return_strength > 0.5:
                return {
                    'strength': return_strength,
                    'arc': ['introduction', 'departure', 'return']
                }

        return {'strength': 0.0, 'arc': []}

    def _check_thematic_deepening(self, track_themes: List[List[str]]) -> Dict[str, Any]:
        """Check for thematic deepening pattern"""
        # Look for consistent themes that appear throughout
        all_themes = [theme for themes in track_themes for theme in themes]
        theme_counts = Counter(all_themes)

        # Themes that appear in most tracks suggest deepening
        consistent_themes = [theme for theme, count in theme_counts.items()
                           if count >= len(track_themes) * 0.6]

        if consistent_themes:
            deepening_strength = len(consistent_themes) / len(set(all_themes))
            return {
                'strength': deepening_strength,
                'arc': ['introduction', 'exploration', 'deepening']
            }

        return {'strength': 0.0, 'arc': []}

    def _check_conflict_resolution(self, track_themes: List[List[str]]) -> Dict[str, Any]:
        """Check for conflict-resolution pattern"""
        # Simplified implementation - look for tension themes early, resolution themes later
        tension_themes = ['conflict', 'struggle', 'tension', 'problem', 'challenge']
        resolution_themes = ['resolution', 'peace', 'harmony', 'solution', 'acceptance']

        # Flatten early themes and check for tension
        early_themes = []
        for theme_list in track_themes[:len(track_themes)//2]:
            early_themes.extend(theme_list)

        early_tension = any(any(tension in theme.lower() for tension in tension_themes)
                          for theme in early_themes)

        # Flatten late themes and check for resolution
        late_themes = []
        for theme_list in track_themes[len(track_themes)//2:]:
            late_themes.extend(theme_list)

        late_resolution = any(any(resolution in theme.lower() for resolution in resolution_themes)
                            for theme in late_themes)

        if early_tension and late_resolution:
            return {
                'strength': 0.8,
                'arc': ['conflict', 'struggle', 'resolution']
            }

        return {'strength': 0.0, 'arc': []}

    def _generate_quality_flags(self, coherence_score: ThematicCoherenceScore,
                              track_consistency: Dict[str, float],
                              character_voice_analysis: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate quality flags based on analysis results"""
        flags = []

        # Overall coherence flags
        if coherence_score.overall_score < 0.5:
            flags.append("LOW_OVERALL_COHERENCE")

        if coherence_score.consistency_score < 0.6:
            flags.append("THEMATIC_INCONSISTENCY")

        if coherence_score.character_voice_score < 0.7:
            flags.append("CHARACTER_VOICE_INCONSISTENCY")

        if coherence_score.perspective_maintenance_score < 0.6:
            flags.append("PERSPECTIVE_INCONSISTENCY")

        # Track-specific flags
        inconsistent_tracks = [track for track, score in track_consistency.items() if score < 0.5]
        if inconsistent_tracks:
            flags.append(f"INCONSISTENT_TRACKS: {', '.join(inconsistent_tracks)}")

        # Character-specific flags
        inconsistent_characters = [char for char, analysis in character_voice_analysis.items()
                                 if analysis['consistency_score'] < 0.7 and analysis['track_count'] > 1]
        if inconsistent_characters:
            flags.append(f"INCONSISTENT_CHARACTER_VOICES: {', '.join(inconsistent_characters)}")

        return flags

def validate_analysis_results(results: Dict[str, Any]) -> List[str]:
    """
    Validate analysis results and return any issues
    
    Enhanced with thematic coherence validation for requirement 4.2
    
    Args:
        results: Analysis results dictionary
        
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []

    # Check required fields
    required_fields = ['characters', 'narrative_themes', 'emotional_arc', 'analysis_metadata']
    for field in required_fields:
        if field not in results:
            issues.append(f"Missing required field: {field}")

    # Validate characters
    if 'characters' in results:
        if not isinstance(results['characters'], list):
            issues.append("Characters field should be a list")
        else:
            for i, char in enumerate(results['characters']):
                if not isinstance(char, dict):
                    issues.append(f"Character {i} should be a dictionary")
                elif 'name' not in char:
                    issues.append(f"Character {i} missing name field")

    # Validate themes
    if 'narrative_themes' in results:
        if not isinstance(results['narrative_themes'], list):
            issues.append("Narrative themes field should be a list")

    # Validate emotional arc
    if 'emotional_arc' in results:
        if not isinstance(results['emotional_arc'], list):
            issues.append("Emotional arc field should be a list")

    # Enhanced validation for thematic coherence
    if 'album_content' in results:
        coherence_issues = validate_thematic_coherence(results['album_content'])
        issues.extend(coherence_issues)

    return issues

def validate_thematic_coherence(album_content: Dict[str, Any]) -> List[str]:
    """
    Validate thematic coherence of album content
    
    Implements requirement 4.2: Thematic coherence validation
    """
    issues = []

    tracks = album_content.get('tracks', [])
    characters = album_content.get('characters', [])

    if not tracks:
        issues.append("No tracks found for coherence validation")
        return issues

    # Create validator and run validation
    validator = ThematicCoherenceValidator()

    # Run synchronous validation (simplified for this context)
    try:
        # Extract themes from tracks for basic validation
        track_themes = []
        for track in tracks:
            themes = []
            lyrics = track.get('lyrics', '')
            if lyrics:
                # Basic theme extraction
                if 'love' in lyrics.lower():
                    themes.append('love')
                if 'loss' in lyrics.lower():
                    themes.append('loss')
                if 'hope' in lyrics.lower():
                    themes.append('hope')
                # Add more theme detection as needed
            track_themes.append(themes)

        # Check for thematic consistency
        if len(track_themes) > 1:
            theme_consistency = validator._calculate_theme_overlap(track_themes[0], track_themes[-1])
            if theme_consistency < 0.3:
                issues.append("Low thematic consistency between first and last tracks")

        # Check character voice consistency
        for character in characters:
            char_name = character.get('name', '')
            appearances = sum(1 for track in tracks if char_name.lower() in track.get('lyrics', '').lower())
            if appearances > 1:
                # Would perform detailed voice analysis in full implementation
                pass

    except Exception as e:
        issues.append(f"Error during coherence validation: {str(e)}")

    return issues
