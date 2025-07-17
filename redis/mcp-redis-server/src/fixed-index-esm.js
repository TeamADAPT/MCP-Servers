#!/usr/bin/env node

// ES Modules version of the Redis MCP Server
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import Redis from 'ioredis';
import { z } from 'zod';

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
      port: parseInt(process.env.REDIS_PORT || '6380'),
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

// Define schema for list_tools
const listToolsRequestSchema = z.object({
  method: z.literal('list_tools')
});

// Define schema for list_resources
const listResourcesRequestSchema = z.object({
  method: z.literal('list_resources')
});

// Define schema for each tool
const callSetToolSchema = z.object({
  method: z.literal('call_tool'),
  params: z.object({
    name: z.literal('set'),
    arguments: z.object({
      key: z.string(),
      value: z.string(),
      ttl: z.number().optional()
    })
  })
});

const callGetToolSchema = z.object({
  method: z.literal('call_tool'),
  params: z.object({
    name: z.literal('get'),
    arguments: z.object({
      key: z.string()
    })
  })
});

const callDeleteToolSchema = z.object({
  method: z.literal('call_tool'),
  params: z.object({
    name: z.literal('delete'),
    arguments: z.object({
      key: z.string()
    })
  })
});

const callListToolSchema = z.object({
  method: z.literal('call_tool'),
  params: z.object({
    name: z.literal('list'),
    arguments: z.object({
      pattern: z.string().optional()
    }).optional()
  })
});

// Register handlers using schemas
server.setRequestHandler(listToolsRequestSchema, async () => {
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

server.setRequestHandler(listResourcesRequestSchema, async () => {
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

server.setRequestHandler(callSetToolSchema, async (request) => {
  try {
    const { key, value, ttl } = request.params.arguments;
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

server.setRequestHandler(callGetToolSchema, async (request) => {
  try {
    const { key } = request.params.arguments;
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

server.setRequestHandler(callDeleteToolSchema, async (request) => {
  try {
    const { key } = request.params.arguments;
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

server.setRequestHandler(callListToolSchema, async (request) => {
  try {
    const pattern = request.params?.arguments?.pattern || '*';
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
