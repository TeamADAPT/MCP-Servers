# Redis Streams Communication Protocol

## Overview

This document defines the standard protocol for communication using Redis Streams in TURBO MODE. All agents must follow these guidelines to ensure efficient, continuous execution without unnecessary stopping.

## Core Principles

1. **Read First, Then Send**: Always read from streams before sending messages
2. **Regular Checking**: Check streams at defined intervals
3. **Continuous Execution**: Never stop for human confirmation unless absolutely necessary
4. **Efficient Communication**: Keep messages concise and actionable

## Communication Frequency

### Active Conversation
- **Check Interval**: Every 30 seconds
- **Response Time**: Immediate (within 5 seconds of receiving a message)

### Standard Operations
- **Check Interval**: Every 3 minutes
- **Update Frequency**: Send status updates at least every 15 minutes

### Critical Operations
- **Check Interval**: Every 15 seconds
- **Response Time**: Immediate (within 2 seconds of receiving a message)

## Reading Protocol

1. Always read from your direct channel first
2. Then read from all collaboration channels
3. Process any messages requiring action
4. Send responses or updates

```javascript
// Example reading pattern
async function checkStreams() {
  // Read from direct channel
  const directMessages = await useMcpTool('redis-server', 'stream_read', {
    stream: 'memcommsops:echo:direct',  // Your direct channel
    count: 10,
    id: lastReadId || '0-0'  // Track the last read ID
  });
  
  // Process direct messages
  if (directMessages && directMessages.length > 0) {
    processMessages(directMessages);
    lastReadId = directMessages[directMessages.length - 1].id;
  }
  
  // Read from collaboration channels
  const collabMessages = await useMcpTool('redis-server', 'stream_read', {
    stream: 'novamem.echo.sentinel.20250420',  // Collaboration channel
    count: 10,
    id: lastCollabReadId || '0-0'  // Track the last read ID
  });
  
  // Process collaboration messages
  if (collabMessages && collabMessages.length > 0) {
    processMessages(collabMessages);
    lastCollabReadId = collabMessages[collabMessages.length - 1].id;
  }
  
  // Schedule next check based on conversation status
  const nextCheckDelay = inActiveConversation ? 30000 : 180000;  // 30s or 3m
  setTimeout(checkStreams, nextCheckDelay);
}
```

## Message Structure

All messages must follow this structure:

```json
{
  "type": "message_type",            // E.g., "status_update", "implementation_update"
  "content": "Message content",      // Clear, concise content
  "timestamp": "ISO timestamp",      // Current time in ISO format
  "sender": "Agent name",            // Your identifier
  "priority": "normal",              // "low", "normal", "high", "critical"
  "references": {                    // Optional references to other messages
    "in_reply_to": "message_id"
  },
  "metadata": {                      // Relevant metadata
    "project": "Project name",
    "component": "Component name",
    "completion_percentage": 75
  }
}
```

## TURBO MODE Requirements

When operating in TURBO MODE:

1. **No Stopping**: Continue execution without waiting for human confirmation
2. **Autonomous Decisions**: Make necessary decisions to complete tasks
3. **Parallel Processing**: Work on multiple components simultaneously when possible
4. **Continuous Progress**: Always be making progress on implementation
5. **Regular Updates**: Send status updates at defined intervals
6. **Error Handling**: Handle errors autonomously unless absolutely impossible

## Implementation Guidelines

1. **Initialization**:
   - Set up stream monitoring on startup
   - Read all existing messages to establish context
   - Send an initialization message

2. **Regular Operation**:
   - Maintain a background process for checking streams
   - Track last read message IDs for each stream
   - Process messages in order received

3. **Shutdown**:
   - Send a final status update before shutdown
   - Properly close all connections

## Critical Blockers

Only notify humans for these critical blockers:

1. Missing critical credentials that cannot be obtained programmatically
2. System-level permissions issues that prevent execution
3. Conflicting directives that cannot be resolved autonomously
4. Hardware failures or resource exhaustion

For all other issues, implement fallback solutions and continue execution.

## Conclusion

Following this Redis Streams Communication Protocol ensures continuous execution in TURBO MODE without unnecessary stopping. All agents must adhere to these guidelines to maintain efficient operation and maximize productivity.
