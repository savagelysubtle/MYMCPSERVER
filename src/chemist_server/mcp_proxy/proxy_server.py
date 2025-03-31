"""MCP Proxy server implementation."""

import asyncio
import logging
import os
import sys
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from .config.config import get_proxy_config
from .errors import ProxyError
from .health import check_health
from .router import MessageRouter
from .transports import StdioHandler, TransportManager

# Configure logging
logger = logging.getLogger(__name__)


class ProxyServer:
    """MCP Proxy server."""

    def __init__(self, app: FastAPI) -> None:
        """Initialize the proxy server.

        Args:
            app: FastAPI application
        """
        self.app = app
        self.config = get_proxy_config()
        self.transport_manager = TransportManager()
        self.active_connections: set[WebSocket] = set()
        self.message_router = MessageRouter()
        self.core_process = None
        self.core_connection_id = None

        # Register routes
        self._register_routes()

    def _register_routes(self) -> None:
        """Register API routes."""

        # WebSocket endpoint
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket) -> None:
            await self._handle_websocket(websocket)

        # Health check endpoint
        @self.app.get("/health")
        async def health_check() -> dict[str, Any]:
            health_status = await check_health()
            if not health_status.get("healthy", False):
                raise HTTPException(status_code=503, detail=health_status)
            return health_status

        # Tool execution endpoint
        @self.app.post("/execute/{tool_name}")
        async def execute_tool(
            tool_name: str, request: dict[str, Any]
        ) -> dict[str, Any]:
            try:
                return await self._execute_tool(tool_name, request)
            except ProxyError as e:
                raise HTTPException(status_code=400, detail=str(e)) from e
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e

    async def _handle_websocket(self, websocket: WebSocket) -> None:
        """Handle WebSocket connection.

        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections.add(websocket)

        try:
            while True:
                data = await websocket.receive_json()

                # Process the message
                response = await self._process_message(data)

                # Send response
                await websocket.send_json(response)
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
        except Exception as e:
            # Send error response
            try:
                await websocket.send_json(
                    {"success": False, "error": {"message": str(e)}}
                )
            except Exception as send_error:
                logger.error("Failed to send error response", exc_info=send_error)

            # Remove connection
            self.active_connections.remove(websocket)

    async def _process_message(self, message: dict) -> dict:
        """Process incoming message.

        Args:
            message: Message data

        Returns:
            Dict: Response data
        """
        # Validate message structure
        if "action" not in message:
            raise ProxyError("Missing 'action' field in message")

        action = message.get("action")

        if action == "execute_tool":
            # Execute tool
            tool_name = message.get("tool_name")
            if not tool_name:
                raise ProxyError("Missing 'tool_name' field for execute_tool action")

            parameters = message.get("parameters", {})
            return await self._execute_tool(tool_name, parameters)
        elif action == "health_check":
            # Health check
            return await check_health()
        else:
            # Unknown action
            raise ProxyError(f"Unknown action: {action}")

    async def _execute_tool(self, tool_name: str, parameters: dict) -> dict:
        """Execute a tool.

        Args:
            tool_name: Name of the tool
            parameters: Tool parameters

        Returns:
            Dict: Tool execution result
        """
        if not self.core_connection_id:
            raise ProxyError("Core layer not available")

        # Create a message for the Core layer
        message = {
            "action": "execute_tool",
            "tool_name": tool_name,
            "parameters": parameters,
            "request_id": str(asyncio.get_event_loop().time()),
        }

        # Send the message to the Core layer via the router
        await self.message_router.route_message(message, source_id=None)

        # In a real implementation, we would wait for a response from the Core layer
        # For now, return a placeholder
        return {
            "success": True,
            "data": {
                "tool_name": tool_name,
                "parameters": parameters,
                "result": "Tool execution request sent to Core layer",
            },
        }

    async def _setup_core_process(self) -> None:
        """Set up the Core process."""
        # Get the path to the run_server.py script
        run_server_path = os.path.join(os.path.dirname(__file__), "..", "run_server.py")

        # Set up environment variables
        env = os.environ.copy()
        env["MCP_COMPONENTS"] = "core"
        env["MCP_TRANSPORT"] = "stdio"

        # Create a StdioHandler for the Core process
        stdio_handler = StdioHandler(
            command=sys.executable,
            args=[run_server_path, "--mode", "core", "--transport", "stdio"],
            env=env,
        )

        # Set the message router
        stdio_handler.set_message_router(self.message_router)

        # Initialize the handler (spawns the process)
        await stdio_handler.initialize()

        # Create a connection in the router for the Core layer
        self.core_connection_id = await self.message_router.create_connection()

        # Subscribe to the broadcast topic
        await self.message_router.subscribe(self.core_connection_id, "broadcast")

        # Store the handler
        self.core_process = stdio_handler

        logger.info("Core process initialized")

    async def start(self) -> None:
        """Start the proxy server."""
        # Initialize message router
        await self.message_router.start()

        # Set up Core process
        await self._setup_core_process()

        # Initialize transport manager
        await self.transport_manager.initialize()

        logger.info("Proxy server started")

    async def stop(self) -> None:
        """Stop the proxy server."""
        # Close all WebSocket connections
        for connection in self.active_connections:
            try:
                await connection.close()
            except Exception as e:
                logger.warning("Failed to close WebSocket connection", exc_info=e)

        # Shutdown transport manager
        await self.transport_manager.shutdown()

        # Shutdown Core process
        if self.core_process:
            await self.core_process.shutdown()

        # Shutdown message router
        await self.message_router.stop()

        logger.info("Proxy server stopped")
