"""Dagger Test Repair Agent

An automated system that monitors GitHub Actions workflows, detects test failures,
analyzes them using AI, generates fixes, and creates pull requests.

This module provides Dagger functions for:
- Running tests in containerized environments
- Validating fixes across multiple Python versions
- Processing GitHub workflow failures
- Running quality checks and security scans

The agent integrates with GitHub Actions, DeepSeek API, and uses Dagger.io
for reproducible containerized operations.
"""

from .main import DaggerTestRepairAgent
