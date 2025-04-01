"""Tool registry for MCP Core.

This module provides the central registry for managing tool registrations and versions.
"""

import time
from dataclasses import dataclass, field
from typing import Any

from .adapters.base_adapter import BaseAdapter
from .adapters.circuit_breaker import CircuitBreaker
from .errors import AdapterError, CircuitBreakerError
from .logger import logger


@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""

    tool_name: str
    adapter_type: str  # Type of adapter (e.g., python, typescript)
    version: str
    description: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    is_active: bool = True
    tags: set[str] = field(default_factory=set)
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5
    recovery_timeout: float = 30.0
    health_check_interval: float = 60.0
    metadata: dict[str, Any] = field(default_factory=dict)


class ToolRegistry:
    """Registry for MCP tools.

    This registry manages tool registrations, provides version control,
    and handles adapter selection.
    """

    def __init__(self) -> None:
        """Initialize the tool registry."""
        self.tools: dict[
            str, dict[str, BaseAdapter]
        ] = {}  # tool_name -> version -> adapter
        self.metadata: dict[
            str, dict[str, ToolMetadata]
        ] = {}  # tool_name -> version -> metadata
        self.circuit_breakers: dict[
            str, CircuitBreaker
        ] = {}  # tool_name:version -> circuit breaker
        self.latest_versions: dict[str, str] = {}  # tool_name -> latest version

    def register_tool(
        self,
        tool_name: str,
        adapter: BaseAdapter,
        version: str,
        metadata: dict[str, Any] | None = None,
        make_latest: bool = True,
        **kwargs: Any,
    ) -> None:
        """Register a tool with the registry.

        Args:
            tool_name: Name of the tool
            adapter: Adapter instance for the tool
            version: Tool version
            metadata: Additional metadata for the tool
            make_latest: Whether to make this the latest version
            **kwargs: Additional metadata fields

        Raises:
            AdapterError: If the tool already exists with the same version
        """
        # Check if tool exists with this version
        if tool_name in self.tools and version in self.tools[tool_name]:
            raise AdapterError(f"Tool {tool_name} v{version} already registered")

        # Initialize tool entry if needed
        if tool_name not in self.tools:
            self.tools[tool_name] = {}
            self.metadata[tool_name] = {}

        # Register the adapter
        self.tools[tool_name][version] = adapter

        # Create circuit breaker
        circuit_name = f"{tool_name}:{version}"
        failure_threshold = kwargs.get("circuit_breaker_threshold", 5)
        recovery_timeout = kwargs.get("recovery_timeout", 30.0)

        self.circuit_breakers[circuit_name] = CircuitBreaker(
            name=circuit_name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )

        # Store metadata
        tool_metadata = ToolMetadata(
            tool_name=tool_name,
            adapter_type=adapter.__class__.__name__,
            version=version,
            description=kwargs.get("description", ""),
            tags=set(kwargs.get("tags", [])),
            circuit_breaker_enabled=kwargs.get("circuit_breaker_enabled", True),
            circuit_breaker_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            health_check_interval=kwargs.get("health_check_interval", 60.0),
            metadata=metadata or {},
        )

        self.metadata[tool_name][version] = tool_metadata

        # Update latest version if requested
        if make_latest or tool_name not in self.latest_versions:
            self.latest_versions[tool_name] = version

        logger.info(
            f"Registered tool {tool_name} v{version}",
            tool=tool_name,
            version=version,
            adapter=adapter.__class__.__name__,
        )

    def get_tool(self, tool_name: str, version: str | None = None) -> BaseAdapter:
        """Get a tool adapter by name and version.

        Args:
            tool_name: Name of the tool
            version: Tool version (uses latest if None)

        Returns:
            BaseAdapter: Tool adapter

        Raises:
            AdapterError: If tool not found
        """
        if tool_name not in self.tools:
            raise AdapterError(f"Tool {tool_name} not found")

        # Use latest version if not specified
        if version is None:
            version = self.latest_versions.get(tool_name)
            if version is None:
                raise AdapterError(f"No versions found for tool {tool_name}")

        # Check if version exists
        if version not in self.tools[tool_name]:
            raise AdapterError(f"Version {version} not found for tool {tool_name}")

        return self.tools[tool_name][version]

    def get_metadata(self, tool_name: str, version: str | None = None) -> ToolMetadata:
        """Get metadata for a tool.

        Args:
            tool_name: Name of the tool
            version: Tool version (uses latest if None)

        Returns:
            ToolMetadata: Tool metadata

        Raises:
            AdapterError: If tool not found
        """
        if tool_name not in self.metadata:
            raise AdapterError(f"Tool {tool_name} not found")

        # Use latest version if not specified
        if version is None:
            version = self.latest_versions.get(tool_name)
            if version is None:
                raise AdapterError(f"No versions found for tool {tool_name}")

        # Check if version exists
        if version not in self.metadata[tool_name]:
            raise AdapterError(f"Version {version} not found for tool {tool_name}")

        return self.metadata[tool_name][version]

    def list_tools(self) -> list[dict[str, Any]]:
        """List all registered tools.

        Returns:
            List[Dict[str, Any]]: List of tool metadata
        """
        result = []
        for tool_name, versions in self.metadata.items():
            for version, metadata in versions.items():
                is_latest = self.latest_versions.get(tool_name) == version
                result.append(
                    {
                        "tool_name": tool_name,
                        "version": version,
                        "is_latest": is_latest,
                        "description": metadata.description,
                        "adapter_type": metadata.adapter_type,
                    }
                )

        return result

    def list_versions(self, tool_name: str) -> list[str]:
        """List all versions for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            List[str]: List of versions

        Raises:
            AdapterError: If tool not found
        """
        if tool_name not in self.tools:
            raise AdapterError(f"Tool {tool_name} not found")

        return list(self.tools[tool_name].keys())

    def get_circuit_breaker(
        self, tool_name: str, version: str | None = None
    ) -> CircuitBreaker:
        """Get circuit breaker for a tool.

        Args:
            tool_name: Name of the tool
            version: Tool version (uses latest if None)

        Returns:
            CircuitBreaker: Circuit breaker instance

        Raises:
            AdapterError: If tool not found
        """
        # Get the appropriate version
        if version is None:
            version = self.latest_versions.get(tool_name)
            if version is None:
                raise AdapterError(f"No versions found for tool {tool_name}")

        circuit_name = f"{tool_name}:{version}"
        if circuit_name not in self.circuit_breakers:
            raise AdapterError(f"Circuit breaker not found for {tool_name} v{version}")

        return self.circuit_breakers[circuit_name]

    async def execute_tool(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        context: dict[str, Any] | None = None,
        version: str | None = None,
        use_circuit_breaker: bool = True,
    ) -> dict[str, Any]:
        """Execute a tool with circuit breaker protection.

        Args:
            tool_name: Name of the tool
            parameters: Tool parameters
            context: Execution context
            version: Tool version (uses latest if None)
            use_circuit_breaker: Whether to use circuit breaker

        Returns:
            Dict[str, Any]: Tool result

        Raises:
            AdapterError: If adapter execution fails
            CircuitBreakerError: If circuit breaker is open
        """
        # Get the appropriate version
        if version is None:
            version = self.latest_versions.get(tool_name)
            if version is None:
                raise AdapterError(f"No versions found for tool {tool_name}")

        # Get tool and metadata
        adapter = self.get_tool(tool_name, version)
        metadata = self.get_metadata(tool_name, version)

        # Check if circuit breaker is enabled
        if use_circuit_breaker and metadata.circuit_breaker_enabled:
            circuit_breaker = self.get_circuit_breaker(tool_name, version)

            # Execute with circuit breaker
            try:
                result = await circuit_breaker.execute(
                    adapter.execute,
                    tool_name,
                    parameters,
                    context,
                )
                return await result
            except CircuitBreakerError:
                # Propagate circuit breaker errors
                raise
            except Exception as e:
                # Wrap other exceptions
                raise AdapterError(f"Error executing tool {tool_name}: {e!s}") from e
        else:
            # Execute directly without circuit breaker
            try:
                result = await adapter.execute(tool_name, parameters, context)
                return result
            except Exception as e:
                raise AdapterError(f"Error executing tool {tool_name}: {e!s}") from e

    async def shutdown(self) -> None:
        """Shutdown all adapters.

        Raises:
            AdapterError: If shutdown fails
        """
        errors = []

        # Shutdown all adapters
        for tool_name, versions in self.tools.items():
            for version, adapter in versions.items():
                try:
                    await adapter.shutdown()
                except Exception as e:
                    errors.append(
                        f"Error shutting down {tool_name} v{version}: {e!s}"
                    )

        if errors:
            raise AdapterError(f"Errors during shutdown: {', '.join(errors)}")

        # Clear registries
        self.tools.clear()
        self.metadata.clear()
        self.circuit_breakers.clear()
        self.latest_versions.clear()
