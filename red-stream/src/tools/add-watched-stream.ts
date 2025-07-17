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

export interface AddWatchedStreamArgs {
    userId: string;
    streamName: string;
}

export const addWatchedStreamDefinition = {
    name: 'add_watched_stream',
    description: 'Add a stream to the user\'s watch list',
    inputSchema: {
        type: 'object' as const,
        properties: {
            userId: {
                type: 'string',
                description: 'User ID',
            },
            streamName: {
                type: 'string',
                description: 'Stream name to add',
            },
        },
        required: ['userId', 'streamName'],
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

// Helper function to save preferences
function savePreferences(preferences: Record<string, string[]>): void {
    try {
        fs.writeJSONSync(CONFIG_FILE, preferences, { spaces: 2 });
    } catch (error) {
        console.error('[RedStream] Error saving preferences:', error);
    }
}

// Helper function to add user stream
function addUserStream(userId: string, streamName: string): void {
    const preferences = loadPreferences();
    
    if (!preferences[userId]) {
        preferences[userId] = [];
    }
    
    if (!preferences[userId].includes(streamName)) {
        preferences[userId].push(streamName);
        savePreferences(preferences);
    }
}

export async function addWatchedStream(redis: RedisClient, args: unknown): Promise<McpToolResponse> {
    if (!isAddWatchedStreamArgs(args)) {
        throw new Error('Invalid arguments: User ID and stream name are required');
    }

    // Verify the stream exists
    try {
        // Use Redis SCAN to get all keys that match the stream pattern
        let streamExists = false;
        let cursor = 0;
        
        do {
            const result = await redis.scan(cursor, { MATCH: '*', COUNT: 100 });
            cursor = result.cursor;
            
            // Check if the stream exists
            for (const key of result.keys) {
                const type = await redis.type(key) as string;
                if (type === 'stream' && key === args.streamName) {
                    streamExists = true;
                    break;
                }
            }
            
            if (streamExists) {
                break;
            }
        } while (cursor !== 0);
        
        if (!streamExists) {
            throw new Error(`Stream "${args.streamName}" does not exist`);
        }
    } catch (error: any) {
        console.error('[RedStream] Error verifying stream:', error);
        throw new Error(`Failed to verify stream: ${error.message}`);
    }

    addUserStream(args.userId, args.streamName);
    
    return {
        content: [
            {
                type: 'text',
                text: `Stream "${args.streamName}" added to user ${args.userId}'s watch list`,
            },
        ],
    };
}

export function isAddWatchedStreamArgs(obj: unknown): obj is AddWatchedStreamArgs {
    return typeof obj === 'object' && 
           obj !== null && 
           'userId' in obj && 
           typeof (obj as any).userId === 'string' &&
           'streamName' in obj &&
           typeof (obj as any).streamName === 'string';
}