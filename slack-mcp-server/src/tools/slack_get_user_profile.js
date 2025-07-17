/**
 * Tool: slack_get_user_profile
 * Get detailed profile information for a specific user
 */

const slack = require('../utils/slack');
const logger = require('../utils/logger');

const name = 'slack_get_user_profile';
const description = 'Get detailed profile information for a specific user';

const inputSchema = {
  type: 'object',
  properties: {
    user_id: {
      type: 'string',
      description: 'The user\'s ID'
    }
  },
  required: ['user_id']
};

/**
 * Execute the tool to get user profile from Slack
 * @param {Object} args - Tool arguments
 * @returns {Promise<Object>} - User profile details
 */
async function execute(args) {
  try {
    // Validate required parameters
    if (!args.user_id) {
      throw new Error('Missing required parameter: user_id');
    }
    
    // Execute the API call
    const result = await slack.getUserProfile(args.user_id);
    
    if (!result.ok || !result.user) {
      throw new Error(`Failed to retrieve user profile for ${args.user_id}`);
    }
    
    const user = result.user;
    
    // Format the response with comprehensive user details
    const formattedResponse = {
      id: user.id,
      name: user.name,
      real_name: user.real_name,
      display_name: user.profile?.display_name,
      status_text: user.profile?.status_text,
      status_emoji: user.profile?.status_emoji,
      avatar: user.profile?.image_192 || user.profile?.image_72,
      email: user.profile?.email,
      phone: user.profile?.phone,
      title: user.profile?.title,
      team: user.profile?.team,
      
      // Account type and privileges
      is_admin: user.is_admin || false,
      is_owner: user.is_owner || false,
      is_primary_owner: user.is_primary_owner || false,
      is_restricted: user.is_restricted || false,
      is_ultra_restricted: user.is_ultra_restricted || false,
      is_bot: user.is_bot || false,
      is_app_user: user.is_app_user || false,
      
      // Time properties
      updated: user.updated,
      created: user.created,
      deleted: user.deleted || false,
      
      // Timezone information
      tz: user.tz,
      tz_label: user.tz_label,
      tz_offset: user.tz_offset,
      
      // Team details
      team_id: user.team_id,
      
      // Additional profile fields if available
      fields: user.profile?.fields ? Object.entries(user.profile.fields).map(([id, field]) => ({
        id,
        label: field.label,
        value: field.value
      })) : []
    };
    
    logger.info(`Retrieved profile for user ${args.user_id}`);
    return formattedResponse;
  } catch (err) {
    logger.error(`Error in slack_get_user_profile: ${err.message}`, { stack: err.stack });
    throw err;
  }
}

module.exports = {
  name,
  description,
  inputSchema,
  execute
};
