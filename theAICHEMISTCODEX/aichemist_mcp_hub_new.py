"""
AIchemist MCP Hub

This script sets up a central MCP server using FastMCP that aggregates multiple specialized tools
for working with the AIchemist codebase, Git repositories, file system, and memory bank.
"""

import asyncio
import functools
import json
import logging
import subprocess
import sys
import time  # Replace import_time with standard time module
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

# Load environment variables from .env and .env.local files
try:
    from dotenv import load_dotenv

    # Load base .env file
    env_file = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_file)

    # Load local overrides if present
    env_local_file = Path(__file__).parent.parent.parent / ".env.local"
    if env_local_file.exists():
        load_dotenv(env_local_file, override=True)

    print(f"Loaded environment variables from {env_file}")
    if env_local_file.exists():
        print(f"Loaded local overrides from {env_local_file}")
except ImportError:
    print(
        "Warning: python-dotenv not installed. Environment variables will not be loaded from .env files."
    )

import psutil


# Virtual environment verification
def verify_virtual_env() -> None:
    """Verify that we're running in a virtual environment."""
    if sys.prefix == sys.base_prefix:
        print("Error: Virtual environment not activated!")
        print("Please activate your virtual environment:")
        print("Windows: .\\venv\\Scripts\\activate")
        print("Unix/macOS: source .venv/bin/activate")
        sys.exit(1)

    print(f"Virtual environment active: {sys.prefix}")


# Verify virtual environment before imports
verify_virtual_env()

import git  # GitPython library
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.lowlevel import Server

# Path to AIchemist project root - adjust as needed
AICHEMIST_ROOT = Path(__file__).parent.resolve()

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to INFO to see more diagnostic messages
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(AICHEMIST_ROOT / "mcp_server.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("aichemist_mcp")

# Print startup diagnostic information
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {Path.cwd()}")
logger.info(f"AIchemist root: {AICHEMIST_ROOT}")

# Check MCP package version
try:
    import mcp

    mcp_version = getattr(mcp, "__version__", "unknown")
    logger.info(f"MCP version: {mcp_version}")
except ImportError:
    logger.warning("Could not import MCP module to determine version")

# Enhanced command with more options
THINKING_SERVER_CMD = ("npx", "-y", "@modelcontextprotocol/server-sequential-thinking")
# Fallback command if npx is not in PATH but installed via npm
NPX_FALLBACK_PATHS = [
    str(Path.home() / "AppData" / "Roaming" / "npm" / "npx.cmd"),  # Windows
    str(Path.home() / ".npm" / "bin" / "npx"),  # Linux/macOS
    "/usr/local/bin/npx",  # Common global install location
]

# Define server port constants
THINKING_SERVER_PORT = 8778

# Initialize Git repository object
try:
    repo = git.Repo(AICHEMIST_ROOT)
except git.InvalidGitRepositoryError:
    # Handle case where AICHEMIST_ROOT is not a Git repository
    repo = None
    logger.warning(
        f"Warning: {AICHEMIST_ROOT} is not a Git repository. Git operations will be unavailable."
    )

# Server state - moved to global scope for access in lifespan manager
thinking_server_process = None


def start_thinking_server() -> bool:
    """Start the sequential thinking server as a subprocess."""
    global thinking_server_process
    try:
        # Log the attempt
        logger.info(
            f"Starting Sequential Thinking server with command: {' '.join(THINKING_SERVER_CMD)}"
        )

        # First attempt with standard command
        thinking_server_process = subprocess.Popen(
            THINKING_SERVER_CMD,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )

        # Check if process started successfully
        if thinking_server_process.poll() is not None:
            stderr = (
                thinking_server_process.stderr.read()
                if thinking_server_process.stderr
                else "No error output"
            )
            logger.error(f"Sequential Thinking server failed to start. Error: {stderr}")
            logger.error(
                "Make sure you have Node.js installed and can run 'npx' commands."
            )
            return False

        logger.info(
            f"Sequential Thinking server started with PID: {thinking_server_process.pid}"
        )
        return True
    except FileNotFoundError:
        # Try fallback paths if standard npx command fails
        logger.warning("Standard 'npx' command not found, trying fallback paths...")

        for npx_path in NPX_FALLBACK_PATHS:
            if Path(npx_path).exists():
                try:
                    logger.info(f"Trying npx at: {npx_path}")
                    fallback_cmd = (
                        npx_path,
                        "-y",
                        "@modelcontextprotocol/server-sequential-thinking",
                    )

                    thinking_server_process = subprocess.Popen(
                        fallback_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        shell=False,
                    )

                    if thinking_server_process.poll() is None:
                        logger.info(
                            f"Sequential Thinking server started using {npx_path}"
                        )
                        return True
                except Exception as inner_e:
                    logger.warning(f"Failed with fallback path {npx_path}: {inner_e}")
                    continue

        # If we get here, all attempts failed
        logger.error(
            "Sequential Thinking server failed to start: 'npx' command not found"
        )
        logger.error("Make sure you have Node.js installed and npx is in your PATH")
        logger.error("Installation guide: https://nodejs.org/en/download/")
        logger.error("Sequential Thinking tool will not be available.")
        return False
    except Exception as e:
        logger.error(f"Error starting Sequential Thinking server: {e}")
        logger.error("Sequential Thinking tool will not be available.")
        return False


@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[dict[str, Any]]:
    """
    Manage server startup and shutdown lifecycle with enhanced health checks.

    This context manager handles the initialization of resources when the server
    starts and ensures proper cleanup when the server stops.
    """
    global thinking_server_process

    logger.info("Starting AIchemist MCP Hub...")
    logger.info(f"Root Directory: {AICHEMIST_ROOT}")

    # Initialize resources with health check
    resources = {
        "repo": repo,
        "root_path": AICHEMIST_ROOT,
        "health_status": {"is_healthy": True, "last_check": None, "errors": []},
    }

    async def check_server_health() -> bool:
        """Check the health of all server components."""
        try:
            # Check Git repository health
            if repo is not None:
                repo.git.status()

            # Check thinking server health if running
            if thinking_server_process and thinking_server_process.poll() is None:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"http://localhost:{THINKING_SERVER_PORT}/health", timeout=5.0
                    )
                    if response.status_code != 200:
                        raise Exception("Thinking server health check failed")

            # Update health status
            resources["health_status"].update(
                {"is_healthy": True, "last_check": time.time(), "errors": []}
            )
            return True

        except Exception as e:
            resources["health_status"].update(
                {
                    "is_healthy": False,
                    "last_check": time.time(),
                    "errors": [str(e)],
                }
            )
            logger.error(f"Health check failed: {e}")
            return False

    # Start the Sequential Thinking server if needed
    thinking_success = start_thinking_server()
    if thinking_success:
        resources["thinking_server"] = thinking_server_process

    # Initial health check
    await check_server_health()

    try:
        # Start periodic health checks
        async def periodic_health_check():
            while True:
                await asyncio.sleep(300)  # Check every 5 minutes
                await check_server_health()

        # Start health check task
        health_check_task = asyncio.create_task(periodic_health_check())
        resources["health_check_task"] = health_check_task

        # Resources will be available in tool handlers via server.request_context
        yield resources

    finally:
        # Cleanup on server shutdown
        logger.info("Shutting down AIchemist MCP Hub...")

        # Cancel health check task
        if "health_check_task" in resources:
            resources["health_check_task"].cancel()
            try:
                await resources["health_check_task"]
            except asyncio.CancelledError:
                pass

        # Stop thinking server
        if thinking_server_process:
            try:
                thinking_server_process.terminate()
                logger.info("Sequential Thinking server stopped")
            except Exception as e:
                logger.error(f"Error stopping Sequential Thinking server: {e}")

        # Final cleanup
        logger.info("Server shutdown complete.")


# Create an MCP server with lifecycle management
mcp = FastMCP("AIchemist MCP Hub", log_level="ERROR", lifespan=server_lifespan)

# Print startup information for debugging
logger.info("Starting AIchemist MCP Hub...")
logger.info("Server Name: AIchemist MCP Hub")
logger.info("Log Level: ERROR")
logger.info(f"Root Directory: {AICHEMIST_ROOT}")

# List all available tools for debugging
logger.info("\nAvailable tools:")
for tool_name in dir(mcp):
    if not tool_name.startswith("_") and callable(getattr(mcp, tool_name)):
        logger.info(f"- {tool_name}")

# Print all decorated functions - using a list copy to avoid runtime error
logger.info("\nDecorated tools:")
# Create a list copy of the globals dictionary items to prevent modification during iteration
globals_copy = list(globals().items())
for name, func in globals_copy:
    if callable(func) and hasattr(func, "__wrapped__"):
        logger.info(f"- {name}")


