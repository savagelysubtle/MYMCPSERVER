import { McpServer } from '@modelcontextprotocol/sdk/server/mcp';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio';
import { z } from 'zod';
import { thinkingTool } from './n3';
import { anotherTool } from './n4';
import { logger } from './logger';
import { healthCheck } from './health';

// Create MCP server
const server = new McpServer({
  name: 'TypeScript Tool Server',
  version: '1.0.0',
});

// Register tools
server.tool('thinking', thinkingTool.schema, thinkingTool.handler);

server.tool('another', anotherTool.schema, anotherTool.handler);

// Add health check
server.health(healthCheck);

// Start server
async function main() {
  try {
    logger.info('Starting TypeScript Tool Server');

    // Connect to transport
    const transport = new StdioServerTransport();
    await server.connect(transport);

    logger.info('Server started successfully');
  } catch (error) {
    logger.error('Failed to start server', { error });
    process.exit(1);
  }
}

main();
