/**
 * Memory Bank Initialization for Redis MCP Server
 * 
 * This module initializes the memory bank for the Redis MCP server,
 * setting up default memory structures and ensuring persistence.
 */

import { RedStream } from "../redis-streams/redstream.js";

// Memory bank stream name
const MEMORY_BANK_STREAM = 'adapt:memory:redis:bank';
const MEMORY_STATE_PREFIX = 'adapt:memory:';

// Memory categories
enum MemoryCategory {
  SYSTEM = 'system',
  USER = 'user',
  CONVERSATION = 'conversation',
  TASK = 'task',
  KNOWLEDGE = 'knowledge'
}

// Memory priority levels
enum MemoryPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

/**
 * Memory Bank Manager
 */
export class MemoryBank {
  private redStream: RedStream;
  private serverId: string;

  /**
   * Create a new MemoryBank instance
   * 
   * @param redStream RedStream instance
   * @param serverId Server identity
   */
  constructor(redStream: RedStream, serverId: string) {
    this.redStream = redStream;
    this.serverId = serverId;
  }

  /**
   * Initialize the memory bank
   */
  async initialize(): Promise<void> {
    console.log('Initializing memory bank...');
    
    try {
      // Create memory bank stream if it doesn't exist
      await this.ensureMemoryBankStream();
      
      // Initialize system memories
      await this.initializeSystemMemories();
      
      // Initialize default categories
      await this.initializeCategories();
      
      console.log('Memory bank initialized successfully');
    } catch (error) {
      console.error('Error initializing memory bank:', error);
      throw error;
    }
  }

  /**
   * Ensure memory bank stream exists
   */
  private async ensureMemoryBankStream(): Promise<void> {
    try {
      // Check if stream exists
      const streams = await this.redStream.listStreams(MEMORY_BANK_STREAM);
      
      if (streams.length === 0) {
        // Create stream with initial message
        await this.redStream.publishMessage(MEMORY_BANK_STREAM, {
          type: 'stream_created',
          content: 'Memory bank stream initialized',
          metadata: {
            creator: this.serverId,
            created_at: new Date().toISOString()
          }
        });
        console.log('Memory bank stream created');
      } else {
        console.log('Memory bank stream already exists');
      }
    } catch (error) {
      console.error('Error ensuring memory bank stream:', error);
      throw error;
    }
  }

  /**
   * Initialize system memories
   */
  private async initializeSystemMemories(): Promise<void> {
    try {
      // System configuration memory
      await this.storeMemory(
        'system_config',
        {
          server_id: this.serverId,
          initialized_at: new Date().toISOString(),
          version: '1.0.0',
          capabilities: [
            'task_management',
            'stream_communication',
            'state_persistence'
          ]
        },
        MemoryCategory.SYSTEM,
        MemoryPriority.HIGH
      );

      // Server status memory
      await this.storeMemory(
        'server_status',
        {
          status: 'active',
          last_heartbeat: new Date().toISOString(),
          uptime: 0
        },
        MemoryCategory.SYSTEM,
        MemoryPriority.MEDIUM
      );
    } catch (error) {
      console.error('Error initializing system memories:', error);
      throw error;
    }
  }

  /**
   * Initialize default memory categories
   */
  private async initializeCategories(): Promise<void> {
    try {
      // Store category definitions
      await this.storeMemory(
        'categories',
        {
          [MemoryCategory.SYSTEM]: {
            description: 'System-related memories',
            retention: 'permanent'
          },
          [MemoryCategory.USER]: {
            description: 'User-related memories',
            retention: 'long-term'
          },
          [MemoryCategory.CONVERSATION]: {
            description: 'Conversation-related memories',
            retention: 'medium-term'
          },
          [MemoryCategory.TASK]: {
            description: 'Task-related memories',
            retention: 'task-dependent'
          },
          [MemoryCategory.KNOWLEDGE]: {
            description: 'Knowledge base memories',
            retention: 'permanent'
          }
        },
        MemoryCategory.SYSTEM,
        MemoryPriority.MEDIUM
      );
    } catch (error) {
      console.error('Error initializing categories:', error);
      throw error;
    }
  }

