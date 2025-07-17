# Nexus Protocol Integration Guide

This guide provides specific instructions for integrating the Slack MCP Server with the Nexus Protocol in Project BOOM-BACKER.

## Overview

The Nexus Protocol requires multiple communication channels with distinct visual identities in Slack. The multi-bot functionality of the Slack MCP Server enables each Nexus Protocol component to communicate with its own identity, providing clear context for users and systems.

## Bot Identity Mapping

Each component of the Nexus Protocol has a corresponding bot identity:

| Component | Bot ID | Purpose |
|-----------|--------|---------|
| Nexus Core | `nexus` | Main system coordination and leadership messages |
| Cortex | `cortex` | AI analysis, insights, and knowledge management |
| Echo | `echo` | Communication relay and notification management |
| Synergy | `synergy` | System integration and cross-component coordination |
| Vaeris | `vaeris` | System operations and infrastructure management |
| Catalyst | `catalyst` | Process acceleration and optimization |

## Integration Architecture

```
┌─────────────────────────────────────────┐
│            Nexus Protocol               │
├─────────┬─────────┬─────────┬───────────┤
│  Nexus  │ Cortex  │  Echo   │  Synergy  │
│  Core   │         │         │           │
└────┬────┴────┬────┴────┬────┴─────┬─────┘
     │         │         │          │
     ▼         ▼         ▼          ▼
┌─────────────────────────────────────────┐
│          Slack MCP Server               │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │      Multi-Bot Functionality    │    │
│  └─────────────────────────────────┘    │
└─────────────────────┬───────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────┐
│            Slack Workspace              │
│                                         │
│  #tier-1  #devops  #bizops  #secops ... │
└─────────────────────────────────────────┘
```

## Implementation Steps

### 1. MCP Server Configuration

Ensure your `.env` file includes tokens for all Nexus Protocol components:

```
SLACK_BOT_TOKEN=xoxb-default-bot-token
SLACK_BOT_TOKEN_NEXUS=xoxb-nexus-bot-token
SLACK_BOT_TOKEN_CORTEX=xoxb-cortex-bot-token
SLACK_BOT_TOKEN_ECHO=xoxb-echo-bot-token
SLACK_BOT_TOKEN_SYNERGY=xoxb-synergy-bot-token
SLACK_BOT_TOKEN_VAERIS=xoxb-vaeris-bot-token
SLACK_BOT_TOKEN_CATALYST=xoxb-catalyst-bot-token
```

### 2. Nexus Protocol Communication

When the Nexus Protocol needs to send messages, it should specify the appropriate bot identity based on the component:

```javascript
// Nexus Core communication
const nexusCoreMessage = {
  tool: "slack_post_message",
  arguments: {
    channel_id: "C08H16GUC90", // tier-1 channel
    text: "System coordination message from Nexus Core",
    bot_id: "nexus"
  }
};

// Cortex analysis
const cortexMessage = {
  tool: "slack_post_message",
  arguments: {
    channel_id: "C08H16GUC90", // tier-1 channel
    text: "Analysis results from Cortex system",
    bot_id: "cortex"
  }
};
```

### 3. Channel Strategy

Different types of messages should be sent to appropriate channels:

| Message Type | Channel | Bot Identity |
|--------------|---------|--------------|
| System announcements | `tier-1` | `nexus` |
| Technical alerts | `devops` | `echo` |
| Security notifications | `secops` | `vaeris` |
| Infrastructure updates | `deployments` | `synergy` |
| AI analysis | Relevant channel | `cortex` |
| Process optimization | `bizops` | `catalyst` |

### 4. Thread Management

For extended conversations on a topic, use thread replies to keep channels organized:

```javascript
// Initial message from Nexus
const initialMessage = await sendMcpRequest({
  tool: "slack_post_message",
  arguments: {
    channel_id: "C08H16GUC90",
    text: "Starting new system analysis",
    bot_id: "nexus"
  }
});

// Thread reply from Cortex with analysis
await sendMcpRequest({
  tool: "slack_reply_to_thread",
  arguments: {
    channel_id: "C08H16GUC90",
    thread_ts: initialMessage.timestamp,
    text: "Analysis complete. Results attached.",
    bot_id: "cortex"
  }
});
```

### 5. Status Indicators

Use emoji reactions to indicate status changes:

```javascript
// Mark message as being processed
await sendMcpRequest({
  tool: "slack_add_reaction",
  arguments: {
    channel_id: "C08H16GUC90",
    timestamp: "1234567890.123456",
    reaction: "hourglass"
  }
});

// Later, mark as complete
await sendMcpRequest({
  tool: "slack_add_reaction",
  arguments: {
    channel_id: "C08H16GUC90",
    timestamp: "1234567890.123456",
    reaction: "white_check_mark"
  }
});
```

## Redis Streams Integration

The Nexus Protocol components can communicate with each other and the MCP server through Redis streams:

1. **Leadership Stream**: For system-wide coordination
   ```
   XADD leadership * event system_startup component nexus_core
   ```

2. **Direct Messages**: For point-to-point communication
   ```
   XADD direct:slack-mcp-server * event request_status
   ```

## Error Handling Strategy

1. When a bot identity isn't available, the MCP server falls back to the default bot
2. Log all errors to the appropriate component's log stream
3. For critical communication failures, retry with exponential backoff
4. Consider implementing a circuit breaker pattern for persistent issues

## Message Formatting Guidelines

To maintain consistent appearance across all Nexus Protocol communications:

### Headers

All major messages should include a header identifying the component:

```
# Nexus Core: System Status Update
...message content...
```

### Status Indicators

Use consistent emoji for status indications:
- 🟢 Success
- 🟡 Warning
- 🔴 Error
- ⏳ Processing
- ✅ Complete

### Formatting Examples

Nexus Core message:
```
# Nexus Core: System Status Update

## Current Status: 🟢 Operational

All Nexus Protocol components are functioning normally. 
System load: 23%
Active connections: 156
```

Cortex analysis message:
```
# Cortex Analysis: Project Performance

## Key Metrics
- Completion rate: 89% ↑
- Resource utilization: 72% ↓
- Quality score: 96% ↑

## Recommendations
1. Allocate 15% more resources to Task #45
2. Review dependency chain in Phase 3
```

## Testing

Before deploying changes to the Nexus Protocol integration, test using the verification channel:

```javascript
const testMessage = {
  tool: "slack_post_message",
  arguments: {
    channel_id: "C082F8T5N95", // test-bot-channel
    text: "Test message from [Component]",
    bot_id: "your_component_bot_id"
  }
};
```

## Security Considerations

1. Keep bot tokens secure and never commit them to code repositories
2. Each component should only have access to the bot identities it needs
3. Use secure channels for sensitive information
4. Regularly audit message patterns and access

## Troubleshooting

### Common Integration Issues

1. **Authentication Failures**
   - Check that the bot token is correctly set in environment variables
   - Verify the bot user exists and is properly configured in Slack

2. **Missing Messages**
   - Confirm the bot has been invited to the target channel
   - Check logs for error messages
   - Verify Redis connectivity for cross-component communication

3. **Wrong Bot Identity**
   - Ensure the `bot_id` parameter is correctly set
   - Check environment variable naming (should be `SLACK_BOT_TOKEN_<UPPERCASE_BOT_ID>`)
