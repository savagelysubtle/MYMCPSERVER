"""Request routing for MCP Core.

This module provides the Router component that routes incoming requests
to the appropriate tool adapters registered in the adapter registry.
"""

from typing import Any

from .errors import AdapterError, CircuitBreakerError
from .logger import logger
from .registry import ToolRegistry


class Router:
    """Routes incoming requests to appropriate adapters.

    The Router uses the ToolRegistry to find the appropriate adapter for
    a given tool request, and applies circuit breaking for fault tolerance.
    """

    def __init__(self, registry: ToolRegistry):
        """Initialize the router.

        Args:
            registry: Tool registry containing registered adapters
        """
        self.registry = registry
        logger.info("Router initialized")

    async def route_request(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        context: dict[str, Any] | None = None,
        version: str | None = None,
        use_circuit_breaker: bool = True,
    ) -> dict[str, Any]:
        """Route a request to the appropriate adapter.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            context: Optional execution context
            version: Tool version (uses latest if None)
            use_circuit_breaker: Whether to use circuit breaker

        Returns:
            Dict[str, Any]: Result from the adapter

        Raises:
            AdapterError: If adapter not found or execution fails
            CircuitBreakerError: If circuit breaker is open
        """
        try:
            # Use the registry to execute the tool
            # The registry handles adapter selection, circuit breaking, etc.
            result = await self.registry.execute_tool(
                tool_name=tool_name,
                parameters=parameters,
                context=context,
                version=version,
                use_circuit_breaker=use_circuit_breaker,
            )

            return result
        except (AdapterError, CircuitBreakerError) as e:
            # Log and re-raise errors
            logger.error(
                f"Error routing request to {tool_name}",
                tool=tool_name,
                version=version or "latest",
                error=str(e),
            )
            raise

    async def list_available_tools(self) -> list[dict[str, Any]]:
        """List all available tools and versions.

        Returns:
            List[Dict[str, Any]]: List of tool metadata
        """
        return self.registry.list_tools()

    async def get_tool_metadata(
        self, tool_name: str, version: str | None = None
    ) -> dict[str, Any]:
        """Get metadata for a specific tool.

        Args:
            tool_name: Name of the tool
            version: Tool version (uses latest if None)

        Returns:
            Dict[str, Any]: Tool metadata

        Raises:
            AdapterError: If tool not found
        """
        metadata = self.registry.get_metadata(tool_name, version)
        return {
            "tool_name": metadata.tool_name,
            "version": metadata.version,
            "adapter_type": metadata.adapter_type,
            "description": metadata.description,
            "created_at": metadata.created_at,
            "updated_at": metadata.updated_at,
            "is_active": metadata.is_active,
            "tags": list(metadata.tags),
            "circuit_breaker_enabled": metadata.circuit_breaker_enabled,
            "health_check_interval": metadata.health_check_interval,
        }

    async def get_tool_health(
        self, tool_name: str, version: str | None = None
    ) -> dict[str, Any]:
        """Get health information for a specific tool.

        Args:
            tool_name: Name of the tool
            version: Tool version (uses latest if None)

        Returns:
            Dict[str, Any]: Health information

        Raises:
            AdapterError: If tool not found
        """
        try:
            adapter = self.registry.get_tool(tool_name, version)
            health = await adapter.health_check()

            # Get circuit breaker state
            circuit_breaker = self.registry.get_circuit_breaker(tool_name, version)
            circuit_state = circuit_breaker.get_state()

            return {
                "tool_name": tool_name,
                "version": version
                or self.registry.latest_versions.get(tool_name, "unknown"),
                "status": health.get("status", "unknown"),
                "circuit_state": circuit_state["state"],
                "failure_count": circuit_state["failure_count"],
                "last_failure_time": circuit_state["last_failure_time"],
                "details": health,
            }
        except Exception as e:
            return {
                "tool_name": tool_name,
                "version": version or "unknown",
                "status": "error",
                "error": str(e),
            }
