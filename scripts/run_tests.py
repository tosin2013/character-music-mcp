#!/usr/bin/env python3
"""
Automated Test Execution Script

Executes all test suites with proper configuration, coverage analysis,
and result reporting for CI/CD pipeline integration.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class TestExecutor:
    """Automated test execution with comprehensive reporting"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.test_results = {}
        self.coverage_data = {}

        # Test configuration
        self.test_suites = {
            "unit": {
                "path": "tests/unit/",
                "timeout": 300,
                "coverage": True,
                "required": True
            },
            "integration": {
                "path": "tests/integration/",
                "timeout": 600,
                "coverage": True,
                "required": True
            },
            "performance": {
                "path": "tests/performance/",
                "timeout": 900,
                "coverage": False,
                "required": False
            },
            "validation": {
                "path": "tests/validation/",
                "timeout": 300,
                "coverage": False,
                "required": True
            }
        }

        # Coverage thresholds
        self.coverage_thresholds = {
            "line": 80,
            "branch": 75,
            "function": 90
        }

    def run_command(self, command: List[str], cwd: Optional[str] = None,
                   timeout: int = 300) -> Dict[str, Any]:
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(command)
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "command": " ".join(command)
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "command": " ".join(command)
            }

    def setup_test_environment(self) -> bool:
        """Set up test environment and dependencies"""
        print("🔧 Setting up test environment...")

        # Ensure virtual environment is activated
        if not os.environ.get("VIRTUAL_ENV"):
            print("⚠️ Warning: No virtual environment detected")

        # Install test dependencies
        install_cmd = [
            "python", "-m", "pip", "install",
            "pytest", "pytest-cov", "pytest-asyncio", "pytest-benchmark",
            "coverage[toml]", "pytest-timeout", "pytest-xdist"
        ]

        result = self.run_command(install_cmd, timeout=120)
        if not result["success"]:
            print(f"❌ Failed to install test dependencies: {result['stderr']}")
            return False

        print("✅ Test environment ready")
        return True

    def run_test_suite(self, suite_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific test suite"""
        print(f"🧪 Running {suite_name} tests...")

        test_path = self.project_root / config["path"]
        if not test_path.exists():
            print(f"⚠️ Test path not found: {test_path}")
            return {
                "suite_name": suite_name,
                "success": False,
                "error": f"Test path not found: {test_path}",
                "tests_run": 0,
                "failures": 0,
                "errors": 0,
                "skipped": 0,
                "duration": 0.0
            }

        # Build pytest command
        pytest_cmd = ["python", "-m", "pytest", str(test_path), "-v"]

        # Add coverage if enabled
        if config.get("coverage", False):
            pytest_cmd.extend([
                "--cov=.",
                "--cov-report=xml",
                "--cov-report=term-missing",
                f"--cov-fail-under={self.coverage_thresholds['line']}"
            ])

        # Add timeout
        pytest_cmd.extend(["--timeout", str(config.get("timeout", 300))])

        # Add parallel execution for faster tests
        if suite_name in ["unit", "integration"]:
            pytest_cmd.extend(["-n", "auto"])

        # Add JSON report
        json_report_file = f"{suite_name}_test_results.json"
        pytest_cmd.extend(["--json-report", f"--json-report-file={json_report_file}"])

        # Run tests
        result = self.run_command(pytest_cmd, timeout=config.get("timeout", 300))

        # Parse results
        test_result = {
            "suite_name": suite_name,
            "success": result["success"],
            "command": result["command"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "tests_run": 0,
            "failures": 0,
            "errors": 0,
            "skipped": 0,
            "duration": 0.0
        }

        # Try to parse JSON report if available
        json_report_path = self.project_root / json_report_file
        if json_report_path.exists():
            try:
                with open(json_report_path, 'r') as f:
                    json_data = json.load(f)

                summary = json_data.get("summary", {})
                test_result.update({
                    "tests_run": summary.get("total", 0),
                    "failures": summary.get("failed", 0),
                    "errors": summary.get("error", 0),
                    "skipped": summary.get("skipped", 0),
                    "duration": json_data.get("duration", 0.0)
                })

            except Exception as e:
                print(f"⚠️ Failed to parse JSON report: {e}")

        # Print summary
        if test_result["success"]:
            print(f"✅ {suite_name} tests passed: {test_result['tests_run']} tests in {test_result['duration']:.2f}s")
        else:
            print(f"❌ {suite_name} tests failed: {test_result['failures']} failures, {test_result['errors']} errors")

        return test_result

    def run_unified_test_suite(self) -> Dict[str, Any]:
        """Run the unified test runner"""
        print("🔄 Running unified test suite...")

        unified_cmd = ["python", "tests/test_runner.py"]
        result = self.run_command(unified_cmd, timeout=600)

        unified_result = {
            "suite_name": "unified",
            "success": result["success"],
            "command": result["command"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "duration": 0.0
        }

        # Look for generated test report
        report_files = list(self.project_root.glob("test_report_*.json"))
        if report_files:
            try:
                with open(report_files[0], 'r') as f:
                    report_data = json.load(f)

                unified_result.update({
                    "tests_run": report_data.get("total_tests", 0),
                    "failures": report_data.get("total_failed", 0),
                    "errors": report_data.get("total_errors", 0),
                    "skipped": report_data.get("total_skipped", 0),
                    "duration": report_data.get("total_execution_time", 0.0),
                    "success_rate": report_data.get("overall_success_rate", 0.0)
                })

            except Exception as e:
                print(f"⚠️ Failed to parse unified test report: {e}")

        if unified_result["success"]:
            print("✅ Unified test suite passed")
        else:
            print("❌ Unified test suite failed")

        return unified_result

    def analyze_coverage(self) -> Dict[str, Any]:
        """Analyze code coverage from generated reports"""
        print("📊 Analyzing code coverage...")

        coverage_data = {
            "line_coverage": 0.0,
            "branch_coverage": 0.0,
            "function_coverage": 0.0,
            "missing_lines": [],
            "covered_files": 0,
            "total_files": 0
        }

        # Look for coverage.xml file
        coverage_file = self.project_root / "coverage.xml"
        if coverage_file.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(coverage_file)
                root = tree.getroot()

                # Extract coverage percentages
                coverage_elem = root.find(".")
                if coverage_elem is not None:
                    line_rate = float(coverage_elem.get("line-rate", 0))
                    branch_rate = float(coverage_elem.get("branch-rate", 0))

                    coverage_data["line_coverage"] = line_rate * 100
                    coverage_data["branch_coverage"] = branch_rate * 100

                # Count files
                packages = root.findall(".//package")
                for package in packages:
                    classes = package.findall(".//class")
                    coverage_data["total_files"] += len(classes)

                    for class_elem in classes:
                        line_rate = float(class_elem.get("line-rate", 0))
                        if line_rate > 0:
                            coverage_data["covered_files"] += 1

            except Exception as e:
                print(f"⚠️ Failed to parse coverage report: {e}")

        # Generate coverage report using coverage.py
        coverage_cmd = ["python", "-m", "coverage", "report", "--format=json"]
        result = self.run_command(coverage_cmd)

        if result["success"]:
            try:
                coverage_json = json.loads(result["stdout"])
                totals = coverage_json.get("totals", {})

                coverage_data.update({
                    "line_coverage": totals.get("percent_covered", 0.0),
                    "missing_lines": totals.get("missing_lines", 0),
                    "covered_lines": totals.get("covered_lines", 0),
                    "total_lines": totals.get("num_statements", 0)
                })

            except Exception as e:
                print(f"⚠️ Failed to parse coverage JSON: {e}")

        # Check coverage thresholds
        coverage_passed = (
            coverage_data["line_coverage"] >= self.coverage_thresholds["line"]
        )

        if coverage_passed:
            print(f"✅ Coverage passed: {coverage_data['line_coverage']:.1f}% line coverage")
        else:
            print(f"❌ Coverage failed: {coverage_data['line_coverage']:.1f}% < {self.coverage_thresholds['line']}%")

        coverage_data["passed"] = coverage_passed
        return coverage_data

    def run_all_tests(self, suites: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run all test suites and generate comprehensive report"""
        print("🚀 Starting automated test execution")
        print("=" * 60)

        start_time = datetime.now()

        # Setup environment
        if not self.setup_test_environment():
            return {"success": False, "error": "Failed to setup test environment"}

        # Determine which suites to run
        suites_to_run = suites or list(self.test_suites.keys())

        # Run individual test suites
        suite_results = []
        overall_success = True

        for suite_name in suites_to_run:
            if suite_name not in self.test_suites:
                print(f"⚠️ Unknown test suite: {suite_name}")
                continue

            config = self.test_suites[suite_name]
            result = self.run_test_suite(suite_name, config)
            suite_results.append(result)

            # Check if required suite failed
            if config.get("required", False) and not result["success"]:
                overall_success = False

        # Run unified test suite
        unified_result = self.run_unified_test_suite()
        suite_results.append(unified_result)

        if not unified_result["success"]:
            overall_success = False

        # Analyze coverage
        coverage_data = self.analyze_coverage()
        if not coverage_data.get("passed", False):
            print("⚠️ Coverage threshold not met")

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        # Generate comprehensive report
        report = {
            "timestamp": start_time.isoformat(),
            "duration": total_duration,
            "success": overall_success,
            "suite_results": suite_results,
            "coverage": coverage_data,
            "summary": {
                "total_suites": len(suite_results),
                "passed_suites": len([r for r in suite_results if r["success"]]),
                "failed_suites": len([r for r in suite_results if not r["success"]]),
                "total_tests": sum(r.get("tests_run", 0) for r in suite_results),
                "total_failures": sum(r.get("failures", 0) for r in suite_results),
                "total_errors": sum(r.get("errors", 0) for r in suite_results)
            }
        }

        # Save report
        report_file = f"automated_test_report_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Print summary
        self.print_test_summary(report)

        print(f"📄 Test report saved: {report_file}")

        return report

    def print_test_summary(self, report: Dict[str, Any]) -> None:
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 AUTOMATED TEST SUMMARY")
        print("=" * 60)

        summary = report["summary"]
        print(f"Overall Status: {'✅ PASSED' if report['success'] else '❌ FAILED'}")
        print(f"Total Duration: {report['duration']:.2f}s")
        print(f"Test Suites: {summary['passed_suites']}/{summary['total_suites']} passed")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Failures: {summary['total_failures']}")
        print(f"Errors: {summary['total_errors']}")

        coverage = report["coverage"]
        print(f"Line Coverage: {coverage['line_coverage']:.1f}%")

        print("\n📋 Suite Details:")
        for result in report["suite_results"]:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['suite_name']}: {result.get('tests_run', 0)} tests "
                  f"in {result.get('duration', 0):.2f}s")

        print("=" * 60)


def main():
    """Main test execution"""
    parser = argparse.ArgumentParser(description="Run automated test suite")
    parser.add_argument("--suites", "-s", nargs="+",
                       choices=["unit", "integration", "performance", "validation", "unified"],
                       help="Specific test suites to run")
    parser.add_argument("--coverage-threshold", "-c", type=int, default=80,
                       help="Minimum coverage percentage required")
    parser.add_argument("--fail-fast", "-f", action="store_true",
                       help="Stop on first test suite failure")
    parser.add_argument("--parallel", "-p", action="store_true",
                       help="Run test suites in parallel where possible")

    args = parser.parse_args()

    executor = TestExecutor()

    # Update coverage threshold if specified
    if args.coverage_threshold:
        executor.coverage_thresholds["line"] = args.coverage_threshold

    # Run tests
    report = executor.run_all_tests(args.suites)

    # Exit with appropriate code
    sys.exit(0 if report["success"] else 1)


if __name__ == "__main__":
    main()
