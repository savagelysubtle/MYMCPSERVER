from typing import List, Optional

from pydantic import BaseSettings, Field


class CoreConfig(BaseSettings):
    """MCP Core configuration."""

    # Server settings
    host: str = Field("127.0.0.1", env="MCP_CORE_HOST")
    port: int = Field(8000, env="MCP_CORE_PORT")
    debug: bool = Field(False, env="MCP_DEBUG")

    # Logging
    log_level: str = Field("INFO", env="MCP_LOG_LEVEL")
    log_format: str = Field("json", env="MCP_LOG_FORMAT")

    # Tool settings
    tool_timeout: int = Field(30, env="MCP_TOOL_TIMEOUT")
    max_retries: int = Field(3, env="MCP_MAX_RETRIES")

    # Security
    auth_token: Optional[str] = Field(None, env="MCP_AUTH_TOKEN")
    allowed_origins: List[str] = Field(default_factory=list)

    class Config:
        env_prefix = "MCP_"
        case_sensitive = False


def get_core_config() -> CoreConfig:
    """Get core configuration instance."""
    return CoreConfig()
