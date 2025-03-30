---
created: 2025-03-28
tags: [mcp, implementation, reference, code]
parent: [[Reference MOC]]
---

# MCP Hub Implementation

## Overview

This document provides a reference implementation for an MCP Central Hub using Node.js, including key code components and configuration structures. This implementation serves as a starting point for building a custom MCP hub.

## Directory Structure

```
mcp-central-hub/
├── config/
│   ├── config.json           # Main configuration
│   ├── obsidian.json         # Obsidian MCP configuration
│   ├── sequential.json       # Sequential thinking configuration
│   └── filemanager.json      # File manager configuration
├── src/
│   ├── main.js               # Entry point
│   ├── config.js             # Configuration manager
│   ├── logger.js             # Logging utilities
│   ├── server-manager.js     # Server orchestration
│   ├── tool-registry.js      # Tool metadata management
│   └── servers/              # Server-specific implementations
│       ├── obsidian.js       # Obsidian MCP integration
│       ├── sequential.js     # Sequential thinking integration
│       └── filemanager.js    # Python file manager integration
├── package.json              # Dependencies and scripts
└── README.md                 # Documentation
```

## Key Component Implementations

### Main Entry Point (main.js)

```javascript
const { loadConfig } = require('./config');
const { initLogger } = require('./logger');
const ServerManager = require('./server-manager');
const ToolRegistry = require('./tool-registry');

async function start() {
  // Load configuration
  const config = loadConfig();

  // Initialize logger
  const logger = initLogger(config.logLevel, config.logFile);

  // Initialize tool registry
  const toolRegistry = new ToolRegistry();

  // Initialize server manager
  const serverManager = new ServerManager(config, logger, toolRegistry);

  // Start servers
  try {
    await serverManager.startServers();
    logger.info('MCP Central Hub started successfully');
  } catch (error) {
    logger.error(`Failed to start MCP Central Hub: ${error.message}`);
    process.exit(1);
  }

  // Handle shutdown
  process.on('SIGINT', async () => {
    logger.info('Shutting down MCP Central Hub...');
    await serverManager.stopServers();
    process.exit(0);
  });
}

// Start the hub
start();
```

### Server Manager (server-manager.js)

```javascript
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs').promises;

class ServerManager {
  constructor(config, logger, toolRegistry) {
    this.config = config;
    this.logger = logger;
    this.toolRegistry = toolRegistry;
    this.servers = {};
  }

  async startServers() {
    const { servers } = this.config;

    for (const [id, serverConfig] of Object.entries(servers)) {
      if (!serverConfig.enabled) {
        this.logger.info(`Server ${id} is disabled, skipping`);
        continue;
      }

      try {
        // Load server-specific configuration
        const configPath = path.resolve(serverConfig.configPath);
        const serverConfigData = JSON.parse(
          await fs.readFile(configPath, 'utf8'),
        );

        // Start the appropriate server type
        const serverImpl = require(`./servers/${id}`);
        const server = await serverImpl.startServer(
          serverConfigData,
          this.logger,
        );

        // Register server and its tools
        this.servers[id] = server;
        await this.toolRegistry.registerToolsFromServer(id, server);

        this.logger.info(`Started server: ${id}`);
      } catch (error) {
        this.logger.error(`Failed to start server ${id}: ${error.message}`);
      }
    }

    this.logger.info(`Started ${Object.keys(this.servers).length} servers`);
  }

  async stopServers() {
    for (const [id, server] of Object.entries(this.servers)) {
      try {
        await server.stop();
        this.logger.info(`Stopped server: ${id}`);
      } catch (error) {
        this.logger.error(`Error stopping server ${id}: ${error.message}`);
      }
    }
  }
}

module.exports = ServerManager;
```

### Tool Registry (tool-registry.js)

```javascript
class ToolRegistry {
  constructor() {
    this.tools = new Map();
    this.serverTools = new Map();
  }

  async registerToolsFromServer(serverId, server) {
    const tools = await server.getTools();

    // Track which tools belong to which server
    this.serverTools.set(
      serverId,
      tools.map((t) => t.name),
    );

    // Register each tool
    for (const tool of tools) {
      this.tools.set(tool.name, {
        ...tool,
        serverId,
      });
    }

    return tools.length;
  }

  getToolsByCategory(category) {
    return Array.from(this.tools.values()).filter(
      (tool) => tool.category === category,
    );
  }

  getToolsFromServer(serverId) {
    const toolNames = this.serverTools.get(serverId) || [];
    return toolNames.map((name) => this.tools.get(name));
  }

  getAllTools() {
    return Array.from(this.tools.values());
  }
}

module.exports = ToolRegistry;
```

