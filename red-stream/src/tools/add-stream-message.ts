import { AddStreamMessageArgs, RedisClient, McpToolResponse, isAddStreamMessageArgs } from '../types.js';

export const addStreamMessageDefinition = {
    name: 'add_stream_message' as const,
    description: 'Adds a new message to a stream',
    inputSchema: {
        type: 'object' as const,
        properties: {
            stream: {
                type: 'string',
                description: 'Name of the stream'
            },
            message: {
                type: 'object',
                description: 'Message content'
            }
        },
        required: ['stream', 'message']
    }
};

export async function addStreamMessage(
    redis: RedisClient,
    args: unknown
): Promise<McpToolResponse> {
    if (!isAddStreamMessageArgs(args)) {
        throw new Error('Invalid arguments: stream and message parameters are required');
    }

    // Convert all values to strings, handling objects by stringifying them
    const stringMessage = Object.entries(args.message).reduce<Record<string, string>>(
        (acc, [key, value]) => ({
            ...acc,
            [key]: typeof value === 'object' && value !== null ? JSON.stringify(value) : String(value)
        }), 
        {}
    );

    const result = await redis.xAdd(args.stream, '*', stringMessage);

    return {
        content: [{ 
            type: 'text', 
            text: JSON.stringify({ id: result }, null, 2) 
        }]
    };
}