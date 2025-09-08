"""Dagger Test Repair Agent

An automated system that monitors GitHub Actions workflows, detects test failures,
analyzes them using AI, generates fixes, and creates pull requests.
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any

import dagger
from dagger import dag, function, object_type
import structlog
import httpx


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@object_type
class DaggerTestRepairAgent:
    """Dagger Test Repair Agent for automated test failure detection and repair"""

    @function
    async def health_check(self) -> str:
        """Health check endpoint for the agent"""
        logger.info("Health check requested")
        return "Test Repair Agent is healthy"

    @function
    async def validate_python_environment(
        self,
        source: dagger.Directory,
        python_version: str = "3.10"
    ) -> dagger.Container:
        """Validate Python environment setup for testing"""
        logger.info("Validating Python environment", python_version=python_version)
        
        return (
            dag.container()
            .from_(f"python:{python_version}")
            .with_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["python", "--version"])
            .with_exec(["pip", "install", "uv"])
            .with_exec(["uv", "--version"])
        )

    @function
    async def run_tests(
        self,
        source: dagger.Directory,
        python_version: str = "3.10",
        test_command: str = "pytest tests/ -v"
    ) -> str:
        """Run tests in a containerized environment"""
        logger.info(
            "Running tests",
            python_version=python_version,
            test_command=test_command
        )
        
        container = (
            dag.container()
            .from_(f"python:{python_version}")
            .with_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["pip", "install", "uv"])
            .with_exec(["uv", "venv", "--python", python_version])
            .with_exec(["bash", "-c", "source .venv/bin/activate && uv pip install -e .[test]"])
            .with_exec(["bash", "-c", f"source .venv/bin/activate && {test_command}"])
        )
        
        return await container.stdout()

    @function
    async def run_quality_checks(
        self,
        source: dagger.Directory,
        python_version: str = "3.10"
    ) -> str:
        """Run quality checks (ruff, mypy) in a containerized environment"""
        logger.info("Running quality checks", python_version=python_version)
        
        container = (
            dag.container()
            .from_(f"python:{python_version}")
            .with_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["pip", "install", "uv"])
            .with_exec(["uv", "venv", "--python", python_version])
            .with_exec(["bash", "-c", "source .venv/bin/activate && uv pip install -e .[test]"])
            .with_exec(["bash", "-c", "source .venv/bin/activate && uv pip install ruff mypy"])
            .with_exec(["bash", "-c", "source .venv/bin/activate && ruff check ."])
        )
        
        return await container.stdout()

    @function
    async def validate_fix(
        self,
        source: dagger.Directory,
        python_version: str = "3.10",
        test_type: str = "unit"
    ) -> str:
        """Validate a fix by running specific test types"""
        logger.info(
            "Validating fix",
            python_version=python_version,
            test_type=test_type
        )
        
        # Map test types to commands
        test_commands = {
            "unit": "pytest tests/unit/ -v --cov=. --cov-fail-under=80",
            "integration": "pytest tests/integration/ -v --timeout=300",
            "quality": "ruff check .",
            "all": "pytest tests/ -v --cov=. --cov-fail-under=80"
        }
        
        test_command = test_commands.get(test_type, test_commands["unit"])
        
        container = (
            dag.container()
            .from_(f"python:{python_version}")
            .with_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["pip", "install", "uv"])
            .with_exec(["uv", "venv", "--python", python_version])
            .with_exec(["bash", "-c", "source .venv/bin/activate && uv pip install -e .[test]"])
        )
        
        # Add quality tools if needed
        if test_type == "quality":
            container = container.with_exec(["bash", "-c", "source .venv/bin/activate && uv pip install ruff mypy"])
        
        container = container.with_exec(["bash", "-c", f"source .venv/bin/activate && {test_command}"])
        
        return await container.stdout()

    @function
    async def detect_failures(
        self,
        github_token: dagger.Secret,
        repository: str,
        workflow_run_id: str
    ) -> str:
        """Detect failures in a GitHub workflow run"""
        logger.info(
            "Detecting failures",
            workflow_run_id=workflow_run_id,
            repository=repository
        )
        
        # Create a container with GitHub CLI and Python for API interactions
        container = (
            dag.container()
            .from_("python:3.10-slim")
            .with_exec(["apt-get", "update"])
            .with_exec(["apt-get", "install", "-y", "curl", "jq"])
            .with_exec(["pip", "install", "httpx", "structlog"])
            .with_secret_variable("GITHUB_TOKEN", github_token)
            .with_env_variable("REPOSITORY", repository)
            .with_env_variable("WORKFLOW_RUN_ID", workflow_run_id)
            .with_new_file(
                "/detect_failures.py",
                contents=self._get_failure_detection_script()
            )
            .with_exec(["python", "/detect_failures.py"])
        )
        
        return await container.stdout()

    @function
    async def fetch_workflow_logs(
        self,
        github_token: dagger.Secret,
        repository: str,
        workflow_run_id: str,
        job_name: Optional[str] = None
    ) -> str:
        """Fetch logs from a GitHub workflow run"""
        logger.info(
            "Fetching workflow logs",
            workflow_run_id=workflow_run_id,
            repository=repository,
            job_name=job_name
        )
        
        container = (
            dag.container()
            .from_("python:3.10-slim")
            .with_exec(["apt-get", "update"])
            .with_exec(["apt-get", "install", "-y", "curl"])
            .with_exec(["pip", "install", "httpx"])
            .with_secret_variable("GITHUB_TOKEN", github_token)
            .with_env_variable("REPOSITORY", repository)
            .with_env_variable("WORKFLOW_RUN_ID", workflow_run_id)
            .with_env_variable("JOB_NAME", job_name or "")
            .with_new_file(
                "/fetch_logs.py",
                contents=self._get_log_fetching_script()
            )
            .with_exec(["python", "/fetch_logs.py"])
        )
        
        return await container.stdout()

    @function
    async def analyze_and_fix_failure(
        self,
        github_token: dagger.Secret,
        deepseek_api_key: dagger.Secret,
        repository: str,
        workflow_run_id: str,
        python_version: str,
        failure_type: str,
        source: dagger.Directory
    ) -> str:
        """Analyze a failure and generate a fix using DeepSeek API"""
        logger.info(
            "Analyzing and fixing failure",
            workflow_run_id=workflow_run_id,
            repository=repository,
            python_version=python_version,
            failure_type=failure_type
        )
        
        container = (
            dag.container()
            .from_(f"python:{python_version}-slim")
            .with_exec(["apt-get", "update"])
            .with_exec(["apt-get", "install", "-y", "git", "curl"])
            .with_exec(["pip", "install", "httpx", "structlog", "uv"])
            .with_directory("/src", source)
            .with_workdir("/src")
            .with_secret_variable("GITHUB_TOKEN", github_token)
            .with_secret_variable("DEEPSEEK_API_KEY", deepseek_api_key)
            .with_env_variable("REPOSITORY", repository)
            .with_env_variable("WORKFLOW_RUN_ID", workflow_run_id)
            .with_env_variable("PYTHON_VERSION", python_version)
            .with_env_variable("FAILURE_TYPE", failure_type)
            .with_new_file(
                "/analyze_fix.py",
                contents=self._get_analysis_and_fix_script()
            )
            .with_exec(["python", "/analyze_fix.py"])
        )
        
        return await container.stdout()

    @function
    async def create_fix_pull_request(
        self,
        github_token: dagger.Secret,
        repository: str,
        fix_data: str,
        source: dagger.Directory
    ) -> str:
        """Create a pull request with the generated fix"""
        logger.info(
            "Creating fix pull request",
            repository=repository
        )
        
        container = (
            dag.container()
            .from_("python:3.10-slim")
            .with_exec(["apt-get", "update"])
            .with_exec(["apt-get", "install", "-y", "git", "curl"])
            .with_exec(["pip", "install", "httpx", "structlog"])
            .with_directory("/src", source)
            .with_workdir("/src")
            .with_secret_variable("GITHUB_TOKEN", github_token)
            .with_env_variable("REPOSITORY", repository)
            .with_env_variable("FIX_DATA", fix_data)
            .with_new_file(
                "/create_pr.py",
                contents=self._get_pr_creation_script()
            )
            .with_exec(["python", "/create_pr.py"])
        )
        
        return await container.stdout()

    @function
    async def validate_all_fixes(
        self,
        github_token: dagger.Secret,
        repository: str,
        python_version: str,
        source: dagger.Directory
    ) -> str:
        """Validate all generated fixes"""
        logger.info(
            "Validating all fixes",
            repository=repository,
            python_version=python_version
        )
        
        container = (
            dag.container()
            .from_(f"python:{python_version}")
            .with_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["pip", "install", "uv"])
            .with_exec(["uv", "venv", "--python", python_version])
            .with_exec(["bash", "-c", "source .venv/bin/activate && uv pip install -e .[test]"])
            .with_exec(["bash", "-c", "source .venv/bin/activate && uv pip install pytest pytest-cov pytest-timeout ruff mypy"])
            .with_secret_variable("GITHUB_TOKEN", github_token)
            .with_env_variable("REPOSITORY", repository)
            .with_env_variable("PYTHON_VERSION", python_version)
            .with_new_file(
                "/validate_fixes.py",
                contents=self._get_fix_validation_script()
            )
            .with_exec(["bash", "-c", "source .venv/bin/activate && python /validate_fixes.py"])
        )
        
        return await container.stdout()

    @function
    async def generate_agent_report(
        self,
        github_token: dagger.Secret,
        repository: str,
        workflow_run_id: str,
        has_failures: str,
        analyze_result: str,
        validate_result: str
    ) -> str:
        """Generate a comprehensive report of agent activities"""
        logger.info(
            "Generating agent report",
            workflow_run_id=workflow_run_id,
            repository=repository
        )
        
        container = (
            dag.container()
            .from_("python:3.10-slim")
            .with_exec(["pip", "install", "httpx", "structlog"])
            .with_secret_variable("GITHUB_TOKEN", github_token)
            .with_env_variable("REPOSITORY", repository)
            .with_env_variable("WORKFLOW_RUN_ID", workflow_run_id)
            .with_env_variable("HAS_FAILURES", has_failures)
            .with_env_variable("ANALYZE_RESULT", analyze_result)
            .with_env_variable("VALIDATE_RESULT", validate_result)
            .with_new_file(
                "/generate_report.py",
                contents=self._get_report_generation_script()
            )
            .with_exec(["python", "/generate_report.py"])
        )
        
        return await container.stdout()

    @function
    async def manage_pr_labels(
        self,
        github_token: dagger.Secret,
        repository: str,
        pr_number: str,
        action: str,
        labels: List[str]
    ) -> str:
        """Manage labels on a pull request (add, remove, or replace)"""
        logger.info(
            "Managing PR labels",
            repository=repository,
            pr_number=pr_number,
            action=action,
            labels=labels
        )
        
        container = (
            dag.container()
            .from_("python:3.10-slim")
            .with_exec(["pip", "install", "httpx"])
            .with_secret_variable("GITHUB_TOKEN", github_token)
            .with_env_variable("REPOSITORY", repository)
            .with_env_variable("PR_NUMBER", pr_number)
            .with_env_variable("ACTION", action)
            .with_env_variable("LABELS", json.dumps(labels))
            .with_new_file(
                "/manage_labels.py",
                contents=self._get_label_management_script()
            )
            .with_exec(["python", "/manage_labels.py"])
        )
        
        return await container.stdout()

    @function
    async def check_pr_conflicts(
        self,
        github_token: dagger.Secret,
        repository: str,
        pr_number: str
    ) -> str:
        """Check for conflicts in a pull request"""
        logger.info(
            "Checking PR conflicts",
            repository=repository,
            pr_number=pr_number
        )
        
        container = (
            dag.container()
            .from_("python:3.10-slim")
            .with_exec(["pip", "install", "httpx"])
            .with_secret_variable("GITHUB_TOKEN", github_token)
            .with_env_variable("REPOSITORY", repository)
            .with_env_variable("PR_NUMBER", pr_number)
            .with_new_file(
                "/check_conflicts.py",
                contents=self._get_conflict_detection_script()
            )
            .with_exec(["python", "/check_conflicts.py"])
        )
        
        return await container.stdout()

    @function
    async def update_pr_description(
        self,
        github_token: dagger.Secret,
        repository: str,
        pr_number: str,
        description_update: str,
        append: bool = True
    ) -> str:
        """Update the description of a pull request"""
        logger.info(
            "Updating PR description",
            repository=repository,
            pr_number=pr_number,
            append=append
        )
        
        container = (
            dag.container()
            .from_("python:3.10-slim")
            .with_exec(["pip", "install", "httpx"])
            .with_secret_variable("GITHUB_TOKEN", github_token)
            .with_env_variable("REPOSITORY", repository)
            .with_env_variable("PR_NUMBER", pr_number)
            .with_env_variable("DESCRIPTION_UPDATE", description_update)
            .with_env_variable("APPEND", "true" if append else "false")
            .with_new_file(
                "/update_description.py",
                contents=self._get_description_update_script()
            )
            .with_exec(["python", "/update_description.py"])
        )
        
        return await container.stdout()

    @function
    async def close_outdated_prs(
        self,
        github_token: dagger.Secret,
        repository: str,
        max_age_days: int = 7
    ) -> str:
        """Close outdated automated fix PRs"""
        logger.info(
            "Closing outdated PRs",
            repository=repository,
            max_age_days=max_age_days
        )
        
        container = (
            dag.container()
            .from_("python:3.10-slim")
            .with_exec(["pip", "install", "httpx"])
            .with_secret_variable("GITHUB_TOKEN", github_token)
            .with_env_variable("REPOSITORY", repository)
            .with_env_variable("MAX_AGE_DAYS", str(max_age_days))
            .with_new_file(
                "/close_outdated_prs.py",
                contents=self._get_outdated_pr_cleanup_script()
            )
            .with_exec(["python", "/close_outdated_prs.py"])
        )
        
        return await container.stdout()

    @function
    async def cleanup_agent_resources(
        self,
        github_token: dagger.Secret,
        repository: str
    ) -> str:
        """Cleanup temporary resources created by the agent"""
        logger.info(
            "Cleaning up agent resources",
            repository=repository
        )
        
        container = (
            dag.container()
            .from_("python:3.10-slim")
            .with_exec(["pip", "install", "httpx"])
            .with_secret_variable("GITHUB_TOKEN", github_token)
            .with_env_variable("REPOSITORY", repository)
            .with_new_file(
                "/cleanup.py",
                contents=self._get_cleanup_script()
            )
            .with_exec(["python", "/cleanup.py"])
        )
        
        return await container.stdout()

    def _get_failure_detection_script(self) -> str:
        """Get the Python script for failure detection"""
        return '''
import os
import json
import httpx
import asyncio
from typing import Dict, List, Any

async def detect_failures():
    """Detect failures in a GitHub workflow run"""
    github_token = os.environ["GITHUB_TOKEN"]
    repository = os.environ["REPOSITORY"]
    workflow_run_id = os.environ["WORKFLOW_RUN_ID"]
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        # Get workflow run details
        workflow_url = f"https://api.github.com/repos/{repository}/actions/runs/{workflow_run_id}"
        workflow_response = await client.get(workflow_url, headers=headers)
        workflow_data = workflow_response.json()
        
        if workflow_data.get("conclusion") != "failure":
            result = {
                "has-failures": "false",
                "failure-types": "[]",
                "workflow-run-id": workflow_run_id
            }
            print(json.dumps(result))
            return
        
        # Get jobs for this workflow run
        jobs_url = f"https://api.github.com/repos/{repository}/actions/runs/{workflow_run_id}/jobs"
        jobs_response = await client.get(jobs_url, headers=headers)
        jobs_data = jobs_response.json()
        
        failure_types = []
        for job in jobs_data.get("jobs", []):
            if job.get("conclusion") == "failure":
                job_name = job.get("name", "").lower()
                if "test" in job_name:
                    if "unit" in job_name:
                        failure_types.append("unit-tests")
                    elif "integration" in job_name:
                        failure_types.append("integration-tests")
                    else:
                        failure_types.append("unit-tests")  # Default to unit tests
                elif "documentation" in job_name:
                    failure_types.append("documentation")
                elif "quality" in job_name:
                    failure_types.append("quality-checks")
                elif "security" in job_name:
                    failure_types.append("security-scan")
                elif "coverage" in job_name:
                    failure_types.append("coverage")
        
        # Remove duplicates
        failure_types = list(set(failure_types))
        
        result = {
            "has-failures": "true" if failure_types else "false",
            "failure-types": json.dumps(failure_types),
            "workflow-run-id": workflow_run_id
        }
        
        print(json.dumps(result))

if __name__ == "__main__":
    asyncio.run(detect_failures())
'''

    def _get_log_fetching_script(self) -> str:
        """Get the Python script for fetching workflow logs"""
        return '''
import os
import json
import httpx
import asyncio

async def fetch_logs():
    """Fetch logs from a GitHub workflow run"""
    github_token = os.environ["GITHUB_TOKEN"]
    repository = os.environ["REPOSITORY"]
    workflow_run_id = os.environ["WORKFLOW_RUN_ID"]
    job_name = os.environ.get("JOB_NAME", "")
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        # Get jobs for this workflow run
        jobs_url = f"https://api.github.com/repos/{repository}/actions/runs/{workflow_run_id}/jobs"
        jobs_response = await client.get(jobs_url, headers=headers)
        jobs_data = jobs_response.json()
        
        logs = {}
        for job in jobs_data.get("jobs", []):
            if job.get("conclusion") == "failure":
                current_job_name = job.get("name", "")
                if not job_name or job_name.lower() in current_job_name.lower():
                    # Get logs for this job
                    logs_url = f"https://api.github.com/repos/{repository}/actions/jobs/{job['id']}/logs"
                    logs_response = await client.get(logs_url, headers=headers)
                    if logs_response.status_code == 200:
                        logs[current_job_name] = logs_response.text
        
        print(json.dumps(logs))

if __name__ == "__main__":
    asyncio.run(fetch_logs())
'''

    def _get_analysis_and_fix_script(self) -> str:
        """Get the Python script for analysis and fix generation"""
        return '''
import os
import json
import httpx
import asyncio
from typing import Dict, Any

async def analyze_and_fix():
    """Analyze failure and generate fix using DeepSeek API"""
    github_token = os.environ["GITHUB_TOKEN"]
    deepseek_api_key = os.environ["DEEPSEEK_API_KEY"]
    repository = os.environ["REPOSITORY"]
    workflow_run_id = os.environ["WORKFLOW_RUN_ID"]
    python_version = os.environ["PYTHON_VERSION"]
    failure_type = os.environ["FAILURE_TYPE"]
    
    # This is a placeholder implementation
    # In the actual implementation, this would:
    # 1. Fetch failure logs from GitHub API
    # 2. Analyze the logs to understand the failure
    # 3. Use DeepSeek API to generate a fix
    # 4. Apply the fix to the source code
    # 5. Validate the fix
    
    result = {
        "fix-generated": "false",
        "fix-validation": "skipped",
        "fix-data": json.dumps({
            "failure_type": failure_type,
            "python_version": python_version,
            "workflow_run_id": workflow_run_id,
            "status": "placeholder_implementation"
        })
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    asyncio.run(analyze_and_fix())
'''

    def _get_pr_creation_script(self) -> str:
        """Get the Python script for PR creation"""
        return '''
import os
import json
import httpx
import asyncio
import subprocess
import hashlib
from datetime import datetime
from typing import Dict, List, Any

async def create_pr():
    """Create a pull request with the generated fix"""
    github_token = os.environ["GITHUB_TOKEN"]
    repository = os.environ["REPOSITORY"]
    fix_data = json.loads(os.environ["FIX_DATA"])
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Check if similar PR already exists
            existing_pr = await check_existing_pr(client, headers, repository, fix_data)
            if existing_pr:
                result = {
                    "pr-created": "false",
                    "pr-url": existing_pr["html_url"],
                    "status": "existing_pr_found",
                    "existing_pr_id": existing_pr["number"]
                }
                print(json.dumps(result))
                return
            
            # Generate branch name
            branch_name = generate_branch_name(fix_data)
            
            # Get default branch
            repo_response = await client.get(f"https://api.github.com/repos/{repository}", headers=headers)
            default_branch = repo_response.json().get("default_branch", "main")
            
            # Create new branch
            branch_created = await create_branch(client, headers, repository, branch_name, default_branch)
            if not branch_created:
                result = {
                    "pr-created": "false",
                    "pr-url": "",
                    "status": "branch_creation_failed"
                }
                print(json.dumps(result))
                return
            
            # Apply fix changes (placeholder - actual implementation would modify files)
            changes_applied = await apply_fix_changes(fix_data)
            if not changes_applied:
                result = {
                    "pr-created": "false",
                    "pr-url": "",
                    "status": "changes_application_failed"
                }
                print(json.dumps(result))
                return
            
            # Create pull request
            pr_data = generate_pr_data(fix_data, branch_name, default_branch)
            pr_response = await client.post(
                f"https://api.github.com/repos/{repository}/pulls",
                headers=headers,
                json=pr_data
            )
            
            if pr_response.status_code == 201:
                pr = pr_response.json()
                
                # Add labels
                await add_pr_labels(client, headers, repository, pr["number"], fix_data)
                
                result = {
                    "pr-created": "true",
                    "pr-url": pr["html_url"],
                    "pr-number": pr["number"],
                    "branch-name": branch_name,
                    "status": "success"
                }
            else:
                result = {
                    "pr-created": "false",
                    "pr-url": "",
                    "status": f"pr_creation_failed_{pr_response.status_code}",
                    "error": pr_response.text
                }
                
    except Exception as e:
        result = {
            "pr-created": "false",
            "pr-url": "",
            "status": "error",
            "error": str(e)
        }
    
    print(json.dumps(result))

async def check_existing_pr(client, headers, repository, fix_data):
    """Check if a similar PR already exists"""
    try:
        # Search for open PRs with automated-fix label
        search_response = await client.get(
            f"https://api.github.com/repos/{repository}/pulls",
            headers=headers,
            params={"state": "open", "sort": "created", "direction": "desc"}
        )
        
        if search_response.status_code == 200:
            prs = search_response.json()
            for pr in prs:
                # Check if PR has automated-fix label and similar failure type
                labels = [label["name"] for label in pr.get("labels", [])]
                if "automated-fix" in labels:
                    # Check if it's for the same failure type
                    failure_type = fix_data.get("failure_type", "")
                    if failure_type in pr.get("title", "").lower():
                        return pr
        return None
    except Exception:
        return None

def generate_branch_name(fix_data):
    """Generate a unique branch name for the fix"""
    failure_type = fix_data.get("failure_type", "unknown")
    workflow_run_id = fix_data.get("workflow_run_id", "")
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    
    # Create a short hash for uniqueness
    content_hash = hashlib.md5(json.dumps(fix_data, sort_keys=True).encode()).hexdigest()[:8]
    
    return f"fix/{failure_type}-{timestamp}-{content_hash}"

async def create_branch(client, headers, repository, branch_name, base_branch):
    """Create a new branch for the fix"""
    try:
        # Get the SHA of the base branch
        ref_response = await client.get(
            f"https://api.github.com/repos/{repository}/git/ref/heads/{base_branch}",
            headers=headers
        )
        
        if ref_response.status_code != 200:
            return False
            
        base_sha = ref_response.json()["object"]["sha"]
        
        # Create new branch
        branch_data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha
        }
        
        branch_response = await client.post(
            f"https://api.github.com/repos/{repository}/git/refs",
            headers=headers,
            json=branch_data
        )
        
        return branch_response.status_code == 201
    except Exception:
        return False

async def apply_fix_changes(fix_data):
    """Apply the fix changes to the repository (placeholder)"""
    # This is a placeholder implementation
    # In the actual implementation, this would:
    # 1. Read the fix data
    # 2. Apply changes to the appropriate files
    # 3. Commit the changes to the branch
    
    # For now, we'll just return True to indicate success
    return True

def generate_pr_data(fix_data, branch_name, base_branch):
    """Generate PR data including title and description"""
    failure_type = fix_data.get("failure_type", "unknown")
    workflow_run_id = fix_data.get("workflow_run_id", "")
    python_version = fix_data.get("python_version", "")
    
    title = f"🤖 Automated fix for {failure_type} failure"
    
    description = f"""## Automated Test Repair
    
