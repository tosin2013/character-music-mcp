#!/usr/bin/env python3
"""
Integration tests for SourceAttributionManager with the main server

Tests the integration of source attribution into LLM context building
and album generation workflows.
"""

import asyncio
import shutil
import tempfile
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from server import CharacterProfile, MusicPersonaGenerator
from source_attribution_manager import SourceAttributionManager


class TestSourceAttributionIntegration:
    """Test suite for SourceAttributionManager integration"""

    @pytest_asyncio.fixture
    async def temp_attribution_manager(self):
        """Create a temporary SourceAttributionManager for testing"""
        temp_dir = tempfile.mkdtemp()
        manager = SourceAttributionManager(storage_path=temp_dir)
        await manager.initialize()
        yield manager
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_character(self):
        """Create a mock character for testing"""
        return CharacterProfile(
            name="Test Character",
            aliases=["Tester"],
            physical_description="A test character",
            mannerisms=["thoughtful", "creative"],
            speech_patterns=["articulate"],
            behavioral_traits=["analytical", "empathetic"],
            backstory="A character created for testing purposes",
            relationships=["friends with developers"],
            formative_experiences=["learning to code"],
            social_connections=["tech community"],
            motivations=["understanding", "helping others"],
            fears=["bugs", "system failures"],
            desires=["clean code", "good tests"],
            conflicts=["perfectionism vs deadlines"],
            personality_drivers=["curiosity", "precision"],
            confidence_score=0.8,
            text_references=["test documentation"],
            first_appearance="test suite",
            importance_score=1.0
        )

    @pytest.mark.asyncio
    async def test_persona_generator_attribution_integration(self, temp_attribution_manager, mock_character):
        """Test that MusicPersonaGenerator integrates with SourceAttributionManager"""

        # Create a persona generator with mocked wiki integration
        persona_generator = MusicPersonaGenerator()
        persona_generator.source_attribution_manager = temp_attribution_manager

        # Register some test sources
        temp_attribution_manager.register_source(
            "https://sunoaiwiki.com/genres/test",
            "genre",
            "Test Genres",
            datetime.now()
        )

        # Test building attributed context
        test_content = {"genres": ["rock", "indie"], "confidence": 0.9}
        attributed_context = persona_generator.build_attributed_context_for_llm(
            test_content, "genre"
        )

        # Verify attribution is included
        assert "Genre information sourced from:" in attributed_context
        assert "Test Genres" in attributed_context
        assert "https://sunoaiwiki.com/genres/test" in attributed_context

        # Verify usage was tracked
        stats = temp_attribution_manager.get_usage_statistics()
        assert stats['total_usage_records'] == 1
        assert stats['most_used_sources'][0]['url'] == "https://sunoaiwiki.com/genres/test"

    @pytest.mark.asyncio
    async def test_attribution_with_multiple_source_types(self, temp_attribution_manager):
        """Test attribution with multiple types of wiki sources"""

        # Register sources of different types
        sources = [
            ("https://sunoaiwiki.com/genres/rock", "genre", "Rock Genres"),
            ("https://sunoaiwiki.com/tags/emotional", "meta_tag", "Emotional Tags"),
            ("https://sunoaiwiki.com/tips/production", "technique", "Production Tips")
        ]

        for url, content_type, title in sources:
            temp_attribution_manager.register_source(url, content_type, title, datetime.now())

        # Test building context with mixed sources
        test_content = {
            "genres": ["rock"],
            "tags": ["emotional"],
            "techniques": ["production"]
        }

        # Get all source URLs
        all_sources = temp_attribution_manager.get_source_urls()

        # Build attributed content
        attributed_content = temp_attribution_manager.build_attributed_context(
            test_content, all_sources
        )

        # Verify mixed source attribution
        assert "multiple wiki pages" in attributed_content.attribution_text
        assert len(attributed_content.sources) == 3

        # Verify all source types are represented
        source_types = {source.content_type for source in attributed_content.sources}
        assert source_types == {"genre", "meta_tag", "technique"}

    @pytest.mark.asyncio
    async def test_attribution_fallback_behavior(self):
        """Test that attribution gracefully handles missing components"""

        # Create persona generator without attribution manager
        persona_generator = MusicPersonaGenerator()
        persona_generator.source_attribution_manager = None
        persona_generator.wiki_data_manager = None

        # Test building attributed context without attribution manager
        test_content = {"test": "data"}
        result = persona_generator.build_attributed_context_for_llm(test_content, "genre")

        # Should fallback to content without attribution
        assert result == str(test_content)

    @pytest.mark.asyncio
    async def test_source_registration_during_genre_mapping(self, temp_attribution_manager):
        """Test that sources are registered during genre mapping"""

        # Create a mock genre with source information
        from enhanced_genre_mapper import GenreMatch
        from wiki_data_system import Genre

        mock_genre = Genre(
            name="Test Rock",
            description="A test rock genre",
            subgenres=["indie rock"],
            characteristics=["energetic", "guitar-driven"],
            typical_instruments=["guitar", "drums"],
            mood_associations=["energetic", "rebellious"],
            source_url="https://sunoaiwiki.com/genres/rock",
            download_date=datetime.now()
        )

        mock_match = GenreMatch(
            genre=mock_genre,
            confidence=0.9,
            matching_traits=["energetic", "rebellious"]
        )

        # Create persona generator with attribution manager
        persona_generator = MusicPersonaGenerator()
        persona_generator.source_attribution_manager = temp_attribution_manager

        # Mock the enhanced genre mapper
        mock_mapper = Mock()
        mock_mapper.map_traits_to_genres = AsyncMock(return_value=[mock_match])
        persona_generator.enhanced_genre_mapper = mock_mapper

        # Test genre mapping
        traits = ["energetic", "rebellious"]
        primary_genre, secondary_genres = await persona_generator._map_to_genres(traits)

        # Verify genre was returned
        assert primary_genre == "Test Rock"

        # Verify source was registered
        assert "https://sunoaiwiki.com/genres/rock" in temp_attribution_manager.sources
        registered_source = temp_attribution_manager.sources["https://sunoaiwiki.com/genres/rock"]
        assert registered_source.content_type == "genre"
        assert registered_source.title == "Genre: Test Rock"

    @pytest.mark.asyncio
    async def test_attribution_persistence(self, temp_attribution_manager):
        """Test that attribution data persists across sessions"""

        # Register sources and track usage
        temp_attribution_manager.register_source(
            "https://sunoaiwiki.com/test", "genre", "Test Source", datetime.now()
        )
        temp_attribution_manager.track_content_usage(
            "test_content", "https://sunoaiwiki.com/test", "test usage"
        )

        # Save state
        await temp_attribution_manager.save_state()

        # Create new manager with same storage path
        new_manager = SourceAttributionManager(storage_path=str(temp_attribution_manager.storage_path))
        await new_manager.initialize()

        # Verify data was loaded
        assert "https://sunoaiwiki.com/test" in new_manager.sources
        assert len(new_manager.usage_records) == 1
        assert new_manager.sources["https://sunoaiwiki.com/test"].usage_count == 1

if __name__ == "__main__":
    # Run basic integration test
    async def run_basic_integration_test():
        temp_dir = tempfile.mkdtemp()
        try:
            # Create attribution manager
            attribution_manager = SourceAttributionManager(storage_path=temp_dir)
            await attribution_manager.initialize()

            # Create persona generator
            persona_generator = MusicPersonaGenerator()
            persona_generator.source_attribution_manager = attribution_manager

            # Register a test source
            attribution_manager.register_source(
                "https://sunoaiwiki.com/genres/test",
                "genre",
                "Test Genres",
                datetime.now()
            )

            # Test building attributed context
            test_content = {"genres": ["rock", "indie"]}

            # Debug: Check what sources are available
            genre_sources = attribution_manager.get_source_urls("genre")
            print(f"Available genre sources: {genre_sources}")

            attributed_context = persona_generator.build_attributed_context_for_llm(
                test_content, "genre"
            )

            print(f"Attributed context: {attributed_context}")

            # Verify attribution is included
            if "Genre information sourced from:" in attributed_context:
                print("✓ Attribution integration test passed!")
            else:
                print("⚠ Attribution not found in context, but test completed")

        finally:
            shutil.rmtree(temp_dir)

    asyncio.run(run_basic_integration_test())
