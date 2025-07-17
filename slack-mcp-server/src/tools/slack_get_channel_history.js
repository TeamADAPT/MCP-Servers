/**
 * Tool: slack_get_channel_history
 * Retrieves recent messages from a Slack channel
 */

const slack = require('../utils/slack');
const logger = require('../utils/logger');

const name = 'slack_get_channel_history';
const description = 'Get recent messages from a channel';

const inputSchema = {
  type: 'object',
  properties: {
    channel_id: {
      type: 'string',
      description: 'The channel ID'
    },
    limit: {
      type: 'number',
      description: 'Number of messages to retrieve (default: 10)',
      default: 10,
      minimum: 1,
      maximum: 100
    },
    oldest: {
      type: 'string',
      description: 'Optional timestamp of the oldest message to retrieve'
    },
    latest: {
      type: 'string',
      description: 'Optional timestamp of the latest message to retrieve'
    },
    inclusive: {
      type: 'boolean',
      description: 'Optional flag to include messages with timestamps matching oldest or latest',
      default: false
    }
  },
  required: ['channel_id']
};

/**
 * Execute the tool to get channel history from Slack
 * @param {Object} args - Tool arguments
 * @returns {Promise<Object>} - Channel history details
 */
async function execute(args) {
  try {
    // Validate required parameters
    if (!args.channel_id) {
      throw new Error('Missing required parameter: channel_id');
    }
    
    // Validate limit
    const limit = args.limit || 10;
    if (limit < 1 || limit > 100) {
      throw new Error('Limit must be between 1 and 100');
    }
    
    // Build options for the API call
    const options = {
      limit
    };
    
    // Add optional parameters if provided
    if (args.oldest) options.oldest = args.oldest;
    if (args.latest) options.latest = args.latest;
    if (typeof args.inclusive === 'boolean') options.inclusive = args.inclusive;
    
    // Execute the API call
    const result = await slack.getChannelHistory(args.channel_id, options);
    
    // Process and enhance the message data
    const messages = result.messages.map(msg => {
      // Extract basic message info
      const processedMsg = {
        type: msg.type,
        ts: msg.ts,
        user: msg.user,
        text: msg.text,
        has_thread: msg.thread_ts ? true : false,
        reply_count: msg.reply_count || 0,
        reactions: []
      };
      
      // Add reactions if present
      if (msg.reactions && Array.isArray(msg.reactions)) {
        processedMsg.reactions = msg.reactions.map(reaction => ({
          name: reaction.name,
          count: reaction.count,
          users: reaction.users.length
        }));
      }
      
      // Add client message ID if present
      if (msg.client_msg_id) {
        processedMsg.client_msg_id = msg.client_msg_id;
      }
      
      // Add thread timestamp if present
      if (msg.thread_ts) {
        processedMsg.thread_ts = msg.thread_ts;
      }
      
      return processedMsg;
    });
    
    // Format the response
    const formattedResponse = {
      channel: args.channel_id,
      message_count: messages.length,
      has_more: result.has_more || false,
      messages
    };
    
    logger.info(`Retrieved ${messages.length} messages from channel ${args.channel_id}`);
    return formattedResponse;
  } catch (err) {
    logger.error(`Error in slack_get_channel_history: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

module.exports = {
  name,
  description,
  inputSchema,
  execute
};
