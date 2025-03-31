---
created: 2025-03-30
tags: [mcp, python, sdk, examples]
parent: [[Python SDK Overview]]
---

# Python MCP Implementation Examples

## Project Structure

```
mcp-server/
├── pyproject.toml
└── src/
    └── mcp_server/
        ├── __init__.py
        └── __main__.py
```

## Using the FastMCP Library

### pyproject.toml

```toml
[project]
name = "mcp-server"
version = "0.1.0"
description = "A Model Context Protocol server example"
requires-python = ">=3.10"
dependencies = [
    "fastmcp>=0.4.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

### Basic Server Implementation

```python
from fastmcp import FastMCP

# Create a new server
mcp = FastMCP("Sample MCP Server")

# Add a resource handler
@mcp.resource("sample://text/{text_id}")
def sample_text(text_id: str) -> str:
    """Provides sample text content"""
    return f"This is sample text with ID: {text_id}"

# Add a tool
@mcp.tool()
def echo(message: str) -> str:
    """Echoes a message back to the user"""
    return f"Echo: {message}"

# Add a prompt
@mcp.prompt()
def sample_prompt(topic: str) -> str:
    """A sample prompt template"""
    return f"Please create content about: {topic}"

# Start the server
if __name__ == "__main__":
    mcp.run()
```

## Using the Official Python SDK

### pyproject.toml

```toml
[project]
name = "mcp-server"
version = "0.1.0"
description = "A Model Context Protocol server example"
requires-python = ">=3.10"
dependencies = [
    "mcp>=0.3.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

### Server Implementation

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

# Create a server
server = Server()

# Define a tool collection
tools = ToolCollection(
    "sample_tools",
    "Sample tools for demonstration",
    tools=[
        Tool(
            "echo",
            "Echoes a message back to the user",
            functions=[
                Function(
                    request_schema={
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "The message to echo"}
                        },
                        "required": ["message"]
                    },
                    response_schema={
                        "type": "object",
                        "properties": {
                            "result": {"type": "string"}
                        }
                    }
                )
            ]
        )
    ]
)

# Define resource handler
def handle_sample_resource(uri):
    text_id = uri.split("/")[-1]
    return {
        "contents": [
            {
                "uri": uri,
                "mimeType": "text/plain",
                "text": f"This is sample text with ID: {text_id}"
            }
        ]
    }

# Define tool handler
async def handle_echo(request):
    message = request.get("message", "")
    return {"result": f"Echo: {message}"}

# Register handlers
server.register_tool_collection(tools)
server.register_handler("sample_tools.echo", handle_echo)
server.register_resource_handler("sample://text/", handle_sample_resource)

# Create server factory
def create_server():
    return server

# Start server if executed directly
if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import run_server

    asyncio.run(run_server(create_server()))
```

## Advanced Examples

### Stateful Server

```python
from fastmcp import FastMCP

mcp = FastMCP("Stateful Server")

# In-memory state
notes = {}

@mcp.tool()
def save_note(title: str, content: str) -> str:
    """Save a note with a title"""
    notes[title] = content
    return f'Note "{title}" saved successfully.'

@mcp.tool()
def get_note(title: str) -> str:
    """Retrieve a note by title"""
    if title not in notes:
        return f'Note "{title}" not found.'
    return notes[title]

if __name__ == "__main__":
    mcp.run()
```

### External API Integration

```python
from fastmcp import FastMCP
import aiohttp
import asyncio

mcp = FastMCP("Weather API Server")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather information for a location"""
    try:
        # Note: This is a placeholder. Use a real weather API in production
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://weather-api.example.com/forecast?q={location}") as response:
                data = await response.json()
                return f"Weather for {location}: {data['temperature']}°C, {data['conditions']}"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

if __name__ == "__main__":
    mcp.run()
```

## Related Documentation

### Implementation Guides

- [[../development/Implementation Guide|General Implementation Guide]]
- [[Python Server Development|Server Development Guide]]
- [[Python Tool Implementation|Tool Implementation Guide]]

### Project Examples

- [[../../projects/myMcpServer/implementation/Server Configuration|Server Configuration]]
- [[../../projects/myMcpServer/mcpPlanning/final/python/tool-server|Tool Server Example]]

## External References

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Library](https://github.com/jlowin/fastmcp)

---

[[Python SDK Overview|← Back to Python SDK Overview]]
