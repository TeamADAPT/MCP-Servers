#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { DesktopAutomation } from './automation.js';

const automation = new DesktopAutomation();

const server = new Server(
    {
        name: 'desktop-automation',
        version: '0.1.0',
    },
    {
        capabilities: {
            tools: {
                mouseMove: {
                    description: 'Move mouse cursor to specified coordinates',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            x: { type: 'number', description: 'X coordinate' },
                            y: { type: 'number', description: 'Y coordinate' },
                        },
                        required: ['x', 'y'],
                    },
                },
                mouseClick: {
                    description: 'Click at specified coordinates',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            x: { type: 'number', description: 'X coordinate' },
                            y: { type: 'number', description: 'Y coordinate' },
                            button: { type: 'string', enum: ['left', 'right'], default: 'left' },
                        },
                        required: ['x', 'y'],
                    },
                },
                typeText: {
                    description: 'Type text at current cursor position',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            text: { type: 'string', description: 'Text to type' },
                        },
                        required: ['text'],
                    },
                },
                pressKey: {
                    description: 'Press a keyboard key',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            key: { type: 'string', description: 'Key to press' },
                        },
                        required: ['key'],
                    },
                },
                launchApp: {
                    description: 'Launch an application',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            appName: { type: 'string', description: 'Application name' },
                        },
                        required: ['appName'],
                    },
                },
                closeApp: {
                    description: 'Close an application',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            appName: { type: 'string', description: 'Application name' },
                        },
                        required: ['appName'],
                    },
                },
                captureScreen: {
                    description: 'Capture screenshot',
                    inputSchema: {
                        type: 'object',
                        properties: {},
                        required: [],
                    },
                },
            },
        },
    }
);

// Handle tool calls
server.handleRequest = async (request) => {
    if (request.method !== 'CallTool') {
        return {
            error: {
                code: -32601,
                message: `Method not found: ${request.method}`,
            },
        };
    }

    try {
        const { name, arguments: args } = request.params;
        
        switch (name) {
            case 'mouseMove':
                await automation.mouseMove(args.x, args.y);
                break;
            case 'mouseClick':
                await automation.mouseClick(args.x, args.y, args.button);
                break;
            case 'typeText':
                await automation.typeText(args.text);
                break;
            case 'pressKey':
                await automation.pressKey(args.key);
                break;
            case 'launchApp':
                await automation.launchApp(args.appName);
                break;
            case 'closeApp':
                await automation.closeApp(args.appName);
                break;
            case 'captureScreen':
                try {
                    await automation.captureScreen();
                    return {
                        result: {
                            content: [{ type: 'text', text: 'Screenshot captured successfully' }],
                        },
                    };
                } catch (err) {
                    const error = err instanceof Error ? err : new Error(String(err));
                    return {
                        result: {
                            content: [{ type: 'text', text: `Error capturing screenshot: ${error.message}` }],
                            isError: true,
                        },
                    };
                }
                break;
            default:
                throw new Error(`Unknown tool: ${name}`);
        }

        return {
            result: {
                content: [{ type: 'text', text: 'Success' }],
            },
        };
    } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        return {
            result: {
                content: [{ type: 'text', text: `Error: ${error.message}` }],
                isError: true,
            },
        };
    }
};

// Start the server
const transport = new StdioServerTransport();
server.connect(transport).catch((err: Error) => {
    console.error('Failed to start server:', err);
    process.exit(1);
});

console.log('Desktop Automation MCP server running on stdio');