/**
 * Redis MCP Server
 *
 * Provides Redis-based tools and resources for the MCP system
 */

// Type definitions for MCP Server
interface IMCPServer {
  registerTool: (tool: MCPToolDefinition) => void;
  registerResource: (resource: MCPResourceDefinition) => void;
  start: () => Promise<void>;
  stop: () => Promise<void>;
}

interface MCPToolDefinition {
  name: string;
  description: string;
  inputSchema: any;
  handler: (args: any) => Promise<any>;
}

interface MCPResourceDefinition {
  uriPattern: string;
  description: string;
  handler: (args: any) => Promise<any>;
}

// Memory bank options interface
interface MemoryOptions {
  ttl?: number;
  metadata?: Record<string, any>;
  log?: boolean;
}

// Mock MCPServer class for development
class MCPServer implements IMCPServer {
  name: string;
  version: string;
  description: string;

  constructor(options: { name: string; version: string; description: string }) {
    this.name = options.name;
    this.version = options.version;
    this.description = options.description;
    console.log(`Initializing MCP Server: ${this.name} v${this.version}`);
  }

  registerTool(tool: MCPToolDefinition): void {
    console.log(`Registered tool: ${tool.name}`);
  }

  registerResource(resource: MCPResourceDefinition): void {
    console.log(`Registered resource: ${resource.uriPattern}`);
  }

  async start(): Promise<void> {
    console.log(`Started MCP Server: ${this.name}`);
    return Promise.resolve();
  }

  async stop(): Promise<void> {
    console.log(`Stopped MCP Server: ${this.name}`);
    return Promise.resolve();
  }
}

// Import RedStream and MemoryBank
import { RedStream } from './lib/redstream-es.js';
import { MemoryBank } from '../memory-bank.js';

// Initialize Redis connection and memory bank
let redStream: RedStream;
let memoryBank: MemoryBank;
let serverIdentity = 'redis_mcp_server';

// Define tool schemas
const toolSchemas = {
  // Task operations
  get_task: {
    type: 'object',
    properties: {
      task_id: {
        type: 'string',
        description: 'Task ID to retrieve'
      }
    },
    required: ['task_id']
  },
  
  // Stream operations
  publish_message: {
    type: 'object',
    properties: {
      stream: {
        type: 'string',
        description: 'Stream name to publish to'
      },
      message: {
        type: 'object',
        description: 'Message object to publish'
      },
      maxlen: {
        type: 'number',
        description: 'Maximum length of stream (optional)'
      }
    },
    required: ['stream', 'message']
  },
  
  read_stream: {
    type: 'object',
    properties: {
      stream: {
        type: 'string',
        description: 'Stream name to read from'
      },
      start: {
        type: 'string',
        description: 'Start ID (default: 0)',
        default: '0'
      },
      end: {
        type: 'string',
        description: 'End ID (default: +)',
        default: '+'
      },
      count: {
        type: 'number',
        description: 'Maximum number of messages to read'
      }
    },
    required: ['stream']
  },
  
  create_consumer_group: {
    type: 'object',
    properties: {
      stream: {
        type: 'string',
        description: 'Stream name'
      },
      group: {
        type: 'string',
        description: 'Consumer group name'
      },
      startId: {
        type: 'string',
        description: 'Start ID (default: $)',
        default: '$'
      },
      mkstream: {
        type: 'boolean',
        description: 'Create stream if it doesn\'t exist',
        default: true
      }
    },
    required: ['stream', 'group']
  },
  
  // Memory operations
  store_memory: {
    type: 'object',
    properties: {
      key: {
        type: 'string',
        description: 'Memory key'
      },
      value: {
        type: 'object',
        description: 'Memory value'
      },
      ttl: {
        type: 'number',
        description: 'Time to live in seconds (optional)'
      },
      metadata: {
        type: 'object',
        description: 'Additional metadata (optional)'
      }
    },
    required: ['key', 'value']
  },
  
  retrieve_memory: {
    type: 'object',
    properties: {
      key: {
        type: 'string',
        description: 'Memory key'
      }
    },
    required: ['key']
  },
  
  delete_memory: {
    type: 'object',
    properties: {
      key: {
        type: 'string',
        description: 'Memory key'
      }
    },
    required: ['key']
  },
  
  list_memories: {
    type: 'object',
    properties: {
      pattern: {
        type: 'string',
        description: 'Pattern to match memory keys',
        default: '*'
      }
    }
  },
  
  // State operations
  set_state: {
    type: 'object',
    properties: {
      key: {
        type: 'string',
        description: 'State key'
      },
      value: {
        type: 'object',
        description: 'State value'
      },
      ttl: {
        type: 'number',
        description: 'Time to live in seconds (optional)'
      }
    },
    required: ['key', 'value']
  },
  
  get_state: {
    type: 'object',
    properties: {
      key: {
        type: 'string',
        description: 'State key'
      }
    },
    required: ['key']
  },
  
  delete_state: {
    type: 'object',
    properties: {
      key: {
        type: 'string',
        description: 'State key'
      }
    },
    required: ['key']
  }
};