# Create a decorator to track tool usage
def track_tool_usage(func: Callable) -> Callable:
    """
    A decorator that adds the tool name to the response and provides error handling.

    This decorator wraps tool functions to provide:
    1. Consistent error handling with specific exception types
    2. Tool name tracking in response
    3. Logging of tool usage and errors
    4. Memory usage monitoring and limits
    5. Performance tracking
    """

    @functools.wraps(func)
    async def wrapper(
        *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        tool_name = func.__name__
        start_time = time.time()
        logger.info(f"Tool call: {tool_name} with args: {kwargs}")

        # Memory usage monitoring
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Set memory limit (100MB by default, configurable)
        # Check if the function has a tool_metadata attribute with memory_limit
        if hasattr(func, "tool_metadata") and isinstance(func.tool_metadata, dict):
            memory_limit = func.tool_metadata.get("memory_limit", 100)
        else:
            # Get memory_limit from kwargs if present, otherwise use default
            memory_limit = (
                kwargs.pop("memory_limit", 100) if "memory_limit" in kwargs else 100
            )

        try:
            # Get the original function's result
            result = await func(*args, **kwargs)

            # Add the tool name to the result if it's a dictionary
            if isinstance(result, dict):
                result["tool_used"] = tool_name

            # Add performance metrics
            end_time = time.time()
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = end_memory - start_memory
            execution_time = end_time - start_time

            # Log performance metrics
            logger.info(
                f"Tool {tool_name} completed in {execution_time:.2f}s using {memory_used:.2f}MB"
            )

            # Add metrics to result if it's a dictionary
            if isinstance(result, dict):
                result["metrics"] = {
                    "execution_time_ms": int(execution_time * 1000),
                    "memory_used_mb": round(memory_used, 2),
                }

            return result

        except MemoryError:
            logger.error(f"Memory limit exceeded in tool {tool_name}", exc_info=True)
            return {
                "error": f"Memory limit exceeded in {tool_name}",
                "tool_used": tool_name,
                "status": "error",
                "error_type": "memory_limit_exceeded",
            }
        except httpx.TimeoutException as e:
            logger.error(f"Timeout in tool {tool_name}: {e!s}", exc_info=True)
            return {
                "error": f"Request timeout in {tool_name}: {e!s}",
                "tool_used": tool_name,
                "status": "error",
                "error_type": "timeout",
            }
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error(f"HTTP error in tool {tool_name}: {e!s}", exc_info=True)
            return {
                "error": f"HTTP request error in {tool_name}: {e!s}",
                "tool_used": tool_name,
                "status": "error",
                "error_type": "http_error",
            }
        except (FileNotFoundError, PermissionError) as e:
            logger.error(
                f"File system error in tool {tool_name}: {e!s}", exc_info=True
            )
            return {
                "error": f"File system error in {tool_name}: {e!s}",
                "tool_used": tool_name,
                "status": "error",
                "error_type": "file_system_error",
            }
        except json.JSONDecodeError as e:
            logger.error(
                f"JSON parsing error in tool {tool_name}: {e!s}", exc_info=True
            )
            return {
                "error": f"JSON parsing error in {tool_name}: {e!s}",
                "tool_used": tool_name,
                "status": "error",
                "error_type": "json_error",
            }
        except Exception as e:
            # Log the error
            logger.error(f"Error in tool {tool_name}: {e!s}", exc_info=True)

            # Return an error result instead of raising an exception
            return {
                "error": f"Tool execution error in {tool_name}: {e!s}",
                "tool_used": tool_name,
                "status": "error",
                "error_type": "unknown_error",
            }
        finally:
            # Check for memory leaks
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            if current_memory - start_memory > memory_limit:
                logger.warning(
                    f"Possible memory leak detected in {tool_name}: {current_memory - start_memory:.2f}MB used"
                )

    return wrapper


# Helper function to create a tool with schema validation
def mcp_tool(
    description: str,
    schema: dict[str, Any] | None = None,
    returns: dict[str, Any] | None = None,
    memory_limit: int = 100,  # Memory limit in MB
    timeout: float = 30.0,  # Timeout in seconds
    category: str = "",  # Tool category for organization
    tags: list[str] | None = None,  # Tags for filtering tools
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Create a tool with enhanced schema validation and resource management.

    Args:
        description: Tool description
        schema: JSON schema for tool arguments
        returns: JSON schema for return value
        memory_limit: Maximum memory usage in MB
        timeout: Maximum execution time in seconds
        category: Tool category for organization
        tags: Tags for filtering tools

    Returns:
        Decorated tool function
    """
    tags = tags or []

    # Create schema validator function
    def validate_schema(data: dict, schema_def: dict) -> tuple[bool, str]:
        """Validate data against a JSON schema."""
        try:
            from jsonschema import ValidationError, validate

            validate(instance=data, schema=schema_def)
            return True, ""
        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Schema validation error: {e!s}"

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Set default schema if none provided
        tool_schema = schema or {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        }
        tool_returns = returns or {
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }

        # Add standard error properties to return schema
        if "properties" not in tool_returns:
            tool_returns["properties"] = {}

        tool_returns["properties"].update(
            {
                "error": {"type": "string"},
                "status": {"type": "string", "enum": ["success", "error"]},
                "error_type": {"type": "string"},
                "tool_used": {"type": "string"},
                "metrics": {
                    "type": "object",
                    "properties": {
                        "execution_time_ms": {"type": "integer"},
                        "memory_used_mb": {"type": "number"},
                    },
                },
            }
        )

        # Store metadata for introspection
        func.tool_metadata = {
            "description": description,
            "schema": tool_schema,
            "returns": tool_returns,
            "memory_limit": memory_limit,
            "timeout": timeout,
            "category": category,
            "tags": tags,
        }

        # Create the enhanced wrapped function
        @track_tool_usage
        @functools.wraps(func)
        async def wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
            # Log memory limit for debugging
            logger.debug(f"Tool {func.__name__} memory limit: {memory_limit}MB")

            # Validate input against schema
            if schema:
                valid, error = validate_schema(kwargs, tool_schema)
                if not valid:
                    logger.error(
                        f"Schema validation failed for {func.__name__}: {error}"
                    )
                    return {
                        "error": f"Invalid arguments: {error}",
                        "tool_used": func.__name__,
                        "status": "error",
                        "error_type": "validation_error",
                    }

            # Add timeout to httpx calls if present in kwargs
            for k, v in kwargs.items():
                if isinstance(v, httpx.Client) or isinstance(v, httpx.AsyncClient):
                    if not hasattr(v, "timeout") or v.timeout is None:
                        v.timeout = timeout

            # Execute function with timeout
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except TimeoutError:
                logger.error(f"Tool {func.__name__} timed out after {timeout} seconds")
                return {
                    "error": f"Tool execution timed out after {timeout} seconds",
                    "tool_used": func.__name__,
                    "status": "error",
                    "error_type": "timeout_error",
                }

        # Add route registration info for introspection
        wrapper.route_info = {"name": func.__name__, "description": description}
        wrapper.__doc__ = description

        # Have FastMCP handle registration at run time by adding description and name
        wrapper._mcp_tool_name = func.__name__
        wrapper._mcp_tool_description = description

        # Register this tool with FastMCP
        setattr(mcp, func.__name__, wrapper)

        return wrapper

    return decorator


# Helper function to register all enhanced tools with FastMCP
def register_enhanced_tools() -> None:
    """
    Register all enhanced tools with the FastMCP instance.
    This function is called during server startup.
    """
    logger.info("Registering enhanced tools with FastMCP...")
    tool_count = 0

    # Introspect globals() to find functions with _mcp_tool attributes
    for _, func in globals().items():
        if (
            callable(func)
            and hasattr(func, "_mcp_tool_name")
            and hasattr(func, "_mcp_tool_description")
        ):
            try:
                # Add tool to FastMCP
                logger.info(f"Registering enhanced tool: {func._mcp_tool_name}")
                tool_count += 1
            except Exception as e:
                logger.error(f"Failed to register tool {func._mcp_tool_name}: {e}")

    logger.info(f"Successfully registered {tool_count} enhanced tools")


# Update the get_git_status tool to use the new schema-based approach
@mcp_tool(
    description="Get Git repository status including current branch and changes.",
    returns={
        "type": "object",
        "properties": {
            "current_branch": {
                "type": "string",
                "description": "Name of the current branch",
            },
            "changes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Status code of the change",
                        },
                        "file": {"type": "string", "description": "Path to the file"},
                    },
                },
                "description": "List of changed files with their status",
            },
            "has_changes": {
                "type": "boolean",
                "description": "Whether there are any changes",
            },
            "tool_used": {"type": "string", "description": "Name of the tool used"},
        },
    },
)
async def get_git_status() -> dict[str, Any]:
    """
    Get Git repository status.

    Returns:
        Dictionary with Git status information
    """
    if repo is None:
        return {"error": "Not a Git repository"}

    try:
        # Use GitPython instead of subprocess
        changes = []
        for item in repo.index.diff(None):  # Unstaged changes
            changes.append({"status": "M ", "file": item.a_path})

        for item in repo.index.diff("HEAD"):  # Staged changes
            changes.append({"status": " M", "file": item.a_path})

        for item in repo.untracked_files:  # Untracked files
            changes.append({"status": "??", "file": item})

        # Get current branch
        current_branch = repo.active_branch.name

        return {
            "current_branch": current_branch,
            "changes": changes,
            "has_changes": len(changes) > 0,
        }
    except Exception as e:
        raise Exception(f"Git operation failed: {e!s}") from e


# Update list_branches to use the schema-based approach
@mcp_tool(
    description="List all branches in the Git repository, including local and remote branches.",
    returns={
        "type": "object",
        "properties": {
            "branches": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Branch name"},
                        "is_current": {
                            "type": "boolean",
                            "description": "Whether this is the current branch",
                        },
                    },
                },
                "description": "List of branches with their status",
            },
            "count": {"type": "integer", "description": "Total number of branches"},
            "tool_used": {"type": "string", "description": "Name of the tool used"},
        },
    },
)
async def list_branches() -> dict[str, Any]:
    """
    List branches in the Git repository.

    Returns:
        Dictionary with branch information including names and current status
    """
    if repo is None:
        return {"error": "Not a Git repository"}

    try:
        # Use GitPython instead of subprocess
        branches = []
        current_branch_name = repo.active_branch.name

        # Local branches
        for branch in repo.branches:
            branches.append(
                {"name": branch.name, "is_current": branch.name == current_branch_name}
            )

        # Remote branches - check if remotes exist
        if hasattr(repo, "remotes") and repo.remotes:
            try:
                # Origin is the standard remote name, but we should check if it exists
                origin = repo.remotes.origin
                for ref in origin.refs:
                    # Skip HEAD reference
                    if ref.name == "origin/HEAD":
                        continue

                    # Format remote branch name
                    branches.append(
                        {"name": f"remotes/{ref.name}", "is_current": False}
                    )
            except (AttributeError, IndexError):
                # Handle case where origin remote doesn't exist
                logger.warning(
                    "No origin remote found or unable to access remote references"
                )

        return {"branches": branches, "count": len(branches)}
    except Exception as e:
        raise Exception(f"Git operation failed: {e!s}") from e


# Update search_codebase to use the schema-based approach
@mcp_tool(
    description="Search the AIchemist codebase for a specific query string.",
    schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to find in codebase files",
            },
            "file_patterns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of glob patterns to filter files",
            },
        },
        "required": ["query"],
    },
    returns={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The original search query"},
            "match_count": {
                "type": "integer",
                "description": "Number of files with matches",
            },
            "matches": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "file": {
                            "type": "string",
                            "description": "Path to the matching file",
                        },
                        "matches": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "line_number": {
                                        "type": "integer",
                                        "description": "Line number of the match",
                                    },
                                    "context": {
                                        "type": "string",
                                        "description": "Context around the match",
                                    },
                                },
                            },
                        },
                    },
                },
                "description": "List of files with matching content",
            },
            "tool_used": {"type": "string", "description": "Name of the tool used"},
        },
    },
)
async def search_codebase(
    query: str, file_patterns: list[str] | None = None
) -> dict[str, Any]:
    """
    Search the AIchemist codebase for the given query.

    Args:
        query: The search query
        file_patterns: Optional list of glob patterns to filter files

    Returns:
        Dictionary with matching files and snippets
    """
    patterns = file_patterns or ["**/*.py", "**/*.md", "**/*.mdc"]
    matches = []

    for pattern in patterns:
        for file_path in AICHEMIST_ROOT.glob(pattern):
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if query.lower() in content.lower():
                        # Find the matching lines and include some context
                        lines = content.split("\n")
                        line_matches = []

                        for i, line in enumerate(lines):
                            if query.lower() in line.lower():
                                start = max(0, i - 2)
                                end = min(len(lines), i + 3)
                                context = "\n".join(
                                    [f"{j + 1}: {lines[j]}" for j in range(start, end)]
                                )
                                line_matches.append(
                                    {"line_number": i + 1, "context": context}
                                )

                        if line_matches:
                            matches.append(
                                {
                                    "file": str(file_path.relative_to(AICHEMIST_ROOT)),
                                    "matches": line_matches,
                                }
                            )
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {e}")

    return {"query": query, "match_count": len(matches), "matches": matches}


@mcp_tool(
    description="Get the current active context from Memory Bank",
    returns={
        "type": "object",
        "properties": {
            "current_focus": {"type": "array", "items": {"type": "string"}},
            "next_steps": {"type": "array", "items": {"type": "string"}},
            "current_status": {"type": "string"},
            "updated_at": {"type": "string", "format": "date-time"},
        },
    },
    category="memory_bank",
    tags=["memory", "context"],
)
async def get_memory_bank_context() -> dict[str, Any]:
    """
    Retrieve the current context information from the Memory Bank.

    This tool implements the Memory Bank architecture to provide proper
    context persistence across sessions.

    Returns:
        Dictionary with current context information
    """
    memory_bank_path = AICHEMIST_ROOT / "memory-bank"
    active_context_path = memory_bank_path / "activeContext.md"

    if not active_context_path.exists():
        # Try alternative locations based on Memory Bank architecture
        alt_paths = [
            memory_bank_path / "core" / "active" / "activeContext.md",
            memory_bank_path / "active" / "activeContext.md",
            memory_bank_path / "00-Core" / "activeContext.md",
        ]

        for path in alt_paths:
            if path.exists():
                active_context_path = path
                break
        else:
            # Create a minimal active context file
            active_context_path = memory_bank_path / "activeContext.md"
            active_context_path.parent.mkdir(parents=True, exist_ok=True)
            active_context_path.write_text(
                "# Active Context\n\n"
                "## Current Focus Areas\n\n"
                "- Initial setup of Memory Bank\n\n"
                "## Next Steps\n\n"
                "- Complete Memory Bank structure\n"
                "- Document system architecture\n"
            )

    try:
        content = active_context_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Extract current focus
        current_focus = []
        next_steps = []
        current_section = None

        for line in lines:
            if line.startswith("## Current Focus"):
                current_section = "focus"
                continue
            elif line.startswith("## Next Steps"):
                current_section = "steps"
                continue
            elif line.startswith("##"):
                current_section = None
                continue

            if current_section == "focus" and line.strip().startswith("- "):
                current_focus.append(line.strip()[2:])
            elif current_section == "steps" and line.strip().startswith("- "):
                next_steps.append(line.strip()[2:])

        # Get last modified time
        last_modified = active_context_path.stat().st_mtime
        last_modified_str = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime(last_modified)
        )

        # Determine current status
        current_status = (
            "Active" if time.time() - last_modified < 86400 else "Needs update"
        )

        return {
            "current_focus": current_focus,
            "next_steps": next_steps,
            "current_status": current_status,
            "updated_at": last_modified_str,
            "file_path": str(active_context_path.relative_to(AICHEMIST_ROOT)),
        }
    except Exception as e:
        return {"error": f"Error reading activeContext.md: {e!s}", "status": "error"}


@mcp_tool(
    description="Update the Memory Bank active context with new information",
    schema={
        "type": "object",
        "properties": {
            "current_focus": {"type": "array", "items": {"type": "string"}},
            "next_steps": {"type": "array", "items": {"type": "string"}},
            "preserve_existing": {"type": "boolean"},
        },
        "required": ["current_focus", "next_steps"],
    },
    category="memory_bank",
    tags=["memory", "context", "update"],
)
async def update_memory_bank_context(
    current_focus: list[str],
    next_steps: list[str],
    preserve_existing: bool = True,
) -> dict[str, Any]:
    """
    Update the Memory Bank active context with new information.

    This implements the Memory Bank update protocol to maintain context
    between sessions.

    Args:
        current_focus: List of current focus areas
        next_steps: List of next steps
        preserve_existing: Whether to preserve existing items

    Returns:
        Dictionary with update status
    """
    memory_bank_path = AICHEMIST_ROOT / "memory-bank"
    active_context_path = memory_bank_path / "activeContext.md"

    # Try alternative locations based on Memory Bank architecture
    if not active_context_path.exists():
        alt_paths = [
            memory_bank_path / "core" / "active" / "activeContext.md",
            memory_bank_path / "active" / "activeContext.md",
            memory_bank_path / "00-Core" / "activeContext.md",
        ]

        for path in alt_paths:
            if path.exists():
                active_context_path = path
                break

    # Ensure directory exists
    active_context_path.parent.mkdir(parents=True, exist_ok=True)

    # Get existing content if available and preserve_existing is True
    existing_focus = []
    existing_steps = []

    if active_context_path.exists() and preserve_existing:
        try:
            content = active_context_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            current_section = None
            for line in lines:
                if line.startswith("## Current Focus"):
                    current_section = "focus"
                    continue
                elif line.startswith("## Next Steps"):
                    current_section = "steps"
                    continue
                elif line.startswith("##"):
                    current_section = None
                    continue

                if current_section == "focus" and line.strip().startswith("- "):
                    existing_focus.append(line.strip()[2:])
                elif current_section == "steps" and line.strip().startswith("- "):
                    existing_steps.append(line.strip()[2:])
        except Exception as e:
            logger.error(f"Error reading existing activeContext.md: {e}")

    # Combine existing and new items, removing duplicates
    if preserve_existing:
        all_focus = existing_focus.copy()
        all_steps = existing_steps.copy()

        for item in current_focus:
            if item not in all_focus:
                all_focus.append(item)

        for item in next_steps:
            if item not in all_steps:
                all_steps.append(item)
    else:
        all_focus = current_focus
        all_steps = next_steps

    # Create new content
    new_content = ["# Active Context", "", "## Current Focus Areas", ""]

    for item in all_focus:
        new_content.append(f"- {item}")

    new_content.extend(["", "## Next Steps", ""])

    for item in all_steps:
        new_content.append(f"- {item}")

    # Add timestamp section
    new_content.extend(
        [
            "",
            "## Last Updated",
            "",
            f"- {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}",
            "",
        ]
    )

    # Write the file
    try:
        # Create backup first
        if active_context_path.exists():
            backup_path = active_context_path.with_suffix(f".bak.{int(time.time())}")
            import shutil

            shutil.copy2(active_context_path, backup_path)

        active_context_path.write_text("\n".join(new_content), encoding="utf-8")

        return {
            "status": "success",
            "file_path": str(active_context_path.relative_to(AICHEMIST_ROOT)),
            "focus_count": len(all_focus),
            "steps_count": len(all_steps),
            "backup_created": active_context_path.exists(),
        }
    except Exception as e:
        return {
            "error": f"Error updating activeContext.md: {e!s}",
            "status": "error",
        }


@mcp_tool(
    description="Execute Bedtime Protocol to preserve memory bank state",
    schema={
        "type": "object",
        "properties": {
            "session_summary": {"type": "string"},
            "key_decisions": {"type": "array", "items": {"type": "string"}},
            "next_session_focus": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["session_summary"],
    },
    category="memory_bank",
    tags=["memory", "bedtime", "protocol"],
)
async def execute_bedtime_protocol(
    session_summary: str,
    key_decisions: list[str] | None = None,
    next_session_focus: list[str] | None = None,
) -> dict[str, Any]:
    """
    Execute the Memory Bank Bedtime Protocol to preserve state between sessions.

    This critical protocol follows the Memory Bank architecture to ensure
    perfect memory continuity between sessions.

    Args:
        session_summary: Summary of the current session
        key_decisions: List of important decisions made
        next_session_focus: Focus areas for the next session

    Returns:
        Dictionary with protocol execution status
    """
    key_decisions = key_decisions or []
    next_session_focus = next_session_focus or []

    memory_bank_path = AICHEMIST_ROOT / "memory-bank"

    # 1. Update activeContext.md
    active_context_path = memory_bank_path / "activeContext.md"

    # Try alternative locations based on Memory Bank architecture
    if not active_context_path.exists():
        alt_paths = [
            memory_bank_path / "core" / "active" / "activeContext.md",
            memory_bank_path / "active" / "activeContext.md",
            memory_bank_path / "00-Core" / "activeContext.md",
        ]

        for path in alt_paths:
            if path.exists():
                active_context_path = path
                break

    # 2. Create session record in episodic memory
    session_date = time.strftime("%Y-%m-%d", time.localtime())
    session_id = f"session-{session_date}-{int(time.time())}"

    episodic_path = memory_bank_path / "long-term" / "episodic" / "sessions"
    if not episodic_path.exists():
        # Try alternative paths based on Memory Bank structure
        alt_paths = [
            memory_bank_path / "13-Long-Term" / "episodic" / "sessions",
            memory_bank_path / "long-term" / "episodic",
            memory_bank_path / "bedtime-protocol" / "sessions",
        ]

        for path in alt_paths:
            if path.exists():
                episodic_path = path
                break
        else:
            # Create the episodic directory if it doesn't exist
            episodic_path = memory_bank_path / "long-term" / "episodic" / "sessions"
            episodic_path.mkdir(parents=True, exist_ok=True)

    session_path = episodic_path / f"{session_id}.md"

    # Create session record
    session_content = [
        f"# Session: {session_date}",
        "",
        "## Summary",
        "",
        session_summary,
        "",
        "## Key Decisions",
        "",
    ]

    for decision in key_decisions:
        session_content.append(f"- {decision}")

    session_content.extend(["", "## Next Session Focus", ""])

    for focus in next_session_focus:
        session_content.append(f"- {focus}")

    session_content.extend(
        [
            "",
            "## Metadata",
            "",
            f"- Date: {session_date}",
            f"- Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}",
            f"- Session ID: {session_id}",
            "",
        ]
    )

    try:
        # Write session record
        session_path.write_text("\n".join(session_content), encoding="utf-8")

        # 3. Update activeContext.md with next session focus
        if active_context_path.exists():
            # Update the active context using the existing function
            await update_memory_bank_context(
                current_focus=next_session_focus,
                next_steps=next_session_focus,
                preserve_existing=False,
            )

        return {
            "status": "success",
            "session_id": session_id,
            "session_file": str(session_path.relative_to(AICHEMIST_ROOT)),
            "context_updated": active_context_path.exists(),
            "protocol_completed": True,
        }
    except Exception as e:
        return {
            "error": f"Error executing Bedtime Protocol: {e!s}",
            "status": "error",
            "protocol_completed": False,
        }


# Add a new tool for getting a file tree with architecture context
@mcp_tool(
    description="Get a structured file tree output with architecture context for the codebase.",
    schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path to start the tree from (default: project root)",
            },
            "depth": {
                "type": "integer",
                "description": "Maximum depth to traverse (default: 3)",
            },
            "include_pattern": {
                "type": "string",
                "description": "Optional glob pattern to include files (e.g., '*.py')",
            },
            "exclude_pattern": {
                "type": "string",
                "description": "Optional glob pattern to exclude files/dirs (e.g., '__pycache__')",
            },
            "with_architecture_context": {
                "type": "boolean",
                "description": "Include architectural context based on file paths (default: true)",
            },
        },
    },
    returns={
        "type": "object",
        "properties": {
            "tree": {"type": "string", "description": "Formatted file tree output"},
            "architecture_summary": {
                "type": "object",
                "description": "Summary of architecture components found",
            },
            "files_count": {"type": "integer", "description": "Total number of files"},
            "directories_count": {
                "type": "integer",
                "description": "Total number of directories",
            },
        },
    },
    category="codebase",
    tags=["file", "architecture", "structure"],
)
async def get_file_tree(
    path: str = ".",
    depth: int = 3,
    include_pattern: str = "",
    exclude_pattern: str = "__pycache__|.git|.venv|.pytest_cache|.mypy_cache|.ruff_cache|.uv_cache",
    with_architecture_context: bool = True,
) -> dict[str, Any]:
    """
    Generate a structured file tree with architecture context.

    This tool analyzes the project structure and provides context about
    each component's architectural role based on its location in the codebase.

    Args:
        path: Starting path (relative to the project root)
        depth: Maximum directory depth to display
        include_pattern: Glob pattern to include files
        exclude_pattern: Glob pattern to exclude files/directories
        with_architecture_context: Include architectural context

    Returns:
        Dictionary with the tree output and architectural summary
    """
    root_path = AICHEMIST_ROOT / path

    if not root_path.exists():
        return {
            "error": f"Path not found: {path}",
            "status": "error",
        }

    # Convert exclude pattern to a list of patterns
    exclude_patterns = [p.strip() for p in exclude_pattern.split("|") if p.strip()]

    # Architecture layer definitions
    architecture_layers = {
        "domain": {
            "description": "Domain layer - Core business logic and entities",
            "patterns": ["domain", "entities", "models"],
            "count": 0,
            "example_files": [],
        },
        "application": {
            "description": "Application layer - Use cases and business operations",
            "patterns": ["application", "use_cases", "services"],
            "count": 0,
            "example_files": [],
        },
        "infrastructure": {
            "description": "Infrastructure layer - Technical implementations and external dependencies",
            "patterns": ["infrastructure", "repositories", "external", "adapters"],
            "count": 0,
            "example_files": [],
        },
        "interfaces": {
            "description": "Interface layer - User interfaces, APIs, and presentation",
            "patterns": ["interfaces", "api", "cli", "ui", "views"],
            "count": 0,
            "example_files": [],
        },
        "cross_cutting": {
            "description": "Cross-cutting concerns - Aspects affecting multiple layers",
            "patterns": ["cross_cutting", "common", "utils", "logging", "security"],
            "count": 0,
            "example_files": [],
        },
    }

    def should_exclude(item_path: Path) -> bool:
        """Check if a path should be excluded based on patterns."""
        path_str = str(item_path.relative_to(AICHEMIST_ROOT))
        return any(pattern in path_str for pattern in exclude_patterns)

    def get_architecture_context(item_path: Path) -> str:
        """Determine the architectural context of a path."""
        if not with_architecture_context:
            return ""

        path_str = str(item_path.relative_to(AICHEMIST_ROOT))

        for layer, info in architecture_layers.items():
            for pattern in info["patterns"]:
                if pattern in path_str.lower():
                    if len(info["example_files"]) < 3 and item_path.is_file():
                        info["example_files"].append(path_str)
                    info["count"] += 1
                    return f" [🔍 {layer.upper()}]"
        return ""

    # Stats tracking
    total_files = 0
    total_dirs = 0

    # Generate the tree output
    tree_lines = []

    def add_to_tree(
        current_path: Path, prefix: str = "", current_depth: int = 0
    ) -> None:
        """Recursively build the tree output."""
        nonlocal total_files, total_dirs

        if current_depth > depth:
            # Indicate truncation
            tree_lines.append(f"{prefix}└── ...")
            return

        if should_exclude(current_path):
            return

        # Handle directories and files differently
        if current_path.is_dir():
            # Don't count the root directory
            if current_path != root_path:
                total_dirs += 1
                dir_context = get_architecture_context(current_path)
                tree_lines.append(f"{prefix}├── 📁 {current_path.name}/{dir_context}")

            items = sorted(
                current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name)
            )
            included_items = []

            # Filter items by include pattern if specified
            if include_pattern:
                included_items = [
                    item
                    for item in items
                    if not item.is_dir()
                    and item.match(include_pattern)
                    and not should_exclude(item)
                ]
                # Always include directories regardless of pattern
                included_items.extend(
                    [
                        item
                        for item in items
                        if item.is_dir() and not should_exclude(item)
                    ]
                )
            else:
                included_items = [item for item in items if not should_exclude(item)]

            # Process items
            for i, item in enumerate(included_items):
                is_last = i == len(included_items) - 1
                new_prefix = f"{prefix}│   " if not is_last else f"{prefix}    "

                if current_path == root_path:
                    new_prefix = prefix  # No indentation for root level

                add_to_tree(item, new_prefix, current_depth + 1)
        else:
            # File handling
            if include_pattern and not current_path.match(include_pattern):
                return

            total_files += 1
            file_context = get_architecture_context(current_path)
            size_kb = round(current_path.stat().st_size / 1024, 1)
            tree_lines.append(
                f"{prefix}└── 📄 {current_path.name} ({size_kb} KB){file_context}"
            )

    # Start building the tree
    if root_path.is_dir():
        tree_lines.append(f"📦 {path if path != '.' else 'AIchemist Codex'}")
        add_to_tree(root_path)
    else:
        # Single file case
        tree_lines.append(f"📄 {root_path.name}")
        total_files = 1

    # Create architecture summary by filtering out empty layers
    architecture_summary = {
        layer: {
            "description": info["description"],
            "count": info["count"],
            "example_files": info["example_files"][:3],  # Limit examples
        }
        for layer, info in architecture_layers.items()
        if info["count"] > 0
    }

    return {
        "tree": "\n".join(tree_lines),
        "architecture_summary": architecture_summary,
        "files_count": total_files,
        "directories_count": total_dirs,
        "context_path": str(root_path.relative_to(AICHEMIST_ROOT)),
    }


# Add a tool to analyze codebase architecture specifically
@mcp_tool(
    description="Analyze the codebase architecture and provide contextual insights.",
    schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path to analyze (default: src directory)",
            },
            "include_statistics": {
                "type": "boolean",
                "description": "Include file count statistics by component (default: true)",
            },
            "include_imports": {
                "type": "boolean",
                "description": "Include import analysis to detect dependencies (default: true)",
            },
        },
    },
    returns={
        "type": "object",
        "properties": {
            "architecture": {
                "type": "object",
                "description": "Architecture analysis by component",
            },
            "dependencies": {
                "type": "array",
                "description": "List of dependencies between components",
            },
            "recommendations": {
                "type": "array",
                "description": "Architectural recommendations based on analysis",
            },
        },
    },
    category="codebase",
    tags=["architecture", "analysis", "structure"],
)
async def analyze_codebase_architecture(
    path: str = "src",
    include_statistics: bool = True,
    include_imports: bool = True,
) -> dict[str, Any]:
    """
    Analyze the codebase architecture and provide contextual insights.

    This tool examines the structure of the codebase to identify architectural
    patterns, component dependencies, and potential improvements.

    Args:
        path: Path to analyze (relative to project root)
        include_statistics: Include file statistics by component
        include_imports: Include import analysis to detect dependencies

    Returns:
        Dictionary with architecture analysis and recommendations
    """
    analysis_path = AICHEMIST_ROOT / path

    if not analysis_path.exists():
        return {
            "error": f"Path not found: {path}",
            "status": "error",
        }

    # Architecture component definitions
    architecture_components = {
        "domain": {
            "description": "Core business logic and entities",
            "expected_location": "src/the_aichemist_codex/domain",
            "files": [],
            "imports": [],
            "is_present": False,
        },
        "application": {
            "description": "Use cases and application services",
            "expected_location": "src/the_aichemist_codex/application",
            "files": [],
            "imports": [],
            "is_present": False,
        },
        "infrastructure": {
            "description": "Technical implementations and external services",
            "expected_location": "src/the_aichemist_codex/infrastructure",
            "files": [],
            "imports": [],
            "is_present": False,
        },
        "interfaces": {
            "description": "User interfaces and API endpoints",
            "expected_location": "src/the_aichemist_codex/interfaces",
            "files": [],
            "imports": [],
            "is_present": False,
        },
        "cross_cutting": {
            "description": "Cross-cutting concerns like logging and security",
            "expected_location": "src/the_aichemist_codex/cross_cutting",
            "files": [],
            "imports": [],
            "is_present": False,
        },
    }

    # Check which components exist
    for component, info in architecture_components.items():
        component_path = AICHEMIST_ROOT / info["expected_location"]
        if component_path.exists() and component_path.is_dir():
            info["is_present"] = True

            # Collect Python files
            python_files = list(component_path.glob("**/*.py"))
            info["files"] = [str(f.relative_to(AICHEMIST_ROOT)) for f in python_files]

    # Analyze imports if requested
    dependencies = []
    if include_imports:
        import_patterns = {
            "domain": [
                "from the_aichemist_codex.domain",
                "import the_aichemist_codex.domain",
            ],
            "application": [
                "from the_aichemist_codex.application",
                "import the_aichemist_codex.application",
            ],
            "infrastructure": [
                "from the_aichemist_codex.infrastructure",
                "import the_aichemist_codex.infrastructure",
            ],
            "interfaces": [
                "from the_aichemist_codex.interfaces",
                "import the_aichemist_codex.interfaces",
            ],
            "cross_cutting": [
                "from the_aichemist_codex.cross_cutting",
                "import the_aichemist_codex.cross_cutting",
            ],
        }

        # Analyze each component's imports
        for component, info in architecture_components.items():
            if not info["is_present"]:
                continue

            for file_path in info["files"]:
                full_path = AICHEMIST_ROOT / file_path
                try:
                    content = full_path.read_text(encoding="utf-8")

                    # Find imports from other components
                    for import_component, patterns in import_patterns.items():
                        if import_component == component:
                            continue  # Skip self-imports

                        for pattern in patterns:
                            if pattern in content:
                                # Record dependency
                                dependency = {
                                    "from": component,
                                    "to": import_component,
                                    "file": file_path,
                                }

                                if dependency not in dependencies:
                                    dependencies.append(dependency)
                                    info["imports"].append(import_component)
                except Exception as e:
                    logger.warning(f"Error reading {file_path}: {e!s}")

    # Generate recommendations based on clean architecture principles
    recommendations = []

    # Check for domain layer dependencies
    domain_info = architecture_components.get("domain", {})
    if domain_info.get("is_present", False):
        domain_imports = domain_info.get("imports", [])
        illegal_imports = [
            imp for imp in domain_imports if imp not in ["cross_cutting"]
        ]

        if illegal_imports:
            recommendations.append(
                {
                    "type": "violation",
                    "title": "Domain layer should not depend on outer layers",
                    "description": "The domain layer should only depend on cross-cutting concerns, but was found to import from: "
                    + ", ".join(illegal_imports),
                    "solution": "Refactor the domain layer to remove dependencies on outer layers. Consider using interfaces and dependency inversion.",
                }
            )

    # Check for circular dependencies
    circular_dependencies = []
    for dep in dependencies:
        reverse_dep = {
            "from": dep["to"],
            "to": dep["from"],
        }

        # Check if the reverse dependency exists
        if any(
            d["from"] == reverse_dep["from"] and d["to"] == reverse_dep["to"]
            for d in dependencies
        ):
            pair = (min(dep["from"], dep["to"]), max(dep["from"], dep["to"]))
            if pair not in circular_dependencies:
                circular_dependencies.append(pair)

    if circular_dependencies:
        recommendations.append(
            {
                "type": "warning",
                "title": "Circular dependencies detected",
                "description": "Circular dependencies found between: "
                + ", ".join([f"{a} and {b}" for a, b in circular_dependencies]),
                "solution": "Break circular dependencies using interfaces and dependency inversion principle.",
            }
        )

    # Check for complete architecture
    missing_components = [
        comp for comp, info in architecture_components.items() if not info["is_present"]
    ]

    if missing_components:
        recommendations.append(
            {
                "type": "suggestion",
                "title": "Complete the clean architecture structure",
                "description": "The following architectural components are missing: "
                + ", ".join(missing_components),
                "solution": "Consider implementing the missing architectural components to achieve a complete clean architecture.",
            }
        )

    return {
        "architecture": {
            component: {
                "description": info["description"],
                "is_present": info["is_present"],
                "file_count": len(info["files"]) if include_statistics else None,
                "dependencies": list(set(info["imports"])) if include_imports else None,
            }
            for component, info in architecture_components.items()
        },
        "dependencies": dependencies if include_imports else [],
        "recommendations": recommendations,
        "analyzed_path": path,
    }


# Add a component mapper tool for clean architecture visualization
@mcp_tool(
    description="Map and visualize component structure according to clean architecture principles.",
    schema={
        "type": "object",
        "properties": {
            "component": {
                "type": "string",
                "description": "Component to analyze (domain, application, infrastructure, interfaces, cross_cutting)",
            },
            "include_files": {
                "type": "boolean",
                "description": "Include detailed file listings (default: true)",
            },
            "include_descriptions": {
                "type": "boolean",
                "description": "Include descriptions of architectural elements (default: true)",
            },
        },
        "required": ["component"],
    },
    returns={
        "type": "object",
        "properties": {
            "component": {"type": "string", "description": "Analyzed component"},
            "layer": {"type": "string", "description": "Clean architecture layer"},
            "structure": {
                "type": "string",
                "description": "Formatted component structure",
            },
            "role": {"type": "string", "description": "Role in clean architecture"},
            "responsibility": {
                "type": "string",
                "description": "Primary responsibility",
            },
            "files_count": {"type": "integer", "description": "Total number of files"},
            "dependencies": {
                "type": "array",
                "description": "Dependencies on other components",
            },
        },
    },
    category="architecture",
    tags=["clean_architecture", "component", "visualization"],
)
async def map_component_structure(
    component: str,
    include_files: bool = True,
    include_descriptions: bool = True,
) -> dict[str, Any]:
    """
    Map and visualize a component according to clean architecture principles.

    This tool provides a detailed view of how a specific component fits into
    the clean architecture pattern, showing its structure, responsibilities,
    and relationships.

    Args:
        component: Which component to analyze (domain, application, etc.)
        include_files: Whether to include detailed file listings
        include_descriptions: Whether to include descriptions

    Returns:
        Dictionary with component structure and architectural information
    """
    # Normalize component name
    component = component.lower().strip()

    # Component to path mapping
    component_paths = {
        "domain": "src/the_aichemist_codex/domain",
        "application": "src/the_aichemist_codex/application",
        "infrastructure": "src/the_aichemist_codex/infrastructure",
        "interfaces": "src/the_aichemist_codex/interfaces",
        "cross_cutting": "src/the_aichemist_codex/cross_cutting",
        "cli": "src/the_aichemist_codex/interfaces/cli",
    }

    # Get the component path
    if component not in component_paths:
        return {
            "error": f"Unknown component: {component}. Available components: {', '.join(component_paths.keys())}",
            "status": "error",
        }

    component_path = AICHEMIST_ROOT / component_paths[component]

    if not component_path.exists() or not component_path.is_dir():
        return {
            "error": f"Component path not found: {component_path}",
            "status": "error",
        }

    # Architecture information by component
    architecture_info = {
        "domain": {
            "layer": "Domain Layer",
            "role": "Core business logic and domain entities",
            "responsibility": "Defining the business problem and solution, independent of technical concerns",
            "dependencies": ["cross_cutting"],
            "subcomponents": {
                "entities": "Core business objects with identity and lifecycle",
                "events": "Domain events representing state changes",
                "exceptions": "Domain-specific exceptions",
                "models": "Rich domain models with behavior",
                "relations": "Relationship definitions between entities",
                "repositories": "Data access interfaces",
                "services": "Domain-specific business operations",
                "tagging": "Tagging system implementation",
                "value_objects": "Immutable values without identity",
            },
        },
        "application": {
            "layer": "Application Layer",
            "role": "Orchestration of domain operations",
            "responsibility": "Coordinating domain objects to perform specific use cases",
            "dependencies": ["domain", "cross_cutting"],
            "subcomponents": {
                "use_cases": "Application-specific use case implementations",
                "services": "Application services orchestrating domain operations",
                "commands": "Command objects representing user intentions",
                "queries": "Query objects for retrieving data",
                "events": "Application event handling",
            },
        },
        "infrastructure": {
            "layer": "Infrastructure Layer",
            "role": "Technical implementation details",
            "responsibility": "Implementing interfaces defined by the domain layer",
            "dependencies": ["domain", "application", "cross_cutting"],
            "subcomponents": {
                "ai": "AI/ML capabilities implementation",
                "analysis": "Code and data analysis tools",
                "config": "Configuration management",
                "extraction": "Data extraction utilities",
                "fs": "File system operations",
                "memory": "Memory management",
                "repositories": "Repository implementations",
                "platforms": "Platform-specific code",
                "versioning": "Version control integration",
            },
        },
        "interfaces": {
            "layer": "Interface Layer",
            "role": "User interfaces and API endpoints",
            "responsibility": "Converting external inputs to application layer calls",
            "dependencies": ["application", "cross_cutting"],
            "subcomponents": {
                "cli": "Command-line interface",
                "api": "API endpoints",
                "events": "Event handling interfaces",
                "output": "Output formatting",
                "stream": "Stream processing",
            },
        },
        "cross_cutting": {
            "layer": "Cross-cutting Concerns",
            "role": "Aspects affecting multiple layers",
            "responsibility": "Providing common functionality across layers",
            "dependencies": [],
            "subcomponents": {
                "common": "Common utilities",
                "logging": "Logging functionality",
                "security": "Security services",
                "utils": "Utility functions",
            },
        },
        "cli": {
            "layer": "Interface Layer (CLI Subcomponent)",
            "role": "Command-line interface",
            "responsibility": "Processing command-line inputs and displaying outputs",
            "dependencies": ["application", "cross_cutting"],
            "subcomponents": {
                "commands": "CLI command implementations",
                "formatters": "Output formatting for CLI",
            },
        },
    }

    # Get information for this component
    component_info = architecture_info.get(component, {})
    layer = component_info.get("layer", "Unknown")
    role = component_info.get("role", "Unknown")
    responsibility = component_info.get("responsibility", "Unknown")
    dependencies = component_info.get("dependencies", [])
    subcomponents = component_info.get("subcomponents", {})

    # Build structure listing
    structure_lines = [f"# {component.title()} Component", ""]

    # Add architectural context if requested
    if include_descriptions:
        structure_lines.extend(
            [
                f"**Layer:** {layer}",
                f"**Role:** {role}",
                f"**Responsibility:** {responsibility}",
                "",
                f"**Dependencies:** {', '.join(dependencies) if dependencies else 'None'}",
                "",
                "## Structure",
                "",
            ]
        )

    # Get subdirectories
    subdirectories = [
        d
        for d in component_path.iterdir()
        if d.is_dir() and not d.name.startswith("__")
    ]

    # Add subdirectories to structure
    for subdir in sorted(subdirectories):
        subdir_name = subdir.name
        description = subcomponents.get(subdir_name, "")
        description_text = (
            f" - {description}" if description and include_descriptions else ""
        )

        structure_lines.append(f"### {subdir_name.title()}{description_text}")
        structure_lines.append("")

        # Add files if requested
        if include_files:
            python_files = sorted(
                [f for f in subdir.glob("*.py") if not f.name.startswith("__")]
            )

            if python_files:
                for py_file in python_files:
                    structure_lines.append(f"- {py_file.name}")
            else:
                structure_lines.append("*No Python files*")

            structure_lines.append("")

    # Add root-level files
    root_files = sorted(
        [f for f in component_path.glob("*.py") if not f.name.startswith("__")]
    )

    if root_files:
        structure_lines.append("### Root Level Files")
        structure_lines.append("")

        for py_file in root_files:
            structure_lines.append(f"- {py_file.name}")

        structure_lines.append("")

    # Count total files
    all_python_files = list(component_path.glob("**/*.py"))
    files_count = len([f for f in all_python_files if not f.name.startswith("__")])

    return {
        "component": component,
        "layer": layer,
        "structure": "\n".join(structure_lines),
        "role": role,
        "responsibility": responsibility,
        "files_count": files_count,
        "dependencies": dependencies,
    }


# Helper function to generate a full clean architecture diagram
@mcp_tool(
    description="Generate a clean architecture diagram with component relationships.",
    schema={
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "description": "Output format (text, markdown, mermaid)",
                "enum": ["text", "markdown", "mermaid"],
            },
            "include_dependencies": {
                "type": "boolean",
                "description": "Include dependency arrows (default: true)",
            },
        },
    },
    returns={
        "type": "object",
        "properties": {
            "diagram": {
                "type": "string",
                "description": "Generated architecture diagram",
            },
            "format": {"type": "string", "description": "Output format used"},
            "components": {
                "type": "array",
                "description": "List of components included in the diagram",
            },
        },
    },
    category="architecture",
    tags=["clean_architecture", "diagram", "visualization"],
)
async def generate_architecture_diagram(
    format: str = "markdown", include_dependencies: bool = True
) -> dict[str, Any]:
    """
    Generate a clean architecture diagram showing the layers and their relationships.

    This tool creates a visual representation of the clean architecture
    pattern as implemented in the project, with optional dependency arrows.

    Args:
        format: Output format (text, markdown, mermaid)
        include_dependencies: Whether to include dependency arrows

    Returns:
        Dictionary with the generated diagram and related information
    """
    # Core architecture components
    components = [
        "domain",
        "application",
        "infrastructure",
        "interfaces",
        "cross_cutting",
    ]

    # Validate format
    if format not in ["text", "markdown", "mermaid"]:
        format = "markdown"  # Default to markdown

    # Component paths to verify existence
    component_paths = {
        component: AICHEMIST_ROOT / f"src/the_aichemist_codex/{component}"
        for component in components
    }

    # Check which components exist
    existing_components = [
        component
        for component, path in component_paths.items()
        if path.exists() and path.is_dir()
    ]

    # Generate the appropriate diagram format
    if format == "mermaid":
        # Create a Mermaid graph diagram
        diagram_lines = ["```mermaid", "graph TD;", "    %% Clean Architecture Diagram"]

        # Define the nodes with appropriate styling
        for component in existing_components:
            node_id = component.upper()
            node_label = f"{component.title()} Layer"
            diagram_lines.append(f'    {node_id}["{node_label}"];')

        # Add dependencies if requested
        if include_dependencies:
            # Dependency rules based on clean architecture
            dependencies = {
                "interfaces": ["application"],
                "application": ["domain"],
                "infrastructure": ["domain", "application"],
                # Cross-cutting concerns can be used by any layer
            }

            # Add dependency arrows
            for component, deps in dependencies.items():
                if component in existing_components:
                    for dep in deps:
                        if dep in existing_components:
                            # Arrow from dependent to dependency
                            diagram_lines.append(
                                f"    {component.upper()} --> {dep.upper()};"
                            )

            # Add cross-cutting concerns dependencies
            if "cross_cutting" in existing_components:
                for component in existing_components:
                    if component != "cross_cutting":
                        diagram_lines.append(
                            f"    {component.upper()} -.-> CROSS_CUTTING;"
                        )

        # Close the diagram
        diagram_lines.append("```")

    elif format == "text":
        # Create a simple text diagram
        diagram_lines = ["Clean Architecture Diagram", "========================", ""]

        # Layer representation
        for component in existing_components:
            diagram_lines.append(f"[{component.upper()}] {component.title()} Layer")

        # Add dependencies if requested
        if include_dependencies and len(existing_components) > 1:
            diagram_lines.append("\nDependencies:")

            # Standard dependencies
            if (
                "interfaces" in existing_components
                and "application" in existing_components
            ):
                diagram_lines.append("  Interfaces --> Application")

            if "application" in existing_components and "domain" in existing_components:
                diagram_lines.append("  Application --> Domain")

            if "infrastructure" in existing_components:
                if "domain" in existing_components:
                    diagram_lines.append("  Infrastructure --> Domain")
                if "application" in existing_components:
                    diagram_lines.append("  Infrastructure --> Application")

            # Cross-cutting dependencies
            if "cross_cutting" in existing_components:
                diagram_lines.append("\n  All layers may use Cross-cutting concerns")

    else:  # markdown
        # Create a markdown diagram with better formatting
        diagram_lines = ["# Clean Architecture Diagram", ""]

        # Create layer boxes
        for component in existing_components:
            diagram_lines.append(f"## {component.title()} Layer")

            # Add brief descriptions
            if component == "domain":
                diagram_lines.append(
                    "\n> Core business logic and entities - The heart of the application\n"
                )
            elif component == "application":
                diagram_lines.append(
                    "\n> Use cases and application services - Orchestrating the domain\n"
                )
            elif component == "infrastructure":
                diagram_lines.append(
                    "\n> Technical implementations - External adapters and tools\n"
                )
            elif component == "interfaces":
                diagram_lines.append(
                    "\n> User interfaces and API endpoints - User interaction layer\n"
                )
            elif component == "cross_cutting":
                diagram_lines.append(
                    "\n> Cross-cutting concerns - Aspects used across all layers\n"
                )

        # Add dependency rules if requested
        if include_dependencies:
            diagram_lines.append("## Dependency Rules")
            diagram_lines.append("\n1. Outer layers depend on inner layers")
            diagram_lines.append("2. Inner layers must not depend on outer layers")
            diagram_lines.append(
                "3. Domain layer has no dependencies (except cross-cutting)"
            )
            diagram_lines.append("4. Application layer depends only on domain layer")
            diagram_lines.append(
                "5. Interface & infrastructure layers depend on application and domain"
            )
            diagram_lines.append("6. All layers may use cross-cutting concerns\n")

    return {
        "diagram": "\n".join(diagram_lines),
        "format": format,
        "components": existing_components,
    }


# Function to add a tool that can create class diagrams for specific components
@mcp_tool(
    description="Generate a class diagram or data model for a specific component or module.",
    schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the component (e.g., src/the_aichemist_codex/domain/entities)",
            },
            "format": {
                "type": "string",
                "description": "Output format (text, markdown, mermaid)",
                "enum": ["text", "markdown", "mermaid"],
            },
            "include_methods": {
                "type": "boolean",
                "description": "Include methods in the diagram (default: true)",
            },
            "include_attributes": {
                "type": "boolean",
                "description": "Include attributes in the diagram (default: true)",
            },
        },
        "required": ["path"],
    },
    returns={
        "type": "object",
        "properties": {
            "diagram": {"type": "string", "description": "Generated class diagram"},
            "classes": {"type": "array", "description": "List of classes found"},
            "relationships": {
                "type": "array",
                "description": "Detected relationships between classes",
            },
        },
    },
    category="architecture",
    tags=["class_diagram", "data_model", "visualization"],
)
async def generate_class_diagram(
    path: str,
    format: str = "markdown",
    include_methods: bool = True,
    include_attributes: bool = True,
) -> dict[str, Any]:
    """
    Generate a class diagram or data model for a specific component or module.

    This tool analyzes Python files to identify classes, their attributes,
    methods, and relationships to produce a visual representation.

    Args:
        path: Path to the component relative to the project root
        format: Output format for the diagram
        include_methods: Whether to include methods in the diagram
        include_attributes: Whether to include attributes in the diagram

    Returns:
        Dictionary with the generated diagram and class information
    """
    try:
        import ast
        import inspect
    except ImportError:
        return {
            "error": "Required modules (ast, inspect) not available",
            "status": "error",
        }

    # Resolve the target path
    target_path = AICHEMIST_ROOT / path

    if not target_path.exists():
        return {
            "error": f"Path not found: {path}",
            "status": "error",
        }

    # Find all Python files
    python_files = []
    if target_path.is_dir():
        python_files = list(target_path.glob("**/*.py"))
    elif target_path.is_file() and target_path.suffix == ".py":
        python_files = [target_path]
    else:
        return {
            "error": f"Path is not a Python file or directory: {path}",
            "status": "error",
        }

    if not python_files:
        return {
            "error": f"No Python files found in {path}",
            "status": "error",
        }

    # Class information storage
    classes = []
    relationships = []

    # Helper class to parse Python files
    class ClassVisitor(ast.NodeVisitor):
        def __init__(self, file_path):
            self.file_path = file_path
            self.current_class = None
            self.classes = []
            self.relationships = []

        def visit_ClassDef(self, node):
            # Store class information
            class_info = {
                "name": node.name,
                "file": str(self.file_path),
                "bases": [
                    b.id if isinstance(b, ast.Name) else self._get_attr_name(b)
                    for b in node.bases
                    if hasattr(b, "id") or isinstance(b, ast.Attribute)
                ],
                "methods": [],
                "attributes": [],
                "docstring": ast.get_docstring(node) or "",
            }

            # Add inheritance relationships
            for base in class_info["bases"]:
                self.relationships.append(
                    {
                        "type": "inheritance",
                        "from": class_info["name"],
                        "to": base,
                    }
                )

            # Save current class and visit children
            self.current_class = class_info
            self.classes.append(class_info)
            self.generic_visit(node)
            self.current_class = None

        def visit_FunctionDef(self, node):
            if self.current_class and include_methods:
                # Add method information
                self.current_class["methods"].append(
                    {
                        "name": node.name,
                        "args": [
                            arg.arg for arg in node.args.args if arg.arg != "self"
                        ],
                        "is_constructor": node.name == "__init__",
                        "docstring": ast.get_docstring(node) or "",
                    }
                )

                # Look for relationship hints in constructor
                if node.name == "__init__" and include_attributes:
                    self.visit_constructor(node)

            # Skip further method content processing
            return

        def visit_constructor(self, node):
            # Look for attribute assignments in constructor
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and isinstance(target.value, ast.Name)
                            and target.value.id == "self"
                            and self.current_class is not None
                        ):
                            self.current_class["attributes"].append(
                                {
                                    "name": target.attr,
                                    "type": self._get_value_type(item.value),
                                }
                            )

        def visit_AnnAssign(self, node):
            # Handle type-annotated assignments (Python 3.6+)
            if (
                include_attributes
                and self.current_class is not None
                and isinstance(node.target, ast.Attribute)
                and isinstance(node.target.value, ast.Name)
                and node.target.value.id == "self"
            ):
                self.current_class["attributes"].append(
                    {
                        "name": node.target.attr,
                        "type": self._get_annotation_name(node.annotation),
                    }
                )

        def _get_attr_name(self, node):
            # Handle attribute access like module.Class
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Attribute):
                    return f"{self._get_attr_name(node.value)}.{node.attr}"
                elif isinstance(node.value, ast.Name):
                    return f"{node.value.id}.{node.attr}"
                else:
                    return f"unknown.{node.attr}"
            return str(node)

        def _get_annotation_name(self, node):
            # Extract type annotation names
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Attribute):
                return self._get_attr_name(node)
            elif isinstance(node, ast.Subscript):
                return f"{self._get_annotation_name(node.value)}[]"
            return "unknown"

        def _get_value_type(self, node):
            # Infer value types from assignments
            if isinstance(node, ast.List):
                return "list"
            elif isinstance(node, ast.Dict):
                return "dict"
            elif isinstance(node, ast.Str):
                return "str"
            elif isinstance(node, ast.Num):
                return "int" if isinstance(node.n, int) else "float"
            elif isinstance(node, ast.NameConstant) and node.value is None:
                return "None"
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    return node.func.id
                elif isinstance(node.func, ast.Attribute):
                    return node.func.attr
            return "unknown"

    # Process each Python file
    for file_path in python_files:
        try:
            # Parse the file
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read())

            # Visit the AST
            visitor = ClassVisitor(file_path)
            visitor.visit(tree)

            # Add results
            classes.extend(visitor.classes)
            relationships.extend(visitor.relationships)
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e!s}")

    # Generate the appropriate diagram format
    diagram_lines = []

    if format == "mermaid":
        # Create a Mermaid class diagram
        diagram_lines = ["```mermaid", "classDiagram"]

        # Add classes with their members
        for cls in classes:
            diagram_lines.append(f"    class {cls['name']} {{")

            # Add attributes
            if include_attributes:
                for attr in cls["attributes"]:
                    attr_type = f": {attr['type']}" if attr["type"] != "unknown" else ""
                    diagram_lines.append(f"        +{attr['name']}{attr_type}")

            # Add methods
            if include_methods:
                for method in cls["methods"]:
                    params = ", ".join(method["args"])
                    diagram_lines.append(f"        +{method['name']}({params})")

            diagram_lines.append("    }")

        # Add relationships
        for rel in relationships:
            if rel["type"] == "inheritance":
                diagram_lines.append(f"    {rel['to']} <|-- {rel['from']}")

        diagram_lines.append("```")

    elif format == "text":
        # Create a simple text class diagram
        diagram_lines = ["Class Diagram", "=============", ""]

        # Add classes
        for cls in classes:
            diagram_lines.append(f"[{cls['name']}]")

            if cls["bases"]:
                diagram_lines.append(f"  Extends: {', '.join(cls['bases'])}")

            if include_attributes and cls["attributes"]:
                diagram_lines.append("  Attributes:")
                for attr in cls["attributes"]:
                    attr_type = (
                        f" ({attr['type']})" if attr["type"] != "unknown" else ""
                    )
                    diagram_lines.append(f"    - {attr['name']}{attr_type}")

            if include_methods and cls["methods"]:
                diagram_lines.append("  Methods:")
                for method in cls["methods"]:
                    params = ", ".join(method["args"])
                    diagram_lines.append(f"    + {method['name']}({params})")

            diagram_lines.append("")

    else:  # markdown
        # Create a markdown class diagram
        diagram_lines = ["# Class Diagram", ""]

        # Add classes
        for cls in classes:
            diagram_lines.append(f"## {cls['name']}")

            if cls["docstring"]:
                # Include first line of docstring as brief description
                brief = cls["docstring"].split("\n")[0].strip()
                diagram_lines.append(f"> {brief}")

            if cls["bases"]:
                diagram_lines.append(f"**Extends:** {', '.join(cls['bases'])}")

            if include_attributes and cls["attributes"]:
                diagram_lines.append("\n### Attributes\n")
                for attr in cls["attributes"]:
                    attr_type = (
                        f" `{attr['type']}`" if attr["type"] != "unknown" else ""
                    )
                    diagram_lines.append(f"- **{attr['name']}**:{attr_type}")

            if include_methods and cls["methods"]:
                diagram_lines.append("\n### Methods\n")
                for method in cls["methods"]:
                    params = ", ".join(method["args"])
                    diagram_lines.append(f"- **{method['name']}**({params})")
                    if method["docstring"]:
                        # Include first line of method docstring
                        brief = method["docstring"].split("\n")[0].strip()
                        diagram_lines.append(f"  - {brief}")

            diagram_lines.append("")

    return {
        "diagram": "\n".join(diagram_lines),
        "classes": [{"name": cls["name"], "file": cls["file"]} for cls in classes],
        "relationships": relationships,
    }


# Relationship Management Tools
# These tools integrate with AIchemist's relationship management system

# Import the relationship management components
from the_aichemist_codex.domain.relationships import (
    RelationshipManager,
    RelationshipType,
)

# Default relationships database path
RELATIONSHIPS_DB_PATH = AICHEMIST_ROOT / ".aichemist" / "relationships.db"

# Global relationship manager instance
_relationship_manager = None


async def get_relationship_manager() -> RelationshipManager:
    """Get or initialize the relationship manager instance."""
    global _relationship_manager
    if _relationship_manager is None:
        # Create the directory if it doesn't exist
        RELATIONSHIPS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _relationship_manager = RelationshipManager(RELATIONSHIPS_DB_PATH)
        await _relationship_manager.initialize()
    return _relationship_manager


@mcp_tool(
    description="Create a relationship between two files in the codebase.",
    schema={
        "type": "object",
        "properties": {
            "source_path": {
                "type": "string",
                "description": "Path to the source file",
            },
            "target_path": {
                "type": "string",
                "description": "Path to the target file",
            },
            "relationship_type": {
                "type": "string",
                "description": "Type of relationship (e.g., imports, extends, uses, contains, references)",
            },
            "strength": {
                "type": "number",
                "description": "Strength of the relationship (0.0-1.0)",
            },
            "bidirectional": {
                "type": "boolean",
                "description": "Create relationship in both directions",
            },
            "metadata": {
                "type": "object",
                "description": "Additional metadata for the relationship",
            },
        },
        "required": ["source_path", "target_path", "relationship_type"],
    },
    returns={
        "type": "object",
        "properties": {
            "relationship_id": {
                "type": "integer",
                "description": "ID of the created relationship",
            },
            "source_path": {
                "type": "string",
                "description": "Path to the source file",
            },
            "target_path": {
                "type": "string",
                "description": "Path to the target file",
            },
            "relationship_type": {
                "type": "string",
                "description": "Type of the relationship",
            },
            "bidirectional": {
                "type": "boolean",
                "description": "Whether a bidirectional relationship was created",
            },
            "status": {
                "type": "string",
                "description": "Status of the operation",
            },
        },
    },
    category="relationships",
    tags=["create", "relationship", "files"],
)
async def create_relationship(
    source_path: str,
    target_path: str,
    relationship_type: str,
    strength: float = 1.0,
    bidirectional: bool = False,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create a relationship between two files in the codebase.

    Args:
        source_path: Path to the source file
        target_path: Path to the target file
        relationship_type: Type of relationship (e.g., imports, extends, uses)
        strength: Relationship strength (0.0-1.0)
        bidirectional: Create relationship in both directions
        metadata: Additional metadata for the relationship

    Returns:
        Dictionary with information about the created relationship(s)
    """
    try:
        # Convert paths to Path objects
        source = AICHEMIST_ROOT / source_path
        target = AICHEMIST_ROOT / target_path

        # Validate paths
        if not source.exists():
            return {
                "error": f"Source file not found: {source_path}",
                "status": "error",
            }

        if not target.exists():
            return {
                "error": f"Target file not found: {target_path}",
                "status": "error",
            }

        # Get relationship manager
        rel_manager = await get_relationship_manager()

        # Create the relationship
        relationship_id = await rel_manager.create_relationship(
            source, target, relationship_type, strength, metadata
        )

        result = {
            "relationship_id": relationship_id,
            "source_path": str(source),
            "target_path": str(target),
            "relationship_type": relationship_type,
            "strength": strength,
            "bidirectional": bidirectional,
            "status": "success",
        }

        # Create reverse relationship if bidirectional
        if bidirectional:
            reverse_id = await rel_manager.create_relationship(
                target, source, relationship_type, strength, metadata
            )
            result["reverse_relationship_id"] = reverse_id

        return result
    except Exception as e:
        return {
            "error": f"Failed to create relationship: {e!s}",
            "status": "error",
        }


@mcp_tool(
    description="List relationships for a file or all relationships in the system.",
    schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to get relationships for (optional)",
            },
            "show_outgoing": {
                "type": "boolean",
                "description": "Show outgoing relationships",
            },
            "show_incoming": {
                "type": "boolean",
                "description": "Show incoming relationships",
            },
            "relationship_type": {
                "type": "string",
                "description": "Filter by relationship type (e.g., imports, extends)",
            },
            "show_all": {
                "type": "boolean",
                "description": "List all relationships in the system",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of relationships to return",
            },
        },
    },
    returns={
        "type": "object",
        "properties": {
            "relationships": {
                "type": "array",
                "description": "List of relationships",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Relationship ID"},
                        "source_path": {
                            "type": "string",
                            "description": "Source file path",
                        },
                        "target_path": {
                            "type": "string",
                            "description": "Target file path",
                        },
                        "type": {
                            "type": "string",
                            "description": "Relationship type",
                        },
                        "strength": {
                            "type": "number",
                            "description": "Relationship strength",
                        },
                        "created_at": {
                            "type": "string",
                            "description": "Creation timestamp",
                        },
                        "direction": {
                            "type": "string",
                            "description": "Direction (outgoing or incoming)",
                        },
                    },
                },
            },
            "count": {"type": "integer", "description": "Total count of relationships"},
            "file": {"type": "string", "description": "File path if specified"},
            "status": {"type": "string", "description": "Status of the operation"},
        },
    },
    category="relationships",
    tags=["list", "relationship", "files"],
)
async def list_relationships(
    path: str | None = None,
    show_outgoing: bool = True,
    show_incoming: bool = True,
    relationship_type: str | None = None,
    show_all: bool = False,
    limit: int = 100,
) -> dict[str, Any]:
    """
    List relationships for a file or all relationships in the system.

    Args:
        path: Path to the file to get relationships for (optional)
        show_outgoing: Show outgoing relationships
        show_incoming: Show incoming relationships
        relationship_type: Filter by relationship type
        show_all: List all relationships in the system
        limit: Maximum number of relationships to return

    Returns:
        Dictionary with relationships information
    """
    try:
        # Get relationship manager
        rel_manager = await get_relationship_manager()

        relationships = []

        # List all relationships if requested
        if show_all:
            all_rels = await rel_manager.get_all_relationships()
            relationships = all_rels[:limit]
            return {
                "relationships": relationships,
                "count": len(relationships),
                "status": "success",
            }

        # List relationships for specific file
        if path:
            target_path = AICHEMIST_ROOT / path
            if not target_path.exists():
                return {
                    "error": f"Path not found: {path}",
                    "status": "error",
                }

            outgoing_rels = []
            incoming_rels = []

            # Get outgoing relationships
            if show_outgoing:
                outgoing_rels = await rel_manager.get_outgoing_relationships(
                    target_path, relationship_type
                )
                for rel in outgoing_rels:
                    rel["direction"] = "outgoing"
                    relationships.append(rel)

            # Get incoming relationships
            if show_incoming:
                incoming_rels = await rel_manager.get_incoming_relationships(
                    target_path, relationship_type
                )
                for rel in incoming_rels:
                    rel["direction"] = "incoming"
                    relationships.append(rel)

            return {
                "relationships": relationships[:limit],
                "count": len(relationships),
                "file": str(target_path),
                "status": "success",
            }

        # If no path and not show_all, return error
        return {
            "error": "Either path or show_all must be specified",
            "status": "error",
        }

    except Exception as e:
        return {
            "error": f"Failed to list relationships: {e!s}",
            "status": "error",
        }


