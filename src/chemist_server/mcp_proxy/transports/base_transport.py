"""Base transport interface for MCP Proxy."""

from abc import ABC, abstractmethod
from typing import Any


class BaseTransport(ABC):
    """Base class for transport implementations."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the transport."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the transport."""
        pass

    @abstractmethod
    async def send_message(
        self, message: dict[str, Any], client_id: str | None = None
    ) -> None:
        """Send a message to a client.

        Args:
            message: Message to send
            client_id: Target client ID (None for broadcast)
        """
        pass

    @abstractmethod
    async def receive_message(
        self, client_id: str, timeout: float | None = None
    ) -> dict[str, Any] | None:
        """Receive a message from a client.

        Args:
            client_id: Client ID
            timeout: Receive timeout in seconds

        Returns:
            dict[str, Any] | None: Received message or None if timeout
        """
        pass
