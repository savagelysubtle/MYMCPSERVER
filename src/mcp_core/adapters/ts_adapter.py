"""TypeScript adapter for MCP tools."""

import asyncio
import os
import subprocess
from typing import Any, Dict, Optional

from ..errors import AdapterError
from ..logger import logger
from .base_adapter import BaseAdapter


class TypeScriptAdapter(BaseAdapter):
    """Adapter for TypeScript-based tools."""

    def __init__(
        self,
        server_path: str,
        tool_name: str,
        server_host: str = "localhost",
        server_port: int = 3000,
    ):
        """Initialize TypeScript adapter.

        Args:
            server_path: Path to TypeScript server directory
            tool_name: Name of the tool in the TypeScript server
            server_host: Host where TypeScript server runs
            server_port: Port where TypeScript server runs
        """
        self.server_path = server_path
        self.tool_name = tool_name
        self.server_host = server_host
        self.server_port = server_port
        self.server_url = f"http://{server_host}:{server_port}"
        self.server_process = None

        logger.info(
            f"Initialized TypeScript adapter for {tool_name}",
            tool=tool_name,
            server_path=server_path,
            server_url=self.server_url,
        )

    async def _start_server(self) -> None:
        """Start the TypeScript server.

        Raises:
            AdapterError: If server fails to start
        """
        if self.server_process and self.server_process.returncode is None:
            # Server already running
            return

        try:
            # Start server as subprocess
            self.server_process = subprocess.Popen(
                ["npm", "start"],
                cwd=self.server_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "PORT": str(self.server_port)},
            )

            # Wait a bit for server to start
            await asyncio.sleep(2)

            # Check if process started successfully
            if self.server_process.poll() is not None:
                stderr = (
                    self.server_process.stderr.read()
                    if self.server_process.stderr
                    else ""
                )
                raise AdapterError(f"TypeScript server failed to start: {stderr}")

            logger.info(
                f"Started TypeScript server at {self.server_url}",
                tool=self.tool_name,
                server_url=self.server_url,
            )
        except Exception as e:
            raise AdapterError(f"Failed to start TypeScript server: {str(e)}") from e

    async def execute(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a TypeScript tool.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            context: Optional execution context

        Returns:
            Dict[str, Any]: Tool execution result

        Raises:
            AdapterError: If execution fails
        """
        try:
            # Ensure server is running
            await self._start_server()

            # Use httpx or another HTTP client to make a request to the TypeScript server
            # This is a placeholder for the actual HTTP request
            # In a real implementation, you would make an HTTP request to the server

            # Placeholder implementation
            result = {"status": "success", "message": "TypeScript tool executed"}
            return result
        except Exception as e:
            logger.error(
                f"Error executing TypeScript tool {tool_name}",
                tool=tool_name,
                error=str(e),
            )
            raise AdapterError(f"Error executing TypeScript tool: {str(e)}") from e

    async def health_check(self) -> Dict[str, Any]:
        """Check adapter health.

        Returns:
            Dict[str, Any]: Health check result

        Raises:
            AdapterError: If health check fails
        """
        try:
            # Check if server is running
            if not self.server_process or self.server_process.poll() is not None:
                return {
                    "status": "unhealthy",
                    "message": "TypeScript server not running",
                }

            # Placeholder for making a health check request to the TypeScript server
            # In a real implementation, you would make an HTTP request to a health endpoint

            return {
                "status": "healthy",
                "server_url": self.server_url,
                "tool": self.tool_name,
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def initialize(self) -> None:
        """Initialize the adapter.

        Raises:
            AdapterError: If initialization fails
        """
        try:
            await self._start_server()
        except Exception as e:
            raise AdapterError(
                f"Failed to initialize TypeScript adapter: {str(e)}"
            ) from e

    async def shutdown(self) -> None:
        """Shutdown the adapter.

        Raises:
            AdapterError: If shutdown fails
        """
        if self.server_process and self.server_process.returncode is None:
            try:
                # Terminate the server process
                self.server_process.terminate()

                # Wait for process to terminate
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if not terminated
                    self.server_process.kill()

                logger.info("TypeScript server stopped", tool=self.tool_name)
            except Exception as e:
                logger.error(
                    "Error shutting down TypeScript server",
                    tool=self.tool_name,
                    error=str(e),
                )
                raise AdapterError(
                    f"Error shutting down TypeScript adapter: {str(e)}"
                ) from e
