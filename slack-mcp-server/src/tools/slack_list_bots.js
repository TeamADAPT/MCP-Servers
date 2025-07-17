/**
 * Tool: slack_list_bots
 * Lists available bot identities for multi-bot posting
 */

const multiBot = require('../utils/multi-bot');
const logger = require('../utils/logger');

const name = 'slack_list_bots';
const description = 'List available bot identities that can be used for posting messages';

const inputSchema = {
  type: 'object',
  properties: {}
};

/**
 * Execute the tool to list available bots
 * @param {Object} args - Tool arguments (none required)
 * @returns {Promise<Object>} - List of available bots
 */
async function execute(args = {}) {
  try {
    // Get available bots
    const bots = multiBot.getAvailableBots();
    
    // Format the response
    const formattedResponse = {
      bots: bots,
      total_count: bots.length,
      usage_example: {
        tool: "slack_post_message",
        parameters: {
          "channel_id": "C12345678",
          "text": "Hello from a specific bot!",
          "bot_id": "nexus" // Example bot
        }
      }
    };
    
    logger.info(`Listed ${bots.length} available bots`);
    return formattedResponse;
  } catch (err) {
    logger.error(`Error in slack_list_bots: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

module.exports = {
  name,
  description,
  inputSchema,
  execute
};
