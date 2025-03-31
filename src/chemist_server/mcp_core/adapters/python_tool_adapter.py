# src/mcp_core/adapters/python_tool_adapter.py
from typing import Any

import anyio  # For sleep in retry
import httpx

# Use specific errors
from ...mcp_core.errors import AdapterError, ToolError, TransportError

# Use structured logger
from ...mcp_core.logger import StructuredLogger

# Try to import mcp.types, but provide fallbacks if not available
try:
    import mcp.types as mcp_types

    HAS_MCP_TYPES = True
except ImportError:
    HAS_MCP_TYPES = False

    # Define minimal fallback types for when mcp.types is not available
    class Tool:
        """Simple fallback for mcp.types.Tool when not available."""

        def __init__(self, name: str, description: str, version: str = "1.0.0") -> None:
            self.name = name
            self.description = description
            self.version = version

    class ListToolsResult:
        """Simple fallback for mcp.types.ListToolsResult when not available."""

        def __init__(self, tools: list[Tool]) -> None:
            self.tools = tools

        @classmethod
        def model_validate(cls, data: dict) -> "ListToolsResult":
            """Simple validation method."""
            tools = [
                Tool(
                    name=t.get("name", "unknown"),
                    description=t.get("description", ""),
                    version=t.get("version", "1.0.0"),
                )
                for t in data.get("tools", [])
            ]
            return cls(tools=tools)


from .base_adapter import BaseAdapter

logger = StructuredLogger("adapter.python_tool")


