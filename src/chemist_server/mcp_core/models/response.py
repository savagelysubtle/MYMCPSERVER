"""Response models for MCP Core."""

import time
from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Details for an error response."""

    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model."""

    success: bool = False
    error: ErrorDetail
    correlation_id: str | None = None
    timestamp: float = Field(default_factory=time.time)


class CoreResponse(BaseModel):
    """Core response model for MCP."""

    success: bool = True
    data: dict[str, Any] | None = None
    correlation_id: str | None = None
    timestamp: float = Field(default_factory=time.time)
    tool_name: str | None = None
    version: str | None = None
    execution_time: float | None = None

    @classmethod
    def from_error(
        cls,
        error: ErrorDetail | Exception,
        correlation_id: str | None = None,
        tool_name: str | None = None,
        version: str | None = None,
    ) -> ErrorResponse:
        """Create an error response from an error.

        Args:
            error: Error detail or exception
            correlation_id: Request correlation ID
            tool_name: Tool name
            version: Tool version

        Returns:
            ErrorResponse: Error response model
        """
        if isinstance(error, Exception) and not isinstance(error, ErrorDetail):
            error_detail = ErrorDetail(
                code="INTERNAL_ERROR",
                message=str(error),
                details={"exception_type": error.__class__.__name__},
            )
        else:
            error_detail = error  # type: ignore

        return ErrorResponse(
            error=error_detail, correlation_id=correlation_id, timestamp=time.time()
        )
