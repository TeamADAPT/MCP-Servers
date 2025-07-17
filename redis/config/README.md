# Redis MCP Server Configuration

This directory contains configuration files for the Redis MCP server.

## Configuration Options

### MCP Server Configuration

The Redis MCP server is configured in the Claude extension settings file. Below are the key configuration options:

#### Connection String Format

The Redis connection string can be specified in several formats:

1. **Standard Connection String**:
   ```
   redis://[username][:password]@host[:port][/db-number]
   ```

2. **Connection with Query Parameters**:
   ```
   redis://host[:port][?password=password][&db=db-number]
   ```

3. **Connection with TLS**:
   ```
   rediss://[username][:password]@host[:port][/db-number]
   ```

#### Environment Variables

Alternatively, Redis connection details can be specified using environment variables:

- `REDIS_URL`: The Redis connection URL
- `REDIS_PASSWORD`: The Redis password
- `REDIS_USERNAME`: The Redis username (if required)
- `REDIS_PORT`: The Redis port (default: 6379)
- `REDIS_HOST`: The Redis host (default: localhost)
- `REDIS_DB`: The Redis database number (default: 0)

### Cluster Configuration

For Redis Cluster mode, ensure your connection string points to one of the cluster nodes (typically on ports 7000-7005). The server will automatically detect cluster mode based on the port and configure itself accordingly.

### Authentication

Redis authentication must be provided either in the connection string or through environment variables. For secure deployment, use environment variables rather than embedding credentials in the connection string.

### Example Configurations

#### Standard Redis Server

```json
{
  "mcpServers": {
    "github.com/modelcontextprotocol/servers/tree/main/src/redis": {
      "command": "node",
      "args": [
        "/path/to/redis-mcp-server/src/redis/build/index.js",
        "redis://localhost:6379"
      ],
      "env": {
        "REDIS_PASSWORD": "your-password"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

#### Redis Cluster

```json
{
  "mcpServers": {
    "github.com/modelcontextprotocol/servers/tree/main/src/redis": {
      "command": "node",
      "args": [
        "/path/to/redis-mcp-server/src/redis/build/index.js",
        "redis://:password@127.0.0.1:7000"
      ],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Advanced Configuration

For advanced configuration needs, such as integrating with Boomerang or implementing the full task management system described in the specification, you'll need to modify the server code directly.

See the `src/redis` directory for the implementation details and the `communications/redis_mcp_server_spec.md` file for the full specification.
