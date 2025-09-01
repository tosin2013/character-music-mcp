# StandardCharacterProfile - Unified Character Data Model

## Overview

The `StandardCharacterProfile` class provides a unified, consistent data model for character profiles across all MCP tools. This addresses the format mismatch issues identified in the diagnostic report where different tools expected different character profile formats, causing initialization errors and tool failures.

## Key Features

- **Consistent Format**: Single data model used by all MCP tools
- **Graceful Error Handling**: Handles missing fields and type mismatches automatically
- **Backward Compatibility**: Works with existing legacy formats
- **Three-Layer Analysis**: Supports skin/flesh/core character analysis approach
- **JSON Serialization**: Full support for JSON serialization/deserialization
- **Validation**: Built-in validation and data cleaning
- **Migration Support**: Tools to migrate existing code

## Installation

```python
from standard_character_profile import StandardCharacterProfile
```

## Basic Usage

### Creating a Character Profile

```python
# Basic creation
profile = StandardCharacterProfile(name="Sarah Chen")

# Full creation with all fields
profile = StandardCharacterProfile(
    name="Sarah Chen",
    aliases=["Sarah", "SC"],
    physical_description="Tall, dark hair, expressive eyes",
    mannerisms=["fidgets with pen", "maintains eye contact"],
    speech_patterns=["speaks softly", "uses precise language"],
    behavioral_traits=["perfectionist", "analytical"],
    backstory="Grew up in urban environment, high achiever",
    relationships=["close to mother", "distant from father"],
    formative_experiences=["moved cities at age 12"],
    social_connections=["college friends", "work colleagues"],
    motivations=["prove herself", "help others"],
    fears=["failure", "disappointing others"],
    desires=["recognition", "meaningful work"],
    conflicts=["perfectionism vs creativity"],
    personality_drivers=["need for control", "desire to belong"],
    confidence_score=0.85,
    text_references=["Chapter 1", "Page 45-67"],
    first_appearance="Opening scene",
    importance_score=0.9
)
```

### Creating from Dictionary (JSON Data)

```python
# From dictionary (handles missing fields gracefully)
data = {
    "name": "John Doe",
    "aliases": ["Johnny", "JD"],
    "backstory": "Interesting background",
    "confidence_score": 0.8
}

profile = StandardCharacterProfile.from_dict(data)
```

### Converting to Dictionary

```python
# Convert to dictionary for JSON serialization
profile_dict = profile.to_dict()

# Convert to legacy format for backward compatibility
legacy_simple = profile.to_legacy_format("simple")
legacy_minimal = profile.to_legacy_format("minimal")
```

## Three-Layer Character Analysis

The `StandardCharacterProfile` supports the three-layer character analysis approach:

### Skin Layer - Observable Characteristics
- `physical_description`: Physical appearance
- `mannerisms`: Observable habits and behaviors
- `speech_patterns`: How the character speaks
- `behavioral_traits`: Personality traits visible to others

### Flesh Layer - Background and Relationships
- `backstory`: Character's history and background
- `relationships`: Key relationships with others
- `formative_experiences`: Important life events
- `social_connections`: Social networks and groups

### Core Layer - Deep Psychology
- `motivations`: What drives the character
- `fears`: What the character is afraid of
- `desires`: What the character wants
- `conflicts`: Internal and external conflicts
- `personality_drivers`: Deep psychological drivers

## Error Handling and Type Conversion

The `StandardCharacterProfile` automatically handles common format issues:

### Missing Fields
```python
# Missing fields get default values
minimal_data = {"name": "Test Character"}
profile = StandardCharacterProfile.from_dict(minimal_data)
# All other fields will have appropriate defaults
```

### Type Mismatches
```python
# Automatic type conversion
mismatched_data = {
    "name": "Test Character",
    "aliases": "single_alias",  # String instead of list
    "mannerisms": "fidgets,taps,looks",  # Comma-separated string
    "confidence_score": "0.75"  # String instead of float
}

profile = StandardCharacterProfile.from_dict(mismatched_data)
# Automatically converts to correct types
```

### Problematic Parameters
```python
# Ignores unknown/problematic parameters
problematic_data = {
    "name": "Test Character",
    "skin": "This parameter causes errors",  # Ignored
    "age": 25,  # Ignored
    "backstory": "Valid field"  # Used
}

profile = StandardCharacterProfile.from_dict(problematic_data)
# Only uses valid fields, ignores problematic ones
```

## Validation

### Data Validation
```python
from standard_character_profile import validate_character_profile_data

data = {"name": "Test", "confidence_score": 1.5}  # Score out of range
issues = validate_character_profile_data(data)
# Returns list of validation issues
```

### Completeness Check
```python
# Check if profile has sufficient information
if profile.is_complete():
    print("Profile has information in all three layers")
else:
    print("Profile needs more information")
```

## Utility Functions

### Create from Text
```python
from standard_character_profile import create_character_profile_from_text

text = "John Smith is a creative and quiet person who loves art."
profile = create_character_profile_from_text(text)
```

### Merge Profiles
```python
# Merge two character profiles
profile1 = StandardCharacterProfile(name="Character A", backstory="Background A")
profile2 = StandardCharacterProfile(name="Character B", motivations=["Goal B"])

merged = profile1.merge_with(profile2)
# Combines information from both profiles
```

