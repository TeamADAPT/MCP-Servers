# Redis MCP Server Setup Guide (No Authentication)

This guide walks through setting up a local Redis server with no authentication for development purposes and connecting it to Cline.

## Prerequisites

1. A local Redis server instance
2. Node.js and npm
3. ioredis library

## Step 1: Install Local Redis Server

If you haven't installed Redis locally, you need to do that first:

```bash
# For Ubuntu/Debian systems
sudo apt update
sudo apt install redis-server

# For Red Hat/CentOS systems 
sudo yum install redis

# For macOS (using Homebrew)
brew install redis
```

## Step 2: Start Redis Server

Start the Redis server with default settings:

```bash
# Ubuntu/Debian (as a service)
sudo systemctl start redis-server

# macOS (using Homebrew)
brew services start redis

# Or start directly
redis-server
```

## Step 3: Disable Authentication (Development Only)

We've created a script that disables authentication on your local Redis server for development purposes:

```bash
# Make the script executable
chmod +x disable_redis_auth_local.sh

# Run the script (make sure Redis is running first)
./disable_redis_auth_local.sh
```

⚠️ **SECURITY WARNING**: Disabling authentication should only be done in isolated development environments. Never do this in production!

## Step 4: Test Redis Connection

Use the test script to verify Redis connection and basic operations:

```bash
node scripts/test-redis-connection.js
```

If successful, you should see output confirming:
- Connection to Redis
- Key-value operations (set, get, delete)
- Stream operations (publishing messages, reading streams)

## Step 5: Configure Cline MCP Integration

1. Add the Redis MCP server to your Cline MCP settings:

```json
{
  "mcpServers": {
    "redis-local": {
      "autoApprove": [
        "set", "get", "delete", "list",
        "stream_publish", "stream_read"
      ],
      "disabled": false,
      "timeout": 60,
      "command": "node",
      "args": [
        "/absolute/path/to/redis/mcp-redis-server/src/index.js"
      ],
      "env": {
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6380",
        "REDIS_NAMESPACE_PREFIX": "dev:"
      },
      "transportType": "stdio"
    }
  }
}
```

2. We've created a sample configuration file at `redis-local-config.json` that you can use.

3. Add this configuration to your Cline MCP settings:

```bash
# For Claude
cp redis-local-config.json ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# For other Cline applications, use the appropriate path
```

## Step 6: Restart Cline

Restart Cline to load the new MCP server configuration.

## Testing MCP Integration

After restarting Cline, you can test the Redis MCP server integration using:

```
I'll store a value in Redis:

use_mcp_tool(
  server_name: "redis-local",
  tool_name: "set",
  arguments: {
    "key": "greeting",
    "value": "Hello from Redis MCP!"
  }
)

Now I'll retrieve it:

use_mcp_tool(
  server_name: "redis-local",
  tool_name: "get",
  arguments: {
    "key": "greeting"
  }
)
```

## Restoring Authentication (When Needed)

When you're ready to restore authentication:

```bash
# Set a new password
redis-cli CONFIG SET requirepass "your_new_password"

# Save the configuration
redis-cli -a "your_new_password" CONFIG REWRITE
```

Then update your MCP configuration to include the password:

```json
"env": {
  "REDIS_HOST": "localhost",
  "REDIS_PORT": "6379",
  "REDIS_PASSWORD": "your_new_password",
  "REDIS_NAMESPACE_PREFIX": "dev:"
}
```

## Troubleshooting

### Connection Errors

If you see "connect ECONNREFUSED" errors:
- Ensure Redis is running (`redis-cli ping` should return "PONG")
- Check the port configuration (default is 6379)
- Verify there are no firewall rules blocking the connection

### Authentication Errors

If you see "NOAUTH Authentication required" errors:
- Redis still has authentication enabled
- Run the `disable_redis_auth_local.sh` script again
- Or provide the correct password in your configuration

### Permission Errors

If you see permission errors when running Redis commands:
- Ensure you have sufficient privileges to access Redis
- Check if ACL rules are restricting access

## Next Steps

Once you have the basic Redis MCP server working, you can:
1. Explore more advanced Redis operations through the MCP interface
2. Implement Redis Streams for real-time data processing
3. Use Redis for caching, message queuing, or state management in your applications
