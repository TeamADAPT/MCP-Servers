import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
// Removed RedStream import from here, it's handled by StreamsIntegration
import { StreamsIntegration } from "./streams-integration.js";
import { MemoryBank } from "./memory-bank.js";

// Removed top-level Redis config and connection logic (ensureConnection, startHeartbeat, etc.)
// It will be managed within StreamsIntegration

// Initialize StreamsIntegration and MemoryBank instances
let streamsIntegration: StreamsIntegration;
let memoryBank: MemoryBank;


// Start the server
async function main() {
    try {
        // Initialize StreamsIntegration (this now handles RedStream creation)
        streamsIntegration = await StreamsIntegration.create('redis_mcp_server');
        console.log("StreamsIntegration initialized."); // Log success
        
        // Initialize MemoryBank using the RedStream instance from StreamsIntegration
        memoryBank = new MemoryBank(streamsIntegration.redStream, 'redis_mcp_server');
        await memoryBank.initialize();
        console.log("MemoryBank initialized."); // Log success
        
        // Register tools with the server (handled by StreamsIntegration)
        streamsIntegration.registerTools(server);
        
        // Connect server to transport
        const transport = new StdioServerTransport();
        await server.connect(transport);
        console.log("Redis MCP Server connected to transport."); // Log success

    } catch (error) {
        console.error("Error during startup:", error);
        await cleanup();
    }
}

// Removed withConnection wrapper, connection handled internally by StreamsIntegration/RedStream

// Task Schema (Keep for potential use in resource handlers if needed, or remove if unused)
const TaskSchema = z.object({
    task_id: z.string().optional(), // Example field
    title: z.string().min(1), // Example field
    description: z.string().optional(), // Example field
    // ... other task fields ...
    status: z.enum(['new', 'in_progress', 'blocked', 'completed', 'cancelled']).default('new'), // Example field
    priority: z.enum(['low', 'medium', 'high', 'critical']).default('medium'), // Example field
    assignee: z.string().optional(), // Example field
    // ... other task fields ...
});

// Removed other specific schemas (MessageSchema, Task Management, Stream Communication)
// as tool logic is now handled within StreamsIntegration

// Create server instance (keep this)
const server = new Server(
    { name: "redis", version: "1.0.0" },
    {
        // Capabilities are now largely defined by the tools registered
        // by StreamsIntegration. We might still need resource capabilities here.
        capabilities: {
            // Tools are registered dynamically by StreamsIntegration
            tools: {}, 
            // Keep resource definitions if they are still needed
            resources: {} 
        }
    }
);

// Removed ListToolsRequestSchema handler, as StreamsIntegration handles tool registration.

// Add resource handlers (Update to use streamsIntegration.redStream)
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
    // Example resource definitions (adjust as needed)
    resources: [
        {
            uri: `task://{task_id}`, // Keep if task resource is needed
            name: "Task Data", // Keep if task resource is needed
            description: "Direct access to a task's data", // Keep if task resource is needed
            mimeType: "application/json" // Keep if task resource is needed
        },
        {
            uri: `stream://{stream_name}/latest`, // Keep if stream resource is needed
            name: "Latest Stream Messages", // Keep if stream resource is needed
            description: "Access to the latest messages in a stream", // Keep if stream resource is needed
            mimeType: "application/json" // Keep if stream resource is needed
        },
        {
            uri: `state://{key}`, // Keep if state resource is needed
            name: "State Value", // Keep if state resource is needed
            description: "Access to a state value", // Keep if state resource is needed
            mimeType: "application/json" // Keep if state resource is needed
        }
    ]
}));

// Update ReadResourceRequestSchema handler to use streamsIntegration.redStream
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
    const { uri } = request.params;
    const localRedStream = streamsIntegration.redStream; // Get the single RedStream instance

    // Ensure the connection is ready (optional, RedStream might handle internally)
    // await localRedStream.ensureConnected(); // Assuming RedStream has such a method or handles it

    // Parse task resource
    const taskMatch = uri.match(/^task:\/\/([^/]+)$/);
    if (taskMatch) {
        const taskId = taskMatch[1];
        // Use localRedStream directly, assuming it handles connection retries internally
        const task = await localRedStream.readMessages('adapt:task:boomerang:tasks', {
            count: 1, // Example: fetch only the latest state for the task ID
            start: taskId, // Assuming task ID can be used as stream ID start/end
            end: taskId
        });
        // Process the result (assuming readMessages returns an array)
        const taskData = task && task.length > 0 ? task[0] : null; 
        return {
            contents: [{
                uri,
                mimeType: "application/json",
                text: JSON.stringify(taskData) // Return the found task data or null
            }]
        };
    }

    // Parse stream resource
    const streamMatch = uri.match(/^stream:\/\/([^/]+)\/latest$/);
    if (streamMatch) {
        const streamName = streamMatch[1];
        // Use localRedStream directly
        const messages = await localRedStream.readMessages(streamName, {
            count: 10, // Example: fetch last 10 messages
            reverse: true // Read newest first
        });
        return {
            contents: [{
                uri,
                mimeType: "application/json",
                text: JSON.stringify({ messages }) // Return the array of messages
            }]
        };
    }

    // Parse state resource
    const stateMatch = uri.match(/^state:\/\/([^/]+)$/);
    if (stateMatch) {
        const key = stateMatch[1];
        // Use localRedStream directly
        const result = await localRedStream.getState(key); // Assuming getState exists on RedStream
        return {
            contents: [{
                uri,
                mimeType: "application/json",
                text: JSON.stringify(result) // Return the state value
            }]
        };
    }

    // If no match, throw an error
    throw new Error(`Invalid or unsupported resource URI: ${uri}`);
});

// Removed the large CallToolRequestSchema handler block.
// Tool execution is now handled by StreamsIntegration.registerTools(server)


// Cleanup function (Update to close StreamsIntegration)
async function cleanup() {
    try {
        // Send shutdown notification (optional, might be handled by StreamsIntegration)
        if (streamsIntegration && streamsIntegration.redStream) { // Check if initialized
            try {
                // Assuming publishMessage exists and handles connection state
                await streamsIntegration.redStream.publishMessage('adapt:system:mcp:control', {
                    type: 'shutdown', // Standard shutdown message type
                    server: 'redis_mcp_server', // Identify the server shutting down
                    timestamp: new Date().toISOString() // Timestamp the event
                });
            } catch (e) {
                console.error("Error sending shutdown notification via StreamsIntegration:", e);
            }
        }
        
        // Close StreamsIntegration (which should handle closing its RedStream instance)
        if (streamsIntegration) {
            await streamsIntegration.close();
            console.log("StreamsIntegration closed.");
        }
        // Removed direct redStream.close() as it's handled by streamsIntegration.close()

    } catch (error) {
        console.error("Error during cleanup:", error);
    }
    // Exit with error code 1 on cleanup after error, 0 otherwise? Consider process exit logic.
    process.exit(1); // Exit indicating an issue occurred if cleanup was triggered by error
}

// Handle process termination
process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);

main().catch((error) => {
    console.error("Fatal error in main():", error);
    cleanup();
});
