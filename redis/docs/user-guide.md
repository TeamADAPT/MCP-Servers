# Redis MCP Server User Guide

## Overview
The Redis MCP Server provides a set of tools for interacting with Redis streams, managing tasks, and handling state through the Model Context Protocol (MCP). This guide covers all available operations and their usage.

## Table of Contents
- [Getting Started](#getting-started)
- [Basic Operations](#basic-operations)
- [Stream Operations](#stream-operations)
- [Task Management](#task-management)
- [State Management](#state-management)
- [Best Practices](#best-practices)

## Getting Started

### Connection
The Redis MCP server connects automatically to the configured Redis cluster. No additional connection setup is required from users.

### Tool Overview
Available tools are categorized into:
- Basic Redis operations (get/set)
- Stream operations (publish/subscribe)
- Task management (create/update/complete)
- State management (set/get/delete)

## Basic Operations

### Set and Get Values
```typescript
// Set a value
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "set",
    arguments: {
        key: "mykey",
        value: "myvalue",
        expireSeconds: 3600 // optional
    }
});

// Get a value
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "get",
    arguments: {
        key: "mykey"
    }
});
```

### Delete Keys
```typescript
// Delete a single key
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "delete",
    arguments: {
        key: "mykey"
    }
});

// Delete multiple keys
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "delete",
    arguments: {
        key: ["key1", "key2", "key3"]
    }
});
```

### List Keys
```typescript
// List all keys matching a pattern
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "list",
    arguments: {
        pattern: "user:*" // optional, defaults to "*"
    }
});
```

## Stream Operations

### Publishing Messages
```typescript
// Publish a message to a stream
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "stream_publish",
    arguments: {
        stream: "mystream",
        message: {
            type: "event",
            data: { id: 123, name: "example" }
        },
        maxlen: 1000 // optional
    }
});
```

### Reading Messages
```typescript
// Read messages from a stream
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "stream_read",
    arguments: {
        stream: "mystream",
        count: 10, // optional
        reverse: false // optional
    }
});
```

### Consumer Groups
```typescript
// Create a consumer group
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "create_consumer_group",
    arguments: {
        stream: "mystream",
        groupName: "mygroup",
        startId: "$", // optional, defaults to "$" (latest)
        mkstream: true // optional, create stream if not exists
    }
});

// Read from a consumer group
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "read_group",
    arguments: {
        stream: "mystream",
        group: "mygroup",
        consumer: "consumer1",
        count: 10, // optional
        block: 2000, // optional, block for 2 seconds
        noAck: false, // optional
        id: ">" // optional, defaults to ">" (new messages)
    }
});
```

### Multiple Streams
```typescript
// Read from multiple streams
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "read_multiple_streams",
    arguments: {
        streams: ["stream1", "stream2"],
        count: 10, // optional
        block: 2000, // optional
        id: "0" // optional, defaults to "0"
    }
});
```

## Task Management

### Creating Tasks
```typescript
// Create a new task
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "create_task",
    arguments: {
        taskData: {
            name: "Process Data",
            priority: "high",
            metadata: { source: "api" }
        }
    }
});
```

### Managing Tasks
```typescript
// Get task details
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "get_task",
    arguments: {
        taskId: "task123"
    }
});

// Update task
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "update_task",
    arguments: {
        taskId: "task123",
        updates: {
            status: "processing",
            progress: 50
        }
    }
});

// Complete task
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "complete_task",
    arguments: {
        taskId: "task123",
        result: {
            status: "success",
            data: { processed: 100 }
        }
    }
});
```

### Listing Tasks
```typescript
// List tasks with filtering
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "list_tasks",
    arguments: {
        pattern: "backup:*", // optional
        status: "completed" // optional
    }
});
```

## State Management

### Managing State
```typescript
// Set state
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "set_state",
    arguments: {
        key: "app:state",
        value: {
            mode: "active",
            settings: { theme: "dark" }
        },
        ttl: 3600 // optional
    }
});

// Get state
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "get_state",
    arguments: {
        key: "app:state"
    }
});

// Delete state
await mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "delete_state",
    arguments: {
        key: "app:state"
    }
});
```

## Best Practices

### Key Naming Conventions
- Use colon `:` as namespace separator
- Use descriptive prefixes
- Keep keys short but meaningful
Examples:
```
user:1234:profile
order:5678:status
stream:events:system
task:backup:daily
```

### Stream Management
- Use appropriate stream lengths (maxlen)
- Create consumer groups for parallel processing
- Handle acknowledgments properly
- Use meaningful consumer names

### Task Management
- Include sufficient task metadata
- Use consistent status values
- Handle task updates atomically
- Clean up completed tasks

### Error Handling
- Always check for error responses
- Implement proper retry logic
- Log errors appropriately
- Handle timeouts gracefully

### Performance Tips
- Batch operations when possible
- Use appropriate read timeouts
- Monitor stream lengths
- Clean up unused keys
- Use TTL for temporary data
