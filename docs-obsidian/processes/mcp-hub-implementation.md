---
created: 2025-03-28
tags: process, mcp, implementation
parent: [[Processes MOC]]
---

# MCP Hub Implementation Process

## Overview

This process documents the implementation of the MCP Central Hub, a unified system for managing multiple MCP servers within a single structure. The hub integrates various MCP servers including Obsidian knowledge management, sequential thinking tools, and a custom file manager.

## Key Points

- Provides a centralized configuration system for multiple MCP servers
- Implements a PowerShell startup script for unified server management
- Creates a custom Python-based file management MCP server
- Integrates with existing Node.js MCP servers (Obsidian and Sequential Thinking)
- Offers command-line interface for server control

## Details

### Project Structure

The MCP Central Hub is organized with the following directory structure:

```
/src/mcpServer/
├── config/               # Configuration files
│   └── hub-config.json   # Main configuration
├── servers/              # Server implementations
│   ├── node/             # Node.js-based servers
│   │   ├── obsidian/     # Obsidian MCP integration
│   │   └── sequential/   # Sequential thinking tools
│   └── python/           # Python-based servers
│       └── filemanager/  # Custom file management
├── scripts/              # Management scripts
│   └── start-hub.ps1     # Main startup script
├── utils/                # Utility functions
│   ├── server_manager.py # Server management
│   └── __init__.py       # Package initialization
├── logs/                 # Log files directory
├── main.py               # Python entry point
└── __init__.py           # Package initialization
```

### Implementation Components

#### 1. Configuration System

The central configuration file (`hub-config.json`) defines all server settings:

```json
{
  "servers": {
    "obsidian": {
      "type": "node",
      "package": "mcp-obsidian",
      "args": ["D:/Coding/Python_Projects/mcpServer/docs-obsidian"],
      "enabled": true
    },
    "sequentialThinking": {
      "type": "node",
      "package": "@spences10/mcp-sequentialthinking-tools",
      "enabled": true
    },
    "fileManager": {
      "type": "python",
      "path": "./servers/python/filemanager",
      "enabled": true
    }
  },
  "startup": {
    "autoStart": true,
    "startOrder": ["obsidian", "sequentialThinking", "fileManager"]
  },
  "logging": {
    "path": "./logs",
    "level": "info"
  }
}
```

This configuration:

- Defines three MCP servers (Obsidian, Sequential Thinking, and File Manager)
- Specifies their type, package information, and arguments
- Sets the startup order and logging options

#### 2. PowerShell Startup Script

The startup script (`start-hub.ps1`) manages server launching:

```powershell
param (
    [string]$configPath = (Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) "config\hub-config.json")
)

# Load configuration
$configFullPath = Resolve-Path $configPath
$config = Get-Content -Path $configFullPath | ConvertFrom-Json

# Set up logging
$baseDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$logPath = Join-Path $baseDir "logs"
if (!(Test-Path $logPath)) {
    New-Item -ItemType Directory -Path $logPath | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"
$logFile = Join-Path -Path $logPath -ChildPath "mcp-hub-$timestamp.log"

function Write-Log {
    param (
        [string]$message
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $message" | Tee-Object -FilePath $logFile -Append
}

# Function to start a server
function Start-McpServer {
    param (
        [string]$name,
        [PSCustomObject]$serverConfig
    )

    Write-Log "Starting $name server..."

    if ($serverConfig.type -eq "node") {
        $processArgs = @(
            "-y",
            $serverConfig.package
        )

        if ($serverConfig.args) {
            $processArgs += $serverConfig.args
        }

        Start-Process -FilePath "npx" -ArgumentList $processArgs -NoNewWindow
        Write-Log "Started Node.js server: $name"
    }
    elseif ($serverConfig.type -eq "python") {
        $pythonPath = Join-Path $baseDir $serverConfig.path
        if (Test-Path $pythonPath) {
            $currentDir = Get-Location
            Set-Location -Path $pythonPath
            Start-Process -FilePath "python" -ArgumentList "-m", "main" -NoNewWindow
            Set-Location -Path $currentDir
            Write-Log "Started Python server: $name"
        } else {
            Write-Log "Error: Python server path not found: $pythonPath"
        }
    }
}

# Start servers in the specified order
Write-Log "Starting MCP Central Hub..."
foreach ($serverName in $config.startup.startOrder) {
    $serverConfig = $config.servers.$serverName

    if ($serverConfig.enabled) {
        Start-McpServer -name $serverName -serverConfig $serverConfig
    }
}

Write-Log "All MCP servers started!"
```

Key features:

- Detects and loads the configuration file
- Sets up logging with timestamps
- Dynamically starts different types of MCP servers
- Handles different server types (Node.js vs Python)

#### 3. Python Server Manager

The `server_manager.py` module provides a programmatic interface for controlling servers:

