#!/bin/bash

# Start Redis MCP Server
# This script starts the Redis MCP server with the updated configuration

# Set environment variables
export REDIS_CLUSTER_MODE=true
export REDIS_CLUSTER_NODES="[{\"host\":\"redis-cluster-01.memcommsops.internal\",\"port\":7000},{\"host\":\"redis-cluster-02.memcommsops.internal\",\"port\":7001},{\"host\":\"redis-cluster-03.memcommsops.internal\",\"port\":7002}]"
export REDIS_USERNAME="adapt-mcp-readwrite"
export REDIS_PASSWORD="adapt-mcp-readwrite-acc9582bc2eaead3"
export REDIS_SCALE_READS="slave"
export REDIS_MAX_REDIRECTIONS="16"
export REDIS_RETRY_DELAY="300"
export REDIS_CONNECT_TIMEOUT="5000"
export REDIS_MAX_RETRIES="3"
export REDIS_NAMESPACE_PREFIX="adapt:"
export REDIS_SHARED_NAMESPACE_PREFIX="shared:"

# Kill any existing Redis MCP server processes
echo "Stopping any existing Redis MCP server processes..."
pkill -f "node /data-nova/ax/DevOps/mcp/mcp-servers/database-mcp-servers/redis/src/redis/build/redis/index.js" || true

# Wait for processes to terminate
sleep 2

# Start the Redis MCP server
echo "Starting Redis MCP server..."
node /data-nova/ax/DevOps/mcp/mcp-servers/database-mcp-servers/redis/src/redis/build/redis/index.js redis://adapt-mcp-readwrite:adapt-mcp-readwrite-acc9582bc2eaead3@redis-cluster-01.memcommsops.internal:7000 > /data-nova/ax/DevOps/mcp/mcp-servers/database-mcp-servers/redis/logs/redis-mcp-server.log 2>&1 &

# Get the process ID
PID=$!
echo "Redis MCP server started with PID: $PID"

# Check if the process is running
if ps -p $PID > /dev/null; then
    echo "Redis MCP server is running."
    echo "Log file: /data-nova/ax/DevOps/mcp/mcp-servers/database-mcp-servers/redis/logs/redis-mcp-server.log"
else
    echo "Failed to start Redis MCP server."
    exit 1
fi

# Register the server with MCP system
echo "Registering Redis MCP server with MCP system..."
echo "To register the server, run the following command:"
echo "mcp-cli register-server --name redis --url redis-mcp.memcommsops.internal:3000 --auth-token mcp-redis-auth-token-2025-04"

# Verify the connection
echo "To verify the connection, run the following command:"
echo "mcp-cli test-connection --server redis"

echo "Redis MCP server setup complete."