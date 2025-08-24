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
import sys
import os
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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