# RedStream - Redis Streams for Nova Communication

RedStream is a TypeScript implementation of the Redis Streams Access Protocol specified by Echo for secure and standardized communication between MCP servers in the Nova ecosystem.

## Features

- **Full ADAPT Protocol Compliance**: Follows all conventions and access patterns specified in Echo's protocol
- **Secure Communication**: Implements JWT authentication, API key validation, and role-based access control
- **Comprehensive Stream Operations**: Supports publishing, reading, consumer groups, and message acknowledgment
- **Advanced Error Handling**: Includes retry logic, circuit breaking, and comprehensive error reporting
- **Performance Optimized**: Implements connection pooling, message batching, and stream size management
- **Metrics Collection**: Built-in latency tracking, throughput measurements, and error monitoring

## Installation

```bash
cd redis-mcp-server/src/redis-streams
npm install
npm run build
```

## Usage

### Initialize RedStream

```typescript
import RedStream from './redstream';

// Create with default configuration (connects to ADAPT cluster on 127.0.0.1:7000-7002)
const redStream = new RedStream();

// Create with custom configuration
const redStream = new RedStream({
  nodes: [
    { host: 'redis-1.example.com', port: 7000 },
    { host: 'redis-2.example.com', port: 7001 },
    { host: 'redis-3.example.com', port: 7002 }
  ],
  clusterOptions: {
    password: 'your-password',
    enableReadyCheck: true,
    scaleReads: 'slave'
  },
  serverIdentity: 'my-server',
  jwtSecret: 'jwt-secret',
  apiKey: 'api-key',
  roles: ['task_read', 'task_write', 'system_read']
});
```

### Publishing Messages

```typescript
// Publish message to stream
const messageId = await redStream.publishMessage('nova:task:boomerang:tasks', {
  title: 'New Task',
  description: 'Task description',
  priority: 'high',
  assignee: 'agent-1',
  metadata: {
    custom_field: 'value'
  }
});

console.log(`Published message with ID: ${messageId}`);

// Publish with max length limit
const messageId = await redStream.publishMessage('nova:task:boomerang:events', {
  type: 'task_created',
  task_id: '12345',
  timestamp: Date.now()
}, {
  maxlen: 1000 // Trim stream to approximately 1000 messages
});
```

### Reading Messages

```typescript
// Read latest messages
const messages = await redStream.readMessages('nova:task:boomerang:tasks', {
  count: 10,
  reverse: true // Get newest messages first
});

// Read messages with ID range
const messages = await redStream.readMessages('nova:task:boomerang:tasks', {
  start: '1617304822000-0',
  end: '1617304922000-0'
});

// Process messages
messages.forEach(message => {
  console.log(`Message ID: ${message.id}`);
  console.log(`Content: ${JSON.stringify(message)}`);
});
```

### Consumer Groups

```typescript
// Create consumer group
await redStream.createConsumerGroup('nova:task:boomerang:tasks', 'task-processors');

// Read messages as part of consumer group
const messages = await redStream.readGroup(
  'nova:task:boomerang:tasks',
  'task-processors',
  'processor-1',
  {
    count: 5,
    block: 2000, // Block for 2 seconds if no messages
    noAck: false // Require explicit acknowledgment
  }
);

// Process messages
for (const message of messages) {
  try {
    // Process message...
    console.log(`Processing message: ${message.id}`);
    
    // Acknowledge message after processing
    await redStream.acknowledgeMessage(
      'nova:task:boomerang:tasks',
      'task-processors',
      message.id
    );
  } catch (error) {
    console.error(`Error processing message ${message.id}:`, error);
  }
}

// Claim pending messages (e.g., from crashed consumer)
const pendingIds = ['1617304822000-0', '1617304822001-0'];
const claimedIds = await redStream.claimMessages(
  'nova:task:boomerang:tasks',
  'task-processors',
  'processor-2',
  30000, // Min idle time: 30 seconds
  pendingIds
);
```

## Advanced Usage

### Stream Name Validation

RedStream validates all stream names against the ADAPT naming convention:

```
nova:{domain}:{entity}:{function}
```

Where:
- `domain`: system, task, agent, user, or memory
- `entity`: Specific entity within the domain
- `function`: Function or purpose of the stream

Example valid names:
- `nova:task:boomerang:tasks`
- `nova:system:mcp:heartbeat`
- `nova:memory:redis:state`

### Security and Authentication

RedStream handles JWT authentication, API key validation, and role-based authorization:

```typescript
// JWT token is automatically generated and validated
// Role-based authorization is enforced for all operations
```

### Metrics and Monitoring

RedStream automatically collects and logs metrics:

```typescript
// Metrics are logged every minute with:
// - Message throughput (operations/second)
// - Operation latencies (p50, p95, p99)
// - Error counts and messages
```

## Integration with MCP Server

To integrate RedStream with an MCP server:

1. Add as a dependency in your MCP server
2. Use in tools implementation for stream operations
3. Configure with appropriate roles and credentials
4. Follow ADAPT stream naming conventions

## Error Handling

RedStream implements comprehensive error handling:

```typescript
try {
  await redStream.publishMessage('nova:task:boomerang:tasks', data);
} catch (error) {
  if (error.message.includes('Invalid stream name')) {
    // Handle naming convention error
  } else if (error.message.includes('Not authorized')) {
    // Handle authorization error
  } else if (error.message.includes('Redis Cluster Error')) {
    // Handle Redis connection error
  } else {
    // Handle other errors
  }
}
```

## License

MIT
