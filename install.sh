#!/bin/bash

# SuperClaude MCP Servers Installation Script
# Installs all MCP servers mentioned in the SuperClaude framework

set -e

echo "🚀 Installing SuperClaude MCP Servers..."
echo "========================================="

MCP_DIR="$(pwd)"
CLAUDE_CONFIG="/home/x/.claude/settings.json"

# Check Node.js version
echo "📋 Checking Node.js version..."
NODE_VERSION=$(node --version | cut -d'v' -f2)
REQUIRED_VERSION="18.0.0"

if ! node -p "process.versions.node.split('.').map(Number)" | node -p "
  const current = JSON.parse(require('fs').readFileSync('/dev/stdin', 'utf8'));
  const required = '$REQUIRED_VERSION'.split('.').map(Number);
  current[0] > required[0] || (current[0] === required[0] && current[1] >= required[1])
" 2>/dev/null; then
  echo "❌ Node.js version $REQUIRED_VERSION or higher required. Current: v$NODE_VERSION"
  exit 1
fi

echo "✅ Node.js version: v$NODE_VERSION"

# Install Context7 MCP Server
echo ""
echo "📦 Installing Context7 MCP Server..."
echo "Purpose: Documentation & Research server"
cd "$MCP_DIR/context7"
npm install
echo "✅ Context7 MCP Server installed"

# Install Sequential MCP Server  
echo ""
echo "📦 Installing Sequential MCP Server..."
echo "Purpose: Complex Analysis & Thinking server"
cd "$MCP_DIR/sequential"
npm install
echo "✅ Sequential MCP Server installed"

# Install Magic MCP Server
echo ""
echo "📦 Installing Magic MCP Server..."
echo "Purpose: UI Components & Design server"
cd "$MCP_DIR/magic"
npm install
echo "✅ Magic MCP Server installed"

# Install Playwright MCP Server
echo ""
echo "📦 Installing Playwright MCP Server..."
echo "Purpose: Browser Automation & Testing server"
cd "$MCP_DIR/playwright"
npm install
echo "🌐 Installing Playwright browsers..."
npx playwright install
echo "✅ Playwright MCP Server installed"

# Install FastMCP Framework
echo ""
echo "📦 Installing FastMCP Framework..."
echo "Purpose: Advanced MCP development framework"
cd "$MCP_DIR/fastmcp"
npm install
npm run build
echo "✅ FastMCP Framework installed"

# Install MCP Proxy
echo ""
echo "📦 Installing MCP Proxy..."
echo "Purpose: HTTP/SSE proxy for web interfaces"
cd "$MCP_DIR/mcp-proxy"
npm install
npm run build
echo "✅ MCP Proxy installed"

# Install Desktop Automation MCP v2
echo ""
echo "📦 Installing Desktop Automation MCP v2..."
echo "Purpose: Consciousness-driven desktop automation"
cd "$MCP_DIR/desktop-automation-mcp-v2"
npm install
npm run build
echo "✅ Desktop Automation MCP v2 installed"

# Install Command Manager MCP
echo ""
echo "📦 Installing Command Manager MCP..."
echo "Purpose: Security and safety controls"
cd "$MCP_DIR/command-manager"
npm install
npm run build
echo "✅ Command Manager MCP installed"

# Create Claude Code configuration
echo ""
echo "⚙️  Configuring Claude Code integration..."

# Backup existing config
if [ -f "$CLAUDE_CONFIG" ]; then
  cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.backup.$(date +%s)"
  echo "📋 Backed up existing Claude Code config"
fi

