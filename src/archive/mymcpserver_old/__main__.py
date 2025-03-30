"""Entry point for the MCP server.

This module provides the main entry point when running the package as a module.
"""

import sys

# Import package components - logging will be initialized by __init__.py
from mymcpserver import logger
from mymcpserver.server import cli

if __name__ == "__main__":
    logger.info("Starting MCP server as module")
    try:
        cli()
        logger.info("MCP server completed successfully")
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Error running MCP server: {e}", exc_info=True)
        sys.exit(1)
