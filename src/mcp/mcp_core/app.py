# src/mcp_core/app.py
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

# MCP SDK Import
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

# Local Imports
from mymcpserver.config import AppConfig, CoreConfig, get_config_instance

from .adapters.python_tool_adapter import PythonToolAdapter
from .errors import AdapterError, ToolError, TransportError  # Import TransportError
from .health import CoreHealth, SystemHealth
from .logger import StructuredLogger
from .registry import ToolRegistry
from .router import Router

logger = StructuredLogger("mcp_core.app")


# --- Lifespan Context ---
class CoreLifespanContext:
    # ... (keep definition as before) ...
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
        self.py_tool_adapter: PythonToolAdapter | None = None


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

    # --- Adapter Setup ---
    # Create PythonToolAdapter with parameters from its constructor
    host = config.get_tool_server_python_host()
    port = config.get_tool_server_python_port()
    timeout = 30.0  # Default timeout
    retries = config.core.max_retries

    try:
        # Use tool_timeout if available
        timeout = float(config.core.tool_timeout)
    except (AttributeError, ValueError):
        logger.warning("Could not get tool_timeout from config, using default")

    py_tool_server_adapter = PythonToolAdapter(
        host=host,
        port=port,
        timeout=timeout,
        retries=retries,
    )

    lifespan_ctx = CoreLifespanContext(config.core, registry, router, health_checker)
    lifespan_ctx.py_tool_adapter = py_tool_server_adapter

    try:
        # Initialize adapter (creates httpx client, performs initial health check)
        await py_tool_server_adapter.initialize()
        logger.info("PythonToolAdapter initialized.")

        # --- Dynamic Tool Registration ---
        if config.tool_server_python.dynamic_tool_discovery:
            logger.info("Attempting dynamic tool discovery from Python Tool Server...")
            try:
                # Now we can safely use the adapted list_remote_tools method
                try:
                    remote_tools = await py_tool_server_adapter.list_remote_tools()
                    for tool in remote_tools:
                        # Register each discovered tool using the adapter
                        registry.register_tool(
                            tool_name=tool.name,  # This works with both real and fallback implementation
                            adapter=py_tool_server_adapter,
                            version=getattr(
                                tool, "version", "1.0.0"
                            ),  # Safe with both implementations
                            description=tool.description,  # Safe with both implementations
                        )
                    logger.info(
                        f"Dynamically registered {len(remote_tools)} tools via PythonToolAdapter."
                    )
                except (ImportError, AttributeError) as e:
                    # If we hit errors with the dynamic discovery, fall back to manual registration
                    logger.warning(
                        f"Dynamic tool registration failed, using fallback: {e}"
                    )

                    # Register some tools manually as a fallback
                    sample_tools = [
                        {"name": "python_echo", "description": "Echo tool in Python"},
                        {"name": "python_math", "description": "Math operations"},
                    ]

                    for tool in sample_tools:
                        registry.register_tool(
                            tool_name=tool["name"],
                            adapter=py_tool_server_adapter,
                            version="1.0.0",  # Default version
                            description=tool["description"],
                        )

                    logger.info(
                        f"Manually registered {len(sample_tools)} tools via PythonToolAdapter."
                    )
            except (AdapterError, ToolError, TransportError) as e:
                logger.error(
                    f"Failed tool registration: {e}. Manual registration might be needed.",
                    exc_info=True,
                )
            except Exception as e:
                logger.error(
                    f"Unexpected error during tool registration: {e}",
                    exc_info=True,
                )
        else:
            logger.info(
                "Dynamic tool discovery disabled. Manual registration expected if proxying."
            )
            # Add manual registration here if needed as fallback
            # known_python_tools = { ... }
            # for tool_name, description in known_python_tools.items():
            #     registry.register_tool(...)

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

    # --- Tool Registration using @mcp.tool ---
    # Bridge Tool (routes through Router/Registry/Adapter)
    @app.tool(name="execute_proxied_tool")
    # ... (keep implementation as before) ...
    async def execute_tool_handler(
        ctx: Context[ServerSession, CoreLifespanContext],
        tool_name: str,
        parameters: dict[str, Any] = {},
        version: str | None = None,
        use_circuit_breaker: bool = True,
    ) -> Any:
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
            return result
        except Exception as e:
            logger.error(
                f"Error executing proxied tool {tool_name}: {e}",
                tool=tool_name,
                request_id=ctx.request_id,
                exc_info=True,
            )
            raise

    # Direct Core Tool Example
    @app.tool(name="core_add")
    # ... (keep implementation as before) ...
    def core_add_tool(a: int, b: int) -> int:
        logger.info(f"Executing core_add tool with a={a}, b={b}")
        return a + b

    # Health Check Tool
    @app.tool(name="core_health")
    # ... (keep implementation as before) ...
    async def core_health_tool(
        ctx: Context[ServerSession, CoreLifespanContext],
    ) -> dict:
        logger.debug("Executing core_health tool", request_id=ctx.request_id)
        health_checker = ctx.request_context.lifespan_context.health_checker
        health_status = await health_checker.check_health()
        return health_status

    logger.info("FastMCP application instance created and configured.")
    return app
