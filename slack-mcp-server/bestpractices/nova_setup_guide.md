# Nova Leadership System Setup Guide

This guide provides step-by-step instructions for setting up and configuring the Nova Leadership System components.

## Prerequisites

- Node.js v16+ and npm
- Access to a Slack workspace with admin privileges
- Redis server (for state management)
- Git for version control

## 1. Setting Up the Enhanced Slack MCP Server

### 1.1. Create Slack App

1. Visit [Slack API Apps page](https://YOUR-CREDENTIALS@YOUR-DOMAIN/server-slack
```

#### Using Docker (Alternative)

```bash
docker pull mcp/slack:latest
```

### 1.3. Configure MCP Settings

Add the Slack MCP server to your Claude MCP settings file:

For VSCode Claude extension, edit:
`~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

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
        "slack_get_user_profile"
      ],
      "disabled": false,
      "timeout": 60,
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-slack"
      ],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-bot-token",
        "SLACK_TEAM_ID": "T01234567"
      },
      "transportType": "stdio"
    }
  }
}
```

Replace the placeholder values with your actual Bot Token and Team ID.

## 2. Setting Up Redis MCP Server

### 2.1. Install Redis

#### On Ubuntu/Debian

```bash
sudo apt update
sudo apt install redis-server
```

#### On macOS

```bash
brew install redis
brew services start redis
```

### 2.2. Configure Redis MCP Server

Add the Redis MCP server to your Claude MCP settings file:

```json
{
  "mcpServers": {
    "github.com/modelcontextprotocol/servers/tree/main/src/slack": { ... },
    "github.com/modelcontextprotocol/servers/tree/main/src/redis": {
      "autoApprove": [
        "set",
        "get",
        "delete",
        "list"
      ],
      "disabled": false,
      "timeout": 60,
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-redis",
        "redis://localhost:6379"
      ],
      "transportType": "stdio"
    }
  }
}
```

## 3. Setting Up Enhanced MCP Servers (Optional for Phase 1)

### 3.1. Fork the Base Server Template

```bash
# Clone the MCP server template
git clone https://YOUR-CREDENTIALS@YOUR-DOMAIN/web-api @slack/bolt axios
```

### 3.2. Implement Enhanced Slack Tools

1. Create enhanced tools following the development standards
2. Build and test the server locally
3. Add to your MCP settings file once ready

## 4. Setting Up Development Environment

### 4.1. Development Tools

Install recommended development tools:

```bash
# Install TypeScript and development tools
npm install -g typescript ts-node nodemon
```

### 4.2. Project Structure Setup

```bash
mkdir -p /path/to/nova/leadership
cd /path/to/nova/leadership

# Create directory structure
mkdir -p src/slack src/redis src/orchestration docs tests

# Initialize project
npm init -y
npm install typescript @types/node ts-node jest @types/jest --save-dev
```

### 4.3. Configuration Files

Create a `tsconfig.json` file:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "esModuleInterop": true,
    "strict": true,
    "outDir": "dist",
    "declaration": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "**/*.spec.ts"]
}
```

## 5. Basic Orchestration Setup

### 5.1. Create Orchestration Module

```bash
cd /path/to/nova/leadership
mkdir -p src/orchestration/{router,context,agents}
```

### 5.2. Implement Basic Router

Create basic routing implementation in `src/orchestration/router/index.ts`

## 6. Testing Your Setup

### 6.1. Test Slack MCP Server

1. Restart your Claude VSCode extension to load the new MCP settings
2. Use the following prompt to test the Slack integration:
   "List all channels in my Slack workspace"

### 6.2. Test Redis MCP Server

1. Use the following prompt to test the Redis integration:
   "Store a test value in Redis with key 'nova_test'"

## 7. Troubleshooting

### 7.1. Slack Connection Issues

- Verify bot token is correct and not expired
- Ensure the app is installed to your workspace
- Check that all required scopes are enabled
- Verify the bot user is invited to necessary channels

### 7.2. Redis Connection Issues

- Check if Redis server is running: `redis-cli ping`
- Verify connection string is correct
- Check firewall settings if Redis is on a remote server

### 7.3. MCP Server Issues

- Check log files for error messages
- Verify MCP settings file format is correct
- Ensure the environment variables are set correctly
- Verify the path to the MCP server executable is correct

## 8. Next Steps

After successfully setting up the Nova Leadership System foundation:

1. Begin implementing enhanced Slack tools
2. Set up data schemas in Redis
3. Test basic messaging capabilities
4. Continue with Phase 1 implementation tasks

## 9. Environment Variables Reference

### Slack MCP Server

- `SLACK_BOT_TOKEN`: Bot User OAuth Token from Slack
- `SLACK_TEAM_ID`: Your Slack workspace ID
- `SLACK_SIGNING_SECRET`: Optional for handling events/interactions
- `LOG_LEVEL`: Logging level (debug, info, warn, error)

### Redis MCP Server

- `REDIS_URL`: Redis connection string
- `REDIS_USERNAME`: Username for authenticated Redis
- `REDIS_PASSWORD`: Password for authenticated Redis
- `REDIS_PREFIX`: Optional prefix for all keys
- `LOG_LEVEL`: Logging level (debug, info, warn, error)

## 10. Additional Resources

- [MCP Protocol Documentation](https://github.com/modelcontextprotocol/protocol)
- [Slack API Documentation](https://api.slack.com/docs)
- [Redis Documentation](https://redis.io/documentation)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
