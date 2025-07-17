#!/bin/bash
# MCP Proxy Startup Script

cd /Threshold/bloom-memory/mcp-servers/mcp-proxy

# Check if built
if [ ! -f "dist/bin/mcp-proxy.js" ]; then
    echo "Building MCP Proxy..."
    npm run build
fi

# Start MCP Proxy server
echo "Starting MCP Proxy..."
node dist/bin/mcp-proxy.js "$@"