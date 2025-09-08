"""Tests for GitHub context handling in Dagger functions"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import dagger

from character_music_mcp.main import DaggerTestRepairAgent


class TestGitHubContextHandling:
    """Test GitHub context handling functionality"""

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
    def mock_deepseek_api_key(self):
        """Mock DeepSeek API key secret"""
        mock_secret = MagicMock(spec=dagger.Secret)
        return mock_secret

    @pytest.fixture
    def mock_source_directory(self):
        """Mock source directory"""
        mock_directory = MagicMock(spec=dagger.Directory)
        return mock_directory

    @pytest.fixture
    def sample_workflow_data(self):
        """Sample workflow data for testing"""
        return {
            "id": 12345,
            "conclusion": "failure",
            "jobs": [
                {
                    "id": 67890,
                    "name": "Test Suite",
                    "conclusion": "failure",
                    "steps": [
                        {
                            "name": "Run unit tests",
                            "conclusion": "failure"
                        }
                    ]
                }
            ]
        }

    def test_failure_detection_script_generation(self, agent):
        """Test that failure detection script is properly generated"""
        script = agent._get_failure_detection_script()
        
        assert "detect_failures" in script
        assert "GITHUB_TOKEN" in script
        assert "WORKFLOW_RUN_ID" in script
        assert "httpx.AsyncClient" in script
        assert "has-failures" in script
        assert "failure-types" in script

    def test_log_fetching_script_generation(self, agent):
        """Test that log fetching script is properly generated"""
        script = agent._get_log_fetching_script()
        
        assert "fetch_logs" in script
        assert "GITHUB_TOKEN" in script
        assert "WORKFLOW_RUN_ID" in script
        assert "jobs" in script
        assert "logs" in script

    def test_analysis_and_fix_script_generation(self, agent):
        """Test that analysis and fix script is properly generated"""
        script = agent._get_analysis_and_fix_script()
        
        assert "analyze_and_fix" in script
        assert "DEEPSEEK_API_KEY" in script
        assert "FAILURE_TYPE" in script
        assert "fix-generated" in script
        assert "fix-validation" in script

    def test_pr_creation_script_generation(self, agent):
        """Test that PR creation script is properly generated"""
        script = agent._get_pr_creation_script()
        
        assert "create_pr" in script
        assert "GITHUB_TOKEN" in script
        assert "FIX_DATA" in script
        assert "pr-created" in script
        assert "pr-url" in script

    def test_fix_validation_script_generation(self, agent):
        """Test that fix validation script is properly generated"""
        script = agent._get_fix_validation_script()
        
        assert "validate_fixes" in script
        assert "pytest" in script
        assert "unit_tests" in script
        assert "integration_tests" in script
        assert "quality_checks" in script
        assert "overall_status" in script

    def test_report_generation_script_generation(self, agent):
        """Test that report generation script is properly generated"""
        script = agent._get_report_generation_script()
        
        assert "generate_report" in script
        assert "WORKFLOW_RUN_ID" in script
        assert "timestamp" in script
        assert "summary" in script
        assert "report-generated" in script

    def test_cleanup_script_generation(self, agent):
        """Test that cleanup script is properly generated"""
        script = agent._get_cleanup_script()
        
        assert "cleanup" in script
        assert "REPOSITORY" in script
        assert "cleanup_completed" in script

    @patch('dagger.dag')
    async def test_detect_failures_function(self, mock_dag, agent, mock_github_token):
        """Test the detect_failures Dagger function"""
        # Mock the container chain
        mock_container = MagicMock()
        mock_container.from_.return_value = mock_container
        mock_container.with_exec.return_value = mock_container
        mock_container.with_secret_variable.return_value = mock_container
        mock_container.with_env_variable.return_value = mock_container
        mock_container.with_new_file.return_value = mock_container
        mock_container.stdout.return_value = '{"has-failures": "true", "failure-types": ["unit-tests"]}'
        
        mock_dag.container.return_value = mock_container
        
        result = await agent.detect_failures(
            github_token=mock_github_token,
            repository="test/repo",
            workflow_run_id="12345"
        )
        
        assert result == '{"has-failures": "true", "failure-types": ["unit-tests"]}'
        mock_container.from_.assert_called_with("python:3.10-slim")
        mock_container.with_secret_variable.assert_called_with("GITHUB_TOKEN", mock_github_token)

    @patch('dagger.dag')
    async def test_fetch_workflow_logs_function(self, mock_dag, agent, mock_github_token):
        """Test the fetch_workflow_logs Dagger function"""
        # Mock the container chain
        mock_container = MagicMock()
        mock_container.from_.return_value = mock_container
        mock_container.with_exec.return_value = mock_container
        mock_container.with_secret_variable.return_value = mock_container
        mock_container.with_env_variable.return_value = mock_container
        mock_container.with_new_file.return_value = mock_container
        mock_container.stdout.return_value = '{"Test Suite": "test log content"}'
        
        mock_dag.container.return_value = mock_container
        
        result = await agent.fetch_workflow_logs(
            github_token=mock_github_token,
            repository="test/repo",
            workflow_run_id="12345",
            job_name="Test Suite"
        )
        
        assert result == '{"Test Suite": "test log content"}'
        mock_container.with_env_variable.assert_any_call("JOB_NAME", "Test Suite")

    @patch('dagger.dag')
    async def test_analyze_and_fix_failure_function(
        self, 
        mock_dag, 
        agent, 
        mock_github_token, 
        mock_deepseek_api_key,
        mock_source_directory
    ):
        """Test the analyze_and_fix_failure Dagger function"""
        # Mock the container chain
        mock_container = MagicMock()
        mock_container.from_.return_value = mock_container
        mock_container.with_exec.return_value = mock_container
        mock_container.with_directory.return_value = mock_container
        mock_container.with_workdir.return_value = mock_container
        mock_container.with_secret_variable.return_value = mock_container
        mock_container.with_env_variable.return_value = mock_container
        mock_container.with_new_file.return_value = mock_container
        mock_container.stdout.return_value = '{"fix-generated": "true", "fix-validation": "passed"}'
        
        mock_dag.container.return_value = mock_container
        
        result = await agent.analyze_and_fix_failure(
            github_token=mock_github_token,
            deepseek_api_key=mock_deepseek_api_key,
            repository="test/repo",
            workflow_run_id="12345",
            python_version="3.10",
            failure_type="unit-tests",
            source=mock_source_directory
        )
        
        assert result == '{"fix-generated": "true", "fix-validation": "passed"}'
        mock_container.from_.assert_called_with("python:3.10-slim")
        mock_container.with_secret_variable.assert_any_call("DEEPSEEK_API_KEY", mock_deepseek_api_key)

    @patch('dagger.dag')
    async def test_create_fix_pull_request_function(
        self, 
        mock_dag, 
        agent, 
        mock_github_token,
        mock_source_directory
    ):
        """Test the create_fix_pull_request Dagger function"""
        # Mock the container chain
        mock_container = MagicMock()
        mock_container.from_.return_value = mock_container
        mock_container.with_exec.return_value = mock_container
        mock_container.with_directory.return_value = mock_container
        mock_container.with_workdir.return_value = mock_container
        mock_container.with_secret_variable.return_value = mock_container
        mock_container.with_env_variable.return_value = mock_container
        mock_container.with_new_file.return_value = mock_container
        mock_container.stdout.return_value = '{"pr-created": "true", "pr-url": "https://github.com/test/repo/pull/123"}'
        
        mock_dag.container.return_value = mock_container
        
        fix_data = json.dumps({"type": "unit-test-fix", "files": ["test_file.py"]})
        
        result = await agent.create_fix_pull_request(
            github_token=mock_github_token,
            repository="test/repo",
            fix_data=fix_data,
            source=mock_source_directory
        )
        
        assert result == '{"pr-created": "true", "pr-url": "https://github.com/test/repo/pull/123"}'
        mock_container.with_env_variable.assert_any_call("FIX_DATA", fix_data)

    @patch('dagger.dag')
    async def test_validate_all_fixes_function(
        self, 
        mock_dag, 
        agent, 
        mock_github_token,
        mock_source_directory
    ):
        """Test the validate_all_fixes Dagger function"""
        # Mock the container chain
        mock_container = MagicMock()
        mock_container.from_.return_value = mock_container
        mock_container.with_directory.return_value = mock_container
        mock_container.with_workdir.return_value = mock_container
        mock_container.with_exec.return_value = mock_container
        mock_container.with_secret_variable.return_value = mock_container
        mock_container.with_env_variable.return_value = mock_container
        mock_container.with_new_file.return_value = mock_container
        mock_container.stdout.return_value = '{"overall_status": "passed", "unit_tests": "passed"}'
        
        mock_dag.container.return_value = mock_container
        
        result = await agent.validate_all_fixes(
            github_token=mock_github_token,
            repository="test/repo",
            python_version="3.10",
            source=mock_source_directory
        )
        
        assert result == '{"overall_status": "passed", "unit_tests": "passed"}'
        mock_container.from_.assert_called_with("python:3.10")

    @patch('dagger.dag')
    async def test_generate_agent_report_function(self, mock_dag, agent, mock_github_token):
        """Test the generate_agent_report Dagger function"""
        # Mock the container chain
        mock_container = MagicMock()
        mock_container.from_.return_value = mock_container
        mock_container.with_exec.return_value = mock_container
        mock_container.with_secret_variable.return_value = mock_container
        mock_container.with_env_variable.return_value = mock_container
        mock_container.with_new_file.return_value = mock_container
        mock_container.stdout.return_value = '{"report-generated": "true", "summary": "Report generated"}'
        
        mock_dag.container.return_value = mock_container
        
        result = await agent.generate_agent_report(
            github_token=mock_github_token,
            repository="test/repo",
            workflow_run_id="12345",
            has_failures="true",
            analyze_result="success",
            validate_result="success"
        )
        
        assert result == '{"report-generated": "true", "summary": "Report generated"}'
        mock_container.with_env_variable.assert_any_call("HAS_FAILURES", "true")

    @patch('dagger.dag')
    async def test_cleanup_agent_resources_function(self, mock_dag, agent, mock_github_token):
        """Test the cleanup_agent_resources Dagger function"""
        # Mock the container chain
        mock_container = MagicMock()
        mock_container.from_.return_value = mock_container
        mock_container.with_exec.return_value = mock_container
        mock_container.with_secret_variable.return_value = mock_container
        mock_container.with_env_variable.return_value = mock_container
        mock_container.with_new_file.return_value = mock_container
        mock_container.stdout.return_value = '{"cleanup_completed": "true"}'
        
        mock_dag.container.return_value = mock_container
        
        result = await agent.cleanup_agent_resources(
            github_token=mock_github_token,
            repository="test/repo"
        )
        
        assert result == '{"cleanup_completed": "true"}'
        mock_container.with_env_variable.assert_called_with("REPOSITORY", "test/repo")

    def test_github_context_parameter_validation(self, agent):
        """Test that GitHub context parameters are properly validated"""
        # Test that all required parameters are present in function signatures
        import inspect
        
        # Check detect_failures function
        sig = inspect.signature(agent.detect_failures)
        assert 'github_token' in sig.parameters
        assert 'repository' in sig.parameters
        assert 'workflow_run_id' in sig.parameters
        
        # Check analyze_and_fix_failure function
        sig = inspect.signature(agent.analyze_and_fix_failure)
        assert 'github_token' in sig.parameters
        assert 'deepseek_api_key' in sig.parameters
        assert 'repository' in sig.parameters
        assert 'workflow_run_id' in sig.parameters
        assert 'python_version' in sig.parameters
        assert 'failure_type' in sig.parameters
        assert 'source' in sig.parameters

    def test_script_error_handling(self, agent):
        """Test that generated scripts include proper error handling"""
        scripts = [
            agent._get_failure_detection_script(),
            agent._get_log_fetching_script(),
            agent._get_analysis_and_fix_script(),
            agent._get_pr_creation_script(),
            agent._get_fix_validation_script(),
            agent._get_report_generation_script(),
            agent._get_cleanup_script()
        ]
        
        for script in scripts:
            # Check that scripts have basic error handling structure
            assert "try:" in script or "except" in script or "if __name__" in script
            # Check that scripts produce JSON output
            assert "json" in script
            assert "print" in script

    def test_github_api_integration_patterns(self, agent):
        """Test that GitHub API integration follows proper patterns"""
        detection_script = agent._get_failure_detection_script()
        log_script = agent._get_log_fetching_script()
        
        # Check for proper GitHub API usage patterns
        for script in [detection_script, log_script]:
            assert "https://api.github.com" in script
            assert "Authorization" in script
            assert "application/vnd.github.v3+json" in script
            assert "httpx.AsyncClient" in script

    def test_deepseek_api_integration_pattern(self, agent):
        """Test that DeepSeek API integration is properly structured"""
        analysis_script = agent._get_analysis_and_fix_script()
        
        # Check for DeepSeek API key handling
        assert "DEEPSEEK_API_KEY" in analysis_script
        assert "deepseek_api_key" in analysis_script
        
        # Note: Actual DeepSeek API integration will be implemented in later tasks
        # This test ensures the structure is in place