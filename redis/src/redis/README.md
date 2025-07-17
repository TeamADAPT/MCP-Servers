# Redis MCP Server Implementation

This directory contains the implementation of the Redis MCP server.

## Files

- `index.ts` - The main implementation file containing the Redis MCP server logic
- `package.json` - Dependencies and build scripts
- `build/` - Compiled JavaScript files (created after running `npm run build`)

## Implementation Details

The Redis MCP server implements the Model Context Protocol (MCP) interface for Redis. It provides the following functionality:

### Redis Client

The server uses `ioredis` to connect to Redis, with support for both standalone Redis servers and Redis Clusters. The Redis client automatically detects cluster mode based on the port number.

### Tool Implementation

The server implements the following tools:

- `set` - Set a Redis key-value pair with optional expiration
- `get` - Get a value by key from Redis
- `delete` - Delete one or more keys from Redis
- `list` - List Redis keys matching a pattern

### Error Handling

The server implements comprehensive error handling, including:

- Redis connection errors
- Invalid parameter errors
- Redis operation errors

## Building

To build the server:

```bash
npm install
npm run build
```

This will create the compiled JavaScript files in the `build/` directory.

## Future Enhancements

The implementation can be extended to support the full specification described in `communications/redis_mcp_server_spec.md`, including:

- Task management tools
- Stream communication tools
- State management tools
- Resource specifications
- Boomerang integration

See the specification document for details on these enhancements.
