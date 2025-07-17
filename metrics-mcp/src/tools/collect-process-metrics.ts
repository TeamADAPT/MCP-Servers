import { ProcessMetrics } from '../types.js';
import { logger } from '../utils/logger.js';

export async function collectProcessMetrics(): Promise<ProcessMetrics> {
    logger.debug('Collecting process metrics');
    
    try {
        // CPU usage metrics
        const startUsage = process.cpuUsage();
        // Small delay to calculate CPU usage
        await new Promise(resolve => setTimeout(resolve, 100));
        const endUsage = process.cpuUsage(startUsage);
        
        // Convert from microseconds to percentage
        const totalUsage = (endUsage.user + endUsage.system) / 1000000;
        const userUsage = endUsage.user / 1000000;
        const systemUsage = endUsage.system / 1000000;

        // Memory metrics
        const memoryUsage = process.memoryUsage();

        // Get active handles count safely
        let handleCount = 0;
        try {
            // @ts-ignore - _getActiveHandles is an internal Node.js API
            handleCount = process._getActiveHandles?.()?.length ?? 0;
        } catch {
            // Fallback if internal API is not available
            handleCount = 0;
        }

        // Process metrics
        const metrics: ProcessMetrics = {
            cpu: {
                usage: totalUsage,
                user: userUsage,
                system: systemUsage
            },
            memory: {
                rss: memoryUsage.rss,
                heapTotal: memoryUsage.heapTotal,
                heapUsed: memoryUsage.heapUsed,
                external: memoryUsage.external
            },
            handles: handleCount,
            uptime: process.uptime()
        };

        logger.debug('Process metrics collected:', metrics);
        return metrics;
    } catch (error) {
        logger.error('Error collecting process metrics:', error);
        throw error;
    }
}

export async function formatProcessMetrics(metrics: ProcessMetrics): Promise<Array<{name: string; value: number; labels?: Record<string, string>}>> {
    return [
        // CPU metrics
        {
            name: 'process_cpu_usage',
            value: metrics.cpu.usage,
            labels: { unit: 'percent' }
        },
        {
            name: 'process_cpu_user',
            value: metrics.cpu.user,
            labels: { unit: 'percent' }
        },
        {
            name: 'process_cpu_system',
            value: metrics.cpu.system,
            labels: { unit: 'percent' }
        },

        // Memory metrics
        {
            name: 'process_memory_rss',
            value: metrics.memory.rss,
            labels: { unit: 'bytes' }
        },
        {
            name: 'process_memory_heap_total',
            value: metrics.memory.heapTotal,
            labels: { unit: 'bytes' }
        },
        {
            name: 'process_memory_heap_used',
            value: metrics.memory.heapUsed,
            labels: { unit: 'bytes' }
        },
        {
            name: 'process_memory_external',
            value: metrics.memory.external,
            labels: { unit: 'bytes' }
        },

        // Other process metrics
        {
            name: 'process_handles',
            value: metrics.handles
        },
        {
            name: 'process_uptime',
            value: metrics.uptime,
            labels: { unit: 'seconds' }
        }
    ];
}

// Helper function to calculate memory usage percentages
export function calculateMemoryPercentages(metrics: ProcessMetrics): Record<string, number> {
    const total = metrics.memory.heapTotal;
    return {
        heapUsedPercent: (metrics.memory.heapUsed / total) * 100,
        externalPercent: (metrics.memory.external / total) * 100,
        rssPercent: (metrics.memory.rss / total) * 100
    };
}

// Helper function to check if memory usage is within acceptable limits
export function checkMemoryThresholds(metrics: ProcessMetrics): Record<string, boolean> {
    const percentages = calculateMemoryPercentages(metrics);
    return {
        heapUsed: percentages.heapUsedPercent < 90, // Warning if heap usage > 90%
        rss: percentages.rssPercent < 95, // Warning if RSS > 95%
        external: percentages.externalPercent < 50 // Warning if external > 50%
    };
}

// Helper function to get memory usage summary
export function getMemorySummary(metrics: ProcessMetrics): string {
    const percentages = calculateMemoryPercentages(metrics);
    const thresholds = checkMemoryThresholds(metrics);
    
    return Object.entries(thresholds)
        .map(([key, ok]) => {
            const percent = percentages[`${key}Percent`];
            const status = ok ? 'OK' : 'WARNING';
            return `${key}: ${percent.toFixed(2)}% (${status})`;
        })
        .join(', ');
}