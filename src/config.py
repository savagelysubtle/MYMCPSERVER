# src/mymcpserver/config.py
import os
from pathlib import Path
from typing import Literal

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Import sub-configs - ensure their model_config doesn't clash if loaded nested
# or rely on prefixes defined here.
from mcp_core.config.config import CoreConfig


class LoggingConfig(BaseSettings):
    """Nested Logging configuration."""

    # No prefix needed if nested under AppConfig with env_nested_delimiter
    # model_config = SettingsConfigDict(env_prefix='MCP_LOGGING_')

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: Literal["json", "text"] = "json"
    enable_stdout: bool = True
    file_name_template: str = "{service}.{date}.log"
    max_size_mb: int = 10
    backup_count: int = 5


class ToolServerPythonConfig(BaseSettings):
    """Configuration specific to the Python Tool Server."""

    # No prefix needed if nested
    # model_config = SettingsConfigDict(env_prefix='MCP_TOOL_PYTHON_')
    host: str = "127.0.0.1"
    port: int = 8001
    # modules_to_load: List[str] = ["tool_servers.python_tool_server.n1.tool", "tool_servers.python_tool_server.n2.tool"]


class AppConfig(BaseSettings):
    """Unified application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_nested_delimiter="__",  # e.g., MCP_LOGGING__LEVEL maps to logging.level
        env_prefix="MCP_",  # Global prefix for top-level settings
        case_sensitive=False,
        extra="ignore",
    )

    # --- Top Level Settings ---
    # WORKSPACE_FOLDER is useful contextually but maybe not part of the core config model itself
    # We can derive paths from it if needed. VAULT_PATH and LOGS_PATH are better candidates.
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
    # CoreConfig needs its own env_prefix defined within its class if it's to read MCP_CORE_* vars
    # If AppConfig reads them via nesting, CoreConfig shouldn't have its own prefix.
    # Let's assume CoreConfig reads MCP_CORE_* directly
    core: CoreConfig = CoreConfig()
    tool_server_python: ToolServerPythonConfig = (
        ToolServerPythonConfig()
    )  # Reads MCP_TOOL_PYTHON_*

    # --- Overrides (Optional - Read from generic env vars if set) ---
    # These allow MCP_HOST/MCP_PORT to override specific component hosts/ports easily
    host_override: str | None = Field(None, validation_alias="MCP_HOST")
    port_override: int | None = Field(None, validation_alias="MCP_PORT")

    # --- Helper Methods to get effective values ---
    def get_effective_log_level(self) -> str:
        # Allow direct MCP_LOG_LEVEL override for convenience
        # Check env var directly OR add another field like 'log_level_override'
        return os.getenv("MCP_LOG_LEVEL", self.logging.level).upper()

    def get_core_host(self) -> str:
        return self.host_override or self.core.host

    def get_core_port(self) -> int:
        return self.port_override or self.core.port

    def get_tool_server_python_host(self) -> str:
        return self.host_override or self.tool_server_python.host

    def get_tool_server_python_port(self) -> int:
        # Offset from *effective* core port if override exists, else use specific tool port
        return (
            (self.get_core_port() + 1)
            if self.port_override
            else self.tool_server_python.port
        )

    # Ensure directories exist after validation
    @validator("vault_path", "logs_path")
    def ensure_dir_exists(cls, v: Path) -> Path:
        v.mkdir(parents=True, exist_ok=True)
        return v


# Singleton instance management
_app_config: AppConfig | None = None


def load_and_get_config(cli_args: dict | None = None) -> AppConfig:
    """Loads, validates, applies CLI overrides, and returns the app config."""
    global _app_config
    if _app_config is None:
        try:
            # Load initial config from env/.env file via Pydantic
            # Pydantic-settings automatically reads env vars based on field names/prefixes
            _app_config = AppConfig()

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

            # Re-validate paths after potential overrides (though BaseSettings usually handles this)
            _app_config.vault_path.mkdir(parents=True, exist_ok=True)
            _app_config.logs_path.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            # Use basic print for critical config errors before logging is set up
            print(f"FATAL: Failed to load configuration: {e}", file=sys.stderr)
            raise  # Re-raise to stop execution

    return _app_config


def get_config_instance() -> AppConfig:
    """Returns the loaded config instance. Raises error if not loaded."""
    if _app_config is None:
        # This should ideally not happen if load_and_get_config is called first
        return load_and_get_config()  # Attempt to load if not already done
    return _app_config
