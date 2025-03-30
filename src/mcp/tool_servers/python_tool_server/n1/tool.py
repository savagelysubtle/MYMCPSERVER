# src/tool_servers/python_tool_server/n1/tool.py
from __future__ import annotations

import json
# Use the structured logger
try:
    # Assumes src path is added correctly when run via run_server.py
    from mcp_core.logger import StructuredLogger
    logger = StructuredLogger("tool.obsidian")
except ImportError:
    # Fallback for standalone or testing
    import logging
    logger = logging.getLogger("tool.obsidian") # type: ignore

import os
from datetime import datetime
from pathlib import Path

try:
    from mcp import ToolContext, ToolResponse, tool, types # Use SDK types
    SDK_AVAILABLE = True
except ImportError:
    # Stubs
    SDK_AVAILABLE = False
    class ToolContext: pass
    class ToolResponse: pass
    def tool(*args, **kwargs): return lambda f: f
    class types: class TextContent: pass # Add others if needed by stubs

from pydantic import BaseModel, Field, field_validator

# --- Models (Copied from models.py for self-containment or import) ---
class Note(BaseModel):
    # ... (Keep Note model as before) ...
    title: str = Field(..., description="The title of the note")
    content: str = Field(..., description="The content of the note")
    created_at: datetime = Field(default_factory=datetime.now, description="When the note was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When the note was last updated")
    tags: set[str] = Field(default_factory=set, description="Tags associated with the note")
    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}

class ObsidianConfig(BaseModel):
    # ... (Keep ObsidianConfig model as before, maybe load path differently) ...
     vault_path: Path = Field(default_factory=lambda: Path(os.path.expandvars(os.environ.get("VAULT_PATH", "docs-obsidian"))).resolve())
     excluded_folders: set[str] = Field(default_factory=lambda: {".git", ".obsidian", "node_modules"})
     supported_extensions: set[str] = Field(default_factory=lambda: {"md", "markdown"})
     template_folder: str = Field(default="templates")

     @field_validator("vault_path")
     def validate_vault_path(cls, v: Path) -> Path:
         path = Path(v)
         if not path.exists():
             logger.warning(f"Vault path does not exist: {path}") # Use logger
             try:
                 path.mkdir(parents=True, exist_ok=True)
                 logger.info(f"Created vault directory: {path}")
             except OSError as e:
                 logger.error(f"Failed to create vault directory {path}: {e}", exc_info=True)
                 raise ValueError(f"Could not create vault path: {path}") from e
         elif not path.is_dir():
             raise ValueError(f"Vault path is not a directory: {path}")
         logger.info(f"Using vault path: {path}")
         return path


# --- Tool Implementation ---
class ObsidianTool:
    # ... (Keep __init__ and _load_notes as before, using logger) ...
    def __init__(self):
        self.config = ObsidianConfig()
        self.notes: dict[str, Note] = {}
        self._load_notes() # Initial load

    def _load_notes(self) -> None:
        try:
            vault_path = self.config.vault_path
            logger.debug(f"Loading notes from vault: {vault_path}")
            if not vault_path.is_dir():
                logger.warning(f"Vault path is not a directory or doesn't exist: {vault_path}")
                return
            # Clear existing notes before reload
            current_notes = {}
            for file in vault_path.rglob("*"):
                # Check if it's in an excluded folder
                is_excluded = False
                for part in file.relative_to(vault_path).parts:
                    if part in self.config.excluded_folders:
                        is_excluded = True
                        break
                if is_excluded:
                    continue

                if file.is_file() and file.suffix[1:] in self.config.supported_extensions:
                    relative_path = str(file.relative_to(vault_path)).replace("\\", "/") # Normalize path sep
                    try:
                        with open(file, "r", encoding="utf-8") as f:
                            content = f.read()
                        stat = file.stat()
                        note = Note(
                            title=file.stem,
                            content=content,
                            created_at=datetime.fromtimestamp(stat.st_ctime),
                            updated_at=datetime.fromtimestamp(stat.st_mtime),
                            # Add tag parsing logic here if needed
                        )
                        current_notes[relative_path] = note
                        logger.debug(f"Loaded note: {relative_path}")
                    except Exception as e:
                        logger.error(f"Error loading note {file}: {e}")
            self.notes = current_notes # Update cache atomically
            logger.info(f"Loaded {len(self.notes)} notes from vault")
        except Exception as e:
            logger.error(f"Error loading notes: {e}", exc_info=True)

    def _resolve_and_validate_path(self, relative_path: str) -> Path:
        """Resolves path relative to vault and validates it's within the vault."""
        vault_base = self.config.vault_path
        # Basic normalization, prevent going up directories
        normalized_path_str = os.path.normpath(relative_path).lstrip('/\\')
        if '..' in normalized_path_str.split(os.path.sep):
            raise ValueError(f"Invalid path component '..' found in '{relative_path}'")

        # Ensure it ends with a valid extension if not already present
        if not any(normalized_path_str.lower().endswith(f".{ext}") for ext in self.config.supported_extensions):
             normalized_path_str += ".md" # Default to .md

        full_path = vault_base.joinpath(normalized_path_str).resolve()

        # Check if path is within the vault directory
        if not full_path.is_relative_to(vault_base): # Requires Python 3.9+
             # Fallback check for older Python (less robust)
             # if str(vault_base.resolve()) not in str(full_path.resolve().parent):
            raise ValueError(f"Path traversal attempt detected: '{relative_path}' resolves outside vault")

        return full_path


