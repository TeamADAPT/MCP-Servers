#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ErrorCode, ListToolsRequestSchema, McpError, } from '@modelcontextprotocol/sdk/types.js';
import { createClient } from 'redis';
import net from 'net';

class RedMemServer {
    private server: Server;
    private redis: ReturnType<typeof createClient>;
    private keepAlive: boolean;
    private readonly DEFAULT_TTL = 604800; // 7 days in seconds (7 * 24 * 60 * 60)

    constructor() {
        this.server = new Server({
            name: 'red-mem-server',
            version: '0.1.0',
        }, {
            capabilities: {
                tools: {},
            },
        });

        this.redis = createClient({
            socket: {
                host: process.env.REDIS_HOST || 'localhost',
                port: parseInt(process.env.REDIS_PORT || '6379'),
            },
            password: process.env.REDIS_PASSWORD,
        });

        this.setupRequestHandlers();
        this.setupErrorHandler();
        this.keepAlive = true;
    }

    private setupRequestHandlers(): void {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: [
                {
                    name: 'remember',
                    description: 'Store a memory with TTL',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            key: {
                                type: 'string',
                                description: 'Memory key',
                            },
                            value: {
                                type: 'object',
                                description: 'Memory content',
                            },
                            ttl: {
                                type: 'number',
                                description: 'Time to live in seconds (default: 7 days)',
                                default: 604800,
                            },
                            context: {
                                type: 'string',
                                description: 'Memory context (e.g., conversation, task)',
                            },
                        },
                        required: ['key', 'value'],
                    },
                },
                {
                    name: 'recall',
                    description: 'Retrieve a memory',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            key: {
                                type: 'string',
                                description: 'Memory key',
                            },
                        },
                        required: ['key'],
                    },
                },
                {
                    name: 'forget',
                    description: 'Delete a memory',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            key: {
                                type: 'string',
                                description: 'Memory key',
                            },
                        },
                        required: ['key'],
                    },
                },
                {
                    name: 'recall_context',
                    description: 'Retrieve all memories in a context',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            context: {
                                type: 'string',
                                description: 'Memory context to recall',
                            },
                        },
                        required: ['context'],
                    },
                },
            ],
        }));

        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            await this.ensureConnection();
            switch (request.params.name) {
                case 'remember':
                    return this.remember(request.params.arguments);
                case 'recall':
                    return this.recall(request.params.arguments);
                case 'forget':
                    return this.forget(request.params.arguments);
                case 'recall_context':
                    return this.recallContext(request.params.arguments);
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
        this.server.onerror = (error: Error) => {
            console.error('[MCP Error]', error);
        };

        process.on('uncaughtException', (error: Error) => {
            console.error('[Uncaught Exception]', error);
            this.handleError(error);
        });

        process.on('unhandledRejection', (reason: unknown) => {
            const error = reason instanceof Error ? reason : new Error(String(reason));
            console.error('[Unhandled Rejection]', error);
            this.handleError(error);
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
            console.error('RedMem MCP server reconnected');
        } catch (error) {
            console.error('[Reconnection Error]', error);
            if (this.keepAlive) {
                setTimeout(() => this.reconnect(), 5000);
            }
        }
    }

    private async remember(args: any) {
        const { key, value, ttl = this.DEFAULT_TTL, context } = args;
        const memoryKey = context ? `${context}:${key}` : key;
        const memoryValue = {
            ...value,
            _meta: {
                timestamp: Date.now(),
                context: context || 'default',
            },
        };
        await this.redis.set(memoryKey, JSON.stringify(memoryValue), {
            EX: ttl,
        });
        if (context) {
            await this.redis.sAdd(`contexts:${context}`, memoryKey);
            await this.redis.expire(`contexts:${context}`, ttl);
        }
        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify({ status: 'remembered', key: memoryKey, ttl }, null, 2),
                },
            ],
        };
    }

    private async recall(args: any) {
        const value = await this.redis.get(args.key);
        if (!value) {
            return {
                content: [
                    {
                        type: 'text',
                        text: JSON.stringify({ status: 'forgotten', key: args.key }, null, 2),
                    },
                ],
            };
        }
        return {
            content: [
                {
                    type: 'text',
                    text: value,
                },
            ],
        };
    }

    private async forget(args: any) {
        const deleted = await this.redis.del(args.key);
        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify({
                        status: deleted ? 'forgotten' : 'not_found',
                        key: args.key,
                    }, null, 2),
                },
            ],
        };
    }

    private async recallContext(args: any) {
        const keys = await this.redis.sMembers(`contexts:${args.context}`);
        const memories = [];
        for (const key of keys) {
            const value = await this.redis.get(key);
            if (value) {
                memories.push({ key, value: JSON.parse(value) });
            }
        }
        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify(memories, null, 2),
                },
            ],
        };
    }

    async run(): Promise<void> {
        // Check if we're running under systemd socket activation
        const listenFds = process.env.LISTEN_FDS ? parseInt(process.env.LISTEN_FDS, 10) : 0;
        if (listenFds > 0) {
            const server = net.createServer((socket) => {
                const transport = new StdioServerTransport(socket, socket);
                this.server.connect(transport).catch(console.error);
            });

            // Socket activation - fd starts at 3
            server.listen({ fd: 3 }, () => {
                console.error('RedMem MCP server running on systemd socket');
            });
        } else {
            // Fallback to standard stdio
            const transport = new StdioServerTransport();
            await this.server.connect(transport);
            console.error('RedMem MCP server running on stdio');
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

const server = new RedMemServer();
server.run().catch(console.error);