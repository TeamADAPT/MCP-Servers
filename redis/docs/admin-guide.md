# Redis MCP Server Administrator Guide

## Overview
The Redis MCP Server provides a robust interface for Redis operations through the Model Context Protocol (MCP). This guide covers installation, configuration, maintenance, and troubleshooting for system administrators.

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Cluster Management](#cluster-management)
- [Monitoring](#monitoring)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## Installation

### Prerequisites
- Node.js v18 or higher
- Redis Cluster (version 6.0 or higher)
- Systemd-based Linux system

### Installation Steps
1. Clone the repository
2. Install dependencies:
   ```bash
   npm ci --production
   ```
3. Build the project:
   ```bash
   npm run build
   ```
4. Install the service:
   ```bash
   sudo ./install-service.sh
   ```

### Service Configuration
The service is configured through `/etc/systemd/system/redis-mcp.service` with the following key settings:
- Resource limits (memory, file descriptors)
- Restart policies
- Security constraints
- Logging configuration

## Configuration

### Cluster Configuration
Located in `src/config/cluster.ts`, the cluster configuration includes:
- Node definitions
- Connection retry strategies
- Failover settings
- Performance tuning parameters

Key configuration options:
```typescript
{
    scaleReads: 'slave',              // Read scaling strategy
    maxRedirections: 16,              // Max redirections for cluster operations
    retryDelayOnFailover: 2000,       // Retry delay on node failover (ms)
    slotsRefreshTimeout: 10000,       // Slots refresh timeout (ms)
    slotsRefreshInterval: 5000        // Slots refresh interval (ms)
}
```

### Environment Variables
- `REDIS_URL`: Redis cluster connection URL
- `NODE_ENV`: Environment mode (production/development)
- `DEBUG`: Debug logging settings

## Cluster Management

### Node Management
Monitor and manage cluster nodes:
```bash
# Check node status
redis-cli -h 127.0.0.1 -p 7000 cluster nodes

# Check cluster info
redis-cli -h 127.0.0.1 -p 7000 cluster info
```

### Failover Handling
The server implements automatic failover handling with:
- Exponential backoff with jitter
- READONLY error detection and handling
- Automatic slot refresh
- Command queue management

## Monitoring

### Logging
Logs are available through journald:
```bash
# View service logs
journalctl -u redis-mcp -f

# View error logs
journalctl -u redis-mcp -p err
```

### Metrics
Key metrics to monitor:
- Connection status
- Command latency
- Error rates
- Memory usage
- Stream operations

### Health Checks
Perform health checks:
```bash
# Check service status
systemctl status redis-mcp

# Check Redis connection
redis-cli -h 127.0.0.1 -p 7000 ping
```

## Security

### Authentication
- Password authentication required for Redis connections
- TLS support for encrypted communications
- Service runs with limited privileges

### System Hardening
The service includes several security measures:
- NoNewPrivileges=true
- ProtectSystem=full
- ProtectHome=true
- PrivateTmp=true
- RestrictNamespaces=true

### Access Control
- Redis ACL configuration
- Network access restrictions
- Command restrictions

## Troubleshooting

### Common Issues

1. Connection Failures
```
Problem: Connection to Redis cluster fails
Solution: 
- Check Redis cluster status
- Verify network connectivity
- Check authentication credentials
```

2. Performance Issues
```
Problem: High latency or slow operations
Solution:
- Check network latency
- Monitor Redis memory usage
- Review command patterns
```

3. Service Failures
```
Problem: Service fails to start
Solution:
- Check service logs
- Verify Redis cluster availability
- Check configuration settings
```

### Debug Mode
Enable debug logging:
```bash
# Edit service configuration
sudo systemctl edit redis-mcp

# Add environment variable
[Service]
Environment=DEBUG=redis*
```

## Maintenance

### Backup Procedures
1. Stream Data Backup
```bash
# Export stream data
redis-cli -h 127.0.0.1 -p 7000 --csv XRANGE mystream - +
```

2. Configuration Backup
```bash
# Backup service configuration
sudo cp /etc/systemd/system/redis-mcp.service /etc/systemd/system/redis-mcp.service.bak
```

### Updates
1. Update Service
```bash
# Stop service
sudo systemctl stop redis-mcp

# Update code and rebuild
git pull
npm ci
npm run build

# Start service
sudo systemctl start redis-mcp
```

2. Update Configuration
```bash
# Edit configuration
sudo systemctl edit redis-mcp

# Reload configuration
sudo systemctl daemon-reload
```

### Recovery Procedures
1. Service Recovery
```bash
# Check service status
systemctl status redis-mcp

# View recent logs
journalctl -u redis-mcp -n 100

# Restart service
sudo systemctl restart redis-mcp
```

2. Data Recovery
```bash
# Check stream integrity
redis-cli -h 127.0.0.1 -p 7000 XINFO STREAM mystream

# Recover from backup if needed
redis-cli -h 127.0.0.1 -p 7000 XADD mystream LOAD backup.csv
