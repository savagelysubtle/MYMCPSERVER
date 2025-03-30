"""Python Tool Adapter for communicating with the Python Tool Server."""

from typing import Any

import httpx

from ..errors import AdapterError
from ..logger import logger
from .base_adapter import BaseAdapter


class PythonToolAdapter(BaseAdapter):
    """Adapter for Python Tool Server communication."""

    def __init__(
        self, host: str = "127.0.0.1", port: int = 8001, timeout: float = 30.0
    ):
        """Initialize the Python Tool Adapter.

        Args:
            host: Host of the Python Tool Server
            port: Port of the Python Tool Server
            timeout: Request timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"
        self.client = httpx.AsyncClient(timeout=timeout)
        logger.info(
            f"Initialized Python Tool Adapter for {self.base_url}",
            adapter="python-tool",
            host=host,
            port=port,
        )

    async def execute(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a tool via the Python Tool Server.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            context: Optional execution context

        Returns:
            Dict[str, Any]: Tool execution result

        Raises:
            AdapterError: If execution fails
        """
        # Route the request to the appropriate tool
        return await self.route_request(tool_name, parameters, context)

    async def route_request(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Route a request to the Python Tool Server.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            context: Optional execution context

        Returns:
            Dict[str, Any]: Tool execution result

        Raises:
            AdapterError: If the request fails
        """
        try:
            # Prepare request
            url = f"{self.base_url}/tools/{tool_name}"
            payload = {
                "tool_name": tool_name,
                "parameters": parameters,
                "context": context or {},
            }

            # Send request
            logger.debug(
                f"Sending request to Python Tool Server: {tool_name}",
                adapter="python-tool",
                tool=tool_name,
            )
            response = await self.client.post(url, json=payload)

            # Handle response
            if response.status_code != 200:
                error_msg = f"Error from Python Tool Server: {response.text}"
                logger.error(
                    error_msg,
                    adapter="python-tool",
                    tool=tool_name,
                    status_code=response.status_code,
                )
                raise AdapterError(error_msg)

            result = response.json()
            return result
        except httpx.RequestError as e:
            error_msg = f"Request to Python Tool Server failed: {str(e)}"
            logger.error(
                error_msg,
                adapter="python-tool",
                tool=tool_name,
                error=str(e),
            )
            raise AdapterError(error_msg) from e
        except Exception as e:
            error_msg = f"Error executing {tool_name}: {str(e)}"
            logger.error(
                error_msg,
                adapter="python-tool",
                tool=tool_name,
                error=str(e),
            )
            raise AdapterError(error_msg) from e

    async def initialize(self) -> None:
        """Initialize the adapter.

        Raises:
            AdapterError: If initialization fails
        """
        try:
            await self.health_check()
        except Exception as e:
            raise AdapterError(f"Failed to initialize adapter: {str(e)}") from e

    async def shutdown(self) -> None:
        """Shutdown the adapter.

        Raises:
            AdapterError: If shutdown fails
        """
        try:
            await self.client.aclose()
        except Exception as e:
            raise AdapterError(f"Failed to shutdown adapter: {str(e)}") from e

    async def health_check(self) -> dict[str, Any]:
        """Check adapter health.

        Returns:
            Dict[str, Any]: Health check result

        Raises:
            AdapterError: If health check fails
        """
        try:
            url = f"{self.base_url}/health"
            response = await self.client.get(url)

            if response.status_code != 200:
                return {
                    "status": "unhealthy",
                    "message": f"Health check failed with status {response.status_code}: {response.text}",
                }

            return {
                "status": "healthy",
                "server": self.base_url,
                "details": response.json(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "server": self.base_url,
                "error": str(e),
            }
