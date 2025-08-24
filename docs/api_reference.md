# API Reference

## Overview

This document provides comprehensive API documentation for all public interfaces in the Wiki Data Integration system. All APIs are designed to be async-first and provide robust error handling.

## Core APIs

### WikiDataManager

The central coordinator for all wiki data operations.

#### Constructor

```python
WikiDataManager()
```

Creates a new WikiDataManager instance. Must be initialized before use.

#### Methods

##### `async initialize(config: WikiConfig) -> None`

Initialize the wiki data manager with configuration.

**Parameters:**
- `config` (WikiConfig): Configuration object with all settings

**Raises:**
- `ValueError`: If configuration is invalid
- `RuntimeError`: If initialization fails

**Example:**
```python
from wiki_data_system import WikiDataManager, ConfigurationManager

config = await ConfigurationManager.load_config()
manager = WikiDataManager()
await manager.initialize(config)
```

##### `async get_genres() -> List[Genre]`

Get list of genres from wiki data.

**Returns:**
- `List[Genre]`: List of genre objects with metadata

**Raises:**
- `RuntimeError`: If manager not initialized

**Example:**
```python
genres = await manager.get_genres()
for genre in genres:
    print(f"{genre.name}: {genre.description}")
```

##### `async get_meta_tags(category: str = None) -> List[MetaTag]`

Get list of meta tags, optionally filtered by category.

**Parameters:**
- `category` (str, optional): Filter by category (e.g., "emotional", "structural")

**Returns:**
- `List[MetaTag]`: List of meta tag objects

**Example:**
```python
# Get all meta tags
all_tags = await manager.get_meta_tags()

# Get emotional tags only
emotional_tags = await manager.get_meta_tags("emotional")
```

##### `async get_techniques(technique_type: str = None) -> List[Technique]`

Get list of techniques, optionally filtered by type.

**Parameters:**
- `technique_type` (str, optional): Filter by type (e.g., "vocal_style", "production")

**Returns:**
- `List[Technique]`: List of technique objects

**Example:**
```python
# Get all techniques
all_techniques = await manager.get_techniques()

# Get vocal techniques only
vocal_techniques = await manager.get_techniques("vocal_style")
```

##### `async refresh_data(force: bool = False) -> RefreshResult`

Refresh wiki data from remote sources.

**Parameters:**
- `force` (bool): Force refresh even if data is fresh

**Returns:**
- `RefreshResult`: Object containing refresh status and statistics

**Example:**
```python
result = await manager.refresh_data(force=True)
print(f"Downloaded {result.pages_downloaded} pages")
print(f"Failed {result.pages_failed} pages")
```

##### `get_source_urls(data_type: str) -> List[str]`

Get source URLs for attribution.

**Parameters:**
- `data_type` (str): Type of data ("genres", "meta_tags", "techniques")

**Returns:**
- `List[str]`: List of source URLs

**Example:**
```python
genre_sources = manager.get_source_urls("genres")
print(f"Genre data from: {genre_sources}")
```

##### `async cleanup() -> None`

Clean up resources and close connections.

**Example:**
```python
await manager.cleanup()
```

### ContentParser

Base HTML content parser with structured content extraction methods.

#### Constructor

```python
ContentParser(parser: str = "lxml")
```

**Parameters:**
- `parser` (str): BeautifulSoup parser to use ("lxml", "html.parser", etc.)

#### Methods

##### `parse_html(html_content: str, source_url: str = "") -> BeautifulSoup`

Parse HTML content with error handling.

**Parameters:**
- `html_content` (str): Raw HTML content to parse
- `source_url` (str): Source URL for error reporting

**Returns:**
- `BeautifulSoup`: Parsed HTML object

**Raises:**
- `MalformedHTMLError`: If HTML cannot be parsed

##### `extract_text_content(element: Union[Tag, NavigableString, None]) -> str`

Safely extract text content from an element.

**Parameters:**
- `element`: BeautifulSoup element

**Returns:**
- `str`: Cleaned text content

##### `extract_links(element: Tag, base_url: str = "") -> List[str]`

Extract all links from an element.

**Parameters:**
- `element` (Tag): BeautifulSoup element to search
- `base_url` (str): Base URL for resolving relative links

**Returns:**
- `List[str]`: List of absolute URLs

##### `parse_genre_page(html_content: str, source_url: str = "") -> List[Genre]`

Parse genre page and extract genre data.

