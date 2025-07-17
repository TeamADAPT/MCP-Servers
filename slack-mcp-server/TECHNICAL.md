# Slack MCP Server: Technical Documentation

This document provides detailed technical information about the Slack MCP Server implementation for developers who need to maintain, extend, or integrate with this system.

## Architecture Overview

The Slack MCP Server is built on the Model Context Protocol (MCP) SDK and follows a modular architecture designed for extensibility and maintainability.

### Key Components

```
slack-mcp-server/
├── src/
│   ├── config/           # Configuration management
│   │   └── env.js        # Environment variable handling
│   ├── tools/            # API tools implementation
│   │   ├── slack_*.js    # Individual tool implementations
│   │   └── ...
│   ├── utils/            # Utility modules
│   │   ├── logger.js     # Logging functionality
│   │   ├── redis.js      # Redis communication
│   │   ├── multi-bot.js  # Multi-bot token management
│   │   └── slack.js      # Slack API utilities
│   └── server.js         # Main server implementation
└── index.js              # Entry point
```

## Core Implementation Details

### MCP Server (src/server.js)

The main server class (`SlackMcpServer`) initializes the MCP server, registers tools, and handles tool execution requests. It also manages Redis connections for cross-system communication.

Key responsibilities:
- Tool registration and listing
- Request/response handling
- Error management
- Redis integration
- Server lifecycle management

### Multi-Bot Support (src/utils/multi-bot.js)

This utility provides the ability to use different bot identities when communicating with Slack. It manages bot tokens and creates appropriate WebClient instances.

Implementation details:
- Token management through environment variables
- Dynamic WebClient creation for each bot identity
- Fallback to default bot when a requested bot is unavailable
- Error handling for invalid tokens

### Tool Implementations (src/tools/)

Each tool is implemented as a separate module with a consistent structure:
- Metadata (name, description, input schema)
- Execute function that performs the actual operation
- Error handling and logging

#### slack_post_message.js

This tool has been enhanced to support the multi-bot functionality. It:
1. Creates a request configuration with channel, text, and optional parameters
2. Determines which bot identity to use (default or specified)
3. Gets the appropriate token for that bot
4. Creates a new WebClient instance with that token
5. Executes the message post
6. Returns structured response information

```javascript
// Get the appropriate token based on the bot_id
const botId = args.bot_id || 'default';
let token = process.env.SLACK_BOT_TOKEN; // Default token

if (botId !== 'default') {
  const botTokenEnvVar = `SLACK_BOT_TOKEN_${botId.toUpperCase()}`;
  const botToken = process.env[botTokenEnvVar];
  
  if (botToken) {
    token = botToken;
    logger.info(`Using token from ${botTokenEnvVar} for bot ${botId}`);
  } else {
    logger.warn(`No token found for bot ${botId}, using default bot token`);
  }
}

// Create a client with the selected token
const client = new WebClient(token);
```

### Redis Integration (src/utils/redis.js)

The Redis utility provides:
- Connection to Redis server in cluster mode
- Leadership stream for system-wide coordination
- Direct message streams for point-to-point communication
- Message publishing and subscription
- Error handling and reconnection logic

## Token Management

Bot tokens are managed through environment variables. The primary bot token is specified as `SLACK_BOT_TOKEN`, and additional bot tokens follow the naming pattern `SLACK_BOT_TOKEN_<BOT_ID>`, where `<BOT_ID>` is the uppercase name of the bot.

For example:
- `SLACK_BOT_TOKEN_NEXUS` for the "nexus" bot
- `SLACK_BOT_TOKEN_CORTEX` for the "cortex" bot

This approach:
1. Keeps tokens secure (not hardcoded)
2. Makes it easy to add new bot identities
3. Provides clear organization of tokens

## Slack API Integration

The server uses the official Slack Web API client (`@slack/web-api`) for communication with the Slack API. Key aspects:

1. Each WebClient instance requires a valid bot token
2. Separate instances can be created for different bot identities
3. API calls are properly structured and error-handled
4. Responses are parsed and formatted for the MCP protocol

## Error Handling

The server implements multi-layered error handling:
1. Tool-level error handling (catches API errors, validation issues)
2. Server-level error handling (catches MCP protocol errors, tool execution errors)
3. Redis error handling (connection issues, publication failures)
4. Global process error handling (uncaught exceptions, process signals)

Errors are logged with appropriate context and returned to the requester when possible.

## Logging

The logging system uses a structured logging approach with different log levels:
- ERROR: Application errors
- WARN: Non-critical issues
- INFO: Operational information
- DEBUG: Detailed debugging information

Logs include:
- Timestamp
- Log level
- Message context
- Structured data for machine processing

## Adding New Tools

To add a new tool:

1. Create a new file in `src/tools/` with the pattern `slack_<tool_name>.js`
2. Implement the tool with the standard structure:
   ```javascript
   const name = 'slack_new_tool';
   const description = 'Description of the new tool';
   const inputSchema = { /* JSON Schema */ };
   async function execute(args) { /* Implementation */ }
   module.exports = { name, description, inputSchema, execute };
   ```
3. Add the tool to the tools array in `src/server.js`

## Adding New Bot Identities

To add a new bot identity:

1. Create a new bot user in your Slack workspace
2. Obtain the bot token (starts with `xoxb-`)
3. Add the token to your `.env` file as `SLACK_BOT_TOKEN_<BOT_ID>`
4. Restart the server

The new bot will automatically be available for use with the `bot_id` parameter.

## Performance Considerations

- WebClient instances are created for each request for multi-bot functionality
- Redis connections are maintained to reduce connection overhead
- Error responses are properly structured to avoid hanging or crashing
- Token validation is performed before API calls

## Security Considerations

- Tokens are stored in environment variables, not in code
- Logging systems exclude sensitive information (tokens, private messages)
- Error messages are sanitized to avoid leaking internal details
- Redis connections can be secured with authentication

## Testing

To test the server:

1. Ensure environment variables are properly set up
2. Start the server with `npm start`
3. Send MCP requests to the server using the MCP client SDK or a compatible client
4. Validate responses to ensure they match expected formats

## Future Development Roadmap

1. **Dynamic Bot Registration**
   - API for registering new bots at runtime
   - Secure storage of dynamically added bot tokens

2. **Extended Slack API Support**
   - File uploads and sharing
   - Channel management (create, archive, invite)
   - Admin functionality

3. **Enhanced Monitoring**
   - Activity dashboards
   - Token usage tracking
   - Performance metrics

4. **Integration Expansions**
   - Slack Events API support
   - Interactive components (buttons, menus)
   - Slash command handling

## Troubleshooting

### Invalid Authentication
- Check that the token is correctly formatted and starts with `xoxb-`
- Ensure the bot is added to the workspace and has proper scopes
- Verify that the bot has been invited to channels it needs to access

### Rate Limiting
- The Slack API has rate limits for different operations
- Consider implementing retry logic with exponential backoff
- Monitor rate limit headers in API responses

### Redis Issues
- Verify Redis connection string format
- Check Redis server availability
- Ensure proper authentication if Redis requires it
- Consider using Redis Sentinel or Redis Cluster for production
