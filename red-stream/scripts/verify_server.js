#!/usr/bin/env node

const net = require('net');
const fs = require('fs');
const path = require('path');

// Read MCP settings
const settingsPath = path.join(process.env.HOME, '.vscode-server/data/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json');
const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));

// Server details
const serverName = 'red-stream';
const serverConfig = settings.mcpServers[serverName];

if (!serverConfig) {
    console.error(`Server ${serverName} not found in MCP settings`);
    process.exit(1);
}

console.log('Server configuration:', JSON.stringify(serverConfig, null, 2));

// Test Redis connection
const redis = require('redis');
const client = redis.createClient({
    url: `redis://${serverConfig.env.REDIS_HOST}:${serverConfig.env.REDIS_PORT}`
});

async function verifyRedis() {
    try {
        await client.connect();
        console.log('Redis connection successful');
        
        // Test basic operations
        await client.set('mcp:test:key', 'test');
        const value = await client.get('mcp:test:key');
        console.log('Redis test operation successful:', value);
        
        // Test stream operations
        const streamId = await client.xAdd('mcp:test:stream', '*', { test: 'data' });
        console.log('Stream operation successful:', streamId);
        
        await client.quit();
        console.log('Redis verification complete');
    } catch (error) {
        console.error('Redis verification failed:', error);
        process.exit(1);
    }
}

// Verify server process
async function verifyProcess() {
    try {
        const serverPath = serverConfig.args[0];
        if (!fs.existsSync(serverPath)) {
            console.error('Server executable not found:', serverPath);
            process.exit(1);
        }
        console.log('Server executable exists');

        // Check if process is running
        const isRunning = require('is-running');
        const ps = require('ps-node');
        
        ps.lookup({
            command: 'node',
            arguments: serverPath
        }, (err, resultList) => {
            if (err) {
                console.error('Error checking process:', err);
                process.exit(1);
            }

            console.log('Running processes:', resultList);
            
            if (resultList.length === 0) {
                console.log('Server process not running');
            } else {
                console.log('Server process running:', resultList[0].pid);
            }
        });
    } catch (error) {
        console.error('Process verification failed:', error);
        process.exit(1);
    }
}

// Run verifications
async function main() {
    console.log('Starting server verification...');
    await verifyRedis();
    await verifyProcess();
}

main().catch(console.error);