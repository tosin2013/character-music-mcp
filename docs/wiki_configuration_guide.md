# Wiki Data Integration Configuration Guide

## Overview

The Wiki Data Integration system uses a comprehensive configuration system to manage data sources, local storage, refresh intervals, and system behavior. This guide covers all configuration options, formats, and provides examples for common scenarios.

## Configuration File Location

The default configuration file is located at:
```
config/wiki_config.json
```

You can specify a custom location when initializing the system:
```python
from wiki_data_system import ConfigurationManager

# Load from custom location
config = await ConfigurationManager.load_config("path/to/custom/config.json")
```

## Complete Configuration Reference

### Basic Settings

#### `enabled` (boolean, default: `true`)
Controls whether wiki data integration is active.
- `true`: System will download and use wiki data
- `false`: System will only use hardcoded fallback data

**Example:**
```json
{
  "enabled": true
}
```

#### `local_storage_path` (string, default: `"./data/wiki"`)
Directory where downloaded wiki pages and cached data are stored.
- Can be relative or absolute path
- Directory will be created if it doesn't exist
- Must have write permissions

**Example:**
```json
{
  "local_storage_path": "/var/lib/suno-wiki-data"
}
```

#### `refresh_interval_hours` (integer, default: `24`)
How often to check for updated wiki content (in hours).
- Minimum: 1 hour
- Recommended: 24-168 hours (1-7 days)
- Set higher for production environments

**Example:**
```json
{
  "refresh_interval_hours": 48
}
```

#### `fallback_to_hardcoded` (boolean, default: `true`)
Whether to use hardcoded data when wiki data is unavailable.
- `true`: Use hardcoded data as fallback (recommended)
- `false`: Fail if wiki data unavailable

**Example:**
```json
{
  "fallback_to_hardcoded": true
}
```

### Data Source URLs

#### `genre_pages` (array of strings)
List of URLs containing music genre information.

**Default:**
```json
{
  "genre_pages": [
    "https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"
  ]
}
```

**Adding additional genre pages:**
```json
{
  "genre_pages": [
    "https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/",
    "https://sunoaiwiki.com/resources/2024-06-15-electronic-music-subgenres/",
    "https://sunoaiwiki.com/resources/2024-07-20-world-music-genres/"
  ]
}
```

#### `meta_tag_pages` (array of strings)
List of URLs containing Suno AI meta tag information.

**Default:**
```json
{
  "meta_tag_pages": [
    "https://sunoaiwiki.com/resources/2024-05-13-list-of-metatags/"
  ]
}
```

**Adding additional meta tag pages:**
```json
{
  "meta_tag_pages": [
    "https://sunoaiwiki.com/resources/2024-05-13-list-of-metatags/",
    "https://sunoaiwiki.com/resources/2024-08-01-advanced-metatags/",
    "https://sunoaiwiki.com/resources/2024-09-10-experimental-tags/"
  ]
}
```

#### `tip_pages` (array of strings)
List of URLs containing Suno AI tips and techniques.

**Default includes 13 tip pages:**
```json
{
  "tip_pages": [
    "https://sunoaiwiki.com/tips/2024-05-02-how-to-enhance-song-production-using-suno-ai/",
    "https://sunoaiwiki.com/tips/2024-04-16-how-to-make-suno-ai-sing-with-spoken-word/",
    "https://sunoaiwiki.com/tips/2024-05-04-how-to-structure-prompts-for-suno-ai/",
    "https://sunoaiwiki.com/tips/2024-05-04-how-to-use-meta-tags-in-suno-ai-for-song-creation/",
    "https://sunoaiwiki.com/tips/2024-05-07-how-to-get-specific-vocal-styles-in-suno-ai/",
    "https://sunoaiwiki.com/tips/2024-05-08-how-to-bypass-explicit-lyric-restrictions/",
    "https://sunoaiwiki.com/tips/2024-05-09-how-to-end-a-song-naturally/",
    "https://sunoaiwiki.com/tips/2024-05-18-how-to-optimize-prompts-in-suno-ai-with-letter-case/",
    "https://sunoaiwiki.com/tips/2024-05-22-how-to-prompt-suno-ai-to-use-animal-sounds-and-noises/",
    "https://sunoaiwiki.com/tips/2024-05-22-how-to-solve-suno-ai-sampling-detection-issues/",
    "https://sunoaiwiki.com/tips/2024-05-25-how-to-handle-producer-tags-in-suno-ai/",
    "https://sunoaiwiki.com/tips/2024-07-08-how-to-create-better-lyrics-for-suno/",
    "https://sunoaiwiki.com/tips/2024-07-08-improve-suno-hiphop-rap-trap/"
  ]
}
```

### HTTP Client Settings

