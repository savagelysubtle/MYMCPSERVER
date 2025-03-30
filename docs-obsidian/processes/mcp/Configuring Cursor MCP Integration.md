---
created: 2025-03-28
tags: [mcp, cursor, integration, configuration]
parent: [[Processes MOC]]
---

# Configuring Cursor MCP Integration

## Overview

This guide outlines the process for configuring Cursor IDE to integrate with MCP servers, including both the graphical interface method and the configuration file approach.

## Prerequisites

- Cursor IDE (latest version)
- MCP server implementation(s)
- Node.js (for Node-based servers)
- Python (for Python-based servers)

## Step-by-Step Process

### Method 1: Using the Cursor GUI

1. Open Cursor Settings:

   - Use keyboard shortcut: `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
   - Type "Cursor Settings" and select it

2. Navigate to MCP Section:

   - Find the "MCP" section in the sidebar of settings
   - Review currently configured servers (if any)

3. Add New MCP Server:

   - Click the "Add New MCP Server" button
   - Fill in the required fields:
     - **Name**: Descriptive name for the server
     - **Command**: Command to run the server (e.g., `npx`, `python`, `node`)
     - **Arguments**: Arguments for the command (e.g., `["-y", "mcp-sequentialthinking-tools"]`)
     - **Environment Variables** (optional): Key-value pairs for environment configuration

4. Save Configuration:
   - Click "Add" to save the server configuration
   - Verify that the server appears with a green status indicator

### Method 2: Using Configuration Files

1. Project-Specific Configuration:

   - Create `.cursor/mcp.json` in your project directory:

   ```json
   {
     "mcpServers": {
       "server-name": {
         "command": "npx",
         "args": ["-y", "package-name"],
         "env": {
           "KEY": "value"
         }
       }
     }
   }
   ```

2. Global Configuration:

   - Create `~/.cursor/mcp.json` in your home directory for system-wide servers
   - Windows path: `%USERPROFILE%\.cursor\mcp.json`
   - Format is identical to project-specific configuration

3. Environment Variables:
   - Use the `env` prefix for commands with environment variables:
   ```json
   {
     "mcpServers": {
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

### Method 3: Using Central Hub Integration

1. Configure central hub in `.cursor/mcp.json`:

   ```json
   {
     "mcpServers": {
       "central-hub": {
         "command": "node",
         "args": ["./path/to/central-hub/main.js"]
       }
     }
   }
   ```

2. Verify Hub Integration:
   - Open Cursor settings to confirm hub is connected
   - Check logs for any connection issues

## Verification and Testing

1. Check Server Status:

   - Open Cursor settings
   - Verify server has a green status indicator
   - If yellow, try clicking the refresh button

2. Test Server Functionality:
   - Open Cursor's Agent mode
   - Ask the agent to use one of the tools provided by your MCP server
   - Verify the response contains the expected data

## Troubleshooting

### Common Issues and Solutions

1. **Server Not Found**

   - Verify package is installed: `npm list -g package-name`
   - Check if path is correct in configuration

2. **Permission Issues**

   - Run with administrative privileges
   - Check file permissions

3. **Environment Variables Not Working**

   - Use the `env` prefix method
   - Verify variable format

4. **Configuration Not Loading**

   - Restart Cursor after configuration changes
   - Verify JSON syntax is correct

5. **Multiple Tool Conflicts**
   - Ensure unique tool names across servers
   - Use the central hub for better management

## Next Steps

- [[Setting Up MCP Central Hub]]
- [[Adding Sequential Thinking Tools]]
- [[Obsidian MCP Integration]]

## References

- [[MCP Central Hub]]
- [[Cursor MCP Integration]]
- [[Tool Management]]
- [Cursor Documentation](https://cursor.sh/docs/mcp)
