"""Configuration management for the MCP server.

This module provides configuration handling and validation for the MCP server.
"""

from __future__ import annotations

__all__ = ["Config"]
__version__ = "0.1.0"

# Standard library imports
import logging
from pathlib import Path

# Third-party imports
from pydantic import BaseModel, Field, validator

# Get logger for this module
logger = logging.getLogger("mymcpserver.config")


class Config(BaseModel):
    """Main configuration class for the MCP server.

    Attributes:
        vault_path (Path): Path to the Obsidian vault
        log_level (str): Logging level for the server
    """

    vault_path: Path = Field(default=Path("docs-obsidian"))
    log_level: str = Field(default="INFO")

    @validator("vault_path")
    def validate_vault_path(cls, v: Path) -> Path:
        """Validate that the vault path exists and is a directory.

        Args:
            v (Path): The vault path to validate

        Returns:
            Path: The validated path

        Raises:
            ValueError: If path doesn't exist or isn't a directory
        """
        path = Path(v)
        if not path.exists():
            logger.error(f"Vault path does not exist: {path}")
            raise ValueError(f"Vault path does not exist: {path}")
        if not path.is_dir():
            logger.error(f"Vault path is not a directory: {path}")
            raise ValueError(f"Vault path is not a directory: {path}")

        logger.info(f"Validated vault path: {path}")
        return path

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate that the log level is valid.

        Args:
            v (str): The log level to validate

        Returns:
            str: The validated log level

        Raises:
            ValueError: If log level is not valid
        """
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            logger.error(f"Invalid log level: {v}")
            raise ValueError(
                f"Invalid log level. Must be one of: {', '.join(valid_levels)}"
            )

        logger.info(f"Using log level: {v.upper()}")
        return v.upper()

    class Config:
        """Pydantic config class."""

        arbitrary_types_allowed = True

    def __init__(self, **data):
        """Initialize Config with logging."""
        logger.debug("Initializing configuration")
        super().__init__(**data)
        logger.info("Configuration initialized successfully")
