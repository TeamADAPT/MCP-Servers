import { z } from "zod";

export const RequestPayloadSchema = z.object({
  url: z.string().url(),
  headers: z.record(z.string()).optional(),
});

export const RecursiveRequestPayloadSchema = z.object({
  url: z.string().url(),
  maxDepth: z.number().min(1).max(5).default(1),
  headers: z.record(z.string()).optional(),
  includeAssets: z.boolean().default(false),
  followPattern: z.string().optional(),
});

export type RequestPayload = z.infer<typeof RequestPayloadSchema>;
export type RecursiveRequestPayload = z.infer<typeof RecursiveRequestPayloadSchema>;
