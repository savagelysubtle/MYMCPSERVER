# Transport Layer Technical Specification

## 1. Core Components

### 1.1 Transport Manager

```python
from dataclasses import dataclass
from typing import Optional, List
import logging
import asyncio

@dataclass
class TransportConfig:
    """Configuration for the transport layer."""
    sse_port: int = 8080
    sse_host: str = "127.0.0.1"
    log_level: str = "INFO"
    allow_origins: Optional[List[str]] = None
    pass_environment: bool = False

class TransportManager:
    """Manages transport layer components and lifecycle."""

    def __init__(self, config: TransportConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.sse_server = SSEServer(config)
        self.stdio_handler = StdioHandler(config)
        self.message_router = MessageRouter()

    async def start(self):
        """Start all transport components."""
        try:
            await asyncio.gather(
                self.sse_server.start(),
                self.stdio_handler.start(),
                self.message_router.start()
            )
        except Exception as e:
            self.logger.error(f"Failed to start transport layer: {e}")
            raise

    async def stop(self):
        """Stop all transport components."""
        try:
            await asyncio.gather(
                self.sse_server.stop(),
                self.stdio_handler.stop(),
                self.message_router.stop()
            )
        except Exception as e:
            self.logger.error(f"Failed to stop transport layer: {e}")
            raise
```

### 1.2 SSE Server Implementation

```python
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route, Mount
import uvicorn

class SSEServer:
    """Server-Sent Events server implementation."""

    def __init__(self, config: TransportConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.app = self._create_app()

    def _create_app(self) -> Starlette:
        """Create and configure the Starlette application."""
        middleware = []
        if self.config.allow_origins:
            middleware.append(
                Middleware(
                    CORSMiddleware,
                    allow_origins=self.config.allow_origins,
                    allow_methods=["*"],
                    allow_headers=["*"]
                )
            )

        return Starlette(
            debug=(self.config.log_level == "DEBUG"),
            middleware=middleware,
            routes=[
                Route("/sse", endpoint=self.handle_sse),
                Mount("/messages", app=self.handle_messages)
            ]
        )

    async def handle_sse(self, request):
        """Handle incoming SSE connections."""
        async with self.message_router.create_connection() as connection:
            async for message in connection:
                yield self._format_sse_message(message)

    async def handle_messages(self, request):
        """Handle incoming messages via HTTP POST."""
        message = await request.json()
        await self.message_router.route_message(message)
        return JSONResponse({"status": "ok"})
```

### 1.3 stdio Handler

```python
import asyncio
import os
from typing import Dict, Optional

class StdioHandler:
    """Handles stdio communication with processes."""

    def __init__(self, config: TransportConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.processes: Dict[str, asyncio.subprocess.Process] = {}

    async def spawn_process(
        self,
        command: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None
    ) -> str:
        """Spawn a new process and return its ID."""
        process_env = os.environ.copy() if self.config.pass_environment else {}
        if env:
            process_env.update(env)

        process = await asyncio.create_subprocess_exec(
            command,
            *(args or []),
            env=process_env,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        process_id = str(process.pid)
        self.processes[process_id] = process

        # Start reading from stdout/stderr
        asyncio.create_task(self._read_output(process_id))
        return process_id

    async def _read_output(self, process_id: str):
        """Read output from process stdout/stderr."""
        process = self.processes[process_id]
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            await self.message_router.route_message({
                "type": "process_output",
                "process_id": process_id,
                "data": line.decode()
            })
```

### 1.4 Message Router

```python
from asyncio import Queue
from typing import Dict, Set
import json

class MessageRouter:
    """Routes messages between components."""

    def __init__(self):
        self.connections: Dict[str, Queue] = {}
        self.subscriptions: Dict[str, Set[str]] = {}

    async def create_connection(self) -> str:
        """Create a new connection and return its ID."""
        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = Queue()
        return connection_id

    async def subscribe(self, connection_id: str, topic: str):
        """Subscribe a connection to a topic."""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        self.subscriptions[topic].add(connection_id)

    async def route_message(self, message: Dict):
        """Route a message to subscribed connections."""
        topic = message.get("topic", "broadcast")
        subscribers = self.subscriptions.get(topic, set())

        for connection_id in subscribers:
            if connection_id in self.connections:
                await self.connections[connection_id].put(message)
```

## 2. Protocol Adapters

### 2.1 SSE Protocol Adapter

