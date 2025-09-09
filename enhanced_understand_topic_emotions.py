#!/usr/bin/env python3

"""
Enhanced understand_topic_with_emotions tool implementation

This module provides the enhanced version of understand_topic_with_emotions that:
1. Implements meaningful emotional analysis instead of generic "contemplative" responses
2. Generates varied emotional insights based on actual content analysis
3. Creates contextually appropriate emotional responses for different topics
4. Generates meaningful beat patterns and musical elements aligned with emotional content
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from enhanced_beat_generator import EnhancedBeatGenerator
from enhanced_emotional_analyzer import EmotionalProfile, EnhancedEmotionalAnalyzer


class EnhancedTopicEmotionAnalyzer:
    """
    Enhanced topic emotion analyzer that provides meaningful, varied insights
    instead of generic responses.
    """

    def __init__(self):
        self.emotional_analyzer = EnhancedEmotionalAnalyzer()
        self.beat_generator = EnhancedBeatGenerator()

    async def analyze_topic_with_emotions(
        self,
        topic_text: str,
        source_type: str = "book",
        focus_areas: Optional[List[str]] = None,
        ctx = None
    ) -> str:
        """
        Enhanced topic analysis with meaningful emotional insights and beat patterns
        
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

            # Perform comprehensive emotional analysis
            emotional_profile = self.emotional_analyzer.analyze_emotional_content(topic_text, source_type)

            # Generate genre preferences based on emotional content
            genre_preferences = self._extract_genre_preferences(emotional_profile, source_type)

            # Generate beat patterns and musical elements
            beat_analysis = self.beat_generator.generate_beat_patterns(emotional_profile, genre_preferences)

            # Create comprehensive understanding result
            understanding_result = {
                "topic_analysis": {
                    "source_type": source_type,
                    "content_preview": topic_text[:200] + ("..." if len(topic_text) > 200 else ""),
                    "content_length": len(topic_text),
                    "focus_areas": focus_areas if focus_areas else ["emotional_understanding", "musical_interpretation"],
                    "analysis_timestamp": self._get_timestamp()
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
                    "analysis_confidence": self._calculate_analysis_confidence(emotional_profile)
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
                    "emotional_directives": self._generate_emotional_directives(emotional_profile),
                    "production_commands": self._generate_production_commands(emotional_profile),
                    "complete_command_set": self._generate_complete_suno_commands(emotional_profile, beat_analysis)
                },
                "production_notes": {
                    "emotional_production_notes": beat_analysis.get("production_notes", []),
                    "technical_recommendations": self._generate_technical_recommendations(emotional_profile),
                    "creative_suggestions": self._generate_creative_suggestions(emotional_profile, source_type)
                },
                "comprehensive_understanding": self._generate_comprehensive_summary(emotional_profile, source_type, beat_analysis)
            }

            if ctx:
                await ctx.info(f"Completed enhanced analysis with {len(emotional_profile.primary_emotions)} emotions detected")

            return json.dumps(understanding_result, indent=2)

        except Exception as e:
            error_msg = f"Enhanced topic understanding failed: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            return json.dumps({"error": error_msg})

    def _extract_genre_preferences(self, emotional_profile: EmotionalProfile, source_type: str) -> List[str]:
        """Extract genre preferences based on emotional content and source type"""
        genre_preferences = []

        # Add genres from musical recommendations
        if "genre_suggestions" in emotional_profile.musical_recommendations:
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

        for emotion in emotional_profile.primary_emotions[:2]:  # Top 2 emotions
            if emotion.emotion in emotion_genre_mappings:
                for genre in emotion_genre_mappings[emotion.emotion]:
                    if genre not in genre_preferences:
                        genre_preferences.append(genre)

        return genre_preferences[:5]  # Return top 5 genre preferences

    def _calculate_analysis_confidence(self, emotional_profile: EmotionalProfile) -> float:
        """Calculate confidence score for the emotional analysis"""
        if not emotional_profile.primary_emotions:
            return 0.0

        # Base confidence on number of emotions detected and their intensities
        num_emotions = len(emotional_profile.primary_emotions)
        if num_emotions == 0:
            return 0.0

        avg_intensity = sum(e.intensity for e in emotional_profile.primary_emotions) / num_emotions

        # Higher confidence with more emotions and higher intensities
        confidence = min((num_emotions * 0.2) + (avg_intensity * 0.8), 1.0)

        return round(confidence, 2)

    def _generate_emotional_directives(self, emotional_profile: EmotionalProfile) -> List[str]:
        """Generate Suno AI emotional directives based on analysis"""
        directives = []

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
        if emotional_profile.emotional_arc["beginning"] != emotional_profile.emotional_arc["end"]:
            directives.append(f"[emotional_journey_{emotional_profile.emotional_arc['beginning']}_to_{emotional_profile.emotional_arc['end']}]")

        # Complexity directive
        if emotional_profile.emotional_complexity > 0.7:
            directives.append("[complex_emotions]")
        elif emotional_profile.emotional_complexity < 0.3:
            directives.append("[simple_emotions]")

        return directives

    def _generate_production_commands(self, emotional_profile: EmotionalProfile) -> List[str]:
        """Generate production-specific Suno commands"""
        commands = []

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
        if emotional_profile.emotional_complexity > 0.7:
            commands.extend(["[layered_arrangement]", "[rich_texture]", "[complex_harmony]"])
        elif emotional_profile.emotional_complexity < 0.3:
            commands.extend(["[minimal_arrangement]", "[simple_texture]", "[clear_structure]"])

        return commands

    def _generate_complete_suno_commands(self, emotional_profile: EmotionalProfile, beat_analysis: Dict[str, Any]) -> List[str]:
        """Generate a complete set of Suno commands for the track"""
        commands = []

        # Start with beat pattern commands
        if "suno_commands" in beat_analysis:
            commands.extend(beat_analysis["suno_commands"])

        # Add emotional directives
        commands.extend(self._generate_emotional_directives(emotional_profile))

        # Add production commands
        commands.extend(self._generate_production_commands(emotional_profile))

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

    def _generate_technical_recommendations(self, emotional_profile: EmotionalProfile) -> List[str]:
        """Generate technical production recommendations"""
        recommendations = []

        # Recommendations based on emotional intensity
        if emotional_profile.primary_emotions:
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
        if emotional_profile.emotional_complexity > 0.7:
            recommendations.extend([
                "Use frequency separation techniques to manage complex arrangements",
                "Apply subtle panning to create space for multiple elements",
                "Consider automation to highlight different emotional layers"
            ])

        return recommendations

    def _generate_creative_suggestions(self, emotional_profile: EmotionalProfile, source_type: str) -> List[str]:
        """Generate creative suggestions based on analysis"""
        suggestions = []

        # Suggestions based on emotional themes
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
        if emotional_profile.emotional_arc["beginning"] != emotional_profile.emotional_arc["end"]:
            suggestions.append(f"Create a musical journey that mirrors the emotional arc from {emotional_profile.emotional_arc['beginning']} to {emotional_profile.emotional_arc['end']}")

        return suggestions

    def _generate_comprehensive_summary(self, emotional_profile: EmotionalProfile, source_type: str, beat_analysis: Dict[str, Any]) -> str:
        """Generate a comprehensive summary of the analysis"""
        primary_emotion = emotional_profile.primary_emotions[0] if emotional_profile.primary_emotions else None

        if not primary_emotion:
            return f"Analysis of {source_type} content completed with minimal emotional content detected."

        summary_parts = []

        # Emotional analysis summary
        summary_parts.append(f"The {source_type} content reveals a primarily {primary_emotion.emotion} emotional landscape with {primary_emotion.intensity:.1f} intensity.")

        # Emotional complexity
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
        if emotional_profile.emotional_themes:
            themes_str = ", ".join(emotional_profile.emotional_themes[:3])
            summary_parts.append(f"Key emotional themes include {themes_str}, which should inform the musical narrative structure.")

        # Production approach summary
        if emotional_profile.dominant_mood:
            summary_parts.append(f"The dominant {emotional_profile.dominant_mood} mood suggests a production approach that emphasizes {self._get_mood_production_focus(emotional_profile.dominant_mood)}.")

        return " ".join(summary_parts)

    def _get_mood_production_focus(self, mood: str) -> str:
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

    def _get_timestamp(self) -> str:
        """Get current timestamp for analysis"""
        import datetime
        return datetime.datetime.now().isoformat()


