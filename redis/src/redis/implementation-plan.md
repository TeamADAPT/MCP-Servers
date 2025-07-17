# Redis MCP Server Implementation Plan for Boomerang Integration

Based on Keystone's specification in `communications/redis_mcp_server_spec.md`, this document outlines the implementation plan to fully support the Boomerang integration features.

## Current Status

The Redis MCP server currently implements basic Redis operations:
- `set` - Set a key-value pair
- `get` - Get a value by key
- `delete` - Delete keys
- `list` - List keys matching a pattern

## Required Enhancements

To fully implement Keystone's specification, the following enhancements are needed:

### 1. Task Management Tools

- [ ] `create_task` - Create a new task with title, description, priority, assignee, etc.
- [ ] `get_task` - Retrieve a task by ID
- [ ] `update_task` - Update an existing task
- [ ] `complete_task` - Mark a task as completed
- [ ] `list_tasks` - List tasks with filtering and pagination

### 2. Stream Communication Tools

- [ ] `publish_message` - Publish a message to a Redis stream
- [ ] `read_messages` - Read messages from a Redis stream
- [ ] `create_consumer_group` - Create a consumer group for a Redis stream
- [ ] `read_group` - Read messages from a stream as part of a consumer group

### 3. State Management Tools

- [ ] `set_state` - Set a state value with optional TTL
- [ ] `get_state` - Get a state value
- [ ] `delete_state` - Delete a state value

### 4. Resources

- [ ] `task://{task_id}` - Direct access to task data
- [ ] `stream://{stream_name}/latest` - Access to latest messages in a stream
- [ ] `state://{key}` - Access to a state value

## Implementation Approach

1. **Phase 1: Core Infrastructure**
   - Update Redis client module to support all required operations
   - Expand the existing MCP server implementation
   - Implement common utilities and helper functions

2. **Phase 2: Task Management Tools**
   - Implement Redis data structures for tasks
   - Implement CRUD operations for tasks
   - Implement task querying and filtering

3. **Phase 3: Stream Communication Tools**
   - Implement Redis Streams functionality
   - Implement consumer groups
   - Implement message publishing and reading

4. **Phase 4: State Management Tools**
   - Implement state storage
   - Implement TTL handling

5. **Phase 5: Resources**
   - Implement resource handlers
   - Connect resources to underlying Redis operations

6. **Phase 6: Testing and Documentation**
   - Comprehensive testing of all functionality
   - Update documentation

## Implementation Details

### Task Storage

Tasks will be stored in Redis using a combination of:
- Hash structures for task properties
- Sets for indexing and querying
- Sorted sets for ordering and pagination

### Stream Implementation

Redis Streams will be used directly, with proper error handling and reconnection logic.

### State Management

States will be stored as Redis keys with JSON values, with proper TTL management.

## Next Steps

1. Begin implementation of the Task Management tools
2. Create a test suite for the new functionality
3. Implement Stream Communication tools
4. Implement State Management tools
5. Implement Resources

The implementation will follow the modular architecture established in the current codebase, ensuring maintainability and extensibility.
