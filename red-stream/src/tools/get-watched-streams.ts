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

export interface GetWatchedStreamsArgs {
    userId: string;
}

export const getWatchedStreamsDefinition = {
    name: 'get_watched_streams',
    description: 'Get the list of streams the user is watching',
    inputSchema: {
        type: 'object' as const,
        properties: {
            userId: {
                type: 'string',
                description: 'User ID',
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

export async function getWatchedStreams(redis: RedisClient, args: unknown): Promise<McpToolResponse> {
    if (!isGetWatchedStreamsArgs(args)) {
        throw new Error('Invalid arguments: User ID is required');
    }

    const streams = getUserStreams(args.userId);
    
    return {
        content: [
            {
                type: 'text',
                text: JSON.stringify(streams, null, 2),
            },
        ],
    };
}

export function isGetWatchedStreamsArgs(obj: unknown): obj is GetWatchedStreamsArgs {
    return typeof obj === 'object' && 
           obj !== null && 
           'userId' in obj && 
           typeof (obj as any).userId === 'string';
}