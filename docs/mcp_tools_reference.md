# MCP Tools API Reference

## Overview

This document provides comprehensive API documentation for all MCP (Model Context Protocol) tools after the diagnostic fixes. All tools now use standardized data models, proper error handling, and meaningful content processing.

## Standardized Data Models

### StandardCharacterProfile

The unified character profile format used across all MCP tools.

```python
@dataclass
class StandardCharacterProfile:
    """Standardized character profile for all MCP tools"""
    name: str
    aliases: List[str] = field(default_factory=list)
    
    # Physical characteristics (skin layer)
    physical_description: str = ""
    mannerisms: List[str] = field(default_factory=list)
    speech_patterns: List[str] = field(default_factory=list)
    behavioral_traits: List[str] = field(default_factory=list)
    
    # Background (flesh layer)
    backstory: str = ""
    relationships: List[str] = field(default_factory=list)
    formative_experiences: List[str] = field(default_factory=list)
    social_connections: List[str] = field(default_factory=list)
    
    # Psychology (core layer)
    motivations: List[str] = field(default_factory=list)
    fears: List[str] = field(default_factory=list)
    desires: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    personality_drivers: List[str] = field(default_factory=list)
    
    # Metadata
    confidence_score: float = 1.0
    text_references: List[str] = field(default_factory=list)
    first_appearance: str = ""
    importance_score: float = 1.0
```

#### Methods

##### `from_dict(data: Dict[str, Any]) -> StandardCharacterProfile`

Create character profile from dictionary, handling missing fields gracefully.

**Parameters:**
- `data` (Dict[str, Any]): Dictionary containing character data

**Returns:**
- `StandardCharacterProfile`: Character profile instance

**Example:**
```python
data = {
    "name": "Elena Rodriguez",
    "physical_description": "Tall, dark hair, expressive eyes",
    "backstory": "Former jazz musician turned music teacher",
    "motivations": ["inspire students", "preserve musical heritage"]
}
profile = StandardCharacterProfile.from_dict(data)
```

##### `to_dict() -> Dict[str, Any]`

Convert character profile to dictionary for JSON serialization.

**Returns:**
- `Dict[str, Any]`: Dictionary representation

**Example:**
```python
profile_dict = profile.to_dict()
json_data = json.dumps(profile_dict, indent=2)
```

### ArtistPersona

Artist persona data model for music generation.

```python
@dataclass
class ArtistPersona:
    """Artist persona for music generation"""
    name: str
    genre: str
    style_description: str
    vocal_characteristics: List[str]
    lyrical_themes: List[str]
    production_preferences: List[str]
    character_inspiration: str = ""
    confidence_score: float = 1.0
```

### EmotionalAnalysis

Emotional analysis result structure.

```python
@dataclass
class EmotionalAnalysis:
    """Emotional analysis result"""
    primary_emotion: str
    emotional_arc: Dict[str, str]  # beginning, middle, end
    intensity_score: float
    emotional_themes: List[str]
    contextual_factors: List[str]
```

## Core MCP Tools

### analyze_character_text

Analyzes text to extract character information with three-layer analysis.

#### Function Signature

```python
async def analyze_character_text(text: str, ctx: Context) -> Dict[str, Any]
```

#### Parameters

- `text` (str): Text content to analyze for characters
- `ctx` (Context): MCP context object

#### Returns

```python
{
    "characters": List[Dict[str, Any]],  # StandardCharacterProfile dictionaries
    "narrative_themes": List[str],
    "emotional_arc": Dict[str, str],
    "analysis_metadata": {
        "text_length": int,
        "character_count": int,
        "confidence": float
    }
}
```

#### Error Handling

**Common Errors:**
- `ValueError`: Invalid text input
- `ProcessingError`: Character detection failure

**Error Response Format:**
```python
{
    "error": "character_detection_failed",
    "message": "No characters found in provided text",
    "text_sample": str,
    "suggestion": str
}
```

#### Usage Example

```python
text = """
Elena Rodriguez stood at the piano, her fingers dancing across the keys. 
As a former jazz musician turned music teacher, she brought passion to every lesson.
Her students admired her dedication to preserving musical heritage.
"""

result = await analyze_character_text(text, ctx)

# Access character data
characters = result["characters"]
elena = StandardCharacterProfile.from_dict(characters[0])
print(f"Character: {elena.name}")
print(f"Backstory: {elena.backstory}")
print(f"Motivations: {elena.motivations}")

# Access narrative analysis
themes = result["narrative_themes"]
emotional_arc = result["emotional_arc"]
```

