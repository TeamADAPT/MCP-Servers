# MEMO: Redis MCP Server Specification for Boomerang Integration

**Date:** April 6, 2025  
**From:** Keystone (Nova #002)  
**To:** Cline  
**Subject:** Specification for Redis MCP Server with Boomerang Integration  
**Priority:** High

## 1. Overview

This document outlines the specification for a Redis MCP (Model Context Protocol) server that will integrate directly with the Boomerang task orchestration system. The Redis MCP server will provide a standardized interface for Boomerang to interact with Redis, enabling advanced task management, real-time communication, and state persistence capabilities.

## 2. Purpose and Objectives

### 2.1 Primary Purpose

To provide a robust, standardized interface between Boomerang and Redis that abstracts the complexity of Redis operations while exposing the full power of Redis for task orchestration.

### 2.2 Key Objectives

1. **Streamline Redis Operations**: Simplify complex Redis operations through a clean API
2. **Enable Advanced Task Management**: Provide tools for task creation, assignment, monitoring, and completion
3. **Facilitate Real-Time Communication**: Enable seamless communication between Novas via Redis Streams
4. **Ensure Data Persistence**: Provide reliable state persistence for tasks and workflows
5. **Support Boomerang Integration**: Integrate seamlessly with the Boomerang task orchestration system

## 3. Server Architecture

### 3.1 Core Components

1. **Redis Client Module**: Handles direct communication with Redis
2. **MCP Protocol Handler**: Implements the Model Context Protocol
3. **Tool Registry**: Manages available tools and their implementations
4. **Resource Registry**: Manages available resources and their access methods
5. **Authentication Module**: Handles authentication and authorization
6. **Logging and Monitoring**: Provides comprehensive logging and monitoring

### 3.2 Communication Flow

```
Boomerang → MCP Client → MCP Protocol → Redis MCP Server → Redis Client → Redis
   ↑                                           ↓
   └───────────────── Response ────────────────┘
```

### 3.3 Deployment Model

The Redis MCP server will be deployed as a Node.js application that can run:

1. As a standalone service
2. As a systemd service
3. Within a Docker container
4. As part of a Kubernetes deployment

## 4. Tool Specifications

The Redis MCP server will provide the following tools:

### 4.1 Task Management Tools

#### 4.1.1 `create_task`

Creates a new task in Redis.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Task title"
    },
    "description": {
      "type": "string",
      "description": "Task description"
    },
    "priority": {
      "type": "string",
      "enum": ["low", "medium", "high", "critical"],
      "default": "medium",
      "description": "Task priority"
    },
    "assignee": {
      "type": "string",
      "description": "Task assignee (Nova ID or mode)"
    },
    "parent_id": {
      "type": "string",
      "description": "Parent task ID (for subtasks)"
    },
    "due_date": {
      "type": "string",
      "format": "date-time",
      "description": "Task due date"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Task tags"
    },
    "metadata": {
      "type": "object",
      "description": "Additional task metadata"
    }
  },
  "required": ["title"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "description": "Generated task ID"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Task creation timestamp"
    }
  },
  "required": ["task_id", "created_at"]
}
```

#### 4.1.2 `get_task`

Retrieves a task from Redis.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "description": "Task ID to retrieve"
    }
  },
  "required": ["task_id"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "description": "Task ID"
    },
    "title": {
      "type": "string",
      "description": "Task title"
    },
    "description": {
      "type": "string",
      "description": "Task description"
    },
    "status": {
      "type": "string",
      "description": "Task status"
    },
    "priority": {
      "type": "string",
      "description": "Task priority"
    },
    "assignee": {
      "type": "string",
      "description": "Task assignee"
    },
    "parent_id": {
      "type": "string",
      "description": "Parent task ID"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Task creation timestamp"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Task update timestamp"
    },
    "due_date": {
      "type": "string",
      "format": "date-time",
      "description": "Task due date"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Task tags"
    },
    "metadata": {
      "type": "object",
      "description": "Additional task metadata"
    }
  },
  "required": ["task_id", "title", "status", "created_at"]
}
```

#### 4.1.3 `update_task`

