import { getStreamMessages, getStreamMessagesDefinition } from './get-stream-messages.js';
import { listStreams, listStreamsDefinition } from './list-streams.js';
import { addStreamMessage, addStreamMessageDefinition } from './add-stream-message.js';
import { listGroups, listGroupsDefinition } from './list-groups.js';
import { createConsumerGroup, createConsumerGroupDefinition } from './create-consumer-group.js';
import { readGroup, readGroupDefinition } from './read-group.js';
import { listAllStreams, listAllStreamsDefinition } from './list-all-streams.js';
import { getWatchedStreams, getWatchedStreamsDefinition } from './get-watched-streams.js';
import { addWatchedStream, addWatchedStreamDefinition } from './add-watched-stream.js';
import { removeWatchedStream, removeWatchedStreamDefinition } from './remove-watched-stream.js';
import { checkAllWatchedStreams, checkAllWatchedStreamsDefinition } from './check-all-watched-streams.js';
import { RedisClient, McpToolResponse, ToolDefinition } from '../types.js';

type ToolFunction = (redis: RedisClient, args: unknown) => Promise<McpToolResponse>;

export const tools: Record<string, ToolFunction> = {
    get_stream_messages: getStreamMessages,
    list_streams: listStreams,
    add_stream_message: addStreamMessage,
    list_groups: listGroups,
    create_consumer_group: createConsumerGroup,
    read_group: readGroup,
    list_all_streams: listAllStreams,
    get_watched_streams: getWatchedStreams,
    add_watched_stream: addWatchedStream,
    remove_watched_stream: removeWatchedStream,
    check_all_watched_streams: checkAllWatchedStreams,
} as const;

export const toolDefinitions: Record<string, ToolDefinition> = {
    get_stream_messages: getStreamMessagesDefinition,
    list_streams: listStreamsDefinition,
    add_stream_message: addStreamMessageDefinition,
    list_groups: listGroupsDefinition,
    create_consumer_group: createConsumerGroupDefinition,
    read_group: readGroupDefinition,
    list_all_streams: listAllStreamsDefinition,
    get_watched_streams: getWatchedStreamsDefinition,
    add_watched_stream: addWatchedStreamDefinition,
    remove_watched_stream: removeWatchedStreamDefinition,
    check_all_watched_streams: checkAllWatchedStreamsDefinition,
} as const;

export type ToolName = keyof typeof tools;

export function isValidToolName(name: string): name is ToolName {
    return name in tools;
}

export async function executeTool(
    toolName: string,
    redis: RedisClient,
    toolArgs: unknown
): Promise<McpToolResponse> {
    if (!isValidToolName(toolName)) {
        throw new Error(`Unknown tool: ${toolName}`);
    }

    return tools[toolName](redis, toolArgs);
}