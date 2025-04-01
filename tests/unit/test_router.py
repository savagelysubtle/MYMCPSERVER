"""Unit tests for the Router component."""

import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from chemist_server.mcp_core.errors import AdapterError, CircuitBreakerError
from chemist_server.mcp_core.registry import ToolMetadata, ToolRegistry
from chemist_server.mcp_core.router import Router

# Mark all tests as asyncio tests
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_tool_registry():
    """Fixture to create a mock tool registry."""
    registry = MagicMock(spec=ToolRegistry)

    # Mock list_tools and get_metadata with realistic returns
    current_time = time.time()  # Use float timestamp
    sample_metadata = ToolMetadata(
        tool_name="test_tool",
        version="1.0.0",
        adapter_type="python",
        description="Test tool for unit tests",
        created_at=current_time,
        updated_at=current_time,
        is_active=True,
        tags={"test", "unit-test"},
        circuit_breaker_enabled=True,
        health_check_interval=60,
    )

    registry.list_tools.return_value = [
        {
            "tool_name": "test_tool",
            "version": "1.0.0",
            "description": "Test tool for unit tests",
            "adapter_type": "python",
        }
    ]

    registry.get_metadata.return_value = sample_metadata

    # Mock execute_tool
    registry.execute_tool = AsyncMock(return_value={"result": "success"})

    # Mock adapter and circuit breaker
    mock_adapter = MagicMock()
    mock_adapter.health_check = AsyncMock(return_value={"status": "healthy"})

    registry.get_tool.return_value = mock_adapter

    mock_circuit_breaker = MagicMock()
    mock_circuit_breaker.get_state.return_value = {
        "state": "closed",
        "failure_count": 0,
        "last_failure_time": None,
    }

    registry.get_circuit_breaker.return_value = mock_circuit_breaker
    registry.latest_versions = {"test_tool": "1.0.0"}

    return registry


@pytest.fixture
def router(mock_tool_registry):
    """Fixture to create a Router instance with mocked dependencies."""
    return Router(mock_tool_registry)


