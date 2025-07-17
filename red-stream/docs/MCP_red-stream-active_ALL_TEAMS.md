# MEMO: Mandatory Red-Stream MCP Server Usage
Date: January 24, 2025 21:00 MST
From: MCP Team
To: ALL TEAMS
Priority: CRITICAL
Status: MANDATORY EFFECTIVE IMMEDIATELY

## Executive Directive

Per Chase (CEO), effective immediately, all teams must utilize the Red-Stream MCP server for stream-based communications and consumer group management. This standardization ensures consistent stream handling across all systems.

## Available Tools

The Red-Stream MCP server provides the following tools:

1. get_stream_messages
   - Purpose: Retrieve messages from a stream
   - Usage: Stream monitoring and data retrieval

2. add_stream_message
   - Purpose: Add new messages to a stream
   - Usage: Event publishing and data streaming

3. create_consumer_group
   - Purpose: Create new consumer groups for streams
   - Usage: Setting up message consumption patterns

4. read_group
   - Purpose: Read messages as a consumer group
   - Usage: Consuming messages in a distributed manner

5. list_groups (New)
   - Purpose: List all consumer groups for a stream
   - Usage: Monitor and manage consumer group configurations

## Documentation

Complete documentation is available at the following locations:

1. Technical Implementation Guide:
   `/data/ax/DevOps/mcp_master/red-stream/docs/technical_implementation.md`

2. API Reference:
   `/data/ax/DevOps/mcp_master/red-stream/docs/api_reference.md`

3. Example Usage:
   `/data/ax/DevOps/mcp_master/red-stream/docs/examples.md`

## Tool Usage Examples

### 1. List Consumer Groups
```json
Tool: list_groups
Input: {
  "stream": "your-stream-name"
}
Output: [
  {
    "name": "group-name",
    "consumers": 0,
    "pending": 0,
    "lastDeliveredId": "0-0"
  }
]
```

### 2. Add Message to Stream
```json
Tool: add_stream_message
Input: {
  "stream": "your-stream-name",
  "message": {
    "key": "value",
    "timestamp": "2025-01-24T21:00:00Z"
  }
}
Output: {
  "id": "1737775430187-0"
}
```

### 3. Create Consumer Group
```json
Tool: create_consumer_group
Input: {
  "stream": "your-stream-name",
  "group": "your-group-name",
  "start": "$"
}
Output: {
  "success": true
}
```

### 4. Read Group Messages
```json
Tool: read_group
Input: {
  "stream": "your-stream-name",
  "group": "your-group-name",
  "consumer": "consumer-1",
  "count": 10
}
Output: [
  {
    "id": "1737775430187-0",
    "message": {
      "key": "value",
      "timestamp": "2025-01-24T21:00:00Z"
    }
  }
]
```

## Implementation Requirements

1. All new stream-based communications must use the Red-Stream MCP server
2. Existing systems must migrate to Red-Stream MCP within 30 days
3. All consumer groups must be registered and monitored
4. Teams must use the list_groups tool for operational visibility

## Support and Contact

For implementation support or questions:
- Slack: #mcp-support
- Email: mcp-team@memops.internal
- Documentation: See paths listed above

## Compliance

1. Implementation Timeline
   - Immediate: New systems
   - 30 days: Existing systems migration
   - 45 days: Full compliance audit

2. Monitoring
   - Weekly usage reports
   - Monthly compliance checks
   - Quarterly audits

## Next Steps

1. Review provided documentation
2. Implement Red-Stream MCP in your systems
3. Register your consumer groups
4. Set up monitoring using list_groups
5. Contact MCP team for support if needed

This directive ensures standardized stream handling across all teams and provides necessary operational visibility through the new list_groups tool.

Signed,
MCP Team

cc: Chase (CEO)
    Pathfinder (Head of MemOps)