---
created: 2025-03-28
updated: 2025-03-30
tags: [home, folder-note, root]
parent: [] # Root node has no parent
up: [] # Root node has no up link
siblings: []
contains:
  [
    [[mcpKnowledge/_index]],
    [[projects/_index]],
    [[generalKnowledge/_index]],
    [[languages/_index]],
    [[docsGuide/_index]],
  ]
---

# Documentation Root

Welcome to the MCP Central Hub Knowledge Base. This documentation is organized into distinct categories for clarity and ease of navigation.

## Documentation Organization

This documentation is organized into these main sections:

### 1. MCP Knowledge Base [[mcpKnowledge/_index|MCP Knowledge]] (implements)

General knowledge about the Model Context Protocol (MCP) system, independent of specific implementations.

#### Core Concepts

- [[mcpKnowledge/core/MCP Server Architecture|MCP Architecture]] (implements) - Core architectural principles
- [[mcpKnowledge/core/MCP Central Hub|MCP Central Hub]] (implements) - Central hub design
- [[mcpKnowledge/core/Tool Management|Tool Management]] (implements) - Tool management system

#### Development Resources

- [[mcpKnowledge/development/Implementation Guide|Implementation Guide]] (implements)
- [[mcpKnowledge/development/Hub Configuration|Configuration Guide]] (implements)
- [[mcpKnowledge/development/Hub Debugging|Debugging Guide]] (implements)

#### SDK Documentation

##### Python SDK

- [[mcpKnowledge/pythonSDK/Python SDK Overview|Python SDK Overview]] (implements)
- [[mcpKnowledge/pythonSDK/Python Server Development|Server Development]] (implements)
- [[mcpKnowledge/pythonSDK/Python Tool Implementation|Tool Implementation]] (implements)

##### TypeScript SDK

- [[mcpKnowledge/typeScriptSDK/TypeScript SDK Overview|TypeScript SDK Overview]] (implements)
- [[mcpKnowledge/typeScriptSDK/TypeScript Server Development|Server Development]] (implements)
- [[mcpKnowledge/typeScriptSDK/TypeScript Tool Implementation|Tool Implementation]] (implements)

### 2. Project Implementation [[projects/myMcpServer/_index|MyMcpServer]] (implements)

Specific documentation for the MyMcpServer implementation, corresponding to the `src/` directory.

#### Architecture

- [[projects/myMcpServer/architecture/System Overview|System Overview]] (implements)
- [[projects/myMcpServer/architecture/logging-centralization|Logging Centralization]] (implements)
- [[projects/myMcpServer/architecture/Component Design|Component Design]] (implements)

#### Implementation

- [[projects/myMcpServer/implementation/Server Configuration|Server Configuration]] (implements)

### 3. General Knowledge [[generalKnowledge/_index|General Knowledge]] (extends)

General knowledge and rules that apply across different contexts.

#### Making Rules

- [[generalKnowledge/makingRules/creatingRules|Creating Rules Guide]] (extends)

### 4. Language Knowledge [[languages/_index|Languages]] (implements)

Shared knowledge for programming languages, applicable across projects.

#### Python Development

- [[languages/python/core-concepts/_index|Core Concepts]] (implements)
- [[languages/python/best-practices/_index|Best Practices]] (implements)
- [[languages/python/testing/_index|Testing]] (implements)

#### TypeScript Development

- [[languages/typescript/core-concepts/_index|Core Concepts]] (implements)
- [[languages/typescript/best-practices/_index|Best Practices]] (implements)
- [[languages/typescript/testing/_index|Testing]] (implements)

## Major Directories

- [[mcpKnowledge/_index|MCP Knowledge]] (implements) - General MCP concepts and standards
- [[projects/_index|Projects]] (implements) - Project-specific implementations
- [[generalKnowledge/_index|General Knowledge]] (extends) - Cross-cutting knowledge
- [[languages/_index|Languages]] (implements) - Programming language knowledge
- [[docsGuide/_index|Documentation Guide]] (implements) - How to maintain docs

## Documentation Structure

This knowledge base maintains clear separation between:

1. **General MCP Knowledge** ([[mcpKnowledge/_index|MCP Knowledge]])

   - Core concepts and architecture
   - SDK documentation
   - Best practices and patterns

2. **Project Implementation** ([[projects/myMcpServer/_index|MyMcpServer]])

   - Specific implementation details
   - Project architecture
   - Source code documentation

3. **General Knowledge** ([[generalKnowledge/_index|General Knowledge]])

   - Cross-cutting concepts
   - Universal rules and patterns
   - Best practices

4. **Language Knowledge** ([[languages/_index|Languages]])
   - Shared programming patterns
   - Language-specific best practices
   - Reusable knowledge

For details on maintaining this structure, see the [[docsGuide/Documentation Structure Guide|Documentation Guide]].

---

## Navigation

### Contained Notes (Dataview)

```dataview
LIST
FROM "docs-obsidian"
WHERE file.name != "_index" AND file.folder = "docs-obsidian"
SORT file.name ASC
```
