#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema, McpError, ErrorCode } from '@modelcontextprotocol/sdk/types.js';
import { createClient } from 'redis';
import { executeTool } from './tools/index.js';
import net from 'net';
// Initialize Redis client
const redis = createClient({
    socket: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6380'),
    },
});
redis.on('error', (error) => {
    console.error('Redis error:', error);
});
// Create MCP server with empty tools object
const server = new Server({
    name: 'red-stream',
    version: '0.2.0',
}, {
    capabilities: {
        tools: {},
    },
});
// Ensure Redis connection
async function ensureConnection() {
    if (!redis.isOpen) {
        try {
            await redis.connect();
        }
        catch (error) {
            throw new McpError(ErrorCode.InternalError, `Failed to connect to Redis: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
}
// Register tools through ListToolsRequestSchema handler
server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
        {
            name: 'get_stream_messages',
            description: 'Get messages from a Redis Stream',
            inputSchema: {
                type: 'object',
                properties: {
                    stream: { type: 'string', description: 'Name of the stream' },
                    count: { type: 'number', description: 'Number of messages to retrieve', default: 1 },
                    start: { type: 'string', description: 'Start ID (0 for beginning, $ for end)', default: '0' },
                },
                required: ['stream'],
            },
        },
        {
            name: 'list_streams',
            description: 'List all available Redis streams',
            inputSchema: {
                type: 'object',
                properties: {
                    pattern: { type: 'string', description: 'Pattern to match stream names (e.g., "user:*")', default: '*' },
                },
            },
        },
        {
            name: 'add_stream_message',
            description: 'Adds a new message to a stream',
            inputSchema: {
                type: 'object',
                properties: {
                    stream: { type: 'string', description: 'Name of the stream' },
                    message: { type: 'object', description: 'Message content' },
                },
                required: ['stream', 'message'],
            },
        },
        {
            name: 'list_groups',
            description: 'Lists all consumer groups for a specified stream',
            inputSchema: {
                type: 'object',
                properties: {
                    stream: { type: 'string', description: 'Name of the stream' },
                },
                required: ['stream'],
            },
        },
        {
            name: 'create_consumer_group',
            description: 'Creates a new consumer group for a stream',
            inputSchema: {
                type: 'object',
                properties: {
                    stream: { type: 'string', description: 'Name of the stream' },
                    group: { type: 'string', description: 'Consumer group name' },
                    start: { type: 'string', description: 'Start position (default: "$")', default: '$' },
                },
                required: ['stream', 'group'],
            },
        },
        {
            name: 'read_group',
            description: 'Reads messages from a stream as a consumer group',
            inputSchema: {
                type: 'object',
                properties: {
                    stream: { type: 'string', description: 'Name of the stream' },
                    group: { type: 'string', description: 'Consumer group name' },
                    consumer: { type: 'string', description: 'Consumer name' },
                    count: { type: 'number', description: 'Number of messages (default: 1)', default: 1 },
                },
                required: ['stream', 'group', 'consumer'],
            },
        },
    ],
}));
// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    try {
        await ensureConnection();
        return await executeTool(request.params.name, redis, request.params.arguments);
    }
    catch (error) {
        if (error instanceof McpError) {
            throw error;
        }
        throw new McpError(ErrorCode.InternalError, `Tool execution failed: ${error instanceof Error ? error.message : String(error)}`);
    }
});
// Handle errors
server.onerror = (error) => {
    console.error('[MCP Error]', error);
};
// Handle shutdown
async function shutdown() {
    console.error('Shutting down...');
    try {
        if (redis.isOpen) {
            await redis.quit();
        }
        await server.close();
    }
    catch (shutdownError) {
        console.error('Error during shutdown:', shutdownError);
    }
    process.exit(0);
}
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
// Check if we're running under systemd socket activation
const listenFds = process.env.LISTEN_FDS ? parseInt(process.env.LISTEN_FDS, 10) : 0;
if (listenFds > 0) {
    const netServer = net.createServer((socket) => {
        const transport = new StdioServerTransport(socket, socket);
        server.connect(transport).catch(console.error);
    });
    // Socket activation - fd starts at 3
    netServer.listen({ fd: 3 }, () => {
        console.error('RedStream MCP server running on systemd socket');
    });
}
else {
    // Fallback to standard stdio
    const transport = new StdioServerTransport();
    server.connect(transport).catch((startupError) => {
        console.error('Failed to start server:', startupError);
        process.exit(1);
    });
    console.error('RedStream MCP server running on stdio');
}
