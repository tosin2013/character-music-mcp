#!/usr/bin/env python3
"""
Character-Driven Music Generation MCP Server - Usage Examples

This file demonstrates various usage patterns and workflows for the MCP server.
These examples show how to interact with the server both programmatically and
through the MCP client interface.
"""

import asyncio
import json

# Sample narrative texts for testing
SAMPLE_NARRATIVES = {
    "fantasy_adventure": """
    Elara stood at the edge of the ancient forest, her silver bow gleaming in the moonlight. 
    She had always been the fearless one among her companions, the elf who charged into danger 
    while others hesitated. Her emerald eyes held centuries of wisdom, yet they also carried 
    the weight of loss - her family had been destroyed by the dark sorcerer Malachar, and 
    revenge burned in her heart like an unquenchable flame.
    
    "We move at dawn," she whispered to her companion, Marcus, a gruff human warrior whose 
    loyalty had never wavered despite the dangers they faced. Marcus nodded, understanding 
    the pain that drove her forward. He had his own demons - a past as a royal guard who 
    had failed to protect his king, leading to a life of wandering and self-imposed exile.
    
    In the distance, they could see the flickering lights of the enemy camp. Tonight would 
    determine their fate, and Elara felt the familiar mix of fear and determination that 
    had carried her through countless battles.
    """,

    "modern_drama": """
    Sarah Chen stared at her reflection in the coffee shop window, wondering when she had 
    become so tired. At thirty-five, she was a successful architect with a corner office 
    and a reputation for innovative designs, but something felt hollow inside. Her phone 
    buzzed with another message from her mother, asking when she would settle down and 
    give her grandchildren.
    
    "Another late night at the office?" asked David, sliding into the seat across from her. 
    Her oldest friend since college, David had always been the dreamer while she was the 
    practical one. Now he ran a small nonprofit and seemed more fulfilled than she had ever felt.
    
    "I've been thinking about what you said," Sarah admitted, pushing her untouched latte 
    away. "About finding something that matters." David smiled knowingly - he had been 
    waiting for this conversation for years, watching his ambitious friend climb the 
    corporate ladder while losing pieces of herself along the way.
    """,

    "mystery_thriller": """
    Detective Ray Morrison lit his third cigarette of the morning as he studied the crime 
    scene photos spread across his cluttered desk. Twenty years on the force had taught 
    him to read between the lines, to see the stories that evidence told. This case was 
    different though - personal in a way that made his hands shake as he reached for his coffee.
    
    The victim, Maria Santos, had been a witness in a case he'd worked five years ago. 
    Back then, she'd been terrified but brave, willing to testify against the crime family 
    that had destroyed her neighborhood. Ray had promised her protection, assured her that 
    justice would prevail. Now she was dead, and he couldn't shake the feeling that his 
    failure to keep that promise had cost an innocent woman her life.
    
    His partner, Detective Lisa Wong, watched him with concern. She was younger, more optimistic, 
    still believing that the system worked. "Ray, we'll find who did this," she said quietly. 
    But Ray knew that some promises, once broken, could never be repaired.
    """
}

