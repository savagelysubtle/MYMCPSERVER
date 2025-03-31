"""Request models for MCP Core."""

import time
import uuid
from typing import Any

from pydantic import BaseModel, Field, field_validator


class RequestContext(BaseModel):
    """Context information for a request."""

    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    user_id: str | None = None
    session_id: str | None = None
    source: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        json_encoders = {uuid.UUID: str}


class CoreRequest(BaseModel):
    """Core request model for MCP."""

    tool_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    context: RequestContext = Field(default_factory=RequestContext)
    version: str | None = None
    timeout: float | None = None

    @field_validator("timeout")
    def validate_timeout(self, value: float | None) -> float | None:
        """Validate timeout is positive."""
        if value is not None and value <= 0:
            raise ValueError("Timeout must be positive")
        return value
