"""Main entry point for MCP Proxy server."""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from .config.config import get_proxy_config
from .proxy_server import ProxyServer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager.

    Args:
        app: FastAPI application
    """
    # Initialize proxy server
    proxy_server = ProxyServer(app)
    app.state.proxy_server = proxy_server

    # Start the server
    await proxy_server.start()

    yield

    # Shutdown the server
    await proxy_server.stop()


def create_app() -> FastAPI:
    """Create FastAPI application.

    Returns:
        FastAPI: Application instance
    """
    app = FastAPI(
        title="MCP Proxy Server",
        description="Proxy server for Model Context Protocol",
        version="1.0.0",
        lifespan=lifespan,
    )

    return app


async def async_main() -> int:
    """Async main entry point.

    Returns:
        int: Exit code
    """
    # Create FastAPI application
    app = create_app()

    # Get configuration
    config = get_proxy_config()

    # Initialize proxy server
    proxy_server = ProxyServer(app)

    try:
        # Start the server
        await proxy_server.start()

        # In a real implementation, we would keep the server running
        # For now, just log and return success
        return 0
    except Exception as e:
        print(f"Error starting proxy server: {e}")
        return 1


def main() -> int:
    """Main entry point.

    Returns:
        int: Exit code
    """
    # Create FastAPI application
    app = create_app()

    # Get configuration
    config = get_proxy_config()

    # Start server
    uvicorn.run(
        app,
        host=config.sse_host,
        port=config.sse_port,
        log_level="info",
    )

    return 0


if __name__ == "__main__":
    main()
