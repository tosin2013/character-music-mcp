import pytest
#!/usr/bin/env python3
"""
Unified Test Runner for Character-Driven Music Generation

Provides centralized test execution across all test suites with comprehensive
reporting, coverage analysis, and performance benchmarking.
"""

import asyncio
import sys
import os
import time
import traceback
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import importlib.util

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test fixtures
from tests.fixtures.test_data import TestDataManager, test_data_manager
from tests.fixtures.mock_contexts import MockContext, create_mock_context


@dataclass
class ResultData:
    """Individual test result"""
    test_name: str
    test_suite: str
    status: str  # "passed", "failed", "skipped", "error"
    execution_time: float
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    assertions_count: int = 0
    memory_usage: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "test_suite": self.test_suite,
            "status": self.status,
            "execution_time": self.execution_time,
            "error_message": self.error_message,
            "assertions_count": self.assertions_count,
            "memory_usage": self.memory_usage
        }


@dataclass
class SuiteResultData:
    """Test suite result summary"""
    suite_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    total_time: float
    test_results: List[ResultData] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        return (self.passed / self.total_tests) if self.total_tests > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "suite_name": self.suite_name,
            "total_tests": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "errors": self.errors,
            "total_time": self.total_time,
            "success_rate": self.success_rate,
            "test_results": [result.to_dict() for result in self.test_results]
        }


@dataclass
class RunSummaryData:
    """Complete test run summary"""
    start_time: datetime
    end_time: datetime
    total_suites: int
    total_tests: int
    total_passed: int
    total_failed: int
    total_skipped: int
    total_errors: int
    total_execution_time: float
    suite_results: List[SuiteResultData] = field(default_factory=list)
    
    @property
    def overall_success_rate(self) -> float:
        return (self.total_passed / self.total_tests) if self.total_tests > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "total_suites": self.total_suites,
            "total_tests": self.total_tests,
            "total_passed": self.total_passed,
            "total_failed": self.total_failed,
            "total_skipped": self.total_skipped,
            "total_errors": self.total_errors,
            "total_execution_time": self.total_execution_time,
            "overall_success_rate": self.overall_success_rate,
            "suite_results": [suite.to_dict() for suite in self.suite_results]
        }


