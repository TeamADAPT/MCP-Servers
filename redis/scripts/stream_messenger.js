#!/usr/bin/env node
/**
 * Stream Messenger CLI
 * 
 * Command-line interface for interacting with Redis streams in the cluster.
 * Supports sending messages and reading replies from any stream, with special
 * handling for cluster redirections.
 */

const { execSync } = require('child_process');
const readline = require('readline');

// Default settings
const DEFAULT_STREAM = 'coo.vaeris.direct';
const DEFAULT_COUNT = 10;

// Redis Cluster nodes (all known nodes)
const REDIS_NODES = [
  { host: '127.0.0.1', port: 7000 },
  { host: '127.0.0.1', port: 7001 },
  { host: '127.0.0.1', port: 7002 }
];
const REDIS_PASSWORD = 'd5d7817937232ca5';

// Track the correct node for the current stream
let currentNode = REDIS_NODES[0]; // Will be updated automatically if needed
let currentStream = DEFAULT_STREAM;

/**
 * Execute a Redis command handling cluster redirections
 * 
 * @param {string} cmd The Redis command to execute
 * @param {boolean} allowRedirection Whether to follow Redis MOVED/ASK redirections
 * @returns {string|null} Command output or null on error
 */
function executeRedisCommand(cmd, allowRedirection = true) {
  try {
    // Execute the command on the current node
    const result = execSync(
      `redis-cli -h ${currentNode.host} -p ${currentNode.port} -a ${REDIS_PASSWORD} ${cmd}`,
      { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }
    ).trim();
    
    // Check if we need to handle a redirection
    if (allowRedirection && (result.startsWith('MOVED') || result.startsWith('ASK'))) {
      const parts = result.split(' ');
      if (parts.length >= 3) {
        const redirectParts = parts[2].split(':');
        if (redirectParts.length === 2) {
          const redirectHost = redirectParts[0];
          const redirectPort = parseInt(redirectParts[1]);
          
          // Update current node for future commands
          currentNode = { host: redirectHost, port: redirectPort };
          console.log(`Following redirection to ${redirectHost}:${redirectPort}...`);
          
          // Re-execute command on the correct node
          return executeRedisCommand(cmd, false); // Don't follow further redirections to avoid loops
        }
      }
      
      throw new Error(`Failed to parse redirection: ${result}`);
    }
    
    return result;
  } catch (error) {
    // Only print error message if not a redirection
    if (!error.message.includes('MOVED') && !error.message.includes('ASK')) {
      console.error(`Error executing: ${cmd}`);
      console.error(error.message);
    }
    return null;
  }
}

/**
 * Find the correct node for a stream
 * 
 * @param {string} stream The stream name
 * @returns {boolean} True if found the correct node, false otherwise
 */
function findCorrectNode(stream) {
  console.log(`Determining correct Redis Cluster node for stream '${stream}'...`);
  
  for (const node of REDIS_NODES) {
    console.log(`Trying node ${node.host}:${node.port}...`);
    currentNode = node;
    
    // Try to check the stream on this node
    const result = executeRedisCommand(`TYPE ${stream}`, true);
    
    // If we get a valid result (not a MOVED error), we've found the correct node
    if (result && !result.startsWith('MOVED') && !result.startsWith('ASK')) {
      console.log(`Found correct node: ${currentNode.host}:${currentNode.port}`);
      return true;
    }
    
    // If we got redirected, then currentNode has been updated and we've found it
    if (currentNode.host !== node.host || currentNode.port !== node.port) {
      console.log(`Redirected to correct node: ${currentNode.host}:${currentNode.port}`);
      return true;
    }
  }
  
  console.error(`Could not determine correct node for stream '${stream}'`);
  return false;
}

/**
 * Publish a message to a stream
 * 
 * @param {string} stream The stream name
 * @param {string} message The message content
 * @param {Object} metadata Additional metadata to include
 * @returns {string|null} Message ID if successful, null otherwise
 */
