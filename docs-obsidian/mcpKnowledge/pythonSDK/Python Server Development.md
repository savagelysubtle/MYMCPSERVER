---
created: 2025-03-28
updated: 2025-03-30
tags: [mcp, python, sdk, development, guide]
parent: [[Python SDK Overview]]
---

# Custom Python MCP Development

## Overview

This guide walks you through creating custom Python-based MCP servers using the official Model Context Protocol SDK. The focus is on creating servers that can be integrated into your MCP central hub, with examples for file management functionality.

## Key Points

- Uses the official MCP Python SDK and create-python-server tool
- Follows best practices for MCP server development
- Provides examples for file management operations
- Includes resource type handling, error management, and testing
- Designed to be deployed in a central hub architecture

## Details

### Prerequisites

1. **Python**: 3.10 or newer installed
2. **UV package manager**: Install with `pip install uv`
3. **MCP Tools**: Install with `pip install create-mcp-server`
4. **Basic Python knowledge**: Understanding of Python functions and async operations
5. **IDE**: VS Code, Cursor IDE, or any Python-compatible editor

### Step 1: Project Setup

1. Create a new Python MCP server project:

   ```bash
   # Navigate to your workspace
   cd /path/to/workspace

   # Create a new server project
   uv create-mcp-server
   ```

2. Follow the interactive prompts:

   - Server name: Your desired name (e.g., `file-manager`)
   - Description: Brief explanation of functionality
   - Package name: Python package name (e.g., `file_manager`)

3. Navigate to the generated project:

   ```bash
   cd file-manager
   ```

### Step 2: Understanding the Project Structure

The generated project has this structure:

```
file-manager/
├── README.md           # Documentation
├── pyproject.toml      # Package configuration
└── src/
    └── file_manager/   # Main package
        ├── __init__.py # Package initialization
        ├── __main__.py # Entry point
        └── server.py   # MCP server implementation
```

Important files:

1. **server.py**: Contains your tool definitions
2. ****main**.py**: Server entry point
3. **pyproject.toml**: Package metadata and dependencies

### Step 3: Defining Custom Tools

See [[Implementation Examples#File Management Tools|File Management Tools Example]] for detailed implementation examples.

### Step 4: Update Dependencies

1. Edit `pyproject.toml` to add required dependencies:

```toml
[project]
name = "file-manager"
description = "File management tools for MCP"
requires-python = ">=3.10"
dependencies = [
    "mcp>=0.3.0",
    "aiofiles>=23.0",
]
```

2. Install dependencies:

```bash
uv sync --all-extras
```

### Step 5: Testing Your Server

1. Start your server locally:

```bash
uv run .
```

2. Test with an MCP client like Cursor IDE:
   - Configure Cursor to connect to your local server
   - Create a test directory and files
   - Try each tool with appropriate parameters

3. Debug common issues:
   - Check standard output for error messages
   - Verify JSON schema formats match your implementation
   - Test handlers independently with sample data

### Step 6: Integration with MCP Central Hub

1. Install in your central hub's Python servers directory:

```bash
cd /path/to/mcp-central-hub/python-servers
git clone /path/to/file-manager
cd file-manager
uv sync --all-extras
```

2. Update the hub's configuration to include your new server:

```json
// config/hub-config.json
{
  "servers": {
    // ... existing servers
    "fileManager": {
      "type": "python",
      "path": "./python-servers/file-manager",
      "enabled": true
    }
  },
  "startup": {
    "autoStart": true,
    "startOrder": [
      // ... existing servers
      "fileManager"
    ]
  }
}
```

3. Restart your MCP central hub to include the new server

### Best Practices

1. **Error Handling**: Always return descriptive error messages
2. **Input Validation**: Validate all inputs before processing
3. **Async Operations**: Use async/await for I/O operations
4. **Resource Management**: Close files and connections properly
5. **Security**: Validate file paths to prevent directory traversal attacks
6. **Documentation**: Document each tool's purpose and parameters clearly
7. **Testing**: Create automated tests for your server tools

## Related Documentation

### Implementation

- [[Implementation Examples|Python Implementation Examples]]
- [[../../development/Implementation Guide|General Implementation Guide]]
- [[../../development/Hub Configuration|Hub Configuration Guide]]

### Project Examples

- [[../../../projects/myMcpServer/implementation/Server Configuration|Server Configuration]]
- [[../../../projects/myMcpServer/mcpPlanning/final/python/tool-server|Tool Server Example]]

## References

- [Create Python MCP Server](https://github.com/modelcontextprotocol/create-python-server)
- [MCP Python SDK Documentation](https://modelcontextprotocol.io/docs/python-sdk)
- [Python AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)

---

[[Python SDK Overview|← Back to Python SDK Overview]]
