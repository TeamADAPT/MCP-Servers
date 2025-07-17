import { GetStreamMessagesArgs, RedisClient, McpToolResponse, isGetStreamMessagesArgs } from '../types.js';

export const getStreamMessagesDefinition = {
    name: 'get_stream_messages' as const,
    description: 'Get messages from a Redis Stream',
    inputSchema: {
        type: 'object' as const,
        properties: {
            stream: { 
                type: 'string', 
                description: 'Name of the stream' 
            },
            count: { 
                type: 'number', 
                description: 'Number of messages to retrieve', 
                default: 1 
            },
            start: { 
                type: 'string', 
                description: 'Start ID (0 for beginning, $ for end)', 
                default: '0' 
            }
        },
        required: ['stream']
    }
};

export async function getStreamMessages(
    redis: RedisClient,
    args: unknown
): Promise<McpToolResponse> {
    if (!isGetStreamMessagesArgs(args)) {
        throw new Error('Invalid arguments: stream parameter is required');
    }

    const rawMessages = await redis.xRead(
        [{ key: args.stream, id: args.start || '0' }],
        { COUNT: args.count || 1 }
    );

    // Parse any JSON string values back into objects
    const messages = rawMessages?.map(stream => ({
        name: stream.name,
        messages: stream.messages.map(msg => ({
            id: msg.id,
            message: Object.entries(msg.message).reduce((acc, [key, value]) => {
                try {
                    // Try parsing any string value as JSON
                    if (typeof value === 'string') {
                        try {
                            const parsed = JSON.parse(value);
                            return { ...acc, [key]: parsed };
                        } catch (e) {
                            // If parsing fails, use the original value
                            return { ...acc, [key]: value };
                        }
                    }
                    return { ...acc, [key]: value };
                } catch (e) {
                    // If any error occurs, use the original value
                    return { ...acc, [key]: value };
                }
            }, {})
        }))
    }));

    return {
        content: [{ 
            type: 'text', 
            text: JSON.stringify(
                messages || [],
                null,
                2
            ) 
        }]
    };
}