#!/usr/bin/env node

/**
 * Redis Direct Adapter
 * 
 * This module provides direct Redis operations that map to the MCP tool interface.
 * It's a fallback mechanism when the MCP server connection is having issues.
 */

const Redis = require('ioredis');
const { v4: uuidv4 } = require('uuid');

class RedisDirectAdapter {
    constructor(config = {}) {
        this.config = {
            host: config.host || '127.0.0.1',
            port: config.port || 7000,
            password: config.password || 'd5d7817937232ca5',
            retryStrategy: (times) => {
                if (times > 10) return null; // Stop retrying
                return Math.min(times * 100, 3000); // Max 3s delay
            },
            ...config
        };
        
        this.client = new Redis.Cluster([
            { host: this.config.host, port: this.config.port },
            { host: this.config.host, port: 7001 },
            { host: this.config.host, port: 7002 }
        ], {
            redisOptions: {
                password: this.config.password,
                enableReadyCheck: true
            },
            scaleReads: 'slave',
            maxRedirections: 16,
            retryStrategy: this.config.retryStrategy
        });
        
        this.client.on('error', (err) => {
            console.error('Redis Error:', err);
        });
        
        this.client.on('connect', () => {
            console.log('Connected to Redis');
        });
    }
    
    async close() {
        await this.client.quit();
    }
    
    // Direct operations that map to MCP tools
    
    // Basic operations
    async set(key, value, expireSeconds) {
        if (expireSeconds) {
            return await this.client.set(key, value, 'EX', expireSeconds);
        }
        return await this.client.set(key, value);
    }
    
    async get(key) {
        return await this.client.get(key);
    }
    
    async del(key) {
        if (Array.isArray(key)) {
            return await this.client.del(...key);
        }
        return await this.client.del(key);
    }
    
    async list(pattern = '*') {
        return await this.client.keys(pattern);
    }
    
    // Stream operations
    async streamPublish(stream, message, options = {}) {
        // Convert message object to key-value pairs
        const entries = [];
        for (const [key, value] of Object.entries(message)) {
            entries.push(key, JSON.stringify(value));
        }
        
        if (options.maxlen) {
            return await this.client.xadd(stream, 'MAXLEN', '~', options.maxlen, '*', ...entries);
        }
        
        return await this.client.xadd(stream, '*', ...entries);
    }
    
    async streamRead(stream, options = {}) {
        const count = options.count || 10;
        const start = options.start || '-';
        const end = options.end || '+';
        
        const messages = await this.client.xrange(stream, start, end, 'COUNT', count);
        
        // Transform messages to a more usable format
        return messages.map(([id, fields]) => {
            const data = {};
            for (let i = 0; i < fields.length; i += 2) {
                const key = fields[i];
                const value = fields[i + 1];
                try {
                    data[key] = JSON.parse(value);
                } catch (e) {
                    data[key] = value;
                }
            }
            return { id, data };
        });
    }
    
    async listStreams(pattern = '*') {
        const keys = await this.client.keys(pattern);
        const streams = [];
        
        for (const key of keys) {
            const type = await this.client.type(key);
            if (type === 'stream') {
                streams.push(key);
            }
        }
        
        return streams;
    }
    
    async createConsumerGroup(stream, group, options = {}) {
        const startId = options.startId || '$';
        const args = ['CREATE', stream, group, startId];
        
        if (options.mkstream) {
            args.push('MKSTREAM');
        }
        
        try {
            return await this.client.xgroup(...args);
        } catch (error) {
            // Check if group already exists
            if (error.message && error.message.includes('BUSYGROUP')) {
                return 'OK (Group already exists)';
            }
            throw error;
        }
    }
    
    async readGroup(stream, group, consumer, options = {}) {
        const args = [
            'GROUP', group, consumer
        ];
        
        if (options.count) {
            args.push('COUNT', options.count);
        }
        
        if (options.block) {
            args.push('BLOCK', options.block);
        }
        
        if (options.noAck) {
            args.push('NOACK');
        }
        
        args.push('STREAMS', stream, options.id || '>');
        
        const result = await this.client.xreadgroup(...args);
        
        if (!result) return [];
        
        // Transform the nested array structure to a more usable format
        const messages = [];
        for (const [streamName, entries] of result) {
            for (const [id, fields] of entries) {
                const data = {};
                for (let i = 0; i < fields.length; i += 2) {
                    const key = fields[i];
                    const value = fields[i + 1];
                    try {
                        data[key] = JSON.parse(value);
                    } catch (e) {
                        data[key] = value;
                    }
                }
                messages.push({ id, stream: streamName, data });
            }
        }
        
        return messages;
    }
    
    async readMultipleStreams(streams, options = {}) {
        const args = [];
        
        if (options.count) {
            args.push('COUNT', options.count);
        }
        
        if (options.block) {
            args.push('BLOCK', options.block);
        }
        
        args.push('STREAMS', ...streams);
        
        const ids = Array(streams.length).fill(options.id || '0');
        args.push(...ids);
        
        const result = await this.client.xread(...args);
        
        if (!result) return {};
        
        // Transform the nested array structure to a more usable format
        const streamMessages = {};
        
        for (const [streamName, entries] of result) {
            streamMessages[streamName] = entries.map(([id, fields]) => {
                const data = {};
                for (let i = 0; i < fields.length; i += 2) {
                    const key = fields[i];
                    const value = fields[i + 1];
                    try {
                        data[key] = JSON.parse(value);
                    } catch (e) {
                        data[key] = value;
                    }
                }
                return { id, data };
            });
        }
        
        return streamMessages;
    }
    
