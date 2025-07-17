#!/usr/bin/env node

/**
 * Start Redis MCP Server
 * 
 * This script starts the Redis MCP server with the correct configuration
 */

const { spawn } = require('child_process');
const path = require('path');

// Path to MCP server script
const MCP_SERVER_PATH = path.resolve('./mcp-redis-server/src/fixed-index.js');

console.log(`Starting Redis MCP Server at ${MCP_SERVER_PATH}...`);

// Set environment variables
const env = {
  ...process.env,
  REDIS_HOST: 'localhost',
  REDIS_PORT: '6380',
  REDIS_NAMESPACE_PREFIX: 'dev:'
};

// Start the server process
const serverProcess = spawn('node', [MCP_SERVER_PATH], {
  env,
  stdio: 'inherit'
});

// Handle process events
serverProcess.on('error', (err) => {
  console.error('Failed to start MCP server:', err);
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('Stopping Redis MCP Server...');
  serverProcess.kill();
  process.exit(0);
});

console.log('Redis MCP Server started. Press Ctrl+C to stop.');
