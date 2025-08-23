# Character-Driven Music Generation MCP Server

A revolutionary Model Context Protocol (MCP) server that bridges narrative content and musical expression through systematic character psychology analysis. This FastMCP-based server extracts detailed character profiles from unlimited-length text and transforms them into coherent musical artist personas with optimized Suno AI commands.

## Overview

This MCP server implements a comprehensive pipeline that:

1. **Analyzes narrative text** using advanced three-layer character bible methodology
2. **Extracts character profiles** with psychological depth and narrative importance ranking
3. **Generates musical artist personas** through sophisticated trait-to-genre mapping
4. **Creates optimized Suno AI commands** with multiple variations and approaches
5. **Supports creative workflows** for both character-driven and abstract concept music generation

## Features

### 🎭 Advanced Character Analysis
- **Three-Layer Character Bible Methodology**:
  - **Skin Layer**: Physical descriptions, mannerisms, speech patterns, behavioral traits
  - **Flesh Layer**: Relationships, backstory, formative experiences, social connections
  - **Core Layer**: Motivations, fears, desires, conflicts, personality drivers
- **Unlimited text length processing** with efficient streaming capabilities
- **Character identity consistency tracking** across long narratives with aliases and references
- **Confidence scoring** and importance ranking for character prioritization
- **Multi-character analysis** with relationship mapping and social dynamics

### 🎵 Musical Persona Generation
- **Psychological-to-musical mapping** using comprehensive trait analysis
- **Genre selection** based on character psychology and narrative themes
- **Vocal style determination** from speech patterns and emotional range
- **Artist identity creation** with authentic names and artistic influences
- **Thematic content generation** from character motivations and conflicts
- **Collaboration style analysis** based on character relationships

### 🎼 Suno AI Integration
- **Multiple command formats**: Simple prompts, custom mode, bracket notation
- **Optimized meta tag combinations** for Structure, Style/Genre, Sound Effects, and Vocals
- **Command variation generation** for creative exploration and refinement
- **Effectiveness scoring** and rationale documentation for quality assurance
- **Character-authentic music translation** maintaining narrative integrity

### 🔧 MCP Architecture
- **Comprehensive Tools**: Character analysis, persona generation, command creation, creative mode
- **Rich Resources**: Character methodology guides, genre mappings, command formats, workflow integration
- **Guided Prompts**: Optimized templates for effective character extraction and music generation
- **Batch operations** for complex projects with multiple characters
- **Error handling** and validation systems throughout the pipeline

## Installation

### Prerequisites
- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) (recommended for dependency management)

### Setup
1. Clone or download the MCP server files
2. Navigate to the project directory
3. The server will automatically set up dependencies on first run

```bash
cd character-music-mcp
chmod +x run.sh
./run.sh
```

## Usage

### Tools

#### `analyze_character_text(text: str)`
Performs comprehensive character analysis on narrative text using three-layer methodology.

**Input**: Narrative text content (unlimited length)
**Output**: Detailed character profiles with psychological analysis

```python
# Example usage
result = await analyze_character_text("""
Emma stood at the window, her fingers tracing the glass as memories flooded back. 
She had always been the brave one, the sister who faced dangers head-on, but now 
she felt lost. The weight of her family's expectations pressed down on her shoulders...
""")
```

#### `generate_artist_personas(characters_json: str)`
Transforms character profiles into musical artist personas with genre mappings and creative characteristics.

**Input**: JSON output from `analyze_character_text`
**Output**: Musical artist personas with detailed artistic identities

#### `create_suno_commands(personas_json: str, characters_json: str)`
Generates optimized Suno AI commands from artist personas and character profiles.

**Input**: JSON outputs from previous tools
**Output**: Multiple Suno AI command variations with effectiveness ratings

#### `complete_workflow(text: str)`
Executes the entire pipeline in one operation for rapid prototyping.

**Input**: Raw narrative text
**Output**: Complete analysis from characters to final Suno commands

