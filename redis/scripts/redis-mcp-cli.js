#!/usr/bin/env node

/**
 * Redis MCP CLI
 * 
 * A command-line tool for Redis operations that uses the same interface as the MCP server.
 * This provides an alternative when the MCP server is having connection issues.
 */

const { program } = require('commander');
const RedisDirectAdapter = require('../src/redis-streams/direct-adapter');
const readline = require('readline');
const fs = require('fs');
const path = require('path');

// Create adapter instance
const adapter = new RedisDirectAdapter();

// Create CLI program
program
  .name('redis-mcp-cli')
  .description('CLI for Redis operations when MCP has connection issues')
  .version('1.0.0');

// Basic Redis operations
program
  .command('set <key> <value>')
  .description('Set a key-value pair')
  .option('-e, --expire <seconds>', 'Expiration time in seconds')
  .action(async (key, value, options) => {
    try {
      const result = await adapter.set(key, value, options.expire);
      console.log(`Successfully set key: ${key}`);
      await adapter.close();
    } catch (error) {
      console.error('Error:', error.message);
      await adapter.close();
      process.exit(1);
    }
  });

program
  .command('get <key>')
  .description('Get a value by key')
  .action(async (key) => {
    try {
      const value = await adapter.get(key);
      console.log(value);
      await adapter.close();
    } catch (error) {
      console.error('Error:', error.message);
      await adapter.close();
      process.exit(1);
    }
  });

program
  .command('delete <key>')
  .description('Delete a key')
  .action(async (key) => {
    try {
      await adapter.del(key);
      console.log(`Successfully deleted key: ${key}`);
      await adapter.close();
    } catch (error) {
      console.error('Error:', error.message);
      await adapter.close();
      process.exit(1);
    }
  });

program
  .command('list [pattern]')
  .description('List keys matching a pattern (default: *)')
  .action(async (pattern = '*') => {
    try {
      const keys = await adapter.list(pattern);
      if (keys.length > 0) {
        console.log('Found keys:');
        keys.forEach(key => console.log(key));
      } else {
        console.log('No keys found matching pattern');
      }
      await adapter.close();
    } catch (error) {
      console.error('Error:', error.message);
      await adapter.close();
      process.exit(1);
    }
  });

// Stream operations
program
  .command('stream-publish <stream>')
  .description('Publish a message to a Redis stream')
  .option('-m, --message <json>', 'Message as JSON string')
  .option('-f, --file <path>', 'JSON file containing message')
  .option('-l, --maxlen <number>', 'Maximum stream length')
  .action(async (stream, options) => {
    try {
      let message;
      if (options.file) {
        const filePath = path.resolve(options.file);
        message = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      } else if (options.message) {
        message = JSON.parse(options.message);
      } else {
        console.error('Error: Either --message or --file is required');
        await adapter.close();
        process.exit(1);
      }
      
      const msgOptions = {};
      if (options.maxlen) {
        msgOptions.maxlen = parseInt(options.maxlen);
      }
      
      const messageId = await adapter.streamPublish(stream, message, msgOptions);
      console.log(`Successfully published message to stream ${stream} with ID ${messageId}`);
      await adapter.close();
    } catch (error) {
      console.error('Error:', error.message);
      await adapter.close();
      process.exit(1);
    }
  });

program
  .command('stream-read <stream>')
  .description('Read messages from a Redis stream')
  .option('-c, --count <number>', 'Number of messages to read', '10')
  .option('-r, --reverse', 'Read in reverse order')
  .action(async (stream, options) => {
    try {
      const count = parseInt(options.count);
      const messages = await adapter.streamRead(stream, {
        count,
        reverse: options.reverse
      });
      
      if (messages.length > 0) {
        console.log(`Read ${messages.length} messages from stream ${stream}:`);
        console.log(JSON.stringify(messages, null, 2));
      } else {
        console.log(`No messages found in stream ${stream}`);
      }
      await adapter.close();
    } catch (error) {
      console.error('Error:', error.message);
      await adapter.close();
      process.exit(1);
    }
  });

