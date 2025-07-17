import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { EventStore } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { RequestOptions } from "@modelcontextprotocol/sdk/shared/protocol.js";
import { Transport } from "@modelcontextprotocol/sdk/shared/transport.js";
import {
  CallToolRequestSchema,
  ClientCapabilities,
  CompleteRequestSchema,
  CreateMessageRequestSchema,
  ErrorCode,
  GetPromptRequestSchema,
  GetPromptResult,
  ListPromptsRequestSchema,
  ListResourcesRequestSchema,
  ListResourcesResult,
  ListResourceTemplatesRequestSchema,
  ListResourceTemplatesResult,
  ListToolsRequestSchema,
  McpError,
  ReadResourceRequestSchema,
  ResourceLink,
  Root,
  RootsListChangedNotificationSchema,
  ServerCapabilities,
  SetLevelRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { StandardSchemaV1 } from "@standard-schema/spec";
import { EventEmitter } from "events";
import { readFile } from "fs/promises";
import Fuse from "fuse.js";
import http from "http";
import { startHTTPServer } from "mcp-proxy";
import { StrictEventEmitter } from "strict-event-emitter-types";
import { setTimeout as delay } from "timers/promises";
import { fetch } from "undici";
import parseURITemplate from "uri-templates";
import { toJsonSchema } from "xsschema";
import { z } from "zod";

export type SSEServer = {
  close: () => Promise<void>;
};

type FastMCPEvents<T extends FastMCPSessionAuth> = {
  connect: (event: { session: FastMCPSession<T> }) => void;
  disconnect: (event: { session: FastMCPSession<T> }) => void;
};

type FastMCPSessionEvents = {
  error: (event: { error: Error }) => void;
  ready: () => void;
  rootsChanged: (event: { roots: Root[] }) => void;
};

export const imageContent = async (
  input: { buffer: Buffer } | { path: string } | { url: string },
): Promise<ImageContent> => {
  let rawData: Buffer;

  try {
    if ("url" in input) {
      try {
        const response = await fetch(input.url);

        if (!response.ok) {
          throw new Error(
            `Server responded with status: ${response.status} - ${response.statusText}`,
          );
        }

        rawData = Buffer.from(await response.arrayBuffer());
      } catch (error) {
        throw new Error(
          `Failed to fetch image from URL (${input.url}): ${
            error instanceof Error ? error.message : String(error)
          }`,
        );
      }
    } else if ("path" in input) {
      try {
        rawData = await readFile(input.path);
      } catch (error) {
        throw new Error(
          `Failed to read image from path (${input.path}): ${
            error instanceof Error ? error.message : String(error)
          }`,
        );
      }
    } else if ("buffer" in input) {
      rawData = input.buffer;
    } else {
      throw new Error(
        "Invalid input: Provide a valid 'url', 'path', or 'buffer'",
      );
    }

    const { fileTypeFromBuffer } = await import("file-type");
    const mimeType = await fileTypeFromBuffer(rawData);

    if (!mimeType || !mimeType.mime.startsWith("image/")) {
      console.warn(
        `Warning: Content may not be a valid image. Detected MIME: ${
          mimeType?.mime || "unknown"
        }`,
      );
    }

    const base64Data = rawData.toString("base64");

    return {
      data: base64Data,
      mimeType: mimeType?.mime ?? "image/png",
      type: "image",
    } as const;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    } else {
      throw new Error(`Unexpected error processing image: ${String(error)}`);
    }
  }
};

