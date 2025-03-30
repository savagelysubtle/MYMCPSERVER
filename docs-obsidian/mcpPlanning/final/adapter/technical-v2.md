# Enhanced Adapter/Registry Layer Technical Specification

## 1. Overview

The Adapter/Registry Layer serves as a sophisticated decoupling mechanism between the MCP Core and tool servers. This enhanced specification incorporates circuit breakers, versioning support, health monitoring, and improved error handling based on modern microservices best practices.

## 2. Core Components

### 2.1 Base Adapter Interface

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime

class BaseAdapter(ABC):
    """Abstract base class for all tool server adapters."""

    @abstractmethod
    async def route_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route a request to the appropriate tool server."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of the tool server."""
        pass

    @abstractmethod
    def get_version(self) -> str:
        """Get the version of the tool server."""
        pass
```

### 2.2 Circuit Breaker Implementation

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"     # Normal operation
    OPEN = "open"        # Failing, no requests allowed
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: int = 30
    half_open_max_calls: int = 3
    min_throughput: int = 10

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_success = 0
        self.half_open_calls = 0

    async def execute(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError()

        try:
            result = await func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self._handle_half_open_success()
            else:
                self.failure_count = 0
            return result
        except Exception as e:
            self._handle_failure()
            raise

    def _handle_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
        elif self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
```

### 2.3 Enhanced Registry

```python
from typing import Dict, Type
import asyncio
import logging

class AdapterRegistry:
    def __init__(self):
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._logger = logging.getLogger(__name__)

    async def register_adapter(
        self,
        tool_name: str,
        adapter: BaseAdapter,
        version: str,
        circuit_breaker: Optional[CircuitBreaker] = None
    ):
        """Register a new adapter with version control and circuit breaker."""
        if tool_name not in self._registry:
            self._registry[tool_name] = {}

        self._registry[tool_name][version] = {
            'adapter': adapter,
            'circuit_breaker': circuit_breaker or CircuitBreaker(CircuitBreakerConfig()),
            'health': await adapter.health_check(),
            'registered_at': datetime.now()
        }

        # Start health monitoring
        asyncio.create_task(self._monitor_adapter_health(tool_name, version))

    async def get_adapter(
        self,
        tool_name: str,
        version: Optional[str] = None
    ) -> BaseAdapter:
        """Get an adapter by name and optional version."""
        if tool_name not in self._registry:
            raise AdapterNotFoundError(f"No adapter found for tool: {tool_name}")

        if version:
            if version not in self._registry[tool_name]:
                raise VersionNotFoundError(
                    f"Version {version} not found for tool: {tool_name}"
                )
            return self._registry[tool_name][version]['adapter']

        # Return latest version if no specific version requested
        latest_version = max(self._registry[tool_name].keys())
        return self._registry[tool_name][latest_version]['adapter']

    async def _monitor_adapter_health(self, tool_name: str, version: str):
        """Continuously monitor adapter health."""
        while True:
            try:
                adapter_info = self._registry[tool_name][version]
                health = await adapter_info['adapter'].health_check()
                adapter_info['health'] = health

                if not health['healthy']:
                    self._logger.warning(
                        f"Unhealthy adapter detected: {tool_name} v{version}"
                    )

            except Exception as e:
                self._logger.error(
                    f"Error monitoring adapter health: {tool_name} v{version}: {str(e)}"
                )

            await asyncio.sleep(30)  # Check every 30 seconds
```

### 2.4 Concrete Adapter Implementations

```python
class PythonToolAdapter(BaseAdapter):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._version = "1.0.0"

    async def route_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation for Python tool server routing
        pass

    async def health_check(self) -> Dict[str, Any]:
        try:
            # Implement actual health check logic
            return {
                "healthy": True,
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "connection": "ok",
                    "latency_ms": 42
                }
            }
        except Exception as e:
            return {
                "healthy": False,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def get_version(self) -> str:
        return self._version

class TypeScriptToolAdapter(BaseAdapter):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self._version = "1.0.0"

    async def route_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation for TypeScript tool server routing
        pass

    async def health_check(self) -> Dict[str, Any]:
        # Similar to PythonToolAdapter implementation
        pass

    def get_version(self) -> str:
        return self._version
```

## 3. Usage Example

```python
async def main():
    # Initialize registry
    registry = AdapterRegistry()

    # Create and register Python tool adapter
    python_adapter = PythonToolAdapter(host="localhost", port=5000)
    await registry.register_adapter(
        tool_name="python_tool",
        adapter=python_adapter,
        version="1.0.0"
    )

    # Create and register TypeScript tool adapter
    ts_adapter = TypeScriptToolAdapter(base_url="http://localhost:3000")
    await registry.register_adapter(
        tool_name="typescript_tool",
        adapter=ts_adapter,
        version="1.0.0"
    )

    try:
        # Get adapter and route request
        adapter = await registry.get_adapter("python_tool")
        result = await adapter.route_request({"action": "example"})

    except CircuitBreakerOpenError:
        # Handle circuit breaker open state
        pass
    except AdapterNotFoundError:
        # Handle missing adapter
        pass
    except Exception as e:
        # Handle other errors
        pass
```