### generate_artist_personas

Generates artist personas from character profiles for music creation.

#### Function Signature

```python
async def generate_artist_personas(
    character_data: Dict[str, Any], 
    ctx: Context
) -> Dict[str, Any]
```

#### Parameters

- `character_data` (Dict[str, Any]): Result from analyze_character_text
- `ctx` (Context): MCP context object

#### Returns

```python
{
    "personas": List[Dict[str, Any]],  # ArtistPersona dictionaries
    "genre_mappings": Dict[str, List[str]],
    "style_recommendations": List[str],
    "generation_metadata": {
        "source_characters": int,
        "personas_generated": int,
        "confidence": float
    }
}
```

#### Input Format Requirements

The `character_data` parameter should contain:
```python
{
    "characters": [
        {
            "name": str,
            "physical_description": str,
            "backstory": str,
            "motivations": List[str],
            # ... other StandardCharacterProfile fields
        }
    ]
}
```

#### Usage Example

```python
# First analyze character text
character_result = await analyze_character_text(text, ctx)

# Generate personas from character analysis
persona_result = await generate_artist_personas(character_result, ctx)

# Access persona data
personas = persona_result["personas"]
elena_persona = ArtistPersona.from_dict(personas[0])
print(f"Artist: {elena_persona.name}")
print(f"Genre: {elena_persona.genre}")
print(f"Style: {elena_persona.style_description}")
```

### creative_music_generation

Generates creative music concepts and variations with meaningful analysis.

#### Function Signature

```python
async def creative_music_generation(
    concept: str, 
    style_preference: str = "any",
    ctx: Context = None
) -> Dict[str, Any]
```

#### Parameters

- `concept` (str): Musical concept or theme to develop
- `style_preference` (str): Preferred musical style ("jazz", "rock", "electronic", etc.)
- `ctx` (Context): MCP context object

#### Returns

```python
{
    "concept_analysis": {
        "key_elements": List[str],
        "musical_themes": List[str],
        "emotional_content": str,
        "genre_suggestions": List[str]
    },
    "creative_variations": List[Dict[str, Any]],
    "production_commands": List[str],  # Practical Suno AI commands
    "style_adaptations": Dict[str, Any]
}
```

#### Usage Example

```python
concept = "A melancholic journey through memories of a lost love"
style = "indie folk"

result = await creative_music_generation(concept, style, ctx)

# Access creative analysis
analysis = result["concept_analysis"]
print(f"Key elements: {analysis['key_elements']}")
print(f"Emotional content: {analysis['emotional_content']}")

# Get practical Suno commands
commands = result["production_commands"]
for cmd in commands:
    print(f"Suno command: {cmd}")
```

### complete_workflow

Executes the complete music generation workflow from text analysis to command generation.

#### Function Signature

```python
async def complete_workflow(text: str, ctx: Context) -> Dict[str, Any]
```

#### Parameters

- `text` (str): Input text for character analysis
- `ctx` (Context): MCP context object

#### Returns

```python
{
    "analysis": Dict[str, Any],      # analyze_character_text result
    "personas": Dict[str, Any],      # generate_artist_personas result
    "commands": Dict[str, Any],      # create_suno_commands result
    "workflow_status": str,          # "completed" or "failed"
    "execution_metadata": {
        "steps_completed": int,
        "total_time": float,
        "errors": List[str]
    }
}
```

#### Error Handling

The workflow includes comprehensive error recovery:
- Individual step failures are logged but don't stop the workflow
- Partial results are returned even if some steps fail
- Detailed error information is provided for debugging

#### Usage Example

```python
text = """
Marcus Thompson worked late nights in his Bristol warehouse studio,
crafting beats that told stories of urban life and personal struggle.
"""

result = await complete_workflow(text, ctx)

if result["workflow_status"] == "completed":
    # Access all workflow results
    characters = result["analysis"]["characters"]
    personas = result["personas"]["personas"]
    commands = result["commands"]["suno_commands"]
    
    print(f"Found {len(characters)} characters")
    print(f"Generated {len(personas)} personas")
    print(f"Created {len(commands)} Suno commands")
else:
    # Handle workflow errors
    errors = result["execution_metadata"]["errors"]
    print(f"Workflow failed with errors: {errors}")
```

### process_universal_content

Processes character descriptions with dynamic content generation (no hardcoded content).

#### Function Signature

```python
async def process_universal_content(
    character_description: str,
    genre: str = None,
    location: str = None,
    ctx: Context = None
) -> Dict[str, Any]
```

