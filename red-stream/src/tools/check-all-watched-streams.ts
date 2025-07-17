import { McpToolResponse, RedisClient } from '../types.js';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const CONFIG_DIR = process.env.CONFIG_DIR || path.join(__dirname, '..', '..', 'config');
const CONFIG_FILE = path.join(CONFIG_DIR, 'stream_preferences.json');

// Ensure config directory exists
fs.ensureDirSync(CONFIG_DIR);

export interface CheckAllWatchedStreamsArgs {
    userId: string;
    messageCount?: number;
}

export const checkAllWatchedStreamsDefinition = {
    name: 'check_all_watched_streams',
    description: 'Check all streams in the user\'s watch list',
    inputSchema: {
        type: 'object' as const,
        properties: {
            userId: {
                type: 'string',
                description: 'User ID',
            },
            messageCount: {
                type: 'number',
                description: 'Number of messages to retrieve per stream',
                default: 5,
            },
        },
        required: ['userId'],
    },
};

// Helper function to load preferences
function loadPreferences(): Record<string, string[]> {
    try {
        if (fs.existsSync(CONFIG_FILE)) {
            return fs.readJSONSync(CONFIG_FILE);
        } else {
            console.error('[RedStream] No preferences file found, creating new one');
            fs.writeJSONSync(CONFIG_FILE, {}, { spaces: 2 });
            return {};
        }
    } catch (error) {
        console.error('[RedStream] Error loading preferences:', error);
        fs.writeJSONSync(CONFIG_FILE, {}, { spaces: 2 });
        return {};
    }
}

// Helper function to get user streams
function getUserStreams(userId: string): string[] {
    const preferences = loadPreferences();
    return preferences[userId] || [];
}

// Helper function to get stream messages
async function getStreamMessages(redis: RedisClient, streamName: string, count: number = 5): Promise<any[]> {
    try {
        const messages = await redis.xRevRange(streamName, '+', '-', { COUNT: count });
        return messages.map(({ id, message }) => {
            // Try to parse JSON values in the message
            const messageObj: Record<string, any> = { ...message };
            for (const key in messageObj) {
                try {
                    // Try to parse as JSON, fall back to string if not valid JSON
                    messageObj[key] = JSON.parse(messageObj[key] as string);
                } catch {
                    // Keep as is if not valid JSON
                }
            }
            return { id, message: messageObj };
        });
    } catch (error: any) {
        console.error(`[RedStream] Error getting messages from stream ${streamName}:`, error);
        return [];
    }
}

export async function checkAllWatchedStreams(redis: RedisClient, args: unknown): Promise<McpToolResponse> {
    if (!isCheckAllWatchedStreamsArgs(args)) {
        throw new Error('Invalid arguments: User ID is required');
    }

    const messageCount = typeof args.messageCount === 'number' ? args.messageCount : 5;
    const streams = getUserStreams(args.userId);
    
    if (streams.length === 0) {
        return {
            content: [
                {
                    type: 'text',
                    text: `User ${args.userId} is not watching any streams`,
                },
            ],
        };
    }

    const results: Record<string, any[]> = {};
    
    for (const stream of streams) {
        results[stream] = await getStreamMessages(redis, stream, messageCount);
    }

    return {
        content: [
            {
                type: 'text',
                text: JSON.stringify(results, null, 2),
            },
        ],
    };
}

export function isCheckAllWatchedStreamsArgs(obj: unknown): obj is CheckAllWatchedStreamsArgs {
    return typeof obj === 'object' && 
           obj !== null && 
           'userId' in obj && 
           typeof (obj as any).userId === 'string' &&
           (!('messageCount' in obj) || typeof (obj as any).messageCount === 'number');
}