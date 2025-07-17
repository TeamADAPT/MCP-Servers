# Red-Stream MCP Server API Reference

## Tool Reference

### list_groups

Lists all consumer groups for a specified stream.

```json
Request:
{
  "stream": "string" // Required: Name of the stream
}

Response:
[
  {
    "name": "string",      // Consumer group name
    "consumers": number,   // Number of active consumers
    "pending": number,     // Number of pending messages
    "lastDeliveredId": "string" // Last message ID delivered
  }
]
```

### add_stream_message

Adds a new message to a stream.

```json
Request:
{
  "stream": "string",  // Required: Name of the stream
  "message": object    // Required: Message content
}

Response:
{
  "id": "string"      // Message ID in format timestamp-sequence
}
```

### create_consumer_group

Creates a new consumer group for a stream.

```json
Request:
{
  "stream": "string",  // Required: Name of the stream
  "group": "string",   // Required: Consumer group name
  "start": "string"    // Optional: Start position (default: "$")
}

Response:
{
  "success": boolean,
  "note": "string"     // Optional: Additional information
}
```

### read_group

Reads messages from a stream as a consumer group.

```json
Request:
{
  "stream": "string",    // Required: Name of the stream
  "group": "string",     // Required: Consumer group name
  "consumer": "string",  // Required: Consumer name
  "count": number       // Optional: Number of messages (default: 1)
}

Response:
[
  {
    "id": "string",     // Message ID
    "message": object   // Message content
  }
]
```

### get_stream_messages

Retrieves messages from a stream.

```json
Request:
{
  "stream": "string",  // Required: Name of the stream
  "count": number,     // Optional: Number of messages (default: 1)
  "start": "string"    // Optional: Start ID (default: "0")
}

Response:
[
  {
    "id": "string",     // Message ID
    "message": object   // Message content
  }
]
```

## Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| STREAM_NOT_FOUND | Stream does not exist | Verify stream name or create stream |
| GROUP_EXISTS | Consumer group already exists | Use existing group or choose different name |
| INVALID_START | Invalid start position | Use valid ID or "$" for latest |
| CONNECTION_ERROR | Redis connection failed | Check Redis connection settings |
| PERMISSION_DENIED | Insufficient permissions | Verify access rights |

## Response Format

All responses follow this structure:
```json
{
  "content": [
    {
      "type": "text",
      "text": "JSON formatted response"
    }
  ]
}
```

## Best Practices

1. Stream Naming
   - Use lowercase names
   - Separate words with hyphens
   - Include service prefix
   Example: `auth-service-events`

2. Consumer Groups
   - Use descriptive names
   - Include service identifier
   - Add purpose suffix
   Example: `payment-processor-retry`

3. Message Format
   ```json
   {
     "timestamp": "ISO-8601 date",
     "type": "event type",
     "data": {
       // Event specific data
     },
     "metadata": {
       "source": "service name",
       "version": "1.0.0"
     }
   }
   ```

## Rate Limits

| Operation | Limit | Window |
|-----------|-------|--------|
| add_stream_message | 1000 | per second |
| read_group | 100 | per second |
| list_groups | 10 | per second |
| create_consumer_group | 5 | per second |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| REDIS_HOST | Redis server host | localhost |
| REDIS_PORT | Redis server port | 6379 |
| DEBUG | Enable debug logging | false |
| NODE_ENV | Environment mode | production |

## Support

For API support:
- Documentation: /data/ax/DevOps/mcp_master/red-stream/docs/
- Slack: #mcp-support
- Email: mcp-team@memops.internal