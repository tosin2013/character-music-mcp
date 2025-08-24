# Wiki Data System Documentation

## Overview

The Wiki Data System provides dynamic integration with the Suno AI Wiki to enhance music generation capabilities. Instead of relying on static hardcoded mappings, the system downloads, caches, and manages wiki content locally.

## Core Components

### WikiConfig

Configuration data model that defines:
- **enabled**: Whether wiki integration is active
- **local_storage_path**: Where to store downloaded wiki data
- **refresh_interval_hours**: How often to refresh data from wiki
- **fallback_to_hardcoded**: Whether to use hardcoded data when wiki unavailable
- **genre_pages**: List of genre resource URLs
- **meta_tag_pages**: List of meta tag resource URLs  
- **tip_pages**: List of technique tip URLs

### WikiDataManager

Central coordinator that provides:
- `initialize(config)`: Set up the system with configuration
- `get_genres()`: Retrieve genre data from wiki
- `get_meta_tags(category=None)`: Retrieve meta tags, optionally filtered
- `get_techniques(technique_type=None)`: Retrieve techniques, optionally filtered
- `refresh_data(force=False)`: Update data from wiki sources
- `get_source_urls(data_type)`: Get source URLs for attribution

### Data Models

- **Genre**: Music genre with description, subgenres, characteristics
- **MetaTag**: Suno meta tag with category, description, usage examples
- **Technique**: Production technique with type, examples, scenarios

## Configuration

### Default Configuration File

Location: `config/wiki_config.json`

```json
{
  "enabled": true,
  "local_storage_path": "./data/wiki",
  "refresh_interval_hours": 24,
  "fallback_to_hardcoded": true,
  "genre_pages": [
    "https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"
  ],
  "meta_tag_pages": [
    "https://sunoaiwiki.com/resources/2024-05-13-list-of-metatags/"
  ],
  "tip_pages": [
    "https://sunoaiwiki.com/tips/2024-05-02-how-to-enhance-song-production-using-suno-ai/",
    "https://sunoaiwiki.com/tips/2024-04-16-how-to-make-suno-ai-sing-with-spoken-word/",
    ...
  ]
}
```

### Configuration Management

```python
from wiki_data_system import ConfigurationManager

# Load configuration
config = await ConfigurationManager.load_config("path/to/config.json")

# Save configuration
await ConfigurationManager.save_config(config, "path/to/config.json")
```

## Usage Example

```python
from wiki_data_system import WikiDataManager, ConfigurationManager

# Initialize system
config = await ConfigurationManager.load_config()
manager = WikiDataManager()
await manager.initialize(config)

# Get wiki data
genres = await manager.get_genres()
emotional_tags = await manager.get_meta_tags("emotional")
vocal_techniques = await manager.get_techniques("vocal_style")

# Get source URLs for attribution
genre_sources = manager.get_source_urls("genres")

# Refresh data
result = await manager.refresh_data()
print(f"Downloaded {result.pages_downloaded} pages")

# Cleanup
await manager.cleanup()
```

## Local Storage Structure

```
data/wiki/
├── genres/           # Genre resource pages
├── meta_tags/        # Meta tag resource pages  
├── techniques/       # Technique tip pages
└── cache/           # Parsed data cache (JSON)
```

## Error Handling

The system implements graceful degradation:

1. **Network failures**: Uses cached local files if available
2. **Parse failures**: Falls back to hardcoded data with logging
3. **Missing files**: Attempts re-download, then uses hardcoded fallbacks
4. **Invalid URLs**: Logs error and skips problematic URLs

## Integration with Main Server

The wiki data system is designed to integrate seamlessly with the existing MCP server:

```python
class EnhancedMusicServer:
    def __init__(self):
        self.wiki_manager = WikiDataManager()
    
    async def initialize(self):
        config = await ConfigurationManager.load_config()
        await self.wiki_manager.initialize(config)
        
        # Perform initial refresh
        if config.enabled:
            await self.wiki_manager.refresh_data()
    
    async def generate_persona(self, character_traits):
        # Use wiki data for enhanced generation
        genres = await self.wiki_manager.get_genres()
        meta_tags = await self.wiki_manager.get_meta_tags()
        
        # Enhanced persona generation logic here...
```

## Testing

Unit tests are provided in `tests/unit/test_wiki_infrastructure.py` covering:
- Configuration validation
- Data model serialization
- Manager initialization
- Error handling scenarios
- Disabled system behavior

Run tests with:
```bash
python -m pytest tests/unit/test_wiki_infrastructure.py -v
```

## Next Steps

This infrastructure provides the foundation for:
1. HTML content parsing (Task 2)
2. Enhanced genre mapping (Task 4)
3. Source attribution (Task 5)
4. Advanced meta tag strategies (Task 6)

The system is designed to be extensible - new wiki page types can be added by updating the configuration and implementing corresponding parsers.