async def demo_complete_workflow():
    """Demonstrate the complete character-to-music workflow"""
    print("🎭 Character-Driven Music Generation Demo")
    print("=" * 50)

    # For demo purposes, we'll simulate the MCP server responses
    # In actual usage, you would connect to the running MCP server

    narrative = SAMPLE_NARRATIVES["fantasy_adventure"]

    print("📖 Sample Narrative:")
    print(narrative[:200] + "...")
    print()

    print("🔍 Step 1: Character Analysis")
    print("Analyzing narrative text for character profiles...")

    # Simulated character analysis result
    character_analysis = {
        "characters": [
            {
                "name": "Elara",
                "aliases": ["The Silver Archer"],
                "physical_description": "Elf with emerald eyes and silver bow, moves with practiced grace",
                "mannerisms": ["stands at edges observing", "whispers when planning", "touches bow when nervous"],
                "speech_patterns": ["direct communication", "military-style commands", "soft-spoken intensity"],
                "behavioral_traits": ["fearless: charges into danger", "loyal: protective of companions"],
                "backstory": "Family destroyed by dark sorcerer Malachar, seeks revenge",
                "relationships": ["Marcus - trusted human companion", "Lost family - source of motivation"],
                "formative_experiences": ["Family destruction by Malachar", "Becoming a warrior", "Meeting Marcus"],
                "motivations": ["Revenge against Malachar", "Protecting innocent people", "Honoring family memory"],
                "fears": ["Failing to protect others", "Being too late for justice", "Losing Marcus"],
                "personality_drivers": ["brave (strength: 3)", "vengeful (strength: 2)", "protective (strength: 2)"],
                "confidence_score": 0.9,
                "importance_score": 0.95
            }
        ],
        "narrative_themes": ["revenge", "justice", "friendship", "sacrifice"],
        "emotional_arc": ["Section 1: determination", "Section 2: loyalty", "Section 3: anticipation"]
    }

    print(f"✅ Found {len(character_analysis['characters'])} character(s)")
    print(f"   - Primary character: {character_analysis['characters'][0]['name']}")
    print(f"   - Key traits: {', '.join(character_analysis['characters'][0]['personality_drivers'][:2])}")
    print()

    print("🎵 Step 2: Artist Persona Generation")
    print("Mapping character psychology to musical identity...")

    # Simulated artist persona generation
    artist_persona = {
        "character_name": "Elara",
        "artist_name": "Elara Storm",
        "primary_genre": "epic orchestral",
        "secondary_genres": ["symphonic metal", "cinematic rock"],
        "vocal_style": "powerful, commanding vocals with ethereal undertones",
        "lyrical_themes": ["justice and vengeance", "protection of innocents", "honor and sacrifice"],
        "emotional_palette": ["determination", "intensity", "nobility"],
        "artistic_influences": ["epic film composers", "symphonic metal masters", "classical orchestrators"],
        "persona_description": "Epic orchestral artist channeling ancient warrior spirit with modern cinematic power",
        "character_mapping_confidence": 0.85
    }

    print(f"✅ Generated artist persona: {artist_persona['artist_name']}")
    print(f"   - Primary genre: {artist_persona['primary_genre']}")
    print(f"   - Vocal style: {artist_persona['vocal_style']}")
    print()

    print("🎼 Step 3: Suno AI Command Generation")
    print("Creating optimized music generation commands...")

    # Simulated Suno command generation
    suno_commands = [
        {
            "command_type": "simple",
            "prompt": "An epic orchestral composition about a fearless elven warrior seeking justice for her fallen family, with powerful commanding vocals and cinematic intensity",
            "estimated_effectiveness": 0.9,
            "rationale": "Simple command focusing on core epic orchestral elements and Elara's primary emotional themes"
        },
        {
            "command_type": "custom",
            "prompt": "Create an epic orchestral piece exploring justice and vengeance. The music should embody determination and intensity while reflecting Elara's brave and protective nature",
            "style_tags": ["epic orchestral", "cinematic", "powerful", "heroic"],
            "structure_tags": ["building intensity", "dramatic climax", "resolution"],
            "vocal_tags": ["commanding vocals", "ethereal undertones", "heroic delivery"],
            "estimated_effectiveness": 0.95,
            "rationale": "Custom command leveraging detailed character analysis for nuanced epic orchestral composition"
        },
        {
            "command_type": "bracket_notation",
            "prompt": "[epic orchestral] [determination] [powerful commanding vocals] [strings, brass, percussion] [heroic energy] Song inspired by Elara's journey through justice and vengeance",
            "estimated_effectiveness": 0.88,
            "rationale": "Bracket notation command for precise musical element control based on character analysis"
        }
    ]

    print(f"✅ Generated {len(suno_commands)} optimized commands")
    for i, cmd in enumerate(suno_commands, 1):
        print(f"   {i}. {cmd['command_type'].title()} Command (effectiveness: {cmd['estimated_effectiveness']})")
        print(f"      \"{cmd['prompt'][:80]}...\"")
    print()

    print("🎯 Workflow Complete!")
    print("Character successfully transformed into musical artist with Suno AI commands.")

