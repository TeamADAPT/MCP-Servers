/**
 * CEO Stream Checker
 * 
 * This script specifically checks for and interacts with the CEO's stream.
 * It demonstrates connectivity and the ability to publish/read messages.
 */

const { execSync } = require('child_process');
const readline = require('readline');

// Redis connection details
const REDIS_HOST = '127.0.0.1';
const REDIS_PORT = 7000;
const REDIS_PASSWORD = 'd5d7817937232ca5';
const CEO_STREAM = 'ceo.chase.direct';

// Execute command and return output
function executeRedisCommand(cmd) {
  try {
    return execSync(
      `redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} -a ${REDIS_PASSWORD} ${cmd}`,
      { encoding: 'utf8' }
    ).trim();
  } catch (error) {
    console.error(`Error executing command: ${cmd}`);
    console.error(error.message);
    return null;
  }
}

// Publish a message to the CEO stream
async function publishToCEOStream(message) {
  const timestamp = new Date().toISOString();
  const fields = [
    'source', 'redis_mcp_server',
    'timestamp', timestamp,
    'message', message,
    'server_id', 'redis_mcp_implementation'
  ];
  
  const result = executeRedisCommand(`XADD ${CEO_STREAM} * ${fields.join(' ')}`);
  return result;
}

// Read from CEO stream
function readFromCEOStream(count = 5) {
  // Check if stream exists
  const type = executeRedisCommand(`TYPE ${CEO_STREAM}`);
  
  if (type !== 'stream') {
    console.log(`\nStream '${CEO_STREAM}' does not exist or is not a stream type.`);
    return null;
  }
  
  // Get stream length
  const length = parseInt(executeRedisCommand(`XLEN ${CEO_STREAM}`));
  
  if (length === 0) {
    console.log(`\nStream '${CEO_STREAM}' exists but is empty.`);
    return [];
  }
  
  // Read from stream
  const messages = executeRedisCommand(`XREVRANGE ${CEO_STREAM} + - COUNT ${count}`);
  return messages;
}

// Create consumer group for the CEO stream
function createConsumerGroup(group) {
  try {
    // Check if stream exists, create if it doesn't
    const type = executeRedisCommand(`TYPE ${CEO_STREAM}`);
    
    if (type !== 'stream') {
      // Create the stream with an initial message
      executeRedisCommand(`XADD ${CEO_STREAM} * init_message "Stream created for CEO communication"`);
      console.log(`Created stream '${CEO_STREAM}'`);
    }
    
    // Try to create the consumer group
    const result = executeRedisCommand(`XGROUP CREATE ${CEO_STREAM} ${group} $ MKSTREAM`);
    if (result === 'OK') {
      console.log(`Created consumer group '${group}' for stream '${CEO_STREAM}'`);
    } else {
      // Group might already exist
      console.log(`Consumer group operation result: ${result}`);
      
      // Check if group exists
      const groups = executeRedisCommand(`XINFO GROUPS ${CEO_STREAM}`);
      console.log(`Existing groups: ${groups}`);
    }
  } catch (error) {
    if (error.message && error.message.includes('BUSYGROUP')) {
      console.log(`Consumer group '${group}' already exists`);
    } else {
      console.error(`Error creating consumer group: ${error.message}`);
    }
  }
}

// Read as a consumer
function readAsConsumer(group, consumer, count = 5) {
  // First try to create the group (will do nothing if it exists)
  createConsumerGroup(group);
  
  // Read messages as the consumer
  const messages = executeRedisCommand(`XREADGROUP GROUP ${group} ${consumer} COUNT ${count} STREAMS ${CEO_STREAM} >`);
  
  if (!messages || messages.trim() === '') {
    console.log(`No new messages for consumer '${consumer}' in group '${group}'`);
    
    // Try reading some history
    console.log(`Trying to read some history...`);
    const history = executeRedisCommand(`XREADGROUP GROUP ${group} ${consumer} COUNT ${count} STREAMS ${CEO_STREAM} 0`);
    
    if (!history || history.trim() === '') {
      console.log(`No history available or all messages already processed`);
    } else {
      console.log(`\nHistory messages:\n${history}`);
    }
    
    return null;
  }
  
  return messages;
}

// Acknowledge a message
function acknowledgeMessage(group, messageId) {
  const result = executeRedisCommand(`XACK ${CEO_STREAM} ${group} ${messageId}`);
  return parseInt(result) === 1;
}

