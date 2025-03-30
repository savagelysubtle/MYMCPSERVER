---
created: 2025-03-30
updated: 2025-03-30
tags: [MOC, mcp, knowledge-base]
parent: [[Home]]
up: [[Home]]
siblings: [[Project MOC]], [[Tech MOC]], [[Processes MOC]]
implements: [[mcpKnowledge/core/MCP Architecture]]
extends: [[Tech MOC]]
contains: [
  [[mcp/concepts/MCP Architecture]],
  [[mcp/concepts/MCP Protocol]],
  [[mcp/concepts/MCP Server Types]],
  [[mcp/concepts/MCP Central Hub]],
  [[mcp/concepts/MCP Tool Management]]
]
---

# MCP MOC

This Map of Content organizes all knowledge specific to the Model Context Protocol (MCP) system.

## Core Concepts

### Architecture (implements)

- [[mcp/concepts/MCP Architecture]] - Fundamental structure and components
- [[mcp/concepts/MCP Protocol]] - Protocol design and specifications
- [[mcp/concepts/MCP Server Types]] - Types of MCP servers and their roles

### Components (implements)

- [[mcp/concepts/MCP Central Hub]] - Central management system
- [[mcp/concepts/MCP Remote Servers]] - Remote server architecture
- [[mcp/concepts/MCP Tool Management]] - Tool discovery and management

### Integration (extends)

- [[mcp/concepts/Cursor Integration]] - Cursor IDE integration
- [[mcp/concepts/IDE Integration]] - General IDE integration patterns
- [[mcp/concepts/API Integration]] - External API integration

## Implementation Patterns

### Development (implements)

- [[mcp/patterns/Server Development]] - MCP server development guidelines
- [[mcp/patterns/Tool Development]] - Tool development best practices
- [[mcp/patterns/Protocol Implementation]] - Protocol implementation patterns

### Security (extends)

- [[mcp/patterns/Authentication]] - Authentication patterns
- [[mcp/patterns/Authorization]] - Authorization patterns
- [[mcp/patterns/Security Best Practices]] - Security guidelines

### Performance (implements)

- [[mcp/patterns/Scaling]] - Scaling strategies
- [[mcp/patterns/Optimization]] - Performance optimization
- [[mcp/patterns/Resource Management]] - Resource handling

## Reference

### Technical Specifications (implements)

- [[mcp/reference/Protocol Specification]] - Detailed protocol specs
- [[mcp/reference/API Reference]] - API documentation
- [[mcp/reference/Configuration Reference]] - Configuration guide

### SDKs (implements)

- [[mcp/reference/Python SDK]] - Python implementation
- [[mcp/reference/TypeScript SDK]] - TypeScript implementation
- [[mcp/reference/SDK Guidelines]] - SDK development guidelines

### Standards (extends)

- [[mcp/reference/Coding Standards]] - Code style and standards
- [[mcp/reference/Documentation Standards]] - Documentation guidelines
- [[mcp/reference/Testing Standards]] - Testing requirements

## Navigation

### Breadcrumb Trail

1. [[Home|Home]]
2. Current: MCP Knowledge

### Related MOCs

- [[Project MOC]] (implements) - Project-specific implementation details
- [[Tech MOC]] (extends) - General technical knowledge
- [[Processes MOC]] (related) - Implementation procedures
- [[Reference MOC]] (extends) - Detailed technical references

## Knowledge Organization

### Core Knowledge

```dataview
list from [[MCP MOC]]
where type = "implements"
```

### Extended Knowledge

```dataview
list from [[MCP MOC]]
where type = "extends"
```

### Related Knowledge

```dataview
list from [[MCP MOC]]
where type = "related"
```

---

_This MOC focuses on MCP-specific knowledge, separate from project implementation details and general technical concepts._

## Automatically Linked Notes

_Notes that link to this MOC:_

```dataview
list from [[MCP MOC]] and !outgoing([[MCP MOC]])
```

---

[[Home|← Back to Home]]
