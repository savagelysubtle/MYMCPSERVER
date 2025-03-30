---
created: 2025-03-30
tags: [mcp, typescript, sdk, examples]
parent: [[TypeScript Server Development]]
---

# TypeScript MCP Implementation Examples

## Project Structure

```
mcp-server/
├── package.json
├── tsconfig.json
└── src/
    └── index.ts
```

## Setup and Configuration

### package.json

```json
{
  "name": "mcp-server",
  "version": "0.1.0",
  "description": "A Model Context Protocol server example",
  "private": true,
  "type": "module",
  "bin": {
    "mcp-server": "./build/index.js"
  },
  "files": ["build"],
  "scripts": {
    "build": "tsc && node -e \"require('fs').chmodSync('build/index.js', '755')\"",
    "prepare": "npm run build",
    "watch": "tsc --watch",
    "inspector": "npx @modelcontextprotocol/inspector build/index.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "0.6.0"
  },
  "devDependencies": {
    "@types/node": "^20.11.24",
    "typescript": "^5.3.3"
  }
}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./build",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

## Basic Server Implementation

```typescript
#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server';
import {
  zodLiteral,
  zodObject,
  zodString,
} from '@modelcontextprotocol/sdk/schema';
import { z } from 'zod';

// Create a new server
const server = new Server({
  name: 'Sample MCP Server',
  version: '1.0.0',
});

// Add a simple tool
server.tool('echo', {
  description: 'Echoes a message back to the user',
  parameters: zodObject({
    message: zodString({
      description: 'The message to echo',
    }),
  }),
  handler: async ({ message }) => {
    return {
      content: [
        {
          type: 'text',
          text: `Echo: ${message}`,
        },
      ],
    };
  },
});

// Add a resource handler
server.resource(
  'sample://text/{id}',
  'Provides sample text content',
  async (uri) => {
    const id = uri.pathname.split('/').pop();
    return {
      contents: [
        {
          uri: uri.href,
          mimeType: 'text/plain',
          text: `This is sample text with ID: ${id}`,
        },
      ],
    };
  },
);

// Add a prompt
server.prompt('sample_prompt', {
  description: 'A sample prompt template',
  parameters: zodObject({
    topic: zodString({
      description: 'The topic to create content about',
    }),
  }),
  template: async ({ topic }) => {
    return {
      content: [
        {
          type: 'text',
          text: `Please create content about: ${topic}`,
        },
      ],
    };
  },
});

// Start the server
server.start();
```

## Advanced Examples

### Stateful Server

```typescript
import { Server } from '@modelcontextprotocol/sdk/server';
import { zodObject, zodString } from '@modelcontextprotocol/sdk/schema';

const server = new Server({
  name: 'Stateful Server',
  version: '1.0.0',
});

// In-memory state
const notes = new Map<string, string>();

// Tools to manage notes
server.tool('save_note', {
  description: 'Save a note with a title',
  parameters: zodObject({
    title: zodString({ description: 'The note title' }),
    content: zodString({ description: 'The note content' }),
  }),
  handler: async ({ title, content }) => {
    notes.set(title, content);
    return {
      content: [{ type: 'text', text: `Note "${title}" saved successfully.` }],
    };
  },
});

server.tool('get_note', {
  description: 'Retrieve a note by title',
  parameters: zodObject({
    title: zodString({ description: 'The note title' }),
  }),
  handler: async ({ title }) => {
    const content = notes.get(title);
    if (!content) {
      return {
        content: [{ type: 'text', text: `Note "${title}" not found.` }],
      };
    }

    return {
      content: [{ type: 'text', text: content }],
    };
  },
});

server.start();
```

### External API Integration

```typescript
import { Server } from '@modelcontextprotocol/sdk/server';
import { zodObject, zodString } from '@modelcontextprotocol/sdk/schema';
import fetch from 'node-fetch';

const server = new Server({
  name: 'Weather API Server',
  version: '1.0.0',
});

server.tool('get_weather', {
  description: 'Get weather information for a location',
  parameters: zodObject({
    location: zodString({ description: 'City name or location' }),
  }),
  handler: async ({ location }) => {
    try {
      // Note: This is a placeholder. Use a real weather API in production
      const response = await fetch(
        `https://weather-api.example.com/forecast?q=${encodeURIComponent(
          location,
        )}`,
      );
      const data = await response.json();

      return {
        content: [
          {
            type: 'text',
            text: `Weather for ${location}: ${data.temperature}°C, ${data.conditions}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error fetching weather: ${error.message}`,
          },
        ],
      };
    }
  },
});

server.start();
```

## Related Documentation

### Implementation Guides

- [[../development/Implementation Guide|General Implementation Guide]]
- [[TypeScript Server Development|Server Development Guide]]
- [[TypeScript Tool Implementation|Tool Implementation Guide]]

### Project Examples

- [[../../projects/myMcpServer/implementation/Server Configuration|Server Configuration]]
- [[../../projects/myMcpServer/mcpPlanning/final/typescript/tool-server|Tool Server Example]]

## External References

- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Hackteam MCP Tutorial](https://hackteam.io/blog/build-your-first-mcp-server-with-typescript-in-under-10-minutes/)

---

[[TypeScript Server Development|← Back to TypeScript Server Development]]
