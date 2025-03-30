"""Models for Obsidian tool implementation.

This module defines the data models used by the Obsidian tool for representing
notes and configuration.
"""

from __future__ import annotations

__all__ = ["Note", "ObsidianConfig"]

# Standard library imports
import os
from datetime import datetime
from pathlib import Path
from typing import Set

# Third-party imports
from pydantic import BaseModel, Field, field_validator

# Application imports
from mcp_core.logger import logger


class Note(BaseModel):
    """Represents a note in the vault.

    Attributes:
        title: The title of the note
        content: The content of the note
        created_at: When the note was created
        updated_at: When the note was last updated
        tags: Tags associated with the note
    """

    title: str = Field(..., description="The title of the note")
    content: str = Field(..., description="The content of the note")
    created_at: datetime = Field(
        default_factory=datetime.now, description="When the note was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, description="When the note was last updated"
    )
    tags: Set[str] = Field(
        default_factory=set, description="Tags associated with the note"
    )

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class ObsidianConfig(BaseModel):
    """Configuration model for Obsidian integration.

    Attributes:
        vault_path: Path to the Obsidian vault
        excluded_folders: Folders to exclude from processing
        supported_extensions: File extensions to process
        template_folder: Folder containing note templates
    """

    vault_path: Path = Field(
        default_factory=lambda: Path(
            os.path.expandvars(os.environ.get("VAULT_PATH", "docs-obsidian"))
        ).resolve()
    )
    excluded_folders: Set[str] = Field(
        default_factory=lambda: {".git", ".obsidian", "node_modules"}
    )
    supported_extensions: Set[str] = Field(default_factory=lambda: {"md", "markdown"})
    template_folder: str = Field(default="templates")

    @field_validator("vault_path")
    def validate_vault_path(cls, v: Path) -> Path:
        """Validate that the vault path exists and is a directory.

        Args:
            v: The path to validate

        Returns:
            Path: The validated path

        Raises:
            ValueError: If the path is not a directory
        """
        path = Path(v)
        if not path.exists():
            logger.warning(f"Vault path does not exist: {path}")
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created vault directory: {path}")
        elif not path.is_dir():
            raise ValueError(f"Vault path is not a directory: {path}")

        logger.info(f"Using vault path: {path}")
        return path
