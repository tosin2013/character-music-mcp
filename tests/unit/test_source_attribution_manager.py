#!/usr/bin/env python3
"""
Tests for SourceAttributionManager

Tests the source attribution system for tracking content sources and building
attribution metadata for LLM context.
"""

import asyncio
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
import pytest_asyncio

from source_attribution_manager import (
    AttributedContent,
    ContentSource,
    SourceAttributionManager,
)


class TestSourceAttributionManager:
    """Test suite for SourceAttributionManager"""

    @pytest_asyncio.fixture
    async def temp_manager(self):
        """Create a temporary SourceAttributionManager for testing"""
        temp_dir = tempfile.mkdtemp()
        manager = SourceAttributionManager(storage_path=temp_dir)
        await manager.initialize()
        yield manager
        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test manager initialization"""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = SourceAttributionManager(storage_path=temp_dir)
            assert not manager.initialized

            await manager.initialize()
            assert manager.initialized
            assert Path(temp_dir).exists()
        finally:
            shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_register_source(self, temp_manager):
        """Test source registration"""
        url = "https://sunoaiwiki.com/resources/genres"
        title = "Music Genres List"
        content_type = "genre"
        download_date = datetime.now()

        temp_manager.register_source(url, content_type, title, download_date)

        assert url in temp_manager.sources
        source = temp_manager.sources[url]
        assert source.url == url
        assert source.title == title
        assert source.content_type == content_type
        assert source.download_date == download_date
        assert source.usage_count == 0

    @pytest.mark.asyncio
    async def test_build_attributed_content(self, temp_manager):
        """Test building attributed content"""
        # Register some sources
        sources = [
            "https://sunoaiwiki.com/resources/genres",
            "https://sunoaiwiki.com/resources/meta-tags"
        ]

        temp_manager.register_source(
            sources[0], "genre", "Music Genres", datetime.now()
        )
        temp_manager.register_source(
            sources[1], "meta_tag", "Meta Tags", datetime.now()
        )

        content = {"genres": ["rock", "pop"], "tags": ["upbeat", "energetic"]}

        attributed_content = temp_manager.build_attributed_context(content, sources)

        assert isinstance(attributed_content, AttributedContent)
        assert attributed_content.content == content
        assert len(attributed_content.sources) == 2
        assert attributed_content.attribution_text != ""
        assert attributed_content.content_id != ""

    @pytest.mark.asyncio
    async def test_format_source_references(self, temp_manager):
        """Test source reference formatting"""
        # Test with single genre source
        genre_url = "https://sunoaiwiki.com/resources/genres"
        temp_manager.register_source(
            genre_url, "genre", "Music Genres", datetime.now()
        )

        formatted = temp_manager.format_source_references([genre_url])
        assert "Genre information sourced from:" in formatted
        assert "Music Genres" in formatted
        assert genre_url in formatted

        # Test with multiple mixed sources
        meta_url = "https://sunoaiwiki.com/resources/meta-tags"
        temp_manager.register_source(
            meta_url, "meta_tag", "Meta Tags", datetime.now()
        )

        formatted = temp_manager.format_source_references([genre_url, meta_url])
        assert "multiple wiki pages" in formatted

    @pytest.mark.asyncio
    async def test_track_content_usage(self, temp_manager):
        """Test content usage tracking"""
        url = "https://sunoaiwiki.com/resources/genres"
        temp_manager.register_source(url, "genre", "Music Genres", datetime.now())

        content_id = "test_content_123"
        context = "Used in album generation"

        # Track usage
        temp_manager.track_content_usage(content_id, url, context)

        # Check source usage count updated
        source = temp_manager.sources[url]
        assert source.usage_count == 1
        assert source.last_used is not None

        # Check usage record created
        assert len(temp_manager.usage_records) == 1
        record = temp_manager.usage_records[0]
        assert record.content_id == content_id
        assert record.source_url == url
        assert record.context == context

    @pytest.mark.asyncio
    async def test_get_source_urls(self, temp_manager):
        """Test getting source URLs with filtering"""
        # Register sources of different types
        temp_manager.register_source(
            "https://sunoaiwiki.com/genres", "genre", "Genres", datetime.now()
        )
        temp_manager.register_source(
            "https://sunoaiwiki.com/tags", "meta_tag", "Tags", datetime.now()
        )
        temp_manager.register_source(
            "https://sunoaiwiki.com/tips", "technique", "Tips", datetime.now()
        )

        # Test getting all URLs
        all_urls = temp_manager.get_source_urls()
        assert len(all_urls) == 3

        # Test filtering by type
        genre_urls = temp_manager.get_source_urls("genre")
        assert len(genre_urls) == 1
        assert "https://sunoaiwiki.com/genres" in genre_urls

        tag_urls = temp_manager.get_source_urls("meta_tag")
        assert len(tag_urls) == 1
        assert "https://sunoaiwiki.com/tags" in tag_urls

    @pytest.mark.asyncio
    async def test_usage_statistics(self, temp_manager):
        """Test usage statistics generation"""
        # Register sources and track usage
        url1 = "https://sunoaiwiki.com/genres"
        url2 = "https://sunoaiwiki.com/tags"

        temp_manager.register_source(url1, "genre", "Genres", datetime.now())
        temp_manager.register_source(url2, "meta_tag", "Tags", datetime.now())

        # Track some usage
        temp_manager.track_content_usage("content1", url1, "test1")
        temp_manager.track_content_usage("content2", url1, "test2")
        temp_manager.track_content_usage("content3", url2, "test3")

        stats = temp_manager.get_usage_statistics()

        assert stats['total_sources'] == 2
        assert stats['total_usage_records'] == 3
        assert stats['sources_by_type']['genre'] == 1
        assert stats['sources_by_type']['meta_tag'] == 1
        assert len(stats['most_used_sources']) == 2
        assert len(stats['recent_usage']) == 3

        # Check most used source is first
        most_used = stats['most_used_sources'][0]
        assert most_used['url'] == url1
        assert most_used['usage_count'] == 2

    @pytest.mark.asyncio
    async def test_save_and_load_state(self, temp_manager):
        """Test saving and loading state"""
        # Register a source and track usage
        url = "https://sunoaiwiki.com/genres"
        temp_manager.register_source(url, "genre", "Genres", datetime.now())
        temp_manager.track_content_usage("content1", url, "test")

        # Save state
        await temp_manager.save_state()

        # Create new manager with same storage path
        new_manager = SourceAttributionManager(storage_path=str(temp_manager.storage_path))
        await new_manager.initialize()

        # Check data was loaded
        assert url in new_manager.sources
        assert len(new_manager.usage_records) == 1
        assert new_manager.sources[url].usage_count == 1

    def test_content_source_serialization(self):
        """Test ContentSource serialization"""
        source = ContentSource(
            url="https://example.com",
            content_type="genre",
            title="Test Source",
            download_date=datetime.now(),
            usage_count=5
        )

        # Test to_dict
        data = source.to_dict()
        assert data['url'] == source.url
        assert data['content_type'] == source.content_type
        assert data['title'] == source.title
        assert data['usage_count'] == source.usage_count

        # Test from_dict
        restored = ContentSource.from_dict(data)
        assert restored.url == source.url
        assert restored.content_type == source.content_type
        assert restored.title == source.title
        assert restored.usage_count == source.usage_count

    @pytest.mark.asyncio
    async def test_attributed_content_creation(self, temp_manager):
        """Test AttributedContent creation and properties"""
        sources = ["https://sunoaiwiki.com/genres"]
        temp_manager.register_source(sources[0], "genre", "Genres", datetime.now())

        content = {"test": "data"}
        attributed = temp_manager.build_attributed_context(content, sources)

        assert attributed.content == content
        assert len(attributed.sources) == 1
        assert attributed.sources[0].url == sources[0]
        assert attributed.content_id != ""
        assert attributed.attribution_text != ""
        assert isinstance(attributed.created_at, datetime)

        # Test serialization
        data = attributed.to_dict()
        assert data['content'] == content
        assert len(data['sources']) == 1
        assert data['content_id'] == attributed.content_id

if __name__ == "__main__":
    # Run basic tests
    async def run_basic_tests():
        temp_dir = tempfile.mkdtemp()
        try:
            manager = SourceAttributionManager(storage_path=temp_dir)
            await manager.initialize()

            # Test basic functionality
            url = "https://sunoaiwiki.com/resources/genres"
            manager.register_source(url, "genre", "Music Genres", datetime.now())

            content = {"genres": ["rock", "pop"]}
            attributed = manager.build_attributed_context(content, [url])

            print(f"Attribution text: {attributed.attribution_text}")
            print(f"Content ID: {attributed.content_id}")

            manager.track_content_usage(attributed.content_id, url, "test usage")
            stats = manager.get_usage_statistics()
            print(f"Usage stats: {stats}")

            print("Basic tests passed!")

        finally:
            shutil.rmtree(temp_dir)

    asyncio.run(run_basic_tests())
