# To install obsidian mcp to python fullserverhub

Installation
Install the Smithery and MCP SDKs using pip:
pip install smithery mcp
Python SDK
Use Smithery's Python SDK to connect to this MCP server:
import mcp
from mcp.client.stdio import stdio_client

# Create server parameters for stdio connection

server_params = mcp.StdioServerParameters(
command="python", # Executable
args=["your_server.py"] # Arguments
)

async def main(): # Connect to the server using stdio client
async with stdio_client(server_params) as (read, write):
async with mcp.ClientSession(read, write) as session: # List available tools
tools_list = await session.list_tools()
print(f"Available tools: {', '.join([t.name for t in tools_list.tools])}")

            # Example: Call a tool
            # result = await session.call_tool("tool-name", arguments={"param1": "value1"})

Configuration Schema
Full JSON Schema for server configuration:
{
"type": "object",
"required": [
"vaultPath"
],
"properties": {
"vaultPath": {
"type": "string",
"description": "The path to your Obsidian vault."
}
}
}
