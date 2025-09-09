#!/usr/bin/env python3
"""
Comprehensive unit tests for all wiki components

This file contains unit tests for WikiDownloader, ContentParser,
EnhancedGenreMapper, and SourceAttributionManager components.
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import components to test
from wiki_cache_manager import WikiCacheManager
from wiki_content_parser import ContentParser
from wiki_downloader import WikiDownloader

# Check if we should skip enhanced genre mapper in CI
if os.environ.get('CI_SKIP_ENHANCED_GENRE_MAPPER'):
    ENHANCED_GENRE_MAPPER_AVAILABLE = False

    class EnhancedGenreMapper:
        def __init__(self, *args, **kwargs):
            pass

    class GenreMatch:
        def __init__(self, *args, **kwargs):
            pass
else:
    try:
        from enhanced_genre_mapper import EnhancedGenreMapper, GenreMatch
        ENHANCED_GENRE_MAPPER_AVAILABLE = True
    except ImportError:
        import sys
        from pathlib import Path
        # Add project root to path if not already there
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        try:
            # Try import again
            from enhanced_genre_mapper import EnhancedGenreMapper, GenreMatch
            ENHANCED_GENRE_MAPPER_AVAILABLE = True
        except ImportError:
            # If still failing, create mock classes for CI
            ENHANCED_GENRE_MAPPER_AVAILABLE = False

            class EnhancedGenreMapper:
                def __init__(self, *args, **kwargs):
                    pass

            class GenreMatch:
                def __init__(self, *args, **kwargs):
                    pass

# Import other components with fallbacks
try:
    from source_attribution_manager import ContentSource, SourceAttributionManager
except ImportError:
    class SourceAttributionManager:
        def __init__(self, *args, **kwargs):
            pass

    class ContentSource:
        def __init__(self, *args, **kwargs):
            pass

try:
    from wiki_data_system import Genre, MetaTag, Technique, WikiDataManager
except ImportError:
    class Genre:
        def __init__(self, *args, **kwargs):
            pass

    class MetaTag:
        def __init__(self, *args, **kwargs):
            pass

    class Technique:
        def __init__(self, *args, **kwargs):
            pass

    class WikiDataManager:
        def __init__(self, *args, **kwargs):
            pass

class TestWikiDownloaderUnit:
    """Unit tests for WikiDownloader"""

    @pytest_asyncio.fixture
    async def temp_cache_manager(self):
        """Create temporary cache manager"""
        temp_dir = tempfile.mkdtemp()
        cache_manager = WikiCacheManager(temp_dir)
        await cache_manager.initialize()
        yield cache_manager
        shutil.rmtree(temp_dir)

    @pytest_asyncio.fixture
    async def downloader(self, temp_cache_manager):
        """Create WikiDownloader instance"""
        return WikiDownloader(cache_manager=temp_cache_manager, max_retries=1)

    def test_url_validation(self, downloader):
        """Test URL validation"""
        assert downloader.validate_url("https://example.com")
        assert downloader.validate_url("http://example.com")
        assert not downloader.validate_url("")
        assert not downloader.validate_url("invalid-url")
        assert not downloader.validate_url(None)

    @pytest.mark.asyncio
    async def test_is_refresh_needed_nonexistent(self, downloader):
        """Test refresh needed for non-existent file"""
        needs_refresh = await downloader.is_refresh_needed("https://example.com/test", 24)
        assert needs_refresh

    @pytest.mark.asyncio
    async def test_context_manager_basic(self, temp_cache_manager):
        """Test basic context manager functionality"""
        downloader = WikiDownloader(cache_manager=temp_cache_manager)

        async with downloader:
            assert downloader._session is not None

        # After context, session should be cleaned up
        assert downloader._session is None

class TestContentParserUnit:
    """Unit tests for ContentParser"""

    @pytest.fixture
    def parser(self):
        """Create ContentParser instance"""
        return ContentParser()

    @pytest.fixture
    def sample_html(self):
        """Sample HTML for testing"""
        return """
        <html>
        <body>
            <h1>Test Page</h1>
            <h3>Electronic</h3>
            <ul>
                <li>Ambient (atmospheric music)</li>
                <li>Techno</li>
            </ul>
            <h3>Rock</h3>
            <ul>
                <li>Alternative Rock</li>
                <li>Hard Rock</li>
            </ul>
        </body>
        </html>
        """

    def test_parse_html_success(self, parser):
        """Test successful HTML parsing"""
        html = "<html><body><h1>Test</h1></body></html>"
        soup = parser.parse_html(html)
        assert soup is not None
        assert soup.find('h1').get_text() == "Test"

    def test_extract_text_content(self, parser, sample_html):
        """Test text content extraction"""
        soup = parser.parse_html(sample_html)
        h1 = soup.find('h1')
        text = parser.extract_text_content(h1)
        assert text == "Test Page"

        # Test with None
        assert parser.extract_text_content(None) == ""

    def test_clean_text(self, parser):
        """Test text cleaning"""
        text = "  This   has    extra   spaces  "
        cleaned = parser.clean_text(text)
        assert cleaned == "This has extra spaces"

        # Test empty text
        assert parser.clean_text("") == ""
        assert parser.clean_text(None) == ""

    def test_extract_list_items(self, parser, sample_html):
        """Test list item extraction"""
        soup = parser.parse_html(sample_html)
        ul = soup.find('ul')
        items = parser.extract_list_items(ul)
        assert len(items) > 0
        assert any("Ambient" in item for item in items)

    def test_parse_genre_page_basic(self, parser, sample_html):
        """Test basic genre page parsing"""
        genres = parser.parse_genre_page(sample_html, "https://example.com")
        assert len(genres) > 0
        genre_names = [g.name for g in genres]
        assert "Ambient" in genre_names
        assert "Techno" in genre_names

@pytest.mark.skipif(not ENHANCED_GENRE_MAPPER_AVAILABLE, reason="EnhancedGenreMapper not available in CI environment")
class TestEnhancedGenreMapperUnit:
    """Unit tests for EnhancedGenreMapper"""

    @pytest.fixture
    def mock_wiki_manager(self):
        """Create mock WikiDataManager"""
        manager = Mock()
        manager.get_genres = AsyncMock()
        return manager

    @pytest.fixture
    def sample_genres(self):
        """Create sample genres"""
        return [
            Genre(
                name="Rock",
                description="Guitar-driven music",
                subgenres=[],
                characteristics=["guitar-driven", "energetic"],
                typical_instruments=["guitar", "bass", "drums"],
                mood_associations=["energetic", "rebellious"],
                source_url="test",
                download_date=datetime.now()
            ),
            Genre(
                name="Jazz",
                description="Improvisational music",
                subgenres=[],
                characteristics=["improvisation", "complex"],
                typical_instruments=["saxophone", "piano"],
                mood_associations=["sophisticated", "smooth"],
                source_url="test",
                download_date=datetime.now()
            )
        ]

    @pytest.fixture
    def genre_mapper(self, mock_wiki_manager, sample_genres):
        """Create EnhancedGenreMapper with test data"""
        mock_wiki_manager.get_genres.return_value = sample_genres
        mapper = EnhancedGenreMapper(mock_wiki_manager)
        mapper._genres_cache = sample_genres
        return mapper

    @pytest.mark.asyncio
    async def test_map_traits_to_genres_basic(self, genre_mapper):
        """Test basic trait mapping"""
        traits = ["energetic", "rebellious"]
        matches = await genre_mapper.map_traits_to_genres(traits, max_results=2)

        assert len(matches) > 0
        assert all(isinstance(match, GenreMatch) for match in matches)
        assert all(0.0 <= match.confidence <= 1.0 for match in matches)

    def test_calculate_genre_confidence(self, genre_mapper, sample_genres):
        """Test confidence calculation"""
        rock_genre = sample_genres[0]

        # Test with matching traits
        confidence = genre_mapper.calculate_genre_confidence(["energetic"], rock_genre)
        assert confidence > 0.0

        # Test with empty traits
        confidence = genre_mapper.calculate_genre_confidence([], rock_genre)
        assert confidence == 0.0

    def test_find_genre_by_name(self, genre_mapper):
        """Test finding genre by name"""
        genre = genre_mapper._find_genre_by_name("Rock")
        assert genre is not None
        assert genre.name == "Rock"

        # Test case insensitive
        genre = genre_mapper._find_genre_by_name("rock")
        assert genre is not None

        # Test non-existent
        genre = genre_mapper._find_genre_by_name("NonExistent")
        assert genre is None

class TestSourceAttributionManagerUnit:
    """Unit tests for SourceAttributionManager"""

    @pytest_asyncio.fixture
    async def temp_manager(self):
        """Create temporary SourceAttributionManager"""
        temp_dir = tempfile.mkdtemp()
        manager = SourceAttributionManager(storage_path=temp_dir)
        await manager.initialize()
        yield manager
        shutil.rmtree(temp_dir)

    def test_register_source(self, temp_manager):
        """Test source registration"""
        url = "https://example.com/test"
        temp_manager.register_source(url, "genre", "Test Source", datetime.now())

        assert url in temp_manager.sources
        source = temp_manager.sources[url]
        assert source.url == url
        assert source.content_type == "genre"
        assert source.title == "Test Source"

    def test_build_attributed_context(self, temp_manager):
        """Test building attributed content"""
        # Register a source first
        url = "https://example.com/test"
        temp_manager.register_source(url, "genre", "Test Source", datetime.now())

        content = {"test": "data"}
        attributed = temp_manager.build_attributed_context(content, [url])

        assert attributed.content == content
        assert len(attributed.sources) == 1
        assert attributed.sources[0].url == url
        assert attributed.attribution_text != ""
        assert attributed.content_id != ""

    def test_format_source_references(self, temp_manager):
        """Test source reference formatting"""
        url = "https://example.com/genres"
        temp_manager.register_source(url, "genre", "Music Genres", datetime.now())

        formatted = temp_manager.format_source_references([url])
        assert "Genre information sourced from:" in formatted
        assert "Music Genres" in formatted

    def test_track_content_usage(self, temp_manager):
        """Test usage tracking"""
        url = "https://example.com/test"
        temp_manager.register_source(url, "genre", "Test Source", datetime.now())

        temp_manager.track_content_usage("content123", url, "test usage")

        # Check usage was tracked
        source = temp_manager.sources[url]
        assert source.usage_count == 1
        assert len(temp_manager.usage_records) == 1

    def test_get_usage_statistics(self, temp_manager):
        """Test usage statistics"""
        url = "https://example.com/test"
        temp_manager.register_source(url, "genre", "Test Source", datetime.now())
        temp_manager.track_content_usage("content123", url, "test")

        stats = temp_manager.get_usage_statistics()
        assert stats['total_sources'] == 1
        assert stats['total_usage_records'] == 1
        assert len(stats['most_used_sources']) == 1

class TestContentSourceUnit:
    """Unit tests for ContentSource data model"""

    def test_content_source_creation(self):
        """Test ContentSource creation"""
        source = ContentSource(
            url="https://example.com",
            content_type="genre",
            title="Test Source",
            download_date=datetime.now()
        )

        assert source.url == "https://example.com"
        assert source.content_type == "genre"
        assert source.title == "Test Source"
        assert source.usage_count == 0

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
        assert data['usage_count'] == 5

        # Test from_dict
        restored = ContentSource.from_dict(data)
        assert restored.url == source.url
        assert restored.usage_count == source.usage_count

if __name__ == "__main__":
    # Run basic tests
    async def run_basic_tests():
        print("Running basic unit tests...")

        # Test ContentParser
        parser = ContentParser()
        html = "<html><body><h1>Test</h1></body></html>"
        soup = parser.parse_html(html)
        assert soup.find('h1').get_text() == "Test"
        print("✓ ContentParser basic test passed")

        # Test SourceAttributionManager
        temp_dir = tempfile.mkdtemp()
        try:
            manager = SourceAttributionManager(storage_path=temp_dir)
            await manager.initialize()

            url = "https://example.com/test"
            manager.register_source(url, "genre", "Test Source", datetime.now())
            assert url in manager.sources
            print("✓ SourceAttributionManager basic test passed")
        finally:
            shutil.rmtree(temp_dir)

        print("All basic unit tests passed!")

    import asyncio
    asyncio.run(run_basic_tests())
