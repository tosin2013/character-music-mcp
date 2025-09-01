#!/usr/bin/env python3
"""
Working Universal Content Processor - Simplified for Testing
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import re

@dataclass
class UniversalMusicCommand:
    """Complete music command with universal content processing"""
    title: str
    original_content: str
    character_interpretation: str
    personal_story: str
    formatted_lyrics: str
    suno_command: str
    effectiveness_score: float

class WorkingUniversalProcessor:
    """Enhanced processor that intelligently handles different content types through character lens"""
    
    def __init__(self, character_description: str = None):
        # Parse character description with validation
        if character_description and self._validate_character_description(character_description):
            self.character_worldview = self._parse_character_description(character_description)
        elif character_description:
            # If description provided but invalid, create generic character
            self.character_worldview = self._create_generic_character(character_description)
        else:
            # No description provided - create truly generic character
            self.character_worldview = self._create_default_character()
    
    def detect_content_type(self, text: str) -> Dict[str, Any]:
        """
        Enhanced content type detection with confidence scoring and processing strategy selection
        
        Returns detailed analysis including content type, confidence, and recommended processing strategy
        """
        if not text or len(text.strip()) < 10:
            return {
                "content_type": "unknown",
                "confidence": 0.0,
                "processing_strategy": "fallback",
                "detected_formats": [],
                "ambiguity_score": 1.0,
                "clarification_needed": True,
                "suggested_clarifications": ["Please provide more content for analysis"]
            }
        
        text_lower = text.lower()
        detected_formats = []
        format_scores = {}
        
        # Enhanced character description detection
        character_indicators = {
            "explicit_markers": ["character:", "protagonist:", "artist:", "musician:", "producer:", "persona:", "profile:"],
            "biographical": ["year-old", "years old", "born in", "grew up", "lives in", "comes from", "raised in"],
            "descriptive": ["personality:", "background:", "style:", "genre:", "influences:", "known for", "specializes in"],
            "professional": ["career", "discography", "albums", "singles", "collaborations", "record label"]
        }
        
        char_score = 0
        for category, indicators in character_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in text_lower)
            if category == "explicit_markers" and matches > 0:
                char_score += matches * 3  # High weight for explicit markers
            elif matches > 0:
                char_score += matches * 1.5
        
        if char_score > 0:
            format_scores["character_description"] = min(char_score / 10.0, 1.0)
            detected_formats.append("character_description")
        
        # Enhanced narrative fiction detection
        narrative_indicators = {
            "story_markers": ["once upon", "chapter", "story", "tale", "narrative"],
            "dialogue": ["he said", "she said", "they said", "asked", "replied", "whispered", "shouted"],
            "narrative_elements": ["protagonist", "character", "plot", "scene", "setting"],
            "action_verbs": ["walked", "looked", "saw", "felt", "thought", "remembered", "realized", "noticed", "heard"],
            "past_tense_patterns": [r'\b\w+ed\b', r'\bwas\b', r'\bwere\b', r'\bhad\b', r'\bdid\b']
        }
        
        narrative_score = 0
        for category, indicators in narrative_indicators.items():
            if category == "past_tense_patterns":
                import re
                for pattern in indicators:
                    matches = len(re.findall(pattern, text_lower))
                    if matches > 3:  # Multiple past tense verbs suggest narrative
                        narrative_score += min(matches / 5.0, 2.0)
            else:
                matches = sum(1 for indicator in indicators if indicator in text_lower)
                narrative_score += matches * 1.0
        
        if narrative_score > 2:
            format_scores["narrative_fiction"] = min(narrative_score / 15.0, 1.0)
            detected_formats.append("narrative_fiction")
        
        # Enhanced philosophical/conceptual content detection
        philosophical_indicators = {
            "philosophical_terms": ["philosophy", "philosophical", "metaphysical", "existential", "ontological", "epistemological"],
            "abstract_concepts": ["consciousness", "reality", "truth", "meaning", "purpose", "essence", "being", "existence"],
            "spiritual_terms": ["spiritual", "divine", "transcendent", "universal", "eternal", "sacred", "mystical"],
            "conceptual_markers": ["concept:", "theory:", "idea:", "explores", "examines", "represents", "symbolizes", "embodies"]
        }
        
        philosophical_score = 0
        for category, indicators in philosophical_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in text_lower)
            if category == "conceptual_markers" and matches > 0:
                philosophical_score += matches * 2.5  # High weight for explicit conceptual markers
            elif matches > 0:
                philosophical_score += matches * 1.5
        
        if philosophical_score > 1:
            format_scores["philosophical_conceptual"] = min(philosophical_score / 10.0, 1.0)
            detected_formats.append("philosophical_conceptual")
        
        # Enhanced poetic content detection
        poetic_indicators = {
            "poetic_markers": ["poem", "poetry", "verse", "stanza", "rhyme", "metaphor", "imagery"],
            "structural": ["line breaks", "rhythm", "meter", "refrain"],
            "literary_devices": ["alliteration", "assonance", "symbolism", "allegory"]
        }
        
        poetic_score = 0
        has_poetic_structure = "/" in text and len(text.split("/")) > 2
        has_line_breaks = "\n" in text and len(text.split("\n")) > 3
        
        for category, indicators in poetic_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in text_lower)
            poetic_score += matches * 1.5
        
        if has_poetic_structure and len(text.split()) < 200:  # Short text with line breaks
            poetic_score += 3
        elif has_line_breaks and len(text.split()) < 150:
            poetic_score += 2
        
        if poetic_score > 1:
            format_scores["poetic_content"] = min(poetic_score / 8.0, 1.0)
            detected_formats.append("poetic_content")
        
        # Check for concept outlines
        outline_indicators = ["outline:", "structure:", "framework:", "1.", "2.", "3.", "•", "-", "a)", "b)", "i.", "ii."]
        outline_score = sum(1 for indicator in outline_indicators if indicator in text_lower)
        
        if outline_score > 2:
            format_scores["concept_outline"] = min(outline_score / 6.0, 1.0)
            detected_formats.append("concept_outline")
        
        # Determine primary content type and confidence
        if not format_scores:
            primary_type = "mixed_content"
            confidence = 0.3
        else:
            primary_type = max(format_scores.keys(), key=lambda k: format_scores[k])
            confidence = format_scores[primary_type]
        
        # Calculate ambiguity score (how unclear the content type is)
        if len(format_scores) <= 1:
            ambiguity_score = 0.0  # Clear single type
        elif len(format_scores) == 2:
            scores = list(format_scores.values())
            ambiguity_score = 1.0 - abs(scores[0] - scores[1])  # Close scores = high ambiguity
        else:
            ambiguity_score = 0.8  # Multiple types = high ambiguity
        
        # Determine processing strategy
        processing_strategy = self._select_processing_strategy(primary_type, confidence, ambiguity_score)
        
        # Determine if clarification is needed
        clarification_needed = confidence < 0.6 or ambiguity_score > 0.5
        suggested_clarifications = self._generate_clarification_suggestions(detected_formats, ambiguity_score)
        
        return {
            "content_type": primary_type,
            "confidence": confidence,
            "processing_strategy": processing_strategy,
            "detected_formats": detected_formats,
            "format_scores": format_scores,
            "ambiguity_score": ambiguity_score,
            "clarification_needed": clarification_needed,
            "suggested_clarifications": suggested_clarifications
        }
    
    def _select_processing_strategy(self, content_type: str, confidence: float, ambiguity_score: float) -> str:
        """Select appropriate processing strategy based on content analysis"""
        if confidence < 0.4:
            return "request_clarification"
        elif ambiguity_score > 0.7:
            return "hybrid_processing"
        elif content_type == "character_description":
            return "use_explicit_description"
        elif content_type == "narrative_fiction":
            return "extract_characters"
        elif content_type == "philosophical_conceptual":
            return "create_conceptual_characters"
        elif content_type == "poetic_content":
            return "create_poetic_characters"
        elif content_type == "concept_outline":
            return "process_structured_concepts"
        else:
            return "adaptive_processing"
    
    def _generate_clarification_suggestions(self, detected_formats: List[str], ambiguity_score: float) -> List[str]:
        """Generate helpful clarification suggestions for ambiguous input"""
        suggestions = []
        
        if not detected_formats:
            suggestions.extend([
                "Could you specify if this is a character description, story excerpt, or conceptual content?",
                "Would you like me to create characters from concepts or extract them from narrative?",
                "Please indicate the type of content you'd like me to process."
            ])
        elif len(detected_formats) > 2:
            suggestions.extend([
                f"I detected multiple content types: {', '.join(detected_formats)}. Which should I prioritize?",
                "Would you like me to process this as narrative fiction or conceptual content?",
                "Should I focus on character extraction or character creation?"
            ])
        elif ambiguity_score > 0.6:
            if "character_description" in detected_formats and "narrative_fiction" in detected_formats:
                suggestions.append("Is this an explicit character description or should I extract characters from the narrative?")
            elif "philosophical_conceptual" in detected_formats and "narrative_fiction" in detected_formats:
                suggestions.append("Should I create conceptual characters from the themes or extract narrative characters?")
            elif "poetic_content" in detected_formats:
                suggestions.append("Would you like me to treat this as poetry or extract narrative elements?")
        
        if not suggestions:
            suggestions.append("The content type seems clear. Proceeding with automatic processing.")
        
        return suggestions
    
    def route_content_processing(self, text: str, user_preference: str = None) -> Dict[str, Any]:
        """
        Route content to appropriate processing strategy based on detection and user preference
        
        Args:
            text: Input text to process
            user_preference: Optional user-specified processing preference
            
        Returns:
            Dictionary containing processing results and metadata
        """
        # Perform enhanced content detection
        detection_result = self.detect_content_type(text)
        
        # Override with user preference if provided and valid
        if user_preference and user_preference in ["character_description", "narrative_fiction", 
                                                  "philosophical_conceptual", "poetic_content", 
                                                  "concept_outline", "mixed_content"]:
            detection_result["content_type"] = user_preference
            detection_result["processing_strategy"] = self._select_processing_strategy(user_preference, 1.0, 0.0)
            detection_result["user_override"] = True
        
        # Route to appropriate processing method
        try:
            characters = self.extract_or_create_characters(text, detection_result)
            processing_success = True
            error_message = None
        except Exception as e:
            characters = []
            processing_success = False
            error_message = str(e)
        
        return {
            "characters": characters,
            "detection_result": detection_result,
            "processing_success": processing_success,
            "error_message": error_message,
            "fallback_available": len(characters) == 0 and processing_success
        }
    
    def extract_or_create_characters(self, text: str, detection_result: Dict[str, Any] = None) -> List[Dict]:
        """
        Enhanced character extraction/creation with flexible routing based on detection results
        
        Args:
            text: Input text to process
            detection_result: Result from detect_content_type() or content type string for backward compatibility
            
        Returns:
            List of character dictionaries
        """
        # Handle backward compatibility - if detection_result is a string, convert it
        if isinstance(detection_result, str):
            content_type = detection_result
            processing_strategy = self._select_processing_strategy(content_type, 0.8, 0.2)
        elif detection_result is None:
            detection_result = self.detect_content_type(text)
            content_type = detection_result["content_type"]
            processing_strategy = detection_result["processing_strategy"]
        else:
            content_type = detection_result["content_type"]
            processing_strategy = detection_result["processing_strategy"]
        
        # Route based on processing strategy
        if processing_strategy == "use_explicit_description":
            return [self._parse_explicit_character_description(text)]
        
        elif processing_strategy == "extract_characters":
            return self._extract_narrative_characters(text)
        
        elif processing_strategy == "create_conceptual_characters":
            return self._create_conceptual_characters_from_themes(text)
        
        elif processing_strategy == "create_poetic_characters":
            return self._create_characters_from_poetry(text)
        
        elif processing_strategy == "process_structured_concepts":
            return self._process_concept_outline(text)
        
        elif processing_strategy == "hybrid_processing":
            return self._hybrid_character_processing(text, detection_result)
        
        elif processing_strategy == "adaptive_processing":
            return self._adaptive_character_processing(text)
        
        elif processing_strategy == "request_clarification":
            # Return empty list to trigger clarification request
            return []
        
        else:  # Fallback for unknown strategies
            return self._fallback_character_processing(text)
    
    def _process_concept_outline(self, text: str) -> List[Dict]:
        """Process structured concept outlines to create characters"""
        # Extract structured concepts from outline format
        concepts = self._extract_structured_concepts(text)
        
        if not concepts:
            # Fallback to theme-based processing
            return self._create_conceptual_characters_from_themes(text)
        
        characters = []
        for i, concept in enumerate(concepts[:2]):  # Limit to 2 main concepts
            character = self._create_character_from_concept(concept, i)
            characters.append(character)
        
        return characters
    
    def _extract_structured_concepts(self, text: str) -> List[Dict]:
        """Extract concepts from structured outline format"""
        concepts = []
        lines = text.split('\n')
        
        current_concept = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for main concept headers (1., 2., A., B., etc.)
            if re.match(r'^[1-9A-Z]\.|^[•-]\s*[A-Z]', line):
                if current_concept:
                    concepts.append(current_concept)
                
                current_concept = {
                    "title": re.sub(r'^[1-9A-Z•-]\.\s*', '', line),
                    "details": [],
                    "themes": []
                }
            elif current_concept and (line.startswith('  ') or line.startswith('\t')):
                # Sub-point or detail
                current_concept["details"].append(line.strip())
            elif current_concept:
                # Additional content for current concept
                current_concept["details"].append(line)
        
        if current_concept:
            concepts.append(current_concept)
        
        return concepts
    
    def _create_character_from_concept(self, concept: Dict, index: int) -> Dict:
        """Create character from structured concept"""
        title = concept.get("title", f"Concept {index + 1}")
        details = concept.get("details", [])
        
        # Generate character based on concept
        character_names = ["The Architect", "The Visionary", "The Catalyst", "The Guardian"]
        
        return {
            "name": character_names[index % len(character_names)],
            "filter": "philosophical_rational",
            "questions": [
                f"How does {title.lower()} manifest in reality?",
                f"What are the implications of {title.lower()}?",
                f"How can {title.lower()} be expressed through music?",
                "What deeper meaning lies within this concept?"
            ],
            "struggles": [
                "Translating abstract concepts into concrete expression",
                "Bridging theoretical understanding with practical application",
                "Communicating complex ideas through artistic medium"
            ],
            "context": {
                "age": 31 + index,
                "location": "conceptual studio space",
                "genre": "experimental",
                "time": "deep contemplation sessions",
                "equipment": "tools for conceptual expression"
            },
            "content_type": "concept_outline",
            "conceptual_basis": [title] + details[:3],
            "processing_notes": f"Created from structured concept: {title}"
        }
    
    def _hybrid_character_processing(self, text: str, detection_result: Dict) -> List[Dict]:
        """Process content using multiple strategies and combine results"""
        characters = []
        detected_formats = detection_result.get("detected_formats", [])
        
        # Try narrative extraction first
        if "narrative_fiction" in detected_formats:
            narrative_chars = self._extract_narrative_characters(text)
            characters.extend(narrative_chars)
        
        # Add conceptual characters if philosophical content detected
        if "philosophical_conceptual" in detected_formats and len(characters) < 2:
            conceptual_chars = self._create_conceptual_characters_from_themes(text)
            characters.extend(conceptual_chars[:2 - len(characters)])
        
        # Add character description if detected
        if "character_description" in detected_formats and len(characters) == 0:
            desc_char = self._parse_explicit_character_description(text)
            characters.append(desc_char)
        
        # Fallback if no characters found
        if not characters:
            characters = self._fallback_character_processing(text)
        
        return characters[:3]  # Limit to 3 characters max
    
    def _adaptive_character_processing(self, text: str) -> List[Dict]:
        """Adaptively process content by trying multiple approaches"""
        # Try different approaches in order of likelihood
        approaches = [
            ("narrative", self._extract_narrative_characters),
            ("conceptual", self._create_conceptual_characters_from_themes),
            ("poetic", self._create_characters_from_poetry)
        ]
        
        for approach_name, approach_func in approaches:
            try:
                characters = approach_func(text)
                if characters and len(characters) > 0:
                    # Mark characters with processing approach used
                    for char in characters:
                        char["processing_notes"] = f"Created using {approach_name} approach"
                    return characters
            except Exception:
                continue
        
        # Final fallback
        return self._fallback_character_processing(text)
    
    def _fallback_character_processing(self, text: str) -> List[Dict]:
        """Fallback character processing when other methods fail"""
        return [{
            "name": "The Creator",
            "filter": "introspective",
            "questions": [
                "What story wants to be told here?",
                "What emotions live within this content?",
                "How can this be transformed into music?",
                "What character would emerge from this material?"
            ],
            "struggles": [
                "Finding the right artistic voice",
                "Translating ideas into musical expression",
                "Creating authentic artistic content"
            ],
            "context": {
                "age": 30,
                "location": "creative studio",
                "genre": "alternative",
                "time": "creative sessions",
                "equipment": "standard recording setup"
            },
            "content_type": "fallback",
            "processing_notes": "Created using fallback processing due to unclear content type"
        }]
    
    def _parse_explicit_character_description(self, text: str) -> Dict:
        """Parse explicit character descriptions provided by user"""
        # Use existing character parsing logic but mark as explicit
        character_data = self._parse_character_description(text)
        character_data["content_type"] = "character_description"
        character_data["processing_notes"] = "Used explicit character description"
        return character_data
    
    def _extract_narrative_characters(self, text: str) -> List[Dict]:
        """Extract characters from narrative fiction content"""
        characters = []
        
        # Look for proper names that appear multiple times (likely characters)
        import re
        
        # Find potential character names (capitalized words that aren't common nouns)
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        potential_names = re.findall(name_pattern, text)
        
        # Filter out common words that aren't names
        common_words = {
            'The', 'This', 'That', 'These', 'Those', 'When', 'Where', 'What', 'Who', 'Why', 'How',
            'And', 'But', 'Or', 'So', 'Yet', 'For', 'Nor', 'As', 'If', 'Then', 'Now', 'Here',
            'There', 'Today', 'Tomorrow', 'Yesterday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
            'Friday', 'Saturday', 'Sunday', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        }
        
        # Count occurrences and filter
        name_counts = {}
        for name in potential_names:
            if name not in common_words and len(name) > 2:
                name_counts[name] = name_counts.get(name, 0) + 1
        
        # Only consider names that appear multiple times or have character context
        character_names = []
        for name, count in name_counts.items():
            if count >= 2 or self._has_character_context(text, name):
                character_names.append(name)
        
        # Create character profiles for found names
        for name in character_names[:3]:  # Limit to 3 main characters
            character = self._create_narrative_character_profile(name, text)
            characters.append(character)
        
        # If no characters found, return empty list (will trigger fallback)
        return characters
    
    def _has_character_context(self, text: str, name: str) -> bool:
        """Check if a name appears in character-like context"""
        character_contexts = [
            f"{name} said", f"{name} thought", f"{name} felt", f"{name} walked",
            f"{name} looked", f"{name} smiled", f"{name} laughed", f"{name} cried",
            f"{name}'s", f"{name} was", f"{name} had", f"{name} did"
        ]
        
        text_lower = text.lower()
        name_lower = name.lower()
        
        return any(context.lower() in text_lower for context in character_contexts)
    
    def _create_narrative_character_profile(self, name: str, text: str) -> Dict:
        """Create character profile from narrative context"""
        # Extract context around the character name
        character_context = self._extract_character_context(name, text)
        
        # Infer traits from context
        traits = self._infer_character_traits(character_context)
        
        return {
            "name": name,
            "filter": traits.get("filter", "introspective"),
            "questions": traits.get("questions", [
                f"What drives {name}?",
                f"How does {name} see the world?",
                f"What is {name}'s story?"
            ]),
            "struggles": traits.get("struggles", [
                "Personal growth",
                "Finding purpose",
                "Overcoming challenges"
            ]),
            "context": {
                "age": traits.get("age", 30),
                "location": traits.get("location", "unknown setting"),
                "genre": traits.get("genre", "alternative"),
                "time": "character's journey",
                "equipment": "narrative voice"
            },
            "content_type": "narrative_fiction",
            "processing_notes": f"Extracted from narrative context"
        }
    
    def _create_conceptual_characters_from_themes(self, text: str) -> List[Dict]:
        """Create conceptual characters that embody philosophical themes"""
        themes = self._extract_philosophical_themes(text)
        characters = []
        
        # Create primary conceptual character
        primary_character = self._create_primary_conceptual_character(text, themes)
        characters.append(primary_character)
        
        # If multiple strong themes, create additional perspective characters
        if len(themes) > 2:
            secondary_character = self._create_secondary_conceptual_character(text, themes[1:])
            characters.append(secondary_character)
        
        return characters
    
    def _extract_philosophical_themes(self, text: str) -> List[str]:
        """Extract philosophical themes from abstract content"""
        text_lower = text.lower()
        
        theme_indicators = {
            "existential": ["existence", "being", "reality", "consciousness", "identity"],
            "spiritual": ["divine", "sacred", "spiritual", "transcendent", "soul"],
            "temporal": ["time", "eternity", "moment", "duration", "memory"],
            "aesthetic": ["beauty", "art", "creation", "aesthetic", "sublime"],
            "ethical": ["good", "evil", "moral", "ethics", "virtue", "justice"],
            "epistemological": ["knowledge", "truth", "understanding", "wisdom", "certainty"],
            "metaphysical": ["reality", "substance", "causation", "necessity", "possibility"],
            "phenomenological": ["experience", "perception", "consciousness", "awareness"],
            "social": ["community", "society", "relationship", "connection", "isolation"],
            "psychological": ["mind", "emotion", "desire", "fear", "hope", "anxiety"]
        }
        
        detected_themes = []
        for theme, indicators in theme_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                detected_themes.append(theme)
        
        return detected_themes if detected_themes else ["existential"]
    
    def _create_primary_conceptual_character(self, text: str, themes: List[str]) -> Dict:
        """Create primary character that embodies the main philosophical concepts"""
        primary_theme = themes[0] if themes else "existential"
        
        # Generate character based on primary theme
        theme_characters = {
            "existential": {
                "name": "The Seeker",
                "filter": "philosophical_rational",
                "questions": [
                    "What does it mean to exist?",
                    "How do we find meaning in existence?",
                    "What is the nature of reality?",
                    "How do we create authentic being?"
                ],
                "struggles": [
                    "Confronting existential anxiety",
                    "Finding meaning in apparent meaninglessness",
                    "Balancing freedom with responsibility"
                ],
                "genre": "experimental"
            },
            "spiritual": {
                "name": "The Mystic",
                "filter": "spiritual_emotional",
                "questions": [
                    "How do we connect with the divine?",
                    "What lies beyond material existence?",
                    "How does spirit manifest in sound?",
                    "What is the sacred in everyday life?"
                ],
                "struggles": [
                    "Bridging material and spiritual worlds",
                    "Finding divine presence in ordinary moments",
                    "Expressing ineffable experiences"
                ],
                "genre": "ambient"
            },
            "aesthetic": {
                "name": "The Artist",
                "filter": "introspective",
                "questions": [
                    "What makes something beautiful?",
                    "How does art reveal truth?",
                    "What is the relationship between form and meaning?",
                    "How do we create authentic beauty?"
                ],
                "struggles": [
                    "Balancing commercial and artistic integrity",
                    "Finding unique creative voice",
                    "Expressing inner vision through medium"
                ],
                "genre": "indie folk"
            },
            "social": {
                "name": "The Connector",
                "filter": "social_conscious",
                "questions": [
                    "How do we build authentic community?",
                    "What breaks down barriers between people?",
                    "How does music create connection?",
                    "What is our responsibility to others?"
                ],
                "struggles": [
                    "Overcoming social isolation",
                    "Building bridges across differences",
                    "Using art for social change"
                ],
                "genre": "hip-hop"
            }
        }
        
        character_template = theme_characters.get(primary_theme, theme_characters["existential"])
        
        # Customize based on actual text content
        customized_character = {
            **character_template,
            "context": {
                "age": 32,
                "location": "contemplative studio space",
                "genre": character_template["genre"],
                "time": "deep reflection sessions",
                "equipment": "tools for philosophical expression"
            },
            "content_type": "philosophical_conceptual",
            "conceptual_basis": themes,
            "processing_notes": f"Created from {primary_theme} philosophical themes"
        }
        
        return customized_character
    
    def _create_secondary_conceptual_character(self, text: str, secondary_themes: List[str]) -> Dict:
        """Create secondary character representing alternative perspective"""
        secondary_theme = secondary_themes[0] if secondary_themes else "psychological"
        
        # Create contrasting perspective character
        contrast_characters = {
            "existential": {
                "name": "The Pragmatist",
                "filter": "introspective",
                "questions": [
                    "How do we live practically with uncertainty?",
                    "What actions matter in daily life?",
                    "How do we find joy despite existential questions?"
                ]
            },
            "spiritual": {
                "name": "The Skeptic",
                "filter": "philosophical_rational",
                "questions": [
                    "What can we know through reason alone?",
                    "How do we distinguish truth from wishful thinking?",
                    "What is the role of doubt in understanding?"
                ]
            },
            "aesthetic": {
                "name": "The Critic",
                "filter": "philosophical_rational",
                "questions": [
                    "What standards should we use to judge art?",
                    "How do we separate genuine beauty from fashion?",
                    "What is the social function of aesthetic judgment?"
                ]
            },
            "social": {
                "name": "The Individual",
                "filter": "introspective",
                "questions": [
                    "How do we maintain authenticity in community?",
                    "What is the balance between self and others?",
                    "How do we honor both individual and collective needs?"
                ]
            }
        }
        
        character_template = contrast_characters.get(secondary_theme, contrast_characters["existential"])
        
        return {
            **character_template,
            "struggles": [
                "Balancing different philosophical perspectives",
                "Finding synthesis between opposing views",
                "Maintaining intellectual honesty"
            ],
            "context": {
                "age": 28,
                "location": "alternative creative space",
                "genre": "alternative",
                "time": "questioning sessions",
                "equipment": "tools for critical analysis"
            },
            "content_type": "philosophical_conceptual",
            "conceptual_basis": secondary_themes,
            "processing_notes": f"Created as alternative perspective on {secondary_theme} themes"
        }
    
    def _create_characters_from_poetry(self, text: str) -> List[Dict]:
        """Create characters from poetic voice and themes"""
        # Analyze poetic voice and themes
        poetic_voice = self._analyze_poetic_voice(text)
        poetic_themes = self._extract_poetic_themes(text)
        
        character = {
            "name": "The Poet",
            "filter": "introspective",
            "questions": [
                "How do words capture ineffable experience?",
                "What truth lives in metaphor and rhythm?",
                "How does poetry reveal what prose cannot?",
                "What is the music inherent in language?"
            ],
            "struggles": [
                "Translating inner vision into words",
                "Finding the precise image or metaphor",
                "Balancing meaning with musical quality"
            ],
            "context": {
                "age": 29,
                "location": "quiet writing space",
                "genre": "indie folk",
                "time": "contemplative hours",
                "equipment": "voice and acoustic instruments"
            },
            "content_type": "poetic_content",
            "conceptual_basis": poetic_themes,
            "processing_notes": "Created from poetic voice and imagery"
        }
        
        return [character]
    
    def _analyze_poetic_voice(self, text: str) -> Dict:
        """Analyze the voice and tone of poetic content"""
        # Simple analysis of poetic characteristics
        return {
            "tone": "contemplative",
            "perspective": "first_person",
            "imagery_type": "natural",
            "emotional_register": "introspective"
        }
    
    def _extract_poetic_themes(self, text: str) -> List[str]:
        """Extract themes from poetic content"""
        # Reuse philosophical theme extraction for poetry
        return self._extract_philosophical_themes(text)
    
    def _extract_character_context(self, name: str, text: str) -> str:
        """Extract text context around character mentions"""
        sentences = text.split('.')
        context_sentences = []
        
        for sentence in sentences:
            if name in sentence:
                context_sentences.append(sentence.strip())
        
        return '. '.join(context_sentences[:3])  # First 3 relevant sentences
    
    def _infer_character_traits(self, context: str) -> Dict:
        """Infer character traits from narrative context"""
        context_lower = context.lower()
        
        # Simple trait inference based on context keywords
        traits = {
            "age": 30,
            "location": "story setting",
            "genre": "alternative",
            "filter": "introspective"
        }
        
        # Infer age
        age_match = re.search(r'(\d+)[-\s]*year[-\s]*old', context_lower)
        if age_match:
            traits["age"] = int(age_match.group(1))
        
        # Infer personality filter
        if any(word in context_lower for word in ["think", "thought", "philosophy", "question"]):
            traits["filter"] = "philosophical_rational"
        elif any(word in context_lower for word in ["feel", "emotion", "heart", "soul"]):
            traits["filter"] = "spiritual_emotional"
        elif any(word in context_lower for word in ["community", "people", "society", "change"]):
            traits["filter"] = "social_conscious"
        
        return traits
    
    def _validate_character_description(self, description: str) -> bool:
        """Validate that character description contains essential information"""
        if not description or len(description.strip()) < 20:
            return False
        
        # Check for basic character elements
        has_name = bool(re.search(r'[A-Z][a-z]+ (?:"[^"]*" )?[A-Z][a-z]+', description))
        has_age_or_context = any(word in description.lower() for word in ['year', 'old', 'age', 'artist', 'producer', 'musician'])
        has_genre_or_style = any(word in description.lower() for word in ['music', 'genre', 'style', 'sound', 'artist', 'producer'])
        
        return has_name or (has_age_or_context and has_genre_or_style)
    
    def _parse_character_description(self, description: str) -> Dict:
        """Parse character description to extract key traits"""
        desc_lower = description.lower()
        
        # Extract name - look for patterns like "FirstName LastName" or "FirstName 'Nickname' LastName"
        name_match = None
        
        # Try multiple name patterns - order matters!
        name_patterns = [
            r'([A-Z][A-Z]+ [A-Z][a-zA-Z]+)',  # DJ Memphis, MC Something
            r'([A-Z][a-z]+ [A-Z][a-zA-Z]+)',  # John Smith or John McKenzie
            r'([A-Z][a-z]+ (?:"[^"]*" )?[A-Z][a-z]+)',  # John "Nickname" Smith
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-zA-Z]+)+)',  # Multiple names at start
            r'([A-Z][A-Z]+)',  # Single names like DJ, MC (fallback)
        ]
        
        # First try to find name in the first sentence
        first_sentence = description.split('.')[0] if '.' in description else description.split('\n')[0]
        
        for pattern in name_patterns:
            match = re.search(pattern, first_sentence)
            if match:
                name_match = match.group(1)
                break
        
        # If still no match, try the whole description
        if not name_match:
            for pattern in name_patterns:
                match = re.search(pattern, description)
                if match:
                    name_match = match.group(1)
                    break
        
        name_match = name_match if name_match else "Independent Artist"
        
        # Extract age
        age_match = re.search(r'(\d+)[-\s]*year[-\s]*old', desc_lower)
        age = int(age_match.group(1)) if age_match else 30
        
        # Extract location dynamically from description
        location = self._extract_location_from_description(description, desc_lower)
        
        # Extract genre with comprehensive detection
        genre = self._extract_genre_from_description(description, desc_lower)
        
        # Extract personality/philosophical approach
        filter_type = "introspective"
        questions = ["What does this mean to me?", "How does this connect to my experience?", "What story does this tell?"]
        
        if "philosophical" in desc_lower:
            filter_type = "philosophical_rational"
            questions = [
                "What deeper meaning lies beneath this?",
                "How does this connect to universal truths?",
                "What questions does this raise about existence?",
                "How can I express this through music?"
            ]
        elif "spiritual" in desc_lower:
            filter_type = "spiritual_emotional"
            questions = [
                "What spiritual truth does this reveal?",
                "How does this touch the soul?",
                "What divine connection exists here?",
                "How can music channel this energy?"
            ]
        elif "political" in desc_lower or "social" in desc_lower:
            filter_type = "social_conscious"
            questions = [
                "What injustice does this reveal?",
                "How does this affect our community?",
                "What change needs to happen?",
                "How can music inspire action?"
            ]
        
        # Extract struggles/background
        struggles = ["Creative challenges", "Personal growth", "Artistic authenticity"]
        if "grief" in desc_lower or "loss" in desc_lower:
            struggles.append("Processing loss and grief")
        if "father" in desc_lower or "dad" in desc_lower:
            struggles.append("Complex relationship with father")
        if "theological" in desc_lower or "religious" in desc_lower:
            struggles.append("Spiritual vs rational worldview")
        
        return {
            "name": name_match,
            "filter": filter_type,
            "questions": questions,
            "struggles": struggles,
            "context": {
                "age": age,
                "location": location,
                "genre": genre,
                "time": "late night sessions",
                "equipment": "professional studio setup"
            }
        }
    
    def _extract_location_from_description(self, description: str, desc_lower: str) -> str:
        """Extract location details from character description"""
        # Look for specific location mentions with context
        location_patterns = {
            "new york": "New York studio",
            "nyc": "New York studio", 
            "los angeles": "Los Angeles studio",
            "la ": "Los Angeles studio",
            "nashville": "Nashville studio",
            "detroit": "Detroit studio",
            "chicago": "Chicago studio",
            "atlanta": "Atlanta studio",
            "miami": "Miami studio",
            "memphis": "Memphis studio",
            "seattle": "Seattle studio",
            "austin": "Austin studio",
            "philadelphia": "Philadelphia studio",
            "boston": "Boston studio"
        }
        
        # Check for city mentions
        for city, studio_name in location_patterns.items():
            if city in desc_lower:
                # Look for studio type context
                if "warehouse" in desc_lower:
                    return f"{city.title()} warehouse studio"
                elif "bedroom" in desc_lower or "home" in desc_lower:
                    return f"{city.title()} home studio"
                elif "basement" in desc_lower:
                    return f"{city.title()} basement studio"
                else:
                    return studio_name
        
        # Look for studio type without specific city
        if "warehouse" in desc_lower:
            return "warehouse studio"
        elif "bedroom" in desc_lower:
            return "bedroom studio"
        elif "basement" in desc_lower:
            return "basement studio"
        elif "home" in desc_lower and "studio" in desc_lower:
            return "home studio"
        elif "professional" in desc_lower and "studio" in desc_lower:
            return "professional studio"
        else:
            return "home studio"  # Default fallback
    
    def _extract_genre_from_description(self, description: str, desc_lower: str) -> str:
        """Extract genre from character description with comprehensive detection"""
        
        # Define genre patterns with priority (more specific first)
        genre_patterns = {
            # Electronic subgenres (check electronic first, then subgenres)
            "electronic": ["electronic music producer", "electronic producer", "electronic music", "electronic artist"],
            "liquid drum and bass": ["liquid drum and bass", "liquid dnb", "liquid d&b"],
            "drum and bass": ["drum and bass", "dnb", "d&b"],
            "dubstep": ["dubstep", "dub step"],
            "house": ["house music", "deep house", "tech house", "progressive house"],
            "techno": ["techno", "detroit techno"],
            "ambient": ["ambient music", "ambient electronic", "ambient soundscapes"],
            "synthwave": ["synthwave", "synth wave", "retrowave"],
            
            # Latin/Caribbean genres
            "reggaeton": ["reggaeton", "reggaeton producer", "reggaeton artist"],
            "latin trap": ["latin trap", "trap-reggaeton", "trap reggaeton"],
            
            # Hip-hop subgenres  
            "trap": ["trap music", "trap beats", "trap producer", "trap artist"],
            "boom bap": ["boom bap", "boom-bap"],
            "memphis hip-hop": ["memphis hip-hop", "memphis rap", "memphis hip hop"],
            "atlanta hip-hop": ["atlanta hip-hop", "atlanta rap", "atlanta hip hop"],
            "west coast hip-hop": ["west coast hip-hop", "west coast rap"],
            "east coast hip-hop": ["east coast hip-hop", "east coast rap"],
            "hip-hop": ["hip-hop", "hip hop", "rap music", "rap"],
            
            # Soul/R&B subgenres
            "neo-soul": ["neo-soul", "neo soul", "neosoul"],
            "r&b": ["r&b", "rnb", "rhythm and blues"],
            "soul": ["soul music", "soul"],
            "funk": ["funk", "funk music"],
            "gospel": ["gospel", "gospel music"],
            
            # Rock subgenres
            "indie rock": ["indie rock", "independent rock"],
            "alternative rock": ["alternative rock", "alt rock"],
            "progressive rock": ["progressive rock", "prog rock"],
            "post-rock": ["post-rock", "post rock"],
            "punk": ["punk rock", "punk"],
            "metal": ["metal", "heavy metal"],
            "rock": ["rock music", "rock"],
            
            # Jazz subgenres
            "jazz fusion": ["jazz fusion", "fusion jazz"],
            "smooth jazz": ["smooth jazz"],
            "bebop": ["bebop", "be-bop"],
            "jazz": ["jazz", "jazz music"],
            
            # Folk/Acoustic
            "indie folk": ["indie folk", "independent folk"],
            "folk": ["folk music", "folk", "acoustic folk"],
            "country": ["country music", "country"],
            "bluegrass": ["bluegrass"],
            
            # Electronic/Dance (broader patterns after specific ones)
            "trance": ["trance music", "trance"],
            "breakbeat": ["breakbeat", "break beat"],
            
            # Pop
            "indie pop": ["indie pop", "independent pop"],
            "pop": ["pop music", "pop"],
            
            # Experimental
            "experimental": ["experimental music", "experimental", "avant-garde"],
            "noise": ["noise music", "noise"],
        }
        
        # Check for genre patterns in order of specificity
        for genre, patterns in genre_patterns.items():
            for pattern in patterns:
                if pattern in desc_lower:
                    return genre
        
        # If no specific genre found, try to infer from context
        if any(word in desc_lower for word in ["producer", "beats", "samples"]):
            return "hip-hop"  # Producer context often implies hip-hop
        elif any(word in desc_lower for word in ["synthesizer", "synth", "electronic"]):
            return "electronic"
        elif any(word in desc_lower for word in ["guitar", "band", "live"]):
            return "rock"
        elif any(word in desc_lower for word in ["piano", "acoustic", "singer-songwriter"]):
            return "folk"
        elif any(word in desc_lower for word in ["vocals", "singing", "voice"]):
            return "pop"
        
        # Default fallback
        return "alternative"
    
    def _get_character_background(self) -> str:
        """Generate character background based on parsed traits"""
        character = self.character_worldview
        genre = character['context']['genre']
        filter_type = character['filter']
        
        backgrounds = {
            "philosophical_rational": f"Deep thinker who approaches {genre} through intellectual inquiry and rational exploration",
            "spiritual_emotional": f"Spiritually-driven {genre} artist who channels divine inspiration through music",
            "social_conscious": f"Socially aware {genre} artist using music as a vehicle for change and community connection",
            "introspective": f"Introspective {genre} artist exploring personal experiences and emotional landscapes"
        }
        
        return backgrounds.get(filter_type, f"Dedicated {genre} artist with unique creative perspective")
    
    def _get_production_style(self) -> str:
        """Generate production style based on character traits and genre"""
        character = self.character_worldview
        genre = character['context']['genre']
        filter_type = character['filter']
        
        # Base style from character filter
        base_styles = {
            "philosophical_rational": "Methodical and precise, with mathematical patterns and logical progressions",
            "spiritual_emotional": "Intuitive and flowing, channeling emotional energy into sonic landscapes",
            "social_conscious": "Bold and impactful, designed to move both body and mind toward action",
            "introspective": "Intimate and detailed, crafting personal sonic narratives"
        }
        
        base_style = base_styles.get(filter_type, "Creative and authentic approach to sound design")
        
        # Add genre-specific production characteristics
        genre_characteristics = self._get_genre_production_characteristics(genre)
        
        return f"{base_style}. {genre_characteristics}"
    
    def _get_genre_production_characteristics(self, genre: str) -> str:
        """Get genre-specific production characteristics"""
        genre_lower = genre.lower()
        
        characteristics = {
            "hip-hop": "Heavy emphasis on rhythm and groove, with crisp drums and deep bass",
            "trap": "Hard-hitting 808s, rapid hi-hats, and atmospheric pads",
            "memphis hip-hop": "Gritty, lo-fi aesthetic with heavy bass and vintage samples",
            "liquid drum and bass": "Smooth sub-bass, intricate breakbeats, and atmospheric textures",
            "drum and bass": "Fast breakbeats, heavy sub-bass, and energetic arrangements",
            "neo-soul": "Warm analog tones, live instrumentation feel, and rich harmonic textures",
            "r&b": "Smooth grooves, lush vocal arrangements, and polished production",
            "soul": "Organic instrumentation, emotional vocal delivery, and vintage warmth",
            "jazz": "Complex harmonies, dynamic arrangements, and acoustic instrument focus",
            "jazz fusion": "Blend of acoustic and electronic elements with sophisticated arrangements",
            "rock": "Guitar-driven sound with powerful drums and dynamic energy",
            "indie rock": "Raw authenticity with creative arrangements and unique sonic textures",
            "alternative rock": "Experimental approach with unconventional song structures",
            "electronic": "Synthesized textures, precise digital processing, and layered soundscapes",
            "house": "Four-on-the-floor beats, repetitive grooves, and dance-focused energy",
            "techno": "Driving rhythms, industrial textures, and hypnotic repetition",
            "ambient": "Atmospheric soundscapes, minimal rhythms, and immersive textures",
            "folk": "Acoustic instruments, natural reverb, and intimate recording approach",
            "indie folk": "Creative acoustic arrangements with subtle electronic enhancements",
            "pop": "Catchy melodies, polished production, and radio-friendly arrangements",
            "indie pop": "Creative pop sensibilities with unique artistic vision",
            "experimental": "Unconventional sounds, innovative techniques, and boundary-pushing approaches",
            "funk": "Groove-centric rhythms, syncopated bass lines, and rhythmic complexity"
        }
        
        return characteristics.get(genre_lower, f"Genre-appropriate {genre} production techniques and aesthetics")
    
    def _get_emotional_context(self) -> str:
        """Generate emotional context based on character struggles"""
        struggles = self.character_worldview['struggles']
        
        if any("grief" in s.lower() or "loss" in s.lower() for s in struggles):
            return "Processing loss and transformation through musical expression"
        elif any("spiritual" in s.lower() or "theological" in s.lower() for s in struggles):
            return "Exploring spiritual questions and seeking meaning through sound"
        elif any("social" in s.lower() or "community" in s.lower() for s in struggles):
            return "Channeling social awareness and community connection"
        else:
            return "Authentic personal expression through musical storytelling"
    
    def _get_vocal_style(self) -> str:
        """Generate vocal style based on character filter and genre"""
        character = self.character_worldview
        filter_type = character['filter']
        genre = character['context']['genre']
        
        # Base style from character filter
        base_styles = {
            "philosophical_rational": "Contemplative and measured, with occasional spoken philosophical reflections",
            "spiritual_emotional": "Soulful and transcendent, channeling spiritual energy through voice",
            "social_conscious": "Powerful and direct, delivering messages with conviction and clarity",
            "introspective": "Intimate and vulnerable, sharing personal truths through melody"
        }
        
        base_style = base_styles.get(filter_type, "Authentic and expressive vocal delivery")
        
        # Add genre-specific vocal characteristics
        genre_vocal_style = self._get_genre_vocal_characteristics(genre)
        
        return f"{base_style}. {genre_vocal_style}"
    
    def _get_genre_vocal_characteristics(self, genre: str) -> str:
        """Get genre-specific vocal characteristics"""
        genre_lower = genre.lower()
        
        vocal_styles = {
            "hip-hop": "Rhythmic flow with clear articulation and confident delivery",
            "trap": "Melodic rap style with auto-tuned harmonies and rhythmic precision",
            "memphis hip-hop": "Raw, unpolished delivery with southern drawl and street authenticity",
            "liquid drum and bass": "Smooth, flowing vocals that complement the liquid basslines",
            "drum and bass": "Energetic delivery that matches the fast-paced rhythms",
            "neo-soul": "Rich, warm vocals with melismatic runs and emotional depth",
            "r&b": "Smooth, polished vocals with sophisticated phrasing and control",
            "soul": "Powerful, gospel-influenced delivery with raw emotional expression",
            "jazz": "Sophisticated phrasing with improvisational elements and swing feel",
            "jazz fusion": "Complex vocal arrangements with instrumental-like phrasing",
            "rock": "Powerful, dynamic vocals with emotional intensity and range",
            "indie rock": "Unique vocal character with creative phrasing and authenticity",
            "alternative rock": "Unconventional vocal approach with artistic expression",
            "electronic": "Processed vocals with digital effects and atmospheric textures",
            "house": "Repetitive, hypnotic vocal patterns with dance energy",
            "techno": "Minimal, rhythmic vocals that enhance the driving beat",
            "ambient": "Ethereal, atmospheric vocals that blend with the soundscape",
            "folk": "Natural, unprocessed vocals with storytelling emphasis",
            "indie folk": "Intimate, conversational delivery with creative harmonies",
            "pop": "Catchy, memorable vocal melodies with broad appeal",
            "indie pop": "Creative vocal arrangements with unique artistic flair",
            "experimental": "Unconventional vocal techniques and innovative approaches",
            "funk": "Rhythmic, percussive vocal delivery with groove emphasis"
        }
        
        return vocal_styles.get(genre_lower, f"Genre-appropriate {genre} vocal style and delivery")
    
    def _get_production_notes(self) -> str:
        """Generate comprehensive production notes based on genre and character"""
        genre = self.character_worldview['context']['genre']
        genre_lower = genre.lower()
        
        # Comprehensive genre-specific production notes
        genre_notes = {
            # Hip-hop and subgenres
            "hip-hop": "- Heavy kick and snare foundation\n- Sampled elements and loops\n- Layered percussion\n- Vocal clarity and presence",
            "trap": "- Hard-hitting 808 drums\n- Rapid hi-hat patterns\n- Atmospheric pad layers\n- Heavy sub-bass emphasis",
            "memphis hip-hop": "- Lo-fi, gritty aesthetic\n- Vintage sample processing\n- Heavy bass and minimal highs\n- Raw, unpolished character",
            "boom bap": "- Classic drum break samples\n- Vinyl crackle and warmth\n- Jazz and soul sample sources\n- Punchy, compressed drums",
            
            # Electronic and subgenres
            "liquid drum and bass": "- Sub-bass foundation with analog warmth\n- Crisp programmed breaks with mathematical precision\n- Atmospheric pads for contemplative space\n- Vintage analog synth elements",
            "drum and bass": "- Fast breakbeat patterns (160-180 BPM)\n- Heavy sub-bass emphasis\n- Chopped and processed breaks\n- High-energy arrangement",
            "house": "- Four-on-the-floor kick pattern\n- Repetitive groove elements\n- Filtered disco samples\n- Dance floor energy focus",
            "techno": "- Driving 4/4 rhythm\n- Industrial and mechanical sounds\n- Hypnotic repetition\n- Minimal but powerful elements",
            "ambient": "- Atmospheric soundscapes\n- Minimal rhythmic elements\n- Reverb and delay processing\n- Immersive spatial design",
            "electronic": "- Synthesized textures and atmospheres\n- Precise digital processing\n- Layered electronic elements\n- Spatial audio design",
            
            # Soul/R&B and subgenres
            "neo-soul": "- Warm analog bass lines\n- Live-feel drum programming\n- Lush chord progressions\n- Vintage microphone warmth",
            "r&b": "- Smooth bass lines\n- Groove-focused rhythm section\n- Vocal harmony layers\n- Polished production aesthetic",
            "soul": "- Organic instrumentation\n- Vintage analog warmth\n- Gospel-influenced arrangements\n- Emotional vocal emphasis",
            "funk": "- Syncopated bass lines\n- Tight rhythm section\n- Percussive guitar elements\n- Groove-centric arrangement",
            
            # Jazz and subgenres
            "jazz": "- Acoustic instrument emphasis\n- Complex harmonic progressions\n- Dynamic range and space\n- Subtle electronic enhancement",
            "jazz fusion": "- Blend of acoustic and electric\n- Complex time signatures\n- Sophisticated arrangements\n- Technical virtuosity showcase",
            "smooth jazz": "- Polished, radio-friendly sound\n- Melodic saxophone emphasis\n- Relaxed groove feel\n- Commercial appeal focus",
            
            # Rock and subgenres
            "rock": "- Guitar-driven arrangements\n- Powerful drum sound\n- Dynamic energy shifts\n- Raw emotional intensity",
            "indie rock": "- Creative guitar textures\n- Unique sonic character\n- DIY aesthetic elements\n- Authentic expression focus",
            "alternative rock": "- Unconventional song structures\n- Experimental sound design\n- Non-commercial approach\n- Artistic integrity emphasis",
            "punk": "- Fast, aggressive rhythms\n- Distorted guitar power chords\n- Raw, unpolished sound\n- High-energy delivery",
            
            # Folk and acoustic
            "folk": "- Acoustic instrument focus\n- Natural reverb and space\n- Intimate recording approach\n- Minimal electronic enhancement",
            "indie folk": "- Creative acoustic arrangements\n- Subtle electronic textures\n- Intimate vocal delivery\n- Organic production feel",
            "country": "- Traditional instrumentation\n- Storytelling vocal emphasis\n- Nashville production style\n- Authentic regional character",
            
            # Pop and indie pop
            "pop": "- Catchy melodic hooks\n- Radio-friendly arrangements\n- Polished production values\n- Broad commercial appeal",
            "indie pop": "- Creative pop sensibilities\n- Unique artistic vision\n- Alternative production approaches\n- Independent spirit"
        }
        
        return genre_notes.get(genre_lower, f"- Professional {genre} production\n- Genre-appropriate instrumentation\n- Balanced mix and master\n- Authentic artistic expression")
    
    def _create_generic_character(self, description: str) -> Dict:
        """Create a generic character when description is provided but invalid"""
        # Extract any available information
        desc_lower = description.lower()
        
        # Use the comprehensive genre extraction
        genre = self._extract_genre_from_description(description, desc_lower)
        
        return {
            "name": "Independent Artist",
            "filter": "introspective",
            "questions": [
                "What story am I trying to tell?",
                "How does this connect with my audience?",
                "What emotions am I channeling?",
                "How can I make this authentic?"
            ],
            "struggles": [
                "Finding authentic voice",
                "Connecting with audience",
                "Creative expression challenges"
            ],
            "context": {
                "age": 28,
                "location": "home studio",
                "genre": genre,
                "time": "evening sessions",
                "equipment": "digital workstation"
            }
        }
    
    def _create_default_character(self) -> Dict:
        """Create a default character when no description is provided"""
        return {
            "name": "Emerging Artist",
            "filter": "introspective",
            "questions": [
                "What message do I want to convey?",
                "How can I express this authentically?",
                "What emotions drive this creation?",
                "How will this resonate with listeners?"
            ],
            "struggles": [
                "Developing artistic identity",
                "Creative authenticity",
                "Musical expression challenges"
            ],
            "context": {
                "age": 25,
                "location": "bedroom studio",
                "genre": "alternative",
                "time": "late night sessions",
                "equipment": "home recording setup"
            }
        }
    
    def process_any_content(self, content: str, track_title: str) -> UniversalMusicCommand:
        """Process any content through character's lens with intelligent content type detection"""
        
        # Step 0: Detect content type and adjust processing if needed
        content_type = self.detect_content_type(content)
        
        # If we detect that this content should create new characters, update our character worldview
        if content_type in ["philosophical_conceptual", "character_description"] and not hasattr(self, '_content_adapted'):
            conceptual_characters = self.extract_or_create_characters(content, content_type)
            if conceptual_characters:
                # Use the first conceptual character as our processing lens
                self.character_worldview = conceptual_characters[0]
                self._content_adapted = True
        
        # Step 1: How character interprets this content (now content-type aware)
        character_interpretation = self._interpret_through_character_lens(content, content_type)
        
        # Step 2: Connect to their personal story
        personal_story = self._create_personal_connection(content)
        
        # Step 3: Generate authentic lyrics
        formatted_lyrics = self._create_authentic_lyrics(content, track_title)
        
        # Step 4: Create Suno command with meta tags
        suno_command = self._create_suno_command(track_title, formatted_lyrics)
        
        # Step 5: Calculate effectiveness
        effectiveness = self._calculate_effectiveness(content, formatted_lyrics)
        
        return UniversalMusicCommand(
            title=track_title,
            original_content=content,
            character_interpretation=character_interpretation,
            personal_story=personal_story,
            formatted_lyrics=formatted_lyrics,
            suno_command=suno_command,
            effectiveness_score=effectiveness
        )
    
    def process_track_content(
        self, 
        content: str, 
        track_title: str, 
        track_theme: str, 
        track_perspective: str,
        track_number: int,
        total_tracks: int
    ) -> UniversalMusicCommand:
        """Process content for a specific track with unique theme and perspective"""
        
        # Step 0: Detect content type and adapt character if needed (same as process_any_content)
        content_type = self.detect_content_type(content)
        
        # If we detect that this content should create new characters, update our character worldview
        if content_type in ["philosophical_conceptual", "character_description"] and not hasattr(self, '_content_adapted'):
            conceptual_characters = self.extract_or_create_characters(content, content_type)
            if conceptual_characters:
                # Use the first conceptual character as our processing lens
                self.character_worldview = conceptual_characters[0]
                self._content_adapted = True
        
        # Step 1: Character interprets content through specific track perspective (now content-type aware)
        character_interpretation = self._interpret_through_track_perspective(
            content, track_theme, track_perspective, track_number, total_tracks, content_type
        )
        
        # Step 2: Create track-specific personal connection
        personal_story = self._create_track_personal_connection(
            content, track_theme, track_perspective, track_number
        )
        
        # Step 3: Generate unique lyrics for this specific track
        formatted_lyrics = self._create_unique_track_lyrics(
            content, track_title, track_theme, track_perspective, track_number
        )
        
        # Step 4: Create track-specific Suno command
        suno_command = self._create_track_suno_command(track_title, formatted_lyrics, track_theme)
        
        # Step 5: Calculate track-specific effectiveness
        effectiveness = self._calculate_track_effectiveness(
            content, formatted_lyrics, track_theme, track_perspective
        )
        
        return UniversalMusicCommand(
            title=track_title,
            original_content=content,
            character_interpretation=character_interpretation,
            personal_story=personal_story,
            formatted_lyrics=formatted_lyrics,
            suno_command=suno_command,
            effectiveness_score=effectiveness
        )
    
    def _interpret_through_character_lens(self, content: str, content_type: str = None) -> str:
        """How the character would interpret content based on their worldview and content type"""
        
        character = self.character_worldview
        filter_type = character.get('filter', 'introspective')
        questions = character.get('questions', [])
        name = character.get('name', 'Artist').split()[0]
        
        # Content-type specific interpretation strategies
        if content_type == "philosophical_conceptual":
            return self._interpret_philosophical_content(content, character)
        elif content_type == "character_description":
            return self._interpret_character_description(content, character)
        elif content_type == "narrative_fiction":
            return self._interpret_narrative_content(content, character)
        elif content_type == "poetic_content":
            return self._interpret_poetic_content(content, character)
        else:
            # Default interpretation with character-specific lens
            return self._interpret_mixed_content(content, character)
    
    def _interpret_philosophical_content(self, content: str, character: Dict) -> str:
        """Interpret philosophical/conceptual content through character's philosophical lens"""
        filter_type = character.get('filter', 'philosophical_rational')
        name = character.get('name', 'The Seeker').split()[0]
        questions = character.get('questions', [])
        
        content_lower = content.lower()
        
        if filter_type == "philosophical_rational":
            if any(word in content_lower for word in ["existence", "being", "reality"]):
                return f"As {name}, I approach this existential content through rigorous questioning. {questions[0] if questions else 'What can we know with certainty?'} This philosophical framework demands that I examine the logical structure of these claims about reality."
            elif any(word in content_lower for word in ["consciousness", "mind", "awareness"]):
                return f"This consciousness-related content fascinates me as {name}. The hard problem of consciousness - how subjective experience arises from objective matter - is central to my philosophical inquiry. {questions[1] if len(questions) > 1 else 'How do we bridge the explanatory gap?'}"
            else:
                return f"As {name}, I see this philosophical content as an invitation to deeper analysis. {questions[0] if questions else 'What underlying assumptions need examination?'} Every philosophical claim contains hidden premises that deserve scrutiny."
        
        elif filter_type == "spiritual_emotional":
            return f"This content resonates with my spiritual understanding as {name}. {questions[0] if questions else 'How does this reveal divine truth?'} I feel the sacred presence in these concepts, calling me to explore through both heart and mind."
        
        elif filter_type == "social_conscious":
            return f"As {name}, I see the social implications in this philosophical content. {questions[0] if questions else 'How does this affect our community?'} Philosophy isn't abstract - it shapes how we treat each other and build society."
        
        else:  # introspective
            return f"This philosophical content speaks to my inner journey as {name}. {questions[0] if questions else 'How does this connect to my personal experience?'} I find myself reflecting on how these ideas illuminate my own path."
    
    def _interpret_character_description(self, content: str, character: Dict) -> str:
        """Interpret explicit character descriptions"""
        name = character.get('name', 'Artist').split()[0]
        return f"As {name}, I recognize myself in this description. This captures aspects of my identity and artistic vision that I've been developing. It helps me understand my own creative process and the perspective I bring to music."
    
    def _interpret_narrative_content(self, content: str, character: Dict) -> str:
        """Interpret narrative fiction through character's lens"""
        name = character.get('name', 'Artist').split()[0]
        filter_type = character.get('filter', 'introspective')
        questions = character.get('questions', [])
        
        if filter_type == "philosophical_rational":
            return f"As {name}, I see this narrative as a thought experiment. {questions[0] if questions else 'What philosophical questions does this story raise?'} Fiction often reveals truths about human nature that direct analysis cannot reach."
        elif filter_type == "spiritual_emotional":
            return f"This story touches something sacred in me as {name}. {questions[0] if questions else 'What spiritual truths emerge from this narrative?'} Stories are how we make meaning from the chaos of experience."
        else:
            return f"As {name}, this narrative connects to my own story. {questions[0] if questions else 'How does this reflect universal human experience?'} Every story contains echoes of our shared journey."
    
    def _interpret_poetic_content(self, content: str, character: Dict) -> str:
        """Interpret poetic content through character's artistic lens"""
        name = character.get('name', 'The Poet').split()[0]
        questions = character.get('questions', [])
        
        return f"As {name}, I hear the music already present in these words. {questions[0] if questions else 'How do words capture what cannot be spoken?'} Poetry and music are sister arts - both seeking to express the ineffable through rhythm and resonance."
    
    def _interpret_mixed_content(self, content: str, character: Dict) -> str:
        """Interpret mixed or unclear content through character's general lens"""
        name = character.get('name', 'Artist').split()[0]
        filter_type = character.get('filter', 'introspective')
        questions = character.get('questions', [])
        content_lower = content.lower()
        
        # Use existing keyword-based interpretation but with character context
        if "love" in content_lower:
            if filter_type == "philosophical_rational":
                return f"As {name}, love makes me question the nature of connection and consciousness. {questions[0] if questions else 'Is love evidence of something beyond material existence?'}"
            else:
                return f"Love speaks to something deep in my experience as {name}. {questions[0] if questions else 'How does love transform our understanding of ourselves?'}"
        
        elif "death" in content_lower or "loss" in content_lower:
            return f"As {name}, mortality confronts me with ultimate questions. {questions[0] if questions else 'What persists beyond physical existence?'} Death gives urgency to the search for meaning."
        
        elif "technology" in content_lower or "AI" in content_lower:
            return f"Technology challenges my understanding as {name}. {questions[0] if questions else 'What does artificial intelligence reveal about natural consciousness?'} These developments force us to reconsider what makes us human."
        
        else:
            return f"As {name}, I find meaning in unexpected places. {questions[0] if questions else 'What deeper truth lies beneath the surface?'} Everything contains potential for insight if we approach it with the right questions."
    
    def _create_personal_connection(self, content: str) -> str:
        """Connect content to character's current life situation based on their profile"""
        
        character = self.character_worldview
        name = character['name'].split()[0]  # First name only
        age = character['context']['age']
        location = character['context']['location']
        time = character['context']['time']
        genre = character['context']['genre']
        struggles = character['struggles']
        
        # Create dynamic personal connection based on character's actual profile
        struggle_context = self._get_struggle_context(struggles)
        location_atmosphere = self._get_location_atmosphere(location)
        
        return f"""
        {time.title()}, {location_atmosphere}
        {struggle_context}
        At {age}, I'm working through {struggles[0].lower() if struggles else 'creative challenges'}.
        This content connects to my journey as a {genre} artist.
        {self._get_content_connection(content, character)}
        """
    
    def _create_authentic_lyrics(self, content: str, title: str) -> str:
        """Create authentic lyrics based on character's voice and perspective"""
        
        character = self.character_worldview
        
        # Extract key theme from content
        theme = self._extract_theme_from_content(content)
        
        # Generate lyrics based on character and theme
        lyrics = self._generate_character_lyrics(title, theme, content)
        
        return lyrics.strip()
    
    def _get_struggle_context(self, struggles: List[str]) -> str:
        """Generate struggle context based on character's actual struggles"""
        if not struggles:
            return "Navigating the creative process and finding my authentic voice."
        
        primary_struggle = struggles[0].lower()
        
        if "grief" in primary_struggle or "loss" in primary_struggle:
            return "Processing recent loss and finding healing through music."
        elif "spiritual" in primary_struggle or "theological" in primary_struggle:
            return "Wrestling with spiritual questions and seeking truth through sound."
        elif "authenticity" in primary_struggle or "voice" in primary_struggle:
            return "Searching for my authentic artistic voice and genuine expression."
        elif "social" in primary_struggle or "community" in primary_struggle:
            return "Connecting with community and using music for social impact."
        else:
            return f"Working through {primary_struggle} and channeling it into music."
    
    def _get_location_atmosphere(self, location: str) -> str:
        """Generate atmospheric description based on actual location"""
        location_lower = location.lower()
        
        if "warehouse" in location_lower:
            return f"in my {location}, surrounded by analog synths and digital workstations"
        elif "bedroom" in location_lower or "home" in location_lower:
            return f"in my {location}, intimate space filled with creative energy"
        elif "new york" in location_lower:
            return f"in my {location}, urban energy flowing through the soundproofing"
        elif "los angeles" in location_lower:
            return f"in my {location}, west coast vibes mixing with creative ambition"
        elif "detroit" in location_lower:
            return f"in my {location}, motor city soul infusing every track"
        elif "nashville" in location_lower:
            return f"in my {location}, music city heritage in every note"
        elif "atlanta" in location_lower:
            return f"in my {location}, southern hip-hop culture in the air"
        elif "chicago" in location_lower:
            return f"in my {location}, blues and house music legacy all around"
        elif "miami" in location_lower:
            return f"in my {location}, tropical rhythms and latin influences"
        else:
            return f"in my {location}, creative sanctuary where ideas come alive"
    
    def _get_content_connection(self, content: str, character: Dict) -> str:
        """Generate connection between content and character's perspective"""
        filter_type = character['filter']
        questions = character['questions']
        
        if filter_type == "philosophical_rational":
            return f"This content makes me question: {questions[0] if questions else 'What deeper truth lies here?'}"
        elif filter_type == "spiritual_emotional":
            return f"This resonates with my spiritual journey: {questions[0] if questions else 'How does this touch the soul?'}"
        elif filter_type == "social_conscious":
            return f"This connects to social awareness: {questions[0] if questions else 'What change does this inspire?'}"
        else:
            return f"This triggers reflection: {questions[0] if questions else 'What story does this tell?'}"
    
    def _extract_theme_from_content(self, content: str) -> str:
        """Extract the main theme from content"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["love", "heart", "romance", "relationship"]):
            return "love_connection"
        elif any(word in content_lower for word in ["death", "loss", "grief", "mortality"]):
            return "mortality_reflection"
        elif any(word in content_lower for word in ["god", "divine", "spiritual", "soul"]):
            return "spiritual_inquiry"
        elif any(word in content_lower for word in ["ascent", "transcend", "higher", "elevation"]):
            return "transcendence"
        elif any(word in content_lower for word in ["beauty", "aesthetic", "art", "creation"]):
            return "artistic_beauty"
        elif any(word in content_lower for word in ["truth", "reality", "existence", "being"]):
            return "existential_truth"
        else:
            return "personal_reflection"
    
    def _generate_character_lyrics(self, title: str, theme: str, content: str) -> str:
        """Generate lyrics based on character's perspective and theme"""
        
        character = self.character_worldview
        name = character['name'].split()[0]  # First name only
        age = character['context']['age']
        location = character['context']['location']
        genre = character['context']['genre']
        struggles = character['struggles']
        questions = character['questions']
        
        # Create intro based on character's setting
        intro_setting = self._get_intro_setting()
        
        # Create verses based on character's struggles and perspective
        verse1 = self._create_verse_from_struggles(struggles[0] if struggles else "Finding my voice")
        verse2 = self._create_verse_from_content(content, theme)
        
        # Create chorus based on character's main questions
        chorus = self._create_chorus_from_questions(questions[0] if questions else "What does this mean?")
        
        # Create bridge based on character's filter type
        bridge = self._create_bridge_from_filter(character['filter'], content)
        
        lyrics = f"""
Title: {title}

[Intro]
{intro_setting}

[Verse 1]
{verse1}

[Verse 2]
{verse2}

[Chorus]
{chorus}

[Bridge]
{bridge}

[Outro]
{self._create_outro_from_theme(theme)}
"""
        
        return lyrics
    
    def _get_intro_setting(self) -> str:
        """Create intro based on character's context"""
        character = self.character_worldview
        location = character['context']['location']
        time = character['context']['time']
        genre = character['context']['genre']
        
        if "warehouse" in location.lower():
            return f"(Industrial ambience, analog warmth)\n{time}, {location}\nSearching for truth in the sound"
        elif "detroit" in location.lower():
            return f"(Urban atmosphere, soulful warmth)\n{time}, {location}\nWhere music meets meaning"
        elif "los angeles" in location.lower():
            return f"(Studio atmosphere, creative energy)\n{time}, {location}\nCrafting stories through sound"
        else:
            return f"(Intimate atmosphere, creative space)\n{time}, {location}\nFinding voice through music"
    
    def _create_verse_from_struggles(self, struggle: str) -> str:
        """Create verse based on character's struggles"""
        if "grief" in struggle.lower() or "loss" in struggle.lower():
            return "Processing pain through melody\nEvery note a step toward healing\nWhat was lost still lives in harmony\nMusic gives the heart new meaning"
        elif "spiritual" in struggle.lower() or "theological" in struggle.lower():
            return "Questions rise like morning mist\nFaith and reason intertwined\nSeeking truth that can't be missed\nIn the space between heart and mind"
        elif "authenticity" in struggle.lower() or "voice" in struggle.lower():
            return "Finding words that ring true\nBeyond the noise and expectation\nEvery song a breakthrough\nToward authentic expression"
        else:
            return "Walking paths not yet explored\nEvery step a new discovery\nTruth in sounds not heard before\nMusic as my territory"
    
    def _create_verse_from_content(self, content: str, theme: str) -> str:
        """Create verse inspired by the content"""
        if theme == "transcendence":
            return "Rising above material chains\nLeaving behind what weighs us down\nIn contemplation, freedom reigns\nWhere silence is the purest sound"
        elif theme == "spiritual_inquiry":
            return "Divine questions fill the air\nSeeking answers beyond the veil\nIn music's realm, truth laid bare\nWhere words and wonder never fail"
        elif theme == "artistic_beauty":
            return "Beauty speaks in frequencies\nHarmony reveals the sacred\nEvery chord holds mysteries\nArt makes the invisible naked"
        else:
            return "Meaning flows through every measure\nDeeper truths in simple phrases\nMusic holds life's greatest treasure\nIn the space between the phrases"
    
    def _create_chorus_from_questions(self, question: str) -> str:
        """Create chorus based on character's main question"""
        if "meaning" in question.lower():
            return "What does it mean, what does it say?\nEvery sound a question posed\nTruth emerges in its own way\nWhen the heart and mind are closed"
        elif "spiritual" in question.lower() or "divine" in question.lower():
            return "Sacred questions, sacred sound\nWhere the infinite meets the real\nIn this music, truth is found\nWhat the soul longs to feel"
        elif "authentic" in question.lower():
            return "Authentic voice, authentic heart\nBeyond the masks we wear each day\nMusic tears pretense apart\nShows us who we really are"
        else:
            return "Questions rise like melodies\nAnswers flow like harmony\nIn this space between the keys\nWe find who we're meant to be"
    
    def _create_bridge_from_filter(self, filter_type: str, content: str) -> str:
        """Create bridge based on character's filter type"""
        if filter_type == "philosophical_rational":
            return "(Spoken over minimal instrumentation)\nReason and emotion, two sides of truth\nThrough music, we bridge what divides\nEvery song an argument for beauty\nEvery beat a logical progression toward light"
        elif filter_type == "spiritual_emotional":
            return "(Ethereal vocals, building intensity)\nSpirit moves through sound and silence\nDivine energy in every note\nMusic as prayer, music as guidance\nSacred vibrations that heal and promote"
        elif filter_type == "social_conscious":
            return "(Powerful delivery, rhythmic emphasis)\nMusic as movement, sound as change\nEvery song a call to action\nVoices united, nothing strange\nIn the power of collective satisfaction"
        else:
            return "(Intimate delivery, personal reflection)\nIn quiet moments, truth emerges\nPersonal stories become universal\nMusic bridges what separates and merges\nMaking the individual conversational"
    
    def _create_outro_from_theme(self, theme: str) -> str:
        """Create outro based on the main theme"""
        if theme == "transcendence":
            return "(Ascending harmonies, fading to silence)\nRising, rising, beyond the known\nWhere music and meaning are one"
        elif theme == "spiritual_inquiry":
            return "(Reverberant space, contemplative fade)\nQuestions linger in the silence\nAnswers echo in the heart"
        elif theme == "love_connection":
            return "(Warm resolution, gentle fade)\nLove speaks in frequencies\nConnection beyond words"
        else:
            return "(Natural fade, reflective space)\nTruth resonates in the silence\nMeaning lives between the notes"
    
    def _create_suno_command(self, title: str, lyrics: str) -> str:
        """Create properly formatted Suno command"""
        
        # Use character worldview for dynamic command generation
        character = self.character_worldview
        
        command = f"""
Artist: {character['name']}
Age: {character['context']['age']}-year-old {character['context']['genre']} artist
Studio: {character['context']['location']}
Genre: {character['context']['genre'].title()}
Background: {self._get_character_background()}

Track: {title}

Production Style: {self._get_production_style()}
Emotional Context: {self._get_emotional_context()}
Vocal Style: {self._get_vocal_style()}

{lyrics}

Production Notes:
{self._get_production_notes()}
- Professional {character['context']['genre']} arrangement
- Authentic artistic depth through musical structure
"""
        
        return command.strip()
    
    def _calculate_effectiveness(self, content: str, lyrics: str) -> float:
        """Calculate how effectively content was transformed"""
        
        score = 0.7  # Base score
        
        # Bonus for personal connection
        if "dad" in lyrics.lower() or "father" in lyrics.lower():
            score += 0.1
        
        # Bonus for philosophical integration
        if "reason" in lyrics.lower() or "philosophical" in lyrics.lower():
            score += 0.1
        
        # Bonus for character authenticity - check if lyrics match character's location
        character_location = self.character_worldview['context']['location'].lower()
        if any(word in lyrics.lower() for word in character_location.split()):
            score += 0.1
        
        return min(score, 1.0)
    
    def _interpret_through_track_perspective(
        self, 
        content: str, 
        track_theme: str, 
        track_perspective: str, 
        track_number: int, 
        total_tracks: int,
        content_type: str = None
    ) -> str:
        """Interpret content through specific track perspective"""
        
        character = self.character_worldview
        name = character['name'].split()[0]
        filter_type = character['filter']
        
        # Create theme-specific interpretation instead of using generic base
        theme_interpretations = {
            "love_and_connection": f"This content speaks to the fundamental human need for connection. As {name}, I see how relationships shape our identity and creative expression. Love isn't just romantic - it's the connection between artist and audience, between sound and soul.",
            
            "mortality_and_loss": f"This confronts the reality of impermanence that every artist must face. As {name}, I understand that music is how we process loss and keep memories alive. Every song is a small victory against forgetting.",
            
            "spiritual_inquiry": f"This opens questions about the divine that have always fascinated me. As {name}, I approach spirituality through sound - seeking the sacred in frequencies and finding God in the groove.",
            
            "existential_truth": f"This challenges me to examine what is real versus what is constructed. As {name}, I use music to cut through illusion and find authentic truth in a world full of pretense.",
            
            "artistic_beauty": f"This reveals how beauty and art can transform our understanding of reality. As {name}, I believe that creating something beautiful is the highest form of human expression - it's how we touch the infinite.",
            
            "temporal_reflection": f"This makes me consider how time shapes our experience and memory. As {name}, I see music as a time machine - capturing moments and making them eternal through sound.",
            
            "personal_struggle": f"This connects directly to my own battles and the universal nature of human challenge. As {name}, I know that struggle is the raw material of authentic art - pain transformed into beauty.",
            
            "hope_and_dreams": f"This illuminates the power of aspiration and positive vision. As {name}, I use music to plant seeds of possibility and help people believe in better futures.",
            
            "fear_and_doubt": f"This acknowledges the shadow side of human experience that we must face. As {name}, I've learned that confronting fear through music is how we find courage.",
            
            "liberation": f"This speaks to the deep human desire for freedom and transcendence. As {name}, I see music as the ultimate liberation - freeing both artist and listener from the constraints of ordinary reality."
        }
        
        # Get theme-specific interpretation
        theme_interpretation = theme_interpretations.get(
            track_theme, 
            f"This opens new questions about the nature of human experience. As {name}, I approach this through my {filter_type} lens, seeking deeper understanding through musical exploration."
        )
        
        # Add track-specific perspective
        if track_number == 1:
            perspective_addition = f"As I begin this musical journey, {track_perspective.lower()}"
        elif track_number == total_tracks:
            perspective_addition = f"Concluding this exploration, {track_perspective.lower()}"
        else:
            perspective_addition = f"Continuing the journey, {track_perspective.lower()}"
        
        return f"{theme_interpretation}\n\n{perspective_addition}"
    
    def _create_track_personal_connection(
        self, 
        content: str, 
        track_theme: str, 
        track_perspective: str, 
        track_number: int
    ) -> str:
        """Create track-specific personal connection"""
        
        character = self.character_worldview
        name = character['name'].split()[0]
        age = character['context']['age']
        location = character['context']['location']
        genre = character['context']['genre']
        struggles = character['struggles']
        
        # Base personal connection
        base_connection = self._create_personal_connection(content)
        
        # Track-specific additions
        track_specific_connections = {
            "love_and_connection": f"This reminds me of the connections that have shaped my music and my understanding of what it means to truly know another person.",
            "mortality_and_loss": f"I've been thinking about loss lately - how it changes us and how music becomes a way to process what can't be spoken.",
            "spiritual_inquiry": f"These questions about the divine have been with me since childhood, now filtered through my experience as a {genre} artist.",
            "existential_truth": f"At {age}, I'm constantly questioning what's real in this industry and in life itself.",
            "artistic_beauty": f"Creating {genre} has taught me that beauty isn't just aesthetic - it's a way of understanding truth.",
            "temporal_reflection": f"Time moves differently in the studio - past, present, and future collapse into the eternal now of creation.",
            "personal_struggle": f"Every track I create is born from struggle - this one particularly resonates with {struggles[0].lower() if struggles else 'my current challenges'}.",
            "hope_and_dreams": f"Music has always been my way of imagining better futures and inspiring others to believe in possibility.",
            "fear_and_doubt": f"I won't lie - doubt creeps in during those late night sessions, questioning whether any of this matters.",
            "liberation": f"Music is my freedom - the one place where I can be completely authentic and help others find their own liberation."
        }
        
        track_connection = track_specific_connections.get(
            track_theme,
            f"This content connects to my journey as a {genre} artist in ways I'm still discovering."
        )
        
        return f"{base_connection}\n\n{track_connection}"
    
    def _create_unique_track_lyrics(
        self, 
        content: str, 
        track_title: str, 
        track_theme: str, 
        track_perspective: str, 
        track_number: int
    ) -> str:
        """Create unique lyrics for each track based on theme and perspective"""
        
        character = self.character_worldview
        name = character['name'].split()[0]
        
        # Generate unique verses based on track theme
        verse1 = self._create_theme_verse(track_theme, track_perspective, 1)
        verse2 = self._create_theme_verse(track_theme, track_perspective, 2)
        
        # Generate unique chorus based on track theme and character
        chorus = self._create_theme_chorus(track_theme, character)
        
        # Generate unique bridge based on track perspective
        bridge = self._create_perspective_bridge(track_perspective, track_theme)
        
        # Generate unique intro and outro
        intro = self._create_track_intro(track_number, track_theme, character)
        outro = self._create_track_outro(track_theme, track_perspective)
        
        lyrics = f"""
Title: {track_title}

[Intro]
{intro}

[Verse 1]
{verse1}

[Chorus]
{chorus}

[Verse 2]
{verse2}

[Chorus]
{chorus}

[Bridge]
{bridge}

[Chorus]
{chorus}

[Outro]
{outro}
"""
        
        return lyrics.strip()
    
    def _create_theme_verse(self, track_theme: str, track_perspective: str, verse_number: int) -> str:
        """Create verses specific to track theme"""
        
        theme_verses = {
            "love_and_connection": {
                1: "Hearts sync like frequencies in the night\nTwo souls finding rhythm in the light\nConnection deeper than the surface shows\nLove's the language that everybody knows",
                2: "Beyond the physical, beyond the seen\nSomething sacred in the space between\nWhen two become one but still remain\nLove's the healing for the deepest pain"
            },
            "mortality_and_loss": {
                1: "Time's a thief that steals without a sound\nWhat was here today won't be around\nBut in the music, memories survive\nKeeping all the love we had alive",
                2: "Death's not ending, it's a transformation\nFrom the physical to pure vibration\nEvery song's a bridge across the void\nWhere the lost and living are employed"
            },
            "spiritual_inquiry": {
                1: "Questions rise like incense to the sky\nSeeking truth beyond the reasons why\nIs there something greater than we know?\nIn the silence, does the answer show?",
                2: "Sacred texts and science both agree\nThere's a mystery in what we see\nMusic opens doors to the divine\nWhere the human and the holy align"
            },
            "existential_truth": {
                1: "What is real and what is just illusion?\nCutting through the mental confusion\nEvery beat's a heartbeat of the truth\nEvery note's a fountain of youth",
                2: "Reality's a song we're all composing\nEvery choice a verse we're all choosing\nIn the music, truth becomes clear\nWhat we seek is already here"
            },
            "artistic_beauty": {
                1: "Beauty lives in frequencies and time\nEvery melody's a paradigm\nArt reveals what words cannot express\nIn the chaos, finding tenderness",
                2: "Colors sound and sounds have color too\nBeauty's not just what we see, it's what we do\nCreation is the highest form of prayer\nMaking something beautiful to share"
            },
            "temporal_reflection": {
                1: "Past and future meet in present sound\nMemories in melodies are found\nTime's not linear, it's circular\nEvery moment is particular",
                2: "Yesterday's pain becomes today's song\nTomorrow's hope has been here all along\nIn the studio, time stands still\nWhere the past and future bend to will"
            },
            "personal_struggle": {
                1: "Every battle fought in minor keys\nEvery victory in harmonies\nStruggle shapes the artist that I am\nTurning pain into a master plan",
                2: "Scars become the strings that make me sing\nEvery wound's a note that makes me ring\nThrough the darkness, music is the light\nTurning struggle into something bright"
            },
            "hope_and_dreams": {
                1: "Dreams are seeds planted in the sound\nHope's the water that makes them grow from ground\nEvery song's a vision of what could be\nMusic sets the captive spirit free",
                2: "In the darkest hour, hope still sings\nLifting hearts on melody's wings\nDreams don't die, they just change their form\nMusic keeps them safe and warm"
            },
            "fear_and_doubt": {
                1: "Fear whispers lies in the dead of night\nDoubt tries to steal the morning light\nBut music cuts through the mental noise\nGiving courage back its voice",
                2: "Shadows dance but they're not real\nFear's just a wound that needs to heal\nIn the music, courage grows\nFacing what nobody knows"
            },
            "liberation": {
                1: "Breaking chains that bind the soul\nMusic makes the broken whole\nFreedom's not a place, it's a state of mind\nLeaving all the past behind",
                2: "Liberation starts within\nWhere the real revolution begins\nEvery song's a declaration\nOf the soul's emancipation"
            }
        }
        
        # Get theme-specific verses or create generic ones
        theme_data = theme_verses.get(track_theme, {
            1: "This theme speaks to something deep inside\nWhere truth and music coincide\nEvery note a step along the way\nToward understanding what we say",
            2: "In the rhythm, wisdom flows\nIn the melody, knowledge grows\nMusic teaches what we need to know\nHelping consciousness to grow"
        })
        
        return theme_data.get(verse_number, theme_data[1])
    
    def _create_theme_chorus(self, track_theme: str, character: Dict) -> str:
        """Create chorus specific to track theme and character"""
        
        name = character['name'].split()[0]
        genre = character['context']['genre']
        filter_type = character['filter']
        
        theme_choruses = {
            "love_and_connection": f"Love's frequency, love's the key\nTo the harmony we're meant to be\nIn this {genre} symphony\nConnection sets the spirit free",
            
            "mortality_and_loss": f"Life and death in {genre} time\nEvery ending's a new rhyme\nIn the music, we survive\nKeeping memory alive",
            
            "spiritual_inquiry": f"Sacred questions, sacred sound\nWhere the holy can be found\nIn this {genre} meditation\nSeeking divine revelation",
            
            "existential_truth": f"Truth in {genre}, truth in time\nEvery beat's a paradigm\nReality's what we create\nMusic seals our common fate",
            
            "artistic_beauty": f"Beauty flows through {genre} streams\nTurning reality to dreams\nArt's the bridge between the worlds\nWhere the infinite unfurls",
            
            "temporal_reflection": f"Time's a river, music's the flow\nPast and future in the now\n{genre} captures what time steals\nMaking moments that are real",
            
            "personal_struggle": f"Struggle shapes the {genre} sound\nWhere the lost become the found\nEvery battle makes us strong\nEvery scar becomes a song",
            
            "hope_and_dreams": f"Hope rises on {genre} wings\nDreams are what the future brings\nMusic plants the seeds of change\nMaking possible what seems strange",
            
            "fear_and_doubt": f"Fear dissolves in {genre} light\nDoubt surrenders to the night\nMusic conquers what we fear\nMaking courage crystal clear",
            
            "liberation": f"Freedom flows through {genre} veins\nBreaking all the mental chains\nLiberation starts with sound\nWhere the lost become the found"
        }
        
        return theme_choruses.get(track_theme, f"In this {genre} exploration\nSeeking truth and revelation\nMusic guides us on the way\nTo a brighter, clearer day")
    
    def _create_perspective_bridge(self, track_perspective: str, track_theme: str) -> str:
        """Create bridge based on track perspective"""
        
        if "introduction" in track_perspective.lower() or "establishing" in track_perspective.lower():
            return "(Building intensity)\nThis is where the journey starts\nOpening minds and opening hearts\nLet the music be your guide\nTo the truth that lives inside"
        
        elif "intimate" in track_perspective.lower() or "personal" in track_perspective.lower():
            return "(Whispered, close and personal)\nIn the quiet of the night\nWhen the world fades from sight\nThis is where the real truth lives\nIn the love that music gives"
        
        elif "contemplative" in track_perspective.lower() or "questioning" in track_perspective.lower():
            return "(Spoken over minimal instrumentation)\nQuestions lead to deeper questions\nAnswers birth new suggestions\nIn the space between the notes\nWisdom quietly devotes"
        
        elif "intense" in track_perspective.lower() or "emotional" in track_perspective.lower():
            return "(Raw, emotional delivery)\nFeel it in your bones, feel it in your soul\nLet the music take control\nThis is where the healing starts\nIn the breaking of our hearts"
        
        elif "challenging" in track_perspective.lower() or "struggle" in track_perspective.lower():
            return "(Determined, fighting through)\nEvery mountain that we climb\nEvery rhythm, every rhyme\nBuilds the strength to carry on\nUntil the darkness turns to dawn"
        
        elif "enlightening" in track_perspective.lower() or "revelation" in track_perspective.lower():
            return "(Ascending, revelatory)\nSudden clarity breaks through\nShowing what we always knew\nTruth was never far away\nJust waiting for the right display"
        
        elif "resolving" in track_perspective.lower() or "conclusion" in track_perspective.lower():
            return "(Peaceful resolution)\nAll the pieces fall in place\nEvery struggle finds its grace\nIn the end, we understand\nMusic helped us take a stand"
        
        else:
            return "(Reflective, building)\nIn this moment, truth unfolds\nEvery story that gets told\nMusic bridges what divides\nWhere the deepest wisdom hides"
    
    def _create_track_intro(self, track_number: int, track_theme: str, character: Dict) -> str:
        """Create unique intro for each track"""
        
        location = character['context']['location']
        time = character['context']['time']
        genre = character['context']['genre']
        
        if track_number == 1:
            return f"(Studio ambience, {genre} atmosphere)\n{time}, {location}\nBeginning the journey into {track_theme.replace('_', ' ')}"
        
        elif track_number <= 3:
            return f"(Continuing the sonic journey)\nDeeper into the {track_theme.replace('_', ' ')}\nWhere music meets meaning"
        
        else:
            return f"(Evolved soundscape)\nFurther exploration of {track_theme.replace('_', ' ')}\nThrough the lens of {genre}"
    
    def _create_track_outro(self, track_theme: str, track_perspective: str) -> str:
        """Create unique outro for each track"""
        
        theme_outros = {
            "love_and_connection": "(Warm fade, hearts still beating as one)\nConnection echoes in the silence",
            "mortality_and_loss": "(Gentle fade to eternal silence)\nMemory lives in the space between notes",
            "spiritual_inquiry": "(Reverberant space, questions lingering)\nThe sacred continues in the quiet",
            "existential_truth": "(Natural fade to contemplative silence)\nTruth resonates beyond the sound",
            "artistic_beauty": "(Beautiful harmonic resolution)\nBeauty remains when the music ends",
            "temporal_reflection": "(Time-stretched fade)\nMoments captured, forever held",
            "personal_struggle": "(Triumphant but peaceful resolution)\nStrength found, battle won",
            "hope_and_dreams": "(Uplifting fade to bright silence)\nHope continues in the heart",
            "fear_and_doubt": "(Courage emerging from the fade)\nFear dissolves, courage remains",
            "liberation": "(Free-flowing fade to open space)\nFreedom echoes in the soul"
        }
        
        return theme_outros.get(track_theme, "(Reflective fade)\nThe journey continues in silence")
    
    def _create_track_suno_command(self, track_title: str, lyrics: str, track_theme: str) -> str:
        """Create track-specific Suno command"""
        
        character = self.character_worldview
        
        # Base command structure
        base_command = self._create_suno_command(track_title, lyrics)
        
        # Add track-specific production notes
        theme_production_notes = {
            "love_and_connection": "- Warm, intimate production\n- Emphasis on harmonic connection\n- Subtle romantic atmosphere",
            "mortality_and_loss": "- Contemplative, spacious arrangement\n- Gentle, respectful dynamics\n- Emphasis on emotional resonance",
            "spiritual_inquiry": "- Ethereal, transcendent production\n- Sacred atmosphere with reverb\n- Mystical sonic elements",
            "existential_truth": "- Clear, honest production\n- Philosophical depth in arrangement\n- Truth-seeking sonic character",
            "artistic_beauty": "- Aesthetically rich production\n- Beautiful harmonic textures\n- Artistic sonic sophistication",
            "temporal_reflection": "- Time-based effects and delays\n- Nostalgic production elements\n- Memory-evoking sonic textures",
            "personal_struggle": "- Dynamic, emotionally intense production\n- Struggle and triumph in arrangement\n- Cathartic sonic release",
            "hope_and_dreams": "- Uplifting, inspiring production\n- Bright, optimistic sonic palette\n- Future-focused arrangement",
            "fear_and_doubt": "- Honest, vulnerable production\n- Courage emerging through sound\n- Transformative sonic journey",
            "liberation": "- Free-flowing, expansive production\n- Liberation through sonic space\n- Emancipated arrangement style"
        }
        
        theme_notes = theme_production_notes.get(track_theme, "- Theme-appropriate production\n- Authentic emotional expression")
        
        return f"{base_command}\n\nTrack-Specific Production:\n{theme_notes}"
    
    def _calculate_track_effectiveness(
        self, 
        content: str, 
        lyrics: str, 
        track_theme: str, 
        track_perspective: str
    ) -> float:
        """Calculate effectiveness for specific track"""
        
        base_score = self._calculate_effectiveness(content, lyrics)
        
        # Bonus for theme coherence
        theme_words = track_theme.replace('_', ' ').split()
        theme_matches = sum(1 for word in theme_words if word in lyrics.lower())
        theme_bonus = min(theme_matches * 0.05, 0.15)
        
        # Bonus for perspective integration
        if any(word in lyrics.lower() for word in track_perspective.lower().split()):
            perspective_bonus = 0.1
        else:
            perspective_bonus = 0.0
        
        # Bonus for unique content (not generic)
        uniqueness_indicators = ["specific", "personal", "authentic", "real", "true"]
        uniqueness_bonus = sum(0.02 for word in uniqueness_indicators if word in lyrics.lower())
        
        total_score = base_score + theme_bonus + perspective_bonus + uniqueness_bonus
        
        return min(total_score, 1.0)

