"""Error definitions for MCP Proxy."""

from typing import Dict, Optional


class ProxyError(Exception):
    """Base error for MCP Proxy system."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class TransportError(ProxyError):
    """Transport-related errors."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(f"Transport error: {message}", details)


class ConnectionError(ProxyError):
    """Connection-related errors."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(f"Connection error: {message}", details)


class MessageError(ProxyError):
    """Message-related errors."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(f"Message error: {message}", details)


class ConfigError(ProxyError):
    """Configuration-related errors."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(f"Configuration error: {message}", details)
