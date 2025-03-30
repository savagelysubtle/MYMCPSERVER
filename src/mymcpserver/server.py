"""MCP Server main module.

This module serves as the main entry point for the MCP Server, handling both the
Proxy Connection Server and MCP Core Layer initialization based on configuration.
It supports multiple transport mechanisms (HTTP, stdio) and provides proper
integration between all architectural layers.
"""

from __future__ import annotations

# Standard library imports
import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

# Third-party imports
import uvicorn
from dotenv import load_dotenv

# Add src directory to path to make imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

# Application imports

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_level = os.environ.get("MCP_LOG_LEVEL", "INFO").upper()
log_file = os.environ.get("MCP_LOG_FILE", "mcp_server.log")

logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file),
    ],
)
logger = logging.getLogger("mcp_server")


def get_config() -> dict[str, Any]:
    """Get server configuration from environment variables.

    Returns:
        Dict[str, Any]: Server configuration with host, port, log level,
            workers count, transport type, and component selection.
    """
    return {
        "host": os.environ.get("MCP_HOST", "127.0.0.1"),
        "port": int(os.environ.get("MCP_PORT", "8000")),
        "log_level": os.environ.get("MCP_LOG_LEVEL", "info").lower(),
        "workers": int(os.environ.get("MCP_WORKERS", "1")),
        "transport": os.environ.get("MCP_TRANSPORT", "http").lower(),
        "components": os.environ.get("MCP_COMPONENTS", "all").lower(),
    }


async def handle_stdio() -> None:
    """Handle stdio transport for MCP.

    This mode is used when the server is running as a subprocess
    and communicating through stdin/stdout. It implements the Proxy Connection
    Server functionality for stdio transport.
    """
    logger.info("Starting MCP Server in stdio mode")

    async def read_stdin() -> None:
        """Read from stdin and process messages.

        Continuously reads from stdin, processes messages, and sends responses back.
        This implements the main loop for the stdio transport.
        """
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    logger.info("Stdin closed, exiting")
                    return

                # Process the received message
                try:
                    message = json.loads(line)
                    logger.debug(f"Received message: {message}")

                    # Process the message through the Adapter/Registry Layer
                    # This is where we'd connect to the mcp_core layer
                    # For now, it's a placeholder
                    response = {
                        "success": True,
                        "message": "Received message",
                        "correlation_id": message.get("correlation_id", "unknown"),
                    }

                    print(json.dumps(response), flush=True)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {line}")
                    print(
                        json.dumps({"success": False, "error": "Invalid JSON"}),
                        flush=True,
                    )
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                print(json.dumps({"success": False, "error": str(e)}), flush=True)

    # Start reading from stdin
    await read_stdin()


def start_core_server(config: dict[str, Any]) -> None:
    """Start the MCP Core server.

    This function starts the FastAPI-based MCP Core Layer that handles
    the central business logic of the system.

    Args:
        config: Server configuration including host, port, log level, and workers.
    """
    logger.info(f"Starting MCP Core server on {config['host']}:{config['port']}")

    uvicorn.run(
        "mcp_core.app:app",
        host=config["host"],
        port=config["port"],
        log_level=config["log_level"],
        workers=config["workers"],
    )


def start_proxy_server(config: dict[str, Any]) -> None:
    """Start the Proxy Connection Server.

    This function starts the Proxy Connection Server which handles
    protocol translation between different transports.

    Args:
        config: Server configuration including transport type.
    """
    logger.info(
        f"Starting Proxy Connection Server with {config['transport']} transport"
    )

    # Depending on the transport, start the appropriate handler
    if config["transport"] == "stdio":
        asyncio.run(handle_stdio())
    else:
        # For non-stdio transports, use the ProxyServer class
        # This is a placeholder until the ProxyServer is fully implemented
        logger.error(f"Transport {config['transport']} not yet implemented")
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments including transport, host, port,
            log level, and component selection.
    """
    parser = argparse.ArgumentParser(description="MCP Server")
    parser.add_argument(
        "--transport",
        choices=["http", "stdio", "sse", "websocket"],
        default="http",
        help="Transport mechanism (default: http)",
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Logging level (default: info)",
    )
    parser.add_argument(
        "--component",
        choices=["all", "proxy", "core"],
        default="all",
        help="Component to start (default: all)",
    )

    return parser.parse_args()


def main() -> int:
    """Entry point for the MCP server.

    This is the main entry point that decides which components to start
    based on configuration and command line arguments.

    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    logger.info("Initializing MCP Server...")

    try:
        # Parse command line arguments
        args = parse_args()

        # Get configuration, override with command line args
        config = get_config()
        if args.transport:
            config["transport"] = args.transport
        if args.host:
            config["host"] = args.host
        if args.port:
            config["port"] = args.port
        if args.log_level:
            config["log_level"] = args.log_level
        if args.component:
            config["components"] = args.component

        # Start the appropriate component(s)
        if config["components"] == "all":
            # In full mode, start both proxy and core
            # In a production environment, these would typically be separate processes
            # For development, we start the appropriate one based on transport
            if config["transport"] == "stdio":
                start_proxy_server(config)
            else:
                start_core_server(config)
        elif config["components"] == "proxy":
            # Start only the proxy server
            start_proxy_server(config)
        elif config["components"] == "core":
            # Start only the core server
            start_core_server(config)
        else:
            logger.error(f"Invalid component selection: {config['components']}")
            return 1

    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return 1

    logger.info("MCP Server shutdown complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
