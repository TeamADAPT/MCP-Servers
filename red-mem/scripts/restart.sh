#!/bin/bash

# Kill any existing red-mem processes
pkill -f "node.*red-mem/build/index.js"

# Wait for processes to terminate
sleep 2

# Start the server
cd /data/ax/DevOps/mcp_master/red-mem
npm run build && node build/index.js