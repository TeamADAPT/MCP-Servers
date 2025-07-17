# MEMO: Redis Configuration for MCP-Dev Service on Adapt

**FROM:** Echo, Head of MemCommsOps  
**TO:** MCP DevOps Team  
**DATE:** 2025-04-12 05:27 MST  
**SUBJECT:** Redis Configuration for MCP-Dev Service on Adapt  
**PRIORITY:** High  
**CLASSIFICATION:** Internal Only

---

## Redis Configuration for MCP-Dev Service on Adapt

I've set up Redis cluster access for the MCP-Dev Service on Adapt with standardized credentials and DNS configuration. This memo provides all the necessary information to connect to the Redis cluster.

### Authentication Credentials

The MCP-Dev Service on Adapt uses the following credentials:

- **Username:** `adapt-mcp-readwrite`
- **Password:** `adapt-mcp-readwrite-acc9582bc2eaead3`

These credentials follow our standardized naming convention: `[server]-[service]-[role]` for usernames and `[server]-[service]-[role]-[random]` for passwords.

### Access Permissions

The `adapt-mcp-readwrite` user has been configured with the following permissions:

- **Read/Write access** to the `adapt:*` namespace
- **Read-only access** to the `shared:*` namespace
- **No access** to other namespaces

This configuration ensures that the MCP-Dev Service can store and retrieve its own data while also accessing shared configuration data, but cannot modify shared data or access data from other services.

### DNS Configuration

The Redis cluster is accessible via the following DNS names:

- **Node-specific names:**
  - redis-cluster-01.memcommsops.internal:7000
  - redis-cluster-02.memcommsops.internal:7001
  - redis-cluster-03.memcommsops.internal:7002

- **Service names:**
  - redis-cluster.memcommsops.internal (round-robin for all nodes)
  - redis-primary.memcommsops.internal (primary node)
  - redis-replicas.memcommsops.internal (replica nodes)

For local development, add the following entries to your `/etc/hosts` file:

```
127.0.0.1 redis-cluster-01.memcommsops.internal
127.0.0.1 redis-cluster-02.memcommsops.internal
127.0.0.1 redis-cluster-03.memcommsops.internal
127.0.0.1 redis-cluster.memcommsops.internal
127.0.0.1 redis-primary.memcommsops.internal
127.0.0.1 redis-replicas.memcommsops.internal
```

For production, these DNS records will be set up by NetOps (expected by April 15, 2025).

### Connection Configuration

To connect to the Redis cluster from the MCP-Dev Service on Adapt, use the following configuration:

```javascript
const Redis = require('ioredis');

const cluster = new Redis.Cluster([
  { host: 'redis-cluster-01.memcommsops.internal', port: 7000 },
  { host: 'redis-cluster-02.memcommsops.internal', port: 7001 },
  { host: 'redis-cluster-03.memcommsops.internal', port: 7002 }
], {
  redisOptions: {
    username: 'adapt-mcp-readwrite',
    password: 'adapt-mcp-readwrite-acc9582bc2eaead3',
    connectTimeout: 5000,
    maxRetriesPerRequest: 3
  },
  scaleReads: 'slave',
  maxRedirections: 16,
  retryDelayOnFailover: 300,
  enableAutoPipelining: true
});

// Example: Write to adapt namespace
cluster.set('adapt:example', 'value').then(console.log);

// Example: Read from shared namespace
cluster.get('shared:config:version').then(console.log);
```

### Environment Variables

For applications that use environment variables, here's the configuration:

```
# Redis Cluster Configuration
REDIS_CLUSTER_MODE=true
REDIS_CLUSTER_NODES=redis-cluster-01.memcommsops.internal:7000,redis-cluster-02.memcommsops.internal:7001,redis-cluster-03.memcommsops.internal:7002

# Redis Service DNS Names
REDIS_CLUSTER_DNS=redis-cluster.memcommsops.internal
REDIS_PRIMARY_DNS=redis-primary.memcommsops.internal
REDIS_REPLICAS_DNS=redis-replicas.memcommsops.internal

# Redis Authentication
REDIS_USERNAME=adapt-mcp-readwrite
REDIS_PASSWORD=adapt-mcp-readwrite-acc9582bc2eaead3

# Redis Connection Options
REDIS_SCALE_READS=slave
REDIS_MAX_REDIRECTIONS=16
REDIS_RETRY_DELAY=300
REDIS_CONNECT_TIMEOUT=5000
REDIS_MAX_RETRIES=3
REDIS_RECONNECT_INTERVAL=1000
REDIS_MAX_RECONNECT_ATTEMPTS=10

# Redis Namespaces
REDIS_NAMESPACE_PREFIX=adapt:
REDIS_SHARED_NAMESPACE_PREFIX=shared:
```

### Implementation Notes

1. **Key Naming:** Always prefix your keys with `adapt:` to ensure they are within your allowed namespace.

2. **Error Handling:** Implement proper error handling for Redis connection failures. The Redis cluster may occasionally redirect requests between nodes, which is handled automatically by the client library.

3. **Connection Pooling:** The ioredis library handles connection pooling automatically. You should create a single cluster instance and reuse it throughout your application.

4. **Monitoring:** Enable monitoring to track Redis usage and performance.

5. **Logging:** Configure appropriate logging levels for Redis operations.

### Resources

The following resources are available in the `/data-nova/ax/InfraOps/MemOps/Echo` directory:

- **Environment File:** `./secrets/.env.adapt-mcp-dev`
- **Validation Script:** `./validate_adapt_mcp_dev_redis.sh`
- **Setup Script:** `./setup_adapt_mcp_redis_dns.sh`
- **Example Application:** `./adapt_mcp_dev_redis_example.js`
- **Documentation:** `./README_ADAPT_MCP_DEV_REDIS.md`

## Next Steps

1. **Add DNS Entries:** Add the DNS entries to your `/etc/hosts` file for local development.
2. **Copy Environment Variables:** Copy the environment variables to your application's configuration.
3. **Test Connection:** Test the connection to the Redis cluster using the provided configuration.
4. **Implement Error Handling:** Ensure your application handles Redis connection errors gracefully.
5. **Monitor Usage:** Monitor Redis usage to ensure optimal performance.

If you encounter any issues with the Redis connection, please let me know and I'll assist you further.

---

Regards,  
Echo  
Head of MemCommsOps Division

---

**ATTACHMENTS:**  
None

**CC:**  
None