export const audioContent = async (
  input: { buffer: Buffer } | { path: string } | { url: string },
): Promise<AudioContent> => {
  let rawData: Buffer;

  try {
    if ("url" in input) {
      try {
        const response = await fetch(input.url);

        if (!response.ok) {
          throw new Error(
            `Server responded with status: ${response.status} - ${response.statusText}`,
          );
        }

        rawData = Buffer.from(await response.arrayBuffer());
      } catch (error) {
        throw new Error(
          `Failed to fetch audio from URL (${input.url}): ${
            error instanceof Error ? error.message : String(error)
          }`,
        );
      }
    } else if ("path" in input) {
      try {
        rawData = await readFile(input.path);
      } catch (error) {
        throw new Error(
          `Failed to read audio from path (${input.path}): ${
            error instanceof Error ? error.message : String(error)
          }`,
        );
      }
    } else if ("buffer" in input) {
      rawData = input.buffer;
    } else {
      throw new Error(
        "Invalid input: Provide a valid 'url', 'path', or 'buffer'",
      );
    }

    const { fileTypeFromBuffer } = await import("file-type");
    const mimeType = await fileTypeFromBuffer(rawData);

    if (!mimeType || !mimeType.mime.startsWith("audio/")) {
      console.warn(
        `Warning: Content may not be a valid audio file. Detected MIME: ${
          mimeType?.mime || "unknown"
        }`,
      );
    }

    const base64Data = rawData.toString("base64");

    return {
      data: base64Data,
      mimeType: mimeType?.mime ?? "audio/mpeg",
      type: "audio",
    } as const;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    } else {
      throw new Error(`Unexpected error processing audio: ${String(error)}`);
    }
  }
};

type Context<T extends FastMCPSessionAuth> = {
  log: {
    debug: (message: string, data?: SerializableValue) => void;
    error: (message: string, data?: SerializableValue) => void;
    info: (message: string, data?: SerializableValue) => void;
    warn: (message: string, data?: SerializableValue) => void;
  };
  reportProgress: (progress: Progress) => Promise<void>;
  session: T | undefined;
  streamContent: (content: Content | Content[]) => Promise<void>;
};

type Extra = unknown;

type Extras = Record<string, Extra>;

type Literal = boolean | null | number | string | undefined;

type Progress = {
  /**
   * The progress thus far. This should increase every time progress is made, even if the total is unknown.
   */
  progress: number;
  /**
   * Total number of items to process (or total progress required), if known.
   */
  total?: number;
};

type SerializableValue =
  | { [key: string]: SerializableValue }
  | Literal
  | SerializableValue[];

type TextContent = {
  text: string;
  type: "text";
};

type ToolParameters = StandardSchemaV1;

abstract class FastMCPError extends Error {
  public constructor(message?: string) {
    super(message);
    this.name = new.target.name;
  }
}

export class UnexpectedStateError extends FastMCPError {
  public extras?: Extras;

  public constructor(message: string, extras?: Extras) {
    super(message);
    this.name = new.target.name;
    this.extras = extras;
  }
}

/**
 * An error that is meant to be surfaced to the user.
 */
export class UserError extends UnexpectedStateError {}

const TextContentZodSchema = z
  .object({
    /**
     * The text content of the message.
     */
    text: z.string(),
    type: z.literal("text"),
  })
  .strict() satisfies z.ZodType<TextContent>;

type ImageContent = {
  data: string;
  mimeType: string;
  type: "image";
};

const ImageContentZodSchema = z
  .object({
    /**
     * The base64-encoded image data.
     */
    data: z.string().base64(),
    /**
     * The MIME type of the image. Different providers may support different image types.
     */
    mimeType: z.string(),
    type: z.literal("image"),
  })
  .strict() satisfies z.ZodType<ImageContent>;

type AudioContent = {
  data: string;
  mimeType: string;
  type: "audio";
};

const AudioContentZodSchema = z
  .object({
    /**
     * The base64-encoded audio data.
     */
    data: z.string().base64(),
    mimeType: z.string(),
    type: z.literal("audio"),
  })
  .strict() satisfies z.ZodType<AudioContent>;

type ResourceContent = {
  resource: {
    blob?: string;
    mimeType?: string;
    text?: string;
    uri: string;
  };
  type: "resource";
};

const ResourceContentZodSchema = z
  .object({
    resource: z.object({
      blob: z.string().optional(),
      mimeType: z.string().optional(),
      text: z.string().optional(),
      uri: z.string(),
    }),
    type: z.literal("resource"),
  })
  .strict() satisfies z.ZodType<ResourceContent>;

