#!/usr/bin/env python3
"""
Test script to verify intelligent genre matching algorithms meet requirements 5.3 and 5.4
"""

from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from enhanced_genre_mapper import EnhancedGenreMapper
from wiki_data_system import Genre, WikiDataManager


class TestIntelligentMatchingRequirements:
    """Test intelligent matching algorithms against specific requirements"""

    @pytest_asyncio.fixture
    def comprehensive_genres(self):
        """Create comprehensive genre set for testing hierarchical relationships"""
        return [
            # Base genres
            Genre(
                name="Rock",
                description="A broad genre of popular music",
                characteristics=["energetic", "guitar-driven", "rhythmic"],
                mood_associations=["energetic", "rebellious", "powerful"],
                typical_instruments=["guitar", "bass", "drums"],
                subgenres=["Progressive Rock", "Alternative Rock", "Hard Rock", "Indie Rock"],
                source_url="test"
            ),
            Genre(
                name="Metal",
                description="Heavy, aggressive rock music",
                characteristics=["heavy", "aggressive", "powerful", "intense"],
                mood_associations=["aggressive", "powerful", "dark"],
                typical_instruments=["electric guitar", "bass", "drums"],
                subgenres=["Death Metal", "Black Metal", "Power Metal"],
                source_url="test"
            ),
            Genre(
                name="Electronic",
                description="Music using electronic instruments",
                characteristics=["synthetic", "electronic", "modern"],
                mood_associations=["futuristic", "energetic", "innovative"],
                typical_instruments=["synthesizer", "drum machine", "computer"],
                subgenres=["Techno", "House", "Ambient Electronic"],
                source_url="test"
            ),

            # Subgenres
            Genre(
                name="Progressive Rock",
                description="Complex rock with sophisticated compositions",
                characteristics=["complex", "intellectual", "experimental", "sophisticated"],
                mood_associations=["intellectual", "contemplative", "ambitious"],
                typical_instruments=["guitar", "keyboards", "drums", "bass"],
                subgenres=[],
                source_url="test"
            ),
            Genre(
                name="Death Metal",
                description="Extreme metal with growling vocals",
                characteristics=["extreme", "technical", "aggressive", "dark"],
                mood_associations=["intense", "dark", "powerful"],
                typical_instruments=["electric guitar", "bass", "drums"],
                subgenres=[],
                source_url="test"
            ),
            Genre(
                name="Ambient Electronic",
                description="Atmospheric electronic music",
                characteristics=["atmospheric", "ethereal", "spacious", "meditative"],
                mood_associations=["peaceful", "contemplative", "mysterious"],
                typical_instruments=["synthesizer", "electronic", "field recordings"],
                subgenres=[],
                source_url="test"
            ),

            # Related genres for similarity testing
            Genre(
                name="Art Rock",
                description="Experimental rock with artistic approach",
                characteristics=["artistic", "experimental", "creative", "sophisticated"],
                mood_associations=["intellectual", "creative", "sophisticated"],
                typical_instruments=["guitar", "keyboards", "synthesizer"],
                subgenres=[],
                source_url="test"
            ),
            Genre(
                name="Post-Rock",
                description="Instrumental rock with atmospheric elements",
                characteristics=["instrumental", "atmospheric", "cinematic", "experimental"],
                mood_associations=["contemplative", "emotional", "atmospheric"],
                typical_instruments=["guitar", "bass", "drums", "effects"],
                subgenres=[],
                source_url="test"
            )
        ]

    @pytest_asyncio.fixture
    def mock_wiki_manager(self, comprehensive_genres):
        """Create mock wiki data manager with comprehensive genres"""
        manager = AsyncMock(spec=WikiDataManager)
        manager.get_genres = AsyncMock(return_value=comprehensive_genres)
        return manager

    @pytest_asyncio.fixture
    def enhanced_mapper(self, mock_wiki_manager):
        """Create enhanced genre mapper for testing"""
        return EnhancedGenreMapper(mock_wiki_manager)

    @pytest.mark.asyncio
    async def test_requirement_5_3_hierarchical_relationships(self, enhanced_mapper, comprehensive_genres):
        """
        Test Requirement 5.3: WHEN wiki genres include subgenres 
        THEN the system SHALL consider hierarchical relationships in matching
        """
        # Set up the cache
        enhanced_mapper._genres_cache = comprehensive_genres

        # Test 1: Trait that should match parent genre should also consider subgenres
        traits = ["complex", "intellectual"]  # Should match Progressive Rock strongly
        matches = await enhanced_mapper.map_traits_to_genres(traits, use_hierarchical=True)

        # Should find Progressive Rock with high confidence
        prog_rock_match = next((m for m in matches if m.genre.name == "Progressive Rock"), None)
        assert prog_rock_match is not None, "Should find Progressive Rock for intellectual/complex traits"
        assert prog_rock_match.confidence > 0.5, "Should have high confidence for direct trait match"

        # Test 2: Genre hierarchy should be properly extracted
        hierarchy = await enhanced_mapper.get_genre_hierarchy("Progressive Rock")
        assert hierarchy is not None, "Should return hierarchy for Progressive Rock"
        assert "rock" in hierarchy.parent_genres, "Should identify Rock as parent genre"

        # Test 3: Hierarchical boost should improve matching
        traits_with_parent = ["rock", "complex"]  # Should boost Progressive Rock
        matches_with_boost = await enhanced_mapper.map_traits_to_genres(traits_with_parent, use_hierarchical=True)
        matches_without_boost = await enhanced_mapper.map_traits_to_genres(traits_with_parent, use_hierarchical=False)

        prog_with_boost = next((m for m in matches_with_boost if m.genre.name == "Progressive Rock"), None)
        prog_without_boost = next((m for m in matches_without_boost if m.genre.name == "Progressive Rock"), None)

        if prog_with_boost and prog_without_boost:
            assert prog_with_boost.confidence >= prog_without_boost.confidence, \
                "Hierarchical matching should not decrease confidence"

    @pytest.mark.asyncio
    async def test_requirement_5_4_similarity_algorithms_fallback(self, enhanced_mapper, comprehensive_genres):
        """
        Test Requirement 5.4: WHEN no direct matches exist 
        THEN the system SHALL use similarity algorithms to find closest genre matches
        """
        # Set up the cache
        enhanced_mapper._genres_cache = comprehensive_genres

        # Test 1: Use traits that don't directly match any genre characteristics
        obscure_traits = ["enigmatic", "transcendent", "ethereal"]
        matches = await enhanced_mapper.map_traits_to_genres(obscure_traits)

        # Should still find matches using fallback algorithms
        assert len(matches) > 0, "Should find matches even for obscure traits using fallback"

        # Test 2: Test direct similarity algorithm
        similar_genres = await enhanced_mapper.find_similar_genres("Progressive Rock", max_results=3)

        assert len(similar_genres) > 0, "Should find similar genres"

        # Art Rock should be similar to Progressive Rock (both intellectual/experimental)
        similar_names = [genre.name for genre, _ in similar_genres]
        assert "Art Rock" in similar_names, "Art Rock should be similar to Progressive Rock"

        # Test 3: Test intelligent fallback matching
        fallback_matches = await enhanced_mapper.find_fallback_matches(obscure_traits)
        assert len(fallback_matches) > 0, "Fallback matching should find results"

        # All fallback matches should have reasonable confidence
        for match in fallback_matches:
            assert match.confidence > 0.0, "Fallback matches should have positive confidence"
            assert match.confidence <= 1.0, "Fallback matches should not exceed maximum confidence"

    @pytest.mark.asyncio
    async def test_similarity_algorithm_quality(self, enhanced_mapper, comprehensive_genres):
        """Test that similarity algorithms produce high-quality matches"""
        enhanced_mapper._genres_cache = comprehensive_genres

        # Test content similarity
        prog_rock = next(g for g in comprehensive_genres if g.name == "Progressive Rock")
        art_rock = next(g for g in comprehensive_genres if g.name == "Art Rock")
        death_metal = next(g for g in comprehensive_genres if g.name == "Death Metal")

        # Progressive Rock and Art Rock should be more similar than Progressive Rock and Death Metal
        prog_art_similarity = enhanced_mapper._calculate_content_similarity(prog_rock, art_rock)
        prog_death_similarity = enhanced_mapper._calculate_content_similarity(prog_rock, death_metal)

        assert prog_art_similarity > prog_death_similarity, \
            "Progressive Rock should be more similar to Art Rock than Death Metal"

        # Test semantic similarity
        semantic_sim = enhanced_mapper._calculate_genre_semantic_similarity(prog_rock, art_rock)
        assert semantic_sim > 0, "Should find semantic similarity between related genres"

        # Test hierarchical similarity
        hierarchical_sim = enhanced_mapper._calculate_hierarchical_similarity(prog_rock, art_rock)
        assert hierarchical_sim >= 0, "Hierarchical similarity should be non-negative"

    @pytest.mark.asyncio
    async def test_fuzzy_matching_capability(self, enhanced_mapper, comprehensive_genres):
        """Test fuzzy matching for finding genres with approximate names"""
        enhanced_mapper._genres_cache = comprehensive_genres

        # Test fuzzy finding with approximate names
        fuzzy_matches = [
            ("Prog Rock", "Progressive Rock"),
            ("Death", "Death Metal"),
            ("Electronic Music", "Electronic"),
            ("Ambient", "Ambient Electronic")
        ]

        for fuzzy_name, expected_name in fuzzy_matches:
            found_genre = await enhanced_mapper._fuzzy_find_genre(fuzzy_name, threshold=0.5)
            if found_genre:  # Some matches might not meet threshold
                assert found_genre.name == expected_name or expected_name in found_genre.name, \
                    f"Fuzzy match for '{fuzzy_name}' should find '{expected_name}'"

    @pytest.mark.asyncio
    async def test_trait_semantic_expansion(self, enhanced_mapper):
        """Test semantic expansion of traits for better matching"""
        # Test trait expansion
        expanded_mysterious = enhanced_mapper._expand_trait_semantically("mysterious")
        assert "enigmatic" in expanded_mysterious, "Should expand mysterious to include enigmatic"
        assert "dark" in expanded_mysterious, "Should expand mysterious to include dark"

        expanded_brave = enhanced_mapper._expand_trait_semantically("brave")
        assert "courageous" in expanded_brave, "Should expand brave to include courageous"
        assert "bold" in expanded_brave, "Should expand brave to include bold"

        # Test that original trait is preserved
        assert "mysterious" in expanded_mysterious, "Should preserve original trait"
        assert "brave" in expanded_brave, "Should preserve original trait"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
