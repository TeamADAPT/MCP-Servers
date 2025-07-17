import { Server as McpServer } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { createClient, RedisClientType } from 'redis';
import { listGroups } from './tools/listGroups.js';
import { listStreams } from './tools/listStreams.js';

const TOOLS = {
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

export class RedStreamServer {
    private readonly server: McpServer;
    private readonly redis: RedisClientType;
    private keepAlive: boolean;

    constructor() {
        console.error('Initializing RedStream server...');
        this.keepAlive = true;
        
        this.server = new McpServer(
            {
                name: 'red-stream',
                version: '0.2.0',
            },
            {
                capabilities: {
                    tools: TOOLS,
                },
            }
        );

        this.redis = createClient({
            socket: {
                host: process.env.REDIS_HOST || 'localhost',
                port: parseInt(process.env.REDIS_PORT || '6379'),
            },
        }) as RedisClientType;

        this.redis.on('error', (err: Error) => {
            console.error('Redis error:', err);
        });

        this.setupRequestHandlers();
        this.setupErrorHandler();
    }

    private setupRequestHandlers(): void {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: Object.entries(TOOLS).map(([name, def]) => ({
                name,
                ...def,
            })),
        }));

        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            console.error('Handling tool request:', request.params.name);
            await this.ensureConnection();

            switch (request.params.name) {
                case 'get_stream_messages': {
                    const args = request.params.arguments as { stream: string; count?: number; start?: string };
                    const messages = await this.redis.xRead(
                        [{ key: args.stream, id: args.start || '0' }],
                        { COUNT: args.count || 1 }
                    );
                    return {
                        content: [{ type: 'text', text: JSON.stringify(messages || [], null, 2) }],
                    };
                }

                case 'add_stream_message': {
                    const args = request.params.arguments as { stream: string; message: Record<string, unknown> };
                    const id = await this.redis.xAdd(args.stream, '*', args.message);
                    return {
                        content: [{ type: 'text', text: JSON.stringify({ id }, null, 2) }],
                    };
                }

                case 'create_consumer_group': {
                    const args = request.params.arguments as { stream: string; group: string; start?: string };
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

                case 'read_group': {
                    const args = request.params.arguments as { stream: string; group: string; consumer: string; count?: number };
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

                case 'list_groups': {
                    const args = request.params.arguments as { stream: string };
                    const result = await listGroups(this.redis, args.stream);
                    return {
                        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
                    };
                }

                case 'list_streams': {
                    const args = request.params.arguments as { pattern?: string };
                    const result = await listStreams(this.redis, args.pattern || '*');
                    return {
                        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
                    };
                }

                default:
                    throw new Error(`Unknown tool: ${request.params.name}`);
            }
        });
    }

    private async ensureConnection(): Promise<void> {
        if (!this.redis.isOpen) {
            await this.redis.connect();
        }
    }

    private setupErrorHandler(): void {
        this.server.onerror = (error: Error) => {
            console.error('[MCP Error]', error);
        };

        process.on('uncaughtException', (error: Error) => {
            console.error('[Uncaught Exception]', error);
            void this.handleError(error);
        });

        process.on('unhandledRejection', (error: Error) => {
            console.error('[Unhandled Rejection]', error);
            void this.handleError(error);
        });
    }

    private async handleError(error: Error): Promise<void> {
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
        if (this.redis.isOpen) {
            await this.redis.quit();
        }
        await this.server.close();
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

    public async run(): Promise<void> {
        console.error('Starting server...');
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error('RedStream MCP server running on stdio');

        const cleanup = async () => {
            this.keepAlive = false;
            await this.cleanup();
            process.exit(0);
        };

        process.on('SIGINT', cleanup);
        process.on('SIGTERM', cleanup);
    }
}