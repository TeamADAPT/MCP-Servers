/**
 * Example Node.js script for connecting to Redis using the adapt-mcp-dev configuration
 * 
 * This script demonstrates how to:
 * 1. Load environment variables from config/.env.adapt-mcp-dev
 * 2. Connect to the Redis cluster
 * 3. Perform read/write operations on the adapt namespace
 * 4. Perform read-only operations on the shared namespace
 * 5. Handle errors and reconnections
 * 
 * Usage:
 * node examples/adapt_mcp_dev_redis_example.js
 */

// Load environment variables from .env file
require('dotenv').config({ path: './config/.env.adapt-mcp-dev' });

// Import ioredis
const Redis = require('ioredis');

// Parse Redis cluster nodes from environment variable
const nodes = process.env.REDIS_CLUSTER_NODES.split(',').map(node => {
  const [host, port] = node.split(':');
  return { host, port: parseInt(port, 10) };
});

// Create Redis cluster client
const cluster = new Redis.Cluster(nodes, {
  redisOptions: {
    username: process.env.REDIS_USERNAME,
    password: process.env.REDIS_PASSWORD,
    connectTimeout: parseInt(process.env.REDIS_CONNECT_TIMEOUT, 10),
    maxRetriesPerRequest: parseInt(process.env.REDIS_MAX_RETRIES, 10)
  },
  scaleReads: process.env.REDIS_SCALE_READS,
  maxRedirections: parseInt(process.env.REDIS_MAX_REDIRECTIONS, 10),
  retryDelayOnFailover: parseInt(process.env.REDIS_RETRY_DELAY, 10),
  enableAutoPipelining: true
});

// Set up event handlers
cluster.on('connect', () => {
  console.log('Connected to Redis cluster');
});

cluster.on('error', (err) => {
  console.error('Redis cluster error:', err);
});

cluster.on('node error', (err, node) => {
  console.error(`Redis node ${node.options.host}:${node.options.port} error:`, err);
});

cluster.on('reconnecting', () => {
  console.log('Reconnecting to Redis cluster...');
});

// Example operations
async function runExamples() {
  try {
    console.log('\n--- Redis Cluster Example for Adapt MCP-Dev ---\n');

    // 1. Write to adapt namespace
    const writeKey = `${process.env.REDIS_NAMESPACE_PREFIX}example:${Date.now()}`;
    const writeValue = `Example value created at ${new Date().toISOString()}`;
    
    console.log(`Writing to ${writeKey}...`);
    const writeResult = await cluster.set(writeKey, writeValue);
    console.log(`Write result: ${writeResult}`);

    // 2. Read from adapt namespace
    console.log(`Reading from ${writeKey}...`);
    const readResult = await cluster.get(writeKey);
    console.log(`Read result: ${readResult}`);

    // 3. Read from shared namespace
    const sharedKey = `${process.env.REDIS_SHARED_NAMESPACE_PREFIX}config:version`;
    console.log(`Reading from ${sharedKey}...`);
    const sharedResult = await cluster.get(sharedKey);
    console.log(`Shared config version: ${sharedResult || 'Not found'}`);

    // 4. Try to write to shared namespace (should fail)
    try {
      console.log(`Attempting to write to ${process.env.REDIS_SHARED_NAMESPACE_PREFIX}test (should fail)...`);
      await cluster.set(`${process.env.REDIS_SHARED_NAMESPACE_PREFIX}test`, 'This should fail');
      console.log('Write succeeded (unexpected)');
    } catch (err) {
      console.log(`Write to shared namespace failed as expected: ${err.message}`);
    }

    // 5. Use other Redis commands
    console.log('\nAdditional Redis commands:');
    
    // Set expiration
    await cluster.expire(writeKey, 3600);
    console.log(`Set expiration on ${writeKey} to 1 hour`);
    
    // Get TTL
    const ttl = await cluster.ttl(writeKey);
    console.log(`TTL for ${writeKey}: ${ttl} seconds`);
    
    // Increment a counter
    const counterKey = `${process.env.REDIS_NAMESPACE_PREFIX}counter:example`;
    const counterValue = await cluster.incr(counterKey);
    console.log(`Incremented ${counterKey} to ${counterValue}`);

    console.log('\nAll operations completed successfully!');
  } catch (err) {
    console.error('Error during Redis operations:', err);
  } finally {
    // Close the connection
    cluster.quit();
  }
}

// Run the examples
runExamples();