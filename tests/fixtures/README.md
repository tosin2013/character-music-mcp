# Test Fixtures and Utilities

This directory contains comprehensive test data fixtures and utilities for the character-driven music generation MCP server testing framework.

## Files Overview

### `test_data.py`
Comprehensive test data management system with:

- **12 realistic narrative scenarios** covering different genres, complexity levels, and use cases
- **11 expected character profiles** with complete three-layer analysis
- **11 expected artist personas** with proper genre mappings and artistic details
- **9 expected Suno command sets** with various command types and effectiveness scores
- **Validation framework** for comparing actual vs expected outputs
- **Album creation fixtures** for testing complete album workflows
- **Performance benchmarks** for load and stress testing
- **Batch testing utilities** for processing multiple scenarios

### `mock_contexts.py`
Mock context classes for testing MCP server functionality:

- **MockContext**: Basic context with logging and performance tracking
- **MockBatchContext**: Specialized for batch processing tests
- **MockConcurrentContext**: For testing concurrent request handling
- **MockPerformanceContext**: For performance and resource monitoring tests

## Test Scenarios

### Simple Scenarios
- `single_character_simple`: Sarah Chen's perfectionist breakthrough
- `romance_contemporary`: Maya Patel's coffee shop connection
- `minimal_character_edge`: Edge case with minimal character data

### Medium Complexity
- `multi_character_medium`: Elena Rodriguez and David's artistic relationship
- `sci_fi_adventure`: Captain Zara Okafor's space crisis
- `historical_drama`: Amelia Hartwell's Victorian mathematical rebellion
- `coming_of_age`: Alex Kim's cultural identity struggle
- `family_saga`: Rosa Delgado's generational wisdom

### Complex Scenarios
- `concept_album_complex`: The Philosopher's existential journey
- `emotional_intensity_high`: Marcus's grief transformation
- `urban_fantasy`: Detective Riley Santos's supernatural investigation
- `psychological_thriller`: Dr. Catherine Wells's reality distortion

## Usage Examples

### Basic Test Data Access
```python
from tests.fixtures.test_data import test_data_manager

# Get a narrative scenario
scenario = test_data_manager.get_test_scenario("single_character_simple")
narrative = test_data_manager.get_sample_narrative("single_character_simple")

# Get expected outputs
character = test_data_manager.get_expected_character("Sarah Chen")
persona = test_data_manager.get_expected_persona("Sarah Chen")
commands = test_data_manager.get_expected_commands("Sarah Chen")
```

### Validation Testing
```python
from tests.fixtures.test_data import comprehensive_validator

# Validate complete workflow
results = comprehensive_validator.validate_complete_workflow(
    "single_character_simple",
    actual_character,
    actual_persona,
    actual_commands
)

# Validate album creation
album_result = comprehensive_validator.validate_album_creation(
    "concept_album_complex",
    album_tracks
)
```

### Mock Context Usage
```python
from tests.fixtures.mock_contexts import create_mock_context
import asyncio

async def test_with_mock():
    ctx = create_mock_context("performance")
    await ctx.info("Starting test")
    
    # Your test code here
    
    stats = ctx.get_performance_stats()
    print(f"Test completed with {stats['error_count']} errors")
```

### Album Testing
```python
# Create album test fixture
album_fixture = test_data_manager.create_album_test_fixture(
    "concept_album_complex", 
    track_count=6
)

# Get expected track structure
expected_tracks = album_fixture["expected_track_structure"]
validation_criteria = album_fixture["validation_criteria"]
```

### Performance Testing
```python
# Get performance test scenarios
perf_scenarios = test_data_manager.get_performance_test_scenarios()

# Create performance benchmark
benchmark = comprehensive_validator.create_performance_benchmark(
    ["concept_album_complex", "multi_character_medium"]
)
```

### Batch Testing
```python
# Create batch test data
batch_data = test_data_manager.create_batch_test_data([
    "single_character_simple",
    "multi_character_medium", 
    "concept_album_complex"
])

# Use batch context for testing
batch_ctx = create_mock_context("batch", batch_size=10)
```

## Validation Framework

The validation framework provides comprehensive checking of:

### Character Validation
- Name matching
- Confidence score thresholds
- Required field completeness
- Thematic alignment
- Overall completeness scoring

### Persona Validation
- Character name matching
- Genre alignment (primary and secondary)
- Confidence thresholds
- Required field completeness
- Artistic coherence checking

### Command Validation
- Command type matching
- Character source verification
- Effectiveness thresholds
- Required tag presence
- Tag alignment scoring
- Command completeness

### Album Validation
- Track count and structure
- Thematic consistency across tracks
- Character authenticity maintenance
- Genre coherence
- Overall quality scoring

## Export Utilities

Export test fixtures for external use:

```python
from tests.fixtures.test_data import export_test_fixtures

# Export all fixtures to JSON files
export_test_fixtures("my_test_export/")
```

This creates:
- `test_data.json`: Complete test data
- `unit_test_suite.json`: Simple scenarios for unit tests
- `integration_test_suite.json`: Complex scenarios for integration tests
- `performance_test_suite.json`: Large scenarios for performance tests

## Quality Metrics

The test fixtures are designed to meet these quality standards:

- **Character Confidence**: Minimum 0.7 for all expected characters
- **Persona Confidence**: Minimum 0.7 for all expected personas  
- **Command Effectiveness**: Minimum 0.7 for all expected commands
- **Validation Coverage**: 100% of scenarios have expected outputs
- **Complexity Distribution**: Balanced across simple/medium/complex
- **Genre Coverage**: 15+ different musical genres represented
- **Narrative Diversity**: 12 different narrative types and themes

## Integration with Test Suites

These fixtures integrate with:

- **Unit Tests**: Individual component testing with simple scenarios
- **Integration Tests**: Complete workflow testing with complex scenarios
- **Performance Tests**: Load testing with large narratives and batch processing
- **Album Creation Tests**: Multi-track generation and consistency validation
- **MCP Tools Tests**: All MCP server tools with realistic data
- **Edge Case Tests**: Boundary conditions and error scenarios

The comprehensive test data system ensures reliable, consistent, and thorough testing of all character-driven music generation functionality.