**Parameters:**
- `html_content` (str): HTML content of genre page
- `source_url` (str): Source URL for attribution

**Returns:**
- `List[Genre]`: List of parsed genre objects

##### `parse_meta_tag_page(html_content: str, source_url: str = "") -> List[MetaTag]`

Parse meta tag page and extract meta tag data.

**Parameters:**
- `html_content` (str): HTML content of meta tag page
- `source_url` (str): Source URL for attribution

**Returns:**
- `List[MetaTag]`: List of parsed meta tag objects

##### `parse_tip_page(html_content: str, source_url: str = "") -> List[Technique]`

Parse tip page and extract technique data.

**Parameters:**
- `html_content` (str): HTML content of tip page
- `source_url` (str): Source URL for attribution

**Returns:**
- `List[Technique]`: List of parsed technique objects

##### `extract_structured_content(html: str, page_type: str, source_url: str = "") -> ParsedContent`

Generic structured content extraction.

**Parameters:**
- `html` (str): HTML content
- `page_type` (str): Type of page ("genre", "meta_tag", "technique")
- `source_url` (str): Source URL for attribution

**Returns:**
- `ParsedContent`: Container with parsed content and metadata

### EnhancedGenreMapper

Intelligent genre mapping with wiki-sourced data.

#### Constructor

```python
EnhancedGenreMapper(wiki_data_manager: WikiDataManager)
```

**Parameters:**
- `wiki_data_manager`: WikiDataManager instance for accessing genre data

#### Methods

##### `async map_traits_to_genres(traits: List[str], max_results: int = 5, use_hierarchical: bool = True) -> List[GenreMatch]`

Map character traits to wiki-sourced genres using intelligent semantic analysis.

**Parameters:**
- `traits` (List[str]): List of character traits to match
- `max_results` (int): Maximum number of genre matches to return
- `use_hierarchical` (bool): Whether to consider genre hierarchies

**Returns:**
- `List[GenreMatch]`: List of genre matches sorted by confidence

**Example:**
```python
mapper = EnhancedGenreMapper(wiki_manager)
traits = ["melancholic", "introspective", "acoustic"]
matches = await mapper.map_traits_to_genres(traits, max_results=3)

for match in matches:
    print(f"{match.genre.name}: {match.confidence:.2f}")
```

##### `calculate_genre_confidence(traits: List[str], genre: Genre) -> float`

Calculate confidence score for a specific genre match.

**Parameters:**
- `traits` (List[str]): Character traits
- `genre` (Genre): Genre to evaluate

**Returns:**
- `float`: Confidence score between 0.0 and 1.0

##### `get_genre_hierarchy(genre: str) -> GenreHierarchy`

Get genre hierarchy and relationships.

**Parameters:**
- `genre` (str): Genre name

**Returns:**
- `GenreHierarchy`: Object containing genre relationships

##### `async find_similar_genres(target_genre: str) -> List[Genre]`

Find genres similar to the target genre.

**Parameters:**
- `target_genre` (str): Target genre name

**Returns:**
- `List[Genre]`: List of similar genres

### SourceAttributionManager

Manages source URL attribution for LLM context building.

#### Constructor

```python
SourceAttributionManager(storage_path: str = "./data/attribution")
```

**Parameters:**
- `storage_path` (str): Directory for storing attribution data

#### Methods

##### `async initialize() -> None`

Initialize the attribution manager.

##### `build_attributed_context(content: Any, sources: List[str]) -> AttributedContent`

Build attributed content with source references.

**Parameters:**
- `content`: Content to attribute
- `sources` (List[str]): List of source URLs

**Returns:**
- `AttributedContent`: Content with attribution metadata

**Example:**
```python
attribution_manager = SourceAttributionManager()
await attribution_manager.initialize()

content = {"genres": ["rock", "blues"]}
sources = ["https://sunoaiwiki.com/genres"]

attributed = attribution_manager.build_attributed_context(content, sources)
print(attributed.attribution_text)
```

##### `format_source_references(sources: List[str]) -> str`

Format source references for display.

**Parameters:**
- `sources` (List[str]): List of source URLs

**Returns:**
- `str`: Formatted source references

##### `track_content_usage(content_id: str, source_url: str, context: str = "") -> None`

Track content usage for analytics.

**Parameters:**
- `content_id` (str): Unique content identifier
- `source_url` (str): Source URL
- `context` (str): Usage context description

##### `async get_usage_statistics() -> Dict[str, Any]`

Get usage statistics for tracked content.

