#!/usr/bin/env python3
"""
Comprehensive logging test script.
This script tests logging at multiple levels and to multiple directories
to help diagnose issues with the MCP logging system.
"""

import logging
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

# Ensure src is in path
src_path = Path(__file__).resolve().parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

print("=" * 80)
print(f"LOGGING TEST STARTED AT {datetime.now()}")
print(f"Python: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Script location: {__file__}")
print("=" * 80)

try:
    # 1. Basic file logging test
    print("\n[1/6] Testing basic file logging...")
    logs_dir = Path("logs/test")
    logs_dir.mkdir(parents=True, exist_ok=True)

    basic_log_file = logs_dir / f"basic_test_{time.strftime('%Y%m%d_%H%M%S')}.log"

    # Setup basic file logging
    basic_handler = logging.FileHandler(basic_log_file)
    basic_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(basic_handler)

    # Log test messages at different levels
    root_logger.debug("Basic debug message")
    root_logger.info("Basic info message")
    root_logger.warning("Basic warning message")
    root_logger.error("Basic error message")

    print(f"  ✓ Basic log file created: {basic_log_file}")

    # 2. Test direct file writing
    print("\n[2/6] Testing direct file writing...")
    direct_log_file = logs_dir / f"direct_test_{time.strftime('%Y%m%d_%H%M%S')}.log"

    with open(direct_log_file, "w") as f:
        f.write(f"DIRECT WRITE TEST at {datetime.now().isoformat()}\n")
        f.write(f"Python path: {sys.path}\n")
        f.write("Environment variables:\n")

        for key, value in sorted(os.environ.items()):
            if key.startswith(("MCP_", "PYTHON")):
                f.write(f"  {key}={value}\n")

    print(f"  ✓ Direct file created: {direct_log_file}")

    # 3. Test importing and configuring MCP logging
    print("\n[3/6] Testing MCP configuration import...")
    try:
        from src.chemist_server.config import load_and_get_config

        print("  ✓ Configuration module imported")

        config = load_and_get_config()
        print("  ✓ Configuration loaded")
        print(f"    - Log level: {config.get_effective_log_level()}")
        print(f"    - Log format: {config.logging.format}")
        print(f"    - Log path: {config.logs_path}")

        # Try importing the logger module
        from src.chemist_server.mcp_core.logger import StructuredLogger

        print("  ✓ Logger module imported")

        # Try configuring logging
        from src.chemist_server.mcp_core.logger.logger import configure_logging

        configure_logging(config)
        print("  ✓ Logging system configured")

    except ImportError as e:
        print(f"  ✗ Failed to import MCP modules: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"  ✗ Error during configuration: {e}")
        traceback.print_exc()

    # 4. Test structured logging to each log directory
    print("\n[4/6] Testing structured logging to all directories...")
    try:
        # Ensure all log directories exist
        log_dirs = [
            ("core", "mcp_core.test"),
            ("proxy", "mcp_proxy.test"),
            ("server", "mymcpserver.test"),
            ("tools", "tool_servers.test"),
            ("misc", "misc_test"),
        ]

        for dir_name, logger_name in log_dirs:
            # Create a structured logger for each directory
            test_logger = StructuredLogger(logger_name)

            # Log test messages at all levels
            test_logger.debug("Debug test from logs_tester.py")
            test_logger.info("Info test from logs_tester.py")
            test_logger.warning("Warning test from logs_tester.py")
            test_logger.error("Error test from logs_tester.py")

            print(f"  ✓ Logged to {dir_name} directory using {logger_name}")

    except Exception as e:
        print(f"  ✗ Error during structured logging: {e}")
        traceback.print_exc()

    # 5. Test tool server logger
    print("\n[5/6] Testing Python tool server logger...")
    try:
        # Try to import the tool server module
        from src.chemist_server.tool_servers.python_tool_server.server import (
            logger as tool_logger,
        )

        # Try logging with the tool server logger
        tool_logger.debug("Debug message from logs_tester.py")
        tool_logger.info("Info message from logs_tester.py")
        tool_logger.warning("Warning message from logs_tester.py")
        tool_logger.error("Error message from logs_tester.py")

        print("  ✓ Tool server logger test complete")

    except ImportError as e:
        print(f"  ✗ Failed to import tool server logger: {e}")
    except Exception as e:
        print(f"  ✗ Error using tool server logger: {e}")
        traceback.print_exc()

    # 6. List all log files that were created
    print("\n[6/6] Checking for created log files...")

    for root, dirs, files in os.walk(Path("logs")):
        for file in files:
            file_path = Path(root) / file
            if (
                file_path.stat().st_mtime > time.time() - 300
            ):  # Files modified in the last 5 minutes
                print(f"  - {file_path} ({file_path.stat().st_size} bytes)")

except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()

print("\n" + "=" * 80)
print(f"LOGGING TEST COMPLETED AT {datetime.now()}")
print("=" * 80)