```python
import json
import os
import subprocess
import logging
from pathlib import Path

class ServerManager:
    """Utility class to manage MCP servers programmatically"""

    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.base_dir = self.config_path.parent.parent
        self.load_config()
        self.processes = {}
        self.setup_logging()

    def load_config(self):
        """Load the hub configuration file"""
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

        self.log_path = Path(self.base_dir) / self.config.get('logging', {}).get('path', 'logs')
        self.log_path.mkdir(exist_ok=True)

    def setup_logging(self):
        """Set up logging for the server manager"""
        log_level = getattr(logging, self.config.get('logging', {}).get('level', 'INFO').upper())
        logging.basicConfig(
            filename=self.log_path / 'server-manager.log',
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('ServerManager')

    def start_server(self, name):
        """Start a specific server by name"""
        # Implementation details...

    def start_all(self):
        """Start all enabled servers in the specified order"""
        # Implementation details...

    def stop_server(self, name):
        """Stop a specific server by name"""
        # Implementation details...

    def stop_all(self):
        """Stop all running servers"""
        # Implementation details...
```

#### 4. File Management MCP Server

The custom Python-based file management server (`main.py`):

```python
from mcp import (
    Server,
    Tool,
    Function,
    ToolCollection,
    ResourceType,
)
import os
import json
import aiofiles
from typing import List, Dict, Any, Optional
from datetime import datetime

# Define tools for file operations
file_tools = ToolCollection(
    "file_management",
    "Tools for managing local files and directories",
    tools=[
        Tool(
            "list_directory",
            "List files and directories in the specified path",
            functions=[
                # Function schema definition...
            ]
        ),
        Tool(
            "read_file",
            "Read the contents of a file",
            functions=[
                # Function schema definition...
            ]
        ),
        Tool(
            "write_file",
            "Write content to a file",
            functions=[
                # Function schema definition...
            ]
        ),
        Tool(
            "search_files",
            "Search for files matching a pattern",
            functions=[
                # Function schema definition...
            ]
        )
    ]
)

# Implement handlers for the tools
async def handle_list_directory(request):
    # Implementation details...

async def handle_read_file(request):
    # Implementation details...

async def handle_write_file(request):
    # Implementation details...

async def handle_search_files(request):
    # Implementation details...

# Initialize server with handlers
def create_server():
    server = Server()

    # Register the tool collection
    server.register_tool_collection(file_tools)

    # Register handlers
    server.register_handler("file_management.list_directory", handle_list_directory)
    server.register_handler("file_management.read_file", handle_read_file)
    server.register_handler("file_management.write_file", handle_write_file)
    server.register_handler("file_management.search_files", handle_search_files)

    return server

# Start server if executed directly
if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import run_server

    asyncio.run(run_server(create_server()))
```

This server implements file management operations:

- Listing directory contents
- Reading file contents
- Writing to files
- Searching for files by pattern

#### 5. Command-Line Interface

The main Python entry point (`main.py`) provides a CLI for managing the hub:

```python
#!/usr/bin/env python3
"""
MCP Central Hub - Main entry point

This module provides a central manager for multiple MCP servers,
including Obsidian, Sequential Thinking, and File Management servers.
"""

import sys
import os
import argparse
from pathlib import Path
from utils.server_manager import ServerManager

def main():
    """Main entry point for the MCP Central Hub"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='MCP Central Hub Manager')
    parser.add_argument('--config', type=str, default='config/hub-config.json',
                        help='Path to configuration file')
    parser.add_argument('--action', type=str, choices=['start', 'stop', 'restart'],
                        default='start', help='Action to perform')
    parser.add_argument('--server', type=str, help='Specific server to act on')

    # Implementation details...
```

### Cursor MCP Integration

The hub is integrated with Cursor IDE through the `.cursor/mcp.json` configuration:

```json
{
  "mcpServers": {
    "mcp-central-hub": {
      "command": "powershell.exe",
      "args": [
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "D:/Coding/Python_Projects/mcpServer/src/mcpServer/scripts/start-hub.ps1"
      ]
    }
  }
}
```

This tells Cursor to:

- Run the MCP Central Hub's startup script when connecting to MCP servers
- Bypass PowerShell execution policy restrictions
- Use the absolute path to the script file

## Related Notes

- [[MCP Central Hub]] - Conceptual overview of the central hub architecture
- [[MCP Technical Implementation]] - Technical details and code examples
- [[MCP Server List]] - Reference list of available MCP servers

## References

- [GitHub: smithery-ai/mcp-obsidian](https://github.com/smithery-ai/mcp-obsidian)
- [GitHub: spences10/mcp-sequentialthinking-tools](https://github.com/spences10/mcp-sequentialthinking-tools)
- [GitHub: modelcontextprotocol/create-python-server](https://github.com/modelcontextprotocol/create-python-server)

---

_This note belongs to the [[Processes MOC]]_
