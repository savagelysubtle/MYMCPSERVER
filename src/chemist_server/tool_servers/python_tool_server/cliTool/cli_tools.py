"""CLI tools for the MCP server.

This module provides secure command-line execution tools based on the
cli-mcp-server project (https://github.com/MladenSU/cli-mcp-server).
Optimized for Windows environments with special handling for UV package management.
"""

import logging
import os
import re
import shlex
import sys
from typing import Any

from .command_tools import (
    CommandConfig,
    CommandError,
    CommandExecutor,
    CommandSecurityError,
    CommandTimeoutError,
    create_executor_from_env,
)

# Configure logging
logger = logging.getLogger(__name__)

# Default allowed directory is the current working directory
DEFAULT_ALLOWED_DIR = os.getcwd()

# Define restricted/dangerous operations
RESTRICTED_COMMANDS = [
    # File deletion commands
    "del",
    "erase",
    "rd",
    "rmdir",
    "remove-item",
    "rm",
    # File movement/renaming
    "move",
    "rename",
    "ren",
    "mv",
    "copy",
    "cp",
    # System-related commands
    "format",
    "diskpart",
    "fdisk",
    "chkdsk",
    "sfc",
    "reg",
    "regedit",
    "taskkill",
    "shutdown",
    "netsh",
    "sc",
]

# Critical Windows directories that should be protected
PROTECTED_DIRECTORIES = [
    r"C:\\Windows",
    r"C:\\Program Files",
    r"C:\\Program Files (x86)",
    r"C:\\System",
    r"C:\\System32",
    r"%windir%",
    r"%systemroot%",
    r"C:\\Users\\Default",
    r"C:\\ProgramData",
]

# File operations-related patterns to block (additional safety)
DANGEROUS_PATTERNS = [
    r"rmdir\s+/s",
    r"rm\s+-rf",
    r"deltree",
    r"del\s+/[qsafp]",
    r"rd\s+/s",
    r"format\s+[a-zA-Z]:",
    r"xcopy\s+.*\s+/[echy]",
    r"robocopy",
]

# Command translation tables for Unix to Windows conversions
UNIX_TO_WINDOWS_COMMANDS = {
    "ls": "dir",
    "cat": "type",
    # Removed dangerous commands:
    # "rm": "del",
    # "cp": "copy",
    # "mv": "move",
    "mkdir": "md",
    # "rmdir": "rd",
    "touch": "echo.>",
    "grep": "findstr",
    "pwd": "cd",
    "clear": "cls",
    "find": "where",
}

# Create a CommandExecutor
try:
    # Try to create from environment variables first
    executor = create_executor_from_env()
    logger.info(
        f"CLI command executor initialized with ALLOWED_DIR={executor.allowed_dir}"
    )
except ValueError:
    # Fall back to default configuration with Windows-friendly commands
    config = CommandConfig(
        allowed_dir=os.environ.get("ALLOWED_DIR", DEFAULT_ALLOWED_DIR),
        allowed_commands=[
            "dir",
            "type",
            "cd",
            "echo",
            "where",
            "whoami",
            "python",
            "pip",
            "git",
            "cls",
            "tree",
            "findstr",
            "uv",  # Add uv to allowed commands
        ],
        allowed_flags=[
            "/q",
            "/c",
            "/s",
            "/b",
            "/a",
            "/p",
            "/w",
            "-r",
            "-h",
            "--help",
            "--version",
            "-m",
            "-v",
            "/?",
            "--dev",  # Add UV-specific flags
            "--with",
            "--python",
        ],
        max_command_length=int(os.environ.get("MAX_COMMAND_LENGTH", "1024")),
        command_timeout=int(os.environ.get("COMMAND_TIMEOUT", "30")),
    )
    executor = CommandExecutor(config)
    logger.info(
        f"CLI command executor initialized with default Windows config and ALLOWED_DIR={executor.allowed_dir}"
    )

# Remove any file manipulation commands to ensure they can't be used even with command processing
for restricted_cmd in RESTRICTED_COMMANDS:
    if restricted_cmd in UNIX_TO_WINDOWS_COMMANDS:
        del UNIX_TO_WINDOWS_COMMANDS[restricted_cmd]

