# Character Music MCP Server Maintenance Procedures

## Overview

This document outlines maintenance procedures for the Character-Driven Music Generation MCP Server, focusing on wiki data management, performance optimization, and system health monitoring.

## Regular Maintenance Tasks

### Daily Tasks

#### 1. System Health Check

**Frequency**: Daily  
**Automation**: Recommended

```bash
# Check server status
systemctl status character-music-mcp

# Check disk space for wiki cache
du -sh ./data/wiki/

# Review recent logs
tail -n 100 /var/log/character-music-mcp.log
```

**Expected Results**:
- Server status: Active (running)
- Wiki cache size: < 500MB typically
- No ERROR level log entries

#### 2. Wiki Data Freshness Check

**Frequency**: Daily  
**Automation**: Built-in (configurable)

The system automatically checks wiki data freshness based on `refresh_interval_hours` setting. Monitor logs for:

```
INFO - Checking wiki data freshness...
INFO - Wiki data is current (last updated: YYYY-MM-DD)
```

Or:

```
INFO - Wiki data refresh needed, downloading...
INFO - Wiki data updated successfully
```

### Weekly Tasks

#### 1. Performance Review

**Frequency**: Weekly  
**Automation**: Recommended

```bash
# Check response times
grep "processing_time" /var/log/character-music-mcp.log | tail -20

# Monitor memory usage
ps aux | grep server.py

# Check wiki cache integrity
python -c "
import json
from pathlib import Path
cache_dir = Path('./data/wiki')
for file in cache_dir.rglob('*.json'):
    try:
        with open(file) as f:
            json.load(f)
        print(f'✓ {file}')
    except Exception as e:
        print(f'✗ {file}: {e}')
"
```

#### 2. Log Rotation and Cleanup

**Frequency**: Weekly  
**Automation**: Recommended

```bash
# Rotate logs (if not using systemd/logrotate)
mv /var/log/character-music-mcp.log /var/log/character-music-mcp.log.$(date +%Y%m%d)
touch /var/log/character-music-mcp.log
systemctl restart character-music-mcp

# Clean old wiki cache files (optional)
find ./data/wiki -name "*.html" -mtime +30 -delete
find ./data/wiki -name "*.json" -mtime +30 -delete
```

### Monthly Tasks

#### 1. Comprehensive System Review

**Frequency**: Monthly  
**Manual Task**

1. **Performance Analysis**
   - Review average response times
   - Analyze memory usage patterns
   - Check disk space trends

2. **Error Analysis**
   - Review error logs for patterns
   - Identify recurring issues
   - Plan fixes for common problems

3. **Wiki Data Quality Check**
   - Verify all configured URLs are accessible
   - Check for new wiki pages to add
   - Review genre and meta tag coverage

#### 2. Dependency Updates

**Frequency**: Monthly  
**Manual Task**

```bash
# Check for package updates
pip list --outdated

# Update packages (test in staging first)
pip install --upgrade fastmcp pydantic beautifulsoup4 aiohttp

# Test functionality after updates
python -c "
import server
print('Server imports successfully')
"
```

## Wiki Data Management

### Manual Wiki Data Refresh

Force a wiki data refresh when needed:

```python
# Connect to running server and trigger refresh
import asyncio
from wiki_data_system import WikiDataManager
from wiki_data_models import WikiConfig

async def force_refresh():
    manager = WikiDataManager()
    config = WikiConfig()
    await manager.initialize(config)
    result = await manager.refresh_data(force=True)
    print(f"Refresh result: {result}")

asyncio.run(force_refresh())
```

### Adding New Wiki Pages

1. **Update Configuration**
   
   Edit the `WikiConfig` in `server.py`:

   ```python
   config = WikiConfig(
       # ... existing config ...
       tip_pages=[
           # ... existing pages ...
           "https://sunoaiwiki.com/tips/new-tip-page/",
       ]
   )
   ```

2. **Test New Page**
   
   ```bash
   # Test URL accessibility
   curl -I https://sunoaiwiki.com/tips/new-tip-page/
   
   # Verify page content
   curl -s https://sunoaiwiki.com/tips/new-tip-page/ | head -20
   ```

3. **Restart Server**
   
   ```bash
   systemctl restart character-music-mcp
   ```

4. **Verify Integration**
   
   Check logs for successful download and parsing of the new page.

### Wiki Cache Management

#### Cache Size Monitoring

```bash
# Monitor cache size
du -sh ./data/wiki/
du -h ./data/wiki/* | sort -hr

# Check individual category sizes
du -sh ./data/wiki/genres/
du -sh ./data/wiki/meta_tags/
du -sh ./data/wiki/techniques/
```

#### Cache Cleanup

```bash
# Remove old cache files (older than 60 days)
find ./data/wiki -type f -mtime +60 -delete

# Remove empty directories
find ./data/wiki -type d -empty -delete

# Rebuild cache index
python -c "
from wiki_cache_manager import WikiCacheManager
cache_manager = WikiCacheManager('./data/wiki')
cache_manager.rebuild_index()
print('Cache index rebuilt')
"
```

## Performance Optimization

### Memory Management

#### Monitor Memory Usage

```bash
# Check current memory usage
ps aux | grep server.py | awk '{print $4, $6}'

# Monitor memory over time
while true; do
    echo "$(date): $(ps aux | grep server.py | awk '{print $6}')KB"
    sleep 300  # Check every 5 minutes
done
```

#### Memory Optimization

1. **Adjust Cache Settings**
   
   Modify cache size limits in configuration:

   ```python
   # In enhanced_cache_manager.py
   cache_manager = EnhancedCacheManager(
       max_cache_size_mb=256,  # Reduce if memory constrained
       cleanup_threshold=0.8
   )
   ```

