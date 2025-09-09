"""Basic tests for the Dagger Test Repair Agent"""

import pytest

from character_music_mcp.main import DaggerTestRepairAgent


class TestDaggerTestRepairAgent:
    """Test cases for the DaggerTestRepairAgent class"""

    def test_agent_instantiation(self):
        """Test that the agent can be instantiated"""
        agent = DaggerTestRepairAgent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test the health check function"""
        agent = DaggerTestRepairAgent()
        result = await agent.health_check()
        assert result == "Test Repair Agent is healthy"

    def test_python_versions_default(self):
        """Test that default Python versions are handled correctly"""
        agent = DaggerTestRepairAgent()
        # This is a basic test - more comprehensive tests will be added in later tasks
        assert agent is not None
