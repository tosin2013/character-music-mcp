#!/usr/bin/env python3
"""
Pytest Configuration and Fixtures

Provides shared fixtures for all test modules including mock contexts,
test data, and common test utilities.
"""

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

import asyncio
import os
import sys

# Add the project root to Python path
from pathlib import Path

project_root = Path(__file__).parent.parent
project_root_str = str(project_root.resolve())

# Ensure project root is in Python path
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

# Also add to PYTHONPATH environment variable
os.environ['PYTHONPATH'] = project_root_str + ':' + os.environ.get('PYTHONPATH', '')

# Debug: Print path information for CI debugging
if os.environ.get('CI'):
    print(f"Project root: {project_root_str}")
    print(f"Python path: {sys.path[:3]}...")  # First 3 entries
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")

from tests.fixtures.mock_contexts import MockContext, create_mock_context
from tests.fixtures.test_data import TestDataManager, test_data_manager

if PYTEST_AVAILABLE:
    @pytest.fixture
    def ctx() -> MockContext:
        """Create a basic mock context for testing"""
        return create_mock_context("basic", session_id="pytest_session")


    @pytest.fixture
    def data_manager() -> TestDataManager:
        """Provide test data manager"""
        return test_data_manager


    @pytest.fixture
    def mock_ctx() -> MockContext:
        """Alternative name for ctx fixture"""
        return create_mock_context("basic", session_id="pytest_mock_session")


    @pytest.fixture
    def performance_ctx() -> MockContext:
        """Create a performance mock context for testing"""
        return create_mock_context("performance", session_id="pytest_performance_session")


    @pytest.fixture
    def batch_ctx() -> MockContext:
        """Create a batch mock context for testing"""
        return create_mock_context("batch", session_id="pytest_batch_session")


    @pytest.fixture
    def concurrent_ctx() -> MockContext:
        """Create a concurrent mock context for testing"""
        return create_mock_context("concurrent", session_id="pytest_concurrent_session")


    @pytest.fixture(scope="session")
    def event_loop():
        """Create an instance of the default event loop for the test session."""
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()


    # Configuration for async tests
    pytest_plugins = ['pytest_asyncio']

else:
    # Fallback functions when pytest is not available
    def ctx() -> MockContext:
        """Create a basic mock context for testing"""
        return create_mock_context("basic", session_id="fallback_session")

    def data_manager() -> TestDataManager:
        """Provide test data manager"""
        return test_data_manager
