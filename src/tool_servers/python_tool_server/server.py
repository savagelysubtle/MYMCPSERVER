"""Python Tool Server implementation using MCP SDK."""

import os
import sys
from pathlib import Path

try:
    import mcp
    from mcp import ToolContext, ToolResponse, create_server
except ImportError:
    print("MCP SDK not installed. Please install it using 'pip install mcp-sdk'")
    raise

# Import tools
from .n1.tool import obsidian_list_notes, obsidian_save_note, obsidian_search_notes
from .n2.tool import (
    aichemist_calculate_property,
    aichemist_get_molecule,
    aichemist_list_molecules,
)

# Add project root to path to allow importing mcp_core
# Assumes this file is src/tool_servers/python_tool_server/server.py
project_root = Path(__file__).resolve().parent.parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configure logging using StructuredLogger from mcp_core
try:
    from mcp_core.logger import StructuredLogger

    logger = StructuredLogger("py-tool-server")
    logger.info("Python Tool Server logging initialized.")
except ImportError as e:
    # Fallback basic logging if mcp_core logger cannot be imported
    import logging

    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    logger = logging.getLogger("py-tool-server")
    logger.error(
        f"Could not import StructuredLogger from mcp_core: {e}. Using basic logging."
    )

# Create MCP server
server = create_server(
    name="python-tool-server", description="Python Tool Server for MCP", version="0.1.0"
)

# Register Obsidian tools
server.register_tool(obsidian_list_notes)
server.register_tool(obsidian_search_notes)
server.register_tool(obsidian_save_note)

# Register AIChemist tools
server.register_tool(aichemist_get_molecule)
server.register_tool(aichemist_list_molecules)
server.register_tool(aichemist_calculate_property)


# Configure server transport
def start_server():
    """Start the Python Tool Server."""
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8001"))

    # Start server with HTTP transport
    server.start_http(host=host, port=port)


if __name__ == "__main__":
    start_server()
