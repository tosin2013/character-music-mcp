# MCP Tools Troubleshooting Guide

## Overview

This guide provides comprehensive troubleshooting information for the MCP (Model Context Protocol) tools after the diagnostic fixes. It covers common issues, error messages, and step-by-step solutions.

## Common Issues and Solutions

### 1. Character Profile Format Errors

#### Issue: `format_mismatch` Error
**Error Message:** `Expected format: StandardCharacterProfile, got: <other_format>`

**Symptoms:**
- Tools reject character profile input
- "Parameter not found" errors for character fields
- Initialization failures

**Root Cause:**
Tools now use the standardized `StandardCharacterProfile` format, but input data uses old or incompatible formats.

**Solution:**
```python
# ❌ Old format (will cause errors)
old_format = {
    "name": "John",
    "age": 30,  # Not in StandardCharacterProfile
    "skin": "detailed description"  # Old field name
}

# ✅ Correct format
correct_format = {
    "name": "John",
    "physical_description": "Tall with brown hair",  # Correct field name
    "backstory": "Former musician turned teacher",
    "motivations": ["inspire students", "create music"],
    "fears": ["failure", "being forgotten"],
    "desires": ["recognition", "artistic fulfillment"]
}

# Use from_dict for safe conversion
profile = StandardCharacterProfile.from_dict(correct_format)
```

**Prevention:**
- Always use `StandardCharacterProfile.from_dict()` for data conversion
- Validate input data structure before tool calls
- Use the provided data validation utilities

### 2. Character Detection Failures

#### Issue: "No characters found" Error
**Error Message:** `character_detection_failed: No characters found in provided text`

**Symptoms:**
- Empty character arrays returned
- Tools fail to extract character information from clear descriptions
- Workflow stops at character analysis step

**Root Cause:**
Text doesn't contain explicit character information or uses ambiguous references.

**Solution:**
```python
# ❌ Poor text for character detection
poor_text = """
The music was beautiful and moving. It made everyone feel emotional.
Someone played the piano very well.
"""

# ✅ Good text for character detection
good_text = """
Elena Rodriguez, a classically trained pianist from Barcelona, sat at her 
grandmother's old upright piano. As a former jazz musician turned music teacher, 
she brought decades of experience to every performance. Her students admired 
her dedication to preserving musical heritage while embracing modern techniques.
"""

result = await analyze_character_text(good_text, ctx)
```

**Best Practices for Character Text:**
- Include full character names
- Provide background information
- Describe character motivations and traits
- Use specific details rather than generic descriptions
- Include character relationships and context

### 3. Hardcoded Content Issues

#### Issue: Bristol/Marcus References Appearing
**Error Message:** Content contains hardcoded references despite providing different character descriptions

**Symptoms:**
- Output mentions "Bristol warehouse studio" regardless of input
- Character named "Marcus Thompson" appears in results
- Location and backstory don't match provided descriptions

**Root Cause:**
Using old version of tools or cached results from before the fixes.

**Solution:**
```python
# ✅ Verify dynamic content processing
character_description = """
Sarah Chen is a classically trained violinist who moved to Nashville 
to explore country music. She struggles with blending her formal training 
with the raw emotion of country storytelling.
"""

result = await process_universal_content(
    character_description=character_description,
    genre="country",
    location="Nashville",  # Explicitly specify location
    ctx=ctx
)

# Verify no hardcoded content
assert "Bristol" not in str(result)
assert "Marcus" not in str(result)
assert "Nashville" in result["location"]
```

**Prevention:**
- Always provide explicit character descriptions
- Specify genre and location parameters
- Verify output matches input parameters
- Clear any cached results

### 4. Generic Output Problems

#### Issue: Tools Return Input Repetition
**Error Message:** Output is identical or very similar to input text

**Symptoms:**
- Creative tools just repeat the input concept
- No meaningful analysis or variation
- Generic responses like "contemplative" for all emotional analysis

**Root Cause:**
Tools not properly processing input or using fallback generic responses.

