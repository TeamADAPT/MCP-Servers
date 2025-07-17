import { RedisClient, McpToolResponse, RedisGroupInfo } from '../types.js';

interface ListGroupsArgs {
    stream: string;
}

function isListGroupsArgs(obj: unknown): obj is ListGroupsArgs {
    return typeof obj === 'object' && 
           obj !== null && 
           'stream' in obj &&
           typeof (obj as any).stream === 'string';
}

export const listGroupsDefinition = {
    name: 'list_groups' as const,
    description: 'Lists all consumer groups for a specified stream',
    inputSchema: {
        type: 'object' as const,
        properties: {
            stream: { 
                type: 'string', 
                description: 'Name of the stream' 
            }
        },
        required: ['stream']
    }
};

export async function listGroups(
    redis: RedisClient,
    args: unknown
): Promise<McpToolResponse> {
    if (!isListGroupsArgs(args)) {
        throw new Error('Invalid arguments: stream is required');
    }

    const groups = await redis.xInfoGroups(args.stream);
    
    const formattedGroups = groups.map(group => ({
        name: group.name,
        consumers: group.consumers,
        pending: group.pending,
        lastDeliveredId: group.lastDeliveredId
    }));

    return {
        content: [{ 
            type: 'text', 
            text: JSON.stringify(formattedGroups, null, 2) 
        }]
    };
}