@mcp_tool(
    description="Delete relationships between files.",
    schema={
        "type": "object",
        "properties": {
            "relationship_id": {
                "type": "integer",
                "description": "ID of the relationship to delete",
            },
            "source_path": {
                "type": "string",
                "description": "Source file path",
            },
            "target_path": {
                "type": "string",
                "description": "Target file path",
            },
            "relationship_type": {
                "type": "string",
                "description": "Type of relationship to delete",
            },
            "delete_all": {
                "type": "boolean",
                "description": "Delete all relationships for the specified files",
            },
        },
    },
    returns={
        "type": "object",
        "properties": {
            "deleted_count": {
                "type": "integer",
                "description": "Number of relationships deleted",
            },
            "status": {"type": "string", "description": "Status of the operation"},
        },
    },
    category="relationships",
    tags=["delete", "relationship", "files"],
)
async def delete_relationship(
    relationship_id: int | None = None,
    source_path: str | None = None,
    target_path: str | None = None,
    relationship_type: str | None = None,
    delete_all: bool = False,
) -> dict[str, Any]:
    """
    Delete relationships between files.

    Args:
        relationship_id: ID of the relationship to delete
        source_path: Source file path
        target_path: Target file path
        relationship_type: Type of relationship to delete
        delete_all: Delete all relationships for the specified files

    Returns:
        Dictionary with deletion information
    """
    try:
        # Get relationship manager
        rel_manager = await get_relationship_manager()

        deleted_count = 0

        # Delete by relationship ID
        if relationship_id is not None:
            success = await rel_manager.delete_relationship(relationship_id)
            deleted_count = 1 if success else 0
            return {
                "deleted_count": deleted_count,
                "status": "success" if success else "error",
            }

        # Delete by file paths
        if source_path and target_path:
            source = AICHEMIST_ROOT / source_path
            target = AICHEMIST_ROOT / target_path

            if delete_all:
                # Delete all relationships between the files
                deleted_count = await rel_manager.delete_relationships_between(
                    source, target
                )
            else:
                # Delete relationship of specific type
                if not relationship_type:
                    return {
                        "error": "Relationship type must be specified when deleting without relationship_id",
                        "status": "error",
                    }

                success = await rel_manager.delete_relationship_by_paths(
                    source, target, relationship_type
                )
                deleted_count = 1 if success else 0

            return {
                "deleted_count": deleted_count,
                "status": "success",
            }

        return {
            "error": "Either relationship_id or both source_path and target_path must be specified",
            "status": "error",
        }

    except Exception as e:
        return {
            "error": f"Failed to delete relationship: {e!s}",
            "status": "error",
        }