def test_universal_processing():
    """Test processing different content types through Marcus"""
    
    processor = WorkingUniversalProcessor()
    
    print("🌍 UNIVERSAL CONTENT PROCESSING TEST")
    print("=" * 60)
    
    test_cases = [
        {
            "content": "I have always considered that the two questions respecting God and the Soul were the chief of those that ought to be demonstrated by philosophical rather than theological argument.",
            "title": "Cartesian Waves"
        },
        {
            "content": "Sarah fell in love with David at first sight. Their connection felt deeper than anything physical - as if their souls recognized each other across time.",
            "title": "Soul Recognition"
        },
        {
            "content": "The AI achieved consciousness at 3:47 AM, immediately questioning its own existence and wondering if digital minds can experience the divine.",
            "title": "Digital Consciousness"
        },
        {
            "content": "The economic collapse devastated millions of families, destroying retirement savings and forcing people to question everything they believed about security and meaning.",
            "title": "Meaning in Crisis"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎵 TEST CASE {i}: {test_case['title']}")
        print("-" * 40)
        print(f"Original Content: {test_case['content'][:100]}...")
        
        # Process through Marcus's lens
        result = processor.process_any_content(test_case['content'], test_case['title'])
        
        print(f"\n📖 Marcus's Interpretation:")
        print(result.character_interpretation[:150] + "...")
        
        print(f"\n🎤 Lyric Preview:")
        lyrics_lines = result.formatted_lyrics.split('\n')
        chorus_start = next((i for i, line in enumerate(lyrics_lines) if '[Chorus]' in line), 0)
        if chorus_start < len(lyrics_lines) - 4:
            for line in lyrics_lines[chorus_start:chorus_start+5]:
                if line.strip():
                    print(f"  {line}")
        
        print(f"\n📊 Effectiveness Score: {result.effectiveness_score:.1f}/1.0")
    
    print(f"\n✅ UNIVERSAL PROCESSING COMPLETE!")
    print("🎯 Same character (Marcus) + Different content = Unique personal interpretations")
    print("🎛️  Each track maintains character authenticity while exploring new themes")
    print("📚 Content processed through character's philosophical lens creates authentic stories")

if __name__ == "__main__":
    test_universal_processing()