**Solution:**
```python
# ✅ Verify meaningful processing
concept = "A melancholic journey through memories of a lost love"
result = await creative_music_generation(concept, "indie folk", ctx)

# Check for meaningful processing
analysis = result["concept_analysis"]
assert len(analysis["key_elements"]) > 0
assert analysis["emotional_content"] != "contemplative"  # Should be specific
assert len(result["creative_variations"]) > 1  # Should have multiple variations

# Verify Suno commands are practical
commands = result["production_commands"]
for cmd in commands:
    assert "[" in cmd and "]" in cmd  # Should contain meta tags
    assert len(cmd) > 20  # Should be substantial commands
```

**Prevention:**
- Provide detailed, specific input
- Check output for meaningful content
- Verify tools are generating variations, not repetitions

### 5. Function Callable Errors

#### Issue: `FunctionTool object not callable` Error
**Error Message:** `function_not_callable: Tool function is not properly callable`

**Symptoms:**
- Complete workflow fails to execute
- Individual tools work but workflow integration fails
- TypeError when calling tool functions

**Root Cause:**
Tool registration or function definition issues in workflow management.

**Solution:**
```python
# ✅ Proper tool usage
try:
    # Use tools individually first to verify they work
    character_result = await analyze_character_text(text, ctx)
    persona_result = await generate_artist_personas(character_result, ctx)
    
    # Then use complete workflow
    workflow_result = await complete_workflow(text, ctx)
    
except Exception as e:
    print(f"Tool error: {e}")
    # Check tool registration and function definitions
```

**Debugging Steps:**
1. Test individual tools first
2. Verify tool registration
3. Check function signatures
4. Ensure proper async/await usage
5. Review error logs for specific issues

### 6. Empty Wiki Data Results

#### Issue: Empty Best Practices Data
**Error Message:** Wiki crawling returns empty fields or no data

**Symptoms:**
- `crawl_suno_wiki_best_practices` returns empty results
- No meta tags or techniques found
- Wiki integration appears non-functional

**Root Cause:**
Wiki data system not properly initialized or configured.

**Solution:**
```python
# ✅ Verify wiki integration
result = await crawl_suno_wiki_best_practices("all", ctx)

# Check for actual data
practices = result["best_practices"]
assert len(practices["prompting_guidelines"]) > 0
assert len(practices["meta_tag_usage"]) > 0

# Check data sources
wiki_data = result["wiki_data"]
assert len(wiki_data["source_urls"]) > 0
assert wiki_data["wiki_integration_status"] == "active"
```

**Troubleshooting Steps:**
1. Check wiki configuration file
2. Verify network connectivity to wiki sources
3. Check cache directory permissions
4. Review wiki data manager initialization
5. Test with fallback data if available

## Error Message Reference

### Format Errors

| Error Code | Message | Solution |
|------------|---------|----------|
| `format_mismatch` | Expected format: StandardCharacterProfile | Use `StandardCharacterProfile.from_dict()` |
| `invalid_persona_format` | Persona data structure invalid | Check ArtistPersona format requirements |
| `missing_required_field` | Required field missing: {field_name} | Add missing field to input data |

### Processing Errors

| Error Code | Message | Solution |
|------------|---------|----------|
| `character_detection_failed` | No characters found in text | Provide text with explicit character descriptions |
| `genre_mapping_failed` | Unable to map traits to genres | Check trait descriptions and genre database |
| `emotional_analysis_failed` | Emotional analysis could not be completed | Verify input text has emotional content |

### System Errors

| Error Code | Message | Solution |
|------------|---------|----------|
| `function_not_callable` | Tool function is not properly callable | Check tool registration and function definitions |
| `workflow_execution_failed` | Workflow step failed | Review individual tool functionality |
| `wiki_integration_error` | Wiki data system unavailable | Check wiki configuration and connectivity |

## Diagnostic Procedures

### 1. Basic Tool Functionality Test

```python
async def test_basic_functionality():
    """Test basic tool functionality"""
    
    # Test character analysis
    test_text = """
    John Smith is a 35-year-old jazz musician from New Orleans. 
    He plays saxophone and has been performing for 15 years.
    """
    
    try:
        result = await analyze_character_text(test_text, ctx)
        assert len(result["characters"]) > 0
        print("✅ Character analysis working")
    except Exception as e:
        print(f"❌ Character analysis failed: {e}")
    
    # Test persona generation
    try:
        persona_result = await generate_artist_personas(result, ctx)
        assert len(persona_result["personas"]) > 0
        print("✅ Persona generation working")
    except Exception as e:
        print(f"❌ Persona generation failed: {e}")
```