#### `creative_music_generation(concept: str, style_preference: str)`
Generates creative music commands from abstract concepts without character analysis.

**Input**: Abstract concept or theme, optional style preference
**Output**: Creative musical interpretations and commands

### Resources

- **`character://profiles`**: Character analysis framework documentation
- **`music://genre-mappings`**: Psychological trait to musical genre mapping system
- **`suno://command-formats`**: Suno AI command optimization guide
- **`workflow://integration-guide`**: Complete workflow and integration instructions

### Prompts

- **`character_analysis_prompt(text_sample)`**: Optimized character analysis guidance
- **`music_persona_prompt(character_name, traits)`**: Artist persona generation guidance
- **`suno_optimization_prompt(artist_persona, background)`**: Suno command optimization guidance

## Workflow Examples

### Complete Character-to-Music Pipeline

```python
# 1. Analyze a novel chapter for characters
character_analysis = await analyze_character_text(novel_chapter)

# 2. Generate musical personas from characters  
artist_personas = await generate_artist_personas(character_analysis)

# 3. Create Suno AI commands
suno_commands = await create_suno_commands(artist_personas, character_analysis)

# Or execute all at once:
complete_result = await complete_workflow(novel_chapter)
```

### Creative Abstract Music Generation

```python
# Generate music from abstract concepts
creative_commands = await creative_music_generation(
    concept="The feeling of standing at the edge of forever",
    style_preference="ambient"
)
```

## Character Analysis Methodology

### Three-Layer Analysis Framework

#### Skin Layer - Observable Characteristics
The surface-level traits that can be directly observed:
- Physical appearance and distinctive features
- Mannerisms, gestures, and behavioral tics
- Speech patterns, vocabulary, and communication style
- Observable actions and reactions to situations

#### Flesh Layer - Background and Relationships  
The contextual information that shapes the character:
- Personal backstory and historical events
- Family relationships and social connections
- Formative experiences and life-changing moments
- Professional and romantic relationships

#### Core Layer - Deep Psychology
The fundamental psychological drivers:
- Primary motivations and life goals
- Deepest fears and insecurities
- Core desires and aspirations
- Internal and external conflicts
- Personality drivers and decision-making patterns

## Musical Mapping System

### Personality Trait to Genre Mapping

| Character Trait | Primary Genres | Vocal Style | Thematic Focus |
|----------------|----------------|-------------|----------------|
| **Brave** | Rock, Metal, Epic Orchestral | Powerful, commanding | Heroism, overcoming challenges |
| **Cunning** | Jazz, Classical, Experimental | Smooth, controlled | Complexity, intellectual depth |
| **Compassionate** | Folk, Soul, Gospel | Warm, emotional | Love, relationships, healing |
| **Ambitious** | Electronic, Hip-Hop, Pop | Confident, assertive | Success, power, achievement |
| **Mysterious** | Darkwave, Ambient, Gothic | Ethereal, haunting | Secrets, intrigue, atmosphere |
| **Melancholic** | Indie, Blues, Lo-fi | Soft, introspective | Loss, reflection, nostalgia |
| **Rebellious** | Punk, Grunge, Alternative | Raw, passionate | Independence, defiance, change |

## Suno AI Command Generation

### Command Types

#### Simple Prompts
Natural language descriptions that capture the essence of the character's musical identity:
```
"A rock song about overcoming challenges with powerful vocals, inspired by Emma's journey through adversity and her determination to protect her family."
```

#### Custom Mode Commands
Detailed parameter specifications for precise control:
```json
{
  "prompt": "Create a folk composition exploring love and loss...",
  "style_tags": ["folk", "acoustic", "storytelling", "emotional"],
  "structure_tags": ["verse-chorus-verse", "bridge", "outro"],
  "vocal_tags": ["warm vocals", "expressive delivery"]
}
```

#### Bracket Notation Commands
Precise element control using Suno's bracket syntax:
```
"[folk] [emotional] [warm vocals] [acoustic guitar] [storytelling energy] Song inspired by Emma's journey through love and loss"
```

