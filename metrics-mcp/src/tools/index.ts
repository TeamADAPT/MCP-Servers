import { collectSystemMetrics, formatSystemMetrics } from './collect-system-metrics.js';
import { collectProcessMetrics, formatProcessMetrics } from './collect-process-metrics.js';
import type { MetricType, Metric, MetricQuery, CollectMetricsArgs, QueryMetricsArgs } from '../types.js';
import { logger } from '../utils/logger.js';

// Tool registry
export const TOOLS = {
    collect_metrics: {
        name: 'collect_metrics',
        description: 'Collect metrics from a service',
        inputSchema: {
            type: 'object',
            properties: {
                service: {
                    type: 'string',
                    description: 'Service name to collect metrics from'
                },
                metrics: {
                    type: 'array',
                    description: 'Array of metrics to collect',
                    items: {
                        type: 'object',
                        properties: {
                            name: { type: 'string' },
                            type: { type: 'string', enum: ['counter', 'gauge', 'histogram'] },
                            value: { type: 'number' },
                            labels: { type: 'object', additionalProperties: { type: 'string' } }
                        },
                        required: ['name', 'type', 'value']
                    }
                }
            },
            required: ['service']
        }
    },
    query_metrics: {
        name: 'query_metrics',
        description: 'Query collected metrics',
        inputSchema: {
            type: 'object',
            properties: {
                query: {
                    type: 'object',
                    properties: {
                        service: { type: 'string' },
                        type: { type: 'string', enum: ['counter', 'gauge', 'histogram'] },
                        name: { type: 'string' },
                        labels: { type: 'object', additionalProperties: { type: 'string' } },
                        start: { type: 'string' },
                        end: { type: 'string' },
                        limit: { type: 'number' }
                    }
                }
            },
            required: ['query']
        }
    },
    get_system_metrics: {
        name: 'get_system_metrics',
        description: 'Get system-level metrics',
        inputSchema: {
            type: 'object',
            properties: {}
        }
    },
    get_process_metrics: {
        name: 'get_process_metrics',
        description: 'Get Node.js process metrics',
        inputSchema: {
            type: 'object',
            properties: {}
        }
    }
};

// Tool implementations
export async function executeTool(name: string, args: unknown): Promise<{ content: Array<{ type: string; text: string }> }> {
    logger.debug(`Executing tool: ${name}`, { args });

    try {
        switch (name) {
            case 'collect_metrics': {
                const { service, metrics } = args as CollectMetricsArgs;
                // Store metrics in Redis with timestamp
                const timestamp = new Date().toISOString();
                const result = {
                    service,
                    metrics,
                    timestamp
                };
                return {
                    content: [{
                        type: 'text',
                        text: JSON.stringify(result, null, 2)
                    }]
                };
            }

            case 'query_metrics': {
                const { query } = args as QueryMetricsArgs;
                // Query metrics from Redis based on criteria
                const results = await queryMetrics(query);
                return {
                    content: [{
                        type: 'text',
                        text: JSON.stringify(results, null, 2)
                    }]
                };
            }

            case 'get_system_metrics': {
                const metrics = await collectSystemMetrics();
                const formatted = await formatSystemMetrics(metrics);
                return {
                    content: [{
                        type: 'text',
                        text: JSON.stringify(formatted, null, 2)
                    }]
                };
            }

            case 'get_process_metrics': {
                const metrics = await collectProcessMetrics();
                const formatted = await formatProcessMetrics(metrics);
                return {
                    content: [{
                        type: 'text',
                        text: JSON.stringify(formatted, null, 2)
                    }]
                };
            }

            default:
                throw new Error(`Unknown tool: ${name}`);
        }
    } catch (error) {
        logger.error('Tool execution failed:', error);
        throw error;
    }
}

// Helper function to query metrics
async function queryMetrics(query: MetricQuery): Promise<Metric[]> {
    // TODO: Implement Redis-based metric querying
    logger.debug('Querying metrics:', { query });
    return [];
}

// Helper function to validate metric type
function isValidMetricType(type: string): type is MetricType {
    return ['counter', 'gauge', 'histogram'].includes(type);
}

// Helper function to validate metric value
function isValidMetricValue(value: unknown): value is number {
    return typeof value === 'number' && !isNaN(value);
}

// Helper function to validate metric labels
function isValidLabels(labels: unknown): labels is Record<string, string> {
    if (typeof labels !== 'object' || labels === null) return false;
    return Object.entries(labels).every(([key, value]) => 
        typeof key === 'string' && typeof value === 'string'
    );
}