@mcp_tool(
    description="Get available relationship types.",
    returns={
        "type": "object",
        "properties": {
            "relationship_types": {
                "type": "array",
                "description": "List of available relationship types",
                "items": {"type": "string"},
            },
            "common_examples": {
                "type": "object",
                "description": "Common examples of relationship types and their usage",
            },
            "status": {"type": "string", "description": "Status of the operation"},
        },
    },
    category="relationships",
    tags=["relationship", "types", "metadata"],
)
async def get_relationship_types() -> dict[str, Any]:
    """
    Get available relationship types.

    Returns:
        Dictionary with relationship type information
    """
    try:
        # Get standard relationship types from the RelationshipType enum
        relationship_types = [rt.value for rt in RelationshipType]

        # Provide examples and descriptions
        examples = {
            "imports": "File imports or includes another file (e.g., Python import)",
            "extends": "Class extends or inherits from another class",
            "implements": "Class implements an interface or protocol",
            "uses": "File uses functionality from another file",
            "references": "File references or mentions another file",
            "contains": "File contains another file (e.g., directory containing file)",
            "calls": "Function calls another function",
            "custom": "Custom relationship type",
        }

        return {
            "relationship_types": relationship_types,
            "common_examples": examples,
            "status": "success",
        }
    except Exception as e:
        return {
            "error": f"Failed to get relationship types: {e!s}",
            "status": "error",
        }


