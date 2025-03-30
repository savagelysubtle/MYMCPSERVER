"""MCP Server implementation for Obsidian integration.

This module provides a FastMCP server that exposes Obsidian vault functionality
through the Model Context Protocol (MCP). Supports both stdio and SSE transports.
"""

from __future__ import annotations

__all__ = ["ObsidianTools", "mcp"]
__version__ = "0.1.0"

# Standard library imports
import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, TypeVar

# Third-party imports
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

# Handle imports for both module and direct script usage
try:
    from .logging_config import setup_logging
except ImportError:
    # Add parent directory to path for direct script usage
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from mymcpserver.logging_config import setup_logging

T = TypeVar("T")

# Load environment variables first
env_path = Path(__file__).parent.parent.parent / ".env.local"
load_dotenv(env_path)

# Check transport mode - must disable stdout logging when using stdio transport
transport_mode = os.getenv("MCP_TRANSPORT", "stdio")
enable_stdout = transport_mode != "stdio"

# Initialize logging with resolved path
logs_path = os.getenv("LOGS_PATH", "logs")
logs_path = os.path.expandvars(logs_path)
setup_logging(
    log_level=os.getenv("MCP_LOG_LEVEL", "DEBUG"),
    enable_stdout=enable_stdout,
    cursor_format=True,
    log_dir=Path(logs_path),
)

# Create logger for this module
logger = logging.getLogger("mymcpserver.server")
if not env_path.exists():
    logger.warning(f"No .env file found at {env_path}")

# Log transport mode decision
logger.info(f"Using transport mode: {transport_mode}, stdout logging: {enable_stdout}")

