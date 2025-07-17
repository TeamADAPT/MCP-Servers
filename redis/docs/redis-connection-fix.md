# Redis MCP Server Connection Fix

## Issue Summary

The Redis MCP server was encountering connection timeouts and errors because the MCP settings were pointing to a test server path instead of the production server path.

**Incorrect Path:**
```
/data-nova/ax/DevOps/mcp/redis-mcp-test/build/index.js
```

**Correct Path:**
```
/data-nova/ax/DevOps/mcp/mcp-servers/database-mcp-servers/redis/src/redis/build/index.js
```

## Implemented Solutions

### 1. Configuration Fix

The MCP settings file has been updated to point to the correct Redis server path.

### 2. Fallback Mechanisms

To ensure uninterrupted operations even if the MCP connection has issues, we've implemented:

#### Direct Adapter

A direct Redis adapter (`src/redis-streams/direct-adapter.js`) that provides the same interface as the MCP tools but connects directly to Redis without going through the MCP server.

#### Command-Line Interface

A CLI tool (`scripts/redis-mcp-cli.js`) for Redis operations that can be used when the MCP interface is having issues.

### 3. Documentation

- `docs/redis-message-sending.md` - Comprehensive guide for Redis operations via MCP
- `docs/troubleshoote-1.md` - Troubleshooting guide for common Redis MCP issues

## Using the New Tools

### Command-Line Interface

The `redis-mcp-cli.js` tool provides a command-line interface for all Redis operations:

```bash
# Basic operations
./scripts/redis-mcp-cli.js set my-key "my value"
./scripts/redis-mcp-cli.js get my-key
./scripts/redis-mcp-cli.js delete my-key
./scripts/redis-mcp-cli.js list "nova:*"

# Stream operations
./scripts/redis-mcp-cli.js list-streams "nova:*"
./scripts/redis-mcp-cli.js stream-publish my-stream -m '{"type":"event","data":{"message":"hello"}}'
./scripts/redis-mcp-cli.js stream-read my-stream
./scripts/redis-mcp-cli.js create-consumer-group my-stream my-group -m
./scripts/redis-mcp-cli.js read-group my-stream my-group consumer1

# Task management
./scripts/redis-mcp-cli.js create-task -t "My Task" -d "Task description" -p high -a "user123"
```

Use `--help` with any command to see all available options:

```bash
./scripts/redis-mcp-cli.js --help
./scripts/redis-mcp-cli.js stream-publish --help
```

### Using the Direct Adapter

For programmatic access, the direct adapter can be used:

```javascript
const RedisDirectAdapter = require('./src/redis-streams/direct-adapter');

async function main() {
  const adapter = new RedisDirectAdapter();
  
  try {
    // Set and get a key
    await adapter.set('my-key', 'my-value');
    const value = await adapter.get('my-key');
    console.log('Value:', value);
    
    // Work with streams
    const streams = await adapter.listStreams('nova:*');
    console.log('Available streams:', streams);
    
    // Publish to a stream
    const msgId = await adapter.streamPublish('nova:test:stream', {
      type: 'event',
      data: { message: 'Hello from direct adapter' },
      timestamp: new Date().toISOString()
    });
    console.log('Published message with ID:', msgId);
    
    // Read from a stream
    const messages = await adapter.streamRead('nova:test:stream');
    console.log('Messages:', messages);
  } finally {
    await adapter.close();
  }
}

main().catch(console.error);
```

### Interactive Testing

The `scripts/test-stream-operations.js` script provides an interactive way to test Redis operations:

```bash
./scripts/test-stream-operations.js
```

This will present a menu of operations to test, including:
- Setting and getting keys
- Publishing to streams
- Reading from streams
- Working with consumer groups
- Managing tasks

## Verifying the Fix

To verify that the Redis MCP server connection is working correctly:

1. Check if basic operations work through MCP:
   ```
   <use_mcp_tool>
   <server_name>github.com/modelcontextprotocol/servers/tree/main/src/redis</server_name>
   <tool_name>set</tool_name>
   <arguments>
     {
       "key": "test:mcp:connection",
       "value": "working"
     }
   </arguments>
   </use_mcp_tool>
   ```

2. If the MCP tool still fails, use the direct CLI:
   ```bash
   ./scripts/redis-mcp-cli.js set test:mcp:connection working
   ```

3. To verify if streams are working, list available streams:
   ```bash
   ./scripts/redis-mcp-cli.js list-streams
   ```

## Next Steps

1. Monitor the Redis MCP server connection for any recurrence of the issue
2. Consider setting up automated health checks for the Redis MCP server
3. If needed, implement a fail-over mechanism that automatically switches to the direct adapter if the MCP server is unavailable
