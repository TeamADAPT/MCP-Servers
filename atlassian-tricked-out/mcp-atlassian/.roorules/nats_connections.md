# NATS Connection Documentation

**Date:** May 9, 2025  
**Author:** Keystone  
**Status:** READY FOR MIDNIGHT LAUNCH

## Connection Details

| Parameter | Value | Notes |
|-----------|-------|-------|
| Host | 127.0.0.1 | Local host |
| Port | 12310 | Main NATS port |
| HTTP Port | 8222 | HTTP monitoring interface |
| Authentication | Basic Auth | Username and password required |
| Username | `nats_user` | Authentication username |
| Password | `nats-password-f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2` | Authentication password |
| JetStream Data Directory | `/data-nova/ax/InfraOps/CommsOps/nova-task-system/data/nats/jetstream` | Location of JetStream data files |
| Configuration | `/data-nova/ax/InfraOps/CommsOps/nova-task-system/nats-server.conf` | Main NATS configuration file |
| Service | `nats-server.service` | Systemd service name |
| MCP Server | `nats-mcp-server.service` | NATS MCP server service |

## Connection Examples

### CLI Connection

```bash
# Connect to NATS server
nats-cli connect --server=nats://nats_user:nats-password-f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2@127.0.0.1:12310

# Publish a message
nats-cli publish test.subject "Hello NATS" --server=nats://nats_user:nats-password-f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2@127.0.0.1:12310

# Subscribe to a subject
nats-cli subscribe test.subject --server=nats://nats_user:nats-password-f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2@127.0.0.1:12310
```

### Node.js Connection

```javascript
const { connect, StringCodec } = require('nats');

async function connectToNats() {
  try {
    // Connect to NATS server
    const nc = await connect({
      servers: 'nats://127.0.0.1:12310',
      user: 'nats_user',
      pass: 'nats-password-f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2'
    });
    
    console.log('Connected to NATS server');
    
    // Create a string codec
    const sc = StringCodec();
    
    // Subscribe to a subject
    const sub = nc.subscribe('test.subject');
    
    // Process incoming messages
    (async () => {
      for await (const msg of sub) {
        console.log(`Received: ${sc.decode(msg.data)}`);
      }
    })();
    
    // Publish a message
    nc.publish('test.subject', sc.encode('Hello from Node.js'));
    
    return nc;
  } catch (error) {
    console.error('Error connecting to NATS:', error);
    throw error;
  }
}

// Usage
connectToNats()
  .then(nc => {
    // Close connection after 5 seconds
    setTimeout(() => {
      nc.close();
      console.log('Connection closed');
    }, 5000);
  })
  .catch(error => {
    console.error('Failed to connect:', error);
  });
```

### Python Connection

```python
import asyncio
import nats

async def connect_to_nats():
    try:
        # Connect to NATS server
        nc = await nats.connect(
            servers=["nats://127.0.0.1:12310"],
            user="nats_user",
            password="nats-password-f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2"
        )
        
        print("Connected to NATS server")
        
        # Subscribe to a subject
        async def message_handler(msg):
            subject = msg.subject
            data = msg.data.decode()
            print(f"Received message on {subject}: {data}")
        
        await nc.subscribe("test.subject", cb=message_handler)
        
        # Publish a message
        await nc.publish("test.subject", b"Hello from Python")
        
        # Wait for a moment to receive messages
        await asyncio.sleep(5)
        
        # Close connection
        await nc.close()
        print("Connection closed")
    
    except Exception as e:
        print(f"Error connecting to NATS: {e}")

# Run the async function
asyncio.run(connect_to_nats())
```

## JetStream Operations

### Creating a Stream

```bash
# Using CLI
nats-cli stream create my-stream --subjects="my-subject.*" --server=nats://nats_user:nats-password-f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2@127.0.0.1:12310
```

```javascript
// Using Node.js
const { connect } = require('nats');

async function createStream() {
  const nc = await connect({
    servers: 'nats://127.0.0.1:12310',
    user: 'nats_user',
    pass: 'nats-password-f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2'
  });
  
  const jsm = await nc.jetstreamManager();
  
  await jsm.streams.add({
    name: 'my-stream',
    subjects: ['my-subject.*']
  });
  
  console.log('Stream created');
  await nc.close();
}
```

### Publishing to JetStream

```javascript
// Using Node.js
const { connect, StringCodec } = require('nats');

async function publishToJetStream() {
  const nc = await connect({
    servers: 'nats://127.0.0.1:12310',
    user: 'nats_user',
    pass: 'nats-password-f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2'
  });
  
  const js = nc.jetstream();
  const sc = StringCodec();
  
  const ack = await js.publish('my-subject.test', sc.encode('Hello JetStream'));
  console.log(`Message published, sequence: ${ack.seq}`);
  
  await nc.close();
}
```

## Service Management

```bash
# Check NATS service status
systemctl status nats-server

# Start NATS service
sudo systemctl start nats-server

# Stop NATS service
sudo systemctl stop nats-server

# Restart NATS service
sudo systemctl restart nats-server

# View NATS logs
journalctl -u nats-server -f

# Check NATS MCP server status
systemctl status nats-mcp-server

# Restart NATS MCP server
sudo systemctl restart nats-mcp-server
```

## Troubleshooting

### Connection Issues

```bash
# Check if NATS server is running
ps aux | grep nats-server

# Check NATS port
ss -tlnp | grep 12310

# Check NATS HTTP monitoring port
ss -tlnp | grep 8222

# Check NATS server logs
journalctl -u nats-server -n 50
```

### Authentication Issues

```bash
# Verify authentication settings in config file
grep -A 5 "authorization" /data-nova/ax/InfraOps/CommsOps/nova-task-system/nats-server.conf
```

### JetStream Issues

```bash
# Check JetStream status
nats-cli stream info --server=nats://nats_user:nats-password-f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2@127.0.0.1:12310

# Check JetStream directory permissions
ls -la /data-nova/ax/InfraOps/CommsOps/nova-task-system/data/nats/jetstream
```

## Security Considerations

1. **Authentication**: NATS is configured with username/password authentication. Always include these credentials when connecting.
2. **Network Security**: NATS is currently only accessible from localhost (127.0.0.1).
3. **TLS**: NATS can be configured with TLS for encrypted communications, but this is not currently enabled.
4. **Authorization**: Consider implementing subject-based authorization for production environments.
5. **Credentials Management**: Store NATS credentials securely and rotate them periodically.

## Contact Information

For any issues or questions regarding NATS, please contact:

- **Keystone (CommsOps)**: keystone@nova.ai or via Redis stream `commsops.keystone.direct`
- **DevOps Team**: devops@nova.ai or via Redis stream `devops.genesis.direct`

---

*This document is confidential and contains sensitive information.*
*Store securely and do not share without proper authorization.*