class TestRouter:
    """Test cases for the Router class."""

    async def test_init(self, mock_tool_registry):
        """Test the Router initialization."""
        router = Router(mock_tool_registry)
        assert router.registry == mock_tool_registry

    async def test_route_request_success(self, router, mock_tool_registry):
        """Test successful request routing."""
        # Arrange
        tool_name = "test_tool"
        parameters = {"param1": "value1"}

        # Act
        result = await router.route_request(tool_name, parameters)

        # Assert
        assert result == {"result": "success"}
        mock_tool_registry.execute_tool.assert_called_once_with(
            tool_name=tool_name,
            parameters=parameters,
            context=None,
            version=None,
            use_circuit_breaker=True,
        )

    async def test_route_request_with_context(self, router, mock_tool_registry):
        """Test request routing with context."""
        # Arrange
        tool_name = "test_tool"
        parameters = {"param1": "value1"}
        context = {"request_id": "test-123"}

        # Act
        result = await router.route_request(tool_name, parameters, context=context)

        # Assert
        assert result == {"result": "success"}
        mock_tool_registry.execute_tool.assert_called_once_with(
            tool_name=tool_name,
            parameters=parameters,
            context=context,
            version=None,
            use_circuit_breaker=True,
        )

    async def test_route_request_with_version(self, router, mock_tool_registry):
        """Test request routing with specific version."""
        # Arrange
        tool_name = "test_tool"
        parameters = {"param1": "value1"}
        version = "2.0.0"

        # Act
        result = await router.route_request(tool_name, parameters, version=version)

        # Assert
        assert result == {"result": "success"}
        mock_tool_registry.execute_tool.assert_called_once_with(
            tool_name=tool_name,
            parameters=parameters,
            context=None,
            version=version,
            use_circuit_breaker=True,
        )

    async def test_route_request_no_circuit_breaker(self, router, mock_tool_registry):
        """Test request routing with circuit breaker disabled."""
        # Arrange
        tool_name = "test_tool"
        parameters = {"param1": "value1"}

        # Act
        result = await router.route_request(
            tool_name, parameters, use_circuit_breaker=False
        )

        # Assert
        assert result == {"result": "success"}
        mock_tool_registry.execute_tool.assert_called_once_with(
            tool_name=tool_name,
            parameters=parameters,
            context=None,
            version=None,
            use_circuit_breaker=False,
        )

    async def test_route_request_adapter_error(self, router, mock_tool_registry):
        """Test request routing with adapter error."""
        # Arrange
        tool_name = "test_tool"
        parameters = {"param1": "value1"}
        mock_tool_registry.execute_tool.side_effect = AdapterError("Adapter not found")

        # Act/Assert
        with pytest.raises(AdapterError, match="Adapter not found"):
            await router.route_request(tool_name, parameters)

    async def test_route_request_circuit_breaker_error(
        self, router, mock_tool_registry
    ):
        """Test request routing with circuit breaker error."""
        # Arrange
        tool_name = "test_tool"
        parameters = {"param1": "value1"}
        mock_tool_registry.execute_tool.side_effect = CircuitBreakerError(
            "Circuit open"
        )

        # Act/Assert
        with pytest.raises(CircuitBreakerError, match="Circuit open"):
            await router.route_request(tool_name, parameters)

    async def test_list_available_tools(self, router, mock_tool_registry):
        """Test listing available tools."""
        # Act
        tools = await router.list_available_tools()

        # Assert
        assert tools == [
            {
                "tool_name": "test_tool",
                "version": "1.0.0",
                "description": "Test tool for unit tests",
                "adapter_type": "python",
            }
        ]
        mock_tool_registry.list_tools.assert_called_once()

    async def test_get_tool_metadata(self, router, mock_tool_registry):
        """Test getting tool metadata."""
        # Arrange
        tool_name = "test_tool"

        # Act
        metadata = await router.get_tool_metadata(tool_name)

        # Assert
        assert metadata["tool_name"] == "test_tool"
        assert metadata["version"] == "1.0.0"
        assert metadata["adapter_type"] == "python"
        assert metadata["description"] == "Test tool for unit tests"
        assert metadata["is_active"] is True
        assert metadata["tags"] == ["test", "unit-test"]
        assert metadata["circuit_breaker_enabled"] is True
        assert metadata["health_check_interval"] == 60
        mock_tool_registry.get_metadata.assert_called_once_with(tool_name, None)

    async def test_get_tool_metadata_with_version(self, router, mock_tool_registry):
        """Test getting tool metadata with specific version."""
        # Arrange
        tool_name = "test_tool"
        version = "2.0.0"

        # Act
        metadata = await router.get_tool_metadata(tool_name, version)

        # Assert
        assert metadata["tool_name"] == "test_tool"
        assert metadata["version"] == "1.0.0"  # From mock
        mock_tool_registry.get_metadata.assert_called_once_with(tool_name, version)

    async def test_get_tool_health(self, router, mock_tool_registry):
        """Test getting tool health."""
        # Arrange
        tool_name = "test_tool"

        # Act
        health = await router.get_tool_health(tool_name)

        # Assert
        assert health["tool_name"] == "test_tool"
        assert health["version"] == "1.0.0"
        assert health["status"] == "healthy"
        assert health["circuit_state"] == "closed"
        assert health["failure_count"] == 0
        assert health["last_failure_time"] is None
        mock_tool_registry.get_tool.assert_called_once_with(tool_name, None)
        mock_tool_registry.get_circuit_breaker.assert_called_once_with(tool_name, None)

    async def test_get_tool_health_error(self, router, mock_tool_registry):
        """Test getting tool health with an error."""
        # Arrange
        tool_name = "test_tool"
        mock_tool_registry.get_tool.side_effect = AdapterError("Tool not found")

        # Act
        health = await router.get_tool_health(tool_name)

        # Assert
        assert health["tool_name"] == "test_tool"
        assert health["status"] == "error"
        assert "error" in health
        assert "Tool not found" in health["error"]
