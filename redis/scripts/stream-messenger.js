#!/usr/bin/env node

import { RedStream } from "../src/redis-streams/build/redstream.js";

// Initialize RedStream
const redStream = new RedStream({
    nodes: [
        { host: '127.0.0.1', port: 7000 },
        { host: '127.0.0.1', port: 7001 },
        { host: '127.0.0.1', port: 7002 }
    ],
    clusterOptions: {
        redisOptions: {
            password: 'd5d7817937232ca5',
            showFriendlyErrorStack: true
        },
        slotsRefreshTimeout: 2000,
        enableReadyCheck: true,
        scaleReads: 'slave',
        maxRedirections: 16,
        retryDelayOnFailover: 100,
        retryDelayOnClusterDown: 200,
        retryDelayOnTryAgain: 100,
        // Ensure password is set for all nodes
        dnsLookup: (address, callback) => callback(null, address),
        redisOptions: {
            password: 'd5d7817937232ca5',
            tls: {},
            showFriendlyErrorStack: true
        }
    },
    serverIdentity: 'stream_messenger_cli',
    roles: ['task_read', 'task_write', 'system_read', 'system_write']
});

// CLI Help Text
const HELP_TEXT = `
Stream Messenger - Redis Stream CLI Tool

For detailed naming convention documentation, see: docs/redis-naming-convention.md

Usage:
  stream-messenger <command> [options]

Commands:
  tools                                             List available commands and options
  list [--pattern <pattern>] [--format json|table]    List available streams
  write <stream> --type <type> --content <message>    Write message to stream
    [--priority normal|high|critical]
  read <stream> [--count <n>] [--reverse]            Read messages from stream
    [--watch]                                        Watch for new messages
  monitor <stream...>                                Monitor multiple streams
    [--count <n>] [--watch]                         Watch mode for multiple streams

Examples:
  # List all streams
  stream-messenger list

  # List streams with pattern
  stream-messenger list --pattern "nova:devops:*"

  # Write message (must follow nova:domain:category:name format)
  stream-messenger write nova:devops:general --type update --content "System update"

  # Read messages
  stream-messenger read nova:devops:general --count 10

  # Monitor multiple streams
  stream-messenger monitor nova:devops:general nova:broadcast:all --watch
`;

// Parse command line arguments
function parseArgs() {
    const args = process.argv.slice(2);
    const command = args[0];
    const options = {};
    
    for (let i = 1; i < args.length; i++) {
        if (args[i].startsWith('--')) {
            const key = args[i].slice(2);
            const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true;
            options[key] = value;
            if (value !== true) i++;
        } else if (!options.streams) {
            options.streams = [args[i]];
        } else {
            options.streams.push(args[i]);
        }
    }
    
    return { command, options };
}

// Format output
function formatTable(data) {
    if (!data || !data.length) return 'No data available';
    
    const headers = Object.keys(data[0]);
    const rows = data.map(item => headers.map(header => String(item[header] || '')));
    
    // Calculate column widths
    const widths = headers.map((header, i) => {
        const columnItems = [header, ...rows.map(row => row[i])];
        return Math.max(...columnItems.map(item => item.length));
    });
    
    // Build table
    const separator = widths.map(w => '-'.repeat(w)).join('-+-');
    const header = headers.map((h, i) => h.padEnd(widths[i])).join(' | ');
    const body = rows.map(row => 
        row.map((cell, i) => cell.padEnd(widths[i])).join(' | ')
    );
    
    return [header, separator, ...body].join('\n');
}

// Interactive menu
async function showMenu() {
    console.log(`
Redis Stream Messenger - Interactive Menu

Stream Operations:
1) List all streams
2) List streams with pattern
3) Read messages from stream
4) Write message to stream
5) Monitor multiple streams
6) Add new stream with metadata

Stream Management:
7) Get stream health metrics
8) List consumer groups
9) Get pending messages info

State Management:
10) Set state
11) Get state
12) Delete state

Other:
13) Show help
0) Exit

Choose an option: `);

    const readline = (await import('readline')).default;
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    const answer = await new Promise(resolve => rl.question('', resolve));
    rl.close();
    return answer;
}

async function getInput(prompt) {
    const readline = (await import('readline')).default;
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    const answer = await new Promise(resolve => rl.question(prompt, resolve));
    rl.close();
    return answer;
}

