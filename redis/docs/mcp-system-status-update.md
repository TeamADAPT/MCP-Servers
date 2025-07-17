# MCP System Status Update

## Executive Summary

Two critical issues with the MCP (Model Context Protocol) system have been identified and resolved:

1. **Redis MCP Server Connection Errors** - The Redis MCP server was experiencing connection timeouts and errors due to incorrect server path configuration.
2. **System Process Overload** - The system was accumulating multiple instances of each MCP server, eventually reaching process limits and preventing new applications from launching.

Both issues have been addressed with:
- Configuration fixes for the Redis MCP server
- Fallback mechanisms for Redis operations when MCP is unavailable
- A process management system to control MCP server proliferation
- Implementation guidance for systemd-based management of MCP servers

## Issue 1: Redis MCP Server Connection Errors

### Problem
The Redis MCP server was encountering connection timeouts and errors due to incorrect path configuration in the MCP settings file.

### Root Cause
The MCP settings were pointing to a test server path instead of the production server:

**Incorrect path:**
```
/data-nova/ax/DevOps/mcp/redis-mcp-test/build/index.js
```

**Correct path:**
```
/data-nova/ax/DevOps/mcp/mcp-servers/database-mcp-servers/redis/src/redis/build/index.js
```

### Solution Implemented
1. Updated MCP settings file with the correct Redis server path
2. Created a direct Redis adapter for fallback operations
3. Developed a CLI tool for Redis operations when MCP is unavailable
4. Created comprehensive documentation for Redis operations

## Issue 2: System Process Overload

### Problem
System analysis revealed 349+ node processes running simultaneously, primarily from MCP servers. This caused the system to hit process limits, preventing new applications from launching.

### Root Cause
MCP servers were accumulating multiple instances over time, likely due to:
- Servers not shutting down correctly
- VS Code extension automatically spawning new instances
- Lack of process management mechanisms

### Solution Implemented
Developed a comprehensive MCP Process Manager (`scripts/mcp-process-manager.js`) that can:
1. List all running MCP processes
2. Kill duplicate processes, keeping only the newest instance of each server
3. Check for problematic startup configurations
4. Generate systemd service files for controlled startup of MCP servers

## Using the New Tools

### 1. MCP Process Manager

This tool provides both CLI and interactive interfaces:

```bash
# Interactive mode
./scripts/mcp-process-manager.js

# CLI commands
./scripts/mcp-process-manager.js list              # List all MCP processes
./scripts/mcp-process-manager.js kill-duplicates   # Kill duplicate processes
./scripts/mcp-process-manager.js kill-all          # Kill all MCP processes
./scripts/mcp-process-manager.js check-config      # Check startup configuration
./scripts/mcp-process-manager.js generate-services # Generate systemd service files
```

### 2. Redis Direct CLI

For Redis operations when MCP is unavailable:

```bash
# Basic operations
./scripts/redis-mcp-cli.js set my-key "my value"
./scripts/redis-mcp-cli.js get my-key
./scripts/redis-mcp-cli.js list "nova:*"

# Stream operations
./scripts/redis-mcp-cli.js stream-publish my-stream -m '{"type":"event","data":{"message":"hello"}}'
./scripts/redis-mcp-cli.js stream-read my-stream
./scripts/redis-mcp-cli.js list-streams
```

## Recommended System Management Approach

To maintain system stability, we recommend:

### 1. Immediate Steps

1. Use the MCP Process Manager to kill all duplicate processes:
   ```bash
   ./scripts/mcp-process-manager.js kill-duplicates
   ```

2. Verify the Redis MCP server is working:
   ```bash
   ./scripts/redis-mcp-cli.js set test:connection "working"
   ./scripts/redis-mcp-cli.js get test:connection
   ```

### 2. Long-term Management

1. **Use systemd for MCP service management**:
   ```bash
   # Generate systemd service files
   ./scripts/mcp-process-manager.js generate-services
   
   # Enable and start services
   systemctl --user daemon-reload
   systemctl --user enable mcp-*.service
   systemctl --user start mcp-*.service
   ```

2. **Disable automatic MCP server starting in VS Code**:
   - Modify `.vscode/settings.json` to disable automatic MCP server startup
   - Rely on systemd services for server management

3. **Regular monitoring**:
   - Add a cron job to check for and kill duplicate MCP processes:
   ```bash
   # Add to crontab (every hour)
   0 * * * * /path/to/scripts/mcp-process-manager.js kill-duplicates >> /tmp/mcp-process-cleanup.log 2>&1
   ```

## Additional Documentation

The following documentation has been created:

- `docs/redis-connection-fix.md` - Details of Redis connection fix
- `docs/redis-message-sending.md` - Guide for Redis operations via MCP
- `docs/troubleshoote-1.md` - Troubleshooting guide for Redis MCP issues
- `scripts/mcp-process-manager.js` - Tool for managing MCP processes
- `scripts/redis-mcp-cli.js` - CLI for Redis operations
- `src/redis-streams/direct-adapter.js` - Direct Redis adapter implementation

## Next Steps

1. **Implement systemd-based management** of MCP servers
2. **Set up monitoring** to detect MCP server issues proactively
3. **Review VS Code extension configuration** to prevent process accumulation
4. **Test recovery procedures** to ensure smooth handling of future issues
5. **Document best practices** for MCP server deployment and management

## Conclusion

The implemented solutions address both the immediate Redis connection issues and the larger system stability problems caused by MCP process proliferation. By following the recommended management approach, we can ensure stable operation of the MCP infrastructure going forward.