function publishMessage(stream, message, metadata = {}) {
  const timestamp = new Date().toISOString();
  
  // Format fields as key-value pairs for Redis XADD
  const fields = [
    'source', 'redis_mcp_cli',
    'timestamp', timestamp,
    'message', message,
    'sender', 'cline'
  ];
  
  // Add any additional metadata
  for (const [key, value] of Object.entries(metadata)) {
    fields.push(key, value);
  }
  
  // Properly escape the * character and fields to avoid shell interpretation issues
  const fieldsArg = fields.map(f => `"${f}"`).join(' ');
  const messageId = executeRedisCommand(`XADD ${stream} "*" ${fieldsArg}`);
  
  if (messageId) {
    console.log(`Message published successfully with ID: ${messageId}`);
    return messageId;
  } else {
    console.error('Failed to publish message');
    return null;
  }
}

/**
 * Read messages from a stream
 * 
 * @param {string} stream The stream name
 * @param {number} count Maximum number of messages to read
 * @param {boolean} reverse Read in reverse order (newest first) if true
 * @returns {boolean} True if operation succeeded, false otherwise
 */
function readMessages(stream, count = DEFAULT_COUNT, reverse = true) {
  // Check if stream exists
  const type = executeRedisCommand(`TYPE ${stream}`);
  
  if (type !== 'stream') {
    console.log(`Stream '${stream}' does not exist or is not accessible on this node.`);
    return false;
  }
  
  // Get stream length
  const length = parseInt(executeRedisCommand(`XLEN ${stream}`));
  console.log(`Stream has ${length} total messages`);
  
  if (length === 0) {
    console.log('Stream is empty.');
    return true;
  }
  
  // Read messages
  const command = reverse ? 'XREVRANGE' : 'XRANGE';
  const range = reverse ? '+ -' : '- +';
  const result = executeRedisCommand(`${command} ${stream} ${range} COUNT ${count}`);
  
  if (result) {
    console.log('\nMessages:');
    
    // Process and display the result
    const messages = parseRedisStreamOutput(result);
    displayMessages(messages);
    
    return true;
  }
  
  return false;
}

/**
 * Parse Redis stream output into structured message objects
 * 
 * @param {string} output Raw Redis output from XRANGE or XREVRANGE
 * @returns {Array} Array of message objects
 */
function parseRedisStreamOutput(output) {
  if (!output) return [];
  
  const lines = output.split('\n');
  const messages = [];
  let currentMessage = null;
  let currentField = null;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // Message ID line (always starts with a number and a closing parenthesis)
    if (/^\d+\)/.test(line)) {
      if (currentMessage) {
        messages.push(currentMessage);
      }
      currentMessage = { fields: {} };
      continue;
    }
    
    // Message ID value (always in quotes)
    if (line.startsWith('"') && !currentMessage.id) {
      currentMessage.id = line.replace(/"/g, '');
      continue;
    }
    
    // Fields array marker
    if (line === '1)' && currentMessage && !currentMessage.inFields) {
      currentMessage.inFields = true;
      continue;
    }
    
    // Field name or value
    if (currentMessage && currentMessage.inFields && line.startsWith('"')) {
      const value = line.replace(/"/g, '');
      
      if (!currentField) {
        // This is a field name
        currentField = value;
      } else {
        // This is a field value
        currentMessage.fields[currentField] = value;
        currentField = null;
      }
    }
  }
  
  // Add the last message if any
  if (currentMessage && currentMessage.id) {
    messages.push(currentMessage);
  }
  
  return messages;
}

/**
 * Display messages in a readable format
 * 
 * @param {Array} messages Array of message objects
 */
function displayMessages(messages) {
  if (!messages || messages.length === 0) {
    console.log('No messages to display');
    return;
  }
  
  messages.forEach((msg, index) => {
    console.log(`\n[${index + 1}] Message ID: ${msg.id}`);
    
    if (msg.fields) {
      // Display timestamp and sender first if available
      if (msg.fields.timestamp) {
        console.log(`Timestamp: ${msg.fields.timestamp}`);
      }
      
      if (msg.fields.sender) {
        console.log(`Sender: ${msg.fields.sender}`);
      }
      
      if (msg.fields.source) {
        console.log(`Source: ${msg.fields.source}`);
      }
      
      // Display message content prominently
      if (msg.fields.message) {
        console.log(`\nContent: ${msg.fields.message}\n`);
      }
      
      // Display all other fields
      for (const [key, value] of Object.entries(msg.fields)) {
        if (!['timestamp', 'sender', 'source', 'message'].includes(key)) {
          console.log(`${key}: ${value}`);
        }
      }
    }
  });
}

