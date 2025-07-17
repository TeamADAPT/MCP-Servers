import { getStreamMessages, getStreamMessagesDefinition } from './get-stream-messages.js';
import { listStreams, listStreamsDefinition } from './list-streams.js';
import { addStreamMessage, addStreamMessageDefinition } from './add-stream-message.js';
import { listGroups, listGroupsDefinition } from './list-groups.js';
import { createConsumerGroup, createConsumerGroupDefinition } from './create-consumer-group.js';
import { readGroup, readGroupDefinition } from './read-group.js';
export const tools = {
    get_stream_messages: getStreamMessages,
    list_streams: listStreams,
    add_stream_message: addStreamMessage,
    list_groups: listGroups,
    create_consumer_group: createConsumerGroup,
    read_group: readGroup,
};
export const toolDefinitions = {
    get_stream_messages: getStreamMessagesDefinition,
    list_streams: listStreamsDefinition,
    add_stream_message: addStreamMessageDefinition,
    list_groups: listGroupsDefinition,
    create_consumer_group: createConsumerGroupDefinition,
    read_group: readGroupDefinition,
};
export function isValidToolName(name) {
    return name in tools;
}
export async function executeTool(toolName, redis, toolArgs) {
    if (!isValidToolName(toolName)) {
        throw new Error(`Unknown tool: ${toolName}`);
    }
    return tools[toolName](redis, toolArgs);
}
