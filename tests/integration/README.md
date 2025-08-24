# Integration Test Suites

This directory contains comprehensive integration test suites for the character-driven music generation MCP server. These tests validate complete workflows, album creation processes, and MCP tool functionality.

## Test Suites Overview

### 1. Complete Workflow Integration Tests (`test_complete_workflow.py`)

Tests end-to-end workflow validation, data consistency across all workflow steps, and character analysis to Suno command pipeline integrity.

**Key Test Cases:**
- Single character complete workflow validation
- Multi-character workflow with relationship handling
- Complete workflow MCP tool integration
- Creative music generation integration
- Workflow performance benchmarks
- Error handling and recovery mechanisms
- Data consistency validation across pipeline steps

**Requirements Covered:** 1.5, 3.2

### 2. Album Creation Integration Tests (`test_album_creation.py`)

Tests multi-song generation workflows, thematic consistency validation, and comprehensive album metadata handling.

**Key Test Cases:**
- Single character album creation with thematic consistency
- Multi-character album with relationship exploration
- Concept album generation from abstract themes
- Album metadata completeness validation
- Batch processing of multiple albums
- Track listing accuracy and narrative flow

**Requirements Covered:** 3.1, 3.2, 3.3, 3.4

### 3. MCP Tools Integration Tests (`test_mcp_tools.py`)

Tests all MCP tool validation including parameter validation, error handling, and concurrent execution.

**Key Test Cases:**
- `analyze_character_text` tool validation
- `generate_artist_personas` tool validation  
- `create_suno_commands` tool validation
- `complete_workflow` tool validation
- `creative_music_generation` tool validation
- Enhanced tools integration (if available)
- Concurrent tool execution testing
- Comprehensive error handling validation
- Parameter validation across all tools

**Requirements Covered:** 1.1, 3.5

### 4. Wiki Integration End-to-End Tests (`test_wiki_integration_end_to_end.py`)

Tests complete wiki data integration workflows including download, parse, generate, and attribute flows.

**Key Test Cases:**
- Complete download → parse → generate → attribute flow
- Fallback scenarios with unavailable wiki data
- Configuration changes and system reconfiguration
- Concurrent access and performance under load
- Data consistency across wiki integration components
- Error recovery and resilience testing

**Requirements Covered:** All dynamic Suno data integration requirements

### 5. Wiki Performance and Edge Cases (`test_wiki_performance_and_edge_cases.py`)

Tests performance characteristics, edge cases, and stress scenarios for wiki data integration.

**Key Test Cases:**
- Large dataset handling and parsing performance
- Memory usage patterns and cleanup
- Concurrent stress testing with multiple requests
- Edge case inputs and boundary conditions
- Cache performance and efficiency
- Resource cleanup and limits validation

**Requirements Covered:** Performance validation and edge case handling

### 6. Wiki Integration Test Runner (`test_wiki_integration_runner.py`)

Comprehensive test runner that orchestrates all wiki integration tests with detailed reporting.

**Key Features:**
- Unified execution of all wiki integration tests
- Performance metrics collection and analysis
- Detailed test reporting with JSON output
- Configurable test categories (end-to-end, performance, all)
- Error handling and cleanup management

## Running the Tests

### Prerequisites

```bash
pip install pytest pytest-asyncio
```

### Running Individual Test Suites

```bash
# Complete workflow tests
pytest tests/integration/test_complete_workflow.py -v

# Album creation tests  
pytest tests/integration/test_album_creation.py -v

# MCP tools tests
pytest tests/integration/test_mcp_tools.py -v

# Wiki integration end-to-end tests
pytest tests/integration/test_wiki_integration_end_to_end.py -v

# Wiki performance and edge case tests
pytest tests/integration/test_wiki_performance_and_edge_cases.py -v
```

### Running All Integration Tests

```bash
pytest tests/integration/ -v
```

### Running Wiki Integration Tests

