"""Testing fixtures for the MCP system."""

import asyncio
import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock

import pytest


@dataclass
class MockToolParams:
    """Mock parameters for a tool call."""

    tool_name: str
    params: dict[str, Any]
    request_id: str = "test-request-id"


@dataclass
class MockToolResponse:
    """Mock response from a tool call."""

    content: list[dict[str, Any]]
    is_error: bool = False
    is_partial: bool = False


class MockToolRequest:
    """Simulates an MCP tool request for testing."""

    def __init__(
        self,
        tool_name: str,
        params: dict[str, Any],
        request_id: str = "test-request-id",
    ):
        self.tool_name = tool_name
        self.params = params
        self.request_id = request_id

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary suitable for JSON serialization."""
        return {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {"name": self.tool_name, "parameters": self.params},
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class MockMcpResponse:
    """Simulates an MCP response for testing."""

    def __init__(
        self,
        content: list[dict[str, Any]],
        is_error: bool = False,
        is_partial: bool = False,
        request_id: str = "test-request-id",
    ):
        self.content = content
        self.is_error = is_error
        self.is_partial = is_partial
        self.request_id = request_id

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary suitable for JSON serialization."""
        return {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "result": {
                "content": self.content,
                "isError": self.is_error,
                "isPartial": self.is_partial,
            },
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@pytest.fixture
def mock_mcp_request():
    """Fixture to create mock MCP tool requests."""

    def _create_request(
        tool_name: str, params: dict[str, Any], request_id: str = "test-request-id"
    ):
        return MockToolRequest(tool_name, params, request_id)

    return _create_request


@pytest.fixture
def mock_mcp_response():
    """Fixture to create mock MCP responses."""

    def _create_response(
        content: list[dict[str, Any]],
        is_error: bool = False,
        is_partial: bool = False,
        request_id: str = "test-request-id",
    ):
        return MockMcpResponse(content, is_error, is_partial, request_id)

    return _create_response


class MockStreamResponse:
    """Mock for a streaming response."""

    def __init__(self, responses: list[dict[str, Any]]):
        self.responses = responses
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.responses):
            raise StopAsyncIteration

        response = self.responses[self.index]
        self.index += 1

        # Simulate some async delay
        await asyncio.sleep(0.01)

        return json.dumps(response)


@pytest.fixture
def mock_stream_response():
    """Fixture to create mock streaming responses."""

    def _create_stream(responses: list[dict[str, Any]]):
        return MockStreamResponse(responses)

    return _create_stream


class MockMcpClient:
    """Mock MCP client for testing tool interactions."""

    def __init__(self):
        self.tools = {}
        self.responses = {}
        self.last_call: MockToolParams | None = None

    def register_tool(self, tool_name: str, handler: Callable):
        """Register a tool handler."""
        self.tools[tool_name] = handler

    def register_response(
        self, tool_name: str, response: dict[str, Any] | list[dict[str, Any]]
    ):
        """Register a pre-defined response for a tool."""
        if isinstance(response, list):
            self.responses[tool_name] = response
        else:
            self.responses[tool_name] = [response]

    async def call_tool(
        self,
        tool_name: str,
        params: dict[str, Any],
        request_id: str = "test-request-id",
    ):
        """Call a registered tool or return a pre-defined response."""
        self.last_call = MockToolParams(tool_name, params, request_id)

        if tool_name in self.responses:
            response = self.responses[tool_name]
            if isinstance(response, list):
                if len(response) == 1:
                    return response[0]
                else:
                    return MockStreamResponse(response)
            return response

        if tool_name in self.tools:
            handler = self.tools[tool_name]
            context = MagicMock()
            context.request_id = request_id
            return await handler(context, **params)

        # Tool not found
        return {
            "content": [{"type": "text", "text": f"Tool {tool_name} not found"}],
            "isError": True,
            "isPartial": False,
        }


@pytest.fixture
def mock_mcp_client():
    """Fixture to create a mock MCP client."""
    return MockMcpClient()
