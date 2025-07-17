"use strict";
/**
 * RedStream - Redis Streams Implementation for Nova Communication
 *
 * This module implements the Redis Streams Access Protocol as specified by Echo
 * for secure and standardized communication between MCP servers.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.RedStream = void 0;
/// <reference types="node" />
const Redis = __importStar(require("ioredis"));
// Mock JWT functions since we removed the dependency
const jwt = {
    sign: (payload, secret) => {
        return Buffer.from(JSON.stringify(payload)).toString('base64');
    },
    verify: (token, secret) => {
        try {
            return JSON.parse(Buffer.from(token, 'base64').toString());
        }
        catch {
            throw new Error('Invalid token');
        }
    }
};
// Constants for Stream Naming Conventions
const ADAPT_STREAM_PREFIX = 'nova:';
const ADAPT_STREAM_PATTERN = /^nova:(system|task|agent|user|memory):[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+$/;
const LEGACY_STREAM_PATTERN = /^[a-z]+\.[a-z0-9]+\.direct$/;
// Reserved domains and their governance
const RESERVED_DOMAINS = {
    system: 'MemCommsOps',
    task: 'CommsOps',
    agent: 'AgentOps',
    user: 'UserOps',
    memory: 'MemOps'
};
// Redis Cluster Configuration
const REDIS_NODES = [
    { host: 'redis-cluster.memcommsops.internal', port: 7000 },
    { host: 'redis-cluster.memcommsops.internal', port: 7001 },
    { host: 'redis-cluster.memcommsops.internal', port: 7002 }
];

const REDIS_CONFIG = {
    redisOptions: {
        username: 'mcp-server',
        password: 'd5d7817937232ca5',
        enableACLAuthentication: true,
        reconnectOnError: (err) => {
            // console.error(`Redis error: ${err}`); // Suppress this log too
            return true;
        },
        maxRetriesPerRequest: 10,
        connectTimeout: 10000,
        enableReadyCheck: true,
        showFriendlyErrorStack: false // Attempt to reduce logging
    },
    enableAutoPipelining: true,
    maxRedirections: 16,
    retryDelayOnFailover: 300,
    clusterRetryStrategy: (times) => {
        console.error(`Cluster retry attempt ${times}`);
        return Math.min(100 * times, 3000);
    }
};
/**
 * RedStream class for Redis Streams communication
 */