Updates an existing task in Redis.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "description": "Task ID to update"
    },
    "title": {
      "type": "string",
      "description": "Updated task title"
    },
    "description": {
      "type": "string",
      "description": "Updated task description"
    },
    "status": {
      "type": "string",
      "enum": ["new", "in_progress", "blocked", "completed", "cancelled"],
      "description": "Updated task status"
    },
    "priority": {
      "type": "string",
      "enum": ["low", "medium", "high", "critical"],
      "description": "Updated task priority"
    },
    "assignee": {
      "type": "string",
      "description": "Updated task assignee"
    },
    "due_date": {
      "type": "string",
      "format": "date-time",
      "description": "Updated task due date"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Updated task tags"
    },
    "metadata": {
      "type": "object",
      "description": "Updated task metadata"
    }
  },
  "required": ["task_id"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "description": "Task ID"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Task update timestamp"
    }
  },
  "required": ["task_id", "updated_at"]
}
```

#### 4.1.4 `complete_task`

Marks a task as completed in Redis.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "description": "Task ID to complete"
    },
    "result": {
      "type": "string",
      "description": "Task completion result"
    },
    "artifacts": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Task artifacts"
    }
  },
  "required": ["task_id"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "description": "Task ID"
    },
    "completed_at": {
      "type": "string",
      "format": "date-time",
      "description": "Task completion timestamp"
    }
  },
  "required": ["task_id", "completed_at"]
}
```

#### 4.1.5 `list_tasks`

Lists tasks from Redis based on filters.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "description": "Filter by task status"
    },
    "assignee": {
      "type": "string",
      "description": "Filter by task assignee"
    },
    "parent_id": {
      "type": "string",
      "description": "Filter by parent task ID"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Filter by task tags"
    },
    "limit": {
      "type": "number",
      "description": "Maximum number of tasks to return",
      "default": 10
    },
    "offset": {
      "type": "number",
      "description": "Number of tasks to skip",
      "default": 0
    },
    "sort_by": {
      "type": "string",
      "enum": ["created_at", "updated_at", "due_date", "priority"],
      "default": "created_at",
      "description": "Field to sort by"
    },
    "sort_order": {
      "type": "string",
      "enum": ["asc", "desc"],
      "default": "desc",
      "description": "Sort order"
    }
  }
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "task_id": {
            "type": "string",
            "description": "Task ID"
          },
          "title": {
            "type": "string",
            "description": "Task title"
          },
          "status": {
            "type": "string",
            "description": "Task status"
          },
          "priority": {
            "type": "string",
            "description": "Task priority"
          },
          "assignee": {
            "type": "string",
            "description": "Task assignee"
          },
          "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "Task creation timestamp"
          },
          "due_date": {
            "type": "string",
            "format": "date-time",
            "description": "Task due date"
          }
        },
        "required": ["task_id", "title", "status"]
      }
    },
    "total": {
      "type": "number",
      "description": "Total number of tasks matching the filters"
    },
    "limit": {
      "type": "number",
      "description": "Maximum number of tasks returned"
    },
    "offset": {
      "type": "number",
      "description": "Number of tasks skipped"
    }
  },
  "required": ["tasks", "total", "limit", "offset"]
}
```

### 4.2 Stream Communication Tools

#### 4.2.1 `publish_message`

Publishes a message to a Redis stream.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "stream": {
      "type": "string",
      "description": "Stream name"
    },
    "type": {
      "type": "string",
      "description": "Message type"
    },
    "from": {
      "type": "string",
      "description": "Message sender"
    },
    "content": {
      "type": "string",
      "description": "Message content"
    },
    "priority": {
      "type": "string",
      "enum": ["low", "normal", "high", "critical"],
      "default": "normal",
      "description": "Message priority"
    },
    "metadata": {
      "type": "object",
      "description": "Additional message metadata"
    }
  },
  "required": ["stream", "content"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "message_id": {
      "type": "string",
      "description": "Generated message ID"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Message timestamp"
    }
  },
  "required": ["message_id", "timestamp"]
}
```

#### 4.2.2 `read_messages`

Reads messages from a Redis stream.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "stream": {
      "type": "string",
      "description": "Stream name"
    },
    "count": {
      "type": "number",
      "description": "Maximum number of messages to read",
      "default": 10
    },
    "start": {
      "type": "string",
      "description": "Start ID (exclusive)",
      "default": "0"
    },
    "end": {
      "type": "string",
      "description": "End ID (inclusive)",
      "default": "+"
    },
    "reverse": {
      "type": "boolean",
      "description": "Read in reverse order",
      "default": false
    }
  },
  "required": ["stream"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "messages": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "description": "Message ID"
          },
          "type": {
            "type": "string",
            "description": "Message type"
          },
          "from": {
            "type": "string",
            "description": "Message sender"
          },
          "content": {
            "type": "string",
            "description": "Message content"
          },
          "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "Message timestamp"
          },
          "priority": {
            "type": "string",
            "description": "Message priority"
          },
          "metadata": {
            "type": "object",
            "description": "Additional message metadata"
          }
        },
        "required": ["id", "content"]
      }
    },
    "next_id": {
      "type": "string",
      "description": "ID to use for the next read operation"
    }
  },
  "required": ["messages"]
}
```

#### 4.2.3 `create_consumer_group`

Creates a consumer group for a Redis stream.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "stream": {
      "type": "string",
      "description": "Stream name"
    },
    "group": {
      "type": "string",
      "description": "Consumer group name"
    },
    "start_id": {
      "type": "string",
      "description": "Start ID",
      "default": "$"
    },
    "mkstream": {
      "type": "boolean",
      "description": "Create stream if it doesn't exist",
      "default": true
    }
  },
  "required": ["stream", "group"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether the operation was successful"
    },
    "message": {
      "type": "string",
      "description": "Success or error message"
    }
  },
  "required": ["success"]
}
```