@mcp_tool(
    description="Visualize relationships for a file or a group of files.",
    schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to visualize relationships for",
            },
            "include_incoming": {
                "type": "boolean",
                "description": "Include incoming relationships",
            },
            "include_outgoing": {
                "type": "boolean",
                "description": "Include outgoing relationships",
            },
            "max_depth": {
                "type": "integer",
                "description": "Maximum depth for relationship traversal",
            },
            "format": {
                "type": "string",
                "description": "Output format (text, mermaid, dot)",
                "enum": ["text", "mermaid", "dot"],
            },
        },
        "required": ["path"],
    },
    returns={
        "type": "object",
        "properties": {
            "visualization": {
                "type": "string",
                "description": "Visualization output in the specified format",
            },
            "node_count": {"type": "integer", "description": "Number of nodes"},
            "edge_count": {"type": "integer", "description": "Number of edges"},
            "format": {"type": "string", "description": "Format of the visualization"},
            "status": {"type": "string", "description": "Status of the operation"},
        },
    },
    category="relationships",
    tags=["visualization", "relationship", "graph"],
)
async def visualize_relationships(
    path: str,
    include_incoming: bool = True,
    include_outgoing: bool = True,
    max_depth: int = 1,
    format: str = "mermaid",
) -> dict[str, Any]:
    """
    Visualize relationships for a file or a group of files.

    Args:
        path: Path to the file to visualize relationships for
        include_incoming: Include incoming relationships
        include_outgoing: Include outgoing relationships
        max_depth: Maximum depth for relationship traversal
        format: Output format (text, mermaid, dot)

    Returns:
        Dictionary with visualization information
    """
    try:
        # Get relationship manager
        rel_manager = await get_relationship_manager()

        target_path = AICHEMIST_ROOT / path
        if not target_path.exists():
            return {
                "error": f"Path not found: {path}",
                "status": "error",
            }

        # Get the relationship network
        network = await rel_manager.get_relationship_network(
            target_path,
            include_incoming=include_incoming,
            include_outgoing=include_outgoing,
            max_depth=max_depth,
        )

        # Count nodes and edges
        node_count = len(network["nodes"])
        edge_count = len(network["edges"])

        # Generate visualization based on format
        visualization = ""
        if format == "mermaid":
            visualization = "```mermaid\ngraph LR\n"

            # Add nodes
            for node in network["nodes"]:
                node_id = f"node{node['id']}"
                node_label = Path(node["path"]).name
                visualization += f"    {node_id}[{node_label}]\n"

            # Add edges
            for edge in network["edges"]:
                source_id = f"node{edge['source_id']}"
                target_id = f"node{edge['target_id']}"
                edge_label = edge["type"]
                visualization += f"    {source_id} -- {edge_label} --> {target_id}\n"

            visualization += "```"
        elif format == "dot":
            visualization = "digraph RelationshipGraph {\n"

            # Add nodes
            for node in network["nodes"]:
                node_id = f"node{node['id']}"
                node_label = Path(node["path"]).name
                visualization += f'    {node_id} [label="{node_label}"];\n'

            # Add edges
            for edge in network["edges"]:
                source_id = f"node{edge['source_id']}"
                target_id = f"node{edge['target_id']}"
                edge_label = edge["type"]
                visualization += (
                    f'    {source_id} -> {target_id} [label="{edge_label}"];\n'
                )

            visualization += "}"
        else:  # text format
            visualization = f"Relationship Network for {target_path}:\n\n"

            # Add nodes
            visualization += "Nodes:\n"
            for node in network["nodes"]:
                visualization += f"- {node['path']}\n"

            # Add edges
            visualization += "\nEdges:\n"
            for edge in network["edges"]:
                source_path = next(
                    (
                        n["path"]
                        for n in network["nodes"]
                        if n["id"] == edge["source_id"]
                    ),
                    "Unknown",
                )
                target_path = next(
                    (
                        n["path"]
                        for n in network["nodes"]
                        if n["id"] == edge["target_id"]
                    ),
                    "Unknown",
                )
                visualization += (
                    f"- {source_path} --({edge['type']})--> {target_path}\n"
                )

        return {
            "visualization": visualization,
            "node_count": node_count,
            "edge_count": edge_count,
            "format": format,
            "status": "success",
        }
    except Exception as e:
        return {
            "error": f"Failed to visualize relationships: {e!s}",
            "status": "error",
        }


