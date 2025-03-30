# src/mcp_core/app.py
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

# MCP SDK Import
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession  # For type hint

# Local Imports
from mymcpserver.config import (
    AppConfig,
    CoreConfig,
    get_config_instance,
)  # Use unified config

from .adapters.python_tool_adapter import PythonToolAdapter
from .health import CoreHealth, SystemHealth
from .logger import StructuredLogger  # Use structured logger
from .registry import ToolRegistry
from .router import Router

# No longer need routes.py

logger = StructuredLogger("mcp_core.app")


# --- Lifespan Context ---
class CoreLifespanContext:
    def __init__(
        self,
        config: CoreConfig,
        registry: ToolRegistry,
        router: Router,
        health_checker: SystemHealth,
    ):
        self.config = config
        self.registry = registry
        self.router = router
        self.health_checker = health_checker
        self.py_tool_adapter: Optional[PythonToolAdapter] = (
            None  # Store adapter if needed after init
        )


@asynccontextmanager
async def core_lifespan(app: FastMCP) -> AsyncIterator[CoreLifespanContext]:
    """Application lifecycle manager for FastMCP."""
    # Config is already loaded by run_server.py
    config = get_config_instance()
    logger.info(
        "MCP Core Lifespan starting.",
        core_config=config.core.model_dump(exclude={"auth_token"}),
    )

    registry = ToolRegistry()
    router = Router(registry)
    health_checker = SystemHealth([CoreHealth()])  # Add more checks as needed

    # --- Adapter Setup ---
    # Only set up adapters for components that are meant to be separate processes
    py_tool_server_adapter = PythonToolAdapter(
        host=config.get_tool_server_python_host(),
        port=config.get_tool_server_python_port(),
    )
    lifespan_ctx = CoreLifespanContext(config.core, registry, router, health_checker)
    lifespan_ctx.py_tool_adapter = (
        py_tool_server_adapter  # Store for potential direct use
    )

    # --- Tool Registration (via Adapter Proxy) ---
    # This assumes the Core layer proxies calls to the separate Python Tool Server
    # A better approach might involve fetching the tool list from the tool server
    known_python_tools = {
        "obsidian.list_notes": "List Obsidian notes",
        "obsidian.search_notes": "Search Obsidian notes",
        "obsidian.save_note": "Save an Obsidian note",
        "aichemist.get_molecule": "Get molecule information",
        "aichemist.list_molecules": "List available molecules",
        "aichemist.calculate_property": "Calculate a molecular property",
    }
    for tool_name, description in known_python_tools.items():
        registry.register_tool(
            tool_name=tool_name,
            adapter=py_tool_server_adapter,  # Use the adapter instance
            version="1.0.0",  # TODO: Get version from tool server
            description=f"{description} (via Python Tool Server)",
        )
    logger.info(f"Registered {len(known_python_tools)} tools via PythonToolAdapter.")

    try:
        await py_tool_server_adapter.initialize()
        logger.info("Core Lifespan initialized adapters.")
        yield lifespan_ctx
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
        dependencies=[],  # Project manages dependencies
    )

    # --- Tool Registration using @mcp.tool ---

    # Bridge Tool: Routes calls through the internal Router/Registry/Adapter system
    @app.tool(name="execute_proxied_tool")  # More specific name
    async def execute_tool_handler(
        ctx: Context[ServerSession, CoreLifespanContext],
        tool_name: str,
        parameters: dict[str, Any] = {},
        version: str | None = None,
        use_circuit_breaker: bool = True,
    ) -> Any:
        """Executes a tool registered via adapters by routing the request."""
        router = ctx.request_context.lifespan_context.router
        logger.info(
            f"Executing proxied tool: {tool_name}",
            tool=tool_name,
            request_id=ctx.request_id,
        )
        try:
            result = await router.route_request(
                tool_name=tool_name,
                parameters=parameters,
                version=version,
                use_circuit_breaker=use_circuit_breaker,
            )
            logger.info(
                f"Proxied tool {tool_name} executed successfully.",
                tool=tool_name,
                request_id=ctx.request_id,
            )
            return result  # FastMCP handles result conversion
        except Exception as e:
            logger.error(
                f"Error executing proxied tool {tool_name}: {e}",
                tool=tool_name,
                request_id=ctx.request_id,
                exc_info=True,
            )
            raise  # Let FastMCP handle error response

    # Direct Core Tool Example
    @app.tool(name="core_add")
    def core_add_tool(a: int, b: int) -> int:
        """Adds two numbers directly within the core service."""
        logger.info(f"Executing core_add tool with a={a}, b={b}")
        return a + b

    # Health Check Tool
    @app.tool(name="core_health")
    async def core_health_tool(
        ctx: Context[ServerSession, CoreLifespanContext],
    ) -> dict:
        """Returns the health status of the core service."""
        logger.debug("Executing core_health tool", request_id=ctx.request_id)
        health_checker = ctx.request_context.lifespan_context.health_checker
        # Optionally add dynamic checks here, e.g., pinging tool servers
        # adapter = ctx.request_context.lifespan_context.py_tool_adapter
        # if adapter:
        #     py_tool_health = await adapter.health_check()
        #     health_checker.components.append(lambda: py_tool_health) # Add check result
        health_status = await health_checker.check_health()
        return health_status

    # --- Add Resource/Prompt registrations using app decorators if needed ---
    # @app.resource(...)
    # def my_resource_handler(...): ...
    #
    # @app.prompt(...)
    # def my_prompt_handler(...): ...

    logger.info("FastMCP application instance created and configured.")
    return app