## Migration from Existing Formats

### Server.py Format
The `StandardCharacterProfile` is fully compatible with the existing `server.py` format:

```python
# Existing server.py format works directly
server_data = {
    'name': 'Character Name',
    'aliases': ['Alias'],
    'physical_description': 'Description',
    # ... all other server.py fields
}

profile = StandardCharacterProfile.from_dict(server_data)
```

### Legacy Test Formats
```python
# Legacy simple format (from test files)
legacy_data = {
    'name': 'Legacy Character',
    'backstory': 'Background',
    'conflicts': ['conflict'],
    'fears': ['fear']
}

profile = StandardCharacterProfile.from_legacy_format(legacy_data, "simple")
```

### Migration Tool
Use the migration tool to analyze and update existing code:

```bash
# Analyze files for migration needs
python character_profile_migration.py --verbose

# Perform actual migration with backups
python character_profile_migration.py --migrate --backup
```

## Common Issues Resolved

### 1. 'skin' Parameter Errors
**Problem**: Tools failing with "'skin' parameter doesn't exist" errors
**Solution**: `StandardCharacterProfile` ignores unknown parameters

### 2. 'age' Parameter Errors
**Problem**: Tools failing with "'age' parameter doesn't exist" errors
**Solution**: Age information can be included in `backstory` or `physical_description`

### 3. Format Mismatches
**Problem**: Different tools expecting different field names/types
**Solution**: Consistent format with automatic type conversion

### 4. Missing Field Errors
**Problem**: Tools failing when expected fields are missing
**Solution**: All fields have sensible defaults

## Best Practices

### 1. Always Use from_dict for External Data
```python
# Good - handles format issues gracefully
profile = StandardCharacterProfile.from_dict(external_data)

# Avoid - may fail with format mismatches
profile = StandardCharacterProfile(**external_data)
```

### 2. Validate Data Before Processing
```python
issues = validate_character_profile_data(data)
if issues:
    print(f"Data issues: {issues}")
else:
    profile = StandardCharacterProfile.from_dict(data)
```

### 3. Check Completeness for Analysis
```python
if profile.is_complete():
    # Proceed with full analysis
    detailed_analysis = analyze_character(profile)
else:
    # Use basic analysis or request more information
    basic_analysis = basic_character_analysis(profile)
```

### 4. Use Appropriate Legacy Formats
```python
# For old test compatibility
legacy_format = profile.to_legacy_format("simple")

# For tools that need basic info
minimal_format = profile.to_legacy_format("minimal")

# For full compatibility
full_format = profile.to_dict()
```

## Testing

The `StandardCharacterProfile` comes with comprehensive tests:

```bash
# Run basic tests
python test_standard_character_profile.py

# Run full test suite
python -m pytest test_standard_character_profile.py -v

# Run integration tests
python -m pytest test_standard_character_profile_integration.py -v
```

## API Reference

### Class: StandardCharacterProfile

#### Constructor
```python
StandardCharacterProfile(
    name: str,
    aliases: List[str] = [],
    physical_description: str = "",
    mannerisms: List[str] = [],
    speech_patterns: List[str] = [],
    behavioral_traits: List[str] = [],
    backstory: str = "",
    relationships: List[str] = [],
    formative_experiences: List[str] = [],
    social_connections: List[str] = [],
    motivations: List[str] = [],
    fears: List[str] = [],
    desires: List[str] = [],
    conflicts: List[str] = [],
    personality_drivers: List[str] = [],
    confidence_score: float = 1.0,
    text_references: List[str] = [],
    first_appearance: str = "",
    importance_score: float = 1.0
)
```

#### Class Methods
- `from_dict(data: Dict[str, Any]) -> StandardCharacterProfile`
- `from_legacy_format(data: Dict[str, Any], format_type: str = "auto") -> StandardCharacterProfile`

#### Instance Methods
- `to_dict() -> Dict[str, Any]`
- `to_legacy_format(format_type: str = "simple") -> Dict[str, Any]`
- `merge_with(other: StandardCharacterProfile) -> StandardCharacterProfile`
- `is_complete() -> bool`
- `get_summary() -> str`

#### Utility Functions
- `create_character_profile_from_text(text: str, name: str = None) -> StandardCharacterProfile`
- `validate_character_profile_data(data: Dict[str, Any]) -> List[str]`

## Requirements Addressed

This implementation addresses the following requirements from the specification:

- **Requirement 2.1**: Character profiles accept expected JSON format without 'skin' parameter errors
- **Requirement 2.2**: CharacterProfile uses correct parameter names and structure
- **Requirement 8.1**: Character profiles accept profiles without 'age' parameter errors
- **Requirement 8.2**: CharacterProfile objects use correct initialization parameters
- **Requirement 13.1**: Consistent character profile formats across all tools
- **Requirement 13.2**: Shared and reused data models to prevent format mismatches

## Conclusion

The `StandardCharacterProfile` provides a robust, flexible, and backward-compatible solution to the character profile format issues identified in the MCP tools diagnostic report. It handles all the problematic scenarios while maintaining compatibility with existing code and providing a foundation for future enhancements.