## 4. Error Handling

```python
class AdapterError(Exception):
    """Base class for adapter-related errors."""
    pass

class AdapterNotFoundError(AdapterError):
    """Raised when requested adapter is not found."""
    pass

class VersionNotFoundError(AdapterError):
    """Raised when requested version is not found."""
    pass

class CircuitBreakerOpenError(AdapterError):
    """Raised when circuit breaker is open."""
    pass

class HealthCheckError(AdapterError):
    """Raised when health check fails."""
    pass
```

## 5. Metrics and Monitoring

```python
from dataclasses import dataclass
from typing import List
import time

@dataclass
class AdapterMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    circuit_breaker_trips: int = 0
    average_response_time: float = 0.0
    response_times: List[float] = None

class MetricsCollector:
    def __init__(self):
        self._metrics = {}

    def record_request(
        self,
        tool_name: str,
        version: str,
        success: bool,
        response_time: float
    ):
        """Record metrics for a request."""
        key = f"{tool_name}:{version}"
        if key not in self._metrics:
            self._metrics[key] = AdapterMetrics(response_times=[])

        metrics = self._metrics[key]
        metrics.total_requests += 1
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1

        metrics.response_times.append(response_time)
        metrics.average_response_time = (
            sum(metrics.response_times) / len(metrics.response_times)
        )

    def get_metrics(self, tool_name: str, version: str) -> AdapterMetrics:
        """Get metrics for a specific adapter version."""
        key = f"{tool_name}:{version}"
        return self._metrics.get(key, AdapterMetrics())
```

## 6. Configuration Management

```python
from pydantic import BaseSettings

class AdapterConfig(BaseSettings):
    """Configuration for adapters."""

    # Circuit breaker settings
    failure_threshold: int = 5
    recovery_timeout: int = 30
    half_open_max_calls: int = 3

    # Health check settings
    health_check_interval: int = 30
    health_check_timeout: int = 5

    # Metrics settings
    enable_metrics: bool = True
    metrics_retention_days: int = 7

    # Version control settings
    enable_version_control: bool = True
    max_versions_per_tool: int = 3

    class Config:
        env_prefix = "ADAPTER_"
```

## 7. Integration with MCP Core

The enhanced Adapter/Registry Layer integrates with the MCP Core through a clean interface that handles:

1. Request routing with circuit breaker protection
2. Version management
3. Health monitoring
4. Metrics collection
5. Error propagation

The MCP Core should use the layer as follows:

```python
class MCPCore:
    def __init__(self):
        self.registry = AdapterRegistry()
        self.metrics = MetricsCollector()
        self.config = AdapterConfig()

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = request.get("tool")
        version = request.get("version")

        start_time = time.time()
        success = False

        try:
            adapter = await self.registry.get_adapter(tool_name, version)
            result = await adapter.route_request(request)
            success = True
            return result

        finally:
            response_time = time.time() - start_time
            if self.config.enable_metrics:
                self.metrics.record_request(
                    tool_name,
                    version or "latest",
                    success,
                    response_time
                )
```

## 8. Testing Strategy

The enhanced layer should be tested at multiple levels:

1. Unit tests for individual components
2. Integration tests for adapter interactions
3. Load tests for circuit breaker behavior
4. Health check monitoring tests
5. Version control tests
6. Metrics collection tests

Example test structure:

```python
async def test_circuit_breaker_behavior():
    config = CircuitBreakerConfig(
        failure_threshold=2,
        recovery_timeout=1
    )
    breaker = CircuitBreaker(config)

    # Test normal operation
    result = await breaker.execute(lambda: "success")
    assert result == "success"

    # Test failure threshold
    for _ in range(3):
        try:
            await breaker.execute(lambda: 1/0)
        except:
            pass

    # Verify circuit is open
    assert breaker.state == CircuitState.OPEN

    # Test recovery
    await asyncio.sleep(1)
    result = await breaker.execute(lambda: "recovered")
    assert result == "recovered"
    assert breaker.state == CircuitState.CLOSED
```

## 9. Deployment Considerations

1. **Configuration Management**

   - Use environment variables for configuration
   - Support multiple environments (dev, staging, prod)
   - Enable feature flags for gradual rollout

2. **Monitoring Setup**

   - Export metrics to monitoring system
   - Set up alerts for circuit breaker trips
   - Monitor adapter health status

3. **Scaling**

   - Support horizontal scaling of tool servers
   - Handle multiple instances of same adapter
   - Maintain distributed circuit breaker state

4. **Logging**
   - Structured logging for all operations
   - Correlation IDs for request tracking
   - Error context preservation

## 10. Future Enhancements

1. **Dynamic Configuration**

   - Runtime configuration updates
   - A/B testing support
   - Feature flag integration

2. **Advanced Metrics**

   - Prometheus integration
   - Custom metric exporters
   - Real-time monitoring

3. **Enhanced Versioning**

   - Semantic versioning support
   - Version deprecation
   - Automatic version rollback

4. **Improved Resilience**
   - Retry strategies
   - Fallback mechanisms
   - Rate limiting