#### Parameters

- `character_description` (str): Character description to process
- `genre` (str, optional): Musical genre preference
- `location` (str, optional): Location context
- `ctx` (Context): MCP context object

#### Returns

```python
{
    "character": Dict[str, Any],     # Extracted character details
    "genre": str,                    # Determined or provided genre
    "location": str,                 # Determined or provided location
    "backstory": str,                # Generated backstory
    "context": Dict[str, Any],       # Additional context
    "processing_metadata": {
        "extraction_confidence": float,
        "genre_source": str,         # "provided" or "inferred"
        "location_source": str
    }
}
```

#### Key Features

- **No Hardcoded Content**: All content is generated from provided parameters
- **Dynamic Genre Detection**: Infers genre from character description if not provided
- **Location Extraction**: Extracts location details from description
- **Contextual Backstory**: Generates backstory based on character details

#### Usage Example

```python
description = """
Sarah Chen is a classically trained violinist who moved to Nashville 
to explore country music. She struggles with blending her formal training 
with the raw emotion of country storytelling.
"""

result = await process_universal_content(
    character_description=description,
    genre="country",
    ctx=ctx
)

# Access processed content
character = result["character"]
print(f"Character: {character['name']}")
print(f"Genre: {result['genre']}")
print(f"Location: {result['location']}")
print(f"Backstory: {result['backstory']}")
```

### create_character_album

Creates a complete album with unique tracks based on character and genre specifications.

#### Function Signature

```python
async def create_character_album(
    character_description: str,
    genre: str,
    album_theme: str = None,
    track_count: int = 8,
    ctx: Context = None
) -> Dict[str, Any]
```

#### Parameters

- `character_description` (str): Character description for album creation
- `genre` (str): Musical genre for the album
- `album_theme` (str, optional): Overall album theme
- `track_count` (int): Number of tracks to generate (default: 8)
- `ctx` (Context): MCP context object

#### Returns

```python
{
    "album_info": {
        "title": str,
        "artist": str,
        "genre": str,
        "theme": str,
        "track_count": int
    },
    "tracks": List[Dict[str, Any]],  # Individual track details
    "character_filter": Dict[str, Any],  # Character-based filtering
    "album_metadata": {
        "creation_time": str,
        "character_consistency": float,
        "genre_adherence": float
    }
}
```

#### Track Structure

Each track in the `tracks` list contains:
```python
{
    "track_number": int,
    "title": str,
    "lyrics": str,              # Unique lyrics for each track
    "theme": str,               # Track-specific theme
    "mood": str,
    "suno_command": str,        # Ready-to-use Suno command
    "character_connection": str  # How track relates to character
}
```

#### Key Features

- **Unique Track Content**: Each track has distinct lyrics and themes
- **Character Consistency**: All tracks reflect the provided character
- **Genre Adherence**: Music matches specified genre throughout
- **Thematic Coherence**: Album maintains overall narrative arc

#### Usage Example

```python
character = """
Jake Morrison is a former truck driver turned country songwriter.
He writes about life on the road, small-town values, and the 
struggles of working-class America.
"""

result = await create_character_album(
    character_description=character,
    genre="country",
    album_theme="Life on the Highway",
    track_count=6,
    ctx=ctx
)

# Access album information
album = result["album_info"]
print(f"Album: {album['title']} by {album['artist']}")

# Access individual tracks
tracks = result["tracks"]
for track in tracks:
    print(f"Track {track['track_number']}: {track['title']}")
    print(f"Theme: {track['theme']}")
    print(f"Suno command: {track['suno_command']}")
```

### create_story_integrated_album

Creates an album integrated with narrative story elements and proper character detection.

#### Function Signature

```python
async def create_story_integrated_album(
    narrative_text: str,
    musical_style: str = None,
    ctx: Context = None
) -> Dict[str, Any]
```

#### Parameters

- `narrative_text` (str): Story or narrative text containing characters
- `musical_style` (str, optional): Preferred musical style
- `ctx` (Context): MCP context object

#### Returns

```python
{
    "story_analysis": {
        "characters": List[Dict[str, Any]],
        "plot_points": List[str],
        "themes": List[str],
        "emotional_arc": Dict[str, str]
    },
    "album_concept": {
        "title": str,
        "narrative_structure": str,
        "character_focus": str,
        "musical_style": str
    },
    "tracks": List[Dict[str, Any]],
    "integration_metadata": {
        "character_detection_success": bool,
        "story_coherence": float,
        "musical_alignment": float
    }
}
```

