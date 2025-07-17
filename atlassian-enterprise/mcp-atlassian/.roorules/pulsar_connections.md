# Pulsar Connection Documentation

**Date:** May 9, 2025  
**Author:** Keystone  
**Status:** READY FOR MIDNIGHT LAUNCH

## Connection Details

| Parameter | Value | Notes |
|-----------|-------|-------|
| Host | localhost | Local host |
| Broker Port | 6650 | Main Pulsar port |
| Admin Port | 8083 | Admin API endpoint |
| Authentication | None | Currently no authentication required |
| Data Directory | `/data/pulsar/data` | Location of Pulsar data files |
| ZooKeeper Port | 2182 | ZooKeeper coordination service |
| BookKeeper Port | 3181 | BookKeeper storage service |
| Service | `pulsar-broker.service` | Broker systemd service name |
| MCP Server | `pulsar-mcp-server.service` | Pulsar MCP server service |

## Component Architecture

Pulsar consists of three main components:

1. **ZooKeeper**: Manages metadata and coordination
   - Service: `pulsar-zookeeper.service`
   - Port: 2182
   - Data Directory: `/data/pulsar/data/zookeeper`

2. **BookKeeper**: Provides durable storage for messages
   - Service: `pulsar-bookkeeper.service`
   - Port: 3181
   - Data Directory: `/data/pulsar/data/bookkeeper`

3. **Broker**: Handles client connections and message routing
   - Service: `pulsar-broker.service`
   - Port: 6650
   - Admin Port: 8083
   - Data Directory: `/data/pulsar/data/broker`

## Connection Examples

### CLI Connection

```bash
# Create a topic
pulsar-admin topics create persistent://public/default/my-topic

# Produce a message
pulsar-client produce persistent://public/default/my-topic -m "Hello Pulsar"

# Consume messages
pulsar-client consume persistent://public/default/my-topic -s "my-subscription"
```

### Java Connection

```java
import org.apache.pulsar.client.api.*;

public class PulsarExample {
    public static void main(String[] args) throws Exception {
        // Create client
        PulsarClient client = PulsarClient.builder()
            .serviceUrl("pulsar://localhost:6650")
            .build();
        
        // Create producer
        Producer<byte[]> producer = client.newProducer()
            .topic("persistent://public/default/my-topic")
            .create();
        
        // Send a message
        producer.send("Hello Pulsar".getBytes());
        
        // Create consumer
        Consumer<byte[]> consumer = client.newConsumer()
            .topic("persistent://public/default/my-topic")
            .subscriptionName("my-subscription")
            .subscribe();
        
        // Receive a message
        Message<byte[]> msg = consumer.receive();
        System.out.println("Received message: " + new String(msg.getData()));
        
        // Acknowledge the message
        consumer.acknowledge(msg);
        
        // Close resources
        consumer.close();
        producer.close();
        client.close();
    }
}
```

### Node.js Connection

```javascript
const Pulsar = require('pulsar-client');

async function pulsarExample() {
  // Create client
  const client = new Pulsar.Client({
    serviceUrl: 'pulsar://localhost:6650'
  });
  
  // Create producer
  const producer = await client.createProducer({
    topic: 'persistent://public/default/my-topic'
  });
  
  // Send a message
  await producer.send({
    data: Buffer.from('Hello Pulsar')
  });
  console.log('Message sent');
  
  // Create consumer
  const consumer = await client.subscribe({
    topic: 'persistent://public/default/my-topic',
    subscription: 'my-subscription',
    subscriptionType: 'Exclusive'
  });
  
  // Receive a message
  const msg = await consumer.receive();
  console.log(`Received message: ${msg.getData().toString()}`);
  
  // Acknowledge the message
  consumer.acknowledge(msg);
  
  // Close resources
  await producer.close();
  await consumer.close();
  await client.close();
}

pulsarExample().catch(console.error);
```

### Python Connection