    // State management
    async setState(key, value, ttl = null) {
        const data = JSON.stringify(value);
        if (ttl) {
            await this.client.set(key, data, 'EX', ttl);
        } else {
            await this.client.set(key, data);
        }
        return { success: true };
    }
    
    async getState(key) {
        const data = await this.client.get(key);
        if (!data) {
            throw new Error(`State not found for key: ${key}`);
        }
        
        const ttl = await this.client.ttl(key);
        
        return {
            value: JSON.parse(data),
            ttl: ttl === -1 ? null : ttl
        };
    }
    
    async deleteState(key) {
        await this.client.del(key);
        return { success: true };
    }
    
    // Task management
    async createTask(taskData) {
        const taskId = taskData.task_id || `task_${Date.now()}_${uuidv4()}`;
        const timestamp = new Date().toISOString();
        
        // Prepare task object
        const task = {
            ...taskData,
            task_id: taskId,
            status: taskData.status || 'new',
            created_at: timestamp,
            updated_at: timestamp
        };
        
        // Publish task to stream
        await this.streamPublish('nova:task:boomerang:tasks', task);
        
        return { id: taskId };
    }
    
    async getTask(taskId) {
        const messages = await this.streamRead('nova:task:boomerang:tasks', {
            count: 100,
            reverse: true
        });
        
        const taskMessages = messages.filter(msg => msg.data.task_id === taskId);
        
        if (taskMessages.length === 0) {
            throw new Error(`Task with ID ${taskId} not found`);
        }
        
        return taskMessages[0].data;
    }
    
    async updateTask(taskId, updates) {
        const task = await this.getTask(taskId);
        const updatedTask = {
            ...task,
            ...updates,
            updated_at: new Date().toISOString()
        };
        
        await this.streamPublish('nova:task:boomerang:tasks', updatedTask);
        
        return updatedTask;
    }
    
    async completeTask(taskId, result) {
        const task = await this.getTask(taskId);
        const completedTask = {
            ...task,
            status: 'completed',
            result,
            completed_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        };
        
        await this.streamPublish('nova:task:boomerang:tasks', completedTask);
        
        return completedTask;
    }
    
    async listTasks(pattern = null, status = null) {
        const messages = await this.streamRead('nova:task:boomerang:tasks', {
            count: 100,
            reverse: true
        });
        
        let tasks = messages.map(msg => msg.data);
        
        if (pattern) {
            tasks = tasks.filter(task => task.task_id.includes(pattern));
        }
        
        if (status) {
            tasks = tasks.filter(task => task.status === status);
        }
        
        return tasks;
    }
}

module.exports = RedisDirectAdapter;

// If script is run directly, run a test
if (require.main === module) {
    async function test() {
        const adapter = new RedisDirectAdapter();
        
        try {
            console.log('\n=== Testing Basic Operations ===');
            
            console.log('\nSetting test key...');
            await adapter.set('test:direct:key', 'test-value');
            
            console.log('\nGetting test key...');
            const value = await adapter.get('test:direct:key');
            console.log('Value:', value);
            
            console.log('\n=== Testing Stream Operations ===');
            
            console.log('\nPublishing to test stream...');
            const msgId = await adapter.streamPublish('test:direct:stream', {
                type: 'test',
                data: { hello: 'world' },
                timestamp: new Date().toISOString()
            });
            console.log('Message ID:', msgId);
            
            console.log('\nReading from test stream...');
            const messages = await adapter.streamRead('test:direct:stream');
            console.log('Messages:', JSON.stringify(messages, null, 2));
            
            console.log('\nListing streams...');
            const streams = await adapter.listStreams('test:*');
            console.log('Streams:', streams);
            
            console.log('\n=== Testing Consumer Groups ===');
            
            console.log('\nCreating consumer group...');
            await adapter.createConsumerGroup('test:direct:stream', 'test-group', { mkstream: true });
            
            console.log('\nReading as consumer group...');
            const groupMessages = await adapter.readGroup('test:direct:stream', 'test-group', 'test-consumer', { count: 10 });
            console.log('Group Messages:', JSON.stringify(groupMessages, null, 2));
            
            console.log('\n=== Testing Task Management ===');
            
            console.log('\nCreating task...');
            const task = await adapter.createTask({
                title: 'Test Task',
                description: 'This is a test task',
                priority: 'medium',
                origin_nova_id: '001',
                execution_trace_id: uuidv4()
            });
            console.log('Task:', task);
            
            console.log('\nGetting task...');
            const taskDetails = await adapter.getTask(task.id);
            console.log('Task Details:', JSON.stringify(taskDetails, null, 2));
            
            console.log('\nUpdating task...');
            const updatedTask = await adapter.updateTask(task.id, {
                status: 'in_progress',
                progress: 50
            });
            console.log('Updated Task:', JSON.stringify(updatedTask, null, 2));
            
            console.log('\nCompleting task...');
            const completedTask = await adapter.completeTask(task.id, { success: true });
            console.log('Completed Task:', JSON.stringify(completedTask, null, 2));
            
            console.log('\nListing tasks...');
            const tasks = await adapter.listTasks();
            console.log('Tasks:', JSON.stringify(tasks, null, 2));
            
            console.log('\n=== Testing State Management ===');
            
            console.log('\nSetting state...');
            await adapter.setState('test:direct:state', {
                mode: 'active',
                settings: { theme: 'dark' },
                updated: new Date().toISOString()
            });
            
            console.log('\nGetting state...');
            const state = await adapter.getState('test:direct:state');
            console.log('State:', JSON.stringify(state, null, 2));
            
            console.log('\nAll tests completed successfully!');
        } catch (error) {
            console.error('Test failed:', error);
        } finally {
            await adapter.close();
        }
    }
    
    test();
}