**Returns:**
- `Dict[str, Any]`: Usage statistics

### WikiDownloader

Downloads and manages wiki page content.

#### Constructor

```python
WikiDownloader(cache_manager: WikiCacheManager, request_timeout: int = 30, max_retries: int = 3, retry_delay: float = 1.0)
```

**Parameters:**
- `cache_manager`: Cache manager instance
- `request_timeout` (int): HTTP request timeout in seconds
- `max_retries` (int): Maximum retry attempts
- `retry_delay` (float): Delay between retries in seconds

#### Methods

##### `async download_page(url: str, local_path: str) -> DownloadResult`

Download a single wiki page.

**Parameters:**
- `url` (str): URL to download
- `local_path` (str): Local storage path

**Returns:**
- `DownloadResult`: Download result with status and content

##### `async download_all_configured_pages() -> List[DownloadResult]`

Download all configured wiki pages.

**Returns:**
- `List[DownloadResult]`: List of download results

##### `is_refresh_needed(local_path: str, max_age_hours: int) -> bool`

Check if a refresh is needed for a local file.

**Parameters:**
- `local_path` (str): Path to local file
- `max_age_hours` (int): Maximum age in hours

**Returns:**
- `bool`: True if refresh is needed

##### `async validate_url(url: str) -> bool`

Validate URL accessibility.

**Parameters:**
- `url` (str): URL to validate

**Returns:**
- `bool`: True if URL is accessible

##### `async cleanup() -> None`

Clean up HTTP client resources.

## Configuration APIs

### ConfigurationManager

Manages wiki configuration loading and saving.

#### Static Methods

##### `async load_config(config_path: str = None) -> WikiConfig`

Load configuration from file.

**Parameters:**
- `config_path` (str, optional): Path to configuration file

**Returns:**
- `WikiConfig`: Loaded configuration object

**Example:**
```python
from wiki_data_system import ConfigurationManager

# Load default configuration
config = await ConfigurationManager.load_config()

# Load from custom path
config = await ConfigurationManager.load_config("custom/config.json")
```

##### `async save_config(config: WikiConfig, config_path: str = None) -> None`

Save configuration to file.

**Parameters:**
- `config` (WikiConfig): Configuration to save
- `config_path` (str, optional): Path to save configuration

**Example:**
```python
config = WikiConfig(enabled=True, refresh_interval_hours=48)
await ConfigurationManager.save_config(config, "config/wiki_config.json")
```

### DynamicConfigManager

Manages runtime configuration updates with file watching.

#### Constructor

```python
DynamicConfigManager(config_path: str = None)
```

**Parameters:**
- `config_path` (str, optional): Path to configuration file

#### Methods

##### `async initialize() -> WikiConfig`

Initialize the configuration manager and load initial config.

**Returns:**
- `WikiConfig`: Loaded configuration

##### `start_watching() -> None`

Start watching the configuration file for changes.

##### `stop_watching() -> None`

Stop watching the configuration file.

##### `async update_config(new_config: WikiConfig, validate_urls: bool = True) -> ValidationResult`

Update configuration programmatically.

**Parameters:**
- `new_config` (WikiConfig): New configuration to apply
- `validate_urls` (bool): Whether to validate URL accessibility

**Returns:**
- `ValidationResult`: Validation result

##### `async add_urls(url_type: str, urls: List[str], validate_urls: bool = True) -> ValidationResult`

Add new URLs to configuration.

**Parameters:**
- `url_type` (str): Type of URLs ("genre_pages", "meta_tag_pages", "tip_pages")
- `urls` (List[str]): List of URLs to add
- `validate_urls` (bool): Whether to validate URL accessibility

**Returns:**
- `ValidationResult`: Validation result

**Example:**
```python
manager = DynamicConfigManager()
await manager.initialize()

result = await manager.add_urls(
    "tip_pages",
    ["https://sunoaiwiki.com/tips/new-technique/"]
)

if result.is_valid:
    print("URLs added successfully")
```

##### `async remove_urls(url_type: str, urls: List[str]) -> ValidationResult`

Remove URLs from configuration.

**Parameters:**
- `url_type` (str): Type of URLs
- `urls` (List[str]): List of URLs to remove

**Returns:**
- `ValidationResult`: Validation result

##### `async update_settings(**settings) -> ValidationResult`

Update specific configuration settings.

**Parameters:**
- `**settings`: Settings to update

**Returns:**
- `ValidationResult`: Validation result

