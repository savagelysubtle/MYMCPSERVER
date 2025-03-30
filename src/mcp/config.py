"""Configuration management for MCP Server.

This module provides centralized configuration management for the MCP server
using Pydantic models with environment variable loading capabilities.
"""

from __future__ import annotations

__all__ = [
    "AppConfig",
    "LoggingConfig",
    "ToolServerPythonConfig",
    "load_and_get_config",
    "get_config_instance",
]

# Standard library imports
import os
import sys
from pathlib import Path
from typing import Any, Literal

# Third-party imports
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Application imports
from mcp_core.config.config import CoreConfig


class LoggingConfig(BaseSettings):
    """Nested Logging configuration.

    Attributes:
        level: Log level to use
        format: Log format (json or text)
        enable_stdout: Whether to output logs to stdout
        file_name_template: Template for log file names
        max_size_mb: Maximum size of log files before rotation
        backup_count: Number of backup files to keep
    """

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: Literal["json", "text"] = "json"
    enable_stdout: bool = True
    file_name_template: str = "{service}.{date}.log"
    max_size_mb: int = 10
    backup_count: int = 5


class ToolServerPythonConfig(BaseSettings):
    """Configuration specific to the Python Tool Server.

    Attributes:
        host: Host address for the Python tool server
        port: Port number for the Python tool server
        dynamic_tool_discovery: Whether to dynamically discover tools
    """

    host: str = "127.0.0.1"
    port: int = 8001
    dynamic_tool_discovery: bool = True


class AppConfig(BaseSettings):
    """Unified application configuration.

    Provides a centralized configuration model for the entire application
    with nested configuration sections for different components.

    Attributes:
        vault_path: Path to the Obsidian vault
        logs_path: Path for storing log files
        components: Which components to run
        transport: Transport mechanism to use
        logging: Logging configuration
        core: Core service configuration
        tool_server_python: Python tool server configuration
        host_override: Override for hosts across components
        port_override: Override for ports across components
    """

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_nested_delimiter="__",  # e.g., MCP_LOGGING__LEVEL maps to logging.level
        env_prefix="MCP_",  # Global prefix for top-level settings
        case_sensitive=False,
        extra="ignore",
    )

    # --- Top Level Settings ---
    vault_path: Path = Field(
        default_factory=lambda: Path(
            os.getenv("VAULT_PATH", Path.cwd() / "docs-obsidian")
        ).resolve()
    )
    logs_path: Path = Field(
        default_factory=lambda: Path(
            os.getenv("LOGS_PATH", Path.cwd() / "logs")
        ).resolve()
    )

    # Service Selection & Transport
    components: Literal["all", "core", "tool"] = Field(
        "all", validation_alias="MCP_COMPONENTS"
    )
    transport: Literal["stdio", "sse", "http"] = Field(
        "stdio", validation_alias="MCP_TRANSPORT"
    )

    # --- Nested Configurations ---
    logging: LoggingConfig = LoggingConfig()
    core: CoreConfig = CoreConfig()
    tool_server_python: ToolServerPythonConfig = ToolServerPythonConfig()

    # --- Overrides (Optional - Read from generic env vars if set) ---
    host_override: str | None = Field(None, validation_alias="MCP_HOST")
    port_override: int | None = Field(None, validation_alias="MCP_PORT")

    # --- Helper Methods to get effective values ---
    def get_effective_log_level(self) -> str:
        """Get the effective log level, considering environment overrides.

        Returns:
            str: The effective log level in uppercase
        """
        return os.getenv("MCP_LOG_LEVEL", self.logging.level).upper()

    def get_core_host(self) -> str:
        """Get the effective host for the core service.

        Returns:
            str: Host address for the core service
        """
        return self.host_override or self.core.host

    def get_core_port(self) -> int:
        """Get the effective port for the core service.

        Returns:
            int: Port number for the core service
        """
        return self.port_override or self.core.port

    def get_tool_server_python_host(self) -> str:
        """Get the effective host for the Python tool server.

        Returns:
            str: Host address for the Python tool server
        """
        return self.host_override or self.tool_server_python.host

    def get_tool_server_python_port(self) -> int:
        """Get the effective port for the Python tool server.

        Takes into account port override and applies an offset
        from the core port if an override is active.

        Returns:
            int: Port number for the Python tool server
        """
        return (
            (self.get_core_port() + 1)
            if self.port_override
            else self.tool_server_python.port
        )

    @field_validator("vault_path", "logs_path", mode="after")
    @classmethod
    def ensure_dir_exists(cls, v: Path) -> Path:
        """Ensure the directory exists, creating it if necessary.

        Args:
            v: Path to validate and ensure exists

        Returns:
            Path: The validated path
        """
        v.mkdir(parents=True, exist_ok=True)
        return v


# Singleton instance management
_app_config: AppConfig | None = None


def load_and_get_config(cli_args: dict[str, Any] | None = None) -> AppConfig:
    """Load, validate, apply CLI overrides, and return the app config.

    Args:
        cli_args: Optional dictionary of command line arguments to override config

    Returns:
        AppConfig: The loaded and configured application config

    Raises:
        Exception: If configuration loading fails
    """
    global _app_config
    if _app_config is None:
        try:
            # Load initial config from env/.env file via Pydantic
            _app_config = AppConfig(
                # Explicitly pass defaults to satisfy linter, though these would
                # normally be read from environment variables via BaseSettings
                components="all",
                transport="stdio",
                host_override=None,
                port_override=None,
            )

            # Apply CLI overrides (these take highest precedence)
            if cli_args:
                if cli_args.get("transport") is not None:
                    _app_config.transport = cli_args["transport"].lower()  # type: ignore
                if cli_args.get("host") is not None:
                    _app_config.host_override = cli_args["host"]
                if cli_args.get("port") is not None:
                    _app_config.port_override = cli_args["port"]
                if cli_args.get("log_level") is not None:
                    _app_config.logging.level = cli_args["log_level"].upper()  # type: ignore
                if cli_args.get("component") is not None:
                    _app_config.components = cli_args["component"].lower()  # type: ignore

            # Re-validate paths after potential overrides
            _app_config.vault_path.mkdir(parents=True, exist_ok=True)
            _app_config.logs_path.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            # Use basic print for critical config errors before logging is set up
            print(f"FATAL: Failed to load configuration: {e}", file=sys.stderr)
            raise  # Re-raise to stop execution

    return _app_config


def get_config_instance() -> AppConfig:
    """Return the loaded config instance or load it if not already loaded.

    Returns:
        AppConfig: The application configuration instance
    """
    if _app_config is None:
        return load_and_get_config()  # Attempt to load if not already done
    return _app_config
