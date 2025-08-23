#!/usr/bin/env python3
"""Test the new lyric generation functionality"""

import asyncio
import json
from server import (
    EmotionalBeatEngine, 
    EmotionalLyricGenerator,
    EmotionalState
)

async def test_lyric_generation():
    """Test lyric generation with philosophical text"""
    
    # Simulate emotional states from philosophical text
    emotional_states = [
        EmotionalState(
            primary_emotion="contemplation",
            secondary_emotions=["searching", "curiosity"],
            intensity=0.8,
            factual_triggers=["overbalanced in reasoning faculties"],
            internal_conflict="reasoning vs intuition",
            defense_mechanism=None,
            authenticity_score=0.9
        ),
        EmotionalState(
            primary_emotion="vulnerability",
            secondary_emotions=["uncertainty", "humility"],
            intensity=0.7,
            factual_triggers=["vague idea of how we came to be"],
            internal_conflict="knowledge vs mystery",
            defense_mechanism=None,
            authenticity_score=0.85
        )
    ]
    
    print("Testing Lyric Generation\n")
    print("=" * 60)
    
    # Test lyric generator
    lyric_generator = EmotionalLyricGenerator()
    lyric_structure = lyric_generator.generate_lyric_structure(
        emotional_states, 
        "Philosophical exploration of consciousness and divine creation"
    )
    
    print("Generated Lyric Structure:")
    print("-" * 30)
    
    # Print verse content
    print(f"\nVERSE 1:")
    verse1 = lyric_structure['structure']['verses'][0]
    print(f"  Opening: {verse1['opening']}")
    print(f"  Development: {verse1['development']}")
    if verse1['conflict']:
        print(f"  Conflict: {verse1['conflict']}")
    print(f"  Delivery: {verse1['authenticity_note']}")
    
    if len(lyric_structure['structure']['verses']) > 1:
        print(f"\nVERSE 2:")
        verse2 = lyric_structure['structure']['verses'][1]
        print(f"  Opening: {verse2['opening']}")
        print(f"  Development: {verse2['development']}")
        if verse2['conflict']:
            print(f"  Conflict: {verse2['conflict']}")
    
    # Print chorus content
    print(f"\nCHORUS:")
    chorus = lyric_structure['structure']['chorus']
    print(f"  Hook: {chorus['hook']}")
    print(f"  Emotional Layer: {chorus['emotional_layer']}")
    print(f"  Repetition: {chorus['repetition_pattern']}")
    print(f"  Vocal Direction: {chorus['vocal_direction']}")
    
    # Print bridge content
    print(f"\nBRIDGE:")
    bridge = lyric_structure['structure']['bridge']
    print(f"  Transformation: {bridge['transformation']}")
    print(f"  Concepts: {', '.join(bridge['concepts'])}")
    print(f"  Lyrical Shift: {bridge['lyrical_shift']}")
    print(f"  Musical Direction: {bridge['musical_direction']}")
    
    # Print themes and devices
    print(f"\nTHEMES: {', '.join(lyric_structure['themes'])}")
    print(f"EMOTIONAL ARC: {' -> '.join(lyric_structure['emotional_arc'])}")
    print(f"KEY PHRASES: {', '.join(lyric_structure['key_phrases'])}")
    print(f"LYRICAL DEVICES: {', '.join(lyric_structure['lyrical_devices'])}")
    
    print("\n" + "=" * 60)
    print("Example Full Suno Command with Lyrics:")
    print("-" * 40)
    
    # Simulate a complete Suno command
    suno_command = f"""[ambient electronic] [70-90bpm] [polyrhythmic patterns with space between hits]
A musical exploration of philosophical content expressing contemplation.
Beat elements: brushed snare, soft timpani
Emotional arc: contemplation -> vulnerability
Production: circular patterns representing thought loops
[contrasting rhythms for reasoning vs intuition]

LYRICAL GUIDANCE:
Verse concept: {verse1['opening']}
Chorus hook: {chorus['hook']}
Themes: {', '.join(lyric_structure['themes'][:3])}
Lyrical approach: {', '.join(lyric_structure['lyrical_devices'][:2])}
Key phrases: {', '.join(lyric_structure['key_phrases'][:3])}"""
    
    print(suno_command)

if __name__ == "__main__":
    asyncio.run(test_lyric_generation())