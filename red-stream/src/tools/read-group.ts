import { RedisClient, McpToolResponse } from '../types.js';

interface ReadGroupArgs {
    stream: string;
    group: string;
    consumer: string;
    count?: number;
}

function isReadGroupArgs(obj: unknown): obj is ReadGroupArgs {
    return typeof obj === 'object' && 
           obj !== null && 
           'stream' in obj &&
           typeof (obj as any).stream === 'string' &&
           'group' in obj &&
           typeof (obj as any).group === 'string' &&
           'consumer' in obj &&
           typeof (obj as any).consumer === 'string';
}

export const readGroupDefinition = {
    name: 'read_group' as const,
    description: 'Reads messages from a stream as a consumer group',
    inputSchema: {
        type: 'object' as const,
        properties: {
            stream: { 
                type: 'string', 
                description: 'Name of the stream' 
            },
            group: { 
                type: 'string', 
                description: 'Consumer group name' 
            },
            consumer: { 
                type: 'string', 
                description: 'Consumer name' 
            },
            count: { 
                type: 'number', 
                description: 'Number of messages (default: 1)',
                default: 1
            }
        },
        required: ['stream', 'group', 'consumer']
    }
};

export async function readGroup(
    redis: RedisClient,
    args: unknown
): Promise<McpToolResponse> {
    if (!isReadGroupArgs(args)) {
        throw new Error('Invalid arguments: stream, group, and consumer are required');
    }

    const messages = await redis.xReadGroup(
        args.group,
        args.consumer,
        [{ key: args.stream, id: '>' }],
        { COUNT: args.count || 1 }
    );

    if (!messages) {
        return {
            content: [{ 
                type: 'text', 
                text: JSON.stringify([], null, 2) 
            }]
        };
    }

    const formattedMessages = messages[0].messages.map(msg => ({
        id: msg.id,
        message: msg.message
    }));

    return {
        content: [{ 
            type: 'text', 
            text: JSON.stringify(formattedMessages, null, 2) 
        }]
    };
}