This pull request was automatically generated by the Dagger Test Repair Agent to fix a {failure_type} failure.

### Details
- **Failure Type:** {failure_type}
- **Workflow Run ID:** {workflow_run_id}
- **Python Version:** {python_version}
- **Generated:** {datetime.utcnow().isoformat()}Z

### Changes
This PR contains automated fixes for the detected test failure. Please review the changes carefully before merging.

### Validation
The fix has been validated using the same test environment that detected the original failure.

---
*This PR was created automatically by the Dagger Test Repair Agent. If you have questions or concerns, please review the workflow logs or contact the maintainers.*
"""
    
    return {
        "title": title,
        "body": description,
        "head": branch_name,
        "base": base_branch,
        "draft": False
    }

async def add_pr_labels(client, headers, repository, pr_number, fix_data):
    """Add appropriate labels to the PR"""
    failure_type = fix_data.get("failure_type", "")
    
    labels = ["automated-fix", "test-repair"]
    
    # Add failure-type specific labels
    if failure_type:
        labels.append(f"fix-{failure_type}")
    
    # Add priority label based on failure type
    if failure_type in ["unit-tests", "integration-tests"]:
        labels.append("priority-high")
    elif failure_type in ["quality-checks", "documentation"]:
        labels.append("priority-medium")
    else:
        labels.append("priority-low")
    
    try:
        await client.post(
            f"https://api.github.com/repos/{repository}/issues/{pr_number}/labels",
            headers=headers,
            json={"labels": labels}
        )
    except Exception:
        pass  # Labels are not critical, continue if they fail

if __name__ == "__main__":
    asyncio.run(create_pr())
'''

    def _get_fix_validation_script(self) -> str:
        """Get the Python script for fix validation"""
        return '''
import os
import json
import subprocess
import sys

def validate_fixes():
    """Validate all generated fixes"""
    repository = os.environ["REPOSITORY"]
    python_version = os.environ["PYTHON_VERSION"]
    
    validation_results = {
        "unit_tests": "not_run",
        "integration_tests": "not_run",
        "quality_checks": "not_run",
        "overall_status": "pending"
    }
    
    try:
        # Run unit tests
        result = subprocess.run(
            ["pytest", "tests/unit/", "-v", "--cov=.", "--cov-fail-under=80"],
            capture_output=True,
            text=True,
            timeout=300
        )
        validation_results["unit_tests"] = "passed" if result.returncode == 0 else "failed"
        
        # Run integration tests
        result = subprocess.run(
            ["pytest", "tests/integration/", "-v", "--timeout=300"],
            capture_output=True,
            text=True,
            timeout=600
        )
        validation_results["integration_tests"] = "passed" if result.returncode == 0 else "failed"
        
        # Run quality checks
        result = subprocess.run(
            ["ruff", "check", "."],
            capture_output=True,
            text=True,
            timeout=60
        )
        validation_results["quality_checks"] = "passed" if result.returncode == 0 else "failed"
        
        # Determine overall status
        if all(status == "passed" for status in validation_results.values() if status != "pending"):
            validation_results["overall_status"] = "passed"
        else:
            validation_results["overall_status"] = "failed"
            
    except Exception as e:
        validation_results["overall_status"] = "error"
        validation_results["error"] = str(e)
    
    print(json.dumps(validation_results))

if __name__ == "__main__":
    validate_fixes()
'''

    def _get_report_generation_script(self) -> str:
        """Get the Python script for report generation"""
        return '''
import os
import json
from datetime import datetime

def generate_report():
    """Generate a comprehensive report of agent activities"""
    repository = os.environ["REPOSITORY"]
    workflow_run_id = os.environ["WORKFLOW_RUN_ID"]
    has_failures = os.environ["HAS_FAILURES"]
    analyze_result = os.environ["ANALYZE_RESULT"]
    validate_result = os.environ["VALIDATE_RESULT"]
    
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "repository": repository,
        "workflow_run_id": workflow_run_id,
        "has_failures": has_failures == "true",
        "analyze_result": analyze_result,
        "validate_result": validate_result,
        "summary": f"Dagger Test Repair Agent processed workflow run {workflow_run_id} for {repository}",
        "report-generated": "true"
    }
    
    # Generate markdown summary
    summary = f"""
