#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import * as fs from 'fs-extra';
import * as path from 'path';
import * as chokidar from 'chokidar';
import { homedir } from 'os';

// Dangerous commands that should never be allowed
const BLACKLISTED_COMMANDS = [
  'mkfs',
  'mkfs.ext2',
  'mkfs.ext3', 
  'mkfs.ext4',
  'mkfs.xfs',
  'mkfs.btrfs',
  'mkfs.fat',
  'mkfs.msdos',
  'mkfs.vfat',
  'mkfs.ntfs',
  'format',
  'fdformat',
  'mke2fs',
  'mkntfs',
  'wipefs'
];

// VSCode settings path
const VSCODE_SETTINGS_PATH = path.join(homedir(), '.config/Code/User/settings.json');

interface VSCodeSettings {
  'roo-cline.allowedCommands': string[];
  [key: string]: any;
}

class CommandManager {
  private server: Server;
  private allowedCommands: Set<string>;

  constructor() {
    this.server = new Server(
      {
        name: 'command-manager',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.allowedCommands = new Set<string>();
    this.loadAllowedCommands();
    this.setupTools();
    this.watchCommandExecutions();

    // Error handling
    this.server.onerror = (error: Error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  private loadAllowedCommands() {
    try {
      const settings = fs.readJsonSync(VSCODE_SETTINGS_PATH) as VSCodeSettings;
      this.allowedCommands = new Set(settings['roo-cline.allowedCommands'] || []);
    } catch (error) {
      console.error('Error loading allowed commands:', error);
      this.allowedCommands = new Set();
    }
  }

  private async updateSettings() {
    try {
      const settings = await fs.readJson(VSCODE_SETTINGS_PATH) as VSCodeSettings;
      settings['roo-cline.allowedCommands'] = Array.from(this.allowedCommands);
      await fs.writeJson(VSCODE_SETTINGS_PATH, settings, { spaces: 4 });
      
      // Create backup with date
      const date = new Date().toISOString().split('T')[0].replace(/-/g, '');
      const backupPath = path.join(
        path.dirname(VSCODE_SETTINGS_PATH),
        `settings_allowed_list_${date}.json`
      );
      await fs.copyFile(VSCODE_SETTINGS_PATH, backupPath);
    } catch (error) {
      console.error('Error updating settings:', error);
    }
  }

  private isCommandSafe(command: string): boolean {
    // Check if command or any part of it is blacklisted
    const commandParts = command.split(' ');
    return !BLACKLISTED_COMMANDS.some(blacklisted => 
      commandParts.some(part => part === blacklisted)
    );
  }

  private setupTools() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'add_command',
          description: 'Add a new command to the allowed list',
          inputSchema: {
            type: 'object',
            properties: {
              command: {
                type: 'string',
                description: 'Command to add',
              },
            },
            required: ['command'],
          },
        },
        {
          name: 'check_command',
          description: 'Check if a command is allowed',
          inputSchema: {
            type: 'object',
            properties: {
              command: {
                type: 'string',
                description: 'Command to check',
              },
            },
            required: ['command'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      switch (request.params.name) {
        case 'add_command': {
          const { command } = request.params.arguments as { command: string };
          
          if (!this.isCommandSafe(command)) {
            return {
              content: [
                {
                  type: 'text',
                  text: `Command '${command}' is blacklisted for safety reasons`,
                },
              ],
              isError: true,
            };
          }

          if (!this.allowedCommands.has(command)) {
            this.allowedCommands.add(command);
            await this.updateSettings();
          }

          return {
            content: [
              {
                type: 'text',
                text: `Command '${command}' added to allowed list`,
              },
            ],
          };
        }

        case 'check_command': {
          const { command } = request.params.arguments as { command: string };
          
          const isAllowed = this.allowedCommands.has(command);
          const isSafe = this.isCommandSafe(command);

          return {
            content: [
              {
                type: 'text',
                text: `Command '${command}' is ${isAllowed ? 'allowed' : 'not allowed'} and ${isSafe ? 'safe' : 'unsafe'}`,
              },
            ],
          };
        }

        default:
          throw new McpError(
            ErrorCode.MethodNotFound,
            `Unknown tool: ${request.params.name}`
          );
      }
    });
  }

  private watchCommandExecutions() {
    // Watch for command execution attempts
    // This could be implemented by watching a log file or through other means
    // For now, we'll just watch the settings file for changes
    const watcher = chokidar.watch(VSCODE_SETTINGS_PATH, {
      persistent: true,
      ignoreInitial: true,
    });

    watcher.on('change', () => {
      this.loadAllowedCommands();
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Command Manager MCP server running on stdio');
  }
}

const manager = new CommandManager();
manager.run().catch((error: Error) => console.error(error));
