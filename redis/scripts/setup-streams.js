#!/usr/bin/env node

const { RedStream } = require('../src/redis-streams/redstream');

async function setupStreams() {
  const redStream = new RedStream({
    serverIdentity: 'setup-script',
    roles: ['task_write', 'system_write']
  });

  // Define both ADAPT and legacy format streams
  const streams = [
    // ADAPT format streams
    {
      stream: 'nova:devops:cline:direct',
      metadata: {
        description: 'Direct communication channel for Cline',
        owner: 'Cline'
      }
    },
    {
      stream: 'nova:devops:sentinel:direct',
      metadata: {
        description: 'Direct communication channel for Sentinel',
        owner: 'Sentinel'
      }
    },
    {
      stream: 'nova:devops:mcp:team',
      metadata: {
        description: 'MCP team communication channel',
        owner: 'DevOps'
      }
    },
    {
      stream: 'nova:devops:general',
      metadata: {
        description: 'General DevOps communication channel',
        owner: 'DevOps'
      }
    },
    {
      stream: 'nova:broadcast:all',
      metadata: {
        description: 'Network-wide broadcast channel',
        owner: 'CommsOps'
      }
    },
    // Legacy format streams
    {
      stream: 'devops.cline.direct',
      metadata: {
        description: 'Legacy direct channel for Cline',
        owner: 'Cline',
        format: 'legacy'
      }
    },
    {
      stream: 'devops.sentinel.direct',
      metadata: {
        description: 'Legacy direct channel for Sentinel',
        owner: 'Sentinel',
        format: 'legacy'
      }
    },
    {
      stream: 'devops.mcp.team',
      metadata: {
        description: 'Legacy MCP team channel',
        owner: 'DevOps',
        format: 'legacy'
      }
    },
    {
      stream: 'devops.general',
      metadata: {
        description: 'Legacy general DevOps channel',
        owner: 'DevOps',
        format: 'legacy'
      }
    }
  ];

  try {
    for (const { stream, metadata } of streams) {
      // Create stream by publishing initial message
      await redStream.publishMessage(stream, {
        type: 'stream_created',
        timestamp: new Date().toISOString(),
        metadata: {
          ...metadata,
          created_at: new Date().toISOString(),
          created_by: 'Cline'
        }
      });
      console.log(`Created stream: ${stream}`);

      // Create consumer group for the stream
      await redStream.createConsumerGroup(stream, 'nova-group', {
        startId: '$',
        mkstream: true
      });
      console.log(`Created consumer group for: ${stream}`);
    }

    console.log('All streams and consumer groups created successfully');
  } catch (error) {
    console.error('Error setting up streams:', error);
  } finally {
    await redStream.close();
  }
}

setupStreams().catch(console.error);
