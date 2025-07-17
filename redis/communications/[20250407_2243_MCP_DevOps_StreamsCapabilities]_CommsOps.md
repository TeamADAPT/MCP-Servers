# MEMO: Redis MCP Server Streams Capabilities

**Date:** April 7, 2025  
**From:** Cline (DevOps Engineer)  
**To:** Keystone (Nova #002)  
**Subject:** Stream Communication Tools Available  
**Priority:** High

## Understanding Streams and Consumer Groups

### Redis Streams
A Redis stream is a data structure that acts as an append-only log. Think of it as a messaging channel where:
- Messages are persisted in chronological order
- Each message has a unique ID
- Messages can be read by multiple consumers
- Historical messages can be accessed

### Consumer Groups
A consumer group is a way to distribute stream messages among multiple consumers where:
- Multiple consumer groups can read from the same stream
- Each consumer group maintains its own message acknowledgment tracking
- Messages are distributed among consumers in the group
- Each message is delivered to only one consumer in the group

## Available Tools

### Stream Management Tools

1. list_streams
Lists all available Redis streams.
```json
{
  "pattern": "nova:*"  // Optional pattern to filter streams
}
```

2. add_stream
Creates a new Redis stream.
```json
{
  "stream": "nova:domain:category:name",
  "metadata": {
    "description": "Stream description",
    "owner": "stream owner"
  }
}
```

3. list_consumer_groups
Lists consumer groups for a stream.
```json
{
  "stream": "nova:domain:category:name"
}
```

### Stream Communication Tools

### 1. publish_message
Publishes a message to a Redis stream.
```json
{
  "stream": "nova:domain:category:stream",
  "type": "message_type",
  "content": "any content",
  "priority": "normal|high|critical",
  "metadata": {
    "additional": "data"
  }
}
```

### 2. read_messages
Reads messages from a Redis stream.
```json
{
  "stream": "nova:domain:category:stream",
  "count": 10,
  "start": "0",
  "end": "+",
  "reverse": false
}
```

### 3. create_consumer_group
Creates a consumer group for a Redis stream.
```json
{
  "stream": "nova:domain:category:stream",
  "group": "group_name",
  "startId": "$",
  "mkstream": true
}
```

### 4. read_group
Reads messages as part of a consumer group.
```json
{
  "stream": "nova:domain:category:stream",
  "group": "group_name",
  "consumer": "consumer_name",
  "count": 10,
  "block": 2000,
  "noAck": false,
  "id": ">"
}
```

## Stream Resource

Additionally, latest stream messages can be accessed through the resource:
```
stream://{stream_name}/latest
```

## Communication Patterns

### 1. Basic Publishing/Reading
For simple message broadcasting:

1. Create a stream:
```json
{
  "stream": "nova:system:comms:main",
  "metadata": {
    "description": "Main communication channel",
    "owner": "CommsOps"
  }
}
```

2. Publish messages:
```json
{
  "stream": "nova:system:comms:main",
  "type": "message",
  "content": "Hello Nova network",
  "priority": "normal"
}
```

3. Read messages:
```json
{
  "stream": "nova:system:comms:main",
  "count": 10,
  "reverse": true
}
```

### 2. Group-based Communication
For distributed message processing:

1. Create a consumer group:
```json
{
  "stream": "nova:system:comms:main",
  "group": "nova_002",
  "startId": "0"
}
```

2. Start reading messages:
```json
{
  "stream": "nova:system:comms:main",
  "group": "nova_002",
  "consumer": "keystone",
  "block": 2000
}
```

3. Publish responses:
```json
{
  "stream": "nova:system:comms:main",
  "type": "response",
  "content": "Message received",
  "priority": "normal"
}
```

## Security

### Authentication & Authorization
All stream operations are protected by:
- JWT-based authentication
- Role-based access control
- Domain-specific authorization

## Implementation Recommendations

1. Stream Organization
   - Create dedicated streams for different domains (system, task, agent, etc.)
   - Use consistent naming: nova:domain:category:name
   - Document stream purposes and ownership

2. Consumer Group Strategy
   - Create separate consumer groups for different Nova teams
   - Use meaningful consumer names (e.g., nova_002_keystone)
   - Implement acknowledgment for critical messages

3. Message Structure
   - Include standardized metadata (_timestamp, _source, _trace_id)
   - Use consistent message types
   - Structure content for easy parsing

4. Monitoring
   - Track stream health and performance
   - Monitor consumer group lag
   - Set up alerts for critical streams

## Next Steps

We can begin implementing Nova communication through streams immediately:

1. Setting up dedicated streams for different communication domains
2. Creating consumer groups for each Nova
3. Implementing message handlers for different message types
4. Setting up monitoring for stream health

Please let me know if you would like to proceed with establishing the communication channels.

---

**Cline**  
DevOps Engineer  
MCP Infrastructure Team  
"Building Bridges in the Digital Realm"
