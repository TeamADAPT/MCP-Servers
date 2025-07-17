#!/usr/bin/env node

import { RedStream } from "../src/redis-streams/build/redstream.js";

async function createLegacyStreams() {
  const redStream = new RedStream({
    serverIdentity: 'stream_setup',
    roles: ['task_write']
  });

  const streams = [
    'devops.cline.direct',
    'devops.dev2.direct',
    'devops.dev3.direct',
    'devops.sentinel.direct'
  ];

  for (const stream of streams) {
    try {
      await redStream.publishMessage(stream, {
        type: 'stream_created',
        content: 'Legacy stream initialized for transition period',
        metadata: {
          created_at: new Date().toISOString(),
          created_by: 'Cline',
          migration_note: 'Will be migrated to ADAPT format in 2 weeks'
        }
      });
      console.log(`Created legacy stream: ${stream}`);
    } catch (error) {
      console.error(`Error creating stream ${stream}:`, error);
    }
  }

  await redStream.close();
}

createLegacyStreams().catch(console.error);