/**
 * Create a consumer group for a stream
 * 
 * @param {string} stream The stream name
 * @param {string} group Consumer group name
 * @returns {boolean} True if successful, false otherwise
 */
function createConsumerGroup(stream, group) {
  try {
    // Check if stream exists, create if it doesn't
    const type = executeRedisCommand(`TYPE ${stream}`);
    
    if (type !== 'stream') {
      // Create the stream with an initial message - properly escape * character
      const msgId = executeRedisCommand(`XADD ${stream} "*" "init_message" "Stream created for messaging" "source" "stream_messenger"`);
      if (msgId) {
        console.log(`Created stream '${stream}' with initial message ID: ${msgId}`);
      } else {
        console.error(`Failed to create stream '${stream}'`);
        return false;
      }
    }
    
    // Try to create the consumer group - properly escape $ character
    const result = executeRedisCommand(`XGROUP CREATE ${stream} ${group} "$" MKSTREAM`);
    if (result === 'OK') {
      console.log(`Created consumer group '${group}' for stream '${stream}'`);
      return true;
    } else {
      // Group might already exist
      const groups = executeRedisCommand(`XINFO GROUPS ${stream}`);
      if (groups && groups.includes(group)) {
        console.log(`Consumer group '${group}' already exists`);
        return true;
      }
      console.error(`Failed to create consumer group '${group}': ${result}`);
      return false;
    }
  } catch (error) {
    if (error.message && error.message.includes('BUSYGROUP')) {
      console.log(`Consumer group '${group}' already exists`);
      return true;
    }
    console.error(`Error creating consumer group: ${error.message}`);
    return false;
  }
}

/**
 * Read messages as a consumer in a group
 * 
 * @param {string} stream The stream name
 * @param {string} group Consumer group name
 * @param {string} consumer Consumer name
 * @param {number} count Maximum number of messages to read
 * @param {boolean} includeHistory Include previously read messages
 * @returns {boolean} True if operation succeeded, false otherwise
 */
function readAsConsumer(stream, group, consumer, count = DEFAULT_COUNT, includeHistory = false) {
  // First try to create the group (will do nothing if it exists)
  if (!createConsumerGroup(stream, group)) {
    return false;
  }
  
  // Read messages as the consumer
  // Use ">" in quotes to avoid shell interpretation issues
  const id = includeHistory ? '0' : '">"';  // > for new messages only, 0 for all messages
  const result = executeRedisCommand(`XREADGROUP GROUP ${group} ${consumer} COUNT ${count} STREAMS ${stream} ${id}`);
  
  if (!result || result.trim() === '') {
    console.log(`No ${includeHistory ? '' : 'new '}messages for consumer '${consumer}' in group '${group}'`);
    return true;
  }
  
  console.log(`\nMessages for consumer '${consumer}' in group '${group}':`);
  const messages = parseRedisStreamOutput(result);
  displayMessages(messages);
  
  // Offer to acknowledge messages
  if (messages.length > 0) {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    rl.question('\nAcknowledge these messages? (y/n): ', (answer) => {
      if (answer.toLowerCase() === 'y') {
        let acked = 0;
        for (const msg of messages) {
          const result = executeRedisCommand(`XACK ${stream} ${group} ${msg.id}`);
          if (result === '1') {
            acked++;
          }
        }
        console.log(`Acknowledged ${acked} of ${messages.length} messages`);
      }
      rl.close();
    });
  }
  
  return true;
}

/**
 * Display stream information
 * 
 * @param {string} stream The stream name
 */
