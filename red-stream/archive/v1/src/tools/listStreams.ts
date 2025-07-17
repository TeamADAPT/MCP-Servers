import { RedisClientType } from 'redis';
import { logger } from '../utils/logger.js';

interface StreamInfo {
  name: string;
  length: number;
  groups: number;
  last_id: string;
  first_id: string;
}

interface StreamListResponse {
  streams: StreamInfo[];
}

export async function listStreams(redis: RedisClientType, pattern: string = '*'): Promise<StreamListResponse> {
  try {
    // First, scan for all stream keys
    const streams: string[] = [];
    let cursor = '0';
    do {
      const [nextCursor, keys] = await redis.sendCommand(['SCAN', cursor, 'TYPE', 'stream', 'MATCH', pattern]) as [string, string[]];
      cursor = nextCursor;
      streams.push(...keys);
    } while (cursor !== '0');

    // Get info for each stream
    const streamInfos = await Promise.all(streams.map(async (stream): Promise<StreamInfo> => {
      const info = await redis.sendCommand(['XINFO', 'STREAM', stream]);
      if (!Array.isArray(info)) {
        throw new Error('Invalid stream info response');
      }

      // Parse XINFO STREAM response
      const length = Number(info[1]);
      const groups = await redis.sendCommand(['XINFO', 'GROUPS', stream]);
      const firstId = String(info[5]);
      const lastId = String(info[3]);

      return {
        name: stream,
        length,
        groups: Array.isArray(groups) ? groups.length : 0,
        first_id: firstId,
        last_id: lastId
      };
    }));

    logger.debug(`Listed ${streamInfos.length} streams matching pattern ${pattern}`);

    return {
      streams: streamInfos
    };
  } catch (error) {
    logger.error('Error listing streams:', error);
    throw error;
  }
}