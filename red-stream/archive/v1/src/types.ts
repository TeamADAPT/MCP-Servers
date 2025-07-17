import { RedisClientType } from 'redis';

export interface StreamInfo {
  name: string;
  length: number;
  groups: number;
  last_id: string;
  first_id: string;
}

export interface StreamListResponse {
  streams: StreamInfo[];
}

export interface GroupInfo {
  name: string;
  consumers: number;
  pending: number;
  last_delivered_id: string;
  lag: number;
}

export interface GroupListResponse {
  stream: string;
  groups: GroupInfo[];
}

export interface ListStreamsArgs {
  pattern?: string;
}

export interface ListGroupsArgs {
  stream: string;
}

export interface RedisMessage {
  [key: string]: string | number | boolean;
}

export type RedisClient = RedisClientType<any, any, any>;