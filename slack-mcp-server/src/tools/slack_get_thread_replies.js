/**
 * Tool: slack_get_thread_replies
 * Retrieves all replies in a message thread
 */

const slack = require('../utils/slack');
const logger = require('../utils/logger');

const name = 'slack_get_thread_replies';
const description = 'Get all replies in a message thread';

const inputSchema = {
  type: 'object',
  properties: {
    channel_id: {
      type: 'string',
      description: 'The ID of the channel containing the thread'
    },
    thread_ts: {
      type: 'string',
      description: 'The timestamp of the parent message in the format \'1234567890.123456\'. Timestamps in the format without the period can be converted by adding the period such that 6 numbers come after it.'
    },
    limit: {
      type: 'number',
      description: 'Number of replies to retrieve (default: all replies)',
      minimum: 1,
      maximum: 1000
    },
    oldest: {
      type: 'string',
      description: 'Optional timestamp of the oldest reply to retrieve'
    },
    latest: {
      type: 'string',
      description: 'Optional timestamp of the latest reply to retrieve'
    }
  },
  required: ['channel_id', 'thread_ts']
};

/**
 * Execute the tool to get thread replies from Slack
 * @param {Object} args - Tool arguments
 * @returns {Promise<Object>} - Thread replies details
 */
async function execute(args) {
  try {
    // Validate required parameters
    if (!args.channel_id) {
      throw new Error('Missing required parameter: channel_id');
    }
    
    if (!args.thread_ts) {
      throw new Error('Missing required parameter: thread_ts');
    }
    
    // Format thread_ts if it doesn't contain a period
    let threadTs = args.thread_ts;
    if (!threadTs.includes('.')) {
      // Insert a period 6 characters from the end
      const len = threadTs.length;
      if (len > 6) {
        threadTs = threadTs.substring(0, len - 6) + '.' + threadTs.substring(len - 6);
      } else {
        throw new Error('Invalid thread_ts format');
      }
    }
    
    // Build options for the API call
    const options = {};
    
    // Add optional parameters if provided
    if (args.limit) options.limit = args.limit;
    if (args.oldest) options.oldest = args.oldest;
    if (args.latest) options.latest = args.latest;
    
    // Execute the API call
    const result = await slack.getThreadReplies(args.channel_id, threadTs, options);
    
    // Extract parent message and replies
    let parentMessage = null;
    const replies = [];
    
    result.messages.forEach((msg, index) => {
      const processedMsg = {
        type: msg.type,
        ts: msg.ts,
        user: msg.user,
        text: msg.text,
        reactions: []
      };
      
      // Add reactions if present
      if (msg.reactions && Array.isArray(msg.reactions)) {
        processedMsg.reactions = msg.reactions.map(reaction => ({
          name: reaction.name,
          count: reaction.count,
          users: reaction.users ? reaction.users.length : 0
        }));
      }
      
      // Add client message ID if present
      if (msg.client_msg_id) {
        processedMsg.client_msg_id = msg.client_msg_id;
      }
      
      // First message is the parent message
      if (index === 0 && msg.ts === threadTs) {
        parentMessage = processedMsg;
        parentMessage.reply_count = result.messages.length - 1;
        parentMessage.reply_users_count = result.response_metadata?.scopes?.length || 0;
      } else {
        replies.push(processedMsg);
      }
    });
    
    // Format the response
    const formattedResponse = {
      channel: args.channel_id,
      thread_ts: threadTs,
      parent_message: parentMessage,
      reply_count: replies.length,
      has_more: result.has_more || false,
      replies
    };
    
    logger.info(`Retrieved ${replies.length} replies for thread ${threadTs} in channel ${args.channel_id}`);
    return formattedResponse;
  } catch (err) {
    logger.error(`Error in slack_get_thread_replies: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

module.exports = {
  name,
  description,
  inputSchema,
  execute
};
