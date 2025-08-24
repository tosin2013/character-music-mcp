#!/usr/bin/env python3
"""
Unit tests for EnhancedGenreMapper

Tests the EnhancedGenreMapper class with various character traits to ensure
proper genre matching functionality.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import List

from enhanced_genre_mapper import (
    EnhancedGenreMapper,
    GenreMatch,
    GenreHierarchy
)
from wiki_data_system import Genre, WikiDataManager

class TestEnhancedGenreMapper:
    """Unit tests for EnhancedGenreMapper class"""
    
    @pytest.fixture
    def mock_wiki_data_manager(self):
        """Create a mock WikiDataManager for testing"""
        manager = Mock(spec=WikiDataManager)
        manager.get_genres = AsyncMock()
        return manager
    
    @pytest.fixture
    def sample_genres(self):
        """Create sample genres for testing"""
        return [
            Genre(
                name="Alternative Rock",
                description="A genre of rock music that emerged in the 1980s",
                subgenres=["Indie Rock", "Grunge"],
                characteristics=["guitar-driven", "non-mainstream", "experimental"],
                typical_instruments=["electric guitar", "bass guitar", "drums"],
                mood_associations=["rebellious", "introspective", "energetic"],
                source_url="https://example.com/genres",
                download_date=datetime.now(),
                confidence_score=1.0
            ),
            Genre(
                name="Jazz",
                description="A music genre that originated in African-American communities",
                subgenres=["Bebop", "Smooth Jazz", "Fusion"],
                characteristics=["improvisation", "complex harmonies", "swing rhythm"],
                typical_instruments=["saxophone", "piano", "trumpet", "double bass"],
                mood_associations=["sophisticated", "smooth", "improvisational"],
                source_url="https://example.com/genres",
                download_date=datetime.now(),
                confidence_score=1.0
            ),
            Genre(
                name="Electronic",
                description="Music that employs electronic musical instruments",
                subgenres=["Techno", "House", "Ambient"],
                characteristics=["synthesized sounds", "digital production", "electronic instruments"],
                typical_instruments=["synthesizer", "drum machine", "computer"],
                mood_associations=["futuristic", "danceable", "synthetic"],
                source_url="https://example.com/genres",
                download_date=datetime.now(),
                confidence_score=1.0
            ),
            Genre(
                name="Blues",
                description="A music genre and musical form originated by African Americans",
                subgenres=["Delta Blues", "Chicago Blues"],
                characteristics=["twelve-bar structure", "blue notes", "call and response"],
                typical_instruments=["guitar", "harmonica", "piano"],
                mood_associations=["melancholic", "soulful", "emotional"],
                source_url="https://example.com/genres",
                download_date=datetime.now(),
                confidence_score=1.0
            ),
            Genre(
                name="Ambient",
                description="A genre of music that emphasizes tone and atmosphere",
                subgenres=["Dark Ambient", "Space Ambient"],
                characteristics=["atmospheric", "minimal rhythm", "textural"],
                typical_instruments=["synthesizer", "field recordings", "effects"],
                mood_associations=["meditative", "spacious", "atmospheric"],
                source_url="https://example.com/genres",
                download_date=datetime.now(),
                confidence_score=1.0
            )
        ]
    
    @pytest.fixture
    def genre_mapper(self, mock_wiki_data_manager, sample_genres):
        """Create an EnhancedGenreMapper instance for testing"""
        mock_wiki_data_manager.get_genres.return_value = sample_genres
        mapper = EnhancedGenreMapper(mock_wiki_data_manager)
        mapper._genres_cache = sample_genres  # Pre-populate cache
        return mapper
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_wiki_data_manager):
        """Test EnhancedGenreMapper initialization"""
        mapper = EnhancedGenreMapper(mock_wiki_data_manager)
        
        assert mapper.wiki_data_manager == mock_wiki_data_manager
        assert mapper._genres_cache is None
        assert mapper._trait_keywords_cache is None
        assert mapper._fallback_mappings is not None
    
    @pytest.mark.asyncio
    async def test_map_traits_to_genres_basic(self, genre_mapper):
        """Test basic trait to genre mapping"""
        traits = ["rebellious", "energetic"]
        
        matches = await genre_mapper.map_traits_to_genres(traits, max_results=3)
        
        assert len(matches) > 0
        assert all(isinstance(match, GenreMatch) for match in matches)
        assert all(0.0 <= match.confidence <= 1.0 for match in matches)
        
        # Should be sorted by confidence
        confidences = [match.confidence for match in matches]
        assert confidences == sorted(confidences, reverse=True)
        
        # Alternative Rock should match well with rebellious traits
        alt_rock_match = next((m for m in matches if m.genre.name == "Alternative Rock"), None)
        assert alt_rock_match is not None
        assert alt_rock_match.confidence > 0.1
    
    @pytest.mark.asyncio
    async def test_map_traits_to_genres_melancholic(self, genre_mapper):
        """Test mapping melancholic traits"""
        traits = ["melancholic", "emotional", "introspective"]
        
        matches = await genre_mapper.map_traits_to_genres(traits, max_results=5)
        
        # Blues should match well with melancholic traits
        blues_match = next((m for m in matches if m.genre.name == "Blues"), None)
        assert blues_match is not None
        assert blues_match.confidence > 0.2
        
        # Check matching reasons
        assert len(blues_match.matching_traits) > 0
        assert len(blues_match.matching_reasons) > 0
    
    @pytest.mark.asyncio
    async def test_map_traits_to_genres_sophisticated(self, genre_mapper):
        """Test mapping sophisticated traits"""
        traits = ["sophisticated", "complex", "intellectual"]
        
        matches = await genre_mapper.map_traits_to_genres(traits, max_results=5)
        
        # Jazz should match well with sophisticated traits
        jazz_match = next((m for m in matches if m.genre.name == "Jazz"), None)
        assert jazz_match is not None
        assert jazz_match.confidence > 0.2
    
    @pytest.mark.asyncio
    async def test_map_traits_to_genres_atmospheric(self, genre_mapper):
        """Test mapping atmospheric traits"""
        traits = ["mysterious", "atmospheric", "meditative"]
        
        matches = await genre_mapper.map_traits_to_genres(traits, max_results=5)
        
        # Ambient should match well with atmospheric traits
        ambient_match = next((m for m in matches if m.genre.name == "Ambient"), None)
        assert ambient_match is not None
        assert ambient_match.confidence > 0.2
    
    @pytest.mark.asyncio
    async def test_map_traits_to_genres_empty_traits(self, genre_mapper):
        """Test mapping with empty traits list"""
        matches = await genre_mapper.map_traits_to_genres([])
        
        assert len(matches) == 0
    
    @pytest.mark.asyncio
    async def test_map_traits_to_genres_no_wiki_data(self, mock_wiki_data_manager):
        """Test mapping when no wiki data is available"""
        mock_wiki_data_manager.get_genres.return_value = []
        mapper = EnhancedGenreMapper(mock_wiki_data_manager)
        
        traits = ["rebellious", "energetic"]
        matches = await mapper.map_traits_to_genres(traits)
        
        # Should fall back to hardcoded mappings
        assert len(matches) > 0
    
    @pytest.mark.asyncio
    async def test_map_traits_hierarchical_disabled(self, genre_mapper):
        """Test mapping with hierarchical matching disabled"""
        traits = ["rebellious", "energetic"]
        
        matches_with_hierarchy = await genre_mapper.map_traits_to_genres(
            traits, use_hierarchical=True
        )
        matches_without_hierarchy = await genre_mapper.map_traits_to_genres(
            traits, use_hierarchical=False
        )
        
        # Results may differ when hierarchical matching is disabled
        assert len(matches_with_hierarchy) > 0
        assert len(matches_without_hierarchy) > 0
    
    def test_calculate_genre_confidence(self, genre_mapper, sample_genres):
        """Test genre confidence calculation"""
        alt_rock = sample_genres[0]  # Alternative Rock
        
        # Test with matching traits
        traits = ["rebellious", "guitar-driven"]
        confidence = genre_mapper.calculate_genre_confidence(traits, alt_rock)
        assert confidence > 0.0
        
        # Test with non-matching traits
        traits = ["classical", "orchestral"]
        confidence = genre_mapper.calculate_genre_confidence(traits, alt_rock)
        assert confidence >= 0.0  # Should be low but not negative
        
        # Test with empty traits
        confidence = genre_mapper.calculate_genre_confidence([], alt_rock)
        assert confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_get_genre_hierarchy(self, genre_mapper, sample_genres):
        """Test genre hierarchy retrieval"""
        # Test with existing genre
        hierarchy = await genre_mapper.get_genre_hierarchy("Alternative Rock")
        
        assert hierarchy is not None
        assert hierarchy.main_genre == "Alternative Rock"
        assert "Indie Rock" in hierarchy.subgenres
        assert "Grunge" in hierarchy.subgenres
        
        # Test with non-existent genre
        hierarchy = await genre_mapper.get_genre_hierarchy("NonExistentGenre")
        assert hierarchy is None
    
    @pytest.mark.asyncio
    async def test_find_similar_genres(self, genre_mapper, sample_genres):
        """Test finding similar genres"""
        similar = await genre_mapper.find_similar_genres("Alternative Rock", max_results=3)
        
        assert len(similar) <= 3
        assert all(isinstance(item, tuple) for item in similar)
        assert all(len(item) == 2 for item in similar)
        assert all(isinstance(item[0], Genre) for item in similar)
        assert all(isinstance(item[1], float) for item in similar)
        
        # Similarities should be sorted in descending order
        similarities = [item[1] for item in similar]
        assert similarities == sorted(similarities, reverse=True)
        
        # Should not include the target genre itself
        genre_names = [item[0].name for item in similar]
        assert "Alternative Rock" not in genre_names
    
    @pytest.mark.asyncio
    async def test_find_similar_genres_nonexistent(self, genre_mapper):
        """Test finding similar genres for non-existent genre"""
        similar = await genre_mapper.find_similar_genres("NonExistentGenre")
        
        assert len(similar) == 0
    
    def test_prepare_genre_text(self, genre_mapper, sample_genres):
        """Test genre text preparation"""
        alt_rock = sample_genres[0]
        
        text = genre_mapper._prepare_genre_text(alt_rock)
        
        assert isinstance(text, str)
        assert text == text.lower()  # Should be lowercase
        assert alt_rock.name.lower() in text
        assert alt_rock.description.lower() in text
    
    def test_calculate_trait_genre_score(self, genre_mapper, sample_genres):
        """Test individual trait-genre score calculation"""
        alt_rock = sample_genres[0]
        genre_text = genre_mapper._prepare_genre_text(alt_rock)
        
        # Test direct name match
        score = genre_mapper._calculate_trait_genre_score("alternative", alt_rock, genre_text)
        assert score > 0.5  # Should be high for name match
        
        # Test characteristic match
        score = genre_mapper._calculate_trait_genre_score("guitar-driven", alt_rock, genre_text)
        assert score > 0.3  # Should be moderate for characteristic match
        
        # Test mood match
        score = genre_mapper._calculate_trait_genre_score("rebellious", alt_rock, genre_text)
        assert score > 0.2  # Should be moderate for mood match
        
        # Test no match
        score = genre_mapper._calculate_trait_genre_score("classical", alt_rock, genre_text)
        assert score >= 0.0  # Should be low but not negative
    
    def test_calculate_semantic_similarity(self, genre_mapper):
        """Test semantic similarity calculation"""
        genre_text = "alternative rock guitar-driven rebellious energetic"
        
        # Test semantic match
        similarity = genre_mapper._calculate_semantic_similarity("rebellious", genre_text)
        assert similarity > 0.0
        
        # Test related concept match
        similarity = genre_mapper._calculate_semantic_similarity("brave", genre_text)
        assert similarity >= 0.0  # May find some semantic connection
        
        # Test no match
        similarity = genre_mapper._calculate_semantic_similarity("classical", genre_text)
        assert similarity >= 0.0
    
    def test_calculate_fuzzy_match(self, genre_mapper):
        """Test fuzzy string matching"""
        genre_text = "alternative rock guitar-driven rebellious"
        
        # Test close match
        ratio = genre_mapper._calculate_fuzzy_match("rebel", genre_text)
        assert ratio > 0.0  # Should find some similarity with "rebellious"
        
        # Test exact match
        ratio = genre_mapper._calculate_fuzzy_match("guitar-driven", genre_text)
        assert ratio > 0.8  # Should be very high for exact match
        
        # Test no match
        ratio = genre_mapper._calculate_fuzzy_match("xyz", genre_text)
        assert ratio >= 0.0
    
    def test_get_genre_popularity_boost(self, genre_mapper, sample_genres):
        """Test genre popularity boost calculation"""
        # Popular genre should get boost
        alt_rock = sample_genres[0]  # Alternative Rock contains "rock"
        boost = genre_mapper._get_genre_popularity_boost(alt_rock)
        assert boost >= 1.0
        
        # Create unpopular genre
        unpopular_genre = Genre(
            name="Obscure Experimental Genre",
            description="Very niche genre",
            subgenres=[],
            characteristics=[],
            typical_instruments=[],
            mood_associations=[],
            source_url="",
            download_date=datetime.now()
        )
        boost = genre_mapper._get_genre_popularity_boost(unpopular_genre)
        assert boost == 1.0  # No boost for unpopular genres
    
    def test_analyze_trait_match(self, genre_mapper, sample_genres):
        """Test trait match analysis"""
        alt_rock = sample_genres[0]
        traits = ["rebellious", "guitar-driven", "nonexistent"]
        
        matching_traits, reasons = genre_mapper._analyze_trait_match(traits, alt_rock)
        
        assert len(matching_traits) > 0
        assert len(reasons) > 0
        assert len(matching_traits) == len(reasons)
        
        # Should find matches for rebellious and guitar-driven
        assert "rebellious" in matching_traits
        assert "guitar-driven" in matching_traits
        assert "nonexistent" not in matching_traits
    
    def test_find_genre_by_name(self, genre_mapper, sample_genres):
        """Test finding genre by name"""
        # Test exact match
        genre = genre_mapper._find_genre_by_name("Alternative Rock")
        assert genre is not None
        assert genre.name == "Alternative Rock"
        
        # Test case insensitive
        genre = genre_mapper._find_genre_by_name("alternative rock")
        assert genre is not None
        assert genre.name == "Alternative Rock"
        
        # Test non-existent
        genre = genre_mapper._find_genre_by_name("NonExistent")
        assert genre is None
    
    @pytest.mark.asyncio
    async def test_infer_parent_genres_enhanced(self, genre_mapper, sample_genres):
        """Test enhanced parent genre inference"""
        # Create a subgenre for testing
        indie_rock = Genre(
            name="Indie Rock",
            description="Independent rock music",
            subgenres=[],
            characteristics=["independent", "alternative"],
            typical_instruments=["guitar", "bass", "drums"],
            mood_associations=["indie", "alternative"],
            source_url="",
            download_date=datetime.now()
        )
        
        parents = await genre_mapper._infer_parent_genres_enhanced(indie_rock)
        
        assert isinstance(parents, list)
        # Should infer "rock" as parent
        assert any("rock" in parent.lower() for parent in parents)
    
    def test_extract_compound_genre_parts(self, genre_mapper):
        """Test compound genre name part extraction"""
        # Test compound genre
        parts = genre_mapper._extract_compound_genre_parts("Folk Rock")
        assert "folk" in parts
        assert "rock" in parts
        
        # Test single genre
        parts = genre_mapper._extract_compound_genre_parts("Jazz")
        assert len(parts) == 0  # No compound parts
        
        # Test complex compound
        parts = genre_mapper._extract_compound_genre_parts("Electronic Dance Music")
        assert "electronic" in parts
    
    @pytest.mark.asyncio
    async def test_find_related_genres_enhanced(self, genre_mapper, sample_genres):
        """Test enhanced related genre finding"""
        alt_rock = sample_genres[0]
        
        related = await genre_mapper._find_related_genres_enhanced(alt_rock)
        
        assert isinstance(related, list)
        assert len(related) <= 8  # Should limit to 8 related genres
        assert alt_rock.name not in related  # Should not include itself
    
    def test_calculate_content_similarity(self, genre_mapper, sample_genres):
        """Test content-based similarity calculation"""
        alt_rock = sample_genres[0]
        jazz = sample_genres[1]
        
        # Test similarity between different genres
        similarity = genre_mapper._calculate_content_similarity(alt_rock, jazz)
        assert 0.0 <= similarity <= 1.0
        
        # Test similarity with itself (should be high but we exclude self in actual usage)
        similarity = genre_mapper._calculate_content_similarity(alt_rock, alt_rock)
        assert similarity == 1.0
    
    def test_calculate_structural_similarity(self, genre_mapper, sample_genres):
        """Test structural similarity calculation"""
        alt_rock = sample_genres[0]
        jazz = sample_genres[1]
        
        similarity = genre_mapper._calculate_structural_similarity(alt_rock, jazz)
        assert 0.0 <= similarity <= 1.0
        
        # Create similar genre for testing
        indie_rock = Genre(
            name="Indie Rock",
            description="Independent rock music with alternative influences",
            subgenres=[],
            characteristics=[],
            typical_instruments=[],
            mood_associations=[],
            source_url="",
            download_date=datetime.now()
        )
        
        similarity = genre_mapper._calculate_structural_similarity(alt_rock, indie_rock)
        assert similarity > 0.3  # Should be higher due to "rock" in both names
    
    def test_calculate_genre_semantic_similarity(self, genre_mapper, sample_genres):
        """Test genre semantic similarity calculation"""
        alt_rock = sample_genres[0]
        electronic = sample_genres[2]
        
        similarity = genre_mapper._calculate_genre_semantic_similarity(alt_rock, electronic)
        assert 0.0 <= similarity <= 1.0
        
        # Test with genres in same family
        blues = sample_genres[3]
        jazz = sample_genres[1]
        
        # Blues and Jazz might have some semantic similarity
        similarity = genre_mapper._calculate_genre_semantic_similarity(blues, jazz)
        assert 0.0 <= similarity <= 1.0
    
    def test_calculate_hierarchical_similarity(self, genre_mapper, sample_genres):
        """Test hierarchical similarity calculation"""
        alt_rock = sample_genres[0]
        jazz = sample_genres[1]
        
        similarity = genre_mapper._calculate_hierarchical_similarity(alt_rock, jazz)
        assert 0.0 <= similarity <= 1.0
        
        # Create parent-child relationship for testing
        indie_rock = Genre(
            name="Indie Rock",
            description="Independent rock music",
            subgenres=[],
            characteristics=[],
            typical_instruments=[],
            mood_associations=[],
            source_url="",
            download_date=datetime.now()
        )
        
        # Simulate parent-child relationship
        alt_rock.subgenres = ["Indie Rock"]
        
        similarity = genre_mapper._calculate_hierarchical_similarity(alt_rock, indie_rock)
        assert similarity > 0.5  # Should be high for parent-child relationship
    
    def test_check_name_hierarchy(self, genre_mapper):
        """Test name hierarchy checking"""
        # Test parent-child relationship
        similarity = genre_mapper._check_name_hierarchy("Rock", "Alternative Rock")
        assert similarity > 0.5
        
        # Test sibling relationship
        similarity = genre_mapper._check_name_hierarchy("Hard Rock", "Soft Rock")
        assert similarity > 0.3
        
        # Test unrelated genres
        similarity = genre_mapper._check_name_hierarchy("Jazz", "Electronic")
        assert similarity == 0.0
    
    @pytest.mark.asyncio
    async def test_fuzzy_find_genre(self, genre_mapper, sample_genres):
        """Test fuzzy genre finding"""
        # Test close match
        genre = await genre_mapper._fuzzy_find_genre("Alternative Rock")
        assert genre is not None
        assert genre.name == "Alternative Rock"
        
        # Test fuzzy match
        genre = await genre_mapper._fuzzy_find_genre("Alt Rock")
        assert genre is not None  # Should find Alternative Rock
        
        # Test no match
        genre = await genre_mapper._fuzzy_find_genre("Completely Different Genre")
        assert genre is None
    
    @pytest.mark.asyncio
    async def test_find_fallback_matches(self, genre_mapper):
        """Test fallback matching when wiki data is insufficient"""
        traits = ["rebellious", "energetic"]
        
        fallback_matches = await genre_mapper.find_fallback_matches(traits, max_results=3)
        
        assert len(fallback_matches) <= 3
        assert all(isinstance(match, GenreMatch) for match in fallback_matches)
        assert all(0.0 <= match.confidence <= 1.0 for match in fallback_matches)

class TestGenreMatch:
    """Unit tests for GenreMatch class"""
    
    def test_genre_match_initialization(self, sample_genres):
        """Test GenreMatch initialization"""
        genre = sample_genres[0]
        
        match = GenreMatch(
            genre=genre,
            confidence=0.85,
            matching_traits=["rebellious", "energetic"],
            matching_reasons=["Direct match in mood associations"]
        )
        
        assert match.genre == genre
        assert match.confidence == 0.85
        assert match.matching_traits == ["rebellious", "energetic"]
        assert match.matching_reasons == ["Direct match in mood associations"]
    
    def test_genre_match_confidence_bounds(self, sample_genres):
        """Test confidence score bounds enforcement"""
        genre = sample_genres[0]
        
        # Test confidence > 1.0
        match = GenreMatch(genre=genre, confidence=1.5)
        assert match.confidence == 1.0
        
        # Test confidence < 0.0
        match = GenreMatch(genre=genre, confidence=-0.5)
        assert match.confidence == 0.0
        
        # Test valid confidence
        match = GenreMatch(genre=genre, confidence=0.75)
        assert match.confidence == 0.75

class TestGenreHierarchy:
    """Unit tests for GenreHierarchy class"""
    
    def test_genre_hierarchy_initialization(self):
        """Test GenreHierarchy initialization"""
        hierarchy = GenreHierarchy(
            main_genre="Alternative Rock",
            subgenres=["Indie Rock", "Grunge"],
            parent_genres=["Rock"],
            related_genres=["Punk Rock", "Post-Rock"]
        )
        
        assert hierarchy.main_genre == "Alternative Rock"
        assert hierarchy.subgenres == ["Indie Rock", "Grunge"]
        assert hierarchy.parent_genres == ["Rock"]
        assert hierarchy.related_genres == ["Punk Rock", "Post-Rock"]
    
    def test_genre_hierarchy_defaults(self):
        """Test GenreHierarchy with default values"""
        hierarchy = GenreHierarchy(main_genre="Jazz")
        
        assert hierarchy.main_genre == "Jazz"
        assert hierarchy.subgenres == []
        assert hierarchy.parent_genres == []
        assert hierarchy.related_genres == []

if __name__ == "__main__":
    # Run basic tests
    async def run_basic_tests():
        # Create mock data
        sample_genres = [
            Genre(
                name="Rock",
                description="Guitar-driven music",
                subgenres=[],
                characteristics=["guitar-driven", "energetic"],
                typical_instruments=["guitar", "bass", "drums"],
                mood_associations=["energetic", "rebellious"],
                source_url="",
                download_date=datetime.now()
            )
        ]
        
        # Create mock wiki data manager
        mock_manager = Mock()
        mock_manager.get_genres = AsyncMock(return_value=sample_genres)
        
        # Create mapper
        mapper = EnhancedGenreMapper(mock_manager)
        mapper._genres_cache = sample_genres
        
        # Test basic functionality
        traits = ["energetic", "rebellious"]
        matches = await mapper.map_traits_to_genres(traits)
        
        assert len(matches) > 0
        assert matches[0].genre.name == "Rock"
        print("✓ Basic trait mapping test passed")
        
        # Test confidence calculation
        confidence = mapper.calculate_genre_confidence(traits, sample_genres[0])
        assert confidence > 0.0
        print("✓ Confidence calculation test passed")
        
        print("Basic EnhancedGenreMapper unit tests passed!")
    
    import asyncio
    asyncio.run(run_basic_tests())