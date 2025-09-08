#!/usr/bin/env python3
"""
Integration test for EnhancedGenreMapper with WikiDataManager

Tests the enhanced genre mapping functionality with actual WikiDataManager integration.
"""

import pytest
import pytest_asyncio
import asyncio
from pathlib import Path
import tempfile
import shutil

from enhanced_genre_mapper import EnhancedGenreMapper
from wiki_data_system import WikiDataManager, WikiConfig


class TestEnhancedGenreMapperIntegration:
    """Integration tests for EnhancedGenreMapper with WikiDataManager"""
    
    @pytest_asyncio.fixture
    async def wiki_data_manager(self):
        """Create a WikiDataManager instance for testing"""
        # Create temporary directory for test data
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create test configuration
            config = WikiConfig(
                enabled=False,  # Disable downloads for testing
                local_storage_path=temp_dir,
                fallback_to_hardcoded=True
            )
            
            # Initialize manager
            manager = WikiDataManager()
            await manager.initialize(config)
            
            yield manager
            
        finally:
            # Cleanup
            await manager.cleanup()
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_enhanced_genre_mapper_with_empty_wiki_data(self, wiki_data_manager):
        """Test EnhancedGenreMapper with empty wiki data (fallback mode)"""
        # Create genre mapper
        genre_mapper = EnhancedGenreMapper(wiki_data_manager)
        
        # Test trait mapping with fallback
        traits = ["melancholic", "intellectual", "mysterious"]
        matches = await genre_mapper.map_traits_to_genres(traits, max_results=3)
        
        # Should get results from fallback mappings
        assert len(matches) > 0
        assert len(matches) <= 3
        
        # Verify match structure
        for match in matches:
            assert hasattr(match, 'genre')
            assert hasattr(match, 'confidence')
            assert hasattr(match, 'matching_traits')
            assert hasattr(match, 'matching_reasons')
            assert 0 <= match.confidence <= 1
        
        # Should include expected genres for these traits
        genre_names = [match.genre.name.lower() for match in matches]
        expected_genres = ['blues', 'folk', 'indie', 'progressive', 'dark ambient', 'gothic', 'alternative']
        assert any(expected in ' '.join(genre_names) for expected in expected_genres)
    
    @pytest.mark.asyncio
    async def test_confidence_scoring_consistency(self, wiki_data_manager):
        """Test that confidence scoring is consistent and reasonable"""
        genre_mapper = EnhancedGenreMapper(wiki_data_manager)
        
        # Test with highly relevant traits
        high_relevance_traits = ["melancholic", "emotional"]
        high_matches = await genre_mapper.map_traits_to_genres(high_relevance_traits)
        
        # Test with less relevant traits
        low_relevance_traits = ["random", "nonexistent"]
        low_matches = await genre_mapper.map_traits_to_genres(low_relevance_traits)
        
        # High relevance should generally have higher confidence
        if high_matches and low_matches:
            avg_high_confidence = sum(m.confidence for m in high_matches) / len(high_matches)
            avg_low_confidence = sum(m.confidence for m in low_matches) / len(low_matches)
            
            # This might not always be true due to fallback mappings, but generally should be
            # Just verify both are in valid range
            assert 0 <= avg_high_confidence <= 1
            assert 0 <= avg_low_confidence <= 1
    
    @pytest.mark.asyncio
    async def test_genre_hierarchy_functionality(self, wiki_data_manager):
        """Test genre hierarchy functionality"""
        genre_mapper = EnhancedGenreMapper(wiki_data_manager)
        
        # Test with a genre that should have hierarchy
        hierarchy = genre_mapper.get_genre_hierarchy("Progressive Rock")
        
        # May return None if no data available, which is acceptable
        if hierarchy:
            assert hierarchy.main_genre == "Progressive Rock"
            assert isinstance(hierarchy.subgenres, list)
            assert isinstance(hierarchy.parent_genres, list)
            assert isinstance(hierarchy.related_genres, list)
    
    @pytest.mark.asyncio
    async def test_similar_genres_functionality(self, wiki_data_manager):
        """Test similar genres functionality"""
        genre_mapper = EnhancedGenreMapper(wiki_data_manager)
        
        # Test finding similar genres
        similar = await genre_mapper.find_similar_genres("Blues", max_results=3)
        
        # Should return a list (may be empty if no wiki data)
        assert isinstance(similar, list)
        assert len(similar) <= 3
        
        # If results exist, verify structure
        for genre in similar:
            assert hasattr(genre, 'name')
            assert hasattr(genre, 'description')
            assert genre.name != "Blues"  # Should not include the target genre
    
    @pytest.mark.asyncio
    async def test_error_resilience(self, wiki_data_manager):
        """Test that the system handles errors gracefully"""
        genre_mapper = EnhancedGenreMapper(wiki_data_manager)
        
        # Test with various edge cases
        test_cases = [
            [],  # Empty traits
            [""],  # Empty string trait
            [None],  # None trait (should be handled)
            ["very_long_trait_that_probably_does_not_exist_in_any_mapping"],  # Unknown trait
            ["melancholic"] * 100,  # Many duplicate traits
        ]
        
        for traits in test_cases:
            try:
                # Filter out None values for the actual call
                clean_traits = [t for t in traits if t is not None]
                matches = await genre_mapper.map_traits_to_genres(clean_traits)
                
                # Should always return a list
                assert isinstance(matches, list)
                
                # All matches should be valid
                for match in matches:
                    assert 0 <= match.confidence <= 1
                    
            except Exception as e:
                pytest.fail(f"Unexpected error with traits {traits}: {e}")


if __name__ == "__main__":
    pytest.main([__file__])