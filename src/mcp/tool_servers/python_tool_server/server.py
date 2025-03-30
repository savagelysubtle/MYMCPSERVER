# src/tool_servers/python_tool_server/server.py
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

# --- SDK Import ---
try:
    import mcp  # type: ignore
    from mcp import ToolContext, ToolResponse, create_server  # type: ignore

    SDK_AVAILABLE = True
except ImportError:
    print("ERROR: MCP SDK not installed. Please install 'mcp'.", file=sys.stderr)
    SDK_AVAILABLE = False

    # Define stubs if needed for basic execution without SDK
    class ToolContext:
        """Stub class for ToolContext when SDK is not available."""

        pass

    class ToolResponse:
        """Stub class for ToolResponse when SDK is not available."""

        pass

    # More complete mock implementation to avoid linter errors
    class MagicMockServer:
        """Mock server implementation when SDK is not available."""

        def __init__(self) -> None:
            self.tools: dict[str, Callable] = {}
            self.name = "mock-server"
            self.description = "Mock Server (SDK not available)"
            self.version = "0.0.0"

        def register_tool(self, tool_func: Callable) -> None:
            """Mock register_tool method."""
            tool_name = getattr(tool_func, "_tool_name", tool_func.__name__)
            self.tools[tool_name] = tool_func

        def tool(self, name: str = "", description: str = "") -> Callable:
            """Mock tool decorator."""

            def decorator(func: Callable) -> Callable:
                func._tool_name = name or func.__name__
                func._tool_description = description
                return func

            return decorator

        def start_http(self, host: str = "127.0.0.1", port: int = 8001) -> None:
            """Mock start_http method that logs an error."""
            print(
                f"ERROR: Cannot start server on {host}:{port}: MCP SDK not installed.",
                file=sys.stderr,
            )

    def create_server(**kwargs: Any) -> "MagicMockServer":
        """Create a mock server when SDK is not available."""
        return MagicMockServer()

    def tool(*args: Any, **kwargs: Any) -> Callable[..., Any]:
        """Mock tool decorator when SDK is not available."""
        return lambda f: f


# --- Logging Setup ---
# Attempt to use central logger first
try:
    # Add project root for central logger import
    _project_root_for_logger = Path(__file__).resolve().parent.parent.parent.parent
    _src_path_for_logger = _project_root_for_logger / "src"
    if str(_src_path_for_logger) not in sys.path:
        sys.path.insert(0, str(_src_path_for_logger))
    from mcp_core.logger import StructuredLogger

    logger = StructuredLogger("tool_servers.python_tool_server")
    IS_STRUCTURED_LOGGING = True
except ImportError:
    import logging

    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("py-tool-server")  # type: ignore
    IS_STRUCTURED_LOGGING = False
    logger.warning("Could not import StructuredLogger. Using basic logging.")  # type: ignore

# --- Tool Imports ---
# Ensure these imports succeed
try:
    from .n1.tool import obsidian_list_notes, obsidian_save_note, obsidian_search_notes
    from .n2.tool import (
        aichemist_calculate_property,
        aichemist_get_molecule,
        aichemist_list_molecules,
    )

    TOOLS_IMPORTED = True
except ImportError as e:
    logger.error(f"Failed to import tool modules: {e}", exc_info=True)  # type: ignore
    TOOLS_IMPORTED = False

# --- Server Setup ---
if SDK_AVAILABLE:
    server = create_server(
        name="python-tool-server",
        description="Python Tool Server for MCP",
        version="0.1.0",  # Extract from pyproject?
    )

    # Register tools only if they were imported successfully
    if TOOLS_IMPORTED:
        logger.info("Registering Obsidian tools...")
        server.register_tool(obsidian_list_notes)
        server.register_tool(obsidian_search_notes)
        server.register_tool(obsidian_save_note)

        logger.info("Registering AIChemist tools...")
        server.register_tool(aichemist_get_molecule)
        server.register_tool(aichemist_list_molecules)
        server.register_tool(aichemist_calculate_property)
    else:
        logger.error("Tool imports failed, no tools will be registered.")

    # Add a simple health check endpoint if using HTTP
    @server.tool(
        name="health", description="Check tool server health"
    )  # Expose as a tool
    async def health_check(ctx: ToolContext) -> dict:
        return {"status": "healthy", "registered_tools": list(server.tools.keys())}

else:
    # Create a more complete mock server if SDK is missing
    server = create_server(
        name="python-tool-server-mock",
        description="Mock Python Tool Server (SDK not available)",
        version="0.1.0",
    )

    # Even with mock server, we can still register the tools for bookkeeping
    if TOOLS_IMPORTED:
        logger.info("Registering tools to mock server...")  # type: ignore
        try:
            server.register_tool(obsidian_list_notes)
            server.register_tool(obsidian_search_notes)
            server.register_tool(obsidian_save_note)
            server.register_tool(aichemist_get_molecule)
            server.register_tool(aichemist_list_molecules)
            server.register_tool(aichemist_calculate_property)
        except Exception as e:
            logger.error(f"Failed to register tools to mock server: {e}")  # type: ignore

    # Add a simple health check endpoint to the mock server
    @server.tool(name="health", description="Check tool server health (mock)")
    async def health_check_mock(ctx: Any) -> dict:
        return {"status": "mocked", "registered_tools": list(server.tools.keys())}


# --- Server Start ---
def start_server(host: str = "127.0.0.1", port: int = 8001) -> None:
    """Start the Python Tool Server (Blocking)."""
    if not SDK_AVAILABLE:
        logger.critical("Cannot start server: MCP SDK is not installed.")  # type: ignore
        return

    logger.info(f"Starting Python Tool Server HTTP listener on {host}:{port}")  # type: ignore
    try:
        # start_http is blocking, designed to be run directly or via uvicorn command
        server.start_http(host=host, port=port)
    except Exception as e:
        logger.critical(f"Failed to start Python Tool Server: {e}", exc_info=True)  # type: ignore


if __name__ == "__main__":
    # Standalone execution path
    # Load .env relative to *this* file for standalone
    from dotenv import load_dotenv

    env_path = Path(__file__).parent / ".env"  # Example: Look for .env in this dir
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        if IS_STRUCTURED_LOGGING:
            logger.info(f"Loaded environment variables from {env_path}")
        else:
            print(f"INFO: Loaded environment variables from {env_path}")

    standalone_host = os.environ.get("HOST", "127.0.0.1")
    standalone_port = int(os.environ.get("PORT", 8001))

    # Ensure logging is somewhat configured if running standalone
    if not IS_STRUCTURED_LOGGING:
        logging.basicConfig(
            level=os.environ.get("LOG_LEVEL", "INFO").upper(),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.info("Basic logging configured for standalone execution.")  # type: ignore

    start_server(host=standalone_host, port=standalone_port)