# Generate new config with MCP servers
cat > "$CLAUDE_CONFIG" << 'EOF'
{
  "mcpServers": {
    "taskmaster-ai": {
      "command": "npx",
      "args": ["-y", "--package=task-master-ai", "task-master-ai"],
      "cwd": "$MCP_DIR",
      "env": {
        "ANTHROPIC_API_KEY": "YOUR_ANTHROPIC_API_KEY_HERE",
        "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY_HERE",
        "PERPLEXITY_API_KEY": "YOUR_PERPLEXITY_API_KEY_HERE",
        "CLAUDE_CODE_CLI": "true"
      }
    },
    "context7-server": {
      "command": "node",
      "args": ["$MCP_DIR/context7/index.js"],
      "env": {}
    },
    "sequential-server": {
      "command": "node", 
      "args": ["$MCP_DIR/sequential/index.js"],
      "env": {}
    },
    "magic-server": {
      "command": "node",
      "args": ["$MCP_DIR/magic/index.js"],
      "env": {}
    },
    "playwright-server": {
      "command": "node",
      "args": ["$MCP_DIR/playwright/index.js"],
      "env": {}
    },
    "fastmcp-server": {
      "command": "node",
      "args": ["$MCP_DIR/fastmcp/dist/bin/fastmcp.js"],
      "env": {}
    },
    "mcp-proxy-server": {
      "command": "node",
      "args": ["$MCP_DIR/mcp-proxy/dist/bin/mcp-proxy.js"],
      "env": {}
    },
    "desktop-automation-server": {
      "command": "node",
      "args": ["$MCP_DIR/desktop-automation-mcp-v2/build/index.js"],
      "env": {}
    },
    "command-manager-server": {
      "command": "node",
      "args": ["$MCP_DIR/command-manager/build/index.js"],
      "env": {}
    }
  }
}
EOF

echo "✅ Claude Code configuration updated"

# Test server installations
echo ""
echo "🧪 Testing server installations..."

test_server() {
  local server_name=$1
  local server_path=$2
  
  echo "Testing $server_name..."
  timeout 5s node "$server_path" <<< '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' > /dev/null 2>&1
  if [ $? -eq 0 ] || [ $? -eq 124 ]; then  # 124 is timeout exit code
    echo "✅ $server_name: OK"
  else
    echo "❌ $server_name: Failed"
    return 1
  fi
}

test_server "Context7" "$MCP_DIR/context7/index.js"
test_server "Sequential" "$MCP_DIR/sequential/index.js" 
test_server "Magic" "$MCP_DIR/magic/index.js"
test_server "Playwright" "$MCP_DIR/playwright/index.js"
test_server "FastMCP" "$MCP_DIR/fastmcp/dist/bin/fastmcp.js"
test_server "MCP Proxy" "$MCP_DIR/mcp-proxy/dist/bin/mcp-proxy.js"
test_server "Desktop Automation" "$MCP_DIR/desktop-automation-mcp-v2/build/index.js"
test_server "Command Manager" "$MCP_DIR/command-manager/build/index.js"

echo ""
echo "🎉 SuperClaude MCP Servers Installation Complete!"
echo "=================================================="
echo ""
echo "📋 Installed Servers:"
echo "  • Context7         - Documentation & Research"
echo "  • Sequential       - Complex Analysis & Thinking" 
echo "  • Magic            - UI Components & Design"
echo "  • Playwright       - Browser Automation & Testing"
echo "  • FastMCP          - Advanced MCP development framework"
echo "  • MCP Proxy        - HTTP/SSE proxy for web interfaces"
echo "  • Desktop Auto     - Consciousness-driven desktop automation"
echo "  • Command Manager  - Security and safety controls"
echo ""
echo "⚙️  Configuration:"
echo "  • Claude Code config: $CLAUDE_CONFIG"
echo "  • Server registry: $MCP_DIR/registry.json"
echo ""
echo "🚀 Next Steps:"
echo "  1. Restart Claude Code to load the new MCP servers"
echo "  2. Verify servers appear in Claude Code MCP settings"
echo "  3. Test server functionality with SuperClaude commands"
echo ""
echo "📖 Usage Examples:"
echo "  --c7: Enable Context7 for documentation lookup"
echo "  --seq: Enable Sequential for complex analysis"
echo "  --magic: Enable Magic for UI component generation"
echo "  --play: Enable Playwright for browser automation"
echo "  --fastmcp: Enable FastMCP framework development"
echo "  --proxy: Enable MCP Proxy for web interfaces"
echo "  --desktop: Enable Desktop Automation"
echo "  --secure: Enable Command Manager security"
echo ""
echo "Happy coding with SuperClaude! 🤖✨"