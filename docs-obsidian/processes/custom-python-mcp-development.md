---
created: 2025-03-28
tags: process, mcp, python, development
parent: [[Processes MOC]]
---

# Custom Python MCP Development

## Overview

This process guides you through creating custom Python-based MCP servers using the official Model Context Protocol SDK. The focus is on creating servers that can be integrated into your MCP central hub, with examples for file management functionality.

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

Edit `server.py` to define your custom tools. Here's an example for file management tools:

```python
from mcp import (
    Server,
    Tool,
    Function,
    ToolCollection,
    ResourceType,
    request_schema,
    response_schema,
)
import aiofiles
import os
import json
from typing import List, Dict, Any, Optional


# Define tools for file operations
file_tools = ToolCollection(
    "file_management",
    "Tools for managing local files and directories",
    tools=[
        Tool(
            "list_directory",
            "List files and directories in the specified path",
            functions=[
                Function(
                    request_schema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Directory path to list"},
                            "include_hidden": {"type": "boolean", "description": "Whether to include hidden files"}
                        },
                        "required": ["path"]
                    },
                    response_schema={
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "type": {"type": "string", "enum": ["file", "directory"]},
                                        "size": {"type": "integer"},
                                        "modified": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                )
            ]
        ),
        Tool(
            "read_file",
            "Read the contents of a file",
            functions=[
                Function(
                    request_schema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to the file to read"},
                            "encoding": {"type": "string", "description": "File encoding", "default": "utf-8"}
                        },
                        "required": ["path"]
                    },
                    response_schema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "encoding": {"type": "string"}
                        }
                    }
                )
            ]
        ),
        Tool(
            "write_file",
            "Write content to a file",
            functions=[
                Function(
                    request_schema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to write the file"},
                            "content": {"type": "string", "description": "Content to write"},
                            "encoding": {"type": "string", "description": "File encoding", "default": "utf-8"},
                            "create_dirs": {"type": "boolean", "description": "Create directories if they don't exist", "default": False}
                        },
                        "required": ["path", "content"]
                    },
                    response_schema={
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean"},
                            "bytes_written": {"type": "integer"}
                        }
                    }
                )
            ]
        )
    ]
)


# Implement handlers for the tools
async def handle_list_directory(request):
    path = request["path"]
    include_hidden = request.get("include_hidden", False)

    if not os.path.exists(path):
        return {
            "error": f"Path does not exist: {path}"
        }

    if not os.path.isdir(path):
        return {
            "error": f"Path is not a directory: {path}"
        }

    items = []
    for item in os.listdir(path):
        if not include_hidden and item.startswith('.'):
            continue

        item_path = os.path.join(path, item)
        item_stat = os.stat(item_path)

        items.append({
            "name": item,
            "type": "directory" if os.path.isdir(item_path) else "file",
            "size": item_stat.st_size,
            "modified": item_stat.st_mtime
        })

    return {"items": items}


async def handle_read_file(request):
    path = request["path"]
    encoding = request.get("encoding", "utf-8")

    if not os.path.exists(path):
        return {
            "error": f"File does not exist: {path}"
        }

    if not os.path.isfile(path):
        return {
            "error": f"Path is not a file: {path}"
        }

    try:
        async with aiofiles.open(path, mode='r', encoding=encoding) as file:
            content = await file.read()

        return {
            "content": content,
            "encoding": encoding
        }
    except Exception as e:
        return {
            "error": f"Error reading file: {str(e)}"
        }


async def handle_write_file(request):
    path = request["path"]
    content = request["content"]
    encoding = request.get("encoding", "utf-8")
    create_dirs = request.get("create_dirs", False)

    try:
        # Create directories if requested
        if create_dirs:
            os.makedirs(os.path.dirname(path), exist_ok=True)

        async with aiofiles.open(path, mode='w', encoding=encoding) as file:
            bytes_written = await file.write(content)

        return {
            "success": True,
            "bytes_written": bytes_written
        }
    except Exception as e:
        return {
            "error": f"Error writing file: {str(e)}"
        }


# Initialize server with handlers
def create_server():
    server = Server()

    # Register the tool collection
    server.register_tool_collection(file_tools)

    # Register handlers
    server.register_handler("file_management.list_directory", handle_list_directory)
    server.register_handler("file_management.read_file", handle_read_file)
    server.register_handler("file_management.write_file", handle_write_file)

    return server
```

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

## Related Notes

- [[MCP Central Hub]] - Central hub for managing multiple MCP servers
- [[MCP Architecture]] - Core architecture of MCP protocol
- [[Setting Up MCP Central Hub for Windows]] - Complete hub setup process

## References

- [Create Python MCP Server](https://github.com/modelcontextprotocol/create-python-server)
- [MCP Python SDK Documentation](https://modelcontextprotocol.io/docs/python-sdk)
- [Python AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)

---

_This note belongs to the [[Processes MOC]]_
