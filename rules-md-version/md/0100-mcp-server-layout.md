---
description: ALWAYS Follow the the architecture laid out in linked docs
globs: '**/*'
alwaysApply: false
---

<aiDecision>
  description: ALWAYS Follow the the architecture laid out in linked docs
  globs: "**/*"
  alwaysApply: false
</aiDecision>

<context>
  <IMPORTANT>
  CRITICAL: ALWAYS Follow the the architecture laid out in [filetree.md](mdc:docs-obsidian/user added for indexing later/mcpPlanning/final/filetree.md), [flowchart.md](mdc:docs-obsidian/user added for indexing later/mcpPlanning/final/flowchart/flowchart.md) when working in the project files
  fileTree [filetree.md](mdc:docs-obsidian/user added for indexing later/mcpPlanning/final/filetree.md) shows the rest of the server including test
  flowChart [flowchart.md](mdc:docs-obsidian/user added for indexing later/mcpPlanning/final/flowchart/flowchart.md) shows the overall flow of the project
  </IMPORTANT>
</context>

<fileTreeMAINSRC>
├── src/                            # All source code lives here
│   ├── mcp_proxy/                  # Proxy Connection Server (stdio ⇄ SSE)
│   │   ├── __init__.py
│   │   ├── __main__.py             # Entry point for proxy server
│   │   ├── proxy_server.py         # Core proxy server logic
│   │   ├── transports/             # Transport layer implementations
│   │   │   ├── __init__.py
│   │   │   ├── sse.py              # SSE transport
│   │   │   ├── stdio.py            # stdio transport
│   │   │   └── websocket.py        # WebSocket transport (future)
│   │   ├── health.py               # Health check endpoints
│   │   └── errors.py               # Proxy-specific error handling
│   ├── mcp_core/                   # MCP Core Layer (Python)
│   │   ├── __init__.py
│   │   ├── app.py                  # Main entry point for MCP core
│   │   ├── config.py               # Configuration management
│   │   ├── registry.py             # Tool registry management
│   │   ├── errors.py               # Error handling framework
│   │   ├── logger.py               # Structured logging system
│   │   ├── health.py               # Health monitoring
│   │   ├── metrics/                # Metrics collection
│   │   │   ├── __init__.py
│   │   │   ├── collectors.py       # Metric collectors
│   │   │   └── exporters.py        # Metric exporters
│   │   ├── validation/             # Request/response validation
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py          # JSON schemas
│   │   │   └── validators.py       # Validation logic
│   │   ├── models/                 # Data models for MCP
│   │   │   ├── __init__.py
│   │   │   ├── request.py          # Request model definitions
│   │   │   └── response.py         # Response model definitions
│   │   └── adapters/               # Adapter/Registry Layer
│   │       ├── __init__.py
│   │       ├── base_adapter.py     # Abstract adapter interface
│   │       ├── python_adapter.py   # Python tool server adapter
│   │       ├── ts_adapter.py       # TypeScript tool server adapter
│   │       ├── version.py          # Tool versioning support
│   │       └── circuit_breaker.py  # Circuit breaker implementation
│   └── tool_servers/               # Tool Server implementations
│       ├── python_tool_server/     # Python-based MCP tool server
│       │   ├── __init__.py
│       │   ├── server.py           # Python tool server entry point
│       │   ├── health.py           # Tool server health checks
│       │   ├── errors.py           # Tool-specific error handling
│       │   ├── hot_reload.py       # Hot reload support
│       │   ├── n1/                 # Obsidian Tool
│       │   │   ├── __init__.py
│       │   │   ├── tool.py         # Tool implementation
│       │   │   └── models.py       # Tool-specific data models
│       │   ├── n2/                 # AIChemist Tool
│       │   │   ├── __init__.py
│       │   │   ├── tool.py         # Tool implementation
│       │   │   └── models.py       # Tool-specific data models
│       │   └── requirements.txt    # Python tool server dependencies
│       └── typescript_tool_server/ # TypeScript-based tool server
│           ├── package.json        # Node.js project file
│           ├── tsconfig.json       # TypeScript configuration
│           ├── jest.config.js      # Test configuration
│           └── src/
│               ├── index.ts        # Main entry point
│               ├── health.ts       # Health check implementation
│               ├── errors.ts       # Error handling utilities
│               ├── logger.ts       # Structured logging
│               ├── hot-reload.ts   # Hot reload implementation
│               ├── n3/             # Thinking Tool
│               │   ├── index.ts    # Tool implementation
│               │   └── models.ts   # Tool-specific data models
│               └── n4/             # Another Tool
│                   ├── index.ts    # Tool implementation
│                   └── models.ts   # Tool-specific data models
</fileTreeMAINSRC>

<requirements>
  <!-- Add requirements here based on the fileTree if applicable -->
</requirements>

<examples>
  <!-- Add examples here if applicable -->
</examples>