async def demo_creative_mode():
    """Demonstrate creative music generation from abstract concepts"""
    print("\n🎨 Creative Music Generation Demo")
    print("=" * 40)

    concepts = [
        "The silence between raindrops",
        "Digital nostalgia in a cyberpunk world",
        "The weight of unspoken words"
    ]

    for concept in concepts:
        print(f"💡 Concept: \"{concept}\"")

        # Simulated creative generation
        creative_result = {
            "concept": concept,
            "detected_emotion": "contemplative and atmospheric",
            "creative_commands": [
                {
                    "type": "atmospheric",
                    "prompt": f"Create an atmospheric composition that embodies the concept of '{concept}'. The music should be contemplative and atmospheric with ambient textures and evolving soundscapes.",
                    "approach": "Ambient and textural interpretation"
                },
                {
                    "type": "melodic",
                    "prompt": f"Write a melodic composition that musically translates '{concept}'. The melody should be contemplative and atmospheric and capture the essence of the idea.",
                    "approach": "Melody-centered interpretation"
                }
            ]
        }

        print(f"   🎵 Generated {len(creative_result['creative_commands'])} interpretations")
        for cmd in creative_result['creative_commands']:
            print(f"      - {cmd['approach']}")
        print()

async def demo_mcp_client_integration():
    """Demonstrate MCP client integration patterns"""
    print("\n🔌 MCP Client Integration Demo")
    print("=" * 40)

    print("Example MCP client usage:")
    print("""
    # Connect to the MCP server
    async with Client("./run.sh") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")
        
        # Analyze narrative text
        result = await client.call_tool("analyze_character_text", {
            "text": narrative_content
        })
        
        # Generate artist personas
        personas = await client.call_tool("generate_artist_personas", {
            "characters_json": result.text
        })
        
        # Create Suno commands
        commands = await client.call_tool("create_suno_commands", {
            "personas_json": personas.text,
            "characters_json": result.text
        })
    """)

def demo_configuration_examples():
    """Show configuration examples for different deployment scenarios"""
    print("\n⚙️  Configuration Examples")
    print("=" * 35)

    print("Claude Desktop MCP Configuration:")
    claude_config = {
        "mcpServers": {
            "character-music": {
                "command": "sh",
                "args": ["/path/to/character-music-mcp/run.sh"],
                "env": {
                    "SUNO_COOKIE": "optional_suno_session_cookie",
                    "TWOCAPTCHA_KEY": "optional_captcha_solving_key"
                }
            }
        }
    }
    print(json.dumps(claude_config, indent=2))

    print("\nDocker Compose Configuration:")
    print("""
    services:
      character-music-mcp:
        build: .
        environment:
          - SUNO_COOKIE=${SUNO_COOKIE}
          - TWOCAPTCHA_KEY=${TWOCAPTCHA_KEY}
        volumes:
          - ./data:/app/data
        ports:
          - "8000:8000"
    """)

async def main():
    """Run all demonstration examples"""
    print("🎭🎵 Character-Driven Music Generation MCP Server")
    print("Demonstration and Usage Examples")
    print("=" * 60)

    # Run demonstrations
    await demo_complete_workflow()
    await demo_creative_mode()
    await demo_mcp_client_integration()
    demo_configuration_examples()

    print("\n✨ Demonstration Complete!")
    print("This MCP server bridges narrative content and musical expression")
    print("through systematic character psychology analysis.")

if __name__ == "__main__":
    asyncio.run(main())
