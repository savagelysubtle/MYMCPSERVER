"""API routes for MCP Core."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from .errors import AdapterError, CircuitBreakerError
from .logger import logger
from .router import Router


class ToolRequest(BaseModel):
    """Tool execution request model."""

    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Tool parameters"
    )
    context: dict[str, Any] | None = Field(
        default=None, description="Optional execution context"
    )
    version: str | None = Field(default=None, description="Tool version")
    use_circuit_breaker: bool = Field(
        default=True, description="Whether to use circuit breaker"
    )


class ToolResponse(BaseModel):
    """Tool execution response model."""

    status: str = Field(..., description="Execution status")
    result: dict[str, Any] | None = Field(default=None, description="Execution result")
    error: str | None = Field(default=None, description="Error message if failed")


class ToolInfo(BaseModel):
    """Tool information model."""

    tool_name: str = Field(..., description="Tool name")
    version: str = Field(..., description="Tool version")
    adapter_type: str = Field(..., description="Type of adapter")
    description: str = Field("", description="Tool description")
    is_latest: bool = Field(False, description="Whether this is the latest version")
    is_active: bool = Field(True, description="Whether the tool is active")
    tags: list[str] = Field(default_factory=list, description="Tool tags")


# Create router
router = APIRouter(tags=["tools"])


async def get_router(request: Request) -> Router:
    """Dependency to get the Router from request state.

    Args:
        request: FastAPI request

    Returns:
        Router: Core router instance
    """
    return request.app.state.registry_router


@router.post("/tools", response_model=ToolResponse)
async def execute_tool(request: ToolRequest, router: Router = Depends(get_router)):
    """Execute a tool.

    Args:
        request: Tool execution request
        router: Router dependency

    Returns:
        ToolResponse: Execution response
    """
    try:
        result = await router.route_request(
            tool_name=request.tool_name,
            parameters=request.parameters,
            context=request.context,
            version=request.version,
            use_circuit_breaker=request.use_circuit_breaker,
        )

        return ToolResponse(status="success", result=result)
    except CircuitBreakerError as e:
        logger.warning(
            f"Circuit breaker error for tool {request.tool_name}",
            tool=request.tool_name,
            error=str(e),
        )
        return ToolResponse(status="circuit_open", error=str(e))
    except AdapterError as e:
        logger.error(
            f"Adapter error for tool {request.tool_name}",
            tool=request.tool_name,
            error=str(e),
        )
        return ToolResponse(status="error", error=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error executing tool {request.tool_name}",
            tool=request.tool_name,
            error=str(e),
            traceback=True,  # Add traceback flag to indicate this is an exception
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get("/tools", response_model=list[ToolInfo])
async def list_tools(router: Router = Depends(get_router)):
    """List all available tools.

    Args:
        router: Router dependency

    Returns:
        List[ToolInfo]: List of available tools
    """
    tools = await router.list_available_tools()
    return tools


@router.get("/tools/{tool_name}", response_model=dict[str, Any])
async def get_tool_info(
    tool_name: str, version: str | None = None, router: Router = Depends(get_router)
):
    """Get detailed information about a tool.

    Args:
        tool_name: Tool name
        version: Tool version (optional)
        router: Router dependency

    Returns:
        Dict[str, Any]: Tool metadata
    """
    try:
        return await router.get_tool_metadata(tool_name, version)
    except AdapterError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/tools/{tool_name}/health", response_model=dict[str, Any])
async def get_tool_health(
    tool_name: str, version: str | None = None, router: Router = Depends(get_router)
):
    """Get health information for a tool.

    Args:
        tool_name: Tool name
        version: Tool version (optional)
        router: Router dependency

    Returns:
        Dict[str, Any]: Health information
    """
    health = await router.get_tool_health(tool_name, version)
    if health.get("status") == "error" and "error" in health:
        # Return a 200 with error details rather than a 404 or 500
        # This allows clients to properly display health status
        return health

    return health
