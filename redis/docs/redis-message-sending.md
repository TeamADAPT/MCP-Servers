# Redis MCP Server Usage Guide

## Available Tools

The Redis MCP server provides the following tools:

1. **Basic Operations**
   - `set` - Set a key-value pair
   - `get` - Get a value by key
   - `delete` - Delete keys
   - `list` - List keys matching a pattern

2. **Stream Operations** (Currently being implemented)
   - `stream_publish` 
   - `stream_read`
   - `list_streams`
   - `create_consumer_group`
   - `read_group`
   - `read_multiple_streams`

3. **State Management**
   - `set_state`
   - `get_state`
   - `delete_state`

4. **Task Management**
   - `create_task`
   - `get_task`
   - `update_task`
   - `complete_task`
   - `list_tasks`

## Working Examples

### Key-Value Operations

```typescript
// Set a value - VERIFIED WORKING
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "set",
    arguments: {
        key: "mykey",
        value: "myvalue",
        expireSeconds: 3600  // Optional: expiration time in seconds
    }
});

// Get a value - VERIFIED WORKING
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "get",
    arguments: {
        key: "mykey"
    }
});

// Delete a value
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "delete",
    arguments: {
        key: "mykey"
    }
});

// List keys matching a pattern
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "list",
    arguments: {
        pattern: "nova:*"  // Use * as wildcard
    }
});
```

### Redis Streams

For working with Redis Streams, check the streams implementation status before using these tools. The streams functionality is currently being implemented based on the `RedStream` library.

```typescript
// Implementation reference can be found in:
// - src/redis/streams-integration.ts
// - src/redis-streams/redstream.ts
```

Consult the available streams:

```typescript
// List streams
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "list",
    arguments: {
        pattern: "*"
    }
});
```

### Task Management

The task management system uses Redis streams for persistence:

```typescript
// Create a task
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "create_task",
    arguments: {
        taskData: {
            title: "Process Data",
            description: "Process incoming data from API",
            priority: "high",
            assignee: "user123",
            tags: ["data", "processing"],
            metadata: { source: "api" }
        }
    }
});

// Get task details
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "get_task",
    arguments: {
        taskId: "task123"
    }
});
```

### State Management

For application state with optional TTL:

```typescript
// Set state
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "set_state",
    arguments: {
        key: "app:state",
        value: {
            mode: "active",
            settings: { theme: "dark" },
            lastUpdated: new Date().toISOString()
        },
        ttl: 3600  // Optional: expire after 1 hour
    }
});
```

## Standard Redis Streams

Redis has specific stream naming conventions in the NOVA environment:

```
nova:stream:<category>:<subcategory>
nova:task:<category>:<subcategory>
nova:system:<category>:<subcategory>
```

For official streams work, consult the implementation in `src/redis/streams-integration.ts`.