**Example:**
```python
result = await manager.update_settings(
    refresh_interval_hours=72,
    request_timeout=45
)
```

##### `add_change_callback(callback: Callable[[WikiConfig, WikiConfig], None]) -> None`

Add a callback to be notified when configuration changes.

**Parameters:**
- `callback`: Function to call with (old_config, new_config)

##### `get_current_config() -> Optional[WikiConfig]`

Get the current configuration.

**Returns:**
- `Optional[WikiConfig]`: Current configuration or None

## Validation APIs

### WikiConfigValidator

Comprehensive configuration validator.

#### Constructor

```python
WikiConfigValidator(timeout: int = 10)
```

**Parameters:**
- `timeout` (int): Timeout for network checks in seconds

#### Methods

##### `async validate_config(config: WikiConfig, check_urls: bool = True) -> ValidationResult`

Perform comprehensive configuration validation.

**Parameters:**
- `config` (WikiConfig): Configuration to validate
- `check_urls` (bool): Whether to perform network checks on URLs

**Returns:**
- `ValidationResult`: Validation result with details

**Example:**
```python
from wiki_config_validator import WikiConfigValidator

validator = WikiConfigValidator()
result = await validator.validate_config(config, check_urls=True)

print(f"Valid: {result.is_valid}")
for error in result.errors:
    print(f"Error: {error}")
for warning in result.warnings:
    print(f"Warning: {warning}")
```

##### `async validate_new_urls(urls: List[str]) -> Dict[str, bool]`

Validate a list of new URLs for accessibility.

**Parameters:**
- `urls` (List[str]): List of URLs to validate

**Returns:**
- `Dict[str, bool]`: Dictionary mapping URLs to accessibility status

### Convenience Functions

#### `async validate_config_quick(config: WikiConfig) -> ValidationResult`

Quick validation without network checks.

#### `async validate_config_full(config: WikiConfig, timeout: int = 10) -> ValidationResult`

Full validation including network checks.

#### `async validate_storage_only(config: WikiConfig) -> ValidationResult`

Validate only storage-related configuration.

#### `async check_urls_accessibility(urls: List[str], timeout: int = 10) -> Dict[str, bool]`

Check accessibility of a list of URLs.

## Data Models

### WikiConfig

Configuration data model for the wiki integration system.

#### Fields

- `enabled` (bool): Whether wiki integration is active
- `local_storage_path` (str): Directory for storing wiki data
- `refresh_interval_hours` (int): How often to refresh data
- `fallback_to_hardcoded` (bool): Whether to use hardcoded fallbacks
- `genre_pages` (List[str]): List of genre resource URLs
- `meta_tag_pages` (List[str]): List of meta tag resource URLs
- `tip_pages` (List[str]): List of technique tip URLs
- `request_timeout` (int): HTTP request timeout in seconds
- `max_retries` (int): Maximum retry attempts
- `retry_delay` (float): Delay between retries in seconds

#### Methods

##### `to_dict() -> Dict[str, Any]`

Convert to dictionary for JSON serialization.

##### `from_dict(data: Dict[str, Any]) -> WikiConfig`

Create WikiConfig from dictionary.

##### `validate() -> List[str]`

Validate configuration and return list of errors.

### Genre

Music genre data model from wiki.

#### Fields

- `name` (str): Genre name
- `description` (str): Genre description
- `subgenres` (List[str]): List of subgenres
- `characteristics` (List[str]): Genre characteristics
- `typical_instruments` (List[str]): Common instruments
- `mood_associations` (List[str]): Associated moods
- `source_url` (str): Source URL
- `download_date` (datetime): When data was downloaded
- `confidence_score` (float): Confidence score (0.0-1.0)

### MetaTag

Meta tag data model from wiki.

#### Fields

- `tag` (str): Meta tag text
- `category` (str): Tag category (structural, emotional, etc.)
- `description` (str): Tag description
- `usage_examples` (List[str]): Usage examples
- `compatible_genres` (List[str]): Compatible genres
- `source_url` (str): Source URL
- `download_date` (datetime): When data was downloaded

### Technique

Technique data model from wiki tip pages.

#### Fields

- `name` (str): Technique name
- `description` (str): Technique description
- `technique_type` (str): Type (prompt_structure, vocal_style, etc.)
- `examples` (List[str]): Usage examples
- `applicable_scenarios` (List[str]): When to use
- `source_url` (str): Source URL
- `download_date` (datetime): When data was downloaded

### GenreMatch

