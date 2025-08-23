#!/bin/sh
# STDIO mode startup script for Character-Driven Music Generation MCP Server
set -e

# Change to script directory
cd "$(dirname "$0")"

# Create python3.11 virtual environment (if it doesn't exist)
if [ ! -d "/Users/tosinakinosho/workspaces/character-music-mcp/.venv" ]; then
    echo "Creating virtual environment with python3.11..." >&2
    python3.11 -m venv /Users/tosinakinosho/workspaces/character-music-mcp/.venv
    echo "Upgrading pip..." >&2
    /Users/tosinakinosho/workspaces/character-music-mcp/.venv/bin/pip install --upgrade pip
    echo "Installing dependencies..." >&2
    echo "Note: Dependency installation may take several minutes. Please wait..." >&2
    /Users/tosinakinosho/workspaces/character-music-mcp/.venv/bin/pip install -e .
fi

# Check environment variables (optional for this server)
if [[ -n "$SUNO_COOKIE" ]]; then
    echo "Suno AI integration enabled with provided credentials" >&2
else
    echo "Running in standalone mode (Suno AI integration optional)" >&2
fi

# Start STDIO mode MCP server
echo "Starting Character-Driven Music Generation MCP Server..." >&2
/Users/tosinakinosho/workspaces/character-music-mcp/.venv/bin/python server.py
