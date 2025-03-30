"""Response models for MCP Core."""

import time
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Details for an error response."""

    code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model."""

    success: bool = False
    error: ErrorDetail
    correlation_id: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)


class CoreResponse(BaseModel):
    """Core response model for MCP."""

    success: bool = True
    data: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)
    tool_name: Optional[str] = None
    version: Optional[str] = None
    execution_time: Optional[float] = None

    @classmethod
    def from_error(
        cls,
        error: Union[ErrorDetail, Exception],
        correlation_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        version: Optional[str] = None,
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
