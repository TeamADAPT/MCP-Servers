# Redis Default Ports Blocking

**Date:** 2025-05-09  
**Author:** Keystone (CommsOps)  
**Priority:** HIGH

## Overview

This document explains the measures implemented to block access to the default Redis ports (6379 and 6380) and redirect users to the Redis Cluster ports (7000-7002).

## Background

Redis servers traditionally use port 6379 by default. In our environment, we have:
- Port 6379 reserved as the "Default Redis Port"
- Port 6380 used for "Current Production Redis"
- Ports 7000-7002 designated for the Redis Cluster that all users should connect to

To prevent confusion and ensure users connect to the correct Redis Cluster ports, we have implemented measures to block access to ports 6379 and 6380.

## Implemented Measures

### 1. Firewall Rules

Iptables rules have been implemented to block external connections to ports 6379 and 6380, while still allowing localhost connections for system services:

```bash
# Allow localhost connections to port 6379
sudo iptables -A INPUT -p tcp --dport 6379 -s 127.0.0.1 -j ACCEPT

# Block all other connections to port 6379
sudo iptables -A INPUT -p tcp --dport 6379 -j DROP

# Allow localhost connections to port 6380
sudo iptables -A INPUT -p tcp --dport 6380 -s 127.0.0.1 -j ACCEPT

# Block all other connections to port 6380
sudo iptables -A INPUT -p tcp --dport 6380 -j DROP
```

These rules are made persistent through the `redis-ports-block.service` systemd service.

### 2. Notice Mechanism

A notice mechanism has been implemented to inform users who attempt to connect to the blocked ports. The `redis-port-notice.service` runs a Python script that:

1. Listens on port 6379 (and attempts to listen on 6380 if not already in use)
2. Sends a notice to users who try to connect, informing them to use the Redis Cluster ports instead
3. Logs connection attempts for monitoring purposes

The notice message includes:
- Information about why the port is blocked
- Instructions on which ports to use instead (7000-7002)
- References to documentation for more information
- Contact information for assistance

### 3. Documentation Updates

The following documentation has been updated to include warnings about not using the default Redis ports:

- `docs/redis/REDIS_PORT_RESERVATIONS.md`
- `docs/redis/redis-streams/redis_cluster_guide.md`

## Testing the Blocking Measures

You can test the blocking measures by attempting to connect to ports 6379 and 6380:

```bash
# This will be blocked and show a notice
redis-cli -p 6379

# This will be blocked by the firewall
redis-cli -p 6380
```

## Correct Connection Method

Always use the Redis Cluster ports (7000-7002) for your Redis connections:

```bash
# Connect to Redis Cluster
redis-cli -c -p 7000 -a your_password
```

For more information on connecting to the Redis Cluster, see `docs/redis/redis-streams/redis_cluster_guide.md`.

## Monitoring and Maintenance

### Logs

Connection attempts to blocked ports are logged in:
- `/var/log/redis_port_notice.log`

### Services

The following systemd services manage the blocking measures:
- `redis-ports-block.service`: Manages the iptables rules
- `redis-port-notice.service`: Manages the notice mechanism

To check the status of these services:

```bash
sudo systemctl status redis-ports-block.service
sudo systemctl status redis-port-notice.service
```

## Troubleshooting

If you encounter issues with the blocking measures:

1. Check if the services are running:
   ```bash
   sudo systemctl status redis-ports-block.service
   sudo systemctl status redis-port-notice.service
   ```

2. Check the iptables rules:
   ```bash
   sudo iptables -L INPUT -n | grep -E '6379|6380'
   ```

3. Check the logs:
   ```bash
   sudo tail -f /var/log/redis_port_notice.log
   ```

## Contact

For assistance with Redis connection issues, please contact:
- CommsOps Team: commsops@nova.ai

---

Last Updated: 2025-05-09