## Integration Examples

### Claude Desktop Integration
Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "character-music": {
      "command": "sh",
      "args": ["/path/to/character-music-mcp/run.sh"]
    }
  }
}
```

### API Integration
Use programmatically in your applications:

```python
import asyncio
from fastmcp import Client

async def generate_character_music(narrative_text):
    async with Client("/path/to/character-music-mcp/run.sh") as client:
        # Analyze characters
        analysis = await client.call_tool("analyze_character_text", {
            "text": narrative_text
        })
        
        # Generate personas
        personas = await client.call_tool("generate_artist_personas", {
            "characters_json": analysis.text
        })
        
        # Create Suno commands
        commands = await client.call_tool("create_suno_commands", {
            "personas_json": personas.text,
            "characters_json": analysis.text
        })
        
        return commands.text
```

## Quality Assurance

### Character Analysis Quality Indicators
- **Confidence Score > 0.5**: Strong character analysis with sufficient narrative evidence
- **Multiple Personality Drivers**: Complex characters with rich psychological profiles
- **Detailed Relationships**: Characters with significant social connections and backstory

### Artist Persona Quality Indicators
- **High Mapping Confidence (>0.7)**: Strong character-to-music connection
- **Multiple Lyrical Themes**: Rich thematic content from character analysis
- **Clear Genre Justification**: Well-reasoned musical style selection

### Command Effectiveness Indicators
- **Effectiveness Score > 0.8**: High-quality, well-structured commands
- **Multiple Variations**: Creative options for different musical approaches
- **Clear Rationales**: Documented reasoning for command construction choices

## Optional Suno AI Integration

### Environment Variables (Optional)
- `SUNO_COOKIE`: Suno AI session cookie for direct API integration
- `TWOCAPTCHA_KEY`: 2Captcha API key for solving CAPTCHAs

**Note**: The server operates fully in standalone mode without these credentials, generating optimized commands that can be manually executed in Suno AI.

## Technical Architecture

### FastMCP Framework
Built on the industry-standard FastMCP framework for robust MCP server implementation with:
- High-performance async/await architecture
- Comprehensive error handling and validation
- Modular design with clear separation of concerns
- Production-ready deployment capabilities

### NLP and Analysis Engine
- Advanced pattern recognition for character extraction
- Psychological trait mapping using established frameworks
- Confidence scoring algorithms for quality assurance
- Relationship analysis and social network mapping

### Musical Intelligence System
- Genre classification based on psychological profiles
- Vocal style determination from character speech patterns
- Thematic content generation from narrative analysis
- Command optimization for Suno AI compatibility

## Contributing

This project welcomes contributions in several areas:

### Character Analysis Enhancement
- Additional personality trait recognition patterns
- Improved confidence scoring algorithms
- Enhanced relationship mapping capabilities
- Multi-language narrative support

### Musical Mapping Expansion
- Additional genre mappings and style classifications
- Enhanced vocal style determination algorithms
- Expanded instrumental preference systems
- Cultural and regional music style integration

### Suno AI Optimization
- Command effectiveness improvement
- New command format support
- Enhanced meta tag optimization
- Quality assessment algorithms

## License

MIT License - See LICENSE file for details.

## Support

For issues, questions, or contributions:
1. Check the comprehensive documentation in Resources
2. Review the example workflows and integration guides
3. Examine the quality assurance indicators for optimal results

## Roadmap

### Planned Enhancements
- **Multi-language support** for international narrative content
- **Advanced relationship mapping** with social network analysis
- **Genre fusion detection** for complex character personalities
- **Real-time collaboration features** for multi-user workflows
- **Integration with additional music generation platforms**
- **Character evolution tracking** across narrative progression

---

*This MCP server represents a breakthrough in automated music creation by systematically bridging narrative content and musical expression through rigorous character psychology analysis.*
# character-music-mcp
