#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ErrorCode, ListToolsRequestSchema, McpError } from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import fs from 'fs/promises';
import path from 'path';

class PulsarMcpServer {
    private server: Server;
    private baseUrl: string;
    private brokerUrl: string;
    private socketPath: string;
    private stateDir: string;
    private runtimeDir: string;
    private isConnected: boolean;
    private reconnectAttempts: number;
    private maxReconnectAttempts: number;
    private reconnectDelay: number;

    constructor() {
        this.server = new Server(
            {
                name: process.env.MCP_SERVER_NAME || 'pulsar-mcp',
                version: process.env.MCP_SERVER_VERSION || '1.0.0',
            },
            {
                capabilities: {
                    tools: {},
                },
            }
        );

        // Configuration
        this.baseUrl = `http://${process.env.PULSAR_HOST || 'localhost'}:${process.env.PULSAR_ADMIN_PORT || '8083'}`;
        this.brokerUrl = `pulsar://${process.env.PULSAR_HOST || 'localhost'}:${process.env.PULSAR_PORT || '6650'}`;
        
        // Socket path from environment or default
        this.socketPath = process.env.SOCKET_PATH || '/run/mcp/pulsar.sock';
        
        // State management
        this.stateDir = '/var/lib/pulsar-mcp';
        this.runtimeDir = '/run/mcp';
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;

        // Setup
        this.setupDirectories().catch(error => {
            console.error('Setup error:', error);
            process.exit(1);
        });
        
        this.setupToolHandlers();
        this.setupHealthCheck();
        
        // Error handling
        this.server.onerror = (error) => this.handleError(error);
        
        // Signal handling
        process.on('SIGINT', async () => {
            await this.cleanup();
            process.exit(0);
        });
        
        process.on('SIGTERM', async () => {
            await this.cleanup();
            process.exit(0);
        });
    }

    private async setupDirectories() {
        console.error('Setting up directories...');
        try {
            // Ensure socket directory exists
            const socketDir = path.dirname(this.socketPath);
            await fs.mkdir(socketDir, { recursive: true });
            console.error(`Created socket directory: ${socketDir}`);
            
            // Create state directory if needed
            await fs.mkdir(this.stateDir, { recursive: true });
            
            // Write PID file
            await fs.writeFile(path.join(this.runtimeDir, 'pulsar-mcp.pid'), process.pid.toString());
            console.error('Directory setup complete');
        } catch (error) {
            console.error('Error setting up directories:', error);
            throw error;
        }
    }

    private setupHealthCheck() {
        console.error('Setting up health check...');
        setInterval(async () => {
            try {
                await this.checkConnection();
            } catch (error) {
                console.error('Health check failed:', error);
                if (!this.isConnected) {
                    await this.reconnect();
                }
            }
        }, 30000);
    }

    private async checkConnection() {
        try {
            const response = await axios.get(`${this.baseUrl}/admin/v2/brokers/health`);
            console.error('Health check response:', response.data);
            this.isConnected = true;
            this.reconnectAttempts = 0;
            await fs.writeFile(path.join(this.runtimeDir, 'pulsar-mcp.health'), 'OK');
            console.error('Health check passed');
        } catch (error) {
            this.isConnected = false;
            await fs.writeFile(path.join(this.runtimeDir, 'pulsar-mcp.health'), 'ERROR');
            console.error('Health check error details:', {
                message: error.message,
                response: error.response?.data,
                config: {
                    url: error.config?.url,
                    method: error.config?.method,
                    headers: error.config?.headers
                }
            });
            throw error;
        }
    }