  /**
   * Store a memory in the memory bank
   * 
   * @param key Memory key
   * @param value Memory value
   * @param category Memory category
   * @param priority Memory priority
   * @param ttl Time to live in seconds (0 = no expiration)
   */
  async storeMemory(
    key: string,
    value: any,
    category: MemoryCategory = MemoryCategory.SYSTEM,
    priority: MemoryPriority = MemoryPriority.MEDIUM,
    ttl: number = 0
  ): Promise<string> {
    try {
      // Store in Redis state
      await this.redStream.setState(`${MEMORY_STATE_PREFIX}${key}`, value, ttl);
      
      // Publish to memory bank stream for tracking
      const messageId = await this.redStream.publishMessage(MEMORY_BANK_STREAM, {
        type: 'memory_stored',
        key,
        category,
        priority,
        ttl,
        stored_at: new Date().toISOString(),
        stored_by: this.serverId
      });
      
      return messageId;
    } catch (error) {
      console.error(`Error storing memory ${key}:`, error);
      throw error;
    }
  }

  /**
   * Retrieve a memory from the memory bank
   * 
   * @param key Memory key
   * @returns Memory value or null if not found
   */
  async retrieveMemory(key: string): Promise<any> {
    try {
      const result = await this.redStream.getState(`${MEMORY_STATE_PREFIX}${key}`);
      
      // Publish memory access to stream for tracking
      if (result.value !== null) {
        await this.redStream.publishMessage(MEMORY_BANK_STREAM, {
          type: 'memory_accessed',
          key,
          accessed_at: new Date().toISOString(),
          accessed_by: this.serverId
        });
      }
      
      return result.value;
    } catch (error) {
      console.error(`Error retrieving memory ${key}:`, error);
      throw error;
    }
  }

  /**
   * Delete a memory from the memory bank
   * 
   * @param key Memory key
   */
  async deleteMemory(key: string): Promise<void> {
    try {
      await this.redStream.deleteState(`${MEMORY_STATE_PREFIX}${key}`);
      
      // Publish memory deletion to stream for tracking
      await this.redStream.publishMessage(MEMORY_BANK_STREAM, {
        type: 'memory_deleted',
        key,
        deleted_at: new Date().toISOString(),
        deleted_by: this.serverId
      });
    } catch (error) {
      console.error(`Error deleting memory ${key}:`, error);
      throw error;
    }
  }

  /**
   * List all memories in the memory bank
   * 
   * @param category Optional category filter
   * @returns List of memory keys
   */
  async listMemories(category?: MemoryCategory): Promise<string[]> {
    try {
      // Get all memory keys from Redis
      const pattern = `${MEMORY_STATE_PREFIX}*`;
      const keys = await this.redStream.listStreams(pattern);
      
      // If category filter is provided, filter memories by category
      if (category) {
        // We need to check each memory's category
        const filteredKeys: string[] = [];
        
        for (const fullKey of keys) {
          // Remove prefix to get the actual key
          const key = fullKey.replace(MEMORY_STATE_PREFIX, '');
          
          // Get memory metadata from stream
          const messages = await this.redStream.readMessages(MEMORY_BANK_STREAM, {
            count: 1,
            reverse: true
          });
          
          // Find the latest message for this key
          const memoryMessage = messages.find(msg => 
            (msg.type === 'memory_stored' || msg.type === 'memory_updated') && 
            msg.key === key
          );
          
          if (memoryMessage && memoryMessage.category === category) {
            filteredKeys.push(key);
          }
        }
        
        return filteredKeys;
      }
      
      // Return all keys without the prefix
      return keys.map((key: string) => key.replace(MEMORY_STATE_PREFIX, ''));
    } catch (error) {
      console.error('Error listing memories:', error);
      throw error;
    }
  }
}