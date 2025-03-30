---
created: 2025-03-30
tags: [mcp, documentation, index]
parent: [[MCP Knowledge MOC]]
---

# MCP Knowledge Base

## Overview

This directory contains general knowledge and documentation about the Model Context Protocol (MCP), independent of any specific implementation. It serves as a comprehensive reference for understanding MCP concepts, patterns, and best practices.

## Directory Structure

```
mcpKnowledge/
├── core/                  # Core MCP concepts and architecture
├── development/          # Implementation guides and patterns
├── integration/          # Integration guides for various systems
├── pythonSDK/           # Python SDK documentation
├── typeScriptSDK/       # TypeScript SDK documentation
└── reference/           # Reference materials and lists
```

## Content Categories

### Core Concepts

- [[core/MCP Architecture|MCP Architecture]] - Fundamental architecture and design
- [[core/MCP Central Hub|MCP Central Hub]] - Central hub concepts
- [[core/Tool Management|Tool Management]] - Tool management system
- [[core/Remote Servers|Remote Servers]] - Remote server architecture

### Development Guides

- [[development/Implementation Guide|Implementation Guide]] - General implementation patterns
- [[development/Hub Configuration|Hub Configuration]] - Configuration reference
- [[development/Hub Debugging|Hub Debugging]] - Debugging and troubleshooting

### SDK Documentation

- [[pythonSDK/Python SDK Overview|Python SDK]] - Python implementation
- [[typeScriptSDK/TypeScript Server Development|TypeScript SDK]] - TypeScript implementation

### Integration Guides

- [[integration/Cursor MCP Integration|Cursor Integration]] - Cursor IDE integration
- [[integration/Sequential Thinking Tools|Sequential Thinking]] - Tool integration

## Relationship to Project Implementation

This knowledge base is distinct from the project-specific implementation details found in:

- [[../projects/myMcpServer/Project MOC|MyMcpServer Project]] - Specific implementation
- [[../src/|Source Code]] - Actual code implementation

The content here focuses on general MCP knowledge that applies across different implementations, while project-specific details are maintained in their respective directories.

## Usage Guidelines

1. **General vs. Specific**
   - Keep implementation-specific details in the project directory
   - Maintain general concepts and patterns here
   - Cross-reference between general and specific when needed

2. **Documentation Standards**
   - Follow the [[../docsGuide/Documentation Structure Guide|Documentation Guide]]
   - Use proper metadata and linking
   - Maintain clear separation of concerns

3. **Content Organization**
   - Use appropriate subdirectories
   - Link related content
   - Keep MOCs updated

## Related Documentation

- [[../Home|Home]] - Main documentation hub
- [[MCP Knowledge MOC]] - MCP knowledge map
- [[../docsGuide/Documentation Structure Guide|Documentation Guide]]

---

_This directory maintains general MCP knowledge separate from specific implementations._
