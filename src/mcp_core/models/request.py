"""Request models for MCP Core."""

import time
import uuid
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator


class RequestContext(BaseModel):
    """Context information for a request."""

    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    source: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        json_encoders = {uuid.UUID: str}


class CoreRequest(BaseModel):
    """Core request model for MCP."""

    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: RequestContext = Field(default_factory=RequestContext)
    version: Optional[str] = None
    timeout: Optional[float] = None

    @validator("timeout")
    def validate_timeout(cls, value: Optional[float]) -> Optional[float]:
        """Validate timeout is positive."""
        if value is not None and value <= 0:
            raise ValueError("Timeout must be positive")
        return value
