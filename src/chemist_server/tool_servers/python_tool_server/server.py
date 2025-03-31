# src/tool_servers/python_tool_server/server.py
import asyncio
import importlib.util
import logging
import os
import sys
import time
import traceback
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Attempt to record startup time before any other operations
_startup_timestamp = time.time()

# Direct file logging for startup regardless of other logs
try:
    _startup_log_dir = Path("logs/tools/python-tool-server")
    _startup_log_dir.mkdir(parents=True, exist_ok=True)
    _startup_log_file = (
        _startup_log_dir / f"startup_{time.strftime('%Y%m%d_%H%M%S')}.log"
    )

    with open(_startup_log_file, "w") as f:
        f.write("=== PYTHON TOOL SERVER STARTUP LOG ===\n")
        f.write(f"Started at: {time.ctime(_startup_timestamp)}\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"Platform: {sys.platform}\n")
        f.write(f"Working directory: {os.getcwd()}\n")
        f.write(f"Script path: {__file__}\n")
        f.write(f"Python path: {sys.path}\n\n")
        f.write("Environment variables:\n")
        for key, value in sorted(os.environ.items()):
            if key.startswith(("MCP_", "PYTHON")):
                f.write(f"  {key}={value}\n")
except Exception as e:
    print(f"Failed to create startup log: {e}", file=sys.stderr)

from dotenv import load_dotenv

# --- Direct console debug printing ---
print("=== PYTHON TOOL SERVER INITIALIZING ===", file=sys.stderr)

# --- Logging Setup - Initialize early ---
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for maximum visibility
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr),  # Log to stderr for immediate visibility
    ],
)


# --- Type Definitions ---
@dataclass
class ServerConfig:
    """Server configuration."""

    host: str = "localhost"
    port: int = 8080
    log_dir: str = "logs"


# --- Logging Setup ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Ensure DEBUG level explicitly
IS_STRUCTURED_LOGGING = False
session_id = str(uuid.uuid4())

print(f"=== PYTHON TOOL SERVER SESSION: {session_id} ===", file=sys.stderr)

# Log startup info to the file as well
try:
    with open(_startup_log_file, "a") as f:
        f.write(f"\nSession ID: {session_id}\n")
        f.write(f"Logger initialized with level: {logger.level}\n")
except Exception:
    pass  # Already reported earlier if there's an issue


# Configure structured logging if needed
class StructuredLogAdapter(logging.LoggerAdapter):
    """Adapter for structured logging that accepts keyword arguments."""

    def process(self, msg, kwargs):
        # Extract any custom fields from kwargs
        extra_fields = {}
        for key in list(kwargs.keys()):
            if key not in ["exc_info", "stack_info", "stacklevel", "extra"]:
                extra_fields[key] = kwargs.pop(key)

        # If we have extra fields, format the message with them
        if extra_fields:
            if isinstance(msg, str):
                msg = f"{msg} | " + " | ".join(
                    f"{k}={v}" for k, v in extra_fields.items()
                )

        return msg, kwargs


# Configure the structured logging adapter if enabled
if IS_STRUCTURED_LOGGING:
    logger = StructuredLogAdapter(logger, {})

# --- SDK Import ---
try:
    # Check if mcp is available without importing the whole module
    if importlib.util.find_spec("mcp") is not None:
        from mcp import ToolContext, ToolResponse, create_server  # type: ignore

        SDK_AVAILABLE = True
        # Log SDK info to the startup file
        try:
            with open(_startup_log_file, "a") as f:
                f.write("\nMCP SDK found and imported successfully\n")
                f.write(
                    f"SDK Version: {getattr(sys.modules.get('mcp'), '__version__', 'unknown')}\n"
                )
        except Exception:
            pass
    else:
        SDK_AVAILABLE = False
        try:
            with open(_startup_log_file, "a") as f:
                f.write("\nMCP SDK module not found in sys.path\n")
        except Exception:
            pass
except ImportError as e:
    print("ERROR: MCP SDK not installed. Please install 'mcp'.", file=sys.stderr)
    SDK_AVAILABLE = False
    try:
        with open(_startup_log_file, "a") as f:
            f.write(f"\nImportError when importing MCP SDK: {e}\n")
            f.write(f"Traceback:\n{traceback.format_exc()}\n")
    except Exception:
        pass


# Define stubs if needed for basic execution without SDK
class ToolContext:
    """Stub class for ToolContext when SDK is not available."""

    pass


