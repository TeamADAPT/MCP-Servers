import { RedisClient, McpToolResponse } from '../types.js';
export declare const listGroupsDefinition: {
    name: "list_groups";
    description: string;
    inputSchema: {
        type: "object";
        properties: {
            stream: {
                type: string;
                description: string;
            };
        };
        required: string[];
    };
};
export declare function listGroups(redis: RedisClient, args: unknown): Promise<McpToolResponse>;
