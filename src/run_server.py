#!/usr/bin/env python3
"""MCP System Runner - Single Entry Point."""

import argparse
import logging  # For bootstrap only
import sys
from pathlib import Path

import anyio

# --- Centralized Config and Logging ---
# Make sure src is added before these imports if run directly
_bootstrap_src_path = Path(__file__).parent
if str(_bootstrap_src_path) not in sys.path:
    sys.path.insert(0, str(_bootstrap_path))

try:
    # Import setup_global_logging AFTER potential path modification
    from mcp_core.logger import StructuredLogger, setup_global_logging
    from mymcpserver.config import AppConfig, load_and_get_config
except ImportError as e:
    # Critical error if core modules can't be found
    logging.basicConfig(level="ERROR")
    logging.critical(
        f"Failed to import core modules. Ensure PYTHONPATH is set correctly or run from project root. Error: {e}",
        exc_info=True,
    )
    sys.exit(1)


# --- Component Startups ---
async def start_core_service(config: AppConfig) -> None:
    core_runner_logger = StructuredLogger("mymcpserver.core_runner")
    try:
        # Late import to ensure logging is set up
        from mcp_core.app import get_fastmcp_app

        app = get_fastmcp_app(config)
        transport = config.transport
        core_runner_logger.info(
            f"Starting MCP Core via FastMCP with {transport} transport"
        )

        if transport == "stdio":
            await app.run_stdio_async()
        elif transport in ["sse", "http"]:
            # Use effective host/port from config helpers
            await app.run_sse_async(
                host=config.get_core_host(), port=config.get_core_port()
            )
        else:
            core_runner_logger.error(f"Unsupported transport for Core: {transport}")
            raise ValueError(f"Unsupported transport: {transport}")
        core_runner_logger.info(
            "Core service finished."
        )  # Will only log if it exits cleanly

    except Exception as e:
        core_runner_logger.error(f"Core service failed: {e}", exc_info=True)
        raise  # Propagate failure to task group


async def start_python_tool_server(config: AppConfig) -> None:
    tool_runner_logger = StructuredLogger("mymcpserver.pytool_runner")
    try:
        # Late import
        from tool_servers.python_tool_server.server import (
            start_server as start_py_tool_server,
        )

        tool_runner_logger.info("Attempting to start Python Tool Server...")
        # Run the blocking uvicorn server in a thread
        await anyio.to_thread.run_sync(
            start_py_tool_server,
            host=config.get_tool_server_python_host(),
            port=config.get_tool_server_python_port(),
        )
        tool_runner_logger.info(
            "Python Tool Server finished."
        )  # Will only log on clean exit

    except Exception as e:
        tool_runner_logger.error(f"Python Tool Server failed: {e}", exc_info=True)
        raise  # Propagate failure


async def run_services(config: AppConfig) -> None:
    """Runs the selected MCP services concurrently."""
    runner_logger = StructuredLogger("mymcpserver.service_runner")
    components_to_run = config.components
    runner_logger.info(f"Configured components: {components_to_run}")

    try:
        async with anyio.create_task_group() as tg:
            if components_to_run in ["all", "core"]:
                runner_logger.info("Starting Core Service Task...")
                tg.start_soon(start_core_service, config)

            if components_to_run in ["all", "tool"]:
                # For now, only start Python tool server
                # Add logic here to start other tool servers if needed
                runner_logger.info("Starting Python Tool Server Task...")
                tg.start_soon(start_python_tool_server, config)

            runner_logger.info("All selected services started.")
    except Exception as e:
        runner_logger.error(f"Error within service task group: {e}", exc_info=True)
        raise  # Allow main loop to catch and exit


# --- Main Execution ---
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MCP System Runner")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        help="Override transport mechanism (default: from env/config)",
    )
    parser.add_argument(
        "--host", help="Override host for servers (default: from env/config)"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Override base port for Core server (default: from env/config)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Override logging level (default: from env/config)",
    )
    parser.add_argument(
        "--component",
        choices=["all", "core", "tool"],
        help="Override component(s) to start (default: from env/config)",
    )
    return parser.parse_args()


def main() -> int:
    # Basic bootstrap logging for initial setup/errors
    logging.basicConfig(level="INFO", format="%(levelname)s:%(name)s: %(message)s")
    bootstrap_logger = logging.getLogger("mcp_runner_bootstrap")

    try:
        # Ensure src path is set for potential imports during config loading
        src_path = Path(__file__).parent
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
            bootstrap_logger.info(f"Added {src_path} to sys.path")

        args = parse_args()
        config = load_and_get_config(vars(args))

        # Initialize Structured Logging using loaded config
        # This replaces the basicConfig for subsequent logging
        setup_global_logging(config)
        main_logger = StructuredLogger("mymcpserver.runner")
        main_logger.info(
            "Structured logging initialized.",
            config=config.model_dump(mode="json", exclude={"core": {"auth_token"}}),
        )  # Exclude sensitive fields

    except Exception as e:
        bootstrap_logger.critical(f"Failed during initial setup: {e}", exc_info=True)
        return 1

    # --- Run Services ---
    try:
        main_logger.info(
            f"Running components: {config.components} with transport: {config.transport}"
        )
        anyio.run(run_services, config)
        main_logger.info("run_services completed.")  # Log clean exit if it happens
        exit_code = 0

    except KeyboardInterrupt:
        main_logger.info("Runner interrupted by user")
        exit_code = 0
    except Exception as e:
        main_logger.critical(
            f"Critical error during service execution: {e}", exc_info=True
        )
        exit_code = 1
    finally:
        main_logger.info("MCP Runner shutting down.")
        # Add any final cleanup needed here

    return exit_code


if __name__ == "__main__":
    # Ensure src is in the path *before* any potential imports in __main__ block
    _src_path = Path(__file__).parent
    if str(_src_path) not in sys.path:
        sys.path.insert(0, str(_src_path))
    sys.exit(main())