class ToolResponse:
    """Stub class for ToolResponse when SDK is not available."""

    pass


# Mock implementation for when SDK is not available
class MagicMockServer:
    """Mock server for when MCP SDK is not available."""

    def __init__(self):
        self.host = "localhost"
        self.port = 8080
        self.tools = {}
        self.name = "mock-server"
        self.description = "Mock Server (SDK not available)"
        self.version = "0.0.0"
        logger.warning("Mock server initialized - MCP SDK not available")

    def start(self, host: str = "localhost", port: int = 8080):
        """Mock start method."""
        self.host = host
        self.port = port
        logger.info(f"Mock server starting on {host}:{port}")
        return self

    def tool(self, name: str = "", description: str = ""):
        """Mock tool decorator."""

        def decorator(func):
            tool_name = name or func.__name__
            self.tools[tool_name] = func
            logger.debug(f"Registered mock tool: {tool_name}")
            return func

        return decorator

    async def on_startup(self, app):
        """Mock startup handler."""
        logger.info(f"Mock server startup event triggered | Session: {session_id}")

    async def on_shutdown(self, app):
        """Mock shutdown handler."""
        logger.info(f"Mock server shutdown event triggered | Session: {session_id}")


def create_server(**kwargs: Any) -> "MagicMockServer":
    """Create a mock server when SDK is not available."""
    return MagicMockServer()


def tool(*args: Any, **kwargs: Any) -> Callable[..., Any]:
    """Mock tool decorator when SDK is not available."""
    return lambda f: f


def log_context(func):
    """Decorator to add context to function logging."""

    async def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"Entering {func_name} | Args: {args} | Kwargs: {kwargs}")
        try:
            result = (
                await func(*args, **kwargs)
                if asyncio.iscoroutinefunction(func)
                else func(*args, **kwargs)
            )
            logger.debug(f"Exiting {func_name} | Status: success")
            return result
        except Exception as e:
            logger.error(
                f"Error in {func_name} | Error: {type(e).__name__} - {str(e)}",
                exc_info=True,
            )
            raise

    return wrapper


def configure_server(config: ServerConfig) -> None:
    """Configure server settings."""
    try:
        log_dir = os.path.join(config.log_dir, "tools")
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(
            log_dir, f"python_tool_server_{config.host}_{config.port}.log"
        )
        logger.info(
            f"Server configuration complete | Host: {config.host} | Port: {config.port} | Log: {log_file} | Session: {session_id}"
        )

    except Exception as e:
        logger.error(
            f"Server configuration failed | Error: {type(e).__name__} - {str(e)} | Session: {session_id}"
        )
        raise


def load_environment(env_path: str) -> None:
    """Load environment variables."""
    try:
        load_dotenv(env_path)
        logger.info(f"Environment loaded | File: {env_path} | Session: {session_id}")
    except Exception as e:
        logger.error(
            f"Environment loading failed | Error: {type(e).__name__} - {str(e)} | Session: {session_id}"
        )
        raise


# --- Tool Imports ---
try:
    from .cliTool.cli_tool_registry import register_tools as register_cli_tools

    logger.info("Tool modules imported successfully: cli_tool_registry")
    TOOLS_IMPORTED = True
except ImportError as e:
    logger.error(
        f"Failed to import tool modules: {type(e).__name__} - {str(e)}", exc_info=True
    )
    TOOLS_IMPORTED = False

# --- Server Setup ---
if SDK_AVAILABLE:
    logger.info(
        f"Initializing production server (SDK: {SDK_AVAILABLE}, Tools: {TOOLS_IMPORTED})"
    )
    server = create_server(
        name="python-tool-server",
        description="Python Tool Server for MCP",
        version="0.1.0",
    )

    if TOOLS_IMPORTED:
        try:
            register_cli_tools(server)
            registered_tools = list(server.tools.keys())
            logger.info(
                f"CLI tools registration complete - {len(registered_tools)} tools registered: {registered_tools}"
            )
        except Exception as e:
            logger.error(
                f"CLI tools registration failed: {type(e).__name__} - {str(e)}",
                exc_info=True,
            )
    else:
        logger.error("Tool registration skipped: imports failed")

    @server.tool(name="health", description="Check tool server health")
    @log_context
    async def health_check(ctx: ToolContext) -> dict:
        health_info = {
            "status": "healthy",
            "registered_tools": list(server.tools.keys()),
            "logging_type": "structured" if IS_STRUCTURED_LOGGING else "basic",
            "sdk_version": getattr(sys.modules.get("mcp"), "__version__", "unknown"),
            "session_id": session_id,
            "uptime": time.time() - server_start_time,
        }
        logger.debug(f"Health check executed: {health_info}")
        return health_info


