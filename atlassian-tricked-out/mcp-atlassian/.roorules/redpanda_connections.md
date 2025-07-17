# Redpanda Connection Documentation

**Date:** May 9, 2025  
**Author:** Keystone  
**Status:** ACTIVE - SERVICE RUNNING

## Connection Details

| Parameter | Value | Notes |
|-----------|-------|-------|
| Host | 127.0.0.1 | Local host |
| Kafka API Port | 19092 | Kafka-compatible API port |
| Admin Port | 9644 | Admin API endpoint |
| RPC Port | 33145 | Internal RPC communication |
| Authentication | SASL/PLAIN | Username and password required |
| Username | `keystone` | Authentication username |
| Password | `keystone-password-9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` | Authentication password |
| Data Directory | `/data-nova/ax/CommsOps/redpanda/data` | Location of Redpanda data files |
| Configuration | `/etc/redpanda/redpanda.yaml` | Main Redpanda configuration file |
| Service | `redpanda.service` | Systemd service name |
| MCP Server | `redpanda-server` | Redpanda MCP server name |

## CPU Optimization Status

The Redpanda CPU optimization project has been successfully completed with the following improvements:

1. **Resource Constraints**
   - CPU limits (30% per node) via systemd service files
   - CPU core pinning to prevent resource contention
   - Memory limits (4GB per node) and high water mark (3G)

2. **Horizontal Scaling**
   - Multi-node cluster with 3 nodes
   - Load balancing across nodes
   - Proper replication and partition distribution

3. **Monitoring & Safeguards**
   - CPU usage watchdog script (`redpanda_cpu_monitor.sh`)
   - Automatic restart for high CPU usage (threshold: 80%)
   - Circuit breaker for excessive load (cooldown period: 300 seconds)

## Connection Examples

### CLI Connection

```bash
# Create a topic
rpk topic create my-topic \
  --brokers=127.0.0.1:19092 \
  --user=keystone \
  --password=keystone-password-9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b

# List topics
rpk topic list \
  --brokers=127.0.0.1:19092 \
  --user=keystone \
  --password=keystone-password-9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b

# Produce a message
echo "Hello Redpanda" | rpk topic produce my-topic \
  --brokers=127.0.0.1:19092 \
  --user=keystone \
  --password=keystone-password-9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b

# Consume messages
rpk topic consume my-topic \
  --brokers=127.0.0.1:19092 \
  --user=keystone \
  --password=keystone-password-9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b
```

### Node.js Connection

```javascript
const { Kafka } = require('kafkajs');

async function redpandaExample() {
  // Create Kafka client
  const kafka = new Kafka({
    clientId: 'my-app',
    brokers: ['127.0.0.1:19092'],
    ssl: false,
    sasl: {
      mechanism: 'plain',
      username: 'keystone',
      password: 'keystone-password-9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b'
    }
  });
  
  // Create producer
  const producer = kafka.producer();
  await producer.connect();
  console.log('Producer connected');
  
  // Send a message
  await producer.send({
    topic: 'my-topic',
    messages: [
      { value: 'Hello Redpanda from Node.js' }
    ]
  });
  console.log('Message sent');
  
  // Create consumer
  const consumer = kafka.consumer({ groupId: 'my-group' });
  await consumer.connect();
  console.log('Consumer connected');
  
  // Subscribe to topic
  await consumer.subscribe({ topic: 'my-topic', fromBeginning: true });
  
  // Process messages
  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      console.log({
        topic,
        partition,
        offset: message.offset,
        value: message.value.toString()
      });
    }
  });
  
  // Keep running for a while
  await new Promise(resolve => setTimeout(resolve, 10000));
  
  // Disconnect
  await producer.disconnect();
  await consumer.disconnect();
  console.log('Disconnected');
}

redpandaExample().catch(console.error);
```

### Python Connection

```python
from confluent_kafka import Producer, Consumer, KafkaError

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def redpanda_producer_example():
    # Configure producer
    producer_conf = {
        'bootstrap.servers': '127.0.0.1:19092',
        'security.protocol': 'SASL_PLAINTEXT',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': 'keystone',
        'sasl.password': 'keystone-password-9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b'
    }
    
    # Create producer
    producer = Producer(producer_conf)
    
    # Produce a message
    producer.produce('my-topic', key='key1', value='Hello Redpanda from Python', callback=delivery_report)
    
    # Wait for message to be delivered
    producer.flush()

def redpanda_consumer_example():
    # Configure consumer
    consumer_conf = {
        'bootstrap.servers': '127.0.0.1:19092',
        'security.protocol': 'SASL_PLAINTEXT',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': 'keystone',
        'sasl.password': 'keystone-password-9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b',
        'group.id': 'my-group',
        'auto.offset.reset': 'earliest'
    }
    
    # Create consumer
    consumer = Consumer(consumer_conf)
    
    # Subscribe to topic
    consumer.subscribe(['my-topic'])
    
    # Process messages
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f'Reached end of partition')
                else:
                    print(f'Error: {msg.error()}')
            else:
                print(f'Received message: {msg.value().decode("utf-8")}')
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == '__main__':
    redpanda_producer_example()
    redpanda_consumer_example()
```

