# Redis MCP Server Troubleshooting Guide

## GUI Error: MCP Tool Timeout

### Error Message
```
Error executing MCP tool: {
  "code": -32001,
  "data": {"timeout": 60000},
  "name": "McpError",
  "message": "MCP error -32001: Request timed out",
  "stack": "McpError: MCP error -32001: Request timed out"
}
```

### Autonomous Mode Setup

1. **MCP Settings Configuration**
   ```json
   {
     "autoApprove": [
       "set",
       "get",
       "delete",
       "list",
       "stream_publish",
       "stream_read",
       "list_streams",
       "create_consumer_group",
       "read_group",
       "read_multiple_streams",
       "set_state",
       "get_state",
       "delete_state",
       "create_task",
       "get_task",
       "update_task",
       "complete_task",
       "list_tasks"
     ],
     "disabled": false,
     "timeout": 60
   }
   ```

2. **Command Execution**
   - Set `requires_approval: false` for all execute_command operations
   - Enable auto-approval for all MCP tool operations
   - Allow autonomous operation without user interaction

### Root Causes & Solutions

1. **Server Path Mismatch**
   - Problem: MCP settings pointing to test server instead of production
   - Solution: Update MCP settings to use correct path:
     ```
     /data-nova/ax/DevOps/mcp/mcp-servers/database-mcp-servers/redis/src/redis/build/index.js
     ```
   - Not:
     ```
     /data-nova/ax/DevOps/mcp/redis-mcp-test/build/index.js
     ```

2. **Server Process**
   - Check if server is running:
     ```bash
     ps aux | grep redis-mcp
     ```
   - If not running, restart the service:
     ```bash
     systemctl restart redis-mcp
     ```

3. **Connection Settings**
   - Verify Redis cluster nodes:
     ```
     127.0.0.1:7000
     127.0.0.1:7001
     127.0.0.1:7002
     ```
   - Check password: `d5d7817937232ca5`

4. **Timeout Configuration**
   - Default timeout: 60 seconds
   - If needed, adjust in MCP settings:
     ```json
     {
       "timeout": 60,
       "env": {
         "REDIS_RETRY_MAX": "10",
         "REDIS_RETRY_DELAY": "100"
       }
     }
     ```

### Automated Quick Fixes

1. **Restart MCP Server**
   ```bash
   systemctl restart redis-mcp
   ```

2. **Clear MCP Cache**
   ```bash
   rm -rf ~/.mcp-cache/*
   ```

3. **Verify Redis Connection**
   ```bash
   redis-cli -h 127.0.0.1 -p 7000 -a d5d7817937232ca5 ping
   ```

4. **Check Service Status**
   ```bash
   systemctl status redis-mcp
   journalctl -u redis-mcp -n 50
   ```

### Automated Health Checks

1. **Process Check**
   ```bash
   ps aux | grep redis-mcp
   ```

2. **Port Check**
   ```bash
   netstat -an | grep 700[0-2]
   ```

3. **Log Check**
   ```bash
   tail -f /var/log/redis/redis-mcp.log
   ```

### Prevention

1. Always use production paths in MCP settings
2. Keep connection settings in sync with REDIS_CLINE_CONNECTION_DETAILS.md
3. Monitor server logs for early warning signs
4. Use proper error handling in client code

### Support

If issues persist:
1. Check service logs: `journalctl -u redis-mcp -f`
2. Review MCP server logs
3. Contact DevOps team with error details
