# Design Document

## Overview

This design refactors and integrates existing MCP tools to fix fundamental issues with conceptual album generation. Rather than adding new components, we'll enhance existing tools with better logic, consolidate redundant code, and improve the middleware coordination. The focus is on making the current codebase work properly for conceptual content while reducing overall complexity.

## Architecture

### Refactored Architecture (Reusing Existing Components)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Existing MCP Tools (Refactored)             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Enhanced        │  │ Working         │  │ Existing        │ │
│  │ Character       │  │ Universal       │  │ Album Tools     │ │
│  │ Analyzer        │  │ Processor       │  │ (Consolidated)  │ │
│  │ (Fix Logic)     │  │ (Content Type)  │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                    Existing Middleware (Enhanced)              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ MCP Tools       │  │ MCP Error       │  │ MCP Data        │ │
│  │ Integration     │  │ Recovery        │  │ Validation      │ │
│  │ (Improved)      │  │ (Enhanced)      │  │ (Fixed)         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces (Refactoring Existing Code)

### 1. Fix WorkingUniversalProcessor (Existing File)

**Current Issues**: Fails to detect content types, extracts random words as characters
**Refactoring Approach**: Add intelligent content detection to existing processor

**Enhanced Logic**:
```python
# Enhance existing WorkingUniversalProcessor class
class WorkingUniversalProcessor:
    # Keep existing methods, add content type detection
    
    def detect_content_type(self, text: str) -> str:
        """Add to existing processor - detect if content is narrative, conceptual, or descriptive"""
        # Logic to identify content type
        
    def extract_or_create_characters(self, text: str, content_type: str) -> List[CharacterProfile]:
        """Refactor existing character extraction to handle different content types"""
        # Enhanced logic that doesn't extract random words
```

### 2. Fix EnhancedCharacterAnalyzer (Existing File)

**Current Issues**: Generic character creation, no conceptual understanding
**Refactoring Approach**: Enhance existing methods instead of adding new classes

**Enhanced Methods**:
```python
# Enhance existing EnhancedCharacterAnalyzer class
class EnhancedCharacterAnalyzer:
    # Keep all existing methods
    
    def analyze_character_text(self, ctx: Context, text: str) -> Dict:
        """Enhance existing method to handle conceptual content"""
        # Add content type detection
        # Improve character extraction logic
        # Handle explicit character descriptions
        
    def create_character_from_concepts(self, concepts: List[str]) -> CharacterProfile:
        """Add method to existing class - don't create new class"""
        # Logic for conceptual character creation
```

### 3. Consolidate Album Generation Tools (Existing Files)

**Current Issues**: Multiple album tools with overlapping functionality
**Refactoring Approach**: Consolidate into single, robust album generator

**Files to Consolidate**:
- `create_story_integrated_album` functionality
- `create_character_album` functionality  
- Album generation logic from `server.py`

**Consolidated Interface**:
```python
# Enhance existing album generation in server.py
@mcp.tool()
async def create_conceptual_album(ctx: Context, 
                                narrative_text: str,
                                album_concept: str,
                                track_count: int = 9,
                                genre: str = "alternative") -> str:
    """Consolidate all album generation into single, robust tool"""
    # Use existing middleware for coordination
    # Leverage existing character analysis
    # Generate unique, coherent tracks
```

### 4. Enhance Existing Middleware (No New Components)

**Files to Enhance**:
- `mcp_tools_integration.py` - Better tool coordination
- `mcp_error_recovery.py` - Smarter fallback strategies  
- `mcp_data_validation.py` - Content validation

**Enhanced Coordination**:
```python
# Enhance existing MCPToolsIntegration class
class MCPToolsIntegration:
    # Keep existing methods
    
    async def coordinate_album_workflow(self, content: str, content_type: str) -> Dict:
        """Enhance existing workflow coordination"""
        # Better tool sequencing
        # State management between tools
        # Error recovery
```

## Data Models (Enhance Existing Models)

### Enhance Existing CharacterProfile (Don't Create New Classes)

```python
# Enhance existing CharacterProfile in standard_character_profile.py
@dataclass
class CharacterProfile:
    # Keep all existing fields
    name: str
    aliases: List[str]
    # ... all existing fields ...
    
    # Add optional fields for conceptual processing (backward compatible)
    conceptual_basis: Optional[List[str]] = None
    content_type: Optional[str] = None  # "narrative", "conceptual", "descriptive"
    processing_notes: Optional[str] = None
    
    def is_conceptual(self) -> bool:
        """Helper method to identify conceptual characters"""
        return self.content_type in ["conceptual", "descriptive"]
```

