#!/usr/bin/env python3
"""Test script to verify config loading."""

import os
import sys
from pathlib import Path

# Ensure src is in the path
src_path = Path.cwd()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Create logs directory
logs_dir = Path("logs")
logs_dir.mkdir(parents=True, exist_ok=True)

# Log file path
log_file = logs_dir / "config_test.log"

try:
    with open(log_file, "w") as f:
        f.write("Configuration Test Starting\n")
        f.write(f"Python Path: {sys.path}\n")
        f.write(f"Working Directory: {os.getcwd()}\n")
        f.write("Environment Variables:\n")

        for key, value in sorted(os.environ.items()):
            if key.startswith(("MCP_", "PYTHON")):
                f.write(f"  {key}={value}\n")

        # Now try to import and load the config
        f.write("\nAttempting to import config...\n")

        from src.chemist_server.config import load_and_get_config

        f.write("Config module imported successfully\n")

        config = load_and_get_config()

        f.write("Config loaded successfully\n")
        f.write(f"Vault Path: {config.vault_path}\n")
        f.write(f"Logs Path: {config.logs_path}\n")
        f.write(f"Components: {config.components}\n")
        f.write(f"Transport: {config.transport}\n")
        f.write(f"Log Level: {config.get_effective_log_level()}\n")

        # Try to import logger
        f.write("\nAttempting to import logger...\n")

        from src.chemist_server.mcp_core.logger import StructuredLogger

        f.write("Logger module imported successfully\n")

        # Try to configure logging
        f.write("\nAttempting to configure logging...\n")

        from src.chemist_server.mcp_core.logger.logger import configure_logging

        configure_logging(config)

        f.write("Logging configured successfully\n")

        # Create a logger instance
        logger = StructuredLogger("config_test")

        f.write("Logger instance created successfully\n")

        # Try to log a message
        f.write("\nAttempting to log a message...\n")

        logger.info("Test message from config test")

        f.write("Message logged successfully\n")

    print(f"Config test completed successfully. Check {log_file} for details.")

except Exception as e:
    # Log the error to file and console
    try:
        error_log = logs_dir / "config_test_error.log"
        with open(error_log, "w") as f:
            f.write(f"Error during config test: {e}\n")
            import traceback

            f.write(traceback.format_exc())
    except Exception:
        pass

    print(f"Error during config test: {e}", file=sys.stderr)
    import traceback

    traceback.print_exc()