async function main() {
    try {
        // Check if command line arguments are provided
        if (process.argv.length > 2) {
            const { command, options } = parseArgs();
            await handleCommand(command, options);
            return;
        }

        // Interactive mode
        while (true) {
            const choice = await showMenu();
            
            switch (choice) {
                case '0':
                    console.log('Exiting...');
                    return;
                
                case '1': {
                    const streams = await redStream.listStreams('*');
                    console.log('\nAvailable streams:');
                    streams.forEach(stream => console.log(`- ${stream}`));
                    break;
                }

                case '2': {
                    const pattern = await getInput('Enter pattern (e.g., "nova:devops:*"): ');
                    const streams = await redStream.listStreams(pattern);
                    console.log('\nMatching streams:');
                    streams.forEach(stream => console.log(`- ${stream}`));
                    break;
                }

                case '3': {
                    const stream = await getInput('Enter stream name: ');
                    const count = await getInput('Enter number of messages (default 10): ');
                    const reverse = (await getInput('Read in reverse order? (y/N): ')).toLowerCase() === 'y';
                    
                    const messages = await redStream.readMessages(stream, {
                        count: count ? parseInt(count) : 10,
                        reverse
                    });
                    console.log('\nMessages:', JSON.stringify(messages, null, 2));
                    break;
                }

                case '4': {
                    const stream = await getInput('Enter stream name: ');
                    const type = await getInput('Enter message type: ');
                    const content = await getInput('Enter message content: ');
                    const priority = await getInput('Enter priority (normal/high/critical) [normal]: ');
                    
                    const messageId = await redStream.publishMessage(stream, {
                        type,
                        content,
                        priority: priority || 'normal'
                    });
                    console.log(`\nMessage published with ID: ${messageId}`);
                    break;
                }

                case '5': {
                    const streamsInput = await getInput('Enter stream names (space-separated): ');
                    const count = await getInput('Enter number of messages per stream (default 10): ');
                    const watch = (await getInput('Watch for new messages? (y/N): ')).toLowerCase() === 'y';
                    
                    const streams = streamsInput.split(' ').filter(Boolean);
                    
                    async function monitorStreams() {
                        const results = {};
                        for (const stream of streams) {
                            const messages = await redStream.readMessages(stream, {
                                count: count ? parseInt(count) : 10,
                                reverse: true
                            });
                            if (messages.length > 0) {
                                results[stream] = messages;
                            }
                        }
                        if (Object.keys(results).length > 0) {
                            console.log('\nNew messages:', JSON.stringify(results, null, 2));
                        }
                    }

                    await monitorStreams();
                    
                    if (watch) {
                        console.log('\nWatching for new messages (Ctrl+C to exit)...');
                        setInterval(monitorStreams, 2000);
                    }
                    break;
                }

                case '6': {
                    const stream = await getInput('Enter stream name: ');
                    const description = await getInput('Enter stream description (optional): ');
                    const owner = await getInput('Enter stream owner (optional): ');
                    
                    const result = await streamsIntegration.addStream(stream, {
                        description,
                        owner
                    });
                    console.log('\nStream created:', JSON.stringify(result, null, 2));
                    break;
                }

                case '7': {
                    const stream = await getInput('Enter stream name: ');
                    const health = await streamsIntegration.getStreamHealth(stream);
                    console.log('\nStream health:', JSON.stringify(health, null, 2));
                    break;
                }

                case '8': {
                    const stream = await getInput('Enter stream name: ');
                    const groups = await redStream.listConsumerGroups(stream);
                    console.log('\nConsumer groups:', JSON.stringify(groups, null, 2));
                    break;
                }

                case '9': {
                    const stream = await getInput('Enter stream name: ');
                    const group = await getInput('Enter consumer group name: ');
                    const info = await redStream.getPendingInfo(stream, group);
                    console.log('\nPending messages info:', JSON.stringify(info, null, 2));
                    break;
                }

                case '10': {
                    const key = await getInput('Enter state key: ');
                    const value = await getInput('Enter state value (JSON): ');
                    const ttl = await getInput('Enter TTL in seconds (optional): ');
                    
                    await redStream.setState(key, JSON.parse(value), ttl ? parseInt(ttl) : undefined);
                    console.log('\nState set successfully');
                    break;
                }

                case '11': {
                    const key = await getInput('Enter state key: ');
                    const state = await redStream.getState(key);
                    console.log('\nState:', JSON.stringify(state, null, 2));
                    break;
                }

                case '12': {
                    const key = await getInput('Enter state key: ');
                    await redStream.deleteState(key);
                    console.log('\nState deleted successfully');
                    break;
                }

                case '13':
                    console.log(HELP_TEXT);
                    break;

                default:
                    console.log('\nInvalid option. Please try again.');
            }

            // Add a pause between operations in interactive mode
            if (choice !== '0') {
                await getInput('\nPress Enter to continue...');
                console.clear();
            }
        }
    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    } finally {
        if (!process.argv.includes('--watch')) {
            await redStream.close();
        }
    }
}