2. **Restart Server Periodically**
   
   For high-usage deployments, consider scheduled restarts:

   ```bash
   # Add to crontab for weekly restart
   0 2 * * 0 systemctl restart character-music-mcp
   ```

### Response Time Optimization

#### Monitor Response Times

```bash
# Extract processing times from logs
grep "processing_time" /var/log/character-music-mcp.log | \
awk '{print $NF}' | \
sort -n | \
tail -20
```

#### Optimization Strategies

1. **Preload Common Data**
   
   Implement cache warming on startup:

   ```python
   # Add to server initialization
   async def warm_cache():
       await wiki_data_manager.get_genres()
       await wiki_data_manager.get_meta_tags()
       print("Cache warmed successfully")
   ```

2. **Optimize Wiki Queries**
   
   Review and optimize frequent wiki data queries.

## Monitoring and Alerting

### Key Metrics to Monitor

1. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk space
   - Network connectivity

2. **Application Metrics**
   - Response times
   - Error rates
   - Wiki data freshness
   - Cache hit rates

3. **Business Metrics**
   - Request volume
   - Tool usage patterns
   - Generation success rates

### Alerting Setup

#### Basic Shell Script Monitoring

```bash
#!/bin/bash
# monitor.sh - Basic monitoring script

# Check if server is running
if ! pgrep -f "server.py" > /dev/null; then
    echo "ALERT: Server not running" | mail -s "MCP Server Down" admin@example.com
fi

# Check disk space
DISK_USAGE=$(df ./data/wiki | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "ALERT: Wiki cache disk usage at ${DISK_USAGE}%" | mail -s "High Disk Usage" admin@example.com
fi

# Check wiki data age
LAST_UPDATE=$(stat -c %Y ./data/wiki/cache_index.json 2>/dev/null || echo 0)
CURRENT_TIME=$(date +%s)
AGE_HOURS=$(( (CURRENT_TIME - LAST_UPDATE) / 3600 ))

if [ $AGE_HOURS -gt 48 ]; then
    echo "ALERT: Wiki data not updated for ${AGE_HOURS} hours" | mail -s "Stale Wiki Data" admin@example.com
fi
```

#### Cron Job Setup

```bash
# Add to crontab
*/15 * * * * /path/to/monitor.sh
```

### Log Analysis

#### Important Log Patterns

Monitor for these patterns:

```bash
# Successful operations
grep "initialized successfully" /var/log/character-music-mcp.log

# Errors
grep "ERROR" /var/log/character-music-mcp.log

# Wiki refresh events
grep "Wiki data" /var/log/character-music-mcp.log

# Performance issues
grep "processing_time.*[5-9]\." /var/log/character-music-mcp.log  # >5 second responses
```

## Backup and Recovery

### Wiki Data Backup

```bash
# Create backup
tar -czf wiki-backup-$(date +%Y%m%d).tar.gz ./data/wiki/

# Restore from backup
tar -xzf wiki-backup-YYYYMMDD.tar.gz
```

### Configuration Backup

```bash
# Backup server configuration
cp server.py server.py.backup.$(date +%Y%m%d)
cp -r config/ config.backup.$(date +%Y%m%d)/
```

### Recovery Procedures

1. **Server Crash Recovery**
   
   ```bash
   # Check logs for crash cause
   tail -100 /var/log/character-music-mcp.log
   
   # Restart server
   systemctl restart character-music-mcp
   
   # Verify functionality
   systemctl status character-music-mcp
   ```

2. **Wiki Data Corruption Recovery**
   
   ```bash
   # Remove corrupted cache
   rm -rf ./data/wiki/*
   
   # Restart server (will re-download)
   systemctl restart character-music-mcp
   
   # Monitor re-download progress
   tail -f /var/log/character-music-mcp.log
   ```

## Troubleshooting Common Issues

### Wiki Download Failures

**Symptoms**: `WARNING - Failed to download wiki page`

**Solutions**:
1. Check internet connectivity
2. Verify sunoaiwiki.com accessibility
3. Check firewall/proxy settings
4. Increase timeout settings if needed

### High Memory Usage

**Symptoms**: Server becomes slow or unresponsive

**Solutions**:
1. Restart the server
2. Reduce cache size limits
3. Implement more aggressive cache cleanup
4. Consider server hardware upgrade

### Slow Response Times

**Symptoms**: Generation tools take >10 seconds

**Solutions**:
1. Check system resources
2. Optimize wiki data queries
3. Implement cache warming
4. Review and optimize character analysis algorithms

## Maintenance Schedule Template

### Daily (Automated)
- [ ] System health check
- [ ] Wiki data freshness verification
- [ ] Basic log review

### Weekly (Semi-automated)
- [ ] Performance metrics review
- [ ] Log rotation and cleanup
- [ ] Cache size monitoring

### Monthly (Manual)
- [ ] Comprehensive system review
- [ ] Dependency updates
- [ ] Wiki configuration review
- [ ] Performance optimization review

### Quarterly (Manual)
- [ ] Full system backup
- [ ] Security review
- [ ] Capacity planning
- [ ] Documentation updates

## Contact and Escalation

For issues beyond routine maintenance:

1. **Performance Issues**: Review system resources and optimization guides
2. **Data Issues**: Check wiki source availability and data integrity
3. **Integration Issues**: Review MCP client configuration and compatibility
4. **Critical Failures**: Follow recovery procedures and consider rollback if needed

## Documentation Updates

Keep this maintenance guide updated with:
- New monitoring procedures
- Lessons learned from incidents
- Performance optimization discoveries
- Configuration changes and their impacts