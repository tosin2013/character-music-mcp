#!/usr/bin/env python3
"""
Large Input Processing Performance Tests

Tests system performance with very long narrative texts, complex multi-character
scenarios, and validates memory usage patterns and processing time limits.
"""

import asyncio
import sys
import os
import time
import gc
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Mock psutil for testing without it
    class MockProcess:
        def memory_info(self):
            class MockMemInfo:
                rss = 100 * 1024 * 1024  # 100MB mock
                vms = 200 * 1024 * 1024  # 200MB mock
            return MockMemInfo()
        
        def cpu_percent(self):
            return 10.0  # Mock 10% CPU usage
    
    class MockPsutil:
        def Process(self, pid=None):
            return MockProcess()
        
        def virtual_memory(self):
            class MockVMem:
                total = 8 * 1024 * 1024 * 1024  # 8GB mock
                available = 4 * 1024 * 1024 * 1024  # 4GB mock
                percent = 50.0
            return MockVMem()
    
    psutil = MockPsutil()
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from enhanced_server import (
    CharacterAnalyzer, PersonaGenerator, SunoCommandGenerator,
    CharacterProfile, ArtistPersona, SunoCommand
)
from tests.fixtures.mock_contexts import create_mock_context
from tests.fixtures.test_data import TestDataManager


@dataclass
class PerformanceMetrics:
    """Performance measurement results"""
    processing_time: float
    memory_usage_mb: float
    peak_memory_mb: float
    character_count: int
    text_length: int
    success: bool
    error_message: Optional[str] = None


