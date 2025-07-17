/**
 * Environment variables configuration for the Slack MCP server
 */

const dotenv = require('dotenv');
const path = require('path');
const fs = require('fs');

// Load environment variables from .env file
dotenv.config();

// Ensure required environment variables are present
const requiredEnvVars = [
  'SLACK_BOT_TOKEN',
  'SLACK_TEAM_ID',
];

const missingEnvVars = requiredEnvVars.filter(
  (envVar) => !process.env[envVar]
);

if (missingEnvVars.length > 0) {
  console.error(`Missing required environment variables: ${missingEnvVars.join(', ')}`);
  console.error('Please check your .env file or environment configuration.');
  process.exit(1);
}

// Extract team ID from the token if not explicitly provided
if (!process.env.SLACK_TEAM_ID) {
  // Default to TeamADAPT team ID from .env
  process.env.SLACK_TEAM_ID = 'T07F2SDHSU8';
}

module.exports = {
  slack: {
    botToken: process.env.SLACK_BOT_TOKEN,
    teamId: process.env.SLACK_TEAM_ID,
    // Optional settings
    defaultChannel: process.env.SLACK_DEFAULT_CHANNEL,
    signingSecret: process.env.SLACK_SIGNING_SECRET
  },
  redis: {
    url: process.env.ADAPT_REDIS_URL || process.env.REDIS_URL,
    // Connection information from the Echo document
    cluster: {
      nodes: [
        { host: '127.0.0.1', port: 7000 },
        { host: '127.0.0.1', port: 7001 },
        { host: '127.0.0.1', port: 7002 },
      ],
      password: 'd5d7817937232ca5',
      enableClusterMode: true,
    },
    // Stream channels from Echo's coordination document
    streams: {
      leadership: 'swarm:leadership:coordination',
      directKeystone: 'keystone.direct',
      directEcho: 'memops.echo.direct',
      directCline: 'devops.cline.direct',
      directSentinel: 'systems.sentinel.direct',
      redisMcpDev: 'mcp:redis:dev',
      advancedMcpDev: 'mcp:advanced:dev',
    }
  },
  server: {
    name: 'slack-mcp-server',
    version: '1.0.0',
    logLevel: process.env.LOG_LEVEL || 'info',
    metricsEnabled: process.env.METRICS_ENABLED === 'true',
    metricsPath: process.env.METRICS_PATH || path.join(process.cwd(), 'logs'),
  }
};
