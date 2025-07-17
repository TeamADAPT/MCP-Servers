#!/bin/bash
# Desktop Automation MCP v2 Startup Script

cd /Threshold/bloom-memory/mcp-servers/desktop-automation-mcp-v2

# Check if built
if [ ! -f "build/index.js" ]; then
    echo "Building Desktop Automation MCP v2..."
    npm run build
fi

# Start Desktop Automation server
echo "Starting Desktop Automation MCP v2..."
node build/index.js "$@"