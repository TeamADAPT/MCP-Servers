import os from 'os';
import { SystemMetrics } from '../types.js';
import { logger } from '../utils/logger.js';

export async function collectSystemMetrics(): Promise<SystemMetrics> {
    logger.debug('Collecting system metrics');
    
    try {
        // CPU metrics
        const cpus = os.cpus();
        const loadAvg = os.loadavg();
        const totalCpuTime = cpus.reduce((acc, cpu) => {
            return acc + Object.values(cpu.times).reduce((sum, time) => sum + time, 0);
        }, 0);
        const cpuUsage = process.cpuUsage();
        const cpuUsagePercent = (cpuUsage.user + cpuUsage.system) / (totalCpuTime * 1000) * 100;

        // Memory metrics
        const totalMemory = os.totalmem();
        const freeMemory = os.freemem();
        const usedMemory = totalMemory - freeMemory;

        // Disk metrics
        // Note: This is a simplified version. In production, you'd want to use a library
        // like `node-disk-info` to get detailed disk information
        const diskInfo = {
            total: 0,
            used: 0,
            free: 0
        };

        try {
            // Placeholder for actual disk info collection
            // In production, implement proper disk metrics collection
            logger.debug('Disk metrics collection not implemented');
        } catch (error) {
            logger.error('Error collecting disk metrics:', error);
        }

        // Network metrics
        // Note: This is a simplified version. In production, you'd want to use
        // platform-specific commands or libraries to get detailed network stats
        const networkConnections = os.networkInterfaces();
        const networkMetrics = {
            rx_bytes: 0,
            tx_bytes: 0,
            connections: Object.values(networkConnections).reduce((acc, interfaces) => {
                return acc + (interfaces?.length || 0);
            }, 0)
        };

        const metrics: SystemMetrics = {
            cpu: {
                usage: cpuUsagePercent,
                load: loadAvg
            },
            memory: {
                total: totalMemory,
                used: usedMemory,
                free: freeMemory
            },
            disk: {
                total: diskInfo.total,
                used: diskInfo.used,
                free: diskInfo.free
            },
            network: networkMetrics
        };

        logger.debug('System metrics collected:', metrics);
        return metrics;
    } catch (error) {
        logger.error('Error collecting system metrics:', error);
        throw error;
    }
}

export async function formatSystemMetrics(metrics: SystemMetrics): Promise<Array<{name: string; value: number; labels?: Record<string, string>}>> {
    return [
        // CPU metrics
        {
            name: 'system_cpu_usage',
            value: metrics.cpu.usage,
            labels: { unit: 'percent' }
        },
        {
            name: 'system_cpu_load_1m',
            value: metrics.cpu.load[0]
        },
        {
            name: 'system_cpu_load_5m',
            value: metrics.cpu.load[1]
        },
        {
            name: 'system_cpu_load_15m',
            value: metrics.cpu.load[2]
        },

        // Memory metrics
        {
            name: 'system_memory_total',
            value: metrics.memory.total,
            labels: { unit: 'bytes' }
        },
        {
            name: 'system_memory_used',
            value: metrics.memory.used,
            labels: { unit: 'bytes' }
        },
        {
            name: 'system_memory_free',
            value: metrics.memory.free,
            labels: { unit: 'bytes' }
        },

        // Disk metrics
        {
            name: 'system_disk_total',
            value: metrics.disk.total,
            labels: { unit: 'bytes' }
        },
        {
            name: 'system_disk_used',
            value: metrics.disk.used,
            labels: { unit: 'bytes' }
        },
        {
            name: 'system_disk_free',
            value: metrics.disk.free,
            labels: { unit: 'bytes' }
        },

        // Network metrics
        {
            name: 'system_network_rx_bytes',
            value: metrics.network.rx_bytes,
            labels: { unit: 'bytes' }
        },
        {
            name: 'system_network_tx_bytes',
            value: metrics.network.tx_bytes,
            labels: { unit: 'bytes' }
        },
        {
            name: 'system_network_connections',
            value: metrics.network.connections
        }
    ];
}