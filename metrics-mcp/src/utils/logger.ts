import fs from 'fs';
import path from 'path';
import winston from 'winston';

const { createLogger, format, transports } = winston;
const { combine, timestamp, printf } = format;

class Logger {
    private logger: winston.Logger;
    private readonly logDir = path.join(process.cwd(), 'logs');

    constructor() {
        // Create logs directory if it doesn't exist
        if (!fs.existsSync(this.logDir)) {
            fs.mkdirSync(this.logDir, { recursive: true });
        }

        // Create daily log file name
        const date = new Date().toISOString().split('T')[0];
        const logFile = path.join(this.logDir, `metrics-mcp-${date}.log`);

        // Custom log format
        const logFormat = printf(({ level, message, timestamp, ...meta }) => {
            const metaStr = Object.keys(meta).length ? ` ${JSON.stringify(meta)}` : '';
            return `${timestamp} [${level.toUpperCase()}] ${message}${metaStr}`;
        });

        // Create logger instance
        this.logger = createLogger({
            format: combine(
                timestamp(),
                logFormat
            ),
            transports: [
                // Console transport
                new transports.Console({
                    level: 'debug',
                    handleExceptions: true,
                }),
                // File transport
                new transports.File({
                    filename: logFile,
                    level: 'info',
                    handleExceptions: true,
                    maxsize: 5242880, // 5MB
                    maxFiles: 5,
                }),
            ],
            exitOnError: false,
        });
    }

    info(message: string, meta?: unknown): void {
        this.logger.info(message, meta);
    }

    error(message: string, meta?: unknown): void {
        this.logger.error(message, meta);
    }

    warn(message: string, meta?: unknown): void {
        this.logger.warn(message, meta);
    }

    debug(message: string, meta?: unknown): void {
        if (process.env.DEBUG === 'true') {
            this.logger.debug(message, meta);
        }
    }

    async close(): Promise<void> {
        return new Promise((resolve) => {
            this.logger.on('finish', resolve);
            this.logger.end();
        });
    }
}

export const logger = new Logger();