# Common flag translations
UNIX_TO_WINDOWS_FLAGS = {
    "-l": "/a",  # ls -l → dir /a
    "-a": "/a",  # ls -a → dir /a
    "-la": "/a",  # ls -la → dir /a
    "-n": "/n",  # count lines
    "-i": "/i",  # case insensitive
    "-r": "/s",  # recursive
}

# Common patterns to detect and fix
COMMON_PATTERNS = [
    (r'(?<!\w)echo "([^"]*)"', r"echo \1"),  # Remove unnecessary quotes
    (r"(?<!\w)echo \'([^\']*)\'", r"echo \1"),  # Remove unnecessary single quotes
    (
        r"(?<!\w)\/(?![\w.-]+(?:$|\s))",
        r"\\",
    ),  # Convert forward slashes in paths to backslashes
    (r"(?<!\w)\.\/([^\s]+)", r"\1"),  # Remove "./" prefix
]

# UV command mapping - primary UV commands and their correct format
UV_COMMANDS = {
    # Package management
    "add": "uv add",
    "pip": "uv pip",
    "remove": "uv remove",
    "uninstall": "uv remove",
    "freeze": "uv pip freeze",
    "list": "uv pip list",
    # Environment management
    "venv": "uv venv",
    "sync": "uv sync",
    "lock": "uv lock",
    # Execution
    "run": "uv run",
    "pip-compile": "uv pip compile",
    # Project management
    "init": "uv init",
    "build": "uv build",
}

# Common pip to UV command translations
PIP_TO_UV_COMMANDS = {
    "pip install": "uv add",
    "pip3 install": "uv add",
    "pip uninstall": "uv remove",
    "pip3 uninstall": "uv remove",
    "pip freeze": "uv pip freeze",
    "pip3 freeze": "uv pip freeze",
    "pip list": "uv pip list",
    "pip3 list": "uv pip list",
}

# UV command patterns to auto-fix common mistakes
UV_COMMAND_PATTERNS = [
    # Fix pip install to uv add
    (
        r"(?i)^pip\s+install\s+([\w\[\]\d.-]+(?:\s*(?:>=|<=|==|!=|~=)\s*[\d.]+)?)",
        r"uv add \1",
    ),
    (
        r"(?i)^pip3\s+install\s+([\w\[\]\d.-]+(?:\s*(?:>=|<=|==|!=|~=)\s*[\d.]+)?)",
        r"uv add \1",
    ),
    # Fix pip install with dev dependencies
    (
        r"(?i)^pip\s+install\s+(?:--dev|-d)\s+([\w\[\]\d.-]+(?:\s*(?:>=|<=|==|!=|~=)\s*[\d.]+)?)",
        r"uv add --dev \1",
    ),
    (
        r"(?i)^pip\s+install\s+([\w\[\]\d.-]+(?:\s*(?:>=|<=|==|!=|~=)\s*[\d.]+)?)\s+(?:--dev|-d)",
        r"uv add --dev \1",
    ),
    # Fix pip uninstall to uv remove
    (r"(?i)^pip\s+uninstall\s+([\w\[\]\d.-]+)", r"uv remove \1"),
    (r"(?i)^pip3\s+uninstall\s+([\w\[\]\d.-]+)", r"uv remove \1"),
    # Fix python script.py to uv run script.py
    (r"(?i)^python\s+([\w\[\]\d/\\.-]+\.py\b)", r"uv run \1"),
    (r"(?i)^python3\s+([\w\[\]\d/\\.-]+\.py\b)", r"uv run \1"),
    # Fix python -m to uv run -m
    (r"(?i)^python\s+-m\s+([\w\[\]\d.-]+)", r"uv run -m \1"),
    (r"(?i)^python3\s+-m\s+([\w\[\]\d.-]+)", r"uv run -m \1"),
    # Fix incorrect UV command order (e.g., "uv requests add")
    (r"(?i)^uv\s+([\w\[\]\d.-]+)\s+(add|install)$", r"uv add \1"),
    (r"(?i)^uv\s+([\w\[\]\d.-]+)\s+(remove|uninstall)$", r"uv remove \1"),
    # Fix typos in UV commands
    (r"(?i)^uv\s+instal\b", r"uv add"),
    (r"(?i)^uv\s+install\b", r"uv add"),
    (r"(?i)^uv\s+uninstall\b", r"uv remove"),
    (r"(?i)^uv\s+rmv\b", r"uv remove"),
]