# --- Server Start ---
server_start_time = time.time()


@server.on_startup
@log_context
async def startup(server):
    global server_start_time
    server_start_time = time.time()

    startup_info = {
        "host": server.host,
        "port": server.port,
        "sdk_available": SDK_AVAILABLE,
        "tools_imported": TOOLS_IMPORTED,
        "logging_mode": "structured" if IS_STRUCTURED_LOGGING else "basic",
        "python_version": sys.version,
        "session_id": session_id,
        "status": "starting",
    }

    logger.info(f"Server starting up | Info: {startup_info}")


@server.on_shutdown
@log_context
async def shutdown(server):
    uptime = time.time() - server_start_time
    logger.info(f"Server shutting down | Uptime: {uptime:.2f}s | Session: {session_id}")


def start_server(host: str = "localhost", port: int = 8080):
    """Start the Python Tool Server."""
    server_start = time.time()
    # Directly log to the startup file
    try:
        with open(_startup_log_file, "a") as f:
            f.write(f"\n=== STARTING SERVER at {time.ctime(server_start)} ===\n")
            f.write(f"Host: {host}\n")
            f.write(f"Port: {port}\n")
            f.write(f"SDK Available: {SDK_AVAILABLE}\n")
            f.write(f"Tools Imported: {TOOLS_IMPORTED}\n")
    except Exception:
        pass

    print(f"=== STARTING PYTHON TOOL SERVER ON {host}:{port} ===", file=sys.stderr)
    try:
        if SDK_AVAILABLE:
            logger.info(f"Starting server on {host}:{port}")
            print(f"=== SDK AVAILABLE - SERVER OBJECT: {server} ===", file=sys.stderr)
            server.start(host=host, port=port)
        else:
            err_msg = "Cannot start server: MCP SDK not available"
            logger.error(err_msg)
            print(f"=== ERROR: {err_msg} ===", file=sys.stderr)
            # Log the error to startup file
            try:
                with open(_startup_log_file, "a") as f:
                    f.write(f"\nERROR: {err_msg}\n")
            except Exception:
                pass
            return MagicMockServer()
    except Exception as e:
        err_msg = f"Failed to start server: {type(e).__name__} - {str(e)}"
        logger.error(err_msg, exc_info=True)
        print(f"=== EXCEPTION: {err_msg} ===", file=sys.stderr)

        # Detailed error logging
        traceback_text = traceback.format_exc()
        print(f"=== TRACEBACK: {traceback_text} ===", file=sys.stderr)

        # Log the error to startup file
        try:
            with open(_startup_log_file, "a") as f:
                f.write(f"\nERROR STARTING SERVER: {err_msg}\n")
                f.write(f"Traceback:\n{traceback_text}\n")
        except Exception:
            pass

        return MagicMockServer()


def load_env(env_file: str = ".env") -> None:
    """Load environment variables from file."""
    try:
        load_dotenv(env_file)
        logger.info(f"Environment loaded from {env_file}")
    except Exception as e:
        logger.error(f"Failed to load environment from {env_file}: {str(e)}")


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv

        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            logger.info(f"Environment loaded | File: {str(env_path)} | Status: success")

        standalone_host = os.environ.get("HOST", "127.0.0.1")
        standalone_port = int(os.environ.get("PORT", 8001))

        logger.info(
            f"Standalone mode initialization | Host: {standalone_host} | Port: {standalone_port} | "
            f"Env file: {str(env_path) if env_path.exists() else None} | Status: starting"
        )

        start_server(host=standalone_host, port=standalone_port)
    except Exception as e:
        logger.critical(
            f"Fatal error in standalone mode | Error: {str(e)} | Error type: {type(e).__name__} | "
            f"Session ID: {session_id} | Status: crashed",
            exc_info=True,
        )
        sys.exit(1)
    finally:
        logger.info(
            f"=== PYTHON TOOL SERVER STANDALONE SESSION END === | "
            f"Session ID: {session_id} | Uptime: {time.time() - server_start_time:.2f}s | Status: shutdown"
        )
