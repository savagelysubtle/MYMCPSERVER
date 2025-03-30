from typing import List

from pydantic import BaseSettings, Field


class ProxyConfig(BaseSettings):
    """MCP Proxy configuration."""

    # SSE settings
    sse_host: str = Field(default="127.0.0.1", env="MCP_SSE_HOST")
    sse_port: int = Field(default=8080, env="MCP_SSE_PORT")

    # stdio settings
    stdio_buffer_size: int = Field(default=4096, env="MCP_STDIO_BUFFER_SIZE")
    stdio_encoding: str = Field(default="utf-8", env="MCP_STDIO_ENCODING")

    # Connection settings
    connection_timeout: int = Field(default=30, env="MCP_CONNECTION_TIMEOUT")
    keep_alive_interval: int = Field(default=15, env="MCP_KEEPALIVE_INTERVAL")

    # Security
    allowed_origins: List[str] = Field(default_factory=list)
    auth_required: bool = Field(default=False, env="MCP_AUTH_REQUIRED")

    class Config:
        env_prefix = "MCP_"
        case_sensitive = False


def get_proxy_config() -> ProxyConfig:
    """Get proxy configuration instance."""
    return ProxyConfig()
