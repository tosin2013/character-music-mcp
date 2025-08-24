# Character Music MCP Server Deployment Guide

## Overview

This guide covers the deployment and setup of the Character-Driven Music Generation MCP Server with integrated Suno AI Wiki data support.

## Prerequisites

### System Requirements

- Python 3.8 or higher
- Internet connection for wiki data downloads
- Minimum 1GB free disk space for wiki data cache
- 4GB RAM recommended for optimal performance

### Dependencies

Install required Python packages:

```bash
pip install fastmcp pydantic beautifulsoup4 aiohttp asyncio
```

Or using the project's requirements:

```bash
pip install -r requirements.txt
```

## Deployment Steps

### 1. Environment Setup

1. Clone or download the project files
2. Ensure all Python dependencies are installed
3. Verify network access to sunoaiwiki.com

### 2. Configuration

#### Wiki Data Configuration

The server uses a default configuration that can be customized by modifying the `WikiConfig` in `server.py`:

```python
config = WikiConfig(
    enabled=True,
    local_storage_path="./data/wiki",
    refresh_interval_hours=24,
    fallback_to_hardcoded=True,
    genre_pages=[
        "https://sunoaiwiki.com/resources/2024-05-03-list-of-music-genres-and-styles/"
    ],
    meta_tag_pages=[
        "https://sunoaiwiki.com/resources/2024-05-13-list-of-metatags/"
    ],
    tip_pages=[
        # List of tip page URLs...
    ]
)
```

#### Storage Directory

Ensure the wiki data storage directory exists and is writable:

```bash
mkdir -p ./data/wiki
chmod 755 ./data/wiki
```

### 3. Initial Deployment

1. **Start the server:**
   ```bash
   python server.py
   ```

2. **Verify initialization:**
   Check the logs for successful wiki integration:
   ```
   INFO - Initializing wiki data integration...
   INFO - Wiki integration initialized successfully
   INFO - Genre data available: X genres
   INFO - Meta tag data available: Y meta tags
   ```

3. **Test basic functionality:**
   Use an MCP client to test the `analyze_character_text` tool with sample text.

### 4. Production Deployment

#### Using systemd (Linux)

Create a systemd service file `/etc/systemd/system/character-music-mcp.service`:

```ini
[Unit]
Description=Character Music MCP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/character-music-mcp
ExecStart=/usr/bin/python3 server.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/path/to/character-music-mcp

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable character-music-mcp
sudo systemctl start character-music-mcp
```

#### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p ./data/wiki

EXPOSE 8000

CMD ["python", "server.py"]
```

Build and run:

```bash
docker build -t character-music-mcp .
docker run -d -p 8000:8000 -v $(pwd)/data:/app/data character-music-mcp
```

## Configuration Options

### Wiki Integration Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `enabled` | `True` | Enable/disable wiki data integration |
| `local_storage_path` | `"./data/wiki"` | Local directory for cached wiki data |
| `refresh_interval_hours` | `24` | Hours between wiki data refresh attempts |
| `fallback_to_hardcoded` | `True` | Use hardcoded data when wiki unavailable |

### Performance Tuning

- **Cache Size**: Monitor disk usage in the wiki storage directory
- **Refresh Frequency**: Adjust `refresh_interval_hours` based on needs
- **Concurrent Requests**: The server handles multiple requests asynchronously

## Verification

### Health Checks

1. **Server Status**: Verify the server is running and responding
2. **Wiki Integration**: Check logs for successful wiki data loading
3. **Tool Functionality**: Test each MCP tool with sample data

### Test Commands

Use these test scenarios to verify deployment:

```python
# Test character analysis
await analyze_character_text("A brave knight named Arthur...", ctx)

# Test complete workflow
await complete_workflow("Story about a mysterious detective...", ctx)

# Test album creation
await create_story_integrated_album("Narrative text...", ctx)
```

## Troubleshooting

### Common Issues

1. **Wiki Data Download Failures**
   - Check internet connectivity
   - Verify sunoaiwiki.com accessibility
   - Review firewall settings

2. **Permission Errors**
   - Ensure write permissions on data directory
   - Check user permissions for the service

3. **Memory Issues**
   - Monitor RAM usage during wiki data processing
   - Consider increasing system memory

4. **Import Errors**
   - Verify all dependencies are installed
   - Check Python path configuration

### Log Analysis

Monitor these log messages:

- `INFO - Wiki integration initialized successfully` - Successful setup
- `WARNING - Failed to initialize wiki integration` - Fallback mode active
- `ERROR - Download failed` - Network or permission issues

## Security Considerations

### Network Security

- The server downloads data from sunoaiwiki.com
- Ensure secure network configuration
- Consider using HTTPS proxies if required

### Data Security

- Wiki data is cached locally in plain text
- Ensure appropriate file system permissions
- Consider encryption for sensitive deployments

### Access Control

- Implement MCP client authentication as needed
- Monitor server access logs
- Use firewall rules to restrict access

## Performance Monitoring

### Key Metrics

- Wiki data download success rate
- Response times for generation tools
- Memory usage during processing
- Disk space usage for wiki cache

### Monitoring Tools

- System logs for error tracking
- Performance metrics collection
- Disk space monitoring for cache directory

## Next Steps

After successful deployment:

1. Set up monitoring and alerting
2. Configure backup procedures for wiki data
3. Implement log rotation
4. Plan for scaling if needed

For ongoing maintenance, see the [Maintenance Procedures](maintenance_procedures.md) guide.