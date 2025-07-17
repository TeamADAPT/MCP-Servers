# Redis MCP Server Memory Bank

The Memory Bank is a feature of the Redis MCP Server that provides persistent storage for memories that can be accessed by Claude and other LLMs.

## Overview

The Memory Bank uses Redis as a backend to store and retrieve memories. It provides a standardized interface for memory operations through the MCP protocol.

## Features

- **Persistent Memory Storage**: Store memories that persist across sessions
- **Memory Categories**: Organize memories into categories (system, user, conversation, task, knowledge)
- **Priority Levels**: Assign priority levels to memories (low, medium, high, critical)
- **Time-to-Live (TTL)**: Set expiration times for memories
- **Memory Tracking**: Track memory operations in a dedicated stream

## Memory Bank Tools

The Memory Bank provides the following tools through the MCP protocol:

### remember

Stores a memory in the memory bank.

**Input Parameters:**
- `key` (required): Memory key
- `value` (required): Memory content
- `category` (optional): Memory category (system, user, conversation, task, knowledge)
- `priority` (optional): Memory priority (low, medium, high, critical)
- `ttl` (optional): Time to live in seconds (0 = no expiration)

**Example:**
```json
{
  "key": "user_preferences",
  "value": {
    "theme": "dark",
    "language": "en"
  },
  "category": "user",
  "priority": "medium",
  "ttl": 86400
}
```

### recall

Retrieves a memory from the memory bank.

**Input Parameters:**
- `key` (required): Memory key

**Example:**
```json
{
  "key": "user_preferences"
}
```

### forget

Deletes a memory from the memory bank.

**Input Parameters:**
- `key` (required): Memory key

**Example:**
```json
{
  "key": "user_preferences"
}
```

### list_memories

Lists all memories or memories in a specific category.

**Input Parameters:**
- `category` (optional): Memory category filter

**Example:**
```json
{
  "category": "user"
}
```

## Memory Categories

The Memory Bank supports the following categories:

- **system**: System-related memories (permanent retention)
- **user**: User-related memories (long-term retention)
- **conversation**: Conversation-related memories (medium-term retention)
- **task**: Task-related memories (task-dependent retention)
- **knowledge**: Knowledge base memories (permanent retention)

## Memory Priority Levels

The Memory Bank supports the following priority levels:

- **low**: Low priority memories
- **medium**: Medium priority memories
- **high**: High priority memories
- **critical**: Critical priority memories

## Memory Bank Stream

The Memory Bank uses a dedicated Redis stream (`nova:memory:redis:bank`) to track memory operations. Each operation (store, retrieve, delete) is recorded in the stream with metadata.

## Usage Examples

### Storing a Memory

```javascript
const response = await sendRequest(mcpServer, 'call_tool', {
  name: 'remember',
  arguments: {
    key: 'user_preferences',
    value: {
      theme: 'dark',
      language: 'en'
    },
    category: 'user',
    priority: 'medium',
    ttl: 86400
  }
});
```

### Retrieving a Memory

```javascript
const response = await sendRequest(mcpServer, 'call_tool', {
  name: 'recall',
  arguments: {
    key: 'user_preferences'
  }
});
```

### Deleting a Memory

```javascript
const response = await sendRequest(mcpServer, 'call_tool', {
  name: 'forget',
  arguments: {
    key: 'user_preferences'
  }
});
```

### Listing Memories

```javascript
const response = await sendRequest(mcpServer, 'call_tool', {
  name: 'list_memories',
  arguments: {
    category: 'user'
  }
});
```

## Implementation Details

The Memory Bank is implemented in the `memory-bank.ts` file in the `src/redis` directory. It uses the RedStream class to interact with Redis and provides a clean API for memory operations.

## Testing

You can test the Memory Bank functionality using the provided test scripts:

- `scripts/test-memory-bank.js`: Tests the Memory Bank directly
- `scripts/test-redis-mcp-memory.js`: Tests the Memory Bank through the MCP protocol