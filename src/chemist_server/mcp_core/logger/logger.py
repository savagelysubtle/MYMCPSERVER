# src/mcp_core/logger/logger.py
import json
import logging
import sys
import time
from collections.abc import Callable, Coroutine
from datetime import datetime
from functools import wraps
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ...config import AppConfig, LoggingConfig

# --- Global state for configured logging ---
_is_logging_configured = False
_global_log_config: Optional["LoggingConfig"] = None
_global_logs_path: Path | None = None
_configured_formatter: logging.Formatter | None = None
_log_handlers: dict[str, logging.FileHandler] = {}  # Cache handlers by file path


# --- JSON Formatter (keep as before) ---
class JsonFormatter(logging.Formatter):
    """JSON log formatter that safely handles structured logging data."""

    def format(self, record: logging.LogRecord) -> str:
        # Create base log record with standard fields
        log_record = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=datetime.now().astimezone().tzinfo
            ).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        # Add any additional fields from __dict__ that might have been added via extra
        # This avoids direct attribute access that the linter complains about
        for key, value in record.__dict__.items():
            # Skip standard LogRecord attributes and internal attributes
            if key not in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            } and not key.startswith("_"):
                log_record[key] = value

        # Handle exception info
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Handle stack info
        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(log_record, default=str)


# --- Structured Logger Class ---
class StructuredLogger:
    """JSON-formatted structured logger, configured via AppConfig."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.logger = logging.getLogger(name)

        # Configure level and handlers if global setup has run
        if _is_logging_configured and _global_log_config and _global_logs_path:
            self.logger.setLevel(_global_log_config.level.upper())
            self._add_file_handler_if_needed(_global_log_config, _global_logs_path)
            # Prevent double logging if root has stdout and we have a file handler
            if _global_log_config.enable_stdout and any(
                isinstance(h, logging.FileHandler) for h in self.logger.handlers
            ):
                self.logger.propagate = False
            else:
                self.logger.propagate = (
                    True  # Propagate to root (for stdout) if no file handler added
                )
        else:
            # Default level before configuration, might get overwritten
            self.logger.setLevel(logging.INFO)
            self.logger.propagate = True  # Propagate until configured

    def _add_file_handler_if_needed(
        self, log_cfg: "LoggingConfig", base_logs_path: Path
    ) -> None:
        """Adds a configured RotatingFileHandler for this logger's service if not already added."""
        global _configured_formatter, _log_handlers

        if not _configured_formatter:  # Should not happen if setup_global_logging ran
            print("WARN: Logger formatter not configured.", file=sys.stderr)
            return

        try:
            # Determine service dir and log file path
            log_dir = get_log_dir(base_logs_path, self.name)
            log_file = log_dir / log_cfg.file_name_template.format(
                service=self.name.replace(".", "_"),  # Sanitize name for filename
                date=datetime.now().strftime("%Y%m%d"),
            )
            log_file_str = str(log_file)

            # Check if a handler for this *specific file* already exists
            if log_file_str in _log_handlers:
                # Add existing handler to this logger if not already present
                if _log_handlers[log_file_str] not in self.logger.handlers:
                    self.logger.addHandler(_log_handlers[log_file_str])
            else:
                # Create, configure, and cache new handler
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=log_cfg.max_size_mb * 1024 * 1024,
                    backupCount=log_cfg.backup_count,
                    encoding="utf-8",
                )
                file_handler.setFormatter(_configured_formatter)
                self.logger.addHandler(file_handler)
                _log_handlers[log_file_str] = file_handler  # Cache it
                # Use basic print as this might be called before root logger is fully ready
                # print(f"INFO: Added file handler for {self.name} to {log_file_str}")

        except Exception as e:
            print(
                f"ERROR: Failed to add file handler for {self.name}: {e}",
                file=sys.stderr,
            )

    def _log(
        self,
        level_name: str,
        message: str,
        exc_info: bool | tuple | None = None,
        stack_info: bool | None = None,
        **kwargs: Any,
    ) -> None:
        # Convert level name to numeric level using direct attribute access instead of deprecated getLevelName
        try:
            level = getattr(logging, level_name.upper())
        except AttributeError:
            # Fallback to INFO if level name is invalid
            level = logging.INFO

        # Only log if this level is enabled
        if self.logger.isEnabledFor(level):
            # Ensure stack_info is a boolean, not None
            stack_info_bool = bool(stack_info) if stack_info is not None else False

            # Instead of using a context dict, pass each kwarg as a separate extra field
            extra_data = {}
            for key, value in kwargs.items():
                extra_data[key] = value

            self.logger.log(
                level,
                message,
                exc_info=exc_info,
                stack_info=stack_info_bool,
                extra=extra_data,  # Pass kwargs directly as extra fields
            )

    # --- Public Logging Methods (keep as before) ---
    def debug(self, message: str, **kwargs: Any) -> None:
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log("WARNING", message, **kwargs)

    def error(
        self,
        message: str,
        exc_info: bool | tuple | None = None,
        stack_info: bool | None = None,
        **kwargs: Any,
    ) -> None:
        self._log("ERROR", message, exc_info=exc_info, stack_info=stack_info, **kwargs)

    def critical(
        self,
        message: str,
        exc_info: bool | tuple | None = None,
        stack_info: bool | None = None,
        **kwargs: Any,
    ) -> None:
        self._log(
            "CRITICAL", message, exc_info=exc_info, stack_info=stack_info, **kwargs
        )


