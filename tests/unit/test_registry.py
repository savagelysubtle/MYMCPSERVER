"""Unit tests for the ToolRegistry."""

from unittest.mock import MagicMock

import pytest

# Import components to be tested
from chemist_server.mcp_core.adapters.base_adapter import BaseAdapter
from chemist_server.mcp_core.adapters.circuit_breaker import CircuitBreaker
from chemist_server.mcp_core.errors import AdapterError
from chemist_server.mcp_core.registry import ToolMetadata, ToolRegistry

# --- Fixtures ---


@pytest.fixture
def registry() -> ToolRegistry:
    """Provides a fresh ToolRegistry instance for each test."""
    return ToolRegistry()


@pytest.fixture
def mock_adapter() -> MagicMock:
    """Provides a mock BaseAdapter."""
    adapter = MagicMock(spec=BaseAdapter)
    # Set a class name for adapter_type metadata
    adapter.__class__.__name__ = "MockAdapter"
    return adapter


# --- Test Cases ---


def test_register_tool_success(registry: ToolRegistry, mock_adapter: MagicMock):
    """Test successfully registering a new tool."""
    tool_name = "test_tool"
    version = "1.0.0"
    description = "A test tool"
    tags = ["test", "example"]

    registry.register_tool(
        tool_name=tool_name,
        adapter=mock_adapter,
        version=version,
        make_latest=True,
        description=description,
        tags=tags,
        circuit_breaker_threshold=3,  # Example extra metadata
    )

    # Check internal state
    assert tool_name in registry.tools
    assert version in registry.tools[tool_name]
    assert registry.tools[tool_name][version] is mock_adapter
    assert registry.latest_versions[tool_name] == version

    # Check metadata
    assert tool_name in registry.metadata
    assert version in registry.metadata[tool_name]
    metadata = registry.metadata[tool_name][version]
    assert isinstance(metadata, ToolMetadata)
    assert metadata.tool_name == tool_name
    assert metadata.version == version
    assert metadata.adapter_type == "MockAdapter"
    assert metadata.description == description
    assert metadata.tags == set(tags)
    assert metadata.circuit_breaker_threshold == 3

    # Check circuit breaker
    circuit_name = f"{tool_name}:{version}"
    assert circuit_name in registry.circuit_breakers
    assert isinstance(registry.circuit_breakers[circuit_name], CircuitBreaker)
    assert registry.circuit_breakers[circuit_name].failure_threshold == 3


def test_register_tool_duplicate_version_raises_error(
    registry: ToolRegistry, mock_adapter: MagicMock
):
    """Test that registering the same tool version twice raises AdapterError."""
    tool_name = "duplicate_test"
    version = "1.0.0"

    registry.register_tool(tool_name, mock_adapter, version)

    # Attempt to register again
    with pytest.raises(
        AdapterError, match=f"Tool {tool_name} v{version} already registered"
    ):
        registry.register_tool(tool_name, mock_adapter, version)


def test_get_tool_specific_version(registry: ToolRegistry, mock_adapter: MagicMock):
    """Test getting a tool by specific version."""
    tool_name = "versioned_tool"
    version1 = "1.0.0"
    version2 = "1.1.0"
    adapter1 = MagicMock(spec=BaseAdapter)
    adapter2 = mock_adapter  # Use the fixture mock for v2

    registry.register_tool(tool_name, adapter1, version1, make_latest=False)
    registry.register_tool(tool_name, adapter2, version2, make_latest=True)

    retrieved_adapter1 = registry.get_tool(tool_name, version=version1)
    retrieved_adapter2 = registry.get_tool(tool_name, version=version2)

    assert retrieved_adapter1 is adapter1
    assert retrieved_adapter2 is adapter2


def test_get_tool_latest_version(registry: ToolRegistry, mock_adapter: MagicMock):
    """Test getting the latest version of a tool when version is None."""
    tool_name = "latest_tool"
    version1 = "1.0.0"
    version2 = "1.1.0"
    adapter1 = MagicMock(spec=BaseAdapter)
    adapter2 = mock_adapter  # This is the latest

    registry.register_tool(tool_name, adapter1, version1, make_latest=False)
    registry.register_tool(tool_name, adapter2, version2, make_latest=True)

    latest_adapter = registry.get_tool(tool_name)  # version=None implicitly
    assert latest_adapter is adapter2

    # Register an even newer version
    version3 = "2.0.0-beta"
    adapter3 = MagicMock(spec=BaseAdapter)
    registry.register_tool(tool_name, adapter3, version3, make_latest=True)
    latest_adapter_v3 = registry.get_tool(tool_name)
    assert latest_adapter_v3 is adapter3


