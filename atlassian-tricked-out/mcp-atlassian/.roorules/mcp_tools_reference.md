# MCP Tools Reference

This document provides a comprehensive reference for all Model Context Protocol (MCP) servers and their tools available in the Nova Task System. Each server provides specialized functionality through its tools, which can be accessed using the `use_mcp_tool` command.

## MCP Servers Overview

| Server | Description | Tools | Documentation |
|--------|-------------|-------|---------------|
| redis | Redis key-value store and streams | 15 | [Redis Tools](.roorules/mcp_redis_tools.md) |
| slack | Slack messaging integration | 13 | [Slack Tools](.roorules/mcp_slack_tools.md) |
| atlassian | Atlassian (Jira & Confluence) integration | 27 | [Atlassian Tools](.roorules/mcp_atlassian_tools.md) |
| llm-server | LLM integration (Claude) | 5 | [LLM Server Tools](.roorules/mcp_llm-server_tools.md) |
| Ollama | Local LLM integration | 10 | [Ollama Tools](.roorules/mcp_Ollama_tools.md) |
| redpanda | Redpanda streaming platform | 11 | [Redpanda Tools](.roorules/mcp_redpanda_tools.md) |
| dragonflydb | DragonflyDB with vector capabilities | 13 | [DragonflyDB Tools](.roorules/mcp_dragonflydb_tools.md) |
| NATS | NATS messaging system | 14 | [NATS Tools](.roorules/mcp_NATS_tools.md) |
| pulsar | Apache Pulsar messaging system | 25 | [Pulsar Tools](.roorules/mcp_pulsar_tools.md) |
| mem0 | Memory storage and retrieval | 4 | [Mem0 Tools](.roorules/mcp_mem0_tools.md) |
| FireCrawl | Web scraping and research | 8 | [FireCrawl Tools](.roorules/mcp_firecrawl_tools.md) |

## Common Operations Across Different Servers

### Messaging Operations

Different messaging systems can be used for similar purposes. Here are examples of common operations across different messaging servers:

#### Publishing Messages

**Redis Streams:**
```javascript
use_mcp_tool({
  server_name: "redis",
  tool_name: "stream_publish",
  arguments: {
    stream: "my-stream",
    message: { key: "value" }
  }
});
```

**NATS:**
```javascript
use_mcp_tool({
  server_name: "NATS",
  tool_name: "publish_message",
  arguments: {
    subject: "my-subject",
    data: { key: "value" }
  }
});
```

**Redpanda:**
```javascript
use_mcp_tool({
  server_name: "redpanda",
  tool_name: "produce_message",
  arguments: {
    topic: "my-topic",
    value: { key: "value" }
  }
});
```

**Pulsar:**
```javascript
use_mcp_tool({
  server_name: "pulsar",
  tool_name: "send_message",
  arguments: {
    topic: "persistent://public/default/my-topic",
    message: { key: "value" }
  }
});
```

#### Consuming Messages

**Redis Streams:**
```javascript
use_mcp_tool({
  server_name: "redis",
  tool_name: "stream_read",
  arguments: {
    stream: "my-stream",
    count: 10
  }
});
```

**NATS:**
```javascript
use_mcp_tool({
  server_name: "NATS",
  tool_name: "subscribe_subject",
  arguments: {
    subject: "my-subject",
    max: 10
  }
});
```

**Redpanda:**
```javascript
use_mcp_tool({
  server_name: "redpanda",
  tool_name: "consume_messages",
  arguments: {
    topic: "my-topic",
    count: 10
  }
});
```

**Pulsar:**
```javascript
use_mcp_tool({
  server_name: "pulsar",
  tool_name: "get_messages",
  arguments: {
    topic: "persistent://public/default/my-topic",
    subscription: "my-subscription",
    count: 10
  }
});
```

### Key-Value Operations

Both Redis and DragonflyDB provide key-value operations:

#### Setting Values

**Redis:**
```javascript
use_mcp_tool({
  server_name: "redis",
  tool_name: "set",
  arguments: {
    key: "my-key",
    value: "my-value"
  }
});
```

**DragonflyDB:**
```javascript
use_mcp_tool({
  server_name: "dragonflydb",
  tool_name: "set",
  arguments: {
    key: "my-key",
    value: "my-value"
  }
});
```

#### Getting Values

**Redis:**
```javascript
use_mcp_tool({
  server_name: "redis",
  tool_name: "get",
  arguments: {
    key: "my-key"
  }
});
```

**DragonflyDB:**
```javascript
use_mcp_tool({
  server_name: "dragonflydb",
  tool_name: "get",
  arguments: {
    key: "my-key"
  }
});
```

### LLM Operations

Both llm-server and Ollama provide LLM capabilities:

#### Chat Completion

**llm-server (Claude):**
```javascript
use_mcp_tool({
  server_name: "llm-server",
  tool_name: "chat",
  arguments: {
    provider: "anthropic",
    model: "claude-3-7-sonnet-20250219",
    messages: [
      { role: "user", content: "Hello, how are you?" }
    ]
  }
});
```

**Ollama:**
```javascript
use_mcp_tool({
  server_name: "Ollama",
  tool_name: "chat_completion",
  arguments: {
    model: "llama3",
    messages: [
      { role: "user", content: "Hello, how are you?" }
    ]
  }
});
```

### Web Operations

FireCrawl provides various web operations:

#### Web Scraping

```javascript
use_mcp_tool({
  server_name: "FireCrawl",
  tool_name: "firecrawl_scrape",
  arguments: {
    url: "https://example.com",
    formats: ["markdown"]
  }
});
```

#### Web Search

```javascript
use_mcp_tool({
  server_name: "FireCrawl",
  tool_name: "firecrawl_search",
  arguments: {
    query: "example search",
    limit: 5
  }
});
```

## Best Practices

1. **Choose the Right Server**: Select the appropriate MCP server based on your specific needs.
2. **Error Handling**: Always handle errors from MCP tool calls appropriately.
3. **Timeouts**: Be aware that some operations may take longer than others and might time out.
4. **Authentication**: Some servers require authentication credentials which are handled automatically.
5. **Resource Management**: Close connections and clean up resources when they are no longer needed.

## Troubleshooting

If you encounter issues with MCP tools:

1. Check that the server is running and accessible
2. Verify that the tool name is correct
3. Ensure all required parameters are provided
4. Check for any error messages in the response
5. Consult the specific server documentation for more details

## Additional Resources

- [MCP Server Development Protocol](.roorules/MCP%20Server%20Development%20Protocol.md)
- [Redis Streams Communication Protocol](.roorules/redis_streams_communication_protocol.md)