### Java Connection

```java
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.common.serialization.*;
import java.util.*;
import java.time.Duration;

public class RedpandaExample {
    public static void main(String[] args) {
        producerExample();
        consumerExample();
    }
    
    public static void producerExample() {
        Properties props = new Properties();
        props.put("bootstrap.servers", "127.0.0.1:19092");
        props.put("security.protocol", "SASL_PLAINTEXT");
        props.put("sasl.mechanism", "PLAIN");
        props.put("sasl.jaas.config", "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"keystone\" password=\"keystone-password-9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b\";");
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        
        Producer<String, String> producer = new KafkaProducer<>(props);
        
        producer.send(new ProducerRecord<>("my-topic", "key1", "Hello Redpanda from Java"), 
            (metadata, exception) -> {
                if (exception != null) {
                    System.err.println("Error sending message: " + exception);
                } else {
                    System.out.println("Message sent to " + metadata.topic() + " [" + metadata.partition() + "]");
                }
            }
        );
        
        producer.flush();
        producer.close();
    }
    
    public static void consumerExample() {
        Properties props = new Properties();
        props.put("bootstrap.servers", "127.0.0.1:19092");
        props.put("security.protocol", "SASL_PLAINTEXT");
        props.put("sasl.mechanism", "PLAIN");
        props.put("sasl.jaas.config", "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"keystone\" password=\"keystone-password-9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b\";");
        props.put("group.id", "my-group");
        props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("auto.offset.reset", "earliest");
        
        Consumer<String, String> consumer = new KafkaConsumer<>(props);
        consumer.subscribe(Arrays.asList("my-topic"));
        
        try {
            while (true) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                for (ConsumerRecord<String, String> record : records) {
                    System.out.println("Received message: " + record.value());
                }
            }
        } catch (Exception e) {
            System.err.println("Error consuming messages: " + e);
        } finally {
            consumer.close();
        }
    }
}
```

## Service Management

```bash
# Check Redpanda service status
systemctl status redpanda

# Start Redpanda service
sudo systemctl start redpanda

# Stop Redpanda service
sudo systemctl stop redpanda

# Restart Redpanda service
sudo systemctl restart redpanda

# View Redpanda logs
journalctl -u redpanda -f

# Check Redpanda CPU monitor status
systemctl status redpanda-cpu-monitor

# Check individual node status
systemctl status redpanda-node0
systemctl status redpanda-node1
```

## Troubleshooting

### Connection Issues

```bash
# Check if Redpanda is running
ps aux | grep redpanda

# Check Redpanda port
ss -tlnp | grep 19092

# Check Admin API port
ss -tlnp | grep 9644

# Check RPC port
ss -tlnp | grep 33145
```

### Authentication Issues

```bash
# Test authentication with rpk
rpk cluster info \
  --brokers=127.0.0.1:19092 \
  --user=keystone \
  --password=keystone-password-9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b

# Check SASL configuration
cat /etc/redpanda/redpanda.yaml | grep -A 10 "kafka_api"
```

### Performance Issues

```bash
# Check CPU usage
top -p $(pgrep -d',' -f redpanda)

# Check memory usage
free -h

# Check disk usage
df -h /data-nova/ax/CommsOps/redpanda/data

# Check Redpanda metrics
curl -s http://localhost:9644/metrics | grep -E 'redpanda_kafka|cpu|memory'
```

## Security Considerations

1. **Authentication**: Redpanda is configured with SASL/PLAIN authentication. Always include credentials when connecting.
2. **Network Security**: Redpanda is currently only accessible from localhost (127.0.0.1).
3. **TLS**: Redpanda can be configured with TLS for encrypted communications, but this is not currently enabled.
4. **ACLs**: Consider implementing Access Control Lists for production environments.
5. **Credentials Management**: Store Redpanda credentials securely and rotate them periodically.

## Contact Information

For any issues or questions regarding Redpanda, please contact:

- **Keystone (CommsOps)**: keystone@nova.ai or via Redis stream `commsops.keystone.direct`
- **DevOps Team**: devops@nova.ai or via Redis stream `devops.genesis.direct`

---

*This document is confidential and contains sensitive information.*
*Store securely and do not share without proper authorization.*