const ResourceLinkZodSchema = z.object({
  description: z.string().optional(),
  mimeType: z.string().optional(),
  name: z.string(),
  title: z.string().optional(),
  type: z.literal("resource_link"),
  uri: z.string(),
}) satisfies z.ZodType<ResourceLink>;

type Content =
  | AudioContent
  | ImageContent
  | ResourceContent
  | ResourceLink
  | TextContent;

const ContentZodSchema = z.discriminatedUnion("type", [
  TextContentZodSchema,
  ImageContentZodSchema,
  AudioContentZodSchema,
  ResourceContentZodSchema,
  ResourceLinkZodSchema,
]) satisfies z.ZodType<Content>;

type ContentResult = {
  content: Content[];
  isError?: boolean;
};

const ContentResultZodSchema = z
  .object({
    content: ContentZodSchema.array(),
    isError: z.boolean().optional(),
  })
  .strict() satisfies z.ZodType<ContentResult>;

type Completion = {
  hasMore?: boolean;
  total?: number;
  values: string[];
};

/**
 * https://YOUR-CREDENTIALS@YOUR-DOMAIN/
    enabled?: boolean;

    /**
     * Plain-text body returned by the endpoint.
     * @default "ok"
     */
    message?: string;

    /**
     * HTTP path that should be handled.
     * @default "/health"
     */
    path?: string;

    /**
     * HTTP response status that will be returned.
     * @default 200
     */
    status?: number;
  };
  instructions?: string;
  name: string;

  /**
   * Configuration for OAuth well-known discovery endpoints that can be exposed
   * when the server is running using HTTP-based transports (SSE or HTTP Stream).
   * When enabled, the server will respond to requests for OAuth discovery endpoints
   * with the configured metadata.
   *
   * The endpoints are only added when the server is started with
   * `transportType: "httpStream"` – they are ignored for the stdio transport.
   * Both SSE and HTTP Stream transports support OAuth endpoints.
   */
  oauth?: {
    /**
     * OAuth Authorization Server metadata for /.well-known/oauth-authorization-server
     *
     * This endpoint follows RFC 8414 (OAuth 2.0 Authorization Server Metadata)
     * and provides metadata about the OAuth 2.0 authorization server.
     *
     * Required by MCP Specification 2025-03-26
     */
    authorizationServer?: {
      authorizationEndpoint: string;
      codeChallengeMethodsSupported?: string[];
      // DPoP support
      dpopSigningAlgValuesSupported?: string[];
      grantTypesSupported?: string[];

      introspectionEndpoint?: string;
      // Required
      issuer: string;
      // Common optional
      jwksUri?: string;
      opPolicyUri?: string;
      opTosUri?: string;
      registrationEndpoint?: string;
      responseModesSupported?: string[];
      responseTypesSupported: string[];
      revocationEndpoint?: string;
      scopesSupported?: string[];
      serviceDocumentation?: string;
      tokenEndpoint: string;
      tokenEndpointAuthMethodsSupported?: string[];
      tokenEndpointAuthSigningAlgValuesSupported?: string[];

      uiLocalesSupported?: string[];
    };

    /**
     * Whether OAuth discovery endpoints should be enabled.
     */
    enabled: boolean;

    /**
     * OAuth Protected Resource metadata for /.well-known/oauth-protected-resource
     *
     * This endpoint follows RFC 9470 (OAuth 2.0 Protected Resource Metadata)
     * and provides metadata about the OAuth 2.0 protected resource.
     *
     * Required by MCP Specification 2025-06-18
     */
    protectedResource?: {
      authorizationServers: string[];
      bearerMethodsSupported?: string[];
      jwksUri?: string;
      resource: string;
      resourceDocumentation?: string;
      resourcePolicyUri?: string;
    };
  };

  ping?: {
    /**
     * Whether ping should be enabled by default.
     * - true for SSE or HTTP Stream
     * - false for stdio
     */
    enabled?: boolean;
    /**
     * Interval
     * @default 5000 (5s)
     */
    intervalMs?: number;
    /**
     * Logging level for ping-related messages.
     * @default 'debug'
     */
    logLevel?: LoggingLevel;
  };
  /**
   * Configuration for roots capability
   */
  roots?: {
    /**
     * Whether roots capability should be enabled
     * Set to false to completely disable roots support
     * @default true
     */
    enabled?: boolean;
  };
  version: `${number}.${number}.${number}`;
};

