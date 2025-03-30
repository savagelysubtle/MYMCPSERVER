"""Logging configuration for MCP.

This module provides centralized logging configuration following project structure rules.
"""

import os
from pathlib import Path

from pydantic import BaseModel, Field

# Get project root from environment or default
PROJECT_ROOT = Path(
    os.getenv("MCP_PROJECT_ROOT", "/d:/Coding/Python_Projects/MYMCPSERVER")
)
LOG_ROOT = PROJECT_ROOT / "logs"


class LogConfig(BaseModel):
    """Logging configuration model."""

    # Log directory settings
    log_dir: Path = Field(
        default_factory=lambda: LOG_ROOT, description="Root directory for log files"
    )
    core_log_dir: Path = Field(
        default_factory=lambda: LOG_ROOT / "core",
        description="Directory for core layer logs",
    )
    proxy_log_dir: Path = Field(
        default_factory=lambda: LOG_ROOT / "proxy",
        description="Directory for proxy layer logs",
    )
    tools_log_dir: Path = Field(
        default_factory=lambda: LOG_ROOT / "tools",
        description="Directory for tool server logs",
    )

    # Log file settings
    log_level: str = Field(default="INFO", description="Default logging level")
    file_name_template: str = Field(
        default="{service}-{date}.log", description="Template for log file names"
    )
    max_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum size of log files before rotation",
    )
    backup_count: int = Field(default=5, description="Number of backup files to keep")

    # Output settings
    enable_stdout: bool = Field(
        default=True, description="Whether to output logs to stdout"
    )
    json_format: bool = Field(
        default=True, description="Whether to format logs as JSON"
    )

    def get_log_dir(self, service: str) -> Path:
        """Get the appropriate log directory for a service.

        Args:
            service: The service name (core, proxy, or a tool name)

        Returns:
            Path: The log directory for the service
        """
        if service == "core":
            return self.core_log_dir
        elif service == "proxy":
            return self.proxy_log_dir
        else:
            return self.tools_log_dir / service

    def ensure_log_dirs(self) -> None:
        """Create all required log directories."""
        for directory in [
            self.log_dir,
            self.core_log_dir,
            self.proxy_log_dir,
            self.tools_log_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


# Global configuration instance
log_config = LogConfig()

# Ensure log directories exist
log_config.ensure_log_dirs()
