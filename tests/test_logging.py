#!/usr/bin/env python3
"""Test script for the centralized logging implementation."""

import logging

from config import load_and_get_config

# No need to manually add src path - pytest will handle this via pythonpath in pyproject.toml
# Instead, just import directly from the modules
from mcp_core.logger import StructuredLogger
from mcp_core.logger.logger import configure_logging


def test_logging_centralization() -> None:
    """Test that logging is correctly centralized with appropriate directory structure."""
    # Basic bootstrap logging
    logging.basicConfig(level="INFO", format="%(levelname)s:%(name)s: %(message)s")
    bootstrap_logger = logging.getLogger("test_bootstrap")
    bootstrap_logger.info("Starting logging test")

    # Load config
    config = load_and_get_config()

    # Initialize centralized logging
    bootstrap_logger.info("Configuring centralized logging system...")
    configure_logging(config)
    bootstrap_logger.info(f"Log directories initialized under {config.logs_path}")

    # Test loggers for different services
    loggers = [
        StructuredLogger("mcp_core.test"),
        StructuredLogger("mcp_proxy.test"),
        StructuredLogger("tool_servers.python.test"),
        StructuredLogger("mymcpserver.test"),
        StructuredLogger("misc.test"),
    ]

    # Log messages to each logger
    for logger in loggers:
        logger.info(f"Test log message from {logger.name}")
        logger.debug(f"Debug message from {logger.name}", extra_data="test")
        logger.warning(f"Warning message from {logger.name}")
        logger.error(f"Error message from {logger.name}")

    # Verify directories exist
    assert (config.logs_path / "core").exists(), "Core log directory not created"
    assert (config.logs_path / "proxy").exists(), "Proxy log directory not created"
    assert (config.logs_path / "tools").exists(), "Tools log directory not created"
    assert (config.logs_path / "server").exists(), "Server log directory not created"
    assert (config.logs_path / "misc").exists(), "Misc log directory not created"

    bootstrap_logger.info("Logging test completed. Check log files in each directory.")
    print("\nTest completed! Log files should have been created in these directories:")
    print(f"- {config.logs_path / 'core'}")
    print(f"- {config.logs_path / 'proxy'}")
    print(f"- {config.logs_path / 'tools'}")
    print(f"- {config.logs_path / 'server'}")
    print(f"- {config.logs_path / 'misc'}")


# For manual execution outside pytest
if __name__ == "__main__":
    test_logging_centralization()
