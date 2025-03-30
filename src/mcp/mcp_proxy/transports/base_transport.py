"""Base transport interface for MCP Proxy."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


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
        self, message: Dict[str, Any], client_id: Optional[str] = None
    ) -> None:
        """Send a message to a client.

        Args:
            message: Message to send
            client_id: Target client ID (None for broadcast)
        """
        pass

    @abstractmethod
    async def receive_message(
        self, client_id: str, timeout: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Receive a message from a client.

        Args:
            client_id: Client ID
            timeout: Receive timeout in seconds

        Returns:
            Optional[Dict[str, Any]]: Received message or None if timeout
        """
        pass