### Obsidian Server Integration (servers/obsidian.js)

```javascript
const { spawn } = require('child_process');

async function startServer(config, logger) {
  const { vaultPath } = config;

  if (!vaultPath) {
    throw new Error('Vault path is required for Obsidian MCP');
  }

  logger.info(`Starting Obsidian MCP server with vault: ${vaultPath}`);

  // Prepare config argument
  const configArg = JSON.stringify({ vaultPath });

  // Start the server process
  const process = spawn(
    'npx',
    [
      '-y',
      '@smithery/cli@latest',
      'run',
      'obsidian-mcp',
      '--config',
      configArg,
    ],
    {
      stdio: ['pipe', 'pipe', 'pipe'],
    },
  );

  // Handle process output
  process.stdout.on('data', (data) => {
    logger.info(`[obsidian] ${data.toString().trim()}`);
  });

  process.stderr.on('data', (data) => {
    logger.error(`[obsidian] ${data.toString().trim()}`);
  });

  // Handle process exit
  process.on('exit', (code) => {
    if (code !== 0) {
      logger.error(`Obsidian MCP exited with code ${code}`);
    }
  });

  // Return server interface
  return {
    process,

    async getTools() {
      // Static tool definitions
      return [
        {
          name: 'get_notes',
          description: 'Retrieve note content by title or path',
          category: 'knowledge',
        },
        {
          name: 'search_notes',
          description: 'Search for notes by content',
          category: 'knowledge',
        },
        {
          name: 'list_notes',
          description: 'List available notes in the vault',
          category: 'knowledge',
        },
      ];
    },

    async stop() {
      process.kill();
    },
  };
}

module.exports = { startServer };
```

### Python File Manager Integration (servers/filemanager.js)

```javascript
const { spawn } = require('child_process');
const path = require('path');

async function startServer(config, logger) {
  const { scriptPath } = config;

  if (!scriptPath) {
    throw new Error('Script path is required for File Manager MCP');
  }

  logger.info(`Starting File Manager MCP server with script: ${scriptPath}`);

  // Start the Python server process
  const process = spawn('python', [scriptPath], {
    stdio: ['pipe', 'pipe', 'pipe'],
    env: {
      ...process.env,
      ...config.env,
    },
  });

  // Handle process output
  process.stdout.on('data', (data) => {
    logger.info(`[filemanager] ${data.toString().trim()}`);
  });

  process.stderr.on('data', (data) => {
    logger.error(`[filemanager] ${data.toString().trim()}`);
  });

  // Return server interface
  return {
    process,

    async getTools() {
      // Static tool definitions
      return [
        {
          name: 'organize_files',
          description: 'Organize files by type, date, or custom rules',
          category: 'file-management',
        },
        {
          name: 'find_duplicates',
          description: 'Find and manage duplicate files',
          category: 'file-management',
        },
        {
          name: 'analyze_storage',
          description: 'Analyze storage usage by folder or file type',
          category: 'file-management',
        },
      ];
    },

    async stop() {
      process.kill();
    },
  };
}

module.exports = { startServer };
```

## Package.json

```json
{
  "name": "mcp-central-hub",
  "version": "0.1.0",
  "description": "Central hub for managing multiple MCP servers",
  "main": "src/main.js",
  "scripts": {
    "start": "node src/main.js",
    "dev": "nodemon src/main.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.1.0",
    "dotenv": "^16.3.1",
    "winston": "^3.11.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

## Configuration Examples

### Main Configuration (config/config.json)

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
    "sequential": {
      "enabled": true,
      "configPath": "config/sequential.json"
    },
    "filemanager": {
      "enabled": true,
      "configPath": "config/filemanager.json"
    }
  }
}
```

### Obsidian Configuration (config/obsidian.json)

```json
{
  "vaultPath": "C:/Users/username/Documents/Obsidian Vault",
  "maxSearchResults": 10,
  "cacheResults": true
}
```

### File Manager Configuration (config/filemanager.json)

```json
{
  "scriptPath": "python_servers/file_manager/server.py",
  "rootDirectory": "C:/Users/username/Documents",
  "env": {
    "PYTHONPATH": "${workspaceFolder}/python_servers"
  }
}
```

## Related References

- [[MCP Central Hub]]
- [[Setting Up MCP Central Hub]]
- [[MCP Server Architecture]]
- [[Configuration Examples]]
