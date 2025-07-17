declare module '@modelcontextprotocol/sdk/server/index.js' {
    export interface ServerConfig {
        name: string;
        version: string;
    }

    export interface ServerCapabilities {
        capabilities: {
            tools?: {
                [key: string]: {
                    description: string;
                    inputSchema: any;
                };
            };
        };
    }

    export interface McpRequest {
        method: string;
        params: {
            name: string;
            arguments: any;
        };
    }

    export interface McpResponse {
        error?: {
            code: number;
            message: string;
        };
        result?: {
            content: Array<{
                type: string;
                text: string;
            }>;
            isError?: boolean;
        };
    }

    export class Server {
        constructor(config: ServerConfig, capabilities: ServerCapabilities);
        connect(transport: any): Promise<void>;
        setRequestHandler(method: string, handler: (request: McpRequest) => Promise<McpResponse>): void;
        handleRequest(request: McpRequest): Promise<McpResponse>;
    }
}

declare module '@modelcontextprotocol/sdk/server/stdio.js' {
    export class StdioServerTransport {
        constructor();
    }
}