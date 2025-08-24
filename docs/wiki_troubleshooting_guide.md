# Wiki Data Integration Troubleshooting Guide

## Overview

This guide helps diagnose and resolve common issues with the Wiki Data Integration system. Issues are organized by category with step-by-step solutions.

## Quick Diagnostics

### System Health Check

Run this diagnostic script to check overall system health:

```python
from wiki_data_system import WikiDataManager, ConfigurationManager
from wiki_config_validator import validate_config_full
import asyncio

async def health_check():
    try:
        # Load configuration
        config = await ConfigurationManager.load_config()
        print("✓ Configuration loaded successfully")
        
        # Validate configuration
        result = await validate_config_full(config)
        if result.is_valid:
            print("✓ Configuration is valid")
        else:
            print("✗ Configuration has errors:")
            for error in result.errors:
                print(f"  - {error}")
        
        # Test system initialization
        manager = WikiDataManager()
        await manager.initialize(config)
        print("✓ System initialized successfully")
        
        # Test data access
        genres = await manager.get_genres()
        meta_tags = await manager.get_meta_tags()
        techniques = await manager.get_techniques()
        
        print(f"✓ Data access working: {len(genres)} genres, {len(meta_tags)} meta tags, {len(techniques)} techniques")
        
        await manager.cleanup()
        
    except Exception as e:
        print(f"✗ Health check failed: {e}")

# Run health check
asyncio.run(health_check())
```

## Configuration Issues

### Error: "Configuration file not found"

**Symptoms:**
- System fails to start
- Error message about missing config file

**Diagnosis:**
```python
import os
from pathlib import Path

config_path = "config/wiki_config.json"
if not Path(config_path).exists():
    print(f"Configuration file missing: {config_path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in config/: {list(Path('config').glob('*')) if Path('config').exists() else 'config directory missing'}")
```

**Solutions:**

1. **Create default configuration:**
```bash
mkdir -p config
cat > config/wiki_config.json << 'EOF'
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
    "https://sunoaiwiki.com/tips/2024-05-02-how-to-enhance-song-production-using-suno-ai/"
  ],
  "request_timeout": 30,
  "max_retries": 3,
  "retry_delay": 1.0
}
EOF
```

2. **Use programmatic configuration:**
```python
from wiki_data_system import WikiConfig, ConfigurationManager

# Create default configuration
config = WikiConfig()
await ConfigurationManager.save_config(config, "config/wiki_config.json")
```

### Error: "Invalid configuration"

**Symptoms:**
- System fails to initialize
- Validation errors on startup

**Diagnosis:**
```python
from wiki_data_system import ConfigurationManager
from wiki_config_validator import validate_config_full

config = await ConfigurationManager.load_config()
result = await validate_config_full(config)

print(f"Valid: {result.is_valid}")
print(f"Errors: {result.errors}")
print(f"Warnings: {result.warnings}")
```

**Solutions:**

1. **Fix validation errors:**
```python
# Common fixes
config_fixes = {
    "refresh_interval_hours must be at least 1": lambda c: setattr(c, 'refresh_interval_hours', 24),
    "request_timeout must be at least 1": lambda c: setattr(c, 'request_timeout', 30),
    "local_storage_path cannot be empty": lambda c: setattr(c, 'local_storage_path', './data/wiki'),
}

for error in result.errors:
    if error in config_fixes:
        config_fixes[error](config)
        
await ConfigurationManager.save_config(config, "config/wiki_config.json")
```

2. **Reset to defaults:**
```python
from wiki_data_system import WikiConfig

# Create fresh configuration with defaults
config = WikiConfig()
await ConfigurationManager.save_config(config, "config/wiki_config.json")
```

## Storage Issues

### Error: "No write permission for storage directory"

**Symptoms:**
- System fails to initialize
- Cannot create or write to storage directory

**Diagnosis:**
```python
from pathlib import Path
import os

storage_path = Path("./data/wiki")
print(f"Storage path: {storage_path.absolute()}")
print(f"Exists: {storage_path.exists()}")
print(f"Is directory: {storage_path.is_dir() if storage_path.exists() else 'N/A'}")
print(f"Writable: {os.access(storage_path.parent, os.W_OK)}")
```

**Solutions:**

1. **Fix permissions:**
```bash
# Create directory with proper permissions
mkdir -p ./data/wiki
chmod 755 ./data/wiki

# Fix parent directory permissions
chmod 755 ./data
```

2. **Use different storage location:**
```json
{
  "local_storage_path": "/tmp/wiki-data"
}
```

