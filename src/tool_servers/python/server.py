"""Python tool server for MCP."""

import importlib
import inspect
import logging
import os
import traceback
from typing import Any, Callable, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configure basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("python_tool_server")


class ToolRequest(BaseModel):
    """Tool request model."""

    tool_name: str
    parameters: Dict[str, Any] = {}
    context: Optional[Dict[str, Any]] = None


class ToolResponse(BaseModel):
    """Tool response model."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class ToolMetadata(BaseModel):
    """Tool metadata model."""

    name: str
    version: str
    description: str
    parameters: Dict[str, Dict[str, Any]] = {}
    examples: List[Dict[str, Any]] = []


class ToolDefinition:
    """Tool definition class."""

    def __init__(
        self,
        name: str,
        function: Callable,
        version: str = "1.0.0",
        description: str = "",
        metadata: Optional[ToolMetadata] = None,
    ):
        """Initialize tool definition.

        Args:
            name: Tool name
            function: Tool function
            version: Tool version
            description: Tool description
            metadata: Tool metadata
        """
        self.name = name
        self.function = function
        self.version = version
        self.description = description
        self.metadata = metadata or self._generate_metadata()

        # Check if function is async
        self.is_async = inspect.iscoroutinefunction(function)

    def _generate_metadata(self) -> ToolMetadata:
        """Generate tool metadata from function signature.

        Returns:
            ToolMetadata: Tool metadata
        """
        signature = inspect.signature(self.function)
        parameters = {}

        for name, param in signature.parameters.items():
            # Skip self/cls for methods
            if name in ["self", "cls"]:
                continue

            param_info = {"description": "", "type": "any"}

            # Get type annotation if available
            if param.annotation != inspect.Parameter.empty:
                if hasattr(param.annotation, "__name__"):
                    param_info["type"] = param.annotation.__name__.lower()
                else:
                    param_info["type"] = str(param.annotation)

            # Get default value if available
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default
                param_info["required"] = False
            else:
                param_info["required"] = True

            parameters[name] = param_info

        # Get description from docstring
        doc = inspect.getdoc(self.function)
        description = doc.split("\n")[0] if doc else self.description

        return ToolMetadata(
            name=self.name,
            version=self.version,
            description=description,
            parameters=parameters,
        )

    async def execute(
        self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the tool.

        Args:
            parameters: Tool parameters
            context: Optional execution context

        Returns:
            Dict[str, Any]: Tool execution result
        """
        try:
            # Prepare parameters
            function_params = {}

            for name, param in inspect.signature(self.function).parameters.items():
                if name in ["self", "cls"]:
                    continue

                if name in parameters:
                    function_params[name] = parameters[name]
                elif (
                    context
                    and name == "context"
                    and param.default == inspect.Parameter.empty
                ):
                    # Inject context if parameter exists and doesn't have a default
                    function_params["context"] = context

            # Execute function
            if self.is_async:
                result = await self.function(**function_params)
            else:
                result = self.function(**function_params)

            # Convert result to dict if needed
            if not isinstance(result, dict):
                result = {"result": result}

            return result
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {str(e)}")
            raise


class PythonToolServer:
    """Python tool server implementation."""

    def __init__(self):
        """Initialize the tool server."""
        self.app = FastAPI(
            title="Python Tool Server",
            description="Tool server for Python-based MCP tools",
            version="1.0.0",
        )
        self.tools: Dict[str, ToolDefinition] = {}

        # Register routes
        self._register_routes()

    def _register_routes(self) -> None:
        """Register API routes."""

        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "tools": list(self.tools.keys())}

        @self.app.post("/execute")
        async def execute_tool(request: ToolRequest):
            return await self._execute_tool(request)

        @self.app.get("/tools")
        async def list_tools():
            return {
                "tools": [
                    {
                        "name": tool.name,
                        "version": tool.version,
                        "description": tool.description,
                    }
                    for tool in self.tools.values()
                ]
            }

        @self.app.get("/tools/{tool_name}")
        async def get_tool_metadata(tool_name: str):
            if tool_name not in self.tools:
                raise HTTPException(
                    status_code=404, detail=f"Tool {tool_name} not found"
                )
            return self.tools[tool_name].metadata

    async def _execute_tool(self, request: ToolRequest) -> ToolResponse:
        """Execute a tool.

        Args:
            request: Tool request

        Returns:
            ToolResponse: Tool response
        """
        if request.tool_name not in self.tools:
            return ToolResponse(
                success=False, error={"message": f"Tool {request.tool_name} not found"}
            )

        try:
            # Execute the tool
            tool = self.tools[request.tool_name]
            result = await tool.execute(request.parameters, request.context)

            return ToolResponse(success=True, data=result)
        except Exception as e:
            logger.error(f"Error executing tool {request.tool_name}: {str(e)}")
            return ToolResponse(
                success=False,
                error={"message": str(e), "traceback": traceback.format_exc()},
            )

    def register_tool(
        self,
        name: str,
        function: Callable,
        version: str = "1.0.0",
        description: str = "",
        metadata: Optional[ToolMetadata] = None,
    ) -> None:
        """Register a tool.

        Args:
            name: Tool name
            function: Tool function
            version: Tool version
            description: Tool description
            metadata: Tool metadata
        """
        tool = ToolDefinition(
            name=name,
            function=function,
            version=version,
            description=description,
            metadata=metadata,
        )

        self.tools[name] = tool
        logger.info(f"Registered tool: {name} v{version}")

    def load_tools_from_module(self, module_name: str) -> None:
        """Load tools from a module.

        Args:
            module_name: Module name
        """
        try:
            module = importlib.import_module(module_name)

            # Look for tool definitions
            for name, obj in inspect.getmembers(module):
                if hasattr(obj, "__mcp_tool__") and obj.__mcp_tool__:
                    # Get tool metadata
                    tool_name = getattr(obj, "__mcp_tool_name__", name)
                    tool_version = getattr(obj, "__mcp_tool_version__", "1.0.0")
                    tool_description = getattr(obj, "__mcp_tool_description__", "")

                    # Register the tool
                    self.register_tool(
                        name=tool_name,
                        function=obj,
                        version=tool_version,
                        description=tool_description,
                    )

            logger.info(f"Loaded tools from module: {module_name}")
        except ImportError as e:
            logger.error(f"Error loading module {module_name}: {str(e)}")

    def start(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Start the server.

        Args:
            host: Server host
            port: Server port
        """
        logger.info(f"Starting Python Tool Server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)


def mcp_tool(
    name: Optional[str] = None, version: str = "1.0.0", description: str = ""
) -> Callable:
    """Decorator to mark a function as an MCP tool.

    Args:
        name: Tool name (defaults to function name)
        version: Tool version
        description: Tool description

    Returns:
        Callable: Decorated function
    """

    def decorator(func: Callable) -> Callable:
        func.__mcp_tool__ = True
        func.__mcp_tool_name__ = name or func.__name__
        func.__mcp_tool_version__ = version
        func.__mcp_tool_description__ = description
        return func

    return decorator


def main() -> None:
    """Main entry point."""
    # Create the server
    server = PythonToolServer()

    # Load tools from environment variable
    tool_modules = os.environ.get("MCP_TOOL_MODULES", "").split(",")
    for module in tool_modules:
        if module:
            server.load_tools_from_module(module)

    # Start the server
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8000"))
    server.start(host=host, port=port)


if __name__ == "__main__":
    main()