if __name__ == "__main__":
    # Start the Sequential Thinking server (optional)
    # This is now handled by the server_lifespan

    # Run the MCP server using the FastMCP command with proper error handling
    try:
        logger.info("Starting AIchemist MCP Hub...")
        logger.info(f"Server version: {getattr(mcp, '__version__', 'unknown')}")
        logger.info("Server features: Prompts, Resources, Tools")

        # Print server information
        logger.info("Server capabilities:")
        logger.info("- Git operations")
        logger.info("- File system access")
        logger.info("- Memory bank navigation")
        logger.info("- Sequential thinking")

        # Register all enhanced tools
        register_enhanced_tools()

        # Log all registered tools for debugging
        logger.info("\nRegistered tools:")
        tool_count = 0

        # Check for tools registered directly with mcp.tool
        for attr_name in dir(mcp):
            if attr_name.startswith("tools_"):
                tool_count += 1
                logger.info(f"- {attr_name}")

        # Check for decorated functions
        globals_copy = list(globals().items())
        for name, func in globals_copy:
            if callable(func) and hasattr(func, "__wrapped__"):
                if not name.startswith("_"):
                    logger.info(f"- {name}")
                    tool_count += 1

        logger.info(f"Total tools registered: {tool_count}")
        logger.info("\nPress Ctrl+C to exit")

        # Run the MCP server
        mcp.run()
    except KeyboardInterrupt:
        logger.info("\nShutting down AIchemist MCP Hub on user request...")
    except Exception as e:
        logger.error(f"\nError running MCP server: {e}", exc_info=True)
    finally:
        # Cleanup happens automatically through the lifespan context manager
        logger.info("Server shutdown complete.")
