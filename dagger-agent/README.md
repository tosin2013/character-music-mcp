# Dagger Test Repair Agent

An automated system that monitors GitHub Actions workflows, detects test failures, analyzes them using AI, generates fixes, and creates pull requests.

## Features

- **Automated Failure Detection**: Monitors GitHub Actions for test failures
- **AI-Powered Analysis**: Uses DeepSeek API to analyze failures and generate fixes
- **Containerized Validation**: Uses Dagger.io for reproducible test environments
- **Multi-Python Support**: Tests fixes across Python 3.10, 3.11, and 3.12
- **Pull Request Automation**: Creates PRs with proposed fixes
- **Comprehensive Logging**: Structured logging for monitoring and debugging

## Quick Start

### Prerequisites

- Python 3.10 or higher
- [Dagger CLI](https://docs.dagger.io/install) installed
- GitHub token or GitHub App credentials
- DeepSeek API key

### Installation

1. Clone the repository and navigate to the agent directory:
```bash
cd dagger-agent
```

2. Install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

3. Copy the environment configuration:
```bash
cp .env.example .env
```

4. Edit `.env` with your credentials:
```bash
# Required for local development
DEEPSEEK_API_KEY=your_deepseek_api_key

# Required only for GitHub integration (e.g., in CI/CD)
# GITHUB_TOKEN=your_github_token_here

# Optional - customize as needed
PYTHON_VERSIONS=3.10,3.11,3.12
ENABLED_FIX_TYPES=syntax,import,format,test,coverage
```

### Usage

#### Using Dagger CLI

Check agent health:
```bash
dagger call health-check
```

Run tests in a container:
```bash
dagger call run-tests --source . --python-version 3.10
```

Validate a fix:
```bash
dagger call validate-fix --source . --test-type unit
```

Run quality checks:
```bash
dagger call run-quality-checks --source . --python-version 3.10
```

#### Using the CLI Tool

The agent also provides a CLI interface:

```bash
# Check health
dagger-test-repair-agent health

# Run tests
dagger-test-repair-agent test --source . --python-version 3.10

# Run quality checks
dagger-test-repair-agent quality --source .

# Validate a fix
dagger-test-repair-agent validate --test-type unit

# Process a workflow failure (placeholder)
dagger-test-repair-agent process-failure --workflow-run-id 123456 --repository owner/repo
```

## Dagger Functions

The agent exposes the following Dagger functions:

### `health_check() -> str`
Returns the health status of the agent.

### `validate_python_environment(source: Directory, python_version: str) -> Container`
Validates Python environment setup for testing.

### `run_tests(source: Directory, python_version: str, test_command: str) -> str`
Runs tests in a containerized environment.

### `run_quality_checks(source: Directory, python_version: str) -> str`
Runs quality checks (ruff, mypy) in a containerized environment.

### `validate_fix(source: Directory, python_version: str, test_type: str) -> str`
Validates a fix by running specific test types:
- `unit`: Unit tests with coverage
- `integration`: Integration tests with timeout
- `quality`: Ruff and mypy checks
- `all`: All tests with coverage

### `process_workflow_failure(github_token: Secret, deepseek_api_key: Secret, workflow_run_id: str, repository: str) -> str`
Processes a GitHub workflow failure (placeholder for future implementation).

### `create_test_environment(python_versions: List[str]) -> List[Container]`
Creates test environments for multiple Python versions.

## Configuration

The agent can be configured through environment variables or a `.env` file:

### GitHub Configuration
- `GITHUB_TOKEN`: Personal access token for GitHub API
- `GITHUB_APP_ID`: GitHub App ID (alternative to token)
- `GITHUB_PRIVATE_KEY`: GitHub App private key
- `GITHUB_WEBHOOK_SECRET`: Webhook secret for signature validation

### DeepSeek API Configuration
- `DEEPSEEK_API_KEY`: API key for DeepSeek service
- `DEEPSEEK_MODEL`: Model to use (default: deepseek-coder)
- `DEEPSEEK_MAX_TOKENS`: Maximum tokens per request (default: 4000)
- `DEEPSEEK_TEMPERATURE`: Temperature for generation (default: 0.1)

### Agent Behavior
- `ENABLED_FIX_TYPES`: Comma-separated list of fix types to enable
- `PYTHON_VERSIONS`: Comma-separated list of Python versions to test
- `MAX_CONCURRENT_FIXES`: Maximum number of concurrent fix attempts
- `COVERAGE_THRESHOLD`: Minimum coverage percentage required

### Logging
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `LOG_FORMAT`: Log format (json or console)

## Development

### Running Tests

```bash
# Run unit tests
dagger call validate-fix --test-type unit

# Run integration tests
dagger call validate-fix --test-type integration

# Run all tests
dagger call validate-fix --test-type all
```

### Code Quality

```bash
# Run quality checks
dagger call run-quality-checks --source .

# Or using the CLI
dagger-test-repair-agent quality
```

### Adding New Dagger Functions

1. Add the function to `src/character_music_mcp/main.py` with the `@function` decorator
2. Update the README with documentation
3. Add tests for the new function

## Architecture

The agent is built using:

- **Dagger.io**: For containerized, reproducible operations
- **Structlog**: For structured logging
- **Pydantic**: For data validation and configuration
- **Click**: For CLI interface
- **httpx**: For HTTP client operations
- **PyGithub**: For GitHub API integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run quality checks: `dagger call run-quality-checks --source .`
6. Submit a pull request

## License

Apache 2.0 License - see LICENSE file for details.