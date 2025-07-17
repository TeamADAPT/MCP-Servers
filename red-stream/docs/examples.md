# Red-Stream MCP Server Examples

## Common Use Cases

### 1. Event Streaming System

```javascript
// Publish events
await use_mcp_tool({
  server_name: "red-stream",
  tool_name: "add_stream_message",
  arguments: {
    stream: "user-events",
    message: {
      type: "user_login",
      timestamp: new Date().toISOString(),
      data: {
        userId: "12345",
        device: "mobile",
        location: "US"
      }
    }
  }
});

// Create processing group
await use_mcp_tool({
  server_name: "red-stream",
  tool_name: "create_consumer_group",
  arguments: {
    stream: "user-events",
    group: "analytics-processor",
    start: "$"
  }
});

// Process events
await use_mcp_tool({
  server_name: "red-stream",
  tool_name: "read_group",
  arguments: {
    stream: "user-events",
    group: "analytics-processor",
    consumer: "worker-1",
    count: 10
  }
});

// Monitor consumer groups
await use_mcp_tool({
  server_name: "red-stream",
  tool_name: "list_groups",
  arguments: {
    stream: "user-events"
  }
});
```

### 2. Distributed Task Processing

```javascript
// Add tasks
await use_mcp_tool({
  server_name: "red-stream",
  tool_name: "add_stream_message",
  arguments: {
    stream: "image-processing-tasks",
    message: {
      taskId: "task-123",
      type: "resize",
      timestamp: new Date().toISOString(),
      data: {
        imageUrl: "https://YOUR-CREDENTIALS@YOUR-DOMAIN// Regular group status check
async function monitorGroups(stream) {
  const groups = await use_mcp_tool({
    server_name: "red-stream",
    tool_name: "list_groups",
    arguments: { stream }
  });
  
  for (const group of groups) {
    if (group.pending > 100) {
      console.warn(`High pending messages in group ${group.name}`);
    }
    if (group.consumers === 0) {
      console.error(`No active consumers in group ${group.name}`);
    }
  }
}
```

## Support

For implementation help:
- Documentation: /data/ax/DevOps/mcp_master/red-stream/docs/
- Slack: #mcp-support
- Email: mcp-team@memops.internal