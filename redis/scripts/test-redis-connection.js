#!/usr/bin/env node

/**
 * Test Redis Connection
 * 
 * This script tests the connection to Redis using the ioredis library.
 */

const Redis = require('ioredis');

// Redis Configuration
const REDIS_OPTIONS = {
  host: 'localhost',
  port: 6380, // Using the configured Redis port
  retryStrategy: (times) => {
    if (times > 10) {
      return null; // Stop retrying
    }
    return Math.min(times * 100, 3000); // Exponential backoff with max 3s
  }
};

// Create Redis client
console.log('Creating Redis client...');
const redis = new Redis(REDIS_OPTIONS);

// Set up event handlers
redis.on('ready', () => {
  console.log('Connected to Redis successfully');
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
    const testKey = 'test:connection:' + Date.now();
    const testValue = { message: 'Hello from Redis Connection Test', timestamp: new Date().toISOString() };
    
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
    const testStream = 'test:stream:' + Date.now();
    
    console.log(`Creating stream ${testStream}...`);
    const messageId = await redis.xadd(testStream, '*', 'message', 'Hello from Redis Connection Test', 'timestamp', new Date().toISOString());
    console.log(`Stream created with message ID: ${messageId}`);
    
    console.log(`Reading from stream ${testStream}...`);
    const messages = await redis.xrange(testStream, '-', '+');
    console.log('Messages:', messages);
    
    console.log(`Deleting stream ${testStream}...`);
    await redis.del(testStream);
    console.log('Stream deleted successfully');
    
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
