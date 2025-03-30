---
created: 2025-03-28
tags: concept, mcp, architecture
parent: [[Concepts MOC]]
---

# MCP Architecture

## Overview

The Model Context Protocol (MCP) architecture defines how AI systems like Cursor communicate with external tools and services. It provides a standardized interface for AI models to access data sources, execute commands, and interact with specialized services, enhancing their capabilities beyond their training data.

## Key Points

- Standardizes communication between AI assistants and external tools/services
- Uses a client-server model where Cursor acts as the client
- Defines a structured format for tool definitions, requests, and responses
- Supports two primary transport protocols: stdio and HTTP/SSE
- Enables extensibility through modular tool implementation

## Details

### Core Components

1. **MCP Client**: The application that hosts the AI assistant (e.g., Cursor IDE, Claude Desktop)
2. **MCP Server**: Provides one or more tools that the AI assistant can utilize
3. **Tools**: Individual capabilities provided by servers (e.g., web search, file system access)
4. **Resource Types**: Standardized data formats for exchanging information

### Communication Protocols

MCP supports two primary communication methods:

#### Stdio Protocol

- Uses standard input/output for communication
- Typically used for local servers that run on the same machine
- Client spawns server process and communicates via JSON messages
- Simpler to implement but limited to local operation

#### HTTP/SSE Protocol

- Uses HTTP and Server-Sent Events for communication
- Supports remote servers accessible over a network
- More complex but enables distributed architectures
- Allows third-party service integration

### Message Flow

1. **Initialization**: Client discovers server capabilities
2. **Tool Selection**: AI assistant selects appropriate tool for a task
3. **Request**: Client sends a structured request to the server
4. **Execution**: Server processes the request and performs the action
5. **Response**: Server sends back results or status information

### Resource Types

MCP defines standard resource types for consistent data exchange:

- Plain text
- JSON/structured data
- Files/binary data
- Streaming data
- Error responses

## Related Notes

- [[MCP Central Hub]] - Managing multiple MCP servers
- [[Cursor MCP Integration]] - How Cursor implements MCP
- [[MCP Server Development]] - Creating custom MCP servers

## References

- [Official MCP Documentation](https://modelcontextprotocol.io/)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol)

---

_This note belongs to the [[Concepts MOC]]_
