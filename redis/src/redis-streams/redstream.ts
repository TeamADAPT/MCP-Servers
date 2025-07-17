/**
 * RedStream - Redis Streams Implementation for Nova Communication
 * 
 * This module implements the Redis Streams Access Protocol as specified by Echo
 * for secure and standardized communication between MCP servers.
 */

/// <reference types="node" />

import * as IORedis from 'ioredis';
import { RedisKey, RedisValue, Callback } from 'ioredis';

type RedisInstance = IORedis.Redis | IORedis.Cluster;

type RedisStreamResult = Array<[string, Array<[string, string[]]>]>;

interface ClusterOptions {
  nodes: { host: string; port: number; }[];
  redisOptions?: {
    password?: string;
    connectTimeout?: number;
    maxRetriesPerRequest?: number;
    enableReadyCheck?: boolean;
    lazyConnect?: boolean;
    showFriendlyErrorStack?: boolean;
  };
  clusterRetryStrategy?: (times: number) => number | null;
  enableOfflineQueue?: boolean;
  maxRedirections?: number;
  retryDelayOnFailover?: number;
}

interface XPendingResponse {
  count: number;
  start: string;
  end: string;
  consumers: Array<{ name: string; pending: number; }>;
}

interface JwtPayload {
  server: string;
  apiKey: string;
  roles: string[];
  iat: number;
  exp: number;
}

interface CustomError {
  message: string;
  code?: string;
}

type DomainKey = 'system' | 'task' | 'agent' | 'user' | 'memory' | 'devops' | 'broadcast';
type ReservedDomains = Record<DomainKey, string>;

// Mock JWT functions since we removed the dependency
const jwt = {
  sign: (payload: JwtPayload, secret: string): string => {
    return Buffer.from(JSON.stringify(payload)).toString('base64');
  },
  verify: (token: string, secret: string): JwtPayload => {
    try {
      return JSON.parse(Buffer.from(token, 'base64').toString());
    } catch {
      throw new Error('Invalid token');
    }
  }
};

