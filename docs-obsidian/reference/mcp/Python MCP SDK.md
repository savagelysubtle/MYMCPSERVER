---
created: 2024-03-29
tags: [mcp, python, sdk, reference]
parent: [[Reference MOC]]
---

# Python MCP SDK Reference

## Overview

The Python MCP SDK provides a streamlined way to create Model Context Protocol servers that expose data and functionality to LLM applications. This document serves as a comprehensive reference for the Python implementation of MCP.

## Installation

```bash
pip install mcp smithery
```

## Core Components

### FastMCP Server

The `FastMCP` class is the primary interface for creating MCP servers:

```python
from mcp.server.fastmcp import FastMCP

# Initialize server
mcp = FastMCP("ServerName")
```

### Tools

Tools are functions that provide functionality, similar to POST endpoints:

```python
@mcp.tool()
def tool_name(param1: type, param2: type) -> return_type:
    """Tool description"""
    # Implementation
    return result
```

### Resources

Resources expose data to LLMs, similar to GET endpoints:

```python
@mcp.resource("resource://{parameter}")
def get_resource(parameter: str) -> str:
    """Resource description"""
    return f"Resource content for {parameter}"
```

## Example Implementation

Here's a complete example of a simple MCP server:

```python
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo")

# Add a calculation tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"
```

## Running the Server

There are two main ways to run an MCP server:

1. Install in Claude Desktop:

```bash
mcp install server.py
```

2. Test with MCP Inspector:

```bash
mcp dev server.py
```

## Best Practices

1. **Type Hints**: Always use type hints for parameters and return values
2. **Docstrings**: Provide clear descriptions for all tools and resources
3. **Error Handling**: Implement proper error handling for robust operation
4. **Resource Naming**: Use descriptive and consistent resource URI patterns
5. **Tool Organization**: Group related tools into logical categories

## Integration with LLM Applications

MCP servers can be integrated with various LLM applications. Common integration patterns:

1. **Direct Connection**:

```python
import mcp
from mcp.client.stdio import stdio_client

server_params = mcp.StdioServerParameters(
    command="python",
    args=["server.py"]
)

async def connect():
    async with stdio_client(server_params) as (read, write):
        async with mcp.ClientSession(read, write) as session:
            # Use session to interact with server
            pass
```

2. **Central Hub Integration**:
   Configure the server in your central hub's configuration file.

## Related Documents

- [[Creating Python MCP Servers]]
- [[MCP Server Architecture]]
- [[Tool Management]]

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [Python MCP SDK GitHub](https://github.com/modelcontextprotocol/python-sdk)
