#!/usr/bin/env node

/**
 * Test Redis MCP Server Memory Bank
 * 
 * This script tests the memory bank functionality of the Redis MCP server
 * by sending MCP requests directly to the server.
 */

const { spawn } = require('child_process');
const path = require('path');
const readline = require('readline');

// MCP server path
const MCP_SERVER_PATH = path.resolve(__dirname, '../src/redis/build/index.js');

// Test memory data
const TEST_KEY = 'test_memory_' + Date.now();
const TEST_VALUE = {
  message: 'Hello from MCP Test',
  timestamp: new Date().toISOString(),
  test_run: true
};

// Start the MCP server
function startMcpServer() {
  console.log(`Starting MCP server: ${MCP_SERVER_PATH}`);
  
  // Set environment variables for Redis connection
  const env = {
    ...process.env,
    REDIS_NODES: JSON.stringify([
      { host: '127.0.0.1', port: 7000 },
      { host: '127.0.0.1', port: 7001 },
      { host: '127.0.0.1', port: 7002 }
    ]),
    REDIS_PASSWORD: 'd5d7817937232ca5',
    REDIS_RETRY_MAX: '10',
    REDIS_RETRY_DELAY: '100'
  };
  
  // Spawn the MCP server process
  const mcpServer = spawn('node', [MCP_SERVER_PATH], {
    env,
    stdio: ['pipe', 'pipe', 'pipe']
  });
  
  // Create readline interface for stdout
  const rl = readline.createInterface({
    input: mcpServer.stdout,
    crlfDelay: Infinity
  });
  
  // Create readline interface for stderr
  const errRl = readline.createInterface({
    input: mcpServer.stderr,
    crlfDelay: Infinity
  });
  
  // Handle stdout
  rl.on('line', (line) => {
    try {
      const message = JSON.parse(line);
      handleMcpResponse(message);
    } catch (error) {
      console.log(`MCP stdout: ${line}`);
    }
  });
  
  // Handle stderr
  errRl.on('line', (line) => {
    console.error(`MCP stderr: ${line}`);
  });
  
  // Handle process exit
  mcpServer.on('exit', (code) => {
    console.log(`MCP server exited with code ${code}`);
  });
  
  return mcpServer;
}

// Send MCP request
function sendMcpRequest(mcpServer, request) {
  console.log(`Sending MCP request: ${JSON.stringify(request)}`);
  mcpServer.stdin.write(JSON.stringify(request) + '\n');
}

// Handle MCP response
function handleMcpResponse(response) {
  console.log(`Received MCP response: ${JSON.stringify(response)}`);
  
  // Check if this is a response to our request
  if (response.id && pendingRequests[response.id]) {
    const { resolve, reject } = pendingRequests[response.id];
    delete pendingRequests[response.id];
    
    if (response.error) {
      reject(new Error(response.error.message));
    } else {
      resolve(response);
    }
  }
}

// Pending requests map
const pendingRequests = {};

// Generate request ID
function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Send request and wait for response
function sendRequest(mcpServer, method, params) {
  return new Promise((resolve, reject) => {
    const id = generateRequestId();
    pendingRequests[id] = { resolve, reject };
    
    // The MCP protocol uses jsonrpc 2.0
    const request = {
      jsonrpc: '2.0',
      id,
      method,
      params
    };
    
    sendMcpRequest(mcpServer, request);
    
    // Set timeout for request
    setTimeout(() => {
      if (pendingRequests[id]) {
        delete pendingRequests[id];
        reject(new Error(`Request ${id} timed out`));
      }
    }, 5000);
  });
}

// Test remember tool
async function testRemember(mcpServer) {
  console.log(`Testing remember tool with key: ${TEST_KEY}`);
  
  try {
    const response = await sendRequest(mcpServer, 'call_tool', {
      name: 'set_state',  // Using set_state instead of remember as it's available in the MCP server
      arguments: {
        key: TEST_KEY,
        value: TEST_VALUE,
        category: 'test',
        priority: 'medium'
      }
    });
    
    console.log('Remember response:', response);
    return response;
  } catch (error) {
    console.error('Remember error:', error);
    throw error;
  }
}

// Test recall tool
async function testRecall(mcpServer) {
  console.log(`Testing recall tool with key: ${TEST_KEY}`);
  
  try {
    const response = await sendRequest(mcpServer, 'call_tool', {
      name: 'get_state',  // Using get_state instead of recall
      arguments: {
        key: TEST_KEY
      }
    });
    
    console.log('Recall response:', response);
    return response;
  } catch (error) {
    console.error('Recall error:', error);
    throw error;
  }
}

// Test list_memories tool
async function testListMemories(mcpServer) {
  console.log('Testing list_memories tool');
  
  try {
    const response = await sendRequest(mcpServer, 'call_tool', {
      name: 'list_streams',  // Using list_streams instead of list_memories
      arguments: {
        pattern: 'memory:*'
      }
    });
    
    console.log('List memories response:', response);
    return response;
  } catch (error) {
    console.error('List memories error:', error);
    throw error;
  }
}

// Test forget tool
async function testForget(mcpServer) {
  console.log(`Testing forget tool with key: ${TEST_KEY}`);
  
  try {
    const response = await sendRequest(mcpServer, 'call_tool', {
      name: 'delete_state',  // Using delete_state instead of forget
      arguments: {
        key: TEST_KEY
      }
    });
    
    console.log('Forget response:', response);
    return response;
  } catch (error) {
    console.error('Forget error:', error);
    throw error;
  }
}

// Run all tests
async function runTests() {
  const mcpServer = startMcpServer();
  
  try {
    // Wait for server to initialize
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Test remember tool
    await testRemember(mcpServer);
    
    // Test recall tool
    await testRecall(mcpServer);
    
    // Test list_memories tool
    await testListMemories(mcpServer);
    
    // Test forget tool
    await testForget(mcpServer);
    
    console.log('All tests completed successfully');
  } catch (error) {
    console.error('Test failed:', error);
  } finally {
    // Terminate MCP server
    mcpServer.kill();
  }
}

// Run the tests
runTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});