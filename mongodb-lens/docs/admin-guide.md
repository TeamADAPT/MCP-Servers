# MongoDB Lens MCP Server - Admin Guide

## Quick Start Installation

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Create Configuration**
   ```bash
   node config-create.js
   ```

3. **Edit Configuration Files**
   - `~/.mongodb-lens.jsonc`
   - MCP settings file (typically `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`)

4. **Start the Server**
   ```bash
   node mongodb-lens.js
   ```

## Configuration Quick Reference

### MongoDB Lens Configuration (~/.mongodb-lens.jsonc)

```json
{
  "mongoUri": "mongodb://username:password@hostname:port/database?authSource=admin&replicaSet=replicaSetName&retryWrites=true&w=majority&directConnection=true",
  "connectionOptions": {
    "directConnection": true,
    "ssl": false,
    "authMechanism": "SCRAM-SHA-256",
    "authSource": "admin"
  }
}
```

### MCP Settings Configuration

```json
"mongodb-lens": {
  "autoApprove": [
    "connect-mongodb",
    "list-databases",
    "use-database",
    "find-documents",
    ...
  ],
  "disabled": false,
  "timeout": 60,
  "command": "node",
  "args": [
    "/path/to/mongodb-lens/mongodb-lens.js"
  ],
  "env": {
    "CONFIG_MONGO_URI": "mongodb://admin:password@hostname:port/database?authSource=admin&replicaSet=replicaSetName&retryWrites=true&w=majority&directConnection=true"
  },
  "transportType": "stdio",
  "autoSave": true
}
```

## Common Issues

1. **Connection String Parameters**
   - For replica sets, include `replicaSet` parameter
   - Always set `directConnection=true` for direct connections
   - Use `authSource=admin` for authentication database

2. **Auto-Approve Not Working**
   - Manually edit MCP settings file
   - Restart MongoDB Lens server
   - Full list of tools to auto-approve:
     ```
     connect-mongodb, connect-original, add-connection-alias, list-connections,
     list-databases, current-database, create-database, use-database, 
     drop-database, create-user, drop-user, list-collections,
     create-collection, drop-collection, rename-collection, validate-collection,
     distinct-values, find-documents, count-documents, insert-document,
     update-document, delete-document, aggregate-data, create-index,
     drop-index, get-stats, analyze-schema, generate-schema-validator,
     compare-schemas, explain-query, analyze-query-patterns, bulk-operations,
     create-timeseries, collation-query, text-search, geo-query,
     transaction, watch-changes, gridfs-operation, clear-cache,
     shard-status, export-data
     ```

## Troubleshooting Connection Issues

```
+-------------------------+---------------------+----------------------------------+
| Error                   | Possible Cause      | Solution                         |
+-------------------------+---------------------+----------------------------------+
| Authentication failed   | Incorrect username  | Verify credentials in connection |
|                         | or password         | string                           |
+-------------------------+---------------------+----------------------------------+
| Connection refused      | MongoDB not running | Check if MongoDB is running      |
|                         | Incorrect hostname  | Verify hostname and port         |
+-------------------------+---------------------+----------------------------------+
| Option not supported    | Invalid connection  | Check connection string syntax   |
|                         | parameter           |                                  |
+-------------------------+---------------------+----------------------------------+
| Replica set not found   | Missing replicaSet  | Add replicaSet parameter to     |
|                         | parameter           | connection string                |
+-------------------------+---------------------+----------------------------------+
```

## Maintaining the Server

1. **Memory Management**
   - Configure memory thresholds in config file:
     ```json
     "memory": {
       "enableGC": true,
       "warningThresholdMB": 1500,
       "criticalThresholdMB": 2000
     }
     ```

2. **Logging**
   - Logs are stored in the `logs/` directory
   - Set verbose logging with:
     ```bash
     CONFIG_LOG_LEVEL=verbose node mongodb-lens.js
     ```

3. **Upgrading**
   - Pull the latest version from GitHub
   - Update dependencies with `npm install`
   - Check for new configuration options
   - Restart the server
