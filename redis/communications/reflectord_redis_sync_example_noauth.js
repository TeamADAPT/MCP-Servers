/**
 * ReflectorD Redis Cluster Synchronization Example (No Authentication for Local Cluster)
 * 
 * This script demonstrates how to connect to both Redis clusters and synchronize data between them.
 * The main cluster uses authentication, but the local cluster has authentication disabled.
 * 
 * Usage:
 * 1. Install dependencies: npm install ioredis
 * 2. Update the configuration for your local Redis cluster
 * 3. Run the script: node reflectord_redis_sync_example_noauth.js
 */

// Import ioredis
const Redis = require('ioredis');

// Configuration for the main Redis cluster (with authentication)
const mainClusterConfig = {
  nodes: [
    { host: 'redis-cluster-01.memcommsops.internal', port: 7000 },
    { host: 'redis-cluster-02.memcommsops.internal', port: 7001 },
    { host: 'redis-cluster-03.memcommsops.internal', port: 7002 }
  ],
  options: {
    redisOptions: {
      username: 'reflectord-daemon-readwrite',
      password: 'reflectord-daemon-readwrite-fc33218582110b27',
      connectTimeout: 5000,
      maxRetriesPerRequest: 3
    },
    scaleReads: 'slave',
    maxRedirections: 16,
    retryDelayOnFailover: 300,
    enableAutoPipelining: true
  }
};

// Configuration for the local Redis cluster (without authentication)
// Update these values to match your local Redis cluster
const localClusterConfig = {
  nodes: [
    { host: 'localhost', port: 6379 },  // Update with your local Redis cluster nodes
    { host: 'localhost', port: 6380 },
    { host: 'localhost', port: 6381 }
  ],
  options: {
    // No authentication parameters needed
    scaleReads: 'slave',
    maxRedirections: 16,
    retryDelayOnFailover: 300,
    enableAutoPipelining: true
  }
};

// Create Redis cluster clients
const mainCluster = new Redis.Cluster(mainClusterConfig.nodes, mainClusterConfig.options);
const localCluster = new Redis.Cluster(localClusterConfig.nodes, localClusterConfig.options);

// Set up event handlers for main cluster
mainCluster.on('connect', () => {
  console.log('Connected to main Redis cluster');
});

mainCluster.on('error', (err) => {
  console.error('Main Redis cluster error:', err);
});

// Set up event handlers for local cluster
localCluster.on('connect', () => {
  console.log('Connected to local Redis cluster');
});

localCluster.on('error', (err) => {
  console.error('Local Redis cluster error:', err);
});

// Namespace prefixes
const REFLECTORD_PREFIX = 'reflectord:';
const SHARED_PREFIX = 'shared:';

/**
 * Synchronize data from the main cluster to the local cluster
 * @param {string} keyPattern - The key pattern to synchronize (e.g., 'shared:config:*')
 * @returns {Promise<void>}
 */
async function syncFromMainToLocal(keyPattern) {
  try {
    console.log(`Synchronizing ${keyPattern} from main to local cluster...`);
    
    // Get all keys matching the pattern from the main cluster
    const keys = await scanKeys(mainCluster, keyPattern);
    console.log(`Found ${keys.length} keys matching ${keyPattern}`);
    
    if (keys.length === 0) {
      return;
    }
    
    // Get values for all keys
    const pipeline = mainCluster.pipeline();
    keys.forEach(key => {
      pipeline.get(key);
    });
    
    const values = await pipeline.exec();
    
    // Set values in the local cluster
    const localPipeline = localCluster.pipeline();
    keys.forEach((key, index) => {
      const [err, value] = values[index];
      if (!err && value !== null) {
        localPipeline.set(key, value);
        console.log(`Syncing ${key} = ${value}`);
      }
    });
    
    await localPipeline.exec();
    console.log(`Successfully synchronized ${keys.length} keys from main to local cluster`);
  } catch (err) {
    console.error('Error synchronizing from main to local cluster:', err);
  }
}

/**
 * Synchronize data from the local cluster to the main cluster
 * @param {string} keyPattern - The key pattern to synchronize (e.g., 'reflectord:data:*')
 * @returns {Promise<void>}
 */
async function syncFromLocalToMain(keyPattern) {
  try {
    console.log(`Synchronizing ${keyPattern} from local to main cluster...`);
    
    // Get all keys matching the pattern from the local cluster
    const keys = await scanKeys(localCluster, keyPattern);
    console.log(`Found ${keys.length} keys matching ${keyPattern}`);
    
    if (keys.length === 0) {
      return;
    }
    
    // Get values for all keys
    const pipeline = localCluster.pipeline();
    keys.forEach(key => {
      pipeline.get(key);
    });
    
    const values = await pipeline.exec();
    
    // Set values in the main cluster
    const mainPipeline = mainCluster.pipeline();
    keys.forEach((key, index) => {
      const [err, value] = values[index];
      if (!err && value !== null) {
        mainPipeline.set(key, value);
        console.log(`Syncing ${key} = ${value}`);
      }
    });
    
    await mainPipeline.exec();
    console.log(`Successfully synchronized ${keys.length} keys from local to main cluster`);
  } catch (err) {
    console.error('Error synchronizing from local to main cluster:', err);
  }
}

