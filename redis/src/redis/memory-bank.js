/**
 * Memory Bank for Redis MCP Server
 *
 * Provides memory storage and retrieval capabilities using Redis
 */

export class MemoryBank {
    /**
     * Create a new MemoryBank instance
     *
     * @param {Object} redStream RedStream instance for Redis communication
     * @param {string} serverId Server identity
     */
    constructor(redStream, serverId) {
        this.redStream = redStream;
        this.serverId = serverId;
        this.memoryPrefix = 'memory:';
        this.initialized = false;
    }

    /**
     * Initialize the memory bank
     *
     * @returns {Promise<boolean>} True if initialization was successful
     */
    async initialize() {
        try {
            // Create memory stream if it doesn't exist
            const memoryStreamName = 'adapt:memory:redis:bank';
            
            // Initialize with a marker message
            await this.redStream.publishMessage(memoryStreamName, {
                type: 'initialization',
                server: this.serverId,
                timestamp: Date.now(),
                message: 'Memory bank initialized'
            });
            console.log(`Created memory stream: ${memoryStreamName}`);
            
            this.initialized = true;
            return true;
        } catch (error) {
            console.error('Error initializing memory bank:', error);
            return false;
        }
    }

    /**
     * Store a memory
     *
     * @param {string} key Memory key
     * @param {any} value Memory value
     * @param {Object} options Storage options
     * @returns {Promise<boolean>} True if storage was successful
     */
    async storeMemory(key, value, options = {}) {
        try {
            if (!this.initialized) {
                await this.initialize();
            }
            
            const fullKey = `${this.memoryPrefix}${key}`;
            const ttl = options.ttl || null;
            
            // Store memory in Redis
            await this.redStream.setState(fullKey, {
                value,
                metadata: {
                    created_at: Date.now(),
                    server: this.serverId,
                    ...(options.metadata || {})
                }
            }, ttl);
            
            // Optionally log to memory stream
            if (options.log !== false) {
                await this.redStream.publishMessage('adapt:memory:redis:bank', {
                    type: 'memory_stored',
                    key: fullKey,
                    server: this.serverId,
                    timestamp: Date.now(),
                    ttl
                });
            }
            
            return true;
        } catch (error) {
            console.error(`Error storing memory ${key}:`, error);
            return false;
        }
    }

    /**
     * Retrieve a memory
     *
     * @param {string} key Memory key
     * @returns {Promise<any>} Memory value or null if not found
     */
    async retrieveMemory(key) {
        try {
            if (!this.initialized) {
                await this.initialize();
            }
            
            const fullKey = `${this.memoryPrefix}${key}`;
            
            // Get memory from Redis
            const result = await this.redStream.getState(fullKey);
            
            if (result && result.value) {
                // Optionally log to memory stream
                await this.redStream.publishMessage('adapt:memory:redis:bank', {
                    type: 'memory_retrieved',
                    key: fullKey,
                    server: this.serverId,
                    timestamp: Date.now()
                });
                
                return result.value;
            }
            
            return null;
        } catch (error) {
            console.error(`Error retrieving memory ${key}:`, error);
            return null;
        }
    }

    /**
     * Delete a memory
     *
     * @param {string} key Memory key
     * @returns {Promise<boolean>} True if deletion was successful
     */
    async deleteMemory(key) {
        try {
            if (!this.initialized) {
                await this.initialize();
            }
            
            const fullKey = `${this.memoryPrefix}${key}`;
            
            // Delete memory from Redis
            await this.redStream.deleteState(fullKey);
            
            // Log to memory stream
            await this.redStream.publishMessage('adapt:memory:redis:bank', {
                type: 'memory_deleted',
                key: fullKey,
                server: this.serverId,
                timestamp: Date.now()
            });
            
            return true;
        } catch (error) {
            console.error(`Error deleting memory ${key}:`, error);
            return false;
        }
    }

    /**
     * List all memories with optional pattern matching
     *
     * @param {string} pattern Pattern to match memory keys
     * @returns {Promise<string[]>} Array of memory keys
     */
    async listMemories(pattern = '*') {
        try {
            if (!this.initialized) {
                await this.initialize();
            }
            
            const fullPattern = `${this.memoryPrefix}${pattern}`;
            
            // List keys from Redis
            const keys = await this.redStream.listStreams(fullPattern);
            
            // Remove prefix from keys
            return keys.map(key => key.replace(this.memoryPrefix, ''));
        } catch (error) {
            console.error('Error listing memories:', error);
            return [];
        }
    }
}