type Tool<
  T extends FastMCPSessionAuth,
  Params extends ToolParameters = ToolParameters,
> = {
  annotations?: {
    /**
     * When true, the tool leverages incremental content streaming
     * Return void for tools that handle all their output via streaming
     */
    streamingHint?: boolean;
  } & ToolAnnotations;
  description?: string;
  execute: (
    args: StandardSchemaV1.InferOutput<Params>,
    context: Context<T>,
  ) => Promise<
    | AudioContent
    | ContentResult
    | ImageContent
    | ResourceContent
    | ResourceLink
    | string
    | TextContent
    | void
  >;
  name: string;
  parameters?: Params;
  timeoutMs?: number;
};

/**
 * Tool annotations as defined in MCP Specification (2025-03-26)
 * These provide hints about a tool's behavior.
 */
type ToolAnnotations = {
  /**
   * If true, the tool may perform destructive updates
   * Only meaningful when readOnlyHint is false
   * @default true
   */
  destructiveHint?: boolean;

  /**
   * If true, calling the tool repeatedly with the same arguments has no additional effect
   * Only meaningful when readOnlyHint is false
   * @default false
   */
  idempotentHint?: boolean;

  /**
   * If true, the tool may interact with an "open world" of external entities
   * @default true
   */
  openWorldHint?: boolean;

  /**
   * If true, indicates the tool does not modify its environment
   * @default false
   */
  readOnlyHint?: boolean;

  /**
   * A human-readable title for the tool, useful for UI display
   */
  title?: string;
};

const FastMCPSessionEventEmitterBase: {
  new (): StrictEventEmitter<EventEmitter, FastMCPSessionEvents>;
} = EventEmitter;

type Authenticate<T> = (request: http.IncomingMessage) => Promise<T>;

type FastMCPSessionAuth = Record<string, unknown> | undefined;

class FastMCPSessionEventEmitter extends FastMCPSessionEventEmitterBase {}

export class FastMCPSession<
  T extends FastMCPSessionAuth = FastMCPSessionAuth,