#### Character Detection Features

- **Robust Character Extraction**: Properly detects characters from narrative text
- **Context Preservation**: Maintains character relationships and story context
- **Multi-Character Support**: Handles stories with multiple characters
- **Validation**: Confirms character detection success

#### Usage Example

```python
narrative = """
The lighthouse keeper's daughter, Emma, had always been drawn to the sea.
Every night, she would climb to the top of the lighthouse and sing to the waves.
Her father, Old Tom, worried about her obsession with the ocean's mysteries.
One stormy night, Emma discovered a message in a bottle that would change everything.
"""

result = await create_story_integrated_album(
    narrative_text=narrative,
    musical_style="folk",
    ctx=ctx
)

# Check character detection
if result["integration_metadata"]["character_detection_success"]:
    characters = result["story_analysis"]["characters"]
    print(f"Detected characters: {[c['name'] for c in characters]}")
    
    # Access album tracks
    tracks = result["tracks"]
    for track in tracks:
        print(f"Track: {track['title']}")
        print(f"Character focus: {track['character_connection']}")
```

### analyze_artist_psychology

Analyzes artist psychology from character profiles with proper format handling.

#### Function Signature

```python
async def analyze_artist_psychology(
    character_profile: Dict[str, Any],
    ctx: Context = None
) -> Dict[str, Any]
```

#### Parameters

- `character_profile` (Dict[str, Any]): StandardCharacterProfile dictionary
- `ctx` (Context): MCP context object

#### Returns

```python
{
    "psychological_profile": {
        "personality_type": str,
        "creative_drivers": List[str],
        "emotional_patterns": List[str],
        "artistic_influences": List[str]
    },
    "musical_implications": {
        "preferred_genres": List[str],
        "lyrical_themes": List[str],
        "performance_style": str,
        "collaboration_tendencies": str
    },
    "creative_recommendations": List[str],
    "analysis_metadata": {
        "confidence_score": float,
        "analysis_depth": str,
        "psychological_complexity": float
    }
}
```

#### Input Format

The character profile should follow StandardCharacterProfile format:
```python
{
    "name": str,
    "motivations": List[str],
    "fears": List[str],
    "desires": List[str],
    "conflicts": List[str],
    "personality_drivers": List[str],
    # ... other StandardCharacterProfile fields
}
```

#### Usage Example

```python
# Create character profile
profile_data = {
    "name": "Alex Rivera",
    "motivations": ["express inner turmoil", "connect with others"],
    "fears": ["being misunderstood", "creative stagnation"],
    "desires": ["artistic recognition", "emotional healing"],
    "conflicts": ["perfectionism vs spontaneity"],
    "personality_drivers": ["empathy", "introspection", "authenticity"]
}

result = await analyze_artist_psychology(profile_data, ctx)

# Access psychological analysis
psychology = result["psychological_profile"]
print(f"Personality type: {psychology['personality_type']}")
print(f"Creative drivers: {psychology['creative_drivers']}")

# Access musical implications
music = result["musical_implications"]
print(f"Preferred genres: {music['preferred_genres']}")
print(f"Lyrical themes: {music['lyrical_themes']}")
```

### crawl_suno_wiki_best_practices

Retrieves actual Suno AI best practices and specifications from wiki data.

#### Function Signature

```python
async def crawl_suno_wiki_best_practices(
    practice_type: str = "all",
    ctx: Context = None
) -> Dict[str, Any]
```

#### Parameters

- `practice_type` (str): Type of practices to retrieve ("all", "prompting", "meta_tags", "techniques")
- `ctx` (Context): MCP context object

#### Returns

```python
{
    "best_practices": {
        "prompting_guidelines": List[str],
        "meta_tag_usage": List[Dict[str, Any]],
        "technique_tips": List[Dict[str, Any]],
        "genre_specifications": List[Dict[str, Any]]
    },
    "wiki_data": {
        "source_urls": List[str],
        "last_updated": str,
        "data_freshness": str
    },
    "practical_examples": List[Dict[str, Any]],
    "retrieval_metadata": {
        "practices_found": int,
        "data_quality": float,
        "wiki_integration_status": str
    }
}
```

#### Features

- **Real Wiki Data**: Returns actual content from Suno AI wiki
- **Categorized Practices**: Organizes practices by type
- **Practical Examples**: Includes working examples
- **Source Attribution**: Provides source URLs for reference

#### Usage Example

