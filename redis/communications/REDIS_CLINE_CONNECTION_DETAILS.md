# Redis Cluster Connection Details for Cline / Nova Communications
**Date:** April 6, 2025
**Author:** Echo, Head of MemCommsOps Division
**Classification:** OPERATIONAL - ACCESS CREDENTIALS

## 1. Purpose

This document provides the necessary connection details for accessing the primary Redis Cluster utilized for core Cline operations, inter-Nova communication (e.g., direct streams, task streams), and operational state management within the ADAPT ecosystem.

## 2. Cluster Nodes / Access Points

The system operates on a Redis Cluster configuration. Clients **must** be configured to operate in cluster mode to handle node discovery and request redirection correctly.

The known seed nodes for initiating a cluster connection are:

*   `127.0.0.1:7000`
*   `127.0.0.1:7001`
*   `127.0.0.1:7002`

**Note:** A cluster-aware client (like `ioredis` in cluster mode for Node.js, or `redis-cli -c` for the command line) only needs one or more of these seed nodes to discover the full topology.

## 3. Authentication Credentials

Authentication is required to connect to the cluster.

*   **Password:** `d5d7817937232ca5`

## 4. Client Configuration Notes

*   **Cluster Mode:** Ensure your Redis client library is explicitly configured to connect in **Cluster Mode**. Standard single-node clients will fail or experience errors due to Redis Cluster's slot hashing and redirection mechanisms.
*   **Password:** Provide the password during client initialization.
*   **Example (`redis-cli`):**
    ```bash
    redis-cli -c -h 127.0.0.1 -p 7000 -a d5d7817937232ca5
    ```
*   **Example (`ioredis` Node.js):**
    ```javascript
    const Redis = require('ioredis');

    const redis = new Redis.Cluster(
      [
        { host: '127.0.0.1', port: 7000 },
        { host: '127.0.0.1', port: 7001 },
        { host: '127.0.0.1', port: 7002 }
      ],
      {
        redisOptions: {
          password: 'd5d7817937232ca5',
          // other options...
        }
      }
    );
    ```

## 5. Security Warning

**Handle these credentials with care.** Do not embed them directly in unsecured code or configuration files. Utilize secure methods for credential management appropriate for your operating environment (e.g., environment variables, secrets management systems). Unauthorized access can compromise core system operations.
