import { RedisClientType } from 'redis';
import { logger } from '../utils/logger.js';

interface GroupInfo {
  name: string;
  consumers: number;
  pending: number;
  last_delivered_id: string;
  lag: number;
}

interface GroupListResponse {
  stream: string;
  groups: GroupInfo[];
}

export async function listGroups(redis: RedisClientType, stream: string): Promise<GroupListResponse> {
  try {
    const result = await redis.sendCommand(['XINFO', 'GROUPS', stream]);
    if (!Array.isArray(result)) {
      throw new Error('Invalid response from Redis');
    }

    const groups = result.map((groupData: any): GroupInfo => {
      if (!Array.isArray(groupData)) {
        throw new Error('Invalid group data format');
      }
      
      // XINFO GROUPS returns array with format:
      // [name, consumers, pending, last-delivered-id, entries-read, lag]
      return {
        name: String(groupData[0]),
        consumers: Number(groupData[1]),
        pending: Number(groupData[2]),
        last_delivered_id: String(groupData[3]),
        lag: Number(groupData[5] ?? 0)
      };
    });

    logger.debug(`Listed ${groups.length} groups for stream ${stream}`);
    
    return {
      stream,
      groups
    };
  } catch (error) {
    logger.error('Error listing groups:', error);
    throw error;
  }
}