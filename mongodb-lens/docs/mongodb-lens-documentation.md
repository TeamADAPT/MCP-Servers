# MongoDB Lens MCP Server Documentation

## Table of Contents

- [Admin Guide](#admin-guide)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Auto-Approve Tool Configuration](#auto-approve-tool-configuration)
  - [Troubleshooting](#troubleshooting)
- [User Guide](#user-guide)
  - [Overview](#overview)
  - [Available Tools](#available-tools)
  - [Common Usage Scenarios](#common-usage-scenarios)
  - [Advanced Usage](#advanced-usage)
- [Architecture](#architecture)
- [Reference](#reference)

## Admin Guide

### Installation

MongoDB Lens can be installed using several methods. The recommended approach is to clone the repository and run it directly using Node.js.

```bash
# Clone the repository (if not already done)
git clone https://YOUR-CREDENTIALS@YOUR-DOMAIN/database?authSource=admin&replicaSet=replicaSetName&retryWrites=true&w=majority&directConnection=true",
  "connectionOptions": {
    "maxPoolSize": 20,
    "retryWrites": false,
    "connectTimeoutMS": 5000,
    "socketTimeoutMS": 30000,
    "heartbeatFrequencyMS": 10000,
    "serverSelectionTimeoutMS": 5000,
    "directConnection": true,
    "ssl": false,
    "authMechanism": "SCRAM-SHA-256",
    "authSource": "admin"
  }
}
```

Critical connection parameters:
- **replicaSet** - Include if the MongoDB instance is part of a replica set
- **directConnection** - Set to true to force direct connection
- **retryWrites** - Enable retry for write operations
- **w=majority** - Write concern level

#### MCP Settings Configuration

```json
{
  "mcpServers": {
    "mongodb-lens": {
      "autoApprove": ["list-databases", "use-database", ...],
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
  }
}
```

### Auto-Approve Tool Configuration

To enable auto-approval for MongoDB Lens tools, the MCP settings file must include an `autoApprove` array with the names of the tools to auto-approve. 

#### Steps to Configure Auto-Approval

1. Locate your MCP settings file (typically at `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` or similar)
2. Add or update the `autoApprove` array with the MongoDB Lens tool names
3. Restart the MongoDB Lens server

#### Common Issue: Auto-Approval Not Retained

If auto-approval settings aren't being retained after checking them in the GUI:

1. The MCP settings file needs to be updated directly
2. Add all tool names to the `autoApprove` array
3. Make sure the `env` section has the correct connection string

Here's an example of adding all tools for auto-approval:

```json
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
]
```

### Troubleshooting

#### Connection Issues

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

#### Common Issues and Solutions

1. **Authentication Failure**
   - Verify username and password
   - Check authSource parameter (usually 'admin')
   - Confirm user exists in the specified authSource database

2. **Connection Timeout**
   - Check network connectivity
   - Verify hostname and port
   - Check firewall settings

3. **Auto-approve Not Working**
   - Directly modify MCP settings file
   - Restart MongoDB Lens server
   - Restart MCP client

## User Guide

### Overview

MongoDB Lens provides a natural language interface to MongoDB databases through the Model Context Protocol (MCP). It enables you to perform database operations, analyze schemas, optimize performance, and more.

```
+----------------+      +-------------------+      +------------------+
| MCP Client     |----->| MongoDB Lens MCP  |----->| MongoDB Database |
| (Claude, etc.) |<-----| Server            |<-----| Instance         |
+----------------+      +-------------------+      +------------------+
```

### Available Tools

MongoDB Lens provides 42 tools across different categories:

1. **Connection Management**
   - connect-mongodb, connect-original, add-connection-alias, list-connections

2. **Database Operations**
   - list-databases, current-database, create-database, use-database, drop-database

3. **User Management**
   - create-user, drop-user

4. **Collection Management**
   - list-collections, create-collection, drop-collection, rename-collection, validate-collection

5. **Document Operations**
   - find-documents, count-documents, insert-document, update-document, delete-document, distinct-values

6. **Aggregation and Analysis**
   - aggregate-data, analyze-schema, generate-schema-validator, compare-schemas

7. **Performance Optimization**
   - create-index, drop-index, get-stats, explain-query, analyze-query-patterns

8. **Advanced Features**
   - bulk-operations, create-timeseries, collation-query, text-search, geo-query, transaction, watch-changes, gridfs-operation

9. **System Operations**
   - clear-cache, shard-status, export-data

### Common Usage Scenarios

#### Basic Database Exploration

```
+-----------------+
| 1. List         |
| Databases       |
+-----------------+
        |
        v
+-----------------+
| 2. Use Database |
+-----------------+
        |
        v
+-----------------+
| 3. List         |
| Collections     |
+-----------------+
        |
        v
+-----------------+
| 4. Find         |
| Documents       |
+-----------------+
```

Example queries:
- "List all databases"
- "Switch to the customers database"
- "Show me all collections in this database"
- "Find the first 10 documents in the orders collection"

#### Schema Analysis

```
+-----------------+
| 1. Analyze      |
| Schema          |
+-----------------+
        |
        v
+-----------------+
| 2. Generate     |
| Schema Validator|
+-----------------+
        |
        v
+-----------------+
| 3. Compare      |
| Schemas         |
+-----------------+
```

Example queries:
- "Analyze the schema of the customers collection"
- "Generate a schema validator for the orders collection"
- "Compare the schemas of customers and users collections"

#### Performance Optimization

```
+-----------------+
| 1. Explain      |
| Query           |
+-----------------+
        |
        v
+-----------------+
| 2. Analyze Query|
| Patterns        |
+-----------------+
        |
        v
+-----------------+
| 3. Create Index |
+-----------------+
```

Example queries:
- "Explain the query to find orders with status 'pending'"
- "Analyze query patterns for the products collection"
- "Create an index on the email field in the users collection"

### Advanced Usage

#### Geospatial Queries

```javascript
// Example geospatial query
{
  "collection": "restaurants",
  "operator": "near",
  "field": "location",
  "geometry": {
    "type": "Point",
    "coordinates": [-73.93414657, 40.82302903]
  },
  "maxDistance": 1000,
  "limit": 5
}
```

Example query:
- "Find restaurants within 1km of coordinates [-73.93, 40.82]"

#### Text Search

```javascript
// Example text search
{
  "collection": "articles",
  "searchText": "artificial intelligence",
  "language": "english",
  "caseSensitive": "false",
  "limit": 10
}
```

Example query:
- "Search for articles containing 'artificial intelligence'"

## Architecture

### System Components

```
+--------------------------------------------------------------------------------------------+
|                                                                                            |
|  +----------------------+      +-------------------------+      +----------------------+    |
|  |                      |      |                         |      |                      |    |
|  |  MCP Client          |      |  MongoDB Lens           |      |  MongoDB Database    |    |
|  |  (Claude, etc.)      <----->|  MCP Server             <----->|  Instance            |    |
|  |                      |      |                         |      |                      |    |
|  +----------------------+      +-------------------------+      +----------------------+    |
|                                |                         |                                  |
|                                |  +-------------------+  |                                  |
|                                |  | Tools (42)        |  |                                  |
|                                |  +-------------------+  |                                  |
|                                |                         |                                  |
|                                |  +-------------------+  |                                  |
|                                |  | Resources (12)    |  |                                  |
|                                |  +-------------------+  |                                  |
|                                |                         |                                  |
|                                |  +-------------------+  |                                  |
|                                |  | Prompts (14)      |  |                                  |
|                                |  +-------------------+  |                                  |
|                                |                         |                                  |
|                                +-------------------------+                                  |
|                                                                                            |
+--------------------------------------------------------------------------------------------+
```

### Data Flow

```
+---------------+    +---------------+    +---------------+    +---------------+
| User Request  | -> | MCP Client    | -> | MongoDB Lens  | -> | MongoDB       |
| (Natural Lang)|    | (Processes    |    | (Executes     |    | (Returns      |
|               |    |  Request)     |    |  Command)     |    |  Data)        |
+---------------+    +---------------+    +---------------+    +---------------+
                                              ^     |
                                              |     v
                                         +----------------+
                                         | Configuration  |
                                         | Files         |
                                         +----------------+
```

## Reference

### Connection String Parameters

```
+------------------+------------------+------------------------------------------+
| Parameter        | Example          | Description                              |
+------------------+------------------+------------------------------------------+
| authSource       | admin            | Database for authentication              |
+------------------+------------------+------------------------------------------+
| replicaSet       | nova-rs          | Name of replica set                      |
+------------------+------------------+------------------------------------------+
| retryWrites      | true             | Whether to retry write operations        |
+------------------+------------------+------------------------------------------+
| w                | majority         | Write concern level                      |
+------------------+------------------+------------------------------------------+
| directConnection | true             | Force direct connection                  |
+------------------+------------------+------------------------------------------+
```

### Important Directories and Files

```
+--------------------------------+--------------------------------------------------+
| Path                           | Description                                      |
+--------------------------------+--------------------------------------------------+
| ~/.mongodb-lens.jsonc          | Main configuration file                          |
+--------------------------------+--------------------------------------------------+
| MCP settings file              | MCP server integration configuration             |
+--------------------------------+--------------------------------------------------+
| mongodb-lens.js                | Main server executable                           |
+--------------------------------+--------------------------------------------------+
| logs/                          | Directory containing server logs                 |
+--------------------------------+--------------------------------------------------+
```

### Resource Usage

MongoDB Lens memory usage depends on the size of your database and query complexity.

```
+------------------+------------------+------------------------------------------+
| Operation        | Memory Usage     | Notes                                    |
+------------------+------------------+------------------------------------------+
| Simple queries   | Low              | ~50-100MB                                |
+------------------+------------------+------------------------------------------+
| Aggregations     | Medium           | Depends on pipeline complexity           |
+------------------+------------------+------------------------------------------+
| Schema analysis  | Medium-High      | Scales with document complexity          |
+------------------+------------------+------------------------------------------+
| Bulk operations  | High             | Scales with operation count              |
+------------------+------------------+------------------------------------------+
```

For optimal performance, configure the memory settings in ~/.mongodb-lens.jsonc:

```json
"memory": {
  "enableGC": true,
  "warningThresholdMB": 1500,
  "criticalThresholdMB": 2000
}
