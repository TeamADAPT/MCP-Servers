import { createCluster } from 'redis';

// Get Redis configuration from environment variables
const redisHost = process.env.REDIS_HOST || '127.0.0.1';
const redisPort = process.env.REDIS_PORT || '7000';
const redisPassword = process.env.REDIS_PASSWORD || 'd5d7817937232ca5';
const redisUser = process.env.REDIS_USER || 'genesis';
const redisClusterNodes = process.env.REDIS_CLUSTER_NODES || '127.0.0.1:7000,127.0.0.1:7001,127.0.0.1:7002';

// Parse cluster nodes
const nodes = redisClusterNodes.split(',').map(node => {
  const [host, port] = node.split(':');
  return {
    url: `redis://default:${redisPassword}@${host}:${port}`
  };
});

// Create a Redis cluster client
const createRedisClient = async () => {
  try {
    console.log('Creating Redis cluster client with nodes:', JSON.stringify(nodes, null, 2));
    
    const redis = createCluster({
      rootNodes: nodes,
      defaults: {
        socket: {
          reconnectStrategy: (retries) => Math.min(retries * 50, 1000)
        }
      }
    });
    
    // Connect to the Redis cluster
    await redis.connect();
    console.log('Connected to Redis cluster successfully');
    
    return redis;
  } catch (error) {
    console.error('Error creating Redis cluster client:', error);
    throw error;
  }
};
export { createRedisClient };
