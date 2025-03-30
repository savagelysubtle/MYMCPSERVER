---
created: 2025-03-28
updated: 2025-03-30
tags: [mcp, debugging, development, troubleshooting]
parent: [[../MCP Knowledge MOC]]
---

# MCP Hub Debugging Guide

## Overview

This reference document provides troubleshooting steps and solutions for common issues with the MCP Central Hub, with a focus on Windows environments. It covers logging, error identification, and common failure scenarios.

## Key Points

- Provides solutions for PowerShell script closing immediately
- Explains the structured logging system
- Details how to interpret error logs
- Lists common issues and their solutions
- Covers troubleshooting for both Node.js and Python servers

## Details

### PowerShell Script Closing Immediately

A common issue is the PowerShell window closing immediately when running the startup script, preventing you from seeing errors. The following solutions are implemented in our hub:

1. **Keeping Window Open**: The script now includes a `-keepOpen` parameter that prevents the window from closing:

   ```powershell
   powershell.exe -ExecutionPolicy Bypass -File "path\to\start-hub.ps1" -keepOpen
   ```

2. **Transcript Logging**: The script automatically records all console output to transcript logs:

   ```
   logs/[timestamp]-[sessionId]/transcript.log
   ```

3. **Error Handling**: Try/catch blocks capture and display detailed error information

### Log Directory Structure

The improved MCP Hub uses a structured logging approach:

```
logs/
├── [timestamp]-[sessionId]/    # Run-specific directory
│   ├── transcript.log          # Full console output
│   ├── hub.log                 # Hub-specific messages
│   ├── obsidian/               # Server-specific logs
│   │   ├── server.log          # Server log messages
│   │   ├── output.log          # Standard output
│   │   └── error.log           # Standard error
│   ├── sequentialThinking/     # Another server's logs
│   └── fileManager/            # Another server's logs
└── transcript-[older-run].log  # Logs from previous runs
```

### Reading Logs for Diagnosis

When troubleshooting, examine the logs in this order:

1. **Transcript Log**: Start with `transcript.log` to see all console output
2. **Error Logs**: Check `[server-name]/error.log` for server-specific errors
3. **Hub Log**: Review `hub.log` for hub-level issues

### Common Issues and Solutions

#### 1. Script Closes Immediately

**Symptoms**: PowerShell window appears briefly then disappears

**Solutions**:

- Ensure `-keepOpen` parameter is used in the `.cursor/mcp.json` configuration
- Run script manually in PowerShell to observe errors:

  ```powershell
  cd D:\path\to\mcpServer\src\mcpServer\scripts\
  .\start-hub.ps1 -keepOpen
  ```

- Check transcript logs for error messages

#### 2. NPM Package Not Found

**Symptoms**: Node.js server fails to start with "package not found" error

**Solutions**:

- Verify the package is installed: `npm list -g [package-name]`
- Install the package globally: `npm install -g [package-name]`
- Check for typos in package name in `hub-config.json`

#### 3. Python Module Errors

**Symptoms**: Python server exits immediately with import errors

**Solutions**:

- Install required dependencies: `pip install mcp aiofiles`
- Check Python version compatibility (requires 3.10+)
- Verify file structure matches expected imports

#### 4. Permission Issues

**Symptoms**: "Access denied" or "cannot create file" errors

**Solutions**:

- Run PowerShell as Administrator
- Check write permissions on the logs directory
- Ensure all paths used in configuration exist

#### 5. Communication Errors

**Symptoms**: MCP servers start but Cursor can't communicate with them

**Solutions**:

- Ensure only one instance of each server is running
- Check if antivirus/firewall is blocking communication
- Restart Cursor IDE
- Clear Cursor's MCP cache by restarting with the `--clear-mcp-cache` parameter

### Monitoring Running Servers

The improved script monitors server processes for the first 5 seconds to detect immediate failures. To check server status:

1. **Process IDs**: The script logs each server's PID:

   ```
   [2025-03-28 15:45:23] [SUCCESS] [obsidian] Started Node.js server: obsidian (PID: 12345)
   ```

2. **Check Running Processes**: Verify if processes are still running:

   ```powershell
   Get-Process -Id 12345
   ```

### Restarting Failed Servers

To restart a specific server:

```powershell
.\start-hub.ps1 -server sequentialThinking
```

## Related Documentation

### Implementation Guides

- [[Hub Implementation|MCP Hub Implementation]]
- [[Hub Configuration|Configuration Reference]]
- [[Configuration Examples|Configuration Examples]]

### Core Concepts

- [[../core/MCP Central Hub|MCP Central Hub]]
- [[../core/MCP Server Architecture|MCP Server Architecture]]

### Integration

- [[../integration/Cursor MCP Integration|Cursor Integration]]
- [[../../projects/myMcpServer/implementation/Server Configuration|Server Configuration]]

## External References

- [PowerShell Start-Transcript Documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.host/start-transcript)
- [PowerShell Scripting Solutions for Windows](https://stackoverflow.com/questions/1337229/powershell-window-disappears-before-i-can-read-the-error-message)
- [How to keep PowerShell window open](https://stackoverflow.com/questions/16739322/how-to-keep-the-shell-window-open-after-running-a-powershell-script)

---

[[../MCP Knowledge MOC|← Back to MCP Knowledge]]
