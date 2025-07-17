#!/usr/bin/env node

/**
 * Simple Redis Test
 * Tests basic Redis operations using direct calls
 */

const Redis = require('ioredis');

// Configure Redis client
const redis = new Redis({
  host: 'localhost',
  port: 6380
});

// Test values
const TEST_PREFIX = `test:${Date.now()}`;
const TEST_KEY = `${TEST_PREFIX}:key`;
const TEST_VALUE = JSON.stringify({ message: "Hello from Redis Test", timestamp: new Date().toISOString() });
const TEST_STREAM = `${TEST_PREFIX}:stream`;

console.log('=== Simple Redis Test ===\n');

// Handle Redis events
redis.on('connect', () => {
  console.log('Connected to Redis successfully');
  runTests();
});

redis.on('error', (err) => {
  console.error('Redis connection error:', err);
  process.exit(1);
});

// Run tests
async function runTests() {
  try {
    // Test SET operation
    console.log('\n=== Testing SET operation ===');
    const setResult = await redis.set(TEST_KEY, TEST_VALUE);
    console.log('SET result:', setResult);

    // Test GET operation
    console.log('\n=== Testing GET operation ===');
    const getValue = await redis.get(TEST_KEY);
    console.log('GET result:', getValue);
    try {
      const parsedValue = JSON.parse(getValue);
      console.log('Parsed value:', parsedValue);
    } catch (e) {
      console.log('Could not parse as JSON');
    }

    // Test KEYS operation (LIST)
    console.log('\n=== Testing LIST operation ===');
    const keys = await redis.keys(`${TEST_PREFIX}*`);
    console.log('KEYS result:', keys);

    // Test STREAM_PUBLISH operation
    console.log('\n=== Testing STREAM_PUBLISH operation ===');
    const streamMsgId = await redis.xadd(
      TEST_STREAM,
      '*',
      'message', 'Test message',
      'timestamp', new Date().toISOString()
    );
    console.log('XADD result (message ID):', streamMsgId);

    // Test STREAM_READ operation
    console.log('\n=== Testing STREAM_READ operation ===');
    const streamMessages = await redis.xrange(TEST_STREAM, '-', '+');
    console.log('XRANGE result:', JSON.stringify(streamMessages, null, 2));

    // Test DELETE operation
    console.log('\n=== Testing DELETE operation ===');
    const delKeyResult = await redis.del(TEST_KEY);
    console.log('DEL key result:', delKeyResult);

    const delStreamResult = await redis.del(TEST_STREAM);
    console.log('DEL stream result:', delStreamResult);

    console.log('\n=== All Redis operations completed successfully! ===');
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
  if (redis) {
    redis.quit();
  }
  console.log('Redis connection closed');
  process.exit(0);
});
