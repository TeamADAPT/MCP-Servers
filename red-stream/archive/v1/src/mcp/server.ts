import { Server, ServerConfig, ToolRequest, ToolResponse, StdioServerTransport, McpServer } from './types';
import { logger } from '../utils/logger.js';

export class BaseMcpServer implements McpServer {
  private transport?: StdioServerTransport;
  private handlers: Map<string, (request: any) => Promise<any>>;
  public onerror?: (error: Error) => void;

  constructor(
    private serverInfo: Server,
    private config: ServerConfig
  ) {
    this.handlers = new Map();
  }

  protected setToolHandler(name: string, handler: (request: any) => Promise<any>) {
    if (!this.config.capabilities.tools[name]) {
      throw new Error(`Tool ${name} not defined in server configuration`);
    }
    this.handlers.set(name, handler);
  }

  protected formatResponse(data: any): ToolResponse {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify(data, null, 2)
      }]
    };
  }

  private async handleRequest(message: string) {
    try {
      const request: ToolRequest = JSON.parse(message);
      logger.debug('Received request:', request);

      const handler = this.handlers.get(request.method);
      if (!handler) {
        throw new Error(`Unknown method: ${request.method}`);
      }

      const result = await handler(request);
      const response = {
        id: request.id,
        result
      };

      logger.debug('Sending response:', response);
      return JSON.stringify(response);
    } catch (error: any) {
      logger.error('Error handling request:', error);
      return JSON.stringify({
        id: JSON.parse(message).id,
        error: {
          message: error.message
        }
      });
    }
  }

  public async connect(transport: StdioServerTransport): Promise<void> {
    this.transport = transport;

    transport.onMessage(async (message) => {
      try {
        const response = await this.handleRequest(message);
        transport.send(response);
      } catch (error: any) {
        logger.error('Error processing message:', error);
        if (this.onerror) {
          this.onerror(error);
        }
      }
    });

    logger.info(`MCP server ${this.serverInfo.name} v${this.serverInfo.version} connected`);
  }

  public async close(): Promise<void> {
    if (this.transport) {
      await this.transport.close();
      this.transport = undefined;
      logger.info(`MCP server ${this.serverInfo.name} closed`);
    }
  }
}