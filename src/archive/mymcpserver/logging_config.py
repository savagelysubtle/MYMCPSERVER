"""Centralized logging configuration for MYMCPSERVER.

This module provides a consistent logging setup across all components of the application.
Supports both file-based logging and stdout for Cursor's stdio Transport.
"""

from __future__ import annotations

__all__ = ["setup_logging"]
__version__ = "0.1.0"

# Standard library imports
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    log_filename: str = "mymcpserver.log",
    enable_stdout: bool = True,
    cursor_format: bool = False,
) -> None:
    """Set up logging configuration for the application.

    Args:
        log_level: The logging level to use (default: INFO)
        log_dir: Directory to store log files (default: logs/ in project root)
        log_filename: Name of the log file (default: mymcpserver.log)
        enable_stdout: Whether to enable console output (default: True)
        cursor_format: Whether to use Cursor-specific format for stdio Transport (default: False)
    """
    # Create logs directory if it doesn't exist
    if log_dir is None:
        # Default to logs/ in the project root or src directory
        logs_path = os.getenv("LOGS_PATH", "logs")
        # Make sure to expand any variables in the path
        logs_path = os.path.expandvars(logs_path)
        log_dir = Path(logs_path)

    # Ensure log_dir is properly resolved without variable names
    try:
        log_dir = log_dir.resolve()
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / log_filename
    except Exception as e:
        fallback_dir = Path.cwd() / "logs"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        log_file = fallback_dir / log_filename
        print(
            f"Warning: Could not use specified log directory: {e}. Using {fallback_dir} instead.",
            file=sys.stderr,
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Configure logging formats
    file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Use simpler format for Cursor stdio Transport
    stdout_format = "%(levelname)s: %(message)s" if cursor_format else file_format

    # Set up file handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(logging.Formatter(file_format, date_format))
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not set up file logging: {e}", file=sys.stderr)

    # Set up stdout handler if enabled
    if enable_stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(logging.Formatter(stdout_format, date_format))
        root_logger.addHandler(stdout_handler)

    # Log initial setup
    root_logger.info(f"Logging initialized: {log_file}")
    root_logger.info(f"Log level: {log_level}")
    root_logger.info(f"Stdout enabled: {enable_stdout}")
    root_logger.info(f"Cursor format: {cursor_format}")
