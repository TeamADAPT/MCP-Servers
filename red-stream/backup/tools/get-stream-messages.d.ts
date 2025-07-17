import { RedisClient, McpToolResponse } from '../types.js';
export declare const getStreamMessagesDefinition: {
    name: "get_stream_messages";
    description: string;
    inputSchema: {
        type: "object";
        properties: {
            stream: {
                type: string;
                description: string;
            };
            count: {
                type: string;
                description: string;
                default: number;
            };
            start: {
                type: string;
                description: string;
                default: string;
            };
        };
        required: string[];
    };
};
export declare function getStreamMessages(redis: RedisClient, args: unknown): Promise<McpToolResponse>;
