import { RedisClientType } from 'redis';
export interface StreamMessage {
    id: string;
    message: Record<string, string>;
}
export interface StreamEntry {
    name: string;
    messages: StreamMessage[];
}
export type RedisStreamResponse = StreamEntry[] | null;
export interface RedisGroupInfo {
    name: string;
    consumers: number;
    pending: number;
    lastDeliveredId: string;
}
export type RedisClient = RedisClientType;
export interface GetStreamMessagesArgs {
    stream: string;
    count?: number;
    start?: string;
}
export interface AddStreamMessageArgs {
    stream: string;
    message: Record<string, unknown>;
}
export interface ListStreamsArgs {
    pattern?: string;
}
export interface SchemaProperty {
    type: string;
    description: string;
    default?: unknown;
}
export interface SchemaProperties {
    [key: string]: SchemaProperty;
}
export interface InputSchema {
    type: 'object';
    properties: SchemaProperties;
    required?: string[];
}
export interface ToolDefinition {
    name: string;
    description?: string;
    inputSchema: InputSchema;
}
export interface McpToolContent {
    type: 'text';
    text: string;
}
export interface McpToolResponse {
    content: McpToolContent[];
    _meta?: Record<string, unknown>;
}
export interface McpListToolsResponse {
    tools: ToolDefinition[];
    _meta?: Record<string, unknown>;
}
export interface McpToolCapabilities {
    [key: string]: ToolDefinition;
}
export declare function isGetStreamMessagesArgs(obj: unknown): obj is GetStreamMessagesArgs;
export declare function isAddStreamMessageArgs(obj: unknown): obj is AddStreamMessageArgs;
export declare function isListStreamsArgs(obj: unknown): obj is ListStreamsArgs;
