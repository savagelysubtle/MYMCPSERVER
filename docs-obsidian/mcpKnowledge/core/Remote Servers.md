---
created: 2025-03-28
updated: 2025-03-30
tags: [mcp, remote, architecture, core-concept]
parent: [[../MCP Knowledge MOC]]
---

# MCP Remote Servers

## Overview

MCP Remote Servers extend the Model Context Protocol beyond local machine environments, enabling AI assistants to access tools and resources over the internet. Unlike traditional local MCP servers that communicate via stdio, remote servers use HTTP/SSE (Server-Sent Events) or Streamable HTTP protocols to provide secure, authenticated access to tools from any network-connected device.

## Key Points

- Extends MCP beyond local machine limitations
- Uses HTTP/SSE or Streamable HTTP for remote communication
- Supports OAuth and other authentication methods
- Enables broader access to AI tools for web and mobile users
- Maintains state across sessions using techniques like Durable Objects
- Acts as a bridge between AI assistants and cloud-based services

## Details

### Evolution from Local to Remote

Traditional MCP servers run locally on the same machine as the client application, communicating through standard input/output (stdio). This approach works well for desktop applications but has significant limitations:

1. **Limited to Desktop**: Only users of desktop applications can access MCP tools
2. **No Authentication**: Local servers have no standardized authentication mechanism
3. **Device Tethering**: Users can't continue tasks across different devices
4. **Installation Barriers**: Users must install and configure servers locally

Remote MCP servers solve these problems by making tools accessible over the internet, similar to the transition from desktop software to web applications.

### Transport Protocols

#### HTTP/SSE (Server-Sent Events)

The initial remote MCP specification uses HTTP with Server-Sent Events:

- Client connects to server with HTTP request
- Server maintains an open connection and sends events
- Enables real-time updates from server to client
- Requires separate endpoints for different operations

```javascript
// Example server implementation using SSE
server.addEventListener('open', function(event) {
  // Connection established
});

server.addEventListener('message', function(event) {
  const data = JSON.parse(event.data);
  // Process incoming message
});

// Send message to the server
fetch('https://mcp-server.example.com/message', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ type: 'tool.call', ... })
});
```

#### Streamable HTTP (Emerging Standard)

The MCP specification is evolving to use Streamable HTTP:

- Stateless, pure HTTP connections
- Optional upgrade to SSE for real-time communication
- Simpler implementation with single endpoint
- Better compatibility with various network environments

### Authentication & Authorization

Remote MCP servers implement standardized authentication flows:

- **OAuth 2.0**: Standard authorization framework for secure API access
- **User Consent**: Explicit user permission for accessing specific tools
- **Scoped Access**: Fine-grained control over which tools can be used
- **Token-based Authentication**: Secure, revocable access credentials

```javascript
// Example OAuth flow for MCP
// 1. Client redirects to authorization endpoint
window.location =
  'https://mcp-server.example.com/auth?client_id=abc&redirect_uri=...';

// 2. User approves access

// 3. Server redirects back with authorization code
// 4. Client exchanges code for access token
fetch('https://mcp-server.example.com/token', {
  method: 'POST',
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    code: authCode,
    client_id: 'abc',
    client_secret: 'xyz',
    redirect_uri: '...',
  }),
})
  .then((response) => response.json())
  .then((data) => {
    // Store access token
    const accessToken = data.access_token;
  });
```

### Stateful Implementations

Remote MCP servers can maintain state across sessions, enabling more complex applications:

- **Session Management**: Remembering user context and preferences
- **Persistent Storage**: Database integration for long-term data storage
- **Durable Objects**: Server-side state management techniques
- **User-specific Context**: Customized experiences based on user identity

Example stateful implementation (using Cloudflare Workers):

```javascript
import { McpAgent } from 'agents/mcp';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';

type State = { counter: number };

export class MyMCP extends McpAgent<Env, State, {}> {
  server = new McpServer({
    name: 'Demo',
    version: '1.0.0',
  });

  initialState: State = {
    counter: 1,
  };

  async init() {
    this.server.resource(`counter`, `mcp://resource/counter`, (uri) => {
      return {
        contents: [{ uri: uri.href, text: String(this.state.counter) }],
      };
    });

    this.server.tool(
      'add',
      'Add to the counter, stored in the MCP',
      { a: z.number() },
      async ({ a }) => {
        this.setState({ ...this.state, counter: this.state.counter + a });
        return {
          content: [
            {
              type: 'text',
              text: String(`Added ${a}, total is now ${this.state.counter}`),
            },
          ],
        };
      },
    );
  }
}
```

### Bridging to Local MCP Clients

Until all MCP clients support remote servers, adapter tools like `mcp-remote` can bridge the gap:

- Acts as a local proxy for remote servers
- Translates between local stdio and remote HTTP protocols
- Maintains compatibility with existing MCP clients
- Handles authentication flows transparently

Example configuration for Claude Desktop:

```javascript
{
  "mcpServers": {
    "remote-example": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://remote-server.example.com/sse"
      ]
    }
  }
}
```

## Related Documentation

### Core Concepts

- [[MCP Architecture]] - Core architecture of the Model Context Protocol
- [[MCP Central Hub]] - Centralizing management of multiple MCP servers
- [[../integration/Cursor MCP Integration|Cursor Integration]] - How Cursor IDE implements MCP support

### Implementation

- [[../development/MCP Hub Implementation|Hub Implementation Guide]]
- [[../../projects/myMcpServer/mcpPlanning/final/transport/overview-v2|Transport Layer Implementation]]

### SDK Documentation

- [[../pythonSDK/Python SDK Overview|Python SDK Guide]]
- [[../typeScriptSDK/TypeScript Server Development|TypeScript SDK Guide]]

## External References

- [Cloudflare Remote MCP Announcement](https://blog.cloudflare.com/remote-model-context-protocol-servers-mcp/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Anthropic MCP Announcement](https://www.anthropic.com/news/model-context-protocol)

---

[[../MCP Knowledge MOC|← Back to MCP Knowledge]]
