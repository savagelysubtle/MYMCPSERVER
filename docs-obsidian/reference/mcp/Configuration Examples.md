---
created: 2025-03-28
tags: [mcp, configuration, reference]
parent: [[Reference MOC]]
---

# MCP Configuration Examples

## Overview

This reference document provides examples of configuration files for various MCP server setups, including project-specific configurations, global configurations, and central hub implementations.

## Cursor Configuration Examples

### Basic Project Configuration

**.cursor/mcp.json**

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "brave-search": {
      "command": "env",
      "args": [
        "BRAVE_API_KEY=your-key-here",
        "npx",
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ]
    }
  }
}
```

### Global Configuration

**~/.cursor/mcp.json (Windows: %USERPROFILE%\.cursor\mcp.json)**

```json
{
  "mcpServers": {
    "obsidian-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "@smithery/cli@latest",
        "run",
        "obsidian-mcp",
        "--config",
        "{\"vaultPath\":\"C:/Users/username/Documents/Obsidian Vault\"}"
      ]
    },
    "sequentialThinking": {
      "command": "npx",
      "args": [
        "-y",
        "@smithery/cli@latest",
        "run",
        "sequential-thinking",
        "--config",
        "{}"
      ]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:/Users/username/Documents"
      ]
    }
  }
}
```

### WSL Configuration Example

**For Windows users running Node.js in WSL**

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "wsl.exe",
      "args": [
        "bash",
        "-c",
        "source ~/.nvm/nvm.sh && /home/username/.nvm/versions/node/v20.12.1/bin/npx -y mcp-sequentialthinking-tools"
      ]
    }
  }
}
```

### Python Server Configuration

```json
{
  "mcpServers": {
    "python-server": {
      "command": "python",
      "args": ["-m", "my_server"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

## Central Hub Configuration Examples

### Hub Configuration File

**mcp-central-hub/config/config.json**

```json
{
  "port": 3000,
  "logLevel": "info",
  "logFile": "logs/hub.log",
  "servers": {
    "obsidian": {
      "enabled": true,
      "configPath": "config/obsidian.json"
    },
    "sequentialThinking": {
      "enabled": true,
      "configPath": "config/sequential-thinking.json"
    },
    "fileManager": {
      "enabled": true,
      "configPath": "config/file-manager.json"
    }
  }
}
```

### Server-Specific Configuration

**mcp-central-hub/config/obsidian.json**

```json
{
  "vaultPath": "C:/Users/username/Documents/Obsidian Vault",
  "maxSearchResults": 10,
  "cacheResults": true
}
```

### Hub Integration with Cursor

**.cursor/mcp.json**

```json
{
  "mcpServers": {
    "central-hub": {
      "command": "node",
      "args": ["./mcp-central-hub/src/main.js"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

## Claude Desktop Configuration Examples

**~/Library/Application Support/Claude/claude_desktop_config.json (macOS)**
**%APPDATA%/Claude/claude_desktop_config.json (Windows)**

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/username/Documents"
      ]
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

## Related References

- [[MCP Servers List]]
- [[Setting Up MCP Central Hub]]
- [[Configuring Cursor MCP Integration]]
- [[MCP Server Architecture]]
