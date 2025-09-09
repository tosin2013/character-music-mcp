#!/usr/bin/env python3
"""
Unit tests for WikiDataManager

Tests the WikiDataManager class which coordinates all wiki data operations.
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from wiki_data_system import Genre, MetaTag, RefreshResult, Technique, WikiConfig, WikiDataManager


class TestWikiDataManager:
    """Unit tests for WikiDataManager class"""

    @pytest.fixture
    def sample_config(self):
        """Create a sample WikiConfig for testing"""
        return WikiConfig(
            enabled=True,
            local_storage_path="./test_data/wiki",
            refresh_interval_hours=24,
            fallback_to_hardcoded=True,
            genre_pages=["https://example.com/genres"],
            meta_tag_pages=["https://example.com/meta-tags"],
            tip_pages=["https://example.com/tips"]
        )

    @pytest.fixture
    def sample_genres(self):
        """Create sample genres for testing"""
        return [
            Genre(
                name="Rock",
                description="Guitar-driven music",
                subgenres=["Alternative Rock", "Hard Rock"],
                characteristics=["guitar-driven", "energetic"],
                typical_instruments=["electric guitar", "bass", "drums"],
                mood_associations=["energetic", "rebellious"],
                source_url="https://example.com/genres",
                download_date=datetime.now(),
                confidence_score=1.0
            ),
            Genre(
                name="Jazz",
                description="Improvisational music",
                subgenres=["Bebop", "Smooth Jazz"],
                characteristics=["improvisation", "complex harmonies"],
                typical_instruments=["saxophone", "piano", "trumpet"],
                mood_associations=["sophisticated", "smooth"],
                source_url="https://example.com/genres",
                download_date=datetime.now(),
                confidence_score=1.0
            )
        ]

    @pytest.fixture
    def sample_meta_tags(self):
        """Create sample meta tags for testing"""
        return [
            MetaTag(
                tag="verse",
                category="structural",
                description="Indicates verse section",
                usage_examples=["[verse]", "[verse 1]"],
                compatible_genres=["pop", "rock", "folk"],
                source_url="https://example.com/meta-tags",
                download_date=datetime.now()
            ),
            MetaTag(
                tag="upbeat",
                category="emotional",
                description="Creates energetic mood",
                usage_examples=["upbeat tempo", "upbeat melody"],
                compatible_genres=["pop", "electronic", "dance"],
                source_url="https://example.com/meta-tags",
                download_date=datetime.now()
            )
        ]

    @pytest.fixture
    def sample_techniques(self):
        """Create sample techniques for testing"""
        return [
            Technique(
                name="Prompt Structure",
                description="How to structure prompts effectively",
                technique_type="prompt_optimization",
                examples=["Use specific genre descriptions", "Include mood keywords"],
                applicable_scenarios=["song generation", "style specification"],
                source_url="https://example.com/tips",
                download_date=datetime.now()
            ),
            Technique(
                name="Vocal Direction",
                description="How to specify vocal styles",
                technique_type="vocal_style",
                examples=["raspy male vocals", "smooth female harmonies"],
                applicable_scenarios=["vocal specification", "style matching"],
                source_url="https://example.com/tips",
                download_date=datetime.now()
            )
        ]

    @pytest_asyncio.fixture
    async def temp_manager(self, sample_config):
        """Create a temporary WikiDataManager for testing"""
        temp_dir = tempfile.mkdtemp()
        config = WikiConfig(
            enabled=True,
            local_storage_path=temp_dir,
            refresh_interval_hours=24,
            fallback_to_hardcoded=True,
            genre_pages=["https://example.com/genres"],
            meta_tag_pages=["https://example.com/meta-tags"],
            tip_pages=["https://example.com/tips"]
        )

        manager = WikiDataManager()

        # Mock the dependencies
        manager.downloader = Mock()
        manager.downloader.download_all_configured_pages = AsyncMock()
        manager.downloader.get_cached_file_path = AsyncMock()

        manager.parser = Mock()
        manager.parser.parse_genre_page = Mock()
        manager.parser.parse_meta_tag_page = Mock()
        manager.parser.parse_tip_page = Mock()

        manager.attribution_manager = Mock()
        manager.attribution_manager.register_source = Mock()

        await manager.initialize(config)

        yield manager

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_initialization(self, sample_config):
        """Test WikiDataManager initialization"""
        manager = WikiDataManager()
        assert not manager.initialized
        assert manager.config is None

        await manager.initialize(sample_config)

        assert manager.initialized
        assert manager.config == sample_config
        assert manager.downloader is not None
        assert manager.parser is not None
        assert manager.attribution_manager is not None

    @pytest.mark.asyncio
    async def test_initialization_disabled(self):
        """Test initialization when wiki integration is disabled"""
        config = WikiConfig(enabled=False)
        manager = WikiDataManager()

        await manager.initialize(config)

        assert manager.initialized
        assert manager.config == config
        # Components should still be initialized for fallback functionality
        assert manager.downloader is not None
        assert manager.parser is not None

    @pytest.mark.asyncio
    async def test_get_genres_from_cache(self, temp_manager, sample_genres):
        """Test getting genres from cache"""
        # Pre-populate cache
        temp_manager._genres_cache = sample_genres

        genres = await temp_manager.get_genres()

        assert len(genres) == 2
        assert genres[0].name == "Rock"
        assert genres[1].name == "Jazz"

    @pytest.mark.asyncio
    async def test_get_genres_from_files(self, temp_manager, sample_genres):
        """Test getting genres from cached files"""
        # Mock file reading
        temp_manager.downloader.get_cached_file_path.return_value = "/fake/path/genres.html"
        temp_manager.parser.parse_genre_page.return_value = sample_genres

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open_read="<html>fake content</html>"):
                genres = await temp_manager.get_genres()

        assert len(genres) == 2
        assert temp_manager._genres_cache == sample_genres
        temp_manager.parser.parse_genre_page.assert_called()

    @pytest.mark.asyncio
    async def test_get_genres_fallback(self, temp_manager):
        """Test getting genres with fallback to hardcoded data"""
        # Mock no cached files
        temp_manager.downloader.get_cached_file_path.return_value = None

        genres = await temp_manager.get_genres()

        # Should return fallback genres
        assert len(genres) > 0
        assert all(isinstance(g, Genre) for g in genres)

    @pytest.mark.asyncio
    async def test_get_meta_tags_from_cache(self, temp_manager, sample_meta_tags):
        """Test getting meta tags from cache"""
        temp_manager._meta_tags_cache = sample_meta_tags

        meta_tags = await temp_manager.get_meta_tags()

        assert len(meta_tags) == 2
        assert meta_tags[0].tag == "verse"
        assert meta_tags[1].tag == "upbeat"

    @pytest.mark.asyncio
    async def test_get_meta_tags_filtered(self, temp_manager, sample_meta_tags):
        """Test getting meta tags filtered by category"""
        temp_manager._meta_tags_cache = sample_meta_tags

        structural_tags = await temp_manager.get_meta_tags("structural")
        emotional_tags = await temp_manager.get_meta_tags("emotional")

        assert len(structural_tags) == 1
        assert structural_tags[0].tag == "verse"

        assert len(emotional_tags) == 1
        assert emotional_tags[0].tag == "upbeat"

    @pytest.mark.asyncio
    async def test_get_techniques_from_cache(self, temp_manager, sample_techniques):
        """Test getting techniques from cache"""
        temp_manager._techniques_cache = sample_techniques

        techniques = await temp_manager.get_techniques("prompt_optimization")

        assert len(techniques) == 1
        assert techniques[0].name == "Prompt Structure"

    @pytest.mark.asyncio
    async def test_get_techniques_all_types(self, temp_manager, sample_techniques):
        """Test getting all techniques regardless of type"""
        temp_manager._techniques_cache = sample_techniques

        techniques = await temp_manager.get_techniques()

        assert len(techniques) == 2
        assert any(t.name == "Prompt Structure" for t in techniques)
        assert any(t.name == "Vocal Direction" for t in techniques)

    @pytest.mark.asyncio
    async def test_refresh_data_success(self, temp_manager):
        """Test successful data refresh"""
        # Mock successful downloads
        from wiki_downloader import BatchDownloadResult, DownloadResult

        download_results = [
            DownloadResult(
                url="https://example.com/genres",
                success=True,
                status_code=200,
                file_path="/fake/path/genres.html",
                error_message="",
                download_time=datetime.now(),
                file_size=1024
            )
        ]

        batch_result = BatchDownloadResult(
            total_urls=1,
            successful_downloads=1,
            failed_downloads=0,
            skipped_downloads=0,
            results=download_results,
            start_time=datetime.now(),
            end_time=datetime.now()
        )

        temp_manager.downloader.download_all_configured_pages.return_value = batch_result

        result = await temp_manager.refresh_data()

        assert result.success == True
        assert result.downloaded_pages == 1
        assert result.failed_pages == 0
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_refresh_data_partial_failure(self, temp_manager):
        """Test data refresh with partial failures"""
        from wiki_downloader import BatchDownloadResult, DownloadResult

        download_results = [
            DownloadResult(
                url="https://example.com/genres",
                success=True,
                status_code=200,
                file_path="/fake/path/genres.html",
                error_message="",
                download_time=datetime.now(),
                file_size=1024
            ),
            DownloadResult(
                url="https://example.com/meta-tags",
                success=False,
                status_code=404,
                file_path="",
                error_message="Not found",
                download_time=datetime.now(),
                file_size=0
            )
        ]

        batch_result = BatchDownloadResult(
            total_urls=2,
            successful_downloads=1,
            failed_downloads=1,
            skipped_downloads=0,
            results=download_results,
            start_time=datetime.now(),
            end_time=datetime.now()
        )

        temp_manager.downloader.download_all_configured_pages.return_value = batch_result

        result = await temp_manager.refresh_data()

        assert result.success == True  # Partial success is still success
        assert result.downloaded_pages == 1
        assert result.failed_pages == 1
        assert len(result.errors) == 1

    @pytest.mark.asyncio
    async def test_refresh_data_force(self, temp_manager):
        """Test forced data refresh"""
        temp_manager.downloader.download_all_configured_pages.return_value = Mock(
            total_urls=0,
            successful_downloads=0,
            failed_downloads=0,
            results=[]
        )

        result = await temp_manager.refresh_data(force=True)

        # Should call download with force parameter
        temp_manager.downloader.download_all_configured_pages.assert_called()
        call_args = temp_manager.downloader.download_all_configured_pages.call_args
        assert call_args[1]['max_age_hours'] == 0  # Force refresh

    @pytest.mark.asyncio
    async def test_refresh_data_disabled(self):
        """Test refresh when wiki integration is disabled"""
        config = WikiConfig(enabled=False)
        manager = WikiDataManager()
        await manager.initialize(config)

        result = await manager.refresh_data()

        assert result.success == False
        assert "Wiki integration is disabled" in result.errors[0]

    def test_get_source_urls_genres(self, temp_manager):
        """Test getting source URLs for genres"""
        urls = temp_manager.get_source_urls("genres")

        assert len(urls) == 1
        assert "https://example.com/genres" in urls

    def test_get_source_urls_meta_tags(self, temp_manager):
        """Test getting source URLs for meta tags"""
        urls = temp_manager.get_source_urls("meta_tags")

        assert len(urls) == 1
        assert "https://example.com/meta-tags" in urls

    def test_get_source_urls_techniques(self, temp_manager):
        """Test getting source URLs for techniques"""
        urls = temp_manager.get_source_urls("techniques")

        assert len(urls) == 1
        assert "https://example.com/tips" in urls

    def test_get_source_urls_all(self, temp_manager):
        """Test getting all source URLs"""
        urls = temp_manager.get_source_urls("all")

        assert len(urls) == 3
        assert "https://example.com/genres" in urls
        assert "https://example.com/meta-tags" in urls
        assert "https://example.com/tips" in urls

    def test_get_source_urls_unknown(self, temp_manager):
        """Test getting source URLs for unknown data type"""
        urls = temp_manager.get_source_urls("unknown")

        assert len(urls) == 0

    @pytest.mark.asyncio
    async def test_clear_cache(self, temp_manager, sample_genres):
        """Test cache clearing"""
        # Populate caches
        temp_manager._genres_cache = sample_genres
        temp_manager._meta_tags_cache = []
        temp_manager._techniques_cache = []

        await temp_manager.clear_cache()

        assert temp_manager._genres_cache is None
        assert temp_manager._meta_tags_cache is None
        assert temp_manager._techniques_cache is None

    @pytest.mark.asyncio
    async def test_get_cache_stats(self, temp_manager, sample_genres, sample_meta_tags):
        """Test cache statistics"""
        # Populate caches
        temp_manager._genres_cache = sample_genres
        temp_manager._meta_tags_cache = sample_meta_tags
        temp_manager._techniques_cache = []

        stats = await temp_manager.get_cache_stats()

        assert stats['genres_cached'] == 2
        assert stats['meta_tags_cached'] == 2
        assert stats['techniques_cached'] == 0
        assert stats['total_cached_items'] == 4
        assert 'last_refresh' in stats

    @pytest.mark.asyncio
    async def test_load_genres_from_files_error(self, temp_manager):
        """Test error handling when loading genres from files"""
        temp_manager.downloader.get_cached_file_path.return_value = "/fake/path"
        temp_manager.parser.parse_genre_page.side_effect = Exception("Parse error")

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open_read="<html>content</html>"):
                genres = await temp_manager._load_genres_from_files()

        assert len(genres) == 0  # Should return empty list on error

    @pytest.mark.asyncio
    async def test_load_meta_tags_from_files_error(self, temp_manager):
        """Test error handling when loading meta tags from files"""
        temp_manager.downloader.get_cached_file_path.return_value = "/fake/path"
        temp_manager.parser.parse_meta_tag_page.side_effect = Exception("Parse error")

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open_read="<html>content</html>"):
                meta_tags = await temp_manager._load_meta_tags_from_files()

        assert len(meta_tags) == 0  # Should return empty list on error

    @pytest.mark.asyncio
    async def test_load_techniques_from_files_error(self, temp_manager):
        """Test error handling when loading techniques from files"""
        temp_manager.downloader.get_cached_file_path.return_value = "/fake/path"
        temp_manager.parser.parse_tip_page.side_effect = Exception("Parse error")

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open_read="<html>content</html>"):
                techniques = await temp_manager._load_techniques_from_files()

        assert len(techniques) == 0  # Should return empty list on error

    def test_get_fallback_genres(self, temp_manager):
        """Test fallback genre generation"""
        fallback_genres = temp_manager._get_fallback_genres()

        assert len(fallback_genres) > 0
        assert all(isinstance(g, Genre) for g in fallback_genres)
        assert all(g.source_url == "hardcoded_fallback" for g in fallback_genres)

        # Check for some expected genres
        genre_names = [g.name.lower() for g in fallback_genres]
        assert any("rock" in name for name in genre_names)
        assert any("pop" in name for name in genre_names)
        assert any("jazz" in name for name in genre_names)

    def test_get_fallback_meta_tags(self, temp_manager):
        """Test fallback meta tag generation"""
        fallback_tags = temp_manager._get_fallback_meta_tags()

        assert len(fallback_tags) > 0
        assert all(isinstance(t, MetaTag) for t in fallback_tags)
        assert all(t.source_url == "hardcoded_fallback" for t in fallback_tags)

        # Check for some expected tags
        tag_names = [t.tag.lower() for t in fallback_tags]
        assert any("verse" in name for name in tag_names)
        assert any("chorus" in name for name in tag_names)

    def test_get_fallback_techniques(self, temp_manager):
        """Test fallback technique generation"""
        fallback_techniques = temp_manager._get_fallback_techniques()

        assert len(fallback_techniques) > 0
        assert all(isinstance(t, Technique) for t in fallback_techniques)
        assert all(t.source_url == "hardcoded_fallback" for t in fallback_techniques)

class TestWikiConfig:
    """Unit tests for WikiConfig class"""

    def test_wiki_config_defaults(self):
        """Test WikiConfig default values"""
        config = WikiConfig()

        assert config.enabled == True
        assert config.local_storage_path == "./data/wiki"
        assert config.refresh_interval_hours == 24
        assert config.fallback_to_hardcoded == True
        assert len(config.genre_pages) > 0
        assert len(config.meta_tag_pages) > 0
        assert len(config.tip_pages) > 0

    def test_wiki_config_custom_values(self):
        """Test WikiConfig with custom values"""
        config = WikiConfig(
            enabled=False,
            local_storage_path="/custom/path",
            refresh_interval_hours=12,
            fallback_to_hardcoded=False,
            genre_pages=["https://custom.com/genres"],
            meta_tag_pages=["https://custom.com/tags"],
            tip_pages=["https://custom.com/tips"]
        )

        assert config.enabled == False
        assert config.local_storage_path == "/custom/path"
        assert config.refresh_interval_hours == 12
        assert config.fallback_to_hardcoded == False
        assert config.genre_pages == ["https://custom.com/genres"]
        assert config.meta_tag_pages == ["https://custom.com/tags"]
        assert config.tip_pages == ["https://custom.com/tips"]

class TestRefreshResult:
    """Unit tests for RefreshResult class"""

    def test_refresh_result_initialization(self):
        """Test RefreshResult initialization"""
        result = RefreshResult(
            success=True,
            downloaded_pages=5,
            failed_pages=1,
            refresh_time=datetime.now(),
            errors=["Error 1", "Error 2"]
        )

        assert result.success == True
        assert result.downloaded_pages == 5
        assert result.failed_pages == 1
        assert isinstance(result.refresh_time, datetime)
        assert result.errors == ["Error 1", "Error 2"]

    def test_refresh_result_defaults(self):
        """Test RefreshResult with default values"""
        result = RefreshResult(success=True)

        assert result.success == True
        assert result.downloaded_pages == 0
        assert result.failed_pages == 0
        assert isinstance(result.refresh_time, datetime)
        assert result.errors == []

# Helper function for mocking file operations
def mock_open_read(content):
    """Create a mock for open() that returns specific content"""
    from unittest.mock import mock_open
    return mock_open(read_data=content)

if __name__ == "__main__":
    # Run basic tests
    async def run_basic_tests():
        config = WikiConfig(
            enabled=True,
            local_storage_path="./test_data",
            genre_pages=["https://example.com/genres"]
        )

        manager = WikiDataManager()

        # Mock dependencies
        manager.downloader = Mock()
        manager.parser = Mock()
        manager.attribution_manager = Mock()

        await manager.initialize(config)

        assert manager.initialized
        assert manager.config == config
        print("✓ Initialization test passed")

        # Test fallback data
        fallback_genres = manager._get_fallback_genres()
        assert len(fallback_genres) > 0
        print("✓ Fallback genres test passed")

        fallback_tags = manager._get_fallback_meta_tags()
        assert len(fallback_tags) > 0
        print("✓ Fallback meta tags test passed")

        print("Basic WikiDataManager unit tests passed!")

    import asyncio
    asyncio.run(run_basic_tests())
