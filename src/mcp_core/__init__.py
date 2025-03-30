"""MCP Core Layer."""

from .config.config import CoreConfig, get_core_config
from .errors import (
    AdapterError,
    AuthenticationError,
    ConfigurationError,
    MCPError,
    ToolError,
    TransportError,
    ValidationError,
)
from .health import (
    CoreHealth,
    HealthCheck,
    HealthStatus,
    SystemHealth,
    ToolServerHealth,
)
from .logger.logger import StructuredLogger, log_execution_time

__version__ = "1.0.0"

# Create default logger instance
logger = StructuredLogger("mcp_core")

__all__ = [
    "CoreConfig",
    "get_core_config",
    "MCPError",
    "ConfigurationError",
    "TransportError",
    "ToolError",
    "AdapterError",
    "ValidationError",
    "AuthenticationError",
    "StructuredLogger",
    "log_execution_time",
    "HealthStatus",
    "HealthCheck",
    "SystemHealth",
    "CoreHealth",
    "ToolServerHealth",
    "logger",
]
