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

export interface RemoveWatchedStreamArgs {
    userId: string;
    streamName: string;
}

export const removeWatchedStreamDefinition = {
    name: 'remove_watched_stream',
    description: 'Remove a stream from the user\'s watch list',
    inputSchema: {
        type: 'object' as const,
        properties: {
            userId: {
                type: 'string',
                description: 'User ID',
            },
            streamName: {
                type: 'string',
                description: 'Stream name to remove',
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

// Helper function to remove user stream
function removeUserStream(userId: string, streamName: string): boolean {
    const preferences = loadPreferences();
    
    if (!preferences[userId]) {
        return false;
    }
    
    const index = preferences[userId].indexOf(streamName);
    if (index !== -1) {
        preferences[userId].splice(index, 1);
        savePreferences(preferences);
        return true;
    }
    
    return false;
}

export async function removeWatchedStream(redis: RedisClient, args: unknown): Promise<McpToolResponse> {
    if (!isRemoveWatchedStreamArgs(args)) {
        throw new Error('Invalid arguments: User ID and stream name are required');
    }

    const removed = removeUserStream(args.userId, args.streamName);
    
    return {
        content: [
            {
                type: 'text',
                text: removed
                    ? `Stream "${args.streamName}" removed from user ${args.userId}'s watch list`
                    : `Stream "${args.streamName}" was not in user ${args.userId}'s watch list`,
            },
        ],
    };
}

export function isRemoveWatchedStreamArgs(obj: unknown): obj is RemoveWatchedStreamArgs {
    return typeof obj === 'object' && 
           obj !== null && 
           'userId' in obj && 
           typeof (obj as any).userId === 'string' &&
           'streamName' in obj &&
           typeof (obj as any).streamName === 'string';
}