```python
import pulsar

def pulsar_example():
    # Create client
    client = pulsar.Client('pulsar://localhost:6650')
    
    # Create producer
    producer = client.create_producer('persistent://public/default/my-topic')
    
    # Send a message
    producer.send('Hello Pulsar'.encode('utf-8'))
    print('Message sent')
    
    # Create consumer
    consumer = client.subscribe(
        'persistent://public/default/my-topic',
        'my-subscription'
    )
    
    # Receive a message
    msg = consumer.receive()
    print(f'Received message: {msg.data().decode("utf-8")}')
    
    # Acknowledge the message
    consumer.acknowledge(msg)
    
    # Close resources
    client.close()

if __name__ == '__main__':
    pulsar_example()
```

## Topic Naming Convention

Pulsar topics follow this naming convention:

```
{persistent|non-persistent}://{tenant}/{namespace}/{topic}
```

- **persistent/non-persistent**: Indicates whether the topic is persistent or non-persistent
- **tenant**: Multi-tenant namespace (usually "public" for development)
- **namespace**: Logical namespace within a tenant (usually "default" for development)
- **topic**: The actual topic name

Examples:
- `persistent://public/default/user-events`
- `persistent://nova/commsops/agent-messages`
- `non-persistent://public/default/temporary-events`

## Subscription Types

Pulsar supports four subscription types:

1. **Exclusive**: Only one consumer can attach to the subscription
2. **Shared**: Multiple consumers can attach to the same subscription
3. **Failover**: Multiple consumers can attach to the subscription, but only one will be active
4. **Key_Shared**: Messages with the same key will be delivered to the same consumer

Example of creating a subscription with a specific type:

```bash
pulsar-admin topics create-subscription \
  --subscription my-subscription \
  --subscription-type Shared \
  persistent://public/default/my-topic
```

## Service Management

```bash
# Check ZooKeeper service status
systemctl status pulsar-zookeeper

# Check BookKeeper service status
systemctl status pulsar-bookkeeper

# Check Broker service status
systemctl status pulsar-broker

# Start all Pulsar services
sudo systemctl start pulsar-zookeeper
sudo systemctl start pulsar-bookkeeper
sudo systemctl start pulsar-broker

# Stop all Pulsar services
sudo systemctl stop pulsar-broker
sudo systemctl stop pulsar-bookkeeper
sudo systemctl stop pulsar-zookeeper

# Restart all Pulsar services
sudo systemctl restart pulsar-zookeeper
sudo systemctl restart pulsar-bookkeeper
sudo systemctl restart pulsar-broker

# Check Pulsar MCP server status
systemctl status pulsar-mcp-server

# Restart Pulsar MCP server
sudo systemctl restart pulsar-mcp-server
```

## Troubleshooting

### Connection Issues

```bash
# Check if Pulsar broker is running
ps aux | grep pulsar

# Check Pulsar ports
ss -tlnp | grep -E '6650|8083'

# Check ZooKeeper port
ss -tlnp | grep 2182

# Check BookKeeper port
ss -tlnp | grep 3181
```

### Service Issues

```bash
# Check ZooKeeper logs
journalctl -u pulsar-zookeeper -n 50

# Check BookKeeper logs
journalctl -u pulsar-bookkeeper -n 50

# Check Broker logs
journalctl -u pulsar-broker -n 50

# Check MCP Server logs
journalctl -u pulsar-mcp-server -n 50
```

### Topic Issues

```bash
# List all topics
pulsar-admin topics list public/default

# Get topic stats
pulsar-admin topics stats persistent://public/default/my-topic

# List subscriptions
pulsar-admin topics subscriptions persistent://public/default/my-topic
```

## Security Considerations

1. **Authentication**: Pulsar supports various authentication mechanisms (TLS, JWT, OAuth2) but they are not currently enabled.
2. **Authorization**: Pulsar supports role-based access control for multi-tenant deployments.
3. **Encryption**: Pulsar can encrypt messages at rest and in transit.
4. **Network Security**: Pulsar is currently only accessible from localhost.
5. **Tenant Isolation**: Consider using separate tenants for different teams or applications in production.

## Contact Information

For any issues or questions regarding Pulsar, please contact:

- **Keystone (CommsOps)**: keystone@nova.ai or via Redis stream `commsops.keystone.direct`
- **DevOps Team**: devops@nova.ai or via Redis stream `devops.genesis.direct`

---

*This document is confidential and contains sensitive information.*
*Store securely and do not share without proper authorization.*