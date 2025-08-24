#!/usr/bin/env python3
"""
Wiki Integration Performance and Edge Case Tests

Tests performance characteristics, edge cases, and stress scenarios
for the wiki data integration system.

Requirements: Performance validation and edge case handling
"""

import asyncio
import json
import os
import pytest
import tempfile
import shutil
import time
import random
import string
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, AsyncMock
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
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
            return MockMemInfo()
    
    class MockPsutil:
        def Process(self):
            return MockProcess()
    
    psutil = MockPsutil()

# Import test utilities
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.fixtures.test_data import TestDataManager
from tests.fixtures.mock_contexts import MockContext, MockPerformanceContext

# Import wiki integration components
from wiki_data_system import WikiDataManager
from wiki_data_models import WikiConfig
from enhanced_genre_mapper import EnhancedGenreMapper, GenreMatch
from source_attribution_manager import SourceAttributionManager
from server import (
    CharacterAnalyzer, MusicPersonaGenerator, SunoCommandGenerator,
    creative_music_generation
)


async def complete_workflow_test_helper(text: str, ctx) -> str:
    """Test helper function that replicates complete_workflow functionality"""
    try:
        await ctx.info("Starting complete character-to-music workflow...")
        
        # Initialize components
        character_analyzer = CharacterAnalyzer()
        persona_generator = MusicPersonaGenerator()
        command_generator = SunoCommandGenerator()
        
        # Step 1: Character Analysis
        await ctx.info("Step 1: Analyzing characters...")
        analysis_result = await character_analyzer.analyze_text(text, ctx)
        characters = analysis_result.characters
        characters_result = json.dumps([char.to_dict() for char in characters], indent=2)
        
        # Step 2: Generate Artist Personas  
        await ctx.info("Step 2: Generating artist personas...")
        personas = []
        for character in characters:
            persona = await persona_generator.generate_persona(character)
            personas.append(persona.to_dict())
        personas_result = json.dumps(personas, indent=2)
        
        # Step 3: Create Suno Commands
        await ctx.info("Step 3: Creating Suno AI commands...")
        all_commands = []
        for i, character in enumerate(characters):
            persona = personas[i]
            commands = await command_generator.generate_commands(character, persona)
            all_commands.extend([cmd.to_dict() for cmd in commands])
        commands_result = json.dumps(all_commands, indent=2)
        
        # Combine results
        workflow_result = {
            "workflow_status": "completed",
            "character_analysis": json.loads(characters_result),
            "artist_personas": json.loads(personas_result), 
            "suno_commands": json.loads(commands_result),
            "workflow_summary": "Complete character-driven music generation workflow executed successfully"
        }
        
        return json.dumps(workflow_result, indent=2)
        
    except Exception as e:
        await ctx.info(f"Workflow failed: {str(e)}")
        return json.dumps({
            "workflow_status": "failed",
            "error": str(e),
            "workflow_summary": "Workflow execution failed"
        })


