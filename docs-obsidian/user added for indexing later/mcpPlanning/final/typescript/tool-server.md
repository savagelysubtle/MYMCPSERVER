# TypeScript Tool Server Implementation

## Overview

The TypeScript Tool Server provides a modern, type-safe implementation of the Model Context Protocol (MCP). It leverages the MCP TypeScript SDK to expose tools and resources to LLM applications in a standardized way.

## Core Components

### 1. Server Configuration

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';

interface ServerConfig {
  name: string;
  version: string;
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
}

// Create server instance
const server = new McpServer({
  name: 'TypeScript Tool Server',
  version: '1.0.0',
  logLevel: 'info',
});
```

### 2. Tool Registration

```typescript
import { Tool, ToolContext } from '@modelcontextprotocol/sdk/types';

// Define tool parameters schema
const calculatorSchema = z.object({
  operation: z.enum(['add', 'subtract', 'multiply', 'divide']),
  a: z.number(),
  b: z.number(),
});

// Register tool with type safety
server.tool(
  'calculator',
  calculatorSchema,
  async (context: ToolContext, params) => {
    const { operation, a, b } = params;
    let result: number;

    switch (operation) {
      case 'add':
        result = a + b;
        break;
      case 'subtract':
        result = a - b;
        break;
      case 'multiply':
        result = a * b;
        break;
      case 'divide':
        if (b === 0) throw new Error('Division by zero');
        result = a / b;
        break;
    }

    return {
      content: [{ type: 'text', text: String(result) }],
    };
  },
);
```

### 3. Resource Implementation

```typescript
import { ResourceTemplate } from '@modelcontextprotocol/sdk/server/mcp.js';

// Define dynamic resource
const greetingResource = new ResourceTemplate('greeting://{name}', {
  list: undefined,
});

server.resource('greeting', greetingResource, async (uri, { name }) => ({
  contents: [
    {
      uri: uri.href,
      text: `Hello, ${name}!`,
    },
  ],
}));
```

## Transport Layer Integration

### 1. stdio Transport

```typescript
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

async function setupStdioTransport() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.log('Server connected via stdio transport');
}
```

### 2. SSE Transport

```typescript
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';

async function setupSSETransport() {
  const transport = new SSEServerTransport({
    port: 8080,
    host: '127.0.0.1',
    path: '/sse',
  });

  await server.connect(transport);
  console.log('Server connected via SSE transport');
}
```

### 3. WebSocket Transport

```typescript
import { WebSocketServerTransport } from '@modelcontextprotocol/sdk/server/ws.js';

async function setupWebSocketTransport() {
  const transport = new WebSocketServerTransport({
    port: 8081,
    host: '127.0.0.1',
  });

  await server.connect(transport);
  console.log('Server connected via WebSocket transport');
}
```

## Error Handling

### 1. Custom Error Types

```typescript
import { MCPError } from '@modelcontextprotocol/sdk/errors';

class ValidationError extends MCPError {
  constructor(message: string) {
    super('VALIDATION_ERROR', message);
  }
}

class ResourceNotFoundError extends MCPError {
  constructor(resourceId: string) {
    super('RESOURCE_NOT_FOUND', `Resource ${resourceId} not found`);
  }
}
```

### 2. Error Handling in Tools

```typescript
server.tool(
  'safe_operation',
  z.object({ input: z.string() }),
  async (context, params) => {
    try {
      const result = await performOperation(params.input);
      return {
        content: [{ type: 'text', text: result }],
      };
    } catch (error) {
      if (error instanceof ValidationError) {
        return {
          error: {
            code: 'VALIDATION_ERROR',
            message: error.message,
          },
        };
      }
      throw error; // Let MCP handle unexpected errors
    }
  },
);
```

## Middleware Integration

### 1. Authentication Middleware

```typescript
import { Middleware } from '@modelcontextprotocol/sdk/middleware';

const authMiddleware: Middleware = async (context, next) => {
  const token = context.request.headers.get('authorization');

  if (!token || !validateToken(token)) {
    throw new MCPError('UNAUTHORIZED', 'Invalid or missing token');
  }

  return next(context);
};

server.use(authMiddleware);
```

### 2. Logging Middleware

```typescript
const loggingMiddleware: Middleware = async (context, next) => {
  const startTime = Date.now();

  try {
    const result = await next(context);
    console.log(`Request processed in ${Date.now() - startTime}ms`);
    return result;
  } catch (error) {
    console.error('Request failed:', error);
    throw error;
  }
};

server.use(loggingMiddleware);
```

## Testing

### 1. Unit Tests

```typescript
import { TestContext } from '@modelcontextprotocol/sdk/testing';
import { expect } from 'chai';

describe('Calculator Tool', () => {
  it('should perform addition', async () => {
    const context = new TestContext();
    const result = await server.executeTool(
      'calculator',
      {
        operation: 'add',
        a: 5,
        b: 3,
      },
      context,
    );

    expect(result.content[0].text).to.equal('8');
  });
});
```

### 2. Integration Tests

```typescript
import { TestClient } from '@modelcontextprotocol/sdk/testing';

describe('Server Integration', () => {
  let client: TestClient;

  before(async () => {
    client = await TestClient.connect(server);
  });

  it('should handle resource requests', async () => {
    const response = await client.getResource('greeting://Alice');
    expect(response.contents[0].text).to.equal('Hello, Alice!');
  });
});
```

## Deployment

### 1. Environment Configuration

```typescript
import { config } from 'dotenv';
import { z } from 'zod';

const envSchema = z.object({
  PORT: z.string().transform(Number),
  HOST: z.string(),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']),
  AUTH_TOKEN: z.string(),
});

const env = envSchema.parse(process.env);
```

### 2. Docker Configuration

```dockerfile
FROM node:18-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

ENV NODE_ENV=production
ENV PORT=8080
ENV HOST=0.0.0.0

CMD ["npm", "start"]
```

## Monitoring

### 1. Health Checks

```typescript
import { HealthCheck } from '@modelcontextprotocol/sdk/monitoring';

class ServerHealth implements HealthCheck {
  async check(): Promise<boolean> {
    try {
      await Promise.all([
        this.checkDatabase(),
        this.checkRedis(),
        this.checkFileSystem(),
      ]);
      return true;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }
}

server.registerHealthCheck(new ServerHealth());
```

### 2. Metrics Collection

```typescript
import { MetricsCollector } from '@modelcontextprotocol/sdk/monitoring';

const metrics = new MetricsCollector();

server.tool(
  'monitored_operation',
  z.object({ input: z.string() }),
  async (context, params) => {
    const timer = metrics.startTimer('operation_duration');
    try {
      const result = await performOperation(params.input);
      metrics.increment('operation_success');
      return {
        content: [{ type: 'text', text: result }],
      };
    } finally {
      timer.end();
    }
  },
);
```

## Future Enhancements

1. **Advanced Tool Features:**

   - Tool composition and chaining
   - Versioned tools and resources
   - Tool dependencies management

2. **Performance Optimization:**

   - Response caching
   - Connection pooling
   - Request batching

3. **Security Enhancements:**

   - OAuth2 integration
   - Rate limiting
   - Request validation

4. **Developer Experience:**
   - OpenAPI integration
   - Interactive documentation
   - Development tools and CLI
