---
created: 2025-03-30
updated: 2025-03-31
tags: [folder-note, implementation, myMcpServer]
parent: [[../_index]]
up: [[../_index]]
contains:
  [
    [[core/_index]],
    [[transport/_index]],
    [[adapter/_index]],
    [[python/_index]],
    [[typescript/_index]],
    [[cross-cutting/_index]],
    [[Server Configuration]],
  ]
---

# Implementation Directory Index

This directory contains documentation related to the implementation details of the myMcpServer project, organized by component layers.

## Structure / Key Contents

- [[core/_index|Core]] - Core implementation components
  - [[core/overview-v2|Core Overview]] - Request Processing, Configuration Management, Metrics Collection
  - [[core/technical-v2|Core Implementation]] - Request Validation, Response Formatting, Error Handling
- [[transport/_index|Transport]] - Transport layer implementation
  - [[transport/overview-v2|Transport Overview]] - Protocol Conversion, Connection Management
  - [[transport/technical-v2|Transport Implementation]] - Transport Manager, Protocol Adapters, Health Endpoints
- [[adapter/_index|Adapter]] - Adapter layer implementation
  - [[adapter/technical-v2|Adapter Implementation]] - Tool Registration, Version Management
- [[python/_index|Python]] - Python-specific implementation details
  - [[python/tool-server|Python Tool Server]] - SDK Architecture, Tool Implementation Guide
  - [[python/cli-tool|CLI Tool]] - Secure Command Execution for Windows Environments
- [[typescript/_index|TypeScript]] - TypeScript-specific implementation details
  - [[typescript/tool-server|TypeScript Tool Server]] - SDK Architecture, Tool Implementation Guide
- [[cross-cutting/_index|Cross-Cutting]] - Cross-cutting concerns implementation
  - [[cross-cutting/technical-v1|Cross-Cutting Implementation]] - Configuration System, Error Framework, Logging System
- [[Server Configuration|Server Configuration]] - Server configuration details

## Development

### Setup & Configuration

- [[Server Configuration|Development Setup]] - Environment Setup, Dependencies, Local Development
- Configuration Guide - Environment Variables, Config Files, Defaults
- Deployment Guide - Container Setup, Production Configuration, Monitoring Setup

## Contained Notes (Dataview)

```dataview
LIST
FROM "projects/myMcpServer/implementation"
WHERE file.name != "_index"
SORT file.name ASC
```

## Navigation

- Parent: [[../_index|myMcpServer Project]]
- Related:
  - [[../architecture/_index|Architecture]] (implements)
  - [[../api/_index|API]] (implements)
  - [[../../mcpKnowledge/development/_index|Development Resources]] (references)