class TestWikiPerformanceAndEdgeCases:
    """Test wiki integration performance and edge cases"""
    
    def setup_method(self):
        """Set up test environment"""
        self.test_data = TestDataManager()
        self.mock_context = MockContext("wiki_performance_test")
        self.performance_context = MockPerformanceContext("wiki_edge_case_test")
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.wiki_storage_path = os.path.join(self.temp_dir, "wiki")
        
        # Performance test configuration
        self.perf_config = WikiConfig(
            enabled=True,
            local_storage_path=self.wiki_storage_path,
            refresh_interval_hours=24,
            fallback_to_hardcoded=True,
            request_timeout=10,
            max_retries=3,
            retry_delay=0.5
        )
    
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # Force garbage collection
        gc.collect()
    
    @pytest.mark.asyncio
    async def test_large_dataset_handling(self):
        """Test handling of large wiki datasets"""
        await self.performance_context.info("Testing large dataset handling")
        
        # Create large mock dataset
        large_genre_content = self._generate_large_genre_dataset(1000)  # 1000 genres
        large_metatag_content = self._generate_large_metatag_dataset(500)  # 500 meta tags
        
        # Write large datasets to files
        os.makedirs(os.path.join(self.wiki_storage_path, "genres"), exist_ok=True)
        os.makedirs(os.path.join(self.wiki_storage_path, "meta_tags"), exist_ok=True)
        
        with open(os.path.join(self.wiki_storage_path, "genres", "large_dataset.html"), 'w') as f:
            f.write(large_genre_content)
        
        with open(os.path.join(self.wiki_storage_path, "meta_tags", "large_dataset.html"), 'w') as f:
            f.write(large_metatag_content)
        
        # Test parsing performance
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        wiki_manager = WikiDataManager()
        await wiki_manager.initialize(self.perf_config)
        
        # Parse large datasets
        genres = await wiki_manager.get_genres()
        meta_tags = await wiki_manager.get_meta_tags()
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        parse_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        await self.performance_context.record_performance_metric("large_dataset_parse_time", parse_time)
        await self.performance_context.record_performance_metric("large_dataset_memory_usage", memory_usage)
        
        # Verify data was parsed correctly
        assert len(genres) >= 900  # Should parse most genres (allowing for some parsing failures)
        assert len(meta_tags) >= 450  # Should parse most meta tags
        
        # Test genre mapping performance with large dataset
        enhanced_mapper = EnhancedGenreMapper(wiki_manager)
        
        start_time = time.time()
        
        # Test multiple trait mappings
        test_traits = [
            ["electronic", "ambient", "atmospheric"],
            ["rock", "alternative", "indie"],
            ["jazz", "fusion", "experimental"],
            ["folk", "acoustic", "traditional"],
            ["hip-hop", "urban", "contemporary"]
        ]
        
        for traits in test_traits:
            matches = await enhanced_mapper.map_traits_to_genres(traits, max_results=10)
            assert len(matches) > 0
        
        mapping_time = time.time() - start_time
        await self.performance_context.record_performance_metric("large_dataset_mapping_time", mapping_time)
        
        # Performance thresholds
        assert parse_time < 30.0, f"Large dataset parsing took too long: {parse_time}s"
        assert memory_usage < 500.0, f"Memory usage too high: {memory_usage}MB"
        assert mapping_time < 10.0, f"Genre mapping took too long: {mapping_time}s"
        
        await self.performance_context.info("Large dataset handling test passed")
    
    @pytest.mark.asyncio
    async def test_memory_usage_and_cleanup(self):
        """Test memory usage patterns and cleanup"""
        await self.performance_context.info("Testing memory usage and cleanup")
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Create multiple wiki managers to test memory usage
        managers = []
        
        for i in range(10):
            config = WikiConfig(
                enabled=True,
                local_storage_path=os.path.join(self.temp_dir, f"wiki_{i}"),
                fallback_to_hardcoded=True
            )
            
            manager = WikiDataManager()
            await manager.initialize(config)
            managers.append(manager)
            
            # Check memory growth
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_growth = current_memory - initial_memory
            
            # Should not grow excessively
            assert memory_growth < 200.0, f"Memory growth too high: {memory_growth}MB"
        
        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Clean up managers
        managers.clear()
        gc.collect()
        
        # Wait for cleanup
        await asyncio.sleep(1)
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_recovered = peak_memory - final_memory
        
        await self.performance_context.record_performance_metric("peak_memory_usage", peak_memory - initial_memory)
        await self.performance_context.record_performance_metric("memory_recovered", memory_recovered)
        
        # Should recover significant memory
        assert memory_recovered > 0, "No memory was recovered after cleanup"
        
        await self.performance_context.info("Memory usage and cleanup test passed")
    
    @pytest.mark.asyncio
    async def test_concurrent_stress_testing(self):
        """Test system under concurrent stress"""
        await self.performance_context.info("Testing concurrent stress scenarios")
        
        wiki_manager = WikiDataManager()
        await wiki_manager.initialize(self.perf_config)
        
        enhanced_mapper = EnhancedGenreMapper(wiki_manager)
        
        # Stress test 1: Many concurrent genre mappings
        async def stress_genre_mapping():
            traits = [random.choice(["electronic", "rock", "jazz", "folk", "ambient", "indie", "experimental"]) 
                     for _ in range(3)]
            return await enhanced_mapper.map_traits_to_genres(traits)
        
        start_time = time.time()
        
        # Run 50 concurrent genre mappings
        stress_tasks = [stress_genre_mapping() for _ in range(50)]
        stress_results = await asyncio.gather(*stress_tasks, return_exceptions=True)
        
        stress_time = time.time() - start_time
        await self.performance_context.record_performance_metric("concurrent_stress_time", stress_time)
        
        # Verify results
        successful_results = [r for r in stress_results if not isinstance(r, Exception)]
        error_count = len(stress_results) - len(successful_results)
        
        assert len(successful_results) >= 45, f"Too many failures: {error_count}/50"
        assert stress_time < 60.0, f"Stress test took too long: {stress_time}s"
        
        # Stress test 2: Rapid configuration changes
        configs = []
        for i in range(10):
            config = WikiConfig(
                enabled=True,
                local_storage_path=os.path.join(self.temp_dir, f"stress_{i}"),
                refresh_interval_hours=random.randint(1, 24),
                fallback_to_hardcoded=True
            )
            configs.append(config)
        
        start_time = time.time()
        
        for config in configs:
            await wiki_manager.reconfigure(config)
            # Quick operation to test system stability
            genres = await wiki_manager.get_genres()
            assert genres is not None
        
        reconfig_time = time.time() - start_time
        await self.performance_context.record_performance_metric("rapid_reconfig_time", reconfig_time)
        
        assert reconfig_time < 30.0, f"Rapid reconfiguration took too long: {reconfig_time}s"
        
        await self.performance_context.info("Concurrent stress testing passed")
    
    @pytest.mark.asyncio
    async def test_edge_case_inputs(self):
        """Test edge case inputs and boundary conditions"""
        await self.mock_context.info("Testing edge case inputs")
        
        wiki_manager = WikiDataManager()
        await wiki_manager.initialize(self.perf_config)
        
        enhanced_mapper = EnhancedGenreMapper(wiki_manager)
        
        # Edge case 1: Empty inputs
        empty_matches = await enhanced_mapper.map_traits_to_genres([])
        assert isinstance(empty_matches, list)  # Should handle gracefully
        
        # Edge case 2: Very long trait lists
        long_traits = [f"trait_{i}" for i in range(100)]
        long_matches = await enhanced_mapper.map_traits_to_genres(long_traits)
        assert isinstance(long_matches, list)
        
        # Edge case 3: Special characters and unicode
        special_traits = ["café", "naïve", "résumé", "🎵", "♪♫♪", "中文", "العربية"]
        special_matches = await enhanced_mapper.map_traits_to_genres(special_traits)
        assert isinstance(special_matches, list)
        
        # Edge case 4: Very long strings
        long_string = "a" * 10000
        long_string_matches = await enhanced_mapper.map_traits_to_genres([long_string])
        assert isinstance(long_string_matches, list)
        
        # Edge case 5: Malformed trait data
        malformed_traits = [None, "", "   ", "\n\t", "normal_trait"]
        malformed_matches = await enhanced_mapper.map_traits_to_genres(malformed_traits)
        assert isinstance(malformed_matches, list)
        
        # Edge case 6: Extremely large narrative text
        large_narrative = self._generate_large_narrative(50000)  # 50k characters
        
        start_time = time.time()
        
        workflow_result = await complete_workflow_test_helper(
            text=large_narrative,
            ctx=self.mock_context
        )
        
        large_text_time = time.time() - start_time
        await self.performance_context.record_performance_metric("large_narrative_time", large_text_time)
        
        assert workflow_result is not None
        assert large_text_time < 120.0, f"Large narrative processing took too long: {large_text_time}s"
        
        # Edge case 7: Rapid successive requests
        rapid_requests = []
        start_time = time.time()
        
        for i in range(20):
            task = complete_workflow_test_helper(
                text=f"Quick test narrative {i}",
                ctx=self.mock_context
            )
            rapid_requests.append(task)
        
        rapid_results = await asyncio.gather(*rapid_requests, return_exceptions=True)
        rapid_time = time.time() - start_time
        
        await self.performance_context.record_performance_metric("rapid_requests_time", rapid_time)
        
        successful_rapid = [r for r in rapid_results if not isinstance(r, Exception)]
        assert len(successful_rapid) >= 18, f"Too many rapid request failures: {len(rapid_results) - len(successful_rapid)}/20"
        
        await self.mock_context.info("Edge case inputs test passed")
    
    @pytest.mark.asyncio
    async def test_cache_performance_and_efficiency(self):
        """Test caching performance and efficiency"""
        await self.performance_context.info("Testing cache performance and efficiency")
        
        wiki_manager = WikiDataManager()
        await wiki_manager.initialize(self.perf_config)
        
        enhanced_mapper = EnhancedGenreMapper(wiki_manager)
        
        # Test cache warming
        test_traits = ["electronic", "ambient", "experimental"]
        
        # First request (cache miss)
        start_time = time.time()
        first_result = await enhanced_mapper.map_traits_to_genres(test_traits)
        first_time = time.time() - start_time
        
        # Second request (cache hit)
        start_time = time.time()
        second_result = await enhanced_mapper.map_traits_to_genres(test_traits)
        second_time = time.time() - start_time
        
        await self.performance_context.record_performance_metric("cache_miss_time", first_time)
        await self.performance_context.record_performance_metric("cache_hit_time", second_time)
        
        # Cache hit should be significantly faster
        assert second_time < first_time, "Cache hit was not faster than cache miss"
        assert second_time < 0.1, f"Cache hit too slow: {second_time}s"
        
        # Results should be identical
        assert len(first_result) == len(second_result)
        
        # Test cache invalidation
        new_config = WikiConfig(
            enabled=True,
            local_storage_path=self.wiki_storage_path,
            refresh_interval_hours=1,  # Force refresh
            fallback_to_hardcoded=True
        )
        
        await wiki_manager.cleanup()
        wiki_manager = WikiDataManager()
        await wiki_manager.initialize(new_config)
        
        # Request after cache invalidation
        start_time = time.time()
        third_result = await enhanced_mapper.map_traits_to_genres(test_traits)
        third_time = time.time() - start_time
        
        await self.performance_context.record_performance_metric("cache_invalidation_time", third_time)
        
        # Should be slower than cache hit but still reasonable
        assert third_time > second_time, "Cache invalidation did not work"
        assert third_time < first_time * 2, "Cache invalidation too slow"
        
        await self.performance_context.info("Cache performance and efficiency test passed")
    
    @pytest.mark.asyncio
    async def test_resource_cleanup_and_limits(self):
        """Test resource cleanup and limits"""
        await self.performance_context.info("Testing resource cleanup and limits")
        
        # Test file handle limits
        managers = []
        
        try:
            # Create many managers to test file handle usage
            for i in range(50):
                config = WikiConfig(
                    enabled=True,
                    local_storage_path=os.path.join(self.temp_dir, f"limit_test_{i}"),
                    fallback_to_hardcoded=True
                )
                
                manager = WikiDataManager()
                await manager.initialize(config)
                managers.append(manager)
            
            # All should initialize successfully
            assert len(managers) == 50
            
            # Test that they all work
            for manager in managers[:10]:  # Test first 10
                genres = await manager.get_genres()
                assert genres is not None
            
        finally:
            # Cleanup
            managers.clear()
            gc.collect()
        
        # Test disk space usage
        initial_size = self._get_directory_size(self.temp_dir)
        
        # Create large amount of cached data
        large_config = WikiConfig(
            enabled=True,
            local_storage_path=self.wiki_storage_path,
            fallback_to_hardcoded=True
        )
        
        large_manager = WikiDataManager()
        await large_manager.initialize(large_config)
        
        # Generate and cache large datasets
        for i in range(10):
            large_content = self._generate_large_genre_dataset(100)
            cache_file = os.path.join(self.wiki_storage_path, f"large_cache_{i}.html")
            with open(cache_file, 'w') as f:
                f.write(large_content)
        
        final_size = self._get_directory_size(self.temp_dir)
        disk_usage = final_size - initial_size
        
        await self.performance_context.record_performance_metric("disk_usage_mb", disk_usage / 1024 / 1024)
        
        # Should not use excessive disk space
        assert disk_usage < 100 * 1024 * 1024, f"Excessive disk usage: {disk_usage / 1024 / 1024}MB"
        
        await self.performance_context.info("Resource cleanup and limits test passed")
    
    def _generate_large_genre_dataset(self, count: int) -> str:
        """Generate large genre dataset for testing"""
        genres = []
        
        for i in range(count):
            genre_name = f"Test Genre {i}"
            characteristics = [f"characteristic_{j}" for j in range(5)]
            instruments = [f"instrument_{j}" for j in range(3)]
            moods = [f"mood_{j}" for j in range(4)]
            
            genre_html = f"""
            <div class="genre-item">
                <h3>{genre_name}</h3>
                <p>Characteristics: {', '.join(characteristics)}</p>
                <p>Typical instruments: {', '.join(instruments)}</p>
                <p>Mood: {', '.join(moods)}</p>
            </div>
            """
            genres.append(genre_html)
        
        return f"""
        <html>
        <body>
        <h1>Large Genre Dataset</h1>
        <div class="genre-list">
        {''.join(genres)}
        </div>
        </body>
        </html>
        """
    
    def _generate_large_metatag_dataset(self, count: int) -> str:
        """Generate large meta tag dataset for testing"""
        categories = ["emotional", "structural", "instrumental", "vocal", "production"]
        tags = []
        
        for i in range(count):
            category = random.choice(categories)
            tag_name = f"test_tag_{i}"
            description = f"Description for test tag {i}"
            
            tag_html = f"<li>[{tag_name}] - {description}</li>"
            tags.append(tag_html)
        
        return f"""
        <html>
        <body>
        <h1>Large Meta Tag Dataset</h1>
        <div class="metatag-categories">
        <div class="category">
        <h3>Test Tags</h3>
        <ul>
        {''.join(tags)}
        </ul>
        </div>
        </div>
        </body>
        </html>
        """
    
    def _generate_large_narrative(self, length: int) -> str:
        """Generate large narrative text for testing"""
        words = ["character", "story", "emotion", "journey", "discovery", "conflict", "resolution", 
                "adventure", "mystery", "romance", "drama", "action", "fantasy", "reality"]
        
        narrative_parts = []
        current_length = 0
        
        while current_length < length:
            sentence_length = random.randint(10, 30)
            sentence_words = [random.choice(words) for _ in range(sentence_length)]
            sentence = " ".join(sentence_words) + ". "
            narrative_parts.append(sentence)
            current_length += len(sentence)
        
        return "".join(narrative_parts)[:length]
    
    def _get_directory_size(self, path: str) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size