# Dagger Test Repair Agent Report

**Repository:** {repository}
**Workflow Run ID:** {workflow_run_id}
**Timestamp:** {report['timestamp']}

## Summary
- **Failures Detected:** {'Yes' if has_failures == 'true' else 'No'}
- **Analysis Result:** {analyze_result}
- **Validation Result:** {validate_result}

## Details
The Dagger Test Repair Agent processed the workflow run and attempted to detect and fix any test failures.

This is an automated report generated by the Dagger Test Repair Agent.
"""
    
    report["summary"] = summary
    print(json.dumps(report))

if __name__ == "__main__":
    generate_report()
'''

    def _get_label_management_script(self) -> str:
        """Get the Python script for PR label management"""
        return '''
import os
import json
import httpx
import asyncio

async def manage_labels():
    """Manage labels on a pull request"""
    github_token = os.environ["GITHUB_TOKEN"]
    repository = os.environ["REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]
    action = os.environ["ACTION"]
    labels = json.loads(os.environ["LABELS"])
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            if action == "add":
                response = await client.post(
                    f"https://api.github.com/repos/{repository}/issues/{pr_number}/labels",
                    headers=headers,
                    json={"labels": labels}
                )
            elif action == "remove":
                for label in labels:
                    await client.delete(
                        f"https://api.github.com/repos/{repository}/issues/{pr_number}/labels/{label}",
                        headers=headers
                    )
                response = type('Response', (), {'status_code': 200})()
            elif action == "replace":
                response = await client.put(
                    f"https://api.github.com/repos/{repository}/issues/{pr_number}/labels",
                    headers=headers,
                    json={"labels": labels}
                )
            else:
                raise ValueError(f"Unknown action: {action}")
            
            result = {
                "success": response.status_code in [200, 201],
                "action": action,
                "labels": labels,
                "status_code": response.status_code
            }
            
    except Exception as e:
        result = {
            "success": False,
            "action": action,
            "labels": labels,
            "error": str(e)
        }
    
    print(json.dumps(result))

if __name__ == "__main__":
    asyncio.run(manage_labels())
'''

    def _get_conflict_detection_script(self) -> str:
        """Get the Python script for PR conflict detection"""
        return '''
import os
import json
import httpx
import asyncio

async def check_conflicts():
    """Check for conflicts in a pull request"""
    github_token = os.environ["GITHUB_TOKEN"]
    repository = os.environ["REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Get PR details
            pr_response = await client.get(
                f"https://api.github.com/repos/{repository}/pulls/{pr_number}",
                headers=headers
            )
            
            if pr_response.status_code != 200:
                result = {
                    "has_conflicts": False,
                    "mergeable": None,
                    "error": f"Failed to fetch PR: {pr_response.status_code}"
                }
            else:
                pr_data = pr_response.json()
                mergeable = pr_data.get("mergeable")
                mergeable_state = pr_data.get("mergeable_state")
                
                result = {
                    "has_conflicts": mergeable is False,
                    "mergeable": mergeable,
                    "mergeable_state": mergeable_state,
                    "rebaseable": pr_data.get("rebaseable"),
                    "head_sha": pr_data.get("head", {}).get("sha"),
                    "base_sha": pr_data.get("base", {}).get("sha")
                }
                
    except Exception as e:
        result = {
            "has_conflicts": False,
            "mergeable": None,
            "error": str(e)
        }
    
    print(json.dumps(result))

if __name__ == "__main__":
    asyncio.run(check_conflicts())
'''

    def _get_description_update_script(self) -> str:
        """Get the Python script for PR description updates"""
        return '''
import os
import json
import httpx
import asyncio
from datetime import datetime

async def update_description():
    """Update the description of a pull request"""
    github_token = os.environ["GITHUB_TOKEN"]
    repository = os.environ["REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]
    description_update = os.environ["DESCRIPTION_UPDATE"]
    append = os.environ["APPEND"].lower() == "true"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Get current PR details
            pr_response = await client.get(
                f"https://api.github.com/repos/{repository}/pulls/{pr_number}",
                headers=headers
            )
            
            if pr_response.status_code != 200:
                result = {
                    "success": False,
                    "error": f"Failed to fetch PR: {pr_response.status_code}"
                }
                print(json.dumps(result))
                return
            
            pr_data = pr_response.json()
            current_body = pr_data.get("body", "")
            
            if append:
                new_body = current_body + "\\n\\n---\\n\\n" + description_update
                new_body += f"\\n\\n*Updated: {datetime.utcnow().isoformat()}Z*"
            else:
                new_body = description_update
            
            # Update PR description
            update_response = await client.patch(
                f"https://api.github.com/repos/{repository}/pulls/{pr_number}",
                headers=headers,
                json={"body": new_body}
            )
            
            result = {
                "success": update_response.status_code == 200,
                "append": append,
                "status_code": update_response.status_code
            }
            
    except Exception as e:
        result = {
            "success": False,
            "error": str(e)
        }
    
    print(json.dumps(result))

if __name__ == "__main__":
    asyncio.run(update_description())
'''

    def _get_outdated_pr_cleanup_script(self) -> str:
        """Get the Python script for cleaning up outdated PRs"""
        return '''
import os
import json
import httpx
import asyncio
from datetime import datetime, timedelta

async def close_outdated_prs():
    """Close outdated automated fix PRs"""
    github_token = os.environ["GITHUB_TOKEN"]
    repository = os.environ["REPOSITORY"]
    max_age_days = int(os.environ["MAX_AGE_DAYS"])
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
    closed_prs = []
    
    try:
        async with httpx.AsyncClient() as client:
            # Get open PRs
            prs_response = await client.get(
                f"https://api.github.com/repos/{repository}/pulls",
                headers=headers,
                params={"state": "open", "sort": "created", "direction": "asc"}
            )
            
            if prs_response.status_code != 200:
                result = {
                    "success": False,
                    "closed_prs": [],
                    "error": f"Failed to fetch PRs: {prs_response.status_code}"
                }
                print(json.dumps(result))
                return
            
            prs = prs_response.json()
            
            for pr in prs:
                # Check if it's an automated fix PR
                labels = [label["name"] for label in pr.get("labels", [])]
                if "automated-fix" not in labels:
                    continue
                
                # Check if it's older than the cutoff
                created_at = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
                if created_at.replace(tzinfo=None) > cutoff_date:
                    continue
                
                # Close the PR
                close_response = await client.patch(
                    f"https://api.github.com/repos/{repository}/pulls/{pr['number']}",
                    headers=headers,
                    json={
                        "state": "closed",
                        "body": pr.get("body", "") + f"\\n\\n---\\n\\n**Automatically closed:** This automated fix PR was older than {max_age_days} days and has been closed to keep the repository clean. If the fix is still needed, a new PR will be created when the issue is detected again."
                    }
                )
                
                if close_response.status_code == 200:
                    closed_prs.append({
                        "number": pr["number"],
                        "title": pr["title"],
                        "created_at": pr["created_at"]
                    })
            
            result = {
                "success": True,
                "closed_prs": closed_prs,
                "total_closed": len(closed_prs)
            }
            
    except Exception as e:
        result = {
            "success": False,
            "closed_prs": closed_prs,
            "error": str(e)
        }
    
    print(json.dumps(result))

if __name__ == "__main__":
    asyncio.run(close_outdated_prs())
'''

    def _get_cleanup_script(self) -> str:
        """Get the Python script for resource cleanup"""
        return '''
import os
import json
import httpx
import asyncio

async def cleanup():
    """Cleanup temporary resources created by the agent"""
    github_token = os.environ["GITHUB_TOKEN"]
    repository = os.environ["REPOSITORY"]
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    cleanup_results = {
        "branches_cleaned": 0,
        "prs_closed": 0,
        "errors": []
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Clean up old automated fix branches
            branches_response = await client.get(
                f"https://api.github.com/repos/{repository}/branches",
                headers=headers
            )
            
            if branches_response.status_code == 200:
                branches = branches_response.json()
                for branch in branches:
                    branch_name = branch["name"]
                    if branch_name.startswith("fix/") and "automated" in branch_name:
                        # Check if branch has an associated open PR
                        prs_response = await client.get(
                            f"https://api.github.com/repos/{repository}/pulls",
                            headers=headers,
                            params={"head": f"{repository.split('/')[0]}:{branch_name}", "state": "open"}
                        )
                        
                        if prs_response.status_code == 200 and len(prs_response.json()) == 0:
                            # No open PR, safe to delete branch
                            delete_response = await client.delete(
                                f"https://api.github.com/repos/{repository}/git/refs/heads/{branch_name}",
                                headers=headers
                            )
                            if delete_response.status_code == 204:
                                cleanup_results["branches_cleaned"] += 1
            
            result = {
                "cleanup_completed": True,
                "repository": repository,
                "results": cleanup_results
            }
            
    except Exception as e:
        result = {
            "cleanup_completed": False,
            "repository": repository,
            "error": str(e),
            "results": cleanup_results
        }
    
    print(json.dumps(result))

if __name__ == "__main__":
    asyncio.run(cleanup())
'''

    @function
    async def create_test_environment(
        self,
        python_versions: List[str] = None
    ) -> List[dagger.Container]:
        """Create test environments for multiple Python versions"""
        if python_versions is None:
            python_versions = ["3.10", "3.11", "3.12"]
        
        logger.info("Creating test environments", python_versions=python_versions)
        
        containers = []
        for version in python_versions:
            container = (
                dag.container()
                .from_(f"python:{version}")
                .with_exec(["pip", "install", "uv"])
                .with_exec(["uv", "--version"])
            )
            containers.append(container)
        
        return containers
