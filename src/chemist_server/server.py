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
    sys.path.insert(0, str(_bootstrap_src_path))

try:
    # Import after potential path modification
    from chemist_server.config import AppConfig, load_and_get_config
    from chemist_server.mcp_core.logger import StructuredLogger
    from chemist_server.mcp_core.logger.logger import configure_logging
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
        from chemist_server.mcp_core.app import get_fastmcp_app

        app = get_fastmcp_app(config)
        transport = config.transport
        core_runner_logger.info(
            f"Starting MCP Core via FastMCP with {transport} transport"
        )

        if transport == "stdio":
            await app.run_stdio_async()
        elif transport in ["sse", "http"]:
            # Use effective host/port from config helpers
            # Need to check the actual API of run_sse_async
            core_host = config.get_core_host()
            core_port = config.get_core_port()
            core_runner_logger.info(f"Starting SSE server on {core_host}:{core_port}")
            await app.run_sse_async()  # Assuming it reads host/port from config
        else:
            core_runner_logger.error(f"Unsupported transport for Core: {transport}")
            raise ValueError(f"Unsupported transport: {transport}")
        core_runner_logger.info(
            "Core service finished."
        )  # Will only log if it exits cleanly

    except Exception as e:
        core_runner_logger.error(f"Core service failed: {e}", exc_info=True)
        raise  # Propagate failure to task group


# Removed start_python_tool_server function


async def run_services(config: AppConfig) -> None:
    """Runs the selected MCP services concurrently."""
    runner_logger = StructuredLogger("mymcpserver.service_runner")
    components_to_run = config.components
    runner_logger.info(f"Configured components: {components_to_run}")

    try:
        async with anyio.create_task_group() as tg:
            # All components now mean the same as core, since we've integrated everything
            if components_to_run in ["all", "core", "tool"]:
                runner_logger.info("Starting Core Service with Integrated Tools...")
                tg.start_soon(start_core_service, config)

            runner_logger.info("All services started.")
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
    logging.basicConfig(level="DEBUG", format="%(levelname)s:%(name)s: %(message)s")
    bootstrap_logger = logging.getLogger("mcp_runner_bootstrap")
    bootstrap_logger.debug("Starting MCP Runner with debug logging")

    try:
        # Ensure src path is set for potential imports
        src_path = Path(__file__).parent
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
            bootstrap_logger.debug(f"Added {src_path} to sys.path")
            bootstrap_logger.debug(f"Current sys.path: {sys.path}")

        args = parse_args()
        bootstrap_logger.debug(f"Parsed arguments: {args}")

        bootstrap_logger.debug("Loading configuration...")
        config = load_and_get_config(vars(args))
        bootstrap_logger.debug(f"Loaded config: {config}")

        # Initialize centralized logging configuration
        bootstrap_logger.info("Configuring centralized logging system...")
        configure_logging(config)
        bootstrap_logger.debug(f"Log directories initialized under {config.logs_path}")
        bootstrap_logger.debug(f"Available log handlers: {logging.root.handlers}")

        # Now create a structured logger that will use the configured system
        main_logger = StructuredLogger("mymcpserver.runner")
        main_logger.debug("Python executable: " + str(sys.executable))
        main_logger.debug("Python path: " + str(sys.path))
        main_logger.info(
            "Structured logging initialized.",
            config=config.model_dump(mode="json", exclude={"core": {"auth_token"}}),
        )

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