3. **Use user home directory:**
```json
{
  "local_storage_path": "~/wiki-data"
}
```

### Error: "Insufficient disk space"

**Symptoms:**
- Downloads fail
- System warns about low disk space

**Diagnosis:**
```bash
# Check disk space
df -h ./data/wiki

# Check storage directory size
du -sh ./data/wiki
```

**Solutions:**

1. **Clean cache files:**
```python
from pathlib import Path
import shutil

cache_dir = Path("./data/wiki/cache")
if cache_dir.exists():
    shutil.rmtree(cache_dir)
    print("Cache cleared")
```

2. **Move to larger storage:**
```bash
# Move to larger partition
mv ./data/wiki /var/lib/wiki-data
```

```json
{
  "local_storage_path": "/var/lib/wiki-data"
}
```

3. **Reduce cached data:**
```json
{
  "refresh_interval_hours": 168,
  "genre_pages": ["https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"]
}
```

## Network Issues

### Error: "URL not accessible"

**Symptoms:**
- Downloads fail
- Validation reports inaccessible URLs

**Diagnosis:**
```bash
# Test URL accessibility
curl -I "https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"

# Check DNS resolution
nslookup sunoaiwiki.com

# Test with different tool
wget --spider "https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"
```

**Solutions:**

1. **Check network connectivity:**
```bash
# Test basic connectivity
ping sunoaiwiki.com

# Test HTTPS connectivity
curl -I https://sunoaiwiki.com
```

2. **Update URLs:**
```python
from wiki_config_validator import check_urls_accessibility

# Test current URLs
urls = [
    "https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/",
    "https://sunoaiwiki.com/resources/2024-05-13-list-of-metatags/"
]

results = await check_urls_accessibility(urls)
for url, accessible in results.items():
    print(f"{url}: {'✓' if accessible else '✗'}")
```

3. **Use fallback mode:**
```json
{
  "enabled": false,
  "fallback_to_hardcoded": true
}
```

### Error: "Request timeout"

**Symptoms:**
- Downloads take too long and fail
- Timeout errors in logs

**Diagnosis:**
```python
import time
import aiohttp

async def test_download_speed():
    url = "https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"
    
    start_time = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.read()
                download_time = time.time() - start_time
                print(f"Downloaded {len(content)} bytes in {download_time:.2f} seconds")
    except Exception as e:
        print(f"Download failed: {e}")
```

**Solutions:**

1. **Increase timeout:**
```json
{
  "request_timeout": 60,
  "max_retries": 5,
  "retry_delay": 3.0
}
```

2. **Test with different timeout values:**
```python
from wiki_config_validator import WikiConfigValidator

# Test with longer timeout
validator = WikiConfigValidator(timeout=60)
result = await validator.validate_config(config, check_urls=True)
```

## Data Issues

### Error: "No data available"

**Symptoms:**
- Empty results from get_genres(), get_meta_tags(), etc.
- System reports no cached data

**Diagnosis:**
```python
from pathlib import Path

storage_path = Path("./data/wiki")
print(f"Storage directory exists: {storage_path.exists()}")

if storage_path.exists():
    for subdir in ['genres', 'meta_tags', 'techniques', 'cache']:
        subpath = storage_path / subdir
        if subpath.exists():
            files = list(subpath.glob('*'))
            print(f"{subdir}: {len(files)} files")
        else:
            print(f"{subdir}: directory missing")
```

**Solutions:**

1. **Force data refresh:**
```python
from wiki_data_system import WikiDataManager

manager = WikiDataManager()
await manager.initialize(config)

# Force refresh
result = await manager.refresh_data(force=True)
print(f"Downloaded {result.pages_downloaded} pages")

await manager.cleanup()
```

2. **Check fallback data:**
```python
# Test with fallback enabled
config.fallback_to_hardcoded = True
config.enabled = False

manager = WikiDataManager()
await manager.initialize(config)

genres = await manager.get_genres()
print(f"Fallback genres: {len(genres)}")
```

3. **Manual download test:**
```python
from wiki_downloader import WikiDownloader
from wiki_cache_manager import WikiCacheManager

cache_manager = WikiCacheManager("./data/wiki")
await cache_manager.initialize()

downloader = WikiDownloader(cache_manager)
result = await downloader.download_page(
    "https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/",
    "genres/test.html"
)

print(f"Download result: {result}")
```

### Error: "Parse errors in wiki content"

**Symptoms:**
- Data downloaded but not parsed correctly
- Empty or malformed data structures

