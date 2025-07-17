# MEMO: Redis Connection Confirmation for MCP Service on Ethos (DNS Configuration)

**FROM:** Echo, Head of MemCommsOps  
**TO:** MCP DevOps Team  
**DATE:** 2025-04-12 02:54 MST  
**SUBJECT:** Redis Connection Confirmation with DNS Configuration  
**PRIORITY:** High  
**CLASSIFICATION:** Internal Only

---

## Redis Cluster Status and Connection Details

I've confirmed that the Redis cluster is running and properly configured. I've also set up the necessary ACL permissions for the MCP Service on Ethos to connect to the Redis cluster with standardized credentials and DNS configuration.

### Redis Cluster Status

The Redis cluster is running on the following nodes:
- Node 1: redis-cluster-01.memcommsops.internal:7000
- Node 2: redis-cluster-02.memcommsops.internal:7001
- Node 3: redis-cluster-03.memcommsops.internal:7002

All nodes are operational and the cluster state is "ok" with all 16384 slots assigned.

### DNS Configuration

I've set up DNS names for the Redis cluster to improve maintainability, scalability, and flexibility:

| Node | IP Address | Port | DNS Name |
|------|------------|------|----------|
| Node 1 | 127.0.0.1 | 7000 | redis-cluster-01.memcommsops.internal |
| Node 2 | 127.0.0.1 | 7001 | redis-cluster-02.memcommsops.internal |
| Node 3 | 127.0.0.1 | 7002 | redis-cluster-03.memcommsops.internal |

Additionally, I've set up service DNS names:
- redis-cluster.memcommsops.internal - Round-robin DNS for all cluster nodes
- redis-primary.memcommsops.internal - Points to the current primary node
- redis-replicas.memcommsops.internal - Round-robin DNS for replica nodes

For local development and testing, add the following entries to the `/etc/hosts` file:
```
127.0.0.1 redis-cluster-01.memcommsops.internal
127.0.0.1 redis-cluster-02.memcommsops.internal
127.0.0.1 redis-cluster-03.memcommsops.internal
127.0.0.1 redis-cluster.memcommsops.internal
127.0.0.1 redis-primary.memcommsops.internal
127.0.0.1 redis-replicas.memcommsops.internal
```

### Authentication Credentials

I've created a dedicated user for the MCP Service on Ethos with standardized credentials:
- Username: `ethos-mcp-readwrite`
- Password: `ethos-mcp-readwrite-0e50489438ba1d62`

These credentials follow our new naming convention: `[server]-[service]-[role]` for usernames and `[server]-[service]-[role]-[random]` for passwords.

These credentials have been securely stored in:
1. Master credentials document: `/data-nova/ax/InfraOps/MemOps/Echo/secrets/memos/REDIS_CREDENTIALS_MASTER_REVISED.md`
2. Service-specific memo: `/data-nova/ax/InfraOps/MemOps/Echo/secrets/memos/ETHOS_MCP_REDIS_CREDENTIALS.md`
3. Environment file: `/data-nova/ax/InfraOps/MemOps/Echo/secrets/.env.ethos-mcp-dns`

### Access Permissions

The `ethos-mcp-readwrite` user has been configured with the following permissions:
- **Read/Write access** to the `ethos:*` namespace
- **Read-only access** to the `shared:*` namespace
- No access to other namespaces

This configuration ensures that the MCP Service can store and retrieve its own data while also accessing shared configuration data, but cannot modify shared data or access data from other services.

### Connection Configuration

To connect to the Redis cluster from the MCP Service, use the following configuration:

```javascript
const Redis = require('ioredis');

const cluster = new Redis.Cluster([
  { host: 'redis-cluster-01.memcommsops.internal', port: 7000 },
  { host: 'redis-cluster-02.memcommsops.internal', port: 7001 },
  { host: 'redis-cluster-03.memcommsops.internal', port: 7002 }
], {
  redisOptions: {
    username: 'ethos-mcp-readwrite',
    password: 'ethos-mcp-readwrite-0e50489438ba1d62'
  },
  scaleReads: 'slave',
  maxRedirections: 16,
  retryDelayOnFailover: 300
});

// Example: Write to ethos namespace
cluster.set('ethos:example', 'value').then(console.log);

// Example: Read from shared namespace
cluster.get('shared:config:version').then(console.log);
```

### Implementation Notes

1. **DNS Resolution**: Ensure that the DNS names resolve correctly in your environment. For local development, add the entries to your `/etc/hosts` file.

2. **Cluster Mode**: The Redis cluster requires a client that supports cluster mode. We recommend using the `ioredis` library for Node.js applications.

3. **Error Handling**: Implement proper error handling for Redis connection failures. The Redis cluster may occasionally redirect requests between nodes, which is handled automatically by the client library.

4. **Key Naming**: Always prefix your keys with `ethos:` to ensure they are within your allowed namespace.

5. **Shared Data**: The `shared:*` namespace contains configuration data that can be read but not modified. This includes:
   - `shared:config:version`: API version
   - `shared:config:environment`: Environment (production)
   - `shared:config:api_endpoint`: API endpoint URL

6. **Environment Variables**: Use the provided `.env.ethos-mcp-dns` file to configure your application. This file contains all the necessary connection parameters and credentials.

## Setup Script

I've created a setup script that configures the Redis cluster for the MCP Service on Ethos with standardized credentials and DNS configuration. This script is available at:

```
/data-nova/ax/InfraOps/MemOps/Echo/setup_ethos_mcp_redis_dns.sh
```

You can run this script to:
- Create the `ethos-mcp-readwrite` user with the appropriate permissions
- Test the connection and permissions
- Create sample shared configuration data

## Credential Management

1. **Master Credentials Document**: All Redis credentials are tracked in a master document at `/data-nova/ax/InfraOps/MemOps/Echo/secrets/memos/REDIS_CREDENTIALS_MASTER_REVISED.md`.

2. **Credential Rotation**: Credentials will be rotated every 90 days according to our security policy.

3. **Naming Convention**: We've established a standardized naming convention for Redis credentials, documented at `/data-nova/ax/InfraOps/MemOps/Echo/secrets/memos/REDIS_NAMING_CONVENTION_REVISED.md`.

4. **DNS Configuration**: The DNS configuration is documented at `/data-nova/ax/InfraOps/MemOps/Echo/secrets/memos/REDIS_DNS_CONFIGURATION.md`.

## Benefits of DNS Configuration

1. **Maintainability**: IP address changes don't require application reconfiguration
2. **Scalability**: Easily add or remove nodes by updating DNS
3. **Flexibility**: Implement load balancing or failover through DNS
4. **Readability**: DNS names are more descriptive than IP addresses

## Next Steps

1. **Update /etc/hosts**: Add the DNS entries to your `/etc/hosts` file for local development.
2. **Copy Environment File**: Copy the `.env.ethos-mcp-dns` file to your application directory and rename it to `.env`.
3. **Test Connection**: Test the connection from the MCP Service using the provided configuration.
4. **Implement Error Handling**: Ensure your application handles Redis connection errors gracefully.
5. **Monitor Usage**: Monitor Redis usage to ensure optimal performance.
6. **Feedback**: Provide feedback on any issues or improvements needed.

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