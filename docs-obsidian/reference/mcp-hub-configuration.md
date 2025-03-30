---
created: 2025-03-28
tags: reference, mcp, configuration
parent: [[Reference MOC]]
---

# MCP Hub Configuration Reference

## Overview

This reference document details the configuration options and structure for the MCP Central Hub system. It covers the JSON configuration format, available options, and examples for different server types and configurations.

## Key Points

- Defines the schema for the hub-config.json file
- Documents all configuration options and their purposes
- Provides examples for different server types (Node.js and Python)
- Explains environment variable configuration
- Covers logging and startup options

## Details

### Configuration File Structure

The MCP Hub configuration uses a JSON format with the following top-level sections:

```json
{
  "servers": {
    // Server definitions
  },
  "startup": {
    // Startup configuration
  },
  "logging": {
    // Logging configuration
  }
}
```

### Server Configuration

Each server is defined with a unique key in the `servers` object:

```json
"servers": {
  "server-name": {
    "type": "node|python",
    "package": "package-name",
    "args": ["arg1", "arg2"],
    "path": "./relative/path",
    "env": {
      "ENV_VAR": "value"
    },
    "enabled": true|false
  }
}
```

#### Common Server Properties

| Property  | Type    | Required | Description                                          |
| --------- | ------- | -------- | ---------------------------------------------------- |
| `type`    | string  | Yes      | Server type: "node" or "python"                      |
| `enabled` | boolean | No       | Whether the server should be started (default: true) |
| `env`     | object  | No       | Environment variables to set when running the server |

#### Node.js Server Properties

| Property  | Type   | Required | Description                                  |
| --------- | ------ | -------- | -------------------------------------------- |
| `package` | string | Yes      | NPM package name for the MCP server          |
| `args`    | array  | No       | Command-line arguments to pass to the server |

#### Python Server Properties

| Property | Type   | Required | Description                             |
| -------- | ------ | -------- | --------------------------------------- |
| `path`   | string | Yes      | Path to the Python MCP server directory |

### Startup Configuration

Controls how servers are started:

```json
"startup": {
  "autoStart": true,
  "startOrder": ["server1", "server2", "server3"]
}
```

| Property     | Type    | Required | Description                                            |
| ------------ | ------- | -------- | ------------------------------------------------------ |
| `autoStart`  | boolean | No       | Whether to start servers automatically (default: true) |
| `startOrder` | array   | Yes      | Order in which to start the servers                    |

### Logging Configuration

Controls logging behavior:

```json
"logging": {
  "path": "./logs",
  "level": "info"
}
```

| Property | Type   | Required | Description                                                          |
| -------- | ------ | -------- | -------------------------------------------------------------------- |
| `path`   | string | No       | Path to the log directory (default: "./logs")                        |
| `level`  | string | No       | Logging level: "debug", "info", "warning", "error" (default: "info") |

### Complete Configuration Example

```json
{
  "servers": {
    "obsidian": {
      "type": "node",
      "package": "mcp-obsidian",
      "args": ["D:/path/to/obsidian/vault"],
      "enabled": true
    },
    "sequentialThinking": {
      "type": "node",
      "package": "@spences10/mcp-sequentialthinking-tools",
      "enabled": true
    },
    "brave-search": {
      "type": "node",
      "package": "@modelcontextprotocol/server-brave-search",
      "env": {
        "BRAVE_API_KEY": "your-api-key-here"
      },
      "enabled": false
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

### Cursor Integration

The MCP Hub is integrated with Cursor through `.cursor/mcp.json`:

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

This configuration tells Cursor to run the MCP Hub startup script, which will handle starting all the configured servers.

### Environment Variables

You can set environment variables for servers that require API keys or other configuration:

```json
"servers": {
  "github": {
    "type": "node",
    "package": "@modelcontextprotocol/server-github",
    "env": {
      "GITHUB_TOKEN": "ghp_yourpersonalaccesstoken"
    },
    "enabled": true
  }
}
```

### Dynamic Paths

Paths in the configuration can use:

1. **Absolute paths**: Full system path (e.g., `D:/path/to/resource`)
2. **Relative paths**: Relative to the hub directory (e.g., `./servers/python/filemanager`)

### Best Practices

1. **Security**: Never commit configuration files with sensitive API keys. Use environment variables or separate configuration for sensitive data.

2. **Modularity**: Define servers in logical groups to make management easier.

3. **Start Order**: Order servers by dependency (base services first, dependent services later).

4. **Error Handling**: Enable debug logging during initial setup to diagnose issues.

## Related Notes

- [[MCP Hub Implementation Process]] - Process for implementing the hub
- [[MCP Technical Implementation]] - Code examples and implementation details
- [[MCP Server List]] - Reference list of available MCP servers

## References

- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Cursor MCP Configuration](https://docs.cursor.com/context/model-context-protocol)

---

_This note belongs to the [[Reference MOC]]_
