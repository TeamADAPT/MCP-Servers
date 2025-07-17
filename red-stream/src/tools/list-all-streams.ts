import { McpToolResponse, RedisClient } from '../types.js';

export interface ListAllStreamsArgs {
    // No arguments needed for this tool
}

export const listAllStreamsDefinition = {
    name: 'list_all_streams',
    description: 'List all available Redis streams',
    inputSchema: {
        type: 'object' as const,
        properties: {},
        required: [],
    },
};

export async function listAllStreams(redis: RedisClient, args: unknown): Promise<McpToolResponse> {
    try {
        // Use Redis SCAN to get all keys that match the stream pattern
        let streams: string[] = [];
        let cursor = 0;
        
        do {
            const result = await redis.scan(cursor, { MATCH: '*', COUNT: 100 });
            cursor = result.cursor;
            
            // Filter out non-stream keys
            for (const key of result.keys) {
                const type = await redis.type(key) as string;
                if (type === 'stream') {
                    streams.push(key);
                }
            }
        } while (cursor !== 0);
        
        return {
            content: [
                {
                    type: 'text',
                    text: JSON.stringify(streams, null, 2),
                },
            ],
        };
    } catch (error: any) {
        console.error('[RedStream] Error getting streams:', error);
        throw new Error('Failed to retrieve streams');
    }
}

export function isListAllStreamsArgs(obj: unknown): obj is ListAllStreamsArgs {
    return typeof obj === 'object' && obj !== null;
}