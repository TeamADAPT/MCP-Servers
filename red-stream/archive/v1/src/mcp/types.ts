export interface Server {
  name: string;
  version: string;
}

export interface ServerConfig {
  capabilities: {
    tools: Record<string, ToolDefinition>;
  };
}

export interface ToolDefinition {
  description: string;
  inputSchema: {
    type: string;
    properties: Record<string, any>;
    required?: string[];
  };
}

export interface ToolRequest<T = any> {
  id: string;
  method: string;
  params: T;
}

export interface ToolResponse {
  content: Array<{
    type: string;
    text: string;
  }>;
  isError?: boolean;
}

export interface StdioServerTransport {
  onMessage: (handler: (message: string) => void) => void;
  send: (message: string) => void;
  close: () => Promise<void>;
}

export interface McpServer {
  connect: (transport: StdioServerTransport) => Promise<void>;
  close: () => Promise<void>;
  onerror?: (error: Error) => void;
}