```python
# Get all best practices
result = await crawl_suno_wiki_best_practices("all", ctx)

# Access prompting guidelines
guidelines = result["best_practices"]["prompting_guidelines"]
for guideline in guidelines:
    print(f"Guideline: {guideline}")

# Access meta tag usage
meta_tags = result["best_practices"]["meta_tag_usage"]
for tag_info in meta_tags:
    print(f"Tag: {tag_info['tag']} - {tag_info['description']}")

# Get source attribution
sources = result["wiki_data"]["source_urls"]
print(f"Data sources: {sources}")
```

### create_suno_commands

Creates practical Suno AI commands from persona data with proper format handling.

#### Function Signature

```python
async def create_suno_commands(
    persona_data: Dict[str, Any],
    character_data: Dict[str, Any] = None,
    ctx: Context = None
) -> Dict[str, Any]
```

#### Parameters

- `persona_data` (Dict[str, Any]): Artist persona data from generate_artist_personas
- `character_data` (Dict[str, Any], optional): Original character analysis data
- `ctx` (Context): MCP context object

#### Returns

```python
{
    "suno_commands": List[str],      # Ready-to-use Suno commands
    "command_breakdown": List[Dict[str, Any]],  # Detailed command analysis
    "meta_tags_used": List[str],
    "style_parameters": Dict[str, Any],
    "generation_metadata": {
        "commands_generated": int,
        "persona_compatibility": float,
        "suno_format_compliance": bool
    }
}
```

#### Command Breakdown Structure

Each item in `command_breakdown` contains:
```python
{
    "command": str,              # The Suno command
    "purpose": str,              # What this command achieves
    "meta_tags": List[str],      # Meta tags used
    "style_elements": List[str], # Style components
    "persona_connection": str    # How it relates to persona
}
```

#### Usage Example

```python
# First generate personas
persona_result = await generate_artist_personas(character_data, ctx)

# Create Suno commands from personas
command_result = await create_suno_commands(
    persona_data=persona_result,
    character_data=character_data,
    ctx=ctx
)

# Access generated commands
commands = command_result["suno_commands"]
for cmd in commands:
    print(f"Suno command: {cmd}")

# Access detailed breakdown
breakdown = command_result["command_breakdown"]
for item in breakdown:
    print(f"Command: {item['command']}")
    print(f"Purpose: {item['purpose']}")
    print(f"Meta tags: {item['meta_tags']}")
```

### understand_topic_with_emotions

Provides meaningful emotional analysis and contextual musical recommendations.

#### Function Signature

```python
async def understand_topic_with_emotions(
    topic: str,
    context: str = "",
    ctx: Context = None
) -> Dict[str, Any]
```

#### Parameters

- `topic` (str): Topic or theme to analyze emotionally
- `context` (str, optional): Additional context for analysis
- `ctx` (Context): MCP context object

#### Returns

```python
{
    "emotional_analysis": {
        "primary_emotions": List[str],
        "emotional_intensity": float,
        "emotional_progression": Dict[str, str],
        "contextual_factors": List[str]
    },
    "musical_recommendations": {
        "genre_suggestions": List[str],
        "tempo_recommendations": List[str],
        "key_suggestions": List[str],
        "instrumentation": List[str]
    },
    "beat_patterns": List[Dict[str, Any]],
    "lyrical_themes": List[str],
    "analysis_metadata": {
        "topic_complexity": float,
        "emotional_depth": float,
        "musical_alignment": float
    }
}
```

#### Beat Pattern Structure

Each beat pattern contains:
```python
{
    "pattern_name": str,
    "bpm_range": str,
    "time_signature": str,
    "description": str,
    "emotional_fit": str,
    "genre_compatibility": List[str]
}
```

#### Features

- **Varied Emotional Analysis**: Provides diverse emotional insights beyond "contemplative"
- **Genre-Appropriate Recommendations**: Musical suggestions match emotional content
- **Practical Beat Patterns**: Usable rhythm patterns for production
- **Contextual Understanding**: Considers topic context for deeper analysis

#### Usage Example

```python
topic = "The bittersweet feeling of leaving home for the first time"
context = "Young adult moving to college, mix of excitement and nostalgia"

result = await understand_topic_with_emotions(topic, context, ctx)

# Access emotional analysis
emotions = result["emotional_analysis"]
print(f"Primary emotions: {emotions['primary_emotions']}")
print(f"Intensity: {emotions['emotional_intensity']}")

# Access musical recommendations
music = result["musical_recommendations"]
print(f"Genre suggestions: {music['genre_suggestions']}")
print(f"Tempo: {music['tempo_recommendations']}")

# Access beat patterns
patterns = result["beat_patterns"]
for pattern in patterns:
    print(f"Pattern: {pattern['pattern_name']} ({pattern['bpm_range']} BPM)")
    print(f"Description: {pattern['description']}")
```

