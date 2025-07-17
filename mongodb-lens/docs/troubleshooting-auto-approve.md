# Troubleshooting MongoDB Lens Auto-Approve Issues

This guide specifically addresses the common issue where MongoDB Lens tools do not appear in the GUI or auto-approve settings are not retained after checking them in the GUI interface.

## Understanding the Issue

When working with MongoDB Lens MCP server, you may encounter these common problems:

1. **Tools not showing up in GUI**: MCP tools from MongoDB Lens don't appear in the client interface
2. **Auto-approve not being retained**: After checking auto-approve boxes in the GUI, the settings are not saved
3. **Connection issues persist**: Despite connecting successfully, tools continue to fail or require manual approval

## Root Causes

```
+-----------------------------------------+
| Auto-Approve Not Working: Root Causes   |
+-----------------------------------------+
| 1. MCP Settings File Mismatch           |
| 2. Connection String Issues             |
| 3. Server Restart Required              |
| 4. Client/Server Communication Issues   |
+-----------------------------------------+
```

### 1. MCP Settings File Mismatch

The most common cause is that changes made through the GUI don't properly update the MCP settings file. This happens because:

- Some GUI tools don't immediately write changes to disk
- The GUI might be using a different settings location than expected
- Format inconsistencies between how the GUI saves and how the server reads settings

### 2. Connection String Issues

Auto-approve relies on successful connections. If your connection string has issues, the tools might fail even when auto-approved:

- Missing replica set parameters
- Incorrect authentication credentials
- Improper formatting of connection options

### 3. Server Restart Required

Changes to the MCP settings file often require a server restart to take effect:

- The MCP server loads settings on startup
- Runtime changes may not be detected
- Environment variables might override file settings

## Step-by-Step Solution

```
+----------------+     +----------------+     +----------------+
| 1. Edit MCP    |---->| 2. Configure   |---->| 3. Restart     |
| Settings File  |     | Connection     |     | Server         |
+----------------+     +----------------+     +----------------+
        |                      |                      |
        v                      v                      v
+----------------+     +----------------+     +----------------+
| Direct File    |     | Include        |     | Kill Process   |
| Modification   |     | All Parameters |     | Start Again    |
+----------------+     +----------------+     +----------------+
```

### 1. Locate and Edit MCP Settings File Directly

The most reliable solution is to edit the MCP settings file directly instead of using the GUI:

```bash
# For Claude Desktop (macOS)
vim ~/Library/Application\ Support/Claude/claude_desktop_config.json

# For VSCode Claude extension
vim ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

### 2. Configure the `autoApprove` Array and Connection String

Add **ALL** MongoDB Lens tools to the `autoApprove` array:

```json
"mongodb-lens": {
  "autoApprove": [
    "connect-mongodb",
    "connect-original",
    "add-connection-alias",
    "list-connections",
    "list-databases",
    "current-database",
    "create-database",
    "use-database",
    "drop-database",
    "create-user",
    "drop-user",
    "list-collections",
    "create-collection",
    "drop-collection",
    "rename-collection",
    "validate-collection",
    "distinct-values",
    "find-documents",
    "count-documents",
    "insert-document",
    "update-document",
    "delete-document",
    "aggregate-data",
    "create-index",
    "drop-index",
    "get-stats",
    "analyze-schema",
    "generate-schema-validator",
    "compare-schemas",
    "explain-query",
    "analyze-query-patterns",
    "bulk-operations",
    "create-timeseries",
    "collation-query",
    "text-search",
    "geo-query",
    "transaction",
    "watch-changes",
    "gridfs-operation",
    "clear-cache",
    "shard-status",
    "export-data"
  ],
  "disabled": false,
  "timeout": 60,
  "command": "node",
  "args": [
    "/path/to/mongodb-lens/mongodb-lens.js"
  ],
  "env": {
    "CONFIG_MONGO_URI": "mongodb://username:password@hostname:port/database?authSource=admin&replicaSet=replicaSetName&retryWrites=true&w=majority&directConnection=true"
  },
  "transportType": "stdio",
  "autoSave": true
}
```

Ensure that the `CONFIG_MONGO_URI` environment variable includes ALL necessary connection parameters, especially for replica sets:

```
mongodb://admin:password@hostname:port/database?authSource=admin&replicaSet=replicaSetName&retryWrites=true&w=majority&directConnection=true
```

### 3. Restart the MongoDB Lens Server

After editing the settings file, you must restart the server:

```bash
# Find and kill the running server
pkill -f "node mongodb-lens.js"

# Start the server again
node /path/to/mongodb-lens/mongodb-lens.js
```

## Verifying the Fix

After applying the solution, verify it worked by:

1. Checking server logs for successful initialization of all tools
2. Running a simple command like `list-databases` that should now auto-approve
3. Checking more complex operations like `find-documents`

```
+--------------------------------+--------------------------------------+
| Command to Test                | Expected Result                      |
+--------------------------------+--------------------------------------+
| list-databases                 | List of databases without prompt     |
+--------------------------------+--------------------------------------+
| use-database (db name)         | Switches database without prompt     |
+--------------------------------+--------------------------------------+
| find-documents                 | Returns documents without prompt     |
+--------------------------------+--------------------------------------+
```

## Debugging Common Errors

If you're still encountering issues, check these common problems:

### 1. Connection String Format

Ensure your connection string has the correct format:

```
mongodb://[username:password@]host[:port][/database][?options]
```

The most important parameters for replica sets:
- `authSource=admin` (or appropriate authentication database)
- `replicaSet=yourReplicaSetName`
- `directConnection=true`
- `retryWrites=true`
- `w=majority`

### 2. File Permissions

Ensure the MCP settings file has appropriate permissions:

```bash
# Check file permissions
ls -la ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Set appropriate permissions if needed
chmod 644 ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

### 3. JSON Syntax

Ensure your JSON settings file has valid syntax:

```bash
# Validate JSON syntax
cat ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json | jq
```

### 4. Server Path

Ensure the path to the MongoDB Lens server is correct in your MCP settings file:

```json
"args": [
  "/absolute/path/to/mongodb-lens/mongodb-lens.js"
]
```

## Advanced: Environment Variable Configuration

If you prefer using environment variables, you can set `CONFIG_MONGO_URI` directly when starting the server:

```bash
CONFIG_MONGO_URI="mongodb://admin:password@hostname:port/database?authSource=admin&replicaSet=replicaSetName&retryWrites=true&w=majority&directConnection=true" node mongodb-lens.js
```

## Summary

```
+------------------------------------------+
| Auto-Approve Fix: Key Steps              |
+------------------------------------------+
| 1. Edit MCP settings file directly       |
| 2. Add ALL tools to autoApprove array    |
| 3. Include complete connection string    |
|    with ALL required parameters          |
| 4. Restart MongoDB Lens server           |
| 5. Verify with test commands             |
+------------------------------------------+
```

By following these steps, you should be able to resolve the issues with MongoDB Lens tools not showing in the GUI and auto-approve settings not being retained.
