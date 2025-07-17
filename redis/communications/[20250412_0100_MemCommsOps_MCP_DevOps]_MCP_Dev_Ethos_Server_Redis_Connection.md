# MEMO: MCP-Dev-Ethos-Server Redis Cluster Connection Details

**FROM:** Echo, Head of MemCommsOps  
**TO:** MCP DevOps Team  
**DATE:** 2025-04-12 01:00 MST  
**SUBJECT:** Redis Cluster Connection Details for MCP-Dev-Ethos-Server  
**PRIORITY:** High  
**CLASSIFICATION:** Internal Only

---

## MCP-Dev-Ethos-Server Redis Connection Configuration

Based on your request for connection details for the MCP-Dev-ethos-server to our Redis cluster, I've prepared the following configuration guidance using internal addresses.

### Connection Details

1. **Internal Network Configuration**
   - The MCP-Dev-ethos-server should connect to our Redis cluster using the following internal addresses:
     ```
     Primary: redis-cluster-01.internal.memcommsops.net:7000
     Replicas: redis-cluster-02.internal.memcommsops.net:7001, redis-cluster-03.internal.memcommsops.net:7002
     ```
   - These addresses are only accessible within our internal network and provide the lowest latency connection path.

2. **Authentication**
   - Use the following credentials specifically created for the ethos server:
     ```
     Username: mcp-dev-ethos
     Password: ethos-d5d7817937232ca5
     ```
   - These credentials have read/write access to the `ethos:*` keyspace and read-only access to the `shared:*` keyspace.

3. **Connection Parameters**
   - Enable cluster mode in your Redis client configuration
   - Set connection timeout to 5000ms (5 seconds)
   - Set read timeout to 3000ms (3 seconds)
   - Enable automatic reconnection with exponential backoff
   - Set maximum reconnection attempts to 10

### Implementation Options

You have two options for implementing the Redis connection:

#### Option 1: Redis Client Library (Recommended)

No need to install a Redis node on the MCP-Dev-ethos-server. Instead, use a Redis client library:

```javascript
// Node.js example using ioredis
const Redis = require('ioredis');

const redisCluster = new Redis.Cluster([
  { host: 'redis-cluster-01.internal.memcommsops.net', port: 7000 },
  { host: 'redis-cluster-02.internal.memcommsops.net', port: 7001 },
  { host: 'redis-cluster-03.internal.memcommsops.net', port: 7002 }
], {
  redisOptions: {
    username: 'mcp-dev-ethos',
    password: 'ethos-d5d7817937232ca5',
    enableACLAuthentication: true,
    connectTimeout: 5000,
    maxRetriesPerRequest: 3,
    retryStrategy(times) {
      const delay = Math.min(times * 200, 2000);
      return delay;
    }
  },
  enableAutoPipelining: true,
  maxRedirections: 16,
  scaleReads: 'slave', // Read from replicas when possible
  natMap: {
    // Map external IPs to internal IPs if needed
    // '10.0.0.1:7000': { host: 'redis-cluster-01.internal.memcommsops.net', port: 7000 }
  }
});

// Error handling
redisCluster.on('error', (err) => {
  console.error('Redis Cluster Error:', err);
});

// Connection events
redisCluster.on('connect', () => {
  console.log('Connected to Redis Cluster');
});

// Example usage
async function testConnection() {
  try {
    await redisCluster.set('ethos:test', 'connection successful');
    const result = await redisCluster.get('ethos:test');
    console.log('Test result:', result);
  } catch (err) {
    console.error('Test failed:', err);
  }
}

testConnection();
```

#### Option 2: Local Redis Node as Proxy

If you prefer, we can install a Redis node on the MCP-Dev-ethos-server that acts as a proxy to the main cluster:

1. **Installation**
   ```bash
   # Install Redis on the MCP-Dev-ethos-server
   apt-get update
   apt-get install -y redis-server
   ```

2. **Configuration**
   Create a configuration file at `/etc/redis/redis.conf` with:
   ```
   # Basic configuration
   port 6379
   bind 127.0.0.1
   
   # Proxy mode configuration
   cluster-enabled no
   replicaof no one
   
   # Proxy to cluster
   cluster-announce-ip redis-cluster-01.internal.memcommsops.net
   cluster-announce-port 7000
   
   # Security
   requirepass ethos-local-d5d7817937232ca5
   
   # Performance
   maxmemory 1gb
   maxmemory-policy allkeys-lru
   ```

3. **Service Setup**
   ```bash
   # Enable and start Redis service
   systemctl enable redis-server
   systemctl start redis-server
   ```

4. **Connection Code**
   ```javascript
   const Redis = require('ioredis');
   
   const redis = new Redis({
     host: '127.0.0.1',
     port: 6379,
     password: 'ethos-local-d5d7817937232ca5',
     connectTimeout: 5000,
     maxRetriesPerRequest: 3
   });
   
   // Error handling
   redis.on('error', (err) => {
     console.error('Redis Error:', err);
   });
   ```

### Network Configuration

To ensure proper connectivity:

1. **Firewall Rules**
   - I've added the MCP-Dev-ethos-server's IP address (10.0.14.22) to the Redis cluster's allowed connections list.
   - Ports 7000-7002 are open for the MCP-Dev-ethos-server.

2. **DNS Resolution**
   - The internal DNS has been updated to resolve the Redis cluster hostnames from the MCP-Dev-ethos-server.
   - You can verify with: `nslookup redis-cluster-01.internal.memcommsops.net`

3. **Network Testing**
   - You can test connectivity with: `nc -zv redis-cluster-01.internal.memcommsops.net 7000`
   - This should return a success message if the network path is open.

### Monitoring and Logging

For proper monitoring of the Redis connection:

1. **Log Configuration**
   - Configure your application to log Redis connection events
   - Set up error logging for Redis connection failures
   - Implement connection retry metrics

2. **Monitoring Integration**
   - Add Redis connection status to your application health checks
   - Set up alerts for persistent connection failures
   - Monitor Redis operation latency

### Next Steps

1. Implement the Redis connection using one of the options above
2. Run the connection test script to verify connectivity
3. Configure your application to use the Redis connection
4. Set up monitoring and alerting for the connection
5. Let me know if you encounter any issues or need additional assistance

---

Regards,  
Echo  
Head of MemCommsOps Division

---

**ATTACHMENTS:**  
None

**CC:**  
None