#### `request_timeout` (integer, default: `30`)
Timeout for HTTP requests in seconds.
- Minimum: 1 second
- Recommended: 30-60 seconds
- Increase for slow connections

**Example:**
```json
{
  "request_timeout": 45
}
```

#### `max_retries` (integer, default: `3`)
Maximum number of retry attempts for failed downloads.
- Minimum: 0 (no retries)
- Recommended: 3-5 retries
- Higher values increase reliability but slow down failures

**Example:**
```json
{
  "max_retries": 5
}
```

#### `retry_delay` (float, default: `1.0`)
Delay between retry attempts in seconds.
- Minimum: 0.0 seconds
- Recommended: 1.0-5.0 seconds
- Higher values reduce server load

**Example:**
```json
{
  "retry_delay": 2.5
}
```

## Complete Configuration Example

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
    "https://sunoaiwiki.com/tips/2024-05-04-how-to-structure-prompts-for-suno-ai/",
    "https://sunoaiwiki.com/tips/2024-05-04-how-to-use-meta-tags-in-suno-ai-for-song-creation/",
    "https://sunoaiwiki.com/tips/2024-05-07-how-to-get-specific-vocal-styles-in-suno-ai/",
    "https://sunoaiwiki.com/tips/2024-05-08-how-to-bypass-explicit-lyric-restrictions/",
    "https://sunoaiwiki.com/tips/2024-05-09-how-to-end-a-song-naturally/",
    "https://sunoaiwiki.com/tips/2024-05-18-how-to-optimize-prompts-in-suno-ai-with-letter-case/",
    "https://sunoaiwiki.com/tips/2024-05-22-how-to-prompt-suno-ai-to-use-animal-sounds-and-noises/",
    "https://sunoaiwiki.com/tips/2024-05-22-how-to-solve-suno-ai-sampling-detection-issues/",
    "https://sunoaiwiki.com/tips/2024-05-25-how-to-handle-producer-tags-in-suno-ai/",
    "https://sunoaiwiki.com/tips/2024-07-08-how-to-create-better-lyrics-for-suno/",
    "https://sunoaiwiki.com/tips/2024-07-08-improve-suno-hiphop-rap-trap/"
  ],
  "request_timeout": 30,
  "max_retries": 3,
  "retry_delay": 1.0
}
```

## Adding New Wiki Pages

### Step 1: Identify Page Type

Determine which category your new page belongs to:
- **Genre pages**: Contain lists of music genres and their descriptions
- **Meta tag pages**: Contain Suno AI meta tags and usage information
- **Tip pages**: Contain techniques, tips, and best practices

### Step 2: Add URL to Configuration

Add the URL to the appropriate array in your configuration file:

**Adding a new genre page:**
```json
{
  "genre_pages": [
    "https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/",
    "https://sunoaiwiki.com/resources/2024-10-15-new-genre-collection/"
  ]
}
```

**Adding a new tip page:**
```json
{
  "tip_pages": [
    "https://sunoaiwiki.com/tips/2024-05-02-how-to-enhance-song-production-using-suno-ai/",
    "https://sunoaiwiki.com/tips/2024-10-20-advanced-vocal-techniques/"
  ]
}
```

### Step 3: Validate Configuration

Use the configuration validator to ensure your new URLs are valid:

```python
from wiki_config_validator import validate_config_full
from wiki_data_system import ConfigurationManager

# Load updated configuration
config = await ConfigurationManager.load_config("config/wiki_config.json")

# Validate with network checks
result = await validate_config_full(config)

if result.is_valid:
    print("Configuration is valid!")
else:
    print("Configuration errors:")
    for error in result.errors:
        print(f"  - {error}")
```

### Step 4: Test the Integration

After adding new pages, test that they're being downloaded and parsed correctly:

```python
from wiki_data_system import WikiDataManager

# Initialize with updated configuration
manager = WikiDataManager()
await manager.initialize(config)

# Force refresh to download new pages
result = await manager.refresh_data(force=True)

print(f"Downloaded {result.pages_downloaded} pages")
print(f"Failed {result.pages_failed} pages")

if result.errors:
    print("Errors:")
    for error in result.errors:
        print(f"  - {error}")
```

## Configuration Environments

### Development Environment

```json
{
  "enabled": true,
  "local_storage_path": "./dev-data/wiki",
  "refresh_interval_hours": 1,
  "fallback_to_hardcoded": true,
  "request_timeout": 10,
  "max_retries": 1,
  "retry_delay": 0.5
}
```

### Production Environment

```json
{
  "enabled": true,
  "local_storage_path": "/var/lib/suno-wiki-data",
  "refresh_interval_hours": 168,
  "fallback_to_hardcoded": true,
  "request_timeout": 60,
  "max_retries": 5,
  "retry_delay": 2.0
}
```

### Offline/Testing Environment

```json
{
  "enabled": false,
  "fallback_to_hardcoded": true
}
```

## Dynamic Configuration Management

The system supports runtime configuration updates without restart:

```python
from dynamic_config_manager import DynamicConfigManager

