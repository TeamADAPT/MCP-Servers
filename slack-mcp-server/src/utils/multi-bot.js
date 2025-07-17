/**
 * Multi-Bot Support Utility
 * Provides functionality to work with multiple Slack bot identities
 */

const { WebClient } = require('@slack/web-api');
const logger = require('./logger');

// Main bot token from env (default)
const DEFAULT_BOT_TOKEN = process.env.SLACK_BOT_TOKEN;

// Map of bot identifiers to their tokens
// These tokens come from the .env file
const BOT_TOKENS = {
  'default': DEFAULT_BOT_TOKEN,
  'mybizai': process.env.SLACK_BOT_TOKEN, // Same as default for now
  'nexus': process.env.SLACK_BOT_TOKEN_NEXUS || DEFAULT_BOT_TOKEN,
  'cortex': process.env.SLACK_BOT_TOKEN_CORTEX || DEFAULT_BOT_TOKEN,
  'echo': process.env.SLACK_BOT_TOKEN_ECHO || DEFAULT_BOT_TOKEN,
  'synergy': process.env.SLACK_BOT_TOKEN_SYNERGY || DEFAULT_BOT_TOKEN,
  'vaeris': process.env.SLACK_BOT_TOKEN_VAERIS || DEFAULT_BOT_TOKEN,
  'catalyst': process.env.SLACK_BOT_TOKEN_CATALYST || DEFAULT_BOT_TOKEN,
  'cosmos': process.env.SLACK_BOT_TOKEN_COSMOS || DEFAULT_BOT_TOKEN,
  'vertex': process.env.SLACK_BOT_TOKEN_VERTEX || DEFAULT_BOT_TOKEN
};

// Cache of WebClient instances for each bot
const clients = {};

/**
 * Get a Slack WebClient for the specified bot
 * @param {string} botId - Bot identifier (default, nexus, cortex, etc.)
 * @returns {WebClient} Slack Web API client
 */
function getClientForBot(botId = 'default') {
  // Normalize botId to lowercase
  const normalizedBotId = botId.toLowerCase();
  
  // If we already have a client for this bot, return it
  if (clients[normalizedBotId]) {
    return clients[normalizedBotId];
  }
  
  // Get the token for the requested bot
  const token = BOT_TOKENS[normalizedBotId] || DEFAULT_BOT_TOKEN;
  
  if (!token) {
    logger.warn(`No token found for bot ${normalizedBotId}, using default bot`);
    return getClientForBot('default');
  }
  
  logger.info(`Creating client for bot ${normalizedBotId} with token: ${token.substring(0, 10)}...`);
  
  // Create a new client
  const client = new WebClient(token);
  
  // Cache the client
  clients[normalizedBotId] = client;
  
  return client;
}

/**
 * Get information about available bots
 * @returns {Array<Object>} Array of bot info objects
 */
function getAvailableBots() {
  return Object.keys(BOT_TOKENS).map(botId => ({
    id: botId,
    available: !!BOT_TOKENS[botId]
  }));
}

module.exports = {
  getClientForBot,
  getAvailableBots
};
