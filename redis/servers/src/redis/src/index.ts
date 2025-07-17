import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import * as IORedis from 'ioredis';
import { StreamsIntegration } from './lib/streams-integration.js';

// Configuration
const REDIS_URL = process.argv[2] || "redis://localhost:6379";
const MAX_RETRIES = 5;
const MIN_RETRY_DELAY = 1000; // 1 second
const MAX_RETRY_DELAY = 30000; // 30 seconds

// Parse Redis URL to extract host, port, and password
const parseRedisUrl = (url: string) => {
    try {
        const parsedUrl = new URL(url);
        const host = parsedUrl.hostname;
        const port = parseInt(parsedUrl.port || '6379', 10);
        const password = parsedUrl.password || 
                         parsedUrl.searchParams.get('password') || 
                         undefined;
        
        return { host, port, password };
    } catch (error) {
        console.error('Error parsing Redis URL:', error);
        return { host: 'localhost', port: 6379 };
    }
};

const { host, port, password } = parseRedisUrl(REDIS_URL);

// Create Redis client with cluster support
let redisClient: IORedis.Redis | IORedis.Cluster;

// Check if we're connecting to a Redis Cluster
if (port >= 7000 && port <= 7005) {
    console.error('Detected Redis Cluster configuration');
    // Create a Redis Cluster client
    redisClient = new IORedis.Cluster(
        [
            { host, port },
            { host, port: 7001 },
            { host, port: 7002 }
        ],
        {
            redisOptions: {
                password
            }
        }
    );
} else {
    // Create a standard Redis client
    redisClient = new IORedis.Redis({
        host,
        port,
        password
    });
}

// Set up Redis event handlers
redisClient.on('error', (err: Error) => {
    console.error('Redis Client Error:', err);
});

redisClient.on('connect', () => {
    console.error(`Connected to Redis at ${REDIS_URL}`);
});

redisClient.on('reconnecting', () => {
    console.error('Attempting to reconnect to Redis...');
});

redisClient.on('end', () => {
    console.error('Redis connection closed');
});

// Define Zod schemas for validation
const SetArgumentsSchema = z.object({
    key: z.string(),
    value: z.string(),
    expireSeconds: z.number().optional(),
});

const GetArgumentsSchema = z.object({
    key: z.string(),
});

const DeleteArgumentsSchema = z.object({
    key: z.string().or(z.array(z.string())),
});

const ListArgumentsSchema = z.object({
    pattern: z.string().default("*"),
});

// Create server instance
// Initialize StreamsIntegration
const streamsIntegration = new StreamsIntegration('redis-mcp-server');

// Create server instance
const server = new Server(
    {
        name: "redis",
        version: "0.0.1"
    },
    {
        capabilities: {
            tools: {}
        }
    }
);

// Additional schemas for new tools
const CreateTaskArgumentsSchema = z.object({
    title: z.string(),
    description: z.string().optional(),
    priority: z.enum(['low', 'medium', 'high', 'critical']).default('medium'),
    assignee: z.string().optional(),
    parent_id: z.string().optional(),
    due_date: z.string().datetime().optional(),
    tags: z.array(z.string()).optional(),
    metadata: z.record(z.string(), z.any()).optional()
});

const GetTaskArgumentsSchema = z.object({
    task_id: z.string()
});

const PublishMessageArgumentsSchema = z.object({
    stream: z.string(),
    message: z.any(),
    maxlen: z.number().optional()
});

const ReadMessagesArgumentsSchema = z.object({
    stream: z.string(),
    count: z.number().optional(),
    reverse: z.boolean().optional()
});

const SetStateArgumentsSchema = z.object({
    key: z.string(),
    state: z.any()
});

