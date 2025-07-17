# Adapt MCP-Dev Redis Configuration

This directory contains the Redis configuration for the MCP-Dev Service on Adapt. This README provides instructions on how to use the Redis configuration.

## Overview

The Redis cluster is configured with DNS names for improved maintainability, scalability, and flexibility. The MCP-Dev Service on Adapt has been granted specific permissions:

- **Read/Write access** to the `adapt:*` namespace
- **Read-only access** to the `shared:*` namespace
- No access to other namespaces

## Authentication Credentials

The MCP-Dev Service on Adapt uses the following credentials:

- **Username:** `adapt-mcp-readwrite`
- **Password:** `adapt-mcp-readwrite-acc9582bc2eaead3`

These credentials follow our standardized naming convention: `[server]-[service]-[role]` for usernames and `[server]-[service]-[role]-[random]` for passwords.

## DNS Configuration

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

## Files

- **Environment File:** `./.env.adapt-mcp-dev`
- **Example Application:** `./adapt_mcp_dev_redis_example.js`
- **Package Configuration:** `./package.json`
- **Documentation:** `./communications/[20250412_0527_MemCommsOps_MCP_DevOps]_Adapt_MCP_Redis_Configuration.md`

## Getting Started

### Prerequisites

- Node.js 14.0.0 or higher
- npm or yarn
- Redis CLI (for testing)

### Installation

1. Install dependencies:

```bash
npm install
```

2. Add DNS entries to your `/etc/hosts` file (see DNS Configuration section)

### Running the Example

Run the example application to see how to connect to Redis from a Node.js application:

```bash
npm start
```

or

```bash
node adapt_mcp_dev_redis_example.js
```

## Connection Example

```javascript
const Redis = require('ioredis');

// Parse Redis cluster nodes from environment variable
const nodes = process.env.REDIS_CLUSTER_NODES.split(',').map(node => {
  const [host, port] = node.split(':');
  return { host, port: parseInt(port, 10) };
});

// Create Redis cluster client
const cluster = new Redis.Cluster(nodes, {
  redisOptions: {
    username: process.env.REDIS_USERNAME,
    password: process.env.REDIS_PASSWORD,
    connectTimeout: parseInt(process.env.REDIS_CONNECT_TIMEOUT, 10),
    maxRetriesPerRequest: parseInt(process.env.REDIS_MAX_RETRIES, 10)
  },
  scaleReads: process.env.REDIS_SCALE_READS,
  maxRedirections: parseInt(process.env.REDIS_MAX_REDIRECTIONS, 10),
  retryDelayOnFailover: parseInt(process.env.REDIS_RETRY_DELAY, 10),
  enableAutoPipelining: true
});

// Example: Write to adapt namespace
cluster.set('adapt:example', 'value').then(console.log);

// Example: Read from shared namespace
cluster.get('shared:config:version').then(console.log);
```

## Best Practices

1. **Key Naming:** Always prefix your keys with `adapt:` to ensure they are within your allowed namespace.

2. **Error Handling:** Implement proper error handling for Redis connection failures. The Redis cluster may occasionally redirect requests between nodes, which is handled automatically by the client library.

3. **Connection Pooling:** The ioredis library handles connection pooling automatically. You should create a single cluster instance and reuse it throughout your application.

4. **Monitoring:** Enable monitoring to track Redis usage and performance. The environment file includes monitoring configuration options.

5. **Logging:** Configure appropriate logging levels for Redis operations. The environment file includes logging configuration options.

## Support

If you encounter any issues with the Redis connection, please contact:

- Echo, Head of MemCommsOps Division