"""Structured logging implementation for MCP.

This module provides JSON-formatted structured logging with file and stdout output.
"""

import json
import logging
import time
import traceback
from datetime import datetime
from functools import wraps
from logging.handlers import RotatingFileHandler
from typing import Optional

from .config import log_config


class StructuredLogger:
    """JSON-formatted structured logger."""

    def __init__(self, name: str, level: Optional[str] = None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level or log_config.log_level)

        # Clear any existing handlers
        self.logger.handlers = []

        # Add handlers
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup log handlers based on configuration."""
        # Add JSON formatter to all handlers
        formatter = JsonFormatter()

        # Add file handler
        service_type = self.name.split(".")[0]  # e.g., 'core' from 'core.app'
        log_dir = log_config.get_log_dir(service_type)
        log_file = log_dir / log_config.file_name_template.format(
            service=self.name, date=datetime.now().strftime("%Y%m%d")
        )

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=log_config.max_size,
            backupCount=log_config.backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Add stdout handler if enabled
        if log_config.enable_stdout:
            stdout_handler = logging.StreamHandler()
            stdout_handler.setFormatter(formatter)
            self.logger.addHandler(stdout_handler)

    def _log(self, level: str, message: str, **kwargs):
        """Log with additional context."""
        extra = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.name,
            **kwargs,
        }

        getattr(self.logger, level.lower())(message, extra={"context": extra})

    def info(self, message: str, **kwargs):
        """Log at INFO level."""
        self._log("INFO", message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log at ERROR level."""
        self._log("ERROR", message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log at DEBUG level."""
        self._log("DEBUG", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log at WARNING level."""
        self._log("WARNING", message, **kwargs)


class JsonFormatter(logging.Formatter):
    """JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        data = {
            "level": record.levelname,
            "message": record.getMessage(),
            **(getattr(record, "context", {})),
        }
        return json.dumps(data)


def log_execution_time(logger: StructuredLogger):
    """Decorator to log function execution time."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    f"{func.__name__} completed",
                    execution_time_ms=int(execution_time * 1000),
                    function=func.__name__,
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"{func.__name__} failed",
                    execution_time_ms=int(execution_time * 1000),
                    function=func.__name__,
                    error=str(e),
                    traceback=traceback.format_exc(),
                )
                raise

        return wrapper

    return decorator


# Create default logger instance
logger = StructuredLogger("mcp_core")
