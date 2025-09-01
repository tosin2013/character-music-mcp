# MCP Tools Quick Reference

## Overview

Quick reference guide for MCP tools after diagnostic fixes. Use this for rapid lookup of tool signatures, formats, and common usage patterns.

## Tool Signatures

### Character Analysis
```python
# Analyze text for characters
await analyze_character_text(text: str, ctx: Context) -> Dict[str, Any]

# Returns: {"characters": [...], "narrative_themes": [...], "emotional_arc": {...}}
```

### Persona Generation
```python
# Generate artist personas from character data
await generate_artist_personas(character_data: Dict, ctx: Context) -> Dict[str, Any]

# Returns: {"personas": [...], "genre_mappings": {...}, "style_recommendations": [...]}
```

### Creative Generation
```python
# Generate creative music concepts
await creative_music_generation(concept: str, style: str = "any", ctx: Context = None) -> Dict[str, Any]

# Returns: {"concept_analysis": {...}, "creative_variations": [...], "production_commands": [...]}
```

### Complete Workflow
```python
# Execute complete workflow
await complete_workflow(text: str, ctx: Context) -> Dict[str, Any]

# Returns: {"analysis": {...}, "personas": {...}, "commands": {...}, "workflow_status": str}
```

### Content Processing
```python
# Process character content dynamically
await process_universal_content(character_description: str, genre: str = None, location: str = None, ctx: Context = None) -> Dict[str, Any]

# Returns: {"character": {...}, "genre": str, "location": str, "backstory": str}
```

### Album Creation
```python
# Create character-based album
await create_character_album(character_description: str, genre: str, album_theme: str = None, track_count: int = 8, ctx: Context = None) -> Dict[str, Any]

# Returns: {"album_info": {...}, "tracks": [...], "character_filter": {...}}
```

### Story Integration
```python
# Create story-integrated album
await create_story_integrated_album(narrative_text: str, musical_style: str = None, ctx: Context = None) -> Dict[str, Any]

# Returns: {"story_analysis": {...}, "album_concept": {...}, "tracks": [...]}
```

### Psychology Analysis
```python
# Analyze artist psychology
await analyze_artist_psychology(character_profile: Dict, ctx: Context = None) -> Dict[str, Any]

# Returns: {"psychological_profile": {...}, "musical_implications": {...}, "creative_recommendations": [...]}
```

### Wiki Best Practices
```python
# Get Suno wiki best practices
await crawl_suno_wiki_best_practices(practice_type: str = "all", ctx: Context = None) -> Dict[str, Any]

# Returns: {"best_practices": {...}, "wiki_data": {...}, "practical_examples": [...]}
```

### Suno Commands
```python
# Create Suno AI commands
await create_suno_commands(persona_data: Dict, character_data: Dict = None, ctx: Context = None) -> Dict[str, Any]

# Returns: {"suno_commands": [...], "command_breakdown": [...], "meta_tags_used": [...]}
```

### Emotional Analysis
```python
# Understand topic with emotions
await understand_topic_with_emotions(topic: str, context: str = "", ctx: Context = None) -> Dict[str, Any]

# Returns: {"emotional_analysis": {...}, "musical_recommendations": {...}, "beat_patterns": [...]}
```

## Data Formats

### StandardCharacterProfile
```python
{
    "name": str,                          # Required
    "aliases": List[str],                 # Optional
    "physical_description": str,          # Physical characteristics
    "mannerisms": List[str],
    "speech_patterns": List[str],
    "behavioral_traits": List[str],
    "backstory": str,                     # Background
    "relationships": List[str],
    "formative_experiences": List[str],
    "social_connections": List[str],
    "motivations": List[str],             # Psychology
    "fears": List[str],
    "desires": List[str],
    "conflicts": List[str],
    "personality_drivers": List[str],
    "confidence_score": float,            # Metadata
    "text_references": List[str],
    "first_appearance": str,
    "importance_score": float
}
```

### ArtistPersona
```python
{
    "name": str,
    "genre": str,
    "style_description": str,
    "vocal_characteristics": List[str],
    "lyrical_themes": List[str],
    "production_preferences": List[str],
    "character_inspiration": str,
    "confidence_score": float
}
```

### EmotionalAnalysis
```python
{
    "primary_emotion": str,
    "emotional_arc": {
        "beginning": str,
        "middle": str,
        "end": str
    },
    "intensity_score": float,
    "emotional_themes": List[str],
    "contextual_factors": List[str]
}
```

