/**
 * Memory Bank Initialization Script
 * 
 * This script initializes the memory bank and registers tools with the MCP system.
 */

import { MemoryBank } from './memory-bank.js';
import { RedStream } from '../redis/build/redis/src/lib/redstream-es.js';

// Redis connection configuration
const REDIS_CONFIG = {
  url: 'redis://adapt-mcp-readwrite:adapt-mcp-readwrite-acc9582bc2eaead3@redis-cluster-01.memcommsops.internal:7000',
  clusterMode: true,
  clusterNodes: [
    { host: 'redis-cluster-01.memcommsops.internal', port: 7000 },
    { host: 'redis-cluster-02.memcommsops.internal', port: 7001 },
    { host: 'redis-cluster-03.memcommsops.internal', port: 7002 }
  ],
  username: 'adapt-mcp-readwrite',
  password: 'adapt-mcp-readwrite-acc9582bc2eaead3',
  scaleReads: 'slave',
  maxRedirections: 16,
  retryDelay: 300,
  connectTimeout: 5000,
  maxRetries: 3,
  namespacePrefix: 'adapt:',
  sharedNamespacePrefix: 'shared:'
};

// Initialize RedStream
async function initializeRedStream() {
  console.log('Initializing RedStream...');
  const redStream = new RedStream(REDIS_CONFIG);
  console.log('RedStream initialized successfully');
  return redStream;
}

// Initialize Memory Bank
async function initializeMemoryBank(redStream) {
  console.log('Initializing Memory Bank...');
  const memoryBank = new MemoryBank(redStream, 'redis_mcp_server');
  await memoryBank.initialize();
  console.log('Memory Bank initialized successfully');
  return memoryBank;
}

// Register tools with MCP system
async function registerTools(memoryBank) {
  console.log('Registering tools with MCP system...');
  
  // Store tool definitions in memory bank
  const tools = [
    'set',
    'get',
    'delete',
    'list',
    'stream_publish',
    'stream_read',
    'list_streams',
    'create_consumer_group',
    'read_group',
    'read_multiple_streams',
    'set_state',
    'get_state',
    'delete_state',
    'create_task',
    'get_task',
    'update_task',
    'complete_task',
    'list_tasks',
    'remember',
    'recall',
    'forget',
    'list_memories',
    'receive_all',
    'publish_message',
    'add_stream',
    'list_consumer_groups'
  ];
  
  // Store tool definitions in memory bank
  await memoryBank.storeMemory('mcp:tools', tools, {
    metadata: {
      server: 'redis_mcp_server',
      type: 'tool_definitions'
    }
  });
  
  console.log('Tools registered successfully');
}

// Main function
async function main() {
  try {
    const redStream = await initializeRedStream();
    const memoryBank = await initializeMemoryBank(redStream);
    await registerTools(memoryBank);
    console.log('Memory Bank initialization complete');
    process.exit(0);
  } catch (error) {
    console.error('Error initializing Memory Bank:', error);
    process.exit(1);
  }
}

// Run main function
main();