class LargeInputGenerator:
    """Generates large test inputs for performance testing"""
    
    def __init__(self):
        self.base_narratives = {
            "character_focused": """
            Elena Rodriguez stood in her cramped studio apartment, paintbrush trembling 
            in her hand as she stared at the blank canvas. At twenty-eight, she had already 
            given up three different career paths, each time running when success seemed within reach.
            
            The phone rang, startling her from her thoughts. It was David, her best friend 
            since art school and the only person who truly understood her creative struggles.
            """,
            
            "multi_character": """
            The coffee shop buzzed with the morning rush as five strangers found themselves 
            drawn together by circumstance. Sarah, the barista with dreams of becoming a writer, 
            watched as Marcus, the grieving widower, sat alone at his usual table. 
            
            Dr. Catherine Wells entered, her psychiatric training evident in how she observed 
            the room's dynamics. Meanwhile, Captain Zara Okafor, on leave from her space command, 
            studied the interactions with tactical precision. Finally, Maya Patel, working 
            remotely from her corner table, noticed how they all seemed connected by invisible threads.
            """,
            
            "philosophical": """
            The Philosopher sat in contemplation, wrestling with the fundamental questions 
            that had plagued humanity since consciousness first emerged. What is the nature 
            of existence? How do we find meaning in an apparently meaningless universe? 
            These questions echoed through the corridors of his mind like ancient prayers.
            """
        }
    
    def generate_large_narrative(self, base_type: str, target_words: int) -> str:
        """Generate a large narrative by expanding base content"""
        if base_type not in self.base_narratives:
            base_type = "character_focused"
        
        base_text = self.base_narratives[base_type]
        base_words = len(base_text.split())
        
        # Calculate how many repetitions/expansions needed
        multiplier = max(1, target_words // base_words)
        
        # Create variations to avoid exact repetition
        variations = []
        for i in range(multiplier):
            variation = self._create_variation(base_text, i)
            variations.append(variation)
        
        # Add connecting narrative
        connecting_text = self._generate_connecting_narrative(base_type, multiplier)
        
        # Combine all parts
        full_narrative = "\n\n".join(variations + [connecting_text])
        
        # Trim to approximate target length
        words = full_narrative.split()
        if len(words) > target_words:
            words = words[:target_words]
            full_narrative = " ".join(words)
        
        return full_narrative
    
    def _create_variation(self, base_text: str, variation_index: int) -> str:
        """Create a variation of the base text"""
        # Simple variation by adding context and time progression
        time_markers = [
            "Earlier that day,", "Later that evening,", "The next morning,",
            "Hours later,", "As the day progressed,", "Meanwhile,",
            "In another moment,", "Subsequently,", "At the same time,"
        ]
        
        marker = time_markers[variation_index % len(time_markers)]
        return f"{marker} {base_text}"
    
    def _generate_connecting_narrative(self, base_type: str, sections: int) -> str:
        """Generate connecting narrative to link sections"""
        if base_type == "multi_character":
            return f"""
            As these {sections} interconnected stories unfolded, the complexity of human 
            relationships became increasingly apparent. Each character's journey intersected 
            with the others in ways both subtle and profound, creating a tapestry of 
            experiences that spoke to the universal nature of struggle, growth, and connection.
            
            The narrative threads wove together like a symphony, each voice contributing 
            its unique melody to the larger composition. Through their individual challenges 
            and triumphs, a greater story emerged - one of resilience, hope, and the 
            enduring power of human connection in an often isolating world.
            """
        elif base_type == "philosophical":
            return f"""
            Through {sections} layers of contemplation, the philosophical journey deepened. 
            Each level of understanding revealed new questions, new paradoxes to explore. 
            The search for meaning became not just an intellectual exercise, but a lived 
            experience of grappling with existence itself.
            
            The complexity of thought mirrored the complexity of being, with each insight 
            leading to further mysteries. This was the nature of philosophical inquiry - 
            not to find final answers, but to engage more deeply with the questions that 
            define human consciousness.
            """
        else:
            return f"""
            Through {sections} chapters of this journey, the character's evolution became 
            clear. Each phase of growth built upon the last, creating a rich narrative 
            of transformation and self-discovery. The story's complexity reflected the 
            intricate nature of human development and the many factors that shape our 
            understanding of ourselves and our place in the world.
            """
    
    def generate_complex_multi_character_narrative(self, character_count: int) -> str:
        """Generate complex narrative with specified number of characters"""
        character_templates = [
            "Elena Rodriguez, the struggling artist with trembling hands and fierce determination",
            "Marcus Thompson, the grieving widower finding new purpose in unexpected places", 
            "Dr. Catherine Wells, the psychiatrist questioning her own grip on reality",
            "Captain Zara Okafor, the space commander adapting to life on solid ground",
            "Maya Patel, the remote worker seeking connection in an isolated world",
            "Detective Riley Santos, the cop with supernatural abilities she tries to suppress",
            "Amelia Hartwell, the Victorian mathematician hiding her genius behind propriety",
            "Alex Kim, the young musician torn between tradition and artistic freedom",
            "Rosa Delgado, the family matriarch preserving stories through recipes",
            "The Philosopher, wrestling with existential questions in his book-lined study"
        ]
        
        # Select characters based on count
        selected_characters = character_templates[:character_count]
        
        # Generate interconnected narrative
        narrative_parts = []
        
        # Introduction
        narrative_parts.append(f"""
        In the sprawling metropolis where {character_count} lives intersected, 
        each person carried their own burden of dreams, fears, and unspoken longings. 
        Their stories would weave together in ways none of them could anticipate, 
        creating a complex tapestry of human experience.
        """)
        
        # Individual character sections
        for i, character in enumerate(selected_characters):
            section = f"""
            {character} moved through their daily routine, unaware that their path 
            would soon cross with others facing similar struggles. Each carried the weight 
            of their personal history - formative experiences that had shaped their worldview, 
            relationships that had defined their understanding of connection, and internal 
            conflicts that drove their deepest motivations.
            
            The complexity of their inner life reflected in their external actions, 
            creating ripple effects that would touch the lives of strangers in profound ways. 
            Their fears and desires, spoken and unspoken, created an invisible network 
            of shared humanity that transcended individual circumstances.
            """
            narrative_parts.append(section)
        
        # Interconnection section
        narrative_parts.append(f"""
        As fate would have it, these {character_count} individuals found themselves 
        drawn together by circumstances beyond their control. A chance encounter at 
        a coffee shop, a delayed train, a community event - the specific catalyst 
        mattered less than the profound connections that emerged.
        
        Each person brought their unique perspective to the group dynamic, their 
        individual struggles creating a collective strength none had experienced alone. 
        The relationships that formed challenged their preconceptions, forced growth 
        in unexpected directions, and ultimately revealed the transformative power 
        of authentic human connection.
        
        Through their interactions, deeper themes emerged: the search for meaning 
        in an uncertain world, the courage required for vulnerability, the healing 
        that comes from being truly seen and understood. Their individual journeys 
        became part of a larger narrative about resilience, hope, and the enduring 
        capacity for human beings to support one another through life's challenges.
        """)
        
        return "\n\n".join(narrative_parts)


class LargeInputPerformanceTester:
    """Performance tester for large input processing"""
    
    def __init__(self):
        self.generator = LargeInputGenerator()
        self.character_analyzer = CharacterAnalyzer()
        self.persona_generator = PersonaGenerator()
        self.command_generator = SunoCommandGenerator()
        
        # Performance thresholds (from requirements)
        self.thresholds = {
            "max_processing_time": 30.0,  # 30 seconds for very large inputs
            "max_memory_usage_mb": 1000,   # 1GB max memory usage
            "min_characters_detected": 1,   # At least 1 character should be found
            "max_memory_growth_mb": 500    # Max 500MB memory growth during processing
        }
    
    async def test_10k_word_narrative(self) -> PerformanceMetrics:
        """Test processing of 10,000+ word narrative"""
        print("🔍 Testing 10k+ word narrative processing...")
        
        # Generate large narrative
        large_narrative = self.generator.generate_large_narrative("character_focused", 10000)
        actual_words = len(large_narrative.split())
        
        return await self._measure_processing_performance(
            large_narrative, f"10k_words_actual_{actual_words}"
        )
    
    async def test_complex_multi_character_narrative(self, character_count: int = 8) -> PerformanceMetrics:
        """Test processing of complex multi-character narrative"""
        print(f"🔍 Testing complex {character_count}-character narrative...")
        
        # Generate complex narrative
        complex_narrative = self.generator.generate_complex_multi_character_narrative(character_count)
        
        return await self._measure_processing_performance(
            complex_narrative, f"multi_character_{character_count}"
        )
    
    async def test_extremely_long_narrative(self) -> PerformanceMetrics:
        """Test processing of extremely long narrative (20k+ words)"""
        print("🔍 Testing extremely long narrative (20k+ words)...")
        
        # Generate very large narrative
        huge_narrative = self.generator.generate_large_narrative("multi_character", 20000)
        actual_words = len(huge_narrative.split())
        
        return await self._measure_processing_performance(
            huge_narrative, f"extreme_length_{actual_words}"
        )
    
    async def test_philosophical_complexity(self) -> PerformanceMetrics:
        """Test processing of philosophically complex narrative"""
        print("🔍 Testing philosophically complex narrative...")
        
        # Generate complex philosophical narrative
        philosophical_narrative = self.generator.generate_large_narrative("philosophical", 15000)
        
        return await self._measure_processing_performance(
            philosophical_narrative, "philosophical_complex"
        )
    
    async def _measure_processing_performance(self, narrative: str, test_name: str) -> PerformanceMetrics:
        """Measure performance of processing a narrative"""
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Force garbage collection before test
        gc.collect()
        
        start_time = time.time()
        peak_memory = initial_memory
        success = False
        error_message = None
        character_count = 0
        
        try:
            # Create mock context
            ctx = create_mock_context("performance_test", session_id=f"large_input_{test_name}")
            
            # Monitor memory during processing
            async def memory_monitor():
                nonlocal peak_memory
                while True:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    peak_memory = max(peak_memory, current_memory)
                    await asyncio.sleep(0.1)  # Check every 100ms
            
            # Start memory monitoring
            monitor_task = asyncio.create_task(memory_monitor())
            
            try:
                # Step 1: Character Analysis
                print(f"  📊 Analyzing characters in {len(narrative.split())} word narrative...")
                characters = await self.character_analyzer.analyze_character_text(ctx, narrative)
                character_count = len(characters)
                
                if character_count > 0:
                    # Step 2: Persona Generation (for primary character)
                    print(f"  🎭 Generating persona for primary character...")
                    primary_character = max(characters, key=lambda c: c.importance_score)
                    persona = await self.persona_generator.generate_artist_personas(
                        ctx, [primary_character]
                    )
                    
                    # Step 3: Command Generation
                    print(f"  🎵 Generating Suno commands...")
                    if persona:
                        commands = await self.command_generator.create_suno_commands(
                            ctx, persona[0], primary_character
                        )
                
                success = True
                
            finally:
                # Stop memory monitoring
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass
        
        except Exception as e:
            error_message = str(e)
            print(f"  ❌ Error during processing: {error_message}")
        
        # Calculate final metrics
        end_time = time.time()
        processing_time = end_time - start_time
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_usage = final_memory - initial_memory
        
        # Force garbage collection after test
        gc.collect()
        
        metrics = PerformanceMetrics(
            processing_time=processing_time,
            memory_usage_mb=memory_usage,
            peak_memory_mb=peak_memory,
            character_count=character_count,
            text_length=len(narrative),
            success=success,
            error_message=error_message
        )
        
        # Print results
        self._print_performance_results(test_name, metrics)
        
        return metrics
    
    def _print_performance_results(self, test_name: str, metrics: PerformanceMetrics) -> None:
        """Print performance test results"""
        status = "✅" if metrics.success else "❌"
        print(f"  {status} {test_name} Results:")
        print(f"    ⏱️  Processing Time: {metrics.processing_time:.2f}s")
        print(f"    💾 Memory Usage: {metrics.memory_usage_mb:.1f}MB")
        print(f"    📈 Peak Memory: {metrics.peak_memory_mb:.1f}MB")
        print(f"    👥 Characters Found: {metrics.character_count}")
        print(f"    📝 Text Length: {metrics.text_length:,} chars")
        
        # Check against thresholds
        if metrics.processing_time > self.thresholds["max_processing_time"]:
            print(f"    ⚠️  Processing time exceeded threshold ({self.thresholds['max_processing_time']}s)")
        
        if metrics.peak_memory_mb > self.thresholds["max_memory_usage_mb"]:
            print(f"    ⚠️  Memory usage exceeded threshold ({self.thresholds['max_memory_usage_mb']}MB)")
        
        if metrics.character_count < self.thresholds["min_characters_detected"]:
            print(f"    ⚠️  Too few characters detected (min: {self.thresholds['min_characters_detected']})")
        
        if metrics.error_message:
            print(f"    ❌ Error: {metrics.error_message}")
    
    def validate_performance_requirements(self, metrics: PerformanceMetrics) -> Dict[str, bool]:
        """Validate performance against requirements"""
        return {
            "processing_time_acceptable": metrics.processing_time <= self.thresholds["max_processing_time"],
            "memory_usage_acceptable": metrics.peak_memory_mb <= self.thresholds["max_memory_usage_mb"],
            "characters_detected": metrics.character_count >= self.thresholds["min_characters_detected"],
            "processing_successful": metrics.success,
            "memory_growth_acceptable": metrics.memory_usage_mb <= self.thresholds["max_memory_growth_mb"]
        }


# Test functions for integration with test runner
async def test_large_narrative_processing_10k():
    """Test processing of 10k+ word narratives"""
    tester = LargeInputPerformanceTester()
    metrics = await tester.test_10k_word_narrative()
    
    # Validate requirements
    validation = tester.validate_performance_requirements(metrics)
    
    assert metrics.success, f"Processing failed: {metrics.error_message}"
    assert validation["processing_time_acceptable"], f"Processing time too slow: {metrics.processing_time}s"
    assert validation["memory_usage_acceptable"], f"Memory usage too high: {metrics.peak_memory_mb}MB"
    assert validation["characters_detected"], f"No characters detected in large narrative"


async def test_complex_multi_character_processing():
    """Test processing of complex multi-character narratives"""
    tester = LargeInputPerformanceTester()
    metrics = await tester.test_complex_multi_character_narrative(6)
    
    # Validate requirements
    validation = tester.validate_performance_requirements(metrics)
    
    assert metrics.success, f"Multi-character processing failed: {metrics.error_message}"
    assert metrics.character_count >= 3, f"Expected multiple characters, found {metrics.character_count}"
    assert validation["processing_time_acceptable"], f"Processing time too slow: {metrics.processing_time}s"


async def test_extremely_long_narrative_processing():
    """Test processing of extremely long narratives (20k+ words)"""
    tester = LargeInputPerformanceTester()
    metrics = await tester.test_extremely_long_narrative()
    
    # Validate requirements
    validation = tester.validate_performance_requirements(metrics)
    
    assert metrics.success, f"Extreme length processing failed: {metrics.error_message}"
    assert validation["memory_growth_acceptable"], f"Memory growth too high: {metrics.memory_usage_mb}MB"


async def test_philosophical_complexity_processing():
    """Test processing of philosophically complex narratives"""
    tester = LargeInputPerformanceTester()
    metrics = await tester.test_philosophical_complexity()
    
    # Validate requirements
    validation = tester.validate_performance_requirements(metrics)
    
    assert metrics.success, f"Philosophical processing failed: {metrics.error_message}"
    assert validation["processing_successful"], "Processing should handle complex philosophical content"


async def test_memory_usage_patterns():
    """Test memory usage patterns during large input processing"""
    tester = LargeInputPerformanceTester()
    
    # Test multiple scenarios to check memory patterns
    scenarios = [
        ("small", 1000),
        ("medium", 5000), 
        ("large", 10000)
    ]
    
    memory_results = []
    
    for scenario_name, word_count in scenarios:
        narrative = tester.generator.generate_large_narrative("character_focused", word_count)
        metrics = await tester._measure_processing_performance(narrative, f"memory_test_{scenario_name}")
        memory_results.append((word_count, metrics.memory_usage_mb))
    
    # Validate that memory usage scales reasonably
    for i in range(1, len(memory_results)):
        prev_words, prev_memory = memory_results[i-1]
        curr_words, curr_memory = memory_results[i]
        
        # Memory should not grow exponentially
        word_ratio = curr_words / prev_words
        memory_ratio = curr_memory / prev_memory if prev_memory > 0 else 1
        
        assert memory_ratio <= word_ratio * 2, f"Memory growth too steep: {memory_ratio}x for {word_ratio}x words"


# Main execution for standalone testing
async def main():
    """Main function for standalone performance testing"""
    print("🚀 Large Input Performance Testing")
    print("=" * 50)
    
    tester = LargeInputPerformanceTester()
    
    # Run all performance tests
    tests = [
        ("10k Word Narrative", tester.test_10k_word_narrative),
        ("Complex Multi-Character", lambda: tester.test_complex_multi_character_narrative(8)),
        ("Extremely Long Narrative", tester.test_extremely_long_narrative),
        ("Philosophical Complexity", tester.test_philosophical_complexity)
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
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE TEST SUMMARY")
    print("=" * 50)
    
    successful_tests = 0
    total_tests = len(results)
    
    for test_name, metrics in results:
        if metrics and metrics.success:
            successful_tests += 1
            status = "✅"
            validation = tester.validate_performance_requirements(metrics)
            all_valid = all(validation.values())
            perf_status = "✅" if all_valid else "⚠️"
            print(f"{status} {test_name}: {perf_status} {metrics.processing_time:.2f}s, {metrics.peak_memory_mb:.1f}MB")
        else:
            print(f"❌ {test_name}: Failed")
    
    print(f"\n🎯 Results: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests == total_tests:
        print("🎉 All large input performance tests passed!")
        return True
    else:
        print("⚠️ Some performance tests failed or exceeded thresholds")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)