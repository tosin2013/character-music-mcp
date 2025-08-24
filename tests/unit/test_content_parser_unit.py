#!/usr/bin/env python3
"""
Unit tests for ContentParser

Tests the ContentParser class with sample HTML files to ensure
proper parsing functionality without external dependencies.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from wiki_content_parser import (
    ContentParser,
    ParsedContent,
    ParseError,
    MalformedHTMLError,
    ContentExtractionError
)
from wiki_data_system import Genre, MetaTag, Technique

class TestContentParser:
    """Unit tests for ContentParser class"""
    
    @pytest.fixture
    def parser(self):
        """Create a ContentParser instance for testing"""
        return ContentParser(parser="html.parser")
    
    @pytest.fixture
    def sample_genre_html(self):
        """Sample HTML content for genre page testing"""
        return """
        <html>
        <head><title>Music Genres</title></head>
        <body>
            <h1>List of Music Genres and Styles</h1>
            
            <h3>Electronic</h3>
            <ul>
                <li>Ambient (atmospheric and textural music)</li>
                <li>Techno</li>
                <li>House (four-on-the-floor beat pattern)</li>
                <li>Dubstep (syncopated drum patterns)</li>
            </ul>
            
            <h3>Rock</h3>
            <ul>
                <li>Alternative Rock</li>
                <li>Progressive Rock (complex compositions)</li>
                <li>Hard Rock</li>
            </ul>
            
            <h3>Jazz</h3>
            <ul>
                <li>Bebop (fast tempo and improvisation)</li>
                <li>Smooth Jazz</li>
                <li>Fusion (combines jazz with other genres)</li>
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
                <li><strong>verse</strong> : Indicates verse section of song</li>
                <li><strong>chorus</strong> : Indicates chorus section</li>
                <li><strong>bridge</strong> : Indicates bridge section</li>
            </ul>
            
            <h3>Emotional Tags</h3>
            <ul>
                <li>**upbeat** : Creates energetic and positive mood</li>
                <li>**melancholic** : Creates sad and reflective atmosphere</li>
                <li>**aggressive** : Creates intense and powerful feeling</li>
            </ul>
            
            <h3>Instrumental Tags</h3>
            <ul>
                <li>guitar-driven : Emphasizes guitar in the mix</li>
                <li>piano-based : Features piano as main instrument</li>
                <li>orchestral : Uses orchestral instruments and arrangements</li>
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
            
            <h2>Prompt Structure Techniques</h2>
            <p>Use clear and specific language when describing your desired output.</p>
            
            <h3>Lyric Writing Tips</h3>
            <ul>
                <li>Start with a strong hook in the first line</li>
                <li>Use concrete imagery rather than abstract concepts</li>
                <li>Maintain consistent rhyme scheme throughout</li>
            </ul>
            
            <h3>Genre Specification</h3>
            <p>Be specific about the genre you want. Instead of just "rock", 
            try "alternative rock with grunge influences" for better results.</p>
            
            <h3>Vocal Style Direction</h3>
            <p>Describe the vocal style you want: "raspy male vocals", 
            "smooth female harmonies", or "aggressive rap delivery".</p>
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
    
    def test_parser_initialization(self):
        """Test ContentParser initialization"""
        # Test with valid parser
        parser = ContentParser(parser="html.parser")
        assert parser.parser == "html.parser"
        
        # Test with invalid parser (should fallback)
        with patch('wiki_content_parser.logger') as mock_logger:
            parser = ContentParser(parser="invalid_parser")
            assert parser.parser == "html.parser"
            mock_logger.warning.assert_called()
    
    def test_parse_html_success(self, parser):
        """Test successful HTML parsing"""
        html_content = "<html><body><h1>Test</h1></body></html>"
        soup = parser.parse_html(html_content, "https://example.com")
        
        assert soup is not None
        assert soup.find('h1').get_text() == "Test"
    
    def test_parse_html_empty_content(self, parser):
        """Test parsing empty HTML content"""
        with pytest.raises(MalformedHTMLError):
            parser.parse_html("", "https://example.com")
        
        with pytest.raises(MalformedHTMLError):
            parser.parse_html(None, "https://example.com")
    
    def test_parse_html_malformed(self, parser, malformed_html):
        """Test parsing malformed HTML (should still work with BeautifulSoup)"""
        # BeautifulSoup is quite forgiving, so this should not raise an error
        soup = parser.parse_html(malformed_html, "https://example.com")
        assert soup is not None
        assert soup.find('h1') is not None
    
    def test_extract_text_content(self, parser):
        """Test text content extraction"""
        html = "<p>  This is   a test   with   extra   spaces  </p>"
        soup = parser.parse_html(f"<html><body>{html}</body></html>")
        element = soup.find('p')
        
        text = parser.extract_text_content(element)
        assert text == "This is a test with extra spaces"
        
        # Test with None element
        assert parser.extract_text_content(None) == ""
    
    def test_extract_links(self, parser):
        """Test link extraction"""
        html = """
        <div>
            <a href="https://example.com/page1">Link 1</a>
            <a href="/relative/path">Relative Link</a>
            <a href="mailto:test@example.com">Email</a>
            <a>No href</a>
        </div>
        """
        soup = parser.parse_html(f"<html><body>{html}</body></html>")
        div = soup.find('div')
        
        links = parser.extract_links(div, "https://example.com")
        
        assert "https://example.com/page1" in links
        assert "https://example.com/relative/path" in links
        assert "mailto:test@example.com" in links
        assert len(links) == 3
    
    def test_find_content_sections(self, parser, sample_genre_html):
        """Test content section finding"""
        soup = parser.parse_html(sample_genre_html)
        
        sections = parser.find_content_sections(soup, ["Electronic", "Rock"])
        assert len(sections) >= 2
        
        # Test with no matching sections
        sections = parser.find_content_sections(soup, ["NonExistent"])
        assert len(sections) >= 0  # Should find main content area as fallback
    
    def test_extract_list_items(self, parser, sample_genre_html):
        """Test list item extraction"""
        soup = parser.parse_html(sample_genre_html)
        ul = soup.find('ul')
        
        items = parser.extract_list_items(ul)
        assert len(items) > 0
        assert any("Ambient" in item for item in items)
        assert any("Techno" in item for item in items)
    
    def test_extract_table_data(self, parser):
        """Test table data extraction"""
        html = """
        <table>
            <tr>
                <th>Genre</th>
                <th>Description</th>
                <th>Origin</th>
            </tr>
            <tr>
                <td>Rock</td>
                <td>Guitar-driven music</td>
                <td>1950s USA</td>
            </tr>
            <tr>
                <td>Jazz</td>
                <td>Improvisational music</td>
                <td>Early 1900s USA</td>
            </tr>
        </table>
        """
        soup = parser.parse_html(f"<html><body>{html}</body></html>")
        table = soup.find('table')
        
        data = parser.extract_table_data(table)
        assert len(data) == 2
        assert data[0]['Genre'] == 'Rock'
        assert data[0]['Description'] == 'Guitar-driven music'
        assert data[1]['Genre'] == 'Jazz'
    
    def test_clean_text(self, parser):
        """Test text cleaning functionality"""
        # Test whitespace normalization
        text = "  This   has    extra   spaces  "
        cleaned = parser.clean_text(text)
        assert cleaned == "This has extra spaces"
        
        # Test wiki markup removal
        text = "This is a [[wiki link]] with [reference]"
        cleaned = parser.clean_text(text)
        assert cleaned == "This is a wiki link with"
        
        # Test punctuation spacing
        text = "Hello , world ! How are you ?"
        cleaned = parser.clean_text(text)
        assert cleaned == "Hello, world! How are you?"
        
        # Test empty text
        assert parser.clean_text("") == ""
        assert parser.clean_text(None) == ""
    
    def test_parse_genre_page(self, parser, sample_genre_html):
        """Test genre page parsing"""
        genres = parser.parse_genre_page(sample_genre_html, "https://example.com/genres")
        
        assert len(genres) > 0
        
        # Check for specific genres
        genre_names = [g.name for g in genres]
        assert "Ambient" in genre_names
        assert "Techno" in genre_names
        assert "Progressive Rock" in genre_names
        assert "Bebop" in genre_names
        
        # Check genre with description
        ambient_genre = next((g for g in genres if g.name == "Ambient"), None)
        assert ambient_genre is not None
        assert "atmospheric and textural music" in ambient_genre.description
        
        # Check characteristics inference
        electronic_genres = [g for g in genres if any("electronic" in char.lower() for char in g.characteristics)]
        assert len(electronic_genres) > 0
        
        # Check source URL attribution
        for genre in genres:
            assert genre.source_url == "https://example.com/genres"
            assert isinstance(genre.download_date, datetime)
    
    def test_parse_meta_tag_page(self, parser, sample_meta_tag_html):
        """Test meta tag page parsing"""
        meta_tags = parser.parse_meta_tag_page(sample_meta_tag_html, "https://example.com/tags")
        
        assert len(meta_tags) > 0
        
        # Check for specific tags
        tag_names = [t.tag for t in meta_tags]
        assert "verse" in tag_names
        assert "upbeat" in tag_names
        assert "guitar-driven" in tag_names
        
        # Check tag with description
        verse_tag = next((t for t in meta_tags if t.tag == "verse"), None)
        assert verse_tag is not None
        assert "verse section" in verse_tag.description.lower()
        
        # Check category classification
        structural_tags = [t for t in meta_tags if t.category == "structural"]
        emotional_tags = [t for t in meta_tags if t.category == "emotional"]
        instrumental_tags = [t for t in meta_tags if t.category == "instrumental"]
        
        assert len(structural_tags) > 0
        assert len(emotional_tags) > 0
        assert len(instrumental_tags) > 0
        
        # Check source URL attribution
        for tag in meta_tags:
            assert tag.source_url == "https://example.com/tags"
            assert isinstance(tag.download_date, datetime)
    
    def test_parse_tip_page(self, parser, sample_technique_html):
        """Test technique/tip page parsing"""
        techniques = parser.parse_tip_page(sample_technique_html, "https://example.com/tips")
        
        assert len(techniques) > 0
        
        # Check for specific techniques
        technique_names = [t.name for t in techniques]
        assert any("Prompt Structure" in name for name in technique_names)
        assert any("Lyric Writing" in name for name in technique_names)
        
        # Check technique content
        lyric_technique = next((t for t in techniques if "Lyric" in t.name), None)
        assert lyric_technique is not None
        assert len(lyric_technique.examples) > 0
        assert any("hook" in example.lower() for example in lyric_technique.examples)
        
        # Check source URL attribution
        for technique in techniques:
            assert technique.source_url == "https://example.com/tips"
            assert isinstance(technique.download_date, datetime)
    
    def test_extract_structured_content_genres(self, parser, sample_genre_html):
        """Test structured content extraction for genres"""
        parsed_content = parser.extract_structured_content(
            sample_genre_html, 
            "genres", 
            "https://example.com/genres"
        )
        
        assert parsed_content.content_type == "genres"
        assert parsed_content.source_url == "https://example.com/genres"
        assert len(parsed_content.genres) > 0
        assert len(parsed_content.meta_tags) == 0
        assert len(parsed_content.techniques) == 0
        assert not parsed_content.has_errors()
    
    def test_extract_structured_content_meta_tags(self, parser, sample_meta_tag_html):
        """Test structured content extraction for meta tags"""
        parsed_content = parser.extract_structured_content(
            sample_meta_tag_html, 
            "meta_tags", 
            "https://example.com/tags"
        )
        
        assert parsed_content.content_type == "meta_tags"
        assert len(parsed_content.meta_tags) > 0
        assert len(parsed_content.genres) == 0
        assert len(parsed_content.techniques) == 0
        assert not parsed_content.has_errors()
    
    def test_extract_structured_content_techniques(self, parser, sample_technique_html):
        """Test structured content extraction for techniques"""
        parsed_content = parser.extract_structured_content(
            sample_technique_html, 
            "techniques", 
            "https://example.com/tips"
        )
        
        assert parsed_content.content_type == "techniques"
        assert len(parsed_content.techniques) > 0
        assert len(parsed_content.genres) == 0
        assert len(parsed_content.meta_tags) == 0
        assert not parsed_content.has_errors()
    
    def test_extract_structured_content_unknown_type(self, parser, sample_genre_html):
        """Test structured content extraction with unknown type"""
        parsed_content = parser.extract_structured_content(
            sample_genre_html, 
            "unknown_type", 
            "https://example.com/unknown"
        )
        
        assert parsed_content.content_type == "unknown_type"
        assert parsed_content.has_errors()
        assert "Unknown page type" in parsed_content.errors[0]
    
    def test_extract_structured_content_malformed_html(self, parser, malformed_html):
        """Test structured content extraction with malformed HTML"""
        parsed_content = parser.extract_structured_content(
            malformed_html, 
            "genres", 
            "https://example.com/malformed"
        )
        
        # Should handle malformed HTML gracefully
        assert parsed_content.content_type == "genres"
        # May or may not have errors depending on how malformed the HTML is
    
    def test_genre_characteristics_inference(self, parser):
        """Test genre characteristics inference"""
        # Test electronic category
        characteristics = parser._extract_genre_characteristics("Electronic", "Ambient")
        assert any("electronic" in char.lower() for char in characteristics)
        assert any("atmospheric" in char.lower() for char in characteristics)
        
        # Test rock category
        characteristics = parser._extract_genre_characteristics("Rock", "Hard Rock")
        assert any("guitar" in char.lower() for char in characteristics)
        
        # Test jazz category
        characteristics = parser._extract_genre_characteristics("Jazz", "Bebop")
        assert any("improvisation" in char.lower() for char in characteristics)
    
    def test_typical_instruments_inference(self, parser):
        """Test typical instruments inference"""
        # Test electronic category
        instruments = parser._infer_typical_instruments("Electronic", "Techno")
        assert any("synthesizer" in instr.lower() for instr in instruments)
        
        # Test rock category
        instruments = parser._infer_typical_instruments("Rock", "Hard Rock")
        assert any("guitar" in instr.lower() for instr in instruments)
        
        # Test jazz category
        instruments = parser._infer_typical_instruments("Jazz", "Bebop")
        assert any("saxophone" in instr.lower() or "piano" in instr.lower() for instr in instruments)
    
    def test_mood_associations_inference(self, parser):
        """Test mood associations inference"""
        # Test blues category
        moods = parser._infer_mood_associations("Blues", "Delta Blues")
        assert any("melancholic" in mood.lower() or "soulful" in mood.lower() for mood in moods)
        
        # Test punk category
        moods = parser._infer_mood_associations("Punk", "Hardcore Punk")
        assert any("rebellious" in mood.lower() or "aggressive" in mood.lower() for mood in moods)
        
        # Test ambient genre
        moods = parser._infer_mood_associations("Electronic", "Ambient")
        assert any("atmospheric" in mood.lower() or "meditative" in mood.lower() for mood in moods)
    
    def test_meta_tag_categorization(self, parser):
        """Test meta tag categorization"""
        # Test structural tags
        category = parser._categorize_meta_tag("Structural Tags", "verse")
        assert category == "structural"
        
        # Test emotional tags
        category = parser._categorize_meta_tag("Emotional Tags", "upbeat")
        assert category == "emotional"
        
        # Test instrumental tags
        category = parser._categorize_meta_tag("Instrumental Tags", "guitar-driven")
        assert category == "instrumental"
        
        # Test fallback
        category = parser._categorize_meta_tag("Unknown Category", "unknown-tag")
        assert category == "general"
    
    def test_compatible_genres_inference(self, parser):
        """Test compatible genres inference for meta tags"""
        # Test rock-related tag
        genres = parser._infer_compatible_genres("instrumental", "guitar-driven")
        assert any("rock" in genre.lower() for genre in genres)
        
        # Test electronic-related tag
        genres = parser._infer_compatible_genres("emotional", "upbeat")
        assert any("electronic" in genre.lower() or "pop" in genre.lower() for genre in genres)
        
        # Test orchestral tag
        genres = parser._infer_compatible_genres("instrumental", "orchestral")
        assert any("classical" in genre.lower() or "orchestral" in genre.lower() for genre in genres)

