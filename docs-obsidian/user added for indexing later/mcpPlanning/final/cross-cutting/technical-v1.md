# Cross-Cutting Technical Concerns

## 1. Global Configuration Management

### 1.1 Configuration Structure

```python
from pydantic import BaseSettings, Field
from typing import Dict, List, Optional

class BaseConfig(BaseSettings):
    """Base configuration with common settings."""
    environment: str = Field("development", env="MCP_ENV")
    debug: bool = Field(False, env="MCP_DEBUG")
    log_level: str = Field("INFO", env="MCP_LOG_LEVEL")

    class Config:
        env_prefix = "MCP_"
        case_sensitive = False

class CoreConfig(BaseConfig):
    """MCP Core specific configuration."""
    host: str = Field("127.0.0.1", env="CORE_HOST")
    port: int = Field(8000, env="CORE_PORT")
    tool_timeout: int = Field(30, env="TOOL_TIMEOUT")
    max_retries: int = Field(3, env="MAX_RETRIES")

class ProxyConfig(BaseConfig):
    """Proxy server configuration."""
    sse_port: int = Field(8080, env="SSE_PORT")
    stdio_buffer_size: int = Field(4096, env="STDIO_BUFFER_SIZE")
    allowed_origins: List[str] = Field(default_factory=list)
```

### 1.2 Configuration Loading

```python
import os
from pathlib import Path
import yaml

class ConfigLoader:
    """Unified configuration loader."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv(
            "MCP_CONFIG_PATH",
            "config.yaml"
        )

    def load_config(self) -> Dict:
        """Load configuration from multiple sources."""
        config = {}

        # Load base config from YAML
        if Path(self.config_path).exists():
            with open(self.config_path) as f:
                config.update(yaml.safe_load(f))

        # Override with environment variables
        config.update(self._load_env_vars())

        return config

    def _load_env_vars(self) -> Dict:
        """Load configuration from environment variables."""
        return {
            key: value for key, value in os.environ.items()
            if key.startswith("MCP_")
        }
```

### 1.3 Configuration Usage

```python
from functools import lru_cache

@lru_cache()
def get_config() -> CoreConfig:
    """Get cached configuration instance."""
    loader = ConfigLoader()
    config_dict = loader.load_config()
    return CoreConfig(**config_dict)

# Usage example
config = get_config()
print(f"Server running on {config.host}:{config.port}")
```

## 2. System-wide Error Handling

### 2.1 Error Hierarchy

```python
class MCPError(Exception):
    """Base error for MCP system."""

    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict] = None
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

class ConfigurationError(MCPError):
    """Configuration-related errors."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__("CONFIG_ERROR", message, details)

class TransportError(MCPError):
    """Transport layer errors."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__("TRANSPORT_ERROR", message, details)

class ToolError(MCPError):
    """Tool-related errors."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__("TOOL_ERROR", message, details)
```

### 2.2 Error Handling Middleware

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.middleware("http")
async def error_handler(request: Request, call_next):
    """Global error handling middleware."""
    try:
        return await call_next(request)
    except MCPError as e:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": e.details
                }
            }
        )
    except Exception as e:
        # Log unexpected errors
        logger.exception("Unexpected error")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred"
                }
            }
        )
```

## 3. Logging System

### 3.1 Structured Logger

```python
import logging
import json
from datetime import datetime
from typing import Any, Dict

class StructuredLogger:
    """JSON-formatted structured logger."""

    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Add JSON handler
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        self.logger.addHandler(handler)

    def _log(self, level: str, message: str, **kwargs):
        """Log with additional context."""
        extra = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.logger.name,
            **kwargs
        }

        getattr(self.logger, level.lower())(
            message,
            extra={"context": extra}
        )

    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("ERROR", message, **kwargs)

    def debug(self, message: str, **kwargs):
        self._log("DEBUG", message, **kwargs)

