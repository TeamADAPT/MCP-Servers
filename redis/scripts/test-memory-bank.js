#!/usr/bin/env node

/**
 * Test Memory Bank Functionality
 * 
 * This script tests the memory bank functionality of the Redis MCP server.
 * It connects to the Redis server and performs various memory operations.
 */

const { RedStream } = require('../src/redis-streams/redstream.js');

// Memory bank stream name
const MEMORY_BANK_STREAM = 'nova:memory:redis:bank';
const MEMORY_STATE_PREFIX = 'memory:';

// Test configuration
const TEST_KEY = 'test_memory_' + Date.now();
const TEST_VALUE = {
  message: 'Hello from Memory Bank Test',
  timestamp: new Date().toISOString(),
  test_run: true
};

// Initialize RedStream
async function initRedStream() {
  console.log('Initializing RedStream...');
  
  try {
    // Import the TypeScript version which has the create method
    const { RedStream } = require('../src/redis-streams/redstream.ts');
    
    const redStream = await RedStream.create({
      serverIdentity: 'memory_bank_test',
      roles: ['memory_read', 'memory_write', 'system_read', 'system_write'],
      nodes: [
        { host: '127.0.0.1', port: 7000 },
        { host: '127.0.0.1', port: 7001 },
        { host: '127.0.0.1', port: 7002 }
      ],
      clusterOptions: {
        password: 'd5d7817937232ca5',
        enableReadyCheck: true,
        scaleReads: 'slave',
        maxRedirections: 16
      }
    });
    
    console.log('RedStream initialized successfully');
    return redStream;
  } catch (error) {
    console.error('Error initializing RedStream:', error);
    throw error;
  }
}

// Store a memory
async function storeMemory(redStream, key, value) {
  console.log(`Storing memory with key: ${key}`);
  
  try {
    // Store in Redis state
    await redStream.setState(`${MEMORY_STATE_PREFIX}${key}`, value);
    
    // Publish to memory bank stream for tracking
    const messageId = await redStream.publishMessage(MEMORY_BANK_STREAM, {
      type: 'memory_stored',
      key,
      category: 'test',
      priority: 'medium',
      stored_at: new Date().toISOString(),
      stored_by: 'memory_bank_test'
    });
    
    console.log(`Memory stored with message ID: ${messageId}`);
    return messageId;
  } catch (error) {
    console.error(`Error storing memory ${key}:`, error);
    throw error;
  }
}

// Retrieve a memory
async function retrieveMemory(redStream, key) {
  console.log(`Retrieving memory with key: ${key}`);
  
  try {
    const result = await redStream.getState(`${MEMORY_STATE_PREFIX}${key}`);
    
    // Publish memory access to stream for tracking
    if (result.value !== null) {
      await redStream.publishMessage(MEMORY_BANK_STREAM, {
        type: 'memory_accessed',
        key,
        accessed_at: new Date().toISOString(),
        accessed_by: 'memory_bank_test'
      });
    }
    
    console.log(`Memory retrieved:`, result.value);
    return result.value;
  } catch (error) {
    console.error(`Error retrieving memory ${key}:`, error);
    throw error;
  }
}

// List memories
async function listMemories(redStream) {
  console.log('Listing memories...');
  
  try {
    // Get all memory keys from Redis
    const pattern = `${MEMORY_STATE_PREFIX}*`;
    const keys = await redStream.listStreams(pattern);
    
    // Return all keys without the prefix
    const memoryKeys = keys.map(key => key.replace(MEMORY_STATE_PREFIX, ''));
    console.log('Memory keys:', memoryKeys);
    return memoryKeys;
  } catch (error) {
    console.error('Error listing memories:', error);
    throw error;
  }
}

// Delete a memory
async function deleteMemory(redStream, key) {
  console.log(`Deleting memory with key: ${key}`);
  
  try {
    await redStream.deleteState(`${MEMORY_STATE_PREFIX}${key}`);
    
    // Publish memory deletion to stream for tracking
    await redStream.publishMessage(MEMORY_BANK_STREAM, {
      type: 'memory_deleted',
      key,
      deleted_at: new Date().toISOString(),
      deleted_by: 'memory_bank_test'
    });
    
    console.log(`Memory deleted: ${key}`);
  } catch (error) {
    console.error(`Error deleting memory ${key}:`, error);
    throw error;
  }
}

// Check memory bank stream
async function checkMemoryBankStream(redStream) {
  console.log('Checking memory bank stream...');
  
  try {
    const messages = await redStream.readMessages(MEMORY_BANK_STREAM, {
      count: 10,
      reverse: true
    });
    
    console.log('Memory bank stream messages:');
    messages.forEach((msg, index) => {
      console.log(`[${index + 1}] ${msg.type} - ${msg.key || 'N/A'} (${msg._timestamp})`);
    });
    
    return messages;
  } catch (error) {
    console.error('Error checking memory bank stream:', error);
    throw error;
  }
}

// Run all tests
async function runTests() {
  let redStream;
  
  try {
    // Initialize RedStream
    redStream = await initRedStream();
    
    // Check memory bank stream
    await checkMemoryBankStream(redStream);
    
    // Store a memory
    await storeMemory(redStream, TEST_KEY, TEST_VALUE);
    
    // Retrieve the memory
    const retrievedValue = await retrieveMemory(redStream, TEST_KEY);
    
    // Verify the retrieved value
    if (JSON.stringify(retrievedValue) === JSON.stringify(TEST_VALUE)) {
      console.log('✅ Memory retrieval test passed');
    } else {
      console.error('❌ Memory retrieval test failed');
      console.error('Expected:', TEST_VALUE);
      console.error('Received:', retrievedValue);
    }
    
    // List memories
    await listMemories(redStream);
    
    // Delete the memory
    await deleteMemory(redStream, TEST_KEY);
    
    // Verify deletion
    const deletedValue = await retrieveMemory(redStream, TEST_KEY);
    if (deletedValue === null) {
      console.log('✅ Memory deletion test passed');
    } else {
      console.error('❌ Memory deletion test failed');
      console.error('Memory still exists:', deletedValue);
    }
    
    // Check memory bank stream again
    await checkMemoryBankStream(redStream);
    
    console.log('All tests completed successfully');
  } catch (error) {
    console.error('Test failed:', error);
  } finally {
    // Close RedStream connection
    if (redStream) {
      await redStream.close();
      console.log('RedStream connection closed');
    }
  }
}

// Run the tests
runTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});