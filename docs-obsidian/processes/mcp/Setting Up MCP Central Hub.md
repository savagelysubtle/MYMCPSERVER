---
created: 2025-03-28
tags: [mcp, setup, process]
parent: [[Processes MOC]]
---

# Setting Up MCP Central Hub

## Overview

This guide outlines the process for setting up a central hub for managing multiple MCP servers on a Windows system, specifically for Cursor integration.

## Prerequisites

- Node.js (latest LTS version)
- Python 3.8+ with pip
- Git
- Windows 10/11
- Cursor IDE (latest version)

## Project Structure

```
mcpServer/
├── mcp-central-hub/
│   ├── config/             # Configuration files
│   ├── src/                # Source code
│   │   ├── main.js         # Entry point
│   │   ├── servers/        # Server modules
│   │   └── utils/          # Utility functions
│   ├── package.json        # Dependencies
│   └── README.md           # Documentation
└── .cursor/
    └── mcp.json            # Cursor MCP configuration
```

## Step-by-Step Process

### 1. Initialize Project

1. Create project directories
2. Initialize npm project: `npm init -y`
3. Install core dependencies:
   ```bash
   npm install @modelcontextprotocol/sdk dotenv winston
   ```

### 2. Configure Server Registry

1. Create `config/servers.json` to define available servers:
   ```json
   {
     "obsidian": {
       "type": "npm",
       "package": "@smithery/obsidian-mcp",
       "configPath": "config/obsidian.json"
     },
     "sequentialThinking": {
       "type": "npm",
       "package": "mcp-sequentialthinking-tools",
       "configPath": "config/sequential-thinking.json"
     },
     "fileManager": {
       "type": "python",
       "path": "python_servers/file_manager/server.py",
       "configPath": "config/file-manager.json"
     }
   }
   ```

### 3. Implement Central Hub

1. Create main entry point (`src/main.js`)
2. Implement server registry and management
3. Add configuration loading and validation
4. Implement startup script

### 4. Configure Cursor Integration

1. Create `.cursor/mcp.json` with hub configuration:
   ```json
   {
     "mcpServers": {
       "central-hub": {
         "command": "node",
         "args": ["./mcp-central-hub/src/main.js"],
         "env": {}
       }
     }
   }
   ```

### 5. Create Python Tools (if using)

1. Use create-python-server to scaffold Python MCP servers:
   ```bash
   pip install create-python-server
   create-python-server
   ```
2. Implement custom tools in Python

### 6. Test Integration

1. Start Cursor IDE
2. Verify connection to MCP servers
3. Test functionality of each tool

## Troubleshooting

- Check Cursor settings to ensure MCP servers are detected
- Review logs in `logs/` directory for error messages
- Verify path configurations are correct for Windows environment
- Try running servers manually to debug connection issues

## Next Steps

- [[Configuring Obsidian MCP Integration]]
- [[Adding Sequential Thinking Tools]]
- [[Python File Manager Integration]]
- [[Advanced MCP Hub Configuration]]

## References

- [[MCP Central Hub]]
- [[MCP Server Architecture]]
- [[Tool Management]]