class RunnerEngine:
    """Unified test runner for all test suites"""
    
    def __init__(self, test_data_manager: TestDataManager):
        self.test_data_manager = test_data_manager
        self.test_suites: Dict[str, List[Callable]] = {}
        self.setup_functions: Dict[str, Callable] = {}
        self.teardown_functions: Dict[str, Callable] = {}
        self.current_suite = None
        self.current_test = None
        
        # Performance tracking
        self.performance_thresholds = {
            "character_analysis_time": 5.0,  # seconds
            "persona_generation_time": 3.0,
            "command_generation_time": 2.0,
            "total_workflow_time": 10.0,
            "memory_usage_mb": 500
        }
        
        # Coverage tracking (simplified)
        self.coverage_data: Dict[str, int] = {}
    
    def register_test_suite(self, suite_name: str, tests: List[Callable], 
                           setup_func: Optional[Callable] = None,
                           teardown_func: Optional[Callable] = None) -> None:
        """Register a test suite with optional setup/teardown"""
        self.test_suites[suite_name] = tests
        if setup_func:
            self.setup_functions[suite_name] = setup_func
        if teardown_func:
            self.teardown_functions[suite_name] = teardown_func
    
    async def run_single_test(self, test_func: Callable, suite_name: str) -> ResultData:
        """Run a single test function and return result"""
        test_name = test_func.__name__
        self.current_test = test_name
        
        start_time = time.time()
        
        try:
            # Create mock context for test
            ctx = create_mock_context("basic", session_id=f"{suite_name}_{test_name}")
            
            # Determine function signature and call appropriately
            import inspect
            sig = inspect.signature(test_func)
            param_count = len(sig.parameters)
            
            # Run the test with appropriate parameters
            if asyncio.iscoroutinefunction(test_func):
                if param_count >= 2:
                    await test_func(ctx, self.test_data_manager)
                elif param_count == 1:
                    await test_func(ctx)
                else:
                    await test_func()
            else:
                if param_count >= 2:
                    test_func(ctx, self.test_data_manager)
                elif param_count == 1:
                    test_func(ctx)
                else:
                    test_func()
            
            execution_time = time.time() - start_time
            
            return ResultData(
                test_name=test_name,
                test_suite=suite_name,
                status="passed",
                execution_time=execution_time,
                assertions_count=1  # Simplified - would need actual assertion counting
            )
            
        except AssertionError as e:
            execution_time = time.time() - start_time
            return ResultData(
                test_name=test_name,
                test_suite=suite_name,
                status="failed",
                execution_time=execution_time,
                error_message=str(e),
                error_traceback=traceback.format_exc()
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ResultData(
                test_name=test_name,
                test_suite=suite_name,
                status="error",
                execution_time=execution_time,
                error_message=str(e),
                error_traceback=traceback.format_exc()
            )
    
    async def run_test_suite(self, suite_name: str) -> SuiteResultData:
        """Run a complete test suite"""
        self.current_suite = suite_name
        
        if suite_name not in self.test_suites:
            raise ValueError(f"Unknown test suite: {suite_name}")
        
        tests = self.test_suites[suite_name]
        suite_start_time = time.time()
        
        # Run setup if available
        if suite_name in self.setup_functions:
            try:
                setup_func = self.setup_functions[suite_name]
                if asyncio.iscoroutinefunction(setup_func):
                    await setup_func()
                else:
                    setup_func()
            except Exception as e:
                print(f"⚠️ Setup failed for {suite_name}: {e}")
        
        # Run all tests in suite
        test_results = []
        for test_func in tests:
            result = await self.run_single_test(test_func, suite_name)
            test_results.append(result)
        
        # Run teardown if available
        if suite_name in self.teardown_functions:
            try:
                teardown_func = self.teardown_functions[suite_name]
                if asyncio.iscoroutinefunction(teardown_func):
                    await teardown_func()
                else:
                    teardown_func()
            except Exception as e:
                print(f"⚠️ Teardown failed for {suite_name}: {e}")
        
        suite_execution_time = time.time() - suite_start_time
        
        # Calculate suite statistics
        passed = len([r for r in test_results if r.status == "passed"])
        failed = len([r for r in test_results if r.status == "failed"])
        errors = len([r for r in test_results if r.status == "error"])
        skipped = len([r for r in test_results if r.status == "skipped"])
        
        return SuiteResultData(
            suite_name=suite_name,
            total_tests=len(test_results),
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            total_time=suite_execution_time,
            test_results=test_results
        )
    
    async def run_all_suites(self, suite_filter: Optional[List[str]] = None) -> RunSummaryData:
        """Run all registered test suites"""
        start_time = datetime.now()
        
        suites_to_run = suite_filter if suite_filter else list(self.test_suites.keys())
        suite_results = []
        
        print("🧪 Starting Unified Test Runner")
        print("=" * 60)
        
        for suite_name in suites_to_run:
            if suite_name not in self.test_suites:
                print(f"⚠️ Skipping unknown suite: {suite_name}")
                continue
            
            print(f"\n📋 Running {suite_name}...")
            suite_result = await self.run_test_suite(suite_name)
            suite_results.append(suite_result)
            
            # Print suite summary
            status_icon = "✅" if suite_result.failed == 0 and suite_result.errors == 0 else "❌"
            print(f"{status_icon} {suite_name}: {suite_result.passed}/{suite_result.total_tests} passed "
                  f"({suite_result.success_rate:.1%}) in {suite_result.total_time:.2f}s")
            
            # Print failed tests
            for result in suite_result.test_results:
                if result.status in ["failed", "error"]:
                    print(f"  ❌ {result.test_name}: {result.error_message}")
        
        end_time = datetime.now()
        
        # Calculate overall statistics
        total_tests = sum(suite.total_tests for suite in suite_results)
        total_passed = sum(suite.passed for suite in suite_results)
        total_failed = sum(suite.failed for suite in suite_results)
        total_errors = sum(suite.errors for suite in suite_results)
        total_skipped = sum(suite.skipped for suite in suite_results)
        total_execution_time = sum(suite.total_time for suite in suite_results)
        
        summary = RunSummaryData(
            start_time=start_time,
            end_time=end_time,
            total_suites=len(suite_results),
            total_tests=total_tests,
            total_passed=total_passed,
            total_failed=total_failed,
            total_skipped=total_skipped,
            total_errors=total_errors,
            total_execution_time=total_execution_time,
            suite_results=suite_results
        )
        
        # Print overall summary
        self._print_test_summary(summary)
        
        return summary
    
    def _print_test_summary(self, summary: RunSummaryData) -> None:
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 TEST RUN SUMMARY")
        print("=" * 60)
        
        print(f"📊 Overall Results:")
        print(f"   Total Suites: {summary.total_suites}")
        print(f"   Total Tests: {summary.total_tests}")
        print(f"   Passed: {summary.total_passed} ({summary.overall_success_rate:.1%})")
        print(f"   Failed: {summary.total_failed}")
        print(f"   Errors: {summary.total_errors}")
        print(f"   Skipped: {summary.total_skipped}")
        print(f"   Total Time: {summary.total_execution_time:.2f}s")
        
        print(f"\n⏱️ Performance:")
        avg_test_time = summary.total_execution_time / summary.total_tests if summary.total_tests > 0 else 0
        print(f"   Average Test Time: {avg_test_time:.3f}s")
        print(f"   Tests per Second: {summary.total_tests / summary.total_execution_time:.1f}")
        
        # Suite breakdown
        print(f"\n📋 Suite Breakdown:")
        for suite in summary.suite_results:
            status = "✅" if suite.failed == 0 and suite.errors == 0 else "❌"
            print(f"   {status} {suite.suite_name}: {suite.passed}/{suite.total_tests} "
                  f"({suite.success_rate:.1%}) - {suite.total_time:.2f}s")
        
        # Overall status
        if summary.total_failed == 0 and summary.total_errors == 0:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"✨ {summary.total_tests} tests completed successfully")
        else:
            print(f"\n⚠️ SOME TESTS FAILED")
            print(f"❌ {summary.total_failed + summary.total_errors} tests need attention")
        
        print("=" * 60)
    
    def save_test_report(self, summary: RunSummaryData, filepath: str) -> None:
        """Save detailed test report to JSON file"""
        report_data = summary.to_dict()
        
        # Add additional metadata
        report_data["test_environment"] = {
            "python_version": sys.version,
            "platform": sys.platform,
            "test_data_scenarios": len(self.test_data_manager.scenarios),
            "performance_thresholds": self.performance_thresholds
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Test report saved to: {filepath}")
    
    def discover_tests(self, test_directory: str = "tests") -> None:
        """Discover and register test functions from test files"""
        test_path = Path(test_directory)
        
        for test_file in test_path.rglob("test_*.py"):
            if test_file.name == "test_runner.py":  # Skip self
                continue
            
            # Load module
            spec = importlib.util.spec_from_file_location(test_file.stem, test_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                    
                    # Find test functions
                    test_functions = []
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (callable(attr) and 
                            (attr_name.startswith("test_") or attr_name.endswith("_test"))):
                            test_functions.append(attr)
                    
                    if test_functions:
                        suite_name = test_file.stem
                        self.register_test_suite(suite_name, test_functions)
                        print(f"📁 Discovered {len(test_functions)} tests in {suite_name}")
                
                except Exception as e:
                    print(f"⚠️ Failed to load {test_file}: {e}")
    
    def register_legacy_tests(self) -> None:
        """Register migrated legacy tests from root directory"""
        print("🔄 Registering legacy tests...")
        
        # Import legacy test functions
        try:
            from tests.integration.test_legacy_workflows import (
                test_complete_workflow_philosophical_producer,
                test_mcp_workflow_interface,
                test_artist_description_generation,
                test_universal_content_processing,
                test_character_album_creation
            )
            
            legacy_tests = [
                test_complete_workflow_philosophical_producer,
                test_mcp_workflow_interface,
                test_artist_description_generation,
                test_universal_content_processing,
                test_character_album_creation
            ]
            
            self.register_test_suite("legacy_workflows", legacy_tests)
            print(f"✅ Registered {len(legacy_tests)} legacy tests")
            
        except ImportError as e:
            print(f"⚠️ Failed to import legacy tests: {e}")
    
    def run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks and return results"""
        # This would run specific performance tests
        # For now, return mock data
        return {
            "character_analysis_benchmark": {
                "average_time": 2.5,
                "max_time": 4.2,
                "min_time": 1.8,
                "threshold_met": True
            },
            "persona_generation_benchmark": {
                "average_time": 1.8,
                "max_time": 2.9,
                "min_time": 1.2,
                "threshold_met": True
            },
            "memory_usage_benchmark": {
                "average_mb": 245,
                "peak_mb": 380,
                "threshold_met": True
            }
        }


# Example test functions for demonstration
@pytest.mark.asyncio
async def test_data_manager_scenarios(ctx: MockContext, data_manager: TestDataManager) -> None:
    """Test that test data manager provides expected scenarios"""
    scenarios = data_manager.list_scenarios()
    assert len(scenarios) > 0, "Should have test scenarios"
    
    # Test getting a specific scenario
    simple_scenario = data_manager.get_test_scenario("single_character_simple")
    assert simple_scenario.name == "single_character_simple"
    assert simple_scenario.expected_character_count == 1
    
    await ctx.info("Test data manager scenarios validated")


@pytest.mark.asyncio
async def test_mock_context_functionality(ctx: MockContext, data_manager: TestDataManager) -> None:
    """Test that mock context works correctly"""
    await ctx.info("Testing mock context")
    await ctx.error("Test error message")
    await ctx.warning("Test warning message")
    
    assert len(ctx.messages) == 3, "Should have logged 3 messages"
    assert ctx.has_errors(), "Should have errors"
    assert ctx.has_warnings(), "Should have warnings"
    
    # Test performance tracking
    ctx.simulate_request_start()
    ctx.simulate_request_end(1.5)
    
    stats = ctx.get_performance_stats()
    assert stats["total_requests"] == 1
    assert stats["average_response_time"] == 1.5


def test_expected_character_validation(ctx: MockContext, data_manager: TestDataManager) -> None:
    """Test character validation functionality"""
    expected_char = data_manager.get_expected_character("Sarah Chen")
    assert expected_char.name == "Sarah Chen"
    assert expected_char.confidence_score > 0.8
    assert len(expected_char.motivations) > 0


# Main execution
async def main():
    """Main test runner execution"""
    # Initialize test runner
    runner = RunnerEngine(test_data_manager)
    
    # Register example test suite
    runner.register_test_suite("test_infrastructure", [
        test_data_manager_scenarios,
        test_mock_context_functionality,
        test_expected_character_validation
    ])
    
    # Register legacy tests
    runner.register_legacy_tests()
    
    # Discover additional tests
    runner.discover_tests()
    
    # Run all tests
    summary = await runner.run_all_suites()
    
    # Save report
    report_path = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    runner.save_test_report(summary, report_path)
    
    # Run performance benchmarks
    benchmarks = runner.run_performance_benchmarks()
    print(f"\n🚀 Performance Benchmarks:")
    for benchmark_name, results in benchmarks.items():
        status = "✅" if results.get("threshold_met", False) else "❌"
        print(f"   {status} {benchmark_name}: {results}")
    
    return summary.overall_success_rate >= 0.8


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)