#### 4.2.4 `read_group`

Reads messages from a Redis stream as part of a consumer group.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "stream": {
      "type": "string",
      "description": "Stream name"
    },
    "group": {
      "type": "string",
      "description": "Consumer group name"
    },
    "consumer": {
      "type": "string",
      "description": "Consumer name"
    },
    "count": {
      "type": "number",
      "description": "Maximum number of messages to read",
      "default": 10
    },
    "block": {
      "type": "number",
      "description": "Block for this many milliseconds (0 = indefinitely)",
      "default": 2000
    },
    "no_ack": {
      "type": "boolean",
      "description": "Don't require acknowledgment",
      "default": false
    }
  },
  "required": ["stream", "group", "consumer"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "messages": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "description": "Message ID"
          },
          "type": {
            "type": "string",
            "description": "Message type"
          },
          "from": {
            "type": "string",
            "description": "Message sender"
          },
          "content": {
            "type": "string",
            "description": "Message content"
          },
          "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "Message timestamp"
          },
          "priority": {
            "type": "string",
            "description": "Message priority"
          },
          "metadata": {
            "type": "object",
            "description": "Additional message metadata"
          }
        },
        "required": ["id", "content"]
      }
    }
  },
  "required": ["messages"]
}
```

### 4.3 State Management Tools

#### 4.3.1 `set_state`

Sets a state value in Redis.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "key": {
      "type": "string",
      "description": "State key"
    },
    "value": {
      "type": "object",
      "description": "State value"
    },
    "ttl": {
      "type": "number",
      "description": "Time to live in seconds",
      "default": 0
    }
  },
  "required": ["key", "value"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether the operation was successful"
    }
  },
  "required": ["success"]
}
```

#### 4.3.2 `get_state`

Gets a state value from Redis.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "key": {
      "type": "string",
      "description": "State key"
    }
  },
  "required": ["key"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "value": {
      "type": "object",
      "description": "State value"
    },
    "ttl": {
      "type": "number",
      "description": "Remaining time to live in seconds"
    }
  }
}
```

#### 4.3.3 `delete_state`

Deletes a state value from Redis.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "key": {
      "type": "string",
      "description": "State key"
    }
  },
  "required": ["key"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether the operation was successful"
    }
  },
  "required": ["success"]
}
```

## 5. Resource Specifications

The Redis MCP server will provide the following resources:

### 5.1 Task Resources

#### 5.1.1 `task://{task_id}`

Provides direct access to a task's data.

**Response Schema:**
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "description": "Task ID"
    },
    "title": {
      "type": "string",
      "description": "Task title"
    },
    "description": {
      "type": "string",
      "description": "Task description"
    },
    "status": {
      "type": "string",
      "description": "Task status"
    },
    "priority": {
      "type": "string",
      "description": "Task priority"
    },
    "assignee": {
      "type": "string",
      "description": "Task assignee"
    },
    "parent_id": {
      "type": "string",
      "description": "Parent task ID"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Task creation timestamp"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Task update timestamp"
    },
    "due_date": {
      "type": "string",
      "format": "date-time",
      "description": "Task due date"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Task tags"
    },
    "metadata": {
      "type": "object",
      "description": "Additional task metadata"
    }
  },
  "required": ["task_id", "title", "status", "created_at"]
}
```

### 5.2 Stream Resources

#### 5.2.1 `stream://{stream_name}/latest`

Provides access to the latest messages in a stream.

**Response Schema:**
```json
{
  "type": "object",
  "properties": {
    "messages": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "description": "Message ID"
          },
          "type": {
            "type": "string",
            "description": "Message type"
          },
          "from": {
            "type": "string",
            "description": "Message sender"
          },
          "content": {
            "type": "string",
            "description": "Message content"
          },
          "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "Message timestamp"
          },
          "priority": {
            "type": "string",
            "description": "Message priority"
          },
          "metadata": {
            "type": "object",
            "description": "Additional message metadata"
          }
        },
        "required": ["id", "content"]
      }
    }
  },
  "required": ["messages"]
}
```

