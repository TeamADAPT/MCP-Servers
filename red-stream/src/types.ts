import { RedisClientType } from 'redis';

// Redis Types
export interface StreamMessage {
    id: string;
    message: Record<string, string>;
}

export interface StreamEntry {
    name: string;
    messages: StreamMessage[];
}

export type RedisStreamResponse = StreamEntry[] | null;

// Redis Group Info Type
export interface RedisGroupInfo {
    name: string;
    consumers: number;
    pending: number;
    lastDeliveredId: string;
}

// Use the default RedisClientType without type parameters
export type RedisClient = RedisClientType;

// Tool Types
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

// Schema Types
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

// MCP Protocol Response Types
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

// Type Guards
export function isGetStreamMessagesArgs(obj: unknown): obj is GetStreamMessagesArgs {
    return typeof obj === 'object' && 
           obj !== null && 
           'stream' in obj && 
           typeof (obj as any).stream === 'string';
}

export function isAddStreamMessageArgs(obj: unknown): obj is AddStreamMessageArgs {
    return typeof obj === 'object' && 
           obj !== null && 
           'stream' in obj && 
           typeof (obj as any).stream === 'string' &&
           'message' in obj &&
           typeof (obj as any).message === 'object';
}

export function isListStreamsArgs(obj: unknown): obj is ListStreamsArgs {
    return typeof obj === 'object' && 
           obj !== null && 
           (!('pattern' in obj) || typeof (obj as any).pattern === 'string');
}