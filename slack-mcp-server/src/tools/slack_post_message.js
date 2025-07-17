/**
 * Tool: slack_post_message
 * Posts a new message to a Slack channel with support for multiple bot identities
 */

const { WebClient } = require('@slack/web-api');
const logger = require('../utils/logger');

const name = 'slack_post_message';
const description = 'Post a new message to a Slack channel';

const inputSchema = {
  type: 'object',
  properties: {
    channel_id: {
      type: 'string',
      description: 'The ID of the channel to post to'
    },
    text: {
      type: 'string',
      description: 'The message text to post'
    },
    blocks: {
      type: 'array',
      description: 'Optional message blocks for rich formatting (see Slack Block Kit documentation)'
    },
    attachments: {
      type: 'array',
      description: 'Optional message attachments'
    },
    as_user: {
      type: 'boolean',
      description: 'Optional flag to post as user rather than bot',
      default: true
    },
    unfurl_links: {
      type: 'boolean',
      description: 'Optional flag to enable link unfurling',
      default: true
    },
    unfurl_media: {
      type: 'boolean',
      description: 'Optional flag to enable media unfurling',
      default: true
    },
    bot_id: {
      type: 'string',
      description: 'Optional bot identity to use for posting (default, nexus, cortex, echo, synergy, etc.)',
      default: 'default'
    }
  },
  required: ['channel_id', 'text']
};

/**
 * Execute the tool to post a message to Slack
 * @param {Object} args - Tool arguments
 * @returns {Promise<Object>} - Posted message details
 */
async function execute(args) {
  try {
    // Validate required parameters
    if (!args.channel_id) {
      throw new Error('Missing required parameter: channel_id');
    }
    
    if (!args.text) {
      throw new Error('Missing required parameter: text');
    }
    
    // Build options for the API call
    const options = {
      channel: args.channel_id,
      text: args.text
    };
    
    // Add optional parameters if provided
    if (args.blocks) options.blocks = args.blocks;
    if (args.attachments) options.attachments = args.attachments;
    if (typeof args.as_user === 'boolean') options.as_user = args.as_user;
    if (typeof args.unfurl_links === 'boolean') options.unfurl_links = args.unfurl_links;
    if (typeof args.unfurl_media === 'boolean') options.unfurl_media = args.unfurl_media;
    
    // Get the appropriate token based on the bot_id
    const botId = args.bot_id || 'default';
    let token = process.env.SLACK_BOT_TOKEN; // Default token
    
    if (botId !== 'default') {
      const botTokenEnvVar = `SLACK_BOT_TOKEN_${botId.toUpperCase()}`;
      const botToken = process.env[botTokenEnvVar];
      
      if (botToken) {
        token = botToken;
        logger.info(`Using token from ${botTokenEnvVar} for bot ${botId}`);
      } else {
        logger.warn(`No token found for bot ${botId} (${botTokenEnvVar}), using default bot token`);
      }
    }
    
    // Create a client with the selected token
    const client = new WebClient(token);
    
    logger.info(`Posting message to channel ${args.channel_id} using bot ${botId}`);
    
    // Execute the API call
    const result = await client.chat.postMessage(options);
    
    // Format the response
    const formattedResponse = {
      ok: result.ok,
      timestamp: result.ts,
      channel: result.channel,
      message_sent: true,
      bot_used: botId,
      text: args.text.substring(0, 50) + (args.text.length > 50 ? '...' : '')
    };
    
    logger.info(`Posted message to channel ${args.channel_id} using bot ${botId}`, { timestamp: result.ts });
    return formattedResponse;
  } catch (err) {
    logger.error(`Error in slack_post_message: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

module.exports = {
  name,
  description,
  inputSchema,
  execute
};