# Common UV syntax errors and their fixes
UV_SYNTAX_FIXES = {
    # Fix option spacing issues
    (r"(?i)(uv\s+\w+\s+)--dev([\w\[\]\d.-]+)", r"\1--dev \2"),
    (r"(?i)(uv\s+\w+\s+)--with([\w\[\]\d.-]+)", r"\1--with \2"),
    (r"(?i)(uv\s+\w+\s+)--python([\w\[\]\d.]+)", r"\1--python \2"),
    # Fix incomplete commands
    (r"(?i)^uv$", r"uv --help"),
    (r"(?i)^uv\s+add$", r"uv add --help"),
    (r"(?i)^uv\s+remove$", r"uv remove --help"),
    (r"(?i)^uv\s+run$", r"uv run --help"),
}


def check_for_restricted_operations(command: str) -> str | None:
    """
    Check if the command contains any restricted operations that could be dangerous.

    Args:
        command: The command string to check

    Returns:
        Error message if restricted operation found, None otherwise
    """
    # Convert to lowercase for case-insensitive matching
    cmd_lower = command.lower()

    # Check for restricted base commands
    cmd_parts = shlex.split(cmd_lower, posix=False)
    if not cmd_parts:
        return None

    base_cmd = cmd_parts[0]

    # Check if it's a UV command with restricted operation (e.g., "uv run rm -rf /")
    if base_cmd == "uv" and len(cmd_parts) >= 3 and cmd_parts[1] == "run":
        # Extract the command being run
        run_command = cmd_parts[2]
        if any(restricted in run_command for restricted in RESTRICTED_COMMANDS):
            return f"Execution of '{run_command}' through UV run is not allowed for security reasons"

    # Check base command against restricted list
    if base_cmd in RESTRICTED_COMMANDS:
        return f"Command '{base_cmd}' is restricted for security reasons"

    # Check for dangerous operation patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, cmd_lower):
            return f"Command contains restricted operation pattern: {pattern}"

    # Check for attempts to access protected directories
    for protected_dir in PROTECTED_DIRECTORIES:
        # Replace environment variables
        expanded_dir = os.path.expandvars(protected_dir).lower()
        if expanded_dir in cmd_lower:
            return (
                f"Access to protected system directory '{protected_dir}' is restricted"
            )

    # No restricted operations found
    return None


