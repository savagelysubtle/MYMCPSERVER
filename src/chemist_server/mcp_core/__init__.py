"""MCP Core Layer."""

from .config.config import CoreConfig
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
    "AdapterError",
    "AuthenticationError",
    "ConfigurationError",
    "CoreConfig",
    "CoreHealth",
    "HealthCheck",
    "HealthStatus",
    "MCPError",
    "StructuredLogger",
    "SystemHealth",
    "ToolError",
    "ToolServerHealth",
    "TransportError",
    "ValidationError",
    "log_execution_time",
    "logger",
]