# --- Global Logging Setup ---
def get_log_dir(base_log_path: Path, service_name: str) -> Path:
    """Get the appropriate log directory for a service.

    Args:
        base_log_path: Base logs directory
        service_name: Name of the service/logger (dot notation)

    Returns:
        Path: The appropriate log directory
    """
    parts = service_name.split(".")

    # Map service name patterns to log directories according to architecture doc
    if parts[0] == "mcp_core" or service_name.startswith("mcp_core."):
        service_dir = base_log_path / "core"
    elif parts[0] == "tool_servers" or service_name.startswith("tool_servers."):
        # For tool servers, create specific subdirectories if available
        if len(parts) > 1:
            service_dir = base_log_path / "tools" / parts[1].replace("_", "-")
        else:
            service_dir = base_log_path / "tools"
    elif parts[0] == "mcp_proxy" or service_name.startswith("mcp_proxy."):
        service_dir = base_log_path / "proxy"
    elif parts[0] == "mymcpserver" or service_name.startswith("mymcpserver."):
        # Server-wide logs go to the server directory
        service_dir = base_log_path / "server"
    else:
        # Other/miscellaneous logs
        service_dir = base_log_path / "misc"

    # Ensure directory exists
    service_dir.mkdir(parents=True, exist_ok=True)
    return service_dir


def configure_logging(config: "AppConfig") -> None:
    """Configures the root logger (mainly for stdout) and stores config.

    Args:
        config: Application configuration object
    """
    global \
        _is_logging_configured, \
        _global_log_config, \
        _global_logs_path, \
        _configured_formatter

    if _is_logging_configured:
        print("INFO: Logging already configured.")
        return

    log_config = config.logging
    logs_path = config.logs_path

    # Ensure all required log directories exist
    required_dirs = [
        logs_path / "core",
        logs_path / "proxy",
        logs_path / "server",
        logs_path / "tools",
        logs_path / "misc",
    ]
    for directory in required_dirs:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"INFO: Ensured log directory exists: {directory}")

    root_logger = logging.getLogger()
    log_level_int = logging.getLevelName(config.get_effective_log_level())

    root_logger.setLevel(log_level_int)

    # Determine formatter
    if log_config.format == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    _configured_formatter = formatter

    # Clear existing root handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    # Add stdout handler to root logger IF enabled
    if log_config.enable_stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        root_logger.addHandler(stdout_handler)
        print("INFO: Logging to stdout enabled.")
    else:
        print("INFO: Logging to stdout disabled.")

    # Store config for StructuredLogger instances to use
    _global_log_config = log_config
    _global_logs_path = logs_path
    _is_logging_configured = True

    print(f"INFO: Root logger level set to {log_config.level}")
    # Use basic print here as structured logger might not be fully ready yet


# --- Decorator (keep as before) ---
def log_execution_time(logger_instance: StructuredLogger) -> Callable:
    # ...
    def decorator(
        func: Callable[..., Coroutine[Any, Any, Any]],
    ) -> Callable[..., Coroutine[Any, Any, Any]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            func_name = func.__name__
            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000  # milliseconds
                logger_instance.debug(
                    f"{func_name} completed",
                    duration_ms=f"{execution_time:.2f}",
                    function=func_name,
                )
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger_instance.error(
                    f"{func_name} failed",
                    duration_ms=f"{execution_time:.2f}",
                    function=func_name,
                    error=str(e),
                    exc_info=True,  # Capture traceback
                )
                raise

        return wrapper

    return decorator


# --- Default Logger Instance ---
# This logger will get its handlers configured when setup_global_logging is called
logger = StructuredLogger("mcp_core.default")
