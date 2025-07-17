#!/usr/bin/env node

const net = require('net');
const fs = require('fs');
const path = require('path');

// Enable debug logging
const DEBUG = true;
const log = (...args) => DEBUG && console.log('[DEBUG]', ...args);

// Read MCP settings
const serverName = 'red-stream';
const serverConfig = settings.mcpServers[serverName];

console.log('Verifying MCP connection...\n');

// Test direct communication
const testMessage = {
    id: 'test-' + Date.now(),
    method: 'initialize',
    params: {}
};

// Create a pipe to the server process
const child_process = require('child_process');
const server = child_process.spawn('node', [serverConfig.args[0]], {
    env: {
        ...process.env,
        ...serverConfig.env,
        AUTO_INITIALIZE: 'true',
        DEBUG: 'true'
    },
    stdio: ['pipe', 'pipe', 'pipe']
});

// Handle server output
server.stdout.on('data', (data) => {
    console.log('Server output:', data.toString());
});

server.stderr.on('data', (data) => {
    console.error('Server error:', data.toString());
});

// Send test message
console.log('Sending test message:', JSON.stringify(testMessage, null, 2));
server.stdin.write(JSON.stringify(testMessage) + '\n');

// Wait for response
setTimeout(() => {
    console.log('\nClosing test...');
    server.kill();
    process.exit(0);
}, 5000);