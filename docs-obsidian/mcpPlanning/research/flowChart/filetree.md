this uses the proxy server
https://github.com/sparfenyuk/mcp-proxy?tab=readme-ov-file#installing-via-github-repository-latest

configuration for this server
https://github.com/sparfenyuk/mcp-proxy?tab=readme-ov-file#2-sse-to-stdio

Please see @flowchart.md for the flowchart

```richtext
MYMCPSERVER/
├── docs/                           # Documentation and diagrams
│   ├── architecture.md           # Detailed architecture & design decisions
│   ├── flowchart.png             # Our latest flowchart image
│   └── file_tree.md              # Explanation of the project structure
├── Makefile                        # Targets to launch each service locally
├── Procfile                        # Optional, for process management (e.g., using Honcho)
├── pyproject.toml                  # Project-level build and metadata configuration
├── requirements.txt                # Top-level dependencies (if any common ones)
├── src/                            # All source code lives here
│   ├── mcp_proxy/                 # Proxy Connection Server (stdio ⇄ SSE)
│   │   ├── __init__.py
│   │   ├── __main__.py            # Entry point for starting the proxy server
│   │   ├── proxy_server.py        # Core proxy server logic
│   │   ├── sse_client.py          # Implements SSE client functionality
│   │   └── sse_server.py          # Implements SSE server functionality
│   ├── mcp_core/                  # MCP Core Layer (Python)
│   │   ├── app.py                 # Main entry point for the MCP core service
│   │   ├── config.py              # Configuration management
│   │   ├── registry.py            # Registry/facade for dynamic tool server lookup
│   │   └── adapters/              # Adapter/Registry Layer
│   │       ├── __init__.py
│   │       ├── base_adapter.py    # Abstract adapter interface
│   │       ├── python_adapter.py  # Adapter for Python tool servers (using Python SDK)
│   │       └── ts_adapter.py      # Adapter for TypeScript tool servers (via REST/RPC)
│   └── tool_servers/              # Tool Server implementations
│       ├── python_tool_server/    # Python-based MCP tool server
│       │   ├── server.py          # Main entry point for this tool server
│       │   ├── n1/                # Subpackage for tool n1 (e.g., Obsidian Tool)
│       │   │   ├── __init__.py
│       │   │   └── tool.py
│       │   ├── n2/                # Subpackage for tool n2 (e.g., AIChemist Tool)
│       │   │   ├── __init__.py
│       │   │   └── tool.py
│       │   └── requirements.txt   # Dependencies specific to the Python tool server
│       └── typescript_tool_server/  # TypeScript-based MCP tool server
│           ├── package.json       # Node.js project file
│           ├── tsconfig.json      # TypeScript configuration
│           └── src/
│               ├── index.ts       # Main entry point for the TS tool server
│               ├── n3/            # Subpackage for tool n3 (e.g., Thinking Tool)
│               │   └── index.ts
│               └── n4/            # Subpackage for tool n4 (e.g., Another Tool)
│                   └── index.ts
└── tests/                        # Integration tests for the microservices system
    ├── integration_tests/
    │   ├── test_mcp_core.py      # Tests for core logic and adapter integration
    │   ├── test_proxy_server.py  # Tests for proxy server functionality
    │   └── test_tool_servers.py  # Tests for tool server endpoints and responses
    └── README.md

```
