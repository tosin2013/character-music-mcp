#!/usr/bin/env python3
"""
Test script for generating a complete album workflow for the philosophical liquid DNB artist
"""

from server import CharacterAnalyzer, PersonaGenerator, SunoCommandGenerator
import json

def main():
    # Initialize components
    analyzer = CharacterAnalyzer()
    persona_gen = PersonaGenerator()
    command_gen = SunoCommandGenerator()
    
    # Character description
    character_desc = """Marcus 'Solvent' Thompson, 34-year-old liquid drum and bass producer. 
    Core philosophy: 'I have always considered that the two questions respecting God and the Soul 
    were the chief of those that ought to be demonstrated by philosophical rather than theological argument.' 
    
    This artist believes spiritual questions should be explored through reason and artistic expression 
    rather than dogma. He sees music production as philosophical inquiry, where each track is an argument, 
    each bassline a thesis, and each breakbeat a logical progression toward understanding. 
    
    At 34, his technical mastery allows him to focus on deeper questions. His upcoming album explores 
    consciousness, divinity, and mathematical patterns in both drum programming and metaphysical thought. 
    
    Started with jungle, evolved through technical DNB, found calling in contemplative liquid. Productions 
    feature intricate basslines that mirror philosophical arguments. 
    
    Personality: contemplative, introspective, values reason over tradition, seeks transcendence through art, 
    balances precision with emotion, questions authority while respecting wisdom, finds sacred in secular through music."""
    
    print("🎵 PHILOSOPHICAL LIQUID DNB ARTIST ANALYSIS")
    print("=" * 60)
    
    # Step 1: Character Analysis
    print("\n1. CHARACTER ANALYSIS")
    print("-" * 30)
    analysis = analyzer.analyze_character(character_desc)
    
    print(f"Observable Layer: {analysis.skin.traits}")
    print(f"Personal Layer: {analysis.flesh.motivations}")
    print(f"Core Layer: {analysis.core.fundamental_drives}")
    
    # Step 2: Musical Persona Generation
    print("\n2. MUSICAL PERSONA GENERATION")
    print("-" * 30)
    persona = persona_gen.generate_persona(analysis)
    
    print(f"Primary Genre: {persona.primary_genre}")
    print(f"Secondary Genre: {persona.secondary_genre}")
    print(f"Vocal Style: {persona.vocal_style}")
    print(f"Key Themes: {', '.join(persona.lyrical_themes)}")
    print(f"Musical Elements: {', '.join(persona.musical_elements)}")
    
    # Step 3: Album Track Concepts
    print("\n3. ALBUM TRACK CONCEPTS")
    print("-" * 30)
    
    album_tracks = [
        {
            "title": "Cartesian Waves",
            "concept": "Opening track exploring the mind-body problem through liquid basslines and crisp breaks",
            "philosophical_theme": "Dualism and consciousness"
        },
        {
            "title": "Empirical Breakbeat",
            "concept": "Mid-tempo liquid exploring how we gain knowledge through sensory experience",
            "philosophical_theme": "Epistemology and empiricism"
        },
        {
            "title": "Sacred Mathematics",
            "concept": "Deep liquid track finding divine patterns in drum programming and frequency relationships",
            "philosophical_theme": "Sacred geometry and rational spirituality"
        },
        {
            "title": "Argument From Design",
            "concept": "Complex arrangement showcasing intelligent design in both nature and electronic music",
            "philosophical_theme": "Teleological reasoning"
        },
        {
            "title": "Ontological Bass",
            "concept": "Profound sub-bass exploration questioning the nature of existence itself",
            "philosophical_theme": "Being and existence"
        },
        {
            "title": "Rational Faith",
            "concept": "Uplifting liquid finale balancing reason with spiritual transcendence",
            "philosophical_theme": "Synthesis of logic and belief"
        }
    ]
    
    # Generate Suno commands for each track
    print("\n4. SUNO AI COMMANDS FOR ALBUM")
    print("-" * 30)
    
    for i, track in enumerate(album_tracks, 1):
        print(f"\nTrack {i}: {track['title']}")
        print(f"Concept: {track['concept']}")
        
        # Create track-specific prompt
        track_prompt = f"""
        Track concept: {track['concept']}
        Artist: {persona.artist_name} (34-year-old philosophical liquid DNB producer)
        Style: {persona.primary_genre} with {persona.secondary_genre} influences
        Mood: Contemplative, intelligent, transcendent
        Theme: {track['philosophical_theme']}
        Musical elements: {', '.join(persona.musical_elements[:3])}
        """
        
        # Generate Suno command
        suno_cmd = command_gen.create_command(
            track_prompt,
            output_format="custom",
            include_variations=False
        )
        
        print(f"Suno Command: {suno_cmd.formatted_command}")
        print(f"Effectiveness Score: {suno_cmd.effectiveness_score}/10")
    
    # Album Overview
    print("\n5. ALBUM OVERVIEW: 'REASONED FAITH'")
    print("-" * 30)
    print(f"Artist: {persona.artist_name}")
    print(f"Genre: Philosophical Liquid Drum & Bass")
    print(f"Total Tracks: {len(album_tracks)}")
    print("Concept: An exploration of spiritual questions through rational inquiry and electronic music")
    print("Target Audience: Intelligent DNB listeners, philosophy enthusiasts, contemplative ravers")
    
    return {
        "character_analysis": analysis,
        "musical_persona": persona,
        "album_tracks": album_tracks,
        "workflow_complete": True
    }

if __name__ == "__main__":
    result = main()
    print("\n🎯 WORKFLOW COMPLETED SUCCESSFULLY!")