---
created: 2024-03-29
updated: 2025-03-30
tags: [mcp, tools, sequential-thinking, integration]
parent: [[../_index]]
up: [[_index]]
siblings: [[Cursor Integration]], [[Cursor MCP Integration]]
---

# Sequential Thinking Tools Integration

## Overview

The MCP Sequential Thinking Tools is a specialized server that helps break down complex problems into manageable steps and provides intelligent tool recommendations for each stage of problem-solving.

## Features

- Dynamic problem-solving through sequential thoughts
- Intelligent tool recommendations
- Confidence scoring for suggestions
- Detailed rationale for recommendations
- Progress tracking
- Support for branching and revision

## Installation

The server is configured in the MCP configuration file (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "mcp-sequentialthinking-tools": {
      "command": "powershell.exe",
      "args": [
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        "npx -y mcp-sequentialthinking-tools"
      ]
    }
  }
}
```

## Usage

The server provides a single tool `sequentialthinking_tools` with the following parameters:

- `thought` (string, required): Current thinking step
- `next_thought_needed` (boolean): Whether another step is needed
- `thought_number` (integer): Current thought number
- `total_thoughts` (integer): Estimated total thoughts needed
- `is_revision` (boolean): Whether this revises previous thinking
- `current_step` (object): Current step recommendation

### Example Response

```json
{
  "thought": "Initial research step",
  "current_step": {
    "step_description": "Gather initial information",
    "expected_outcome": "Clear understanding of concept",
    "recommended_tools": [
      {
        "tool_name": "search_docs",
        "confidence": 0.9,
        "rationale": "Search documentation for information",
        "priority": 1
      }
    ]
  }
}
```

## Implementation Examples

For implementation examples, see:

- [[../../projects/myMcpServer/mcpPlanning/final/core/overview-v2|Core Implementation]]
- [[../../projects/myMcpServer/mcpPlanning/final/transport/overview-v2|Transport Layer]]

## Related Documentation

### Core Concepts

- [[../core/Tool Management|Tool Management]] - Tool management system
- [[../core/MCP Server Architecture|MCP Server Architecture]] - Server architecture

### Reference

- [[../reference/MCP Servers List|MCP Servers List]] - Available MCP servers
- [[../pythonSDK/Python SDK Overview|Python MCP SDK]] - SDK documentation

### Configuration

- [[../development/Configuration Examples|Configuration Examples]]
- [[../development/MCP Hub Implementation|Hub Implementation]]

## External References

- [Sequential Thinking Tools Repository](https://github.com/spences10/mcp-sequentialthinking-tools)
- [Model Context Protocol](https://modelcontextprotocol.io)

---

[[../_index|← Back to MCP Knowledge]]
