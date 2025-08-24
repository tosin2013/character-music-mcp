#!/usr/bin/env python3
"""
Unit tests for SourceAttributionManager

Tests the SourceAttributionManager class with different content types to ensure
proper source attribution and tracking functionality.
"""

import pytest
import pytest_asyncio
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from source_attribution_manager import (
    SourceAttributionManager,
    ContentSource,
    AttributedContent,
    UsageRecord
)

class TestSourceAttributionManager:
    """Unit tests for SourceAttributionManager class"""
    
    @pytest_asyncio.fixture
    async def temp_manager(self):
        """Create a temporary SourceAttributionManager for testing"""
        temp_dir = tempfile.mkdtemp()
        manager = SourceAttributionManager(storage_path=temp_dir)
        await manager.initialize()
        yield manager
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest_asyncio.fixture
    async def manager_with_data(self, temp_manager):
        """Create a manager with some test data"""
        # Register some test sources
        temp_manager.register_source(
            "https://sunoaiwiki.com/genres",
            "genre",
            "Music Genres List",
            datetime.now()
        )
        temp_manager.register_source(
            "https://sunoaiwiki.com/meta-tags",
            "meta_tag",
            "Meta Tags Reference",
            datetime.now()
        )
        temp_manager.register_source(
            "https://sunoaiwiki.com/techniques",
            "technique",
            "Production Techniques",
            datetime.now()
        )
        
        return temp_manager
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test SourceAttributionManager initialization"""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = SourceAttributionManager(storage_path=temp_dir)
            assert not manager.initialized
            assert len(manager.sources) == 0
            assert len(manager.usage_records) == 0
            
            await manager.initialize()
            assert manager.initialized
            assert Path(temp_dir).exists()
        finally:
            shutil.rmtree(temp_dir)
    
    def test_register_source(self, temp_manager):
        """Test source registration"""
        url = "https://example.com/test"
        content_type = "genre"
        title = "Test Source"
        download_date = datetime.now()
        
        temp_manager.register_source(url, content_type, title, download_date)
        
        assert url in temp_manager.sources
        source = temp_manager.sources[url]
        assert source.url == url
        assert source.content_type == content_type
        assert source.title == title
        assert source.download_date == download_date
        assert source.usage_count == 0
        assert source.last_used is None
    
    def test_build_attributed_context(self, manager_with_data):
        """Test building attributed content"""
        content = {"genres": ["rock", "pop"], "description": "Test content"}
        sources = ["https://sunoaiwiki.com/genres", "https://sunoaiwiki.com/meta-tags"]
        
        attributed_content = manager_with_data.build_attributed_context(content, sources)
        
        assert isinstance(attributed_content, AttributedContent)
        assert attributed_content.content == content
        assert len(attributed_content.sources) == 2
        assert attributed_content.attribution_text != ""
        assert attributed_content.content_id != ""
        assert isinstance(attributed_content.created_at, datetime)
        
        # Check that sources are properly referenced
        source_urls = [s.url for s in attributed_content.sources]
        assert "https://sunoaiwiki.com/genres" in source_urls
        assert "https://sunoaiwiki.com/meta-tags" in source_urls
    
    def test_build_attributed_context_unknown_source(self, temp_manager):
        """Test building attributed content with unknown source"""
        content = {"test": "data"}
        sources = ["https://unknown-source.com"]
        
        attributed_content = temp_manager.build_attributed_context(content, sources)
        
        assert len(attributed_content.sources) == 1
        assert attributed_content.sources[0].url == "https://unknown-source.com"
        assert attributed_content.sources[0].content_type == "general"
        
        # Should have registered the unknown source
        assert "https://unknown-source.com" in temp_manager.sources
    
    def test_format_source_references_single_genre(self, manager_with_data):
        """Test source reference formatting for single genre source"""
        sources = ["https://sunoaiwiki.com/genres"]
        
        formatted = manager_with_data.format_source_references(sources)
        
        assert "Genre information sourced from:" in formatted
        assert "Music Genres List" in formatted
        assert "https://sunoaiwiki.com/genres" in formatted
    
    def test_format_source_references_single_meta_tag(self, manager_with_data):
        """Test source reference formatting for single meta tag source"""
        sources = ["https://sunoaiwiki.com/meta-tags"]
        
        formatted = manager_with_data.format_source_references(sources)
        
        assert "Meta tag data sourced from:" in formatted
        assert "Meta Tags Reference" in formatted
        assert "https://sunoaiwiki.com/meta-tags" in formatted
    
    def test_format_source_references_single_technique(self, manager_with_data):
        """Test source reference formatting for single technique source"""
        sources = ["https://sunoaiwiki.com/techniques"]
        
        formatted = manager_with_data.format_source_references(sources)
        
        assert "Technique information sourced from:" in formatted
        assert "Production Techniques" in formatted
        assert "https://sunoaiwiki.com/techniques" in formatted
    
    def test_format_source_references_mixed(self, manager_with_data):
        """Test source reference formatting for mixed sources"""
        sources = [
            "https://sunoaiwiki.com/genres",
            "https://sunoaiwiki.com/meta-tags"
        ]
        
        formatted = manager_with_data.format_source_references(sources)
        
        assert "multiple wiki pages" in formatted
        assert "Music Genres List" in formatted
        assert "Meta Tags Reference" in formatted
    
    def test_format_source_references_empty(self, temp_manager):
        """Test source reference formatting with empty sources"""
        formatted = temp_manager.format_source_references([])
        assert formatted == ""
    
    def test_track_content_usage(self, manager_with_data):
        """Test content usage tracking"""
        content_id = "test_content_123"
        source_url = "https://sunoaiwiki.com/genres"
        context = "Used in album generation"
        
        # Track usage
        manager_with_data.track_content_usage(content_id, source_url, context)
        
        # Check source usage count updated
        source = manager_with_data.sources[source_url]
        assert source.usage_count == 1
        assert source.last_used is not None
        
        # Check usage record created
        assert len(manager_with_data.usage_records) == 1
        record = manager_with_data.usage_records[0]
        assert record.content_id == content_id
        assert record.source_url == source_url
        assert record.context == context
        assert isinstance(record.used_at, datetime)
    
    def test_track_content_usage_unknown_source(self, temp_manager):
        """Test tracking usage for unknown source"""
        content_id = "test_content"
        source_url = "https://unknown.com"
        
        # Should not raise error, just log warning
        temp_manager.track_content_usage(content_id, source_url, "test")
        
        # Usage record should still be created
        assert len(temp_manager.usage_records) == 1
        assert temp_manager.usage_records[0].source_url == source_url
    
    def test_track_content_usage_uninitialized(self):
        """Test tracking usage when manager is not initialized"""
        manager = SourceAttributionManager()
        
        # Should not raise error, just log warning
        manager.track_content_usage("test", "https://example.com", "test")
        
        # No records should be created
        assert len(manager.usage_records) == 0
    
    def test_get_source_urls_all(self, manager_with_data):
        """Test getting all source URLs"""
        urls = manager_with_data.get_source_urls()
        
        assert len(urls) == 3
        assert "https://sunoaiwiki.com/genres" in urls
        assert "https://sunoaiwiki.com/meta-tags" in urls
        assert "https://sunoaiwiki.com/techniques" in urls
    
    def test_get_source_urls_filtered(self, manager_with_data):
        """Test getting source URLs filtered by content type"""
        # Test genre filter
        genre_urls = manager_with_data.get_source_urls("genre")
        assert len(genre_urls) == 1
        assert "https://sunoaiwiki.com/genres" in genre_urls
        
        # Test meta_tag filter
        tag_urls = manager_with_data.get_source_urls("meta_tag")
        assert len(tag_urls) == 1
        assert "https://sunoaiwiki.com/meta-tags" in tag_urls
        
        # Test technique filter
        technique_urls = manager_with_data.get_source_urls("technique")
        assert len(technique_urls) == 1
        assert "https://sunoaiwiki.com/techniques" in technique_urls
        
        # Test non-existent filter
        empty_urls = manager_with_data.get_source_urls("nonexistent")
        assert len(empty_urls) == 0
    
    def test_get_usage_statistics(self, manager_with_data):
        """Test usage statistics generation"""
        # Track some usage
        manager_with_data.track_content_usage("content1", "https://sunoaiwiki.com/genres", "test1")
        manager_with_data.track_content_usage("content2", "https://sunoaiwiki.com/genres", "test2")
        manager_with_data.track_content_usage("content3", "https://sunoaiwiki.com/meta-tags", "test3")
        
        stats = manager_with_data.get_usage_statistics()
        
        assert stats['total_sources'] == 3
        assert stats['total_usage_records'] == 3
        assert stats['sources_by_type']['genre'] == 1
        assert stats['sources_by_type']['meta_tag'] == 1
        assert stats['sources_by_type']['technique'] == 1
        
        # Check most used sources
        assert len(stats['most_used_sources']) == 3
        most_used = stats['most_used_sources'][0]
        assert most_used['url'] == "https://sunoaiwiki.com/genres"
        assert most_used['usage_count'] == 2
        
        # Check recent usage
        assert len(stats['recent_usage']) == 3
        assert all('content_id' in record for record in stats['recent_usage'])
        assert all('source_url' in record for record in stats['recent_usage'])
        assert all('used_at' in record for record in stats['recent_usage'])
    
    @pytest.mark.asyncio
    async def test_save_and_load_state(self, temp_manager):
        """Test saving and loading state"""
        # Add some data
        temp_manager.register_source(
            "https://example.com",
            "genre",
            "Test Source",
            datetime.now()
        )
        temp_manager.track_content_usage("content1", "https://example.com", "test")
        
        # Save state
        await temp_manager.save_state()
        
        # Verify files were created
        sources_file = temp_manager.storage_path / "sources.json"
        usage_file = temp_manager.storage_path / "usage_records.json"
        assert sources_file.exists()
        assert usage_file.exists()
        
        # Create new manager with same storage path
        new_manager = SourceAttributionManager(storage_path=str(temp_manager.storage_path))
        await new_manager.initialize()
        
        # Check data was loaded
        assert "https://example.com" in new_manager.sources
        assert len(new_manager.usage_records) == 1
        assert new_manager.sources["https://example.com"].usage_count == 1
    
    @pytest.mark.asyncio
    async def test_load_corrupted_data(self, temp_manager):
        """Test loading corrupted data files"""
        # Create corrupted sources file
        sources_file = temp_manager.storage_path / "sources.json"
        with open(sources_file, 'w') as f:
            f.write("invalid json content")
        
        # Create corrupted usage file
        usage_file = temp_manager.storage_path / "usage_records.json"
        with open(usage_file, 'w') as f:
            f.write("invalid json content")
        
        # Should handle corruption gracefully
        new_manager = SourceAttributionManager(storage_path=str(temp_manager.storage_path))
        await new_manager.initialize()
        
        # Should have empty data due to corruption
        assert len(new_manager.sources) == 0
        assert len(new_manager.usage_records) == 0
    
    def test_extract_title_from_url(self, temp_manager):
        """Test title extraction from URL"""
        # Test with path
        title = temp_manager._extract_title_from_url("https://example.com/music-genres")
        assert title == "Music Genres"
        
        # Test with complex path
        title = temp_manager._extract_title_from_url("https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/")
        assert "Music Genres And Styles" in title
        
        # Test with file extension
        title = temp_manager._extract_title_from_url("https://example.com/page.html")
        assert title == "Page"
        
        # Test with invalid URL
        title = temp_manager._extract_title_from_url("invalid-url")
        assert title == "invalid-url"
    
    def test_generate_content_id(self, temp_manager):
        """Test content ID generation"""
        content1 = {"test": "data"}
        sources1 = ["https://example.com"]
        
        content2 = {"test": "data"}
        sources2 = ["https://example.com"]
        
        content3 = {"different": "data"}
        sources3 = ["https://example.com"]
        
        # Same content and sources should generate same ID
        id1 = temp_manager._generate_content_id(content1, sources1)
        id2 = temp_manager._generate_content_id(content2, sources2)
        assert id1 == id2
        
        # Different content should generate different ID
        id3 = temp_manager._generate_content_id(content3, sources3)
        assert id1 != id3
        
        # IDs should be reasonable length
        assert len(id1) == 16
        assert isinstance(id1, str)

class TestContentSource:
    """Unit tests for ContentSource class"""
    
    def test_content_source_initialization(self):
        """Test ContentSource initialization"""
        url = "https://example.com"
        content_type = "genre"
        title = "Test Source"
        download_date = datetime.now()
        
        source = ContentSource(
            url=url,
            content_type=content_type,
            title=title,
            download_date=download_date
        )
        
        assert source.url == url
        assert source.content_type == content_type
        assert source.title == title
        assert source.download_date == download_date
        assert source.last_used is None
        assert source.usage_count == 0
    
    def test_content_source_to_dict(self):
        """Test ContentSource serialization to dictionary"""
        download_date = datetime.now()
        last_used = datetime.now() - timedelta(hours=1)
        
        source = ContentSource(
            url="https://example.com",
            content_type="genre",
            title="Test Source",
            download_date=download_date,
            last_used=last_used,
            usage_count=5
        )
        
        data = source.to_dict()
        
        assert data['url'] == "https://example.com"
        assert data['content_type'] == "genre"
        assert data['title'] == "Test Source"
        assert data['download_date'] == download_date.isoformat()
        assert data['last_used'] == last_used.isoformat()
        assert data['usage_count'] == 5
    
    def test_content_source_from_dict(self):
        """Test ContentSource deserialization from dictionary"""
        download_date = datetime.now()
        last_used = datetime.now() - timedelta(hours=1)
        
        data = {
            'url': "https://example.com",
            'content_type': "genre",
            'title': "Test Source",
            'download_date': download_date.isoformat(),
            'last_used': last_used.isoformat(),
            'usage_count': 5
        }
        
        source = ContentSource.from_dict(data)
        
        assert source.url == "https://example.com"
        assert source.content_type == "genre"
        assert source.title == "Test Source"
        assert abs((source.download_date - download_date).total_seconds()) < 1
        assert abs((source.last_used - last_used).total_seconds()) < 1
        assert source.usage_count == 5
    
    def test_content_source_from_dict_no_last_used(self):
        """Test ContentSource deserialization without last_used"""
        data = {
            'url': "https://example.com",
            'content_type': "genre",
            'title': "Test Source",
            'download_date': datetime.now().isoformat(),
            'usage_count': 0
        }
        
        source = ContentSource.from_dict(data)
        
        assert source.last_used is None
        assert source.usage_count == 0

class TestAttributedContent:
    """Unit tests for AttributedContent class"""
    
    def test_attributed_content_initialization(self):
        """Test AttributedContent initialization"""
        content = {"test": "data"}
        sources = [
            ContentSource(
                url="https://example.com",
                content_type="genre",
                title="Test Source",
                download_date=datetime.now()
            )
        ]
        attribution_text = "Information sourced from: Test Source"
        content_id = "test123"
        
        attributed = AttributedContent(
            content=content,
            sources=sources,
            attribution_text=attribution_text,
            content_id=content_id
        )
        
        assert attributed.content == content
        assert attributed.sources == sources
        assert attributed.attribution_text == attribution_text
        assert attributed.content_id == content_id
        assert isinstance(attributed.created_at, datetime)
    
    def test_attributed_content_to_dict(self):
        """Test AttributedContent serialization"""
        content = {"test": "data"}
        source = ContentSource(
            url="https://example.com",
            content_type="genre",
            title="Test Source",
            download_date=datetime.now()
        )
        
        attributed = AttributedContent(
            content=content,
            sources=[source],
            attribution_text="Test attribution",
            content_id="test123"
        )
        
        data = attributed.to_dict()
        
        assert data['content'] == content
        assert len(data['sources']) == 1
        assert data['sources'][0]['url'] == "https://example.com"
        assert data['attribution_text'] == "Test attribution"
        assert data['content_id'] == "test123"
        assert 'created_at' in data

class TestUsageRecord:
    """Unit tests for UsageRecord class"""
    
    def test_usage_record_initialization(self):
        """Test UsageRecord initialization"""
        content_id = "test123"
        source_url = "https://example.com"
        used_at = datetime.now()
        context = "Test usage"
        
        record = UsageRecord(
            content_id=content_id,
            source_url=source_url,
            used_at=used_at,
            context=context
        )
        
        assert record.content_id == content_id
        assert record.source_url == source_url
        assert record.used_at == used_at
        assert record.context == context
    
    def test_usage_record_to_dict(self):
        """Test UsageRecord serialization"""
        used_at = datetime.now()
        
        record = UsageRecord(
            content_id="test123",
            source_url="https://example.com",
            used_at=used_at,
            context="Test usage"
        )
        
        data = record.to_dict()
        
        assert data['content_id'] == "test123"
        assert data['source_url'] == "https://example.com"
        assert data['used_at'] == used_at.isoformat()
        assert data['context'] == "Test usage"

if __name__ == "__main__":
    # Run basic tests
    async def run_basic_tests():
        temp_dir = tempfile.mkdtemp()
        try:
            manager = SourceAttributionManager(storage_path=temp_dir)
            await manager.initialize()
            
            # Test source registration
            url = "https://example.com/test"
            manager.register_source(url, "genre", "Test Source", datetime.now())
            assert url in manager.sources
            print("✓ Source registration test passed")
            
            # Test attribution building
            content = {"test": "data"}
            attributed = manager.build_attributed_context(content, [url])
            assert attributed.content == content
            assert len(attributed.sources) == 1
            print("✓ Attribution building test passed")
            
            # Test usage tracking
            manager.track_content_usage(attributed.content_id, url, "test usage")
            assert manager.sources[url].usage_count == 1
            print("✓ Usage tracking test passed")
            
            # Test statistics
            stats = manager.get_usage_statistics()
            assert stats['total_sources'] == 1
            assert stats['total_usage_records'] == 1
            print("✓ Statistics generation test passed")
            
            print("Basic SourceAttributionManager unit tests passed!")
            
        finally:
            shutil.rmtree(temp_dir)
    
    import asyncio
    asyncio.run(run_basic_tests())