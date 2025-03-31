"""Tests for the integration between the Python Tool Server and CLI tools."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

# Import conftest first to ensure mocks are in place
import conftest  # noqa
import pytest

# Now we can use the ToolContext from our mocked mcp module
from mcp import ToolContext

# Import server initialization and CLI tool functions
from src.chemist_server.tool_servers.python_tool_server.cliTool.cli_tools import (
    run_command,
    show_security_rules,
)
from src.chemist_server.tool_servers.python_tool_server.server import server


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Server integration test file")
        yield temp_dir


class TestServerCliIntegration:
    """Tests for the server's integration with CLI tools."""

    def test_cli_tools_registered(self):
        """Test that CLI tools are registered with the server."""
        # Check if the CLI tools are in the server's registered tools
        assert "run_command" in server.tools
        assert "show_security_rules" in server.tools

        # Verify the registered functions match our expected functions
        assert server.tools["run_command"] == run_command
        assert server.tools["show_security_rules"] == show_security_rules

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"ALLOWED_DIR": "PLACEHOLDER"})
    async def test_server_invokes_cli_tool(self, temp_test_dir):
        """Test that the server can properly invoke the CLI tool."""
        # Set the allowed directory for the CLI tool
        os.environ["ALLOWED_DIR"] = temp_test_dir

        # Create a mock tool context with parameters for run_command
        context = ToolContext(command="dir")

        # Get the run_command function from the server
        server_run_command = server.tools["run_command"]

        # Invoke the function through the server
        result = await server_run_command(context)

        # Verify the result
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is True
        assert "test.txt" in result["stdout"]
        assert "command" in result
        assert result["command"] == "dir"
        assert "working_directory" in result

    @pytest.mark.asyncio
    async def test_server_handles_cli_tool_errors(self):
        """Test that the server properly handles errors from the CLI tool."""
        # Create a mock tool context with an invalid command
        context = ToolContext(command="invalid_command")

        # Get the run_command function from the server
        server_run_command = server.tools["run_command"]

        # Invoke the function through the server
        result = await server_run_command(context)

        # Verify the error is handled correctly
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        assert "command" in result
        assert result["command"] == "invalid_command"

    @pytest.mark.asyncio
    async def test_server_invokes_show_security_rules(self):
        """Test that the server can properly invoke the show_security_rules tool."""
        # Get the show_security_rules function from the server
        server_show_rules = server.tools["show_security_rules"]

        # Create an empty context (no parameters needed)
        context = ToolContext()

        # Invoke the function through the server
        result = await server_show_rules(context)

        # Verify the result
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is True
        assert "security_rules" in result
        assert "working_directory" in result["security_rules"]
        assert "platform_specific" in result


class TestServerHealth:
    """Tests for the server's health check with CLI tools."""

    @pytest.mark.asyncio
    async def test_health_check_includes_cli_tools(self):
        """Test that the health check includes CLI tools."""
        # Get the health check function
        health_check = server.tools.get("health")

        if not health_check:
            pytest.skip("Health check tool not registered with server")

        # Create a context for the health check
        context = ToolContext()

        # Invoke the health check
        result = await health_check(context)

        # Verify CLI tools are included in the registered tools
        assert "status" in result
        assert "registered_tools" in result
        assert "run_command" in result["registered_tools"]
        assert "show_security_rules" in result["registered_tools"]
