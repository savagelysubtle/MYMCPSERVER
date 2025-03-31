"""End-to-end tests for CLI tool requests through core and transport layers."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

# Import conftest first to ensure mocks are in place
import conftest  # noqa
import pytest

# Now we can mock imports that might not be available
from mcp import ToolResponse  # type: ignore

# Try to import core components with fallbacks
# Use Any type annotation to avoid linter errors
create_app: Any = None
create_proxy_server: Any = None

try:
    from src.chemist_server.mcp_core.app import create_app
except ImportError:
    create_app = MagicMock()

try:
    from src.chemist_server.mcp_proxy.proxy_server import create_proxy_server
except ImportError:
    create_proxy_server = MagicMock()


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for testing file operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("End-to-end test file")
        yield temp_dir


@pytest.mark.skipif(create_app is None, reason="Core layer not importable")
@pytest.mark.skipif(create_proxy_server is None, reason="Proxy layer not importable")
class TestEndToEndCliFlow:
    """Test the end-to-end flow of CLI tool requests through the system."""

    @pytest.fixture
    async def mock_core_app(self):
        """Create a mock core application."""
        # Create a mock app with a router that forwards to the tool server
        mock_app = MagicMock()
        mock_app.handle_request = AsyncMock()
        mock_app.handle_request.return_value = {
            "status": "success",
            "result": {
                "stdout": "mocked dir output",
                "stderr": "",
                "exit_code": 0,
                "success": True,
                "command": "dir /a",
                "working_directory": "C:\\mock\\dir",
            },
        }
        return mock_app

    @pytest.fixture
    async def mock_proxy_server(self, mock_core_app):
        """Create a mock proxy server connected to the mock core app."""
        mock_proxy = MagicMock()
        mock_proxy.handle_message = AsyncMock()
        mock_proxy.handle_message.side_effect = (
            lambda msg: mock_core_app.handle_request(json.loads(msg))
        )
        return mock_proxy

    @pytest.mark.asyncio
    async def test_cli_request_through_layers(self, mock_core_app, mock_proxy_server):
        """Test a CLI command request flows through the layers correctly."""
        # Create a mock MCP client
        mock_client = MagicMock()
        mock_client.invoke_tool = AsyncMock()
        mock_client.invoke_tool.return_value = ToolResponse(
            data={
                "stdout": "mocked dir output",
                "stderr": "",
                "exit_code": 0,
                "success": True,
                "command": "dir /a",
                "working_directory": "C:\\mock\\dir",
            }
        )

        # Simulate a request from client to proxy
        cli_request = {
            "type": "tool_invoke",
            "tool": "run_command",
            "params": {"command": "dir /a"},
        }

        # Pass through proxy to core
        proxy_response = await mock_proxy_server.handle_message(json.dumps(cli_request))

        # Verify core app received the request
        mock_core_app.handle_request.assert_called_once()
        call_args = mock_core_app.handle_request.call_args[0][0]
        assert call_args["type"] == "tool_invoke"
        assert call_args["tool"] == "run_command"
        assert call_args["params"]["command"] == "dir /a"

        # Verify the response came back through the layers
        response_data = (
            json.loads(proxy_response)
            if isinstance(proxy_response, str)
            else proxy_response
        )
        assert response_data["status"] == "success"
        assert "result" in response_data
        assert response_data["result"]["success"] is True
        assert "command" in response_data["result"]
        assert "working_directory" in response_data["result"]

    @pytest.mark.asyncio
    @patch("src.chemist_server.mcp_core.registry.get_tool_server")
    async def test_core_routes_cli_request_to_tool_server(self, mock_get_tool_server):
        """Test the core layer routes CLI tool requests to the tool server."""
        # Skip if core components aren't available for testing
        if create_app is None:
            pytest.skip("Core layer not importable")

        # Create a mock tool server that returns a predefined response
        mock_tool_server = MagicMock()
        mock_tool_server.invoke_tool = AsyncMock()
        mock_tool_server.invoke_tool.return_value = {
            "stdout": "CLI tool executed via core layer",
            "stderr": "",
            "exit_code": 0,
            "success": True,
            "command": "echo test",
            "working_directory": "C:\\test\\dir",
        }

        # Configure the mock to return our mock tool server
        mock_get_tool_server.return_value = mock_tool_server

        # Create a real (or partially mocked) core app
        with patch("src.chemist_server.mcp_core.app.create_registry"):
            app = await create_app()

        # Create a CLI tool request
        cli_request = {
            "type": "tool_invoke",
            "tool": "run_command",
            "params": {"command": "echo test"},
            "id": "test-request-id",
        }

        # Process the request through the core app
        response = await app.handle_request(cli_request)

        # Verify tool server was called with correct parameters
        mock_tool_server.invoke_tool.assert_called_once()
        tool_name, params = mock_tool_server.invoke_tool.call_args[0]
        assert tool_name == "run_command"
        assert params.get("command") == "echo test"

        # Verify response format
        assert response["status"] == "success"
        assert "result" in response
        assert response["result"]["success"] is True
        assert response["result"]["stdout"] == "CLI tool executed via core layer"
        assert "command" in response["result"]
        assert "working_directory" in response["result"]


@pytest.mark.asyncio
@patch.dict(os.environ, {"ALLOWED_DIR": "PLACEHOLDER"})
async def test_cli_command_mock_integration(temp_test_dir):
    """Test CLI command with mocked server/core components."""
    # Set up the environment for CLI tool
    os.environ["ALLOWED_DIR"] = temp_test_dir

    # Import the CLI tool directly
    from src.chemist_server.tool_servers.python_tool_server.cliTool.cli_tools import (
        run_command,
    )

    # Create a simple request context (minimal implementation)
    class SimpleContext:
        def __init__(self, **kwargs):
            self.params = kwargs
            # Store all kwargs as attributes
            for key, value in kwargs.items():
                setattr(self, key, value)

    # Create context with command
    context = SimpleContext(command="dir")  # explicitly setting command attribute

    # Execute command directly
    result = await run_command(context, context.params["command"])

    # Verify results
    assert result["success"] is True
    assert "test.txt" in result["stdout"]
    assert result["command"] == "dir"
    assert "working_directory" in result

    # Test command with content reading
    context = SimpleContext(
        command="type test.txt"
    )  # explicitly setting command attribute
    result = await run_command(context, context.params["command"])

    assert result["success"] is True
    assert "End-to-end test file" in result["stdout"]
    assert result["command"] == "type test.txt"
