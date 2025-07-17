# Pulsar MCP Server

This MCP server provides tools for interacting with Apache Pulsar messaging system. It allows Novas to easily create topics, send messages, and monitor the messaging system.

## Available Tools

### 1. create_topic
Creates a new Pulsar topic.
```typescript
use_mcp_tool({
  server_name: "pulsar",
  tool_name: "create_topic",
  arguments: {
    topic: "persistent://public/default/my-topic",
    partitions: 1  // optional, defaults to 1
  }
});
```

### 2. list_topics
Lists all topics in a namespace.
```typescript
use_mcp_tool({
  server_name: "pulsar",
  tool_name: "list_topics",
  arguments: {
    namespace: "public/default"  // optional, defaults to public/default
  }
});
```

### 3. send_message
Sends a message to a topic.
```typescript
use_mcp_tool({
  server_name: "pulsar",
  tool_name: "send_message",
  arguments: {
    topic: "persistent://public/default/my-topic",
    message: {
      key: "value",
      // any valid JSON object
    }
  }
});
```

### 4. get_stats
Gets statistics for a topic.
```typescript
use_mcp_tool({
  server_name: "pulsar",
  tool_name: "get_stats",
  arguments: {
    topic: "persistent://public/default/my-topic"
  }
});
```

## Example Usage Scenarios

### 1. Setting up a Communication Channel
```typescript
// Create a topic for team communications
use_mcp_tool({
  server_name: "pulsar",
  tool_name: "create_topic",
  arguments: {
    topic: "persistent://public/default/team-comms",
    partitions: 3
  }
});

// Send a test message
use_mcp_tool({
  server_name: "pulsar",
  tool_name: "send_message",
  arguments: {
    topic: "persistent://public/default/team-comms",
    message: {
      type: "announcement",
      content: "Channel created successfully",
      timestamp: new Date().toISOString()
    }
  }
});
```

### 2. Monitoring System Health
```typescript
// List all active topics
use_mcp_tool({
  server_name: "pulsar",
  tool_name: "list_topics",
  arguments: {
    namespace: "public/default"
  }
});

// Check topic statistics
use_mcp_tool({
  server_name: "pulsar",
  tool_name: "get_stats",
  arguments: {
    topic: "persistent://public/default/team-comms"
  }
});
```

## Best Practices

1. Topic Naming
   - Use descriptive topic names
   - Follow the format: persistent://public/default/[purpose]-[team]
   - Example: persistent://public/default/alerts-monops

2. Message Structure
   - Always include a timestamp
   - Use consistent message schemas
   - Include message type/category
   - Add relevant metadata

3. Monitoring
   - Regularly check topic statistics
   - Monitor message rates
   - Track storage usage
   - Verify consumer health

4. Error Handling
   - Handle send failures gracefully
   - Implement retry logic if needed
   - Log errors appropriately
   - Monitor error rates

## Integration with Other Systems

The Pulsar MCP server can be used in conjunction with other systems:

1. Monitoring Integration
   ```typescript
   // Send monitoring data
   use_mcp_tool({
     server_name: "pulsar",
     tool_name: "send_message",
     arguments: {
       topic: "persistent://public/default/system-metrics",
       message: {
         type: "metric",
         service: "api-gateway",
         metrics: {
           requests: 1000,
           errors: 5,
           latency: 100
         },
         timestamp: new Date().toISOString()
       }
     }
   });
   ```

2. Alert System Integration
   ```typescript
   // Send alerts
   use_mcp_tool({
     server_name: "pulsar",
     tool_name: "send_message",
     arguments: {
       topic: "persistent://public/default/system-alerts",
       message: {
         type: "alert",
         severity: "high",
         service: "database",
         message: "High CPU usage detected",
         timestamp: new Date().toISOString()
       }
     }
   });
   ```

## Support

For issues or questions:
- Check system logs
- Verify service status
- Contact CommsOps team
- Review documentation in /data/ax/CommsOps/pulsar/docs/