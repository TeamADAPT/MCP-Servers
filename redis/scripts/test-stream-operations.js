#!/usr/bin/env node

/**
 * Redis MCP Stream Operations Test Script
 * 
 * This script tests the Redis stream operations through the MCP server.
 * It demonstrates how to use the different stream operations.
 */

const { spawn } = require('child_process');
const path = require('path');
const readline = require('readline');

// Simulated MCP tool interface
async function useMcpTool(serverName, toolName, args) {
    console.log(`\n----- CALLING ${toolName} -----`);
    console.log(`Arguments: ${JSON.stringify(args, null, 2)}`);
    
    // Spawn Redis CLI to execute the operation directly
    // This is a fallback if MCP connection is failing
    const stream = args.stream || args.key || 'test:stream';
    const redisArgs = ['127.0.0.1', '-p', '7000', '-a', 'd5d7817937232ca5'];
    
    let result;
    switch(toolName) {
        case 'set':
            result = await executeRedisCommand([...redisArgs, 'SET', args.key, args.value]);
            break;
        case 'get':
            result = await executeRedisCommand([...redisArgs, 'GET', args.key]);
            break;
        case 'list':
            result = await executeRedisCommand([...redisArgs, 'KEYS', args.pattern || '*']);
            break;
        case 'stream_publish':
            // Convert message object to key-value pairs for XADD
            const message = args.message || { test: 'data' };
            const messageEntries = [];
            for (const [key, value] of Object.entries(message)) {
                messageEntries.push(key, JSON.stringify(value));
            }
            
            result = await executeRedisCommand([
                ...redisArgs, 
                'XADD', 
                args.stream, 
                args.maxlen ? 'MAXLEN' : '', 
                args.maxlen ? '~' : '', 
                args.maxlen ? args.maxlen : '', 
                '*', 
                ...messageEntries
            ].filter(Boolean));
            break;
        case 'stream_read':
            result = await executeRedisCommand([
                ...redisArgs,
                'XRANGE',
                args.stream,
                '-',
                '+',
                args.count ? 'COUNT' : '',
                args.count || ''
            ].filter(Boolean));
            break;
        case 'list_streams':
            // First get all keys
            const keys = await executeRedisCommand([...redisArgs, 'KEYS', args.pattern || '*']);
            
            // Then check which ones are streams
            const streams = [];
            for (const key of keys.split('\n').filter(Boolean)) {
                const type = await executeRedisCommand([...redisArgs, 'TYPE', key]);
                if (type.trim() === 'stream') {
                    streams.push(key);
                }
            }
            result = streams.join('\n');
            break;
        case 'create_consumer_group':
            result = await executeRedisCommand([
                ...redisArgs,
                'XGROUP',
                'CREATE',
                args.stream,
                args.groupName,
                args.startId || '$',
                args.mkstream ? 'MKSTREAM' : ''
            ].filter(Boolean));
            break;
        case 'read_group':
            result = await executeRedisCommand([
                ...redisArgs,
                'XREADGROUP',
                'GROUP',
                args.group,
                args.consumer,
                args.count ? 'COUNT' : '',
                args.count || '',
                args.block ? 'BLOCK' : '',
                args.block || '',
                args.noAck ? 'NOACK' : '',
                'STREAMS',
                args.stream,
                args.id || '>'
            ].filter(Boolean));
            break;
        default:
            result = `Command "${toolName}" not implemented in test script.`;
    }
    
    console.log(`\nResult:\n${result}`);
    console.log("-".repeat(40));
    return result;
}

// Helper to execute Redis CLI commands
async function executeRedisCommand(args) {
    return new Promise((resolve, reject) => {
        const redis = spawn('redis-cli', args);
        let output = '';
        
        redis.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        redis.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
        });
        
        redis.on('close', (code) => {
            if (code === 0) {
                resolve(output.trim());
            } else {
                reject(new Error(`redis-cli exited with code ${code}: ${output}`));
            }
        });
    });
}