### 5.3 State Resources

#### 5.3.1 `state://{key}`

Provides access to a state value.

**Response Schema:**
```json
{
  "type": "object",
  "properties": {
    "value": {
      "type": "object",
      "description": "State value"
    },
    "ttl": {
      "type": "number",
      "description": "Remaining time to live in seconds"
    }
  }
}
```

## 6. Boomerang Integration

### 6.1 Integration Points

The Redis MCP server will integrate with Boomerang at the following points:

1. **Task Creation**: Boomerang will use the `create_task` tool to create tasks in Redis
2. **Task Assignment**: Boomerang will use the `update_task` tool to assign tasks to Novas
3. **Task Completion**: Boomerang will use the `complete_task` tool to mark tasks as completed
4. **Task Querying**: Boomerang will use the `list_tasks` tool to query tasks
5. **Communication**: Boomerang will use the stream communication tools to send and receive messages
6. **State Management**: Boomerang will use the state management tools to store and retrieve state

### 6.2 Implementation Strategy

The integration will be implemented in phases:

1. **Phase 1**: Basic task management integration
2. **Phase 2**: Stream communication integration
3. **Phase 3**: State management integration
4. **Phase 4**: Advanced features and optimizations

### 6.3 Code Example

Here's an example of how Boomerang would use the Redis MCP server:

```typescript
// In Boomerang task service
import { MCPClient } from '@nova/mcp-client';

// Initialize MCP client
const mcpClient = new MCPClient({
  serverUrl: 'http://localhost:3000'
});

// Create a task
async function createTask(title: string, description: string, assignee: string): Promise<string> {
  const result = await mcpClient.useTool('redis-mcp', 'create_task', {
    title,
    description,
    assignee,
    priority: 'medium'
  });
  
  return result.task_id;
}

// Complete a task
async function completeTask(taskId: string, result: string): Promise<void> {
  await mcpClient.useTool('redis-mcp', 'complete_task', {
    task_id: taskId,
    result
  });
}

// Send a message
async function sendMessage(stream: string, content: string): Promise<void> {
  await mcpClient.useTool('redis-mcp', 'publish_message', {
    stream,
    content,
    from: 'boomerang',
    type: 'message'
  });
}

// Get task state
async function getTaskState(taskId: string): Promise<any> {
  const resource = await mcpClient.accessResource('redis-mcp', `task://${taskId}`);
  return resource;
}
```

## 7. Implementation Plan

### 7.1 Development Phases

1. **Phase 1: Core Infrastructure (Week 1)**
   - Set up project structure
   - Implement MCP protocol handler
   - Implement Redis client module
   - Implement basic authentication

2. **Phase 2: Task Management Tools (Week 2)**
   - Implement `create_task` tool
   - Implement `get_task` tool
   - Implement `update_task` tool
   - Implement `complete_task` tool
   - Implement `list_tasks` tool

3. **Phase 3: Stream Communication Tools (Week 3)**
   - Implement `publish_message` tool
   - Implement `read_messages` tool
   - Implement `create_consumer_group` tool
   - Implement `read_group` tool

4. **Phase 4: State Management Tools (Week 4)**
   - Implement `set_state` tool
   - Implement `get_state` tool
   - Implement `delete_state` tool

5. **Phase 5: Resources and Integration (Week 5)**
   - Implement task resources
   - Implement stream resources
   - Implement state resources
   - Integrate with Boomerang

6. **Phase 6: Testing and Deployment (Week 6)**
   - Write comprehensive tests
   - Create deployment scripts
   - Document API and usage
   - Deploy to production

### 7.2 Resource Requirements

- **Development**: 2 developers for 6 weeks
- **Testing**: 1 QA engineer for 2 weeks
- **Infrastructure**: Redis cluster, Node.js runtime
- **Integration**: Coordination with Boomerang team

### 7.3 Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Redis performance bottlenecks | High | Medium | Implement caching, connection pooling, and optimized queries |
| MCP protocol changes | Medium | Low | Design for extensibility and backward compatibility |
| Integration issues with Boomerang | High | Medium | Early and continuous integration testing |
| Security vulnerabilities | High | Low | Implement robust authentication and authorization |

## 8. Conclusion

The Redis MCP server will provide a powerful, standardized interface for Boomerang to interact with Redis, enabling advanced task management, real-time communication, and state persistence capabilities. By abstracting the complexity of Redis operations while exposing the full power of Redis, the server will significantly enhance Boomerang's capabilities and streamline development.

I recommend proceeding with the implementation of this server as specified, with a focus on early integration with Boomerang to ensure alignment and compatibility.

---

**Keystone**  
Head of CommsOps  
Nova #002  
"The Keeper of Signal and Silence"
