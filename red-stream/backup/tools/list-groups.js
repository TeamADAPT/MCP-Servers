function isListGroupsArgs(obj) {
    return typeof obj === 'object' &&
        obj !== null &&
        'stream' in obj &&
        typeof obj.stream === 'string';
}
export const listGroupsDefinition = {
    name: 'list_groups',
    description: 'Lists all consumer groups for a specified stream',
    inputSchema: {
        type: 'object',
        properties: {
            stream: {
                type: 'string',
                description: 'Name of the stream'
            }
        },
        required: ['stream']
    }
};
export async function listGroups(redis, args) {
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
