# Redis MCP Server Quick Reference

## Common Operations

### Basic Redis Commands
```typescript
// Set value
mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "set",
    arguments: { key: "mykey", value: "myvalue" }
});

// Get value
mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "get",
    arguments: { key: "mykey" }
});
```

### Stream Operations
```typescript
// Publish message
mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "stream_publish",
    arguments: {
        stream: "mystream",
        message: { type: "event", data: {} }
    }
});

// Read messages
mcp.use_mcp_tool({
    server_name: "github.com/modelcontextprotocol/servers/tree/main/src/redis",
    tool_name: "stream_read",
    arguments: { stream: "mystream" }
});
```

## Quick Health Checks

### Service Status
```bash
# Check service
systemctl status redis-mcp

# View logs
journalctl -u redis-mcp -f

# Check Redis
redis-cli -h 127.0.0.1 -p 7000 ping
```

### Common Issues & Solutions

1. Connection Lost
```
Problem: Redis connection drops
Solution: Check network and Redis cluster status
Command: redis-cli -h 127.0.0.1 -p 7000 cluster info
```

2. Service Failed
```
Problem: Service won't start
Solution: Check logs and Redis availability
Command: journalctl -u redis-mcp -n 50
```

3. Performance Issues
```
Problem: Slow operations
Solution: Check network latency and Redis memory
Command: redis-cli -h 127.0.0.1 -p 7000 info memory
```

## Best Practices Summary

### Key Naming
- Use `:` as separator
- Format: `<prefix>:<id>:<field>`
- Example: `user:1234:profile`

### Stream Management
- Set appropriate maxlen
- Use consumer groups for parallel processing
- Handle acknowledgments
- Clean up old messages

### Task Management
- Include metadata
- Use consistent status values
- Clean up completed tasks
- Handle updates atomically

### Error Handling
- Check responses
- Implement retries
- Log errors
- Handle timeouts

### Performance
- Batch operations
- Use appropriate timeouts
- Monitor stream lengths
- Clean up unused keys
- Use TTL for temp data

## Common Commands

### Service Management
```bash
# Start service
sudo systemctl start redis-mcp

# Stop service
sudo systemctl stop redis-mcp

# Restart service
sudo systemctl restart redis-mcp

# Enable on boot
sudo systemctl enable redis-mcp
```

### Log Viewing
```bash
# View all logs
journalctl -u redis-mcp

# View recent errors
journalctl -u redis-mcp -p err

# Follow logs
journalctl -u redis-mcp -f

# View today's logs
journalctl -u redis-mcp --since today
```

### Redis CLI
```bash
# Check cluster
redis-cli -h 127.0.0.1 -p 7000 cluster info

# List streams
redis-cli -h 127.0.0.1 -p 7000 TYPE *

# Monitor stream
redis-cli -h 127.0.0.1 -p 7000 XINFO STREAM mystream

# Check memory
redis-cli -h 127.0.0.1 -p 7000 info memory
```

## Environment Variables
```bash
REDIS_URL=redis://localhost:7000
NODE_ENV=production
DEBUG=redis*
```

## Important Paths
```
/etc/systemd/system/redis-mcp.service  # Service configuration
/var/log/journal                       # System logs
~/.config/redis-mcp/                   # Local configuration
```

## Support Resources
- Documentation: `docs/` directory
- Admin Guide: `docs/admin-guide.md`
- User Guide: `docs/user-guide.md`
- Issue Tracker: GitHub repository
- Logs: journalctl
