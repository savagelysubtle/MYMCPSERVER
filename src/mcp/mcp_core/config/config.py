# src/mcp_core/config/config.py

from pydantic_settings import BaseSettings


class CoreConfig(BaseSettings):
    """MCP Core configuration (loaded nested under AppConfig)."""

    # No separate env_prefix needed if nested in AppConfig with env_nested_delimiter='__'
    # e.g., MCP_CORE__HOST maps to core.host
    # model_config = SettingsConfigDict(env_prefix="MCP_CORE_") # Remove if nested

    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False  # This might be redundant if AppConfig.logging.level is DEBUG
    tool_timeout: int = 30
    max_retries: int = 3  # Used by circuit breaker?
    auth_token: str | None = None
    # allowed_origins might be handled by FastMCP/Uvicorn directly if using SSE/HTTP
    # allowed_origins: List[str] = Field(default_factory=list)

    # Add any other core-specific settings here


# Remove get_core_config() if AppConfig is the single source
# def get_core_config() -> CoreConfig:
#     return CoreConfig()
