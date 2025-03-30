---
created: 2025-03-28
tags: [mcp, python, development]
parent: [[Processes MOC]]
---

# Creating Python MCP Servers

## Overview

This guide outlines the process for creating Python-based MCP servers using the official `create-python-server` tool, which provides a standardized way to structure and implement Model Context Protocol servers in Python.

## Prerequisites

- Python 3.8 or higher
- UV package manager (recommended)
- Basic knowledge of Python development
- Understanding of MCP concepts

## Step-by-Step Process

### 1. Setting Up the Development Environment

1. Install UV package manager (if not already installed):

   ```bash
   pip install uv
   ```

2. Create a new MCP server project:

   ```bash
   # Using UV (recommended method)
   uv create-mcp-server

   # Alternative: using pip
   pip install create-python-server
   create-python-server
   ```

3. Follow the interactive prompts to configure:
   - Server name
   - Package name
   - Initial version
   - Description
   - Author information

### 2. Understanding the Project Structure

Once created, your project will have this structure:

```
my-server/
├── README.md
├── pyproject.toml
└── src/
    └── my_server/
        ├── __init__.py
        ├── __main__.py
        └── server.py
```

Key files:

- `server.py`: Main implementation of MCP server
- `__main__.py`: Entry point for running the server
- `pyproject.toml`: Package configuration and dependencies

### 3. Implementing Tools and Resources

1. Open `server.py` and add your custom tools:

   ```python
   from modelcontextprotocol.server import McpServer, Resource, Tool

   server = McpServer(name="my-server", version="0.1.0")

   # Define a tool
   @server.tool("my_tool")
   def my_tool(param1: str, param2: int = 0) -> dict:
       """
       Description of what your tool does.

       Args:
           param1: Description of param1
           param2: Description of param2 (optional)

       Returns:
           Result with content
       """
       # Tool implementation
       result = f"Processed {param1} with value {param2}"
       return {"content": [{"type": "text", "text": result}]}

   # Define a resource (optional)
   @server.resource("my_resource")
   def my_resource(uri: str) -> dict:
       """Resource implementation"""
       return {
           "contents": [
               {"uri": uri, "text": "Resource content here"}
           ]
       }
   ```

### 4. Testing the Server Locally

1. Install development dependencies:

   ```bash
   cd my-server
   uv sync --dev --all-extras
   ```

2. Run the server:

   ```bash
   uv run my-server
   ```

3. The server will start running in stdio mode, ready to receive MCP requests

### 5. Integrating with Cursor

1. Configure the server in Cursor's MCP settings or in `.cursor/mcp.json`:

   ```json
   {
     "mcpServers": {
       "my-python-server": {
         "command": "python",
         "args": ["-m", "my_server"],
         "env": {}
       }
     }
   }
   ```

2. For central hub integration, add to `servers.json`:
   ```json
   "myPythonServer": {
     "type": "python",
     "path": "path/to/my_server",
     "configPath": "config/my-server.json"
   }
   ```

## Best Practices

- Keep tool descriptions clear and concise
- Handle errors gracefully with appropriate error messages
- Use type hints for all parameters
- Implement proper validation of input parameters
- Use docstrings to document tools and resources
- Create separate modules for complex tool implementations

## Related Processes

- [[Setting Up MCP Central Hub]]
- [[Tool Integration Strategy]]
- [[Python Server Deployment]]

## References

- [[MCP Server Architecture]]
- [[Python MCP Server Components]]
- [Create Python Server GitHub Repository](https://github.com/modelcontextprotocol/create-python-server)
