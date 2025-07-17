#!/bin/bash

# Script to disable authentication on local Redis server for development only
# WARNING: This should NEVER be used in production environments!

echo "WARNING: This script disables Redis authentication for LOCAL DEVELOPMENT ONLY."
echo "This is NOT suitable for production environments and could lead to security vulnerabilities."
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [[ "$confirm" != "yes" ]]; then
    echo "Operation cancelled."
    exit 1
fi

# Redis nodes to configure - default is localhost:6380 (custom port)
REDIS_NODES=("localhost:6380")

echo ""
echo "Will disable authentication on the following Redis nodes:"
for node in "${REDIS_NODES[@]}"; do
    echo "- $node"
done

echo ""
read -p "Continue with these nodes? (yes/no): " confirm_nodes

if [[ "$confirm_nodes" != "yes" ]]; then
    echo "Operation cancelled. Edit the script to update the Redis node addresses."
    exit 1
fi

# Process each Redis node
for node in "${REDIS_NODES[@]}"; do
    IFS=':' read -r host port <<< "$node"
    
    echo ""
    echo "Configuring Redis node at $host:$port..."
    
    # Disable protected mode
    echo "Disabling protected mode..."
    redis-cli -h "$host" -p "$port" CONFIG SET protected-mode no
    
    # Disable authentication
    echo "Removing password authentication..."
    redis-cli -h "$host" -p "$port" CONFIG SET requirepass ""
    
    # Reset default user to allow all commands without password
    echo "Resetting default user permissions..."
    redis-cli -h "$host" -p "$port" ACL SETUSER default on nopass ~* +@all
    
    # Save configuration
    echo "Saving configuration..."
    redis-cli -h "$host" -p "$port" CONFIG REWRITE
    redis-cli -h "$host" -p "$port" SAVE
    
    echo "Configuration of $host:$port completed successfully."
done

echo ""
echo "Authentication has been disabled on all specified Redis nodes."
echo "Remember to re-enable authentication before using in any production environment!"
echo ""
echo "To update your connection code, remove authentication parameters:"
echo ""
echo "const redis = new Redis({
  host: 'localhost',
  port: 6379
  // No password or authentication needed
});"
