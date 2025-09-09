#!/usr/bin/env python3
"""
Wiki Content Parser for Dynamic Suno Data Integration

This module provides HTML content parsing utilities for extracting structured data
from Suno AI Wiki pages including genres, meta tags, and techniques.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin

try:
    from bs4 import BeautifulSoup, NavigableString, Tag
    from bs4.element import ResultSet
except ImportError:
    raise ImportError(
        "BeautifulSoup4 is required for HTML parsing. "
        "Install it with: pip install beautifulsoup4 lxml"
    )

from performance_monitor import PerformanceMonitor
from wiki_data_models import Genre, MetaTag, Technique

# Configure logging
logger = logging.getLogger(__name__)

# ================================================================================================
# PARSING EXCEPTIONS
# ================================================================================================

class ParseError(Exception):
    """Base exception for parsing errors"""
    pass

class MalformedHTMLError(ParseError):
    """Exception for malformed HTML content"""
    pass

class ContentExtractionError(ParseError):
    """Exception for content extraction failures"""
    pass

# ================================================================================================
# PARSED CONTENT DATA MODEL
# ================================================================================================

class ParsedContent:
    """Container for parsed content with metadata"""

    def __init__(self, content_type: str, source_url: str = ""):
        self.content_type = content_type
        self.source_url = source_url
        self.parse_time = datetime.now()
        self.genres: List[Genre] = []
        self.meta_tags: List[MetaTag] = []
        self.techniques: List[Technique] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_error(self, error: str) -> None:
        """Add parsing error"""
        self.errors.append(error)
        logger.error(f"Parse error for {self.source_url}: {error}")

    def add_warning(self, warning: str) -> None:
        """Add parsing warning"""
        self.warnings.append(warning)
        logger.warning(f"Parse warning for {self.source_url}: {warning}")

    def has_errors(self) -> bool:
        """Check if parsing had errors"""
        return len(self.errors) > 0

    def get_total_items(self) -> int:
        """Get total number of parsed items"""
        return len(self.genres) + len(self.meta_tags) + len(self.techniques)

# ================================================================================================
# BASE CONTENT PARSER
# ================================================================================================

class ContentParser:
    """Base HTML content parser with structured content extraction methods"""

    def __init__(self, parser: str = "lxml", performance_monitor: Optional[PerformanceMonitor] = None):
        """
        Initialize ContentParser
        
        Args:
            parser: BeautifulSoup parser to use ('lxml', 'html.parser', etc.)
            performance_monitor: PerformanceMonitor instance for tracking metrics
        """
        self.parser = parser
        self.performance_monitor = performance_monitor
        self._validate_parser()

    def _validate_parser(self) -> None:
        """Validate that the specified parser is available"""
        try:
            BeautifulSoup("<html></html>", self.parser)
        except Exception as e:
            logger.warning(f"Parser '{self.parser}' not available, falling back to 'html.parser': {e}")
            self.parser = "html.parser"

    def parse_html(self, html_content: str, source_url: str = "") -> BeautifulSoup:
        """
        Parse HTML content with error handling
        
        Args:
            html_content: Raw HTML content to parse
            source_url: Source URL for error reporting
            
        Returns:
            BeautifulSoup object
            
        Raises:
            MalformedHTMLError: If HTML cannot be parsed
        """
        if not html_content or not isinstance(html_content, str):
            raise MalformedHTMLError("HTML content is empty or not a string")

        try:
            soup = BeautifulSoup(html_content, self.parser)

            # Basic validation - check if we got a valid document
            if not soup or not soup.find():
                raise MalformedHTMLError("Parsed HTML appears to be empty or invalid")

            logger.debug(f"Successfully parsed HTML from {source_url or 'unknown source'}")
            return soup

        except Exception as e:
            error_msg = f"Failed to parse HTML: {str(e)}"
            logger.error(f"HTML parsing error for {source_url}: {error_msg}")
            raise MalformedHTMLError(error_msg) from e

    def extract_text_content(self, element: Union[Tag, NavigableString, None]) -> str:
        """
        Safely extract text content from an element
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Cleaned text content
        """
        if not element:
            return ""

        try:
            if isinstance(element, NavigableString):
                return str(element).strip()
            elif isinstance(element, Tag):
                # Get text and clean it up
                text = element.get_text(separator=' ', strip=True)
                # Remove extra whitespace
                text = re.sub(r'\s+', ' ', text)
                return text.strip()
            else:
                return str(element).strip()
        except Exception as e:
            logger.warning(f"Error extracting text content: {e}")
            return ""

    def extract_links(self, element: Tag, base_url: str = "") -> List[str]:
        """
        Extract all links from an element
        
        Args:
            element: BeautifulSoup element to search
            base_url: Base URL for resolving relative links
            
        Returns:
            List of absolute URLs
        """
        links = []

        try:
            for link in element.find_all('a', href=True):
                href = link['href']
                if href:
                    # Convert relative URLs to absolute
                    if base_url and not href.startswith(('http://', 'https://')):
                        href = urljoin(base_url, href)
                    links.append(href)
        except Exception as e:
            logger.warning(f"Error extracting links: {e}")

        return links

    def find_content_sections(self, soup: BeautifulSoup,
                            section_indicators: List[str]) -> List[Tag]:
        """
        Find content sections based on various indicators
        
        Args:
            soup: BeautifulSoup object
            section_indicators: List of text patterns to look for in headings
            
        Returns:
            List of section elements
        """
        sections = []

        try:
            # Look for headings that match our indicators
            for indicator in section_indicators:
                # Try different heading levels
                for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    headings = soup.find_all(heading_tag, string=re.compile(indicator, re.IGNORECASE))
                    for heading in headings:
                        # Find the parent section or the heading itself
                        section = heading.find_parent(['section', 'div', 'article']) or heading
                        if section and section not in sections:
                            sections.append(section)

            # If no specific sections found, look for main content areas
            if not sections:
                main_content = soup.find(['main', 'article', 'div'], class_=re.compile(r'content|main|body', re.IGNORECASE))
                if main_content:
                    sections.append(main_content)

        except Exception as e:
            logger.warning(f"Error finding content sections: {e}")

        return sections

    def extract_list_items(self, element: Tag) -> List[str]:
        """
        Extract items from lists (ul, ol, dl)
        
        Args:
            element: Element to search for lists
            
        Returns:
            List of text items
        """
        items = []

        try:
            # Find all list items
            list_items = element.find_all(['li', 'dt', 'dd'])
            for item in list_items:
                text = self.extract_text_content(item)
                if text and text not in items:  # Avoid duplicates
                    items.append(text)

            # Also look for items in paragraphs that might be formatted as lists
            paragraphs = element.find_all('p')
            for p in paragraphs:
                text = self.extract_text_content(p)
                # Check if paragraph looks like a list item (starts with bullet, number, etc.)
                if text and (text.startswith(('•', '-', '*', '→')) or re.match(r'^\d+\.', text)):
                    # Clean up list markers
                    cleaned_text = re.sub(r'^[•\-*→\d\.]+\s*', '', text).strip()
                    if cleaned_text and cleaned_text not in items:
                        items.append(cleaned_text)

        except Exception as e:
            logger.warning(f"Error extracting list items: {e}")

        return items

    def extract_table_data(self, element: Tag) -> List[Dict[str, str]]:
        """
        Extract data from tables
        
        Args:
            element: Element to search for tables
            
        Returns:
            List of dictionaries representing table rows
        """
        table_data = []

        try:
            tables = element.find_all('table')
            for table in tables:
                # Get headers
                headers = []
                header_row = table.find('tr')
                if header_row:
                    for th in header_row.find_all(['th', 'td']):
                        headers.append(self.extract_text_content(th))

                # Get data rows
                rows = table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_data = {}
                        for i, cell in enumerate(cells):
                            header = headers[i] if i < len(headers) else f"column_{i}"
                            row_data[header] = self.extract_text_content(cell)
                        table_data.append(row_data)

        except Exception as e:
            logger.warning(f"Error extracting table data: {e}")

        return table_data

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove common wiki markup that might remain
        text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)  # [[link]] -> link
        text = re.sub(r'\[([^\]]+)\]', '', text)  # Remove [references]

        # Clean up punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # Fix spacing before punctuation

        return text.strip()

    def extract_structured_content(self, html_content: str, page_type: str,
                                 source_url: str = "") -> ParsedContent:
        """
        Extract structured content from HTML based on page type
        
        Args:
            html_content: Raw HTML content
            page_type: Type of page ('genres', 'meta_tags', 'techniques')
            source_url: Source URL for attribution
            
        Returns:
            ParsedContent object with extracted data
        """
        parsed_content = ParsedContent(page_type, source_url)

        try:
            soup = self.parse_html(html_content, source_url)

            # Route to specific parsing method based on page type
            if page_type.lower() == 'genres':
                parsed_content.genres = self.parse_genre_page(html_content, source_url)
            elif page_type.lower() == 'meta_tags':
                parsed_content.meta_tags = self.parse_meta_tag_page(html_content, source_url)
            elif page_type.lower() == 'techniques':
                parsed_content.techniques = self.parse_tip_page(html_content, source_url)
            else:
                parsed_content.add_error(f"Unknown page type: {page_type}")

        except Exception as e:
            error_msg = f"Failed to extract structured content: {str(e)}"
            parsed_content.add_error(error_msg)

        return parsed_content

    # Abstract methods to be implemented by subclasses or in this class
    def parse_genre_page(self, html_content: str, source_url: str = "") -> List[Genre]:
        """
        Parse genre page content from Suno AI Wiki
        
        Args:
            html_content: Raw HTML content
            source_url: Source URL for attribution
            
        Returns:
            List of Genre objects
        """
        start_time = datetime.now()
        genres = []

        try:
            soup = self.parse_html(html_content, source_url)

            # Find all H3 headings which represent genre categories
            category_headings = soup.find_all('h3')

            for heading in category_headings:
                category_name = self.extract_text_content(heading)
                if not category_name:
                    continue

                logger.debug(f"Processing genre category: {category_name}")

                # Find the next sibling element which should contain the genre list
                next_element = heading.find_next_sibling()

                if next_element and next_element.name == 'ul':
                    # Extract genre items from the list
                    genre_items = self.extract_list_items(next_element)

                    for genre_item in genre_items:
                        if not genre_item.strip():
                            continue

                        # Parse genre name and potential description
                        genre_name, description = self._parse_genre_item(genre_item)

                        if genre_name:
                            # Create Genre object
                            genre = Genre(
                                name=genre_name,
                                description=description or f"{genre_name} is a music genre in the {category_name} category.",
                                subgenres=[],  # Will be populated if we find hierarchical info
                                characteristics=self._extract_genre_characteristics(category_name, genre_name),
                                typical_instruments=self._infer_typical_instruments(category_name, genre_name),
                                mood_associations=self._infer_mood_associations(category_name, genre_name),
                                source_url=source_url,
                                download_date=datetime.now(),
                                confidence_score=1.0
                            )

                            genres.append(genre)
                            logger.debug(f"Parsed genre: {genre_name} in category {category_name}")

            logger.info(f"Successfully parsed {len(genres)} genres from {source_url}")

            # Record performance metrics
            if self.performance_monitor:
                duration = (datetime.now() - start_time).total_seconds()
                content_size = len(html_content.encode('utf-8'))
                asyncio.create_task(self.performance_monitor.record_parsing_metrics(
                    content_type="genre_page",
                    content_size=content_size,
                    duration=duration,
                    success=True,
                    items_parsed=len(genres)
                ))

        except Exception as e:
            error_msg = f"Error parsing genre page: {str(e)}"
            logger.error(error_msg)

            # Record performance metrics for failed parsing
            if self.performance_monitor:
                duration = (datetime.now() - start_time).total_seconds()
                content_size = len(html_content.encode('utf-8'))
                asyncio.create_task(self.performance_monitor.record_parsing_metrics(
                    content_type="genre_page",
                    content_size=content_size,
                    duration=duration,
                    success=False,
                    items_parsed=0
                ))

            raise ContentExtractionError(error_msg) from e

        return genres

    def _parse_genre_item(self, genre_item: str) -> tuple[str, str]:
        """
        Parse individual genre item to extract name and description
        
        Args:
            genre_item: Raw genre item text
            
        Returns:
            Tuple of (genre_name, description)
        """
        # Clean the text
        cleaned_item = self.clean_text(genre_item)

        # Check if there's a description in parentheses
        if '(' in cleaned_item and ')' in cleaned_item:
            # Extract description from parentheses
            parts = cleaned_item.split('(', 1)
            genre_name = parts[0].strip()
            description_part = parts[1].split(')', 1)[0].strip()

            # Handle cases like "Brazilian music (e.g., Samba, Bossa nova)"
            if description_part.startswith('e.g.,'):
                subgenres_text = description_part[5:].strip()  # Remove "e.g., "
                description = f"A category that includes genres such as {subgenres_text}."
            else:
                description = description_part

            return genre_name, description
        else:
            # No description in parentheses, just return the name
            return cleaned_item, ""

    def _extract_genre_characteristics(self, category: str, genre_name: str) -> List[str]:
        """
        Extract or infer characteristics based on category and genre name
        
        Args:
            category: Genre category (e.g., "Electronic", "Rock")
            genre_name: Specific genre name
            
        Returns:
            List of characteristics
        """
        characteristics = []

        # Category-based characteristics
        category_lower = category.lower()
        if 'electronic' in category_lower:
            characteristics.extend(['synthesized sounds', 'digital production', 'electronic instruments'])
        elif 'rock' in category_lower:
            characteristics.extend(['guitar-driven', 'strong rhythm section', 'amplified instruments'])
        elif 'jazz' in category_lower:
            characteristics.extend(['improvisation', 'complex harmonies', 'swing rhythm'])
        elif 'folk' in category_lower:
            characteristics.extend(['acoustic instruments', 'traditional melodies', 'storytelling lyrics'])
        elif 'hip hop' in category_lower or 'hip-hop' in category_lower:
            characteristics.extend(['rhythmic speech', 'strong beats', 'sampling'])
        elif 'blues' in category_lower:
            characteristics.extend(['twelve-bar structure', 'blue notes', 'call and response'])
        elif 'country' in category_lower:
            characteristics.extend(['acoustic guitar', 'storytelling', 'rural themes'])
        elif 'pop' in category_lower:
            characteristics.extend(['catchy melodies', 'mainstream appeal', 'verse-chorus structure'])
        elif 'metal' in category_lower:
            characteristics.extend(['heavy guitar riffs', 'powerful vocals', 'aggressive sound'])
        elif 'punk' in category_lower:
            characteristics.extend(['fast tempo', 'short songs', 'rebellious attitude'])

        # Genre-specific characteristics
        genre_lower = genre_name.lower()
        if 'ambient' in genre_lower:
            characteristics.extend(['atmospheric', 'minimal rhythm', 'textural'])
        elif 'trap' in genre_lower:
            characteristics.extend(['hi-hats', '808 drums', 'southern hip hop'])
        elif 'techno' in genre_lower:
            characteristics.extend(['repetitive beats', 'electronic dance music', 'four-on-the-floor'])
        elif 'reggae' in genre_lower:
            characteristics.extend(['offbeat rhythm', 'Jamaican origin', 'social consciousness'])

        return list(set(characteristics))  # Remove duplicates

    def _infer_typical_instruments(self, category: str, genre_name: str) -> List[str]:
        """
        Infer typical instruments based on category and genre
        
        Args:
            category: Genre category
            genre_name: Specific genre name
            
        Returns:
            List of typical instruments
        """
        instruments = []

        category_lower = category.lower()
        genre_lower = genre_name.lower()

        # Category-based instruments
        if 'electronic' in category_lower:
            instruments.extend(['synthesizer', 'drum machine', 'computer', 'sampler'])
        elif 'rock' in category_lower or 'metal' in category_lower:
            instruments.extend(['electric guitar', 'bass guitar', 'drums', 'vocals'])
        elif 'jazz' in category_lower:
            instruments.extend(['piano', 'saxophone', 'trumpet', 'double bass', 'drums'])
        elif 'folk' in category_lower:
            instruments.extend(['acoustic guitar', 'vocals', 'harmonica', 'banjo'])
        elif 'hip hop' in category_lower:
            instruments.extend(['turntables', 'microphone', 'drum machine', 'sampler'])
        elif 'blues' in category_lower:
            instruments.extend(['guitar', 'harmonica', 'piano', 'vocals'])
        elif 'country' in category_lower:
            instruments.extend(['acoustic guitar', 'fiddle', 'banjo', 'steel guitar', 'vocals'])
        elif 'pop' in category_lower:
            instruments.extend(['vocals', 'guitar', 'piano', 'drums', 'bass'])

        # Genre-specific instruments
        if 'orchestral' in genre_lower or 'classical' in genre_lower:
            instruments.extend(['violin', 'cello', 'flute', 'oboe', 'timpani'])
        elif 'reggae' in genre_lower:
            instruments.extend(['bass guitar', 'drums', 'guitar', 'keyboard'])
        elif 'samba' in genre_lower:
            instruments.extend(['percussion', 'cavaquinho', 'pandeiro', 'surdo'])

        return list(set(instruments))  # Remove duplicates

    def _infer_mood_associations(self, category: str, genre_name: str) -> List[str]:
        """
        Infer mood associations based on category and genre
        
        Args:
            category: Genre category
            genre_name: Specific genre name
            
        Returns:
            List of mood associations
        """
        moods = []

        category_lower = category.lower()
        genre_lower = genre_name.lower()

        # Category-based moods
        if 'blues' in category_lower:
            moods.extend(['melancholic', 'soulful', 'emotional'])
        elif 'jazz' in category_lower:
            moods.extend(['sophisticated', 'smooth', 'improvisational'])
        elif 'punk' in category_lower:
            moods.extend(['rebellious', 'energetic', 'aggressive'])
        elif 'folk' in category_lower:
            moods.extend(['nostalgic', 'storytelling', 'authentic'])
        elif 'pop' in category_lower:
            moods.extend(['upbeat', 'catchy', 'accessible'])
        elif 'metal' in category_lower:
            moods.extend(['intense', 'powerful', 'aggressive'])
        elif 'easy listening' in category_lower:
            moods.extend(['relaxing', 'smooth', 'comfortable'])
        elif 'electronic' in category_lower:
            moods.extend(['futuristic', 'danceable', 'synthetic'])

        # Genre-specific moods
        if 'ambient' in genre_lower:
            moods.extend(['atmospheric', 'meditative', 'spacious'])
        elif 'trap' in genre_lower:
            moods.extend(['dark', 'heavy', 'urban'])
        elif 'bossa nova' in genre_lower:
            moods.extend(['smooth', 'romantic', 'sophisticated'])
        elif 'reggae' in genre_lower:
            moods.extend(['laid-back', 'spiritual', 'positive'])
        elif 'gospel' in genre_lower:
            moods.extend(['uplifting', 'spiritual', 'joyful'])

        return list(set(moods))  # Remove duplicates

    def parse_meta_tag_page(self, html_content: str, source_url: str = "") -> List[MetaTag]:
        """
        Parse meta tag page content from Suno AI Wiki
        
        Args:
            html_content: Raw HTML content
            source_url: Source URL for attribution
            
        Returns:
            List of MetaTag objects
        """
        meta_tags = []

        try:
            soup = self.parse_html(html_content, source_url)

            # Find all H3 headings which represent meta tag categories
            category_headings = soup.find_all('h3')

            for heading in category_headings:
                category_name = self.extract_text_content(heading)
                if not category_name:
                    continue

                # Skip non-meta-tag sections
                if any(skip_word in category_name.lower() for skip_word in ['how to use', 'what are']):
                    continue

                logger.debug(f"Processing meta tag category: {category_name}")

                # Find the next sibling element which should contain the meta tag list
                next_element = heading.find_next_sibling()

                if next_element and next_element.name == 'ul':
                    # Extract meta tag items from the list
                    tag_items = next_element.find_all('li')

                    for li_item in tag_items:
                        # Get the raw HTML content of the list item to preserve formatting
                        tag_html = str(li_item)
                        tag_text = self.extract_text_content(li_item)

                        if not tag_text.strip():
                            continue

                        # Parse meta tag name and description from HTML
                        tag_name, description, examples = self._parse_meta_tag_item(tag_html)

                        if tag_name:
                            # Determine category type
                            category_type = self._categorize_meta_tag(category_name, tag_name)

                            # Create MetaTag object
                            meta_tag = MetaTag(
                                tag=tag_name,
                                category=category_type,
                                description=description or f"{tag_name} meta tag for {category_name.lower()}.",
                                usage_examples=examples,
                                compatible_genres=self._infer_compatible_genres(category_type, tag_name),
                                source_url=source_url,
                                download_date=datetime.now()
                            )

                            meta_tags.append(meta_tag)
                            logger.debug(f"Parsed meta tag: {tag_name} in category {category_name}")

            logger.info(f"Successfully parsed {len(meta_tags)} meta tags from {source_url}")

        except Exception as e:
            error_msg = f"Error parsing meta tag page: {str(e)}"
            logger.error(error_msg)
            raise ContentExtractionError(error_msg) from e

        return meta_tags

    def _parse_meta_tag_item(self, tag_item: str) -> tuple[str, str, List[str]]:
        """
        Parse individual meta tag item to extract name, description, and examples
        
        Args:
            tag_item: Raw meta tag item text or HTML
            
        Returns:
            Tuple of (tag_name, description, examples)
        """
        # If it's HTML, extract text content first
        if tag_item.strip().startswith('<'):
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(tag_item, self.parser)
                cleaned_item = soup.get_text()
            except:
                cleaned_item = tag_item
        else:
            cleaned_item = tag_item

        # Clean the text
        cleaned_item = self.clean_text(cleaned_item)

        # Look for pattern: **Tag Name** : Description or Tag Name : Description
        # Handle both markdown bold and HTML strong tags
        colon_patterns = [
            r'\*\*(.*?)\*\*\s*:\s*(.*)',  # **Tag** : Description
            r'<strong>(.*?)</strong>\s*:\s*(.*)',  # <strong>Tag</strong> : Description
            r'([^:]+?)\s*:\s*(.*)'  # Tag : Description (fallback)
        ]

        tag_name = None
        description = ""

        for pattern in colon_patterns:
            match = re.search(pattern, cleaned_item, re.IGNORECASE)
            if match:
                tag_name = match.group(1).strip()
                description = match.group(2).strip()
                break

        if tag_name:
            # Extract examples if present
            examples = []
            if 'example' in description.lower():
                # Try to extract examples from description
                example_patterns = [
                    r'example[s]?[:\-]?\s*([^.]+)',
                    r'such as\s+([^.]+)',
                    r'like\s+([^.]+)'
                ]
                for pattern in example_patterns:
                    match = re.search(pattern, description, re.IGNORECASE)
                    if match:
                        example_text = match.group(1).strip()
                        # Split on common separators
                        example_items = re.split(r'[,;]', example_text)
                        examples.extend([ex.strip() for ex in example_items if ex.strip()])
                        break

            return tag_name, description, examples
        else:
            # No colon separator, treat entire text as tag name after removing formatting
            tag_name = re.sub(r'(\*\*(.*?)\*\*|<strong>(.*?)</strong>)', r'\2\3', cleaned_item)
            return tag_name.strip(), "", []

    def _categorize_meta_tag(self, category_name: str, tag_name: str) -> str:
        """
        Categorize meta tag based on category name and tag name
        
        Args:
            category_name: Category heading text
            tag_name: Meta tag name
            
        Returns:
            Category type string
        """
        category_lower = category_name.lower()
        tag_lower = tag_name.lower()

        # Category-based classification
        if 'sound effects' in category_lower or 'environment' in category_lower:
            return 'sound_effects'
        elif 'vocal' in category_lower or 'expressions' in category_lower:
            return 'vocal'
        elif 'static' in category_lower or 'effects' in category_lower:
            return 'effects'
        elif 'structural' in category_lower or 'structure' in category_lower:
            return 'structural'
        elif 'styles' in category_lower or 'genres' in category_lower:
            return 'genre'

        # Tag-based classification
        if any(word in tag_lower for word in ['intro', 'outro', 'verse', 'chorus', 'bridge']):
            return 'structural'
        elif any(word in tag_lower for word in ['pop', 'rock', 'jazz', 'hip hop', 'electronic', 'metal', 'blues']):
            return 'genre'
        elif any(word in tag_lower for word in ['man', 'woman', 'boy', 'girl', 'narrator', 'announcer']):
            return 'vocal'
        elif any(word in tag_lower for word in ['barking', 'beeping', 'ringing', 'clapping', 'cheering']):
            return 'sound_effects'
        elif any(word in tag_lower for word in ['silence', 'censored', 'applause']):
            return 'effects'
        elif any(word in tag_lower for word in ['acoustic', 'ambient', 'chill', 'lo-fi']):
            return 'style'
        elif any(word in tag_lower for word in ['piano', 'guitar', 'drums', 'cello', 'orchestra']):
            return 'instrumental'
        else:
            return 'general'

    def _infer_compatible_genres(self, category_type: str, tag_name: str) -> List[str]:
        """
        Infer compatible genres for a meta tag
        
        Args:
            category_type: Category type of the meta tag
            tag_name: Meta tag name
            
        Returns:
            List of compatible genres
        """
        compatible_genres = []
        tag_lower = tag_name.lower()

        # Universal tags that work with most genres
        if category_type in ['structural', 'effects']:
            compatible_genres.extend(['pop', 'rock', 'hip hop', 'electronic', 'jazz', 'blues', 'country'])

        # Genre-specific tags
        if 'jazz' in tag_lower:
            compatible_genres.extend(['jazz', 'blues', 'soul'])
        elif 'rock' in tag_lower or 'metal' in tag_lower:
            compatible_genres.extend(['rock', 'metal', 'punk'])
        elif 'hip hop' in tag_lower or 'rap' in tag_lower:
            compatible_genres.extend(['hip hop', 'rap', 'trap'])
        elif 'electronic' in tag_lower or 'edm' in tag_lower or 'techno' in tag_lower:
            compatible_genres.extend(['electronic', 'edm', 'techno', 'house'])
        elif 'pop' in tag_lower:
            compatible_genres.extend(['pop', 'dance-pop', 'synth-pop'])
        elif 'country' in tag_lower:
            compatible_genres.extend(['country', 'folk', 'americana'])
        elif 'gospel' in tag_lower or 'christian' in tag_lower:
            compatible_genres.extend(['gospel', 'soul', 'r&b'])
        elif 'acoustic' in tag_lower:
            compatible_genres.extend(['folk', 'country', 'indie', 'singer-songwriter'])
        elif 'ambient' in tag_lower or 'chill' in tag_lower:
            compatible_genres.extend(['ambient', 'electronic', 'new age'])
        elif 'orchestra' in tag_lower or 'classical' in tag_lower:
            compatible_genres.extend(['classical', 'orchestral', 'cinematic'])

        # Instrument-based compatibility
        if 'piano' in tag_lower:
            compatible_genres.extend(['jazz', 'classical', 'pop', 'ballad'])
        elif 'guitar' in tag_lower:
            compatible_genres.extend(['rock', 'country', 'folk', 'blues'])
        elif 'drums' in tag_lower:
            compatible_genres.extend(['rock', 'hip hop', 'electronic', 'jazz'])

        # Vocal style compatibility
        if category_type == 'vocal':
            if any(word in tag_lower for word in ['announcer', 'reporter']):
                compatible_genres.extend(['spoken word', 'hip hop', 'experimental'])
            else:
                compatible_genres.extend(['pop', 'r&b', 'soul', 'jazz'])

        # Sound effects are generally compatible with most genres
        if category_type == 'sound_effects':
            compatible_genres.extend(['experimental', 'electronic', 'hip hop', 'cinematic'])

        return list(set(compatible_genres))  # Remove duplicates

    def parse_tip_page(self, html_content: str, source_url: str = "") -> List[Technique]:
        """
        Parse tip page content from Suno AI Wiki to extract techniques
        
        Args:
            html_content: Raw HTML content
            source_url: Source URL for attribution
            
        Returns:
            List of Technique objects
        """
        techniques = []

        try:
            soup = self.parse_html(html_content, source_url)

            # Extract the main technique from the page title and content
            main_technique = self._extract_main_technique(soup, source_url)
            if main_technique:
                techniques.append(main_technique)

            # Extract additional techniques from numbered examples and sections
            additional_techniques = self._extract_additional_techniques(soup, source_url)
            techniques.extend(additional_techniques)

            logger.info(f"Successfully parsed {len(techniques)} techniques from {source_url}")

        except Exception as e:
            error_msg = f"Error parsing tip page: {str(e)}"
            logger.error(error_msg)
            raise ContentExtractionError(error_msg) from e

        return techniques

    def _extract_main_technique(self, soup, source_url: str) -> Optional[Technique]:
        """
        Extract the main technique from the page title and overall content
        
        Args:
            soup: BeautifulSoup object
            source_url: Source URL for attribution
            
        Returns:
            Main Technique object or None
        """
        try:
            # Get the page title
            title_element = soup.find('h1')
            if not title_element:
                return None

            title = self.extract_text_content(title_element)
            if not title:
                return None

            # Extract technique name from title (remove "How to" prefix)
            technique_name = re.sub(r'^How to\s+', '', title, flags=re.IGNORECASE)
            technique_name = re.sub(r'\s+for Suno AI$', '', technique_name, flags=re.IGNORECASE)
            technique_name = technique_name.strip()

            # Get the main content description
            main_content = soup.find('div', class_='sl-markdown-content')
            if not main_content:
                return None

            # Extract the solution/description paragraph
            description = ""
            solution_p = main_content.find('p')
            if solution_p:
                description = self.extract_text_content(solution_p)
                # Clean up the description
                description = re.sub(r'^\*\*Solution:\*\*\s*', '', description)
                description = self.clean_text(description)

            # Extract examples from the content
            examples = self._extract_examples_from_content(main_content)

            # Determine technique type based on title and content
            technique_type = self._determine_technique_type(technique_name, description)

            # Extract applicable scenarios
            scenarios = self._extract_applicable_scenarios(technique_name, description, examples)

            return Technique(
                name=technique_name,
                description=description or f"Technique for {technique_name.lower()}",
                technique_type=technique_type,
                examples=examples,
                applicable_scenarios=scenarios,
                source_url=source_url,
                download_date=datetime.now()
            )

        except Exception as e:
            logger.warning(f"Error extracting main technique: {e}")
            return None

    def _extract_additional_techniques(self, soup, source_url: str) -> List[Technique]:
        """
        Extract additional techniques from numbered examples and sections
        
        Args:
            soup: BeautifulSoup object
            source_url: Source URL for attribution
            
        Returns:
            List of additional Technique objects
        """
        techniques = []

        try:
            main_content = soup.find('div', class_='sl-markdown-content')
            if not main_content:
                return techniques

            # Look for numbered lists with techniques
            numbered_lists = main_content.find_all('ol')
            for ol in numbered_lists:
                list_items = ol.find_all('li')
                for li in list_items:
                    technique = self._parse_technique_from_list_item(li, source_url)
                    if technique:
                        techniques.append(technique)

            # Look for sections with headings that might contain techniques
            headings = main_content.find_all(['h2', 'h3', 'h4'])
            for heading in headings:
                if 'tip' in heading.get_text().lower():
                    technique = self._parse_technique_from_section(heading, source_url)
                    if technique:
                        techniques.append(technique)

        except Exception as e:
            logger.warning(f"Error extracting additional techniques: {e}")

        return techniques

    def _parse_technique_from_list_item(self, li_element, source_url: str) -> Optional[Technique]:
        """
        Parse a technique from a list item
        
        Args:
            li_element: List item BeautifulSoup element
            source_url: Source URL for attribution
            
        Returns:
            Technique object or None
        """
        try:
            text_content = self.extract_text_content(li_element)
            if not text_content or len(text_content) < 20:  # Skip very short items
                return None

            # Look for technique name in bold or at the beginning
            technique_name = ""
            description = text_content

            # Check for bold text that might be the technique name
            strong_elements = li_element.find_all(['strong', 'b'])
            if strong_elements:
                technique_name = self.extract_text_content(strong_elements[0])
                # Remove the technique name from description
                description = text_content.replace(technique_name, '', 1).strip()
                description = re.sub(r'^[:\-]\s*', '', description)  # Remove leading colon or dash
            else:
                # Try to extract technique name from the first sentence
                sentences = text_content.split('.')
                if sentences:
                    first_sentence = sentences[0].strip()
                    if len(first_sentence) < 100:  # Reasonable length for a technique name
                        technique_name = first_sentence
                        description = '.'.join(sentences[1:]).strip()

            if not technique_name:
                technique_name = text_content[:50] + "..." if len(text_content) > 50 else text_content

            # Extract code examples
            examples = []
            code_elements = li_element.find_all('code')
            for code in code_elements:
                code_text = self.extract_text_content(code)
                if code_text:
                    examples.append(code_text)

            # Determine technique type
            technique_type = self._determine_technique_type(technique_name, description)

            # Extract applicable scenarios
            scenarios = self._extract_applicable_scenarios(technique_name, description, examples)

            return Technique(
                name=technique_name,
                description=description,
                technique_type=technique_type,
                examples=examples,
                applicable_scenarios=scenarios,
                source_url=source_url,
                download_date=datetime.now()
            )

        except Exception as e:
            logger.warning(f"Error parsing technique from list item: {e}")
            return None

    def _parse_technique_from_section(self, heading_element, source_url: str) -> Optional[Technique]:
        """
        Parse a technique from a section with heading
        
        Args:
            heading_element: Heading BeautifulSoup element
            source_url: Source URL for attribution
            
        Returns:
            Technique object or None
        """
        try:
            technique_name = self.extract_text_content(heading_element)
            if not technique_name:
                return None

            # Get content following the heading
            description_parts = []
            current = heading_element.find_next_sibling()

            while current and current.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if current.name in ['p', 'div']:
                    text = self.extract_text_content(current)
                    if text:
                        description_parts.append(text)
                current = current.find_next_sibling()

            description = ' '.join(description_parts)

            # Determine technique type
            technique_type = self._determine_technique_type(technique_name, description)

            # Extract applicable scenarios
            scenarios = self._extract_applicable_scenarios(technique_name, description, [])

            return Technique(
                name=technique_name,
                description=description,
                technique_type=technique_type,
                examples=[],
                applicable_scenarios=scenarios,
                source_url=source_url,
                download_date=datetime.now()
            )

        except Exception as e:
            logger.warning(f"Error parsing technique from section: {e}")
            return None

    def _extract_examples_from_content(self, content_element) -> List[str]:
        """
        Extract code examples and practical examples from content
        
        Args:
            content_element: BeautifulSoup element containing content
            
        Returns:
            List of example strings
        """
        examples = []

        try:
            # Extract code blocks
            code_elements = content_element.find_all('code')
            for code in code_elements:
                code_text = self.extract_text_content(code)
                if code_text and code_text not in examples:
                    examples.append(code_text)

            # Extract pre blocks
            pre_elements = content_element.find_all('pre')
            for pre in pre_elements:
                pre_text = self.extract_text_content(pre)
                if pre_text and pre_text not in examples:
                    examples.append(pre_text)

            # Look for example patterns in text
            paragraphs = content_element.find_all('p')
            for p in paragraphs:
                text = self.extract_text_content(p)
                if 'example' in text.lower():
                    # Try to extract examples from the text
                    example_match = re.search(r'example[s]?[:\-]?\s*([^.]+)', text, re.IGNORECASE)
                    if example_match:
                        example_text = example_match.group(1).strip()
                        if example_text and example_text not in examples:
                            examples.append(example_text)

        except Exception as e:
            logger.warning(f"Error extracting examples: {e}")

        return examples

    def _determine_technique_type(self, technique_name: str, description: str) -> str:
        """
        Determine the type of technique based on name and description
        
        Args:
            technique_name: Name of the technique
            description: Description of the technique
            
        Returns:
            Technique type string
        """
        name_lower = technique_name.lower()
        desc_lower = description.lower()

        # Prompt-related techniques
        if any(word in name_lower for word in ['prompt', 'structure', 'format']):
            return 'prompt_structure'

        # Vocal techniques
        if any(word in name_lower for word in ['vocal', 'voice', 'sing', 'spoken']):
            return 'vocal_style'

        # Production techniques
        if any(word in name_lower for word in ['production', 'enhance', 'quality', 'master']):
            return 'production'

        # Meta tag techniques
        if any(word in name_lower for word in ['meta', 'tag']):
            return 'meta_tags'

        # Lyric techniques
        if any(word in name_lower for word in ['lyric', 'lyrics', 'word']):
            return 'lyrics'

        # Song structure techniques
        if any(word in name_lower for word in ['song', 'extension', 'ending', 'structure']):
            return 'song_structure'

        # Technical techniques
        if any(word in name_lower for word in ['bypass', 'solve', 'fix', 'handle']):
            return 'technical'

        # Check description for additional clues
        if any(word in desc_lower for word in ['prompt', 'prompting']):
            return 'prompt_structure'
        elif any(word in desc_lower for word in ['vocal', 'voice']):
            return 'vocal_style'
        elif any(word in desc_lower for word in ['production', 'quality']):
            return 'production'

        return 'general'

    def _extract_applicable_scenarios(self, technique_name: str, description: str,
                                    examples: List[str]) -> List[str]:
        """
        Extract applicable scenarios for the technique
        
        Args:
            technique_name: Name of the technique
            description: Description of the technique
            examples: List of examples
            
        Returns:
            List of applicable scenarios
        """
        scenarios = []

        name_lower = technique_name.lower()
        desc_lower = description.lower()

        # Genre-specific scenarios
        if any(genre in name_lower or genre in desc_lower for genre in ['metal', 'rock', 'pop', 'jazz', 'hip hop', 'electronic']):
            scenarios.append('genre-specific music')

        # Vocal scenarios
        if any(word in name_lower or word in desc_lower for word in ['vocal', 'voice', 'sing']):
            scenarios.extend(['vocal music', 'singer-songwriter', 'vocal effects'])

        # Production scenarios
        if any(word in name_lower or word in desc_lower for word in ['production', 'quality', 'enhance']):
            scenarios.extend(['music production', 'audio enhancement', 'professional recording'])

        # Prompt scenarios
        if any(word in name_lower or word in desc_lower for word in ['prompt', 'structure']):
            scenarios.extend(['AI music generation', 'prompt engineering', 'consistent results'])

        # Lyric scenarios
        if any(word in name_lower or word in desc_lower for word in ['lyric', 'lyrics']):
            scenarios.extend(['songwriting', 'lyric creation', 'narrative songs'])

        # Technical scenarios
        if any(word in name_lower or word in desc_lower for word in ['bypass', 'solve', 'fix']):
            scenarios.extend(['troubleshooting', 'technical issues', 'workarounds'])

        # Default scenarios if none found
        if not scenarios:
            scenarios.extend(['music creation', 'AI-assisted composition'])

        return list(set(scenarios))  # Remove duplicates

# ================================================================================================
# UTILITY FUNCTIONS
# ================================================================================================

def detect_page_type(url: str, html_content: str = "") -> str:
    """
    Detect the type of wiki page based on URL and content
    
    Args:
        url: Page URL
        html_content: Optional HTML content for additional detection
        
    Returns:
        Page type string ('genres', 'meta_tags', 'techniques', 'unknown')
    """
    url_lower = url.lower()

    # URL-based detection
    if 'genres' in url_lower or 'music-genres' in url_lower:
        return 'genres'
    elif 'metatags' in url_lower or 'meta-tags' in url_lower:
        return 'meta_tags'
    elif '/tips/' in url_lower:
        return 'techniques'

    # Content-based detection if HTML is provided
    if html_content:
        content_lower = html_content.lower()
        if 'genre' in content_lower and ('music' in content_lower or 'style' in content_lower):
            return 'genres'
        elif 'meta tag' in content_lower or 'metatag' in content_lower:
            return 'meta_tags'
        elif any(keyword in content_lower for keyword in ['tip', 'technique', 'how to', 'guide']):
            return 'techniques'

    return 'unknown'

def validate_parsed_data(data: Union[Genre, MetaTag, Technique]) -> List[str]:
    """
    Validate parsed data object
    
    Args:
        data: Parsed data object to validate
        
    Returns:
        List of validation errors
    """
    errors = []

    if isinstance(data, Genre):
        if not data.name:
            errors.append("Genre name is required")
        if not data.description:
            errors.append("Genre description is required")

    elif isinstance(data, MetaTag):
        if not data.tag:
            errors.append("Meta tag is required")
        if not data.category:
            errors.append("Meta tag category is required")
        if not data.description:
            errors.append("Meta tag description is required")

    elif isinstance(data, Technique):
        if not data.name:
            errors.append("Technique name is required")
        if not data.description:
            errors.append("Technique description is required")
        if not data.technique_type:
            errors.append("Technique type is required")

    return errors
