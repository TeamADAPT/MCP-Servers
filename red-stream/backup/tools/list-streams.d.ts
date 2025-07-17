import { RedisClient, McpToolResponse } from '../types.js';
export declare const listStreamsDefinition: {
    name: "list_streams";
    description: string;
    inputSchema: {
        type: "object";
        properties: {
            pattern: {
                type: string;
                description: string;
                default: string;
            };
        };
    };
};
export declare function listStreams(redis: RedisClient, args: unknown): Promise<McpToolResponse>;