/**
 * Scan for keys matching a pattern
 * @param {Redis.Cluster} cluster - The Redis cluster client
 * @param {string} pattern - The key pattern to scan for
 * @returns {Promise<string[]>} - Array of keys matching the pattern
 */
async function scanKeys(cluster, pattern) {
  const keys = [];
  let cursor = '0';
  
  do {
    const result = await cluster.scan(cursor, 'MATCH', pattern, 'COUNT', 100);
    cursor = result[0];
    keys.push(...result[1]);
  } while (cursor !== '0');
  
  return keys;
}

/**
 * Set up real-time synchronization using keyspace notifications
 * Note: This requires Redis to have keyspace notifications enabled
 * @returns {Promise<void>}
 */
async function setupRealtimeSync() {
  try {
    // Create separate connections for keyspace notifications
    const mainSubscriber = new Redis(mainClusterConfig.nodes[0].port, mainClusterConfig.nodes[0].host, {
      ...mainClusterConfig.options.redisOptions
    });
    
    const localSubscriber = new Redis(localClusterConfig.nodes[0].port, localClusterConfig.nodes[0].host);
    
    // Enable keyspace notifications if not already enabled
    await mainSubscriber.config('SET', 'notify-keyspace-events', 'KEA');
    await localSubscriber.config('SET', 'notify-keyspace-events', 'KEA');
    
    // Subscribe to keyspace events for reflectord namespace in local cluster
    localSubscriber.psubscribe('__keyspace@*__:reflectord:*');
    
    // Subscribe to keyspace events for shared namespace in main cluster
    mainSubscriber.psubscribe('__keyspace@*__:shared:*');
    
    // Handle events from local cluster
    localSubscriber.on('pmessage', async (pattern, channel, message) => {
      const key = channel.split(':').slice(1).join(':');
      if (key.startsWith(REFLECTORD_PREFIX) && (message === 'set' || message === 'del')) {
        console.log(`Local cluster event: ${message} ${key}`);
        
        if (message === 'set') {
          const value = await localCluster.get(key);
          await mainCluster.set(key, value);
          console.log(`Real-time sync: ${key} = ${value} (local -> main)`);
        } else if (message === 'del') {
          await mainCluster.del(key);
          console.log(`Real-time sync: deleted ${key} (local -> main)`);
        }
      }
    });
    
    // Handle events from main cluster
    mainSubscriber.on('pmessage', async (pattern, channel, message) => {
      const key = channel.split(':').slice(1).join(':');
      if (key.startsWith(SHARED_PREFIX) && (message === 'set' || message === 'del')) {
        console.log(`Main cluster event: ${message} ${key}`);
        
        if (message === 'set') {
          const value = await mainCluster.get(key);
          await localCluster.set(key, value);
          console.log(`Real-time sync: ${key} = ${value} (main -> local)`);
        } else if (message === 'del') {
          await localCluster.del(key);
          console.log(`Real-time sync: deleted ${key} (main -> local)`);
        }
      }
    });
    
    console.log('Real-time synchronization set up successfully');
  } catch (err) {
    console.error('Error setting up real-time synchronization:', err);
  }
}

/**
 * Run a demo of the synchronization
 */
async function runDemo() {
  try {
    console.log('\n--- Redis Cluster Synchronization Demo (No Auth for Local) ---\n');
    
    // Initial synchronization
    await syncFromMainToLocal(`${SHARED_PREFIX}*`);
    await syncFromLocalToMain(`${REFLECTORD_PREFIX}*`);
    
    // Set up real-time synchronization
    await setupRealtimeSync();
    
    // Demo: Write to main cluster and verify it's synchronized to local
    console.log('\nDemo: Writing to main cluster...');
    const mainKey = `${SHARED_PREFIX}demo:${Date.now()}`;
    const mainValue = `Main cluster demo value at ${new Date().toISOString()}`;
    await mainCluster.set(mainKey, mainValue);
    console.log(`Main cluster: ${mainKey} = ${mainValue}`);
    
    // Wait a moment for synchronization
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Verify the value was synchronized to local
    const localValue = await localCluster.get(mainKey);
    console.log(`Local cluster: ${mainKey} = ${localValue}`);
    
    // Demo: Write to local cluster and verify it's synchronized to main
    console.log('\nDemo: Writing to local cluster...');
    const localKey = `${REFLECTORD_PREFIX}demo:${Date.now()}`;
    const localDemoValue = `Local cluster demo value at ${new Date().toISOString()}`;
    await localCluster.set(localKey, localDemoValue);
    console.log(`Local cluster: ${localKey} = ${localDemoValue}`);
    
    // Wait a moment for synchronization
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Verify the value was synchronized to main
    const mainDemoValue = await mainCluster.get(localKey);
    console.log(`Main cluster: ${localKey} = ${mainDemoValue}`);
    
    console.log('\nDemo complete! Press Ctrl+C to exit.');
  } catch (err) {
    console.error('Error running demo:', err);
  }
}

// Run the demo
runDemo();

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('\nShutting down...');
  await mainCluster.quit();
  await localCluster.quit();
  console.log('Disconnected from Redis clusters');
  process.exit(0);
});
