# Character Music MCP - Test Automation Makefile

.PHONY: help install test test-unit test-integration test-performance test-validation test-all
.PHONY: coverage benchmark validate lint format security clean setup-ci

# Default target
help:
	@echo "Character Music MCP - Test Automation"
	@echo "====================================="
	@echo ""
	@echo "Available targets:"
	@echo "  install          Install dependencies"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-performance Run performance tests only"
	@echo "  test-validation  Run validation tests only"
	@echo "  test-all         Run comprehensive test suite"
	@echo "  coverage         Generate coverage report"
	@echo "  benchmark        Run performance benchmarks"
	@echo "  validate         Validate documentation and examples"
	@echo "  lint             Run code linting"
	@echo "  format           Format code"
	@echo "  security         Run security scans"
	@echo "  setup-ci         Setup CI environment"
	@echo "  clean            Clean build artifacts"
	@echo ""

# Environment setup
install:
	@echo "📦 Installing dependencies..."
	python -m pip install --upgrade pip
	python -m pip install -e .
	python -m pip install pytest pytest-cov pytest-asyncio pytest-benchmark pytest-timeout pytest-xdist
	python -m pip install coverage[toml] ruff mypy safety bandit
	python -m pip install jinja2 markdown

# Test execution
test: test-unit test-integration

test-unit:
	@echo "🧪 Running unit tests..."
	python -m pytest tests/unit/ -v --cov=. --cov-report=term-missing

test-integration:
	@echo "🔗 Running integration tests..."
	python -m pytest tests/integration/ -v --timeout=300

test-performance:
	@echo "⚡ Running performance tests..."
	python -m pytest tests/performance/ -v --benchmark-only

test-validation:
	@echo "📚 Running validation tests..."
	python -m pytest tests/validation/ -v

test-all:
	@echo "🚀 Running comprehensive test suite..."
	python scripts/run_tests.py

# Coverage analysis
coverage:
	@echo "📊 Generating coverage report..."
	python -m pytest tests/unit/ tests/integration/ --cov=. --cov-report=html --cov-report=xml --cov-report=term
	@echo "Coverage report generated in htmlcov/"

# Performance benchmarking
benchmark:
	@echo "🏃 Running performance benchmarks..."
	python scripts/run_benchmarks.py
	@if [ -f baseline_benchmark_results.json ]; then \
		python scripts/compare_benchmarks.py benchmark_results.json; \
	fi

# Documentation validation
validate:
	@echo "📋 Validating documentation and examples..."
	python scripts/validate_all.py

# Code quality
lint:
	@echo "🔍 Running code linting..."
	python -m ruff check .
	python -m mypy . --ignore-missing-imports --no-strict-optional

format:
	@echo "✨ Formatting code..."
	python -m ruff format .

# Security scanning
security:
	@echo "🔒 Running security scans..."
	python -m safety check --json --output safety_report.json || true
	python -m bandit -r . -f json -o bandit_report.json || true
	@echo "Security reports generated: safety_report.json, bandit_report.json"

# CI setup
setup-ci:
	@echo "🔧 Setting up CI environment..."
	python scripts/run_tests.py --coverage-threshold 80
	python scripts/run_benchmarks.py
	python scripts/validate_all.py
	python scripts/generate_dashboard.py

# Cleanup
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf test_report_*.json
	rm -rf benchmark_results.json
	rm -rf validation_report_*.json
	rm -rf safety_report.json
	rm -rf bandit_report.json

# Development workflow
dev-test: clean install test coverage

# CI workflow
ci: clean install test-all benchmark validate security

# Quick checks
quick: test-unit lint

# Full validation
full: clean install test-all coverage benchmark validate lint security