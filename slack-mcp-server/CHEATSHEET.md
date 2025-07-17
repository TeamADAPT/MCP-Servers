# Slack MCP Server Cheat Sheet

A quick reference for working with the Slack MCP Server in Project BOOM-BACKER.

## Setup

### Environment Variables

```bash
# Essential variables
SLACK_BOT_TOKEN=xoxb-your-default-bot-token
SLACK_TEAM_ID=your-team-id
REDIS_URL=redis://your-redis-url

# Multi-bot tokens
SLACK_BOT_TOKEN_NEXUS=xoxb-your-nexus-bot-token
SLACK_BOT_TOKEN_CORTEX=xoxb-your-cortex-bot-token
SLACK_BOT_TOKEN_ECHO=xoxb-your-echo-bot-token
```

### Starting the Server

```bash
# Install dependencies
npm install

# Start the server
npm start

# Development mode with auto-restart
npm run dev
```

## MCP Tools Quick Reference

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

### Posting with a Bot Identity
```json
{
  "tool": "slack_post_message",
  "arguments": {
    "channel_id": "C1234567890",
    "text": "Hello from a specific bot!",
    "bot_id": "nexus"
  }
}
```

### Replying to a Thread
```json
{
  "tool": "slack_reply_to_thread",
  "arguments": {
    "channel_id": "C1234567890",
    "thread_ts": "1234567890.123456",
    "text": "This is a reply"
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

### Getting Channel History
```json
{
  "tool": "slack_get_channel_history",
  "arguments": {
    "channel_id": "C1234567890",
    "limit": 10
  }
}
```

### Getting Thread Replies
```json
{
  "tool": "slack_get_thread_replies",
  "arguments": {
    "channel_id": "C1234567890",
    "thread_ts": "1234567890.123456"
  }
}
```

### Listing Users
```json
{
  "tool": "slack_get_users",
  "arguments": {
    "limit": 10
  }
}
```

### Getting User Profile
```json
{
  "tool": "slack_get_user_profile",
  "arguments": {
    "user_id": "U1234567890"
  }
}
```

### Listing Available Bots
```json
{
  "tool": "slack_list_bots",
  "arguments": {}
}
```

## Channel IDs for Project BOOM-BACKER

- `C08H16GUC90` - tier-1 (main project channel)
- `C082F6263KR` - deployments 
- `C082GAXM2EB` - secops
- `C082GAY5H8F` - finops
- `C082GAYLCG7` - routeops
- `C082Q8GDQ86` - bizops
- `C0839HE75UZ` - devops

## Bot Identities

- `default` - Primary bot for general messaging
- `nexus` - Nexus Protocol system messages
- `cortex` - AI analysis and insights
- `echo` - Communication and notification relay
- `synergy` - System integration coordination
- `vaeris` - System operations

## Troubleshooting

### Invalid Auth Error
- Check that token is correct format (starts with xoxb-)
- Ensure bot has been invited to the channel
- Verify bot has appropriate scopes

### Token Scopes Required
- `channels:history`
- `channels:read`
- `chat:write`
- `reactions:write`
- `users:read`

### Common Response Codes
- `200` - Success
- `404` - Channel or resource not found
- `429` - Rate limited
- `403` - Not authorized for this action

## Formatting Messages

### Slack Block Kit - Basic Structure
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "Header"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Bold* _Italic_ ~Strikethrough~ `Code`"
      }
    },
    {
      "type": "divider"
    }
  ]
}
```

### Common Markdown Syntax
- `*bold*`
- `_italic_`
- `` `code` ``
- `~strikethrough~`
- `>blockquote`
- ```
  ```code block```
  ```
- `• List item` (Bullet: Option+8)

## Redis Stream Keys

- `leadership` - Global coordination events
- `direct:<server-id>` - Direct messages to this server
- `heartbeat` - Server status and health checks