class RedStream {
    client;
    serverIdentity;
    jwtSecret;
    apiKey;
    roles;
    metrics;
    /**
     * Create a new RedStream instance
     *
     * @param options Configuration options for RedStream
     */
    constructor(options = {}) {
        // Initialize Redis cluster client
        const nodes = options.nodes || REDIS_NODES;
        const clusterOptions = options.clusterOptions || REDIS_CONFIG;
        // console.log("Creating Redis cluster client with config:", clusterOptions); // Suppress log
        // console.log("Using nodes:", nodes); // Suppress log
        this.client = new Redis.Cluster(nodes, clusterOptions);
        // Set server identity
        this.serverIdentity = options.serverIdentity || 'redis_mcp_server';
        // Security credentials
        this.jwtSecret = options.jwtSecret || 'default_secret_change_in_production';
        this.apiKey = options.apiKey || 'default_api_key_change_in_production';
        this.roles = options.roles || ['redis_mcp'];
        // Initialize metrics
        this.metrics = new StreamMetrics(this.serverIdentity);
        // Set up error handling
        this.setupErrorHandling();
        // Log initialization
        // console.log(`RedStream initialized for server: ${this.serverIdentity}`); // Suppress log
    }
    /**
     * Setup error handling for Redis Cluster
     */
    setupErrorHandling() {
        this.client.on('error', (err) => {
            // console.error('Redis Cluster Error:', err); // Suppress log
            this.metrics.recordError('cluster', err.message);
        });
        this.client.on('node error', (err, node) => {
            // console.error(`Redis Node ${node.host}:${node.port} Error:`, err); // Suppress log
            this.metrics.recordError('node', err.message);
        });
    }
    /**
     * Validate stream name against ADAPT conventions
     *
     * @param streamName Stream name to validate
     * @returns True if valid, throws error if invalid
     */
    validateStreamName(streamName) {
        if (!ADAPT_STREAM_PATTERN.test(streamName) && !LEGACY_STREAM_PATTERN.test(streamName)) {
            const error = new Error(`Stream name "${streamName}" does not follow naming conventions. Must be either:
      - ADAPT format: ${ADAPT_STREAM_PATTERN}
      - Legacy format: ${LEGACY_STREAM_PATTERN}`);
            this.metrics.recordError('validation', error.message);
            throw error;
        }
        return true;
    }
    /**
     * Generate JWT token for authentication
     *
     * @returns JWT token
     */
    generateJwtToken() {
        const payload = {
            server: this.serverIdentity,
            apiKey: this.apiKey,
            roles: this.roles,
            iat: Math.floor(Date.now() / 1000),
            exp: Math.floor(Date.now() / 1000) + (60 * 60) // 1 hour expiration
        };
        return jwt.sign(payload, this.jwtSecret);
    }
    /**
     * Verify JWT token
     *
     * @param token JWT token to verify
     * @returns Decoded token payload or null if invalid
     */
    verifyJwtToken(token) {
        try {
            return jwt.verify(token, this.jwtSecret);
        }
        catch (error) {
            this.metrics.recordError('auth', 'JWT verification failed');
            return null;
        }
    }
    /**
     * Check if server is authorized for operation on stream
     *
     * @param roles Server roles
     * @param stream Stream name
     * @param operation Operation type (read/write)
     * @returns True if authorized, false otherwise
     */
    isAuthorizedForStream(roles, stream, operation) {
        // Check if it's a legacy stream
        if (LEGACY_STREAM_PATTERN.test(stream)) {
            // Legacy streams use simplified auth - just need task_read/write roles
            return roles.includes(`task_${operation}`) || roles.includes('admin');
        }
        // For ADAPT streams, use domain-based auth
        const parts = stream.split(':');
        if (parts.length < 2)
            return false;
        const domain = parts[1];
        // Check if domain exists in reserved domains
        if (!RESERVED_DOMAINS[domain])
            return false;
        // Simple role check - can be expanded based on requirements
        const requiredRole = `${domain}_${operation}`;
        return roles.includes(requiredRole) || roles.includes('admin');
    }
    /**
     * Flatten message object for Redis (key-value pairs)
     *
     * @param message Message object
     * @returns Flattened array of key-value pairs
     */
    flattenMessageForRedis(message) {
        const result = [];
        for (const [key, value] of Object.entries(message)) {
            result.push(key);
            result.push(typeof value === 'object' ? JSON.stringify(value) : String(value));
        }
        return result;
    }
    /**
     * Process stream results into structured message objects
     *
     * @param results Raw results from Redis
     * @returns Processed messages
     */
    processStreamResults(results) {
        if (!results || results.length === 0)
            return [];
        const messages = [];
        for (const result of results) {
            const [streamName, entries] = result;
            for (const entry of entries) {
                const [id, fields] = entry;
                // Convert array of key-values to object
                const message = { id };
                for (let i = 0; i < fields.length; i += 2) {
                    const key = fields[i];
                    const value = fields[i + 1];
                    // Try to parse JSON values
                    try {
                        message[key] = JSON.parse(value);
                    }
                    catch {
                        message[key] = value;
                    }
                }
                messages.push(message);
            }
        }
        return messages;
    }
    /**
     * Publish message to Redis Stream with authentication
     *
     * @param stream Stream name
     * @param message Message object
     * @param options Additional options
     * @returns Message ID
     */
    async publishMessage(stream, message, options = {}) {
        const startTime = Date.now();
        try {
            // Validate stream name
            this.validateStreamName(stream);
            // Get or validate JWT token
            const token = options.token || this.generateJwtToken();
            const verified = this.verifyJwtToken(token);
            if (!verified) {
                throw new Error('Invalid JWT token');
            }
            // Check authorization
            if (!this.isAuthorizedForStream(verified.roles, stream, 'write')) {
                throw new Error(`Not authorized to write to stream: ${stream}`);
            }
            // Add standard fields
            const enrichedMessage = {
                ...message,
                _timestamp: Date.now(),
                _source: this.serverIdentity,
                _trace_id: message._trace_id || Date.now().toString(36) + Math.random().toString(36).substr(2)
            };
            // Build XADD command args
            const args = [stream];
            // Add MAXLEN if specified
            if (options.maxlen) {
                args.push('MAXLEN', '~', options.maxlen);
            }
            // Add message ID (auto-generate with *)
            args.push('*');
            // Add flattened message fields
            args.push(...this.flattenMessageForRedis(enrichedMessage));
            // Execute XADD command
            const messageId = await this.client.xadd(...args);
            // Record metrics
            this.metrics.recordLatency('publish', Date.now() - startTime);
            this.metrics.incrementCounter('publish');
            return messageId;
        }
        catch (error) {
            const err = error;
            this.metrics.recordError('publish', err.message || 'Unknown error');
            throw error;
        }
    }
    /**
     * Read messages from Redis Stream
     *
     * @param stream Stream name
     * @param options Read options
     * @returns Array of messages
     */
    async readMessages(stream, options = {}) {
        const startTime = Date.now();
        try {
            // Validate stream name
            this.validateStreamName(stream);
            // Get or validate JWT token
            const token = options.token || this.generateJwtToken();
            const verified = this.verifyJwtToken(token);
            if (!verified) {
                throw new Error('Invalid JWT token');
            }
            // Check authorization
            if (!this.isAuthorizedForStream(verified.roles, stream, 'read')) {
                throw new Error(`Not authorized to read from stream: ${stream}`);
            }
            // Set defaults
            const count = options.count || 10;
            const start = options.start || '0';
            const end = options.end || '+';
            // Choose command based on direction
            const command = options.reverse ? 'xrevrange' : 'xrange';
            // Execute command
            const results = await this.client[command](stream, start, end, 'COUNT', count);
            // Process results
            const messages = results.map((entry) => {
                const [id, fields] = entry;
                // Convert array of key-values to object
                const message = { id };
                for (let i = 0; i < fields.length; i += 2) {
                    const key = fields[i];
                    const value = fields[i + 1];
                    // Try to parse JSON values
                    try {
                        message[key] = JSON.parse(value);
                    }
                    catch {
                        message[key] = value;
                    }
                }
                return message;
            });
            // Record metrics
            this.metrics.recordLatency('read', Date.now() - startTime);
            this.metrics.incrementCounter('read');
            return messages;
        }
        catch (error) {
            const err = error;
            this.metrics.recordError('read', err.message || 'Unknown error');
            throw error;
        }
    }
    /**
     * Create consumer group for Redis Stream
     *
     * @param stream Stream name
     * @param group Consumer group name
     * @param options Additional options
     * @returns True if successful
     */
    async createConsumerGroup(stream, group, options = {}) {
        const startTime = Date.now();
        try {
            // Validate stream name
            this.validateStreamName(stream);
            // Get or validate JWT token
            const token = options.token || this.generateJwtToken();
            const verified = this.verifyJwtToken(token);
            if (!verified) {
                throw new Error('Invalid JWT token');
            }
            // Check authorization
            if (!this.isAuthorizedForStream(verified.roles, stream, 'write')) {
                throw new Error(`Not authorized to create consumer group on stream: ${stream}`);
            }
            // Set defaults
            const startId = options.startId || '$';
            const mkstream = options.mkstream !== undefined ? options.mkstream : true;
            // Build command args
            const args = ['CREATE', stream, group, startId];
            if (mkstream) {
                args.push('MKSTREAM');
            }
            // Create consumer group
            try {
                await this.client.xgroup(...args);
                // Record metrics
                this.metrics.recordLatency('createGroup', Date.now() - startTime);
                this.metrics.incrementCounter('createGroup');
                return true;
            }
            catch (error) {
                const err = error;
                // Group may already exist, which is fine
                if (err.message && err.message.includes('BUSYGROUP')) {
                    return true;
                }
                throw error;
            }
        }
        catch (error) {
            const err = error;
            this.metrics.recordError('createGroup', err.message || 'Unknown error');
            throw error;
        }
    }
    /**
     * Read messages from Redis Stream as part of consumer group
     *
     * @param stream Stream name
     * @param group Consumer group name
     * @param consumer Consumer name
     * @param options Additional options
     * @returns Array of messages
     */
    async readGroup(stream, group, consumer, options = {}) {
        const startTime = Date.now();
        try {
            // Validate stream name
            this.validateStreamName(stream);
            // Get or validate JWT token
            const token = options.token || this.generateJwtToken();
            const verified = this.verifyJwtToken(token);
            if (!verified) {
                throw new Error('Invalid JWT token');
            }
            // Check authorization
            if (!this.isAuthorizedForStream(verified.roles, stream, 'read')) {
                throw new Error(`Not authorized to read from stream: ${stream}`);
            }
            // Set defaults
            const count = options.count || 10;
            const block = options.block !== undefined ? options.block : 2000;
            const id = options.id || '>'; // > means new messages only
            // Build command args
            const args = [
                'GROUP', group, consumer,
            ];
            if (count) {
                args.push('COUNT', count);
            }
            if (block !== undefined) {
                args.push('BLOCK', block);
            }
            if (options.noAck) {
                args.push('NOACK');
            }
            args.push('STREAMS', stream, id);
            // Execute command
            const results = await this.client.xreadgroup(...args);
            // Record metrics
            this.metrics.recordLatency('readGroup', Date.now() - startTime);
            this.metrics.incrementCounter('readGroup');
            // Process and return messages
            return this.processStreamResults(results || []);
        }
        catch (error) {
            const err = error;
            this.metrics.recordError('readGroup', err.message || 'Unknown error');
            throw error;
        }
    }
    /**
     * Acknowledge processing of message in consumer group
     *
     * @param stream Stream name
     * @param group Consumer group name
     * @param id Message ID
     * @returns True if successful
     */
    async acknowledgeMessage(stream, group, id) {
        const startTime = Date.now();
        try {
            // Validate stream name
            this.validateStreamName(stream);
            // Execute command
            await this.client.xack(stream, group, id);
            // Record metrics
            this.metrics.recordLatency('ack', Date.now() - startTime);
            this.metrics.incrementCounter('ack');
            return true;
        }
        catch (error) {
            const err = error;
            this.metrics.recordError('ack', err.message || 'Unknown error');
            throw error;
        }
    }
    /**
     * Claim pending messages in consumer group
     *
     * @param stream Stream name
     * @param group Consumer group name
     * @param consumer Consumer name
     * @param minIdleTime Minimum idle time in milliseconds
     * @param ids Array of message IDs to claim
     * @returns Claimed messages
     */
    async claimMessages(stream, group, consumer, minIdleTime, ids) {
        const startTime = Date.now();
        try {
            // Validate stream name
            this.validateStreamName(stream);
            // Execute command
            const results = await this.client.xclaim(stream, group, consumer, minIdleTime, ...ids, 'JUSTID');
            // Record metrics
            this.metrics.recordLatency('claim', Date.now() - startTime);
            this.metrics.incrementCounter('claim');
            return results;
        }
        catch (error) {
            const err = error;
            this.metrics.recordError('claim', err.message || 'Unknown error');
            throw error;
        }
    }
    /**
     * Set state value in Redis
     *
     * @param key State key
     * @param value State value
     * @param ttl Time to live in seconds (optional)
     */
    async setState(key, value, ttl) {
        const stateKey = `state:${key}`;
        await this.client.set(stateKey, JSON.stringify(value));
        if (ttl && ttl > 0) {
            await this.client.expire(stateKey, ttl);
        }
    }
    /**
     * Get state value from Redis
     *
     * @param key State key
     * @returns State value and TTL
     */
    async getState(key) {
        const stateKey = `state:${key}`;
        const value = await this.client.get(stateKey);
        const ttl = await this.client.ttl(stateKey);
        return {
            value: value ? JSON.parse(value) : null,
            ttl: ttl >= 0 ? ttl : null
        };
    }
    /**
     * Delete state value from Redis
     *
     * @param key State key
     */
    async deleteState(key) {
        const stateKey = `state:${key}`;
        await this.client.del(stateKey);
    }
    /**
     * List available streams
     *
     * @param pattern Pattern to match stream names
     * @returns Array of stream names
     */
    async listStreams(pattern = "*") {
        return await this.client.keys(pattern);
    }
    /**
     * List consumer groups for a stream
     *
     * @param stream Stream name
     * @returns Array of consumer group info
     */
    async listConsumerGroups(stream) {
        return await this.client.xinfo("GROUPS", stream);
    }
    /**
     * Close Redis connection
     */
    async close() {
        await this.client.quit();
        console.log('RedStream connection closed');
    }
}
exports.RedStream = RedStream;
/**
 * StreamMetrics class for tracking Redis Stream metrics
 */
