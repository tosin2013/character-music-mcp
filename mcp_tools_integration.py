#!/usr/bin/env python3
"""
MCP Tools Integration with Error Handling

This module demonstrates how to integrate the comprehensive error handling system
with existing MCP tools and provides enhanced versions of key tools.
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from fastmcp import Context

# Import error handling components
from mcp_error_handler import get_error_handler
from mcp_error_recovery import get_recovery_system
from mcp_tool_decorator import (
    character_analysis_tool,
    persona_generation_tool, 
    command_generation_tool,
    creative_generation_tool,
    workflow_tool,
    mcp_tool_with_error_handling
)

# Import existing components (these would be the actual imports in the real system)
try:
    from standard_character_profile import StandardCharacterProfile
    from enhanced_character_analyzer import EnhancedCharacterAnalyzer
    from working_universal_processor import WorkingUniversalProcessor
except ImportError:
    # Fallback for testing
    StandardCharacterProfile = None
    EnhancedCharacterAnalyzer = None
    WorkingUniversalProcessor = None

class EnhancedMCPTools:
    """Enhanced MCP tools with comprehensive error handling and workflow coordination"""
    
    def __init__(self):
        self.error_handler = get_error_handler()
        self.recovery_system = get_recovery_system()
        
        # Initialize workflow state management
        self.workflow_state = {}
        self.content_type_cache = {}
        self.processing_strategies = {
            "narrative_fiction": self._process_narrative_content,
            "character_description": self._process_character_description,
            "philosophical_conceptual": self._process_conceptual_content,
            "poetic_content": self._process_poetic_content,
            "concept_outline": self._process_concept_outline,
            "mixed_content": self._process_mixed_content,
            "hybrid_processing": self._process_hybrid_content,
            "adaptive_processing": self._process_adaptive_content
        }
        
        # Initialize input format detection and routing
        self.format_detectors = {
            "character_description": self._detect_character_description,
            "narrative_fiction": self._detect_narrative_fiction,
            "philosophical_conceptual": self._detect_philosophical_content,
            "poetic_content": self._detect_poetic_content,
            "concept_outline": self._detect_concept_outline
        }
        
        # Initialize components with error handling
        try:
            self.character_analyzer = EnhancedCharacterAnalyzer() if EnhancedCharacterAnalyzer else None
            self.universal_processor = WorkingUniversalProcessor() if WorkingUniversalProcessor else None
        except Exception as e:
            self.error_handler.logger.warning(f"Could not initialize components: {e}")
            self.character_analyzer = None
            self.universal_processor = None
    
    @workflow_tool
    async def detect_input_format_and_route(self, text: str, user_preference: str = None, ctx: Context = None) -> str:
        """
        Detect input format and route to appropriate processing strategy
        
        This implements requirement 8.1: Detect and route different input formats appropriately
        
        Args:
            text: Input text to analyze and route
            user_preference: Optional user-specified processing preference
            ctx: Context for logging
            
        Returns:
            JSON string containing detection results and routing information
        """
        try:
            if ctx:
                await ctx.info(f"Starting input format detection for {len(text)} character text")
            
            # Validate input
            if not text or not text.strip():
                return json.dumps({
                    "error": "Empty input",
                    "clarification_needed": True,
                    "suggested_clarifications": ["Please provide content to analyze"]
                })
            
            # Use universal processor for enhanced detection
            if self.universal_processor:
                routing_result = self.universal_processor.route_content_processing(text, user_preference)
            else:
                # Fallback detection
                routing_result = await self._fallback_format_detection(text, user_preference)
            
            # Cache the detection result for subsequent processing
            content_hash = hash(text)
            self.content_type_cache[content_hash] = routing_result
            
            if ctx:
                detection = routing_result.get("detection_result", {})
                await ctx.info(f"Detected content type: {detection.get('content_type', 'unknown')} "
                             f"(confidence: {detection.get('confidence', 0.0):.2f})")
            
            return json.dumps(routing_result, indent=2)
            
        except Exception as e:
            if ctx:
                await ctx.error(f"Format detection failed: {str(e)}")
            raise
    
    @character_analysis_tool
    async def analyze_character_text_enhanced(self, text: str, processing_strategy: str = None, ctx: Context = None) -> str:
        """
        Enhanced character analysis with flexible input processing strategies
        
        This version includes:
        - Input format detection and routing
        - Multiple processing strategies
        - Detailed error logging
        - Format validation
        - Character detection recovery
        - Graceful degradation
        """
        try:
            if ctx:
                await ctx.info(f"Starting enhanced character analysis for {len(text)} character text")
            
            # Validate input
            if not text or not text.strip():
                raise ValueError("Text input is empty or contains only whitespace")
            
            if len(text.strip()) < 10:
                raise ValueError("Text input is too short for meaningful character analysis")
            
            # Check cache for previous detection results
            content_hash = hash(text)
            routing_result = self.content_type_cache.get(content_hash)
            
            # If no cached result, perform detection
            if not routing_result:
                if self.universal_processor:
                    routing_result = self.universal_processor.route_content_processing(text, processing_strategy)
                else:
                    routing_result = await self._fallback_format_detection(text, processing_strategy)
            
            # Route to appropriate processing method
            detection_result = routing_result.get("detection_result", {})
            content_type = detection_result.get("content_type", "mixed_content")
            
            if ctx:
                await ctx.info(f"Processing as {content_type} with strategy: {detection_result.get('processing_strategy', 'unknown')}")
            
            # Use appropriate processing strategy
            if content_type in self.processing_strategies:
                result = await self.processing_strategies[content_type](text, detection_result, ctx)
            else:
                result = await self._process_mixed_content(text, detection_result, ctx)
            
            # Add detection metadata to result
            result["detection_metadata"] = detection_result
            
            if ctx:
                await ctx.info(f"Character analysis completed successfully")
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            # Error handling is managed by the decorator
            raise
    
    # Input format detection methods
    def _detect_character_description(self, text: str) -> float:
        """Detect if text contains explicit character descriptions"""
        text_lower = text.lower()
        indicators = [
            "character:", "protagonist:", "artist:", "musician:", "producer:",
            "year-old", "years old", "born in", "grew up", "personality:", "background:"
        ]
        return min(sum(1 for indicator in indicators if indicator in text_lower) / 5.0, 1.0)
    
    def _detect_narrative_fiction(self, text: str) -> float:
        """Detect if text contains narrative fiction elements"""
        text_lower = text.lower()
        indicators = [
            "once upon", "chapter", "he said", "she said", "walked", "looked", "thought"
        ]
        return min(sum(1 for indicator in indicators if indicator in text_lower) / 4.0, 1.0)
    
    def _detect_philosophical_content(self, text: str) -> float:
        """Detect if text contains philosophical or conceptual content"""
        text_lower = text.lower()
        indicators = [
            "philosophy", "concept", "meaning", "existence", "consciousness", "reality"
        ]
        return min(sum(1 for indicator in indicators if indicator in text_lower) / 3.0, 1.0)
    
    def _detect_poetic_content(self, text: str) -> float:
        """Detect if text contains poetic content"""
        text_lower = text.lower()
        has_line_breaks = "/" in text or "\n" in text
        poetic_words = ["poem", "poetry", "verse", "metaphor", "imagery"]
        score = sum(1 for word in poetic_words if word in text_lower) / 3.0
        if has_line_breaks and len(text.split()) < 150:
            score += 0.3
        return min(score, 1.0)
    
    def _detect_concept_outline(self, text: str) -> float:
        """Detect if text is structured as a concept outline"""
        outline_indicators = ["1.", "2.", "3.", "•", "-", "a)", "b)", "outline:", "structure:"]
        return min(sum(1 for indicator in outline_indicators if indicator in text) / 4.0, 1.0)
    
    # Processing strategy methods
    async def _process_character_description(self, text: str, detection_result: Dict, ctx: Context = None) -> Dict:
        """Process explicit character descriptions"""
        if ctx:
            await ctx.info("Processing explicit character description")
        
        if self.universal_processor:
            characters = self.universal_processor.extract_or_create_characters(text, detection_result)
        else:
            characters = [{"name": "Described Character", "type": "explicit_description"}]
        
        return {
            "characters": characters,
            "processing_method": "explicit_description",
            "confidence": detection_result.get("confidence", 0.8)
        }
    
    async def _process_narrative_content(self, text: str, detection_result: Dict, ctx: Context = None) -> Dict:
        """Process narrative fiction content"""
        if ctx:
            await ctx.info("Processing narrative fiction content")
        
        if self.universal_processor:
            characters = self.universal_processor.extract_or_create_characters(text, detection_result)
        else:
            characters = [{"name": "Narrative Character", "type": "extracted_from_narrative"}]
        
        return {
            "characters": characters,
            "processing_method": "narrative_extraction",
            "confidence": detection_result.get("confidence", 0.7)
        }
    
    async def _process_conceptual_content(self, text: str, detection_result: Dict, ctx: Context = None) -> Dict:
        """Process philosophical/conceptual content"""
        if ctx:
            await ctx.info("Processing philosophical/conceptual content")
        
        if self.universal_processor:
            characters = self.universal_processor.extract_or_create_characters(text, detection_result)
        else:
            characters = [{"name": "The Philosopher", "type": "conceptual_character"}]
        
        return {
            "characters": characters,
            "processing_method": "conceptual_creation",
            "confidence": detection_result.get("confidence", 0.6)
        }
    
    async def _process_poetic_content(self, text: str, detection_result: Dict, ctx: Context = None) -> Dict:
        """Process poetic content"""
        if ctx:
            await ctx.info("Processing poetic content")
        
        if self.universal_processor:
            characters = self.universal_processor.extract_or_create_characters(text, detection_result)
        else:
            characters = [{"name": "The Poet", "type": "poetic_character"}]
        
        return {
            "characters": characters,
            "processing_method": "poetic_creation",
            "confidence": detection_result.get("confidence", 0.6)
        }
    
    async def _process_concept_outline(self, text: str, detection_result: Dict, ctx: Context = None) -> Dict:
        """Process structured concept outlines"""
        if ctx:
            await ctx.info("Processing concept outline")
        
        if self.universal_processor:
            characters = self.universal_processor.extract_or_create_characters(text, detection_result)
        else:
            characters = [{"name": "The Architect", "type": "concept_character"}]
        
        return {
            "characters": characters,
            "processing_method": "outline_processing",
            "confidence": detection_result.get("confidence", 0.7)
        }
    
    async def _process_mixed_content(self, text: str, detection_result: Dict, ctx: Context = None) -> Dict:
        """Process mixed or unclear content types"""
        if ctx:
            await ctx.info("Processing mixed content with adaptive strategy")
        
        if self.universal_processor:
            characters = self.universal_processor.extract_or_create_characters(text, detection_result)
        else:
            characters = [{"name": "The Creator", "type": "adaptive_character"}]
        
        return {
            "characters": characters,
            "processing_method": "adaptive_processing",
            "confidence": detection_result.get("confidence", 0.5)
        }
    
    async def _process_hybrid_content(self, text: str, detection_result: Dict, ctx: Context = None) -> Dict:
        """Process content using hybrid approach"""
        if ctx:
            await ctx.info("Processing with hybrid strategy")
        
        if self.universal_processor:
            characters = self.universal_processor.extract_or_create_characters(text, detection_result)
        else:
            characters = [{"name": "Hybrid Character", "type": "hybrid_processing"}]
        
        return {
            "characters": characters,
            "processing_method": "hybrid_processing",
            "confidence": detection_result.get("confidence", 0.6)
        }
    
    async def _process_adaptive_content(self, text: str, detection_result: Dict, ctx: Context = None) -> Dict:
        """Process content using adaptive approach"""
        if ctx:
            await ctx.info("Processing with adaptive strategy")
        
        if self.universal_processor:
            characters = self.universal_processor.extract_or_create_characters(text, detection_result)
        else:
            characters = [{"name": "Adaptive Character", "type": "adaptive_processing"}]
        
        return {
            "characters": characters,
            "processing_method": "adaptive_processing",
            "confidence": detection_result.get("confidence", 0.5)
        }
    
    async def _fallback_format_detection(self, text: str, user_preference: str = None) -> Dict:
        """Fallback format detection when universal processor is not available"""
        detection_scores = {}
        
        for format_name, detector in self.format_detectors.items():
            detection_scores[format_name] = detector(text)
        
        if user_preference and user_preference in detection_scores:
            primary_type = user_preference
            confidence = 1.0
        elif detection_scores:
            primary_type = max(detection_scores.keys(), key=lambda k: detection_scores[k])
            confidence = detection_scores[primary_type]
        else:
            primary_type = "mixed_content"
            confidence = 0.3
        
        return {
            "characters": [],
            "detection_result": {
                "content_type": primary_type,
                "confidence": confidence,
                "processing_strategy": "fallback_processing",
                "detected_formats": [k for k, v in detection_scores.items() if v > 0.2],
                "format_scores": detection_scores,
                "clarification_needed": confidence < 0.6
            },
            "processing_success": True,
            "error_message": None
        }

    @workflow_tool
    async def request_input_clarification(self, text: str, detection_result: str = None, ctx: Context = None) -> str:
        """
        Request clarification from user when input type is unclear
        
        This implements requirement 8.4: Ask clarifying questions rather than making incorrect assumptions
        and requirement 6.2: Provide clear feedback about what went wrong and suggest alternatives
        
        Args:
            text: Original input text that needs clarification
            detection_result: JSON string of detection results (optional)
            ctx: Context for logging
            
        Returns:
            JSON string containing clarification prompts and options
        """
        try:
            if ctx:
                await ctx.info("Generating clarification prompts for ambiguous input")
            
            # Parse detection result if provided
            if detection_result:
                try:
                    detection_data = json.loads(detection_result)
                    detection_info = detection_data.get("detection_result", {})
                except json.JSONDecodeError:
                    detection_info = {}
            else:
                # Perform quick detection if not provided
                if self.universal_processor:
                    detection_info = self.universal_processor.detect_content_type(text)
                else:
                    detection_info = {"content_type": "unknown", "confidence": 0.0}
            
            # Generate clarification prompts based on detection results
            clarification_response = self._generate_clarification_prompts(text, detection_info)
            
            if ctx:
                await ctx.info(f"Generated {len(clarification_response.get('prompts', []))} clarification prompts")
            
            return json.dumps(clarification_response, indent=2)
            
        except Exception as e:
            if ctx:
                await ctx.error(f"Failed to generate clarification prompts: {str(e)}")
            raise
    
    @workflow_tool
    async def process_with_user_guidance(self, text: str, user_choice: str, additional_context: str = "", ctx: Context = None) -> str:
        """
        Process content with user-provided guidance and context
        
        This implements requirement 8.4: Interactive prompts to guide users toward appropriate processing modes
        
        Args:
            text: Original input text to process
            user_choice: User's choice of processing method
            additional_context: Additional context provided by user
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
                "poetic_content", "concept_outline", "mixed_content", "create_new_character"
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
            
            # Process with user-specified strategy
            if self.universal_processor:
                routing_result = self.universal_processor.route_content_processing(enhanced_text, user_choice)
            else:
                routing_result = await self._fallback_format_detection(enhanced_text, user_choice)
            
            # Add user guidance metadata
            routing_result["user_guidance"] = {
                "chosen_method": user_choice,
                "additional_context_provided": bool(additional_context.strip()),
                "guidance_applied": True
            }
            
            if ctx:
                await ctx.info(f"Successfully processed content using {user_choice} method")
            
            return json.dumps(routing_result, indent=2)
            
        except Exception as e:
            if ctx:
                await ctx.error(f"Failed to process with user guidance: {str(e)}")
            raise
    
    def _generate_clarification_prompts(self, text: str, detection_info: Dict) -> Dict:
        """
        Generate helpful clarification prompts based on detection results
        
        Args:
            text: Original input text
            detection_info: Detection analysis results
            
        Returns:
            Dictionary containing clarification prompts and options
        """
        content_type = detection_info.get("content_type", "unknown")
        confidence = detection_info.get("confidence", 0.0)
        ambiguity_score = detection_info.get("ambiguity_score", 0.0)
        detected_formats = detection_info.get("detected_formats", [])
        suggested_clarifications = detection_info.get("suggested_clarifications", [])
        
        # Generate context-specific prompts
        prompts = []
        options = []
        
        if confidence < 0.4:
            # Very low confidence - need basic clarification
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
                    "id": "create_new_character",
                    "label": "Create a new character from this content",
                    "description": "Use this if you want me to create an original character inspired by this material"
                }
            ])
        
        elif ambiguity_score > 0.6:
            # High ambiguity - multiple possible interpretations
            if len(detected_formats) > 1:
                format_list = ", ".join(detected_formats)
                prompts.append(f"I detected multiple content types in your input: {format_list}.")
                prompts.append("Which approach would you prefer?")
                
                for format_type in detected_formats:
                    option = self._create_format_option(format_type)
                    if option:
                        options.append(option)
            
            # Add specific clarification based on detected formats
            if "character_description" in detected_formats and "narrative_fiction" in detected_formats:
                prompts.append("Should I use the character details as provided, or extract characters from the narrative elements?")
            
            if "philosophical_conceptual" in detected_formats:
                prompts.append("Would you like me to create characters that embody these philosophical concepts?")
        
        else:
            # Moderate confidence - just confirm the approach
            prompts.append(f"I think this is {content_type.replace('_', ' ')} content.")
            prompts.append("Is this correct, or would you prefer a different processing approach?")
            
            # Add the detected type as the primary option
            primary_option = self._create_format_option(content_type)
            if primary_option:
                options.append(primary_option)
            
            # Add alternative options
            alternative_formats = ["character_description", "narrative_fiction", "philosophical_conceptual", "mixed_content"]
            for alt_format in alternative_formats:
                if alt_format != content_type:
                    alt_option = self._create_format_option(alt_format)
                    if alt_option:
                        options.append(alt_option)
        
        # Add fallback options
        if not options:
            options.extend([
                {
                    "id": "mixed_content",
                    "label": "Process as mixed content",
                    "description": "Let me try multiple approaches and use the best result"
                },
                {
                    "id": "create_new_character",
                    "label": "Create a new character",
                    "description": "Create an original character inspired by this content"
                }
            ])
        
        # Include original suggested clarifications if available
        if suggested_clarifications:
            prompts.extend(suggested_clarifications)
        
        return {
            "clarification_needed": True,
            "confidence": confidence,
            "ambiguity_score": ambiguity_score,
            "detected_formats": detected_formats,
            "prompts": prompts,
            "options": options,
            "text_preview": text[:200] + "..." if len(text) > 200 else text,
            "guidance": [
                "Select the option that best matches your intent",
                "You can also provide additional context to help me understand better",
                "If none of these options seem right, choose 'mixed content' for adaptive processing"
            ]
        }
    
    def _create_format_option(self, format_type: str) -> Dict:
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
    
    @workflow_tool
    async def provide_processing_guidance(self, content_type: str = None, ctx: Context = None) -> str:
        """
        Provide guidance on different processing modes and when to use them
        
        This implements requirement 6.4: Provide fallback options when automatic content detection fails
        
        Args:
            content_type: Specific content type to get guidance for (optional)
            ctx: Context for logging
            
        Returns:
            JSON string containing processing guidance
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
                        "output": "Uses your character details directly to create music content"
                    },
                    "narrative_fiction": {
                        "when_to_use": "When you have stories, narratives, or fictional content with characters",
                        "examples": [
                            "Story excerpts with dialogue and character actions",
                            "Novel chapters or short stories",
                            "Narrative descriptions of events and characters"
                        ],
                        "output": "Extracts characters from the story and creates music from their perspective"
                    },
                    "philosophical_conceptual": {
                        "when_to_use": "When you have abstract ideas, philosophical content, or conceptual themes",
                        "examples": [
                            "Philosophical essays or excerpts",
                            "Abstract concepts like 'the nature of time'",
                            "Thematic content about existentialism, spirituality, etc."
                        ],
                        "output": "Creates characters that embody and explore these concepts through music"
                    },
                    "poetic_content": {
                        "when_to_use": "When you have poetry, lyrical content, or highly metaphorical text",
                        "examples": [
                            "Poems or verses",
                            "Lyrical content with rich imagery",
                            "Metaphorical or symbolic text"
                        ],
                        "output": "Creates characters from the poetic voice and transforms themes into music"
                    },
                    "concept_outline": {
                        "when_to_use": "When you have structured outlines, lists, or organized conceptual content",
                        "examples": [
                            "Numbered lists of ideas or themes",
                            "Structured outlines of concepts",
                            "Organized frameworks or systems"
                        ],
                        "output": "Processes each concept systematically to create coherent characters"
                    },
                    "mixed_content": {
                        "when_to_use": "When your content combines multiple types or you're unsure",
                        "examples": [
                            "Content that mixes narrative with philosophical elements",
                            "Character descriptions embedded in stories",
                            "Any content that doesn't fit clearly into other categories"
                        ],
                        "output": "Uses adaptive processing to handle multiple content types intelligently"
                    }
                },
                "tips": [
                    "Be as specific as possible about what you want to achieve",
                    "If you're unsure, start with 'mixed_content' for adaptive processing",
                    "You can always provide additional context to guide the processing",
                    "Character descriptions work best when they include age, background, and musical style",
                    "Narrative content works best when it has clear characters and dialogue",
                    "Conceptual content works best when themes are clearly articulated"
                ],
                "troubleshooting": {
                    "empty_results": "Try providing more detailed content or switching to a different processing mode",
                    "generic_output": "Add more specific details about characters, themes, or context",
                    "wrong_interpretation": "Use the clarification system to specify the correct processing approach"
                }
            }
            
            # If specific content type requested, focus on that
            if content_type and content_type in guidance["processing_modes"]:
                focused_guidance = {
                    "requested_mode": content_type,
                    "details": guidance["processing_modes"][content_type],
                    "general_tips": guidance["tips"],
                    "troubleshooting": guidance["troubleshooting"]
                }
                return json.dumps(focused_guidance, indent=2)
            
            return json.dumps(guidance, indent=2)
            
        except Exception as e:
            if ctx:
                await ctx.error(f"Failed to provide processing guidance: {str(e)}")
            raise

    @persona_generation_tool  
    async def generate_artist_personas_enhanced(self, characters_json: str, ctx: Context) -> str:
        """
        Enhanced persona generation with comprehensive error handling
        
        This version includes:
        - JSON parsing error recovery
        - Character profile format validation
        - Persona generation fallbacks
        - Quality scoring
        """
        try:
            await ctx.info("Starting enhanced persona generation")
            
            # Parse and validate characters data
            characters_data = await self._parse_and_validate_characters(characters_json)
            
            # Generate personas with error handling
            personas = []
            for character_data in characters_data.get("characters", []):
                try:
                    persona = await self._generate_single_persona(character_data)
                    personas.append(persona)
                except Exception as e:
                    # Log individual persona generation error but continue
                    self.error_handler.logger.warning(f"Failed to generate persona for character: {e}")
                    # Create fallback persona
                    fallback_persona = await self._create_fallback_persona(character_data)
                    personas.append(fallback_persona)
            
            result = {
                "personas": personas,
                "generation_summary": f"Generated {len(personas)} artist personas",
                "quality_metrics": {
                    "total_personas": len(personas),
                    "successful_generations": len([p for p in personas if not p.get("is_fallback", False)]),
                    "fallback_generations": len([p for p in personas if p.get("is_fallback", False)])
                }
            }
            
            await ctx.info(f"Persona generation completed: {len(personas)} personas created")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            raise
    
    @command_generation_tool
    async def create_suno_commands_enhanced(
        self, 
        personas_json: str, 
        characters_json: str, 
        ctx: Context
    ) -> str:
        """
        Enhanced Suno command generation with comprehensive error handling
        
        This version includes:
        - Multi-input validation
        - Command generation recovery
        - Quality assessment
        - Multiple command variations
        """
        try:
            await ctx.info("Starting enhanced Suno command generation")
            
            # Parse and validate both inputs
            personas_data = await self._parse_and_validate_json(personas_json, "personas")
            characters_data = await self._parse_and_validate_json(characters_json, "characters")
            
            # Generate commands with error handling
            commands = []
            for persona in personas_data.get("personas", []):
                try:
                    persona_commands = await self._generate_commands_for_persona(persona, characters_data)
                    commands.extend(persona_commands)
                except Exception as e:
                    self.error_handler.logger.warning(f"Failed to generate commands for persona: {e}")
                    # Create fallback command
                    fallback_command = await self._create_fallback_command(persona)
                    commands.append(fallback_command)
            
            result = {
                "commands": commands,
                "generation_summary": f"Generated {len(commands)} Suno AI commands",
                "command_quality": {
                    "total_commands": len(commands),
                    "high_quality": len([c for c in commands if c.get("effectiveness_score", 0) > 0.8]),
                    "medium_quality": len([c for c in commands if 0.5 < c.get("effectiveness_score", 0) <= 0.8]),
                    "low_quality": len([c for c in commands if c.get("effectiveness_score", 0) <= 0.5])
                }
            }
            
            await ctx.info(f"Command generation completed: {len(commands)} commands created")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            raise
    
    @creative_generation_tool
    async def creative_music_generation_enhanced(
        self, 
        concept: str, 
        style_preference: str = "any", 
        ctx: Context = None
    ) -> str:
        """
        Enhanced creative music generation with comprehensive error handling
        
        This version includes:
        - Concept analysis validation
        - Creative variation generation
        - Style preference handling
        - Production command optimization
        """
        try:
            if ctx:
                await ctx.info(f"Starting enhanced creative generation for concept: {concept[:50]}...")
            
            # Validate and analyze concept
            if not concept or not concept.strip():
                raise ValueError("Concept input is empty")
            
            # Analyze concept for musical elements
            concept_analysis = await self._analyze_concept_enhanced(concept)
            
            # Generate creative variations
            variations = await self._generate_creative_variations_enhanced(concept_analysis, style_preference)
            
            # Create production commands
            production_commands = await self._create_production_commands_enhanced(variations, concept_analysis)
            
            result = {
                "concept_analysis": concept_analysis,
                "creative_variations": variations,
                "production_commands": production_commands,
                "generation_metadata": {
                    "concept_length": len(concept),
                    "variations_count": len(variations),
                    "commands_count": len(production_commands),
                    "style_preference": style_preference,
                    "quality_score": self._calculate_generation_quality(variations, production_commands)
                }
            }
            
            if ctx:
                await ctx.info("Creative generation completed successfully")
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            raise
    
    @workflow_tool
    async def complete_workflow_enhanced(self, text: str, ctx: Context) -> str:
        """
        Enhanced complete workflow with comprehensive error handling and content type coordination
        
        This version includes:
        - Content type detection and routing
        - Step-by-step error handling with content-aware recovery
        - Workflow state management with context preservation
        - Intelligent fallback processing modes
        """
        try:
            await ctx.info("Starting enhanced complete workflow with content type detection")
            
            # Initialize workflow state with content type detection
            workflow_state = {
                "steps_completed": [],
                "steps_failed": [],
                "partial_results": {},
                "overall_success": False,
                "content_type": None,
                "processing_strategy": None,
                "fallback_attempts": []
            }
            
            # Step 0: Content Type Detection and Strategy Selection
            try:
                await ctx.info("Step 0: Content Type Detection")
                content_type = await self._detect_content_type_enhanced(text)
                processing_strategy = self.processing_strategies.get(content_type, self._process_mixed_content)
                
                workflow_state["content_type"] = content_type
                workflow_state["processing_strategy"] = processing_strategy.__name__
                workflow_state["steps_completed"].append("content_detection")
                
                await ctx.info(f"Detected content type: {content_type}, using strategy: {processing_strategy.__name__}")
                
            except Exception as e:
                workflow_state["steps_failed"].append({"step": "content_detection", "error": str(e)})
                content_type = "mixed_content"
                processing_strategy = self._process_mixed_content
                await ctx.info("Content detection failed, using mixed content strategy")
            
            # Step 1: Content-Aware Character Analysis
            try:
                await ctx.info("Step 1: Content-Aware Character Analysis")
                analysis_result = await self._coordinate_character_analysis(text, content_type, ctx)
                workflow_state["steps_completed"].append("character_analysis")
                workflow_state["partial_results"]["analysis"] = analysis_result
                
            except Exception as e:
                workflow_state["steps_failed"].append({"step": "character_analysis", "error": str(e)})
                # Content-aware fallback
                fallback_result = await self._fallback_character_analysis(text, content_type, e, ctx)
                workflow_state["partial_results"]["analysis"] = fallback_result
                workflow_state["fallback_attempts"].append("character_analysis")
            
            # Step 2: Context-Preserving Persona Generation
            try:
                await ctx.info("Step 2: Context-Preserving Persona Generation")
                personas_result = await self._coordinate_persona_generation(
                    workflow_state["partial_results"]["analysis"], content_type, ctx
                )
                workflow_state["steps_completed"].append("persona_generation")
                workflow_state["partial_results"]["personas"] = personas_result
                
            except Exception as e:
                workflow_state["steps_failed"].append({"step": "persona_generation", "error": str(e)})
                # Content-aware persona fallback
                fallback_result = await self._fallback_persona_generation(
                    workflow_state["partial_results"]["analysis"], content_type, e, ctx
                )
                workflow_state["partial_results"]["personas"] = fallback_result
                workflow_state["fallback_attempts"].append("persona_generation")
            
            # Step 3: Coordinated Album Generation
            try:
                await ctx.info("Step 3: Coordinated Album Generation")
                album_result = await self._coordinate_album_generation(
                    workflow_state["partial_results"]["analysis"],
                    workflow_state["partial_results"]["personas"],
                    content_type,
                    text,
                    ctx
                )
                workflow_state["steps_completed"].append("album_generation")
                workflow_state["partial_results"]["album"] = album_result
                
            except Exception as e:
                workflow_state["steps_failed"].append({"step": "album_generation", "error": str(e)})
                # Album generation fallback
                fallback_result = await self._fallback_album_generation(
                    workflow_state["partial_results"]["analysis"],
                    workflow_state["partial_results"]["personas"],
                    content_type,
                    e,
                    ctx
                )
                workflow_state["partial_results"]["album"] = fallback_result
                workflow_state["fallback_attempts"].append("album_generation")
            
            # Determine overall success
            workflow_state["overall_success"] = len(workflow_state["steps_completed"]) >= 3
            
            result = {
                "workflow_status": "completed" if workflow_state["overall_success"] else "partial",
                "workflow_state": workflow_state,
                "final_results": workflow_state["partial_results"],
                "content_processing": {
                    "detected_type": workflow_state["content_type"],
                    "processing_strategy": workflow_state["processing_strategy"],
                    "fallback_attempts": workflow_state["fallback_attempts"]
                },
                "summary": {
                    "steps_attempted": 4,  # Including content detection
                    "steps_completed": len(workflow_state["steps_completed"]),
                    "steps_failed": len(workflow_state["steps_failed"]),
                    "success_rate": len(workflow_state["steps_completed"]) / 4 * 100,
                    "fallbacks_used": len(workflow_state["fallback_attempts"])
                }
            }
            
            await ctx.info(f"Enhanced workflow completed with {len(workflow_state['steps_completed'])}/4 steps successful")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            raise
    
    # Helper methods for enhanced functionality
    
    async def _analyze_with_enhanced_analyzer(self, text: str) -> Dict[str, Any]:
        """Use enhanced character analyzer with error handling"""
        try:
            return self.character_analyzer.analyze_text(text)
        except Exception as e:
            self.error_handler.logger.warning(f"Enhanced analyzer failed: {e}")
            return await self._analyze_with_fallback_method(text)
    
    async def _analyze_with_fallback_method(self, text: str) -> Dict[str, Any]:
        """Fallback character analysis method"""
        import re
        
        # Simple character detection
        potential_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        characters = []
        
        for name in set(potential_names[:3]):  # Limit to 3 characters
            character = {
                "name": name,
                "aliases": [],
                "physical_description": "",
                "mannerisms": [],
                "speech_patterns": [],
                "behavioral_traits": [],
                "backstory": f"Character mentioned in text as {name}",
                "relationships": [],
                "formative_experiences": [],
                "social_connections": [],
                "motivations": [],
                "fears": [],
                "desires": [],
                "conflicts": [],
                "personality_drivers": [],
                "confidence_score": 0.4,
                "text_references": [name],
                "first_appearance": text[:100],
                "importance_score": 0.5
            }
            characters.append(character)
        
        return {
            "characters": characters,
            "narrative_themes": ["general_narrative"],
            "emotional_arc": ["contemplative"],
            "analysis_method": "fallback",
            "analysis_quality": "basic"
        }
    
    async def _parse_and_validate_characters(self, characters_json: str) -> Dict[str, Any]:
        """Parse and validate characters JSON with error handling"""
        try:
            data = json.loads(characters_json)
            if not isinstance(data, dict):
                raise ValueError("Characters data must be a dictionary")
            if "characters" not in data:
                raise ValueError("Characters data must contain 'characters' key")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
    
    async def _parse_and_validate_json(self, json_str: str, data_type: str) -> Dict[str, Any]:
        """Generic JSON parsing and validation"""
        try:
            data = json.loads(json_str)
            if not isinstance(data, dict):
                raise ValueError(f"{data_type} data must be a dictionary")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format for {data_type}: {str(e)}")
    
    async def _generate_single_persona(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single persona with error handling"""
        # This would use the actual persona generation logic
        # For now, create a basic persona structure
        
        character_name = character_data.get("name", "Unknown Character")
        
        persona = {
            "character_name": character_name,
            "artist_name": f"{character_name} (Artist)",
            "primary_genre": "alternative",
            "secondary_genres": [],
            "vocal_style": "contemplative",
            "instrumental_preferences": ["acoustic"],
            "lyrical_themes": ["introspection", "experience"],
            "emotional_palette": ["contemplative", "thoughtful"],
            "artistic_influences": [],
            "collaboration_style": "solo",
            "character_mapping_confidence": 0.7,
            "genre_justification": f"Alternative genre chosen for {character_name} based on character analysis",
            "persona_description": f"Musical persona derived from character {character_name}"
        }
        
        return persona
    
    async def _create_fallback_persona(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback persona when generation fails"""
        persona = await self._generate_single_persona(character_data)
        persona["is_fallback"] = True
        persona["character_mapping_confidence"] = 0.3
        persona["generation_note"] = "Fallback persona created due to generation error"
        return persona
    
    async def _generate_commands_for_persona(
        self, 
        persona: Dict[str, Any], 
        characters_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate Suno commands for a persona with genre-specific production intelligence"""
        
        # Import genre intelligence
        try:
            from genre_production_intelligence import get_genre_intelligence
            genre_intelligence = get_genre_intelligence()
        except ImportError:
            self.error_handler.logger.warning("Genre production intelligence not available, using basic generation")
            return await self._generate_basic_commands_for_persona(persona, characters_data)
        
        commands = []
        
        # Extract genre and character context
        genre = persona.get('primary_genre', 'alternative')
        character_context = {
            "emotional_state": persona.get('emotional_profile', {}).get('primary_emotion', 'contemplative'),
            "character_name": persona.get('character_name', 'Unknown'),
            "lyrical_themes": persona.get('lyrical_themes', [])
        }
        
        # Create base command text
        base_command = f"Create a song about {persona.get('lyrical_themes', ['life'])[0] if persona.get('lyrical_themes') else 'life'}"
        
        # Enhance command with genre intelligence
        enhanced_command = genre_intelligence.enhance_suno_command(
            base_command, genre, character_context
        )
        
        # Build comprehensive command structure
        command = {
            "command_type": "enhanced",
            "prompt": enhanced_command["command_text"],
            "style_tags": enhanced_command["style_tags"],
            "meta_tags": enhanced_command["meta_tags"],
            "structure_tags": ["verse", "chorus", "bridge"],
            "tempo_bpm": enhanced_command["tempo_suggestion"],
            "tempo_description": enhanced_command["tempo_description"],
            "instrumentation": enhanced_command["instrumentation"],
            "production_notes": enhanced_command["production_notes"],
            "vocal_direction": enhanced_command["vocal_direction"],
            "character_source": persona.get('character_name', 'Unknown'),
            "artist_persona": persona.get('artist_name', 'Unknown Artist'),
            "genre_profile": enhanced_command["genre_profile"],
            "command_rationale": f"Enhanced genre-specific command for {persona.get('character_name', 'character')} in {genre} style",
            "effectiveness_score": 0.85,  # Higher score for enhanced commands
            "variations": self._generate_command_variations(enhanced_command, persona)
        }
        
        commands.append(command)
        
        # Generate additional commands for different lyrical themes
        if persona.get('lyrical_themes') and len(persona['lyrical_themes']) > 1:
            for theme in persona['lyrical_themes'][1:3]:  # Up to 2 additional themes
                theme_command = f"Create a song exploring {theme}"
                theme_enhanced = genre_intelligence.enhance_suno_command(
                    theme_command, genre, {**character_context, "theme": theme}
                )
                
                additional_command = {
                    "command_type": "thematic",
                    "prompt": theme_enhanced["command_text"],
                    "style_tags": theme_enhanced["style_tags"],
                    "meta_tags": theme_enhanced["meta_tags"],
                    "structure_tags": ["verse", "chorus"],
                    "tempo_bpm": theme_enhanced["tempo_suggestion"],
                    "instrumentation": theme_enhanced["instrumentation"][:3],  # Limit for variety
                    "character_source": persona.get('character_name', 'Unknown'),
                    "theme_focus": theme,
                    "effectiveness_score": 0.8,
                    "variations": []
                }
                commands.append(additional_command)
        
        return commands
    
    async def _generate_basic_commands_for_persona(
        self, 
        persona: Dict[str, Any], 
        characters_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fallback basic command generation when genre intelligence is unavailable"""
        commands = []
        
        # Create basic command
        command = {
            "command_type": "simple",
            "prompt": f"Create a {persona.get('primary_genre', 'alternative')} song with {persona.get('vocal_style', 'contemplative')} vocals",
            "style_tags": [persona.get('primary_genre', 'alternative')],
            "structure_tags": ["verse", "chorus"],
            "sound_effect_tags": [],
            "vocal_tags": [persona.get('vocal_style', 'contemplative')],
            "character_source": persona.get('character_name', 'Unknown'),
            "artist_persona": persona.get('artist_name', 'Unknown Artist'),
            "command_rationale": f"Basic command generated for {persona.get('character_name', 'character')} persona",
            "effectiveness_score": 0.7,
            "variations": []
        }
        
        commands.append(command)
        return commands
    
    def _generate_command_variations(self, enhanced_command: Dict[str, Any], 
                                   persona: Dict[str, Any]) -> List[str]:
        """Generate command variations based on enhanced command"""
        variations = []
        
        base_prompt = enhanced_command["command_text"]
        
        # Tempo variation
        if enhanced_command["tempo_description"] != "moderate":
            tempo_variation = base_prompt.replace(
                enhanced_command["style_tags"][0] if enhanced_command["style_tags"] else "song",
                f"{enhanced_command['tempo_description']} {enhanced_command['style_tags'][0] if enhanced_command['style_tags'] else 'song'}"
            )
            variations.append(tempo_variation)
        
        # Instrumentation variation
        if enhanced_command["instrumentation"]:
            inst_variation = f"{base_prompt} [featuring {enhanced_command['instrumentation'][0]}]"
            variations.append(inst_variation)
        
        # Emotional variation
        if persona.get('emotional_profile', {}).get('secondary_emotions'):
            secondary_emotion = persona['emotional_profile']['secondary_emotions'][0]
            emotion_variation = base_prompt.replace("song", f"{secondary_emotion} song")
            variations.append(emotion_variation)
        
        return variations[:3]  # Limit to 3 variations
    
    async def _create_fallback_command(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback command when generation fails"""
        # Try to use genre intelligence for fallback
        try:
            from genre_production_intelligence import get_genre_intelligence
            genre_intelligence = get_genre_intelligence()
            
            genre = persona.get('primary_genre', 'alternative')
            fallback_enhanced = genre_intelligence.enhance_suno_command(
                "Create a contemplative song", genre
            )
            
            return {
                "command_type": "fallback_enhanced",
                "prompt": fallback_enhanced["command_text"],
                "style_tags": fallback_enhanced["style_tags"],
                "meta_tags": fallback_enhanced.get("meta_tags", []),
                "structure_tags": ["verse", "chorus"],
                "tempo_bpm": fallback_enhanced.get("tempo_suggestion", 120),
                "character_source": persona.get('character_name', 'Unknown'),
                "artist_persona": "Fallback Artist",
                "command_rationale": "Enhanced fallback command created due to generation error",
                "effectiveness_score": 0.5,  # Better than basic fallback
                "variations": [],
                "is_fallback": True
            }
        except ImportError:
            # Basic fallback if genre intelligence unavailable
            return {
                "command_type": "simple",
                "prompt": "Create an alternative song with contemplative vocals",
                "style_tags": ["alternative"],
                "structure_tags": ["verse", "chorus"],
                "sound_effect_tags": [],
                "vocal_tags": ["contemplative"],
                "character_source": persona.get('character_name', 'Unknown'),
                "artist_persona": "Fallback Artist",
                "command_rationale": "Basic fallback command created due to generation error",
                "effectiveness_score": 0.3,
                "variations": [],
                "is_fallback": True
            }
    
    async def _analyze_concept_enhanced(self, concept: str) -> Dict[str, Any]:
        """Enhanced concept analysis"""
        return {
            "core_themes": ["general"],
            "emotional_qualities": {"intensity": "medium", "valence": "neutral"},
            "rhythmic_implications": {"tempo_feel": "moderate"},
            "harmonic_implications": {"complexity": "moderate"},
            "concept_length": len(concept),
            "analysis_method": "enhanced"
        }
    
    async def _generate_creative_variations_enhanced(
        self, 
        concept_analysis: Dict[str, Any], 
        style_preference: str
    ) -> List[Dict[str, Any]]:
        """Generate enhanced creative variations"""
        return [
            {
                "variation_type": "rhythmic_focus",
                "description": "Emphasis on rhythmic elements",
                "style_adaptation": style_preference
            },
            {
                "variation_type": "harmonic_exploration", 
                "description": "Focus on harmonic complexity",
                "style_adaptation": style_preference
            }
        ]
    
    async def _create_production_commands_enhanced(
        self, 
        variations: List[Dict[str, Any]], 
        concept_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create enhanced production commands"""
        commands = []
        
        for i, variation in enumerate(variations):
            command = {
                "command_id": i + 1,
                "variation_source": variation["variation_type"],
                "prompt": f"Create music with {variation['description'].lower()}",
                "effectiveness_score": 0.7
            }
            commands.append(command)
        
        return commands
    
    def _calculate_generation_quality(
        self, 
        variations: List[Dict[str, Any]], 
        commands: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall generation quality score"""
        if not variations or not commands:
            return 0.0
        
        # Simple quality calculation based on completeness
        variation_quality = min(len(variations) / 2, 1.0)  # Expect at least 2 variations
        command_quality = min(len(commands) / 2, 1.0)  # Expect at least 2 commands
        
        return (variation_quality + command_quality) / 2
    
    async def _create_minimal_analysis(self, text: str) -> Dict[str, Any]:
        """Create minimal analysis for workflow recovery"""
        return {
            "characters": [{
                "name": "Unknown Character",
                "confidence_score": 0.1,
                "backstory": "Minimal character for workflow recovery"
            }],
            "narrative_themes": ["general"],
            "emotional_arc": ["neutral"],
            "analysis_note": "Minimal analysis for workflow recovery"
        }
    
    async def _create_minimal_personas(self) -> Dict[str, Any]:
        """Create minimal personas for workflow recovery"""
        return {
            "personas": [{
                "character_name": "Unknown Character",
                "artist_name": "Independent Artist",
                "primary_genre": "alternative",
                "persona_description": "Minimal persona for workflow recovery"
            }],
            "generation_summary": "Minimal personas for workflow recovery"
        }
    
    async def _create_minimal_commands(self) -> Dict[str, Any]:
        """Create minimal commands for workflow recovery"""
        return {
            "commands": [{
                "command_type": "simple",
                "prompt": "Create an alternative song",
                "command_rationale": "Minimal command for workflow recovery"
            }],
            "generation_summary": "Minimal commands for workflow recovery"
        }
    
    # Enhanced workflow coordination methods
    
    async def _detect_content_type_enhanced(self, text: str) -> str:
        """Enhanced content type detection with caching and validation"""
        # Check cache first
        text_hash = hash(text)
        if text_hash in self.content_type_cache:
            return self.content_type_cache[text_hash]
        
        try:
            if self.universal_processor:
                content_type = self.universal_processor.detect_content_type(text)
            else:
                # Fallback content type detection
                content_type = await self._fallback_content_detection(text)
            
            # Cache the result
            self.content_type_cache[text_hash] = content_type
            return content_type
            
        except Exception as e:
            self.error_handler.logger.warning(f"Content type detection failed: {e}")
            return "mixed_content"
    
    async def _coordinate_character_analysis(self, text: str, content_type: str, ctx: Context) -> Dict[str, Any]:
        """Coordinate character analysis based on content type"""
        try:
            if content_type == "character_description":
                # Use explicit character description processing
                return await self._process_character_description(text, ctx)
            
            elif content_type == "narrative_fiction":
                # Use narrative character extraction
                return await self._process_narrative_content(text, ctx)
            
            elif content_type in ["philosophical_conceptual", "poetic_content"]:
                # Use conceptual character creation
                return await self._process_conceptual_content(text, ctx)
            
            else:
                # Mixed content - try multiple approaches
                return await self._process_mixed_content(text, ctx)
                
        except Exception as e:
            self.error_handler.logger.error(f"Character analysis coordination failed: {e}")
            raise
    
    async def _coordinate_persona_generation(self, analysis_data: Dict[str, Any], content_type: str, ctx: Context) -> Dict[str, Any]:
        """Coordinate persona generation with context preservation"""
        try:
            # Preserve content type context in persona generation
            enhanced_analysis = analysis_data.copy()
            enhanced_analysis["content_type"] = content_type
            enhanced_analysis["processing_context"] = {
                "original_content_type": content_type,
                "analysis_method": enhanced_analysis.get("analysis_method", "standard"),
                "character_confidence": enhanced_analysis.get("analysis_quality", "medium")
            }
            
            # Generate personas with content-aware logic
            analysis_json = json.dumps(enhanced_analysis)
            personas_result = await self.generate_artist_personas_enhanced(analysis_json, ctx)
            
            return json.loads(personas_result)
            
        except Exception as e:
            self.error_handler.logger.error(f"Persona generation coordination failed: {e}")
            raise
    
    async def _coordinate_album_generation(self, analysis_data: Dict[str, Any], personas_data: Dict[str, Any], 
                                         content_type: str, original_text: str, ctx: Context) -> Dict[str, Any]:
        """Coordinate album generation with full context preservation"""
        try:
            # Create comprehensive context for album generation
            album_context = {
                "analysis": analysis_data,
                "personas": personas_data,
                "content_type": content_type,
                "original_text": original_text[:500],  # First 500 chars for context
                "processing_metadata": {
                    "content_type": content_type,
                    "character_count": len(analysis_data.get("characters", [])),
                    "persona_count": len(personas_data.get("personas", [])),
                    "analysis_quality": analysis_data.get("analysis_quality", "medium")
                }
            }
            
            # Generate album with coordinated approach
            if content_type == "narrative_fiction":
                return await self._generate_narrative_album(album_context, ctx)
            elif content_type == "character_description":
                return await self._generate_character_driven_album(album_context, ctx)
            elif content_type in ["philosophical_conceptual", "poetic_content"]:
                return await self._generate_conceptual_album(album_context, ctx)
            else:
                return await self._generate_hybrid_album(album_context, ctx)
                
        except Exception as e:
            self.error_handler.logger.error(f"Album generation coordination failed: {e}")
            raise
    
    # Content processing strategies
    
    async def _process_character_description(self, text: str, ctx: Context) -> Dict[str, Any]:
        """Process explicit character descriptions"""
        if self.universal_processor:
            characters = self.universal_processor.extract_or_create_characters(text, "character_description")
        else:
            characters = await self._fallback_character_creation(text, "character_description")
        
        return {
            "characters": characters,
            "narrative_themes": ["character_study"],
            "emotional_arc": ["character_development"],
            "analysis_method": "explicit_description",
            "analysis_quality": "high",
            "content_type": "character_description"
        }
    
    async def _process_narrative_content(self, text: str, ctx: Context) -> Dict[str, Any]:
        """Process narrative fiction content"""
        if self.universal_processor:
            characters = self.universal_processor.extract_or_create_characters(text, "narrative_fiction")
        else:
            characters = await self._fallback_character_creation(text, "narrative_fiction")
        
        return {
            "characters": characters,
            "narrative_themes": ["story_progression", "character_journey"],
            "emotional_arc": ["narrative_development"],
            "analysis_method": "narrative_extraction",
            "analysis_quality": "high" if characters else "medium",
            "content_type": "narrative_fiction"
        }
    
    async def _process_conceptual_content(self, text: str, ctx: Context) -> Dict[str, Any]:
        """Process philosophical/conceptual content"""
        if self.universal_processor:
            characters = self.universal_processor.extract_or_create_characters(text, "philosophical_conceptual")
        else:
            characters = await self._fallback_character_creation(text, "philosophical_conceptual")
        
        return {
            "characters": characters,
            "narrative_themes": ["philosophical_exploration", "conceptual_development"],
            "emotional_arc": ["intellectual_journey"],
            "analysis_method": "conceptual_creation",
            "analysis_quality": "medium",
            "content_type": "philosophical_conceptual"
        }
    
    async def _process_poetic_content(self, text: str, ctx: Context) -> Dict[str, Any]:
        """Process poetic content"""
        if self.universal_processor:
            characters = self.universal_processor.extract_or_create_characters(text, "poetic_content")
        else:
            characters = await self._fallback_character_creation(text, "poetic_content")
        
        return {
            "characters": characters,
            "narrative_themes": ["poetic_expression", "lyrical_journey"],
            "emotional_arc": ["emotional_exploration"],
            "analysis_method": "poetic_interpretation",
            "analysis_quality": "medium",
            "content_type": "poetic_content"
        }
    
    async def _process_mixed_content(self, text: str, ctx: Context) -> Dict[str, Any]:
        """Process mixed or unknown content types"""
        # Try multiple approaches and use the best result
        approaches = [
            ("narrative", self._process_narrative_content),
            ("conceptual", self._process_conceptual_content),
            ("character", self._process_character_description)
        ]
        
        best_result = None
        best_score = 0
        
        for approach_name, approach_func in approaches:
            try:
                result = await approach_func(text, ctx)
                score = self._score_analysis_result(result)
                
                if score > best_score:
                    best_score = score
                    best_result = result
                    best_result["analysis_method"] = f"mixed_content_{approach_name}"
                    
            except Exception as e:
                self.error_handler.logger.warning(f"Mixed content approach {approach_name} failed: {e}")
                continue
        
        if best_result:
            best_result["content_type"] = "mixed_content"
            return best_result
        else:
            # All approaches failed, create minimal result
            return await self._create_minimal_analysis(text)
    
    # Fallback methods with content-aware recovery
    
    async def _fallback_character_analysis(self, text: str, content_type: str, error: Exception, ctx: Context) -> Dict[str, Any]:
        """Content-aware fallback for character analysis failures"""
        await ctx.info(f"Character analysis failed for {content_type} content, attempting recovery")
        
        try:
            # Try recovery based on content type
            if content_type == "character_description":
                # For character descriptions, create a basic character from the text
                return await self._create_basic_character_from_description(text)
            
            elif content_type == "narrative_fiction":
                # For narrative, try simple name extraction
                return await self._create_characters_from_names(text)
            
            elif content_type in ["philosophical_conceptual", "poetic_content"]:
                # For conceptual content, create thematic character
                return await self._create_thematic_character(text, content_type)
            
            else:
                # Generic fallback
                return await self._create_minimal_analysis(text)
                
        except Exception as fallback_error:
            self.error_handler.logger.error(f"Fallback character analysis also failed: {fallback_error}")
            return await self._create_minimal_analysis(text)
    
    async def _fallback_persona_generation(self, analysis_data: Dict[str, Any], content_type: str, 
                                         error: Exception, ctx: Context) -> Dict[str, Any]:
        """Content-aware fallback for persona generation failures"""
        await ctx.info(f"Persona generation failed for {content_type} content, attempting recovery")
        
        try:
            characters = analysis_data.get("characters", [])
            if not characters:
                # No characters to work with, create generic persona
                return await self._create_generic_persona(content_type)
            
            # Create basic personas from available character data
            personas = []
            for character in characters[:2]:  # Limit to 2 personas
                persona = await self._create_basic_persona_from_character(character, content_type)
                personas.append(persona)
            
            return {
                "personas": personas,
                "generation_summary": f"Fallback personas created for {content_type} content",
                "fallback_used": True
            }
            
        except Exception as fallback_error:
            self.error_handler.logger.error(f"Fallback persona generation also failed: {fallback_error}")
            return await self._create_minimal_personas()
    
    async def _fallback_album_generation(self, analysis_data: Dict[str, Any], personas_data: Dict[str, Any],
                                       content_type: str, error: Exception, ctx: Context) -> Dict[str, Any]:
        """Content-aware fallback for album generation failures"""
        await ctx.info(f"Album generation failed for {content_type} content, attempting recovery")
        
        try:
            # Create simplified album based on available data
            characters = analysis_data.get("characters", [])
            personas = personas_data.get("personas", [])
            
            if not characters and not personas:
                return await self._create_minimal_album(content_type)
            
            # Create basic album structure
            album = {
                "tracks": await self._create_basic_tracks(characters, personas, content_type),
                "album_concept": f"Album generated from {content_type} content",
                "generation_method": "fallback",
                "content_type": content_type,
                "fallback_used": True
            }
            
            return album
            
        except Exception as fallback_error:
            self.error_handler.logger.error(f"Fallback album generation also failed: {fallback_error}")
            return await self._create_minimal_album(content_type)

# Global enhanced tools instance
_enhanced_tools = None

def get_enhanced_tools() -> EnhancedMCPTools:
    """Get or create the global enhanced tools instance"""
    global _enhanced_tools
    if _enhanced_tools is None:
        _enhanced_tools = EnhancedMCPTools()
    return _enhanced_tools    
   
 # Additional helper methods for enhanced coordination
    
    async def _fallback_content_detection(self, text: str) -> str:
        """Fallback content type detection when universal processor is unavailable"""
        text_lower = text.lower()
        
        # Simple heuristics for content type detection
        if any(indicator in text_lower for indicator in ["character:", "protagonist:", "artist:", "musician:"]):
            return "character_description"
        elif any(indicator in text_lower for indicator in ["philosophy", "concept", "theory", "abstract"]):
            return "philosophical_conceptual"
        elif any(indicator in text_lower for indicator in ["poem", "poetry", "verse", "stanza"]):
            return "poetic_content"
        elif any(indicator in text_lower for indicator in ["story", "narrative", "character", "protagonist"]):
            return "narrative_fiction"
        else:
            return "mixed_content"
    
    async def _fallback_character_creation(self, text: str, content_type: str) -> List[Dict[str, Any]]:
        """Fallback character creation when universal processor is unavailable"""
        import re
        
        if content_type == "character_description":
            # Extract basic info from character description
            return [{
                "name": "Described Character",
                "aliases": [],
                "backstory": text[:200],
                "confidence_score": 0.6,
                "content_type": content_type,
                "processing_notes": "Created from character description fallback"
            }]
        
        elif content_type == "narrative_fiction":
            # Simple name extraction
            names = re.findall(r'\b[A-Z][a-z]+\b', text)
            unique_names = list(set(names))[:2]  # Limit to 2 characters
            
            characters = []
            for name in unique_names:
                characters.append({
                    "name": name,
                    "aliases": [],
                    "backstory": f"Character from narrative: {name}",
                    "confidence_score": 0.4,
                    "content_type": content_type,
                    "processing_notes": "Created from narrative fallback"
                })
            
            return characters if characters else [await self._create_generic_character_fallback(content_type)]
        
        else:
            # Conceptual or other content types
            return [await self._create_generic_character_fallback(content_type)]
    
    async def _create_generic_character_fallback(self, content_type: str) -> Dict[str, Any]:
        """Create a generic character for fallback scenarios"""
        character_names = {
            "philosophical_conceptual": "The Philosopher",
            "poetic_content": "The Poet",
            "mixed_content": "The Narrator",
            "unknown": "The Speaker"
        }
        
        return {
            "name": character_names.get(content_type, "Unknown Character"),
            "aliases": [],
            "backstory": f"Generic character created for {content_type} content",
            "confidence_score": 0.2,
            "content_type": content_type,
            "processing_notes": "Generic fallback character"
        }
    
    def _score_analysis_result(self, result: Dict[str, Any]) -> float:
        """Score analysis result quality for mixed content processing"""
        score = 0.0
        
        # Score based on character count and quality
        characters = result.get("characters", [])
        if characters:
            score += len(characters) * 0.3
            
            # Bonus for character confidence
            avg_confidence = sum(char.get("confidence_score", 0) for char in characters) / len(characters)
            score += avg_confidence * 0.4
        
        # Score based on analysis quality
        quality_scores = {"high": 0.3, "medium": 0.2, "low": 0.1}
        analysis_quality = result.get("analysis_quality", "low")
        score += quality_scores.get(analysis_quality, 0.1)
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _create_basic_character_from_description(self, text: str) -> Dict[str, Any]:
        """Create basic character from description text"""
        # Extract potential name from first line or sentence
        first_sentence = text.split('.')[0].split('\n')[0]
        
        return {
            "characters": [{
                "name": "Described Character",
                "aliases": [],
                "backstory": text[:300],
                "confidence_score": 0.5,
                "content_type": "character_description",
                "processing_notes": "Basic character from description"
            }],
            "narrative_themes": ["character_study"],
            "emotional_arc": ["character_development"],
            "analysis_method": "basic_description_parsing",
            "analysis_quality": "medium"
        }
    
    async def _create_characters_from_names(self, text: str) -> Dict[str, Any]:
        """Create characters from simple name extraction"""
        import re
        
        # Find potential names
        names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        unique_names = list(set(names))[:3]  # Limit to 3 characters
        
        characters = []
        for name in unique_names:
            if len(name) > 2 and name not in ['The', 'This', 'That', 'When', 'Where']:
                characters.append({
                    "name": name,
                    "aliases": [],
                    "backstory": f"Character mentioned in narrative: {name}",
                    "confidence_score": 0.3,
                    "content_type": "narrative_fiction",
                    "processing_notes": "Created from name extraction"
                })
        
        return {
            "characters": characters,
            "narrative_themes": ["story_progression"],
            "emotional_arc": ["narrative_development"],
            "analysis_method": "name_extraction",
            "analysis_quality": "low" if not characters else "medium"
        }
    
    async def _create_thematic_character(self, text: str, content_type: str) -> Dict[str, Any]:
        """Create thematic character from conceptual content"""
        character_names = {
            "philosophical_conceptual": "The Thinker",
            "poetic_content": "The Poet"
        }
        
        character = {
            "name": character_names.get(content_type, "The Contemplator"),
            "aliases": [],
            "backstory": f"Character embodying themes from {content_type} content",
            "confidence_score": 0.4,
            "content_type": content_type,
            "processing_notes": "Thematic character creation"
        }
        
        return {
            "characters": [character],
            "narrative_themes": ["thematic_exploration"],
            "emotional_arc": ["conceptual_journey"],
            "analysis_method": "thematic_character_creation",
            "analysis_quality": "medium"
        }
    
    async def _create_generic_persona(self, content_type: str) -> Dict[str, Any]:
        """Create generic persona for fallback scenarios"""
        persona_types = {
            "character_description": "Character-Based Artist",
            "narrative_fiction": "Storytelling Artist",
            "philosophical_conceptual": "Conceptual Artist",
            "poetic_content": "Poetic Artist",
            "mixed_content": "Versatile Artist"
        }
        
        return {
            "personas": [{
                "character_name": "Generic Character",
                "artist_name": persona_types.get(content_type, "Independent Artist"),
                "primary_genre": "alternative",
                "persona_description": f"Generic persona for {content_type} content",
                "fallback_used": True
            }],
            "generation_summary": f"Generic persona created for {content_type} content"
        }
    
    async def _create_basic_persona_from_character(self, character: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Create basic persona from character data"""
        character_name = character.get("name", "Unknown Character")
        
        return {
            "character_name": character_name,
            "artist_name": f"{character_name} (Artist)",
            "primary_genre": "alternative",
            "persona_description": f"Basic persona derived from {character_name}",
            "content_type": content_type,
            "fallback_used": True
        }
    
    async def _create_minimal_album(self, content_type: str) -> Dict[str, Any]:
        """Create minimal album for fallback scenarios"""
        return {
            "tracks": [
                {
                    "title": f"Track 1 - {content_type.replace('_', ' ').title()}",
                    "concept": f"Basic track for {content_type} content",
                    "fallback_used": True
                }
            ],
            "album_concept": f"Minimal album for {content_type} content",
            "generation_method": "minimal_fallback",
            "content_type": content_type
        }
    
    async def _create_basic_tracks(self, characters: List[Dict], personas: List[Dict], content_type: str) -> List[Dict[str, Any]]:
        """Create basic tracks from available character and persona data"""
        tracks = []
        
        # Create tracks based on available data
        if characters:
            for i, character in enumerate(characters[:3]):  # Max 3 tracks
                track = {
                    "title": f"Track {i+1} - {character.get('name', 'Character')}",
                    "concept": f"Track exploring {character.get('name', 'character')} from {content_type} content",
                    "character_source": character.get('name', 'Unknown'),
                    "fallback_used": True
                }
                tracks.append(track)
        
        elif personas:
            for i, persona in enumerate(personas[:3]):  # Max 3 tracks
                track = {
                    "title": f"Track {i+1} - {persona.get('artist_name', 'Artist')}",
                    "concept": f"Track by {persona.get('artist_name', 'artist')} from {content_type} content",
                    "persona_source": persona.get('artist_name', 'Unknown'),
                    "fallback_used": True
                }
                tracks.append(track)
        
        else:
            # No characters or personas, create generic track
            tracks.append({
                "title": f"Track 1 - {content_type.replace('_', ' ').title()}",
                "concept": f"Generic track for {content_type} content",
                "fallback_used": True
            })
        
        return tracks
    
    # Album generation methods (simplified versions for coordination)
    
    async def _generate_narrative_album(self, album_context: Dict[str, Any], ctx: Context) -> Dict[str, Any]:
        """Generate album for narrative content"""
        await ctx.info("Generating narrative-focused album")
        
        characters = album_context["analysis"].get("characters", [])
        if not characters:
            raise ValueError("No characters available for narrative album")
        
        # Create story-progression tracks
        tracks = []
        for i, character in enumerate(characters[:5]):  # Max 5 tracks
            track = {
                "title": f"Chapter {i+1} - {character.get('name', 'Character')}",
                "concept": f"Story progression featuring {character.get('name', 'character')}",
                "character_focus": character.get('name', 'Unknown'),
                "narrative_position": f"chapter_{i+1}"
            }
            tracks.append(track)
        
        return {
            "tracks": tracks,
            "album_concept": "Narrative progression album",
            "generation_method": "narrative_coordination",
            "content_type": "narrative_fiction"
        }
    
    async def _generate_character_driven_album(self, album_context: Dict[str, Any], ctx: Context) -> Dict[str, Any]:
        """Generate album for character-driven content"""
        await ctx.info("Generating character-driven album")
        
        characters = album_context["analysis"].get("characters", [])
        if not characters:
            raise ValueError("No characters available for character-driven album")
        
        main_character = characters[0]
        
        # Create character exploration tracks
        tracks = []
        aspects = ["Introduction", "Background", "Struggles", "Growth", "Resolution"]
        
        for i, aspect in enumerate(aspects):
            track = {
                "title": f"{main_character.get('name', 'Character')} - {aspect}",
                "concept": f"Exploring {aspect.lower()} of {main_character.get('name', 'character')}",
                "character_focus": main_character.get('name', 'Unknown'),
                "character_aspect": aspect.lower()
            }
            tracks.append(track)
        
        return {
            "tracks": tracks,
            "album_concept": f"Character study of {main_character.get('name', 'character')}",
            "generation_method": "character_coordination",
            "content_type": "character_description"
        }
    
    async def _generate_conceptual_album(self, album_context: Dict[str, Any], ctx: Context) -> Dict[str, Any]:
        """Generate album for conceptual content"""
        await ctx.info("Generating conceptual album")
        
        themes = album_context["analysis"].get("narrative_themes", ["exploration"])
        
        # Create thematic tracks
        tracks = []
        for i, theme in enumerate(themes[:5]):  # Max 5 tracks
            track = {
                "title": f"Movement {i+1} - {theme.replace('_', ' ').title()}",
                "concept": f"Conceptual exploration of {theme}",
                "thematic_focus": theme,
                "conceptual_depth": "high"
            }
            tracks.append(track)
        
        return {
            "tracks": tracks,
            "album_concept": "Conceptual exploration album",
            "generation_method": "conceptual_coordination",
            "content_type": album_context.get("content_type", "philosophical_conceptual")
        }
    
    async def _generate_hybrid_album(self, album_context: Dict[str, Any], ctx: Context) -> Dict[str, Any]:
        """Generate album for mixed/hybrid content"""
        await ctx.info("Generating hybrid album")
        
        # Combine approaches based on available data
        characters = album_context["analysis"].get("characters", [])
        themes = album_context["analysis"].get("narrative_themes", [])
        
        tracks = []
        
        # Add character-based tracks if available
        if characters:
            for i, character in enumerate(characters[:3]):
                track = {
                    "title": f"Portrait {i+1} - {character.get('name', 'Character')}",
                    "concept": f"Character portrait of {character.get('name', 'character')}",
                    "character_focus": character.get('name', 'Unknown'),
                    "track_type": "character"
                }
                tracks.append(track)
        
        # Add thematic tracks
        for i, theme in enumerate(themes[:2]):  # Max 2 thematic tracks
            track = {
                "title": f"Theme {i+1} - {theme.replace('_', ' ').title()}",
                "concept": f"Thematic exploration of {theme}",
                "thematic_focus": theme,
                "track_type": "thematic"
            }
            tracks.append(track)
        
        # Ensure at least one track
        if not tracks:
            tracks.append({
                "title": "Hybrid Expression",
                "concept": "Mixed content exploration",
                "track_type": "hybrid"
            })
        
        return {
            "tracks": tracks,
            "album_concept": "Hybrid content album",
            "generation_method": "hybrid_coordination",
            "content_type": "mixed_content"
        }


# Global enhanced tools instance
_enhanced_tools = None

def get_enhanced_tools() -> EnhancedMCPTools:
    """Get or create the global enhanced tools instance"""
    global _enhanced_tools
    if _enhanced_tools is None:
        _enhanced_tools = EnhancedMCPTools()
    return _enhanced_tools


# Workflow coordination utilities

async def coordinate_album_workflow(content: str, content_type: str = None, ctx: Context = None) -> Dict[str, Any]:
    """
    Coordinate complete album generation workflow with enhanced error handling
    
    This function provides a high-level interface for coordinating the entire
    album generation workflow with content type detection and intelligent fallbacks.
    """
    tools = get_enhanced_tools()
    
    try:
        if ctx:
            await ctx.info("Starting coordinated album workflow")
        
        # Use the enhanced complete workflow
        result_json = await tools.complete_workflow_enhanced(content, ctx)
        result = json.loads(result_json)
        
        return result
        
    except Exception as e:
        if ctx:
            await ctx.error(f"Coordinated workflow failed: {str(e)}")
        
        # Final fallback - return minimal result
        return {
            "workflow_status": "failed",
            "error": str(e),
            "final_results": {
                "analysis": await tools._create_minimal_analysis(content),
                "personas": await tools._create_minimal_personas(),
                "album": await tools._create_minimal_album("unknown")
            }
        }


def get_workflow_statistics() -> Dict[str, Any]:
    """Get workflow coordination statistics"""
    tools = get_enhanced_tools()
    
    return {
        "content_type_cache_size": len(tools.content_type_cache),
        "available_strategies": list(tools.processing_strategies.keys()),
        "workflow_state_keys": list(tools.workflow_state.keys()) if tools.workflow_state else [],
        "components_available": {
            "character_analyzer": tools.character_analyzer is not None,
            "universal_processor": tools.universal_processor is not None,
            "error_handler": tools.error_handler is not None,
            "recovery_system": tools.recovery_system is not None
        }
    }