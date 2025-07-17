import { RedisClient, McpToolResponse } from '../types.js';
export declare const addStreamMessageDefinition: {
    name: "add_stream_message";
    description: string;
    inputSchema: {
        type: "object";
        properties: {
            stream: {
                type: string;
                description: string;
            };
            message: {
                type: string;
                description: string;
            };
        };
        required: string[];
    };
};
export declare function addStreamMessage(redis: RedisClient, args: unknown): Promise<McpToolResponse>;