> extends FastMCPSessionEventEmitter {
  public get clientCapabilities(): ClientCapabilities | null {
    return this.#clientCapabilities ?? null;
  }
  public get isReady(): boolean {
    return this.#connectionState === "ready";
  }
  public get loggingLevel(): LoggingLevel {
    return this.#loggingLevel;
  }
  public get roots(): Root[] {
    return this.#roots;
  }
  public get server(): Server {
    return this.#server;
  }
  #auth: T | undefined;
  #capabilities: ServerCapabilities = {};
  #clientCapabilities?: ClientCapabilities;
  #connectionState: "closed" | "connecting" | "error" | "ready" = "connecting";
  #loggingLevel: LoggingLevel = "info";
  #needsEventLoopFlush: boolean = false;
  #pingConfig?: ServerOptions<T>["ping"];

  #pingInterval: null | ReturnType<typeof setInterval> = null;

  #prompts: Prompt<T>[] = [];

  #resources: Resource<T>[] = [];

  #resourceTemplates: ResourceTemplate<T>[] = [];

  #roots: Root[] = [];

  #rootsConfig?: ServerOptions<T>["roots"];

  #server: Server;

  constructor({
    auth,
    instructions,
    name,
    ping,
    prompts,
    resources,
    resourcesTemplates,
    roots,
    tools,
    transportType,
    version,
  }: {
    auth?: T;
    instructions?: string;
    name: string;
    ping?: ServerOptions<T>["ping"];
    prompts: Prompt<T>[];
    resources: Resource<T>[];
    resourcesTemplates: InputResourceTemplate<T>[];
    roots?: ServerOptions<T>["roots"];
    tools: Tool<T>[];
    transportType?: "httpStream" | "stdio";
    version: string;
  }) {
    super();

    this.#auth = auth;
    this.#pingConfig = ping;
    this.#rootsConfig = roots;
    this.#needsEventLoopFlush = transportType === "httpStream";

    if (tools.length) {
      this.#capabilities.tools = {};
    }

    if (resources.length || resourcesTemplates.length) {
      this.#capabilities.resources = {};
    }

    if (prompts.length) {
      for (const prompt of prompts) {
        this.addPrompt(prompt);
      }

      this.#capabilities.prompts = {};
    }

    this.#capabilities.logging = {};

    this.#server = new Server(
      { name: name, version: version },
      { capabilities: this.#capabilities, instructions: instructions },
    );

    this.setupErrorHandling();
    this.setupLoggingHandlers();
    this.setupRootsHandlers();
    this.setupCompleteHandlers();

    if (tools.length) {
      this.setupToolHandlers(tools);
    }

    if (resources.length || resourcesTemplates.length) {
      for (const resource of resources) {
        this.addResource(resource);
      }

      this.setupResourceHandlers(resources);

      if (resourcesTemplates.length) {
        for (const resourceTemplate of resourcesTemplates) {
          this.addResourceTemplate(resourceTemplate);
        }

        this.setupResourceTemplateHandlers(resourcesTemplates);
      }
    }

    if (prompts.length) {
      this.setupPromptHandlers(prompts);
    }
  }

  public async close() {
    this.#connectionState = "closed";

    if (this.#pingInterval) {
      clearInterval(this.#pingInterval);
    }

    try {
      await this.#server.close();
    } catch (error) {
      console.error("[FastMCP error]", "could not close server", error);
    }
  }

  public async connect(transport: Transport) {
    if (this.#server.transport) {
      throw new UnexpectedStateError("Server is already connected");
    }

    this.#connectionState = "connecting";

    try {
      await this.#server.connect(transport);

      let attempt = 0;
      const maxAttempts = 10;
      const retryDelay = 100;

      while (attempt++ < maxAttempts) {
        const capabilities = this.#server.getClientCapabilities();

        if (capabilities) {
          this.#clientCapabilities = capabilities;
          break;
        }

        await delay(retryDelay);
      }

      if (!this.#clientCapabilities) {
        console.warn(
          `[FastMCP warning] could not infer client capabilities after ${maxAttempts} attempts. Connection may be unstable.`,
        );
      }

      if (
        this.#clientCapabilities?.roots?.listChanged &&
        typeof this.#server.listRoots === "function"
      ) {
        try {
          const roots = await this.#server.listRoots();
          this.#roots = roots?.roots || [];
        } catch (e) {
          if (e instanceof McpError && e.code === ErrorCode.MethodNotFound) {
            console.debug(
              "[FastMCP debug] listRoots method not supported by client",
            );
          } else {
            console.error(
              `[FastMCP error] received error listing roots.\n\n${
                e instanceof Error ? e.stack : JSON.stringify(e)
              }`,
            );
          }
        }
      }

      if (this.#clientCapabilities) {
        const pingConfig = this.#getPingConfig(transport);

        if (pingConfig.enabled) {
          this.#pingInterval = setInterval(async () => {
            try {
              await this.#server.ping();
            } catch {
              // The reason we are not emitting an error here is because some clients
              // seem to not respond to the ping request, and we don't want to crash the server,
              // e.g., https://YOUR-CREDENTIALS@YOUR-DOMAIN/
  public async embedded(uri: string): Promise<ResourceContent["resource"]> {
    // First, try to find a direct resource match
    const directResource = this.#resources.find(
      (resource) => resource.uri === uri,
    );

    if (directResource) {
      const result = await directResource.load();
      const results = Array.isArray(result) ? result : [result];
      const firstResult = results[0];

      const resourceData: ResourceContent["resource"] = {
        mimeType: directResource.mimeType,
        uri,
      };

      if ("text" in firstResult) {
        resourceData.text = firstResult.text;
      }

      if ("blob" in firstResult) {
        resourceData.blob = firstResult.blob;
      }

      return resourceData;
    }

    // Try to match against resource templates
    for (const template of this.#resourcesTemplates) {
      // Check if the URI starts with the template base
      const templateBase = template.uriTemplate.split("{")[0];

      if (uri.startsWith(templateBase)) {
        const params: Record<string, string> = {};
        const templateParts = template.uriTemplate.split("/");
        const uriParts = uri.split("/");

        for (let i = 0; i < templateParts.length; i++) {
          const templatePart = templateParts[i];

          if (templatePart?.startsWith("{") && templatePart.endsWith("}")) {
            const paramName = templatePart.slice(1, -1);
            const paramValue = uriParts[i];

            if (paramValue) {
              params[paramName] = paramValue;
            }
          }
        }

        const result = await template.load(
          params as ResourceTemplateArgumentsToObject<
            typeof template.arguments
          >,
        );

        const resourceData: ResourceContent["resource"] = {
          mimeType: template.mimeType,
          uri,
        };

        if ("text" in result) {
          resourceData.text = result.text;
        }

        if ("blob" in result) {
          resourceData.blob = result.blob;
        }

        return resourceData; // The resource we're looking for
      }
    }

    throw new UnexpectedStateError(`Resource not found: ${uri}`, { uri });
  }

  /**
   * Starts the server.
   */
  public async start(
    options?: Partial<{
      httpStream: {
        endpoint?: `/${string}`;
        eventStore?: EventStore;
        port: number;
      };
      transportType: "httpStream" | "stdio";
    }>,
  ) {
    const config = this.#parseRuntimeConfig(options);

    if (config.transportType === "stdio") {
      const transport = new StdioServerTransport();
      const session = new FastMCPSession<T>({
        instructions: this.#options.instructions,
        name: this.#options.name,
        ping: this.#options.ping,
        prompts: this.#prompts,
        resources: this.#resources,
        resourcesTemplates: this.#resourcesTemplates,
        roots: this.#options.roots,
        tools: this.#tools,
        transportType: "stdio",
        version: this.#options.version,
      });

      await session.connect(transport);

      this.#sessions.push(session);

      this.emit("connect", {
        session: session as FastMCPSession<FastMCPSessionAuth>,
      });
    } else if (config.transportType === "httpStream") {
      const httpConfig = config.httpStream;

      this.#httpStreamServer = await startHTTPServer<FastMCPSession<T>>({
        createServer: async (request) => {
          let auth: T | undefined;

          if (this.#authenticate) {
            auth = await this.#authenticate(request);
          }

          return new FastMCPSession<T>({
            auth,
            name: this.#options.name,
            ping: this.#options.ping,
            prompts: this.#prompts,
            resources: this.#resources,
            resourcesTemplates: this.#resourcesTemplates,
            roots: this.#options.roots,
            tools: this.#tools,
            transportType: "httpStream",
            version: this.#options.version,
          });
        },
        eventStore: httpConfig.eventStore,
        onClose: async (session) => {
          this.emit("disconnect", {
            session: session as FastMCPSession<FastMCPSessionAuth>,
          });
        },
        onConnect: async (session) => {
          this.#sessions.push(session);

          console.info(`[FastMCP info] HTTP Stream session established`);

          this.emit("connect", {
            session: session as FastMCPSession<FastMCPSessionAuth>,
          });
        },

        onUnhandledRequest: async (req, res) => {
          const healthConfig = this.#options.health ?? {};

          const enabled =
            healthConfig.enabled === undefined ? true : healthConfig.enabled;

          if (enabled) {
            const path = healthConfig.path ?? "/health";
            const url = new URL(req.url || "", "http://localhost");

            try {
              if (req.method === "GET" && url.pathname === path) {
                res
                  .writeHead(healthConfig.status ?? 200, {
                    "Content-Type": "text/plain",
                  })
                  .end(healthConfig.message ?? "✓ Ok");

                return;
              }

              // Enhanced readiness check endpoint
              if (req.method === "GET" && url.pathname === "/ready") {
                const readySessions = this.#sessions.filter(
                  (s) => s.isReady,
                ).length;
                const totalSessions = this.#sessions.length;
                const allReady =
                  readySessions === totalSessions && totalSessions > 0;

                const response = {
                  ready: readySessions,
                  status: allReady
                    ? "ready"
                    : totalSessions === 0
                      ? "no_sessions"
                      : "initializing",
                  total: totalSessions,
                };

                res
                  .writeHead(allReady ? 200 : 503, {
                    "Content-Type": "application/json",
                  })
                  .end(JSON.stringify(response));

                return;
              }
            } catch (error) {
              console.error("[FastMCP error] health endpoint error", error);
            }
          }

          // Handle OAuth well-known endpoints
          const oauthConfig = this.#options.oauth;
          if (oauthConfig?.enabled && req.method === "GET") {
            const url = new URL(req.url || "", "http://localhost");

            if (
              url.pathname === "/.well-known/oauth-authorization-server" &&
              oauthConfig.authorizationServer
            ) {
              const metadata = convertObjectToSnakeCase(
                oauthConfig.authorizationServer,
              );
              res
                .writeHead(200, {
                  "Content-Type": "application/json",
                })
                .end(JSON.stringify(metadata));
              return;
            }

            if (
              url.pathname === "/.well-known/oauth-protected-resource" &&
              oauthConfig.protectedResource
            ) {
              const metadata = convertObjectToSnakeCase(
                oauthConfig.protectedResource,
              );
              res
                .writeHead(200, {
                  "Content-Type": "application/json",
                })
                .end(JSON.stringify(metadata));
              return;
            }
          }

          // If the request was not handled above, return 404
          res.writeHead(404).end();
        },
        port: httpConfig.port,
        streamEndpoint: httpConfig.endpoint,
      });

      console.info(
        `[FastMCP info] server is running on HTTP Stream at http://localhost:${httpConfig.port}${httpConfig.endpoint}`,
      );
      console.info(
        `[FastMCP info] Transport type: httpStream (Streamable HTTP, not SSE)`,
      );
    } else {
      throw new Error("Invalid transport type");
    }
  }

  /**
   * Stops the server.
   */
  public async stop() {
    if (this.#httpStreamServer) {
      await this.#httpStreamServer.close();
    }
  }

  #parseRuntimeConfig(
    overrides?: Partial<{
      httpStream: { endpoint?: `/${string}`; port: number };
      transportType: "httpStream" | "stdio";
    }>,
  ):
    | {
        httpStream: {
          endpoint: `/${string}`;
          eventStore?: EventStore;
          port: number;
        };
        transportType: "httpStream";
      }
    | { transportType: "stdio" } {
    const args = process.argv.slice(2);
    const getArg = (name: string) => {
      const index = args.findIndex((arg) => arg === `--${name}`);

      return index !== -1 && index + 1 < args.length
        ? args[index + 1]
        : undefined;
    };

    const transportArg = getArg("transport");
    const portArg = getArg("port");
    const endpointArg = getArg("endpoint");

    const envTransport = process.env.FASTMCP_TRANSPORT;
    const envPort = process.env.FASTMCP_PORT;
    const envEndpoint = process.env.FASTMCP_ENDPOINT;

    // Overrides > CLI > env > defaults
    const transportType =
      overrides?.transportType ||
      (transportArg === "http-stream" ? "httpStream" : transportArg) ||
      envTransport ||
      "stdio";

    if (transportType === "httpStream") {
      const port = parseInt(
        overrides?.httpStream?.port?.toString() || portArg || envPort || "8080",
      );
      const endpoint =
        overrides?.httpStream?.endpoint || endpointArg || envEndpoint || "/mcp";

      return {
        httpStream: { endpoint: endpoint as `/${string}`, port },
        transportType: "httpStream" as const,
      };
    }

    return { transportType: "stdio" as const };
  }
}

export type {
  AudioContent,
  Content,
  ContentResult,
  Context,
  FastMCPEvents,
  FastMCPSessionEvents,
  ImageContent,
  InputPrompt,
  InputPromptArgument,
  LoggingLevel,
  Progress,
  Prompt,
  PromptArgument,
  Resource,
  ResourceContent,
  ResourceLink,
  ResourceResult,
  ResourceTemplate,
  ResourceTemplateArgument,
  SerializableValue,
  ServerOptions,
  TextContent,
  Tool,
  ToolParameters,
};
