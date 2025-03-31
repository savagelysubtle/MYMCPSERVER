---
created: 2025-03-28
updated: 2025-03-30
tags: [mcp, architecture, protocol, core-concept]
parent: [[../MCP Knowledge MOC]]
---

# MCP Server Architecture

## Overview

The Model Context Protocol (MCP) server architecture defines how AI systems connect with external tools and services. This architecture enables AI models to access information and perform actions beyond their trained capabilities through a standardized interface.

## Key Components

### Protocol Format

- **JSON Schema**: Defines tools, resources, and actions
- **Transport Layer**: Commonly SSE (Server-Sent Events) or stdio for local implementations
- **Message Types**: Requests, responses, events, and metadata

### Server Structure

- **Resource Endpoints**: Access points for data sources
- **Tool Definitions**: Callable functions with parameters and return types
- **Authentication**: Methods for securing access to resources and tools
- **Error Handling**: Standardized format for reporting and handling errors

## Implementation Patterns

### Local MCP Server

- **stdio Communication**: Direct pipe communication with the client process
- **Process Management**: Managed by the client application (e.g., Cursor)
- **Access Control**: Limited to local machine resources

### Remote MCP Server

- **HTTP/SSE Communication**: Network-based communication
- **Authentication Flow**: OAuth or custom authentication
- **Multi-tenant Support**: Available to multiple clients simultaneously

## Implementation Examples

For specific implementation examples, see:

- [[../../projects/myMcpServer/mcpPlanning/final/core/overview-v2|Core Implementation]]
- [[../../projects/myMcpServer/mcpPlanning/final/transport/overview-v2|Transport Layer]]

## Related Documentation

### Core Concepts

- [[MCP Central Hub]] - Central hub architecture
- [[Tool Management]] - Tool management system
- [[Remote Servers]] - Remote server architecture

### Implementation Guides

- [[../development/Implementation Guide|Implementation Guide]]
- [[../development/Hub Configuration|Configuration Guide]]
- [[../development/Hub Debugging|Debugging Guide]]

### SDK Documentation

- [[../pythonSDK/Python SDK Overview|Python SDK Guide]]
- [[../typeScriptSDK/TypeScript Server Development|TypeScript SDK Guide]]

### Integration

- [[../integration/Cursor Integration|Cursor Integration]]
- [[../../projects/myMcpServer/implementation/Server Configuration|Server Configuration]]

## External References

- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol)

---

[[../MCP Knowledge MOC|← Back to MCP Knowledge]]
