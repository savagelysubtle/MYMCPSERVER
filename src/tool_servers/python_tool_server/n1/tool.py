"""Obsidian tool implementation for MCP."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path

try:
    from mcp import ToolContext, ToolResponse, tool
except ImportError:
    print("MCP SDK not installed. Please install it using 'pip install mcp-sdk'")

    # Create stub classes/functions for development without the SDK
    class ToolContext:
        pass

    class ToolResponse:
        def __init__(self, content=None, error=None):
            self.content = content
            self.error = error

    def tool(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


from pydantic import BaseModel, Field, field_validator

# Configure logging
logger = logging.getLogger("mcp.tools.obsidian")


class Note(BaseModel):
    """Represents a note in the vault."""

    title: str = Field(..., description="The title of the note")
    content: str = Field(..., description="The content of the note")
    created_at: datetime = Field(
        default_factory=datetime.now, description="When the note was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, description="When the note was last updated"
    )
    tags: set[str] = Field(
        default_factory=set, description="Tags associated with the note"
    )

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class ObsidianConfig(BaseModel):
    """Configuration model for Obsidian integration."""

    vault_path: Path = Field(
        default_factory=lambda: Path(
            os.path.expandvars(os.environ.get("VAULT_PATH", "docs-obsidian"))
        ).resolve()
    )
    excluded_folders: set[str] = Field(
        default_factory=lambda: {".git", ".obsidian", "node_modules"}
    )
    supported_extensions: set[str] = Field(default_factory=lambda: {"md", "markdown"})
    template_folder: str = Field(default="templates")

    @field_validator("vault_path")
    def validate_vault_path(cls, v: Path) -> Path:
        """Validate that the vault path exists and is a directory."""
        path = Path(v)
        if not path.exists():
            logger.warning(f"Vault path does not exist: {path}")
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created vault directory: {path}")
        elif not path.is_dir():
            raise ValueError(f"Vault path is not a directory: {path}")

        logger.info(f"Using vault path: {path}")
        return path


class ObsidianTool:
    """Tool for interacting with Obsidian vault."""

    def __init__(self):
        self.config = ObsidianConfig()
        self.notes: dict[str, Note] = {}
        self._load_notes()

    def _load_notes(self) -> None:
        """Load notes from the vault."""
        try:
            vault_path = self.config.vault_path
            logger.debug(f"Loading notes from vault: {vault_path}")

            if not vault_path.exists():
                logger.warning(f"Vault path does not exist: {vault_path}")
                return

            for file in vault_path.rglob("*"):
                if file.suffix[1:] in self.config.supported_extensions:
                    relative_path = str(file.relative_to(vault_path))
                    if not any(
                        excluded in relative_path
                        for excluded in self.config.excluded_folders
                    ):
                        try:
                            with open(file, encoding="utf-8") as f:
                                content = f.read()
                                self.notes[relative_path] = Note(
                                    title=file.stem,
                                    content=content,
                                    created_at=datetime.fromtimestamp(
                                        file.stat().st_ctime
                                    ),
                                    updated_at=datetime.fromtimestamp(
                                        file.stat().st_mtime
                                    ),
                                )
                                logger.debug(f"Loaded note: {relative_path}")
                        except Exception as e:
                            logger.error(f"Error loading note {file}: {e}")
                            continue

            logger.info(f"Loaded {len(self.notes)} notes from vault")
        except Exception as e:
            logger.error(f"Error loading notes: {e}", exc_info=True)

    async def _read_file(self, path: Path) -> str:
        """Read file contents."""
        with open(path, encoding="utf-8") as f:
            return f.read()


# Create singleton instance
obsidian_instance = ObsidianTool()


@tool(
    name="obsidian.list_notes",
    description="Get contents of specified Obsidian notes",
    schema={
        "type": "object",
        "properties": {
            "paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of note paths to retrieve",
            }
        },
        "required": ["paths"],
    },
)
async def obsidian_list_notes(context: ToolContext, paths: list[str]) -> ToolResponse:
    """Get contents of specified notes."""
    try:
        results = {}
        for path in paths:
            if path in obsidian_instance.notes:
                results[path] = obsidian_instance.notes[path].model_dump()
            else:
                note_path = obsidian_instance.config.vault_path / path
                if note_path.exists() and note_path.is_file():
                    content = await obsidian_instance._read_file(note_path)
                    note = Note(title=note_path.stem, content=content)
                    obsidian_instance.notes[path] = note
                    results[path] = note.model_dump()

        return ToolResponse(
            content=[{"type": "text", "text": json.dumps(results, indent=2)}]
        )
    except Exception as e:
        logger.error(f"Error reading notes: {e}")
        return ToolResponse(error=str(e))


@tool(
    name="obsidian.search_notes",
    description="Search for notes by name or content",
    schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query to find in note titles or content",
            }
        },
        "required": ["query"],
    },
)
async def obsidian_search_notes(context: ToolContext, query: str) -> ToolResponse:
    """Search for notes by name or content."""
    try:
        results = []
        for path, note in obsidian_instance.notes.items():
            if (
                query.lower() in note.title.lower()
                or query.lower() in note.content.lower()
            ):
                results.append({"path": path, **note.model_dump()})

        return ToolResponse(
            content=[{"type": "text", "text": json.dumps(results, indent=2)}]
        )
    except Exception as e:
        logger.error(f"Error searching notes: {e}")
        return ToolResponse(error=str(e))


@tool(
    name="obsidian.save_note",
    description="Save a note to the Obsidian vault",
    schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to save the note to",
            },
            "content": {
                "type": "string",
                "description": "Content of the note",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Tags to associate with the note",
            },
        },
        "required": ["path", "content"],
    },
)
async def obsidian_save_note(
    context: ToolContext, path: str, content: str, tags: list[str] | None = None
) -> ToolResponse:
    """Save a note to the vault."""
    try:
        note_path = obsidian_instance.config.vault_path / path
        note_path.parent.mkdir(parents=True, exist_ok=True)

        with open(note_path, "w", encoding="utf-8") as f:
            f.write(content)

        note = Note(title=note_path.stem, content=content, tags=set(tags or []))
        obsidian_instance.notes[path] = note

        return ToolResponse(
            content=[{"type": "text", "text": f"Note saved successfully: {path}"}]
        )
    except Exception as e:
        logger.error(f"Error saving note: {e}")
        return ToolResponse(error=str(e))
