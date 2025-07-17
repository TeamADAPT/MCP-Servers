/**
 * Slack MCP Server
 * Implements the Model Context Protocol (MCP) server for Slack integration
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} = require('@modelcontextprotocol/sdk/types.js');

const config = require('./config/env');
const logger = require('./utils/logger');
const redis = require('./utils/redis');
const slack = require('./utils/slack');

// Import tools
const slackListChannels = require('./tools/slack_list_channels');
const slackPostMessage = require('./tools/slack_post_message');
const slackReplyToThread = require('./tools/slack_reply_to_thread');
const slackAddReaction = require('./tools/slack_add_reaction');
const slackGetChannelHistory = require('./tools/slack_get_channel_history');
const slackGetThreadReplies = require('./tools/slack_get_thread_replies');
const slackGetUsers = require('./tools/slack_get_users');
const slackGetUserProfile = require('./tools/slack_get_user_profile');
const slackListBots = require('./tools/slack_list_bots');

class SlackMcpServer {
  constructor() {
    this.server = new Server(
      {
        name: config.server.name,
        version: config.server.version,
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Register all tools
    this.registerTools();
    
    // Set up error handling
    this.server.onerror = (error) => {
      logger.error('MCP Server error', { error });
    };
    
    // Handle process termination
    process.on('SIGINT', async () => {
      await this.close();
      process.exit(0);
    });
  }

  registerTools() {
    // Define the tools provided by this server
    const tools = [
      slackListChannels,
      slackPostMessage,
      slackReplyToThread,
      slackAddReaction,
      slackGetChannelHistory,
      slackGetThreadReplies,
      slackGetUsers,
      slackGetUserProfile,
      slackListBots,
    ];

    // Set up tool listing handler
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: tools.map(tool => ({
          name: tool.name,
          description: tool.description,
          inputSchema: tool.inputSchema,
        })),
      };
    });

    // Set up tool execution handler
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const toolName = request.params.name;
      const tool = tools.find(tool => tool.name === toolName);

      if (!tool) {
        throw new McpError(
          ErrorCode.MethodNotFound,
          `Unknown tool: ${toolName}`
        );
      }

      try {
        // Log tool execution
        logger.info(`Executing tool: ${toolName}`, { arguments: request.params.arguments });
        
        // Execute the tool
        const result = await tool.execute(request.params.arguments);
        
        // Log success
        logger.info(`Tool execution successful: ${toolName}`);
        
        // Report to leadership stream
        try {
          await redis.postToLeadershipStream({
            event: 'tool_execution',
            tool: toolName,
            status: 'success',
          });
        } catch (err) {
          logger.warn(`Failed to post to leadership stream: ${err.message}`);
        }
        
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      } catch (error) {
        // Log error
        logger.error(`Tool execution failed: ${toolName}`, { 
          error: error.message,
          stack: error.stack,
        });
        
        // Report to leadership stream
        try {
          await redis.postToLeadershipStream({
            event: 'tool_execution',
            tool: toolName,
            status: 'error',
            error: error.message,
          });
        } catch (err) {
          logger.warn(`Failed to post to leadership stream: ${err.message}`);
        }
        
        return {
          content: [
            {
              type: 'text',
              text: `Error executing ${toolName}: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async initialize() {
    try {
      // Initialize Redis for cross-system communication
      await redis.initRedisClients();
      
      // Announce server startup to leadership stream
      await redis.postToLeadershipStream({
        event: 'server_startup',
        server: config.server.name,
        version: config.server.version,
        timestamp: Date.now(),
      });
      
      // Set up Redis stream listeners
      this.setupStreamListeners();
      
      logger.info('Slack MCP Server initialized successfully');
    } catch (err) {
      logger.error(`Failed to initialize server: ${err.message}`, { stack: err.stack });
      throw err;
    }
  }

  setupStreamListeners() {
    // Listen for leadership coordination messages
    redis.listenToLeadershipStream(async (message) => {
      logger.debug(`Received leadership message`, { id: message.id, fields: message.fields });
      
      // Handle specific message types
      if (message.fields.event === 'server_query') {
        // Respond with server status
        await redis.postToLeadershipStream({
          event: 'server_response',
          respondingTo: message.id,
          server: config.server.name,
          status: 'online',
          uptime: process.uptime(),
        });
      }
    });
    
    // Listen for direct messages to this server
    redis.listenForDirectMessages(async (message) => {
      logger.debug(`Received direct message`, { id: message.id, fields: message.fields });
      
      // Implement specific direct message handlers here
    });
  }

  async run() {
    try {
      // Initialize the server
      await this.initialize();
      
      // Connect using stdio transport
      const transport = new StdioServerTransport();
      await this.server.connect(transport);
      
      logger.info('Slack MCP Server running on stdio');
    } catch (err) {
      logger.error(`Failed to start server: ${err.message}`, { stack: err.stack });
      process.exit(1);
    }
  }

  async close() {
    try {
      // Announce server shutdown
      await redis.postToLeadershipStream({
        event: 'server_shutdown',
        server: config.server.name,
        version: config.server.version,
        timestamp: Date.now(),
      });
      
      // Close server connection
      await this.server.close();
      logger.info('Server closed');
    } catch (err) {
      logger.error(`Error during server shutdown: ${err.message}`, { stack: err.stack });
    }
  }
}

module.exports = SlackMcpServer;
