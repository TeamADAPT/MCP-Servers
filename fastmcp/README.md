# FastMCP

A TypeScript framework for building [MCP](https://YOUR-CREDENTIALS@YOUR-DOMAIN/sdk/client/streamableHttp.js";

const client = new Client(
  {
    name: "example-client",
    version: "1.0.0",
  },
  {
    capabilities: {},
  },
);

const transport = new StreamableHTTPClientTransport(
  new URL(`http://localhost:8080/mcp`),
);

await client.connect(transport);
```

For SSE connections:

```ts
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";

const client = new Client(
  {
    name: "example-client",
    version: "1.0.0",
  },
  {
    capabilities: {},
  },
);

const transport = new SSEClientTransport(new URL(`http://localhost:8080/sse`));

await client.connect(transport);
```

## Core Concepts

### Tools

[Tools](https://YOUR-CREDENTIALS@YOUR-DOMAIN/to-json-schema.

```typescript
import * as v from "valibot";

server.addTool({
  name: "fetch-valibot",
  description: "Fetch the content of a url (using Valibot)",
  parameters: v.object({
    url: v.string(),
  }),
  execute: async (args) => {
    return await fetchWebpageContent(args.url);
  },
});
```

#### Tools Without Parameters

When creating tools that don't require parameters, you have two options:

1. Omit the parameters property entirely:

   ```typescript
   server.addTool({
     name: "sayHello",
     description: "Say hello",
     // No parameters property
     execute: async () => {
       return "Hello, world!";
     },
   });
   ```

2. Explicitly define empty parameters:

   ```typescript
   import { z } from "zod";

   server.addTool({
     name: "sayHello",
     description: "Say hello",
     parameters: z.object({}), // Empty object
     execute: async () => {
       return "Hello, world!";
     },
   });
   ```

> [!NOTE]
>
> Both approaches are fully compatible with all MCP clients, including Cursor. FastMCP automatically generates the proper schema in both cases.

#### Returning a string

`execute` can return a string:

```js
server.addTool({
  name: "download",
  description: "Download a file",
  parameters: z.object({
    url: z.string(),
  }),
  execute: async (args) => {
    return "Hello, world!";
  },
});
```

The latter is equivalent to:

```js
server.addTool({
  name: "download",
  description: "Download a file",
  parameters: z.object({
    url: z.string(),
  }),
  execute: async (args) => {
    return {
      content: [
        {
          type: "text",
          text: "Hello, world!",
        },
      ],
    };
  },
});
```

#### Returning a list

If you want to return a list of messages, you can return an object with a `content` property:

```js
server.addTool({
  name: "download",
  description: "Download a file",
  parameters: z.object({
    url: z.string(),
  }),
  execute: async (args) => {
    return {
      content: [
        { type: "text", text: "First message" },
        { type: "text", text: "Second message" },
      ],
    };
  },
});
```

#### Returning an image

Use the `imageContent` to create a content object for an image:

```js
import { imageContent } from "fastmcp";

server.addTool({
  name: "download",
  description: "Download a file",
  parameters: z.object({
    url: z.string(),
  }),
  execute: async (args) => {
    return imageContent({
      url: "https://YOUR-CREDENTIALS@YOUR-DOMAIN/jwt`](https://YOUR-CREDENTIALS@YOUR-DOMAIN/sdk/client/streamableHttp.js";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";

const transport = new StreamableHTTPClientTransport(
  new URL(`http://localhost:8080/mcp`),
  {
    requestInit: {
      headers: {
        Authorization: "Test 123",
      },
    },
  },
);

const client = new Client({
  name: "example-client",
  version: "1.0.0",
});

(async () => {
  await client.connect(transport);

  // Call a tool
  const result = await client.callTool({
    name: "headerTool",
    arguments: {
      arg1: "value",
    },
  });

  console.log("Tool result:", result);
})().catch(console.error);
```

What would show up in the console after the client runs is something like this:

```
Tool result: {
  content: [
    {
      type: 'text',
      text: 'User-Agent: node\n' +
        'Authorization: Test 123\n' +
        'All Headers: {\n' +
        '  "host": "localhost:8080",\n' +
        '  "connection": "keep-alive",\n' +
        '  "authorization": "Test 123",\n' +
        '  "content-type": "application/json",\n' +
        '  "accept": "application/json, text/event-stream",\n' +
        '  "accept-language": "*",\n' +
        '  "sec-fetch-mode": "cors",\n' +
        '  "user-agent": "node",\n' +
        '  "accept-encoding": "gzip, deflate",\n' +
        '  "content-length": "163"\n' +
        '}'
    }
  ]
}
```

### Providing Instructions

You can provide instructions to the server using the `instructions` option:

```ts
const server = new FastMCP({
  name: "My Server",
  version: "1.0.0",
  instructions:
    'Instructions describing how to use the server and its features.\n\nThis can be used by clients to improve the LLM\'s understanding of available tools, resources, etc. It can be thought of like a "hint" to the model. For example, this information MAY be added to the system prompt.',
});
```

### Sessions

The `session` object is an instance of `FastMCPSession` and it describes active client sessions.

```ts
server.sessions;
```

We allocate a new server instance for each client connection to enable 1:1 communication between a client and the server.

### Typed server events

You can listen to events emitted by the server using the `on` method:

```ts
server.on("connect", (event) => {
  console.log("Client connected:", event.session);
});

server.on("disconnect", (event) => {
  console.log("Client disconnected:", event.session);
});
```

## `FastMCPSession`

`FastMCPSession` represents a client session and provides methods to interact with the client.

Refer to [Sessions](#sessions) for examples of how to obtain a `FastMCPSession` instance.

### `requestSampling`

`requestSampling` creates a [sampling](https://modelcontextprotocol.io/docs/concepts/sampling) request and returns the response.

```ts
await session.requestSampling({
  messages: [
    {
      role: "user",
      content: {
        type: "text",
        text: "What files are in the current directory?",
      },
    },
  ],
  systemPrompt: "You are a helpful file system assistant.",
  includeContext: "thisServer",
  maxTokens: 100,
});
```

#### Options

`requestSampling` accepts an optional second parameter for request options:

```ts
await session.requestSampling(
  {
    messages: [
      {
        role: "user",
        content: {
          type: "text",
          text: "What files are in the current directory?",
        },
      },
    ],
    systemPrompt: "You are a helpful file system assistant.",
    includeContext: "thisServer",
    maxTokens: 100,
  },
  {
    // Progress callback - called when progress notifications are received
    onprogress: (progress) => {
      console.log(`Progress: ${progress.progress}/${progress.total}`);
    },

    // Abort signal for cancelling the request
    signal: abortController.signal,

    // Request timeout in milliseconds (default: DEFAULT_REQUEST_TIMEOUT_MSEC)
    timeout: 30000,

    // Whether progress notifications reset the timeout (default: false)
    resetTimeoutOnProgress: true,

    // Maximum total timeout regardless of progress (no default)
    maxTotalTimeout: 60000,
  },
);
```

**Options:**

- `onprogress?: (progress: Progress) => void` - Callback for progress notifications from the remote end
- `signal?: AbortSignal` - Abort signal to cancel the request
- `timeout?: number` - Request timeout in milliseconds
- `resetTimeoutOnProgress?: boolean` - Whether progress notifications reset the timeout
- `maxTotalTimeout?: number` - Maximum total timeout regardless of progress notifications

### `clientCapabilities`

The `clientCapabilities` property contains the client capabilities.

```ts
session.clientCapabilities;
```

### `loggingLevel`

The `loggingLevel` property describes the logging level as set by the client.

```ts
session.loggingLevel;
```

### `roots`

The `roots` property contains the roots as set by the client.

```ts
session.roots;
```

### `server`

The `server` property contains an instance of MCP server that is associated with the session.

```ts
session.server;
```

### Typed session events

You can listen to events emitted by the session using the `on` method:

```ts
session.on("rootsChanged", (event) => {
  console.log("Roots changed:", event.roots);
});

session.on("error", (event) => {
  console.error("Error:", event.error);
});
```

## Running Your Server

### Test with `mcp-cli`

The fastest way to test and debug your server is with `fastmcp dev`:

```bash
npx fastmcp dev server.js
npx fastmcp dev server.ts
```

This will run your server with [`mcp-cli`](https://github.com/wong2/mcp-cli) for testing and debugging your MCP server in the terminal.

### Inspect with `MCP Inspector`

Another way is to use the official [`MCP Inspector`](https://modelcontextprotocol.io/docs/tools/inspector) to inspect your server with a Web UI:

```bash
npx fastmcp inspect server.ts
```

## FAQ

### How to use with Claude Desktop?

Follow the guide https://modelcontextprotocol.io/quickstart/user and add the following configuration:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "npx",
      "args": ["tsx", "/PATH/TO/YOUR_PROJECT/src/index.ts"],
      "env": {
        "YOUR_ENV_VAR": "value"
      }
    }
  }
}
```

### How to run FastMCP behind a proxy?

Refer to this [issue](https://github.com/punkpeye/fastmcp/issues/25#issuecomment-3004568732) for an example of using FastMCP with `express` and `http-proxy-middleware`.

## Showcase

> [!NOTE]
>
> If you've developed a server using FastMCP, please [submit a PR](https://github.com/punkpeye/fastmcp) to showcase it here!

> [!NOTE]
>
> If you are looking for a boilerplate repository to build your own MCP server, check out [fastmcp-boilerplate](https://github.com/punkpeye/fastmcp-boilerplate).

- [apinetwork/piapi-mcp-server](https://github.com/apinetwork/piapi-mcp-server) - generate media using Midjourney/Flux/Kling/LumaLabs/Udio/Chrip/Trellis
- [domdomegg/computer-use-mcp](https://github.com/domdomegg/computer-use-mcp) - controls your computer
- [LiterallyBlah/Dradis-MCP](https://github.com/LiterallyBlah/Dradis-MCP) – manages projects and vulnerabilities in Dradis
- [Meeting-Baas/meeting-mcp](https://github.com/Meeting-Baas/meeting-mcp) - create meeting bots, search transcripts, and manage recording data
- [drumnation/unsplash-smart-mcp-server](https://github.com/drumnation/unsplash-smart-mcp-server) – enables AI agents to seamlessly search, recommend, and deliver professional stock photos from Unsplash
- [ssmanji89/halopsa-workflows-mcp](https://github.com/ssmanji89/halopsa-workflows-mcp) - HaloPSA Workflows integration with AI assistants
- [aiamblichus/mcp-chat-adapter](https://github.com/aiamblichus/mcp-chat-adapter) – provides a clean interface for LLMs to use chat completion
- [eyaltoledano/claude-task-master](https://github.com/eyaltoledano/claude-task-master) – advanced AI project/task manager powered by FastMCP
- [cswkim/discogs-mcp-server](https://github.com/cswkim/discogs-mcp-server) - connects to the Discogs API for interacting with your music collection
- [Panzer-Jack/feuse-mcp](https://github.com/Panzer-Jack/feuse-mcp) - Frontend Useful MCP Tools - Essential utilities for web developers to automate API integration and code generation

## Acknowledgements

- FastMCP is inspired by the [Python implementation](https://github.com/jlowin/fastmcp) by [Jonathan Lowin](https://github.com/jlowin).
- Parts of codebase were adopted from [LiteMCP](https://github.com/wong2/litemcp).
- Parts of codebase were adopted from [Model Context protocolでSSEをやってみる](https://dev.classmethod.jp/articles/mcp-sse/).
