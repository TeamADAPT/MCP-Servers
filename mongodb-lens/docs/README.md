# MongoDB Lens MCP Server Documentation

## Overview

This directory contains comprehensive documentation for the MongoDB Lens MCP server, which provides a natural language interface to MongoDB databases through the Model Context Protocol (MCP).

## Documentation Structure

- [Quick Start Guide](quick-start.md) - Get up and running quickly
- [Admin Guide](admin-guide.md) - Installation, configuration, and management
- [User Guide](user-guide.md) - Using MongoDB Lens with natural language
- [Architecture Guide](architecture.md) - Technical architecture and design
- [Troubleshooting Auto-Approve Issues](troubleshooting-auto-approve.md) - Solving common tool visibility and auto-approve problems
- [Complete Documentation](../mongodb-lens-documentation.md) - All documentation in a single file

## Key Features

- Natural language interface to MongoDB
- 42 MongoDB tools for database operations
- 12 resource providers for database information
- 14 prompt templates for common operations
- Replica set support
- Auto-approval configuration
- Comprehensive error handling and troubleshooting

## Connection Configuration

The key insight for connecting to the MongoDB instance was identifying it as part of a replica set named "nova-rs" which required specific connection parameters:

```
mongodb://admin:password@hostname:port/database?authSource=admin&replicaSet=nova-rs&retryWrites=true&w=majority&directConnection=true
```

Critical parameters:
- `replicaSet=nova-rs` - The replica set name
- `directConnection=true` - Force direct connection
- `authSource=admin` - Authentication database
- `retryWrites=true` - Enable retry for write operations
- `w=majority` - Write concern level

## Auto-Approve Configuration

All 42 MongoDB tools can be auto-approved for seamless operation by editing the MCP settings file directly:

```json
"autoApprove": [
  "connect-mongodb", "connect-original", "add-connection-alias", "list-connections",
  "list-databases", "current-database", "create-database", "use-database", 
  "drop-database", "create-user", "drop-user", "list-collections",
  "create-collection", "drop-collection", "rename-collection", "validate-collection",
  "distinct-values", "find-documents", "count-documents", "insert-document",
  "update-document", "delete-document", "aggregate-data", "create-index",
  "drop-index", "get-stats", "analyze-schema", "generate-schema-validator",
  "compare-schemas", "explain-query", "analyze-query-patterns", "bulk-operations",
  "create-timeseries", "collation-query", "text-search", "geo-query",
  "transaction", "watch-changes", "gridfs-operation", "clear-cache",
  "shard-status", "export-data"
]
```

## Server Management

```
+------------------+     +------------------+     +------------------+
| Start Server     |---->| Monitor Logs     |---->| View Status      |
+------------------+     +------------------+     +------------------+
        |                        |                         |
        v                        v                         v
+------------------+     +------------------+     +------------------+
| node mongodb-    |     | logs/metrics-mcp-|     | MongoDB Lens     |
| lens.js          |     | yyyy-mm-dd.log   |     | v9.1.0 running   |
+------------------+     +------------------+     +------------------+
```

For detailed information, refer to the specific documentation files.