def preprocess_uv_command(command: str) -> tuple[str, dict[str, Any]]:
    """
    Detect and preprocess UV-specific commands, applying auto-corrections.

    Args:
        command: The raw command string

    Returns:
        Tuple containing:
        - Processed UV command
        - Dict with metadata about corrections made
    """
    original_command = command
    changes = {
        "original": original_command,
        "is_uv_command": False,
        "corrections": [],
        "warnings": [],
    }

    # Strip whitespace
    command = command.strip()

    # Check if empty
    if not command:
        changes["warnings"].append("Empty command")
        return command, changes

    # Extract the base command
    command_parts = shlex.split(command, posix=False)
    if not command_parts:
        return command, changes

    base_cmd = command_parts[0].lower()

    # Check if it's already a UV command
    if base_cmd == "uv":
        changes["is_uv_command"] = True

        # Check for common UV syntax errors
        for pattern, fix in UV_SYNTAX_FIXES:
            if re.search(pattern, command):
                old_cmd = command
                command = re.sub(pattern, fix, command)
                changes["corrections"].append(
                    f"Fixed UV syntax: '{old_cmd}' → '{command}'"
                )

        # If only "uv" is provided, show help
        if len(command_parts) == 1:
            command = "uv --help"
            changes["corrections"].append("Added --help to standalone UV command")

        # Check for incorrect subcommand order
        if len(command_parts) >= 3:
            subcommand = command_parts[1].lower()
            pkg_name = command_parts[2]

            if pkg_name in UV_COMMANDS and subcommand not in UV_COMMANDS:
                # Likely reversed order (e.g., "uv requests add")
                correct_subcommand = next(
                    (
                        cmd
                        for cmd, full_cmd in UV_COMMANDS.items()
                        if pkg_name.startswith(cmd)
                    ),
                    None,
                )
                if correct_subcommand:
                    fixed_cmd = f"uv {pkg_name} {subcommand}"
                    changes["corrections"].append(
                        f"Reordered UV command: '{command}' → '{fixed_cmd}'"
                    )
                    command = fixed_cmd
    else:
        # Check if this is a command that should be converted to UV
        # First, check for pip commands
        pip_cmd_match = next(
            (
                pip_cmd
                for pip_cmd in PIP_TO_UV_COMMANDS.keys()
                if command.lower().startswith(pip_cmd)
            ),
            None,
        )
        if pip_cmd_match:
            uv_cmd = PIP_TO_UV_COMMANDS[pip_cmd_match]
            remaining = command[len(pip_cmd_match) :].strip()
            command = f"{uv_cmd} {remaining}"
            changes["is_uv_command"] = True
            changes["corrections"].append(
                f"Converted pip command to UV: '{pip_cmd_match}' → '{uv_cmd}'"
            )
        else:
            # Try pattern matching for other commands that should be UV
            for pattern, replacement in UV_COMMAND_PATTERNS:
                if re.match(pattern, command, re.IGNORECASE):
                    old_cmd = command
                    command = re.sub(pattern, replacement, command, flags=re.IGNORECASE)
                    changes["is_uv_command"] = True
                    changes["corrections"].append(
                        f"Converted to UV command: '{old_cmd}' → '{command}'"
                    )
                    break

    # For UV commands, add warning if trying to execute outside UV environment
    if changes["is_uv_command"]:
        # Check if we're in a UV virtual environment (basic check)
        in_venv = os.environ.get("VIRTUAL_ENV") is not None
        if not in_venv:
            changes["warnings"].append(
                "UV command detected but may not be running in a virtual environment"
            )

        # Log the preprocessing
        if changes["corrections"]:
            logger.info(f"Preprocessed UV command: '{original_command}' → '{command}'")
            logger.debug(f"UV corrections: {changes['corrections']}")

    return command, changes


