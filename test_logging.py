#!/usr/bin/env python3
"""Test script to verify direct file logging."""

import logging
import os
import sys
import time
from pathlib import Path

# Configure basic logging to file and stderr
log_dir = Path("logs/direct")
log_dir.mkdir(parents=True, exist_ok=True)

log_file = log_dir / f"test_log_{time.strftime('%Y%m%d_%H%M%S')}.log"

# Setup file handler
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

# Setup stderr handler
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)
root_logger.addHandler(stderr_handler)

# Log some test messages
root_logger.info(f"Test logging started - writing to {log_file}")
root_logger.debug("This is a debug message")
root_logger.warning("This is a warning message")
root_logger.error("This is an error message")

# Print some info to stdout
print(f"Wrote log to: {log_file}")
print(f"Current directory: {os.getcwd()}")
print(f"Python version: {sys.version}")

# Also write directly to the file
try:
    with open(log_file, "a") as f:
        f.write(f"\nDIRECT WRITE: Test completed at {time.ctime()}\n")
        f.write(
            f"DIRECT WRITE: Environment: {os.environ.get('MCP_LOG_LEVEL', 'Not set')}\n"
        )
except Exception as e:
    print(f"Error writing directly to file: {e}", file=sys.stderr)

print("Test logging complete!")
