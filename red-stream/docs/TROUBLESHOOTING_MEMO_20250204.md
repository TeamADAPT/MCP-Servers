# Red-Stream MCP Server Troubleshooting Memo
Date: February 4, 2025 07:15 MST
Author: Roo (AI Engineer)
Subject: Tool Registration Issue in Red-Stream MCP Server

## Current Status
The red-stream MCP server is partially working - some tools like `get_stream_messages` function correctly, but newly added tools like `list_streams` are not being recognized, resulting in "Unknown tool" errors.

## What Works
1. Server starts successfully
2. Redis connection is established
3. Existing tools (e.g., get_stream_messages) function properly
4. Socket activation is implemented

## What Doesn't Work
1. The `list_streams` tool returns "Unknown tool: list_streams" error
2. Other newly added tools are also not recognized

## Investigation Steps Taken

1. **Initial Implementation**
   - Added list_streams tool to server capabilities
   - Implemented list_streams functionality
   - Added TypeScript types and interfaces
   - Result: Tool not recognized

2. **Compared with Working Implementation**
   - Examined working slack-mcp server implementation
   - Noted differences in tool registration approach
   - Attempted to replicate slack-mcp pattern
   - Result: Still not working

3. **Server Configuration Changes**
   - Modified server initialization to use empty tools object
   - Updated tool registration in ListToolsRequestSchema handler
   - Implemented proper socket activation
   - Result: No improvement

4. **TypeScript Issues**
   - Fixed Redis client type definitions
   - Addressed type errors in message handling
   - Result: Build succeeds but runtime issues persist

## Key Observations
1. The error suggests a tool registration issue rather than a Redis connectivity problem
2. Working tools and new tools use the same registration pattern but behave differently
3. TypeScript errors don't seem to be the root cause

## Current Implementation Details
1. Server initialization:
```typescript
const server = new Server(
    {
        name: 'red-stream',
        version: '0.2.0',
    },
    {
        capabilities: {
            tools: {},
        },
    }
);
```

2. Tool registration:
```typescript
server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
        {
            name: 'list_streams',
            description: 'List all available streams',
            inputSchema: {
                type: 'object',
                properties: {
                    pattern: { type: 'string', description: 'Pattern to match stream names', default: '*' },
                },
            },
        },
        // ... other tools
    ],
}));
```

## Questions for Specialist
1. Is there a difference in how tool registration is handled between the initial capabilities and the ListToolsRequestSchema handler?
2. Could there be an issue with the MCP protocol version or compatibility?
3. Are there any known issues with adding new tools to an existing MCP server?
4. Should we consider rebuilding the server from scratch using a different approach?

## Next Steps
1. Review MCP protocol documentation for tool registration requirements
2. Compare tool registration patterns across other working MCP servers
3. Consider implementing a minimal test server with just the list_streams tool
4. Investigate if there are any MCP server lifecycle events we need to handle

## Additional Context
- The server is running in a systemd-managed environment
- Redis connectivity is confirmed working
- Other MCP servers (slack-mcp, pulsar) are functioning correctly
- TypeScript build completes successfully despite type errors

Please let me know if you need any additional information or would like to explore specific aspects of the implementation.