---
created: 2025-03-28
tags: reference, mcp, implementation, code
parent: [[Reference MOC]]
---

# MCP Technical Implementation

## Overview

This reference provides detailed technical information about implementing Model Context Protocol (MCP) servers in both TypeScript and Python. It includes code examples, implementation patterns, and architectural guidelines to help developers create robust MCP servers that integrate with Cursor and other MCP clients.

## Key Points

- Covers both TypeScript and Python implementation approaches
- Provides core implementation patterns for tools, resources, and prompts
- Includes complete code examples for basic server setup
- Explains key architectural concepts and best practices
- References official SDKs and their usage patterns

## Details

### Core MCP Primitives

The MCP protocol defines three core primitives that servers can implement:

| Primitive     | Control                | Description                                       | Example Use                  |
| ------------- | ---------------------- | ------------------------------------------------- | ---------------------------- |
| **Tools**     | Model-controlled       | Functions exposed to the LLM to take actions      | API calls, data updates      |
| **Resources** | Application-controlled | Contextual data managed by the client application | File contents, API responses |
| **Prompts**   | User-controlled        | Interactive templates invoked by user choice      | Slash commands, menu options |

### TypeScript Implementation

#### Basic Server Structure

A typical TypeScript MCP server has the following project structure:

```
mcp-server/
├── package.json
├── tsconfig.json
└── src/
    └── index.ts
```

#### Setup and Configuration

**package.json**:

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

**tsconfig.json**:

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

#### Basic Server Implementation

**src/index.ts**:

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

#### Building and Running the TypeScript Server

```bash
# Build the server
npm run build

# Run the server
node build/index.js
```

### Python Implementation

Python MCP servers can be implemented using either the official SDK or the FastMCP library, which provides a more Pythonic interface.

#### Project Structure

```
mcp-server/
├── pyproject.toml
└── src/
    └── mcp_server/
        ├── __init__.py
        └── __main__.py
```

#### Using the FastMCP Library

**pyproject.toml**:

```toml
[project]
name = "mcp-server"
version = "0.1.0"
description = "A Model Context Protocol server example"
requires-python = ">=3.10"
dependencies = [
    "fastmcp>=0.4.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

**src/mcp_server/**main**.py**:

```python
from fastmcp import FastMCP

# Create a new server
mcp = FastMCP("Sample MCP Server")

# Add a resource handler
@mcp.resource("sample://text/{text_id}")
def sample_text(text_id: str) -> str:
    """Provides sample text content"""
    return f"This is sample text with ID: {text_id}"

# Add a tool
@mcp.tool()
def echo(message: str) -> str:
    """Echoes a message back to the user"""
    return f"Echo: {message}"

# Add a prompt
@mcp.prompt()
def sample_prompt(topic: str) -> str:
    """A sample prompt template"""
    return f"Please create content about: {topic}"

# Start the server
if __name__ == "__main__":
    mcp.run()
```

#### Using the Official Python SDK

**pyproject.toml**:

```toml
[project]
name = "mcp-server"
version = "0.1.0"
description = "A Model Context Protocol server example"
requires-python = ">=3.10"
dependencies = [
    "mcp>=0.3.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

**src/mcp_server/**main**.py**:

```python
from mcp import (
    Server,
    Tool,
    Function,
    ToolCollection,
    ResourceType,
    request_schema,
    response_schema,
)

# Create a server
server = Server()

# Define a tool collection
tools = ToolCollection(
    "sample_tools",
    "Sample tools for demonstration",
    tools=[
        Tool(
            "echo",
            "Echoes a message back to the user",
            functions=[
                Function(
                    request_schema={
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "The message to echo"}
                        },
                        "required": ["message"]
                    },
                    response_schema={
                        "type": "object",
                        "properties": {
                            "result": {"type": "string"}
                        }
                    }
                )
            ]
        )
    ]
)

# Define resource handler
def handle_sample_resource(uri):
    text_id = uri.split("/")[-1]
    return {
        "contents": [
            {
                "uri": uri,
                "mimeType": "text/plain",
                "text": f"This is sample text with ID: {text_id}"
            }
        ]
    }

# Define tool handler
async def handle_echo(request):
    message = request.get("message", "")
    return {"result": f"Echo: {message}"}

# Register handlers
server.register_tool_collection(tools)
server.register_handler("sample_tools.echo", handle_echo)
server.register_resource_handler("sample://text/", handle_sample_resource)

# Create server factory
def create_server():
    return server

# Start server if executed directly
if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import run_server

    asyncio.run(run_server(create_server()))
```

### Advanced Implementation Patterns

#### Stateful Servers

MCP servers can maintain state between calls, useful for session management:

**TypeScript Example**:

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

**Python Example**:

```python
from fastmcp import FastMCP

mcp = FastMCP("Stateful Server")

# In-memory state
notes = {}

@mcp.tool()
def save_note(title: str, content: str) -> str:
    """Save a note with a title"""
    notes[title] = content
    return f'Note "{title}" saved successfully.'

@mcp.tool()
def get_note(title: str) -> str:
    """Retrieve a note by title"""
    if title not in notes:
        return f'Note "{title}" not found.'
    return notes[title]

if __name__ == "__main__":
    mcp.run()
```

#### Working with External APIs

MCP servers can integrate with external services:

**TypeScript Example**:

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

**Python Example**:

```python
from fastmcp import FastMCP
import aiohttp
import asyncio

mcp = FastMCP("Weather API Server")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather information for a location"""
    try:
        # Note: This is a placeholder. Use a real weather API in production
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://weather-api.example.com/forecast?q={location}") as response:
                data = await response.json()
                return f"Weather for {location}: {data['temperature']}°C, {data['conditions']}"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

if __name__ == "__main__":
    mcp.run()
```

### Best Practices

1. **Error Handling**: Always implement robust error handling in tool and resource handlers
2. **Input Validation**: Validate all inputs before processing
3. **Resource Management**: Use appropriate MIME types for resources
4. **Documentation**: Provide clear descriptions for all tools, resources, and prompts
5. **Security**: Validate all inputs and implement proper authorization checks
6. **Performance**: Keep handlers lightweight and use async/await for I/O operations
7. **Testing**: Test servers with the MCP Inspector tool before deployment

## Related Notes

- [[MCP Architecture]] - Core architecture and protocol design
- [[MCP Central Hub]] - Managing multiple MCP servers
- [[MCP Server List]] - List of available MCP servers

## References

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Library](https://github.com/jlowin/fastmcp)
- [Hackteam MCP Tutorial](https://hackteam.io/blog/build-your-first-mcp-server-with-typescript-in-under-10-minutes/)

---

_This note belongs to the [[Reference MOC]]_