### Enhance Existing Album Models (Reuse Existing)

```python
# Use existing SunoCommand and ArtistPersona classes
# Add validation methods to existing classes instead of creating new ones

# Enhance existing TextAnalysisResult
class TextAnalysisResult(BaseModel):
    # Keep all existing fields
    characters: List[CharacterProfile]
    # ... existing fields ...
    
    # Add optional field for content type detection
    detected_content_type: Optional[str] = None
    processing_strategy: Optional[str] = None
```

### Simple Content Type Detection (No Complex Enums)

```python
# Simple string-based content types (no new enums)
CONTENT_TYPES = {
    "narrative": "Traditional story with characters",
    "conceptual": "Abstract concepts or philosophical content", 
    "descriptive": "Explicit character or concept descriptions",
    "mixed": "Combination of content types"
}

PROCESSING_STRATEGIES = {
    "extract": "Extract existing characters from narrative",
    "create": "Create characters from concepts",
    "use_explicit": "Use provided character descriptions",
    "hybrid": "Combine extraction and creation"
}
```

## Error Handling

### Enhanced Error Recovery

```python
class ConceptualProcessingError(Exception):
    """Base exception for conceptual processing errors"""
    pass

class CharacterCreationError(ConceptualProcessingError):
    """Raised when character creation fails"""
    pass

class AlbumGenerationError(ConceptualProcessingError):
    """Raised when album generation fails"""
    pass

# Enhanced error handling in middleware
async def handle_processing_error(error: Exception, context: ProcessingContext) -> FallbackResult:
    """Enhanced error handling with multiple fallback strategies"""
    if isinstance(error, CharacterCreationError):
        # Try alternative character creation methods
        return await attempt_fallback_character_creation(context)
    elif isinstance(error, AlbumGenerationError):
        # Try simplified album generation
        return await attempt_simplified_album_generation(context)
    else:
        # Use existing error handling
        return await existing_error_handler(error, context)
```

## Testing Strategy

### Integration with Existing Test Framework

```python
# Extend existing test suites
class TestConceptualAlbumGeneration(TestMCPToolsWorkflowIntegration):
    """Test conceptual album generation capabilities"""
    
    async def test_philosophical_content_processing(self):
        """Test processing of philosophical texts"""
        # Use existing test infrastructure
        
    async def test_character_description_processing(self):
        """Test explicit character description handling"""
        # Leverage existing validation framework
        
    async def test_conceptual_character_creation(self):
        """Test creation of characters from abstract concepts"""
        # Integrate with existing character analysis tests
        
    async def test_album_coherence_validation(self):
        """Test album-wide consistency and quality"""
        # Use existing album creation test framework
```

## Implementation Strategy (Refactor, Don't Add)

### Priority 1: Fix Core Character Analysis Logic
**Files to Refactor**:
- `working_universal_processor.py` - Fix character extraction logic
- `enhanced_character_analyzer.py` - Add content type detection
- `standard_character_profile.py` - Add optional conceptual fields

**Approach**: Enhance existing methods, don't create new classes

### Priority 2: Consolidate Album Generation Tools  
**Files to Consolidate**:
- Merge album generation logic from `server.py` into single robust tool
- Remove redundant album creation functions
- Use existing `ArtistPersona` and `SunoCommand` classes

**Approach**: One consolidated album tool instead of multiple overlapping tools

### Priority 3: Improve Middleware Coordination
**Files to Enhance**:
- `mcp_tools_integration.py` - Better workflow coordination
- `mcp_error_recovery.py` - Smarter fallback strategies
- `mcp_data_validation.py` - Content validation

**Approach**: Enhance existing middleware, don't add new layers

### Priority 4: Code Cleanup and Consolidation
**Cleanup Tasks**:
- Remove unused or redundant functions
- Consolidate similar functionality
- Improve existing error handling
- Enhance existing validation

**Approach**: Reduce codebase size while improving functionality

## Files to Modify (Minimal Changes)

### Core Files (Essential Changes):
1. `working_universal_processor.py` - Fix character extraction
2. `enhanced_character_analyzer.py` - Add content detection  
3. `server.py` - Consolidate album tools
4. `mcp_tools_integration.py` - Improve coordination

### Support Files (Minor Enhancements):
5. `standard_character_profile.py` - Add optional fields
6. `mcp_error_recovery.py` - Better fallbacks
7. `mcp_data_validation.py` - Content validation

### Files to Review for Consolidation:
- Multiple album generation functions in `server.py`
- Overlapping character analysis logic
- Redundant error handling code
- Duplicate validation functions

This approach focuses on fixing existing code rather than adding complexity, addressing your concern about code bloat while solving the core issues.