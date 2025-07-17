#!/usr/bin/env node

/**
 * MCP Client Test
 * Tests Redis MCP server through simplified client implementation
 */

const { spawnSync } = require('child_process');
const { Client } = require('@modelcontextprotocol/sdk/client');
const { ChildProcessClientTransport } = require('@modelcontextprotocol/sdk/client/child-process');

// Path to MCP server
const SERVER_PATH = './mcp-redis-server/src/fixed-index.js';

// Start MCP server process with Redis configuration
const serverProcess = spawnSync('node', [SERVER_PATH], {
  env: {
    ...process.env,
    REDIS_HOST: 'localhost',
    REDIS_PORT: '6380',
    REDIS_NAMESPACE_PREFIX: 'test:'
  },
  // Keep the process running in background
  detached: true,
  stdio: 'ignore'
});

// Test values
const TEST_KEY = `client-test-${Date.now()}`;
const TEST_VALUE = JSON.stringify({ message: "Hello from MCP Client Test", timestamp: new Date().toISOString() });

// Connect to MCP server
async function testMcpServer() {
  // Create a transport to the spawned MCP server
  const transport = new ChildProcessClientTransport('node', [SERVER_PATH], {
    env: {
      ...process.env,
      REDIS_HOST: 'localhost',
      REDIS_PORT: '6380',
      REDIS_NAMESPACE_PREFIX: 'test:'
    }
  });

  // Create MCP client
  const client = new Client();

  try {
    console.log('Connecting to MCP server...');
    await client.connect(transport);
    console.log('Connected!');

    // List available tools
    console.log('\n=== Listing available tools ===');
    const tools = await client.listTools();
    console.log('Available tools:', tools.tools.map(t => t.name));

    // List available resources
    console.log('\n=== Listing available resources ===');
    const resources = await client.listResources();
    console.log('Available resources:', resources.resources.map(r => r.uri));

    // Test SET operation
    console.log('\n=== Testing SET operation ===');
    const setResult = await client.callTool('set', {
      key: TEST_KEY,
      value: TEST_VALUE
    });
    console.log('SET result:', setResult);

    // Test GET operation
    console.log('\n=== Testing GET operation ===');
    const getResult = await client.callTool('get', {
      key: TEST_KEY
    });
    console.log('GET result:', getResult);

    // Test LIST operation
    console.log('\n=== Testing LIST operation ===');
    const listResult = await client.callTool('list', {
      pattern: 'client-test-*'
    });
    console.log('LIST result:', listResult);

    // Test DELETE operation
    console.log('\n=== Testing DELETE operation ===');
    const deleteResult = await client.callTool('delete', {
      key: TEST_KEY
    });
    console.log('DELETE result:', deleteResult);

    console.log('\n=== All MCP operations completed successfully! ===');

  } catch (error) {
    console.error('Error during MCP tests:', error);
  } finally {
    // Close MCP client connection
    try {
      await client.close();
      console.log('MCP client connection closed');
    } catch (err) {
      console.error('Error closing MCP client:', err);
    }
  }
}

// Run tests
testMcpServer()
  .catch(console.error)
  .finally(() => {
    // Make sure to clean up any processes
    process.exit(0);
  });
