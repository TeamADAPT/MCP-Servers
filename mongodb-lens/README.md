# MongoDB Lens

[![License](https://YOUR-CREDENTIALS@YOUR-DOMAIN//docs.docker.com/get-started/get-docker) installed and running on your system.

First, ensure Docker is installed:

```console
docker --version # Ideally >= v27.x
```

Then, run MongoDB Lens via Docker Hub:

```console
# Using default connection string mongodb://localhost:27017
docker run --rm -i --network=host furey/mongodb-lens

# Using custom connection string
docker run --rm -i --network=host furey/mongodb-lens mongodb://your-connection-string

# Using "--pull" to keep the Docker image up-to-date
docker run --rm -i --network=host --pull=always furey/mongodb-lens
```

### Installation: Node.js from Source

> [!NOTE]<br>
> Node.js from source requires [Node.js](https://YOUR-CREDENTIALS@YOUR-DOMAIN/mongodb-lens:8.3.0
```

## Configuration

- [MongoDB Connection String](#configuration-mongodb-connection-string)
- [Config File](#configuration-config-file)
- [Config File Generation](#configuration-config-file-generation)
- [Multiple MongoDB Connections](#configuration-multiple-mongodb-connections)
- [Environment Variable Overrides](#configuration-environment-variable-overrides)
- [Cross-Platform Environment Variables](#configuration-cross-platform-environment-variables)

### Configuration: MongoDB Connection String

The server accepts a MongoDB connection string as its only argument.

Example NPX usage:

```console
npx -y mongodb-lens@latest mongodb://your-connection-string
```

MongoDB connection strings have the following format:

```txt
mongodb://[username:password@]host[:port][/database][?options]
```

Example connection strings:

- Local connection:<br>
  `mongodb://localhost:27017`
- Connection to `mydatabase` with credentials from `admin` database:<br>
  `mongodb://username:password@hostname:27017/mydatabase?authSource=admin`
- Connection to `mydatabase` with various other options:<br>
  `mongodb://hostname:27017/mydatabase?retryWrites=true&w=majority`

If no connection string is provided, the server will attempt to connect via local connection.

### Configuration: Config File

MongoDB Lens supports extensive customization via JSON configuration file.

> [!NOTE]<br>
> The config file is optional. MongoDB Lens will run with default settings if no config file is provided.

> [!TIP]<br>
> You only need to include the settings you want to customize in the config file. MongoDB Lens will use default settings for any omitted values.

> [!TIP]<br>
> MongoDB Lens supports both `.json` and `.jsonc` (JSON with comments) config file formats.

<details>
  <summary><strong>Example configuration file</strong></summary>

```jsonc
{
  "mongoUri": "mongodb://localhost:27017",         // Default MongoDB connection string or object of alias-URI pairs
  "connectionOptions": {
    "maxPoolSize": 20,                             // Maximum number of connections in the pool
    "retryWrites": false,                          // Whether to retry write operations
    "connectTimeoutMS": 30000,                     // Connection timeout in milliseconds
    "socketTimeoutMS": 360000,                     // Socket timeout in milliseconds
    "heartbeatFrequencyMS": 10000,                 // How often to ping servers for status
    "serverSelectionTimeoutMS": 30000              // Timeout for server selection
  },
  "defaultDbName": "admin",                        // Default database if not specified in URI
  "connection": {
    "maxRetries": 5,                               // Maximum number of initial connection attempts
    "maxRetryDelayMs": 30000,                      // Maximum delay between retries
    "reconnectionRetries": 10,                     // Maximum reconnection attempts if connection lost
    "initialRetryDelayMs": 1000                    // Initial delay between retries
  },
  "disabled": {
    "tools": [],                                   // Array of tools to disable or true to disable all
    "prompts": [],                                 // Array of prompts to disable or true to disable all
    "resources": []                                // Array of resources to disable or true to disable all
  },
  "enabled": {
    "tools": true,                                 // Array of tools to enable or true to enable all
    "prompts": true,                               // Array of prompts to enable or true to enable all
    "resources": true                              // Array of resources to enable or true to enable all
  },
  "cacheTTL": {
    "stats": 15000,                                // Stats cache lifetime in milliseconds
    "fields": 30000,                               // Fields cache lifetime in milliseconds
    "schemas": 60000,                              // Schema cache lifetime in milliseconds
    "indexes": 120000,                             // Index cache lifetime in milliseconds
    "collections": 30000,                          // Collections list cache lifetime in milliseconds
    "serverStatus": 20000                          // Server status cache lifetime in milliseconds
  },
  "enabledCaches": [                               // List of caches to enable
    "stats",                                       // Statistics cache
    "fields",                                      // Collection fields cache
    "schemas",                                     // Collection schemas cache
    "indexes",                                     // Collection indexes cache
    "collections",                                 // Database collections cache
    "serverStatus"                                 // MongoDB server status cache
  ],
  "memory": {
    "enableGC": true,                              // Whether to enable garbage collection
    "warningThresholdMB": 1500,                    // Memory threshold for warnings
    "criticalThresholdMB": 2000                    // Memory threshold for cache clearing
  },
  "logLevel": "info",                              // Log level (info or verbose)
  "disableDestructiveOperationTokens": false,      // Whether to skip confirmation for destructive ops
  "watchdogIntervalMs": 30000,                     // Interval for connection monitoring
  "defaults": {
    "slowMs": 100,                                 // Threshold for slow query detection
    "queryLimit": 10,                              // Default limit for query results
    "allowDiskUse": true,                          // Allow operations to use disk for large datasets
    "schemaSampleSize": 100,                       // Sample size for schema inference
    "aggregationBatchSize": 50                     // Batch size for aggregation operations
  },
  "security": {
    "tokenLength": 4,                              // Length of confirmation tokens
    "tokenExpirationMinutes": 5,                   // Expiration time for tokens
    "strictDatabaseNameValidation": true           // Enforce strict database name validation
  },
  "tools": {
    "transaction": {
      "readConcern": "snapshot",                   // Read concern level for transactions
      "writeConcern": {
        "w": "majority"                            // Write concern for transactions
      }
    },
    "bulkOperations": {
      "ordered": true                              // Whether bulk operations execute in order
    },
    "export": {
      "defaultLimit": -1,                          // Default limit for exports (-1 = no limit)
      "defaultFormat": "json"                      // Default export format (json or csv)
    },
    "watchChanges": {
      "maxDurationSeconds": 60,                    // Maximum duration for change streams
      "defaultDurationSeconds": 10                 // Default duration for change streams
    },
    "queryAnalysis": {
      "defaultDurationSeconds": 10                 // Default duration for query analysis
    }
  }
}
```

</details>

By default, MongoDB Lens looks for the config file at:

- `~/.mongodb-lens.jsonc` first, then falls back to
- `~/.mongodb-lens.json` if the former doesn't exist

To customize the config file path, set the environment variable `CONFIG_PATH` to the desired file path.

Example NPX usage:

```console
CONFIG_PATH='/path/to/config.json' npx -y mongodb-lens@latest
```

Example Docker Hub usage:

```console
docker run --rm -i --network=host --pull=always -v /path/to/config.json:/root/.mongodb-lens.json furey/mongodb-lens
```

### Configuration: Config File Generation

You can generate a configuration file automatically using the `config:create` script:

```console
# NPX Usage (recommended)
npx -y mongodb-lens@latest config:create

# Node.js Usage
npm run config:create

# Force overwrite existing files
npx -y mongodb-lens@latest config:create -- --force
npm run config:create -- --force
```

This script extracts the [example configuration file](#configuration-config-file) above and saves it to: `~/.mongodb-lens.jsonc`

#### Config File Generation: Custom Path

You can specify a custom output location using the `CONFIG_PATH` environment variable.

- If `CONFIG_PATH` has no file extension, it's treated as a directory and `.mongodb-lens.jsonc` is appended
- If `CONFIG_PATH` ends with `.json` (not `.jsonc`) comments are removed from the generated file

Example NPX usage:

```console
# With custom path
CONFIG_PATH=/path/to/config.jsonc npx -y mongodb-lens@latest config:create

# Save to directory (will append .mongodb-lens.jsonc to the path)
CONFIG_PATH=/path/to/directory npx -y mongodb-lens@latest config:create

# Save as JSON instead of JSONC
CONFIG_PATH=/path/to/config.json npx -y mongodb-lens@latest config:create
```

Example Node.js usage:

```console
# With custom path
CONFIG_PATH=/path/to/config.jsonc node mongodb-lens.js config:create

# Save to directory (will append .mongodb-lens.jsonc to the path)
CONFIG_PATH=/path/to/directory node mongodb-lens.js config:create

# Save as JSON instead of JSONC
CONFIG_PATH=/path/to/config.json node mongodb-lens.js config:create
```

### Configuration: Multiple MongoDB Connections

MongoDB Lens supports multiple MongoDB URIs with aliases in your [config file](#configuration-config-file), allowing you to easily switch between different MongoDB instances using simple names.

To configure multiple connections, set the `mongoUri` config setting to an object with alias-URI pairs:

```json
{
  "mongoUri": {
    "main": "mongodb://localhost:27017",
    "backup": "mongodb://localhost:27018",
    "atlas": "mongodb+srv://username:password@cluster.mongodb.net/mydb"
  }
}
```

With this configuration:

- The first URI in the list (e.g. `main`) becomes the default connection at startup
- You can switch connections using natural language: `"Connect to backup"` or `"Connect to atlas"`
- The original syntax still works: `"Connect to mongodb://localhost:27018"`
- The `list-connections` tool shows all available connection aliases

> [!NOTE]<br>
> When using the command-line argument to specify a connection, you can use either a full MongoDB URI or an alias defined in your configuration file.

> [!TIP]<br>
> To add connection aliases at runtime, use the `add-connection-alias` tool.

### Configuration: Environment Variable Overrides

MongoDB Lens supports environment variable overrides for configuration settings.

Environment variables take precedence over [config file](#configuration-config-file) settings.

Config environment variables follow the naming pattern:

```txt
CONFIG_[SETTING PATH, SNAKE CASED, UPPERCASED]
```

Example overrides:

| Config Setting                   | Environment Variable Override             |
| -------------------------------- | ----------------------------------------- |
| `mongoUri`                       | `CONFIG_MONGO_URI`                        |
| `logLevel`                       | `CONFIG_LOG_LEVEL`                        |
| `defaultDbName`                  | `CONFIG_DEFAULT_DB_NAME`                  |
| `defaults.queryLimit`            | `CONFIG_DEFAULTS_QUERY_LIMIT`             |
| `tools.export.defaultFormat`     | `CONFIG_TOOLS_EXPORT_DEFAULT_FORMAT`      |
| `connectionOptions.maxPoolSize`  | `CONFIG_CONNECTION_OPTIONS_MAX_POOL_SIZE` |
| `connection.reconnectionRetries` | `CONFIG_CONNECTION_RECONNECTION_RETRIES`  |

For environment variable values:

- For boolean settings, use string values `'true'` or `'false'`.
- For numeric settings, use string representations.
- For nested objects or arrays, use JSON strings.

Example NPX usage:

```console
CONFIG_DEFAULTS_QUERY_LIMIT='25' npx -y mongodb-lens@latest
```

Example Docker Hub usage:

```console
docker run --rm -i --network=host --pull=always -e CONFIG_DEFAULTS_QUERY_LIMIT='25' furey/mongodb-lens
```

### Configuration: Cross-Platform Environment Variables

For consistent environment variable usage across Windows, macOS, and Linux, consider using `cross-env`:

1. Install cross-env globally:<br>
   ```console
   # Using NPM
   npm install -g cross-env

   # Using Volta (see: https://YOUR-CREDENTIALS@YOUR-DOMAIN//claude.ai/download)
1. Open `claude_desktop_config.json` (create if it doesn't exist):
    - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
    - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
1. Add the MongoDB Lens server configuration as per [configuration options](#claude-desktop-configuration-options)
1. Restart Claude Desktop
1. Start a conversation with Claude about your MongoDB data

#### Claude Desktop Configuration Options

- [Option 1: NPX (Recommended)](#option-1-npx-recommended)
- [Option 2: Docker Hub Image](#option-2-docker-hub-image)
- [Option 3: Local Node.js Installation](#option-3-local-nodejs-installation)
- [Option 4: Local Docker Image](#option-4-local-docker-image)

For each option:

- Replace `mongodb://your-connection-string` with your MongoDB connection string or omit it to use the default `mongodb://localhost:27017`.
- To use a custom config file, set [`CONFIG_PATH`](#configuration-config-file) environment variable.
- To include environment variables:
  - For NPX or Node.js add `"env": {}` with key-value pairs, for example:<br>
    ```json
    "command": "/path/to/npx",
    "args": [
      "-y",
      "mongodb-lens@latest",
      "mongodb://your-connection-string"
    ],
    "env": {
      "CONFIG_LOG_LEVEL": "verbose"
    }
    ```
  - For Docker add `-e` flags, for example:<br>
    ```json
    "command": "docker",
    "args": [
      "run", "--rm", "-i",
      "--network=host",
      "--pull=always",
      "-e", "CONFIG_LOG_LEVEL='verbose'",
      "furey/mongodb-lens",
      "mongodb://your-connection-string"
    ]
    ```

##### Option 1: NPX (Recommended)

```json
{
  "mcpServers": {
    "mongodb-lens": {
      "command": "/path/to/npx",
      "args": [
        "-y",
        "mongodb-lens@latest",
        "mongodb://your-connection-string"
      ]
    }
  }
}
```

##### Option 2: Docker Hub Image

```json
{
  "mcpServers": {
    "mongodb-lens": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--network=host",
        "--pull=always",
        "furey/mongodb-lens",
        "mongodb://your-connection-string"
      ]
    }
  }
}
```

##### Option 3: Local Node.js Installation

```json
{
  "mcpServers": {
    "mongodb-lens": {
      "command": "/path/to/node",
      "args": [
        "/path/to/mongodb-lens.js",
        "mongodb://your-connection-string"
      ]
    }
  }
}
```

##### Option 4: Local Docker Image

```json
{
  "mcpServers": {
    "mongodb-lens": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--network=host",
        "mongodb-lens",
        "mongodb://your-connection-string"
      ]
    }
  }
}
```

### Client Setup: MCP Inspector

[MCP Inspector](https://YOUR-CREDENTIALS@YOUR-DOMAIN/inspector npx -y mongodb-lens@latest

    # Using custom connection string
    npx -y @modelcontextprotocol/inspector npx -y mongodb-lens@latest mongodb://your-connection-string

    # Using custom ports
    SERVER_PORT=1234 CLIENT_PORT=5678 npx -y @modelcontextprotocol/inspector npx -y mongodb-lens@latest
    ```
1. Open MCP Inspector: http://localhost:5173

MCP Inspector should support the full range of MongoDB Lens capabilities, including autocompletion for collection names and query fields.

For more, see: [MCP Inspector](https://YOUR-CREDENTIALS@YOUR-DOMAIN/mydatabase
```

Using read-only credentials is a simple yet effective way to enforce security boundaries, especially when you're poking around schemas or running ad-hoc queries.

### Data Protection: Working with Database Backups

When working with MongoDB Lens, consider connecting to a backup copy of your data hosted on a separate MongoDB instance.

Start by generating the backup with `mongodump`. Next, spin up a fresh MongoDB instance (e.g. on a different port like `27018`) and restore the backup there using `mongorestore`. Once it's running, point MongoDB Lens to the backup instance's connection string (e.g. `mongodb://localhost:27018/mydatabase`).

This approach gives you a sandbox to test complex or destructive operations against without risking accidental corruption of your live data.

### Data Protection: Data Flow Considerations

- [How Your Data Flows Through the System](#data-flow-considerations-how-your-data-flows-through-the-system)
- [Protecting Sensitive Data with Projection](#data-flow-considerations-protecting-sensitive-data-with-projection)
- [Connection Aliases and Passwords](#data-flow-considerations-connection-aliases-and-passwords)
- [Local Setup for Maximum Safety](#data-flow-considerations-local-setup-for-maximum-safety)

#### Data Flow Considerations: How Your Data Flows Through the System

When using an MCP Server with a remote LLM provider (such as Anthropic via Claude Desktop) understanding how your data flows through the system is key to protecting sensitive information from unintended exposure.

When you send a MongoDB related query through your MCP client, here’s what happens:

> [!NOTE]<br>
> While this example uses a local MongoDB instance, the same principles apply to remote MongoDB instances.

```mermaid
sequenceDiagram
    actor User
    box Local Machine #d4f1f9
        participant Client as MCP Client
        participant Lens as MongoDB Lens
        participant MongoDB as MongoDB Instance
    end
    box Remote Server #ffe6cc
        participant LLM as Remote LLM Provider
    end

    User->>Client: 1. Submit request<br>"Show me all users older than 30"
    Client->>LLM: 2. User request + available tools
    Note over LLM: Interprets request<br>Chooses appropriate tool
    LLM->>Client: 3. Tool selection (find-documents)
    Client->>Lens: 4. Tool run with parameters
    Lens->>MongoDB: 5. Database query
    MongoDB-->>Lens: 6. Database results
    Lens-->>Client: 7. Tool results (formatted data)
    Client->>LLM: 8. Tool results
    Note over LLM: Processes results<br>Formats response
    LLM-->>Client: 9. Processed response
    Client-->>User: 10. Final answer
```

1. **You sumbit a request**: e.g. _"Show me all users older than 30"_
1. **Your client sends the request to the remote LLM**: The LLM provider receives your exact words, along with a list of currently available MCP tools and their parameters.
1. **The remote LLM interprets your request**: It determines your intent and instructs the client to use a specific MCP tool, such as `find-documents`, with appropriate parameters.
1. **The client asks MongoDB Lens to run the tool**: This occurs locally on your machine via stdio.
1. **MongoDB Lens queries your MongoDB database**
1. **MongoDB Lens retrieves your MongoDB query results**
1. **MongoDB Lens sends the data back to the client**: The client receives results formatted by MongoDB Lens.
1. **The client forwards the data to the remote LLM**: The LLM provider sees the exact data returned by MongoDB Lens.
1. **The remote LLM processes the data**: It may summarize or format the results further.
1. **The remote LLM sends the final response to the client**: The client displays the answer to you.

The remote LLM provider sees both your original request and the full response from MongoDB Lens. If your database includes sensitive fields (e.g. passwords, personal details, etc) this data could be unintentionally transmitted to the remote provider unless you take precautions.

#### Data Flow Considerations: Protecting Sensitive Data with Projection

To prevent sensitive data from being sent to the remote LLM provider, use the concept of projection when using tools like `find-documents`, `aggregate-data`, or `export-data`. Projection allows you to specify which fields to include or exclude in query results, ensuring sensitive information stays local.

Example projection usage:

- _"Show me all users older than 30, but use projection to hide their passwords."_<br>
  <sup>➥ Uses `find-documents` tool with projection</sup>

#### Data Flow Considerations: Connection Aliases and Passwords

When adding new connection aliases using the `add-connection-alias` tool, avoid added aliases to URIs that contain passwords if you're using a remote LLM provider. Since your request is sent to the LLM, any passwords in the URI could be exposed. Instead, define aliases with passwords in the MongoDB Lens [config file](#configuration-multiple-mongodb-connections), where they remain local and are not transmitted to the LLM.

#### Data Flow Considerations: Local Setup for Maximum Safety

While outside the scope of this document, for the highest level of data privacy, consider using a local MCP client paired with a locally hosted LLM model. This approach keeps all requests and data within your local environment, eliminating the risk of sensitive information being sent to a remote provider.

### Data Protection: Confirmation for Destructive Operations

MongoDB Lens implements a token-based confirmation system for potentially destructive operations, requiring a two-step process to execute tools that may otherwise result in unchecked data loss:

1. First tool invocation: Returns a 4-digit confirmation token that expires after 5 minutes
1. Second tool invocation: Executes the operation if provided with the valid token

For an example of the confirmation process, see: [Working with Confirmation Protection](#tutorial-5-working-with-confirmation-protection)

Tools that require confirmation include:

- `drop-user`: Remove a database user
- `drop-index`: Remove an index (potential performance impact)
- `drop-database`: Permanently delete a database
- `drop-collection`: Delete a collection and all its documents
- `delete-document`: Delete one or multiple documents
- `bulk-operations`: When including delete operations
- `rename-collection`: When the target collection exists and will be dropped

This protection mechanism aims to prevent accidental data loss from typos and unintended commands. It's a safety net ensuring you're aware of the consequences before proceeding with potentially harmful actions.

> [!NOTE]<br>
> If you're working in a controlled environment where data loss is acceptable, you can configure MongoDB Lens to [bypass confirmation](#bypassing-confirmation-for-destructive-operations) and perform destructive operations immediately.

#### Bypassing Confirmation for Destructive Operations

You might want to bypass the token confirmation system.

Set the environment variable `CONFIG_DISABLE_DESTRUCTIVE_OPERATION_TOKENS` to `true` to execute destructive operations immediately without confirmation:

```console
# Using NPX
CONFIG_DISABLE_DESTRUCTIVE_OPERATION_TOKENS=true npx -y mongodb-lens@latest

# Using Docker
docker run --rm -i --network=host --pull=always -e CONFIG_DISABLE_DESTRUCTIVE_OPERATION_TOKENS='true' furey/mongodb-lens
```

> [!WARNING]<br>
> Disabling confirmation tokens removes an important safety mechanism. It's strongly recommended to only use this option in controlled environments where data loss is acceptable, such as development or testing. Disable at your own risk.

### Data Protection: Disabling Destructive Operations

- [Disabling Tools](#disabling-tools)
- [High-Risk Tools](#high-risk-tools)
- [Medium-Risk Tools](#medium-risk-tools)
- [Read-Only Configuration](#read-only-configuration)
- [Selective Component Enabling](#selective-component-enabling)

#### Disabling Tools

MongoDB Lens includes several tools that can modify or delete data. To disable specific tools, add them to the `disabled.tools` array in your [configuration file](#configuration-config-file):

```json
{
  "disabled": {
    "tools": [
      "drop-user",
      "drop-index",
      "drop-database",
      "drop-collection",
      "delete-document",
      "bulk-operations",
      "rename-collection"
    ]
  }
}
```

> [!NOTE]<br>
> Resources and prompts can also be disabled via `disabled.resources` and `disabled.prompts` settings.

#### High-Risk Tools

These tools can cause immediate data loss and should be considered for disabling in sensitive environments:

- `drop-user`: Removes database users and their access permissions
- `drop-index`: Removes indexes (can impact query performance)
- `drop-database`: Permanently deletes entire databases
- `drop-collection`: Permanently deletes collections and all their documents
- `delete-document`: Removes documents matching specified criteria
- `bulk-operations`: Can perform batch deletions when configured to do so
- `rename-collection`: Can overwrite existing collections when using the drop target option

#### Medium-Risk Tools

These tools can modify data but typically don't cause immediate data loss:

- `create-user`: Creates users with permissions that could enable further changes
- `transaction`: Executes multiple operations in a transaction (potential for complex changes)
- `update-document`: Updates documents which could overwrite existing data

#### Read-Only Configuration

For a complete read-only configuration, disable all potentially destructive tools:

```json
{
  "disabled": {
    "tools": [
      "drop-user",
      "drop-index",
      "create-user",
      "transaction",
      "create-index",
      "drop-database",
      "drop-collection",
      "insert-document",
      "update-document",
      "delete-document",
      "bulk-operations",
      "create-database",
      "gridfs-operation",
      "create-collection",
      "rename-collection",
      "create-timeseries"
    ]
  }
}
```

This configuration allows MongoDB Lens to query and analyze data while preventing any modifications, providing multiple layers of protection against accidental data loss.

#### Selective Component Enabling

In addition to [disabling components](#disabling-tools), specify exactly which components should be enabled (implicitly disabling all others) using the `enabled` settings in your [configuration file](#configuration-config-file):

```json
{
  "enabled": {
    "tools": [
      "use-database",
      "find-documents",
      "count-documents",
      "aggregate-data"
    ]
  },
  "disabled": {
    "resources": true,
    "prompts": true
  }
}
```

> [!IMPORTANT]<br>
> If a component appears in both `enabled` and `disabled` lists, the `enabled` setting takes precedence.

## Tutorial

This following tutorial guides you through setting up a MongoDB container with sample data, then using MongoDB Lens to interact with it through natural language queries:

1. [Start Sample Data Container](#tutorial-1-start-sample-data-container)
1. [Import Sample Data](#tutorial-2-import-sample-data)
1. [Connect MongoDB Lens](#tutorial-3-connect-mongodb-lens)
1. [Example Queries](#tutorial-4-example-queries)
1. [Working With Confirmation Protection](#tutorial-5-working-with-confirmation-protection)

### Tutorial: 1. Start Sample Data Container

> [!NOTE]<br>
> This tutorial assumes you have [Docker](https://YOUR-CREDENTIALS@YOUR-DOMAIN/sup>
- _"What db am I currently using?"_<br>
  <sup>➥ Uses `current-database` tool</sup>
- _"Switch to the sample_mflix database"_<br>
  <sup>➥ Uses `use-database` tool</sup>
- _"Create a new db called test_db"_<br>
  <sup>➥ Uses `create-database` tool</sup>
- _"Create another db called analytics_db and switch to it"_<br>
  <sup>➥ Uses `create-database` tool with switch=true</sup>
- _"Drop test_db"_<br>
  <sup>➥ Uses `drop-database` tool (with confirmation)</sup>

#### Example Queries: Collection Management

- _"What collections are in the current database?"_<br>
  <sup>➥ Uses `list-collections` tool</sup>
- _"Create user_logs collection"_<br>
  <sup>➥ Uses `create-collection` tool</sup>
- _"Rename user_logs to system_logs"_<br>
  <sup>➥ Uses `rename-collection` tool</sup>
- _"Drop system_logs"_<br>
  <sup>➥ Uses `drop-collection` tool (with confirmation)</sup>
- _"Check the data consistency in the movies collection"_<br>
  <sup>➥ Uses `validate-collection` tool</sup>

#### Example Queries: User Management

- _"Create a read-only user for analytics"_<br>
  <sup>➥ Uses `create-user` tool</sup>
- _"Drop the inactive_user account"_<br>
  <sup>➥ Uses `drop-user` tool (with confirmation)</sup>

#### Example Queries: Querying Data

- _"Count all docs in the movies collection"_<br>
  <sup>➥ Uses `count-documents` tool</sup>
- _"Find the top 5 movies with the highest IMDB rating"_<br>
  <sup>➥ Uses `find-documents` tool</sup>
- _"Show me aggregate data for movies grouped by decade"_<br>
  <sup>➥ Uses `aggregate-data` tool</sup>
- _"List all unique countries where movies were produced"_<br>
  <sup>➥ Uses `distinct-values` tool</sup>
- _"Search for movies containing godfather in their title"_<br>
  <sup>➥ Uses `text-search` tool</sup>
- _"Find German users with last name müller using proper collation"_<br>
  <sup>➥ Uses `collation-query` tool</sup>

#### Example Queries: Schema Analysis

- _"What's the schema structure of the movies collection?"_<br>
  <sup>➥ Uses `analyze-schema` tool</sup>
- _"Compare users and comments schemas"_<br>
  <sup>➥ Uses `compare-schemas` tool</sup>
- _"Generate a schema validator for the movies collection"_<br>
  <sup>➥ Uses `generate-schema-validator` tool</sup>
- _"Analyze common query patterns for the movies collection"_<br>
  <sup>➥ Uses `analyze-query-patterns` tool</sup>

#### Example Queries: Data Modification

- _"Insert new movie document: \<your field data\>"_<br>
  <sup>➥ Uses `insert-document` tool</sup>
- _"Update all movies from 1994 to add a 'classic' flag"_<br>
  <sup>➥ Uses `update-document` tool</sup>
- _"Delete all movies with zero ratings"_<br>
  <sup>➥ Uses `delete-document` tool (with confirmation)</sup>
- _"Run these bulk operations on the movies collection: \<your JSON data\>"_<br>
  <sup>➥ Uses `bulk-operations` tool</sup>

> [!TIP]<br>
> For specialized MongoDB operations (like array operations, bitwise operations, or other complex updates), use MongoDB's native operators via the `update-document` tool's `update` and `options` parameters.

#### Example Queries: Performance & Index Management

- _"Create an index on the title field in the movies collection"_<br>
  <sup>➥ Uses `create-index` tool</sup>
- _"Drop the ratings_idx index"_<br>
  <sup>➥ Uses `drop-index` tool (with confirmation)</sup>
- _"Explain the execution plan for finding movies from 1995"_<br>
  <sup>➥ Uses `explain-query` tool</sup>
- _"Get statistics for the current db"_<br>
  <sup>➥ Uses `get-stats` tool with target=database</sup>
- _"Show collection stats for the movies collection"_<br>
  <sup>➥ Uses `get-stats` tool with target=collection</sup>

#### Example Queries: Geospatial & Special Operations

- _"Switch to sample_geospatial db, then find all shipwrecks within 10km of coordinates [-80.12, 26.46]"_<br>
  <sup>➥ Uses `geo-query` tool</sup>
- _"Switch to sample_analytics db, then execute a transaction to move funds between accounts: \<account ids\>"_<br>
  <sup>➥ Uses `transaction` tool</sup>
- _"Create a time series collection for sensor readings"_<br>
  <sup>➥ Uses `create-timeseries` tool</sup>
- _"Watch for changes in the users collection for 30 seconds"_<br>
  <sup>➥ Uses `watch-changes` tool</sup>
- _"List all files in the images GridFS bucket"_<br>
  <sup>➥ Uses `gridfs-operation` tool with operation=list</sup>

#### Example Queries: Export, Administrative & Other Features

- _"Switch to sample_mflix db, then export the top 20 movies based on 'tomatoes.critic.rating' as a CSV with title, year and rating fields (output in a single code block)"_<br>
  <sup>➥ Uses `export-data` tool</sup>
- _"Switch to sample_analytics db, then check its sharding status"_<br>
  <sup>➥ Uses `shard-status` tool</sup>
- _"Clear the collections cache"_<br>
  <sup>➥ Uses `clear-cache` tool with target=collections</sup>
- _"Clear all caches"_<br>
  <sup>➥ Uses `clear-cache` tool</sup>
- _"Switch to sample_weatherdata db then generate an interactive report on its current state"_<br>
  <sup>➥ Uses numerous tools</sup>

#### Example Queries: Connection Management

- _"Connect to mongodb://localhost:27018"_<br>
  <sup>➥ Uses `connect-mongodb` tool</sup>
- _"Connect to mongodb+srv://username:password@cluster.mongodb.net/mydb"_<br>
  <sup>➥ Uses `connect-mongodb` tool</sup>
- _"Connect back to the original mongodb instance"_<br>
  <sup>➥ Uses `connect-original` tool</sup>
- _"Connect to replica set without validating the connection: \<replica set details\>"_<br>
  <sup>➥ Uses `connect-mongodb` tool with validateConnection=false</sup>
- _"Add connection alias 'prod' for mongodb://username:password@prod-server:27017/mydb"_<br>
<sup>➥ Uses `add-connection-alias` tool</sup>

### Tutorial: 5. Working With Confirmation Protection

MongoDB Lens includes a safety mechanism for potentially destructive operations. Here's how it works in practice:

1. Request to drop a collection:<br>
    ```
    "Drop the collection named test_collection"
    ```
1. MongoDB Lens responds with a warning and confirmation token:<br>
    ```
    ⚠️ DESTRUCTIVE OPERATION WARNING ⚠️

    You've requested to drop the collection 'test_collection'.

    This operation is irreversible and will permanently delete all data in this collection.

    To confirm, you must type the 4-digit confirmation code EXACTLY as shown below:

    Confirmation code: 9876

    This code will expire in 5 minutes for security purposes.
    ```
1. Confirm the operation by submitting the confirmation token:<br>
    ```
    "9876"
    ```
1. MongoDB Lens executes the operation:<br>
    ```
    Collection 'test_collection' has been permanently deleted.
    ```

This two-step process prevents accidental data loss by requiring explicit confirmation.

> [!NOTE]<br>
> If you're working in a controlled environment where data loss is acceptable, you can configure MongoDB Lens to [bypass confirmation](#bypassing-confirmation-for-destructive-operations) and perform destructive operations immediately.

## Test Suite

MongoDB Lens includes a [test suite](./mongodb-lens.test.js) to verify functionality across tools, resources, and prompts.

- [Running Tests](#test-suite-running-tests)
- [Command Line Options](#test-suite-command-line-options)
- [Examples](#test-suite-examples)

### Test Suite: Running Tests

The test suite requires a `CONFIG_MONGO_URI` environment variable which can be set to:

- a MongoDB connection string (e.g. `mongodb://localhost:27017`)
- `mongodb-memory-server` (for in-memory testing)

```console
# Run Tests with MongoDB Connection String
CONFIG_MONGO_URI=mongodb://localhost:27017 node mongodb-lens.test.js

# Run Tests with In-Memory MongoDB (requires mongodb-memory-server)
CONFIG_MONGO_URI=mongodb-memory-server node mongodb-lens.test.js
```

For convenience, the following scripts are available for running tests:

```console
npm test                        # Fails if no CONFIG_MONGO_URI provided
npm run test:localhost          # Uses mongodb://localhost:27017
npm run test:localhost:verbose  # Runs with DEBUG=true for verbose output
npm run test:in-memory          # Uses mongodb-memory-server
npm run test:in-memory:verbose  # Runs with DEBUG=true for verbose output
```

> [!NOTE]<br>
> The test suite creates temporary databases and collections that are cleaned up after test completion.

### Test Suite: Command Line Options

| Option             | Description                                          |
| ------------------ | ---------------------------------------------------- |
| `--list`           | List all available tests without running them        |
| `--test=<n>`       | Run specific test(s) by name (comma-separated)       |
| `--group=<n>`      | Run all tests in specific group(s) (comma-separated) |
| `--pattern=<glob>` | Run tests matching pattern(s) (comma-separated)      |

### Test Suite: Examples

```console
# List All Available Tests
npm test -- --list

# Run Only Connection-Related Tests (:27017)
npm run test:localhost -- --group=Connection\ Tools

# Test Specific Database Operations (In-Memory)
npm run test:in-memory -- --test=create-database\ Tool,drop-database\ Tool

# Test All Document-Related Tools (:27017)
npm run test:localhost -- --pattern=document

# Run Resource Tests Only (In-Memory)
npm run test:in-memory -- --group=Resources

# Run Specific Tests Only (In-Memory)
npm run test:in-memory -- --test=aggregate-data\ Tool,find-documents\ Tool
```

## Disclaimer

MongoDB Lens:

- is licensed under the [MIT License](./LICENSE).
- is not affiliated with or endorsed by MongoDB, Inc.
- is written with the assistance of AI and may contain errors.
- is intended for educational and experimental purposes only.
- is provided as-is with no warranty—please use at your own risk.

## Support

If you've found MongoDB Lens helpful consider supporting my work through:

[Buy Me a Coffee](https://www.buymeacoffee.com/furey) | [GitHub Sponsorship](https://github.com/sponsors/furey)

Contributions help me continue developing and improving this tool, allowing me to dedicate more time to add new features and ensuring it remains a valuable resource for the community.