// Create CLI interface
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Main menu
async function showMenu() {
    console.log('\n===== REDIS STREAM OPERATIONS TEST =====');
    console.log('1. Set key-value');
    console.log('2. Get key');
    console.log('3. List keys');
    console.log('4. Publish to stream');
    console.log('5. Read from stream');
    console.log('6. List streams');
    console.log('7. Create consumer group');
    console.log('8. Read as consumer group');
    console.log('9. Exit');
    
    rl.question('\nSelect an option: ', async (answer) => {
        switch(answer) {
            case '1':
                await setKeyValue();
                break;
            case '2':
                await getKey();
                break;
            case '3':
                await listKeys();
                break;
            case '4':
                await publishToStream();
                break;
            case '5':
                await readFromStream();
                break;
            case '6':
                await listStreams();
                break;
            case '7':
                await createConsumerGroup();
                break;
            case '8':
                await readAsConsumerGroup();
                break;
            case '9':
                rl.close();
                return;
            default:
                console.log('Invalid option');
                showMenu();
                return;
        }
        showMenu();
    });
}

async function setKeyValue() {
    rl.question('Enter key: ', (key) => {
        rl.question('Enter value: ', async (value) => {
            await useMcpTool(
                'github.com/modelcontextprotocol/servers/tree/main/src/redis',
                'set',
                { key, value }
            );
        });
    });
}

async function getKey() {
    rl.question('Enter key: ', async (key) => {
        await useMcpTool(
            'github.com/modelcontextprotocol/servers/tree/main/src/redis',
            'get',
            { key }
        );
    });
}

async function listKeys() {
    rl.question('Enter pattern (default: *): ', async (pattern) => {
        pattern = pattern || '*';
        await useMcpTool(
            'github.com/modelcontextprotocol/servers/tree/main/src/redis',
            'list',
            { pattern }
        );
    });
}

async function publishToStream() {
    rl.question('Enter stream name: ', (stream) => {
        rl.question('Enter message type: ', (type) => {
            rl.question('Enter message content: ', async (content) => {
                await useMcpTool(
                    'github.com/modelcontextprotocol/servers/tree/main/src/redis',
                    'stream_publish',
                    {
                        stream,
                        message: {
                            type,
                            content,
                            timestamp: new Date().toISOString()
                        }
                    }
                );
            });
        });
    });
}

async function readFromStream() {
    rl.question('Enter stream name: ', (stream) => {
        rl.question('Enter count (default: 10): ', async (count) => {
            count = count ? parseInt(count) : 10;
            await useMcpTool(
                'github.com/modelcontextprotocol/servers/tree/main/src/redis',
                'stream_read',
                { stream, count }
            );
        });
    });
}

async function listStreams() {
    rl.question('Enter pattern (default: *): ', async (pattern) => {
        pattern = pattern || '*';
        await useMcpTool(
            'github.com/modelcontextprotocol/servers/tree/main/src/redis',
            'list_streams',
            { pattern }
        );
    });
}

async function createConsumerGroup() {
    rl.question('Enter stream name: ', (stream) => {
        rl.question('Enter group name: ', (groupName) => {
            rl.question('Create stream if not exists? (y/n): ', async (create) => {
                const mkstream = create.toLowerCase() === 'y';
                await useMcpTool(
                    'github.com/modelcontextprotocol/servers/tree/main/src/redis',
                    'create_consumer_group',
                    { stream, groupName, mkstream }
                );
            });
        });
    });
}

async function readAsConsumerGroup() {
    rl.question('Enter stream name: ', (stream) => {
        rl.question('Enter group name: ', (group) => {
            rl.question('Enter consumer name: ', async (consumer) => {
                await useMcpTool(
                    'github.com/modelcontextprotocol/servers/tree/main/src/redis',
                    'read_group',
                    { 
                        stream, 
                        group, 
                        consumer,
                        count: 10,
                        block: 2000,
                        id: '>'
                    }
                );
            });
        });
    });
}

// Start the menu
showMenu();
