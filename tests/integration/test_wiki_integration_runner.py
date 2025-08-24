#!/usr/bin/env python3
"""
Wiki Integration Test Runner

Comprehensive test runner for all wiki integration end-to-end tests.
Provides unified execution, reporting, and validation for the complete
wiki data integration system.

Requirements: All requirements validation for dynamic Suno data integration
"""

import asyncio
import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

# Import test utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.fixtures.test_data import TestDataManager
from tests.fixtures.mock_contexts import MockContext, MockPerformanceContext

# Import test suites
from tests.integration.test_wiki_integration_end_to_end import TestWikiIntegrationEndToEnd
from tests.integration.test_wiki_performance_and_edge_cases import TestWikiPerformanceAndEdgeCases

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WikiIntegrationTestRunner:
    """Comprehensive test runner for wiki integration tests"""
    
    def __init__(self):
        self.test_data = TestDataManager()
        self.mock_context = MockContext("wiki_integration_runner")
        self.performance_context = MockPerformanceContext("wiki_integration_performance")
        
        # Test results tracking
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "test_details": [],
            "performance_metrics": {},
            "start_time": None,
            "end_time": None,
            "total_duration": 0
        }
        
        # Test suites to run
        self.test_suites = [
            ("End-to-End Integration", TestWikiIntegrationEndToEnd),
            ("Performance and Edge Cases", TestWikiPerformanceAndEdgeCases)
        ]
    
    async def run_all_tests(self, include_performance: bool = True, 
                           include_stress: bool = False) -> Dict[str, Any]:
        """
        Run all wiki integration tests
        
        Args:
            include_performance: Whether to run performance tests
            include_stress: Whether to run stress tests (may take longer)
            
        Returns:
            Dictionary with test results and metrics
        """
        self.test_results["start_time"] = time.time()
        
        print("🚀 STARTING COMPREHENSIVE WIKI INTEGRATION TESTS")
        print("=" * 70)
        print(f"Include Performance Tests: {include_performance}")
        print(f"Include Stress Tests: {include_stress}")
        print("=" * 70)
        
        try:
            # Run end-to-end integration tests
            await self._run_end_to_end_tests()
            
            if include_performance:
                # Run performance and edge case tests
                await self._run_performance_tests(include_stress)
            
            # Generate final report
            await self._generate_final_report()
            
        except Exception as e:
            logger.error(f"Test runner failed: {str(e)}")
            self.test_results["runner_error"] = str(e)
            self.test_results["runner_traceback"] = traceback.format_exc()
        
        finally:
            self.test_results["end_time"] = time.time()
            self.test_results["total_duration"] = (
                self.test_results["end_time"] - self.test_results["start_time"]
            )
        
        return self.test_results
    
    async def _run_end_to_end_tests(self):
        """Run end-to-end integration tests"""
        print("\n📋 RUNNING END-TO-END INTEGRATION TESTS")
        print("-" * 50)
        
        test_suite = TestWikiIntegrationEndToEnd()
        
        # Define test methods to run
        end_to_end_tests = [
            ("Complete Download → Parse → Generate → Attribute Flow", 
             test_suite.test_complete_download_parse_generate_attribute_flow),
            ("Fallback Scenarios with Unavailable Wiki Data", 
             test_suite.test_fallback_scenarios_with_unavailable_wiki_data),
            ("Configuration Changes and System Reconfiguration", 
             test_suite.test_configuration_changes_and_system_reconfiguration),
            ("Concurrent Access and Performance Under Load", 
             test_suite.test_concurrent_access_and_performance_under_load),
            ("Data Consistency Across Components", 
             test_suite.test_data_consistency_across_components),
            ("Error Recovery and Resilience", 
             test_suite.test_error_recovery_and_resilience),
            ("Configuration Hot Reload and Validation", 
             test_suite.test_configuration_hot_reload_and_validation),
            ("End-to-End Workflow with Attribution Tracking", 
             test_suite.test_end_to_end_workflow_with_attribution_tracking),
            ("System Performance Under Load Scenarios", 
             test_suite.test_system_performance_under_load_scenarios)
        ]
        
        for test_name, test_method in end_to_end_tests:
            await self._run_single_test(test_name, test_method, test_suite)
    
    async def _run_performance_tests(self, include_stress: bool = False):
        """Run performance and edge case tests"""
        print("\n⚡ RUNNING PERFORMANCE AND EDGE CASE TESTS")
        print("-" * 50)
        
        test_suite = TestWikiPerformanceAndEdgeCases()
        
        # Define performance test methods
        performance_tests = [
            ("Large Dataset Handling", 
             test_suite.test_large_dataset_handling),
            ("Memory Usage and Cleanup", 
             test_suite.test_memory_usage_and_cleanup),
            ("Edge Case Inputs", 
             test_suite.test_edge_case_inputs),
            ("Cache Performance and Efficiency", 
             test_suite.test_cache_performance_and_efficiency),
            ("Resource Cleanup and Limits", 
             test_suite.test_resource_cleanup_and_limits)
        ]
        
        # Add stress tests if requested
        if include_stress:
            performance_tests.append(
                ("Concurrent Stress Testing", 
                 test_suite.test_concurrent_stress_testing)
            )
        
        for test_name, test_method in performance_tests:
            await self._run_single_test(test_name, test_method, test_suite)
    
    async def _run_single_test(self, test_name: str, test_method, test_suite):
        """Run a single test method with error handling and timing"""
        self.test_results["total_tests"] += 1
        
        test_detail = {
            "name": test_name,
            "status": "running",
            "start_time": time.time(),
            "duration": 0,
            "error": None,
            "traceback": None
        }
        
        print(f"🧪 Running: {test_name}")
        
        try:
            # Setup test suite
            test_suite.setup_method()
            
            # Run the test
            await test_method()
            
            # Test passed
            test_detail["status"] = "passed"
            self.test_results["passed_tests"] += 1
            print(f"✅ PASSED: {test_name}")
            
        except Exception as e:
            # Test failed
            test_detail["status"] = "failed"
            test_detail["error"] = str(e)
            test_detail["traceback"] = traceback.format_exc()
            self.test_results["failed_tests"] += 1
            print(f"❌ FAILED: {test_name}")
            print(f"   Error: {str(e)}")
            
        finally:
            # Cleanup test suite
            try:
                test_suite.teardown_method()
            except Exception as cleanup_error:
                print(f"⚠️  Cleanup warning for {test_name}: {cleanup_error}")
            
            # Record timing
            test_detail["end_time"] = time.time()
            test_detail["duration"] = test_detail["end_time"] - test_detail["start_time"]
            
            # Add to results
            self.test_results["test_details"].append(test_detail)
    
    async def _generate_final_report(self):
        """Generate comprehensive final test report"""
        print("\n" + "=" * 70)
        print("📊 FINAL TEST REPORT")
        print("=" * 70)
        
        # Summary statistics
        total = self.test_results["total_tests"]
        passed = self.test_results["passed_tests"]
        failed = self.test_results["failed_tests"]
        duration = self.test_results["total_duration"]
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")
        print(f"Total Duration: {duration:.2f} seconds")
        
        # Performance metrics summary
        if hasattr(self.performance_context, 'get_performance_summary'):
            perf_summary = self.performance_context.get_performance_summary()
            if perf_summary:
                print("\n📈 PERFORMANCE METRICS:")
                for metric, stats in perf_summary.items():
                    if isinstance(stats, dict) and "average" in stats:
                        print(f"  {metric}: {stats['average']:.3f}s (avg)")
                    elif isinstance(stats, (int, float)):
                        print(f"  {metric}: {stats:.3f}")
        
        # Detailed test results
        print("\n📋 DETAILED TEST RESULTS:")
        for test_detail in self.test_results["test_details"]:
            status_icon = "✅" if test_detail["status"] == "passed" else "❌"
            print(f"{status_icon} {test_detail['name']} ({test_detail['duration']:.2f}s)")
            
            if test_detail["status"] == "failed":
                print(f"    Error: {test_detail['error']}")
        
        # Overall result
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("Wiki integration system is working correctly.")
        else:
            print(f"\n⚠️  {failed} TEST(S) FAILED")
            print("Please review the failed tests and fix issues.")
        
        # Save detailed report to file
        await self._save_report_to_file()
    
    async def _save_report_to_file(self):
        """Save detailed test report to JSON file"""
        try:
            report_dir = Path("tests/integration/reports")
            report_dir.mkdir(exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            report_file = report_dir / f"wiki_integration_test_report_{timestamp}.json"
            
            # Prepare report data
            report_data = {
                "test_run_info": {
                    "timestamp": timestamp,
                    "total_duration": self.test_results["total_duration"],
                    "test_environment": "integration_test"
                },
                "summary": {
                    "total_tests": self.test_results["total_tests"],
                    "passed_tests": self.test_results["passed_tests"],
                    "failed_tests": self.test_results["failed_tests"],
                    "success_rate": (self.test_results["passed_tests"] / 
                                   self.test_results["total_tests"] * 100) if self.test_results["total_tests"] > 0 else 0
                },
                "test_details": self.test_results["test_details"],
                "performance_metrics": getattr(self.performance_context, '_metrics', {}),
                "system_info": {
                    "python_version": sys.version,
                    "platform": sys.platform
                }
            }
            
            # Write report
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            print(f"\n📄 Detailed report saved to: {report_file}")
            
        except Exception as e:
            print(f"⚠️  Could not save report to file: {e}")
    
    async def run_specific_test_category(self, category: str) -> Dict[str, Any]:
        """
        Run tests from a specific category
        
        Args:
            category: "end_to_end", "performance", or "all"
            
        Returns:
            Test results dictionary
        """
        self.test_results["start_time"] = time.time()
        
        print(f"🚀 RUNNING {category.upper()} WIKI INTEGRATION TESTS")
        print("=" * 70)
        
        try:
            if category == "end_to_end":
                await self._run_end_to_end_tests()
            elif category == "performance":
                await self._run_performance_tests(include_stress=True)
            elif category == "all":
                await self._run_end_to_end_tests()
                await self._run_performance_tests(include_stress=True)
            else:
                raise ValueError(f"Unknown test category: {category}")
            
            await self._generate_final_report()
            
        except Exception as e:
            logger.error(f"Test category runner failed: {str(e)}")
            self.test_results["runner_error"] = str(e)
        
        finally:
            self.test_results["end_time"] = time.time()
            self.test_results["total_duration"] = (
                self.test_results["end_time"] - self.test_results["start_time"]
            )
        
        return self.test_results
    
    def get_test_summary(self) -> str:
        """Get a brief test summary string"""
        total = self.test_results["total_tests"]
        passed = self.test_results["passed_tests"]
        failed = self.test_results["failed_tests"]
        duration = self.test_results["total_duration"]
        
        if total == 0:
            return "No tests run"
        
        success_rate = passed / total * 100
        status = "PASSED" if failed == 0 else "FAILED"
        
        return (f"Wiki Integration Tests {status}: "
                f"{passed}/{total} passed ({success_rate:.1f}%) "
                f"in {duration:.2f}s")


# Main execution functions
async def run_all_wiki_integration_tests():
    """Run all wiki integration tests"""
    runner = WikiIntegrationTestRunner()
    results = await runner.run_all_tests(include_performance=True, include_stress=False)
    return results

async def run_quick_wiki_tests():
    """Run quick wiki integration tests (no stress tests)"""
    runner = WikiIntegrationTestRunner()
    results = await runner.run_all_tests(include_performance=False, include_stress=False)
    return results

async def run_performance_wiki_tests():
    """Run only performance wiki tests"""
    runner = WikiIntegrationTestRunner()
    results = await runner.run_specific_test_category("performance")
    return results

async def run_end_to_end_wiki_tests():
    """Run only end-to-end wiki tests"""
    runner = WikiIntegrationTestRunner()
    results = await runner.run_specific_test_category("end_to_end")
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Wiki Integration Test Runner")
    parser.add_argument("--category", choices=["all", "end_to_end", "performance", "quick"], 
                       default="all", help="Test category to run")
    parser.add_argument("--stress", action="store_true", 
                       help="Include stress tests (longer execution)")
    
    args = parser.parse_args()
    
    async def main():
        runner = WikiIntegrationTestRunner()
        
        if args.category == "quick":
            results = await runner.run_all_tests(include_performance=False, include_stress=False)
        elif args.category == "all":
            results = await runner.run_all_tests(include_performance=True, include_stress=args.stress)
        else:
            results = await runner.run_specific_test_category(args.category)
        
        # Exit with appropriate code
        exit_code = 0 if results["failed_tests"] == 0 else 1
        print(f"\nExiting with code: {exit_code}")
        sys.exit(exit_code)
    
    asyncio.run(main())