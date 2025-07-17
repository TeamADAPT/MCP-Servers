# MongoDB Lens MCP Server - Architecture Guide

## System Overview

MongoDB Lens is an MCP (Model Context Protocol) server that provides natural language access to MongoDB databases. It acts as a middleware between LLM-powered clients (like Claude) and MongoDB database instances.

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

## Component Architecture

### 1. Core Components

MongoDB Lens comprises several core components:

```
+-------------------------------------+
|        MongoDB Lens Server          |
+-------------------------------------+
|                                     |
|  +-------------------------------+  |
|  |     MCP Server Interface      |  |
|  +-------------------------------+  |
|                                     |
|  +-------------------------------+  |
|  |     MongoDB Client            |  |
|  +-------------------------------+  |
|                                     |
|  +-------------------------------+  |
|  |     Tool Implementations      |  |
|  +-------------------------------+  |
|                                     |
|  +-------------------------------+  |
|  |     Resource Providers        |  |
|  +-------------------------------+  |
|                                     |
|  +-------------------------------+  |
|  |     Configuration Manager     |  |
|  +-------------------------------+  |
|                                     |
+-------------------------------------+
```

- **MCP Server Interface**: Handles communication with MCP clients
- **MongoDB Client**: Manages connections to MongoDB instances
- **Tool Implementations**: Implements the 42 MongoDB operation tools
- **Resource Providers**: Provides access to database resources
- **Configuration Manager**: Handles server configuration

### 2. Data Flow Architecture

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

1. User sends a natural language request to the MCP client
2. MCP client processes the request and sends it to MongoDB Lens
3. MongoDB Lens parses the request and executes the appropriate MongoDB command
4. MongoDB returns the data to MongoDB Lens
5. MongoDB Lens formats the data and returns it to the MCP client
6. MCP client presents the data to the user

### 3. Tool Categories

The 42 tools provided by MongoDB Lens are organized into functional categories:

```
+----------------+       +----------------+       +----------------+
| Connection     |       | Database       |       | Collection     |
| Management     |       | Operations     |       | Management     |
+----------------+       +----------------+       +----------------+
| - connect      |       | - list-dbs     |       | - list-cols    |
| - connect-orig |       | - use-db       |       | - create-col   |
| - add-alias    |       | - create-db    |       | - drop-col     |
| - list-conns   |       | - drop-db      |       | - rename-col   |
+----------------+       +----------------+       +----------------+

+----------------+       +----------------+       +----------------+
| Document       |       | Analytics &    |       | Performance    |
| Operations     |       | Schema         |       | Optimization   |
+----------------+       +----------------+       +----------------+
| - find-docs    |       | - agg-data     |       | - create-index |
| - count-docs   |       | - analyze      |       | - drop-index   |
| - insert-doc   |       | - gen-validator|       | - get-stats    |
| - update-doc   |       | - compare      |       | - explain      |
| - delete-doc   |       |                |       | - analyze-qp   |
+----------------+       +----------------+       +----------------+
```

## Technical Architecture

### 1. MongoDB Connection Management

```
+-------------------+     +-------------------+     +-------------------+
| Connection Config |---->| Connection Pool   |---->| MongoDB Instance  |
+-------------------+     +-------------------+     +-------------------+
       |                          ^                          |
       v                          |                          v
+-------------------+     +-------------------+     +-------------------+
| Auth Mechanism    |     | Connection        |     | Replica Set       |
| (SCRAM-SHA-256)   |     | Monitoring        |     | Discovery         |
+-------------------+     +-------------------+     +-------------------+
```

- **Connection Configuration**: Manages connection strings and options
- **Authentication Mechanism**: Handles SCRAM-SHA-256 authentication
- **Connection Pool**: Maintains a pool of MongoDB connections
- **Connection Monitoring**: Monitors connections and handles reconnection
- **Replica Set Discovery**: Discovers and connects to replica set members

### 2. Command Processing Pipeline

```
+-----------------+     +-----------------+     +-----------------+
| Command Parsing |---->| Validation      |---->| Execution       |
+-----------------+     +-----------------+     +-----------------+
                                |                       |
                                v                       v
                        +-----------------+     +-----------------+
                        | Parameter       |     | Result          |
                        | Transformation  |     | Formatting      |
                        +-----------------+     +-----------------+
```

- **Command Parsing**: Parses MCP tool requests into MongoDB commands
- **Validation**: Validates command parameters
- **Parameter Transformation**: Transforms parameters into MongoDB query language
- **Execution**: Executes commands against MongoDB
- **Result Formatting**: Formats results for MCP client

### 3. Memory Management

```
+----------------+     +----------------+     +----------------+
| Resource       |---->| Cache          |---->| Garbage        |
| Monitoring     |     | Management     |     | Collection     |
+----------------+     +----------------+     +----------------+
        |                      |
        v                      v
+----------------+     +----------------+
| Memory         |     | Threshold      |
| Thresholds     |     | Actions        |
+----------------+     +----------------+
```

- **Resource Monitoring**: Monitors memory usage
- **Memory Thresholds**: Configurable warning and critical thresholds
- **Cache Management**: Manages caches for frequently accessed data
- **Threshold Actions**: Actions taken when thresholds are exceeded
- **Garbage Collection**: Explicit garbage collection

## Security Architecture

```
+-------------------+     +-------------------+     +-------------------+
| Authentication    |---->| Authorization     |---->| Data Protection   |
+-------------------+     +-------------------+     +-------------------+
        |                         |                          |
        v                         v                          v
+-------------------+     +-------------------+     +-------------------+
| Credential        |     | Operation         |     | Confirmation      |
| Management        |     | Validation        |     | Tokens            |
+-------------------+     +-------------------+     +-------------------+
```

- **Authentication**: Handles MongoDB authentication
- **Credential Management**: Manages MongoDB credentials
- **Authorization**: Controls access to MongoDB resources
- **Operation Validation**: Validates operations against permissions
- **Data Protection**: Protects sensitive data
- **Confirmation Tokens**: Requires confirmation for destructive operations

## Configuration Architecture

```
+------------------+     +------------------+     +------------------+
| Configuration    |---->| Environment      |---->| MCP Integration  |
| Files            |     | Variables        |     | Settings         |
+------------------+     +------------------+     +------------------+
        |                        |                         |
        v                        v                         v
+------------------+     +------------------+     +------------------+
| Default          |     | Override         |     | Auto-Approve     |
| Settings         |     | Hierarchy        |     | Settings         |
+------------------+     +------------------+     +------------------+
```

- **Configuration Files**: Main configuration file (~/.mongodb-lens.jsonc)
- **Default Settings**: Default configuration values
- **Environment Variables**: Override configuration via environment variables
- **Override Hierarchy**: Environment variables > Config file > Defaults
- **MCP Integration Settings**: Settings for MCP client integration
- **Auto-Approve Settings**: Configuration for auto-approving tool operations
