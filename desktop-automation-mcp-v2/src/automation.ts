import { exec } from 'child_process';
import { promisify } from 'util';
import { appendFile, readFile, unlink } from 'fs/promises';
import * as activeWin from 'active-win';
import keySender from 'node-key-sender';
import { join } from 'path';
import { homedir } from 'os';

const execAsync = promisify(exec);
const LOG_FILE = '/home/x/Documents/roo_cline_mcp_optimize/desktop-automation.log';
const SCREENSHOT_DIR = join(homedir(), '.config/desktop-automation/screenshots');

async function log(message: string) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}\n`;
    await appendFile(LOG_FILE, logMessage);
}

export class DesktopAutomation {
    private isInitialized: boolean = false;
    private lastLaunchedWindowId: string | null = null;
    private screenshotCounter: number = 0;

    constructor() {
        this.initialize();
    }

    private async initialize() {
        if (!this.isInitialized) {
            await log('Initializing DesktopAutomation');
            if (process.platform === 'linux') {
                try {
                    await execAsync('which xdotool weston-screenshooter');
                    await log('Required tools found');
                } catch (error) {
                    const errorMsg = 'Required tools not installed. Please install using: sudo apt-get install xdotool weston';
                    await log(`Error: ${errorMsg}`);
                    throw new Error(errorMsg);
                }

                // Create screenshot directory
                try {
                    await execAsync(`mkdir -p ${SCREENSHOT_DIR}`);
                    await log(`Created screenshot directory: ${SCREENSHOT_DIR}`);
                } catch (error) {
                    await log(`Error creating screenshot directory: ${error}`);
                }
            }
            this.isInitialized = true;
            await log('Initialization complete');
        }
    }

    private async getScreenResolution(): Promise<{ width: number; height: number }> {
        try {
            const { stdout } = await execAsync('xdpyinfo | grep dimensions');
            const match = stdout.match(/dimensions:\s+(\d+)x(\d+)/);
            if (match) {
                const resolution = {
                    width: parseInt(match[1]),
                    height: parseInt(match[2])
                };
                await log(`Screen resolution: ${resolution.width}x${resolution.height}`);
                return resolution;
            }
        } catch (error) {
            await log(`Error getting screen resolution: ${error}`);
        }
        const defaultResolution = { width: 1920, height: 1080 };
        await log(`Using default resolution: ${defaultResolution.width}x${defaultResolution.height}`);
        return defaultResolution;
    }

    async mouseMove(x: number, y: number): Promise<void> {
        await this.initialize();
        await log(`Moving mouse to ${x},${y}`);
        if (process.platform === 'linux') {
            await execAsync(`xdotool mousemove ${x} ${y}`);
            await this.captureScreen(); // Take a screenshot after moving
        }
    }

    async mouseClick(x: number, y: number, button: 'left' | 'right' = 'left'): Promise<void> {
        await this.initialize();
        await log(`Clicking mouse at ${x},${y} with ${button} button`);
        if (process.platform === 'linux') {
            await execAsync(`xdotool mousemove ${x} ${y} click ${button === 'left' ? '1' : '3'}`);
            await this.captureScreen(); // Take a screenshot after clicking
        }
    }

    async typeText(text: string): Promise<void> {
        await this.initialize();
        await log(`Typing text: ${text}`);
        if (process.platform === 'linux') {
            await execAsync(`xdotool type "${text}"`);
            await this.captureScreen(); // Take a screenshot after typing
        } else {
            await keySender.sendText(text);
        }
    }

    async pressKey(key: string): Promise<void> {
        await this.initialize();
        await log(`Pressing key: ${key}`);
        if (process.platform === 'linux') {
            const xdoKey = this.mapKeyToXdotool(key);
            if (xdoKey) {
                await execAsync(`xdotool key ${xdoKey}`);
                await this.captureScreen(); // Take a screenshot after key press
            }
        } else {
            await keySender.sendKey(this.mapKeyToKeySender(key));
        }
    }

    async launchApp(appName: string): Promise<void> {
        await this.initialize();
        await log(`Launching app: ${appName}`);
        
        try {
            if (appName.toLowerCase() === 'code' || appName.toLowerCase() === 'vscode') {
                if (process.platform === 'linux') {
                    try {
                        await execAsync('code --new-window');
                    } catch {
                        try {
                            await execAsync('/usr/bin/code --new-window');
                        } catch {
                            await execAsync('/usr/share/code/code --new-window');
                        }
                    }

                    await log('Waiting for window to appear');
                    await new Promise(resolve => setTimeout(resolve, 3000));

                    try {
                        const { width, height } = await this.getScreenResolution();
                        
                        const { stdout: windowIds } = await execAsync('xdotool search --name "Visual Studio Code"');
                        const windowId = windowIds.split('\n').filter(Boolean).pop();
                        
                        if (windowId) {
                            this.lastLaunchedWindowId = windowId;
                            await log(`Found window ID: ${windowId}`);
                            
                            await execAsync(`xdotool windowmove ${windowId} 0 0 windowsize ${windowId} ${width} ${height}`);
                            await execAsync(`xdotool windowactivate ${windowId}`);
                            await log('Window positioned and activated');
                            await this.captureScreen(); // Take a screenshot after launch
                        }
                    } catch (error) {
                        await log(`Error maximizing window: ${error}`);
                    }
                } else if (process.platform === 'darwin') {
                    await execAsync('open -n -b "com.microsoft.VSCode" --args --new-window');
                } else if (process.platform === 'win32') {
                    await execAsync('code --new-window');
                }
            } else {
                if (process.platform === 'linux') {
                    try {
                        await execAsync(`gtk-launch ${appName}.desktop`);
                    } catch {
                        await execAsync(appName);
                    }
                } else if (process.platform === 'darwin') {
                    await execAsync(`open -a "${appName}"`);
                } else if (process.platform === 'win32') {
                    await execAsync(`start ${appName}`);
                }
            }
            
            await log('Waiting for application to launch');
            await new Promise(resolve => setTimeout(resolve, 2000));
            
        } catch (error) {
            await log(`Error launching ${appName}: ${error}`);
            throw new Error(`Failed to launch ${appName}`);
        }
    }

    async closeApp(appName: string): Promise<void> {
        await log(`Closing app: ${appName}`);
        if (process.platform === 'linux') {
            if (appName.toLowerCase() === 'code' || appName.toLowerCase() === 'vscode') {
                if (this.lastLaunchedWindowId) {
                    try {
                        await execAsync(`xdotool windowclose ${this.lastLaunchedWindowId}`);
                        this.lastLaunchedWindowId = null;
                        await log('Closed specific window');
                    } catch (error) {
                        await log(`Error closing window: ${error}`);
                    }
                } else {
                    await log('No specific window to close');
                }
            } else {
                await execAsync(`pkill -f "${appName}"`);
            }
        } else if (process.platform === 'darwin') {
            await execAsync(`osascript -e 'quit app "${appName}"'`);
        } else if (process.platform === 'win32') {
            await execAsync(`taskkill /IM "${appName}.exe"`);
        }
    }

    async captureScreen(): Promise<Uint8Array | null> {
        try {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const screenshotPath = join(SCREENSHOT_DIR, `screen_${this.screenshotCounter++}_${timestamp}.png`);
            
            // Use weston-screenshooter for Wayland
            await execAsync(`weston-screenshooter --output='${screenshotPath}'`);
            await log(`Screenshot saved to: ${screenshotPath}`);

            // Read the screenshot file
            const screenshotData = await readFile(screenshotPath);
            
            // Clean up the file
            await unlink(screenshotPath);
            
            return screenshotData;
        } catch (error) {
            await log(`Error capturing screen: ${error}`);
            return null;
        }
    }

    private mapKeyToXdotool(key: string): string | null {
        const keyMap: { [key: string]: string } = {
            'enter': 'Return',
            'tab': 'Tab',
            'space': 'space',
            'backspace': 'BackSpace',
            'escape': 'Escape',
            'up': 'Up',
            'down': 'Down',
            'left': 'Left',
            'right': 'Right',
            'home': 'Home',
            'end': 'End',
            'pageup': 'Page_Up',
            'pagedown': 'Page_Down',
            'delete': 'Delete',
            'insert': 'Insert',
            'f11': 'F11'
        };

        return keyMap[key.toLowerCase()] || null;
    }

    private mapKeyToKeySender(key: string): string {
        const keyMap: { [key: string]: string } = {
            'enter': 'ENTER',
            'tab': 'TAB',
            'space': 'SPACE',
            'backspace': 'BACK_SPACE',
            'escape': 'ESCAPE',
            'up': 'UP',
            'down': 'DOWN',
            'left': 'LEFT',
            'right': 'RIGHT',
            'home': 'HOME',
            'end': 'END',
            'pageup': 'PAGE_UP',
            'pagedown': 'PAGE_DOWN',
            'delete': 'DELETE',
            'insert': 'INSERT',
            'f11': 'F11'
        };

        return keyMap[key.toLowerCase()] || key.toUpperCase();
    }
}