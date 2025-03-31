"""Configuration for pytest with mocks for MCP components."""

import sys
from unittest.mock import MagicMock

import pytest


# Mock MCP core components that might be missing during tests
class MockHealthCheck:
    """Mock HealthCheck base class."""

    async def check_health(self):
        """Mock health check method."""
        return {"status": "healthy"}


class MockHealthStatus:
    """Mock HealthStatus enum."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class MockLogger:
    """Mock logger."""

    def __init__(self):
        self.logs = []

    def info(self, message, **kwargs):
        """Log info message."""
        self.logs.append({"level": "info", "message": message, "kwargs": kwargs})

    def error(self, message, **kwargs):
        """Log error message."""
        self.logs.append({"level": "error", "message": message, "kwargs": kwargs})

    def warning(self, message, **kwargs):
        """Log warning message."""
        self.logs.append({"level": "warning", "message": message, "kwargs": kwargs})

    def debug(self, message, **kwargs):
        """Log debug message."""
        self.logs.append({"level": "debug", "message": message, "kwargs": kwargs})


# Create module mocks
mock_mcp_core = MagicMock()
mock_mcp_core.HealthCheck = MockHealthCheck
mock_mcp_core.HealthStatus = MockHealthStatus
mock_mcp_core.logger = MockLogger()

mock_mcp = MagicMock()


class MockToolContext:
    """Mock ToolContext class for testing."""

    def __init__(self, **kwargs):
        self.params = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)


mock_mcp.ToolContext = MockToolContext


# Add mock modules to sys.modules before imports
sys.modules["mcp_core"] = mock_mcp_core
sys.modules["mcp"] = mock_mcp


@pytest.fixture
def mock_health_components():
    """Fixture to provide access to mock health components."""
    return {
        "HealthCheck": MockHealthCheck,
        "HealthStatus": MockHealthStatus,
        "logger": MockLogger(),
    }


@pytest.fixture
def mock_tool_context():
    """Fixture to provide a mock tool context."""

    def _create_context(**kwargs):
        return MockToolContext(**kwargs)

    return _create_context