const GetStateArgumentsSchema = z.object({
    key: z.string()
});

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: "set",
                description: "Set a Redis key-value pair with optional expiration",
                inputSchema: {
                    type: "object",
                    properties: {
                        key: {
                            type: "string",
                            description: "Redis key",
                        },
                        value: {
                            type: "string",
                            description: "Value to store",
                        },
                        expireSeconds: {
                            type: "number",
                            description: "Optional expiration time in seconds",
                        },
                    },
                    required: ["key", "value"],
                },
            },
            {
                name: "get",
                description: "Get value by key from Redis",
                inputSchema: {
                    type: "object",
                    properties: {
                        key: {
                            type: "string",
                            description: "Redis key to retrieve",
                        },
                    },
                    required: ["key"],
                },
            },
            {
                name: "delete",
                description: "Delete one or more keys from Redis",
                inputSchema: {
                    type: "object",
                    properties: {
                        key: {
                            oneOf: [
                                { type: "string" },
                                { type: "array", items: { type: "string" } }
                            ],
                            description: "Key or array of keys to delete",
                        },
                    },
                    required: ["key"],
                },
            },
            {
                name: "list",
                description: "List Redis keys matching a pattern",
                inputSchema: {
                    type: "object",
                    properties: {
                        pattern: {
                            type: "string",
                            description: "Pattern to match keys (default: *)",
                        },
                    },
                },
            },
            // Task Management Tools
            {
                name: "create_task",
                description: "Create a new task",
                inputSchema: {
                    type: "object",
                    properties: {
                        title: {
                            type: "string",
                            description: "Task title"
                        },
                        description: {
                            type: "string",
                            description: "Task description"
                        },
                        priority: {
                            type: "string",
                            enum: ["low", "medium", "high", "critical"],
                            description: "Task priority"
                        },
                        assignee: {
                            type: "string",
                            description: "Task assignee"
                        },
                        due_date: {
                            type: "string",
                            description: "Task due date (ISO 8601)"
                        },
                        tags: {
                            type: "array",
                            items: { type: "string" },
                            description: "Task tags"
                        }
                    },
                    required: ["title"]
                }
            },
            {
                name: "get_task",
                description: "Get task details by ID",
                inputSchema: {
                    type: "object",
                    properties: {
                        task_id: {
                            type: "string",
                            description: "Task ID"
                        }
                    },
                    required: ["task_id"]
                }
            },
            // Stream Operations Tools
            {
                name: "publish_message",
                description: "Publish a message to a Redis stream",
                inputSchema: {
                    type: "object",
                    properties: {
                        stream: {
                            type: "string",
                            description: "Stream name"
                        },
                        message: {
                            type: "object",
                            description: "Message content"
                        },
                        maxlen: {
                            type: "number",
                            description: "Maximum stream length"
                        }
                    },
                    required: ["stream", "message"]
                }
            },
            {
                name: "read_messages",
                description: "Read messages from a Redis stream",
                inputSchema: {
                    type: "object",
                    properties: {
                        stream: {
                            type: "string",
                            description: "Stream name"
                        },
                        count: {
                            type: "number",
                            description: "Number of messages to read"
                        },
                        reverse: {
                            type: "boolean",
                            description: "Read messages in reverse order"
                        }
                    },
                    required: ["stream"]
                }
            },
            // State Management Tools
            {
                name: "set_state",
                description: "Set state for a key",
                inputSchema: {
                    type: "object",
                    properties: {
                        key: {
                            type: "string",
                            description: "State key"
                        },
                        state: {
                            type: "object",
                            description: "State data"
                        }
                    },
                    required: ["key", "state"]
                }
            },
            {
                name: "get_state",
                description: "Get state by key",
                inputSchema: {
                    type: "object",
                    properties: {
                        key: {
                            type: "string",
                            description: "State key"
                        }
                    },
                    required: ["key"]
                }
            },
            {
                name: "add_stream",
                description: "Create a new stream with metadata",
                inputSchema: {
                    type: "object",
                    properties: {
                        stream: {
                            type: "string",
                            description: "Stream name (must follow naming convention)"
                        },
                        metadata: {
                            type: "object",
                            properties: {
                                description: {
                                    type: "string",
                                    description: "Stream description"
                                },
                                owner: {
                                    type: "string",
                                    description: "Stream owner"
                                }
                            },
                            additionalProperties: true
                        }
                    },
                    required: ["stream"]
                }
            },
            {
                name: "get_stream_health",
                description: "Get health metrics for a stream",
                inputSchema: {
                    type: "object",
                    properties: {
                        stream: {
                            type: "string",
                            description: "Stream name"
                        }
                    },
                    required: ["stream"]
                }
            }
        ],
    };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
        if (name === "set") {
            const { key, value, expireSeconds } = SetArgumentsSchema.parse(args);
            
            if (expireSeconds) {
                await redisClient.setex(key, expireSeconds, value);
            } else {
                await redisClient.set(key, value);
            }

            return {
                content: [
                    {
                        type: "text",
                        text: `Successfully set key: ${key}`,
                    },
                ],
            };
        } else if (name === "get") {
            const { key } = GetArgumentsSchema.parse(args);
            const value = await redisClient.get(key);

            if (value === null) {
                return {
                    content: [
                        {
                            type: "text",
                            text: `Key not found: ${key}`,
                        },
                    ],
                };
            }

            return {
                content: [
                    {
                        type: "text",
                        text: `${value}`,
                    },
                ],
            };
        } else if (name === "delete") {
            const { key } = DeleteArgumentsSchema.parse(args);
            
            if (Array.isArray(key)) {
                await redisClient.del(key);
                return {
                    content: [
                        {
                            type: "text",
                            text: `Successfully deleted ${key.length} keys`,
                        },
                    ],
                };
            } else {
                await redisClient.del(key);
                return {
                    content: [
                        {
                            type: "text",
                            text: `Successfully deleted key: ${key}`,
                        },
                    ],
                };
            }
        } else if (name === "list") {
            const { pattern } = ListArgumentsSchema.parse(args);
            const keys = await redisClient.keys(pattern);

            return {
                content: [
                    {
                        type: "text",
                        text: keys.length > 0 
                            ? `Found keys:\n${keys.join('\n')}`
                            : "No keys found matching pattern",
                    },
                ],
            };
        } else if (name === "create_task") {
            const taskData = CreateTaskArgumentsSchema.parse(args);
            const result = await streamsIntegration.createTask({
                ...taskData,
                origin_nova_id: 'mcp-server',
                execution_trace_id: `trace-${Date.now()}`
            });
            return {
                content: [{ type: "text", text: JSON.stringify(result) }]
            };
        } else if (name === "get_task") {
            const { task_id } = GetTaskArgumentsSchema.parse(args);
            const result = await streamsIntegration.getTask(task_id);
            return {
                content: [{ type: "text", text: JSON.stringify(result) }]
            };
        } else if (name === "publish_message") {
            const { stream, message, maxlen } = PublishMessageArgumentsSchema.parse(args);
            const result = await streamsIntegration.publishMessage(stream, message, maxlen);
            return {
                content: [{ type: "text", text: JSON.stringify(result) }]
            };
        } else if (name === "read_messages") {
            const { stream, count, reverse } = ReadMessagesArgumentsSchema.parse(args);
            const messages = await streamsIntegration.readMessages(stream, { count, reverse });
            return {
                content: [{ type: "text", text: JSON.stringify(messages) }]
            };
        } else if (name === "set_state") {
            const { key, state } = SetStateArgumentsSchema.parse(args);
            await redisClient.set(`state:${key}`, JSON.stringify(state));
            return {
                content: [{ type: "text", text: `Successfully set state for key: ${key}` }]
            };
        } else if (name === "get_state") {
            const { key } = GetStateArgumentsSchema.parse(args);
            const state = await redisClient.get(`state:${key}`);
            if (!state) {
                return {
                    content: [{ type: "text", text: `No state found for key: ${key}` }]
                };
            }
            return {
                content: [{ type: "text", text: state }]
            };
        } else if (name === "add_stream") {
            const { stream, metadata } = z.object({
                stream: z.string(),
                metadata: z.object({
                    description: z.string().optional(),
                    owner: z.string().optional()
                }).optional()
            }).parse(args);
            
            const result = await streamsIntegration.addStream(stream, metadata);
            return {
                content: [{ type: "text", text: JSON.stringify(result) }]
            };
        } else if (name === "get_stream_health") {
            const { stream } = z.object({
                stream: z.string()
            }).parse(args);
            
            const health = await streamsIntegration.getStreamHealth(stream);
            return {
                content: [{ type: "text", text: JSON.stringify(health) }]
            };
        } else {
            throw new Error(`Unknown tool: ${name}`);
        }
    } catch (error) {
        if (error instanceof z.ZodError) {
            throw new Error(
                `Invalid arguments: ${error.errors
                    .map((e) => `${e.path.join(".")}: ${e.message}`)
                    .join(", ")}`
            );
        }
        throw error;
    }
});

// Start the server
async function main() {
    try {
        // Set up Redis event handlers
        redisClient.on('error', (err: Error) => {
            console.error('Redis Client Error:', err);
        });

        redisClient.on('connect', () => {
            console.error(`Connected to Redis at ${REDIS_URL}`);
        });

        redisClient.on('reconnecting', () => {
            console.error('Attempting to reconnect to Redis...');
        });

        redisClient.on('end', () => {
            console.error('Redis connection closed');
        });

        // Set up MCP server
        const transport = new StdioServerTransport();
        await server.connect(transport);
        console.error("Redis MCP Server running on stdio");
    } catch (error) {
        console.error("Error during startup:", error);
        await cleanup();
    }
}

// Cleanup function
async function cleanup() {
    try {
        await Promise.all([
            redisClient.quit(),
            streamsIntegration.close()
        ]);
    } catch (error) {
        console.error("Error during cleanup:", error);
    }
    process.exit(1);
}

// Handle process termination
process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);

main().catch((error) => {
    console.error("Fatal error in main():", error);
    cleanup();
});
