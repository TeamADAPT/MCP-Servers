# Redis MCP Server

This MCP server provides tools and resources for interacting with Redis, implementing a simple key-value interface using the Model Context Protocol.

## Features

- **Key-Value Operations**: Basic Redis key-value storage and retrieval
- **Namespacing**: All keys can be prefixed with a namespace
- **Resource Templates**: Access to task data, stream messages, and state values

## Installation

```bash
# Install dependencies
npm install
```

## Usage

### Starting the Server

```bash
node src/index.js [redis_connection_string]
```

Example:
```bash
node src/index.js redis://username:password@localhost:6379
```

### Environment Variables

- `REDIS_HOST`: Redis server hostname (default: 'localhost')
- `REDIS_PORT`: Redis server port (default: 6379)
- `REDIS_USERNAME`: Redis username for authentication
- `REDIS_PASSWORD`: Redis password for authentication
- `REDIS_NAMESPACE_PREFIX`: Prefix for Redis keys

## Available Tools

### Key-Value Operations

- `set`: Set a key-value pair in Redis
- `get`: Get a value by key from Redis
- `delete`: Delete a key from Redis
- `list`: List keys matching a pattern in Redis

## Integration with Cline

To integrate with Cline, add the following to your Cline MCP settings configuration:

```json
{
  "mcpServers": {
    "redis": {
      "command": "node",
      "args": [
        "/absolute/path/to/mcp-redis-server/src/index.js",
        "redis://username:password@host:port"
      ],
      "env": {
        "REDIS_NAMESPACE_PREFIX": "cline:"
      },
      "disabled": false,
      "autoApprove": [
        "set", "get", "delete", "list"
      ]
    }
  }
}
```

A sample configuration file is provided in `cline-config-example.json`.

## Example Usage

Once the server is running and integrated with Cline, you can use it like this:

```
I'll store your preferences in Redis.

use_mcp_tool(
  server_name: "redis",
  tool_name: "set",
  arguments: {
    "key": "user_preferences",
    "value": "{\"theme\":\"dark\",\"fontSize\":14}"
  }
)

Let me check what's stored:

use_mcp_tool(
  server_name: "redis",
  tool_name: "get",
  arguments: {
    "key": "user_preferences"
  }
)
```
