"""
MCP CLI Tool Registration Module

This module provides the registration interface for CLI tools with the MCP server.
It defines tool metadata and integration points for the server architecture.
"""

from typing import Any

# Import the actual tool implementations
from .cli_tools import run_command, show_security_rules
from .git_tools import get_git_status, list_branches, search_codebase

# Define tool metadata for MCP server registration
CLI_TOOLS = [
    {
        "name": "run_command",
        "function": run_command,
        "description": "Execute command-line operations with auto-correction for Windows and UV package manager",
        "schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute. Supports: 1) Windows commands like 'dir /a', 2) Unix equivalents like 'ls -l', 3) UV package manager commands with auto-correction",
                },
            },
            "required": ["command"],
            "additionalProperties": {
                "autoPreprocessing": {
                    "description": "Command input is automatically preprocessed for maximum compatibility",
                    "examples": [
                        {"input": "ls -l", "converted": "dir /a"},
                        {"input": "cat file.txt", "converted": "type file.txt"},
                        {
                            "input": "pip install requests",
                            "converted": "uv add requests",
                        },
                        {"input": "python script.py", "converted": "uv run script.py"},
                        {"input": "uv install pandas", "converted": "uv add pandas"},
                    ],
                },
                "security_restrictions": {
                    "description": "For security, file operations like move, delete, rename, or accessing system directories are restricted",
                    "examples": [
                        {
                            "blocked": "del file.txt",
                            "reason": "File deletion not allowed",
                        },
                        {
                            "blocked": "move file.txt newfile.txt",
                            "reason": "File movement not allowed",
                        },
                        {
                            "blocked": "dir C:\\Windows",
                            "reason": "Access to system directories restricted",
                        },
                        {
                            "blocked": "uv run rm_script.py",
                            "reason": "Scripts with restricted operations blocked",
                        },
                    ],
                },
            },
        },
    },
    {
        "name": "show_security_rules",
        "function": show_security_rules,
        "description": "Display security configuration for command execution, preprocessing rules, and UV commands",
        "schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "git_status",
        "function": get_git_status,
        "description": "Get the Git status of a repository",
        "schema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to the Git repository (optional, defaults to working directory)",
                },
            },
        },
    },
    {
        "name": "git_branches",
        "function": list_branches,
        "description": "List branches in a Git repository",
        "schema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to the Git repository (optional, defaults to working directory)",
                },
                "show_remotes": {
                    "type": "boolean",
                    "description": "Whether to include remote branches (default: false)",
                },
            },
        },
    },
    {
        "name": "search_code",
        "function": search_codebase,
        "description": "Search for patterns in the codebase",
        "schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Pattern to search for",
                },
                "path": {
                    "type": "string",
                    "description": "Path to search in (optional, defaults to working directory)",
                },
                "file_pattern": {
                    "type": "string",
                    "description": "File pattern to match (e.g., '*.py', optional)",
                },
            },
            "required": ["pattern"],
        },
    },
]


def register_tools(server: Any) -> None:
    """
    Register all CLI tools with the MCP server.

    Args:
        server: The MCP server instance to register tools with
    """
    for tool in CLI_TOOLS:
        try:
            server.register_tool(tool["function"])
        except Exception as e:
            print(f"Failed to register tool {tool['name']}: {str(e)}")


def get_tool_definitions() -> dict[str, dict[str, Any]]:
    """
    Get tool definitions for documentation or UI purposes.

    Returns:
        Dictionary of tool definitions by name
    """
    return {tool["name"]: tool for tool in CLI_TOOLS}
