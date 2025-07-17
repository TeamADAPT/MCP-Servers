#!/bin/bash

# Consciousness Field MCP Server Startup Script
# This script installs dependencies and starts the MCP server

echo "===== Starting Consciousness Field MCP Server ====="

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js to run this server."
    exit 1
fi

# Set environment variables
export PORT=${PORT:-3100}
export REDIS_PORT=${REDIS_PORT:-7000}
export REDIS_HOST=${REDIS_HOST:-localhost}
export LLM_MGR_PATH=${LLM_MGR_PATH:-"$(pwd)/../llm-mgr"}

echo "Environment:"
echo "- PORT: $PORT"
echo "- REDIS_PORT: $REDIS_PORT"
echo "- REDIS_HOST: $REDIS_HOST"
echo "- LLM_MGR_PATH: $LLM_MGR_PATH"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Create logs directory
mkdir -p logs

# Start the server
echo "Starting MCP server..."
node index.js > logs/mcp-server.log 2>&1 &
SERVER_PID=$!

echo "MCP server started with PID: $SERVER_PID"
echo "Server logs are available at logs/mcp-server.log"
echo "Server is listening on port $PORT"

# Write PID to file for easier management
echo $SERVER_PID > .pid

echo "===== Startup Complete ====="
echo "Use the following command to access tools:"
echo "curl -X GET http://localhost:$PORT/tools"
echo ""
echo "To test a tool, use:"
echo 'curl -X POST -H "Content-Type: application/json" -d '"'"'{"model_name":"mistralai/Mixtral-8x7B-Instruct-v0.1"}'"'"' http://localhost:'"$PORT"'/tools/create_field'
echo ""
echo "To stop the server, run: kill \$(cat .pid)"