def test_get_tool_not_found(registry: ToolRegistry):
    """Test getting a non-existent tool raises AdapterError."""
    with pytest.raises(AdapterError, match="Tool non_existent_tool not found"):
        registry.get_tool("non_existent_tool")


def test_get_tool_version_not_found(registry: ToolRegistry, mock_adapter: MagicMock):
    """Test getting a non-existent version of an existing tool raises AdapterError."""
    tool_name = "existing_tool"
    version = "1.0.0"
    registry.register_tool(tool_name, mock_adapter, version)

    with pytest.raises(
        AdapterError, match=f"Version 2.0.0 not found for tool {tool_name}"
    ):
        registry.get_tool(tool_name, version="2.0.0")


def test_get_metadata(registry: ToolRegistry, mock_adapter: MagicMock):
    """Test retrieving metadata for a specific tool version."""
    tool_name = "metadata_tool"
    version = "0.5.0"
    desc = "Tool with specific metadata"
    registry.register_tool(
        tool_name, mock_adapter, version, description=desc, tags=["meta"]
    )

    metadata = registry.get_metadata(tool_name, version)
    latest_metadata = registry.get_metadata(tool_name)

    assert isinstance(metadata, ToolMetadata)
    assert metadata.description == desc
    assert metadata.tags == {"meta"}
    assert metadata.version == version
    assert latest_metadata is metadata  # Since it's the only version


def test_list_tools(registry: ToolRegistry, mock_adapter: MagicMock):
    """Test listing all registered tools."""
    adapter1 = MagicMock(spec=BaseAdapter)
    adapter1.__class__.__name__ = "AdapterA"
    adapter2 = mock_adapter
    adapter2.__class__.__name__ = "AdapterB"

    registry.register_tool("tool_a", adapter1, "1.0", description="Tool A v1")
    registry.register_tool(
        "tool_a", adapter1, "1.1", description="Tool A v1.1", make_latest=True
    )
    registry.register_tool(
        "tool_b", adapter2, "2.0", description="Tool B v2", make_latest=True
    )

    tool_list = registry.list_tools()

    assert len(tool_list) == 3
    # Sort for consistent checking
    tool_list.sort(key=lambda x: (x["tool_name"], x["version"]))

    assert tool_list[0] == {
        "tool_name": "tool_a",
        "version": "1.0",
        "is_latest": False,
        "description": "Tool A v1",
        "adapter_type": "AdapterA",
    }
    assert tool_list[1] == {
        "tool_name": "tool_a",
        "version": "1.1",
        "is_latest": True,
        "description": "Tool A v1.1",
        "adapter_type": "AdapterA",
    }
    assert tool_list[2] == {
        "tool_name": "tool_b",
        "version": "2.0",
        "is_latest": True,
        "description": "Tool B v2",
        "adapter_type": "AdapterB",
    }


def test_list_versions(registry: ToolRegistry, mock_adapter: MagicMock):
    """Test listing versions for a specific tool."""
    tool_name = "multi_version_tool"
    registry.register_tool(tool_name, mock_adapter, "1.0")
    registry.register_tool(tool_name, mock_adapter, "0.9-beta")
    registry.register_tool(tool_name, mock_adapter, "1.1")

    versions = registry.list_versions(tool_name)
    assert sorted(versions) == sorted(["1.0", "0.9-beta", "1.1"])


def test_list_versions_tool_not_found(registry: ToolRegistry):
    """Test listing versions for a non-existent tool raises AdapterError."""
    with pytest.raises(AdapterError, match="Tool not_a_tool not found"):
        registry.list_versions("not_a_tool")


def test_get_circuit_breaker(registry: ToolRegistry, mock_adapter: MagicMock):
    """Test retrieving the circuit breaker for a tool."""
    tool_name = "cb_tool"
    version = "1.0"
    registry.register_tool(
        tool_name, mock_adapter, version, circuit_breaker_threshold=10
    )

    cb = registry.get_circuit_breaker(tool_name, version)
    assert isinstance(cb, CircuitBreaker)
    assert cb.failure_threshold == 10

    latest_cb = registry.get_circuit_breaker(tool_name)  # Get latest
    assert latest_cb is cb


def test_get_circuit_breaker_not_found(registry: ToolRegistry):
    """Test getting circuit breaker for a non-existent tool/version raises AdapterError."""
    with pytest.raises(AdapterError, match="No versions found for tool no_cb_tool"):
        registry.get_circuit_breaker("no_cb_tool")

    registry.register_tool("cb_exists", MagicMock(spec=BaseAdapter), "1.0")
    with pytest.raises(
        AdapterError, match="Circuit breaker not found for cb_exists v2.0"
    ):
        registry.get_circuit_breaker("cb_exists", version="2.0")
