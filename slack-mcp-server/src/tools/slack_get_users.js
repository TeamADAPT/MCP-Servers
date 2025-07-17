/**
 * Tool: slack_get_users
 * Get a list of all users in the workspace with their basic profile information
 */

const slack = require('../utils/slack');
const logger = require('../utils/logger');

const name = 'slack_get_users';
const description = 'Get a list of workspace users with basic profile information';

const inputSchema = {
  type: 'object',
  properties: {
    cursor: {
      type: 'string',
      description: 'Pagination cursor for next page of results'
    },
    limit: {
      type: 'number',
      description: 'Maximum number of users to return (default 100, max 200)',
      default: 100,
      minimum: 1,
      maximum: 200
    }
  }
};

/**
 * Execute the tool to get users from Slack
 * @param {Object} args - Tool arguments
 * @returns {Promise<Object>} - List of users
 */
async function execute(args = {}) {
  try {
    // Validate limit
    const limit = args.limit || 100;
    if (limit < 1 || limit > 200) {
      throw new Error('Limit must be between 1 and 200');
    }
    
    // Execute the API call
    const result = await slack.getUsers({
      limit,
      cursor: args.cursor
    });
    
    // Format the response to focus on relevant information
    const formattedUsers = result.members.map(user => ({
      id: user.id,
      name: user.name,
      real_name: user.real_name,
      display_name: user.profile?.display_name,
      title: user.profile?.title,
      email: user.profile?.email,
      team_id: user.team_id,
      is_bot: user.is_bot || false,
      is_admin: user.is_admin || false,
      is_owner: user.is_owner || false,
      is_restricted: user.is_restricted || false,
      is_ultra_restricted: user.is_ultra_restricted || false,
      tz: user.tz,
      tz_label: user.tz_label,
      updated: user.updated
    }));
    
    const formattedResponse = {
      users: formattedUsers,
      has_more: result.response_metadata?.next_cursor ? true : false,
      next_cursor: result.response_metadata?.next_cursor || null,
      total_count: formattedUsers.length
    };
    
    logger.info(`Retrieved ${formattedUsers.length} users`);
    return formattedResponse;
  } catch (err) {
    logger.error(`Error in slack_get_users: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

module.exports = {
  name,
  description,
  inputSchema,
  execute
};
