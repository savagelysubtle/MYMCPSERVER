---
created: 2025-03-28
tags: process, mcp, setup, windows
parent: [[Processes MOC]]
---

# Setting Up MCP Central Hub for Windows

## Overview

This process guides you through setting up a central hub to manage multiple MCP servers for Cursor IDE on Windows. The hub will integrate Obsidian knowledge management, sequential thinking tools, and file management capabilities into a unified system.

## Key Points

- Creates a modular MCP server hub for Windows
- Centralizes configuration for multiple MCP servers
- Includes startup script for simplified launch
- Organizes servers by functionality
- Configures Cursor to connect to the hub

## Details

### Prerequisites

1. **Node.js**: v18.x or later installed

   - Verify installation with `node --version` in Command Prompt

2. **Python**: 3.10 or later installed

   - Verify with `python --version`
   - Ensure "Add Python to PATH" was selected during installation

3. **Package Managers**:

   - UV for Python package management: `pip install uv`
   - NPM (comes with Node.js)

4. **Cursor IDE**: Latest version with MCP support

### Step 1: Create Project Structure

1. Create a base directory for the central hub:

   ```
   mkdir mcp-central-hub
   cd mcp-central-hub
   ```

2. Create subdirectories for different server types:
   ```
   mkdir python-servers
   mkdir node-servers
   mkdir config
   mkdir scripts
   ```

### Step 2: Set Up Node.js-based Servers

1. Install the Sequential Thinking tools server:

   ```
   cd node-servers
   npm install @spences10/mcp-sequentialthinking-tools
   cd ..
   ```

2. Install the Obsidian MCP server:
   ```
   cd node-servers
   npm install obsidian-mcp
   cd ..
   ```

### Step 3: Set Up Python-based Servers

1. Create a new Python-based MCP server for file management:

   ```
   cd python-servers
   uv create-mcp-server
   ```

   Follow the prompts:

   - Name: filemanagement-server
   - Description: File management tools for Cursor
   - Package name: filemanagement_server

2. Customize the file management server (see detailed instructions in [[Custom Python MCP Development]])

### Step 4: Create Configuration Files

1. Create a hub configuration file in the config directory:
   ```json
   // config/hub-config.json
   {
     "servers": {
       "obsidian": {
         "type": "node",
         "package": "obsidian-mcp",
         "args": ["D:/path/to/your/obsidian/vault"],
         "enabled": true
       },
       "sequentialThinking": {
         "type": "node",
         "package": "@spences10/mcp-sequentialthinking-tools",
         "enabled": true
       },
       "fileManagement": {
         "type": "python",
         "path": "./python-servers/filemanagement-server",
         "enabled": true
       }
     },
     "startup": {
       "autoStart": true,
       "startOrder": ["obsidian", "sequentialThinking", "fileManagement"]
     }
   }
   ```

### Step 5: Create Startup Script

1. Create a PowerShell startup script:

   ```powershell
   # scripts/start-hub.ps1

   param (
       [string]$configPath = "../config/hub-config.json"
   )

   # Load configuration
   $config = Get-Content -Path $configPath | ConvertFrom-Json

   # Function to start a server
   function Start-McpServer {
       param (
           [string]$name,
           [PSCustomObject]$serverConfig
       )

       Write-Host "Starting $name server..."

       if ($serverConfig.type -eq "node") {
           $processArgs = @(
               "-y",
               $serverConfig.package
           )

           if ($serverConfig.args) {
               $processArgs += $serverConfig.args
           }

           Start-Process -FilePath "npx" -ArgumentList $processArgs -NoNewWindow
       }
       elseif ($serverConfig.type -eq "python") {
           $currentDir = Get-Location
           Set-Location -Path $serverConfig.path
           Start-Process -FilePath "uv" -ArgumentList "run", "." -NoNewWindow
           Set-Location -Path $currentDir
       }
   }

   # Start servers in the specified order
   foreach ($serverName in $config.startup.startOrder) {
       $serverConfig = $config.servers.$serverName

       if ($serverConfig.enabled) {
           Start-McpServer -name $serverName -serverConfig $serverConfig
       }
   }

   Write-Host "All MCP servers started!"
   ```

### Step 6: Configure Cursor IDE

1. Open Cursor IDE settings (keyboard shortcut: `Ctrl+,`)
2. Navigate to Features > MCP Servers
3. Add a new MCP server with the following settings:

   - Name: `mcp-central-hub`
   - Command: `powershell.exe`
   - Args: `-ExecutionPolicy Bypass -File "D:/path/to/mcp-central-hub/scripts/start-hub.ps1"`

4. Click "Add" to save the configuration
5. Restart Cursor IDE to apply changes

### Step 7: Verify Setup

1. Open Cursor IDE
2. Check that the MCP servers are running (green indicator in the MCP Servers section)
3. Test by asking Cursor to use one of the tools from your hub
4. Check for any error messages in the Cursor console or server output

## Related Notes

- [[MCP Central Hub]] - Concept explanation of hub architecture
- [[Cursor MCP Integration]] - Details on how Cursor works with MCP
- [[Custom Python MCP Development]] - Creating custom Python-based MCP servers

## References

- [MCP Servers Hub on GitHub](https://github.com/apappascs/mcp-servers-hub)
- [Obsidian MCP Server](https://github.com/StevenStavrakis/obsidian-mcp)
- [Sequential Thinking Tools](https://github.com/spences10/mcp-sequentialthinking-tools)
- [Create Python MCP Server](https://github.com/modelcontextprotocol/create-python-server)

---

_This note belongs to the [[Processes MOC]]_
