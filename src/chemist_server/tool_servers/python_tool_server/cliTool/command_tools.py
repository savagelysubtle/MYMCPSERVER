"""
CLI Command Execution Tool for MCP Server - Windows Version

Provides secure command-line execution with comprehensive security features
based on the cli-mcp-server project (https://github.com/MladenSU/cli-mcp-server).
Optimized for Windows environments.
"""

import asyncio
import os
import re
from dataclasses import dataclass
from typing import Any

# Import StructuredLogger for structured logging
from chemist_server.mcp_core.logger import StructuredLogger

# Configure logger
logger = StructuredLogger("chemist_server.tool_servers.cliTool.command_tools")


# Exception classes for different command errors
class CommandError(Exception):
    """Base class for command execution errors"""

    pass


class CommandSecurityError(CommandError):
    """Security violation during command execution"""

    pass


class CommandTimeoutError(CommandError):
    """Command execution exceeded timeout limit"""

    pass


class CommandExecutionError(CommandError):
    """Error during command execution"""

    pass


@dataclass
class CommandConfig:
    """Configuration for command execution security"""

    allowed_dir: str
    allowed_commands: list[str] | None = None
    allowed_flags: list[str] | None = None
    max_command_length: int = 1024
    command_timeout: int = 30

    def __post_init__(self) -> None:
        if self.allowed_commands is None:
            # Windows-specific default commands
            self.allowed_commands = ["dir", "type", "cd", "echo", "where", "whoami"]
        if self.allowed_flags is None:
            # Windows-specific default flags
            self.allowed_flags = [
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
            ]

        # Convert 'all' to None for unlimited commands/flags
        if self.allowed_commands == ["all"]:
            self.allowed_commands = None  # type: ignore
        if self.allowed_flags == ["all"]:
            self.allowed_flags = None  # type: ignore


