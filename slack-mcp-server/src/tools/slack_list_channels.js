/**
 * Tool: slack_list_channels
 * Lists public channels in the Slack workspace with pagination support
 */

const slack = require('../utils/slack');
const logger = require('../utils/logger');

const name = 'slack_list_channels';
const description = 'List public channels in the workspace with pagination';

const inputSchema = {
  type: 'object',
  properties: {
    limit: {
      type: 'number',
      description: 'Maximum number of channels to return (default 100, max 200)',
      default: 100,
      minimum: 1,
      maximum: 200
    },
    cursor: {
      type: 'string',
      description: 'Pagination cursor for next page of results'
    }
  }
};

/**
 * Execute the tool to list Slack channels
 * @param {Object} args - Tool arguments
 * @returns {Promise<Object>} - List of channels
 */
async function execute(args = {}) {
  try {
    // Validate limit
    const limit = args.limit || 100;
    if (limit < 1 || limit > 200) {
      throw new Error('Limit must be between 1 and 200');
    }
    
    // Execute the API call
    const result = await slack.listChannels({
      limit,
      cursor: args.cursor
    });
    
    // Format the response to focus on relevant information
    const formattedResponse = {
      channels: result.channels.map(channel => ({
        id: channel.id,
        name: channel.name,
        is_private: channel.is_private || false,
        is_archived: channel.is_archived || false,
        num_members: channel.num_members,
        topic: channel.topic?.value,
        purpose: channel.purpose?.value,
        created: channel.created
      })),
      has_more: result.response_metadata?.next_cursor ? true : false,
      next_cursor: result.response_metadata?.next_cursor || null,
      total_count: result.channels.length
    };
    
    logger.info(`Listed ${formattedResponse.channels.length} channels`);
    return formattedResponse;
  } catch (err) {
    logger.error(`Error in slack_list_channels: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

module.exports = {
  name,
  description,
  inputSchema,
  execute
};
