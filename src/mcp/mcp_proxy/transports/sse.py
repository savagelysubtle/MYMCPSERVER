"""Server-Sent Events (SSE) transport for MCP Proxy."""

import asyncio
import json
import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse

from .base_transport import BaseTransport


class SSEConnection:
    """SSE connection wrapper."""

    def __init__(self, client_id: str):
        """Initialize SSE connection.

        Args:
            client_id: Client ID
        """
        self.client_id = client_id
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.connected = True


class SSETransport(BaseTransport):
    """SSE transport implementation."""

    def __init__(self):
        """Initialize SSE transport."""
        self.connections: Dict[str, SSEConnection] = {}
        self.app: Optional[FastAPI] = None

    async def initialize(self) -> None:
        """Initialize the transport."""
        # Nothing to do for initialization
        pass

    async def shutdown(self) -> None:
        """Shutdown the transport."""
        # Clear connections
        self.connections.clear()

    def register_with_app(self, app: FastAPI) -> None:
        """Register routes with FastAPI app.

        Args:
            app: FastAPI application
        """
        self.app = app

        @app.get("/sse")
        async def sse_endpoint(request: Request):
            client_id = str(uuid.uuid4())
            return await self._create_sse_response(request, client_id)

        @app.post("/sse/{client_id}/send")
        async def send_to_sse(client_id: str, message: Dict[str, Any]):
            await self.send_message(message, client_id)
            return {"success": True}

    async def _create_sse_response(
        self, request: Request, client_id: str
    ) -> EventSourceResponse:
        """Create SSE response.

        Args:
            request: HTTP request
            client_id: Client ID

        Returns:
            EventSourceResponse: SSE response
        """
        connection = SSEConnection(client_id)
        self.connections[client_id] = connection

        async def event_generator():
            try:
                # Send initial connection message
                yield {
                    "event": "connected",
                    "data": json.dumps({"client_id": client_id}),
                }

                # Process messages
                while connection.connected:
                    if await request.is_disconnected():
                        break

                    try:
                        message = await asyncio.wait_for(
                            connection.message_queue.get(), timeout=1.0
                        )

                        if message is None:
                            break

                        yield {
                            "event": message.get("event", "message"),
                            "data": json.dumps(message),
                        }

                        connection.message_queue.task_done()
                    except asyncio.TimeoutError:
                        # Just check for disconnection again
                        continue
            finally:
                # Clean up
                connection.connected = False
                if client_id in self.connections:
                    del self.connections[client_id]

        return EventSourceResponse(event_generator())

    async def send_message(
        self, message: Dict[str, Any], client_id: Optional[str] = None
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
        self, client_id: str, timeout: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Receive a message from a client.

        Note: SSE is a one-way transport, so this is not supported.

        Args:
            client_id: Client ID
            timeout: Receive timeout in seconds

        Returns:
            Optional[Dict[str, Any]]: Received message or None if timeout
        """
        # SSE is a one-way transport (server to client)
        # This method is not supported
        return None
