#!/bin/bash

# Start script for Atlassian MCP Server
# Fixed: ModuleNotFoundError resolved with proper virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv-atlassian"

echo "Starting Atlassian MCP Server..."
echo "Script directory: $SCRIPT_DIR"
echo "Virtual environment: $VENV_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "ERROR: Virtual environment not found at $VENV_DIR"
    echo "Please run the setup first by installing dependencies"
    exit 1
fi

# Check if mcp-atlassian command exists
if [ ! -f "$VENV_DIR/bin/mcp-atlassian" ]; then
    echo "ERROR: mcp-atlassian command not found in virtual environment"
    echo "Please reinstall the package with: pip install -e ."
    exit 1
fi

# Activate virtual environment and start server
cd "$SCRIPT_DIR"
source "$VENV_DIR/bin/activate"

echo "Virtual environment activated"
echo "Starting MCP Atlassian server..."

# Run the server
exec mcp-atlassian