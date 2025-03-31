"""WebSocket transport for MCP Proxy."""

import asyncio
import uuid
from typing import Any

from .base_transport import BaseTransport


class WebSocketConnection:
    """WebSocket connection wrapper."""

    def __init__(self, client_id: str) -> None:
        """Initialize WebSocket connection.

        Args:
            client_id: Client ID
        """
        self.client_id = client_id
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.connected = True


class WebSocketTransport(BaseTransport):
    """WebSocket transport implementation."""

    def __init__(self) -> None:
        """Initialize WebSocket transport."""
        self.connections: dict[str, WebSocketConnection] = {}

    async def initialize(self) -> None:
        """Initialize the transport."""
        # Nothing to do for initialization
        pass

    async def shutdown(self) -> None:
        """Shutdown the transport."""
        # Clear connections
        self.connections.clear()

    async def register_client(self, websocket: Any) -> str:
        """Register a new WebSocket client.

        Args:
            websocket: WebSocket connection

        Returns:
            str: Client ID
        """
        client_id = str(uuid.uuid4())
        connection = WebSocketConnection(client_id)
        self.connections[client_id] = connection

        # Start message handler task
        asyncio.create_task(self._handle_websocket(websocket, client_id))

        return client_id

    async def _handle_websocket(self, websocket: Any, client_id: str) -> None:
        """Handle WebSocket connection.

        Args:
            websocket: WebSocket connection
            client_id: Client ID
        """
        connection = self.connections[client_id]

        # Message sending task
        async def sender() -> None:
            try:
                while connection.connected:
                    message = await connection.message_queue.get()
                    if message is None:
                        break
                    await websocket.send_json(message)
                    connection.message_queue.task_done()
            except Exception:
                connection.connected = False

        # Start sender task
        sender_task = asyncio.create_task(sender())

        try:
            # Main message receiving loop
            while connection.connected:
                try:
                    data = await websocket.receive_json()
                    # In a real implementation, you would process the message here
                    # For now, we just echo it back
                    await self.send_message(data, client_id)
                except Exception:
                    connection.connected = False
                    break
        finally:
            # Clean up
            connection.connected = False
            if client_id in self.connections:
                del self.connections[client_id]

            # Cancel sender task
            await connection.message_queue.put(None)
            await sender_task

    async def send_message(
        self, message: dict[str, Any], client_id: str | None = None
    ) -> None:
        """Send a message to a client.

        Args:
            message: Message to send
            client_id: Target client ID (None for broadcast)
        """
        if client_id is not None:
            # Send to specific client
            if client_id in self.connections and self.connections[client_id].connected:
                await self.connections[client_id].message_queue.put(message)
        else:
            # Broadcast to all clients
            for connection in self.connections.values():
                if connection.connected:
                    await connection.message_queue.put(message)

    async def receive_message(
        self, client_id: str, timeout: float | None = None
    ) -> dict[str, Any] | None:
        """Receive a message from a client.

        Args:
            client_id: Client ID
            timeout: Receive timeout in seconds

        Returns:
            Optional[Dict[str, Any]]: Received message or None if timeout
        """
        if client_id not in self.connections:
            return None

        connection = self.connections[client_id]

        try:
            if timeout is not None:
                return await asyncio.wait_for(connection.message_queue.get(), timeout)
            else:
                return await connection.message_queue.get()
        except TimeoutError:
            return None
