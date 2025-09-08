"""CLI entry point for the Dagger Test Repair Agent"""

import asyncio
import sys
from typing import Optional

import click
import dagger

from .config import get_config
from .logging_config import configure_logging, get_logger
from .main import DaggerTestRepairAgent


@click.group()
@click.option("--log-level", default="INFO", help="Set the logging level")
@click.option("--log-format", default="json", help="Set the logging format (json or console)")
@click.pass_context
def cli(ctx: click.Context, log_level: str, log_format: str) -> None:
    """Dagger Test Repair Agent CLI"""
    configure_logging(log_level, log_format)
    ctx.ensure_object(dict)
    # For local CLI operations, we don't require GitHub auth
    ctx.obj["config"] = get_config(require_github_auth=False)


@cli.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check the health of the agent"""
    async def _health_check():
        async with await dagger.connect() as client:
            agent = client.dagger_test_repair_agent()
            result = await agent.health_check()
            click.echo(result)
    
    asyncio.run(_health_check())


@cli.command()
@click.option("--source", default=".", help="Source directory to test")
@click.option("--python-version", default="3.10", help="Python version to use")
@click.option("--test-command", default="pytest tests/ -v", help="Test command to run")
@click.pass_context
def test(ctx: click.Context, source: str, python_version: str, test_command: str) -> None:
    """Run tests in a Dagger container"""
    async def _run_tests():
        async with await dagger.connect() as client:
            agent = client.dagger_test_repair_agent()
            source_dir = client.host().directory(source)
            result = await agent.run_tests(source_dir, python_version, test_command)
            click.echo(result)
    
    asyncio.run(_run_tests())


@cli.command()
@click.option("--source", default=".", help="Source directory to check")
@click.option("--python-version", default="3.10", help="Python version to use")
@click.pass_context
def quality(ctx: click.Context, source: str, python_version: str) -> None:
    """Run quality checks in a Dagger container"""
    async def _run_quality():
        async with await dagger.connect() as client:
            agent = client.dagger_test_repair_agent()
            source_dir = client.host().directory(source)
            result = await agent.run_quality_checks(source_dir, python_version)
            click.echo(result)
    
    asyncio.run(_run_quality())


@cli.command()
@click.option("--source", default=".", help="Source directory to validate")
@click.option("--python-version", default="3.10", help="Python version to use")
@click.option("--test-type", default="unit", help="Type of tests to run (unit, integration, quality, all)")
@click.pass_context
def validate(ctx: click.Context, source: str, python_version: str, test_type: str) -> None:
    """Validate a fix by running tests"""
    async def _validate_fix():
        async with await dagger.connect() as client:
            agent = client.dagger_test_repair_agent()
            source_dir = client.host().directory(source)
            result = await agent.validate_fix(source_dir, python_version, test_type)
            click.echo(result)
    
    asyncio.run(_validate_fix())


@cli.command()
@click.option("--workflow-run-id", required=True, help="GitHub workflow run ID")
@click.option("--repository", required=True, help="GitHub repository (owner/repo)")
@click.pass_context
def process_failure(ctx: click.Context, workflow_run_id: str, repository: str) -> None:
    """Process a GitHub workflow failure"""
    # This command requires GitHub auth, so validate with that requirement
    config = get_config(require_github_auth=True)
    
    async def _process_failure():
        async with await dagger.connect() as client:
            agent = client.dagger_test_repair_agent()
            
            # Convert secrets to Dagger secrets
            github_token = client.set_secret("github_token", config.github_token or "")
            deepseek_key = client.set_secret("deepseek_api_key", config.deepseek_api_key or "")
            
            result = await agent.process_workflow_failure(
                github_token, deepseek_key, workflow_run_id, repository
            )
            click.echo(result)
    
    asyncio.run(_process_failure())


@cli.command()
@click.option("--python-versions", default="3.10,3.11,3.12", help="Comma-separated Python versions")
@click.pass_context
def create_environments(ctx: click.Context, python_versions: str) -> None:
    """Create test environments for multiple Python versions"""
    versions = [v.strip() for v in python_versions.split(",")]
    
    async def _create_environments():
        async with await dagger.connect() as client:
            agent = client.dagger_test_repair_agent()
            containers = await agent.create_test_environment(versions)
            click.echo(f"Created {len(containers)} test environments for Python versions: {', '.join(versions)}")
    
    asyncio.run(_create_environments())


if __name__ == "__main__":
    cli()