function showStreamInfo(stream) {
  // Check if stream exists
  const type = executeRedisCommand(`TYPE ${stream}`);
  
  if (type !== 'stream') {
    console.log(`Stream '${stream}' does not exist or is not accessible on this node.`);
    return;
  }
  
  // Get stream length
  const length = parseInt(executeRedisCommand(`XLEN ${stream}`));
  console.log(`\nStream: ${stream}`);
  console.log(`Total messages: ${length}`);
  
  // Get stream information if available
  const info = executeRedisCommand(`XINFO STREAM ${stream}`);
  if (info) {
    console.log('\nStream Information:');
    console.log(info);
  }
  
  // Get consumer groups
  const groups = executeRedisCommand(`XINFO GROUPS ${stream}`);
  if (groups) {
    console.log('\nConsumer Groups:');
    console.log(groups);
  } else {
    console.log('\nNo consumer groups defined');
  }
}

/**
 * Interactive CLI menu
 */
async function showMenu() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  const question = (prompt) => new Promise((resolve) => rl.question(prompt, resolve));
  
  while (true) {
    console.log('\n=== Stream Messenger CLI ===');
    console.log(`Current stream: ${currentStream}`);
    console.log(`Current node: ${currentNode.host}:${currentNode.port}`);
    console.log('\nOptions:');
    console.log('1. Send message to current stream');
    console.log('2. Read recent messages from current stream');
    console.log('3. Change current stream');
    console.log('4. Show stream information');
    console.log('5. Read as consumer (process new messages)');
    console.log('6. Read history as consumer (including processed messages)');
    console.log('7. Create consumer group');
    console.log('8. Exit');
    
    const choice = await question('\nSelect an option (1-8): ');
    
    if (choice === '1') {
      // Send message
      const message = await question('Enter message: ');
      publishMessage(currentStream, message);
    } 
    else if (choice === '2') {
      // Read messages
      const count = await question('Number of messages to read (default 10): ');
      readMessages(currentStream, parseInt(count) || DEFAULT_COUNT);
    } 
    else if (choice === '3') {
      // Change stream
      const stream = await question('Enter stream name: ');
      if (stream) {
        currentStream = stream;
        findCorrectNode(currentStream);
      }
    } 
    else if (choice === '4') {
      // Show stream info
      showStreamInfo(currentStream);
    } 
    else if (choice === '5') {
      // Read as consumer (new messages)
      const group = await question('Enter consumer group name: ');
      const consumer = await question('Enter consumer name: ');
      const count = await question('Number of messages to read (default 10): ');
      
      if (group && consumer) {
        readAsConsumer(currentStream, group, consumer, parseInt(count) || DEFAULT_COUNT, false);
      }
    } 
    else if (choice === '6') {
      // Read history as consumer
      const group = await question('Enter consumer group name: ');
      const consumer = await question('Enter consumer name: ');
      const count = await question('Number of messages to read (default 10): ');
      
      if (group && consumer) {
        readAsConsumer(currentStream, group, consumer, parseInt(count) || DEFAULT_COUNT, true);
      }
    } 
    else if (choice === '7') {
      // Create consumer group
      const group = await question('Enter consumer group name: ');
      
      if (group) {
        createConsumerGroup(currentStream, group);
      }
    } 
    else if (choice === '8') {
      console.log('Exiting Stream Messenger CLI');
      rl.close();
      break;
    } 
    else {
      console.log('Invalid option. Please try again.');
    }
  }
}

/**
 * Main function
 */
async function main() {
  console.log('\n=== Stream Messenger CLI ===\n');
  
  // Verify connection to Redis
  console.log('Testing connection to Redis Cluster...');
  const pingResult = executeRedisCommand('PING');
  
  if (!pingResult || pingResult !== 'PONG') {
    console.error('Could not connect to Redis Cluster. Please check your connection settings.');
    process.exit(1);
  }
  
  console.log('Connected to Redis Cluster successfully!');
  
  // Find the correct node for the default stream
  if (!findCorrectNode(currentStream)) {
    console.log(`Could not determine the correct node for ${currentStream}. This stream may not exist yet.`);
    console.log('We will create it when you send your first message.');
  }
  
  // Start interactive menu
  await showMenu();
}

// Run the main function
main().catch(console.error);
