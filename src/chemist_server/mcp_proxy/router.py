"""Message routing for MCP Proxy.

This module implements the MessageRouter which is responsible for routing messages
between different transports, such as between the stdio handler and SSE/WebSocket clients.
"""

import asyncio
import logging
import uuid

# Configure logging
logger = logging.getLogger(__name__)


class MessageRouter:
    """Routes messages between transports and clients.

    This class manages connections and subscriptions, routing messages between
    the proxy server components and the core layer.
    """

    def __init__(self) -> None:
        """Initialize the router."""
        self.connections: dict[str, asyncio.Queue] = {}
        self.subscriptions: dict[str, set[str]] = {}
        self.running = False
        self.router_task = None

    async def start(self) -> None:
        """Start the message router."""
        self.running = True
        logger.info("Message router started")

    async def stop(self) -> None:
        """Stop the message router."""
        self.running = False

        # Cancel router task if running
        if self.router_task:
            self.router_task.cancel()

        # Clear all queues
        for _, queue in self.connections.items():
            # Add a sentinel to unblock any consumers
            await queue.put(None)

        logger.info("Message router stopped")

    async def create_connection(self) -> str:
        """Create a new connection and return its ID.

        Returns:
            str: The new connection ID
        """
        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = asyncio.Queue()
        logger.debug(f"Created new connection: {connection_id}")
        return connection_id

    async def close_connection(self, connection_id: str) -> None:
        """Close and remove a connection.

        Args:
            connection_id: The connection ID to close
        """
        if connection_id in self.connections:
            # Remove from all subscriptions
            for _, subscribers in self.subscriptions.items():
                subscribers.discard(connection_id)

            # Remove the connection
            queue = self.connections.pop(connection_id)
            await queue.put(None)  # Add sentinel to unblock consumers

            logger.debug(f"Closed connection: {connection_id}")

    async def subscribe(self, connection_id: str, topic: str) -> None:
        """Subscribe a connection to a topic.

        Args:
            connection_id: The connection ID
            topic: The topic to subscribe to
        """
        if connection_id not in self.connections:
            raise ValueError(f"Connection not found: {connection_id}")

        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()

        self.subscriptions[topic].add(connection_id)
        logger.debug(f"Connection {connection_id} subscribed to topic: {topic}")

    async def unsubscribe(self, connection_id: str, topic: str) -> None:
        """Unsubscribe a connection from a topic.

        Args:
            connection_id: The connection ID
            topic: The topic to unsubscribe from
        """
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(connection_id)
            logger.debug(f"Connection {connection_id} unsubscribed from topic: {topic}")

    async def route_message(self, message: dict, source_id: str | None = None) -> None:
        """Route a message to subscribed connections.

        Args:
            message: The message to route
            source_id: Optional source connection ID to exclude from routing
        """
        topic = message.get("topic", "broadcast")
        subscribers = self.subscriptions.get(topic, set())

        # Also include broadcast subscribers if this is not a broadcast topic
        if topic != "broadcast":
            subscribers = subscribers.union(self.subscriptions.get("broadcast", set()))

        logger.debug(
            f"Routing message to {len(subscribers)} subscribers for topic: {topic}"
        )

        for connection_id in subscribers:
            # Skip the source connection to avoid echo
            if connection_id == source_id:
                continue

            if connection_id in self.connections:
                await self.connections[connection_id].put(message)

    async def get_message(
        self, connection_id: str, timeout: float | None = None
    ) -> dict | None:
        """Get a message for a connection.

        Args:
            connection_id: The connection ID
            timeout: Optional timeout in seconds

        Returns:
            Optional[Dict]: The message or None if timeout or connection closed
        """
        if connection_id not in self.connections:
            raise ValueError(f"Connection not found: {connection_id}")

        queue = self.connections[connection_id]

        try:
            if timeout:
                message = await asyncio.wait_for(queue.get(), timeout)
            else:
                message = await queue.get()

            # Handle sentinel value
            if message is None:
                return None

            return message
        except TimeoutError:
            return None
