#!/usr/bin/env python3
"""MCP System Runner.

This script provides a convenient way to start various components of the MCP
microservices architecture as described in the system documentation.

Usage:
    python run_server.py --mode [full|proxy|core|tool] --transport [http|stdio|sse]
"""

import argparse
import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mymcpserver import main as mcp_main


def setup_logging() -> None:
    """Configure logging for the runner script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("mcp_runner.log")],
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="MCP System Runner")
    parser.add_argument(
        "--mode",
        choices=["full", "proxy", "core", "tool"],
        default="full",
        help="Component(s) to start (default: full)",
    )
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
        "--tool-server",
        choices=["python", "typescript", "all"],
        default="all",
        help="Tool server to start (default: all)",
    )
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Logging level (default: info)",
    )

    return parser.parse_args()


async def run_core_process(transport: str, log_level: str, host: str, port: int) -> int:
    """Run the MCP Core Layer as a separate process.

    Args:
        transport: Transport mechanism
        log_level: Logging level
        host: Host to bind to
        port: Port to bind to

    Returns:
        int: Exit code
    """
    # Prepare environment variables
    env = os.environ.copy()
    env["MCP_TRANSPORT"] = transport
    env["MCP_LOG_LEVEL"] = log_level
    env["MCP_HOST"] = host
    env["MCP_PORT"] = str(port)
    env["MCP_COMPONENTS"] = "core"

    logging.info("Starting MCP Core Layer")

    # If using stdio transport, run directly
    if transport == "stdio":
        logging.info("MCP Core Layer running with stdio transport")

        # Process stdio messages
        # In a real implementation, this would be a loop to read from stdin
        # and write to stdout, communicating with the Core Layer's API

        return 0
    else:
        # Otherwise run via mcp_main
        return mcp_main()


async def run_proxy_process(
    transport: str, log_level: str, host: str, port: int
) -> int:
    """Run the MCP Proxy Connection Server as a separate process.

    Args:
        transport: Transport mechanism
        log_level: Logging level
        host: Host to bind to
        port: Port to bind to

    Returns:
        int: Exit code
    """
    # Prepare environment variables
    env = os.environ.copy()
    env["MCP_TRANSPORT"] = transport
    env["MCP_LOG_LEVEL"] = log_level
    env["MCP_HOST"] = host
    env["MCP_PORT"] = str(port)
    env["MCP_COMPONENTS"] = "proxy"

    logging.info("Starting MCP Proxy Connection Server")

    # If we're using stdio, we need to spawn the Core Layer process
    if transport == "stdio":
        # Import the actual module
        try:
            from mcp_proxy.__main__ import async_main

            # Run the proxy server asynchronously
            return await async_main()
        except ImportError as e:
            logging.error(f"Failed to import proxy modules: {e}")
            return 1
    else:
        # Otherwise run via mcp_main
        return mcp_main()


async def run_python_tool_server(host: str, port: int, log_level: str) -> int:
    """Run the Python Tool Server as a separate process.

    Args:
        host: Host to bind to
        port: Port to bind to
        log_level: Logging level

    Returns:
        int: Exit code
    """
    try:
        # Prepare environment variables
        env = os.environ.copy()
        env["HOST"] = host
        env["PORT"] = str(port)
        env["LOG_LEVEL"] = log_level.upper()

        # Construct path to the Python Tool Server
        tool_server_dir = Path(__file__).parent / "tool_servers" / "python_tool_server"
        server_script = tool_server_dir / "server.py"

        if not server_script.exists():
            logging.error(f"Python Tool Server script not found at {server_script}")
            return 1

        logging.info(f"Starting Python Tool Server at {host}:{port}")

        # Run the server as a subprocess
        process = subprocess.Popen(
            [sys.executable, str(server_script)],
            env=env,
            cwd=str(tool_server_dir),
        )

        # Wait for the process
        return_code = process.wait()
        return return_code
    except Exception as e:
        logging.error(f"Error running Python Tool Server: {e}")
        return 1


def run_mcp_server(args: argparse.Namespace) -> int:
    """Run the MCP server components based on command-line arguments.

    Args:
        args: Command-line arguments

    Returns:
        int: Exit code
    """
    try:
        if args.mode == "full":
            # Run all components
            logging.info("Starting MCP in full mode")

            # In full mode with stdio, we spawn the Proxy which in turn spawns Core
            if args.transport == "stdio":
                return asyncio.run(
                    run_proxy_process(
                        args.transport, args.log_level, args.host, args.port
                    )
                )
            else:
                # Start MCP main components
                mcp_process = mcp_main()

                # Also start tool servers if in full mode
                if args.tool_server == "python" or args.tool_server == "all":
                    logging.info("Starting Python Tool Server")
                    # Use a different port for the tool server
                    tool_port = args.port + 1
                    asyncio.run(
                        run_python_tool_server(args.host, tool_port, args.log_level)
                    )

                return mcp_process

        elif args.mode == "proxy":
            # Run only the proxy server
            return asyncio.run(
                run_proxy_process(args.transport, args.log_level, args.host, args.port)
            )

        elif args.mode == "core":
            # Run only the core server
            return asyncio.run(
                run_core_process(args.transport, args.log_level, args.host, args.port)
            )

        elif args.mode == "tool":
            # Run tool server(s)
            if args.tool_server == "python" or args.tool_server == "all":
                logging.info("Starting Python Tool Server")
                return asyncio.run(
                    run_python_tool_server(args.host, args.port, args.log_level)
                )

            if args.tool_server == "typescript" or args.tool_server == "all":
                logging.info("Starting TypeScript Tool Server")
                # This would start the TypeScript tool server
                # For now, just log since we haven't implemented it yet
                logging.warning("TypeScript Tool Server not yet implemented")

            return 0
        else:
            logging.error(f"Invalid mode: {args.mode}")
            return 1
    except KeyboardInterrupt:
        logging.info("Runner interrupted by user")
        return 0
    except Exception as e:
        logging.error(f"Error running MCP components: {e}")
        return 1


def main() -> int:
    """Main entry point.

    Returns:
        int: Exit code
    """
    setup_logging()
    args = parse_args()

    try:
        return run_mcp_server(args)
    except KeyboardInterrupt:
        logging.info("Runner interrupted by user")
        return 0
    except Exception as e:
        logging.error(f"Error running MCP components: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