// Main function
async function main() {
  console.log(`\n=== CEO Stream Check ===\n`);
  
  // Check connection to Redis
  console.log(`Connecting to Redis at ${REDIS_HOST}:${REDIS_PORT}...`);
  const pingResult = executeRedisCommand('PING');
  
  if (pingResult !== 'PONG') {
    console.error('Error connecting to Redis. Connection test failed.');
    process.exit(1);
  }
  
  console.log('Connection successful!\n');
  
  // Check if CEO stream exists
  console.log(`Checking for CEO stream '${CEO_STREAM}'...`);
  const streamType = executeRedisCommand(`TYPE ${CEO_STREAM}`);
  
  if (streamType === 'stream') {
    console.log(`Found CEO stream: ${CEO_STREAM}`);
    
    // Get stream information
    const length = executeRedisCommand(`XLEN ${CEO_STREAM}`);
    console.log(`  Length: ${length} messages`);
    
    // Try to get some messages
    console.log('\nLatest messages:');
    const messages = readFromCEOStream();
    if (messages) {
      console.log(messages);
    }
    
    // Check if there are any consumer groups
    console.log('\nConsumer groups:');
    const groups = executeRedisCommand(`XINFO GROUPS ${CEO_STREAM}`);
    console.log(groups || 'No consumer groups');
    
  } else if (streamType === 'none') {
    console.log(`CEO stream '${CEO_STREAM}' does not exist yet.`);
    console.log('Creating stream...');
    
    // Create the stream with an initial message
    const messageId = executeRedisCommand(`XADD ${CEO_STREAM} * source "redis_mcp_server" message "Stream initialized for CEO communication" timestamp "${new Date().toISOString()}"`);
    
    if (messageId) {
      console.log(`Stream created successfully. Initial message ID: ${messageId}`);
    } else {
      console.error('Failed to create stream.');
      process.exit(1);
    }
  } else {
    console.error(`Unexpected type for CEO stream: ${streamType}`);
    process.exit(1);
  }
  
  // Interactive menu
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  const promptMenu = async () => {
    console.log('\n=== CEO Stream Operations ===');
    console.log('1. Publish a message to CEO stream');
    console.log('2. Read recent messages from CEO stream');
    console.log('3. Create a consumer group');
    console.log('4. Read as a consumer');
    console.log('5. Exit');
    
    const answer = await new Promise(resolve => {
      rl.question('\nEnter option (1-5): ', resolve);
    });
    
    if (answer === '1') {
      const message = await new Promise(resolve => {
        rl.question('Enter message to publish: ', resolve);
      });
      
      const messageId = await publishToCEOStream(message);
      console.log(`Published message with ID: ${messageId}`);
      promptMenu();
      
    } else if (answer === '2') {
      const count = await new Promise(resolve => {
        rl.question('Number of messages to read: ', resolve);
      });
      
      console.log(`\nReading ${count} recent messages:`);
      const messages = readFromCEOStream(parseInt(count) || 5);
      console.log(messages || 'No messages available');
      promptMenu();
      
    } else if (answer === '3') {
      const group = await new Promise(resolve => {
        rl.question('Enter consumer group name: ', resolve);
      });
      
      createConsumerGroup(group);
      promptMenu();
      
    } else if (answer === '4') {
      const group = await new Promise(resolve => {
        rl.question('Enter consumer group name: ', resolve);
      });
      
      const consumer = await new Promise(resolve => {
        rl.question('Enter consumer name: ', resolve);
      });
      
      console.log(`\nReading as consumer '${consumer}' in group '${group}':`);
      const messages = readAsConsumer(group, consumer);
      
      if (messages) {
        console.log(messages);
        
        const ack = await new Promise(resolve => {
          rl.question('\nAcknowledge a message? (message ID or N): ', resolve);
        });
        
        if (ack && ack.toLowerCase() !== 'n') {
          const result = acknowledgeMessage(group, ack);
          console.log(`Acknowledgment result: ${result ? 'Successful' : 'Failed'}`);
        }
      }
      
      promptMenu();
      
    } else if (answer === '5') {
      console.log('Exiting CEO stream checker.');
      rl.close();
      process.exit(0);
    } else {
      console.log('Invalid option. Please try again.');
      promptMenu();
    }
  };
  
  // Start the menu
  promptMenu();
}

// Run the main function
main().catch(console.error);
