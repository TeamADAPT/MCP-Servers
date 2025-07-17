/**
 * Basic Usage Example for RedStream
 * 
 * This example demonstrates the fundamental usage patterns of RedStream:
 * - Initializing a RedStream instance
 * - Publishing messages to a stream
 * - Reading messages from a stream
 * - Working with consumer groups
 */

import { RedStream } from '../redstream.js';

// Type declarations
interface StreamMessage {
  id: string;
  task_id: string;
  title: string;
  priority: string;
  metadata: Record<string, any>;
}

interface CustomError {
  message?: string;
}

// Define our test stream name following ADAPT naming conventions
const STREAM_NAME = 'nova:task:boomerang:tasks';
const CONSUMER_GROUP = 'example-group';
const CONSUMER_NAME = 'example-consumer';

/**
 * Run the example
 */
async function runExample() {
  console.log('RedStream Basic Usage Example');
  console.log('-----------------------------');
  
  // Create a RedStream instance with default configuration
  console.log('Initializing RedStream...');
  const redStream = new RedStream({
    // Using default Redis cluster config (127.0.0.1:7000-7002)
    serverIdentity: 'example-service',
    roles: ['task_read', 'task_write', 'system_read', 'system_write']
  });
  
  try {
    // 1. Publish messages to the stream
    console.log(`\nPublishing messages to ${STREAM_NAME}...`);
    
    const taskIds = [];
    for (let i = 1; i <= 5; i++) {
      const taskId = `task-${Date.now()}-${i}`;
      taskIds.push(taskId);
      
      const messageId = await redStream.publishMessage(STREAM_NAME, {
        task_id: taskId,
        title: `Example Task ${i}`,
        description: `This is an example task #${i}`,
        priority: i % 2 === 0 ? 'high' : 'medium',
        status: 'new',
        assignee: 'test-agent',
        created_at: new Date().toISOString(),
        origin_nova_id: 'example-nova',
        execution_trace_id: `trace-${Date.now()}-${i}`,
        metadata: {
          example_field: `value-${i}`,
          is_test: true
        }
      });
      
      console.log(`Published task ${taskId} with message ID: ${messageId}`);
    }
    
    // 2. Read messages from the stream
    console.log('\nReading messages from the stream...');
    const messages = await redStream.readMessages(STREAM_NAME, {
      count: 10,
      reverse: true // Get newest messages first
    });
    
    console.log(`Retrieved ${messages.length} messages:`);
    messages.forEach((message, index) => {
      console.log(`\nMessage ${index + 1}:`);
      console.log(`ID: ${message.id}`);
      console.log(`Task ID: ${message.task_id}`);
      console.log(`Title: ${message.title}`);
      console.log(`Priority: ${message.priority}`);
      console.log(`Metadata: ${JSON.stringify(message.metadata)}`);
    });
    
    // 3. Work with consumer groups
    console.log('\nCreating consumer group...');
    
    // Create a consumer group
    try {
      const created = await redStream.createConsumerGroup(STREAM_NAME, CONSUMER_GROUP, {
        startId: '0' // Start from beginning of stream
      });
      console.log(`Consumer group ${CONSUMER_GROUP} created: ${created}`);
    } catch (error) {
      const err = error as CustomError;
      if (err.message?.includes('BUSYGROUP')) {
        console.log(`Consumer group ${CONSUMER_GROUP} already exists`);
      } else {
        throw error;
      }
    }
    
    // 4. Read messages using the consumer group
    console.log('\nReading messages as consumer group...');
    const groupMessages = await redStream.readGroup(
      STREAM_NAME,
      CONSUMER_GROUP,
      CONSUMER_NAME,
      {
        count: 5,
        block: 1000, // Block for 1 second if no messages
        id: '>' // Only new messages not yet delivered to this group
      }
    );
    
    if (groupMessages.length === 0) {
      console.log('No new messages found, reading from beginning of stream...');
      
      // Try reading again from the beginning
      const oldMessages = await redStream.readGroup(
        STREAM_NAME,
        CONSUMER_GROUP,
        CONSUMER_NAME,
        {
          count: 5,
          block: 1000,
          id: '0' // All messages in the stream
        }
      );
      
      console.log(`Retrieved ${oldMessages.length} messages as consumer group`);
      
      // Process messages
      for (const message of oldMessages) {
        console.log(`\nProcessing message: ${message.id}`);
        console.log(`Task: ${message.title}`);
        
        // Acknowledge message after processing
        await redStream.acknowledgeMessage(
          STREAM_NAME,
          CONSUMER_GROUP,
          message.id
        );
        console.log(`Message ${message.id} acknowledged`);
      }
    } else {
      console.log(`Retrieved ${groupMessages.length} new messages as consumer group`);
      
      // Process messages
      for (const message of groupMessages) {
        console.log(`\nProcessing message: ${message.id}`);
        console.log(`Task: ${message.title}`);
        
        // Acknowledge message after processing
        await redStream.acknowledgeMessage(
          STREAM_NAME,
          CONSUMER_GROUP,
          message.id
        );
        console.log(`Message ${message.id} acknowledged`);
      }
    }
    
    console.log('\nBasic example completed successfully!');
  } catch (error) {
    console.error('Error in example:', error);
  } finally {
    // Clean up
    await redStream.close();
    console.log('\nRedStream connection closed');
  }
}

// Run the example
runExample().catch(console.error);
