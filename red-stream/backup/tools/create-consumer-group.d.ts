import { RedisClient, McpToolResponse } from '../types.js';
export declare const createConsumerGroupDefinition: {
    name: "create_consumer_group";
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
            start: {
                type: string;
                description: string;
                default: string;
            };
        };
        required: string[];
    };
};
export declare function createConsumerGroup(redis: RedisClient, args: unknown): Promise<McpToolResponse>;
