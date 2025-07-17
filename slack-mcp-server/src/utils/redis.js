/**
 * Redis utility for Slack MCP server
 * Handles connections to Redis streams for inter-system communication
 */

const Redis = require('ioredis');
const config = require('../config/env');
const logger = require('./logger');

// Redis client instances
let redisClient = null;
let redisSubscriber = null;

/**
 * Initialize Redis clients
 * @returns {Promise<void>}
 */
async function initRedisClients() {
  try {
    // Use cluster mode configuration from Echo's document
    if (config.redis.cluster && config.redis.cluster.enableClusterMode) {
      logger.info('Initializing Redis in cluster mode');
      redisClient = new Redis.Cluster(config.redis.cluster.nodes, {
        redisOptions: {
          password: config.redis.cluster.password,
        },
        scaleReads: 'all', // Read from all replicas
        clusterRetryStrategy: (times) => {
          return Math.min(times * 200, 2000); // Exponential backoff
        }
      });

      // Create a separate subscriber client for PubSub
      redisSubscriber = new Redis.Cluster(config.redis.cluster.nodes, {
        redisOptions: {
          password: config.redis.cluster.password,
        },
        scaleReads: 'all',
        clusterRetryStrategy: (times) => {
          return Math.min(times * 200, 2000);
        }
      });
    } 
    // Fallback to single Redis instance using URL from config
    else if (config.redis.url) {
      logger.info('Initializing Redis with URL connection');
      redisClient = new Redis(config.redis.url);
      redisSubscriber = new Redis(config.redis.url);
    } 
    // Cannot connect to Redis
    else {
      throw new Error('Redis configuration is missing. Please check your environment variables.');
    }

    // Set up error handling
    redisClient.on('error', (err) => {
      logger.error(`Redis client error: ${err.message}`, { stack: err.stack });
    });

    redisSubscriber.on('error', (err) => {
      logger.error(`Redis subscriber error: ${err.message}`, { stack: err.stack });
    });

    logger.info('Redis clients initialized successfully');
  } catch (err) {
    logger.error(`Failed to initialize Redis clients: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

/**
 * Get the Redis client instance
 * @returns {Redis} Redis client
 */
function getRedisClient() {
  if (!redisClient) {
    throw new Error('Redis client not initialized. Call initRedisClients() first.');
  }
  return redisClient;
}

/**
 * Get the Redis subscriber instance
 * @returns {Redis} Redis subscriber client
 */
function getRedisSubscriber() {
  if (!redisSubscriber) {
    throw new Error('Redis subscriber not initialized. Call initRedisClients() first.');
  }
  return redisSubscriber;
}

/**
 * Add a message to a Redis stream
 * @param {string} streamKey - The stream key
 * @param {Object} fields - Message fields
 * @returns {Promise<string>} Message ID
 */
async function addToStream(streamKey, fields) {
  try {
    if (!redisClient) {
      await initRedisClients();
    }
    
    // Add entry to stream with automatic ID generation
    const messageId = await redisClient.xadd(
      streamKey,
      '*',  // Auto-generate message ID
      ...Object.entries(fields).flat()
    );
    
    logger.debug(`Added message to stream ${streamKey}`, { messageId, fields });
    return messageId;
  } catch (err) {
    logger.error(`Failed to add message to stream ${streamKey}: ${err.message}`, { stack: err.stack, fields });
    throw err;
  }
}

/**
 * Read messages from a Redis stream
 * @param {string} streamKey - The stream key
 * @param {string} startId - ID to start reading from (default: '0')
 * @param {number} count - Max number of messages to read (default: 10)
 * @returns {Promise<Array>} Array of messages
 */
async function readFromStream(streamKey, startId = '0', count = 10) {
  try {
    if (!redisClient) {
      await initRedisClients();
    }
    
    const messages = await redisClient.xread('COUNT', count, 'STREAMS', streamKey, startId);
    
    if (!messages || messages.length === 0) {
      return [];
    }
    
    // Format the messages for easier consumption
    const formattedMessages = messages[0][1].map(msg => {
      const [id, fields] = msg;
      const formattedFields = {};
      
      // Convert array of field-value pairs to object
      for (let i = 0; i < fields.length; i += 2) {
        formattedFields[fields[i]] = fields[i + 1];
      }
      
      return {
        id,
        fields: formattedFields
      };
    });
    
    logger.debug(`Read ${formattedMessages.length} messages from stream ${streamKey}`);
    return formattedMessages;
  } catch (err) {
    logger.error(`Failed to read from stream ${streamKey}: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

/**
 * Create a consumer group for a stream
 * @param {string} streamKey - The stream key
 * @param {string} groupName - Consumer group name
 * @param {string} startId - ID to start from (default: '0')
 * @returns {Promise<boolean>} Success status
 */
async function createConsumerGroup(streamKey, groupName, startId = '0') {
  try {
    if (!redisClient) {
      await initRedisClients();
    }
    
    await redisClient.xgroup('CREATE', streamKey, groupName, startId, 'MKSTREAM');
    logger.info(`Created consumer group ${groupName} for stream ${streamKey}`);
    return true;
  } catch (err) {
    // Group already exists, this is fine
    if (err.message.includes('BUSYGROUP')) {
      logger.debug(`Consumer group ${groupName} already exists for stream ${streamKey}`);
      return true;
    }
    
    logger.error(`Failed to create consumer group ${groupName}: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

/**
 * Read messages from a stream as part of a consumer group
 * @param {string} streamKey - The stream key
 * @param {string} groupName - Consumer group name
 * @param {string} consumerName - Consumer name
 * @param {number} count - Max number of messages to read (default: 10)
 * @param {number} blockMs - Time to block waiting for messages (default: 2000)
 * @returns {Promise<Array>} Array of messages
 */
async function readGroupFromStream(streamKey, groupName, consumerName, count = 10, blockMs = 2000) {
  try {
    if (!redisClient) {
      await initRedisClients();
    }
    
    // Try to create the consumer group first (in case it doesn't exist)
    try {
      await createConsumerGroup(streamKey, groupName);
    } catch (err) {
      // Ignore errors from group creation
    }
    
    // Read messages for this consumer
    const messages = await redisClient.xreadgroup(
      'GROUP', groupName, consumerName,
      'COUNT', count,
      'BLOCK', blockMs,
      'STREAMS', streamKey, '>'  // '>' means read new messages not yet delivered to any consumer
    );
    
    if (!messages || messages.length === 0) {
      return [];
    }
    
    // Format the messages for easier consumption
    const formattedMessages = messages[0][1].map(msg => {
      const [id, fields] = msg;
      const formattedFields = {};
      
      // Convert array of field-value pairs to object
      for (let i = 0; i < fields.length; i += 2) {
        formattedFields[fields[i]] = fields[i + 1];
      }
      
      return {
        id,
        fields: formattedFields
      };
    });
    
    logger.debug(`Consumer ${consumerName} read ${formattedMessages.length} messages from stream ${streamKey}`);
    return formattedMessages;
  } catch (err) {
    logger.error(`Failed to read from consumer group ${groupName}: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

/**
 * Acknowledge processing of a message in a consumer group
 * @param {string} streamKey - The stream key
 * @param {string} groupName - Consumer group name
 * @param {string} messageId - Message ID to acknowledge
 * @returns {Promise<number>} Number of messages acknowledged
 */
async function ackMessage(streamKey, groupName, messageId) {
  try {
    if (!redisClient) {
      await initRedisClients();
    }
    
    const result = await redisClient.xack(streamKey, groupName, messageId);
    logger.debug(`Acknowledged message ${messageId} in group ${groupName}`);
    return result;
  } catch (err) {
    logger.error(`Failed to acknowledge message ${messageId}: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

/**
 * Post a message to a leadership coordination stream
 * @param {Object} message - Message to post
 * @returns {Promise<string>} Message ID
 */
async function postToLeadershipStream(message) {
  if (typeof message !== 'object') {
    throw new Error('Message must be an object');
  }
  
  // Add server name and timestamp to message
  const enhancedMessage = {
    ...message,
    server: config.server.name,
    timestamp: Date.now(),
  };
  
  return addToStream(config.redis.streams.leadership, enhancedMessage);
}

/**
 * Post a direct message to another system
 * @param {string} target - Target system (keystone, echo, sentinel, cline)
 * @param {Object} message - Message to post
 * @returns {Promise<string>} Message ID
 */
async function postDirectMessage(target, message) {
  if (typeof message !== 'object') {
    throw new Error('Message must be an object');
  }
  
  let streamKey;
  switch (target.toLowerCase()) {
    case 'keystone':
      streamKey = config.redis.streams.directKeystone;
      break;
    case 'echo':
      streamKey = config.redis.streams.directEcho;
      break;
    case 'sentinel':
      streamKey = config.redis.streams.directSentinel;
      break;
    case 'cline':
      streamKey = config.redis.streams.directCline;
      break;
    default:
      throw new Error(`Unknown target system: ${target}`);
  }
  
  // Add server name and timestamp to message
  const enhancedMessage = {
    ...message,
    server: config.server.name,
    timestamp: Date.now(),
  };
  
  return addToStream(streamKey, enhancedMessage);
}

/**
 * Start listening for messages on a stream with a callback
 * @param {string} streamKey - The stream key
 * @param {string} groupName - Consumer group name
 * @param {string} consumerName - Consumer name
 * @param {Function} callback - Callback function(message)
 * @param {number} pollIntervalMs - Polling interval (default: 1000)
 * @returns {Object} Control object with stop() method
 */
function listenToStream(streamKey, groupName, consumerName, callback, pollIntervalMs = 1000) {
  let running = true;
  
  // Create a polling loop
  const poll = async () => {
    if (!running) return;
    
    try {
      const messages = await readGroupFromStream(streamKey, groupName, consumerName);
      
      // Process each message and acknowledge it
      for (const message of messages) {
        try {
          await callback(message);
          await ackMessage(streamKey, groupName, message.id);
        } catch (err) {
          logger.error(`Error processing message ${message.id}: ${err.message}`, { stack: err.stack });
        }
      }
    } catch (err) {
      logger.error(`Error in stream listener: ${err.message}`, { stack: err.stack });
    }
    
    // Schedule next poll
    setTimeout(poll, pollIntervalMs);
  };
  
  // Start polling
  poll();
  
  // Return control object
  return {
    stop: () => {
      running = false;
      logger.info(`Stopped listening to stream ${streamKey}`);
    }
  };
}

/**
 * Listen for messages on leadership coordination stream
 * @param {Function} callback - Callback function(message)
 * @returns {Object} Control object with stop() method
 */
function listenToLeadershipStream(callback) {
  return listenToStream(
    config.redis.streams.leadership,
    'slack-mcp-server',
    'leadership-listener',
    callback
  );
}

/**
 * Listen for direct messages to this system
 * @param {Function} callback - Callback function(message)
 * @returns {Object} Control object with stop() method
 */
function listenForDirectMessages(callback) {
  return listenToStream(
    config.redis.streams.directCline, // We're listening to messages directed to Cline
    'slack-mcp-server',
    'direct-msg-listener',
    callback
  );
}

module.exports = {
  initRedisClients,
  getRedisClient,
  getRedisSubscriber,
  addToStream,
  readFromStream,
  createConsumerGroup,
  readGroupFromStream,
  ackMessage,
  postToLeadershipStream,
  postDirectMessage,
  listenToStream,
  listenToLeadershipStream,
  listenForDirectMessages,
};
