#!/usr/bin/env python3
"""
Unit Tests for WikiContentParser

Tests the ContentParser class with sample HTML files to verify
parsing functionality, error handling, and content extraction.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from bs4 import BeautifulSoup

# Import the module under test
from wiki_content_parser import (
    ContentExtractionError,
    ContentParser,
    MalformedHTMLError,
    ParsedContent,
    ParseError,
)
from wiki_data_system import Genre, MetaTag, Technique


class TestContentParser:
    """Test suite for ContentParser class"""

    @pytest.fixture
    def parser(self):
        """Create ContentParser instance"""
        return ContentParser(parser="html.parser")

    @pytest.fixture
    def sample_genre_html(self):
        """Sample HTML content for genre page testing"""
        return """
        <html>
        <head><title>Music Genres</title></head>
        <body>
            <h1>List of Music Genres and Styles</h1>
            
            <h3>Electronic Music</h3>
            <ul>
                <li>Techno</li>
                <li>House (e.g., Deep House, Tech House)</li>
                <li>Trance</li>
                <li>Dubstep (Heavy bass and syncopated drum patterns)</li>
            </ul>
            
            <h3>Rock Music</h3>
            <ul>
                <li>Alternative Rock</li>
                <li>Indie Rock</li>
                <li>Hard Rock (Aggressive guitar-driven sound)</li>
            </ul>
            
            <h3>Jazz</h3>
            <ul>
                <li>Bebop</li>
                <li>Smooth Jazz</li>
                <li>Fusion (Combines jazz with other genres)</li>
            </ul>
        </body>
        </html>
        """

    @pytest.fixture
    def sample_meta_tag_html(self):
        """Sample HTML content for meta tag page testing"""
        return """
        <html>
        <head><title>Meta Tags</title></head>
        <body>
            <h1>List of Meta Tags</h1>
            
            <h3>Structural Tags</h3>
            <ul>
                <li><strong>verse</strong> : Defines verse sections of the song</li>
                <li><strong>chorus</strong> : Defines chorus sections with repeated lyrics</li>
                <li><strong>bridge</strong> : Connects different parts of the song</li>
            </ul>
            
            <h3>Emotional Tags</h3>
            <ul>
                <li>**happy** : Creates upbeat and joyful mood</li>
                <li>**melancholic** : Evokes sad and reflective emotions</li>
                <li>**energetic** : High-energy and dynamic feel</li>
            </ul>
            
            <h3>Instrumental Tags</h3>
            <ul>
                <li>guitar : Emphasizes guitar in the mix</li>
                <li>piano : Features piano prominently</li>
                <li>drums : Highlights drum patterns</li>
            </ul>
        </body>
        </html>
        """

    @pytest.fixture
    def sample_technique_html(self):
        """Sample HTML content for technique page testing"""
        return """
        <html>
        <head><title>Suno AI Techniques</title></head>
        <body>
            <h1>How to Structure Prompts for Suno AI</h1>
            
            <h2>Basic Prompt Structure</h2>
            <p>Start with genre and style information, followed by mood and instrumentation.</p>
            
            <h2>Advanced Techniques</h2>
            <ul>
                <li>Use specific genre combinations for unique sounds</li>
                <li>Include emotional descriptors for better mood control</li>
                <li>Specify instruments to guide the AI's choices</li>
            </ul>
            
            <h2>Examples</h2>
            <p>Example: "Indie folk with melancholic vocals and acoustic guitar"</p>
            <p>Example: "Electronic dance music with heavy bass and synthesizers"</p>
        </body>
        </html>
        """

    @pytest.fixture
    def malformed_html(self):
        """Malformed HTML for error testing"""
        return """
        <html>
        <head><title>Broken HTML</title>
        <body>
            <h1>Missing closing tags
            <p>Unclosed paragraph
            <ul>
                <li>Item 1
                <li>Item 2
        """

    def test_init_with_valid_parser(self):
        """Test initialization with valid parser"""
        parser = ContentParser(parser="html.parser")
        assert parser.parser == "html.parser"

    def test_init_with_invalid_parser(self):
        """Test initialization with invalid parser falls back to html.parser"""
        with patch('wiki_content_parser.BeautifulSoup') as mock_bs:
            mock_bs.side_effect = Exception("Parser not available")

            parser = ContentParser(parser="invalid_parser")
            assert parser.parser == "html.parser"

    def test_parse_html_valid_content(self, parser):
        """Test parsing valid HTML content"""
        html = "<html><body><h1>Test</h1></body></html>"

        soup = parser.parse_html(html, "https://example.com")

        assert isinstance(soup, BeautifulSoup)
        assert soup.find('h1').get_text() == "Test"

    def test_parse_html_empty_content(self, parser):
        """Test parsing empty HTML content raises error"""
        with pytest.raises(MalformedHTMLError):
            parser.parse_html("", "https://example.com")

        with pytest.raises(MalformedHTMLError):
            parser.parse_html(None, "https://example.com")

    def test_parse_html_invalid_content(self, parser):
        """Test parsing invalid HTML content"""
        # Very malformed HTML that BeautifulSoup can't handle
        with patch('wiki_content_parser.BeautifulSoup') as mock_bs:
            mock_bs.side_effect = Exception("Parse error")

            with pytest.raises(MalformedHTMLError):
                parser.parse_html("<invalid>", "https://example.com")

    def test_extract_text_content(self, parser):
        """Test text content extraction from elements"""
        html = "<p>  Test   content  with   spaces  </p>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find('p')

        result = parser.extract_text_content(element)
        assert result == "Test content with spaces"

    def test_extract_text_content_none_element(self, parser):
        """Test text extraction from None element"""
        result = parser.extract_text_content(None)
        assert result == ""

    def test_extract_text_content_navigable_string(self, parser):
        """Test text extraction from NavigableString"""
        from bs4 import NavigableString

        text = NavigableString("  Test string  ")
        result = parser.extract_text_content(text)
        assert result == "Test string"

    def test_extract_links(self, parser):
        """Test link extraction from elements"""
        html = """
        <div>
            <a href="https://example.com/page1">Link 1</a>
            <a href="/relative/path">Link 2</a>
            <a href="mailto:test@example.com">Email</a>
            <a>No href</a>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find('div')

        links = parser.extract_links(element, "https://example.com")

        assert "https://example.com/page1" in links
        assert "https://example.com/relative/path" in links
        assert "mailto:test@example.com" in links
        assert len(links) == 3  # Should not include link without href

    def test_find_content_sections(self, parser):
        """Test finding content sections by indicators"""
        html = """
        <html>
        <body>
            <h2>Genre List</h2>
            <div>Content 1</div>
            
            <h3>Meta Tags</h3>
            <section>Content 2</section>
            
            <h1>Other Section</h1>
            <article>Content 3</article>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        sections = parser.find_content_sections(soup, ["Genre", "Meta Tags"])

        assert len(sections) >= 2
        # Should find sections containing the indicators

    def test_extract_list_items(self, parser):
        """Test extracting items from various list types"""
        html = """
        <div>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            
            <ol>
                <li>Ordered 1</li>
                <li>Ordered 2</li>
            </ol>
            
            <dl>
                <dt>Term 1</dt>
                <dd>Definition 1</dd>
            </dl>
            
            <p>• Bullet point item</p>
            <p>1. Numbered item</p>
            <p>- Dash item</p>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find('div')

        items = parser.extract_list_items(element)

        assert "Item 1" in items
        assert "Item 2" in items
        assert "Ordered 1" in items
        assert "Term 1" in items
        assert "Definition 1" in items
        assert "Bullet point item" in items
        assert "Numbered item" in items
        assert "Dash item" in items

    def test_extract_table_data(self, parser):
        """Test extracting data from tables"""
        html = """
        <div>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Description</th>
                </tr>
                <tr>
                    <td>Techno</td>
                    <td>Electronic</td>
                    <td>Repetitive beats</td>
                </tr>
                <tr>
                    <td>Jazz</td>
                    <td>Traditional</td>
                    <td>Improvisation</td>
                </tr>
            </table>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find('div')

        table_data = parser.extract_table_data(element)

        assert len(table_data) == 2
        assert table_data[0]['Name'] == 'Techno'
        assert table_data[0]['Type'] == 'Electronic'
        assert table_data[1]['Name'] == 'Jazz'

    def test_clean_text(self, parser):
        """Test text cleaning functionality"""
        test_cases = [
            ("  Multiple   spaces  ", "Multiple spaces"),
            ("[[Wiki Link]]", "Wiki Link"),
            ("[Reference 1]", ""),
            ("Text with , bad spacing", "Text with, bad spacing"),
            ("Text with . punctuation", "Text with. punctuation"),
            ("Normal text", "Normal text")
        ]

        for input_text, expected in test_cases:
            result = parser.clean_text(input_text)
            assert result == expected, f"Failed for input: {input_text}"

    def test_parse_genre_page(self, parser, sample_genre_html):
        """Test parsing genre page content"""
        genres = parser.parse_genre_page(sample_genre_html, "https://example.com/genres")

        assert len(genres) > 0

        # Check that we got Genre objects
        for genre in genres:
            assert isinstance(genre, Genre)
            assert genre.name
            assert genre.source_url == "https://example.com/genres"
            assert isinstance(genre.download_date, datetime)

        # Check specific genres
        genre_names = [g.name for g in genres]
        assert "Techno" in genre_names
        assert "House" in genre_names
        assert "Alternative Rock" in genre_names

    def test_parse_genre_item(self, parser):
        """Test parsing individual genre items"""
        test_cases = [
            ("Techno", ("Techno", "")),
            ("House (e.g., Deep House, Tech House)", ("House", "A category that includes genres such as Deep House, Tech House.")),
            ("Dubstep (Heavy bass and syncopated drum patterns)", ("Dubstep", "Heavy bass and syncopated drum patterns")),
            ("Alternative Rock", ("Alternative Rock", ""))
        ]

        for input_item, expected in test_cases:
            result = parser._parse_genre_item(input_item)
            assert result == expected, f"Failed for input: {input_item}"

    def test_extract_genre_characteristics(self, parser):
        """Test genre characteristics extraction"""
        # Test electronic category
        characteristics = parser._extract_genre_characteristics("Electronic", "Techno")
        assert "synthesized sounds" in characteristics
        assert "digital production" in characteristics

        # Test rock category
        characteristics = parser._extract_genre_characteristics("Rock", "Hard Rock")
        assert "guitar-driven" in characteristics
        assert "amplified instruments" in characteristics

        # Test specific genre
        characteristics = parser._extract_genre_characteristics("Electronic", "Ambient")
        assert "atmospheric" in characteristics
        assert "minimal rhythm" in characteristics

    def test_infer_typical_instruments(self, parser):
        """Test typical instruments inference"""
        # Test electronic category
        instruments = parser._infer_typical_instruments("Electronic", "Techno")
        assert "synthesizer" in instruments
        assert "drum machine" in instruments

        # Test rock category
        instruments = parser._infer_typical_instruments("Rock", "Hard Rock")
        assert "electric guitar" in instruments
        assert "bass guitar" in instruments
        assert "drums" in instruments

        # Test jazz category
        instruments = parser._infer_typical_instruments("Jazz", "Bebop")
        assert "piano" in instruments
        assert "saxophone" in instruments

    def test_infer_mood_associations(self, parser):
        """Test mood associations inference"""
        # Test blues category
        moods = parser._infer_mood_associations("Blues", "Delta Blues")
        assert "melancholic" in moods
        assert "soulful" in moods

        # Test punk category
        moods = parser._infer_mood_associations("Punk", "Hardcore Punk")
        assert "rebellious" in moods
        assert "energetic" in moods

        # Test specific genre
        moods = parser._infer_mood_associations("Electronic", "Ambient")
        assert "atmospheric" in moods
        assert "meditative" in moods

    def test_parse_meta_tag_page(self, parser, sample_meta_tag_html):
        """Test parsing meta tag page content"""
        meta_tags = parser.parse_meta_tag_page(sample_meta_tag_html, "https://example.com/metatags")

        assert len(meta_tags) > 0

        # Check that we got MetaTag objects
        for tag in meta_tags:
            assert isinstance(tag, MetaTag)
            assert tag.tag
            assert tag.category
            assert tag.source_url == "https://example.com/metatags"
            assert isinstance(tag.download_date, datetime)

        # Check specific tags
        tag_names = [t.tag for t in meta_tags]
        assert "verse" in tag_names
        assert "happy" in tag_names
        assert "guitar" in tag_names

    def test_parse_meta_tag_item(self, parser):
        """Test parsing individual meta tag items"""
        test_cases = [
            ("<strong>verse</strong> : Defines verse sections", ("verse", "Defines verse sections", [])),
            ("**happy** : Creates upbeat mood", ("happy", "Creates upbeat mood", [])),
            ("guitar : Emphasizes guitar", ("guitar", "Emphasizes guitar", [])),
            ("tempo : Controls speed (example: fast, slow)", ("tempo", "Controls speed (example: fast, slow)", ["fast", "slow"]))
        ]

        for input_item, expected in test_cases:
            result = parser._parse_meta_tag_item(input_item)
            assert result[0] == expected[0], f"Tag name failed for: {input_item}"
            assert result[1] == expected[1], f"Description failed for: {input_item}"

    def test_categorize_meta_tag(self, parser):
        """Test meta tag categorization"""
        test_cases = [
            ("Structural Tags", "verse", "structural"),
            ("Emotional Tags", "happy", "emotional"),
            ("Instrumental Tags", "guitar", "instrumental"),
            ("Vocal Tags", "vocals", "vocal"),
            ("Unknown Category", "test", "general")
        ]

        for category, tag, expected in test_cases:
            result = parser._categorize_meta_tag(category, tag)
            assert result == expected, f"Failed for category: {category}, tag: {tag}"

    def test_infer_compatible_genres(self, parser):
        """Test compatible genres inference for meta tags"""
        # Test emotional tags
        genres = parser._infer_compatible_genres("emotional", "melancholic")
        assert "blues" in genres
        assert "folk" in genres

        # Test instrumental tags
        genres = parser._infer_compatible_genres("instrumental", "guitar")
        assert "rock" in genres
        assert "folk" in genres

        # Test structural tags (should be compatible with all)
        genres = parser._infer_compatible_genres("structural", "verse")
        assert len(genres) > 5  # Should have many compatible genres

    def test_parse_tip_page(self, parser, sample_technique_html):
        """Test parsing technique/tip page content"""
        techniques = parser.parse_tip_page(sample_technique_html, "https://example.com/tips")

        assert len(techniques) > 0

        # Check that we got Technique objects
        for technique in techniques:
            assert isinstance(technique, Technique)
            assert technique.name
            assert technique.source_url == "https://example.com/tips"
            assert isinstance(technique.download_date, datetime)

        # Should extract techniques from the content
        technique_names = [t.name for t in techniques]
        assert any("prompt" in name.lower() for name in technique_names)

    def test_extract_structured_content_genres(self, parser, sample_genre_html):
        """Test structured content extraction for genres"""
        parsed_content = parser.extract_structured_content(
            sample_genre_html, "genres", "https://example.com/genres"
        )

        assert isinstance(parsed_content, ParsedContent)
        assert parsed_content.content_type == "genres"
        assert parsed_content.source_url == "https://example.com/genres"
        assert len(parsed_content.genres) > 0
        assert len(parsed_content.meta_tags) == 0
        assert len(parsed_content.techniques) == 0
        assert not parsed_content.has_errors()

    def test_extract_structured_content_meta_tags(self, parser, sample_meta_tag_html):
        """Test structured content extraction for meta tags"""
        parsed_content = parser.extract_structured_content(
            sample_meta_tag_html, "meta_tags", "https://example.com/metatags"
        )

        assert isinstance(parsed_content, ParsedContent)
        assert parsed_content.content_type == "meta_tags"
        assert len(parsed_content.meta_tags) > 0
        assert len(parsed_content.genres) == 0
        assert len(parsed_content.techniques) == 0

    def test_extract_structured_content_techniques(self, parser, sample_technique_html):
        """Test structured content extraction for techniques"""
        parsed_content = parser.extract_structured_content(
            sample_technique_html, "techniques", "https://example.com/tips"
        )

        assert isinstance(parsed_content, ParsedContent)
        assert parsed_content.content_type == "techniques"
        assert len(parsed_content.techniques) > 0
        assert len(parsed_content.genres) == 0
        assert len(parsed_content.meta_tags) == 0

    def test_extract_structured_content_unknown_type(self, parser, sample_genre_html):
        """Test structured content extraction with unknown page type"""
        parsed_content = parser.extract_structured_content(
            sample_genre_html, "unknown_type", "https://example.com/unknown"
        )

        assert isinstance(parsed_content, ParsedContent)
        assert parsed_content.content_type == "unknown_type"
        assert parsed_content.has_errors()
        assert "Unknown page type" in parsed_content.errors[0]

    def test_extract_structured_content_malformed_html(self, parser, malformed_html):
        """Test structured content extraction with malformed HTML"""
        parsed_content = parser.extract_structured_content(
            malformed_html, "genres", "https://example.com/malformed"
        )

        assert isinstance(parsed_content, ParsedContent)
        assert parsed_content.has_errors()


class TestParsedContent:
    """Test suite for ParsedContent data model"""

    def test_parsed_content_creation(self):
        """Test ParsedContent creation and basic properties"""
        content = ParsedContent("genres", "https://example.com/genres")

        assert content.content_type == "genres"
        assert content.source_url == "https://example.com/genres"
        assert isinstance(content.parse_time, datetime)
        assert content.genres == []
        assert content.meta_tags == []
        assert content.techniques == []
        assert content.errors == []
        assert content.warnings == []

    def test_add_error(self):
        """Test adding errors to ParsedContent"""
        content = ParsedContent("test", "https://example.com")

        assert not content.has_errors()

        content.add_error("Test error")

        assert content.has_errors()
        assert "Test error" in content.errors

    def test_add_warning(self):
        """Test adding warnings to ParsedContent"""
        content = ParsedContent("test", "https://example.com")

        content.add_warning("Test warning")

        assert "Test warning" in content.warnings
        assert not content.has_errors()  # Warnings don't count as errors

    def test_get_total_items(self):
        """Test getting total number of parsed items"""
        content = ParsedContent("test", "https://example.com")

        # Initially empty
        assert content.get_total_items() == 0

        # Add some mock items
        content.genres = [Mock(), Mock()]
        content.meta_tags = [Mock()]
        content.techniques = [Mock(), Mock(), Mock()]

        assert content.get_total_items() == 6


class TestParsingExceptions:
    """Test suite for parsing exceptions"""

    def test_parse_error(self):
        """Test ParseError exception"""
        with pytest.raises(ParseError):
            raise ParseError("Test parse error")

    def test_malformed_html_error(self):
        """Test MalformedHTMLError exception"""
        with pytest.raises(MalformedHTMLError):
            raise MalformedHTMLError("Test malformed HTML error")

        # Should also be caught as ParseError
        with pytest.raises(ParseError):
            raise MalformedHTMLError("Test malformed HTML error")

    def test_content_extraction_error(self):
        """Test ContentExtractionError exception"""
        with pytest.raises(ContentExtractionError):
            raise ContentExtractionError("Test content extraction error")

        # Should also be caught as ParseError
        with pytest.raises(ParseError):
            raise ContentExtractionError("Test content extraction error")


if __name__ == "__main__":
    pytest.main([__file__])
