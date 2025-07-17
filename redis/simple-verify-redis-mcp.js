#!/usr/bin/env node

/**
 * Simple Redis MCP Server Verification
 * 
 * This script verifies the basic operations of the Redis server 
 * and confirms the MCP configuration is in place.
 */

const fs = require('fs');
const { exec, spawn } = require('child_process');
const Redis = require('ioredis');

// Test values
const TEST_KEY = `verify-test-${Date.now()}`;
const TEST_VALUE = JSON.stringify({ message: "Verification test data", timestamp: new Date().toISOString() });

console.log('=== Redis MCP Server Simple Verification ===\n');

async function verifyRedisConnection() {
  // Create Redis client
  console.log('Connecting to Redis...');
  const redis = new Redis({
    host: 'localhost',
    port: 6380,
    prefix: 'verify:'
  });
  
  // Set up handlers
  redis.on('error', (err) => {
    console.error('Redis connection error:', err);
    process.exit(1);
  });
  
  try {
    // Test Redis operations
    console.log('\n=== Testing direct Redis operations ===');
    
    // 1. Test SET operation
    console.log('\n=== Testing SET operation ===');
    const setResult = await redis.set(TEST_KEY, TEST_VALUE);
    console.log('SET result:', setResult);
    
    // 2. Test GET operation
    console.log('\n=== Testing GET operation ===');
    const getValue = await redis.get(TEST_KEY);
    console.log('GET result:', getValue === TEST_VALUE ? 'Success - values match' : 'Failed - values do not match');
    
    // 3. Test LIST (KEYS) operation
    console.log('\n=== Testing LIST operation ===');
    const keys = await redis.keys('verify-test-*');
    console.log('KEYS result:', keys);
    
    // 4. Test DELETE operation
    console.log('\n=== Testing DELETE operation ===');
    const deleteResult = await redis.del(TEST_KEY);
    console.log('DEL result:', deleteResult);
    
    console.log('\n=== All Redis operations completed successfully! ===');
    
    return true;
  } catch (error) {
    console.error('Error during Redis operations:', error);
    return false;
  } finally {
    // Close Redis connection
    redis.quit();
    console.log('Redis connection closed');
  }
}

function checkMcpConfiguration() {
  console.log('\n=== Checking MCP Configuration ===');
  
  // Path to Cline MCP settings
  const settingsPath = '/home/x/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json';
  
  try {
    // Read and parse settings file
    const settingsContent = fs.readFileSync(settingsPath, 'utf8');
    const settings = JSON.parse(settingsContent);
    
    // Check if redis-mcp is configured
    if (settings.mcpServers && settings.mcpServers['redis-mcp']) {
      console.log('redis-mcp server is properly configured in Cline settings');
      
      // Show configuration details
      const config = settings.mcpServers['redis-mcp'];
      console.log('Configuration details:');
      console.log(`- Executable: ${config.command} ${config.args.join(' ')}`);
      console.log(`- Redis Host: ${config.env.REDIS_HOST}`);
      console.log(`- Redis Port: ${config.env.REDIS_PORT}`);
      
      return true;
    } else {
      console.error('redis-mcp server configuration not found in Cline settings');
      return false;
    }
  } catch (error) {
    console.error('Error checking MCP configuration:', error);
    return false;
  }
}

function verifyRedisMcpServer() {
  console.log('\n=== Verifying Redis MCP Server ===');
  
  // Start the MCP server process
  const mpcServerProcess = spawn('node', 
    ['mcp-redis-server/src/fixed-index.js'], 
    {
      env: {
        ...process.env,
        REDIS_HOST: 'localhost',
        REDIS_PORT: '6380',
        REDIS_NAMESPACE_PREFIX: 'verify:',
        NODE_OPTIONS: '--no-warnings'
      },
      stdio: ['ignore', 'pipe', 'pipe']
    }
  );
  
  let serverOutput = '';
  
  mpcServerProcess.stdout.on('data', (data) => {
    serverOutput += data.toString();
    console.log('Server output:', data.toString());
  });
  
  mpcServerProcess.stderr.on('data', (data) => {
    serverOutput += data.toString();
    console.log('Server stderr:', data.toString());
  });
  
  // Give the server a few seconds to start
  return new Promise((resolve) => {
    setTimeout(() => {
      // Check if server started successfully
      const successIndicators = [
        'Redis MCP Server running', 
        'Connected to Redis successfully'
      ];
      
      const success = successIndicators.every(indicator => 
        serverOutput.includes(indicator)
      );
      
      if (success) {
        console.log('MCP Server started successfully');
        resolve(true);
      } else {
        console.error('MCP Server did not start properly');
        console.error('Output:', serverOutput);
        resolve(false);
      }
      
      // Clean up
      mpcServerProcess.kill();
    }, 3000);
  });
}

// Run all verification steps
async function runVerification() {
  try {
    // Step 1: Verify Redis connection and operations
    const redisOk = await verifyRedisConnection();
    if (!redisOk) {
      console.error('\n❌ Redis verification failed');
      process.exit(1);
    }
    
    // Step 2: Check MCP configuration
    const configOk = checkMcpConfiguration();
    if (!configOk) {
      console.error('\n❌ MCP configuration verification failed');
      process.exit(1);
    }
    
    // Step 3: Verify MCP server can start properly
    const serverOk = await verifyRedisMcpServer();
    if (!serverOk) {
      console.error('\n❌ MCP server verification failed');
      process.exit(1);
    }
    
    // All steps passed
    console.log('\n✅ All verification steps passed!');
    console.log('\nThe redis-mcp server is correctly set up and ready to use in Cline.');
    console.log('It has been added to the Cline MCP settings and should be available after restarting Cline.');
    
    process.exit(0);
  } catch (error) {
    console.error('\n❌ Verification failed with error:', error);
    process.exit(1);
  }
}

// Start verification
runVerification();