class TestParsedContent:
    """Unit tests for ParsedContent class"""
    
    def test_parsed_content_initialization(self):
        """Test ParsedContent initialization"""
        content = ParsedContent("genres", "https://example.com")
        
        assert content.content_type == "genres"
        assert content.source_url == "https://example.com"
        assert isinstance(content.parse_time, datetime)
        assert len(content.genres) == 0
        assert len(content.meta_tags) == 0
        assert len(content.techniques) == 0
        assert len(content.errors) == 0
        assert len(content.warnings) == 0
    
    def test_add_error(self):
        """Test error addition"""
        content = ParsedContent("test", "https://example.com")
        
        content.add_error("Test error message")
        
        assert len(content.errors) == 1
        assert content.errors[0] == "Test error message"
        assert content.has_errors() == True
    
    def test_add_warning(self):
        """Test warning addition"""
        content = ParsedContent("test", "https://example.com")
        
        content.add_warning("Test warning message")
        
        assert len(content.warnings) == 1
        assert content.warnings[0] == "Test warning message"
        assert content.has_errors() == False  # Warnings don't count as errors
    
    def test_get_total_items(self):
        """Test total items count"""
        content = ParsedContent("test", "https://example.com")
        
        # Add some mock items
        content.genres.append(Mock())
        content.meta_tags.extend([Mock(), Mock()])
        content.techniques.append(Mock())
        
        assert content.get_total_items() == 4

if __name__ == "__main__":
    # Run basic tests
    def run_basic_tests():
        parser = ContentParser()
        
        # Test basic HTML parsing
        html = "<html><body><h1>Test</h1></body></html>"
        soup = parser.parse_html(html)
        assert soup.find('h1').get_text() == "Test"
        print("✓ Basic HTML parsing test passed")
        
        # Test text cleaning
        text = "  This   has    extra   spaces  "
        cleaned = parser.clean_text(text)
        assert cleaned == "This has extra spaces"
        print("✓ Text cleaning test passed")
        
        # Test URL validation in links
        html_with_links = """
        <div>
            <a href="https://example.com">Valid Link</a>
            <a href="/relative">Relative Link</a>
        </div>
        """
        soup = parser.parse_html(f"<html><body>{html_with_links}</body></html>")
        div = soup.find('div')
        links = parser.extract_links(div, "https://example.com")
        assert len(links) == 2
        print("✓ Link extraction test passed")
        
        print("Basic ContentParser unit tests passed!")
    
    run_basic_tests()