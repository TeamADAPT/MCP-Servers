/**
 * Redis Streams Listing Tool
 * 
 * This script connects to the Redis cluster and lists all available streams.
 * It also provides information about stream length and consumer groups.
 */

const { execSync } = require('child_process');
const readline = require('readline');

// Redis connection details
const REDIS_HOST = '127.0.0.1';
const REDIS_PORT = 7000;
const REDIS_PASSWORD = 'd5d7817937232ca5';

// Main function to list streams
async function listStreams() {
  console.log('\n=== Redis Streams Listing Tool ===\n');
  console.log('Connecting to Redis cluster...');
  
  try {
    // Test connection
    const pingResult = execSync(
      `redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} -a ${REDIS_PASSWORD} ping`,
      { encoding: 'utf8' }
    );
    
    if (pingResult.trim() !== 'PONG') {
      console.error('Error connecting to Redis: Connection test failed');
      process.exit(1);
    }
    
    console.log('Connection successful!\n');
    
    // Get all keys (potentially streams)
    console.log('Scanning for streams...');
    const allKeys = execSync(
      `redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} -a ${REDIS_PASSWORD} --scan --pattern '*'`,
      { encoding: 'utf8' }
    ).split('\n').filter(key => key.trim() !== '');
    
    // Check each key to see if it's a stream
    const streams = [];
    let count = 0;
    
    for (const key of allKeys) {
      try {
        // Use TYPE command to check if it's a stream
        const type = execSync(
          `redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} -a ${REDIS_PASSWORD} TYPE "${key}"`,
          { encoding: 'utf8' }
        ).trim();
        
        if (type === 'stream') {
          count++;
          console.log(`[${count}] Found stream: ${key}`);
          
          // Get stream length
          const length = execSync(
            `redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} -a ${REDIS_PASSWORD} XLEN "${key}"`,
            { encoding: 'utf8' }
          ).trim();
          
          // Get consumer groups
          const groupInfo = execSync(
            `redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} -a ${REDIS_PASSWORD} XINFO GROUPS "${key}"`,
            { encoding: 'utf8', stdio: ['pipe', 'pipe', 'ignore'] }
          ).trim();
          
          // Get first message info (if stream is not empty)
          let firstMessage = null;
          if (parseInt(length) > 0) {
            const firstMessageResult = execSync(
              `redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} -a ${REDIS_PASSWORD} XRANGE "${key}" - + COUNT 1`,
              { encoding: 'utf8' }
            ).trim();
            
            if (firstMessageResult && firstMessageResult !== '') {
              firstMessage = firstMessageResult;
            }
          }
          
          streams.push({
            name: key,
            length: parseInt(length),
            groups: groupInfo,
            firstMessage: firstMessage
          });
        }
      } catch (error) {
        // Ignore errors (key might not exist anymore)
      }
    }
    
    // Display results
    console.log('\n=== Redis Streams Summary ===\n');
    
    if (streams.length === 0) {
      console.log('No streams found in Redis.');
    } else {
      console.log(`Found ${streams.length} streams:\n`);
      
      const adaptStreams = streams.filter(s => s.name.startsWith('nova:'));
      const otherStreams = streams.filter(s => !s.name.startsWith('nova:'));
      
      // Show ADAPT streams first
      if (adaptStreams.length > 0) {
        console.log('=== ADAPT Streams ===');
        displayStreams(adaptStreams);
      }
      
      // Then show other streams
      if (otherStreams.length > 0) {
        console.log('\n=== Other Streams ===');
        displayStreams(otherStreams);
      }
    }
    
    // Prompt for more info
    await promptForDetails(streams);
    
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Function to display stream details
function displayStreams(streams) {
  for (const stream of streams) {
    console.log(`\n${stream.name}`);
    console.log(`  Length: ${stream.length} messages`);
    
    // Display consumer group info
    if (stream.groups && !stream.groups.includes('no consumer groups')) {
      console.log('  Consumer Groups: Yes');
    } else {
      console.log('  Consumer Groups: None');
    }
    
    // Display first message if exists
    if (stream.firstMessage && stream.firstMessage !== '') {
      console.log('  Has messages: Yes');
    } else {
      console.log('  Has messages: No');
    }
  }
}

// Function to prompt for more details
async function promptForDetails(streams) {
  if (streams.length === 0) return;
  
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  console.log('\n=== Options ===');
  console.log('1. View message sample from a stream');
  console.log('2. View consumer groups for a stream');
  console.log('3. View all stream names');
  console.log('4. Exit');
  
  const answer = await new Promise(resolve => {
    rl.question('\nEnter option (1-4): ', resolve);
  });
  
  if (answer === '1') {
    const streamName = await new Promise(resolve => {
      rl.question('Enter stream name: ', resolve);
    });
    
    try {
      const stream = streams.find(s => s.name === streamName);
      if (!stream) {
        console.log(`Stream "${streamName}" not found.`);
      } else if (stream.length === 0) {
        console.log(`Stream "${streamName}" is empty.`);
      } else {
        console.log(`\n=== Sample Messages from "${streamName}" ===\n`);
        const messages = execSync(
          `redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} -a ${REDIS_PASSWORD} XRANGE "${streamName}" - + COUNT 5`,
          { encoding: 'utf8' }
        );
        console.log(messages);
      }
    } catch (error) {
      console.error('Error getting messages:', error.message);
    }
    
    await promptForDetails(streams);
  } else if (answer === '2') {
    const streamName = await new Promise(resolve => {
      rl.question('Enter stream name: ', resolve);
    });
    
    try {
      console.log(`\n=== Consumer Groups for "${streamName}" ===\n`);
      const groups = execSync(
        `redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} -a ${REDIS_PASSWORD} XINFO GROUPS "${streamName}"`,
        { encoding: 'utf8' }
      );
      console.log(groups);
    } catch (error) {
      console.error('Error getting consumer groups:', error.message);
    }
    
    await promptForDetails(streams);
  } else if (answer === '3') {
    console.log('\n=== All Stream Names ===\n');
    streams.forEach((stream, index) => {
      console.log(`${index + 1}. ${stream.name}`);
    });
    
    await promptForDetails(streams);
  } else {
    rl.close();
  }
}

// Run the main function
listStreams().catch(console.error);