class CommandExecutor:
    """Secure command execution with configurable security measures for Windows"""

    def __init__(self, config: CommandConfig) -> None:
        self.config = config

        # Ensure allowed_dir is an absolute path in Windows format
        self.allowed_dir = os.path.abspath(
            os.path.expandvars(os.path.expanduser(config.allowed_dir))
        )

        # Validate that the allowed directory exists
        if not os.path.isdir(self.allowed_dir):
            raise ValueError(f"Allowed directory does not exist: {self.allowed_dir}")

    def _validate_command_length(self, cmd: str) -> None:
        """Ensure command length is within allowed limits"""
        if len(cmd) > self.config.max_command_length:
            raise CommandSecurityError(
                f"Command exceeds maximum length of {self.config.max_command_length} characters"
            )

    def _validate_command(self, cmd: str) -> None:
        """Validate that the command is allowed and contains no shell operators"""
        # Check for shell operators that could allow command chaining (Windows and common operators)
        shell_operators = [
            ";",
            "&&",
            "||",
            "|",
            ">",
            ">>",
            "<",
            "%",
            "^",
            "(",
            ")",
            "@",
        ]
        for op in shell_operators:
            if op in cmd:
                raise CommandSecurityError(f"Shell operator '{op}' is not allowed")

        # Parse command into base command and args
        parts = cmd.split()
        if not parts:
            raise CommandSecurityError("Empty command")

        base_cmd = parts[0]

        # Validate base command is allowed if whitelist is active
        if (
            self.config.allowed_commands is not None
            and base_cmd not in self.config.allowed_commands
        ):
            allowed_cmds = ", ".join(self.config.allowed_commands)
            raise CommandSecurityError(
                f"Command '{base_cmd}' is not allowed. Allowed commands: {allowed_cmds}"
            )

        # Validate flags are allowed if whitelist is active
        if self.config.allowed_flags is not None:
            for part in parts[1:]:
                if (
                    part.startswith("-") or part.startswith("/")
                ) and part not in self.config.allowed_flags:
                    allowed_flags = ", ".join(self.config.allowed_flags)
                    raise CommandSecurityError(
                        f"Flag '{part}' is not allowed. Allowed flags: {allowed_flags}"
                    )

    def _validate_path_safety(self, cmd: str) -> None:
        """Ensure any paths in the command are within the allowed directory (Windows-specific)"""
        # Windows path pattern regex - handles both forward and backslashes
        path_pattern = (
            r'(?:^|\s+)([\'"]?)((?:[a-zA-Z]:)?(?:\\|/)(?:[^\'"\s]*))\1(?:\s+|$)'
        )

        for match in re.finditer(path_pattern, cmd):
            path_str = match.group(2)
            path_str = os.path.expandvars(os.path.expanduser(path_str))

            # Convert to absolute path
            if not os.path.isabs(path_str):
                path_str = os.path.abspath(os.path.join(self.allowed_dir, path_str))

            # Resolve any symlinks
            resolved_path = os.path.realpath(path_str)

            # Check if path is within allowed directory
            if (
                not os.path.commonpath([resolved_path, self.allowed_dir])
                == self.allowed_dir
            ):
                raise CommandSecurityError(
                    f"Path '{path_str}' is outside the allowed directory: {self.allowed_dir}"
                )

    async def run_command(self, command: str) -> dict[str, str | int]:
        """
        Execute a command securely with timeout and validation

        Args:
            command: The command string to execute

        Returns:
            Dict containing stdout, stderr, and exit code
        """
        # Validate command
        self._validate_command_length(command)
        self._validate_command(command)
        self._validate_path_safety(command)

        # Prepare for execution
        try:
            # On Windows, we use cmd.exe to run commands
            cmd_prefix = "cmd.exe /c "

            logger.debug(
                "Executing command", command=command, working_dir=self.allowed_dir
            )

            # Create process with timeout
            process = await asyncio.create_subprocess_shell(
                cmd_prefix + command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.allowed_dir,
            )

            # Set up a task for command execution with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=self.config.command_timeout
                )
            except TimeoutError:
                # Kill the process if it times out
                try:
                    process.kill()
                except Exception:
                    # Process may have already exited
                    pass
                raise CommandTimeoutError(
                    f"Command execution timed out after {self.config.command_timeout} seconds"
                )

            # Process results
            stdout_str = stdout.decode("utf-8", errors="replace") if stdout else ""
            stderr_str = stderr.decode("utf-8", errors="replace") if stderr else ""
            exit_code = process.returncode or 0

            logger.debug(
                "Command execution completed",
                exit_code=exit_code,
                stdout_length=len(stdout_str),
                stderr_length=len(stderr_str),
            )

            return {
                "stdout": stdout_str,
                "stderr": stderr_str,
                "exit_code": exit_code,
            }

        except CommandTimeoutError:
            # Re-raise timeout errors
            logger.warning(
                "Command execution timed out",
                command=command,
                timeout=self.config.command_timeout,
            )
            raise
        except CommandSecurityError as e:
            # Re-raise security errors
            logger.warning(
                "Command security validation failed", error=str(e), command=command
            )
            raise
        except Exception as e:
            # Log and wrap other exceptions
            logger.error(
                "Command execution failed unexpectedly",
                error=str(e),
                error_type=type(e).__name__,
                command=command,
                exc_info=True,
            )
            raise CommandExecutionError(f"Command execution failed: {e!s}")

    def get_security_rules(self) -> dict[str, str | list[str] | int | Any]:
        """Get the current security configuration for this executor"""
        logger.debug("Retrieving security rules configuration")
        return {
            "allowed_directory": self.allowed_dir,
            "allowed_commands": self.config.allowed_commands or "all",
            "allowed_flags": self.config.allowed_flags or "all",
            "max_command_length": self.config.max_command_length,
            "command_timeout": self.config.command_timeout,
        }


def create_executor_from_env() -> CommandExecutor:
    """
    Create a CommandExecutor from environment variables

    Returns:
        Configured CommandExecutor instance
    """
    # Get configuration from environment variables
    allowed_dir = os.environ.get("ALLOWED_DIR")
    if not allowed_dir:
        logger.error("ALLOWED_DIR environment variable not set")
        raise ValueError("ALLOWED_DIR environment variable must be set")

    # Parse allowed commands
    allowed_commands_str = os.environ.get(
        "ALLOWED_COMMANDS", "dir,type,cd,echo,where,whoami"
    )
    allowed_commands = (
        allowed_commands_str.split(",") if allowed_commands_str != "all" else ["all"]
    )

    # Parse allowed flags
    allowed_flags_str = os.environ.get(
        "ALLOWED_FLAGS", "/q,/c,/s,/b,/a,/p,/w,-r,-h,--help"
    )
    allowed_flags = (
        allowed_flags_str.split(",") if allowed_flags_str != "all" else ["all"]
    )

    # Get other config values
    max_command_length = int(os.environ.get("MAX_COMMAND_LENGTH", "1024"))
    command_timeout = int(os.environ.get("COMMAND_TIMEOUT", "30"))

    # Create and return the executor
    config = CommandConfig(
        allowed_dir=allowed_dir,
        allowed_commands=allowed_commands,
        allowed_flags=allowed_flags,
        max_command_length=max_command_length,
        command_timeout=command_timeout,
    )

    logger.info(
        "Created CommandExecutor from environment variables",
        allowed_dir=allowed_dir,
        allowed_commands=allowed_commands,
        command_timeout=command_timeout,
    )

    return CommandExecutor(config)
