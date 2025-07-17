#!/bin/bash
# Test script for all MCP servers

echo "🧪 Testing MCP Servers..."
echo "========================"

MCP_DIR="/Threshold/bloom-memory/mcp-servers"

test_server() {
    local name="$1"
    local path="$2"
    
    echo -n "Testing $name... "
    
    # Test if server can start and respond to basic MCP protocol
    cd "$MCP_DIR"
    if timeout 3s node "$path" <<< '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' > /dev/null 2>&1; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAILED"
        return 1
    fi
}

# Test all servers
echo "Testing existing servers:"
test_server "Context7" "context7/index.js"
test_server "Sequential" "sequential/index.js"
test_server "Magic" "magic/index.js"
test_server "Playwright" "playwright/index.js"

echo ""
echo "Testing new servers:"
test_server "FastMCP" "fastmcp/dist/bin/fastmcp.js"
test_server "MCP Proxy" "mcp-proxy/dist/bin/mcp-proxy.js"
test_server "Desktop Automation" "desktop-automation-mcp-v2/build/index.js"
test_server "Command Manager" "command-manager/build/index.js"

echo ""
echo "🎉 Server testing complete!"