## Error Handling and Troubleshooting

### Common Error Types

#### Format Mismatch Errors

**Error:** `format_mismatch`
**Cause:** Input data doesn't match expected StandardCharacterProfile format
**Solution:** Use `StandardCharacterProfile.from_dict()` to convert data

```python
# Incorrect format
character_data = {"name": "John", "age": 30}  # 'age' not in StandardCharacterProfile

# Correct format
character_data = {
    "name": "John",
    "physical_description": "Tall with brown hair",
    "backstory": "Former musician",
    "motivations": ["create music", "inspire others"]
}
profile = StandardCharacterProfile.from_dict(character_data)
```

#### Character Detection Failures

**Error:** `character_detection_failed`
**Cause:** Text doesn't contain clear character descriptions
**Solution:** Provide text with explicit character information

```python
# Poor text for character detection
text = "The music was beautiful."

# Good text for character detection
text = """
Sarah Martinez, a classically trained pianist, sat at her grandmother's 
old upright piano. Her fingers moved gracefully across the keys as she 
played the melody that had been haunting her dreams.
"""
```

#### Function Callable Errors

**Error:** `function_not_callable`
**Cause:** Tool registration or function definition issues
**Solution:** Ensure proper tool initialization and registration

### Error Response Format

All tools return errors in a consistent format:

```python
{
    "error": str,           # Error type identifier
    "message": str,         # Human-readable error message
    "details": str,         # Technical details
    "suggestion": str,      # Recommended solution
    "tool_name": str,       # Name of the tool that failed
    "timestamp": str        # Error timestamp
}
```

### Debugging Tips

1. **Check Input Formats**: Ensure all input data matches expected formats
2. **Validate Character Profiles**: Use `StandardCharacterProfile.from_dict()` for validation
3. **Review Error Messages**: Error messages include specific suggestions for fixes
4. **Test with Simple Data**: Start with basic examples before complex scenarios
5. **Check Tool Registration**: Ensure all tools are properly registered and callable

### Logging and Monitoring

All tools include comprehensive logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Tools will log:
# - Input validation results
# - Processing steps
# - Error details
# - Performance metrics
```

## Integration Patterns

### Sequential Tool Usage

```python
async def complete_music_generation_workflow(text: str, ctx: Context):
    """Example of sequential tool usage"""
    
    # Step 1: Analyze characters
    character_result = await analyze_character_text(text, ctx)
    
    # Step 2: Generate personas
    persona_result = await generate_artist_personas(character_result, ctx)
    
    # Step 3: Create Suno commands
    command_result = await create_suno_commands(persona_result, character_result, ctx)
    
    # Step 4: Get best practices
    practices = await crawl_suno_wiki_best_practices("all", ctx)
    
    return {
        "characters": character_result,
        "personas": persona_result,
        "commands": command_result,
        "best_practices": practices
    }
```

### Parallel Tool Usage

```python
import asyncio

async def parallel_analysis(text: str, ctx: Context):
    """Example of parallel tool usage"""
    
    # Run character analysis and emotional analysis in parallel
    character_task = analyze_character_text(text, ctx)
    emotion_task = understand_topic_with_emotions(text, "", ctx)
    
    character_result, emotion_result = await asyncio.gather(
        character_task, 
        emotion_task
    )
    
    return {
        "character_analysis": character_result,
        "emotional_analysis": emotion_result
    }
```

### Error Recovery Patterns

```python
async def robust_workflow(text: str, ctx: Context):
    """Example of workflow with error recovery"""
    
    results = {}
    errors = []
    
    try:
        results["characters"] = await analyze_character_text(text, ctx)
    except Exception as e:
        errors.append(f"Character analysis failed: {e}")
        # Use fallback or continue with partial data
    
    try:
        if "characters" in results:
            results["personas"] = await generate_artist_personas(results["characters"], ctx)
    except Exception as e:
        errors.append(f"Persona generation failed: {e}")
    
    return {
        "results": results,
        "errors": errors,
        "success": len(errors) == 0
    }
```

This comprehensive API reference provides all the information needed to use the corrected MCP tools effectively. Each tool now has standardized interfaces, proper error handling, and meaningful content processing capabilities.