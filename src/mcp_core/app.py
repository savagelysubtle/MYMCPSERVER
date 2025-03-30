"""MCP Core application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .adapters.python_adapter import PythonAdapter
from .adapters.ts_adapter import TypeScriptAdapter
from .config import get_core_config
from .health import CoreHealth, SystemHealth
from .logger import logger
from .registry import ToolRegistry
from .router import Router
from .routes import router as tools_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    # Load configuration
    config = get_core_config()

    # Initialize components
    registry = ToolRegistry()
    router = Router(registry)
    health_checker = SystemHealth([CoreHealth()])

    # Register dummy adapters for testing
    # In a real implementation, these would be loaded from configuration
    # or discovered dynamically

    # Python adapter example
    python_adapter = PythonAdapter(
        module_path="mcp_core.adapters.testing.python_tool",
        function_name="execute_tool",
        load_module=False,  # Don't load immediately as this is just a dummy
    )
    registry.register_tool(
        tool_name="python-example",
        adapter=python_adapter,
        version="1.0.0",
        description="Example Python tool",
        tags=["example", "python"],
    )

    # TypeScript adapter example
    ts_adapter = TypeScriptAdapter(
        server_path=os.path.join(
            os.path.dirname(__file__), "adapters", "testing", "ts-tools"
        ),
        tool_name="typescript-example",
        server_port=3001,
    )
    registry.register_tool(
        tool_name="typescript-example",
        adapter=ts_adapter,
        version="1.0.0",
        description="Example TypeScript tool",
        tags=["example", "typescript"],
    )

    # Store in app state
    app.state.config = config
    app.state.registry = registry
    app.state.registry_router = (
        router  # This is the router that will be used by the API routes
    )
    app.state.health = health_checker

    logger.info("MCP Core starting up")

    try:
        # Initialize adapters
        await python_adapter.initialize()
        await ts_adapter.initialize()
        yield
    finally:
        # Perform cleanup
        await registry.shutdown()
        logger.info("MCP Core shutting down")


# Create FastAPI application
app = FastAPI(
    title="MCP Core",
    description="Model Context Protocol Core Layer",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(tools_router, prefix="/api/v1")
