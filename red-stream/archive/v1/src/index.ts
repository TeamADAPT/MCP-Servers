#!/usr/bin/env node
import { Server as McpServer } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ErrorCode, ListToolsRequestSchema, McpError } from '@modelcontextprotocol/sdk/types.js';
import { createClient, RedisClientType, RedisClientOptions, RedisModules, RedisFunctions, RedisScripts, RedisCommandArgument } from 'redis';
import { listGroups } from './tools/listGroups.js';
import { listStreams } from './tools/listStreams.js';
import net from 'net';

interface ToolDefinition {
    description: string;
    inputSchema: {
        type: string;
        properties: Record<string, unknown>;
        required?: string[];
    };
}

interface ServerCapabilities {
    tools: {
        [key: string]: ToolDefinition;
    };
}

class RedStreamServer {
    private readonly server: McpServer<any, ServerCapabilities>;
    private readonly redis: RedisClientType;
    private keepAlive: boolean;

    constructor() {
        console.error('Initializing RedStream server...');
        console.error('Setting up tools...');
        this.keepAlive = true;
        
        const tools = {
            get_stream_messages: {
                description: 'Get messages from a Redis Stream',
                inputSchema: {
                    type: 'object',
                    properties: {
                        stream: { type: 'string', description: 'Stream name' },
                        count: { type: 'number', description: 'Number of messages to retrieve', default: 1 },
                        start: { type: 'string', description: 'Start ID (0 for beginning, $ for end)', default: '0' },
                    },
                    required: ['stream'],
                },
            },
            add_stream_message: {
                description: 'Add a message to a Redis Stream',
                inputSchema: {
                    type: 'object',
                    properties: {
                        stream: { type: 'string', description: 'Stream name' },
                        message: { type: 'object', description: 'Message content' },
                    },
                    required: ['stream', 'message'],
                },
            },
            create_consumer_group: {
                description: 'Create a consumer group for a stream',
                inputSchema: {
                    type: 'object',
                    properties: {
                        stream: { type: 'string', description: 'Stream name' },
                        group: { type: 'string', description: 'Consumer group name' },
                        start: { type: 'string', description: 'Start ID (0 for beginning, $ for end)', default: '$' },
                    },
                    required: ['stream', 'group'],
                },
            },
            read_group: {
                description: 'Read messages as a consumer group',
                inputSchema: {
                    type: 'object',
                    properties: {
                        stream: { type: 'string', description: 'Stream name' },
                        group: { type: 'string', description: 'Consumer group name' },
                        consumer: { type: 'string', description: 'Consumer name' },
                        count: { type: 'number', description: 'Number of messages to retrieve', default: 1 },
                    },
                    required: ['stream', 'group', 'consumer'],
                },
            },
            list_groups: {
                description: 'List all consumer groups for a stream',
                inputSchema: {
                    type: 'object',
                    properties: {
                        stream: { type: 'string', description: 'Stream name' },
                    },
                    required: ['stream'],
                },
            },
            list_streams: {
                description: 'List all available streams',
                inputSchema: {
                    type: 'object',
                    properties: {
                        pattern: { type: 'string', description: 'Pattern to match stream names', default: '*' },
                    },
                },
            },
        };

        console.error('Available tools:', Object.keys(tools));
        
        this.server = new McpServer(
            {
                name: 'red-stream',
                version: '0.2.0',
            },
            {
                capabilities: {
                    tools,
                },
            }
        );

        this.redis = createClient<RedisModules, RedisFunctions, RedisScripts>({
            socket: {
                host: process.env.REDIS_HOST || 'localhost',
                port: parseInt(process.env.REDIS_PORT || '6379'),
            },
            password: process.env.REDIS_PASSWORD,
        });

        this.setupRequestHandlers();
        this.setupErrorHandler();
    }

