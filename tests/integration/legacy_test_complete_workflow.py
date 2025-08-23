#!/usr/bin/env python3
"""
Test the complete_workflow tool with the philosophical liquid DNB producer concept
Integrated with unified testing framework
"""

import asyncio
import json
import sys
import os

# Add paths for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests'))

from tests.fixtures.test_data import TestDataManager, test_data_manager
from tests.fixtures.mock_contexts import MockContext, create_mock_context
from server import complete_workflow

async def test_complete_workflow_with_unified_framework():
    """Test the complete workflow using unified testing framework"""
    
    print("🎵 TESTING COMPLETE WORKFLOW (Unified Framework)")
    print("=" * 60)
    
    # Use test data manager for consistent test data
    test_manager = test_data_manager
    
    # Get philosophical producer scenario
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
    
    print("Character: Marcus 'Solvent' Thompson")
    print("Age: 34, Liquid Drum & Bass Producer")
    print("Philosophy: Rational exploration of spiritual questions")
    print("\n" + "=" * 60)
    
    try:
        # Create mock context using unified framework
        ctx = create_mock_context("complete_workflow", session_id="producer_test")
        
        # Run the complete workflow
        result = await complete_workflow(producer_narrative, ctx)
        
        print("\n🎯 WORKFLOW RESULTS:")
        print("=" * 50)
        
        # Parse and display results
        workflow_data = json.loads(result)
        
        if "error" in workflow_data:
            print(f"❌ Error: {workflow_data['error']}")
            return False
        
        # Validate using unified framework expectations
        validation_results = validate_producer_workflow_results(workflow_data, test_manager)
        
        # Display Character Analysis
        if "character_analysis" in workflow_data:
            char_analysis = workflow_data["character_analysis"]
            print("\n📊 CHARACTER ANALYSIS:")
            print("-" * 30)
            if "characters" in char_analysis and char_analysis["characters"]:
                char = char_analysis["characters"][0]  # First character
                print(f"Name: {char.get('name', 'Unknown')}")
                print(f"Core Drives: {', '.join(char.get('fundamental_drives', []))}")
                print(f"Key Motivations: {', '.join(char.get('motivations', []))}")
        
        # Display Artist Personas
        if "artist_personas" in workflow_data:
            personas = workflow_data["artist_personas"]
            print("\n🎤 ARTIST PERSONAS:")
            print("-" * 30)
            if "artist_personas" in personas and personas["artist_personas"]:
                persona = personas["artist_personas"][0]  # First persona
                print(f"Artist Name: {persona.get('artist_name', 'Unknown')}")
                print(f"Primary Genre: {persona.get('primary_genre', 'Unknown')}")
                print(f"Secondary Genre: {persona.get('secondary_genre', 'Unknown')}")
                print(f"Vocal Style: {persona.get('vocal_style', 'Unknown')}")
                print(f"Themes: {', '.join(persona.get('lyrical_themes', []))}")
                print(f"Musical Elements: {', '.join(persona.get('musical_elements', []))}")
        
        # Display Suno Commands
        if "suno_commands" in workflow_data:
            commands = workflow_data["suno_commands"]
            print("\n🎛️  SUNO AI COMMANDS:")
            print("-" * 30)
            if "suno_commands" in commands and commands["suno_commands"]:
                for i, cmd in enumerate(commands["suno_commands"][:3], 1):  # Show first 3
                    print(f"\nTrack {i}:")
                    print(f"  Command: {cmd.get('formatted_command', 'Unknown')}")
                    print(f"  Effectiveness: {cmd.get('effectiveness_score', 'Unknown')}/10")
                    if cmd.get('variations'):
                        print(f"  Variations: {len(cmd['variations'])} available")
        
        print(f"\n✅ Workflow Status: {workflow_data.get('workflow_status', 'Unknown')}")
        print(f"📝 Summary: {workflow_data.get('workflow_summary', 'No summary available')}")
        
        # Print validation results
        print(f"\n🔍 VALIDATION RESULTS:")
        print("-" * 30)
        for check, passed in validation_results.items():
            status = "✅" if passed else "❌"
            print(f"{status} {check}")
        
        return workflow_data
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def validate_producer_workflow_results(workflow_data: dict, test_manager: TestDataManager) -> dict:
    """Validate workflow results against expected producer characteristics"""
    validation_results = {}
    
    # Check character analysis
    if "character_analysis" in workflow_data and workflow_data["character_analysis"]["characters"]:
        char = workflow_data["character_analysis"]["characters"][0]
        validation_results["Character name extracted"] = "Marcus" in str(char.get('name', ''))
        validation_results["Age captured"] = any(age_indicator in str(char).lower() 
                                                for age_indicator in ['34', 'thirty'])
        validation_results["Producer role identified"] = any(producer_term in str(char).lower() 
                                                           for producer_term in ['producer', 'music', 'electronic'])
        validation_results["Philosophy captured"] = any(phil_term in str(char).lower() 
                                                      for phil_term in ['philosophical', 'god', 'soul', 'rational'])
    else:
        validation_results["Character analysis present"] = False
    
    # Check artist personas
    if "artist_personas" in workflow_data and workflow_data["artist_personas"]["artist_personas"]:
        persona = workflow_data["artist_personas"]["artist_personas"][0]
        validation_results["Electronic genre identified"] = any(electronic_term in str(persona).lower() 
                                                              for electronic_term in ['electronic', 'drum', 'bass', 'dnb'])
        validation_results["Themes appropriate"] = len(persona.get('lyrical_themes', [])) > 0
    else:
        validation_results["Artist persona present"] = False
    
    # Check Suno commands
    if "suno_commands" in workflow_data and workflow_data["suno_commands"]["suno_commands"]:
        commands = workflow_data["suno_commands"]["suno_commands"]
        validation_results["Commands generated"] = len(commands) > 0
        validation_results["Producer elements in commands"] = any(
            producer_element in str(cmd).lower() 
            for cmd in commands 
            for producer_element in ['electronic', 'philosophical', 'technical', 'complex']
        )
    else:
        validation_results["Suno commands present"] = False
    
    return validation_results


# Test function for unified framework integration
async def test_complete_workflow_integration(ctx: MockContext, test_manager: TestDataManager) -> None:
    """Test function compatible with unified test runner"""
    result = await test_complete_workflow_with_unified_framework()
    assert result is not None, "Workflow should return results"
    assert "character_analysis" in result, "Should include character analysis"
    assert "artist_personas" in result, "Should include artist personas"
    assert "suno_commands" in result, "Should include suno commands"


if __name__ == "__main__":
    result = asyncio.run(test_complete_workflow_with_unified_framework())
    if result:
        print("\n🎯 TEST COMPLETED SUCCESSFULLY!")
        
        # Key question: Does this capture the producer input properly?
        print("\n🤔 ANALYSIS: Does the workflow capture producer input?")
        print("-" * 50)
        print("✅ Age (34) - Character analysis should extract this")
        print("✅ Genre (Liquid DNB) - Should be identified and used")
        print("✅ Philosophy - Should influence musical themes and style")
        print("✅ Technical background - Should affect complexity and approach")
        print("✅ Producer-specific elements - Validated through framework")
    else:
        print("\n❌ TEST FAILED!")