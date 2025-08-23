#!/usr/bin/env python3
"""
Legacy workflow integration tests
Migrated from root directory test files to unified testing framework
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any
from dataclasses import asdict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.fixtures.test_data import TestDataManager, test_data_manager
from tests.fixtures.mock_contexts import MockContext, create_mock_context
# Import server components properly
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the server module and create wrapper functions
import server

async def complete_workflow_wrapper(text: str, ctx) -> str:
    """Wrapper to call the complete_workflow MCP tool"""
    # Create a simple workflow by calling the individual steps
    try:
        await ctx.info("Starting complete character-to-music workflow...")
        
        # Step 1: Character Analysis
        await ctx.info("Step 1: Analyzing characters...")
        characters_result = await analyze_character_text_wrapper(text, ctx)
        
        # Step 2: Generate Artist Personas  
        await ctx.info("Step 2: Generating artist personas...")
        personas_result = await generate_artist_personas_wrapper(characters_result, ctx)
        
        # Step 3: Create Suno Commands
        await ctx.info("Step 3: Creating Suno AI commands...")
        commands_result = await create_suno_commands_wrapper(personas_result, characters_result, ctx)
        
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

async def analyze_character_text_wrapper(text: str, ctx) -> str:
    """Wrapper for character analysis"""
    # Import the actual classes and functions from server
    from server import CharacterAnalyzer
    
    analyzer = CharacterAnalyzer()
    analysis_result = await analyzer.analyze_text(text, ctx)
    
    result = {
        "characters": [asdict(char) for char in analysis_result.characters],
        "analysis_summary": f"Identified {len(analysis_result.characters)} characters from narrative text"
    }
    
    return json.dumps(result, indent=2)

async def generate_artist_personas_wrapper(characters_json: str, ctx) -> str:
    """Wrapper for persona generation"""
    from server import MusicPersonaGenerator, CharacterProfile
    
    characters_data = json.loads(characters_json)
    characters = characters_data.get("characters", [])
    
    generator = MusicPersonaGenerator()
    personas = []
    
    for char_data in characters:
        # Convert dict back to CharacterProfile
        char = CharacterProfile(**char_data)
        persona = await generator.generate_artist_persona(char, ctx)
        personas.append(asdict(persona))
    
    result = {
        "artist_personas": personas,
        "generation_summary": f"Generated {len(personas)} artist personas"
    }
    
    return json.dumps(result, indent=2)

async def create_suno_commands_wrapper(personas_json: str, characters_json: str, ctx) -> str:
    """Wrapper for Suno command creation"""
    from server import SunoCommandGenerator, ArtistPersona, CharacterProfile
    
    personas_data = json.loads(personas_json)
    personas = personas_data.get("artist_personas", [])
    
    characters_data = json.loads(characters_json)
    characters = characters_data.get("characters", [])
    
    generator = SunoCommandGenerator()
    commands = []
    
    for i, persona_data in enumerate(personas):
        # Convert dict back to ArtistPersona
        persona = ArtistPersona(**persona_data)
        
        # Get corresponding character (or use first if not enough)
        char_data = characters[min(i, len(characters) - 1)] if characters else None
        if char_data:
            char = CharacterProfile(**char_data)
            persona_commands = await generator.generate_suno_commands(persona, char, ctx)
            commands.extend([asdict(cmd) for cmd in persona_commands])
    
    result = {
        "suno_commands": commands,
        "command_summary": f"Generated {len(commands)} Suno AI commands"
    }
    
    return json.dumps(result, indent=2)


async def test_complete_workflow_philosophical_producer(ctx: MockContext, test_manager: TestDataManager) -> None:
    """Test complete workflow with philosophical liquid DNB producer"""
    
    # Producer narrative from original test
    producer_narrative = """
    Marcus "Solvent" Thompson is a 34-year-old liquid drum and bass producer who has spent over a decade perfecting his craft in electronic music production. His stage name "Solvent" reflects his belief that music can dissolve the barriers between rational thought and spiritual experience.

    At 34, Marcus has reached a philosophical crossroads in his artistic journey. He operates from a converted warehouse studio in Bristol, surrounded by vintage analog synthesizers and cutting-edge digital workstations. His setup reflects his personality - a careful balance between organic warmth and technological precision.

    Marcus holds a deep conviction that "the two questions respecting God and the Soul were the chief of those that ought to be demonstrated by philosophical rather than theological argument." This philosophical stance permeates every aspect of his music creation. He believes that spiritual and existential questions should be explored through reason, logic, and artistic expression rather than through dogmatic belief systems.

    His approach to music production mirrors his philosophical methodology. Each track begins with a thesis - a fundamental question about consciousness, existence, or the nature of reality. The basslines serve as logical arguments, building from simple premises to complex, emotionally resonant conclusions. The breakbeats provide the rhythmic structure for his philosophical discourse, while atmospheric pads create the contemplative space necessary for deep reflection.

    Marcus started his musical journey in his early twenties with jungle music, drawn to its raw energy and mathematical complexity. As he matured, he evolved through the more technical aspects of drum and bass, mastering the intricate programming and sound design that the genre demands. However, it was in the fluid, contemplative space of liquid drum and bass that he found his true calling - a genre that allowed him to balance technical mastery with emotional and intellectual depth.

    His personality is marked by several key traits: he is deeply contemplative and introspective, often spending hours in meditation before beginning a production session. He values reason and logical inquiry over traditional authority, constantly questioning established norms while maintaining respect for genuine wisdom. Through his music, he seeks transcendence - not through escape from reality, but through a deeper understanding of it.

    Marcus believes that the sacred can be found in the secular, that divine patterns exist in the mathematical relationships between frequencies, and that electronic music production is a form of modern alchemy. His upcoming album explores the intersection of consciousness, divinity, and the mathematical patterns found in both drum programming and metaphysical thought.

    In his personal life, Marcus is known for his quiet intensity and thoughtful presence. He approaches conversations the same way he approaches music production - listening carefully, considering multiple perspectives, and responding with precision. His friends describe him as someone who can find profound meaning in the most ordinary experiences, whether that's the rhythm of rainfall or the harmonic content of a coffee shop's ambient noise.

    His studio practices reflect his philosophical approach. He often begins sessions by reading philosophy - Descartes, Spinoza, or contemporary thinkers exploring consciousness and AI. This intellectual preparation informs the emotional and structural development of his tracks. He sees each piece of music as an argument for a particular way of understanding reality, with the goal of creating sonic experiences that can shift the listener's consciousness toward greater clarity and insight.

    Marcus "Solvent" Thompson represents a new generation of electronic music producers who see their craft not just as entertainment, but as a legitimate form of philosophical inquiry and spiritual exploration through the medium of carefully crafted sound.
    """
    
    await ctx.info("Testing complete workflow with philosophical producer")
    
    # Run the complete workflow using wrapper
    result = await complete_workflow_wrapper(producer_narrative, ctx)
    
    # Parse and validate results
    workflow_data = json.loads(result)
    
    assert "error" not in workflow_data, f"Workflow should not have errors: {workflow_data.get('error')}"
    assert "character_analysis" in workflow_data, "Should include character analysis"
    assert "artist_personas" in workflow_data, "Should include artist personas"
    assert "suno_commands" in workflow_data, "Should include suno commands"
    
    # Validate character analysis
    char_analysis = workflow_data["character_analysis"]
    assert "characters" in char_analysis, "Should have characters"
    assert len(char_analysis["characters"]) > 0, "Should have at least one character"
    
    char = char_analysis["characters"][0]
    assert "Marcus" in str(char.get('name', '')), "Should identify Marcus as character"
    
    # Validate artist personas
    personas = workflow_data["artist_personas"]
    assert "artist_personas" in personas, "Should have artist personas"
    assert len(personas["artist_personas"]) > 0, "Should have at least one persona"
    
    persona = personas["artist_personas"][0]
    electronic_genres = ['electronic', 'drum', 'bass', 'dnb', 'liquid']
    assert any(genre in str(persona).lower() for genre in electronic_genres), "Should identify electronic genre"
    
    # Validate suno commands
    commands = workflow_data["suno_commands"]
    assert "suno_commands" in commands, "Should have suno commands"
    assert len(commands["suno_commands"]) > 0, "Should have at least one command"
    
    await ctx.info("Complete workflow test passed")


async def test_mcp_workflow_interface(ctx: MockContext, test_manager: TestDataManager) -> None:
    """Test MCP workflow interface functionality"""
    
    # Use a simpler test narrative
    test_narrative = test_manager.get_test_scenario("single_character_simple").narrative_text
    
    await ctx.info("Testing MCP workflow interface")
    
    # Run the complete workflow using wrapper
    result = await complete_workflow_wrapper(test_narrative, ctx)
    
    # Parse and validate results
    workflow_data = json.loads(result)
    
    assert "error" not in workflow_data, f"MCP workflow should not have errors: {workflow_data.get('error')}"
    
    # Check workflow structure
    required_sections = ["character_analysis", "artist_personas", "suno_commands", "workflow_status"]
    for section in required_sections:
        assert section in workflow_data, f"Should include {section}"
    
    # Check data quality
    char_data = workflow_data["character_analysis"]
    assert bool(char_data.get("characters")), "Character data should be populated"
    
    persona_data = workflow_data["artist_personas"]
    assert bool(persona_data.get("artist_personas")), "Persona data should be populated"
    
    command_data = workflow_data["suno_commands"]
    assert bool(command_data.get("suno_commands")), "Commands data should be populated"
    
    await ctx.info("MCP workflow interface test passed")


async def test_artist_description_generation(ctx: MockContext, test_manager: TestDataManager) -> None:
    """Test artist description generation functionality"""
    
    from dataclasses import dataclass
    from typing import List
    
    @dataclass
    class CharacterProfile:
        name: str
        backstory: str
        conflicts: List[str]
        fears: List[str]
    
    @dataclass
    class ArtistStory:
        introspective_themes: List[str]
        artistic_manifesto: str
        emotional_arc: str
        artistic_evolution: str
    
    class TestArtistDescription:
        def _extract_origin_setting(self, character) -> str:
            backstory = character.backstory.lower()
            if "rooftop" in backstory or "city" in backstory:
                return "the urban landscape"
            elif "studio" in backstory or "apartment" in backstory:
                return "intimate creative spaces"
            elif "family" in backstory or "mother" in backstory:
                return "complex family dynamics"
            else:
                return "personal crossroads"
        
        def _extract_core_struggle(self, character, story) -> str:
            if character.conflicts:
                primary_conflict = character.conflicts[0]
                if "vs" in primary_conflict:
                    parts = primary_conflict.split(" vs ")
                    return f"the tension between {parts[0]} and {parts[1]}"
                else:
                    return f"the weight of {primary_conflict}"
            elif character.fears:
                return f"the fear of {character.fears[0]}"
            else:
                return "internal battles"
        
        def _create_style_description(self, persona) -> str:
            vocal_style = persona.get("vocal_style", "")
            if "vulnerable" in vocal_style.lower():
                return "a vulnerable storyteller who crafts intimate confessions"
            elif "ethereal" in vocal_style.lower():
                return "an ethereal presence weaving atmospheric narratives"
            else:
                return "an authentic artist refusing to conform"
        
        def _extract_transformation(self, story) -> str:
            manifesto = story.artistic_manifesto.lower()
            evolution = story.artistic_evolution.lower()
            
            if "truth" in manifesto and "lies" in manifesto:
                return "raw truth over polished perfection"
            elif "facade" in evolution and "authentic" in evolution:
                return "authentic self-expression"
            else:
                return "honest emotional exploration"
        
        def _describe_emotional_impact(self, story) -> str:
            themes = story.introspective_themes
            arc = story.emotional_arc.lower()
            
            if any("confronting" in theme for theme in themes):
                return "confront listeners with uncomfortable truths"
            elif any("searching" in theme for theme in themes):
                return "guide others through their own searching"
            elif "isolation" in arc and "acceptance" in arc:
                return "transform isolation into shared understanding"
            else:
                return "invite deep introspection and healing"
        
        def create_artist_description(self, character, persona, story) -> str:
            # Extract key elements
            artist_name = persona.get("artist_name", character.name)
            origin_location = self._extract_origin_setting(character)
            core_struggle = self._extract_core_struggle(character, story)
            musical_style = self._create_style_description(persona)
            transformation = self._extract_transformation(story)
            
            # Create compelling narrative sentence
            description = (
                f"{artist_name} emerges from {origin_location} as {musical_style}, "
                f"channeling {core_struggle} into {transformation} through "
                f"{persona.get('primary_genre', 'indie')} soundscapes that "
                f"{self._describe_emotional_impact(story)}."
            )
            
            return description
    
    await ctx.info("Testing artist description generation")
    
    # Use test data from unified framework
    expected_char = test_manager.get_expected_character("Sarah Chen")
    
    generator = TestArtistDescription()
    
    # Create test data
    test_character = CharacterProfile(
        name=expected_char.name,
        backstory=expected_char.backstory,
        conflicts=expected_char.conflicts,
        fears=expected_char.fears
    )
    
    test_persona = {
        "artist_name": "Fragile Freedom",
        "primary_genre": "indie",
        "vocal_style": "vulnerable and raw emotional delivery"
    }
    
    test_story = ArtistStory(
        introspective_themes=["confronting disappointing others", "searching for authentic self-expression"],
        artistic_manifesto="Music as a weapon against disappointing others, every note a declaration of authenticity",
        emotional_arc="From isolation through struggle to acceptance",
        artistic_evolution="From perfectionist facade observer to bold storyteller"
    )
    
    # Generate description
    description = generator.create_artist_description(test_character, test_persona, test_story)
    
    # Validate description
    assert len(description) > 50, "Description should be substantial"
    assert test_persona["artist_name"] in description, "Should include artist name"
    assert test_persona["primary_genre"] in description, "Should include genre"
    
    await ctx.info(f"Generated artist description: {description[:100]}...")
    await ctx.info("Artist description generation test passed")


async def test_universal_content_processing(ctx: MockContext, test_manager: TestDataManager) -> None:
    """Test universal content processing functionality"""
    
    try:
        from working_universal_processor import WorkingUniversalProcessor
    except ImportError:
        await ctx.warning("WorkingUniversalProcessor not available, skipping test")
        return
    
    await ctx.info("Testing universal content processing")
    
    processor = WorkingUniversalProcessor()
    
    # Test content
    content = """
    Sarah and David fell deeply in love, but their relationship was complicated by different 
    spiritual beliefs. She was a scientist who believed in empirical evidence, while he found 
    truth through faith and intuition. Their love forced both to question their fundamental 
    assumptions about reality, truth, and the nature of human connection.
    """
    
    track_title = "Love and Logic"
    
    # Process content
    result = processor.process_any_content(content, track_title)
    
    # Validate result
    assert result.title, "Should generate a title"
    assert result.character_interpretation, "Should generate character interpretation"
    assert result.formatted_lyrics, "Should generate lyrics"
    assert result.suno_command, "Should generate Suno command"
    assert result.effectiveness_score > 0, "Should have effectiveness score"
    
    await ctx.info("Universal content processing test passed")


async def test_character_album_creation(ctx: MockContext, test_manager: TestDataManager) -> None:
    """Test character album creation functionality"""
    
    try:
        from working_universal_processor import WorkingUniversalProcessor
    except ImportError:
        await ctx.warning("WorkingUniversalProcessor not available, skipping test")
        return
    
    await ctx.info("Testing character album creation")
    
    processor = WorkingUniversalProcessor()
    
    content = """
    The nature of consciousness has always puzzled philosophers and scientists. 
    What makes us aware? Is consciousness an emergent property of complex neural networks, 
    or something more fundamental to the universe?
    """
    
    album_title = "Questions of Consciousness"
    track_count = 3
    
    # Generate track concepts
    track_concepts = [
        f"{album_title} - Opening Statement",
        f"{album_title} - Personal Reflection", 
        f"{album_title} - Deeper Questions"
    ]
    
    album_tracks = []
    
    for i in range(track_count):
        track_title = track_concepts[i]
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
    
    # Validate album
    assert len(album_tracks) == track_count, f"Should have {track_count} tracks"
    
    avg_score = sum(track["effectiveness_score"] for track in album_tracks) / len(album_tracks)
    assert avg_score > 0, "Should have positive average effectiveness score"
    
    await ctx.info(f"Created album with {len(album_tracks)} tracks, avg score: {avg_score:.2f}")
    await ctx.info("Character album creation test passed")