// Constants for Stream Naming Conventions
const ADAPT_STREAM_PREFIX = 'nova:';
const ADAPT_STREAM_PATTERN = /^nova:(system|task|agent|user|memory|devops|broadcast):[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+$/;
const LEGACY_STREAM_PATTERN = /^[a-z]+\.[a-z0-9]+\.direct$/;

// Error messages
const ERROR_MESSAGES = {
    INVALID_STREAM_NAME: (streamName: string) => 
        `Stream name "${streamName}" does not follow naming conventions. Must be either:
        - ADAPT format: nova:domain:category:name (e.g. nova:devops:general)
        - Legacy format: domain.name.direct (e.g. devops.dev2.direct)`,
    UNAUTHORIZED: (stream: string, operation: string) => 
        `Not authorized to ${operation} stream: ${stream}`,
    CONNECTION_ERROR: (err: Error) => 
        `Redis connection error: ${err.message}`,
    INVALID_TOKEN: 'Invalid JWT token'
};

// Reserved domains and their governance
const RESERVED_DOMAINS: ReservedDomains = {
  system: 'MemCommsOps',
  task: 'CommsOps',
  agent: 'AgentOps',
  user: 'UserOps',
  memory: 'MemOps',
  devops: 'DevOps',
  broadcast: 'CommsOps'
};

// Redis Cluster Configuration
// Redis Connection Configuration
const DEFAULT_NODE = { host: '127.0.0.1', port: 7000 };

const DEFAULT_OPTIONS = {
    password: 'd5d7817937232ca5',
    connectTimeout: 5000,
    maxRetriesPerRequest: 3,
    retryStrategy: (times: number) => {
        if (times > 3) return null;
        return Math.min(times * 200, 1000);
    }
};

/**
 * RedStream class for Redis Streams communication
 */
class RedStream {
  protected client!: RedisInstance;
  private serverIdentity!: string;
  private jwtSecret!: string;
  private apiKey!: string;
  private roles!: string[];
  private metrics!: StreamMetrics;
  
  /**
   * Create a new RedStream instance
   * 
   * @param options Configuration options for RedStream
   */
  private constructor() {}

  /**
   * Create a new RedStream instance
   * This is the recommended way to instantiate RedStream
   */
  static async create(options: {
    nodes?: { host: string, port: number }[];
    clusterOptions?: any;
    serverIdentity?: string;
    jwtSecret?: string;
    apiKey?: string;
    roles?: string[];
  } = {}): Promise<RedStream> {
    const instance = new RedStream();
    
    // Initialize Redis client with simplified configuration
    const node = options.nodes?.[0] || DEFAULT_NODE;
    
    // Create Redis Cluster instance
    const clusterOptions: ClusterOptions = {
      nodes: options.nodes || [
        { host: '127.0.0.1', port: 7000 },
        { host: '127.0.0.1', port: 7001 },
        { host: '127.0.0.1', port: 7002 }
      ],
      redisOptions: {
        password: DEFAULT_OPTIONS.password,
        connectTimeout: DEFAULT_OPTIONS.connectTimeout,
        maxRetriesPerRequest: DEFAULT_OPTIONS.maxRetriesPerRequest,
        enableReadyCheck: true,
        lazyConnect: true,
        showFriendlyErrorStack: true
      },
      clusterRetryStrategy: (times: number) => {
        if (times > 3) return null;
        return Math.min(times * 200, 1000);
      },
      enableOfflineQueue: true,
      maxRedirections: 16,
      retryDelayOnFailover: 100
    };

    instance.client = new IORedis.Cluster(clusterOptions.nodes, clusterOptions);

    // Set up event handlers
    instance.setupEventHandlers();

    try {
      // Wait for connection
      await new Promise<void>((resolve, reject) => {
        instance.client.once('ready', () => resolve());
        instance.client.once('error', (err: Error) => reject(err));
      });

      // Set server identity
      instance.serverIdentity = options.serverIdentity || 'redis_mcp_server';
      
      // Security credentials
      instance.jwtSecret = options.jwtSecret || 'default_secret_change_in_production';
      instance.apiKey = options.apiKey || 'default_api_key_change_in_production';
      instance.roles = options.roles || ['redis_mcp'];
      
      // Initialize metrics
      instance.metrics = new StreamMetrics(instance.serverIdentity);
      
      // Log initialization
      console.log(`RedStream initialized for server: ${instance.serverIdentity}`);

      return instance;
    } catch (error) {
      await instance.client.disconnect();
      throw error;
    }
  }
  
  /**
   * Set up Redis event handlers
   */
  private setupEventHandlers(): void {
    // Connection events
    this.client.on('ready', () => {
      console.log('Connected to Redis successfully');
    });

    this.client.on('connect', () => {
      console.log('Redis connection established');
    });

    this.client.on('reconnecting', () => {
      console.log('Reconnecting to Redis...');
    });

    // Error events
    this.client.on('error', (err: Error) => {
      console.error('Redis Error:', err);
      if (this.metrics) {
        this.metrics.recordError('redis', err.message);
      }
    });

    // Cleanup events
    this.client.on('end', () => {
      console.log('Redis connection ended');
    });

    // Handle process termination
    process.once('SIGINT', async () => {
      console.log('Received SIGINT, closing Redis connection...');
      await this.close();
      process.exit(0);
    });

    process.once('SIGTERM', async () => {
      console.log('Received SIGTERM, closing Redis connection...');
      await this.close();
      process.exit(0);
    });
  }
  
  /**
   * Validate stream name against ADAPT conventions
   * 
   * @param streamName Stream name to validate
   * @returns True if valid, throws error if invalid
   */
  /**
   * Validate stream name against naming conventions
   * 
   * @param streamName Stream name to validate
   * @returns True if valid, throws error if invalid
   */
  public validateStreamName(streamName: string): boolean {
    if (!ADAPT_STREAM_PATTERN.test(streamName) && !LEGACY_STREAM_PATTERN.test(streamName)) {
      const error = new Error(ERROR_MESSAGES.INVALID_STREAM_NAME(streamName));
      this.metrics.recordError('validation', error.message);
      throw error;
    }
    return true;
  }

  /**
   * Check if stream name follows legacy format
   */
  private isLegacyStream(streamName: string): boolean {
    return LEGACY_STREAM_PATTERN.test(streamName);
  }

  /**
   * Check if stream name follows ADAPT format
   */
  private isAdaptStream(streamName: string): boolean {
    return ADAPT_STREAM_PATTERN.test(streamName);
  }
  
  /**
   * Generate JWT token for authentication
   * 
   * @returns JWT token
   */
  private generateJwtToken(): string {
    const payload: JwtPayload = {
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
  private verifyJwtToken(token: string): JwtPayload | null {
    try {
      return jwt.verify(token, this.jwtSecret);
    } catch (error) {
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
  private isAuthorizedForStream(roles: string[], stream: string, operation: 'read' | 'write'): boolean {
    // Check if it's a legacy stream
    if (LEGACY_STREAM_PATTERN.test(stream)) {
      // Legacy streams use simplified auth - just need task_read/write roles
      return roles.includes(`task_${operation}`) || roles.includes('admin');
    }

    // For ADAPT streams, use domain-based auth
    const parts = stream.split(':');
    if (parts.length < 2) return false;
    
    const domain = parts[1] as DomainKey;
    
    // Check if domain exists in reserved domains
    if (!RESERVED_DOMAINS[domain]) return false;
    
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
  private flattenMessageForRedis(message: Record<string, any>): string[] {
    const result: string[] = [];
    
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
  private processStreamResults(results: any[]): any[] {
    if (!results || results.length === 0) return [];
    
    const messages: any[] = [];
    
    for (const result of results) {
      const [streamName, entries] = result;
      
      for (const entry of entries) {
        const [id, fields] = entry;
        
        // Convert array of key-values to object
        const message: Record<string, any> = { id };
        
        for (let i = 0; i < fields.length; i += 2) {
          const key = fields[i];
          const value = fields[i + 1];
          
          // Try to parse JSON values
          try {
            message[key] = JSON.parse(value);
          } catch {
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
  public async publishMessage(
    stream: string,
    message: Record<string, any>,
    options: {
      maxlen?: number;
      token?: string;
    } = {}
  ): Promise<string> {
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
      const args: any[] = [stream];
      
      // Add MAXLEN if specified
      if (options.maxlen) {
        args.push('MAXLEN', '~', options.maxlen);
      }
      
      // Add message ID (auto-generate with *)
      args.push('*');
      
      // Add flattened message fields
      const fields = this.flattenMessageForRedis(enrichedMessage);
      for (let i = 0; i < fields.length; i++) {
        args.push(fields[i]);
      }
      
      // Execute XADD command
      const messageId = await this.client.xadd(args[0] as RedisKey, ...args.slice(1) as RedisValue[]) || '';
      
      // Record metrics
      this.metrics.recordLatency('publish', Date.now() - startTime);
      this.metrics.incrementCounter('publish');
      
      return messageId;
    } catch (error) {
      const err = error as CustomError;
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
  public async readMessages(
    stream: string,
    options: {
      count?: number;
      start?: string;
      end?: string;
      reverse?: boolean;
      token?: string;
    } = {}
  ): Promise<any[]> {
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
      const results = (await this.client[command](stream, start, end, 'COUNT', count)) as Array<[string, string[]]> || [];
      
      // Process results
      const messages = results.map((entry: any[]) => {
        const [id, fields] = entry;
        
        // Convert array of key-values to object
        const message: Record<string, any> = { id };
        
        for (let i = 0; i < fields.length; i += 2) {
          const key = fields[i];
          const value = fields[i + 1];
          
          // Try to parse JSON values
          try {
            message[key] = JSON.parse(value);
          } catch {
            message[key] = value;
          }
        }
        
        return message;
      });
      
      // Record metrics
      this.metrics.recordLatency('read', Date.now() - startTime);
      this.metrics.incrementCounter('read');
      
      return messages;
    } catch (error) {
      const err = error as CustomError;
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
  public async createConsumerGroup(
    stream: string,
    group: string,
    options: {
      startId?: string;
      mkstream?: boolean;
      token?: string;
    } = {}
  ): Promise<boolean> {
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
        await this.client.xgroup('CREATE' as const, stream, group, startId);
        
        // Record metrics
        this.metrics.recordLatency('createGroup', Date.now() - startTime);
        this.metrics.incrementCounter('createGroup');
        
        return true;
      } catch (error) {
        const err = error as CustomError;
        // Group may already exist, which is fine
        if (err.message && err.message.includes('BUSYGROUP')) {
          return true;
        }
        throw error;
      }
    } catch (error) {
      const err = error as CustomError;
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
  public async readGroup(
    stream: string,
    group: string,
    consumer: string,
    options: {
      count?: number;
      block?: number;
      noAck?: boolean;
      id?: string;
      token?: string;
    } = {}
  ): Promise<any[]> {
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
      const args = [];
      
      // Add optional arguments in correct order
      if (block !== undefined) {
        args.push('BLOCK', block.toString());
      }
      if (count) {
        args.push('COUNT', count.toString());
      }
      if (options.noAck) {
        args.push('NOACK');
      }
      
      // Add required arguments
      args.push('GROUP', group, consumer, 'STREAMS', stream, id);
      
      // Execute command using internal command method
      const results = await (this.client as any).sendCommand(['XREADGROUP', ...args]) as RedisStreamResult || [];
      
      // Record metrics
      this.metrics.recordLatency('readGroup', Date.now() - startTime);
      this.metrics.incrementCounter('readGroup');
      
      // Process and return messages
      return this.processStreamResults(results || []);
    } catch (error) {
      const err = error as CustomError;
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
  public async acknowledgeMessage(
    stream: string,
    group: string,
    id: string
  ): Promise<boolean> {
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
    } catch (error) {
      const err = error as CustomError;
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
  public async claimMessages(
    stream: string,
    group: string,
    consumer: string,
    minIdleTime: number,
    ids: string[]
  ): Promise<any[]> {
    const startTime = Date.now();
    
    try {
      // Validate stream name
      this.validateStreamName(stream);
      
      // Execute command
      const results = await this.client.xclaim(
        stream,
        group,
        consumer,
        minIdleTime.toString(),
        ids[0],
        ...ids.slice(1),
        'JUSTID' as const
      ) as string[];
      
      // Record metrics
      this.metrics.recordLatency('claim', Date.now() - startTime);
      this.metrics.incrementCounter('claim');
      
      return results;
    } catch (error) {
      const err = error as CustomError;
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
  public async setState(key: string, value: any, ttl?: number): Promise<void> {
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
  public async getState(key: string): Promise<{ value: any; ttl: number | null }> {
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
  public async deleteState(key: string): Promise<void> {
    const stateKey = `state:${key}`;
    await this.client.del(stateKey);
  }

  /**
   * List available streams
   * 
   * @param pattern Pattern to match stream names
   * @returns Array of stream names
   */
  public async listStreams(pattern: string = "*"): Promise<string[]> {
    return await this.client.keys(pattern);
  }

  /**
   * List consumer groups for a stream
   * 
   * @param stream Stream name
   * @returns Array of consumer group info
   */
  public async listConsumerGroups(stream: string): Promise<any[]> {
    return (await this.client.xinfo("GROUPS", stream)) as Array<any>;
  }

  /**
   * Get pending messages info for a consumer group
   */
  public async getPendingInfo(stream: string, group: string): Promise<{
    count: number;
    start: string;
    end: string;
    consumers: Array<{
      name: string;
      pending: number;
    }>;
  }> {
    try {
      const info = await this.client.xpending(stream, group) as unknown as XPendingResponse;
      return {
        count: info?.count || 0,
        start: info?.start || '0-0',
        end: info?.end || '0-0',
        consumers: info?.consumers || []
      };
    } catch {
      return {
        count: 0,
        start: '0-0',
        end: '0-0',
        consumers: []
      };
    }
  }

  /**
   * Close Redis connection
   */
  public async close(): Promise<void> {
    try {
      // Disconnect all nodes in the cluster
      if (this.client) {
        await this.client.disconnect();
        await this.client.quit();
      }
    } catch (error) {
      console.error('Error closing RedStream connection:', error);
    } finally {
      // Ensure metrics reporter is stopped
      if (this.metrics) {
        this.metrics.stopMetricsReporter();
      }
      console.log('RedStream connection closed');
    }
  }
}

/**
 * StreamMetrics class for tracking Redis Stream metrics
 */
class StreamMetrics {
  private serverIdentity: string;
  private counters: Map<string, number>;
  private latencies: Map<string, number[]>;
  private errors: Map<string, { count: number, messages: string[] }>;
  
  constructor(serverIdentity: string) {
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
  public incrementCounter(operation: string): void {
    const current = this.counters.get(operation) || 0;
    this.counters.set(operation, current + 1);
  }
  
  /**
   * Record latency for operation
   * 
   * @param operation Operation name
   * @param latency Latency in milliseconds
   */
  public recordLatency(operation: string, latency: number): void {
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
  public recordError(operation: string, message: string): void {
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
  public getMetricsSummary(): any {
    const summary: any = {
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
      if (latencies.length === 0) continue;
      
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
  private metricsInterval: NodeJS.Timeout | null = null;

  private startMetricsReporter(): void {
    this.metricsInterval = setInterval(() => {
      const metrics = this.getMetricsSummary();
      console.log('RedStream Metrics:', JSON.stringify(metrics, null, 2));
      
      // Here you would typically send metrics to monitoring system
      // For example: Prometheus, CloudWatch, etc.
    }, 60000); // Every minute
  }

  public stopMetricsReporter(): void {
    if (this.metricsInterval) {
      clearInterval(this.metricsInterval);
      this.metricsInterval = null;
    }
  }
}

export { RedStream };
