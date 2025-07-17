import { isListStreamsArgs } from '../types.js';
export const listStreamsDefinition = {
    name: 'list_streams',
    description: 'List all available Redis streams',
    inputSchema: {
        type: 'object',
        properties: {
            pattern: {
                type: 'string',
                description: 'Pattern to match stream names (e.g., "user:*")',
                default: '*'
            }
        }
    }
};
export async function listStreams(redis, args) {
    if (!isListStreamsArgs(args)) {
        throw new Error('Invalid arguments');
    }
    const pattern = args.pattern || '*';
    const streamKeys = await redis.keys(pattern);
    // Filter to only include stream keys by checking their type
    const streams = await Promise.all(streamKeys.map(async (streamKey) => {
        const type = await redis.type(streamKey);
        return type === 'stream' ? streamKey : null;
    }));
    const streamList = streams.filter((streamKey) => streamKey !== null);
    return {
        content: [{
                type: 'text',
                text: JSON.stringify(streamList, null, 2)
            }]
    };
}
