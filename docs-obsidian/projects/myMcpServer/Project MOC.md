---
created: 2025-03-30
tags: [MOC, project, myMcpServer, mcp-hub]
---

# MyMcpServer Project MOC

This Map of Content organizes all documentation specific to the MyMcpServer implementation, a modular and extensible MCP (Machine Comprehension Platform) system that connects AI clients with specialized tool servers.

## Architecture

### System Design

- [[architecture/System Overview]] - High-level system architecture
  - Transport Layer (SSE ⇄ stdio)
  - Core Processing Layer
  - Registry/Adapter Layer
  - Tool Server Layer
- [[architecture/Component Design]] - Component architecture
  - Component Interactions
  - Design Patterns
  - Implementation Guidelines
- [[architecture/logging-centralization|Logging Centralization]] - Unified logging strategy
- [[architecture/flowchart/flowchart|System Flowcharts]] - Visual architecture diagrams

### Cross-Cutting Concerns

- Configuration Management
- Error Handling Framework
- Health Monitoring
- Metrics Collection

## API Documentation

### Core API

- [[api/core_api|Core API Specification]]
  - Request/Response Format
  - Core Methods
  - Error Handling

### Tool API

- [[api/tool_api|Tool API Specification]]
  - Tool Implementation
  - Registration Process
  - SDK Usage

## Implementation

### Transport Layer

- [[implementation/transport/overview-v2|Transport Overview]]
  - Protocol Conversion
  - Connection Management
  - Error Handling
- [[implementation/transport/technical-v2|Transport Implementation]]
  - Transport Manager
  - Protocol Adapters
  - Health Endpoints

### Core Components

- [[implementation/core/overview-v2|Core Overview]]
  - Request Processing
  - Configuration Management
  - Metrics Collection
- [[implementation/core/technical-v2|Core Implementation]]
  - Request Validation
  - Response Formatting
  - Error Handling

### Adapters

- [[implementation/adapter/technical-v2|Adapter Implementation]]
  - Tool Registration
  - Version Management
  - Circuit Breaker
  - Health Monitoring

### Tool Servers

#### Python

- [[implementation/python/tool-server|Python Tool Server]]
  - SDK Architecture
  - Tool Implementation Guide
  - Example Tools:
    - Obsidian Tool
    - AIChemist Tool

#### TypeScript

- [[implementation/typescript/tool-server|TypeScript Tool Server]]
  - SDK Architecture
  - Tool Implementation Guide
  - Example Tools:
    - Thinking Tool
    - Additional Tools

### Cross-Cutting

- [[implementation/cross-cutting/technical-v1|Cross-Cutting Implementation]]
  - Configuration System
  - Error Framework
  - Logging System
  - Health Checks

## Development

### Setup & Configuration

- [[implementation/Server Configuration|Development Setup]]
  - Environment Setup
  - Dependencies
  - Local Development
- Configuration Guide
  - Environment Variables
  - Config Files
  - Defaults
- Deployment Guide
  - Container Setup
  - Production Configuration
  - Monitoring Setup

### Testing

- Unit Testing Strategy
  - Component Tests
  - Integration Tests
  - Load Testing
- Integration Testing
  - End-to-End Tests
  - Tool Server Tests
- Performance Testing
  - Load Tests
  - Benchmarks
  - Monitoring

## Related Knowledge

### MCP Knowledge

- [[../../mcpKnowledge/core/MCP Server Architecture|MCP Architecture]]
- [[../../mcpKnowledge/core/MCP Central Hub|MCP Central Hub]]
- [[../../mcpKnowledge/core/Tool Management|Tool Management]]

### Language Guides

- [[../../languages/python/Python MOC|Python Development]]
- [[../../languages/typescript/TypeScript MOC|TypeScript Development]]

---

_This MOC focuses on the MyMcpServer implementation, linking to both project-specific documentation and relevant shared knowledge._

## Automatically Linked Notes

_Notes that link to this MOC:_

```dataview
list from [[Project MOC]] and !outgoing([[Project MOC]])
```

---

[[../../Home|← Back to Home]]
