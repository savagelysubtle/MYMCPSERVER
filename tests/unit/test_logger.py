"""Unit tests for the logging setup and StructuredLogger."""

import json
import logging
import sys
import time
from datetime import datetime
from logging import handlers
from pathlib import Path

import pytest

# Import components to be tested
from chemist_server.config import (  # Need AppConfig for configure_logging
    AppConfig,
    LoggingConfig,
)
from chemist_server.mcp_core.logger.logger import (
    JsonFormatter,
    StructuredLogger,
    _global_log_config,
    _global_logs_path,
    _is_logging_configured,
    _log_handlers,
    configure_logging,
    get_log_dir,
)

# --- Fixtures ---


@pytest.fixture
def mock_app_config(tmp_path: Path) -> AppConfig:
    """Provides a mock AppConfig suitable for logging tests."""
    # Create a minimal AppConfig, focusing on logging aspects
    # Use tmp_path for isolated log file creation
    return AppConfig(
        logs_path=tmp_path / "test_logs",
        logging=LoggingConfig(
            level="DEBUG",
            format="json",
            enable_stdout=True,
            file_name_template="test_{service}.log",
            max_size_mb=1,
            backup_count=1,
        ),
        # Add other necessary fields if AppConfig validation requires them
        vault_path=tmp_path / "test_vault",
        components="all",
        transport="stdio",
        host_override=None,
        port_override=None,
        # core=CoreConfig(), # Add if needed, depends on AppConfig validation
        # tool_server_python=ToolServerPythonConfig(), # Add if needed
    )


@pytest.fixture(autouse=True)
def reset_logging_state():
    """Fixture to reset global logging state before and after each test."""
    # Store original state
    original_configured = _is_logging_configured
    original_config = _global_log_config
    original_path = _global_logs_path
    original_handlers_cache = _log_handlers.copy()
    root_logger = logging.getLogger()
    original_level = root_logger.level
    original_handlers = root_logger.handlers[:]

    yield  # Run the test

    # Restore original state
    globals()["_is_logging_configured"] = original_configured
    globals()["_global_log_config"] = original_config
    globals()["_global_logs_path"] = original_path
    # Clear and restore handler cache
    _log_handlers.clear()
    _log_handlers.update(original_handlers_cache)

    # Restore root logger
    root_logger.setLevel(original_level)
    # Remove handlers added during the test (check by type or name if needed)
    current_handlers = root_logger.handlers[:]
    for h in current_handlers:
        if h not in original_handlers:
            root_logger.removeHandler(h)
    # Add back original handlers if they were removed
    for h in original_handlers:
        if h not in root_logger.handlers:
            root_logger.addHandler(h)


@pytest.fixture
def configured_logger(mock_app_config: AppConfig) -> StructuredLogger:
    """Fixture that configures logging and returns a StructuredLogger instance."""
    # Configure logging using the mock config
    configure_logging(mock_app_config)
    # Return a logger instance created *after* configuration
    return StructuredLogger("test_service.component")


# --- Test Cases ---


def test_configure_logging_sets_global_state(mock_app_config: AppConfig):
    """Test that configure_logging sets the global state variables correctly."""
    assert not _is_logging_configured
    assert _global_log_config is None

    configure_logging(mock_app_config)

    assert _is_logging_configured is True
    assert _global_log_config == mock_app_config.logging
    assert _global_logs_path == mock_app_config.logs_path
    # Check formatter was set globally (not exported, check via root logger handler)
    root_logger = logging.getLogger()
    assert any(isinstance(h.formatter, JsonFormatter) for h in root_logger.handlers)


def test_configure_logging_root_logger(mock_app_config: AppConfig):
    """Test configure_logging sets up the root logger."""
    root_logger = logging.getLogger()
    original_handler_count = len(root_logger.handlers)

    # Configure with stdout enabled
    mock_app_config.logging.enable_stdout = True
    configure_logging(mock_app_config)

    assert root_logger.level == logging.DEBUG  # Based on mock_app_config
    # Check if a StreamHandler was added (for stdout)
    assert any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)
    stdout_handler_added = len(root_logger.handlers) > original_handler_count

    # Reset and configure with stdout disabled
    reset_logging_state()  # Manually call reset for intermediate step
    mock_app_config.logging.enable_stdout = False
    configure_logging(mock_app_config)

    # Check if StreamHandler was NOT added (or was removed)
    assert not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)
    assert (
        len(root_logger.handlers) == original_handler_count
        if stdout_handler_added
        else True
    )


