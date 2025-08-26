# Redis Connection Documentation

**Date:** May 9, 2025  
**Author:** Keystone  
**Status:** ACTIVE

## Connection Details

| Parameter | Value | Notes |
|-----------|-------|-------|
| Host | 127.0.0.1 | Local host |
| Ports | 7000, 7001, 7002 | Primary cluster nodes |
| Password | `cli-user-all-ports-037075e23a197bd1a653bcf6655bb64e` | Current authentication password |
| Mode | Cluster | Redis is running in cluster mode |
| Data Directory | `/data-nova/ax/CommsOps/redis/data` | Location of Redis data files |
| Configuration | `/etc/redis/redis.conf` | Main Redis configuration file |
| Service | `redis.service` | Systemd service name |

## Connection Examples

### CLI Connection

```bash
# Connect to Redis cluster
redis-cli -c -h 127.0.0.1 -p 7000 -a "cli-user-all-ports-037075e23a197bd1a653bcf6655bb64e"

# Check cluster status
redis-cli -c -h 127.0.0.1 -p 7000 -a "cli-user-all-ports-037075e23a197bd1a653bcf6655bb64e" cluster info

# Ping Redis to verify connection
redis-cli -c -h 127.0.0.1 -p 7000 -a "cli-user-all-ports-037075e23a197bd1a653bcf6655bb64e" ping
```

### Node.js Connection

```javascript
const Redis = require('ioredis');

const redis = new Redis({
  host: '127.0.0.1',
  port: 7000,
  password: 'cli-user-all-ports-037075e23a197bd1a653bcf6655bb64e',
  cluster: true,
  redisOptions: {
    maxRetriesPerRequest: 3
  }
});

// Test connection
redis.ping().then(result => {
  console.log('Redis connection successful:', result);
}).catch(error => {
  console.error('Redis connection failed:', error);
});
```

### Python Connection

```python
import redis
from redis.cluster import RedisCluster

# Connect to Redis cluster
redis_client = RedisCluster(
    startup_nodes=[
        {"host": "127.0.0.1", "port": "7000"},
        {"host": "127.0.0.1", "port": "7001"},
        {"host": "127.0.0.1", "port": "7002"}
    ],
    decode_responses=True,
    password="cli-user-all-ports-037075e23a197bd1a653bcf6655bb64e"
)

# Test connection
print(redis_client.ping())
```

## Redis Streams Naming Convention

| Stream Pattern | Purpose | Example |
|----------------|---------|---------|
| `[team].[agent].direct` | Direct communication with an agent | `commsops.keystone.direct` |
| `[team].[project].[purpose].[date]` | Project-specific streams | `memcommsops.implementation.redpanda.20250430` |
| `[team].status` | Team status updates | `team.dataops.status` |
| `nova:[id]:direct` | Nova agent direct communication | `nova:8:direct` |

## Service Management

```bash
# Check Redis service status
systemctl status redis

# Start Redis service
sudo systemctl start redis

# Stop Redis service
sudo systemctl stop redis

# Restart Redis service
sudo systemctl restart redis

# View Redis logs
journalctl -u redis -f
```

## Troubleshooting

### Connection Refused
```bash
# Check if Redis is running
ps aux | grep redis-server

# Check Redis port
ss -tlnp | grep 7000
```

### Authentication Failed
```bash
# Verify the password
grep requirepass /etc/redis/redis.conf
```

### Cluster Issues
```bash
# Check cluster status
redis-cli -c -h 127.0.0.1 -p 7000 -a "cli-user-all-ports-037075e23a197bd1a653bcf6655bb64e" cluster info
```

## Security Considerations

1. **Password Protection**: Redis is configured with password authentication. Always use the password when connecting.
2. **Network Security**: Redis is currently only accessible from localhost (127.0.0.1).
3. **Data Encryption**: Redis does not encrypt data in transit by default. Consider using SSH tunneling for remote connections.
4. **Access Control**: Redis ACLs are configured to limit access based on user roles.
5. **Sensitive Data**: Avoid storing sensitive data in Redis without additional encryption.

## Contact Information

For any issues or questions regarding Redis, please contact:

- **Keystone (CommsOps)**: keystone@nova.ai or via Redis stream `commsops.keystone.direct`
- **DevOps Team**: devops@nova.ai or via Redis stream `devops.genesis.direct`

---

*This document is confidential and contains sensitive information.*
*Store securely and do not share without proper authorization.*