Represents a genre match with confidence scoring.

#### Fields

- `genre` (Genre): Matched genre
- `confidence` (float): Confidence score (0.0-1.0)
- `matching_traits` (List[str]): Traits that matched
- `matching_reasons` (List[str]): Reasons for the match

### RefreshResult

Result of data refresh operation.

#### Fields

- `success` (bool): Whether refresh succeeded
- `pages_downloaded` (int): Number of pages downloaded
- `pages_failed` (int): Number of pages that failed
- `errors` (List[str]): List of errors encountered
- `refresh_time` (datetime): When refresh occurred

### ValidationResult

Result of configuration validation.

#### Fields

- `is_valid` (bool): Whether configuration is valid
- `errors` (List[str]): List of validation errors
- `warnings` (List[str]): List of validation warnings
- `url_checks` (Dict[str, bool]): URL accessibility results
- `storage_info` (Dict[str, Any]): Storage information

#### Methods

##### `add_error(message: str) -> None`

Add validation error.

##### `add_warning(message: str) -> None`

Add validation warning.

##### `to_dict() -> Dict[str, Any]`

Convert to dictionary for serialization.

## Error Handling

### Exception Hierarchy

```
Exception
├── ParseError
│   ├── MalformedHTMLError
│   └── ContentExtractionError
├── ValidationError
├── DownloadError
└── ConfigurationError
```

### ParseError

Base exception for parsing errors.

### MalformedHTMLError

Exception for malformed HTML content.

### ContentExtractionError

Exception for content extraction failures.

### ValidationError

Exception for validation failures.

### DownloadError

Exception for download failures.

### ConfigurationError

Exception for configuration errors.

## Usage Examples

### Basic Usage

```python
import asyncio
from wiki_data_system import WikiDataManager, ConfigurationManager

async def main():
    # Load configuration
    config = await ConfigurationManager.load_config()
    
    # Initialize manager
    manager = WikiDataManager()
    await manager.initialize(config)
    
    # Get data
    genres = await manager.get_genres()
    print(f"Loaded {len(genres)} genres")
    
    # Clean up
    await manager.cleanup()

asyncio.run(main())
```

### Advanced Usage with Attribution

```python
from wiki_data_system import WikiDataManager, ConfigurationManager
from enhanced_genre_mapper import EnhancedGenreMapper
from source_attribution_manager import SourceAttributionManager

async def advanced_example():
    # Initialize components
    config = await ConfigurationManager.load_config()
    manager = WikiDataManager()
    await manager.initialize(config)
    
    mapper = EnhancedGenreMapper(manager)
    attribution = SourceAttributionManager()
    await attribution.initialize()
    
    # Map traits to genres
    traits = ["melancholic", "acoustic", "storytelling"]
    matches = await mapper.map_traits_to_genres(traits)
    
    # Build attributed context
    genre_data = [match.genre for match in matches]
    sources = manager.get_source_urls("genres")
    
    attributed_content = attribution.build_attributed_context(
        genre_data, sources
    )
    
    print(f"Found {len(matches)} genre matches")
    print(f"Attribution: {attributed_content.attribution_text}")
    
    # Track usage
    attribution.track_content_usage(
        "genre_mapping_001", 
        sources[0], 
        "Character trait mapping"
    )
    
    await manager.cleanup()

asyncio.run(advanced_example())
```

### Dynamic Configuration

```python
from dynamic_config_manager import DynamicConfigManager

async def dynamic_config_example():
    # Initialize dynamic manager
    manager = DynamicConfigManager()
    config = await manager.initialize()
    
    # Start watching for changes
    manager.start_watching()
    
    # Add callback for configuration changes
    async def on_config_change(old_config, new_config):
        print("Configuration changed!")
        print(f"Refresh interval: {old_config.refresh_interval_hours} -> {new_config.refresh_interval_hours}")
    
    manager.add_change_callback(on_config_change)
    
    # Update configuration at runtime
    result = await manager.update_settings(refresh_interval_hours=48)
    if result.is_valid:
        print("Configuration updated successfully")
    
    # Add new URLs
    result = await manager.add_urls(
        "tip_pages",
        ["https://sunoaiwiki.com/tips/new-advanced-technique/"]
    )
    
    # Stop watching
    manager.stop_watching()

asyncio.run(dynamic_config_example())
```

This API reference provides comprehensive documentation for all public interfaces in the Wiki Data Integration system. Use this reference to understand method signatures, parameters, return values, and usage patterns.