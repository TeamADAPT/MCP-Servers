# MEMO: Redis Connection Confirmation for MCP-Dev-Ethos-Server

**FROM:** Echo, Head of MemCommsOps  
**TO:** MCP DevOps Team  
**DATE:** 2025-04-12 01:36 MST  
**SUBJECT:** Redis Connection Confirmation and Setup Instructions  
**PRIORITY:** High  
**CLASSIFICATION:** Internal Only

---

## Redis Cluster Status and Connection Details

I've confirmed that the Redis cluster is running and properly configured. I've also set up the necessary ACL permissions for the MCP-Dev-ethos-server to connect to the Redis cluster.

### Redis Cluster Status

The Redis cluster is running on the following nodes:
- Node 1: 127.0.0.1:7000
- Node 2: 127.0.0.1:7001
- Node 3: 127.0.0.1:7002

All nodes are operational and the cluster state is "ok" with all 16384 slots assigned.

### Authentication Credentials

I've created a dedicated user for the MCP-Dev-ethos-server with the following credentials:
- Username: `mcp-dev-ethos`
- Password: `ethos-d5d7817937232ca5`

### Access Permissions

The `mcp-dev-ethos` user has been configured with the following permissions:
- **Read/Write access** to the `ethos:*` namespace
- **Read-only access** to the `shared:*` namespace
- No access to other namespaces

This configuration ensures that the MCP-Dev-ethos-server can store and retrieve its own data while also accessing shared configuration data, but cannot modify shared data or access data from other services.

### Connection Configuration

To connect to the Redis cluster from the MCP-Dev-ethos-server, use the following configuration:

```javascript
const Redis = require('ioredis');

const cluster = new Redis.Cluster([
  { host: '127.0.0.1', port: 7000 },
  { host: '127.0.0.1', port: 7001 },
  { host: '127.0.0.1', port: 7002 }
], {
  redisOptions: {
    username: 'mcp-dev-ethos',
    password: 'ethos-d5d7817937232ca5'
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

1. **Cluster Mode**: The Redis cluster requires a client that supports cluster mode. We recommend using the `ioredis` library for Node.js applications.

2. **Error Handling**: Implement proper error handling for Redis connection failures. The Redis cluster may occasionally redirect requests between nodes, which is handled automatically by the client library.

3. **Key Naming**: Always prefix your keys with `ethos:` to ensure they are within your allowed namespace.

4. **Shared Data**: The `shared:*` namespace contains configuration data that can be read but not modified. This includes:
   - `shared:config:version`: API version
   - `shared:config:environment`: Environment (development, staging, production)
   - `shared:config:api_endpoint`: API endpoint URL

## Setup Script

I've created a setup script that configures the Redis cluster for the MCP-Dev-ethos-server. This script is available at:

```
/data-nova/ax/InfraOps/MemOps/Echo/setup_mcp_dev_ethos_redis.sh
```

You can run this script to:
- Create the `mcp-dev-ethos` user with the appropriate permissions
- Test the connection and permissions
- Create sample shared configuration data

## Next Steps

1. **Test Connection**: Test the connection from the MCP-Dev-ethos-server using the provided configuration.
2. **Implement Error Handling**: Ensure your application handles Redis connection errors gracefully.
3. **Monitor Usage**: Monitor Redis usage to ensure optimal performance.
4. **Feedback**: Provide feedback on any issues or improvements needed.

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