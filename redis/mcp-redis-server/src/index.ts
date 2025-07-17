#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import Redis from 'ioredis';

// Server setup
const server = new Server({
  name: 'redis',
  version: '1.0.0'
});

// Configure logging
const logger = {
  info: (message) => console.error(`[INFO] ${message}`),
  error: (message, error) => console.error(`[ERROR] ${message}`, error || '')
};

// Initialize Redis client
let redis;
try {
  // Parse connection string from command line if provided
  const connectionArg = process.argv[2];
  if (connectionArg && connectionArg.startsWith('redis://')) {
    logger.info(`Using connection string from command line: ${connectionArg}`);
    redis = new Redis(connectionArg);
  } else {
    // Use environment variables
    const config = {
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      username: process.env.REDIS_USERNAME,
      password: process.env.REDIS_PASSWORD
    };
    logger.info(`Connecting to Redis at ${config.host}:${config.port}`);
    redis = new Redis(config);
  }
} catch (error) {
  logger.error('Failed to initialize Redis client', error);
  process.exit(1);
}

// Helper to add namespace to keys
function prefixKey(key) {
  const prefix = process.env.REDIS_NAMESPACE_PREFIX || '';
  return prefix ? `${prefix}${key}` : key;
}

// Key-value operations
server.setRequestHandler({
  method: 'call_tool',
  params: {
    name: 'set'
  }
}, async (req) => {
  try {
    const { key, value, ttl } = req.params.arguments;
    let result;
    
    if (ttl) {
      result = await redis.set(prefixKey(key), value, 'EX', ttl);
    } else {
      result = await redis.set(prefixKey(key), value);
    }
    
    return {
      content: [
        { type: 'text', text: JSON.stringify({ success: result === 'OK', key }) }
      ]
    };
  } catch (error) {
    logger.error('Error in set operation', error);
    return {
      content: [
        { type: 'text', text: JSON.stringify({ error: 'Failed to set value' }) }
      ],
      isError: true
    };
  }
});

server.setRequestHandler({
  method: 'call_tool',
  params: {
    name: 'get'
  }
}, async (req) => {
  try {
    const { key } = req.params.arguments;
    const value = await redis.get(prefixKey(key));
    
    return {
      content: [
        { type: 'text', text: JSON.stringify({ key, value }) }
      ]
    };
  } catch (error) {
    logger.error('Error in get operation', error);
    return {
      content: [
        { type: 'text', text: JSON.stringify({ error: 'Failed to get value' }) }
      ],
      isError: true
    };
  }
});

server.setRequestHandler({
  method: 'call_tool',
  params: {
    name: 'delete'
  }
}, async (req) => {
  try {
    const { key } = req.params.arguments;
    const result = await redis.del(prefixKey(key));
    
    return {
      content: [
        { type: 'text', text: JSON.stringify({ success: result > 0, key }) }
      ]
    };
  } catch (error) {
    logger.error('Error in delete operation', error);
    return {
      content: [
        { type: 'text', text: JSON.stringify({ error: 'Failed to delete value' }) }
      ],
      isError: true
    };
  }
});

server.setRequestHandler({
  method: 'call_tool',
  params: {
    name: 'list'
  }
}, async (req) => {
  try {
    const pattern = req.params.arguments.pattern || '*';
    const keys = await redis.keys(prefixKey(pattern));
    
    const prefix = process.env.REDIS_NAMESPACE_PREFIX || '';
    const trimmedKeys = prefix 
      ? keys.map(key => key.startsWith(prefix) ? key.substring(prefix.length) : key)
      : keys;
    
    return {
      content: [
        { type: 'text', text: JSON.stringify({ keys: trimmedKeys }) }
      ]
    };
  } catch (error) {
    logger.error('Error in list operation', error);
    return {
      content: [
        { type: 'text', text: JSON.stringify({ error: 'Failed to list keys' }) }
      ],
      isError: true
    };
  }
});

// List tools
server.setRequestHandler({
  method: 'list_tools'
}, async () => {
  return {
    tools: [
      {
        name: 'set',
        description: 'Set a key-value pair in Redis',
        inputSchema: {
          type: 'object',
          properties: {
            key: { type: 'string', description: 'Key to set' },
            value: { type: 'string', description: 'Value to store' },
            ttl: { type: 'number', description: 'Time to live in seconds (optional)' }
          },
          required: ['key', 'value']
        }
      },
      {
        name: 'get',
        description: 'Get a value by key from Redis',
        inputSchema: {
          type: 'object',
          properties: {
            key: { type: 'string', description: 'Key to get' }
          },
          required: ['key']
        }
      },
      {
        name: 'delete',
        description: 'Delete a key from Redis',
        inputSchema: {
          type: 'object',
          properties: {
            key: { type: 'string', description: 'Key to delete' }
          },
          required: ['key']
        }
      },
      {
        name: 'list',
        description: 'List keys matching a pattern in Redis',
        inputSchema: {
          type: 'object',
          properties: {
            pattern: { type: 'string', description: 'Pattern to match keys', default: '*' }
          }
        }
      }
    ]
  };
});

// Register resources
server.setRequestHandler({
  method: 'list_resources'
}, async () => {
  return {
    resources: [
      {
        uri: 'task://{task_id}',
        name: 'Task Data',
        description: 'Direct access to a task\'s data'
      },
      {
        uri: 'stream://{stream_name}/latest',
        name: 'Latest Stream Messages',
        description: 'Access to the latest messages in a stream'
      },
      {
        uri: 'state://{key}',
        name: 'State Value',
        description: 'Access to a state value'
      }
    ]
  };
});

// Start the server
async function startServer() {
  try {
    // Set up Redis connection events
    redis.on('connect', () => {
      logger.info('Connected to Redis successfully');
    });
    
    redis.on('error', (err) => {
      logger.error('Redis connection error', err);
    });
    
    // Start the server
    logger.info('Starting Redis MCP Server...');
    const transport = new StdioServerTransport();
    await server.connect(transport);
    logger.info('Redis MCP Server running');
    
    // Handle shutdown
    process.on('SIGINT', async () => {
      logger.info('Shutting down Redis MCP Server');
      await redis.quit();
      await server.close();
      process.exit(0);
    });
  } catch (error) {
    logger.error('Error starting Redis MCP Server', error);
    process.exit(1);
  }
}

// Start the server
startServer().catch(error => {
  logger.error('Unhandled error in main', error);
  process.exit(1);
});
