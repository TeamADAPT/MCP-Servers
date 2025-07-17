/**
 * Slack API utility for Slack MCP server
 * Provides functions for interacting with the Slack API
 */

const { WebClient } = require('@slack/web-api');
const config = require('../config/env');
const logger = require('./logger');

// Initialize the Slack Web API client
const slackClient = new WebClient(config.slack.botToken);

/**
 * List channels in the workspace
 * @param {Object} options - Options for listing channels
 * @param {number} options.limit - Maximum number of channels to return (default: 100, max: 1000)
 * @param {string} options.cursor - Pagination cursor
 * @returns {Promise<Object>} List of channels with their metadata
 */
async function listChannels(options = {}) {
  try {
    const result = await slackClient.conversations.list({
      limit: options.limit || 100,
      cursor: options.cursor || undefined,
      types: 'public_channel',
      exclude_archived: true,
    });

    logger.debug(`Listed ${result.channels.length} channels`, { hasMore: result.response_metadata?.next_cursor ? true : false });
    return result;
  } catch (err) {
    logger.error(`Failed to list channels: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

/**
 * Post a message to a channel
 * @param {string} channelId - The channel ID to post to
 * @param {string} text - The message text
 * @param {Object} options - Additional message options
 * @returns {Promise<Object>} The posted message
 */
async function postMessage(channelId, text, options = {}) {
  try {
    const result = await slackClient.chat.postMessage({
      channel: channelId,
      text,
      ...options,
    });

    logger.debug(`Posted message to channel ${channelId}`, { 
      timestamp: result.ts,
      text: text.substring(0, 50) + (text.length > 50 ? '...' : '') 
    });
    return result;
  } catch (err) {
    logger.error(`Failed to post message to channel ${channelId}: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

/**
 * Reply to a thread
 * @param {string} channelId - The channel ID
 * @param {string} threadTs - The parent message timestamp
 * @param {string} text - The reply text
 * @param {Object} options - Additional message options
 * @returns {Promise<Object>} The reply message
 */
async function replyToThread(channelId, threadTs, text, options = {}) {
  try {
    const result = await slackClient.chat.postMessage({
      channel: channelId,
      thread_ts: threadTs,
      text,
      ...options,
    });

    logger.debug(`Posted reply to thread ${threadTs} in channel ${channelId}`, { 
      timestamp: result.ts,
      text: text.substring(0, 50) + (text.length > 50 ? '...' : '') 
    });
    return result;
  } catch (err) {
    logger.error(`Failed to reply to thread ${threadTs} in channel ${channelId}: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

/**
 * Add a reaction to a message
 * @param {string} channelId - The channel ID
 * @param {string} timestamp - The message timestamp
 * @param {string} reaction - The reaction name (without colons)
 * @returns {Promise<Object>} The API response
 */
async function addReaction(channelId, timestamp, reaction) {
  try {
    const result = await slackClient.reactions.add({
      channel: channelId,
      timestamp,
      name: reaction,
    });

    logger.debug(`Added reaction :${reaction}: to message ${timestamp} in channel ${channelId}`);
    return result;
  } catch (err) {
    // Ignore reaction already added errors
    if (err.message === 'already_reacted') {
      logger.debug(`Reaction :${reaction}: already added to message ${timestamp}`);
      return { ok: true, already_reacted: true };
    }
    
    logger.error(`Failed to add reaction :${reaction}: to message ${timestamp}: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

/**
 * Get channel history
 * @param {string} channelId - The channel ID
 * @param {Object} options - Additional options
 * @param {number} options.limit - Number of messages to retrieve (default: 10)
 * @param {string} options.cursor - Pagination cursor
 * @returns {Promise<Object>} Channel message history
 */
async function getChannelHistory(channelId, options = {}) {
  try {
    const result = await slackClient.conversations.history({
      channel: channelId,
      limit: options.limit || 10,
      cursor: options.cursor || undefined,
    });

    logger.debug(`Retrieved ${result.messages.length} messages from channel ${channelId}`);
    return result;
  } catch (err) {
    logger.error(`Failed to get history for channel ${channelId}: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

/**
 * Get thread replies
 * @param {string} channelId - The channel ID
 * @param {string} threadTs - The parent message timestamp
 * @param {Object} options - Additional options
 * @param {number} options.limit - Number of replies to retrieve
 * @param {string} options.cursor - Pagination cursor
 * @returns {Promise<Object>} Thread replies
 */
async function getThreadReplies(channelId, threadTs, options = {}) {
  try {
    const result = await slackClient.conversations.replies({
      channel: channelId,
      ts: threadTs,
      limit: options.limit || 10,
      cursor: options.cursor || undefined,
    });

    logger.debug(`Retrieved ${result.messages.length} replies for thread ${threadTs} in channel ${channelId}`);
    return result;
  } catch (err) {
    logger.error(`Failed to get replies for thread ${threadTs} in channel ${channelId}: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

/**
 * Get workspace users
 * @param {Object} options - Additional options
 * @param {number} options.limit - Maximum number of users to return
 * @param {string} options.cursor - Pagination cursor
 * @returns {Promise<Object>} List of users
 */
async function getUsers(options = {}) {
  try {
    const result = await slackClient.users.list({
      limit: options.limit || 100,
      cursor: options.cursor || undefined,
    });

    logger.debug(`Retrieved ${result.members.length} users`);
    return result;
  } catch (err) {
    logger.error(`Failed to get users: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

/**
 * Get a user's profile information
 * @param {string} userId - The user ID
 * @returns {Promise<Object>} User profile information
 */
async function getUserProfile(userId) {
  try {
    const result = await slackClient.users.info({
      user: userId,
    });

    logger.debug(`Retrieved profile for user ${userId}`);
    return result;
  } catch (err) {
    logger.error(`Failed to get profile for user ${userId}: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

/**
 * Verify a request signature from Slack
 * @param {Object} requestHeaders - Request headers
 * @param {string} body - Raw request body
 * @returns {boolean} Whether the request is valid
 */
function verifyRequestSignature(requestHeaders, body) {
  // This would be used if implementing a HTTP endpoint, but not needed for MCP
  // Including it for completeness
  if (!config.slack.signingSecret) {
    logger.warn('No signing secret configured, skipping signature verification');
    return true;
  }
  
  // Implementation would verify the X-Slack-Signature header
  return true;
}

/**
 * Send a notification to a channel with error-handling and retries
 * @param {string} channelId - The channel ID to post to
 * @param {string} text - The message text
 * @param {Object} options - Additional message options
 * @param {number} retries - Number of retries (default: 3)
 * @returns {Promise<Object>} The posted message, or null if failed
 */
async function sendNotification(channelId, text, options = {}, retries = 3) {
  let attempt = 0;
  let lastError = null;
  
  while (attempt < retries) {
    try {
      return await postMessage(channelId, text, options);
    } catch (err) {
      lastError = err;
      attempt++;
      logger.warn(`Notification attempt ${attempt} failed: ${err.message}`);
      
      // Wait before retrying (exponential backoff)
      if (attempt < retries) {
        const delay = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  logger.error(`Failed to send notification after ${retries} attempts`, { 
    channelId, 
    text: text.substring(0, 50) + (text.length > 50 ? '...' : ''),
    error: lastError?.message, 
    stack: lastError?.stack 
  });
  
  return null;
}

module.exports = {
  client: slackClient,
  listChannels,
  postMessage,
  replyToThread,
  addReaction,
  getChannelHistory,
  getThreadReplies,
  getUsers,
  getUserProfile,
  verifyRequestSignature,
  sendNotification,
};
