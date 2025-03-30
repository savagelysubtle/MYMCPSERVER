# src/mcp_core/logger/logger.py
import json
import logging
import sys  # For stdout handler
import time
from datetime import datetime
from functools import wraps
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mymcpserver.config import AppConfig


# --- JSON Formatter ---
class JsonFormatter(logging.Formatter):
    """JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=datetime.now().astimezone().tzinfo
            ).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "context") and isinstance(record.context, dict):
            log_record.update(record.context)
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            # Add traceback string if needed:
            # log_record["traceback"] = traceback.format_exc()
        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info)

        # Ensure all values are JSON serializable
        return json.dumps(log_record, default=str)


# --- Structured Logger Class ---
class StructuredLogger:
    """JSON-formatted structured logger, configured via AppConfig."""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)
        # Level and handlers are set globally by setup_global_logging

    def _log(
        self, level_name: str, message: str, exc_info=None, stack_info=None, **kwargs
    ):
        level = logging.getLevelName(level_name.upper())
        if not isinstance(level, int):
            level = logging.INFO
        if self.logger.isEnabledFor(level):
            # Pass kwargs directly to the logging call; adapter is not needed
            # if the formatter handles the 'extra' dictionary.
            # Alternatively, manually merge kwargs into an 'extra' dict.
            # Let's modify the formatter slightly or just use extra=kwargs
            self.logger.log(
                level,
                message,
                exc_info=exc_info,
                stack_info=stack_info,
                extra={"context": kwargs},
            )

    def debug(self, message: str, **kwargs):
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, exc_info=None, stack_info=None, **kwargs):
        self._log("ERROR", message, exc_info=exc_info, stack_info=stack_info, **kwargs)

    def critical(self, message: str, exc_info=None, stack_info=None, **kwargs):
        self._log(
            "CRITICAL", message, exc_info=exc_info, stack_info=stack_info, **kwargs
        )


# --- Global Logging Setup ---
_is_logging_configured = False
_configured_formatter: logging.Formatter | None = None


def get_log_dir(base_log_path: Path, service_name: str) -> Path:
    """Determines the log directory for a given service name."""
    parts = service_name.split(".")
    # Create subdirs like logs/core/, logs/tools/py-tool-server/, logs/mymcpserver/
    if len(parts) > 1 and parts[0] in ["mcp_core", "tool_servers", "mymcpserver"]:
        if parts[0] == "tool_servers" and len(parts) > 1:
            # e.g., tool_servers.python_tool_server -> logs/tools/python_tool_server
            service_dir = base_log_path / "tools" / parts[1].replace("_", "-")
        else:
            # e.g., mcp_core.app -> logs/core/
            service_dir = base_log_path / parts[0].replace("_", "-")
    else:
        # Fallback for runner or unknown names -> logs/misc/
        service_dir = base_log_path / "misc"

    service_dir.mkdir(parents=True, exist_ok=True)
    return service_dir


def configure_logging(config: "AppConfig") -> None:
    """Configures the root logger and standard handlers based on AppConfig."""
    global _is_logging_configured, _configured_formatter

    if _is_logging_configured:
        # print("INFO: Logging already configured.") # Use logger after first setup
        return  # Avoid reconfiguring

    log_config = config.logging
    root_logger = logging.getLogger()  # Get the root logger
    log_level_int = logging.getLevelName(config.get_effective_log_level())

    # Set root logger level
    root_logger.setLevel(log_level_int)

    # Determine formatter
    if log_config.format == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    _configured_formatter = formatter

    # Clear existing handlers from root logger
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    # --- Add File Handler ---
    # Use service-specific log files now
    # Note: This configures the ROOT logger to log EVERYTHING to a central file.
    # If you want separate files per component, you'd need to configure handlers
    # on the specific loggers (e.g., logging.getLogger('mcp_core')).
    # Let's keep it simple for now and log everything to one rotating file.
    log_file_dir = config.logs_path / "application"  # A general subdir
    log_file_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_file_dir / log_config.file_name_template.format(
        service="mcp_app", date=datetime.now().strftime("%Y%m%d")
    )

    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=log_config.max_size_mb * 1024 * 1024,
            backupCount=log_config.backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        print(f"INFO: Logging to file: {log_file}")
    except Exception as e:
        print(
            f"ERROR: Failed to set up file logging to {log_file}: {e}", file=sys.stderr
        )

    # --- Add stdout handler if enabled ---
    if log_config.enable_stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        # Prevent duplicate logging if root also logs to stdout
        stdout_handler.addFilter(lambda record: record.name != "mcp_runner_bootstrap")
        root_logger.addHandler(stdout_handler)
        print("INFO: Logging to stdout enabled.")
    else:
        print("INFO: Logging to stdout disabled.")

    print(f"INFO: Root logger level set to {log_config.level}")
    _is_logging_configured = True


# --- Decorator ---
def log_execution_time(logger_instance: StructuredLogger):
    # (Keep decorator as previously defined)
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
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
# Use a placeholder name initially, it gets configured properly in setup
logger = StructuredLogger("mcp_core")
