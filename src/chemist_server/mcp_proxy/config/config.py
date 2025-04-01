from pydantic import Field
from pydantic_settings import BaseSettings


class ProxyConfig(BaseSettings):
    """MCP Proxy configuration."""

    # SSE settings
    sse_host: str = Field(default="127.0.0.1", validation_alias="MCP_SSE_HOST")
    sse_port: int = Field(default=8080, validation_alias="MCP_SSE_PORT")

    # stdio settings
    stdio_buffer_size: int = Field(
        default=4096, validation_alias="MCP_STDIO_BUFFER_SIZE"
    )
    stdio_encoding: str = Field(default="utf-8", validation_alias="MCP_STDIO_ENCODING")

    # Connection settings
    connection_timeout: int = Field(
        default=30, validation_alias="MCP_CONNECTION_TIMEOUT"
    )
    keep_alive_interval: int = Field(
        default=15, validation_alias="MCP_KEEPALIVE_INTERVAL"
    )

    # Security
    allowed_origins: list[str] = Field(default_factory=list)
    auth_required: bool = Field(default=False, validation_alias="MCP_AUTH_REQUIRED")

    model_config = {
        "env_prefix": "MCP_",
        "case_sensitive": False,
    }


def get_proxy_config() -> ProxyConfig:
    """Get proxy configuration instance."""
    return ProxyConfig()