### 2. Data Format Validation

```python
def validate_character_profile(data):
    """Validate character profile format"""
    
    required_fields = ["name"]
    optional_fields = [
        "physical_description", "backstory", "motivations", 
        "fears", "desires", "conflicts"
    ]
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate field types
    if not isinstance(data.get("motivations", []), list):
        return False, "motivations must be a list"
    
    return True, "Valid format"

# Usage
is_valid, message = validate_character_profile(character_data)
if not is_valid:
    print(f"Format error: {message}")
```

### 3. Workflow Integration Test

```python
async def test_workflow_integration():
    """Test complete workflow integration"""
    
    test_text = """
    Maria Gonzalez is a flamenco guitarist from Seville, Spain. 
    She combines traditional flamenco techniques with modern jazz influences.
    Her music tells stories of her grandmother's life in rural Andalusia.
    """
    
    try:
        # Test complete workflow
        result = await complete_workflow(test_text, ctx)
        
        # Verify all steps completed
        assert "analysis" in result
        assert "personas" in result
        assert "commands" in result
        assert result["workflow_status"] == "completed"
        
        print("✅ Complete workflow working")
        return True
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        
        # Test individual components
        try:
            char_result = await analyze_character_text(test_text, ctx)
            print("✅ Character analysis component working")
        except Exception as ce:
            print(f"❌ Character analysis component failed: {ce}")
        
        return False
```

## Performance Troubleshooting

### 1. Slow Response Times

**Symptoms:**
- Tools take longer than 30 seconds to respond
- Timeouts in workflow execution
- High memory usage

**Solutions:**
- Check input text length (limit to reasonable sizes)
- Verify wiki data cache is functioning
- Monitor system resources
- Use parallel processing where appropriate

### 2. Memory Issues

**Symptoms:**
- Out of memory errors
- System slowdown during tool execution
- Process crashes

**Solutions:**
- Limit concurrent tool executions
- Clear cached data periodically
- Process large texts in chunks
- Monitor memory usage patterns

## Configuration Issues

### 1. Wiki Integration Problems

**Check Configuration:**
```python
# Verify wiki configuration
from wiki_data_system import ConfigurationManager

config = await ConfigurationManager.load_config()
print(f"Wiki enabled: {config.enabled}")
print(f"Storage path: {config.local_storage_path}")
print(f"Refresh interval: {config.refresh_interval_hours}")
```

**Common Configuration Issues:**
- Wiki integration disabled
- Invalid storage paths
- Network connectivity problems
- Outdated cached data

### 2. Tool Registration Issues

**Verify Tool Registration:**
```python
# Check if tools are properly registered
available_tools = [
    "analyze_character_text",
    "generate_artist_personas", 
    "creative_music_generation",
    "complete_workflow",
    "process_universal_content",
    "create_character_album",
    "create_story_integrated_album",
    "analyze_artist_psychology",
    "crawl_suno_wiki_best_practices",
    "create_suno_commands",
    "understand_topic_with_emotions"
]

for tool_name in available_tools:
    try:
        # Test tool availability
        tool_func = globals().get(tool_name)
        if tool_func and callable(tool_func):
            print(f"✅ {tool_name} available")
        else:
            print(f"❌ {tool_name} not available or not callable")
    except Exception as e:
        print(f"❌ {tool_name} error: {e}")
```

## Getting Help

### 1. Enable Debug Logging

```python
import logging

# Enable comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Tools will now provide detailed debug information
```

### 2. Collect Diagnostic Information

When reporting issues, include:
- Error messages and stack traces
- Input data samples (anonymized)
- Tool versions and configuration
- System environment details
- Steps to reproduce the issue

### 3. Test with Minimal Examples

Start with simple, known-good examples:
- Single character descriptions
- Basic genre specifications
- Short text inputs
- Standard workflow patterns

### 4. Check Recent Changes

If tools were working previously:
- Review recent configuration changes
- Check for updated dependencies
- Verify data file integrity
- Test with previous working examples

This troubleshooting guide should help resolve most common issues with the MCP tools. For persistent problems, enable debug logging and collect detailed diagnostic information for further analysis.