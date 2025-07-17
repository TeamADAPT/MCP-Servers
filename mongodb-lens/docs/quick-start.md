# MongoDB Lens MCP Server - Quick Start Guide

This guide will help you quickly get started with MongoDB Lens MCP server.

## Prerequisites

- Node.js (v18.0.0 or higher)
- MongoDB instance (v4.0 or higher)
- MCP client (Claude Desktop, Cursor, etc.)

## Installation

```
+-------------------+
| Install           |
| Dependencies      |
+-------------------+
         |
         v
+-------------------+
| Create            |
| Configuration     |
+-------------------+
         |
         v
+-------------------+
| Update MCP        |
| Settings          |
+-------------------+
         |
         v
+-------------------+
| Start the         |
| Server            |
+-------------------+
```

### 1. Install Dependencies

```bash
# Clone the repository (if not already done)
git clone https://YOUR-CREDENTIALS@YOUR-DOMAIN/database?authSource=admin&replicaSet=replicaSetName&retryWrites=true&w=majority&directConnection=true"
}
```

### 3. Update MCP Settings

Edit your MCP settings file (typically at `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`) to add:

```json
"mongodb-lens": {
  "autoApprove": ["list-databases", "use-database", "find-documents", "..."],
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

### 4. Start the Server

```bash
node mongodb-lens.js
```

For debugging or detailed logging:

```bash
CONFIG_LOG_LEVEL=verbose node mongodb-lens.js
```

## Basic Usage

### 1. List Databases
Ask: "List all databases"

### 2. Use Database
Ask: "Switch to database X"

### 3. List Collections
Ask: "List all collections in this database"

### 4. Query Documents
Ask: "Find the first 10 documents in collection Y"

## Connection Troubleshooting

If you encounter connection issues, verify:

1. **Authentication details** are correct
2. **Replica set name** is included if using a replica set
3. **directConnection=true** is set in the connection string
4. **MongoDB is running** and accessible from your machine

## Common Issues

```
+--------------------------------+--------------------------------------+
| Error                          | Solution                             |
+--------------------------------+--------------------------------------+
| Authentication failed          | Check username/password              |
+--------------------------------+--------------------------------------+
| Connection refused             | Verify MongoDB is running            |
+--------------------------------+--------------------------------------+
| Option not supported           | Check connection string parameters    |
+--------------------------------+--------------------------------------+
| Auto-approve not working       | Manually edit MCP settings file      |
+--------------------------------+--------------------------------------+
```

## Advanced Configuration

For detailed configuration options, refer to the [Admin Guide](admin-guide.md).

## Next Steps

1. Explore [User Guide](user-guide.md) for comprehensive usage examples
2. Learn about the system architecture in [Architecture Guide](architecture.md)
3. Review the full MongoDB Lens documentation for detailed features and capabilities