# Validate required environment variables
required_vars = ["VAULT_PATH", "PYTHONPATH", "LOGS_PATH"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(
        f"Missing required environment variables: {', '.join(missing_vars)}"
    )

# Create MCP server instance at module level with stdio transport
mcp = FastMCP("ObsidianMCP", transport=os.getenv("MCP_TRANSPORT", "stdio"))


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
    tags: Set[str] = Field(
        default_factory=set, description="Tags associated with the note"
    )

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class ServerConfig(BaseModel):
    """Configuration for the MCP server transport."""

    host: str = Field(default="localhost")
    port: int = Field(default=8000)
    transport: str = Field(default="stdio")

    @field_validator("transport")
    def validate_transport(cls, v: str) -> str:
        """Validate transport type."""
        if v not in ["stdio", "sse"]:
            raise ValueError(f"Invalid transport type: {v}. Must be 'stdio' or 'sse'")
        return v


class ObsidianConfig(BaseModel):
    """Configuration model for Obsidian integration."""

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


class ObsidianTools:
    """Tools for interacting with Obsidian vault."""

    def __init__(self, config: ObsidianConfig):
        self.config = config
        self.logger = logging.getLogger("mymcpserver.server")
        self.notes: Dict[str, Note] = {}
        self._load_notes()

    def _load_notes(self) -> None:
        """Load notes from the vault."""
        try:
            vault_path = self.config.vault_path
            self.logger.debug(f"Loading notes from vault: {vault_path}")

            if not vault_path.exists():
                self.logger.warning(f"Vault path does not exist: {vault_path}")
                return

            for file in vault_path.rglob("*"):
                if file.suffix[1:] in self.config.supported_extensions:
                    relative_path = str(file.relative_to(vault_path))
                    if not any(
                        excluded in relative_path
                        for excluded in self.config.excluded_folders
                    ):
                        try:
                            with open(file, "r", encoding="utf-8") as f:
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
                                self.logger.debug(f"Loaded note: {relative_path}")
                        except Exception as e:
                            self.logger.error(f"Error loading note {file}: {e}")
                            continue

            self.logger.info(f"Loaded {len(self.notes)} notes from vault")
        except Exception as e:
            self.logger.error(f"Error loading notes: {e}", exc_info=True)

    async def get_notes(self, paths: List[str]) -> Dict[str, Any]:
        """Get contents of specified notes."""
        try:
            results = {}
            for path in paths:
                if path in self.notes:
                    results[path] = self.notes[path].model_dump()
                else:
                    note_path = self.config.vault_path / path
                    if note_path.exists() and note_path.is_file():
                        content = await self._read_file(note_path)
                        note = Note(title=note_path.stem, content=content)
                        self.notes[path] = note
                        results[path] = note.model_dump()
            return {
                "content": [{"type": "text", "text": json.dumps(results, indent=2)}]
            }
        except Exception as e:
            self.logger.error(f"Error reading notes: {e}")
            return {"error": str(e)}

    async def search_notes(self, query: str) -> Dict[str, Any]:
        """Search for notes by name or content."""
        try:
            results = []
            for path, note in self.notes.items():
                if (
                    query.lower() in note.title.lower()
                    or query.lower() in note.content.lower()
                ):
                    results.append(note.model_dump())
            return {
                "content": [{"type": "text", "text": json.dumps(results, indent=2)}]
            }
        except Exception as e:
            self.logger.error(f"Error searching notes: {e}")
            return {"error": str(e)}

    async def save_note(
        self, path: str, content: str, tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Save a note to the vault."""
        try:
            note_path = self.config.vault_path / path
            note_path.parent.mkdir(parents=True, exist_ok=True)

            with open(note_path, "w", encoding="utf-8") as f:
                f.write(content)

            note = Note(title=note_path.stem, content=content, tags=set(tags or []))
            self.notes[path] = note

            return {
                "content": [
                    {"type": "text", "text": f"Note saved successfully: {path}"}
                ]
            }
        except Exception as e:
            self.logger.error(f"Error saving note: {e}")
            return {"error": str(e)}

    async def _read_file(self, path: Path) -> str:
        """Read file contents."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading file {path}: {e}")
            raise


# Initialize Obsidian tools
config = ObsidianConfig()
tools = ObsidianTools(config)


@mcp.tool()
async def read_notes(paths: List[str]) -> Dict[str, Any]:
    """Read the contents of multiple notes."""
    return await tools.get_notes(paths)


@mcp.tool()
async def search_notes(query: str) -> Dict[str, Any]:
    """Search for notes by name or content."""
    return await tools.search_notes(query)


@mcp.tool()
async def save_note(
    path: str, content: str, tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Save a note to the vault."""
    return await tools.save_note(path, content, tags)


async def main(server_config: Optional[ServerConfig] = None) -> None:
    """Main entry point for the MCP server.

    Args:
        server_config: Optional server configuration for transport settings.
                      If None, defaults will be used.
    """
    try:
        # Initialize server configuration
        if server_config is None:
            server_config = ServerConfig()

        logger.info("Starting MCP server")

        # Configure server based on transport
        if server_config.transport == "stdio":
            logger.info("Using stdio transport")
            os.environ["MCP_TRANSPORT"] = "stdio"
        else:  # SSE transport
            logger.info(
                f"Using SSE transport on {server_config.host}:{server_config.port}"
            )
            os.environ["MCP_TRANSPORT"] = "sse"
            os.environ["MCP_HOST"] = server_config.host
            os.environ["MCP_PORT"] = str(server_config.port)

        # Start the server
        logger.info("Starting server...")

        # Run the server with proper error handling
        try:
            mcp.run()
            logger.info("MCP server started successfully")
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error during run: {e}", exc_info=True)
            raise

    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        raise


def cli() -> None:
    """Command-line interface for the MCP server."""
    parser = argparse.ArgumentParser(
        description="Start the MCP server with specified transport"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport type (stdio or sse)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for SSE transport (default: localhost)",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port for SSE transport (default: 8000)"
    )

    args = parser.parse_args()
    config = ServerConfig(transport=args.transport, host=args.host, port=args.port)

    try:
        asyncio.run(main(config))
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