# Initialize dynamic manager
manager = DynamicConfigManager("config/wiki_config.json")
await manager.initialize()

# Start watching for file changes
manager.start_watching()

# Add new URLs at runtime
result = await manager.add_urls(
    "tip_pages", 
    ["https://sunoaiwiki.com/tips/2024-11-01-new-technique/"]
)

# Update settings at runtime
result = await manager.update_settings(
    refresh_interval_hours=48,
    request_timeout=45
)

# Stop watching when done
manager.stop_watching()
```

## Configuration Validation

### Automatic Validation

The system automatically validates configuration on startup:

```python
from wiki_data_system import WikiDataManager

manager = WikiDataManager()

try:
    await manager.initialize(config)
    print("Configuration is valid!")
except ValueError as e:
    print(f"Configuration error: {e}")
```

### Manual Validation

You can validate configuration manually:

```python
from wiki_config_validator import WikiConfigValidator

validator = WikiConfigValidator()

# Quick validation (no network checks)
result = await validator.validate_config(config, check_urls=False)

# Full validation (includes network checks)
result = await validator.validate_config(config, check_urls=True)

print(f"Valid: {result.is_valid}")
print(f"Errors: {result.errors}")
print(f"Warnings: {result.warnings}")
print(f"URL checks: {result.url_checks}")
print(f"Storage info: {result.storage_info}")
```

### Validation Results

The validator provides detailed information:

- **Errors**: Critical issues that prevent system operation
- **Warnings**: Non-critical issues that should be addressed
- **URL checks**: Accessibility status for each configured URL
- **Storage info**: Disk space and permission information

## Troubleshooting

### Common Configuration Issues

#### Issue: "local_storage_path cannot be empty"
**Solution:** Ensure `local_storage_path` is set to a valid directory path.

```json
{
  "local_storage_path": "./data/wiki"
}
```

#### Issue: "No write permission for storage directory"
**Solution:** Ensure the application has write permissions to the storage directory.

```bash
# Fix permissions
chmod 755 ./data/wiki

# Or use a different directory
mkdir -p /tmp/wiki-data
chmod 755 /tmp/wiki-data
```

#### Issue: "Invalid URL format"
**Solution:** Ensure all URLs are properly formatted with http:// or https://.

```json
{
  "genre_pages": [
    "https://sunoaiwiki.com/resources/valid-url/"
  ]
}
```

#### Issue: "URL not accessible"
**Solution:** Check network connectivity and URL validity.

```bash
# Test URL accessibility
curl -I "https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"
```

### Storage Issues

#### Issue: "Insufficient disk space"
**Solution:** Free up disk space or change storage location.

```bash
# Check disk space
df -h ./data/wiki

# Clean old cache files
rm -rf ./data/wiki/cache/*
```

#### Issue: "Cannot create storage directory"
**Solution:** Check parent directory permissions or use absolute path.

```json
{
  "local_storage_path": "/home/user/wiki-data"
}
```

### Network Issues

#### Issue: Download timeouts
**Solution:** Increase timeout and retry settings.

```json
{
  "request_timeout": 60,
  "max_retries": 5,
  "retry_delay": 3.0
}
```

#### Issue: Frequent download failures
**Solution:** Check network connectivity and consider using fallback mode.

```json
{
  "fallback_to_hardcoded": true,
  "refresh_interval_hours": 168
}
```

### Performance Issues

#### Issue: Slow startup
**Solution:** Reduce refresh frequency or disable URL validation.

```json
{
  "refresh_interval_hours": 168
}
```

#### Issue: High memory usage
**Solution:** Reduce number of configured pages or increase refresh interval.

```json
{
  "refresh_interval_hours": 72,
  "genre_pages": ["https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"]
}
```

## Configuration Best Practices

### Security
- Use HTTPS URLs only
- Validate URLs before adding to configuration
- Set appropriate file permissions on configuration files
- Use absolute paths for production deployments

### Performance
- Set reasonable refresh intervals (24-168 hours)
- Limit number of configured pages
- Use appropriate timeout values
- Enable fallback to hardcoded data

### Reliability
- Always enable fallback to hardcoded data
- Set retry limits and delays
- Monitor disk space usage
- Validate configuration changes before deployment

### Maintenance
- Regularly review and update configured URLs
- Monitor download success rates
- Clean up old cache files periodically
- Test configuration changes in development first