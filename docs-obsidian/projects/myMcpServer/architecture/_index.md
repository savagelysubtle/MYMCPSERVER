---
created: 2025-03-30
updated: 2025-03-30
tags: [folder-note, architecture, myMcpServer]
parent: [[../_index]]
up: [[../_index]]
contains:
  [
    [[System Overview]],
    [[Component Design]],
    [[logging-centralization]],
    [[overview]],
    [[filetree]],
    [[flowchart/_index]],
  ]
---

# Architecture Directory Index

This directory contains documentation related to the architecture of the myMcpServer project, including system design, component structure, and architectural decisions.

## Structure / Key Contents

- [[System Overview|System Overview]] - High-level overview of the system architecture
  - Transport Layer (SSE ⇄ stdio)
  - Core Processing Layer
  - Registry/Adapter Layer
  - Tool Server Layer
- [[Component Design|Component Design]] - Detailed design of system components
  - Component Interactions
  - Design Patterns
  - Implementation Guidelines
- [[logging-centralization|Logging Centralization]] - Architecture for centralized logging
- [[overview|Architecture Overview]] - Comprehensive architecture overview
- [[filetree|File Structure]] - Project file structure
- [[flowchart/_index|Flowcharts]] - Visual system flow diagrams

## Cross-Cutting Concerns

- Configuration Management
- Error Handling Framework
- Health Monitoring
- Metrics Collection

## Contained Notes (Dataview)

```dataview
LIST
FROM "projects/myMcpServer/architecture"
WHERE file.name != "_index"
SORT file.name ASC
```

## Navigation

- Parent: [[../_index|myMcpServer Project]]
- Related:
  - [[../implementation/_index|Implementation]] (implements)
  - [[../api/_index|API]] (interfaces)
  - [[../../mcpKnowledge/core/MCP Server Architecture|MCP Architecture]] (references)
