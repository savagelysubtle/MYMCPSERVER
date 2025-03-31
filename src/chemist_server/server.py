#!/usr/bin/env python3
"""MCP System Runner - Single Entry Point."""

import argparse
import logging  # For bootstrap only
import sys
import time
from pathlib import Path

import anyio
from anyio.to_thread import run_sync as anyio_run_sync

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


async def start_python_tool_server(config: AppConfig) -> None:
    tool_runner_logger = StructuredLogger("mymcpserver.pytool_runner")
    print("=== STARTING PYTHON TOOL SERVER WRAPPER ===", file=sys.stderr)
    try:
        # Late import
        print("=== IMPORTING PYTHON TOOL SERVER MODULE ===", file=sys.stderr)
        from chemist_server.tool_servers.python_tool_server.server import (
            start_server as start_py_tool_server,
        )

        tool_runner_logger.info("Attempting to start Python Tool Server...")
        print("=== GETTING PYTHON TOOL SERVER CONFIG ===", file=sys.stderr)

        # Get the configuration parameters
        host = config.get_tool_server_python_host()
        port = config.get_tool_server_python_port()

        # Set up logging directory explicitly for the tool server
        tool_log_dir = Path(config.logs_path) / "tools" / "python-tool-server"
        tool_log_dir.mkdir(parents=True, exist_ok=True)

        # Use plain text file logging to avoid JSON issues
        log_file = tool_log_dir / f"python_tool_server_{host}_{port}.log"
        print(f"=== SETTING UP LOG FILE AT: {log_file} ===", file=sys.stderr)

        # Create a file handler for direct logging (not through the structured logger)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        # Add this handler to the Python logger module
        logging.getLogger().addHandler(file_handler)
        print("=== DIRECT FILE LOGGING SETUP COMPLETE ===", file=sys.stderr)

        # Run the blocking function in a worker thread
        tool_runner_logger.info(f"Starting Python Tool Server on {host}:{port}")
        print(
            f"=== ABOUT TO START PYTHON TOOL SERVER ON {host}:{port} ===",
            file=sys.stderr,
        )

        # Using anyio 4.9.0 syntax for running in worker thread
        # Create a wrapper function to pass the parameters
        def start_server_with_params() -> None:
            print("=== INSIDE WRAPPER FUNCTION ===", file=sys.stderr)
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"\n=== STARTING SERVER AT {time.ctime()} ===\n")

                start_py_tool_server(host=host, port=port)
                print("=== TOOL SERVER START CALL COMPLETED ===", file=sys.stderr)

                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"\n=== SERVER COMPLETED AT {time.ctime()} ===\n")
            except Exception as e:
                print(
                    f"=== ERROR IN WRAPPER: {type(e).__name__} - {str(e)} ===",
                    file=sys.stderr,
                )
                import traceback

                error_trace = traceback.format_exc()
                print(f"=== TRACEBACK: {error_trace} ===", file=sys.stderr)

                # Write error directly to file to avoid JSON issues
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"\n=== ERROR AT {time.ctime()} ===\n")
                    f.write(f"Error: {type(e).__name__} - {str(e)}\n")
                    f.write(f"Traceback:\n{error_trace}\n")

                raise
            # No return statement here, implicitly returns None

        print("=== CALLING ANYIO_RUN_SYNC ===", file=sys.stderr)
        await anyio_run_sync(start_server_with_params)
        print("=== ANYIO_RUN_SYNC RETURNED ===", file=sys.stderr)

        tool_runner_logger.info(
            "Python Tool Server finished."
        )  # Will only log on clean exit

    except Exception as e:
        print(
            f"=== PYTHON TOOL SERVER WRAPPER EXCEPTION: {type(e).__name__} - {str(e)} ===",
            file=sys.stderr,
        )
        import traceback

        error_trace = traceback.format_exc()
        print(f"=== TRACEBACK: {error_trace} ===", file=sys.stderr)

        # Try to write error directly to a fallback file
        try:
            fallback_log = Path(config.logs_path) / "python_tool_server_error.log"
            with open(fallback_log, "a", encoding="utf-8") as f:
                f.write(f"\n=== WRAPPER ERROR AT {time.ctime()} ===\n")
                f.write(f"Error: {type(e).__name__} - {str(e)}\n")
                f.write(f"Traceback:\n{error_trace}\n")
        except Exception:
            pass  # If this fails, we've already printed to stderr

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
