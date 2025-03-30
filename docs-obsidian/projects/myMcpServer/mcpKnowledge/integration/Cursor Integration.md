---
created: 2025-03-28
updated: 2025-03-30
tags: [mcp, cursor, integration]
parent: [[../MCP Knowledge MOC]]
---

# Cursor MCP Integration

## Overview

Cursor IDE integrates with the Model Context Protocol (MCP) to extend its AI capabilities beyond the built-in functions. This integration allows Cursor to communicate with external tools and services through standardized interfaces, enabling more powerful and specialized AI-assisted coding workflows.

## Key Points

- Cursor supports MCP servers via both stdio and HTTP/SSE protocols
- Configuration happens through Cursor Settings > Features > MCP Servers
- Server tools appear in the available tools section when properly configured
- Cursor automatically suggests relevant MCP tools based on task context
- Current limitations include a maximum of ~40 tools per configuration

## Integration Methods

### 1. Local Process (stdio)

Cursor can spawn local processes and communicate with them through standard input/output streams. This is the most common method for integrating locally-running MCP servers. Configuration requires:

- Command: The executable to run (e.g., `npx`, `python`, `node`)
- Arguments: Command-line arguments to pass to the process
- Environment variables: Any environment variables needed by the server

### 2. Remote Server (HTTP/SSE)

Cursor can connect to remote servers using HTTP and Server-Sent Events (SSE). This allows integration with networked services and third-party APIs. Configuration requires:

- URL: The endpoint of the MCP server
- Optional authentication credentials

## Configuration Process

1. Open Cursor Settings (Ctrl+,)
2. Navigate to Features > MCP Servers
3. Click "Add New MCP Server"
4. Enter server details (name, command/URL, arguments, environment variables)
5. Save the configuration
6. Restart Cursor to apply changes

## Usage Patterns

Once configured, Cursor's AI assistant can access MCP server tools in several ways:

1. **Automatic Tool Selection**: Cursor analyzes the current task and suggests appropriate tools
2. **Explicit Tool Invocation**: Users can specify which tool to use for a particular task
3. **Tool Chaining**: Multiple tools can be used in sequence to accomplish complex tasks

## Current Limitations

1. **Tool Limit**: Cursor can only handle approximately 40 MCP tools at once
2. **Configuration Complexity**: Each server must be configured individually
3. **Restart Required**: Changes to MCP server configuration require a Cursor restart
4. **Tool Discovery**: Limited mechanisms for discovering available tools
5. **Performance Impact**: Many active MCP servers can impact Cursor's performance

## Project-Specific Configuration

Cursor supports project-specific MCP configurations through the `.cursor/mcp.json` file. This allows different projects to use different sets of MCP servers based on their specific requirements.

Example `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "project-specific-server": {
      "command": "npx",
      "args": ["-y", "project-specific-mcp-server"]
    }
  }
}
```

## Related Documentation

### Core Concepts

- [[../core/MCP Architecture|MCP Architecture]] - Details of the underlying protocol
- [[../core/MCP Central Hub|MCP Central Hub]] - Managing multiple MCP servers
- [[../core/Remote Servers|Remote Servers]] - Working with remote MCP servers

### Implementation

- [[../development/Hub Configuration|Hub Configuration]]
- [[../development/Hub Setup Guide|Setup Guide]]
- [[../../projects/myMcpServer/implementation/Server Configuration|Server Configuration]]

### Reference

- [[../reference/MCP Servers List|Available MCP Servers]]

## External References

- [Cursor MCP Documentation](https://docs.cursor.com/context/model-context-protocol)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Cursor MCP Forum Discussions](https://forum.cursor.com/t/mcp-install-config-and-management-suggestions/49283)

---

[[../MCP Knowledge MOC|← Back to MCP Knowledge]]