class PythonToolAdapter(BaseAdapter):
    """Adapter for Python Tool Server communication."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8001,
        timeout: float = 30.0,
        retries: int = 1,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.retries = retries
        self.base_url = f"http://{host}:{port}"
        # Initialize client later in initialize()
        self.client: httpx.AsyncClient | None = None
        logger.info(
            f"Python Tool Adapter configured for {self.base_url}",
            adapter="python-tool",
            host=host,
            port=port,
        )

    async def initialize(self) -> None:
        """Initialize the adapter and HTTP client."""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=self.timeout)
            logger.info("HTTPX client initialized for PythonToolAdapter")
        # Optionally perform an initial health check
        try:
            await self.health_check()
        except AdapterError as e:
            logger.warning(f"Initial health check failed for Python Tool Server: {e}")
            # Don't raise here, allow execution attempts with circuit breaker

    async def shutdown(self) -> None:
        """Shutdown the adapter and close HTTP client."""
        if self.client:
            try:
                await self.client.aclose()
                self.client = None
                logger.info("HTTPX client closed for PythonToolAdapter")
            except Exception as e:
                logger.error(f"Error closing HTTPX client: {e}", exc_info=True)
                # Don't raise, just log

    async def execute(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a tool via the Python Tool Server with retries."""
        if not self.client:
            raise AdapterError("Adapter not initialized. Call initialize() first.")

        url = f"{self.base_url}/execute"  # Assuming a single endpoint now per SDK style
        payload = {
            "tool_name": tool_name,
            "parameters": parameters,
            "context": context or {},
        }

        last_exception: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                logger.debug(
                    f"Attempt {attempt + 1}/{self.retries + 1}: Sending request to Python Tool Server",
                    adapter="python-tool",
                    tool=tool_name,
                    url=url,
                )

                response = await self.client.post(url, json=payload)
                response.raise_for_status()  # Check for 4xx/5xx errors

                tool_response_data = response.json()

                # Check the ToolResponse structure from the tool server
                if not tool_response_data.get("success", False):
                    error_detail = tool_response_data.get(
                        "error", {"message": "Unknown tool error"}
                    )
                    error_msg = f"Tool execution failed on server: {error_detail.get('message', 'N/A')}"
                    logger.warning(
                        error_msg,
                        adapter="python-tool",
                        tool=tool_name,
                        error_detail=error_detail,
                    )
                    # Raise a specific ToolError that might be caught by circuit breaker
                    raise ToolError(error_msg, details=error_detail)

                logger.debug(
                    f"Successfully executed tool {tool_name} via adapter",
                    adapter="python-tool",
                    tool=tool_name,
                )
                return tool_response_data.get(
                    "data", {}
                )  # Return the 'data' part of ToolResponse

            except (
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.NetworkError,
            ) as e:
                last_exception = e
                msg = f"Network/Connection error contacting Python Tool Server on attempt {attempt + 1}: {e.__class__.__name__}"
                logger.warning(msg, adapter="python-tool", tool=tool_name, error=str(e))
                if attempt >= self.retries:
                    raise TransportError(
                        f"Failed to connect to Python Tool Server after {self.retries + 1} attempts: {e}"
                    ) from e
                await anyio.sleep(0.5 * (2**attempt))  # Exponential backoff
            except httpx.HTTPStatusError as e:
                last_exception = e
                msg = f"HTTP error from Python Tool Server on attempt {attempt + 1}: {e.response.status_code} - {e.response.text[:200]}"
                logger.warning(
                    msg,
                    adapter="python-tool",
                    tool=tool_name,
                    status_code=e.response.status_code,
                )
                if (
                    e.response.status_code >= 500 and attempt < self.retries
                ):  # Retry on server errors
                    await anyio.sleep(0.5 * (2**attempt))
                    continue  # Retry the loop
                else:  # Don't retry client errors (4xx) or after max retries
                    raise AdapterError(
                        f"HTTP error {e.response.status_code} from tool server: {e.response.text[:200]}"
                    ) from e
            except ToolError as e:
                # Propagate tool errors immediately, circuit breaker might handle this
                raise e
            except Exception as e:
                last_exception = e
                logger.error(
                    f"Unexpected error executing tool {tool_name} via adapter on attempt {attempt + 1}: {e}",
                    adapter="python-tool",
                    tool=tool_name,
                    exc_info=True,
                )
                if attempt >= self.retries:
                    raise AdapterError(
                        f"Failed to execute tool {tool_name} after {self.retries + 1} attempts"
                    ) from e
                await anyio.sleep(0.5 * (2**attempt))

        # Should not be reachable if retries > 0, but satisfies type checker
        raise AdapterError(
            "Tool execution failed after all retries."
        ) from last_exception

    async def health_check(self) -> dict[str, Any]:
        """Check the health of the adapter by connecting to the Python Tool Server."""
        if not self.client:
            return {"status": "unhealthy", "message": "Adapter not initialized"}
        try:
            url = f"{self.base_url}/health"  # Assume SDK server provides this implicitly or add it
            # If health is implemented as a tool:
            # response_data = await self.execute("health", {})
            # return {"status": "healthy", "server": self.base_url, "details": response_data }

            # If checking via simple GET:
            response = await self.client.get(url)
            if response.status_code != 200:
                return {
                    "status": "unhealthy",
                    "message": f"Health check failed: {response.status_code}",
                    "details": response.text[:200],
                }
            return {
                "status": "healthy",
                "server": self.base_url,
                "details": response.json(),
            }

        except (
            AdapterError,
            TransportError,
        ) as e:  # Catch errors from self.execute if health is a tool
            return {"status": "unhealthy", "server": self.base_url, "error": str(e)}
        except Exception as e:
            logger.warning(
                f"Health check failed for Python Tool Server: {e}", exc_info=True
            )
            return {"status": "unhealthy", "server": self.base_url, "error": str(e)}

    async def list_remote_tools(self) -> list[Tool | Any]:
        """Fetches the list of tools from the remote Python Tool Server."""
        if not self.client:
            raise AdapterError("Adapter not initialized. Call initialize() first.")

        # Construct a standard MCP tools/list request
        # Note: MCP SDK client sessions handle request IDs, but raw HTTP needs manual handling
        # For simplicity, we'll assume the SDK server doesn't require strict JSON-RPC framing
        # for a simple GET /tools endpoint if available, OR we need to implement
        # a minimal MCP client call here. Let's assume the SDK server provides /tools/list via GET.
        # **Correction:** The SDK server expects MCP JSON-RPC. We need to send that.
        # Let's use the adapter's *existing* execute logic cleverly, if possible,
        # or implement a minimal JSON-RPC call.

        # Minimal JSON-RPC call:
        request_payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "discovery_request",  # Use a fixed or random ID
        }
        url = f"{self.base_url}/"  # Assume MCP endpoint is root, adjust if different

        try:
            logger.debug(f"Sending tools/list request to {url}")
            response = await self.client.post(url, json=request_payload)
            response.raise_for_status()
            response_data = response.json()

            # Validate the response structure (basic check)
            if "result" not in response_data or "tools" not in response_data["result"]:
                raise AdapterError(
                    "Invalid tools/list response format from tool server."
                )

            # Use the appropriate implementation based on whether mcp.types is available
            if HAS_MCP_TYPES:
                # Use the real mcp.types implementation
                list_result = mcp_types.ListToolsResult.model_validate(
                    response_data["result"]
                )
                logger.info(
                    f"Discovered {len(list_result.tools)} tools from Python Tool Server."
                )
                return list_result.tools
            else:
                # Use our fallback implementation
                list_result = ListToolsResult.model_validate(response_data["result"])
                logger.info(
                    f"Discovered {len(list_result.tools)} tools from Python Tool Server (using fallback types)."
                )
                return list_result.tools

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error(
                f"Failed to list tools from Python Tool Server at {url}: {e}",
                exc_info=True,
            )
            raise TransportError(f"Could not fetch tools from {url}: {e}") from e
        except Exception as e:
            logger.error(
                f"Error parsing tool list from Python Tool Server: {e}", exc_info=True
            )
            raise AdapterError("Failed to parse tool list from remote server") from e
