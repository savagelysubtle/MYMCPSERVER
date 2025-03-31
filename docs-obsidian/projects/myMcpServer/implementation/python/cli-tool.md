---
created: 2025-03-31
updated: 2025-03-31
tags: [implementation, python, cli, windows, security, tool-server]
parent: [[../_index]]
up: [[../_index]]
siblings: [[tool-server]]
implements: [[../../../architecture/Component Design]]
references: []
related: [[../transport/tool-transport]]
based_on_decision: []
informed_by_research: []
next: []
previous: [[tool-server]]
---

# CLI Tool Implementation

## Overview

The CLI Tool provides secure command-line execution capabilities for the MCP server architecture with a focus on Windows compatibility. Built as a Python tool server component, it allows controlled execution of system commands with comprehensive security measures to prevent unauthorized operations.

## Key Points

- Windows-optimized command execution with security constraints
- Based on the cli-mcp-server project architecture (https://github.com/MladenSU/cli-mcp-server)
- Implements security constraints: command whitelisting, flag validation, path safety, shell operator prevention
- Properly integrated with the MCP Python Tool Server infrastructure
- Supports additional Git-specific operations through specialized tools

## Implementation Structure

The CLI Tool implementation consists of several core components:

```
src/chemist_server/tool_servers/python_tool_server/cliTool/
├── __init__.py           # Module exports
├── cli_tool_registry.py  # Tool registration with MCP
├── cli_tools.py          # Primary tool functions (run_command, security_rules)
├── command_tools.py      # Core security and execution engine
└── git_tools.py          # Git-specific command implementations
```

## Security Features

The CLI Tool implements a multi-layered security approach:

1. **Command Whitelisting**: Only explicitly allowed commands can be executed
2. **Flag Validation**: Only approved command flags/options are permitted
3. **Path Safety**: Prevents accessing paths outside the allowed directory
4. **Shell Operator Prevention**: Blocks shell operators that could enable command chaining
5. **Timeout Enforcement**: Commands are terminated if they exceed the specified timeout
6. **Working Directory Constraint**: Commands are executed within a specified allowed directory

## Usage Examples

The CLI Tool exposes several functions to the MCP server:

### Run Command

Executes a command securely with all security constraints applied:

```python
result = await run_command(ctx, "dir /a")
```

Response:

```json
{
  "stdout": "Directory of D:\\Coding\\Python_Projects\\MYMCPSERVER\n...",
  "stderr": "",
  "exit_code": 0,
  "success": true,
  "command": "dir /a",
  "working_directory": "D:\\Coding\\Python_Projects\\MYMCPSERVER"
}
```

### Show Security Rules

Returns the current security configuration:

```python
rules = await show_security_rules(ctx)
```

Response:

```json
{
  "security_rules": {
    "working_directory": "D:\\Coding\\Python_Projects\\MYMCPSERVER",
    "allowed_commands": ["dir", "type", "cd", "echo", "..."],
    "allowed_flags": ["/q", "/c", "/s", "..."],
    "command_length_limit": 1024,
    "execution_timeout_seconds": 30,
    "platform": "Windows",
    "shell": "cmd.exe"
  },
  "success": true,
  "platform_specific": {
    "is_windows": true,
    "windows_version": "Windows_NT"
  }
}
```

### Git Operations

Specialized Git operations are also available:

```python
# Get git status
status = await get_git_status(ctx, repo_path="D:\\project")

# List branches
branches = await list_branches(ctx, repo_path="D:\\project", show_remotes=True)

# Search codebase
results = await search_codebase(ctx, pattern="import os", file_pattern="*.py")
```

## Integration with MCP

The CLI Tool integrates with the MCP architecture through the Python Tool Server:

1. Tools are registered via the `cli_tool_registry.py` module
2. Each tool is registered with the server using:
   ```python
   register_cli_tools(server)
   ```
3. Tool functions receive the MCP context and return structured responses

This approach allows the CLI Tool to operate within the [[../../architecture/System Overview]](defined_by) MCP architecture while maintaining proper isolation and security.

## Configuration

The CLI Tool is configurable through environment variables:

| Variable           | Description                              | Default                            |
| ------------------ | ---------------------------------------- | ---------------------------------- |
| ALLOWED_DIR        | Base directory for command execution     | Current working directory          |
| ALLOWED_COMMANDS   | Comma-separated list of allowed commands | Windows commands (dir, type, etc.) |
| ALLOWED_FLAGS      | Comma-separated list of allowed flags    | Windows flags (/q, /c, etc.)       |
| MAX_COMMAND_LENGTH | Maximum command string length            | 1024                               |
| COMMAND_TIMEOUT    | Maximum execution time (seconds)         | 30                                 |

## Relationships / Links

- Implements: [[../../../architecture/Component Design]](implements)
- Part of: [[../python/_index]](part_of)
- Used by: [[../../../architecture/System Overview]](used_by)
- Based on: [cli-mcp-server](https://github.com/MladenSU/cli-mcp-server)
- Depends on: [[tool-server]](depends_on)

## Related Documentation

- [[tool-server]] - Python Tool Server implementation
- [[../transport/tool-transport]] - Transport layer for tool communications
- [[../../../api/tool_api]] - Tool API specifications

---

_Part of [[../_index|Implementation Documentation]]_
