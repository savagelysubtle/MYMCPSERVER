class MCPError(Exception):
    """Base error for MCP system."""

    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        """Initialize base MCP error.

        Args:
            code: Error code identifier
            message: Human-readable error message
            details: Additional error details dictionary
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ConfigurationError(MCPError):
    """Configuration-related errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        """Initialize configuration error.

        Args:
            message: Human-readable error message
            details: Additional error details dictionary
        """
        super().__init__("CONFIG_ERROR", message, details)


class TransportError(MCPError):
    """Transport layer errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        """Initialize transport error.

        Args:
            message: Human-readable error message
            details: Additional error details dictionary
        """
        super().__init__("TRANSPORT_ERROR", message, details)


class ToolError(MCPError):
    """Tool-related errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        """Initialize tool error.

        Args:
            message: Human-readable error message
            details: Additional error details dictionary
        """
        super().__init__("TOOL_ERROR", message, details)


class AdapterError(MCPError):
    """Adapter-related errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        """Initialize adapter error.

        Args:
            message: Human-readable error message
            details: Additional error details dictionary
        """
        super().__init__("ADAPTER_ERROR", message, details)


class CircuitBreakerError(AdapterError):
    """Circuit breaker related errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        """Initialize circuit breaker error.

        Args:
            message: Human-readable error message
            details: Additional error details dictionary
        """
        super().__init__(message, details)
        self.code = "CIRCUIT_BREAKER_ERROR"


class ValidationError(MCPError):
    """Validation-related errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        """Initialize validation error.

        Args:
            message: Human-readable error message
            details: Additional error details dictionary
        """
        super().__init__("VALIDATION_ERROR", message, details)


class AuthenticationError(MCPError):
    """Authentication-related errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        """Initialize authentication error.

        Args:
            message: Human-readable error message
            details: Additional error details dictionary
        """
        super().__init__("AUTH_ERROR", message, details)
