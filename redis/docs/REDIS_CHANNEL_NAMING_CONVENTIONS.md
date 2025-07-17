# Redis Channel Naming Conventions for MCP Integration

## Overview

This document outlines the standardized Redis channel naming conventions that must be followed for all Redis Streams used in MCP integrations. These conventions ensure consistency, discoverability, and proper integration with the broader Nova ecosystem.

## ADAPT Stream Naming Schema

All Redis stream names must follow this convention:

```
nova:{domain}:{entity}:{function}
```

Where:

- `nova:` - Required prefix identifying the Nova system
- `{domain}` - System domain (e.g., system, task, agent, user, memory)
- `{entity}` - Specific entity within the domain (e.g., boomerang, sentinel, cline)
- `{function}` - Function or purpose of the stream (e.g., tasks, events, logs)

## Reserved Domains

The following domains are reserved and have specific governance:

| Domain | Governance | Purpose |
|--------|------------|---------|
| `system` | MemCommsOps | System-level operations and control plane |
| `task` | CommsOps | Task management and orchestration |
| `agent` | AgentOps | Agent communication and coordination |
| `user` | UserOps | User interactions and sessions |
| `memory` | MemOps | Memory operations and knowledge management |

## Common Stream Allocations

The following streams are commonly used across MCP servers:

| Stream Name | Purpose | Access |
|-------------|---------|--------|
| `nova:task:boomerang:tasks` | Task creation and updates | Read/Write |
| `nova:task:boomerang:events` | Task state change events | Read/Write |
| `nova:system:mcp:heartbeat` | MCP server health signals | Write |
| `nova:system:mcp:control` | Control messages for MCP servers | Read |
| `nova:memory:redis:state` | Redis state management | Read/Write |

## Service-Specific Stream Allocations

For specific MCP services, the following naming pattern should be used:

```
nova:{domain}:{service-name}:{function}
```

Examples:

| Stream Name | Purpose | Access |
|-------------|---------|--------|
| `nova:system:reflectord:status` | ReflectorD daemon status updates | Write |
| `nova:system:reflectord:control` | Control messages for ReflectorD | Read |
| `nova:memory:reflectord:data` | ReflectorD data operations | Read/Write |
| `nova:system:ethos:status` | Ethos service status updates | Write |
| `nova:memory:ethos:data` | Ethos data operations | Read/Write |

## Stream Usage Guidelines

### Publishing Messages

When publishing messages to a stream, follow these guidelines:

1. **Validate Stream Name**: Ensure the stream name follows the ADAPT naming schema
2. **Add Standard Fields**:
   - `_timestamp`: Current timestamp (milliseconds since epoch)
   - `_source`: Service identifier (e.g., 'reflectord', 'ethos-mcp')
   - `_trace_id`: Unique trace ID for the operation

Example:

```javascript
// Publishing a message to a stream
const messageId = await redisClient.xadd(
  'nova:system:mcp:heartbeat',
  '*',  // Auto-generate message ID
  'status', 'active',
  'timestamp', Date.now(),
  'source', 'ethos-mcp',
  'trace_id', generateTraceId()
);
```

### Consuming Messages

When consuming messages from a stream, follow these guidelines:

1. **Use Consumer Groups**: Create and use consumer groups for reliable message processing
2. **Acknowledge Messages**: Acknowledge messages after successful processing
3. **Handle Errors**: Implement proper error handling and retry logic

Example:

```javascript
// Creating a consumer group
try {
  await redisClient.xgroup('CREATE', 'nova:system:mcp:control', 'mcp-group', '$', 'MKSTREAM');
} catch (error) {
  // Group may already exist, which is fine
  if (!error.message.includes('BUSYGROUP')) {
    throw error;
  }
}

// Reading messages from a stream
const results = await redisClient.xreadgroup(
  'GROUP', 'mcp-group', 'mcp-consumer',
  'COUNT', 10,
  'BLOCK', 2000,
  'STREAMS', 'nova:system:mcp:control', '>'
);
```

## Performance Considerations

1. **Stream Size Management**:
   - Use `XADD` with MAXLEN option to automatically trim streams
   - Maintain stream size below 10,000 messages per stream

2. **Message Batching**:
   - Batch read operations with appropriate COUNT values
   - Process messages in efficient batches

## Implementation Example

Here's a complete example of how to implement the Redis channel naming conventions in your code:

```javascript
const Redis = require('ioredis');

// Connect to Redis
const redis = new Redis.Cluster([
  { host: 'redis-cluster-01.memcommsops.internal', port: 7000 },
  { host: 'redis-cluster-02.memcommsops.internal', port: 7001 },
  { host: 'redis-cluster-03.memcommsops.internal', port: 7002 }
], {
  redisOptions: {
    username: 'mcp-service-readwrite',
    password: 'mcp-service-readwrite-password',
    connectTimeout: 5000,
    maxRetriesPerRequest: 3
  },
  scaleReads: 'slave',
  maxRedirections: 16,
  retryDelayOnFailover: 300
});

// Publish status update
async function publishStatusUpdate(status) {
  const stream = 'nova:system:mcp:heartbeat';
  const messageId = await redis.xadd(
    stream,
    'MAXLEN', '~', 1000,  // Keep approximately 1000 messages
    '*',  // Auto-generate message ID
    'status', status,
    'timestamp', Date.now(),
    'source', 'mcp-service',
    'trace_id', generateTraceId()
  );
  console.log(`Published status update to ${stream}: ${messageId}`);
  return messageId;
}

// Consume control messages
async function consumeControlMessages() {
  const stream = 'nova:system:mcp:control';
  const group = 'mcp-group';
  const consumer = 'mcp-consumer';
  
  // Create consumer group if not exists
  try {
    await redis.xgroup('CREATE', stream, group, '$', 'MKSTREAM');
  } catch (error) {
    // Group may already exist, which is fine
    if (!error.message.includes('BUSYGROUP')) {
      throw error;
    }
  }
  
  // Read messages from stream
  const results = await redis.xreadgroup(
    'GROUP', group, consumer,
    'COUNT', 10,
    'BLOCK', 2000,
    'STREAMS', stream, '>'
  );
  
  if (results && results.length > 0) {
    const messages = results[0][1];
    for (const [messageId, fields] of messages) {
      // Process message
      console.log(`Received control message ${messageId}`);
      
      // Convert array of field-value pairs to object
      const message = {};
      for (let i = 0; i < fields.length; i += 2) {
        message[fields[i]] = fields[i + 1];
      }
      
      // Process the message
      handleControlMessage(message);
      
      // Acknowledge the message
      await redis.xack(stream, group, messageId);
    }
  }
}

// Generate trace ID
function generateTraceId() {
  return Math.random().toString(36).substring(2, 15) + 
         Math.random().toString(36).substring(2, 15);
}

// Handle control message
function handleControlMessage(message) {
  console.log('Processing control message:', message);
  // Implement your control message handling logic here
}
```

## Compliance Requirements

All MCP servers must:

1. Follow the ADAPT stream naming schema for all Redis streams
2. Use the appropriate domain for their operations
3. Include the required standard fields in all messages
4. Implement proper consumer group management
5. Follow the performance considerations

Failure to comply with these naming conventions may result in integration issues and operational problems.

---

**Last Updated:** April 13, 2025  
**Author:** Echo, Head of MemCommsOps Division