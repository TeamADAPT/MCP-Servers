/**
 * Tool: slack_add_reaction
 * Adds an emoji reaction to a message in Slack
 */

const slack = require('../utils/slack');
const logger = require('../utils/logger');

const name = 'slack_add_reaction';
const description = 'Add an emoji reaction to a message';

const inputSchema = {
  type: 'object',
  properties: {
    channel_id: {
      type: 'string',
      description: 'The ID of the channel containing the message'
    },
    timestamp: {
      type: 'string',
      description: 'The timestamp of the message to react to'
    },
    reaction: {
      type: 'string',
      description: 'The name of the emoji reaction (without colons)'
    }
  },
  required: ['channel_id', 'timestamp', 'reaction']
};

/**
 * Execute the tool to add a reaction to a message in Slack
 * @param {Object} args - Tool arguments
 * @returns {Promise<Object>} - Reaction result details
 */
async function execute(args) {
  try {
    // Validate required parameters
    if (!args.channel_id) {
      throw new Error('Missing required parameter: channel_id');
    }
    
    if (!args.timestamp) {
      throw new Error('Missing required parameter: timestamp');
    }
    
    if (!args.reaction) {
      throw new Error('Missing required parameter: reaction');
    }
    
    // Remove colons from reaction if present
    let reaction = args.reaction;
    if (reaction.startsWith(':') && reaction.endsWith(':')) {
      reaction = reaction.substring(1, reaction.length - 1);
    }
    
    // Format timestamp if it doesn't contain a period
    let timestamp = args.timestamp;
    if (!timestamp.includes('.')) {
      // Insert a period 6 characters from the end
      const len = timestamp.length;
      if (len > 6) {
        timestamp = timestamp.substring(0, len - 6) + '.' + timestamp.substring(len - 6);
      } else {
        throw new Error('Invalid timestamp format');
      }
    }
    
    // Execute the API call
    const result = await slack.addReaction(args.channel_id, timestamp, reaction);
    
    // Format the response
    const formattedResponse = {
      ok: result.ok,
      channel: args.channel_id,
      timestamp: timestamp,
      reaction: reaction,
      already_reacted: result.already_reacted || false
    };
    
    logger.info(`Added reaction :${reaction}: to message ${timestamp} in channel ${args.channel_id}`);
    return formattedResponse;
  } catch (err) {
    logger.error(`Error in slack_add_reaction: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

module.exports = {
  name,
  description,
  inputSchema,
  execute
};
