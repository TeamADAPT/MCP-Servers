/**
 * Redis MCP Server - Streams Integration
 * 
 * Integrates RedStream for Redis Streams communication into the MCP server.
 * This module provides stream-based implementations for the core MCP tools.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js';
// Import RedStream from our ES module implementation
import { RedStream } from './src/lib/redstream-es.js';
import { v4 as uuidv4 } from 'uuid';
import { z } from 'zod';

// Define stream names following ADAPT naming conventions
const TASK_STREAM = 'adapt:task:boomerang:tasks';
const TASK_EVENTS_STREAM = 'adapt:task:boomerang:events';
const MCP_HEARTBEAT_STREAM = 'adapt:system:mcp:heartbeat';
const MCP_CONTROL_STREAM = 'adapt:system:mcp:control';
const STATE_STREAM = 'adapt:memory:redis:state';

// Task status enum for consistency
enum TaskStatus {
  NEW = 'new',
  IN_PROGRESS = 'in_progress',
  BLOCKED = 'blocked',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

// Task priority enum for consistency
enum TaskPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

// Define request schemas
const CreateTaskSchema = z.object({
  method: z.literal('create_task'),
  params: z.object({
    title: z.string(),
    description: z.string().optional(),
    priority: z.enum([TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH, TaskPriority.CRITICAL]).default(TaskPriority.MEDIUM),
    assignee: z.string().optional(),
    parent_id: z.string().optional(),
    due_date: z.string().datetime().optional(),
    tags: z.array(z.string()).optional(),
    metadata: z.record(z.string(), z.any()).optional(),
    origin_nova_id: z.string(),
    execution_trace_id: z.string()
  })
});

const GetTaskSchema = z.object({
  method: z.literal('get_task'),
  params: z.object({
    task_id: z.string()
  })
});

/**
 * StreamsIntegration class - Provides stream-based implementations for MCP tools
 */
export class StreamsIntegration {
  public redStream!: any; // Using 'any' to avoid type issues with CommonJS import
  private serverId: string;
  private taskConsumerGroup: string;
  private taskConsumerName: string;
  private controlConsumerGroup: string;
  private controlConsumerName: string;
  
  /**
   * Initialize StreamsIntegration
   * 
   * @param serverId Server identity for stream messages
   * @param jwtSecret JWT secret for authentication
   * @param apiKey API key for authorization
   */
  private constructor(serverId: string) {
    this.serverId = serverId;
    this.taskConsumerGroup = `${serverId}-task-group`;
    this.taskConsumerName = `${serverId}-task-consumer`;
    this.controlConsumerGroup = `${serverId}-control-group`;
    this.controlConsumerName = `${serverId}-control-consumer`;
  }

  /**
   * Create a new StreamsIntegration instance
   */
  public static async create(serverId: string, jwtSecret?: string, apiKey?: string): Promise<StreamsIntegration> {
    const instance = new StreamsIntegration(serverId);
    
    // Initialize RedStream with server identity and roles
    instance.redStream = await RedStream.create({
      serverIdentity: serverId,
      jwtSecret: jwtSecret,
      apiKey: apiKey,
      roles: ['task_read', 'task_write', 'system_read', 'system_write', 'memory_read', 'memory_write']
    });
    
    // Initialize consumer groups
    try {
      await instance.initializeConsumerGroups();
    } catch (error) {
      console.error('Error initializing consumer groups:', error);
      throw error;
    }

    return instance;
  }
  
  /**
   * Initialize consumer groups for streams
   */
  private async initializeConsumerGroups(): Promise<void> {
    try {
      // Create consumer group for task stream
      await this.redStream.createConsumerGroup(TASK_STREAM, this.taskConsumerGroup, {
        startId: '$', // Start from latest message
        mkstream: true // Create stream if it doesn't exist
      });
      
      // Create consumer group for control stream
      await this.redStream.createConsumerGroup(MCP_CONTROL_STREAM, this.controlConsumerGroup, {
        startId: '$', // Start from latest message
        mkstream: true // Create stream if it doesn't exist
      });
      
      console.log('Consumer groups initialized successfully');
    } catch (error: unknown) {
      console.error('Error creating consumer groups:', error);
      throw error;
    }
  }
  
