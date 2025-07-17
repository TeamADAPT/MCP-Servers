import { RedisClient, McpToolResponse, ToolDefinition } from '../types.js';
type ToolFunction = (redis: RedisClient, args: unknown) => Promise<McpToolResponse>;
export declare const tools: Record<string, ToolFunction>;
export declare const toolDefinitions: Record<string, ToolDefinition>;
export type ToolName = keyof typeof tools;
export declare function isValidToolName(name: string): name is ToolName;
export declare function executeTool(toolName: string, redis: RedisClient, toolArgs: unknown): Promise<McpToolResponse>;
export {};