```bash
# Run all wiki integration tests
python tests/integration/test_wiki_integration_runner.py --category all

# Run only end-to-end wiki tests
python tests/integration/test_wiki_integration_runner.py --category end_to_end

# Run only performance wiki tests
python tests/integration/test_wiki_integration_runner.py --category performance

# Run quick wiki tests (no performance tests)
python tests/integration/test_wiki_integration_runner.py --category quick

# Run with stress tests (longer execution)
python tests/integration/test_wiki_integration_runner.py --category all --stress
```

### Running with Coverage

```bash
pytest tests/integration/ --cov=server --cov-report=html
```

## Test Structure

Each test suite follows a consistent structure:

```python
class TestSuiteName:
    def setup_method(self):
        """Set up test environment"""
        self.test_data = TestDataManager()
        self.mock_context = MockContext("test_session")
    
    @pytest.mark.asyncio
    async def test_specific_functionality(self):
        """Test specific functionality with validation"""
        # Arrange
        scenario = self.test_data.get_scenario("test_case")
        
        # Act
        result = await target_function(self.mock_context, **params)
        
        # Assert
        assert result is not None
        # ... detailed validations
```

## Test Data and Fixtures

Integration tests use centralized test data from:
- `tests/fixtures/test_data.py` - Realistic test scenarios and expected outputs
- `tests/fixtures/mock_contexts.py` - Mock MCP contexts for testing

## Performance Benchmarks

The integration tests include performance benchmarks:

- **Character Analysis**: < 5 seconds for typical inputs
- **Persona Generation**: < 3 seconds per character
- **Command Generation**: < 2 seconds per song
- **Total Workflow**: < 10 seconds end-to-end
- **Concurrent Capacity**: Handle 3+ simultaneous requests

## Error Handling Validation

Tests validate error handling for:
- Empty or invalid input text
- Malformed character data
- Missing required parameters
- Network/processing failures
- Resource constraints
- Concurrent access conflicts

## Validation Script

Use the validation script to check test structure without running full tests:

```bash
python tests/integration/validate_integration_tests.py
```

## Test Scenarios

The integration tests cover various narrative scenarios:

- **Single Character Simple**: Basic character-driven music generation
- **Multi-Character Medium**: Complex relationship dynamics
- **Emotional Intensity High**: High-stakes emotional content
- **Concept Album Complex**: Philosophical/abstract themes
- **Sci-Fi Adventure**: Genre-specific content adaptation
- **Romance Contemporary**: Modern relationship themes
- **Historical Drama**: Period-specific character challenges
- **Urban Fantasy**: Supernatural/fantasy elements
- **Coming of Age**: Universal growth themes
- **Psychological Thriller**: Complex psychological content

## Integration with Main Test Suite

These integration tests complement the unit tests in `tests/unit/` and work with the unified test runner in `tests/test_runner.py`.

## Continuous Integration

Integration tests are designed to run in CI/CD pipelines with:
- Automated test execution
- Performance regression detection
- Coverage reporting
- Error notification

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure project root is in Python path
2. **Async Test Failures**: Verify pytest-asyncio is installed
3. **Mock Context Issues**: Check mock context setup in test fixtures
4. **Performance Test Failures**: Adjust thresholds for slower environments

### Debug Mode

Run tests with debug output:

```bash
pytest tests/integration/ -v -s --log-cli-level=DEBUG
```

## Contributing

When adding new integration tests:

1. Follow the existing test structure patterns
2. Use the centralized test data manager
3. Include comprehensive validation assertions
4. Add performance benchmarks where appropriate
5. Test both success and error scenarios
6. Update this README with new test descriptions

## Test Coverage Goals

- **Workflow Coverage**: 100% of major workflow paths
- **Tool Coverage**: All MCP tools with parameter variations
- **Error Coverage**: All error conditions and edge cases
- **Performance Coverage**: All critical performance paths
- **Integration Coverage**: All component interactions