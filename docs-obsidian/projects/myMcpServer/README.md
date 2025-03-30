---
created: 2025-03-30
tags: [mcp, project, implementation, documentation, mcp-hub]
parent: [[Project MOC]]
---

# MyMcpServer Project Documentation

## Overview

This directory contains implementation-specific documentation for the MyMcpServer project, a modular MCP (Machine Comprehension Platform) system that connects AI clients with specialized tool servers. While the [[../../mcpKnowledge/README|MCP Knowledge Base]] covers general MCP concepts, this documentation focuses on our specific implementation choices, architecture decisions, and technical details.

## Directory Structure

```
myMcpServer/
├── architecture/         # System architecture and design
│   ├── System Overview.md
│   ├── Component Design.md
│   ├── logging-centralization.md
│   └── flowchart/       # Architecture diagrams
├── api/                 # API documentation
│   ├── core_api.md      # Core API specification
│   └── tool_api.md      # Tool API specification
├── implementation/      # Implementation details
│   ├── adapter/         # Adapter layer implementation
│   ├── core/            # Core layer implementation
│   ├── transport/       # Transport layer implementation
│   ├── python/          # Python SDK implementation
│   ├── typescript/      # TypeScript SDK implementation
│   └── cross-cutting/   # Cross-cutting concerns
└── mcpPlanning/         # Planning documents
    ├── final/          # Final implementation plans
    ├── PLAN/          # Step-by-step implementation plans
    └── research/      # Research and investigation notes
```

## Relationship to Source Code

This documentation directly corresponds to the implementation in:

```
src/
├── mcp_proxy/          # Proxy Connection Server (stdio ⇄ SSE)
│   ├── transports/    # Transport implementations
│   └── config/        # Proxy configuration
├── mcp_core/          # Core MCP functionality
│   ├── adapters/      # Tool server adapters
│   ├── config/        # Core configuration
│   ├── logger/        # Structured logging
│   ├── metrics/       # Performance metrics
│   ├── models/        # Data models
│   └── validation/    # Request/response validation
├── mymcpserver/       # Server-specific code
└── tool_servers/      # Tool server implementations
    ├── python_tool_server/    # Python SDK & tools
    └── typescript_tool_server/ # TypeScript SDK & tools
```

### Documentation-Code Mapping

1. **Architecture Documentation**
   - `architecture/System Overview.md` → Overall system design
   - `architecture/Component Design.md` → Component relationships
   - `architecture/logging-centralization.md` → `src/mcp_core/logger/`

2. **API Documentation**
   - `api/core_api.md` → Core API interfaces
   - `api/tool_api.md` → Tool implementation guides

3. **Implementation Details**
   - `implementation/adapter/` → `src/mcp_core/adapters/`
   - `implementation/core/` → `src/mcp_core/`
   - `implementation/transport/` → `src/mcp_proxy/transports/`
   - `implementation/python/` → `src/tool_servers/python_tool_server/`
   - `implementation/typescript/` → `src/tool_servers/typescript_tool_server/`

## Cross-Cutting Concerns

### Configuration Management

- Environment variables
- Configuration files
- Default settings
- Configuration validation

### Error Handling

- Standardized error types
- Error propagation
- Error response formatting
- Contextual error information

### Logging System

- JSON-structured logging
- Log levels and categories
- Contextual metadata
- Performance logging

### Health Monitoring

- Service health checks
- Dependency monitoring
- Performance metrics
- System diagnostics

## Development Workflow

### 1. Documentation Updates

- Update docs with code changes
- Maintain documentation-code mapping
- Keep implementation details current
- Document architectural decisions

### 2. Code Organization

- Follow layered architecture
- Maintain separation of concerns
- Use consistent patterns
- Implement cross-cutting features

### 3. Testing Strategy

- Write comprehensive tests
- Follow test-driven development
- Include integration tests
- Perform load testing

### 4. Deployment Process

- Use container deployment
- Configure monitoring
- Set up logging
- Manage environment configuration

## Related Documentation

### Project Structure

- [[Project MOC]] - Project documentation map
- [[../../mcpKnowledge/MCP Knowledge MOC|MCP Knowledge]] - General MCP concepts
- [[../../docsGuide/Documentation Structure Guide|Documentation Guide]]

### Implementation References

- [[../../mcpKnowledge/development/Implementation Guide|MCP Implementation Guide]]
- [[../../mcpKnowledge/development/Hub Configuration|Hub Configuration Guide]]
- [[../../mcpKnowledge/development/Hub Debugging|Debugging Guide]]

## Usage Guidelines

1. **Implementation Documentation**
   - Document specific implementation details
   - Reference source code locations
   - Explain architectural decisions

2. **Code Relationship**
   - Maintain clear mapping to source code
   - Update documentation with code changes
   - Cross-reference between docs and code

3. **Knowledge Separation**
   - Implementation-specific details here
   - General MCP knowledge in [[../../mcpKnowledge/README|MCP Knowledge Base]]
   - Cross-reference when needed

---

_This documentation covers the specific implementation of MyMcpServer, complementing the general MCP knowledge base._