```python
class SSEAdapter:
    """Adapts messages to/from SSE format."""

    @staticmethod
    def format_message(message: Dict) -> str:
        """Format a message as an SSE event."""
        event_type = message.get("type", "message")
        data = json.dumps(message.get("data", {}))
        return f"event: {event_type}\ndata: {data}\n\n"

    @staticmethod
    def parse_message(event: str) -> Dict:
        """Parse an SSE event into a message."""
        lines = event.strip().split("\n")
        message = {"type": "message", "data": {}}

        for line in lines:
            if line.startswith("event:"):
                message["type"] = line[6:].strip()
            elif line.startswith("data:"):
                message["data"] = json.loads(line[5:].strip())

        return message
```

### 2.2 stdio Protocol Adapter

```python
class StdioAdapter:
    """Adapts messages to/from stdio format."""

    @staticmethod
    def format_message(message: Dict) -> bytes:
        """Format a message for stdio."""
        data = json.dumps(message)
        return f"{data}\n".encode()

    @staticmethod
    def parse_message(line: bytes) -> Dict:
        """Parse a stdio line into a message."""
        try:
            return json.loads(line.decode().strip())
        except json.JSONDecodeError:
            return {
                "type": "raw",
                "data": {"content": line.decode()}
            }
```

## 3. Error Handling

### 3.1 Custom Exceptions

```python
class TransportError(Exception):
    """Base class for transport layer errors."""
    pass

class ConnectionError(TransportError):
    """Raised when connection operations fail."""
    pass

class ProtocolError(TransportError):
    """Raised when protocol violations occur."""
    pass

class ProcessError(TransportError):
    """Raised when process operations fail."""
    pass
```

### 3.2 Error Recovery

```python
class ConnectionManager:
    """Manages connection lifecycle and recovery."""

    def __init__(self, config: TransportConfig):
        self.config = config
        self.backoff = ExponentialBackoff()
        self.circuit_breaker = CircuitBreaker()

    async def connect_with_retry(self, connector: Callable):
        """Connect with retry and circuit breaker."""
        while True:
            try:
                if not self.circuit_breaker.allow_request():
                    raise ConnectionError("Circuit breaker open")

                return await connector()

            except Exception as e:
                self.circuit_breaker.record_failure()
                delay = self.backoff.next_delay()

                if delay is None:
                    raise ConnectionError("Max retries exceeded") from e

                await asyncio.sleep(delay)
```

## 4. Monitoring

### 4.1 Metrics Collection

```python
from dataclasses import dataclass, field
from typing import Dict
import time

@dataclass
class ConnectionMetrics:
    """Metrics for a single connection."""
    total_messages: int = 0
    total_bytes: int = 0
    errors: int = 0
    start_time: float = field(default_factory=time.time)

    @property
    def uptime(self) -> float:
        return time.time() - self.start_time

class MetricsCollector:
    """Collects and exports metrics."""

    def __init__(self):
        self.connections: Dict[str, ConnectionMetrics] = {}
        self._lock = asyncio.Lock()

    async def record_message(
        self,
        connection_id: str,
        size: int,
        is_error: bool = False
    ):
        """Record message metrics."""
        async with self._lock:
            if connection_id not in self.connections:
                self.connections[connection_id] = ConnectionMetrics()

            metrics = self.connections[connection_id]
            metrics.total_messages += 1
            metrics.total_bytes += size
            if is_error:
                metrics.errors += 1
```

### 4.2 Health Checks

```python
from enum import Enum
from typing import Dict, Any

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheck:
    """Health check implementation."""

    def __init__(self, transport_manager: TransportManager):
        self.transport = transport_manager

    async def check_health(self) -> Dict[str, Any]:
        """Perform health check."""
        status = HealthStatus.HEALTHY
        components = {}

        # Check SSE server
        try:
            sse_health = await self.transport.sse_server.check_health()
            components["sse"] = {
                "status": HealthStatus.HEALTHY,
                "details": sse_health
            }
        except Exception as e:
            status = HealthStatus.DEGRADED
            components["sse"] = {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e)
            }

        # Check stdio handler
        try:
            stdio_health = await self.transport.stdio_handler.check_health()
            components["stdio"] = {
                "status": HealthStatus.HEALTHY,
                "details": stdio_health
            }
        except Exception as e:
            status = HealthStatus.DEGRADED
            components["stdio"] = {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e)
            }

        return {
            "status": status,
            "components": components,
            "timestamp": time.time()
        }
```

## 5. Configuration

### 5.1 Environment Configuration

