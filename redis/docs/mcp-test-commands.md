# Redis MCP Server Test Commands

This file contains commands that can be used to test the Redis MCP server once it's connected.

## Prerequisites

1. The Redis MCP server must be configured in the Claude extension settings
2. The Claude extension or VSCode must be restarted to pick up the new configuration

## Test Commands

Once the Redis MCP server is connected, you can use the following commands to test its functionality:

### 1. List all keys in Redis

```
Use the Redis MCP server to list all keys in the database.
```

### 2. Set a key-value pair

```
Use the Redis MCP server to set the key "greeting" with the value "Hello from Redis MCP Server".
```

### 3. Get a key's value

```
Use the Redis MCP server to get the value of the key "greeting".
```

### 4. Delete a key

```
Use the Redis MCP server to delete the key "greeting".
```

## Troubleshooting

If the Redis MCP server is not connecting, try the following:

1. Verify that the Redis server is running and accessible by running the `test-redis-connection.js` script:
   ```
   node redis-mcp-server/test-redis-connection.js
   ```

2. Check the MCP server configuration in the Claude extension settings file:
   ```
   cat /home/x/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
   ```

3. Restart the Claude extension or VSCode

4. If the issue persists, try one of these alternative configurations:

   a. Using a connection string with password as a query parameter:
   ```json
   {
     "mcpServers": {
       "github.com/modelcontextprotocol/servers/tree/main/src/redis": {
         "command": "npx",
         "args": [
           "-y",
           "@modelcontextprotocol/server-redis",
           "redis://127.0.0.1:7000?password=d5d7817937232ca5"
         ],
         "disabled": false,
         "autoApprove": []
       }
     }
   }
   ```

   b. Using a connection string with password in the URL:
   ```json
   {
     "mcpServers": {
       "github.com/modelcontextprotocol/servers/tree/main/src/redis": {
         "command": "npx",
         "args": [
           "-y",
           "@modelcontextprotocol/server-redis",
           "redis://:d5d7817937232ca5@127.0.0.1:7000"
         ],
         "disabled": false,
         "autoApprove": []
       }
     }
   }
   ```

   c. Using environment variables (current configuration):
   ```json
   {
     "mcpServers": {
       "github.com/modelcontextprotocol/servers/tree/main/src/redis": {
         "command": "npx",
         "args": [
           "-y",
           "@modelcontextprotocol/server-redis"
         ],
         "env": {
           "REDIS_URL": "redis://127.0.0.1:7000",
           "REDIS_PASSWORD": "d5d7817937232ca5"
         },
         "disabled": false,
         "autoApprove": []
       }
     }
   }
   ```

5. If none of the above configurations work, you may need to install the Redis MCP server locally and modify it to support cluster mode explicitly.
