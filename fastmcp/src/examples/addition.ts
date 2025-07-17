/**
 * Example FastMCP server demonstrating core functionality plus streaming output.
 *
 * Features demonstrated:
 * - Basic tool with type-safe parameters
 * - Streaming-enabled tool for incremental output
 * - Advanced tool annotations
 *
 * For a complete project template, see https://YOUR-CREDENTIALS@YOUR-DOMAIN/sdk/client/index.js";
  import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
  
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
    new URL("http://localhost:${PORT}/mcp"),
  );
  
  await client.connect(transport);
  `);
} else if (process.argv.includes("--explicit-ping-config")) {
  server.start({
    transportType: "stdio",
  });

  console.log(
    "Started stdio transport with explicit ping configuration from server options",
  );
} else if (process.argv.includes("--disable-roots")) {
  // Example of disabling roots at runtime
  const serverWithDisabledRoots = new FastMCP({
    name: "Addition (No Roots)",
    ping: {
      intervalMs: 10000,
      logLevel: "debug",
    },
    roots: {
      enabled: false,
    },
    version: "1.0.0",
  });

  serverWithDisabledRoots.start({
    transportType: "stdio",
  });

  console.log("Started stdio transport with roots support disabled");
} else {
  // Disable by default for:
  server.start({
    transportType: "stdio",
  });

  console.log("Started stdio transport with ping disabled by default");
}
