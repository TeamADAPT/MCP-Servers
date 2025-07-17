# Slack MCP Server

A Model Context Protocol (MCP) server implementation for Slack integration, enabling AI systems to communicate with Slack workspaces using multiple bot identities. This server is a key component of Project BOOM-BACKER's Nexus Protocol implementation.

## Overview

The Slack MCP Server provides a set of tools that allow AI systems to interact with Slack workspaces, including:

- Listing channels
- Posting messages
- Replying to threads
- Adding reactions
- Retrieving message history
- Fetching user information
- Using multiple bot identities

## Architecture

The server is built using the Model Context Protocol SDK and follows a modular architecture:

```
slack-mcp-server/
├── src/
│   ├── config/       # Configuration management
│   ├── tools/        # API tools implementation
│   ├── utils/        # Utility modules
│   └── server.js     # Main server implementation
└── index.js          # Entry point
```

### Core Components

1. **MCP Server**: Implements the MCP protocol for communication with AI systems
2. **Tool Handlers**: Implements specific Slack API operations
3. **Redis Integration**: Provides cross-system communication capabilities
4. **Multi-Bot Support**: Enables using different bot identities for communication

## Tools

The server provides the following tools:

1. `slack_list_channels` - Lists public channels in the workspace
2. `slack_post_message` - Posts a new message to a Slack channel
3. `slack_reply_to_thread` - Replies to a specific message thread
4. `slack_add_reaction` - Adds an emoji reaction to a message
5. `slack_get_channel_history` - Gets recent messages from a channel
6. `slack_get_thread_replies` - Gets all replies in a message thread
7. `slack_get_users` - Gets a list of workspace users
8. `slack_get_user_profile` - Gets detailed profile information for a user
9. `slack_list_bots` - Lists available bot identities for multi-bot posting

## Multi-Bot Functionality

The server supports using multiple bot identities for communication, allowing different components of a system to speak with distinct identities in Slack channels. This provides clear visual separation and context for users.

### How It Works

When posting a message, you can specify a `bot_id` parameter to select which bot identity to use:

```json
{
  "channel_id": "C1234567890",
  "text": "Hello from a specific bot!",
  "bot_id": "cortex"
}
```

The server will use the appropriate token from the environment variables based on the specified bot ID.

## Setup

### Prerequisites

- Node.js 16+
- Redis server (for cross-system communication)
- Slack workspace with bot users set up

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   ```
3. Set up environment variables (see Configuration section)
4. Start the server:
   ```
   npm start
   ```

## Configuration

Create a `.env` file with the following variables:

```
# Slack configuration
SLACK_BOT_TOKEN=xoxb-your-default-bot-token
SLACK_TEAM_ID=your-team-id

# Redis configuration
REDIS_URL=redis://your-redis-url

# Server configuration
SERVER_NAME=slack-mcp-server
SERVER_VERSION=1.0.0
LOG_LEVEL=info

# Additional Slack Bot Tokens
SLACK_BOT_TOKEN_NEXUS=xoxb-your-nexus-bot-token
SLACK_BOT_TOKEN_CORTEX=xoxb-your-cortex-bot-token
SLACK_BOT_TOKEN_ECHO=xoxb-your-echo-bot-token
SLACK_BOT_TOKEN_SYNERGY=xoxb-your-synergy-bot-token
# Add more bot tokens as needed
```

### MCP Integration

To use this server with MCP-enabled systems, add the following to your MCP configuration:

```json
{
  "mcpServers": {
    "github.com/modelcontextprotocol/servers/tree/main/src/slack": {
      "autoApprove": [
        "slack_list_channels",
        "slack_post_message",
        "slack_reply_to_thread",
        "slack_add_reaction",
        "slack_get_channel_history",
        "slack_get_thread_replies",
        "slack_get_users",
        "slack_get_user_profile",
        "slack_list_bots"
      ],
      "disabled": false,
      "timeout": 60,
      "command": "node",
      "args": [
        "/path/to/slack-mcp-server/index.js"
      ],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-default-bot-token",
        "SLACK_TEAM_ID": "your-team-id"
      },
      "transportType": "stdio"
    }
  }
}
```

## Usage Examples

### Listing Channels

```json
{
  "tool": "slack_list_channels",
  "arguments": {
    "limit": 10
  }
}
```

### Posting a Message

```json
{
  "tool": "slack_post_message",
  "arguments": {
    "channel_id": "C1234567890",
    "text": "Hello, world!"
  }
}
```

### Posting as a Specific Bot

```json
{
  "tool": "slack_post_message",
  "arguments": {
    "channel_id": "C1234567890",
    "text": "Hello from Cortex!",
    "bot_id": "cortex"
  }
}
```

### Adding a Reaction

```json
{
  "tool": "slack_add_reaction",
  "arguments": {
    "channel_id": "C1234567890",
    "timestamp": "1234567890.123456",
    "reaction": "thumbsup"
  }
}
```

### Getting User Information

```json
{
  "tool": "slack_get_user_profile",
  "arguments": {
    "user_id": "U1234567890"
  }
}
```

## Troubleshooting

### Common Issues

1. **Invalid Authentication**
   - Check if the bot token is correct and has the necessary scopes
   - Ensure the bot is invited to the channel you're trying to interact with

2. **Missing Permissions**
   - Verify that the bot has the necessary OAuth scopes for the operations you're trying to perform

3. **Redis Connection Issues**
   - Check Redis connection string and ensure the Redis server is running

## Future Enhancements

- Dynamic bot registration through API
- Additional Slack API capabilities
- Enhanced error handling and retries
- Bot activity monitoring and analytics
- Integration with other messaging platforms

## License

This project is licensed under the MIT License.
