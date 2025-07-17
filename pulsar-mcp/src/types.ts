import { AxiosError } from 'axios';

export interface PulsarError extends Error {
    response?: {
        data?: any;
        status?: number;
    };
    config?: {
        url?: string;
        method?: string;
        headers?: Record<string, string>;
        data?: any;
    };
}

export interface ConsumerConfig {
    topic: string;
    subscription: string;
    subscriptionType: "Exclusive" | "Shared" | "Failover" | "Key_Shared";
    receiverQueueSize: number;
    acknowledgeTimeout: number;
    ackTimeoutRedeliveryBackoff: {
        minDelayMs: number;
        maxDelayMs: number;
        multiplier: number;
    };
}

export interface TopicMessage {
    messageId: string;
    publishTime: string;
    payload: string;
    properties?: Record<string, string>;
}

export interface TopicStats {
    msgRateIn: number;
    msgRateOut: number;
    msgThroughputIn: number;
    msgThroughputOut: number;
    averageMsgSize: number;
    storageSize: number;
    publishers: any[];
    subscriptions: Record<string, any>;
    replication: Record<string, any>;
    deduplicationStatus: string;
}