class StreamMetrics {
    serverIdentity;
    counters;
    latencies;
    errors;
    constructor(serverIdentity) {
        this.serverIdentity = serverIdentity;
        this.counters = new Map();
        this.latencies = new Map();
        this.errors = new Map();
        // Start metrics reporter
        this.startMetricsReporter();
    }
    /**
     * Increment counter for operation
     *
     * @param operation Operation name
     */
    incrementCounter(operation) {
        const current = this.counters.get(operation) || 0;
        this.counters.set(operation, current + 1);
    }
    /**
     * Record latency for operation
     *
     * @param operation Operation name
     * @param latency Latency in milliseconds
     */
    recordLatency(operation, latency) {
        const latencies = this.latencies.get(operation) || [];
        latencies.push(latency);
        // Limit array size to prevent memory issues
        if (latencies.length > 1000) {
            latencies.shift();
        }
        this.latencies.set(operation, latencies);
    }
    /**
     * Record error for operation
     *
     * @param operation Operation name
     * @param message Error message
     */
    recordError(operation, message) {
        const current = this.errors.get(operation) || { count: 0, messages: [] };
        current.count++;
        current.messages.push(message);
        // Limit array size to prevent memory issues
        if (current.messages.length > 100) {
            current.messages.shift();
        }
        this.errors.set(operation, current);
    }
    /**
     * Get metrics summary
     *
     * @returns Metrics summary object
     */
    getMetricsSummary() {
        const summary = {
            serverIdentity: this.serverIdentity,
            timestamp: new Date().toISOString(),
            counters: {},
            latencies: {},
            errors: {}
        };
        // Process counters
        for (const [operation, count] of this.counters.entries()) {
            summary.counters[operation] = count;
        }
        // Process latencies
        for (const [operation, latencies] of this.latencies.entries()) {
            if (latencies.length === 0)
                continue;
            const sorted = [...latencies].sort((a, b) => a - b);
            const p50Index = Math.floor(sorted.length * 0.5);
            const p95Index = Math.floor(sorted.length * 0.95);
            const p99Index = Math.floor(sorted.length * 0.99);
            summary.latencies[operation] = {
                avg: latencies.reduce((sum, val) => sum + val, 0) / latencies.length,
                min: sorted[0],
                max: sorted[sorted.length - 1],
                p50: sorted[p50Index],
                p95: sorted[p95Index],
                p99: sorted[p99Index],
                count: latencies.length
            };
        }
        // Process errors
        for (const [operation, error] of this.errors.entries()) {
            summary.errors[operation] = {
                count: error.count,
                recentMessages: error.messages.slice(-10) // Last 10 error messages
            };
        }
        return summary;
    }
    /**
     * Start metrics reporter (runs every minute)
     */
    startMetricsReporter() {
        setInterval(() => {
            const metrics = this.getMetricsSummary();
            console.log('RedStream Metrics:', JSON.stringify(metrics, null, 2));
            // Here you would typically send metrics to monitoring system
            // For example: Prometheus, CloudWatch, etc.
        }, 60000); // Every minute
    }
}
