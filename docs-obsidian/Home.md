---
created: 2025-03-28
updated: 2025-03-30
tags: [home, moc]
contains: [
  [[mcpKnowledge/MCP Knowledge MOC]],
  [[projects/myMcpServer/Project MOC]],
  [[generalKnowledge/General Knowledge MOC]],
  [[languages/python/Python MOC]],
  [[languages/typescript/TypeScript MOC]]
]
---

# Home

Welcome to the MCP Central Hub Knowledge Base. This documentation is organized into distinct categories for clarity and ease of navigation.

## Documentation Organization

This documentation is organized into these main sections:

### 1. MCP Knowledge Base [[mcpKnowledge/README|Overview]] (implements)

General knowledge about the Model Context Protocol (MCP) system, independent of specific implementations.

#### Core Concepts

- [[mcpKnowledge/core/MCP Server Architecture|MCP Architecture]] - Core architectural principles
- [[mcpKnowledge/core/MCP Central Hub|MCP Central Hub]] - Central hub design
- [[mcpKnowledge/core/Tool Management|Tool Management]] - Tool management system

#### Development Resources

- [[mcpKnowledge/development/Implementation Guide|Implementation Guide]]
- [[mcpKnowledge/development/Hub Configuration|Configuration Guide]]
- [[mcpKnowledge/development/Hub Debugging|Debugging Guide]]

#### SDK Documentation

##### Python SDK

- [[mcpKnowledge/pythonSDK/Python SDK Overview|Python SDK Overview]]
- [[mcpKnowledge/pythonSDK/Python Server Development|Server Development]]
- [[mcpKnowledge/pythonSDK/Python Tool Implementation|Tool Implementation]]

##### TypeScript SDK

- [[mcpKnowledge/typeScriptSDK/TypeScript SDK Overview|TypeScript SDK Overview]]
- [[mcpKnowledge/typeScriptSDK/TypeScript Server Development|Server Development]]
- [[mcpKnowledge/typeScriptSDK/TypeScript Tool Implementation|Tool Implementation]]

### 2. Project Implementation [[projects/myMcpServer/README|Overview]] (implements)

Specific documentation for the MyMcpServer implementation, corresponding to the `src/` directory.

#### Architecture

- [[projects/myMcpServer/architecture/System Overview|System Overview]]
- [[projects/myMcpServer/architecture/logging-centralization|Logging Centralization]]
- [[projects/myMcpServer/architecture/Component Design|Component Design]]

#### Implementation

- [[projects/myMcpServer/implementation/Setup Guide|Setup Guide]]
- [[projects/myMcpServer/implementation/Configuration|Configuration]]
- [[projects/myMcpServer/implementation/Deployment|Deployment]]

### 3. General Knowledge [[generalKnowledge/README|Overview]] (extends)

General knowledge and rules that apply across different contexts.

#### Making Rules

- [[generalKnowledge/makingRules/Overview|Rules Overview]]
- [[generalKnowledge/makingRules/Best Practices|Rules Best Practices]]
- [[generalKnowledge/makingRules/Implementation|Rules Implementation]]

### 4. Language Knowledge (implements)

Shared knowledge for programming languages, applicable across projects.

#### Python Development

- [[languages/python/core/Python Best Practices|Best Practices]]
- [[languages/python/core/Python Design Patterns|Design Patterns]]
- [[languages/python/testing/Python Testing|Testing Guide]]

#### TypeScript Development

- [[languages/typescript/core/TypeScript Best Practices|Best Practices]]
- [[languages/typescript/core/TypeScript Design Patterns|Design Patterns]]
- [[languages/typescript/testing/TypeScript Testing|Testing Guide]]

## Maps of Content

### Core Documentation

- [[mcpKnowledge/MCP Knowledge MOC|MCP Knowledge]] (implements) - General MCP concepts and standards
- [[projects/myMcpServer/Project MOC|MyMcpServer]] (implements) - Project-specific implementation
- [[generalKnowledge/General Knowledge MOC|General Knowledge]] (extends) - Cross-cutting knowledge
- [[docsGuide/Documentation Structure Guide|Documentation Guide]] (implements) - How to maintain docs

### Language Knowledge

- [[languages/python/Python MOC|Python]] (implements) - Python development knowledge
- [[languages/typescript/TypeScript MOC|TypeScript]] (implements) - TypeScript development knowledge

### Support

- [[templates/Note Template|Create New Note]] (related)
- [[templates/MOC Template|Create New MOC]] (related)

---

## Documentation Structure

This knowledge base maintains clear separation between:

1. **General MCP Knowledge** ([[mcpKnowledge/README|Overview]])
   - Core concepts and architecture
   - SDK documentation
   - Best practices and patterns

2. **Project Implementation** ([[projects/myMcpServer/README|Overview]])
   - Specific implementation details
   - Project architecture
   - Source code documentation

3. **General Knowledge** ([[generalKnowledge/README|Overview]])
   - Cross-cutting concepts
   - Universal rules and patterns
   - Best practices

4. **Language Knowledge**
   - Shared programming patterns
   - Language-specific best practices
   - Reusable knowledge

For details on maintaining this structure, see the [[docsGuide/Documentation Structure Guide|Documentation Guide]].

---

## Navigation

### Contained Documents

```dataview
list from [[Home]]
where contains(file.outlinks, this.file.link)
```

### Implementation Documents

```dataview
list from [[Home]]
where type = "implements"
```

### Extended Knowledge

```dataview
list from [[Home]]
where type = "extends"