## Common Usage Patterns

### Sequential Workflow
```python
# 1. Analyze character
character_result = await analyze_character_text(text, ctx)

# 2. Generate personas
persona_result = await generate_artist_personas(character_result, ctx)

# 3. Create commands
command_result = await create_suno_commands(persona_result, character_result, ctx)
```

### Parallel Processing
```python
import asyncio

# Run multiple analyses in parallel
character_task = analyze_character_text(text, ctx)
emotion_task = understand_topic_with_emotions(text, "", ctx)

character_result, emotion_result = await asyncio.gather(character_task, emotion_task)
```

### Error Handling
```python
try:
    result = await analyze_character_text(text, ctx)
    if not result.get("characters"):
        print("No characters found")
except Exception as e:
    print(f"Tool error: {e}")
```

## Input Validation

### Character Text Requirements
- Minimum 50 characters
- Contains character names or pronouns
- Includes character descriptions or actions
- Provides context about character background

### Good Character Text Example
```python
text = """
Elena Rodriguez is a classically trained pianist from Barcelona. 
As a former jazz musician turned music teacher, she brings passion 
to every lesson. Her greatest fear is that improvisation will be 
lost to digital perfection.
"""
```

### Poor Character Text Example
```python
text = "The music was beautiful."  # Too vague, no character info
```

## Error Messages

### Common Errors
| Error | Cause | Solution |
|-------|-------|----------|
| `format_mismatch` | Wrong data format | Use StandardCharacterProfile.from_dict() |
| `character_detection_failed` | No characters in text | Provide explicit character descriptions |
| `function_not_callable` | Tool registration issue | Check tool initialization |
| `wiki_integration_error` | Wiki system unavailable | Check configuration |

### Error Response Format
```python
{
    "error": str,           # Error type
    "message": str,         # Human-readable message
    "details": str,         # Technical details
    "suggestion": str,      # Recommended solution
    "tool_name": str,       # Tool that failed
    "timestamp": str        # Error timestamp
}
```

## Performance Tips

### Optimization
- Validate input before tool calls
- Use parallel processing for independent operations
- Cache results when appropriate
- Monitor execution times
- Handle errors gracefully

### Resource Management
```python
# Monitor performance
import time

start_time = time.time()
result = await tool_function(input_data, ctx)
execution_time = time.time() - start_time

if execution_time > 30:  # 30 second threshold
    print(f"Warning: Tool took {execution_time:.2f}s")
```

## Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Validate Results
```python
def validate_character_result(result):
    assert "characters" in result
    assert len(result["characters"]) > 0
    assert result["characters"][0].get("name")
    return True
```

### Test with Minimal Data
```python
# Start with simple test case
simple_text = "John Smith is a jazz musician from New Orleans."
result = await analyze_character_text(simple_text, ctx)
```

## Integration Examples

### Basic Integration
```python
async def basic_music_generation(character_description: str):
    ctx = Context()
    
    # Analyze character
    char_result = await analyze_character_text(character_description, ctx)
    
    # Generate persona
    persona_result = await generate_artist_personas(char_result, ctx)
    
    # Create commands
    cmd_result = await create_suno_commands(persona_result, char_result, ctx)
    
    return cmd_result["suno_commands"]
```

### Advanced Integration
```python
async def advanced_music_production(narrative: str, genre: str):
    ctx = Context()
    
    # Multiple analysis approaches
    story_album = await create_story_integrated_album(narrative, genre, ctx)
    char_analysis = await analyze_character_text(narrative, ctx)
    emotional_analysis = await understand_topic_with_emotions(narrative, "", ctx)
    
    # Combine results
    return {
        "story_album": story_album,
        "character_analysis": char_analysis,
        "emotional_analysis": emotional_analysis
    }
```

## Quick Troubleshooting

### Tool Not Working?
1. Check input format
2. Verify tool registration
3. Enable debug logging
4. Test with simple example
5. Check error messages

### No Characters Found?
1. Add explicit character names
2. Include character descriptions
3. Use pronouns (he, she, they)
4. Provide character background

### Generic Output?
1. Provide specific input
2. Check tool version
3. Verify meaningful processing
4. Test with different examples

### Workflow Failing?
1. Test individual tools first
2. Check tool registration
3. Verify async/await usage
4. Review error logs

This quick reference provides essential information for using MCP tools effectively. For detailed examples and comprehensive documentation, refer to the full API reference and examples documents.