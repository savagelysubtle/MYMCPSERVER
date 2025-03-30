from typing import Dict, Optional


class MCPError(Exception):
    """Base error for MCP system."""

    def __init__(self, code: str, message: str, details: Optional[Dict] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ConfigurationError(MCPError):
    """Configuration-related errors."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__("CONFIG_ERROR", message, details)


class TransportError(MCPError):
    """Transport layer errors."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__("TRANSPORT_ERROR", message, details)


class ToolError(MCPError):
    """Tool-related errors."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__("TOOL_ERROR", message, details)


class AdapterError(MCPError):
    """Adapter-related errors."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__("ADAPTER_ERROR", message, details)


class CircuitBreakerError(AdapterError):
    """Circuit breaker related errors."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, details)
        self.code = "CIRCUIT_BREAKER_ERROR"


class ValidationError(MCPError):
    """Validation-related errors."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__("VALIDATION_ERROR", message, details)


class AuthenticationError(MCPError):
    """Authentication-related errors."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__("AUTH_ERROR", message, details)
