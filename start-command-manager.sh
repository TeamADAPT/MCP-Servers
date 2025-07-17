#!/bin/bash
# Command Manager MCP Startup Script

cd /Threshold/bloom-memory/mcp-servers/command-manager

# Check if built
if [ ! -f "build/index.js" ]; then
    echo "Building Command Manager MCP..."
    npm run build
fi

# Start Command Manager server
echo "Starting Command Manager MCP..."
node build/index.js "$@"