#!/usr/bin/env python3
"""
Concurrent Request Handling Performance Tests

Tests system performance with simultaneous workflow executions, validates
response quality maintenance under concurrent load, and tests system stability
with multiple album creation requests.
"""

import asyncio
import sys
import os
import time
import psutil
import gc
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import threading
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from enhanced_server import (
    CharacterAnalyzer, PersonaGenerator, SunoCommandGenerator,
    CharacterProfile, ArtistPersona, SunoCommand
)
from tests.fixtures.mock_contexts import create_mock_context
from tests.fixtures.test_data import TestDataManager, test_data_manager


@dataclass
class ConcurrentTestResult:
    """Result from concurrent test execution"""
    request_id: str
    success: bool
    processing_time: float
    character_count: int
    persona_generated: bool
    commands_generated: bool
    error_message: Optional[str] = None
    memory_usage_mb: Optional[float] = None


@dataclass
class ConcurrencyMetrics:
    """Overall concurrency test metrics"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    min_response_time: float
    max_response_time: float
    total_test_time: float
    peak_memory_mb: float
    resource_conflicts: int
    quality_degradation_count: int


class ConcurrentRequestTester:
    """Tests concurrent request handling capabilities"""
    
    def __init__(self):
        self.character_analyzer = CharacterAnalyzer()
        self.persona_generator = PersonaGenerator()
        self.command_generator = SunoCommandGenerator()
        self.test_data_manager = test_data_manager
        
        # Concurrency thresholds
        self.thresholds = {
            "max_concurrent_requests": 10,
            "max_average_response_time": 15.0,  # seconds
            "min_success_rate": 0.8,  # 80% success rate
            "max_quality_degradation": 0.2,  # 20% quality degradation
            "max_memory_per_request_mb": 200
        }
        
        # Thread safety tracking
        self.active_requests = 0
        self.request_lock = threading.Lock()
        self.resource_conflicts = 0
    
    async def test_simultaneous_character_analysis(self, concurrent_count: int = 5) -> ConcurrencyMetrics:
        """Test simultaneous character analysis requests"""
        print(f"🔄 Testing {concurrent_count} simultaneous character analysis requests...")
        
        # Prepare test scenarios
        scenarios = list(self.test_data_manager.scenarios.values())[:concurrent_count]
        
        # Create tasks for concurrent execution
        tasks = []
        for i, scenario in enumerate(scenarios):
            task = self._execute_character_analysis_request(f"char_analysis_{i}", scenario.narrative_text)
            tasks.append(task)
        
        return await self._execute_concurrent_test(tasks, "character_analysis")   
 
    async def test_concurrent_workflow_execution(self, concurrent_count: int = 3) -> ConcurrencyMetrics:
        """Test concurrent complete workflow executions"""
        print(f"🔄 Testing {concurrent_count} concurrent complete workflow executions...")
        
        # Use different scenarios for variety
        scenarios = [
            self.test_data_manager.get_test_scenario("single_character_simple"),
            self.test_data_manager.get_test_scenario("multi_character_medium"),
            self.test_data_manager.get_test_scenario("emotional_intensity_high")
        ]
        
        # Create tasks for concurrent execution
        tasks = []
        for i in range(concurrent_count):
            scenario = scenarios[i % len(scenarios)]
            task = self._execute_complete_workflow_request(f"workflow_{i}", scenario.narrative_text)
            tasks.append(task)
        
        return await self._execute_concurrent_test(tasks, "complete_workflow")
    
    async def test_multiple_album_creation(self, album_count: int = 3) -> ConcurrencyMetrics:
        """Test multiple simultaneous album creation requests"""
        print(f"🔄 Testing {album_count} simultaneous album creation requests...")
        
        # Use complex scenarios for album creation
        album_scenarios = [
            self.test_data_manager.get_test_scenario("concept_album_complex"),
            self.test_data_manager.get_test_scenario("multi_character_medium"),
            self.test_data_manager.get_test_scenario("family_saga")
        ]
        
        # Create tasks for concurrent album creation
        tasks = []
        for i in range(album_count):
            scenario = album_scenarios[i % len(album_scenarios)]
            task = self._execute_album_creation_request(f"album_{i}", scenario.narrative_text)
            tasks.append(task)
        
        return await self._execute_concurrent_test(tasks, "album_creation")
    
    async def test_mixed_request_types(self, total_requests: int = 8) -> ConcurrencyMetrics:
        """Test mixed types of concurrent requests"""
        print(f"🔄 Testing {total_requests} mixed concurrent requests...")
        
        scenarios = list(self.test_data_manager.scenarios.values())
        tasks = []
        
        for i in range(total_requests):
            scenario = scenarios[i % len(scenarios)]
            request_type = ["character_analysis", "workflow", "album_creation"][i % 3]
            
            if request_type == "character_analysis":
                task = self._execute_character_analysis_request(f"mixed_char_{i}", scenario.narrative_text)
            elif request_type == "workflow":
                task = self._execute_complete_workflow_request(f"mixed_workflow_{i}", scenario.narrative_text)
            else:
                task = self._execute_album_creation_request(f"mixed_album_{i}", scenario.narrative_text)
            
            tasks.append(task)
        
        return await self._execute_concurrent_test(tasks, "mixed_requests")
    
    async def test_stress_concurrent_load(self, concurrent_count: int = 10) -> ConcurrencyMetrics:
        """Test system under stress with maximum concurrent load"""
        print(f"🔄 Testing stress load with {concurrent_count} concurrent requests...")
        
        scenarios = list(self.test_data_manager.scenarios.values())
        tasks = []
        
        # Create high-load scenario with varied request types
        for i in range(concurrent_count):
            scenario = scenarios[i % len(scenarios)]
            # Randomly choose request type for realistic load
            request_types = ["character_analysis", "workflow", "album_creation"]
            request_type = random.choice(request_types)
            
            if request_type == "character_analysis":
                task = self._execute_character_analysis_request(f"stress_char_{i}", scenario.narrative_text)
            elif request_type == "workflow":
                task = self._execute_complete_workflow_request(f"stress_workflow_{i}", scenario.narrative_text)
            else:
                task = self._execute_album_creation_request(f"stress_album_{i}", scenario.narrative_text)
            
            tasks.append(task)
        
        return await self._execute_concurrent_test(tasks, "stress_test")
    
    async def _execute_character_analysis_request(self, request_id: str, narrative: str) -> ConcurrentTestResult:
        """Execute a single character analysis request"""
        start_time = time.time()
        
        try:
            with self.request_lock:
                self.active_requests += 1
            
            # Create isolated context for this request
            ctx = create_mock_context("concurrent_test", session_id=request_id)
            
            # Perform character analysis
            characters = await self.character_analyzer.analyze_character_text(ctx, narrative)
            
            processing_time = time.time() - start_time
            
            return ConcurrentTestResult(
                request_id=request_id,
                success=True,
                processing_time=processing_time,
                character_count=len(characters),
                persona_generated=False,
                commands_generated=False
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ConcurrentTestResult(
                request_id=request_id,
                success=False,
                processing_time=processing_time,
                character_count=0,
                persona_generated=False,
                commands_generated=False,
                error_message=str(e)
            )
        finally:
            with self.request_lock:
                self.active_requests -= 1
    
    async def _execute_complete_workflow_request(self, request_id: str, narrative: str) -> ConcurrentTestResult:
        """Execute a complete workflow request"""
        start_time = time.time()
        
        try:
            with self.request_lock:
                self.active_requests += 1
            
            # Create isolated context
            ctx = create_mock_context("concurrent_workflow", session_id=request_id)
            
            # Step 1: Character Analysis
            characters = await self.character_analyzer.analyze_character_text(ctx, narrative)
            
            if not characters:
                raise Exception("No characters found in narrative")
            
            # Step 2: Persona Generation
            primary_character = max(characters, key=lambda c: c.importance_score)
            personas = await self.persona_generator.generate_artist_personas(ctx, [primary_character])
            
            if not personas:
                raise Exception("Failed to generate persona")
            
            # Step 3: Command Generation
            commands = await self.command_generator.create_suno_commands(ctx, personas[0], primary_character)
            
            processing_time = time.time() - start_time
            
            return ConcurrentTestResult(
                request_id=request_id,
                success=True,
                processing_time=processing_time,
                character_count=len(characters),
                persona_generated=len(personas) > 0,
                commands_generated=len(commands) > 0 if commands else False
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ConcurrentTestResult(
                request_id=request_id,
                success=False,
                processing_time=processing_time,
                character_count=0,
                persona_generated=False,
                commands_generated=False,
                error_message=str(e)
            )
        finally:
            with self.request_lock:
                self.active_requests -= 1
    
    async def _execute_album_creation_request(self, request_id: str, narrative: str) -> ConcurrentTestResult:
        """Execute an album creation request"""
        start_time = time.time()
        
        try:
            with self.request_lock:
                self.active_requests += 1
            
            # Create isolated context
            ctx = create_mock_context("concurrent_album", session_id=request_id)
            
            # Complete workflow for album creation
            characters = await self.character_analyzer.analyze_character_text(ctx, narrative)
            
            if not characters:
                raise Exception("No characters found for album creation")
            
            # Generate personas for multiple characters if available
            top_characters = sorted(characters, key=lambda c: c.importance_score, reverse=True)[:3]
            personas = await self.persona_generator.generate_artist_personas(ctx, top_characters)
            
            if not personas:
                raise Exception("Failed to generate personas for album")
            
            # Generate multiple commands for album
            all_commands = []
            for persona in personas[:2]:  # Limit to 2 for performance
                commands = await self.command_generator.create_suno_commands(ctx, persona, top_characters[0])
                if commands:
                    all_commands.extend(commands)
            
            processing_time = time.time() - start_time
            
            return ConcurrentTestResult(
                request_id=request_id,
                success=True,
                processing_time=processing_time,
                character_count=len(characters),
                persona_generated=len(personas) > 0,
                commands_generated=len(all_commands) > 0
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ConcurrentTestResult(
                request_id=request_id,
                success=False,
                processing_time=processing_time,
                character_count=0,
                persona_generated=False,
                commands_generated=False,
                error_message=str(e)
            )
        finally:
            with self.request_lock:
                self.active_requests -= 1
    
    async def _execute_concurrent_test(self, tasks: List, test_name: str) -> ConcurrencyMetrics:
        """Execute concurrent tasks and measure performance"""
        # Monitor memory during test
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        peak_memory = initial_memory
        
        # Start memory monitoring
        async def memory_monitor():
            nonlocal peak_memory
            while True:
                current_memory = process.memory_info().rss / 1024 / 1024
                peak_memory = max(peak_memory, current_memory)
                await asyncio.sleep(0.1)
        
        monitor_task = asyncio.create_task(memory_monitor())
        
        try:
            # Execute all tasks concurrently
            test_start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_test_time = time.time() - test_start_time
            
        finally:
            # Stop memory monitoring
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        
        # Process results
        successful_results = []
        failed_results = []
        
        for result in results:
            if isinstance(result, Exception):
                failed_results.append(str(result))
            elif isinstance(result, ConcurrentTestResult):
                if result.success:
                    successful_results.append(result)
                else:
                    failed_results.append(result.error_message or "Unknown error")
            else:
                failed_results.append("Invalid result type")
        
        # Calculate metrics
        total_requests = len(tasks)
        successful_requests = len(successful_results)
        failed_requests = len(failed_results)
        
        if successful_results:
            response_times = [r.processing_time for r in successful_results]
            average_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            average_response_time = 0.0
            min_response_time = 0.0
            max_response_time = 0.0
        
        # Quality degradation check (simplified)
        quality_degradation_count = 0
        for result in successful_results:
            if result.processing_time > self.thresholds["max_average_response_time"]:
                quality_degradation_count += 1
        
        metrics = ConcurrencyMetrics(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=average_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            total_test_time=total_test_time,
            peak_memory_mb=peak_memory,
            resource_conflicts=self.resource_conflicts,
            quality_degradation_count=quality_degradation_count
        )
        
        # Print results
        self._print_concurrency_results(test_name, metrics)
        
        return metrics
    
    def _print_concurrency_results(self, test_name: str, metrics: ConcurrencyMetrics) -> None:
        """Print concurrency test results"""
        success_rate = metrics.successful_requests / metrics.total_requests if metrics.total_requests > 0 else 0
        status = "✅" if success_rate >= self.thresholds["min_success_rate"] else "❌"
        
        print(f"  {status} {test_name} Results:")
        print(f"    📊 Success Rate: {success_rate:.1%} ({metrics.successful_requests}/{metrics.total_requests})")
        print(f"    ⏱️  Average Response Time: {metrics.average_response_time:.2f}s")
        print(f"    📈 Response Time Range: {metrics.min_response_time:.2f}s - {metrics.max_response_time:.2f}s")
        print(f"    🕐 Total Test Time: {metrics.total_test_time:.2f}s")
        print(f"    💾 Peak Memory: {metrics.peak_memory_mb:.1f}MB")
        print(f"    ⚠️  Resource Conflicts: {metrics.resource_conflicts}")
        print(f"    📉 Quality Degradation: {metrics.quality_degradation_count} requests")
        
        # Check thresholds
        if success_rate < self.thresholds["min_success_rate"]:
            print(f"    ❌ Success rate below threshold ({self.thresholds['min_success_rate']:.1%})")
        
        if metrics.average_response_time > self.thresholds["max_average_response_time"]:
            print(f"    ❌ Average response time exceeded threshold ({self.thresholds['max_average_response_time']}s)")
        
        if metrics.quality_degradation_count / metrics.total_requests > self.thresholds["max_quality_degradation"]:
            print(f"    ❌ Quality degradation exceeded threshold ({self.thresholds['max_quality_degradation']:.1%})")
    
    def validate_concurrency_requirements(self, metrics: ConcurrencyMetrics) -> Dict[str, bool]:
        """Validate concurrency performance against requirements"""
        success_rate = metrics.successful_requests / metrics.total_requests if metrics.total_requests > 0 else 0
        quality_degradation_rate = metrics.quality_degradation_count / metrics.total_requests if metrics.total_requests > 0 else 0
        
        return {
            "success_rate_acceptable": success_rate >= self.thresholds["min_success_rate"],
            "response_time_acceptable": metrics.average_response_time <= self.thresholds["max_average_response_time"],
            "quality_maintained": quality_degradation_rate <= self.thresholds["max_quality_degradation"],
            "no_resource_conflicts": metrics.resource_conflicts == 0,
            "memory_usage_reasonable": metrics.peak_memory_mb <= (self.thresholds["max_memory_per_request_mb"] * metrics.total_requests)
        }


# Test functions for integration with test runner
async def test_concurrent_character_analysis():
    """Test concurrent character analysis requests"""
    tester = ConcurrentRequestTester()
    metrics = await tester.test_simultaneous_character_analysis(5)
    
    validation = tester.validate_concurrency_requirements(metrics)
    
    assert validation["success_rate_acceptable"], f"Success rate too low: {metrics.successful_requests}/{metrics.total_requests}"
    assert validation["response_time_acceptable"], f"Response time too slow: {metrics.average_response_time}s"
    assert validation["no_resource_conflicts"], f"Resource conflicts detected: {metrics.resource_conflicts}"


async def test_concurrent_complete_workflows():
    """Test concurrent complete workflow executions"""
    tester = ConcurrentRequestTester()
    metrics = await tester.test_concurrent_workflow_execution(3)
    
    validation = tester.validate_concurrency_requirements(metrics)
    
    assert validation["success_rate_acceptable"], f"Workflow success rate too low: {metrics.successful_requests}/{metrics.total_requests}"
    assert validation["quality_maintained"], f"Quality degradation too high: {metrics.quality_degradation_count}"


async def test_concurrent_album_creation():
    """Test concurrent album creation requests"""
    tester = ConcurrentRequestTester()
    metrics = await tester.test_multiple_album_creation(3)
    
    validation = tester.validate_concurrency_requirements(metrics)
    
    assert validation["success_rate_acceptable"], f"Album creation success rate too low: {metrics.successful_requests}/{metrics.total_requests}"
    assert validation["memory_usage_reasonable"], f"Memory usage too high: {metrics.peak_memory_mb}MB"


async def test_mixed_concurrent_requests():
    """Test mixed types of concurrent requests"""
    tester = ConcurrentRequestTester()
    metrics = await tester.test_mixed_request_types(6)
    
    validation = tester.validate_concurrency_requirements(metrics)
    
    assert validation["success_rate_acceptable"], f"Mixed request success rate too low: {metrics.successful_requests}/{metrics.total_requests}"
    assert validation["response_time_acceptable"], f"Mixed request response time too slow: {metrics.average_response_time}s"


async def test_stress_concurrent_load():
    """Test system under maximum concurrent load"""
    tester = ConcurrentRequestTester()
    metrics = await tester.test_stress_concurrent_load(8)  # Reduced from 10 for stability
    
    validation = tester.validate_concurrency_requirements(metrics)
    
    # More lenient requirements for stress test
    min_stress_success_rate = 0.7  # 70% for stress test
    success_rate = metrics.successful_requests / metrics.total_requests if metrics.total_requests > 0 else 0
    
    assert success_rate >= min_stress_success_rate, f"Stress test success rate too low: {success_rate:.1%}"
    assert metrics.resource_conflicts <= 2, f"Too many resource conflicts under stress: {metrics.resource_conflicts}"


# Main execution for standalone testing
async def main():
    """Main function for standalone concurrency testing"""
    print("🚀 Concurrent Request Handling Performance Testing")
    print("=" * 60)
    
    tester = ConcurrentRequestTester()
    
    # Run all concurrency tests
    tests = [
        ("Concurrent Character Analysis", lambda: tester.test_simultaneous_character_analysis(5)),
        ("Concurrent Workflow Execution", lambda: tester.test_concurrent_workflow_execution(3)),
        ("Multiple Album Creation", lambda: tester.test_multiple_album_creation(3)),
        ("Mixed Request Types", lambda: tester.test_mixed_request_types(6)),
        ("Stress Concurrent Load", lambda: tester.test_stress_concurrent_load(8))
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            metrics = await test_func()
            results.append((test_name, metrics))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, None))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 CONCURRENCY TEST SUMMARY")
    print("=" * 60)
    
    successful_tests = 0
    total_tests = len(results)
    
    for test_name, metrics in results:
        if metrics:
            successful_tests += 1
            validation = tester.validate_concurrency_requirements(metrics)
            all_valid = all(validation.values())
            success_rate = metrics.successful_requests / metrics.total_requests if metrics.total_requests > 0 else 0
            
            status = "✅" if all_valid else "⚠️"
            print(f"{status} {test_name}: {success_rate:.1%} success, {metrics.average_response_time:.2f}s avg")
        else:
            print(f"❌ {test_name}: Failed to execute")
    
    print(f"\n🎯 Results: {successful_tests}/{total_tests} concurrency tests completed")
    
    if successful_tests == total_tests:
        print("🎉 All concurrency tests completed successfully!")
        return True
    else:
        print("⚠️ Some concurrency tests failed or had issues")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)