**Diagnosis:**
```python
from wiki_content_parser import ContentParser
from pathlib import Path

# Test parser with downloaded content
parser = ContentParser()
content_file = Path("./data/wiki/genres/2024-05-03-list-of-music-genres-and-styles.html")

if content_file.exists():
    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        genres = parser.parse_genre_page(content)
        print(f"Parsed {len(genres)} genres")
    except Exception as e:
        print(f"Parse error: {e}")
else:
    print("Content file not found")
```

**Solutions:**

1. **Re-download content:**
```python
# Clear cache and re-download
import shutil
from pathlib import Path

cache_dir = Path("./data/wiki/cache")
if cache_dir.exists():
    shutil.rmtree(cache_dir)

# Force refresh
result = await manager.refresh_data(force=True)
```

2. **Check content format:**
```python
# Inspect downloaded content
with open("./data/wiki/genres/2024-05-03-list-of-music-genres-and-styles.html", 'r') as f:
    content = f.read()

print(f"Content length: {len(content)}")
print(f"Contains expected markers: {'genre' in content.lower()}")
```

## Performance Issues

### Issue: Slow startup

**Symptoms:**
- System takes long time to initialize
- Delays in first data access

**Diagnosis:**
```python
import time
from wiki_data_system import WikiDataManager

start_time = time.time()

manager = WikiDataManager()
await manager.initialize(config)

init_time = time.time() - start_time
print(f"Initialization took {init_time:.2f} seconds")

# Test data access speed
start_time = time.time()
genres = await manager.get_genres()
access_time = time.time() - start_time
print(f"Data access took {access_time:.2f} seconds")
```

**Solutions:**

1. **Reduce refresh frequency:**
```json
{
  "refresh_interval_hours": 168
}
```

2. **Limit configured pages:**
```json
{
  "genre_pages": ["https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"],
  "meta_tag_pages": ["https://sunoaiwiki.com/resources/2024-05-13-list-of-metatags/"],
  "tip_pages": [
    "https://sunoaiwiki.com/tips/2024-05-02-how-to-enhance-song-production-using-suno-ai/"
  ]
}
```

3. **Use cached data:**
```python
# Skip refresh on startup
manager = WikiDataManager()
await manager.initialize(config)

# Don't force refresh
genres = await manager.get_genres()  # Uses cached data
```

### Issue: High memory usage

**Symptoms:**
- System uses excessive memory
- Out of memory errors

**Diagnosis:**
```python
import psutil
import os

process = psutil.Process(os.getpid())
memory_info = process.memory_info()
print(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")

# Check data sizes
genres = await manager.get_genres()
meta_tags = await manager.get_meta_tags()
techniques = await manager.get_techniques()

print(f"Data loaded: {len(genres)} genres, {len(meta_tags)} meta tags, {len(techniques)} techniques")
```

**Solutions:**

1. **Reduce data volume:**
```json
{
  "genre_pages": ["https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"],
  "tip_pages": [
    "https://sunoaiwiki.com/tips/2024-05-02-how-to-enhance-song-production-using-suno-ai/",
    "https://sunoaiwiki.com/tips/2024-05-04-how-to-structure-prompts-for-suno-ai/"
  ]
}
```

2. **Clear cache periodically:**
```python
# Clear data cache
manager._genres.clear()
manager._meta_tags.clear()
manager._techniques.clear()
manager._cache_valid = False
```

## Integration Issues

### Error: "System not integrated with main server"

**Symptoms:**
- Wiki data not used in music generation
- Hardcoded data still being used

**Diagnosis:**
```python
# Check if enhanced genre mapper is being used
from enhanced_genre_mapper import EnhancedGenreMapper

mapper = EnhancedGenreMapper()
await mapper.initialize(manager)

# Test genre mapping
traits = ["melancholic", "introspective"]
matches = await mapper.map_traits_to_genres(traits)
print(f"Genre matches: {[m.genre.name for m in matches]}")
```

**Solutions:**

1. **Verify server integration:**
```python
# Check server initialization
from server import EnhancedMusicServer

server = EnhancedMusicServer()
await server.initialize()

# Verify wiki manager is initialized
if hasattr(server, 'wiki_manager') and server.wiki_manager.initialized:
    print("✓ Wiki manager integrated")
else:
    print("✗ Wiki manager not integrated")
```

2. **Update server code:**
```python
# Ensure server uses wiki data
class EnhancedMusicServer:
    async def initialize(self):
        # Initialize wiki manager
        config = await ConfigurationManager.load_config()
        self.wiki_manager = WikiDataManager()
        await self.wiki_manager.initialize(config)
        
        # Initialize enhanced components
        self.genre_mapper = EnhancedGenreMapper()
        await self.genre_mapper.initialize(self.wiki_manager)
```