```python
from pydantic import BaseSettings, Field

class TransportSettings(BaseSettings):
    """Environment-based settings."""

    # Server settings
    sse_port: int = Field(8080, env='TRANSPORT_SSE_PORT')
    sse_host: str = Field('127.0.0.1', env='TRANSPORT_SSE_HOST')
    log_level: str = Field('INFO', env='TRANSPORT_LOG_LEVEL')

    # Security settings
    allow_origins: Optional[List[str]] = Field(None, env='TRANSPORT_ALLOW_ORIGINS')
    api_token: Optional[str] = Field(None, env='API_ACCESS_TOKEN')

    # Process settings
    pass_environment: bool = Field(False, env='TRANSPORT_PASS_ENV')
    max_processes: int = Field(10, env='TRANSPORT_MAX_PROCESSES')

    class Config:
        env_prefix = 'TRANSPORT_'
```

### 5.2 Runtime Configuration

```python
@dataclass
class RuntimeConfig:
    """Runtime configuration options."""

    # Connection settings
    connection_timeout: float = 30.0
    max_reconnect_attempts: int = 3
    reconnect_delay: float = 1.0

    # Buffer settings
    max_queue_size: int = 1000
    message_timeout: float = 5.0

    # Protocol settings
    keepalive_interval: float = 30.0
    max_message_size: int = 1024 * 1024  # 1MB
```

## 6. Testing

### 6.1 Unit Tests

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_sse_server():
    """Test SSE server functionality."""
    config = TransportConfig(sse_port=0)  # Random port
    server = SSEServer(config)

    # Test connection handling
    async with server.create_test_client() as client:
        response = await client.get("/sse")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"

    # Test message handling
    message = {"type": "test", "data": {"key": "value"}}
    async with server.create_test_client() as client:
        await client.post("/messages", json=message)

        async with client.stream("GET", "/sse") as stream:
            event = await stream.receive_event()
            assert event.type == "test"
            assert event.data == {"key": "value"}
```

### 6.2 Integration Tests

```python
@pytest.mark.asyncio
async def test_end_to_end():
    """Test end-to-end message flow."""
    config = TransportConfig()
    manager = TransportManager(config)
    await manager.start()

    try:
        # Start test process
        process_id = await manager.stdio_handler.spawn_process(
            "echo",
            ["Hello, World!"]
        )

        # Connect SSE client
        async with manager.sse_server.create_test_client() as client:
            async with client.stream("GET", "/sse") as stream:
                event = await stream.receive_event()
                assert event.type == "process_output"
                assert event.data["content"] == "Hello, World!\n"

    finally:
        await manager.stop()
```

## 7. Deployment

### 7.1 Docker Configuration

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TRANSPORT_SSE_PORT=8080
ENV TRANSPORT_SSE_HOST=0.0.0.0
ENV TRANSPORT_LOG_LEVEL=INFO

EXPOSE 8080

CMD ["python", "-m", "transport"]
```

### 7.2 Kubernetes Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-transport
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-transport
  template:
    metadata:
      labels:
        app: mcp-transport
    spec:
      containers:
        - name: transport
          image: mcp-transport:latest
          ports:
            - containerPort: 8080
          env:
            - name: TRANSPORT_SSE_PORT
              value: '8080'
            - name: TRANSPORT_SSE_HOST
              value: '0.0.0.0'
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
```

## 8. API Documentation

### 8.1 SSE Endpoints

- **GET /sse**

  - Establishes SSE connection
  - Headers:
    - `Accept: text/event-stream`
    - `Authorization: Bearer <token>` (optional)

- **POST /messages**
  - Sends message to SSE clients
  - Body: JSON message object
  - Headers:
    - `Content-Type: application/json`

### 8.2 Message Formats

```json
// Standard message
{
  "type": "message",
  "data": {
    "content": "string",
    "metadata": {}
  }
}

// Process output message
{
  "type": "process_output",
  "process_id": "string",
  "data": {
    "content": "string",
    "stream": "stdout|stderr"
  }
}

// Control message
{
  "type": "control",
  "action": "string",
  "params": {}
}
```

## 9. Future Enhancements

1. **WebSocket Support:**

   - WebSocket server implementation
   - Protocol adapter for WebSocket
   - Bidirectional communication

2. **Advanced Routing:**

   - Message prioritization
   - Content-based routing
   - Load balancing

3. **Security:**

   - TLS termination
   - JWT authentication
   - Rate limiting

4. **Monitoring:**
   - Prometheus metrics
   - Tracing integration
   - Advanced logging
