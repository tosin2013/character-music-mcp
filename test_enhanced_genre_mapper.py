#!/usr/bin/env python3
"""
Test suite for EnhancedGenreMapper

Tests the enhanced genre mapping functionality with wiki-sourced data,
including trait-to-genre matching, confidence scoring, and fallback mechanisms.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from typing import List

from enhanced_genre_mapper import EnhancedGenreMapper, GenreMatch, GenreHierarchy
from wiki_data_system import Genre, WikiDataManager


class TestEnhancedGenreMapper:
    """Test suite for EnhancedGenreMapper class"""
    
    @pytest.fixture
    def mock_wiki_data_manager(self):
        """Create a mock WikiDataManager for testing"""
        manager = Mock(spec=WikiDataManager)
        return manager
    
    @pytest.fixture
    def sample_genres(self):
        """Create sample genres for testing"""
        return [
            Genre(
                name="Blues",
                description="A music genre characterized by blue notes, call-and-response vocals, and emotional expression",
                characteristics=["emotional", "soulful", "melancholic", "expressive"],
                mood_associations=["sad", "melancholic", "emotional", "introspective"],
                typical_instruments=["guitar", "harmonica", "piano"],
                source_url="https://example.com/blues"
            ),
            Genre(
                name="Progressive Rock",
                description="A rock music subgenre that emphasizes complex compositions and intellectual themes",
                characteristics=["complex", "intellectual", "experimental", "sophisticated"],
                mood_associations=["thoughtful", "introspective", "ambitious"],
                typical_instruments=["synthesizer", "guitar", "drums", "bass"],
                source_url="https://example.com/prog-rock"
            ),
            Genre(
                name="Electronic",
                description="Music that employs electronic musical instruments and technology",
                characteristics=["synthetic", "modern", "technological", "innovative"],
                mood_associations=["energetic", "futuristic", "dynamic"],
                typical_instruments=["synthesizer", "drum machine", "computer"],
                source_url="https://example.com/electronic"
            ),
            Genre(
                name="Folk",
                description="Traditional music passed down through generations",
                characteristics=["traditional", "acoustic", "storytelling", "authentic"],
                mood_associations=["nostalgic", "peaceful", "authentic"],
                typical_instruments=["acoustic guitar", "banjo", "fiddle"],
                source_url="https://example.com/folk"
            )
        ]
    
    @pytest.fixture
    def genre_mapper(self, mock_wiki_data_manager):
        """Create EnhancedGenreMapper instance for testing"""
        return EnhancedGenreMapper(mock_wiki_data_manager)
    
    @pytest.mark.asyncio
    async def test_map_traits_to_genres_with_wiki_data(self, genre_mapper, mock_wiki_data_manager, sample_genres):
        """Test trait-to-genre mapping with wiki data available"""
        # Setup mock to return sample genres
        mock_wiki_data_manager.get_genres = AsyncMock(return_value=sample_genres)
        
        # Test mapping melancholic traits
        traits = ["melancholic", "emotional", "introspective"]
        matches = await genre_mapper.map_traits_to_genres(traits)
        
        # Should return matches
        assert len(matches) > 0
        assert all(isinstance(match, GenreMatch) for match in matches)
        assert all(0 <= match.confidence <= 1 for match in matches)
        
        # Blues should be a top match for melancholic traits
        blues_match = next((m for m in matches if m.genre.name == "Blues"), None)
        assert blues_match is not None
        assert blues_match.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_map_traits_to_genres_intellectual(self, genre_mapper, mock_wiki_data_manager, sample_genres):
        """Test mapping intellectual traits to progressive genres"""
        mock_wiki_data_manager.get_genres = AsyncMock(return_value=sample_genres)
        
        traits = ["intellectual", "complex", "sophisticated"]
        matches = await genre_mapper.map_traits_to_genres(traits)
        
        # Progressive Rock should be a top match
        prog_match = next((m for m in matches if m.genre.name == "Progressive Rock"), None)
        assert prog_match is not None
        assert prog_match.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_map_traits_to_genres_fallback(self, genre_mapper, mock_wiki_data_manager):
        """Test fallback behavior when wiki data is unavailable"""
        # Setup mock to return empty list (no wiki data)
        mock_wiki_data_manager.get_genres = AsyncMock(return_value=[])
        
        traits = ["melancholic", "mysterious"]
        matches = await genre_mapper.map_traits_to_genres(traits)
        
        # Should still return matches using fallback mappings
        assert len(matches) > 0
        assert all(isinstance(match, GenreMatch) for match in matches)
        
        # Check that fallback genres are used
        genre_names = [match.genre.name for match in matches]
        assert any(name in ["blues", "folk", "indie", "dark ambient", "gothic", "alternative"] 
                  for name in genre_names)
    
    @pytest.mark.asyncio
    async def test_map_traits_empty_list(self, genre_mapper, mock_wiki_data_manager, sample_genres):
        """Test mapping with empty traits list"""
        mock_wiki_data_manager.get_genres = AsyncMock(return_value=sample_genres)
        
        matches = await genre_mapper.map_traits_to_genres([])
        
        # Should return empty list or handle gracefully
        assert isinstance(matches, list)
    
    def test_calculate_genre_confidence(self, genre_mapper, sample_genres):
        """Test confidence calculation for trait-genre matches"""
        blues_genre = sample_genres[0]  # Blues genre
        
        # High confidence traits
        high_confidence = genre_mapper.calculate_genre_confidence(
            ["melancholic", "emotional"], blues_genre
        )
        assert high_confidence > 0.5
        
        # Low confidence traits
        low_confidence = genre_mapper.calculate_genre_confidence(
            ["technological", "synthetic"], blues_genre
        )
        assert low_confidence < 0.3
        
        # Empty traits
        zero_confidence = genre_mapper.calculate_genre_confidence([], blues_genre)
        assert zero_confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_get_genre_hierarchy(self, genre_mapper, sample_genres):
        """Test genre hierarchy extraction"""
        # Add a base Rock genre to the sample genres for proper hierarchy testing
        rock_genre = Genre(
            name="Rock",
            description="A broad genre of popular music",
            characteristics=["energetic", "guitar-driven", "rhythmic"],
            mood_associations=["energetic", "rebellious", "powerful"],
            typical_instruments=["guitar", "bass", "drums"],
            subgenres=["Progressive Rock", "Alternative Rock", "Hard Rock"],
            source_url="https://example.com/rock"
        )
        extended_genres = sample_genres + [rock_genre]
        genre_mapper._genres_cache = extended_genres
        
        # Test with a genre that should have hierarchy
        hierarchy = await genre_mapper.get_genre_hierarchy("Progressive Rock")
        
        if hierarchy:
            assert isinstance(hierarchy, GenreHierarchy)
            assert hierarchy.main_genre == "Progressive Rock"
            # Should infer "rock" as parent genre
            assert "rock" in hierarchy.parent_genres
    
    @pytest.mark.asyncio
    async def test_find_similar_genres(self, genre_mapper, mock_wiki_data_manager, sample_genres):
        """Test finding similar genres"""
        mock_wiki_data_manager.get_genres = AsyncMock(return_value=sample_genres)
        
        similar = await genre_mapper.find_similar_genres("Blues")
        
        assert isinstance(similar, list)
        # Should not include the target genre itself
        assert not any(genre.name == "Blues" for genre in similar)
        
        # If similar genres found, they should be Genre objects
        if similar:
            assert all(isinstance(genre, Genre) for genre in similar)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, genre_mapper, mock_wiki_data_manager):
        """Test error handling in genre mapping"""
        # Setup mock to raise exception
        mock_wiki_data_manager.get_genres = AsyncMock(side_effect=Exception("Network error"))
        
        # Should handle error gracefully and use fallback
        traits = ["melancholic"]
        matches = await genre_mapper.map_traits_to_genres(traits)
        
        # Should still return results using fallback
        assert isinstance(matches, list)
    
    def test_semantic_similarity_calculation(self, genre_mapper):
        """Test semantic similarity calculation"""
        # Test the private method for semantic similarity
        similarity = genre_mapper._calculate_semantic_similarity(
            "melancholic", "sad blues emotional music"
        )
        assert 0 <= similarity <= 1
        assert similarity > 0  # Should find some similarity
    
    def test_fuzzy_matching(self, genre_mapper):
        """Test fuzzy string matching"""
        # Test the private method for fuzzy matching
        fuzzy_score = genre_mapper._calculate_fuzzy_match(
            "electronic", "electronic dance music synthesizer"
        )
        assert 0 <= fuzzy_score <= 1
        assert fuzzy_score > 0.8  # Should be high for exact match
    
    def test_fallback_mappings(self, genre_mapper):
        """Test that fallback mappings are properly defined"""
        fallback_mappings = genre_mapper._get_fallback_mappings()
        
        assert isinstance(fallback_mappings, dict)
        assert len(fallback_mappings) > 0
        
        # Check some expected mappings
        assert "melancholic" in fallback_mappings
        assert "blues" in fallback_mappings["melancholic"]
        assert "intellectual" in fallback_mappings
        assert "progressive" in fallback_mappings["intellectual"]


if __name__ == "__main__":
    pytest.main([__file__])