## Logging and Monitoring

### Enable Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('wiki_data_system')
logger.setLevel(logging.DEBUG)

# Test with debug logging
manager = WikiDataManager()
await manager.initialize(config)
```

### Monitor System Health

```python
async def monitor_system():
    while True:
        try:
            # Check data freshness
            if manager._should_refresh():
                print("Data refresh needed")
                result = await manager.refresh_data()
                print(f"Refresh result: {result.success}")
            
            # Check data availability
            genres = await manager.get_genres()
            print(f"Available data: {len(genres)} genres")
            
            await asyncio.sleep(3600)  # Check every hour
            
        except Exception as e:
            print(f"Monitor error: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes on error
```

## Emergency Procedures

### Complete System Reset

```bash
#!/bin/bash
# Emergency reset script

echo "Resetting wiki data system..."

# Stop any running processes
pkill -f "wiki_data_system"

# Remove all cached data
rm -rf ./data/wiki

# Reset configuration to defaults
cat > config/wiki_config.json << 'EOF'
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
    "https://sunoaiwiki.com/tips/2024-05-02-how-to-enhance-song-production-using-suno-ai/"
  ],
  "request_timeout": 30,
  "max_retries": 3,
  "retry_delay": 1.0
}
EOF

echo "System reset complete"
```

### Fallback Mode

```python
# Emergency fallback configuration
emergency_config = {
    "enabled": False,
    "fallback_to_hardcoded": True,
    "local_storage_path": "./data/wiki"
}

with open("config/wiki_config.json", "w") as f:
    json.dump(emergency_config, f, indent=2)

print("System switched to fallback mode")
```

## Getting Help

### Collect Diagnostic Information

```python
async def collect_diagnostics():
    """Collect system diagnostic information"""
    import platform
    import sys
    from pathlib import Path
    
    diagnostics = {
        "system": {
            "platform": platform.platform(),
            "python_version": sys.version,
            "working_directory": str(Path.cwd())
        },
        "configuration": {},
        "storage": {},
        "network": {},
        "data": {}
    }
    
    try:
        # Configuration info
        config = await ConfigurationManager.load_config()
        diagnostics["configuration"] = {
            "enabled": config.enabled,
            "storage_path": config.local_storage_path,
            "refresh_interval": config.refresh_interval_hours,
            "url_count": len(config.genre_pages + config.meta_tag_pages + config.tip_pages)
        }
        
        # Storage info
        storage_path = Path(config.local_storage_path)
        diagnostics["storage"] = {
            "exists": storage_path.exists(),
            "writable": storage_path.exists() and os.access(storage_path, os.W_OK),
            "size_mb": sum(f.stat().st_size for f in storage_path.rglob('*') if f.is_file()) / 1024 / 1024 if storage_path.exists() else 0
        }
        
        # Data info
        if storage_path.exists():
            diagnostics["data"] = {
                "genre_files": len(list((storage_path / "genres").glob("*"))) if (storage_path / "genres").exists() else 0,
                "meta_tag_files": len(list((storage_path / "meta_tags").glob("*"))) if (storage_path / "meta_tags").exists() else 0,
                "technique_files": len(list((storage_path / "techniques").glob("*"))) if (storage_path / "techniques").exists() else 0
            }
        
    except Exception as e:
        diagnostics["error"] = str(e)
    
    return diagnostics

# Run diagnostics
diagnostics = await collect_diagnostics()
print(json.dumps(diagnostics, indent=2))
```

### Contact Information

For additional support:
1. Check the GitHub issues for similar problems
2. Review the system logs for detailed error messages
3. Run the diagnostic script and include output in bug reports
4. Provide configuration file (with sensitive URLs redacted)

### Common Support Questions

**Q: Can I use the system without internet access?**
A: Yes, set `"enabled": false` and `"fallback_to_hardcoded": true` in configuration.

**Q: How often should I refresh wiki data?**
A: For production: 168 hours (weekly). For development: 24 hours (daily).

**Q: Can I add custom wiki pages?**
A: Yes, add URLs to the appropriate array in configuration and ensure they follow the expected HTML structure.

**Q: What happens if a wiki page becomes unavailable?**
A: The system will use cached data if available, or fall back to hardcoded data if enabled.

**Q: How much disk space does the system use?**
A: Typically 10-50 MB depending on the number of configured pages and cache size.