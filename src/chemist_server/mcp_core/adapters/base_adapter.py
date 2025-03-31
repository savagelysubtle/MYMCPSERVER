"""Base adapter interface for MCP tools."""

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """Base class for tool adapters."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the adapter.

        This method should prepare the adapter for usage, such as
        loading necessary resources or establishing connections.

        Raises:
            AdapterError: If initialization fails
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the adapter.

        This method should clean up resources used by the adapter,
        such as closing connections or stopping background tasks.

        Raises:
            AdapterError: If shutdown fails
        """
        pass

    @abstractmethod
    async def execute(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a tool with the adapter.

        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters to pass to the tool
            context: Optional execution context

        Returns:
            Dict[str, Any]: Result of tool execution

        Raises:
            AdapterError: If execution fails
        """
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check the health of the adapter.

        Returns:
            Dict[str, Any]: Health status information

        Raises:
            AdapterError: If health check fails
        """
        pass