# Internal callable version for use by other tools and testing
async def _understand_topic_with_emotions_internal(
    topic_text: str,
    source_type: str = "book",
    focus_areas: Optional[List[str]] = None,
    ctx = None
) -> str:
    """Internal callable version of enhanced understand_topic_with_emotions"""
    analyzer = EnhancedTopicEmotionAnalyzer()
    return await analyzer.analyze_topic_with_emotions(topic_text, source_type, focus_areas, ctx)


# Test function to validate the enhanced implementation
async def test_enhanced_understand_topic_emotions():
    """Test the enhanced understand_topic_with_emotions implementation"""
    print("🧠 Testing Enhanced Topic Emotion Analysis")
    print("=" * 50)

    class MockContext:
        async def info(self, message):
            print(f"INFO: {message}")

        async def error(self, message):
            print(f"ERROR: {message}")

    ctx = MockContext()

    # Test cases with different emotional content
    test_cases = [
        {
            "name": "Melancholic Story",
            "text": "Sarah stood at the window, watching the rain streak down the glass. The empty apartment felt hollow without David's laughter echoing through the rooms. She touched the photograph on the mantle, remembering better days when hope seemed endless and love felt permanent. Now, only memories remained, fragile as autumn leaves.",
            "source_type": "story",
            "focus_areas": ["emotional journey", "loss"]
        },
        {
            "name": "Intense Thriller",
            "text": "The footsteps behind Marcus grew louder, echoing through the narrow alley. His heart pounded against his ribs as he pressed himself against the cold brick wall. The killer was close now, so close he could hear the heavy breathing. Terror gripped him as he realized there was nowhere left to run. The darkness seemed to pulse with malevolent energy.",
            "source_type": "book",
            "focus_areas": ["tension", "fear", "survival"]
        },
        {
            "name": "Philosophical Reflection",
            "text": "What does it mean to truly exist? Descartes suggested that thinking proves our being, but perhaps existence is more than mere cognition. In the quiet moments between thoughts, in the space where consciousness meets the infinite, we might find a deeper truth about our place in the cosmos. The question is not whether we think, but whether we truly live.",
            "source_type": "philosophy",
            "focus_areas": ["existential themes", "consciousness"]
        },
        {
            "name": "Hopeful Journey",
            "text": "Emma packed her bags with trembling hands, but her eyes shone with determination. Tomorrow, she would start her new life in the city, leaving behind the small town that had never understood her dreams. The scholarship letter crumpled in her pocket was her ticket to freedom, to possibility, to becoming who she was meant to be. The future stretched ahead like an open road.",
            "source_type": "story",
            "focus_areas": ["transformation", "hope", "new beginnings"]
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")

        try:
            result = await _understand_topic_with_emotions_internal(
                topic_text=test_case["text"],
                source_type=test_case["source_type"],
                focus_areas=test_case["focus_areas"],
                ctx=ctx
            )

            # Parse and display key results
            result_data = json.loads(result)

            print("✅ Analysis completed successfully")

            # Display emotional analysis
            if "emotional_analysis" in result_data:
                emotional = result_data["emotional_analysis"]
                print(f"   Primary emotion: {emotional.get('dominant_mood', 'unknown')}")
                print(f"   Emotional complexity: {emotional.get('emotional_complexity', 0):.2f}")
                print(f"   Detected emotions: {len(emotional.get('primary_emotions', []))}")

            # Display musical interpretation
            if "musical_interpretation" in result_data:
                musical = result_data["musical_interpretation"]
                tempo = musical.get("tempo_recommendations", {}).get("recommended_tempo", "unknown")
                print(f"   Recommended tempo: {tempo} BPM")
                print(f"   Genre suggestions: {', '.join(musical.get('genre_suggestions', [])[:3])}")

            # Display Suno commands count
            if "suno_commands" in result_data:
                commands = result_data["suno_commands"].get("complete_command_set", [])
                print(f"   Generated Suno commands: {len(commands)}")

        except Exception as e:
            print(f"❌ Test failed: {e}")

    print("\n🎉 Enhanced topic emotion analysis testing completed!")


if __name__ == "__main__":
    asyncio.run(test_enhanced_understand_topic_emotions())