class JsonFormatter(logging.Formatter):
    """JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        data = {
            "level": record.levelname,
            "message": record.getMessage(),
            **(getattr(record, "context", {}))
        }
        return json.dumps(data)
```

### 3.2 Logger Usage

```python
# Create logger instance
logger = StructuredLogger("mcp_core")

# Usage examples
logger.info(
    "Request processed",
    request_id="123",
    duration_ms=45,
    tool="calculator"
)

logger.error(
    "Tool execution failed",
    tool="calculator",
    error_code="TIMEOUT",
    request_id="123"
)
```

## 4. Health Monitoring

### 4.1 Health Check Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, List
from enum import Enum
import time

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheck(ABC):
    """Base health check interface."""

    @abstractmethod
    async def check_health(self) -> Dict:
        """Perform health check."""
        pass

class SystemHealth(HealthCheck):
    """System-wide health monitoring."""

    def __init__(self, components: List[HealthCheck]):
        self.components = components
        self.start_time = time.time()

    async def check_health(self) -> Dict:
        """Check health of all components."""
        status = HealthStatus.HEALTHY
        results = {}

        for component in self.components:
            try:
                component_health = await component.check_health()
                results[component.__class__.__name__] = component_health

                if component_health["status"] == HealthStatus.UNHEALTHY:
                    status = HealthStatus.UNHEALTHY
                elif (component_health["status"] == HealthStatus.DEGRADED
                      and status != HealthStatus.UNHEALTHY):
                    status = HealthStatus.DEGRADED
            except Exception as e:
                results[component.__class__.__name__] = {
                    "status": HealthStatus.UNHEALTHY,
                    "error": str(e)
                }
                status = HealthStatus.UNHEALTHY

        return {
            "status": status,
            "uptime": time.time() - self.start_time,
            "components": results
        }
```

### 4.2 Component Health Checks

```python
class CoreHealth(HealthCheck):
    """MCP Core health check."""

    async def check_health(self) -> Dict:
        """Check core component health."""
        try:
            # Check critical services
            await self.check_database()
            await self.check_cache()

            return {
                "status": HealthStatus.HEALTHY,
                "details": {
                    "database": "connected",
                    "cache": "connected"
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e)
            }

class ToolServerHealth(HealthCheck):
    """Tool server health check."""

    async def check_health(self) -> Dict:
        """Check tool server health."""
        try:
            # Check tool availability
            tools = await self.check_tools()

            return {
                "status": HealthStatus.HEALTHY,
                "details": {
                    "active_tools": len(tools),
                    "tools": tools
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e)
            }
```

### 4.3 Health API Endpoints

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()
health_checker = SystemHealth([
    CoreHealth(),
    ToolServerHealth()
])

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    result = await health_checker.check_health()

    if result["status"] == HealthStatus.UNHEALTHY:
        raise HTTPException(status_code=503, detail=result)

    return result

@app.get("/health/live")
async def liveness():
    """Kubernetes liveness probe."""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    """Kubernetes readiness probe."""
    result = await health_checker.check_health()

    if result["status"] == HealthStatus.UNHEALTHY:
        raise HTTPException(status_code=503, detail=result)

    return {"status": "ready"}
```

## 5. Integration Example

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    # Load configuration
    config = get_config()

    # Setup logging
    logger = StructuredLogger(
        "mcp_core",
        level=config.log_level
    )

    # Initialize health checks
    health_checker = SystemHealth([
        CoreHealth(),
        ToolServerHealth()
    ])

    # Store in app state
    app.state.config = config
    app.state.logger = logger
    app.state.health = health_checker

    yield

    # Cleanup
    logger.info("Shutting down application")

app = FastAPI(lifespan=lifespan)

# Add error handling middleware
app.middleware("http")(error_handler)

# Add health check routes
app.include_router(health_router)
```

## 6. Future Enhancements

1. **Configuration Management:**

   - Dynamic configuration updates
   - Configuration validation
   - Secrets management

2. **Error Handling:**

   - Error aggregation
   - Error reporting service
   - Custom error pages

3. **Logging System:**

   - Log aggregation
   - Log analysis
   - Performance metrics

4. **Health Monitoring:**
   - Metrics export to Prometheus
   - Custom health dashboards
   - Automated recovery procedures
