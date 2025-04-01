# src/chemist_server/mcp_core/app.py
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

# MCP SDK Import - using fallback import paths
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

# Local Imports
from chemist_server.config import AppConfig, CoreConfig, get_config_instance

# Import CLI and Git tools directly
from chemist_server.tool_servers.python_tool_server.cliTool.cli_tools import (
    run_command,
    show_security_rules,
)
from chemist_server.tool_servers.python_tool_server.cliTool.git_tools import (
    get_git_status,
    list_branches,
    search_codebase,
)

# Remove PythonToolAdapter import
from .health import CoreHealth, SystemHealth
from .logger import StructuredLogger
from .registry import ToolRegistry
from .router import Router

logger = StructuredLogger("chemist_server.mcp_core.app")


# --- Lifespan Context ---
class CoreLifespanContext:
    def __init__(
        self,
        config: CoreConfig,
        registry: ToolRegistry,
        router: Router,
        health_checker: SystemHealth,
    ) -> None:
        """Initialize the Core Lifespan Context.

        Args:
            config: Core configuration
            registry: Tool registry
            router: Request router
            health_checker: System health checker
        """
        self.config = config
        self.registry = registry
        self.router = router
        self.health_checker = health_checker
        # Remove py_tool_adapter attribute


@asynccontextmanager
async def core_lifespan(app: FastMCP) -> AsyncIterator[CoreLifespanContext]:
    """Application lifecycle manager for FastMCP."""
    config = get_config_instance()
    logger.info(
        "MCP Core Lifespan starting.",
        core_config=config.core.model_dump(exclude={"auth_token"}),
    )

    registry = ToolRegistry()
    router = Router(registry)
    health_checker = SystemHealth([CoreHealth()])

    # Remove adapter setup section
    lifespan_ctx = CoreLifespanContext(config.core, registry, router, health_checker)

    try:
        # Remove python_tool_adapter initialization
        # Remove dynamic tool discovery

        logger.info("Core Lifespan setup complete.")
        yield lifespan_ctx  # Yield context for the app to run

    finally:
        logger.info("MCP Core shutting down lifespan context")
        await registry.shutdown()  # Shuts down adapters


# --- FastMCP App Factory ---
def get_fastmcp_app(config: AppConfig) -> FastMCP:
    """Creates and configures the FastMCP application."""
    app = FastMCP(
        name="MCP Core Service",
        instructions="Core service managing tools and resources.",
        lifespan=core_lifespan,
        debug=config.logging.level == "DEBUG",
        dependencies=[],
    )

    # Remove execute_proxied_tool handler

    # Direct tools from CLI and Git toolsets
    @app.tool(
        name="run_command",
        description="Execute command-line operations with auto-correction for Windows and UV package manager",
    )
    async def run_command_wrapper(
        ctx: Context[ServerSession, CoreLifespanContext],
        command: str,
    ) -> dict[str, Any]:
        """Execute command-line operations.

        Args:
            ctx: Request context
            command: The command to execute

        Returns:
            Command execution results
        """
        logger.info(
            "Executing run_command tool",
            command=command,
            request_id=ctx.request_id,
        )
        try:
            result = await run_command(ctx=None, command=command)
            logger.info(
                "Command executed successfully",
                request_id=ctx.request_id,
            )
            return result
        except Exception as e:
            logger.error(
                f"Error executing command: {e}",
                request_id=ctx.request_id,
                exc_info=True,
            )
            raise

    @app.tool(
        name="show_security_rules",
        description="Display security configuration for command execution",
    )
    async def show_security_rules_wrapper(
        ctx: Context[ServerSession, CoreLifespanContext],
    ) -> dict[str, Any]:
        """Show security rules for command execution.

        Args:
            ctx: Request context

        Returns:
            Security rules configuration
        """
        logger.info(
            "Executing show_security_rules tool",
            request_id=ctx.request_id,
        )
        try:
            result = await show_security_rules(ctx=None)
            return result
        except Exception as e:
            logger.error(
                f"Error showing security rules: {e}",
                request_id=ctx.request_id,
                exc_info=True,
            )
            raise

    @app.tool(name="git_status", description="Get the Git status of a repository")
    async def git_status_wrapper(
        ctx: Context[ServerSession, CoreLifespanContext],
    ) -> dict[str, Any]:
        """Get Git repository status.

        Args:
            ctx: Request context

        Returns:
            Git status information
        """
        logger.info(
            "Executing git_status tool",
            request_id=ctx.request_id,
        )
        try:
            result = await get_git_status()
            return result
        except Exception as e:
            logger.error(
                f"Error getting git status: {e}",
                request_id=ctx.request_id,
                exc_info=True,
            )
            raise

    @app.tool(name="git_branches", description="List branches in a Git repository")
    async def git_branches_wrapper(
        ctx: Context[ServerSession, CoreLifespanContext],
    ) -> dict[str, Any]:
        """List Git repository branches.

        Args:
            ctx: Request context

        Returns:
            List of branches
        """
        logger.info(
            "Executing git_branches tool",
            request_id=ctx.request_id,
        )
        try:
            result = await list_branches()
            return result
        except Exception as e:
            logger.error(
                f"Error listing git branches: {e}",
                request_id=ctx.request_id,
                exc_info=True,
            )
            raise

    @app.tool(name="search_code", description="Search for patterns in the codebase")
    async def search_code_wrapper(
        ctx: Context[ServerSession, CoreLifespanContext],
        query: str,
        file_patterns: list[str] | None = None,
    ) -> dict[str, Any]:
        """Search codebase for patterns.

        Args:
            ctx: Request context
            query: Pattern to search for
            file_patterns: Optional file patterns to search

        Returns:
            Search results
        """
        logger.info(
            "Executing search_code tool",
            query=query,
            file_patterns=file_patterns,
            request_id=ctx.request_id,
        )
        try:
            result = await search_codebase(query=query, file_patterns=file_patterns)
            return result
        except Exception as e:
            logger.error(
                f"Error searching code: {e}",
                request_id=ctx.request_id,
                exc_info=True,
            )
            raise

    # Core Tool Example
    @app.tool(name="core_add")
    def core_add_tool(a: int, b: int) -> int:
        logger.info(f"Executing core_add tool with a={a}, b={b}")
        return a + b

    # Health Check Tool
    @app.tool(name="core_health")
    async def core_health_tool(
        ctx: Context[ServerSession, CoreLifespanContext],
    ) -> dict:
        logger.debug("Executing core_health tool", request_id=ctx.request_id)
        health_checker = ctx.request_context.lifespan_context.health_checker
        health_status = await health_checker.check_health()
        return health_status

    logger.info("FastMCP application instance created and configured.")
    return app