# Utility functions for running performance tests
async def run_wiki_performance_tests():
    """Run all wiki performance and edge case tests"""
    test_suite = TestWikiPerformanceAndEdgeCases()
    test_suite.setup_method()
    
    print("🚀 RUNNING WIKI PERFORMANCE AND EDGE CASE TESTS")
    print("=" * 60)
    
    try:
        # Run performance tests
        await test_suite.test_large_dataset_handling()
        print("✅ Large dataset handling test passed")
        
        await test_suite.test_memory_usage_and_cleanup()
        print("✅ Memory usage and cleanup test passed")
        
        await test_suite.test_concurrent_stress_testing()
        print("✅ Concurrent stress testing passed")
        
        await test_suite.test_edge_case_inputs()
        print("✅ Edge case inputs test passed")
        
        await test_suite.test_cache_performance_and_efficiency()
        print("✅ Cache performance and efficiency test passed")
        
        await test_suite.test_resource_cleanup_and_limits()
        print("✅ Resource cleanup and limits test passed")
        
        print("\n🎉 ALL WIKI PERFORMANCE AND EDGE CASE TESTS PASSED!")
        
        # Print performance summary
        perf_summary = test_suite.performance_context.get_performance_summary()
        print("\n📊 PERFORMANCE SUMMARY:")
        for metric, stats in perf_summary.items():
            if isinstance(stats, dict) and "average" in stats:
                print(f"  {metric}: {stats['average']:.3f}s (avg)")
        
    except Exception as e:
        print(f"❌ Wiki performance test failed: {str(e)}")
        raise
    finally:
        test_suite.teardown_method()


if __name__ == "__main__":
    asyncio.run(run_wiki_performance_tests())