def preprocess_command(command: str) -> tuple[str, dict[str, Any]]:
    """
    Preprocess and normalize commands from LLMs to work on Windows systems.
    Includes special handling for UV package management commands.

    Args:
        command: The raw command string from the LLM

    Returns:
        Tuple containing:
        - Preprocessed command string
        - Dict with metadata about changes made
    """
    original_command = command
    changes = {
        "original": original_command,
        "modifications": [],
        "warnings": [],
        "is_uv_command": False,
    }

    # Strip leading/trailing whitespace
    command = command.strip()
    if command != original_command:
        changes["modifications"].append("Removed extra whitespace")

    # Check if empty
    if not command:
        changes["warnings"].append("Empty command")
        return command, changes

    # Check for restricted operations before any preprocessing
    restriction_error = check_for_restricted_operations(command)
    if restriction_error:
        changes["warnings"].append(restriction_error)
        # Return the original command, but with a warning flag for later stages
        changes["contains_restricted_operation"] = True
        return command, changes

    # First, try UV-specific preprocessing
    uv_command, uv_changes = preprocess_uv_command(command)

    if uv_changes["is_uv_command"]:
        # This is a UV command, use the UV-preprocessed version
        command = uv_command
        changes["modifications"].extend(uv_changes["corrections"])
        changes["warnings"].extend(uv_changes["warnings"])
        changes["is_uv_command"] = True

        # Double-check for restricted operations after UV preprocessing
        restriction_error = check_for_restricted_operations(command)
        if restriction_error:
            changes["warnings"].append(restriction_error)
            changes["contains_restricted_operation"] = True

        # Return early for UV commands - skip Unix/Windows conversions
        return command, changes

    # If not a UV command, continue with standard Unix-to-Windows preprocessing
    # Handle simple command conversion (Unix → Windows)
    cmd_parts = command.split(None, 1)
    base_cmd = cmd_parts[0].lower()

    # Check if this is a Unix command that needs conversion
    if base_cmd in UNIX_TO_WINDOWS_COMMANDS:
        win_cmd = UNIX_TO_WINDOWS_COMMANDS[base_cmd]
        original_base = base_cmd

        # Replace the command part
        if len(cmd_parts) > 1:
            args = cmd_parts[1]
            command = f"{win_cmd} {args}"
        else:
            command = win_cmd

        changes["modifications"].append(
            f"Converted Unix command '{original_base}' to Windows command '{win_cmd}'"
        )

    # Apply flag conversions
    for unix_flag, win_flag in UNIX_TO_WINDOWS_FLAGS.items():
        if (
            f" {unix_flag} " in f" {command} "
            or f" {unix_flag}" == command[-len(unix_flag) - 1 :]
        ):
            command = re.sub(rf"(?<!\w){re.escape(unix_flag)}(?!\w)", win_flag, command)
            changes["modifications"].append(
                f"Converted Unix flag '{unix_flag}' to Windows flag '{win_flag}'"
            )

    # Apply common pattern fixes
    for pattern, replacement in COMMON_PATTERNS:
        old_command = command
        command = re.sub(pattern, replacement, command)
        if command != old_command:
            changes["modifications"].append(f"Applied pattern fix: {pattern}")

    # Handle specific command adjustments
    if command.startswith("dir"):
        # Ensure dir uses Windows style
        if " -" in command and " /" not in command:
            command = command.replace(" -", " /")
            changes["modifications"].append(
                "Converted dir flags from '-' style to '/' style"
            )

    # Normalize backslash escaping (common LLM output issue)
    if "\\\\" in command:
        command = command.replace("\\\\", "\\")
        changes["modifications"].append("Normalized double backslashes")

    # If command seems too complex or has potential issues
    if ";" in command or "&&" in command or "|" in command:
        changes["warnings"].append(
            "Command contains operators that might be rejected by security checks"
        )

    # One final check for restricted operations after all preprocessing
    restriction_error = check_for_restricted_operations(command)
    if restriction_error:
        changes["warnings"].append(restriction_error)
        changes["contains_restricted_operation"] = True

    # Log the preprocessing
    if changes["modifications"]:
        logger.info(f"Preprocessed command: '{original_command}' → '{command}'")
        logger.debug(f"Modifications: {changes['modifications']}")

    return command, changes


