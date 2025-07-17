/**
 * Logger utility for the Slack MCP server
 */

const fs = require('fs');
const path = require('path');
const config = require('../config/env');

// Ensure metrics directory exists if metrics are enabled
if (config.server.metricsEnabled) {
  if (!fs.existsSync(config.server.metricsPath)) {
    fs.mkdirSync(config.server.metricsPath, { recursive: true });
  }
}

// Get current date string for log file naming
const getDateString = () => {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
};

// Log levels
const LOG_LEVELS = {
  error: 0,
  warn: 1,
  info: 2,
  debug: 3,
};

// Current log level from config
const currentLogLevel = LOG_LEVELS[config.server.logLevel.toLowerCase()] || LOG_LEVELS.info;

/**
 * Write to log file if metrics are enabled
 * @param {string} level - Log level
 * @param {string} message - Log message
 * @param {Object} data - Additional data to log
 */
const writeToLogFile = (level, message, data) => {
  if (!config.server.metricsEnabled) return;
  
  const dateStr = getDateString();
  const logFile = path.join(config.server.metricsPath, `metrics-mcp-${dateStr}.log`);
  
  const timestamp = new Date().toISOString();
  const logEntry = {
    timestamp,
    level,
    server: config.server.name,
    message,
    ...(data ? { data } : {}),
  };
  
  try {
    fs.appendFileSync(logFile, JSON.stringify(logEntry) + '\n');
  } catch (err) {
    console.error(`Failed to write to log file: ${err.message}`);
  }
};

/**
 * Logger object with methods for different log levels
 */
const logger = {
  error: (message, data) => {
    if (currentLogLevel >= LOG_LEVELS.error) {
      console.error(`[ERROR] ${message}`, data || '');
      writeToLogFile('error', message, data);
    }
  },
  
  warn: (message, data) => {
    if (currentLogLevel >= LOG_LEVELS.warn) {
      console.warn(`[WARN] ${message}`, data || '');
      writeToLogFile('warn', message, data);
    }
  },
  
  info: (message, data) => {
    if (currentLogLevel >= LOG_LEVELS.info) {
      console.info(`[INFO] ${message}`, data || '');
      writeToLogFile('info', message, data);
    }
  },
  
  debug: (message, data) => {
    if (currentLogLevel >= LOG_LEVELS.debug) {
      console.debug(`[DEBUG] ${message}`, data || '');
      writeToLogFile('debug', message, data);
    }
  },
  
  /**
   * Log metrics about server operations
   * @param {string} metricName - Name of the metric
   * @param {Object} metricData - Metric data
   */
  metric: (metricName, metricData) => {
    if (!config.server.metricsEnabled) return;
    
    const timestamp = new Date().toISOString();
    const dateStr = getDateString();
    const metricFile = path.join(config.server.metricsPath, `metrics-mcp-${dateStr}.log`);
    
    const metricEntry = {
      timestamp,
      type: 'metric',
      server: config.server.name,
      metricName,
      metricData,
    };
    
    try {
      fs.appendFileSync(metricFile, JSON.stringify(metricEntry) + '\n');
    } catch (err) {
      console.error(`Failed to write metric to file: ${err.message}`);
    }
  },
};

module.exports = logger;
