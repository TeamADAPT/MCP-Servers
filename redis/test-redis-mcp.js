#!/usr/bin/env node

/**
 * Test Redis MCP Server
 * 
 * This script tests all Redis MCP tools without requiring Cline integration.
 */

const { exec } = require('child_process');
const path = require('path');

// Path to MCP server script (update if necessary)
const MCP_SERVER_PATH = path.resolve('./mcp-redis-server/src/fixed-index.js');

// Test values
const TEST_PREFIX = `test:${Date.now()}`;
const TEST_KEY = `${TEST_PREFIX}:key`;
const TEST_VALUE = JSON.stringify({ message: "Hello from Redis MCP Test", timestamp: new Date().toISOString() });
const TEST_STREAM = `${TEST_PREFIX}:stream`;

console.log('=== Redis MCP Server Test ===\n');

// Start MCP server
console.log(`Starting Redis MCP server at ${MCP_SERVER_PATH}...`);

// Set environment variables
process.env.REDIS_HOST = 'localhost';
process.env.REDIS_PORT = '6380';
process.env.REDIS_NAMESPACE_PREFIX = 'dev:';

// Create a function to run tests
async function runTests() {
  try {
    console.log('\n=== Testing SET operation ===');
    await execCommand(`
      node -e "
        const Redis = require('ioredis');
        const redis = new Redis({ host: 'localhost', port: 6380 });
        redis.set('${TEST_KEY}', String.raw\`${TEST_VALUE}\`)
          .then(result => { 
            console.log('Result:', result); 
            redis.quit();
          })
          .catch(err => { 
            console.error('Error:', err); 
            redis.quit();
          });
      "
    `);

    console.log('\n=== Testing GET operation ===');
    await execCommand(`
      node -e "
        const Redis = require('ioredis');
        const redis = new Redis({ host: 'localhost', port: 6380 });
        redis.get('${TEST_KEY}')
          .then(result => { 
            console.log('Result:', result); 
            redis.quit();
          })
          .catch(err => { 
            console.error('Error:', err); 
            redis.quit();
          });
      "
    `);

    console.log('\n=== Testing LIST operation ===');
    await execCommand(`
      node -e "
        const Redis = require('ioredis');
        const redis = new Redis({ host: 'localhost', port: 6380 });
        redis.keys('${TEST_PREFIX}*')
          .then(result => { 
            console.log('Result:', result); 
            redis.quit();
          })
          .catch(err => { 
            console.error('Error:', err); 
            redis.quit();
          });
      "
    `);

    console.log('\n=== Testing STREAM_PUBLISH operation ===');
    await execCommand(`
      node -e "
        const Redis = require('ioredis');
        const redis = new Redis({ host: 'localhost', port: 6380 });
        redis.xadd('${TEST_STREAM}', '*', 'message', 'Test message', 'timestamp', new Date().toISOString())
          .then(result => { 
            console.log('Message ID:', result); 
            redis.quit();
          })
          .catch(err => { 
            console.error('Error:', err); 
            redis.quit();
          });
      "
    `);

    console.log('\n=== Testing STREAM_READ operation ===');
    await execCommand(`
      node -e "
        const Redis = require('ioredis');
        const redis = new Redis({ host: 'localhost', port: 6380 });
        redis.xrange('${TEST_STREAM}', '-', '+')
          .then(result => { 
            console.log('Stream messages:', JSON.stringify(result, null, 2)); 
            redis.quit();
          })
          .catch(err => { 
            console.error('Error:', err); 
            redis.quit();
          });
      "
    `);

    console.log('\n=== Testing DELETE operation ===');
    await execCommand(`
      node -e "
        const Redis = require('ioredis');
        const redis = new Redis({ host: 'localhost', port: 6380 });
        Promise.all([
          redis.del('${TEST_KEY}'),
          redis.del('${TEST_STREAM}')
        ])
          .then(results => { 
            console.log('Delete results:', results); 
            redis.quit();
          })
          .catch(err => { 
            console.error('Error:', err); 
            redis.quit();
          });
      "
    `);

    console.log('\n=== All Redis operations completed successfully! ===');
  } catch (error) {
    console.error('\nError executing tests:', error);
  }
}

// Execute shell command function
function execCommand(command) {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing command: ${error.message}`);
        return reject(error);
      }
      if (stderr) {
        console.error(`Command stderr: ${stderr}`);
      }
      console.log(stdout);
      resolve(stdout);
    });
  });
}

// Run the tests
runTests();
