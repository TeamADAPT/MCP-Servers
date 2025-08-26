#!/bin/bash

# Atlassian Enterprise MCP Server Startup Script
# Provides enterprise analytics, AI, and app integration features (~22 tools)

set -euo pipefail

# Change to the server directory
cd "$(dirname "$0")"

# Set environment variables for the enterprise server
export PYTHONPATH="${PWD}/src:${PYTHONPATH:-}"
export MCP_SERVER_NAME="mcp-atlassian-enterprise"

# Check for required dependencies
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not installed." >&2
    exit 1
fi

# Ensure virtual environment exists and is activated
if [[ ! -d "venv" ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies if needed
if [[ ! -f "venv/.deps_installed" ]]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt || pip install -e .
    touch venv/.deps_installed
fi

# Log startup
echo "Starting Atlassian Enterprise MCP Server..." >&2
echo "Server: $MCP_SERVER_NAME" >&2
echo "Tools: Authentication, Analytics, AI, Marketplace apps" >&2
echo "Expected tool count: ~22 tools (4 auth + 6 analytics + 6 AI + 6 apps)" >&2

# Start the server using the enterprise module
exec python3 -m mcp_atlassian.server_enterprise_main