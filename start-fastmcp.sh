#!/bin/bash
# FastMCP Framework Startup Script

cd /Threshold/bloom-memory/mcp-servers/fastmcp

# Check if built
if [ ! -f "dist/bin/fastmcp.js" ]; then
    echo "Building FastMCP..."
    npm run build
fi

# Start FastMCP server
echo "Starting FastMCP Framework..."
node dist/bin/fastmcp.js "$@"