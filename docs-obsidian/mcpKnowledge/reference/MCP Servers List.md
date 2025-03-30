---
created: 2025-03-28
updated: 2025-03-30
tags: [mcp, reference, servers, tools]
parent: [[../MCP Knowledge MOC]]
---

# MCP Servers List

## Overview

This reference document catalogs MCP servers relevant to the central hub implementation, including information about their purpose, installation methods, and configuration options.

## Core Servers

### 1. Obsidian MCP

**Repository**: [smithery-ai/mcp-obsidian](https://github.com/smithery-ai/mcp-obsidian)
**Description**: Connects to Obsidian vaults, allowing AI to read, search, and explore notebook content.
**Installation**:

```bash
npx @smithery/cli@latest run obsidian-mcp --config {"vaultPath":"/path/to/vault"}
```

**Tools Provided**:

- `get_notes`: Retrieve note content by title or path
- `search_notes`: Search for notes by content
- `list_notes`: List available notes in the vault
- `get_backlinks`: Get notes linking to a specific note

### 2. Sequential Thinking Tools

**Repository**: [spences10/mcp-sequentialthinking-tools](https://github.com/spences10/mcp-sequentialthinking-tools)
**Description**: Provides structured thinking capabilities with tool recommendations for each step.
**Installation**:

```bash
npx -y mcp-sequentialthinking-tools
```

**Tools Provided**:

- `sequentialthinking_tools`: Break down complex problems with tool recommendations

### 3. File Management (Python)

**Description**: Custom Python MCP server for file management operations.
**Installation**: Created using create-python-server
**Tools Provided**:

- Custom file management tools

### 4. Model Context Protocol Sequential Thinking

**Repository**: [@modelcontextprotocol/server-sequential-thinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)
**Description**: Official sequential thinking implementation from Model Context Protocol.
**Installation**:

```bash
npx -y @modelcontextprotocol/server-sequential-thinking
```

**Tools Provided**:

- `sequential_thinking`: Dynamic problem-solving through thought sequences

## Additional Useful Servers

### 5. Brave Search

**Repository**: [@modelcontextprotocol/server-brave-search](https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search)
**Description**: Web search capabilities using Brave Search API.
**Installation**:

```bash
env BRAVE_API_KEY=your-key-here npx -y @modelcontextprotocol/server-brave-search
```

**Tools Provided**:

- `web_search`: Search the web for information

### 6. Puppeteer

**Repository**: [@modelcontextprotocol/server-puppeteer](https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer)
**Description**: Browser automation for web scraping and testing.
**Installation**:

```bash
npx -y @modelcontextprotocol/server-puppeteer
```

**Tools Provided**:

- `browse`: Navigate to a URL
- `scroll`: Scroll the page
- `click`: Click on elements
- `type`: Type into input fields
- `screenshot`: Take screenshots

### 7. Filesystem

**Repository**: [@modelcontextprotocol/server-filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
**Description**: Provides access to the local filesystem.
**Installation**:

```bash
npx -y @modelcontextprotocol/server-filesystem /path/to/directory
```

**Tools Provided**:

- `read_file`: Read file contents
- `write_file`: Write to files
- `list_directory`: List files in directory
- `delete_file`: Remove files

## Related Documentation

### Core Concepts

- [[../core/MCP Central Hub|MCP Central Hub]] - Central hub architecture
- [[../core/MCP Server Architecture|MCP Server Architecture]] - Server architecture
- [[../core/Tool Management|Tool Management]] - Tool management system

### Implementation

- [[../development/MCP Hub Implementation|Hub Implementation Guide]]
- [[../development/Configuration Examples|Configuration Examples]]

### Integration

- [[../integration/cursor-mcp-integration|Cursor Integration Guide]]
- [[../../projects/myMcpServer/implementation/Server Configuration|Server Configuration Guide]]

## External References

- [MCP Servers Hub](https://github.com/apappascs/mcp-servers-hub)
- [Model Context Protocol](https://modelcontextprotocol.io)

---

[[../MCP Knowledge MOC|← Back to MCP Knowledge]]
