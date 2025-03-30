---
created: 2025-03-28
tags: reference, mcp, servers
parent: [[Reference MOC]]
---

# MCP Server List

## Overview

This reference compiles popular Model Context Protocol (MCP) servers compatible with Cursor IDE, categorized by their primary functionality. Each entry includes installation commands, basic configuration information, and relevant links.

## Key Points

- Comprehensive list of popular MCP servers for Cursor IDE
- Categorized by primary functionality
- Includes installation commands and basic configuration
- Features both official and community-created servers
- Updated as of March 28, 2025

## Details

### Knowledge Management

| Server Name           | Description                                                  | Installation                                            |
| --------------------- | ------------------------------------------------------------ | ------------------------------------------------------- |
| **Obsidian MCP**      | Connects Cursor to Obsidian vaults for knowledge base access | `npm install obsidian-mcp`                              |
| **File System**       | Provides file system access capabilities                     | `npx -y @modelcontextprotocol/server-fs`                |
| **Document Analysis** | Analyzes PDFs, Word docs, and other document formats         | `npx -y @modelcontextprotocol/server-document-analysis` |
| **Notion**            | Integrates with Notion workspaces                            | `npx -y @modelcontextprotocol/server-notion`            |

### Search & Research

| Server Name         | Description                                           | Installation                                                                    |
| ------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------- |
| **Brave Search**    | Provides web search capabilities via Brave API        | `env BRAVE_API_KEY=[your-key] npx -y @modelcontextprotocol/server-brave-search` |
| **Puppeteer**       | Enables web browsing and scraping                     | `npx -y @modelcontextprotocol/server-puppeteer`                                 |
| **Web Archive**     | Searches internet archives for historical information | `npx -y @modelcontextprotocol/server-web-archive`                               |
| **Research Papers** | Searches academic papers and research publications    | `npx -y @modelcontextprotocol/server-research-papers`                           |

### Development Tools

| Server Name             | Description                                         | Installation                                              |
| ----------------------- | --------------------------------------------------- | --------------------------------------------------------- |
| **Sequential Thinking** | Breaks down complex problems into manageable steps  | `npx -y @modelcontextprotocol/server-sequential-thinking` |
| **GitHub**              | Interacts with GitHub repositories, issues, and PRs | `npx -y @modelcontextprotocol/server-github`              |
| **Kubernetes**          | Manages Kubernetes clusters and resources           | `npx -y @modelcontextprotocol/server-kubernetes`          |
| **Code Analyzer**       | Performs static code analysis and quality checking  | `npx -y @modelcontextprotocol/server-code-analyzer`       |
| **Docker**              | Manages Docker containers and images                | `npx -y @modelcontextprotocol/server-docker`              |

### AI Enhancement

| Server Name      | Description                                            | Installation                                       |
| ---------------- | ------------------------------------------------------ | -------------------------------------------------- |
| **MCP Reasoner** | Provides advanced reasoning capabilities               | `npx -y @modelcontextprotocol/server-mcp-reasoner` |
| **MCTS**         | Implements Monte Carlo Tree Search for decision-making | `npx -y @modelcontextprotocol/server-mcts`         |
| **Memory**       | Long-term memory and knowledge retrieval               | `npx -y @modelcontextprotocol/server-memory`       |
| **Multi-Agent**  | Coordinates multiple specialized agents                | `npx -y multi-agent-with-mcp`                      |

### Database & API

| Server Name    | Description                                | Installation                                     |
| -------------- | ------------------------------------------ | ------------------------------------------------ |
| **SQL Server** | Connects to Microsoft SQL Server databases | `npx -y mssql-mcp-server`                        |
| **MongoDB**    | Interacts with MongoDB databases           | `npx -y @modelcontextprotocol/server-mongodb`    |
| **PostgreSQL** | Manages PostgreSQL databases               | `npx -y @modelcontextprotocol/server-postgresql` |
| **REST API**   | Creates and tests REST APIs                | `npx -y @modelcontextprotocol/server-rest-api`   |

### Configuration Examples

#### Obsidian MCP

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "obsidian-mcp", "D:/path/to/your/vault"]
    }
  }
}
```

#### Sequential Thinking

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

#### Brave Search

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Related Notes

- [[MCP Central Hub]] - Setting up a central hub for multiple MCP servers
- [[MCP Architecture]] - Understanding MCP architecture and components
- [[Cursor MCP Integration]] - How Cursor integrates with MCP

## References

- [MCP Servers Hub](https://github.com/apappascs/mcp-servers-hub)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [HiMCP - MCP Server Directory](https://himcp.ai/)

---

_This note belongs to the [[Reference MOC]]_
