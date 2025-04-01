"""Integration tests for MCP tool execution."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from chemist_server.mcp_core.registry import ToolRegistry
from chemist_server.mcp_core.router import Router

# Mark all tests as asyncio tests
pytestmark = pytest.mark.asyncio


class MockTool:
    """A simple tool implementation for testing."""

    def __init__(self, name="test_tool", version="1.0.0", schema=None):
        self.name = name
        self.version = version
        self.schema = schema or {
            "type": "object",
            "properties": {"message": {"type": "string"}, "count": {"type": "integer"}},
            "required": ["message"],
        }
        self.calls = []

    async def execute(self, **kwargs):
        """Execute the tool with the given parameters."""
        self.calls.append(kwargs)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Executed {self.name} v{self.version} with params: {json.dumps(kwargs)}",
                }
            ]
        }


class MockAdapter:
    """Mock adapter for testing."""

    def __init__(self, tool):
        self.tool = tool
        self.schema = tool.schema
        self.metadata = {
            "tool_name": tool.name,
            "version": tool.version,
            "adapter_type": "mock",
            "schema": tool.schema,
        }

    async def execute(self, parameters, context=None):
        """Execute the tool with the given parameters."""
        return await self.tool.execute(**parameters)

    async def health_check(self):
        """Return health status."""
        return {"status": "healthy"}


@pytest.fixture
def mock_registry_with_tools():
    """Create a registry with mock tools."""
    # Create a mock instead of a real instance to avoid attribute issues
    registry = MagicMock(spec=ToolRegistry)

    # Create and register some tools
    tools = [
        MockTool("echo", "1.0.0"),
        MockTool(
            "calculator",
            "1.0.0",
            {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                    },
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["operation", "a", "b"],
            },
        ),
        MockTool(
            "translator",
            "1.0.0",
            {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "source_language": {"type": "string"},
                    "target_language": {"type": "string"},
                },
                "required": ["text", "target_language"],
            },
        ),
    ]

    # Mock methods
    registry.execute_tool = AsyncMock()
    registry.get_tool = MagicMock()
    registry.get_metadata = MagicMock()
    registry.get_circuit_breaker = MagicMock()
    registry.list_tools = MagicMock(
        return_value=[
            {"tool_name": tool.name, "version": tool.version} for tool in tools
        ]
    )

    # Set up tool execution mocks
    for tool in tools:
        adapter = MockAdapter(tool)
        # Make execute_tool return the result of adapter.execute when called with the right tool name
        registry.execute_tool.side_effect = (
            lambda **kwargs: adapter.execute(kwargs["parameters"])
            if kwargs["tool_name"] == tool.name
            else None
        )
        # Make get_tool return the adapter when called with the right tool name
        registry.get_tool.side_effect = (
            lambda name, version=None: adapter if name == tool.name else None
        )
        registry.get_metadata.side_effect = (
            lambda name, version=None: adapter.metadata if name == tool.name else None
        )

    return registry, tools


@pytest.fixture
def router_with_tools(mock_registry_with_tools):
    """Create a router with mock tools."""
    registry, tools = mock_registry_with_tools
    router = Router(registry)
    return router, tools


class TestToolExecution:
    """Test cases for tool execution."""

    async def test_route_simple_request(self, router_with_tools):
        """Test routing a simple request."""
        router, tools = router_with_tools

        # Execute the "echo" tool
        result = await router.route_request("echo", {"message": "Hello, world!"})

        # Verify the result contains the expected content
        assert "content" in result
        assert len(result["content"]) > 0
        assert result["content"][0]["type"] == "text"
        assert "Hello, world!" in result["content"][0]["text"]

    async def test_route_calculator_request(self, router_with_tools):
        """Test routing a calculator request."""
        router, tools = router_with_tools

        # Execute the "calculator" tool with add operation
        result = await router.route_request(
            "calculator", {"operation": "add", "a": 5, "b": 3}
        )

        # Verify the result contains the expected content
        assert "content" in result
        assert len(result["content"]) > 0
        assert result["content"][0]["type"] == "text"
        assert "calculator" in result["content"][0]["text"]
        assert "add" in result["content"][0]["text"]
        assert "5" in result["content"][0]["text"]
        assert "3" in result["content"][0]["text"]

    async def test_route_translator_request(self, router_with_tools):
        """Test routing a translator request."""
        router, tools = router_with_tools

        # Execute the "translator" tool
        result = await router.route_request(
            "translator",
            {"text": "Hello", "source_language": "en", "target_language": "es"},
        )

        # Verify the result contains the expected content
        assert "content" in result
        assert len(result["content"]) > 0
        assert result["content"][0]["type"] == "text"
        assert "translator" in result["content"][0]["text"]
        assert "Hello" in result["content"][0]["text"]
        assert "es" in result["content"][0]["text"]

    async def test_list_available_tools(self, router_with_tools):
        """Test listing available tools."""
        router, tools = router_with_tools

        # List available tools
        result = await router.list_available_tools()

        # Verify the result contains all expected tools
        assert len(result) == len(tools)
        tool_names = [tool["tool_name"] for tool in result]
        assert "echo" in tool_names
        assert "calculator" in tool_names
        assert "translator" in tool_names

    async def test_get_tool_metadata(self, router_with_tools, mock_registry_with_tools):
        """Test getting tool metadata."""
        router, tools = router_with_tools
        registry, _ = mock_registry_with_tools

        # Mock the get_metadata method to return a specific metadata
        calculator_tool = next(tool for tool in tools if tool.name == "calculator")
        adapter = MockAdapter(calculator_tool)
        registry.get_metadata.return_value = adapter.metadata

        # Get metadata for the "calculator" tool
        result = await router.get_tool_metadata("calculator")

        # Verify the result contains the expected metadata
        assert result["tool_name"] == "calculator"
        assert result["version"] == "1.0.0"

    async def test_route_request_with_context(self, router_with_tools):
        """Test routing a request with a context."""
        router, tools = router_with_tools

        # Define a context
        context = {"request_id": "test-123", "user_id": "user-456"}

        # Execute the "echo" tool with a context
        result = await router.route_request(
            "echo", {"message": "Hello with context"}, context=context
        )

        # Verify the result contains the expected content
        assert "content" in result
        assert len(result["content"]) > 0
        assert result["content"][0]["type"] == "text"
        assert "Hello with context" in result["content"][0]["text"]

    async def test_route_nonexistent_tool(
        self, router_with_tools, mock_registry_with_tools
    ):
        """Test routing a request to a nonexistent tool."""
        router, tools = router_with_tools
        registry, _ = mock_registry_with_tools

        # Configure the registry to raise an exception for a nonexistent tool
        from chemist_server.mcp_core.errors import AdapterError

        registry.execute_tool.side_effect = AdapterError(
            "Tool not found: nonexistent_tool"
        )

        # Execute a nonexistent tool
        with pytest.raises(AdapterError, match="Tool not found"):
            await router.route_request("nonexistent_tool", {"message": "Should fail"})

    async def test_multiple_tool_requests(self, router_with_tools):
        """Test making multiple tool requests in sequence."""
        router, tools = router_with_tools

        # Make multiple requests
        results = []
        for i in range(3):
            result = await router.route_request("echo", {"message": f"Message {i + 1}"})
            results.append(result)

        # Verify each result
        for i, result in enumerate(results):
            assert "content" in result
            assert len(result["content"]) > 0
            assert result["content"][0]["type"] == "text"
            assert f"Message {i + 1}" in result["content"][0]["text"]

    async def test_nested_tool_calls(self, router_with_tools, mock_registry_with_tools):
        """Test making nested tool calls (one tool calling another)."""
        router, tools = router_with_tools
        registry, _ = mock_registry_with_tools

        # Create a special "nested" tool that calls the echo tool
        nested_tool = MockTool("nested", "1.0.0")
        original_execute = nested_tool.execute

        # Override the execute method to make it call the echo tool first
        async def nested_execute(**kwargs):
            # Call the echo tool
            echo_result = await router.route_request(
                "echo", {"message": f"Echo from nested: {kwargs.get('message', '')}"}
            )
            # Then continue with the original implementation
            result = await original_execute(**kwargs)
            # Combine the results
            result["content"] = echo_result["content"] + result["content"]
            return result

        nested_tool.execute = nested_execute

        # Add the nested tool to the mocks
        adapter = MockAdapter(nested_tool)
        registry.execute_tool.side_effect = (
            lambda **kwargs: adapter.execute(kwargs["parameters"])
            if kwargs["tool_name"] == "nested"
            else registry.execute_tool.side_effect(**kwargs)
        )
        registry.get_tool.side_effect = (
            lambda name, version=None: adapter
            if name == "nested"
            else registry.get_tool.side_effect(name, version)
        )

        # Execute the nested tool
        result = await router.route_request("nested", {"message": "Nested call"})

        # Verify the result contains both the echo and nested results
        assert "content" in result
        assert len(result["content"]) >= 2  # Should have at least 2 content items
        assert any(
            "Echo from nested" in item["text"]
            for item in result["content"]
            if item["type"] == "text"
        )
        assert any(
            "Nested call" in item["text"]
            for item in result["content"]
            if item["type"] == "text"
        )
