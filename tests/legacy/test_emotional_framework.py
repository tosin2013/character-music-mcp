#!/usr/bin/env python3
"""Test the new emotional framework functionality"""

import asyncio
import json
from server import (
    EmotionalBeatEngine, 
    MetaNarrativeProcessor, 
    SelfReflectionAnalyzer,
    CharacterProfile,
    EmotionalState
)

async def test_emotional_framework():
    """Test the emotional framework components"""
    
    # Test text with emotional content
    test_text = """
    Sarah stood at the edge of the cliff, her heart pounding. She had lost everything - 
    her family, her home, her sense of purpose. The wind whipped through her hair as 
    tears streamed down her face. But then she remembered her mother's words: 
    "Even in the darkest moments, there is always hope." She took a deep breath, 
    feeling a strange mix of grief and determination. She realized she had a choice - 
    let the pain consume her or use it to become stronger. Sarah smiled through her tears, 
    understanding that this wasn't an ending, but a beginning.
    """
    
    print("Testing Emotional Framework Components\n")
    print("=" * 60)
    
    # Test EmotionalBeatEngine
    print("\n1. Testing EmotionalBeatEngine:")
    beat_engine = EmotionalBeatEngine()
    emotional_states = beat_engine.analyze_emotional_facts(test_text)
    
    print(f"   Found {len(emotional_states)} emotional states:")
    for state in emotional_states:
        print(f"   - {state.primary_emotion} (intensity: {state.intensity}, authenticity: {state.authenticity_score})")
        if state.internal_conflict:
            print(f"     Internal conflict: {state.internal_conflict}")
    
    # Test beat progression
    if emotional_states:
        beat_progression = beat_engine.generate_beat_progression(emotional_states)
        print(f"\n   Beat Progression:")
        print(f"   - Tempo range: {beat_progression['overall_tempo_range']}")
        print(f"   - Sections: {len(beat_progression['sections'])}")
        for section in beat_progression['sections'][:2]:
            print(f"     * {section['timestamp']}: {section['emotion']} @ {section['intensity']} intensity")
    
    # Test MetaNarrativeProcessor
    print("\n2. Testing MetaNarrativeProcessor:")
    meta_processor = MetaNarrativeProcessor()
    emotional_subtext = meta_processor.extract_emotional_subtext(test_text, emotional_states)
    
    print(f"   Found {len(emotional_subtext)} subtext elements:")
    for subtext in emotional_subtext[:3]:
        print(f"   - Type: {subtext['type']}")
        print(f"     Evidence: '{subtext['text_evidence']}'")
        print(f"     Implied emotions: {', '.join(subtext['implied_emotions'])}")
    
    # Test SelfReflectionAnalyzer
    print("\n3. Testing SelfReflectionAnalyzer:")
    reflection_analyzer = SelfReflectionAnalyzer()
    
    # Create a test character
    test_character = CharacterProfile(
        name="Sarah",
        aliases=[],
        physical_description="Young woman with flowing hair",
        mannerisms=["thoughtful", "determined"],
        speech_patterns=[],
        behavioral_traits=["resilient", "emotional"],
        backstory="Lost everything but finding hope",
        relationships=["deceased family members"],
        formative_experiences=["loss", "grief"],
        social_connections=[],
        motivations=["survival", "honoring memory"],
        fears=["being alone", "forgetting"],
        desires=["peace", "purpose"],
        conflicts=["grief vs hope"],
        personality_drivers=["resilience", "love"],
        confidence_score=0.8,
        text_references=[],
        first_appearance="",
        importance_score=1.0
    )
    
    introspection_data = reflection_analyzer.analyze_character_introspection(test_text, test_character)
    
    print(f"   Self-awareness moments: {len(introspection_data['self_awareness_moments'])}")
    print(f"   Emotional processing stages: {len(introspection_data['emotional_processing_stages'])}")
    print(f"   Defense mechanisms: {len(introspection_data['defense_mechanisms'])}")
    
    if introspection_data['vulnerability_scores']:
        print(f"   Vulnerability progression: {introspection_data['vulnerability_scores'][:3]}")
    
    print("\n" + "=" * 60)
    print("Emotional Framework Test Complete!")
    
    # Test integration with beat patterns
    print("\n4. Testing Beat Pattern Mapping:")
    for emotion, pattern in beat_engine.emotion_beat_map.items():
        print(f"   {emotion}:")
        print(f"   - Tempo: {pattern.tempo_range[0]}-{pattern.tempo_range[1]} BPM")
        print(f"   - Pattern: {pattern.rhythm_pattern}")
        print(f"   - Elements: {', '.join(pattern.percussion_elements[:2])}")
        print()

if __name__ == "__main__":
    asyncio.run(test_emotional_framework())