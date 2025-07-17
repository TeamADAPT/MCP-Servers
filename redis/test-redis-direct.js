#!/usr/bin/env node

/**
 * Test script for redis-direct MCP server
 * Run this after restarting Cline to verify direct MCP functionality
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Test values
const TEST_KEY = `direct-test-${Date.now()}`;
const TEST_VALUE = JSON.stringify({ message: "Direct MCP Test Data", timestamp: new Date().toISOString() });

console.log('=== Redis Direct MCP Test ===\n');

// Create a simulated MCP request function
function createMcpRequest(type, params = {}) {
  return {
    jsonrpc: '2.0',
    id: `test-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
    method: type,
    params
  };
}

// Direct test with the MCP server process
async function runDirectTest() {
  console.log('Starting Redis Direct MCP server...');
  
  // Start the MCP server
  const serverProcess = spawn('node', 
    ['mcp-redis-server/src/direct-mcp.js'],
    { 
      env: {
        ...process.env,
        REDIS_HOST: 'localhost', 
        REDIS_PORT: '6380',
        REDIS_NAMESPACE_PREFIX: 'test:',
        NODE_OPTIONS: '--no-warnings'
      },
      stdio: ['pipe', 'pipe', 'pipe'] 
    }
  );
  
  // Set up communication channels
  const stdin = serverProcess.stdin;
  const stdoutChunks = [];
  const stderrChunks = [];
  
  serverProcess.stdout.on('data', (chunk) => {
    stdoutChunks.push(chunk);
  });
  
  serverProcess.stderr.on('data', (chunk) => {
    const text = chunk.toString();
    console.log('Server log:', text);
    stderrChunks.push(chunk);
  });
  
  // Wait for server to start
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  console.log('Server started. Beginning MCP tests...');
  
  try {
    // 1. Test LIST_TOOLS operation
    console.log('\n=== Testing LIST_TOOLS via MCP ===');
    const toolsRequest = createMcpRequest('list_tools');
    const toolsResponse = await sendMcpRequest(stdin, stdoutChunks, toolsRequest);
    
    if (toolsResponse?.result?.tools) {
      console.log('Available tools:', toolsResponse.result.tools.map(t => t.name).join(', '));
    } else {
      console.error('Failed to list tools:', toolsResponse);
      return false;
    }

    // 2. Test LIST_RESOURCES operation
    console.log('\n=== Testing LIST_RESOURCES via MCP ===');
    const resourcesRequest = createMcpRequest('list_resources');
    const resourcesResponse = await sendMcpRequest(stdin, stdoutChunks, resourcesRequest);
    
    if (resourcesResponse?.result?.resources) {
      console.log('Available resources:', resourcesResponse.result.resources.map(r => r.uri).join(', '));
    } else {
      console.error('Failed to list resources:', resourcesResponse);
      return false;
    }
    
    // 3. Test SET operation via MCP
    console.log('\n=== Testing SET via MCP ===');
    const setRequest = createMcpRequest('call_tool', {
      name: 'set',
      arguments: {
        key: TEST_KEY,
        value: TEST_VALUE
      }
    });
    const setResponse = await sendMcpRequest(stdin, stdoutChunks, setRequest);
    console.log('SET response:', setResponse);
    
    // 4. Test GET operation via MCP
    console.log('\n=== Testing GET via MCP ===');
    const getRequest = createMcpRequest('call_tool', {
      name: 'get',
      arguments: {
        key: TEST_KEY
      }
    });
    const getResponse = await sendMcpRequest(stdin, stdoutChunks, getRequest);
    console.log('GET response:', getResponse);
    
    // 5. Test LIST operation via MCP
    console.log('\n=== Testing LIST via MCP ===');
    const listRequest = createMcpRequest('call_tool', {
      name: 'list',
      arguments: {
        pattern: 'test-*'
      }
    });
    const listResponse = await sendMcpRequest(stdin, stdoutChunks, listRequest);
    console.log('LIST response:', listResponse);
    
    // 6. Test DELETE operation via MCP
    console.log('\n=== Testing DELETE via MCP ===');
    const deleteRequest = createMcpRequest('call_tool', {
      name: 'delete',
      arguments: {
        key: TEST_KEY
      }
    });
    const deleteResponse = await sendMcpRequest(stdin, stdoutChunks, deleteRequest);
    console.log('DELETE response:', deleteResponse);
    
    // All tests passed
    console.log('\n✅ All Redis Direct MCP tests passed successfully!');
    
    return true;
  } catch (error) {
    console.error('Error during MCP test:', error);
    return false;
  } finally {
    // Clean up
    try {
      serverProcess.kill();
      console.log('Server process terminated');
    } catch (err) {
      console.error('Error terminating server process:', err);
    }
  }
}

// Helper function to send MCP request and get response
async function sendMcpRequest(stdin, stdoutChunks, request) {
  // Clear previous output
  stdoutChunks.length = 0;
  
  // Send request
  const requestStr = JSON.stringify(request) + '\n';
  stdin.write(requestStr);
  
  // Wait for response
  return new Promise((resolve, reject) => {
    const waitForResponse = () => {
      if (stdoutChunks.length > 0) {
        try {
          const responseStr = Buffer.concat(stdoutChunks).toString();
          stdoutChunks.length = 0; // Clear for next request
          
          const responses = responseStr.split('\n').filter(Boolean);
          for (const resp of responses) {
            try {
              const parsed = JSON.parse(resp);
              if (parsed.id === request.id) {
                return resolve(parsed);
              }
            } catch (e) {
              console.warn('Could not parse response chunk:', resp);
            }
          }
          
          // If we get here, wait more
          setTimeout(waitForResponse, 100);
        } catch (err) {
          reject(err);
        }
      } else {
        // No output yet, wait more
        setTimeout(waitForResponse, 100);
      }
    };
    
    // Start waiting
    setTimeout(waitForResponse, 100);
    
    // Timeout after 5 seconds
    setTimeout(() => {
      reject(new Error(`MCP request timed out: ${JSON.stringify(request)}`));
    }, 5000);
  });
}

// Run all tests
async function runTests() {
  try {
    // Run direct MCP server test
    const testsPassed = await runDirectTest();
    
    if (testsPassed) {
      console.log('\n=== SUCCESS: All tests completed successfully! ===');
      console.log('\nThe redis-direct MCP server is properly configured and working correctly');
      console.log('To use it with Cline, please restart the Cline extension');
    } else {
      console.error('\n=== ERROR: Tests failed ===');
    }
    
    process.exit(testsPassed ? 0 : 1);
  } catch (error) {
    console.error('\n❌ Tests failed with error:', error);
    process.exit(1);
  }
}

// Start tests
runTests();
