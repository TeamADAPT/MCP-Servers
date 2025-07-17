import { RedisClient, McpToolResponse } from '../types.js';
export declare const readGroupDefinition: {
    name: "read_group";
    description: string;
    inputSchema: {
        type: "object";
        properties: {
            stream: {
                type: string;
                description: string;
            };
            group: {
                type: string;
                description: string;
            };
            consumer: {
                type: string;
                description: string;
            };
            count: {
                type: string;
                description: string;
                default: number;
            };
        };
        required: string[];
    };
};
export declare function readGroup(redis: RedisClient, args: unknown): Promise<McpToolResponse>;
