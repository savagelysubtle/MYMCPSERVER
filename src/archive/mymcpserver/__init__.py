"""MCP Server package for Obsidian integration.

This package provides a FastMCP server that exposes Obsidian vault functionality
through the Model Context Protocol (MCP).
"""

from __future__ import annotations

__all__ = ["main", "server", "logger"]
__version__ = "0.1.0"

# Standard library imports
import asyncio
import logging
import os
from pathlib import Path

# Local imports
from . import server
from .logging_config import setup_logging

# Initialize logging at package level
logs_path = os.getenv("LOGS_PATH", "logs")
logs_path = os.path.expandvars(logs_path)

# Determine if we should enable stdout logging based on transport
# We disable stdout when using stdio transport to avoid interference
transport_mode = os.getenv("MCP_TRANSPORT", "stdio")
enable_stdout = transport_mode != "stdio"

# Set up logging with resolved path
setup_logging(
    log_level=os.getenv("MCP_LOG_LEVEL", "INFO"),
    enable_stdout=enable_stdout,
    cursor_format=True,
    log_dir=Path(logs_path),
)

# Create package-level logger
logger = logging.getLogger("mymcpserver")
logger.debug("Package initialization complete")


def main():
    """Main entry point for the package."""
    try:
        logger.info("Starting MCP server from package entry point")
        asyncio.run(server.main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Error running server: {e}", exc_info=True)
        raise
