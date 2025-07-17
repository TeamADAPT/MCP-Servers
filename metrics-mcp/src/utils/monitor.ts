import { createClient } from 'redis';
import { logger } from './logger.js';

interface ServiceStatus {
    service: string;
    status: 'up' | 'down' | 'degraded';
    timestamp: string;
    details?: unknown;
}

class ServiceMonitor {
    private redis;
    private readonly SERVICE_NAME = 'metrics-mcp';
    private readonly STATUS_STREAM = 'mcp:service:status';
    private readonly HEALTH_CHECK_INTERVAL = 30000; // 30 seconds
    private isInitialized = false;
    private healthCheckInterval: ReturnType<typeof setInterval> | null = null;

    constructor() {
        this.redis = createClient({
            socket: {
                host: process.env.REDIS_HOST || 'localhost',
                port: parseInt(process.env.REDIS_PORT || '6379'),
            },
        });

        this.redis.on('error', (error: Error) => {
            logger.error('Redis connection error:', error);
        });
    }

    async initialize(): Promise<void> {
        if (this.isInitialized) return;

        try {
            await this.redis.connect();
            this.isInitialized = true;
            logger.info('Service monitor initialized');

            // Start health check interval
            this.healthCheckInterval = setInterval(() => {
                void this.reportStatus('up');
            }, this.HEALTH_CHECK_INTERVAL);

            // Create consumer group for monitoring other services
            try {
                await this.redis.xGroupCreate(this.STATUS_STREAM, 'service-monitors', '0', {
                    MKSTREAM: true
                });
            } catch (error) {
                // Group may already exist, which is fine
                logger.debug('Consumer group creation:', error);
            }

            // Start monitoring other services
            void this.monitorServices();
        } catch (error) {
            logger.error('Failed to initialize service monitor:', error);
            throw error;
        }
    }

    async reportStatus(status: ServiceStatus['status'], details?: unknown): Promise<void> {
        if (!this.isInitialized) {
            logger.warn('Service monitor not initialized');
            return;
        }

        const statusUpdate: ServiceStatus = {
            service: this.SERVICE_NAME,
            status,
            timestamp: new Date().toISOString(),
            details
        };

        try {
            await this.redis.xAdd(this.STATUS_STREAM, '*', {
                data: JSON.stringify(statusUpdate)
            });
            logger.debug('Status reported:', statusUpdate);
        } catch (error) {
            logger.error('Failed to report status:', error);
        }
    }

    private async monitorServices(): Promise<void> {
        while (this.isInitialized) {
            try {
                const results = await this.redis.xReadGroup(
                    'service-monitors',
                    `monitor-${this.SERVICE_NAME}`,
                    [{ key: this.STATUS_STREAM, id: '>' }],
                    { COUNT: 10, BLOCK: 2000 }
                );

                if (results) {
                    for (const result of results) {
                        for (const message of result.messages) {
                            try {
                                const status: ServiceStatus = JSON.parse(message.message.data);
                                if (status.service !== this.SERVICE_NAME) {
                                    logger.info(`Service ${status.service} status: ${status.status}`, status.details);
                                }
                            } catch (error) {
                                logger.error('Error parsing status message:', error);
                            }
                        }
                    }
                }
            } catch (error) {
                logger.error('Error monitoring services:', error);
                await new Promise(resolve => setTimeout(resolve, 5000));
            }
        }
    }

    async reportError(error: Error): Promise<void> {
        await this.reportStatus('degraded', {
            error: error.message,
            stack: error.stack
        });
    }

    async shutdown(): Promise<void> {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
        }

        if (this.isInitialized) {
            await this.reportStatus('down');
            await this.redis.quit();
            this.isInitialized = false;
        }
    }
}

export const monitor = new ServiceMonitor();