program
  .command('list-streams [pattern]')
  .description('List all Redis streams matching a pattern (default: *)')
  .action(async (pattern = '*') => {
    try {
      const streams = await adapter.listStreams(pattern);
      if (streams.length > 0) {
        console.log('Found streams:');
        streams.forEach(stream => console.log(stream));
      } else {
        console.log('No streams found matching pattern');
      }
      await adapter.close();
    } catch (error) {
      console.error('Error:', error.message);
      await adapter.close();
      process.exit(1);
    }
  });

program
  .command('create-consumer-group <stream> <group>')
  .description('Create a consumer group for a Redis stream')
  .option('-s, --start-id <id>', 'ID to start reading from', '$')
  .option('-m, --mkstream', 'Create stream if it doesn\'t exist')
  .action(async (stream, group, options) => {
    try {
      await adapter.createConsumerGroup(stream, group, {
        startId: options.startId,
        mkstream: options.mkstream
      });
      console.log(`Successfully created consumer group ${group} for stream ${stream}`);
      await adapter.close();
    } catch (error) {
      console.error('Error:', error.message);
      await adapter.close();
      process.exit(1);
    }
  });

program
  .command('read-group <stream> <group> <consumer>')
  .description('Read messages from a stream as part of a consumer group')
  .option('-c, --count <number>', 'Number of messages to read', '10')
  .option('-b, --block <ms>', 'Block for this many milliseconds', '2000')
  .option('-n, --no-ack', 'Skip message acknowledgment')
  .option('-i, --id <id>', 'ID to start reading from', '>')
  .action(async (stream, group, consumer, options) => {
    try {
      const messages = await adapter.readGroup(stream, group, consumer, {
        count: parseInt(options.count),
        block: parseInt(options.block),
        noAck: !options.ack,
        id: options.id
      });
      
      if (messages.length > 0) {
        console.log(`Read ${messages.length} messages from group ${group} on stream ${stream}:`);
        console.log(JSON.stringify(messages, null, 2));
      } else {
        console.log(`No messages available for group ${group} on stream ${stream}`);
      }
      await adapter.close();
    } catch (error) {
      console.error('Error:', error.message);
      await adapter.close();
      process.exit(1);
    }
  });

program
  .command('read-multiple-streams <streams...>')
  .description('Read from multiple streams simultaneously')
  .option('-c, --count <number>', 'Number of messages per stream', '10')
  .option('-b, --block <ms>', 'Block for this many milliseconds', '2000')
  .option('-i, --id <id>', 'ID to start reading from', '0')
  .action(async (streams, options) => {
    try {
      const results = await adapter.readMultipleStreams(streams, {
        count: parseInt(options.count),
        block: parseInt(options.block),
        id: options.id
      });
      
      console.log('Results from multiple streams:');
      console.log(JSON.stringify(results, null, 2));
      await adapter.close();
    } catch (error) {
      console.error('Error:', error.message);
      await adapter.close();
      process.exit(1);
    }
  });

// Task management
program
  .command('create-task')
  .description('Create a new task')
  .option('-t, --title <title>', 'Task title', 'New Task')
  .option('-d, --description <desc>', 'Task description')
  .option('-p, --priority <priority>', 'Task priority (low/medium/high/critical)', 'medium')
  .option('-a, --assignee <assignee>', 'Task assignee')
  .option('-n, --nova-id <id>', 'Origin Nova ID', '001')
  .option('-j, --json <json>', 'Task data as JSON string')
  .option('-f, --file <path>', 'JSON file containing task data')
  .action(async (options) => {
    try {
      let taskData;
      
      if (options.file) {
        const filePath = path.resolve(options.file);
        taskData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      } else if (options.json) {
        taskData = JSON.parse(options.json);
      } else {
        taskData = {
          title: options.title,
          description: options.description,
          priority: options.priority,
          assignee: options.assignee,
          origin_nova_id: options.novaId,
          execution_trace_id: require('uuid').v4()
        };
      }
      
      const task = await adapter.createTask(taskData);
      console.log(`Successfully created task with ID: ${task.id}`);
      await adapter.close();
    } catch (error) {
      console.error('Error:', error.message);
      await adapter.close();
      process.exit(1);
    }
  });

// Parse arguments and execute
program.parse(process.argv);

// If no arguments, show help
if (process.argv.length === 2) {
  program.help();
}
