#!/bin/bash

# Kill any existing red-stream processes
pkill -f "node.*red-stream/build/index.js"

# Wait for processes to terminate
sleep 2

# Start the server
cd /data/ax/DevOps/mcp_master/red-stream
npm run build && node build/index.js