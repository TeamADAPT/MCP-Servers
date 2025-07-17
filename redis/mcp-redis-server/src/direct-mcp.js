#!/usr/bin/env node

/**
 * Simple Redis MCP Server Implementation
 * Direct implementation that follows MCP protocol exactly
 */

const Redis = require('ioredis');

// Set up logger
const logger = {
  info: (msg) => console.error(`[INFO] ${msg}`),
  error: (msg, err) => console.error(`[ERROR] ${msg}`, err || '')
};

// Initialize Redis client
let redis;
try {
  const config = {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6380'),
    username: process.env.REDIS_USERNAME,
    password: process.env.REDIS_PASSWORD
  };
  logger.info(`Connecting to Redis at ${config.host}:${config.port}`);
  redis = new Redis(config);
} catch (error) {
  logger.error('Failed to initialize Redis client', error);
  process.exit(1);
}

// Helper to add namespace to keys
function prefixKey(key) {
  const prefix = process.env.REDIS_NAMESPACE_PREFIX || '';
  return prefix ? `${prefix}${key}` : key;
}

// Define the available tools
const TOOLS = [
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
];

// Define the available resources
const RESOURCES = [
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
];

// Handle requests
async function handleRequest(request) {
  try {
    const { id, method, params } = request;
    
    if (method === 'list_tools') {
      return {
        jsonrpc: '2.0',
        id,
        result: { tools: TOOLS }
      };
    }
    
    if (method === 'list_resources') {
      return {
        jsonrpc: '2.0',
        id,
        result: { resources: RESOURCES }
      };
    }
    
    if (method === 'call_tool') {
      const { name, arguments: args } = params;
      
      if (name === 'set') {
        const { key, value, ttl } = args;
        let result;
        
        if (ttl) {
          result = await redis.set(prefixKey(key), value, 'EX', ttl);
        } else {
          result = await redis.set(prefixKey(key), value);
        }
        
        return {
          jsonrpc: '2.0',
          id,
          result: {
            content: [
              { type: 'text', text: JSON.stringify({ success: result === 'OK', key }) }
            ]
          }
        };
      }
      
      if (name === 'get') {
        const { key } = args;
        const value = await redis.get(prefixKey(key));
        
        return {
          jsonrpc: '2.0',
          id,
          result: {
            content: [
              { type: 'text', text: JSON.stringify({ key, value }) }
            ]
          }
        };
      }
      
      if (name === 'delete') {
        const { key } = args;
        const result = await redis.del(prefixKey(key));
        
        return {
          jsonrpc: '2.0',
          id,
          result: {
            content: [
              { type: 'text', text: JSON.stringify({ success: result > 0, key }) }
            ]
          }
        };
      }
      
      if (name === 'list') {
        const pattern = args?.pattern || '*';
        const keys = await redis.keys(prefixKey(pattern));
        
        const prefix = process.env.REDIS_NAMESPACE_PREFIX || '';
        const trimmedKeys = prefix 
          ? keys.map(key => key.startsWith(prefix) ? key.substring(prefix.length) : key)
          : keys;
        
        return {
          jsonrpc: '2.0',
          id,
          result: {
            content: [
              { type: 'text', text: JSON.stringify({ keys: trimmedKeys }) }
            ]
          }
        };
      }
      
      // Tool not found
      return {
        jsonrpc: '2.0',
        id,
        error: {
          code: -32601,
          message: `Tool '${name}' not found`
        }
      };
    }
    
    // Method not found
    return {
      jsonrpc: '2.0',
      id,
      error: {
        code: -32601,
        message: `Method '${method}' not found`
      }
    };
    
  } catch (error) {
    logger.error('Error processing request', error);
    return {
      jsonrpc: '2.0',
      id: request.id,
      error: {
        code: -32000,
        message: `Internal error: ${error.message}`
      }
    };
  }
}

// Set up Redis connection events
redis.on('connect', () => {
  logger.info('Connected to Redis successfully');
});

redis.on('error', (err) => {
  logger.error('Redis connection error', err);
});

// Start the server
async function startServer() {
  try {
    logger.info('Starting Redis MCP Server...');
    
    // Process stdin/stdout for communication
    process.stdin.setEncoding('utf8');
    
    let buffer = '';
    process.stdin.on('data', async (chunk) => {
      buffer += chunk;
      const lines = buffer.split('\n');
      
      // Process all complete lines
      for (let i = 0; i < lines.length - 1; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        try {
          const request = JSON.parse(line);
          const response = await handleRequest(request);
          process.stdout.write(JSON.stringify(response) + '\n');
        } catch (error) {
          logger.error('Error processing request', error);
          if (line) {
            try {
              const requestId = JSON.parse(line).id;
              process.stdout.write(JSON.stringify({
                jsonrpc: '2.0',
                id: requestId,
                error: {
                  code: -32700,
                  message: 'Parse error'
                }
              }) + '\n');
            } catch (e) {
              // Can't extract ID, no response
            }
          }
        }
      }
      
      // Keep the incomplete line in the buffer
      buffer = lines[lines.length - 1];
    });
    
    logger.info('Redis MCP Server running');
    
    // Handle shutdown
    process.on('SIGINT', async () => {
      logger.info('Shutting down Redis MCP Server');
      await redis.quit();
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