# Create singleton instance
obsidian_instance = ObsidianTool()

# --- MCP Tools ---
@tool(name="obsidian.list_notes", ...) # Keep decorator args
async def obsidian_list_notes(context: ToolContext, paths: list[str]) -> ToolResponse:
    # Reload notes before serving the request for freshness
    obsidian_instance._load_notes()
    results = {}
    errors = []
    for path_str in paths:
        try:
            # Validate path before accessing
            full_path = obsidian_instance._resolve_and_validate_path(path_str)
            relative_path = str(full_path.relative_to(obsidian_instance.config.vault_path)).replace("\\", "/")

            if relative_path in obsidian_instance.notes:
                results[relative_path] = obsidian_instance.notes[relative_path].model_dump(mode='json')
            elif full_path.exists() and full_path.is_file(): # Read on demand if not cached
                 with open(full_path, "r", encoding="utf-8") as f:
                     content = f.read()
                 stat = full_path.stat()
                 note = Note(title=full_path.stem, content=content, created_at=datetime.fromtimestamp(stat.st_ctime), updated_at=datetime.fromtimestamp(stat.st_mtime))
                 obsidian_instance.notes[relative_path] = note # Cache it
                 results[relative_path] = note.model_dump(mode='json')
            else:
                 errors.append(f"Note not found: {path_str}")
        except ValueError as e: # Catch validation errors
             errors.append(f"Invalid path '{path_str}': {e}")
        except Exception as e:
             logger.error(f"Error processing path '{path_str}' in list_notes: {e}", exc_info=True)
             errors.append(f"Error processing path '{path_str}'.")

    response_data = {"notes": results}
    if errors:
         response_data["errors"] = errors

    # Use SDK types for response content
    return ToolResponse(content=[types.TextContent(type="text", text=json.dumps(response_data, indent=2))])


@tool(name="obsidian.search_notes", ...) # Keep decorator args
async def obsidian_search_notes(context: ToolContext, query: str) -> ToolResponse:
    obsidian_instance._load_notes() # Refresh cache
    results = []
    query_lower = query.lower()
    try:
        for path, note in obsidian_instance.notes.items():
            if query_lower in note.title.lower() or query_lower in note.content.lower():
                results.append({"path": path, **note.model_dump(mode='json')})
        return ToolResponse(content=[types.TextContent(type="text", text=json.dumps(results, indent=2))])
    except Exception as e:
        logger.error(f"Error searching notes: {e}", exc_info=True)
        return ToolResponse(error={"code": "SEARCH_FAILED", "message": str(e)})


@tool(name="obsidian.save_note", ...) # Keep decorator args
async def obsidian_save_note(
    context: ToolContext, path: str, content: str, tags: list[str] | None = None
) -> ToolResponse:
    try:
        note_path = obsidian_instance._resolve_and_validate_path(path)
        note_path.parent.mkdir(parents=True, exist_ok=True)

        # Use anyio for async file write
        async with await anyio.open_file(note_path, "w", encoding="utf-8") as f:
            await f.write(content)

        # Update internal cache
        stat = await anyio.Path(note_path).stat()
        note = Note(
             title=note_path.stem,
             content=content,
             tags=set(tags or []),
             created_at=datetime.fromtimestamp(stat.st_ctime),
             updated_at=datetime.fromtimestamp(stat.st_mtime)
        )
        relative_path = str(note_path.relative_to(obsidian_instance.config.vault_path)).replace("\\", "/")
        obsidian_instance.notes[relative_path] = note

        logger.info(f"Note saved: {relative_path}")
        return ToolResponse(content=[types.TextContent(type="text", text=f"Note saved successfully: {relative_path}")])
    except ValueError as e: # Catch validation errors
        logger.warning(f"Invalid path provided for save: {e}", tool="obsidian.save_note", path=path)
        return ToolResponse(error={"code": "INVALID_PATH", "message": str(e)})
    except OSError as e:
        logger.error(f"Error saving note - OS error: {e}", tool="obsidian.save_note", path=path, exc_info=True)
        return ToolResponse(error={"code": "SAVE_FAILED", "message": f"Failed to write note: {e.strerror}"})
    except Exception as e:
        logger.error(f"Unexpected error saving note: {e}", tool="obsidian.save_note", path=path, exc_info=True)
        return ToolResponse(error={"code": "UNKNOWN_ERROR", "message": str(e)})