    private setupRequestHandlers(): void {
        console.error('Setting up request handlers...');
        
        this.server.setRequestHandler(ListToolsRequestSchema, async () => {
            const tools = Object.entries(
                (this.server as any).options?.capabilities?.tools || {}
            ).map(([name, def]) => ({
                name,
                description: (def as ToolDefinition).description,
                inputSchema: (def as ToolDefinition).inputSchema,
            }));
            
            console.error('Listing tools:', tools.map(t => t.name));
            return { tools };
        });

        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            console.error('Handling tool request:', request.params.name);
            console.error('Tool arguments:', request.params.arguments);
            
            await this.ensureConnection();

            switch (request.params.name) {
                case 'get_stream_messages':
                    return this.getStreamMessages(request.params.arguments as { stream: string; count?: number; start?: string });
                case 'add_stream_message':
                    return this.addStreamMessage(request.params.arguments as { stream: string; message: Record<string, RedisCommandArgument> });
                case 'create_consumer_group':
                    return this.createConsumerGroup(request.params.arguments as { stream: string; group: string; start?: string });
                case 'read_group':
                    return this.readGroup(request.params.arguments as { stream: string; group: string; consumer: string; count?: number });
                case 'list_groups':
                    return this.listGroups(request.params.arguments as { stream: string });
                case 'list_streams':
                    return this.listStreams(request.params.arguments as { pattern?: string });
                default:
                    throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${request.params.name}`);
            }
        });
    }

    private async ensureConnection(): Promise<void> {
        if (!this.redis.isOpen) {
            await this.redis.connect();
        }
    }

    private setupErrorHandler(): void {
        this.server.onerror = (error) => {
            console.error('[MCP Error]', error);
        };

        process.on('uncaughtException', (error) => {
            console.error('[Uncaught Exception]', error);
            void this.handleError(error);
        });

        process.on('unhandledRejection', (error) => {
            console.error('[Unhandled Rejection]', error);
            void this.handleError(error);
        });
    }

    private async handleError(error: unknown): Promise<void> {
        try {
            await this.cleanup();
        } catch (cleanupError) {
            console.error('[Cleanup Error]', cleanupError);
        }
        if (this.keepAlive) {
            console.error('Attempting to reconnect...');
            await this.reconnect();
        }
    }

    private async cleanup(): Promise<void> {
        try {
            if (this.redis.isOpen) {
                await this.redis.quit();
            }
            await this.server.close();
        } catch (error) {
            console.error('[Cleanup Error]', error);
        }
    }

    private async reconnect(): Promise<void> {
        try {
            const transport = new StdioServerTransport();
            await this.server.connect(transport);
            console.error('RedStream MCP server reconnected');
        } catch (error) {
            console.error('[Reconnection Error]', error);
            if (this.keepAlive) {
                setTimeout(() => void this.reconnect(), 5000);
            }
        }
    }

    private async getStreamMessages(args: { stream: string; count?: number; start?: string }) {
        const messages = await this.redis.xRead(
            [{ key: args.stream, id: args.start || '0' }],
            { COUNT: args.count || 1 }
        );
        return {
            content: [{ type: 'text', text: JSON.stringify(messages || [], null, 2) }],
        };
    }

    private async addStreamMessage(args: { stream: string; message: Record<string, RedisCommandArgument> }) {
        const id = await this.redis.xAdd(args.stream, '*', args.message as Record<string, RedisCommandArgument>);
        return {
            content: [{ type: 'text', text: JSON.stringify({ id }, null, 2) }],
        };
    }

    private async createConsumerGroup(args: { stream: string; group: string; start?: string }) {
        try {
            await this.redis.xGroupCreate(args.stream, args.group, args.start || '$', { MKSTREAM: true });
            return {
                content: [{ type: 'text', text: JSON.stringify({ success: true }, null, 2) }],
            };
        } catch (error: any) {
            if (error.message.includes('BUSYGROUP')) {
                return {
                    content: [{ type: 'text', text: JSON.stringify({ success: true, note: 'Group already exists' }, null, 2) }],
                };
            }
            throw error;
        }
    }

    private async readGroup(args: { stream: string; group: string; consumer: string; count?: number }) {
        const messages = await this.redis.xReadGroup(
            args.group,
            args.consumer,
            [{ key: args.stream, id: '>' }],
            { COUNT: args.count || 1 }
        );
        return {
            content: [{ type: 'text', text: JSON.stringify(messages || [], null, 2) }],
        };
    }

    private async listGroups(args: { stream: string }) {
        const result = await listGroups(this.redis, args.stream);
        return {
            content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        };
    }

    private async listStreams(args: { pattern?: string }) {
        const result = await listStreams(this.redis, args.pattern || '*');
        return {
            content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        };
    }

    public async run(): Promise<void> {
        console.error('Starting server...');
        // Check if we're running under systemd socket activation
        if (process.env.LISTEN_FDS && parseInt(process.env.LISTEN_FDS, 10) > 0) {
            const server = net.createServer((socket) => {
                const transport = new StdioServerTransport(socket, socket);
                this.server.connect(transport).catch(console.error);
            });

            // Socket activation - fd starts at 3
            server.listen({ fd: 3 }, () => {
                console.error('RedStream MCP server running on systemd socket');
            });
        } else {
            // Fallback to standard stdio
            const transport = new StdioServerTransport();
            await this.server.connect(transport);
            console.error('RedStream MCP server running on stdio');
        }

        const cleanup = async () => {
            this.keepAlive = false;
            await this.cleanup();
            process.exit(0);
        };

        process.on('SIGINT', cleanup);
        process.on('SIGTERM', cleanup);
    }
}

const server = new RedStreamServer();
server.run().catch(console.error);