    private async reconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            process.exit(1);
        }

        this.reconnectAttempts++;
        console.error(`Reconnection attempt ${this.reconnectAttempts}`);
        
        await new Promise(resolve => setTimeout(resolve, this.reconnectDelay));
        await this.checkConnection();
    }

    private handleError(error: any) {
        const errorDetails = {
            message: error.message,
            stack: error.stack,
            response: error.response?.data,
            config: error.config ? {
                url: error.config.url,
                method: error.config.method,
                headers: error.config.headers,
                data: error.config.data
            } : undefined
        };
        
        console.error('[MCP Error]', JSON.stringify(errorDetails, null, 2));
        
        fs.appendFile(
            path.join(this.stateDir, 'error.log'),
            `${new Date().toISOString()} - ${JSON.stringify(errorDetails)}\n`
        ).catch(console.error);
    }

    private async cleanup() {
        console.error('Cleaning up...');
        try {
            await this.server.close();
            await fs.unlink(path.join(this.runtimeDir, 'pulsar-mcp.pid')).catch(() => {});
            await fs.unlink(path.join(this.runtimeDir, 'pulsar-mcp.health')).catch(() => {});
            console.error('Cleanup complete');
        } catch (error) {
            console.error('Cleanup error:', error);
        }
    }

    private setupToolHandlers() {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: [
                {
                    name: 'create_topic',
                    description: 'Create a new Pulsar topic',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            topic: {
                                type: 'string',
                                description: 'Topic name (e.g., persistent://public/default/my-topic)',
                            },
                            partitions: {
                                type: 'number',
                                description: 'Number of partitions',
                                default: 1,
                            },
                        },
                        required: ['topic'],
                    },
                },
                {
                    name: 'list_topics',
                    description: 'List all topics in a namespace',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            namespace: {
                                type: 'string',
                                description: 'Namespace (e.g., public/default)',
                                default: 'public/default',
                            },
                        },
                    },
                },
                {
                    name: 'send_message',
                    description: 'Send a message to a topic',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            topic: {
                                type: 'string',
                                description: 'Topic name (e.g., persistent://public/default/my-topic)',
                            },
                            message: {
                                type: 'object',
                                description: 'Message content',
                            },
                        },
                        required: ['topic', 'message'],
                    },
                },
                {
                    name: 'get_messages',
                    description: 'Read messages from a topic',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            topic: {
                                type: 'string',
                                description: 'Topic name (e.g., persistent://public/default/my-topic)',
                            },
                            subscription: {
                                type: 'string',
                                description: 'Subscription name',
                            },
                            count: {
                                type: 'number',
                                description: 'Number of messages to retrieve',
                                default: 10,
                            },
                        },
                        required: ['topic', 'subscription'],
                    },
                },
                {
                    name: 'get_stats',
                    description: 'Get topic statistics',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            topic: {
                                type: 'string',
                                description: 'Topic name (e.g., persistent://public/default/my-topic)',
                            },
                        },
                        required: ['topic'],
                    },
                },
            ],
        }));

        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            if (!this.isConnected) {
                throw new McpError(ErrorCode.ServiceUnavailable, 'Pulsar service not connected');
            }

            switch (request.params.name) {
                case 'create_topic':
                    return await this.handleCreateTopic(request.params.arguments || {});
                case 'list_topics':
                    return await this.handleListTopics(request.params.arguments || {});
                case 'send_message':
                    return await this.handleSendMessage(request.params.arguments || {});
                case 'get_messages':
                    return await this.handleGetMessages(request.params.arguments || {});
                case 'get_stats':
                    return await this.handleGetStats(request.params.arguments || {});
                default:
                    throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${request.params.name}`);
            }
        });
    }

    private async handleCreateTopic(args: any) {
        try {
            const namespace = args.topic.split('/').slice(0, -1).join('/');
            console.error(`Creating topic in namespace: ${namespace}`);
            
            // Ensure namespace exists
            try {
                const namespaceResponse = await axios.get(`${this.baseUrl}/admin/v2/namespaces/${namespace}`);
                console.error('Namespace exists:', namespaceResponse.data);
            } catch (error) {
                if (error.response?.status === 404) {
                    console.error('Creating namespace');
                    const createResponse = await axios.put(`${this.baseUrl}/admin/v2/namespaces/${namespace}`);
                    console.error('Namespace created:', createResponse.data);
                } else {
                    console.error('Namespace check error:', error.response?.data || error.message);
                    throw error;
                }
            }

            // Create non-partitioned topic
            console.error('Creating topic');
            const createResponse = await axios.put(`${this.baseUrl}/admin/v2/persistent/${args.topic}`, null, {
                headers: { 'Content-Type': 'application/json' }
            });
            console.error('Topic created:', createResponse.data);

            // Update to partitioned if specified
            if (args.partitions && args.partitions > 0) {
                console.error(`Setting partitions: ${args.partitions}`);
                const partitionResponse = await axios.post(
                    `${this.baseUrl}/admin/v2/persistent/${args.topic}/partitions`,
                    args.partitions,
                    { headers: { 'Content-Type': 'application/json' } }
                );
                console.error('Partitions set:', partitionResponse.data);
            }

            return {
                content: [{
                    type: 'text',
                    text: `Topic ${args.topic} created successfully${args.partitions ? ` with ${args.partitions} partitions` : ''}`,
                }],
            };
        } catch (error) {
            this.handleError(error);
            return {
                content: [{
                    type: 'text',
                    text: `Error creating topic: ${error.response?.data || error.message}`,
                }],
                isError: true,
            };
        }
    }

    private async handleListTopics(args: any) {
        try {
            const namespace = args.namespace || 'public/default';
            console.error(`Listing topics in namespace: ${namespace}`);
            const response = await axios.get(`${this.baseUrl}/admin/v2/persistent/${namespace}`);
            console.error('Topics response:', response.data);
            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify(response.data, null, 2),
                }],
            };
        } catch (error) {
            this.handleError(error);
            return {
                content: [{
                    type: 'text',
                    text: `Error listing topics: ${error.response?.data || error.message}`,
                }],
                isError: true,
            };
        }
    }

    private async handleSendMessage(args: any) {
        try {
            console.error(`Sending message to topic: ${args.topic}`);
            const messageBuffer = Buffer.from(JSON.stringify(args.message));
            const response = await axios.post(
                `${this.baseUrl}/admin/v2/persistent/${args.topic}/messages`,
                { payload: messageBuffer.toString('base64') },
                { headers: { 'Content-Type': 'application/json' } }
            );
            console.error('Message sent:', response.data);
            return {
                content: [{
                    type: 'text',
                    text: `Message sent successfully to ${args.topic}`,
                }],
            };
        } catch (error) {
            this.handleError(error);
            return {
                content: [{
                    type: 'text',
                    text: `Error sending message: ${error.response?.data || error.message}`,
                }],
                isError: true,
            };
        }
    }

    private async handleGetMessages(args: any) {
        try {
            console.error(`Reading messages from topic: ${args.topic}`);
            
            // Create subscription if it doesn't exist
            try {
                await axios.post(
                    `${this.baseUrl}/admin/v2/persistent/${args.topic}/subscription/${args.subscription}`,
                    null,
                    { headers: { 'Content-Type': 'application/json' } }
                );
                console.error('Subscription created/verified');
            } catch (error) {
                if (error.response?.status !== 409) { // 409 means subscription already exists
                    throw error;
                }
            }

            // Get messages
            const response = await axios.get(
                `${this.baseUrl}/admin/v2/persistent/${args.topic}/subscription/${args.subscription}/position/${args.count || 10}`,
                { headers: { 'Accept': 'application/json' } }
            );

            console.error('Messages retrieved:', response.data);
            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify(response.data, null, 2),
                }],
            };
        } catch (error) {
            this.handleError(error);
            return {
                content: [{
                    type: 'text',
                    text: `Error reading messages: ${error.response?.data || error.message}`,
                }],
                isError: true,
            };
        }
    }

    private async handleGetStats(args: any) {
        try {
            console.error(`Getting stats for topic: ${args.topic}`);
            const response = await axios.get(`${this.baseUrl}/admin/v2/persistent/${args.topic}/stats`);
            console.error('Stats response:', response.data);
            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify(response.data, null, 2),
                }],
            };
        } catch (error) {
            this.handleError(error);
            return {
                content: [{
                    type: 'text',
                    text: `Error getting stats: ${error.response?.data || error.message}`,
                }],
                isError: true,
            };
        }
    }

    async run() {
        try {
            console.error('Starting Pulsar MCP server...');
            
            // Initial connection check
            await this.checkConnection();
            console.error('Initial connection check passed');
            
            const transport = new StdioServerTransport();
            await this.server.connect(transport);
            
            console.error('Pulsar MCP server running on stdio');
            
            // Notify systemd we're ready
            if (process.env.NOTIFY_SOCKET) {
                process.send?.('READY=1');
                console.error('Sent ready notification to systemd');
            }
        } catch (error) {
            this.handleError(error);
            process.exit(1);
        }
    }
}

const server = new PulsarMcpServer();
server.run().catch(console.error);