  /**
   * Register stream-based tools with the MCP server
   * 
   * @param server MCP server instance
   */
  /**
   * Update a task
   * 
   * @param taskId Task ID
   * @param updates Task updates
   * @returns Update result
   */
  private async updateTask(taskId: string, updates: any): Promise<any> {
    try {
      // Get current task
      const taskResult = await this.getTask(taskId);
      
      if (!taskResult.success) {
        return taskResult; // Return error from getTask
      }
      
      const task = taskResult.task;
      
      // Apply updates
      const updatedTask = {
        ...task,
        ...updates,
        task_id: taskId, // Ensure task_id is preserved
        updated_at: new Date().toISOString()
      };
      
      // Publish updated task
      const messageId = await this.redStream.publishMessage(TASK_STREAM, updatedTask);
      
      // Publish task update event
      await this.redStream.publishMessage(TASK_EVENTS_STREAM, {
        type: 'task_updated',
        task_id: taskId,
        timestamp: new Date().toISOString(),
        details: {
          updates: Object.keys(updates)
        }
      });
      
      return {
        success: true,
        task_id: taskId,
        message_id: messageId
      };
    } catch (error: unknown) {
      console.error(`Error updating task ${taskId}:`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
  
  /**
   * Complete a task
   * 
   * @param taskId Task ID
   * @param result Task result
   * @param artifacts Task artifacts
   * @returns Completion result
   */
  private async completeTask(taskId: string, result?: any, artifacts?: string[]): Promise<any> {
    try {
      // Get current task
      const taskResult = await this.getTask(taskId);
      
      if (!taskResult.success) {
        return taskResult; // Return error from getTask
      }
      
      const task = taskResult.task;
      
      // Apply completion updates
      const completedTask = {
        ...task,
        task_id: taskId,
        status: TaskStatus.COMPLETED,
        result: result || task.result,
        artifacts: artifacts || task.artifacts,
        completed_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      // Publish completed task
      const messageId = await this.redStream.publishMessage(TASK_STREAM, completedTask);
      
      // Publish task completion event
      await this.redStream.publishMessage(TASK_EVENTS_STREAM, {
        type: 'task_completed',
        task_id: taskId,
        timestamp: new Date().toISOString()
      });
      
      return {
        success: true,
        task_id: taskId,
        message_id: messageId
      };
    } catch (error: unknown) {
      console.error(`Error completing task ${taskId}:`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
  
  /**
   * List tasks with filtering
   * 
   * @param filters Task filters
   * @returns List of tasks
   */
  private async listTasks(filters: any): Promise<any> {
    try {
      // Read messages from the task stream
      const messages = await this.redStream.readMessages(TASK_STREAM, {
        count: filters?.limit || 100,
        reverse: true
      });
      
      // Apply filters
      let filteredTasks = messages;
      
      if (filters?.status) {
        filteredTasks = filteredTasks.filter((task: any) => task.status === filters.status);
      }
      
      if (filters?.assignee) {
        filteredTasks = filteredTasks.filter((task: any) => task.assignee === filters.assignee);
      }
      
      if (filters?.priority) {
        filteredTasks = filteredTasks.filter((task: any) => task.priority === filters.priority);
      }
      
      // Apply pagination
      const offset = filters?.offset || 0;
      const limit = filters?.limit || 10;
      const paginatedTasks = filteredTasks.slice(offset, offset + limit);
      
      return {
        success: true,
        tasks: paginatedTasks,
        total: filteredTasks.length,
        offset,
        limit
      };
    } catch (error: unknown) {
      console.error('Error listing tasks:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  public registerTools(server: Server): void {
    // Register all tools via the CallToolRequestSchema
    server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      try {
        switch (name) {
          // Task Management Tools
          case 'create_task': {
            const result = await this.createTask(args as any);
            return { content: [{ type: 'text', text: JSON.stringify(result) }] };
          }
          
          case 'get_task': {
            const taskId = (args as any)?.task_id;
            if (!taskId) {
              throw new Error('task_id is required');
            }
            const result = await this.getTask(taskId);
            return { content: [{ type: 'text', text: JSON.stringify(result) }] };
          }
          
          case 'update_task': {
            const taskId = (args as any)?.task_id;
            if (!taskId) {
              throw new Error('task_id is required');
            }
            const result = await this.updateTask(taskId, args as any);
            return { content: [{ type: 'text', text: JSON.stringify(result) }] };
          }
          
          case 'complete_task': {
            const taskId = (args as any)?.task_id;
            if (!taskId) {
              throw new Error('task_id is required');
            }
            const result = await this.completeTask(
              taskId, 
              (args as any)?.result, 
              (args as any)?.artifacts
            );
            return { content: [{ type: 'text', text: JSON.stringify(result) }] };
          }
          
          case 'list_tasks': {
            const result = await this.listTasks(args as any);
            return { content: [{ type: 'text', text: JSON.stringify(result) }] };
          }
          
          // Stream Communication Tools
          case 'publish_message': {
            const stream = (args as any)?.stream;
            if (!stream) {
              throw new Error('stream is required');
            }
            const result = await this.publishMessage(stream, args as any);
            return { content: [{ type: 'text', text: JSON.stringify(result) }] };
          }
          
          case 'read_messages': {
            const stream = (args as any)?.stream;
            if (!stream) {
              throw new Error('stream is required');
            }
            const messages = await this.redStream.readMessages(stream, {
              count: (args as any)?.count,
              start: (args as any)?.start,
              end: (args as any)?.end,
              reverse: (args as any)?.reverse
            });
            return { content: [{ type: 'text', text: JSON.stringify(messages) }] };
          }
          
          case 'create_consumer_group': {
            const stream = (args as any)?.stream;
            const group = (args as any)?.group;
            if (!stream || !group) {
              throw new Error('stream and group are required');
            }
            const result = await this.redStream.createConsumerGroup(stream, group, {
              startId: (args as any)?.startId,
              mkstream: (args as any)?.mkstream
            });
            return { content: [{ type: 'text', text: `Consumer group ${group} created for stream ${stream}` }] };
          }
          
          case 'read_group': {
            const stream = (args as any)?.stream;
            const group = (args as any)?.group;
            const consumer = (args as any)?.consumer;
            if (!stream || !group || !consumer) {
              throw new Error('stream, group, and consumer are required');
            }
            const messages = await this.redStream.readGroup(stream, group, consumer, {
              count: (args as any)?.count,
              block: (args as any)?.block,
              noAck: (args as any)?.noAck,
              id: (args as any)?.id
            });
            return { content: [{ type: 'text', text: JSON.stringify(messages) }] };
          }
          
          // State Management Tools
          case 'set_state': {
            const key = (args as any)?.key;
            const value = (args as any)?.value;
            if (!key || value === undefined) {
              throw new Error('key and value are required');
            }
            await this.redStream.setState(key, value, (args as any)?.ttl);
            return { content: [{ type: 'text', text: JSON.stringify({ success: true }) }] };
          }
          
          case 'get_state': {
            const key = (args as any)?.key;
            if (!key) {
              throw new Error('key is required');
            }
            const result = await this.redStream.getState(key);
            return { content: [{ type: 'text', text: JSON.stringify(result) }] };
          }
          
          case 'delete_state': {
            const key = (args as any)?.key;
            if (!key) {
              throw new Error('key is required');
            }
            await this.redStream.deleteState(key);
            return { content: [{ type: 'text', text: JSON.stringify({ success: true }) }] };
          }
          
          // Stream Management Tools
          case 'list_streams': {
            const pattern = (args as any)?.pattern || '*';
            const streams = await this.redStream.listStreams(pattern);
            return { content: [{ type: 'text', text: JSON.stringify(streams) }] };
          }
          
          case 'add_stream': {
            const stream = (args as any)?.stream;
            if (!stream) {
              throw new Error('stream is required');
            }
            // Validate stream name format
            if (!stream.match(/^adapt:[a-z]+:[a-z]+:[a-z0-9_-]+$/)) {
              throw new Error("Invalid stream name format. Must follow: adapt:domain:category:name");
            }
            // Create stream by publishing an initial message
            const messageId = await this.redStream.publishMessage(stream, {
              type: "stream_created",
              content: "Stream initialized",
              metadata: (args as any)?.metadata
            });
            return { content: [{ type: 'text', text: `Stream ${stream} created with message ID: ${messageId}` }] };
          }
          
          case 'list_consumer_groups': {
            const stream = (args as any)?.stream;
            if (!stream) {
              throw new Error('stream is required');
            }
            const groups = await this.redStream.listConsumerGroups(stream);
            return { content: [{ type: 'text', text: JSON.stringify(groups) }] };
          }
          
          case 'send_to_nova': {
            const novaId = (args as any)?.nova_id;
            const type = (args as any)?.type;
            const content = (args as any)?.content;
            if (!novaId || !type || content === undefined) {
              throw new Error('nova_id, type, and content are required');
            }
            // Format stream name for Nova's direct channel
            const stream = `devops.${novaId}.direct`;
            
            const messageId = await this.redStream.publishMessage(stream, {
              type,
              content,
              priority: (args as any)?.priority || 'normal',
              metadata: {
                sender: "Cline",
                role: "DevOps Engineer",
                timestamp: new Date().toISOString()
              }
            });
            
            return { content: [{ type: 'text', text: `Message sent to ${stream} with ID: ${messageId}` }] };
          }
          
          case 'read_multiple_streams': {
            const streams = (args as any)?.streams;
            if (!streams || !Array.isArray(streams)) {
              throw new Error('streams array is required');
            }
            const results: Record<string, any[]> = {};
            for (const stream of streams) {
              const messages = await this.redStream.readMessages(stream, {
                count: (args as any)?.count || 10,
                reverse: true
              });
              results[stream] = messages;
            }
            return { content: [{ type: 'text', text: JSON.stringify(results) }] };
          }
          
          case 'receive_all': {
            const streams = await this.redStream.listStreams("nova:*");
            const results: Record<string, any[]> = {};
            for (const stream of streams) {
              const messages = await this.redStream.readMessages(stream, {
                count: (args as any)?.count || 10,
                reverse: true
              });
              if (messages.length > 0) {
                results[stream] = messages;
              }
            }
            return { content: [{ type: 'text', text: JSON.stringify(results) }] };
          }
          
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        console.error(`Error executing tool ${name}:`, error);
        return {
          content: [{ type: 'text', text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}` }],
          isError: true
        };
      }
    });

    // Start background processes
    this.startHeartbeat();
    this.startControlMessageListener();
  }
  
  /**
   * Create a task
   * 
   * @param taskData Task data
   * @returns Task creation result
   */
  private async createTask(taskData: any): Promise<any> {
    try {
      // Generate task ID if not provided
      const taskId = taskData.task_id || `task-${uuidv4()}`;
      const timestamp = new Date().toISOString();
      
      // Prepare task object
      const task = {
        ...taskData,
        task_id: taskId,
        status: TaskStatus.NEW,
        created_at: timestamp,
        updated_at: timestamp
      };
      
      // Publish task to stream
      const messageId = await this.redStream.publishMessage(TASK_STREAM, task);
      
      // Publish task creation event
      await this.redStream.publishMessage(TASK_EVENTS_STREAM, {
        type: 'task_created',
        task_id: taskId,
        timestamp: timestamp,
        details: {
          title: task.title,
          assignee: task.assignee,
          priority: task.priority
        }
      });
      
      return {
        success: true,
        task_id: taskId,
        message_id: messageId
      };
    } catch (error: unknown) {
      console.error('Error creating task:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
  
  /**
   * Get a task by ID
   * 
   * @param taskId Task ID
   * @returns Task data or error
   */
  private async getTask(taskId: string): Promise<any> {
    try {
      // Read messages from the task stream
      const messages = await this.redStream.readMessages(TASK_STREAM, {
        count: 100, // Read a reasonable number of messages
        reverse: true // Start with newest
      });
      
      // Find the task with the matching ID
      // In a real implementation, this would use a more efficient lookup method
      const taskMessages = messages.filter((msg: { task_id: string }) => msg.task_id === taskId);
      
      if (taskMessages.length === 0) {
        return {
          success: false,
          error: `Task with ID ${taskId} not found`
        };
      }
      
      // Return the most recent version of the task
      return {
        success: true,
        task: taskMessages[0]
      };
    } catch (error: unknown) {
      console.error(`Error getting task ${taskId}:`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
  
  /**
   * Start heartbeat process
   * Sends periodic heartbeat messages to the system heartbeat stream
   */
  private startHeartbeat(): void {
    const sendHeartbeat = async () => {
      try {
        await this.redStream.publishMessage(MCP_HEARTBEAT_STREAM, {
          server_id: this.serverId,
          timestamp: new Date().toISOString(),
          status: 'active',
          memory_usage: process.memoryUsage(),
          uptime: process.uptime()
        }, { maxlen: 1000 }); // Keep last 1000 heartbeats
      } catch (error: unknown) {
        console.error('Error sending heartbeat:', error);
      }
    };
    
    // Send heartbeat every 30 seconds
    setInterval(sendHeartbeat, 30000);
    
    // Send initial heartbeat
    sendHeartbeat();
  }
  
  /**
   * Start control message listener
   * Listens for control messages on the system control stream
   */
  private startControlMessageListener(): void {
    const checkForControlMessages = async () => {
      try {
        const messages = await this.redStream.readGroup(
          MCP_CONTROL_STREAM,
          this.controlConsumerGroup,
          this.controlConsumerName,
          {
            count: 10,
            block: 1000,
            id: '>' // Only new messages
          }
        );
        
        for (const message of messages) {
          try {
            // Process control message
            console.log(`Received control message: ${message.id}`, message);
            
            // Handle different control message types
            switch (message.type) {
              case 'shutdown':
                console.log('Shutdown command received');
                // Implement graceful shutdown
                break;
              case 'reload_config':
                console.log('Reload config command received');
                // Implement config reload
                break;
              case 'status_request':
                console.log('Status request received');
                // Send status report
                await this.publishMessage(MCP_HEARTBEAT_STREAM, {
                  server_id: this.serverId,
                  timestamp: new Date().toISOString(),
                  status: 'active',
                  memory_usage: process.memoryUsage(),
                  uptime: process.uptime(),
                  is_response: true,
                  request_id: message.request_id
                });
                break;
              default:
                console.log(`Unknown control message type: ${message.type}`);
            }
            
            // Acknowledge message
            await this.redStream.acknowledgeMessage(
              MCP_CONTROL_STREAM,
              this.controlConsumerGroup,
              message.id
            );
          } catch (error: unknown) {
            console.error(`Error processing control message ${message.id}:`, error);
          }
        }
      } catch (error: unknown) {
        console.error('Error checking for control messages:', error);
      }
      
      // Schedule next check
      setTimeout(checkForControlMessages, 1000);
    };
    
    // Start checking for control messages
    checkForControlMessages();
  }
  
  /**
   * Publish a message to a stream
   * 
   * @param stream Stream name
   * @param message Message content
   * @param maxlen Maximum stream length
   * @returns Publication result
   */
  private async publishMessage(stream: string, message: any, maxlen?: number): Promise<any> {
    try {
      const messageId = await this.redStream.publishMessage(stream, message, maxlen ? { maxlen } : undefined);
      
      return {
        success: true,
        message_id: messageId,
        stream: stream
      };
    } catch (error: unknown) {
      console.error(`Error publishing message to ${stream}:`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  public async close(): Promise<void> {
    await this.redStream.close();
  }
}

export default StreamsIntegration;