// Initialize MCP server
const server = new MCPServer({
  name: 'redis',
  version: '1.0.0',
  description: 'Redis MCP Server for streams, memory, and state management'
});

// Initialize Redis connection and memory bank
async function initializeRedis() {
  try {
    // Create RedStream instance
    redStream = new RedStream({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6380'),
      serverIdentity
    });
    
    // Create MemoryBank instance
    memoryBank = new MemoryBank(redStream, serverIdentity);
    await memoryBank.initialize();
    
    console.log('Redis connection and memory bank initialized');
    return true;
  } catch (error) {
    console.error('Error initializing Redis:', error);
    return false;
  }
}

// Helper function to get error message
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}

// Register tools
function registerTools() {
  // Task operations
  server.registerTool({
    name: 'get_task',
    description: 'Get task data from Redis',
    inputSchema: toolSchemas.get_task,
    handler: async ({ task_id }: { task_id: string }) => {
      try {
        const taskKey = `task:${task_id}`;
        const result = await redStream.getState(taskKey);
        return result?.value || null;
      } catch (error) {
        console.error(`Error getting task ${task_id}:`, error);
        throw new Error(`Failed to get task: ${getErrorMessage(error)}`);
      }
    }
  });
  
  // Stream operations
  server.registerTool({
    name: 'publish_message',
    description: 'Publish a message to a Redis stream',
    inputSchema: toolSchemas.publish_message,
    handler: async ({ stream, message, maxlen }: { stream: string; message: any; maxlen?: number }) => {
      try {
        const messageId = await redStream.publishMessage(stream, message, maxlen);
        return { success: true, message_id: messageId };
      } catch (error) {
        console.error(`Error publishing to stream ${stream}:`, error);
        throw new Error(`Failed to publish message: ${getErrorMessage(error)}`);
      }
    }
  });
  
  server.registerTool({
    name: 'read_stream',
    description: 'Read messages from a Redis stream',
    inputSchema: toolSchemas.read_stream,
    handler: async ({ stream, start, end, count }: { stream: string; start?: string; end?: string; count?: number }) => {
      try {
        const messages = await redStream.readMessages(stream, start, end, count);
        return { success: true, messages };
      } catch (error) {
        console.error(`Error reading from stream ${stream}:`, error);
        throw new Error(`Failed to read stream: ${getErrorMessage(error)}`);
      }
    }
  });
  
  server.registerTool({
    name: 'create_consumer_group',
    description: 'Create a consumer group for a Redis stream',
    inputSchema: toolSchemas.create_consumer_group,
    handler: async ({ stream, group, startId, mkstream }: { stream: string; group: string; startId?: string; mkstream?: boolean }) => {
      try {
        const success = await redStream.createConsumerGroup(stream, group, { startId, mkstream });
        return { success };
      } catch (error) {
        console.error(`Error creating consumer group ${group} for stream ${stream}:`, error);
        throw new Error(`Failed to create consumer group: ${getErrorMessage(error)}`);
      }
    }
  });
  
  // Memory operations
  server.registerTool({
    name: 'store_memory',
    description: 'Store a memory in Redis',
    inputSchema: toolSchemas.store_memory,
    handler: async ({ key, value, ttl, metadata }: { key: string; value: any; ttl?: number; metadata?: any }) => {
      try {
        const success = await memoryBank.storeMemory(key, value, { ttl, metadata });
        return { success };
      } catch (error) {
        console.error(`Error storing memory ${key}:`, error);
        throw new Error(`Failed to store memory: ${getErrorMessage(error)}`);
      }
    }
  });
  
  server.registerTool({
    name: 'retrieve_memory',
    description: 'Retrieve a memory from Redis',
    inputSchema: toolSchemas.retrieve_memory,
    handler: async ({ key }: { key: string }) => {
      try {
        const memory = await memoryBank.retrieveMemory(key);
        return memory;
      } catch (error) {
        console.error(`Error retrieving memory ${key}:`, error);
        throw new Error(`Failed to retrieve memory: ${getErrorMessage(error)}`);
      }
    }
  });
  
  server.registerTool({
    name: 'delete_memory',
    description: 'Delete a memory from Redis',
    inputSchema: toolSchemas.delete_memory,
    handler: async ({ key }: { key: string }) => {
      try {
        const success = await memoryBank.deleteMemory(key);
        return { success };
      } catch (error) {
        console.error(`Error deleting memory ${key}:`, error);
        throw new Error(`Failed to delete memory: ${getErrorMessage(error)}`);
      }
    }
  });
  
  server.registerTool({
    name: 'list_memories',
    description: 'List memories in Redis with optional pattern matching',
    inputSchema: toolSchemas.list_memories,
    handler: async ({ pattern }: { pattern?: string }) => {
      try {
        const keys = await memoryBank.listMemories(pattern);
        return { keys };
      } catch (error) {
        console.error('Error listing memories:', error);
        throw new Error(`Failed to list memories: ${getErrorMessage(error)}`);
      }
    }
  });
  
  // State operations
  server.registerTool({
    name: 'set_state',
    description: 'Set a state value in Redis',
    inputSchema: toolSchemas.set_state,
    handler: async ({ key, value, ttl }: { key: string; value: any; ttl?: number }) => {
      try {
        await redStream.setState(key, value, ttl);
        return { success: true };
      } catch (error) {
        console.error(`Error setting state ${key}:`, error);
        throw new Error(`Failed to set state: ${getErrorMessage(error)}`);
      }
    }
  });
  server.registerTool({
    name: 'get_state',
    description: 'Get a state value from Redis',
    inputSchema: toolSchemas.get_state,
    handler: async ({ key }: { key: string }) => {
      try {
        const result = await redStream.getState(key);
        return result;
      } catch (error) {
        console.error(`Error getting state ${key}:`, error);
        throw new Error(`Failed to get state: ${getErrorMessage(error)}`);
      }
    }
  });
  
  server.registerTool({
    name: 'delete_state',
    description: 'Delete a state value from Redis',
    inputSchema: toolSchemas.delete_state,
    handler: async ({ key }: { key: string }) => {
      try {
        await redStream.deleteState(key);
        return { success: true };
      } catch (error) {
        console.error(`Error deleting state ${key}:`, error);
        throw new Error(`Failed to delete state: ${getErrorMessage(error)}`);
      }
    }
  });
}

