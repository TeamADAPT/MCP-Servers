#!/usr/bin/env node
/**
 * Slack MCP Server Entry Point
 */

const SlackMcpServer = require('./src/server');
const logger = require('./src/utils/logger');

async function main() {
  try {
    logger.info('Starting Slack MCP Server...');
    
    const server = new SlackMcpServer();
    await server.run();
    
    // Keep the process running
    process.stdin.resume();
    
    process.on('uncaughtException', (err) => {
      logger.error(`Uncaught exception: ${err.message}`, { stack: err.stack });
    });
    
    process.on('unhandledRejection', (reason, promise) => {
      logger.error('Unhandled Rejection at:', { promise, reason });
    });
  } catch (err) {
    logger.error(`Failed to start server: ${err.message}`, { stack: err.stack });
    process.exit(1);
  }
}

main();
