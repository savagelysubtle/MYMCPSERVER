# MCP Core Layer Technical Specification

## 1. System Architecture

### 1.1 Core Components

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import asyncio
import logging
from pydantic import BaseModel

class RequestContext(BaseModel):
    """Request context with correlation ID and metadata."""
    correlation_id: str
    timestamp: datetime
    source: str
    version: Optional[str] = None
    metadata: Dict[str, Any] = {}

class CoreRequest(BaseModel):
    """Validated request model."""
    tool_name: str
    action: str
    params: Dict[str, Any]
    context: RequestContext

class CoreResponse(BaseModel):
    """Standardized response model."""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[Dict[str, str]]
    context: RequestContext
    metrics: Dict[str, Any]

class RequestProcessor:
    """Handles request validation and enrichment."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def process_request(self, raw_request: Dict[str, Any]) -> CoreRequest:
        """Process and validate incoming request."""
        try:
            # Create request context
            context = RequestContext(
                correlation_id=self._generate_correlation_id(),
                timestamp=datetime.now(),
                source=raw_request.get('source', 'unknown')
            )

            # Validate and create request
            request = CoreRequest(
                tool_name=raw_request['tool'],
                action=raw_request['action'],
                params=raw_request.get('params', {}),
                context=context
            )

            self.logger.info(f"Request processed: {request.correlation_id}")
            return request

        except Exception as e:
            self.logger.error(f"Request processing failed: {str(e)}")
            raise RequestProcessingError(str(e))

class Router:
    """Intelligent request router with circuit breaker integration."""

    def __init__(self, registry: 'AdapterRegistry', config: Dict[str, Any]):
        self.registry = registry
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def route_request(self, request: CoreRequest) -> CoreResponse:
        """Route request to appropriate adapter with circuit breaker protection."""
        try:
            # Get adapter with circuit breaker
            adapter = await self.registry.get_adapter(
                request.tool_name,
                request.context.version
            )

            # Execute request through circuit breaker
            circuit_breaker = self.registry.get_circuit_breaker(request.tool_name)
            response = await circuit_breaker.execute(
                adapter.route_request,
                request
            )

            return response

        except CircuitBreakerOpenError as e:
            self.logger.warning(f"Circuit breaker open for {request.tool_name}")
            return self._create_error_response(request, "Service temporarily unavailable")

        except Exception as e:
            self.logger.error(f"Routing error: {str(e)}")
            return self._create_error_response(request, str(e))

class MetricsCollector:
    """Collects and manages system metrics."""

    def __init__(self):
        self.metrics = {}
        self._lock = asyncio.Lock()

    async def record_request(
        self,
        request: CoreRequest,
        response: CoreResponse,
        duration: float
    ):
        """Record request metrics."""
        async with self._lock:
            key = f"{request.tool_name}:{request.context.version or 'latest'}"
            if key not in self.metrics:
                self.metrics[key] = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'total_duration': 0,
                    'average_duration': 0
                }

            metrics = self.metrics[key]
            metrics['total_requests'] += 1
            if response.success:
                metrics['successful_requests'] += 1
            else:
                metrics['failed_requests'] += 1

            metrics['total_duration'] += duration
            metrics['average_duration'] = (
                metrics['total_duration'] / metrics['total_requests']
            )
```

### 1.2 Main Application

```python
class MCPCore:
    """Main MCP Core application."""

    def __init__(self):
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.metrics = MetricsCollector()
        self.registry = AdapterRegistry()
        self.router = Router(self.registry, self.config)
        self.processor = RequestProcessor(self.config)

    async def handle_request(self, raw_request: Dict[str, Any]) -> Dict[str, Any]:
        """Main request handling pipeline."""
        start_time = time.time()

        try:
            # Process and validate request
            request = await self.processor.process_request(raw_request)

            # Route request and get response
            response = await self.router.route_request(request)

            # Record metrics
            duration = time.time() - start_time
            await self.metrics.record_request(request, response, duration)

            return response.dict()

        except Exception as e:
            self.logger.error(f"Request handling failed: {str(e)}")
            return self._create_error_response(raw_request, str(e))
```

## 2. Configuration Management

### 2.1 Environment Configuration

```python
from pydantic import BaseSettings, Field

class CoreConfig(BaseSettings):
    """Core configuration settings."""

    # Server settings
    port: int = Field(5000, env='CORE_PORT')
    host: str = Field('localhost', env='CORE_HOST')

    # Feature flags
    enable_circuit_breaker: bool = Field(True, env='ENABLE_CIRCUIT_BREAKER')
    enable_metrics: bool = Field(True, env='ENABLE_METRICS')
    enable_tracing: bool = Field(True, env='ENABLE_TRACING')

    # Circuit breaker settings
    circuit_breaker_failure_threshold: int = Field(5, env='CB_FAILURE_THRESHOLD')
    circuit_breaker_recovery_timeout: int = Field(30, env='CB_RECOVERY_TIMEOUT')

    # Logging settings
    log_level: str = Field('INFO', env='LOG_LEVEL')
    log_format: str = Field(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        env='LOG_FORMAT'
    )

    class Config:
        env_prefix = 'MCP_'
```

## 3. Error Handling

### 3.1 Custom Exceptions

```python
class MCPError(Exception):
    """Base exception for MCP Core."""
    pass

class RequestProcessingError(MCPError):
    """Raised when request processing fails."""
    pass

class RoutingError(MCPError):
    """Raised when request routing fails."""
    pass

class AdapterError(MCPError):
    """Raised when adapter operations fail."""
    pass
```

### 3.2 Error Response Creation

```python
def create_error_response(
    request: Dict[str, Any],
    error: str,
    status_code: int = 500
) -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        'success': False,
        'error': {
            'message': error,
            'code': status_code,
            'request_id': request.get('correlation_id', 'unknown')
        },
        'data': None,
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'service': 'mcp-core'
        }
    }
```

## 4. Logging and Monitoring

### 4.1 Logging Configuration

```python
import logging.config
import yaml

def setup_logging(config_path: str = 'logging.yaml'):
    """Configure logging using YAML configuration."""
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    except Exception as e:
        # Fallback to basic configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
```

### 4.2 Metrics Export

```python
class MetricsExporter:
    """Exports metrics to monitoring system."""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector

    async def export_metrics(self) -> Dict[str, Any]:
        """Export current metrics."""
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.collector.metrics,
            'system_stats': await self._get_system_stats()
        }

    async def _get_system_stats(self) -> Dict[str, Any]:
        """Collect system statistics."""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'connections': len(psutil.net_connections())
        }
```

## 5. Testing

### 5.1 Unit Tests

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_request_processing():
    """Test request processing pipeline."""
    processor = RequestProcessor(config={})

    # Test valid request
    raw_request = {
        'tool': 'test_tool',
        'action': 'test_action',
        'params': {'key': 'value'}
    }

    request = await processor.process_request(raw_request)
    assert request.tool_name == 'test_tool'
    assert request.action == 'test_action'

    # Test invalid request
    with pytest.raises(RequestProcessingError):
        await processor.process_request({})
```

### 5.2 Integration Tests

```python
@pytest.mark.asyncio
async def test_full_request_pipeline():
    """Test complete request handling pipeline."""
    core = MCPCore()

    # Test successful request
    request = {
        'tool': 'test_tool',
        'action': 'test_action',
        'params': {'key': 'value'}
    }

    response = await core.handle_request(request)
    assert response['success'] is True

    # Test circuit breaker
    with patch('mcp_core.router.Router.route_request') as mock_route:
        mock_route.side_effect = CircuitBreakerOpenError()
        response = await core.handle_request(request)
        assert response['success'] is False
        assert 'Service temporarily unavailable' in response['error']['message']
```

## 6. Deployment

### 6.1 Docker Configuration

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MCP_PORT=5000
ENV MCP_HOST=0.0.0.0
ENV MCP_LOG_LEVEL=INFO

CMD ["python", "-m", "mcp_core"]
```

### 6.2 Kubernetes Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-core
  template:
    metadata:
      labels:
        app: mcp-core
    spec:
      containers:
        - name: mcp-core
          image: mcp-core:latest
          ports:
            - containerPort: 5000
          env:
            - name: MCP_PORT
              value: '5000'
            - name: MCP_LOG_LEVEL
              value: 'INFO'
          livenessProbe:
            httpGet:
              path: /health
              port: 5000
          readinessProbe:
            httpGet:
              path: /ready
              port: 5000
```

## 7. API Documentation

### 7.1 Request Format

```json
{
  "tool": "string",
  "action": "string",
  "params": {
    "key": "value"
  },
  "metadata": {
    "version": "string",
    "source": "string"
  }
}
```

### 7.2 Response Format

```json
{
  "success": true,
  "data": {
    "key": "value"
  },
  "error": null,
  "context": {
    "correlation_id": "string",
    "timestamp": "string",
    "source": "string"
  },
  "metrics": {
    "duration_ms": 0,
    "status": "string"
  }
}
```

## 8. Future Enhancements

1. **Advanced Request Routing:**

   - AI-based routing decisions
   - Request prioritization
   - Traffic shaping

2. **Enhanced Monitoring:**

   - Prometheus integration
   - Grafana dashboards
   - Custom metric exporters

3. **Performance Optimizations:**

   - Request batching
   - Response streaming
   - Connection pooling

4. **Security Enhancements:**
   - Request signing
   - Rate limiting
   - Access control
