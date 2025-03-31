"""Error definitions for MCP Proxy."""

from typing import Any


class ProxyError(Exception):
    """Base error for MCP Proxy system."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)


class TransportError(ProxyError):
    """Transport-related errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(f"Transport error: {message}", details)


class ProxyConnectionError(ProxyError):
    """Connection-related errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(f"Connection error: {message}", details)


class MessageError(ProxyError):
    """Message-related errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(f"Message error: {message}", details)


class ConfigError(ProxyError):
    """Configuration-related errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(f"Configuration error: {message}", details)