async def run_command(ctx: Any, command: str) -> dict[str, Any]:
    """
    Executes the specified command within the configured security constraints.

    Automatically preprocesses commands to normalize them for Windows execution,
    with special handling for UV package management commands.

    Args:
        ctx: The tool context from MCP
        command: The command to execute (e.g., 'uv add requests', 'dir /a' or 'type file.txt')

    Returns:
        Dictionary with command output (stdout, stderr, exit_code)

    Notes:
        - Commands are executed in a Windows cmd.exe context
        - Security constraints prevent escaping the allowed directory
        - Shell operators like && and | are forbidden
        - Unix-style commands will be automatically converted to Windows equivalents
        - UV package management commands will be auto-corrected if needed
        - File operations like move, delete, or list critical system files are restricted
    """
    # Get the command from context if not explicitly provided
    if (
        not command
        and hasattr(ctx, "params")
        and ctx.params
        and "command" in ctx.params
    ):
        command = ctx.params["command"]

    if not command:
        logger.error("No command provided")
        return {
            "error": "No command provided",
            "type": "InvalidCommand",
            "success": False,
        }

    # Preprocess the command to make it Windows-friendly and handle UV commands
    try:
        processed_command, changes = preprocess_command(command)

        # Handle restricted operations detected during preprocessing
        if changes.get("contains_restricted_operation", False):
            restriction_message = next(
                (
                    warning
                    for warning in changes["warnings"]
                    if "restricted" in warning or "protected" in warning
                ),
                "Operation contains restricted commands",
            )
            logger.error(f"Security restriction: {restriction_message}")
            return {
                "error": restriction_message,
                "type": "SecurityViolation",
                "success": False,
                "command": command,
                "original_command": command if command != processed_command else None,
            }

        # Include preprocessing metadata in debugging logs
        if changes["modifications"]:
            logger.debug(f"Command preprocessing changes: {changes['modifications']}")
        if changes["warnings"]:
            logger.warning(f"Command preprocessing warnings: {changes['warnings']}")

        # Use the processed command for execution
        command_to_execute = processed_command

        logger.info(f"Executing command: {command_to_execute}")
        result = await executor.run_command(command_to_execute)

        # Format the output for better readability in client
        formatted_result = {
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "exit_code": result["exit_code"],
            "success": result["exit_code"] == 0,
            "command": command_to_execute,
            "working_directory": executor.allowed_dir,
            "original_command": command if command != command_to_execute else None,
            "command_modifications": changes["modifications"]
            if changes["modifications"]
            else None,
        }

        # Add UV-specific metadata if relevant
        if changes.get("is_uv_command", False):
            formatted_result["is_uv_command"] = True

            # Add helpful note for UV-specific errors
            stderr_str = str(result["stderr"])
            if not formatted_result["success"] and "No module named 'uv'" in stderr_str:
                formatted_result["uv_error_help"] = (
                    "UV package manager not found. Install with: "
                    "pip install uv or python -m pip install uv"
                )

        # Log success/failure
        if formatted_result["success"]:
            logger.info(
                f"Command executed successfully with exit code: {result['exit_code']}"
            )
        else:
            logger.warning(f"Command failed with exit code: {result['exit_code']}")

        return formatted_result

    except CommandSecurityError as e:
        logger.error(f"Security violation: {str(e)}")
        return {
            "error": str(e),
            "type": "SecurityViolation",
            "success": False,
            "command": command,
        }
    except CommandTimeoutError as e:
        logger.error(f"Command timeout: {str(e)}")
        return {
            "error": f"Command timed out after {executor.config.command_timeout} seconds",
            "type": "CommandTimeout",
            "success": False,
            "command": command,
        }
    except CommandError as e:
        logger.error(f"Command execution error: {str(e)}")
        return {
            "error": str(e),
            "type": e.__class__.__name__,
            "success": False,
            "command": command,
        }
    except Exception as e:
        logger.error(f"Unexpected error executing command: {str(e)}")
        return {
            "error": f"Unexpected error: {str(e)}",
            "type": "UnexpectedError",
            "success": False,
            "command": command,
        }


async def show_security_rules(ctx: Any) -> dict[str, Any]:
    """
    Returns the current security configuration for CLI command execution.

    Args:
        ctx: The tool context from MCP

    Returns:
        Dictionary with security configuration details
    """
    try:
        rules = executor.get_security_rules()

        # Check if running on Windows
        is_windows = sys.platform.startswith("win")

        # Format rules for better readability
        formatted_rules = {
            "working_directory": rules["working_directory"],
            "allowed_commands": rules["allowed_commands"],
            "allowed_flags": rules["allowed_flags"],
            "command_length_limit": rules["max_command_length"],
            "execution_timeout_seconds": rules["command_timeout"],
            "platform": "Windows" if is_windows else sys.platform,
            "shell": "cmd.exe" if is_windows else os.environ.get("SHELL", "unknown"),
            "restricted_commands": RESTRICTED_COMMANDS,  # Add new restrictions to output
            "protected_directories": PROTECTED_DIRECTORIES,
        }

        return {
            "security_rules": formatted_rules,
            "success": True,
            "platform_specific": {
                "is_windows": is_windows,
                "windows_version": os.environ.get("OS", "Unknown Windows")
                if is_windows
                else "N/A",
                "command_preprocessing": {
                    "unix_to_windows_commands": list(UNIX_TO_WINDOWS_COMMANDS.keys()),
                    "unix_to_windows_flags": list(UNIX_TO_WINDOWS_FLAGS.keys()),
                    "uv_commands": {
                        "supported_base_commands": list(UV_COMMANDS.keys()),
                        "pip_to_uv_translations": PIP_TO_UV_COMMANDS,
                    },
                },
            },
        }

    except Exception as e:
        logger.error(f"Error retrieving security rules: {str(e)}")
        return {
            "error": f"Failed to retrieve security rules: {str(e)}",
            "success": False,
        }