async function handleCommand(command, options) {
    try {
        switch (command) {
            case 'tools': {
                console.log(HELP_TEXT);
                break;
            }
            case 'list': {
                const streams = await redStream.listStreams(options.pattern || '*');
                const output = streams.map(stream => ({
                    stream,
                    format: stream.includes(':') ? 'new' : 'legacy'
                }));
                
                if (options.format === 'table') {
                    console.log(formatTable(output));
                } else {
                    console.log(JSON.stringify(output, null, 2));
                }
                break;
            }

            case 'write': {
                if (!options.streams?.[0] || !options.type || !options.content) {
                    console.error('Error: stream, type, and content are required');
                    console.log(HELP_TEXT);
                    process.exit(1);
                }

                // Validate stream name format (allow both legacy and new format)
                const legacyStreamRegex = /^[a-z]+\.[a-z0-9_-]+(\.[a-z0-9_-]+)*$/;
                const newStreamRegex = /^nova:(system|task|agent|user|memory|devops|broadcast):[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+$/;
                if (!legacyStreamRegex.test(options.streams[0]) && !newStreamRegex.test(options.streams[0])) {
                    console.error('Error: Invalid stream name format.');
                    console.error('Must follow either:');
                    console.error('  Legacy format: domain.name.direct (e.g. devops.dev2.direct)');
                    console.error('  New format: nova:domain:category:name (e.g. nova:devops:general)');
                    process.exit(1);
                }

                const message = {
                    type: options.type,
                    content: options.content,
                    priority: options.priority || 'normal'
                };

                // Support multiple streams in write command
                const results = await Promise.all(options.streams.map(async (stream) => {
                    const messageId = await redStream.publishMessage(stream, message);
                    return { stream, messageId };
                }));

                for (const result of results) {
                    console.log(`Message published to ${result.stream} with ID: ${result.messageId}`);
                }
                break;
            }

            case 'read': {
                if (!options.streams?.[0]) {
                    console.error('Error: stream is required');
                    console.log(HELP_TEXT);
                    process.exit(1);
                }

                // Validate stream name format (allow both legacy and new format)
                const legacyStreamRegex = /^[a-z]+\.[a-z0-9_-]+(\.[a-z0-9_-]+)*$/;
                const newStreamRegex = /^nova:(system|task|agent|user|memory|devops|broadcast):[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+$/;
                if (!legacyStreamRegex.test(options.streams[0]) && !newStreamRegex.test(options.streams[0])) {
                    console.error('Error: Invalid stream name format.');
                    console.error('Must follow either:');
                    console.error('  Legacy format: domain.name.direct (e.g. devops.dev2.direct)');
                    console.error('  New format: nova:domain:category:name (e.g. nova:devops:general)');
                    process.exit(1);
                }

                async function readStream() {
                    const messages = await redStream.readMessages(options.streams[0], {
                        count: options.count ? parseInt(options.count) : 10,
                        reverse: options.reverse !== 'false'
                    });
                    console.log(JSON.stringify(messages, null, 2));
                }

                await readStream();
                
                if (options.watch) {
                    console.log('\nWatching for new messages (Ctrl+C to exit)...\n');
                    setInterval(readStream, 2000);
                }
                break;
            }

            case 'monitor': {
                if (!options.streams?.length) {
                    console.error('Error: at least one stream is required');
                    console.log(HELP_TEXT);
                    process.exit(1);
                }

                // Validate stream name format (allow both legacy and new format)
                const legacyStreamRegex = /^[a-z]+\.[a-z0-9_-]+(\.[a-z0-9_-]+)*$/;
                const newStreamRegex = /^nova:(system|task|agent|user|memory|devops|broadcast):[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+$/;
                for (const stream of options.streams) {
                    if (!legacyStreamRegex.test(stream) && !newStreamRegex.test(stream)) {
                        console.error(`Error: Invalid stream name format for "${stream}".`);
                        console.error('Must follow either:');
                        console.error('  Legacy format: domain.name.direct (e.g. devops.dev2.direct)');
                        console.error('  New format: nova:domain:category:name (e.g. nova:devops:general)');
                        process.exit(1);
                    }
                }

                async function monitorStreams() {
                    const results = {};
                    for (const stream of options.streams) {
                        const messages = await redStream.readMessages(stream, {
                            count: options.count ? parseInt(options.count) : 10,
                            reverse: true
                        });
                        if (messages.length > 0) {
                            results[stream] = messages;
                        }
                    }
                    if (Object.keys(results).length > 0) {
                        console.log(JSON.stringify(results, null, 2));
                    }
                }

                await monitorStreams();
                
                if (options.watch) {
                    console.log('\nWatching streams (Ctrl+C to exit)...\n');
                    setInterval(monitorStreams, 2000);
                }
                break;
            }

            default:
                console.error('Unknown command:', command);
                console.log(HELP_TEXT);
                process.exit(1);
        }
    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    } finally {
        if (!process.argv.includes('--watch')) {
            await redStream.close();
            process.exit(0);
        }
    }
}

// Handle Ctrl+C in watch mode
process.on('SIGINT', async () => {
    console.log('\nClosing connections...');
    await redStream.close();
    process.exit(0);
});

// Handle other termination signals
process.on('SIGTERM', async () => {
    console.log('\nReceived SIGTERM, closing connections...');
    await redStream.close();
    process.exit(0);
});

process.on('uncaughtException', async (error) => {
    console.error('\nUncaught exception:', error);
    await redStream.close();
    process.exit(1);
});

process.on('unhandledRejection', async (reason, promise) => {
    console.error('\nUnhandled rejection at:', promise, 'reason:', reason);
    await redStream.close();
    process.exit(1);
});

main();
