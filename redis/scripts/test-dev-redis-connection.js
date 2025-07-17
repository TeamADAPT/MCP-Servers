#!/usr/bin/env node

/**
 * Test Development Redis Cluster Connection
 * 
 * This script tests the connection to the development Redis cluster
 * using the updated connection parameters provided by Echo.
 */

const Redis = require('ioredis');

// Development Redis Cluster Configuration
const REDIS_NODES = [
  { host: 'redis-test.memcommsops.internal', port: 7000 },
  { host: 'redis-test.memcommsops.internal', port: 7001 },
  { host: 'redis-test.memcommsops.internal', port: 7002 }
];

const REDIS_OPTIONS = {
  redisOptions: {
    username: 'mcp-dev',
    password: 'dev-d5d7817937232ca5',
    enableACLAuthentication: true,
    retryStrategy: (times) => {
      console.log(`Retry attempt ${times}`);
      if (times > 10) {
        return null; // Stop retrying
      }
      return Math.min(times * 100, 3000); // Exponential backoff with max 3s
    }
  },
  enableAutoPipelining: true,
  maxRedirections: 16,
  retryDelayOnFailover: 300
};

// Create Redis client
console.log('Creating Redis client for development cluster...');
const redis = new Redis.Cluster(REDIS_NODES, REDIS_OPTIONS);

// Set up event handlers
redis.on('ready', () => {
  console.log('Connected to development Redis cluster successfully');
  testRedis();
});

redis.on('error', (err) => {
  console.error('Redis Error:', err);
});

redis.on('node error', (err, node) => {
  console.error(`Redis Node ${node.host}:${node.port} Error:`, err);
});

// Test Redis operations
async function testRedis() {
  try {
    // Test key-value operations
    console.log('\nTesting key-value operations...');
    const testKey = 'test:dev:connection:' + Date.now();
    const testValue = { 
      message: 'Hello from Development Redis Cluster Test', 
      timestamp: new Date().toISOString(),
      source: 'MCP DevOps Team'
    };
    
    console.log(`Setting key ${testKey}...`);
    await redis.set(testKey, JSON.stringify(testValue));
    console.log('Key set successfully');
    
    console.log(`Getting key ${testKey}...`);
    const value = await redis.get(testKey);
    console.log('Value:', JSON.parse(value));
    
    console.log(`Deleting key ${testKey}...`);
    await redis.del(testKey);
    console.log('Key deleted successfully');
    
    // Test stream operations
    console.log('\nTesting stream operations...');
    const testStream = 'test:dev:stream:' + Date.now();
    
    console.log(`Creating stream ${testStream}...`);
    const messageId = await redis.xadd(testStream, '*', 'message', 'Hello from Development Redis Cluster Test', 'timestamp', new Date().toISOString());
    console.log(`Stream created with message ID: ${messageId}`);
    
    console.log(`Reading from stream ${testStream}...`);
    const messages = await redis.xrange(testStream, '-', '+');
    console.log('Messages:', messages);
    
    console.log(`Deleting stream ${testStream}...`);
    await redis.del(testStream);
    console.log('Stream deleted successfully');
    
    // Test memory operations
    console.log('\nTesting memory operations...');
    const memoryKey = 'memory:test:' + Date.now();
    const memory = {
      content: 'This is a test memory for the development Redis cluster',
      category: 'test',
      priority: 'medium',
      timestamp: new Date().toISOString(),
      ttl: 3600
    };
    
    console.log(`Storing memory ${memoryKey}...`);
    await redis.set(memoryKey, JSON.stringify(memory));
    console.log('Memory stored successfully');
    
    console.log(`Retrieving memory ${memoryKey}...`);
    const retrievedMemory = await redis.get(memoryKey);
    console.log('Memory:', JSON.parse(retrievedMemory));
    
    console.log(`Deleting memory ${memoryKey}...`);
    await redis.del(memoryKey);
    console.log('Memory deleted successfully');
    
    console.log('\nAll tests passed successfully!');
  } catch (error) {
    console.error('Error during Redis tests:', error);
  } finally {
    // Close Redis connection
    redis.quit();
    console.log('Redis connection closed');
  }
}

// Handle process termination
process.on('SIGINT', () => {
  redis.quit();
  console.log('Redis connection closed');
  process.exit(0);
});