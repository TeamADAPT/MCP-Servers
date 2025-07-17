// Metric Types
export type MetricType = 'counter' | 'gauge' | 'histogram';

export interface BaseMetric {
    name: string;
    help: string;
    type: MetricType;
    labels?: Record<string, string>;
    timestamp: string;
}

export interface CounterMetric extends BaseMetric {
    type: 'counter';
    value: number;
}

export interface GaugeMetric extends BaseMetric {
    type: 'gauge';
    value: number;
}

export interface HistogramMetric extends BaseMetric {
    type: 'histogram';
    buckets: Record<string, number>;
    sum: number;
    count: number;
}

export type Metric = CounterMetric | GaugeMetric | HistogramMetric;

// Service Types
export interface ServiceMetrics {
    service: string;
    metrics: Metric[];
    timestamp: string;
}

export interface MetricQuery {
    service?: string;
    type?: MetricType;
    name?: string;
    labels?: Record<string, string>;
    start?: string;
    end?: string;
    limit?: number;
}

// Tool Types
export interface CollectMetricsArgs {
    service: string;
    metrics: Metric[];
}

export interface QueryMetricsArgs {
    query: MetricQuery;
}

export interface CreateMetricArgs {
    name: string;
    help: string;
    type: MetricType;
    labels?: Record<string, string>;
}

export interface UpdateMetricArgs {
    name: string;
    value: number;
    labels?: Record<string, string>;
}

// Response Types
export interface MetricResponse {
    metrics: Metric[];
    timestamp: string;
}

export interface ServiceResponse {
    services: string[];
    timestamp: string;
}

// Error Types
export interface MetricError {
    code: string;
    message: string;
    details?: unknown;
}

// Configuration Types
export interface MetricConfig {
    name: string;
    help: string;
    type: MetricType;
    labels?: string[];
    buckets?: number[];  // For histograms
}

export interface ServiceConfig {
    name: string;
    metrics: MetricConfig[];
}

// Redis Types
export interface RedisMetricData {
    service: string;
    name: string;
    type: MetricType;
    value: string;  // JSON stringified metric data
    timestamp: string;
}

// Prometheus Types
export interface PrometheusMetric {
    name: string;
    help: string;
    type: string;
    values: Array<{
        labels: Record<string, string>;
        value: number;
    }>;
}

// System Metric Types
export interface SystemMetrics {
    cpu: {
        usage: number;
        load: number[];
    };
    memory: {
        total: number;
        used: number;
        free: number;
    };
    disk: {
        total: number;
        used: number;
        free: number;
    };
    network: {
        rx_bytes: number;
        tx_bytes: number;
        connections: number;
    };
}

// Process Metric Types
export interface ProcessMetrics {
    cpu: {
        usage: number;
        system: number;
        user: number;
    };
    memory: {
        rss: number;
        heapTotal: number;
        heapUsed: number;
        external: number;
    };
    handles: number;
    uptime: number;
}

// Application Metric Types
export interface ApplicationMetrics {
    requests: {
        total: number;
        active: number;
        error: number;
    };
    response: {
        time: number;
        errors: number;
    };
    connections: {
        active: number;
        idle: number;
        closed: number;
    };
}