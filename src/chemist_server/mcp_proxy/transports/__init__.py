"""Transport mechanisms for MCP Proxy."""

from typing import Dict, List, Type

from .base_transport import BaseTransport
from .sse import SSETransport
from .stdio import StdioHandler
from .websocket import WebSocketTransport


class TransportManager:
    """Manages different transport mechanisms."""

    def __init__(self):
        """Initialize transport manager."""
        self.transports: dict[str, BaseTransport] = {}

        # Register default transports
        self.register_transport("websocket", WebSocketTransport())
        self.register_transport("sse", SSETransport())
        self.register_transport("stdio", StdioHandler())

    def register_transport(self, name: str, transport: BaseTransport) -> None:
        """Register a transport.

        Args:
            name: Transport name
            transport: Transport instance
        """
        self.transports[name] = transport

    def get_transport(self, name: str) -> BaseTransport:
        """Get a transport by name.

        Args:
            name: Transport name

        Returns:
            BaseTransport: Transport instance

        Raises:
            KeyError: If transport not found
        """
        if name not in self.transports:
            raise KeyError(f"Transport not found: {name}")

        return self.transports[name]

    def list_transports(self) -> list[str]:
        """List available transports.

        Returns:
            List[str]: List of transport names
        """
        return list(self.transports.keys())

    async def initialize(self) -> None:
        """Initialize all transports."""
        for name, transport in self.transports.items():
            await transport.initialize()

    async def shutdown(self) -> None:
        """Shutdown all transports."""
        for name, transport in self.transports.items():
            await transport.shutdown()


__all__ = [
    "BaseTransport",
    "SSETransport",
    "StdioHandler",
    "TransportManager",
    "WebSocketTransport",
]
