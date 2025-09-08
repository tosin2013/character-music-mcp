"""Tests for PR creation and management Dagger functions"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import dagger

from character_music_mcp.main import DaggerTestRepairAgent


class TestPRCreationAndManagement:
    """Test PR creation and management functionality"""

    @pytest.fixture
    def agent(self):
        """Create a DaggerTestRepairAgent instance for testing"""
        return DaggerTestRepairAgent()

    @pytest.fixture
    def mock_github_token(self):
        """Mock GitHub token secret"""
        mock_secret = MagicMock(spec=dagger.Secret)
        return mock_secret

    @pytest.fixture
    def mock_source_directory(self):
        """Mock source directory"""
        mock_directory = MagicMock(spec=dagger.Directory)
        return mock_directory

    @pytest.fixture
    def sample_fix_data(self):
        """Sample fix data for testing"""
        return {
            "failure_type": "unit-tests",
            "workflow_run_id": "12345",
            "python_version": "3.10",
            "files_changed": ["test_example.py"],
            "fix_description": "Fixed assertion error in unit test"
        }

    def test_pr_creation_script_generation(self, agent):
        """Test that PR creation script is properly generated"""
        script = agent._get_pr_creation_script()
        
        assert "create_pr" in script
        assert "check_existing_pr" in script
        assert "generate_branch_name" in script
        assert "create_branch" in script
        assert "apply_fix_changes" in script
        assert "generate_pr_data" in script
        assert "add_pr_labels" in script
        assert "GITHUB_TOKEN" in script
        assert "FIX_DATA" in script

    def test_label_management_script_generation(self, agent):
        """Test that label management script is properly generated"""
        script = agent._get_label_management_script()
        
        assert "manage_labels" in script
        assert "ACTION" in script
        assert "LABELS" in script
        assert "add" in script
        assert "remove" in script
        assert "replace" in script

    def test_conflict_detection_script_generation(self, agent):
        """Test that conflict detection script is properly generated"""
        script = agent._get_conflict_detection_script()
        
        assert "check_conflicts" in script
        assert "mergeable" in script
        assert "mergeable_state" in script
        assert "has_conflicts" in script

    def test_description_update_script_generation(self, agent):
        """Test that description update script is properly generated"""
        script = agent._get_description_update_script()
        
        assert "update_description" in script
        assert "DESCRIPTION_UPDATE" in script
        assert "APPEND" in script
        assert "current_body" in script

    def test_outdated_pr_cleanup_script_generation(self, agent):
        """Test that outdated PR cleanup script is properly generated"""
        script = agent._get_outdated_pr_cleanup_script()
        
        assert "close_outdated_prs" in script
        assert "MAX_AGE_DAYS" in script
        assert "automated-fix" in script
        assert "cutoff_date" in script

    @patch('dagger.dag')
    async def test_manage_pr_labels_function(self, mock_dag, agent, mock_github_token):
        """Test the manage_pr_labels Dagger function"""
        # Mock the container chain
        mock_container = MagicMock()
        mock_container.from_.return_value = mock_container
        mock_container.with_exec.return_value = mock_container
        mock_container.with_secret_variable.return_value = mock_container
        mock_container.with_env_variable.return_value = mock_container
        mock_container.with_new_file.return_value = mock_container
        mock_container.stdout.return_value = '{"success": true, "action": "add", "labels": ["automated-fix"]}'
        
        mock_dag.container.return_value = mock_container
        
        result = await agent.manage_pr_labels(
            github_token=mock_github_token,
            repository="test/repo",
            pr_number="123",
            action="add",
            labels=["automated-fix", "test-repair"]
        )
        
        assert result == '{"success": true, "action": "add", "labels": ["automated-fix"]}'
        mock_container.with_env_variable.assert_any_call("ACTION", "add")

    @patch('dagger.dag')
    async def test_check_pr_conflicts_function(self, mock_dag, agent, mock_github_token):
        """Test the check_pr_conflicts Dagger function"""
        # Mock the container chain
        mock_container = MagicMock()
        mock_container.from_.return_value = mock_container
        mock_container.with_exec.return_value = mock_container
        mock_container.with_secret_variable.return_value = mock_container
        mock_container.with_env_variable.return_value = mock_container
        mock_container.with_new_file.return_value = mock_container
        mock_container.stdout.return_value = '{"has_conflicts": false, "mergeable": true}'
        
        mock_dag.container.return_value = mock_container
        
        result = await agent.check_pr_conflicts(
            github_token=mock_github_token,
            repository="test/repo",
            pr_number="123"
        )
        
        assert result == '{"has_conflicts": false, "mergeable": true}'
        mock_container.with_env_variable.assert_any_call("PR_NUMBER", "123")

    @patch('dagger.dag')
    async def test_update_pr_description_function(self, mock_dag, agent, mock_github_token):
        """Test the update_pr_description Dagger function"""
        # Mock the container chain
        mock_container = MagicMock()
        mock_container.from_.return_value = mock_container
        mock_container.with_exec.return_value = mock_container
        mock_container.with_secret_variable.return_value = mock_container
        mock_container.with_env_variable.return_value = mock_container
        mock_container.with_new_file.return_value = mock_container
        mock_container.stdout.return_value = '{"success": true, "append": true}'
        
        mock_dag.container.return_value = mock_container
        
        result = await agent.update_pr_description(
            github_token=mock_github_token,
            repository="test/repo",
            pr_number="123",
            description_update="Additional validation results",
            append=True
        )
        
        assert result == '{"success": true, "append": true}'
        mock_container.with_env_variable.assert_any_call("APPEND", "true")

    @patch('dagger.dag')
    async def test_close_outdated_prs_function(self, mock_dag, agent, mock_github_token):
        """Test the close_outdated_prs Dagger function"""
        # Mock the container chain
        mock_container = MagicMock()
        mock_container.from_.return_value = mock_container
        mock_container.with_exec.return_value = mock_container
        mock_container.with_secret_variable.return_value = mock_container
        mock_container.with_env_variable.return_value = mock_container
        mock_container.with_new_file.return_value = mock_container
        mock_container.stdout.return_value = '{"success": true, "total_closed": 2}'
        
        mock_dag.container.return_value = mock_container
        
        result = await agent.close_outdated_prs(
            github_token=mock_github_token,
            repository="test/repo",
            max_age_days=7
        )
        
        assert result == '{"success": true, "total_closed": 2}'
        mock_container.with_env_variable.assert_any_call("MAX_AGE_DAYS", "7")

    def test_pr_creation_workflow_components(self, agent):
        """Test that PR creation script includes all necessary workflow components"""
        script = agent._get_pr_creation_script()
        
        # Check for GitHub API integration patterns
        assert "https://api.github.com/repos" in script
        assert "Authorization" in script
        assert "application/vnd.github.v3+json" in script
        
        # Check for branch management
        assert "refs/heads/" in script
        assert "default_branch" in script
        
        # Check for PR data generation
        assert "title" in script
        assert "body" in script
        assert "head" in script
        assert "base" in script
        
        # Check for label management
        assert "automated-fix" in script
        assert "test-repair" in script
        assert "priority-" in script

    def test_pr_conflict_detection_components(self, agent):
        """Test that conflict detection includes proper GitHub API calls"""
        script = agent._get_conflict_detection_script()
        
        # Check for proper PR status checking
        assert "mergeable" in script
        assert "mergeable_state" in script
        assert "rebaseable" in script
        assert "head_sha" in script
        assert "base_sha" in script

    def test_label_management_actions(self, agent):
        """Test that label management supports all required actions"""
        script = agent._get_label_management_script()
        
        # Check for all supported actions
        assert 'action == "add"' in script
        assert 'action == "remove"' in script
        assert 'action == "replace"' in script
        
        # Check for proper API endpoints
        assert "/labels" in script
        assert "POST" in script or "post" in script
        assert "DELETE" in script or "delete" in script
        assert "PUT" in script or "put" in script

    def test_pr_description_update_functionality(self, agent):
        """Test that PR description update handles both append and replace modes"""
        script = agent._get_description_update_script()
        
        # Check for append functionality
        assert "append" in script
        assert "current_body" in script
        assert "new_body" in script
        
        # Check for timestamp addition
        assert "Updated:" in script
        assert "datetime" in script

    def test_outdated_pr_cleanup_logic(self, agent):
        """Test that outdated PR cleanup has proper age filtering"""
        script = agent._get_outdated_pr_cleanup_script()
        
        # Check for age calculation
        assert "timedelta" in script
        assert "cutoff_date" in script
        assert "created_at" in script
        
        # Check for automated fix filtering
        assert "automated-fix" in script
        assert "labels" in script
        
        # Check for proper closure message
        assert "Automatically closed" in script