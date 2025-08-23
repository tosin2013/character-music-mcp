# Test Automation Scripts

This directory contains scripts for automated testing, performance benchmarking, and continuous validation of the Character Music MCP server.

## Scripts Overview

### 🧪 Test Execution

#### `run_tests.py`
Comprehensive test execution script that runs all test suites with proper configuration and reporting.

**Features:**
- Runs unit, integration, performance, and validation test suites
- Generates coverage reports with configurable thresholds
- Provides detailed test result reporting
- Supports parallel test execution
- Integrates with CI/CD pipelines

**Usage:**
```bash
# Run all test suites
python scripts/run_tests.py

# Run specific test suites
python scripts/run_tests.py --suites unit integration

# Set custom coverage threshold
python scripts/run_tests.py --coverage-threshold 85

# Fail fast on first failure
python scripts/run_tests.py --fail-fast
```

### 🚀 Performance Benchmarking

#### `run_benchmarks.py`
Performance benchmark runner that measures execution time, memory usage, and system performance.

**Features:**
- Benchmarks character analysis, persona generation, and command creation
- Tests concurrent request handling
- Measures large text processing performance
- Generates detailed performance reports
- Tracks performance against configurable thresholds

**Usage:**
```bash
# Run all benchmarks
python scripts/run_benchmarks.py

# Save results to custom file
python scripts/run_benchmarks.py --output my_benchmarks.json

# Run with custom iteration count
python scripts/run_benchmarks.py --iterations 20
```

#### `compare_benchmarks.py`
Compares current benchmark results with baseline to detect performance regressions.

**Features:**
- Compares execution time and memory usage
- Detects performance regressions and improvements
- Generates comparison reports
- Supports automated regression detection

**Usage:**
```bash
# Compare with automatic baseline detection
python scripts/compare_benchmarks.py benchmark_results.json

# Compare with specific baseline
python scripts/compare_benchmarks.py benchmark_results.json --baseline baseline_results.json

# Fail on regression detection
python scripts/compare_benchmarks.py benchmark_results.json --fail-on-regression
```

### 📚 Documentation Validation

#### `validate_all.py`
Comprehensive validation of documentation, examples, and templates.

**Features:**
- Validates documentation completeness and accuracy
- Tests all examples for correctness
- Verifies prompt template effectiveness
- Checks internal and external links
- Validates expected file structure

**Usage:**
```bash
# Run all validations
python scripts/validate_all.py

# Run specific validation types
python scripts/validate_all.py --types documentation examples

# Set custom success threshold
python scripts/validate_all.py --threshold 0.95

# Save to custom output file
python scripts/validate_all.py --output validation_results.json
```

### 📊 Quality Dashboard

#### `generate_dashboard.py`
Generates an HTML quality dashboard from CI artifacts and test results.

**Features:**
- Aggregates test results, benchmarks, and validation reports
- Creates interactive HTML dashboard
- Provides quality metrics and trends
- Supports GitHub Pages deployment

**Usage:**
```bash
# Generate dashboard from current directory
python scripts/generate_dashboard.py

# Specify artifacts directory
python scripts/generate_dashboard.py --artifacts-dir ./ci-artifacts

# Custom output directory
python scripts/generate_dashboard.py --output-dir ./reports
```

## Integration with CI/CD

### GitHub Actions Integration

The scripts are designed to work seamlessly with the GitHub Actions workflow defined in `.github/workflows/ci.yml`:

1. **Test Execution**: `run_tests.py` runs all test suites with coverage
2. **Performance Monitoring**: `run_benchmarks.py` measures performance
3. **Regression Detection**: `compare_benchmarks.py` detects performance issues
4. **Documentation Validation**: `validate_all.py` ensures documentation quality
5. **Quality Reporting**: `generate_dashboard.py` creates comprehensive reports

### Makefile Integration

Use the provided `Makefile` for easy script execution:

```bash
# Run all tests
make test-all

# Run benchmarks
make benchmark

# Validate documentation
make validate

# Generate dashboard
make setup-ci
```

## Configuration

### Performance Thresholds

Benchmark thresholds are configured in `run_benchmarks.py`:

```python
thresholds = {
    "character_analysis_time": 5.0,  # seconds
    "persona_generation_time": 3.0,
    "command_generation_time": 2.0,
    "complete_workflow_time": 10.0,
    "memory_usage_mb": 500,
    "concurrent_requests": 5,
    "large_text_processing": 15.0,
}
```

### Coverage Thresholds

Coverage requirements are set in `run_tests.py`:

```python
coverage_thresholds = {
    "line": 80,      # 80% line coverage
    "branch": 75,    # 75% branch coverage
    "function": 90   # 90% function coverage
}
```

### Validation Thresholds

Documentation validation thresholds in `validate_all.py`:

```python
thresholds = {
    "documentation_completeness": 0.90,  # 90% completeness
    "example_accuracy": 0.95,            # 95% examples work
    "template_effectiveness": 0.85,      # 85% templates effective
    "link_validity": 0.98                # 98% links valid
}
```

## Output Files

The scripts generate various output files:

### Test Results
- `automated_test_report_YYYYMMDD_HHMMSS.json` - Comprehensive test results
- `coverage.xml` - Coverage report in XML format
- `htmlcov/` - HTML coverage report directory

### Benchmark Results
- `benchmark_results.json` - Performance benchmark results
- `benchmark_comparison.json` - Performance comparison report

### Validation Results
- `validation_report_YYYYMMDD_HHMMSS.json` - Documentation validation results

### Quality Dashboard
- `dashboard/index.html` - Interactive quality dashboard
- `dashboard/summary.json` - Quality metrics summary

### Security Reports
- `safety_report.json` - Dependency vulnerability scan
- `bandit_report.json` - Code security analysis

## Error Handling

All scripts include comprehensive error handling:

- **Graceful Degradation**: Scripts continue execution even if individual components fail
- **Detailed Logging**: Comprehensive error messages and stack traces
- **Exit Codes**: Proper exit codes for CI/CD integration
- **Timeout Handling**: Configurable timeouts for long-running operations

## Extending the Scripts

### Adding New Benchmarks

To add new performance benchmarks:

1. Add benchmark method to `PerformanceBenchmarkRunner` class
2. Update the `benchmarks` list in `run_all_benchmarks()`
3. Add threshold configuration

### Adding New Validations

To add new validation checks:

1. Add validation method to `ComprehensiveValidator` class
2. Update the validation list in `run_all_validations()`
3. Add threshold configuration

### Customizing Dashboard

To customize the quality dashboard:

1. Modify the HTML template in `generate_dashboard.py`
2. Add new data collection methods
3. Update the template data structure

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the project root is in Python path
2. **Permission Errors**: Check file permissions for output directories
3. **Timeout Issues**: Increase timeout values for slow systems
4. **Memory Issues**: Reduce benchmark iterations for resource-constrained environments

### Debug Mode

Enable debug output by setting environment variables:

```bash
export DEBUG=1
export VERBOSE=1
python scripts/run_tests.py
```

## Contributing

When adding new scripts:

1. Follow the existing code structure and patterns
2. Include comprehensive error handling
3. Add proper documentation and help text
4. Update this README with new script information
5. Add integration tests for the new functionality