#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ErrorCode, ListToolsRequestSchema, McpError } from '@modelcontextprotocol/sdk/types.js';
import net from 'net';
import { logger } from './utils/logger.js';
import { monitor } from './utils/monitor.js';
import { TOOLS, executeTool } from './tools/index.js';

class MetricsServer {
    private server: Server;
    private isInitialized = false;

    constructor() {
        logger.info('Initializing Metrics MCP server');
        this.server = new Server(
            {
                name: process.env.MCP_SERVER_NAME || 'metrics-mcp',
                version: process.env.MCP_SERVER_VERSION || '0.1.0',
            },
            {
                capabilities: {
                    tools: TOOLS,
                },
            }
        );

        this.setupRequestHandlers();
        this.setupErrorHandler();
    }

    private setupRequestHandlers(): void {
        // Register tools
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: Object.values(TOOLS)
        }));

        // Handle tool execution
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            try {
                return await executeTool(request.params.name, request.params.arguments);
            } catch (error) {
                if (error instanceof McpError) {
                    throw error;
                }
                throw new McpError(
                    ErrorCode.InternalError,
                    `Tool execution failed: ${error instanceof Error ? error.message : String(error)}`
                );
            }
        });
    }

    private setupErrorHandler(): void {
        this.server.onerror = (error) => {
            logger.error('[MCP Error]', error);
            void monitor.reportError(error);
        };

        process.on('uncaughtException', (error) => {
            logger.error('[Uncaught Exception]', error);
            void monitor.reportError(error);
        });

        process.on('unhandledRejection', (reason) => {
            const error = reason instanceof Error ? reason : new Error(String(reason));
            logger.error('[Unhandled Rejection]', error);
            void monitor.reportError(error);
        });
    }

    async initialize(): Promise<void> {
        if (this.isInitialized) return;

        try {
            // Initialize service monitor
            await monitor.initialize();
            await monitor.reportStatus('up');
            this.isInitialized = true;
            logger.info('Metrics MCP server initialized');
        } catch (error) {
            logger.error('Failed to initialize server:', error);
            throw error;
        }
    }

    async shutdown(): Promise<void> {
        logger.info('Shutting down Metrics MCP server');
        try {
            await monitor.shutdown();
            await this.server.close();
            this.isInitialized = false;
        } catch (error) {
            logger.error('Error during shutdown:', error);
            throw error;
        }
    }

    async run(): Promise<void> {
        await this.initialize();

        // Check if we're running under systemd socket activation
        const listenFds = process.env.LISTEN_FDS ? parseInt(process.env.LISTEN_FDS, 10) : 0;
        if (listenFds > 0) {
            logger.info('Using systemd socket activation');
            const server = net.createServer((socket) => {
                const transport = new StdioServerTransport(socket, socket);
                this.server.connect(transport).catch(error => {
                    logger.error('Failed to establish MCP connection:', error);
                });
            });

            // Socket activation - fd starts at 3
            server.listen({ fd: 3 }, () => {
                logger.info('Metrics MCP server running on systemd socket');
            });
        } else {
            logger.info('Using standard stdio transport');
            const transport = new StdioServerTransport();
            await this.server.connect(transport);
            logger.info('Metrics MCP server running on stdio');
        }

        const cleanup = async () => {
            logger.info('Received shutdown signal');
            await this.shutdown();
            process.exit(0);
        };

        process.on('SIGINT', cleanup);
        process.on('SIGTERM', cleanup);
    }
}

// Start server
const server = new MetricsServer();
server.run().catch(error => {
    logger.error('Server startup failed:', error);
    process.exit(1);
});