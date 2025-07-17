function isCreateConsumerGroupArgs(obj) {
    return typeof obj === 'object' &&
        obj !== null &&
        'stream' in obj &&
        typeof obj.stream === 'string' &&
        'group' in obj &&
        typeof obj.group === 'string';
}
export const createConsumerGroupDefinition = {
    name: 'create_consumer_group',
    description: 'Creates a new consumer group for a stream',
    inputSchema: {
        type: 'object',
        properties: {
            stream: {
                type: 'string',
                description: 'Name of the stream'
            },
            group: {
                type: 'string',
                description: 'Consumer group name'
            },
            start: {
                type: 'string',
                description: 'Start position (default: "$")',
                default: '$'
            }
        },
        required: ['stream', 'group']
    }
};
export async function createConsumerGroup(redis, args) {
    if (!isCreateConsumerGroupArgs(args)) {
        throw new Error('Invalid arguments: stream and group are required');
    }
    try {
        await redis.xGroupCreate(args.stream, args.group, args.start || '$', { MKSTREAM: true });
        return {
            content: [{
                    type: 'text',
                    text: JSON.stringify({
                        success: true,
                        note: `Created consumer group '${args.group}' for stream '${args.stream}'`
                    }, null, 2)
                }]
        };
    }
    catch (error) {
        if (error instanceof Error && error.message.includes('BUSYGROUP')) {
            return {
                content: [{
                        type: 'text',
                        text: JSON.stringify({
                            success: false,
                            note: `Consumer group '${args.group}' already exists for stream '${args.stream}'`
                        }, null, 2)
                    }]
            };
        }
        throw error;
    }
}