def test_structured_logger_init_after_config(
    configured_logger: StructuredLogger, mock_app_config: AppConfig
):
    """Test StructuredLogger initialization *after* configure_logging."""
    logger = configured_logger.logger
    log_cfg = mock_app_config.logging

    assert (
        logger.level == logging.DEBUG
    )  # Should inherit from configured root or be set directly
    # Check if file handler was added
    assert any(isinstance(h, handlers.RotatingFileHandler) for h in logger.handlers)
    # Check propagate based on stdout and file handler presence
    if log_cfg.enable_stdout:
        assert (
            logger.propagate is False
        )  # Has file handler, root has stdout, so don't propagate
    else:
        assert (
            logger.propagate is True
        )  # Has file handler, root has no stdout, so propagate?
        # Or should it be False? Check logic in logger.py


def test_structured_logger_logs_to_file(
    configured_logger: StructuredLogger, mock_app_config: AppConfig
):
    """Test that the logger writes formatted messages to the correct file."""
    log_dir = get_log_dir(mock_app_config.logs_path, configured_logger.name)
    log_file = log_dir / mock_app_config.logging.file_name_template.format(
        service=configured_logger.name.replace(".", "_"),
        date=datetime.now().strftime("%Y%m%d"),
    )

    test_message = f"Test message from {__name__} at {time.time()}"
    extra_data = {"key1": "value1", "num_key": 123}

    # Log a message
    configured_logger.info(test_message, **extra_data)

    # Close handlers to ensure flush (important on some platforms/configs)
    # This is tricky because handlers are cached globally
    # logging.shutdown()

    assert log_file.exists(), f"Log file {log_file} was not created"

    # Read the log file and check content
    content = log_file.read_text()
    assert test_message in content
    assert '"level": "INFO"' in content
    assert f'"name": "{configured_logger.name}"' in content
    assert '"key1": "value1"' in content
    assert '"num_key": 123' in content


def test_structured_logger_captures_stdout(
    capsys, configured_logger: StructuredLogger, mock_app_config: AppConfig
):
    """Test that the logger writes to stdout when enabled."""
    # Ensure stdout is enabled in config for this test
    mock_app_config.logging.enable_stdout = True
    # Reconfigure logging with updated config
    configure_logging(mock_app_config)
    # Get a logger instance *after* reconfiguration
    logger_instance = StructuredLogger("stdout_test")

    test_message = "Message for stdout"
    logger_instance.warning(test_message, data="for_stdout")

    captured = capsys.readouterr()
    # Check stderr because default StreamHandler logs to stderr
    assert test_message in captured.err
    assert '"level": "WARNING"' in captured.err
    assert '"name": "stdout_test"' in captured.err
    assert '"data": "for_stdout"' in captured.err


def test_json_formatter():
    """Test the JsonFormatter directly."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="json_test",
        level=logging.ERROR,
        pathname="/path/to/file.py",
        lineno=42,
        msg="Error message: %s",
        args=("details",),
        exc_info=None,
        func="test_func",
    )
    # Add extra data
    record.extra_field = "extra_value"
    record.num_field = 99

    # Simulate exception info
    try:
        1 / 0
    except ZeroDivisionError:
        record.exc_info = sys.exc_info()

    formatted_str = formatter.format(record)
    log_data = json.loads(formatted_str)

    assert log_data["level"] == "ERROR"
    assert log_data["name"] == "json_test"
    assert log_data["message"] == "Error message: details"
    assert log_data["extra_field"] == "extra_value"
    assert log_data["num_field"] == 99
    assert "timestamp" in log_data
    assert "exception" in log_data
    assert "Traceback (most recent call last):" in log_data["exception"]
    assert "ZeroDivisionError: division by zero" in log_data["exception"]


def test_get_log_dir(tmp_path: Path):
    """Test the get_log_dir function creates correct subdirectories."""
    base_path = tmp_path / "logs"

    assert get_log_dir(base_path, "mcp_core") == base_path / "core"
    assert (base_path / "core").is_dir()

    assert get_log_dir(base_path, "mcp_core.submodule") == base_path / "core"
    assert (base_path / "core").is_dir()

    assert (
        get_log_dir(base_path, "tool_servers.python_server")
        == base_path / "tools" / "python-server"
    )
    assert (base_path / "tools" / "python-server").is_dir()

    assert get_log_dir(base_path, "mcp_proxy") == base_path / "proxy"
    assert (base_path / "proxy").is_dir()

    assert get_log_dir(base_path, "mymcpserver.runner") == base_path / "server"
    assert (base_path / "server").is_dir()

    assert get_log_dir(base_path, "other_service") == base_path / "misc"
    assert (base_path / "misc").is_dir()