// Register resources
function registerResources() {
  // Task resource
  server.registerResource({
    uriPattern: 'task://{task_id}',
    description: 'Task Data',
    handler: async ({ task_id }: { task_id: string }) => {
      try {
        const taskKey = `task:${task_id}`;
        const result = await redStream.getState(taskKey);
        return result?.value || null;
      } catch (error) {
        console.error(`Error accessing task resource ${task_id}:`, error);
        throw new Error(`Failed to access task resource: ${getErrorMessage(error)}`);
      }
    }
  });
  
  // Stream resource
  server.registerResource({
    uriPattern: 'stream://{stream_name}/latest',
    description: 'Latest Stream Messages',
    handler: async ({ stream_name }: { stream_name: string }) => {
      try {
        // Get the latest 10 messages from the stream
        const messages = await redStream.readMessages(stream_name, '-', '+', 10);
        return messages;
      } catch (error) {
        console.error(`Error accessing stream resource ${stream_name}:`, error);
        throw new Error(`Failed to access stream resource: ${getErrorMessage(error)}`);
      }
    }
  });
  
  // State resource
  server.registerResource({
    uriPattern: 'state://{key}',
    description: 'State Value',
    handler: async ({ key }: { key: string }) => {
      try {
        const result = await redStream.getState(key);
        return result;
      } catch (error) {
        console.error(`Error accessing state resource ${key}:`, error);
        throw new Error(`Failed to access state resource: ${getErrorMessage(error)}`);
      }
    }
  });
}

// Start the server
async function startServer() {
  try {
    // Initialize Redis
    const redisInitialized = await initializeRedis();
    if (!redisInitialized) {
      console.error('Failed to initialize Redis, exiting');
      process.exit(1);
    }
    
    // Register tools and resources
    registerTools();
    registerResources();
    
    // Start the server
    await server.start();
    console.log('Redis MCP Server started');
    
    // Handle shutdown
    process.on('SIGINT', async () => {
      console.log('Shutting down Redis MCP Server');
      await redStream.close();
      await server.stop();
      process.exit(0);
    });
  } catch (error) {
    console.error('Error starting Redis MCP Server:', error);
    process.exit(1);
  }
}

// Start the server
startServer();
