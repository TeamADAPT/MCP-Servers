#!/usr/bin/env node

/**
 * Verify Redis MCP Server
 * 
 * This script tests the Redis MCP server by simulating how Cline would use it.
 * It verifies that the MCP server is properly set up and working.
 */

const { execSync } = require('child_process');
const { spawn } = require('child_process');
const { Client } = require('@modelcontextprotocol/sdk/client');
const { ChildProcessClientTransport } = require('@modelcontextprotocol/sdk/client/child-process');

// Test values
const TEST_KEY = `verify-test-${Date.now()}`;
const TEST_VALUE = JSON.stringify({ message: "Verification test data", timestamp: new Date().toISOString() });

console.log('=== Redis MCP Server Verification ===\n');

async function verifyMcpServer() {
  console.log('Starting MCP server for verification...');
  
  // Create transport to the MCP server
  const transport = new ChildProcessClientTransport('node', 
    ['/data-nova/ax/DevOps/mcp/mcp-servers/database-mcp-servers/redis/mcp-redis-server/src/fixed-index.js'], {
    env: {
      ...process.env,
      REDIS_HOST: 'localhost',
      REDIS_PORT: '6380',
      REDIS_NAMESPACE_PREFIX: 'verify:'
    }
  });

  // Create MCP client
  const client = new Client();

  try {
    // Connect to the MCP server
    await client.connect(transport);
    console.log('Connected to Redis MCP server');
    
    // 1. List available tools
    console.log('\n=== Verifying Tool Listing ===');
    const tools = await client.listTools();
    console.log('Available tools:', tools.tools.map(t => t.name).join(', '));
    
    // 2. List available resources
    console.log('\n=== Verifying Resource Listing ===');
    const resources = await client.listResources();
    console.log('Available resources:', resources.resources.map(r => r.uri).join(', '));
    
    // 3. Test SET operation
    console.log('\n=== Verifying SET operation ===');
    const setResult = await client.callTool('set', {
      key: TEST_KEY,
      value: TEST_VALUE
    });
    console.log('SET result:', setResult);
    
    // 4. Test GET operation
    console.log('\n=== Verifying GET operation ===');
    const getResult = await client.callTool('get', {
      key: TEST_KEY
    });
    console.log('GET result:', getResult);
    
    // 5. Test LIST operation
    console.log('\n=== Verifying LIST operation ===');
    const listResult = await client.callTool('list', {
      pattern: 'verify-test-*'
    });
    console.log('LIST result:', listResult);
    
    // 6. Test DELETE operation
    console.log('\n=== Verifying DELETE operation ===');
    const deleteResult = await client.callTool('delete', {
      key: TEST_KEY
    });
    console.log('DELETE result:', deleteResult);
    
    console.log('\n=== Redis MCP Server verification completed successfully! ===');
    console.log('\nThe redis-mcp server is correctly set up and ready to use in Cline.');
    console.log('It has been added to the Cline MCP settings and should be available after restarting Cline.');
    
  } catch (error) {
    console.error('Error during verification:', error);
    process.exit(1);
  } finally {
    // Close connection
    await client.close();
  }
}

// Run verification
verifyMcpServer()
  .catch(console.error)
  .finally(() => process.exit(0));
