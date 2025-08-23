# Test Infrastructure for Character-Driven Music Generation

This directory contains the unified test infrastructure for the Character-Driven Music Generation MCP Server.

## Directory Structure

```
tests/
├── unit/                    # Unit tests for individual components
├── integration/             # Integration tests for complete workflows  
├── performance/             # Performance and load tests
├── fixtures/                # Test data and utilities
│   ├── test_data.py        # Centralized test data management
│   ├── mock_contexts.py    # Mock MCP contexts for testing
│   └── sample_narratives.py # Sample narrative texts
├── test_runner.py          # Unified test execution
├── test_config.py          # Test configuration management
└── README.md               # This file
```

## Quick Start

### Run All Tests
```bash
python tests/test_runner.py
```

### Run Specific Test Suite
```bash
python tests/test_runner.py --suite unit
python tests/test_runner.py --suite integration
```

### Run with Custom Configuration
```bash
TEST_ENV=ci python tests/test_runner.py
TEST_VERBOSE=true python tests/test_runner.py
```

## Test Data Management

The `TestDataManager` class provides centralized access to test scenarios:

```python
from tests.fixtures.test_data import test_data_manager

# Get a test scenario
scenario = test_data_manager.get_test_scenario("single_character_simple")
narrative = test_data_manager.get_sample_narrative("single_character_simple")

# Get expected results for validation
expected_char = test_data_manager.get_expected_character("Sarah Chen")
expected_persona = test_data_manager.get_expected_persona("Sarah Chen")
```

### Available Test Scenarios

1. **single_character_simple** - Simple narrative with one clear character
2. **multi_character_medium** - Multiple characters with relationships
3. **concept_album_complex** - Complex philosophical narrative
4. **minimal_character_edge** - Edge case with minimal character data
5. **emotional_intensity_high** - High emotional intensity testing

## Mock Contexts

Use mock contexts for testing without MCP server:

```python
from tests.fixtures.mock_contexts import MockContext, create_mock_context

# Basic mock context
ctx = MockContext()
await ctx.info("Test message")

# Specialized contexts
batch_ctx = create_mock_context("batch", batch_size=10)
perf_ctx = create_mock_context("performance")
```

## Writing Tests

### Unit Tests
Place in `tests/unit/` directory:

```python
async def test_character_analysis(ctx: MockContext, data_manager: TestDataManager):
    """Test character analysis functionality"""
    narrative = data_manager.get_sample_narrative("single_character_simple")
    
    # Your test logic here
    result = await analyze_character_text(narrative, ctx)
    
    assert len(result.characters) > 0
    assert result.characters[0].confidence_score > 0.8
```

### Integration Tests
Place in `tests/integration/` directory:

```python
async def test_complete_workflow(ctx: MockContext, data_manager: TestDataManager):
    """Test complete workflow integration"""
    scenario = data_manager.get_test_scenario("single_character_simple")
    
    # Test full pipeline
    characters = await analyze_characters(scenario.narrative_text, ctx)
    personas = await generate_personas(characters, ctx)
    commands = await create_suno_commands(personas, ctx)
    
    assert len(commands) > 0
```

### Performance Tests
Place in `tests/performance/` directory:

```python
async def test_large_input_processing(ctx: MockPerformanceContext, data_manager: TestDataManager):
    """Test processing of large inputs"""
    large_text = "..." * 10000  # Large text
    
    start_time = time.time()
    result = await analyze_character_text(large_text, ctx)
    processing_time = time.time() - start_time
    
    await ctx.record_performance_metric("large_text_processing_time", processing_time)
    assert processing_time < 15.0  # Should complete within 15 seconds
```

## Configuration

Test behavior is controlled by `test_config.py`:

### Environment Variables
- `TEST_ENV` - Environment (development, ci, production)
- `TEST_VERBOSE` - Enable verbose output (true/false)
- `TEST_PARALLEL` - Enable parallel execution (true/false)
- `TEST_TIMEOUT` - Test timeout in seconds
- `TEST_CHARACTER_ANALYSIS_TIME` - Performance threshold for character analysis

### Performance Thresholds
Default performance thresholds:
- Character analysis: 5.0 seconds
- Persona generation: 3.0 seconds  
- Command generation: 2.0 seconds
- Total workflow: 10.0 seconds
- Memory usage: 500 MB

## Test Reports

Test reports are automatically generated:

### JSON Report
```json
{
  "start_time": "2024-01-01T10:00:00",
  "total_tests": 25,
  "total_passed": 23,
  "total_failed": 2,
  "overall_success_rate": 0.92,
  "suite_results": [...]
}
```

### Performance Benchmarks
```
🚀 Performance Benchmarks:
   ✅ character_analysis_benchmark: avg 2.5s (threshold: 5.0s)
   ✅ persona_generation_benchmark: avg 1.8s (threshold: 3.0s)
   ✅ memory_usage_benchmark: avg 245MB (threshold: 500MB)
```

## Best Practices

### Test Organization
- One test file per major component
- Group related tests in test classes
- Use descriptive test names
- Include docstrings explaining test purpose

### Test Data
- Use TestDataManager for consistent test data
- Create realistic test scenarios
- Include edge cases and error conditions
- Validate against expected results

### Performance Testing
- Set realistic performance thresholds
- Test with various input sizes
- Monitor memory usage
- Test concurrent scenarios

### Error Handling
- Test error conditions explicitly
- Verify error messages are helpful
- Test recovery mechanisms
- Validate graceful degradation

## Integration with Existing Tests

The new infrastructure is compatible with existing tests:
- Existing test files are automatically discovered
- Old test functions work without modification
- Gradual migration to new patterns is supported

## Continuous Integration

For CI/CD environments:

```bash
# Set CI environment
export TEST_ENV=ci

# Run with CI-optimized settings
python tests/test_runner.py

# Check exit code
echo $?  # 0 for success, 1 for failure
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure parent directory is in Python path
2. **Test Discovery**: Check test file naming (test_*.py)
3. **Performance Failures**: Adjust thresholds in test_config.py
4. **Mock Context Issues**: Verify async/await usage

### Debug Mode
```bash
TEST_VERBOSE=true python tests/test_runner.py
```

### Individual Test Execution
```python
# Run specific test
python -c "
import asyncio
from tests.fixtures.test_data import test_data_manager
from tests.fixtures.mock_contexts import MockContext

async def main():
    ctx = MockContext()
    # Your test code here
    
asyncio.run(main())
"
```

## Future Enhancements

Planned improvements:
- HTML test reports with charts
- Code coverage integration
- Parallel test execution
- Test result caching
- Integration with pytest
- Visual regression testing for UI components
- Load testing capabilities
- Test data generation tools