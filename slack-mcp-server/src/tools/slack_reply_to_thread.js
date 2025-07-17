/**
 * Tool: slack_reply_to_thread
 * Replies to a specific message thread in Slack
 */

const slack = require('../utils/slack');
const logger = require('../utils/logger');

const name = 'slack_reply_to_thread';
const description = 'Reply to a specific message thread in Slack';

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
    text: {
      type: 'string',
      description: 'The reply text'
    },
    blocks: {
      type: 'array',
      description: 'Optional message blocks for rich formatting (see Slack Block Kit documentation)'
    },
    attachments: {
      type: 'array',
      description: 'Optional message attachments'
    }
  },
  required: ['channel_id', 'thread_ts', 'text']
};

/**
 * Execute the tool to reply to a thread in Slack
 * @param {Object} args - Tool arguments
 * @returns {Promise<Object>} - Reply message details
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
    
    if (!args.text) {
      throw new Error('Missing required parameter: text');
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
    
    // Execute the API call
    const options = {
      thread_ts: threadTs
    };
    
    // Add optional parameters if provided
    if (args.blocks) options.blocks = args.blocks;
    if (args.attachments) options.attachments = args.attachments;
    
    const result = await slack.replyToThread(args.channel_id, threadTs, args.text, options);
    
    // Format the response
    const formattedResponse = {
      ok: result.ok,
      timestamp: result.ts,
      channel: result.channel,
      thread_ts: threadTs,
      reply_sent: true,
      text: args.text.substring(0, 50) + (args.text.length > 50 ? '...' : '')
    };
    
    logger.info(`Posted reply to thread ${threadTs} in channel ${args.channel_id}`, { timestamp: result.ts });
    return formattedResponse;
  } catch (err) {
    logger.error(`Error in slack_reply_to_thread: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

module.exports = {
  name,
  description,
  inputSchema,
  execute
};
