"""Integration tests for app initialization and startup process."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chemist_server.config import AppConfig
from chemist_server.mcp_core.app import get_fastmcp_app

# Mark all tests as asyncio tests
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    config = MagicMock(spec=AppConfig)

    # Set default values
    config.transport = "stdio"
    config.get_core_host = MagicMock(return_value="localhost")
    config.get_core_port = MagicMock(return_value=8000)
    config.logs_path = "/tmp/test_logs"
    config.components = "all"
    config.debug = True
    config.tool_servers = {
        "python": {
            "enabled": True,
            "host": "localhost",
            "port": 8001,
            "path": "/tools/python",
        }
    }
    config.core = {
        "host": "localhost",
        "port": 8000,
        "debug": True,
        "auth_token": "test_token",
    }

    return config


class TestAppStartup:
    """Test cases for app startup and initialization."""

    @pytest.mark.parametrize("transport", ["stdio", "sse", "http"])
    async def test_app_initialization_with_transport(self, mock_config, transport):
        """Test app initialization with different transports."""
        # Set the transport
        mock_config.transport = transport

        # Mock the FastMCP class to avoid actual server startup
        mock_fastmcp = MagicMock()
        mock_fastmcp.initialize = AsyncMock()

        with patch("chemist_server.mcp_core.app.FastMCP", return_value=mock_fastmcp):
            # Call the function to get the app
            app = get_fastmcp_app(mock_config)

            # Verify the app was created with the correct configuration
            assert app == mock_fastmcp
            # Verify the app was initialized
            mock_fastmcp.initialize.assert_called_once()

    async def test_app_registers_health_checks(self, mock_config):
        """Test that the app registers health checks during initialization."""
        # Mock the FastMCP class
        mock_fastmcp = MagicMock()
        mock_fastmcp.initialize = AsyncMock()
        mock_fastmcp.register_health_check = MagicMock()

        with patch("chemist_server.mcp_core.app.FastMCP", return_value=mock_fastmcp):
            # Call the function to get the app
            app = get_fastmcp_app(mock_config)

            # Verify health checks were registered
            # The actual number depends on the implementation
            assert mock_fastmcp.register_health_check.call_count > 0

    async def test_app_registers_tools(self, mock_config):
        """Test that the app registers tools during initialization."""
        # Mock the FastMCP class
        mock_fastmcp = MagicMock()
        mock_fastmcp.initialize = AsyncMock()
        mock_fastmcp.register_tool = MagicMock()

        # Mock the tool registration process
        with (
            patch("chemist_server.mcp_core.app.FastMCP", return_value=mock_fastmcp),
            patch(
                "chemist_server.mcp_core.app.register_core_tools"
            ) as mock_register_tools,
        ):
            # Call the function to get the app
            app = get_fastmcp_app(mock_config)

            # Verify tools were registered
            mock_register_tools.assert_called_once_with(mock_fastmcp, mock_config)

    async def test_initialization_with_python_tool_server_enabled(self, mock_config):
        """Test initialization with Python tool server enabled."""
        # Ensure Python tool server is enabled
        mock_config.tool_servers["python"]["enabled"] = True

        # Mock the FastMCP class
        mock_fastmcp = MagicMock()
        mock_fastmcp.initialize = AsyncMock()

        # Mock the tool server setup
        with (
            patch("chemist_server.mcp_core.app.FastMCP", return_value=mock_fastmcp),
            patch(
                "chemist_server.mcp_core.app.setup_python_tool_server"
            ) as mock_setup_python,
        ):
            # Call the function to get the app
            app = get_fastmcp_app(mock_config)

            # Verify Python tool server was set up
            mock_setup_python.assert_called_once_with(mock_fastmcp, mock_config)

    async def test_initialization_with_python_tool_server_disabled(self, mock_config):
        """Test initialization with Python tool server disabled."""
        # Disable Python tool server
        mock_config.tool_servers["python"]["enabled"] = False

        # Mock the FastMCP class
        mock_fastmcp = MagicMock()
        mock_fastmcp.initialize = AsyncMock()

        # Mock the tool server setup
        with (
            patch("chemist_server.mcp_core.app.FastMCP", return_value=mock_fastmcp),
            patch(
                "chemist_server.mcp_core.app.setup_python_tool_server"
            ) as mock_setup_python,
        ):
            # Call the function to get the app
            app = get_fastmcp_app(mock_config)

            # Verify Python tool server was not set up
            mock_setup_python.assert_not_called()


class TestAppRuntime:
    """Test cases for app runtime behavior."""

    async def test_app_stdio_transport_lifecycle(self, mock_config):
        """Test app lifecycle with stdio transport."""
        # Set the transport to stdio
        mock_config.transport = "stdio"

        # Mock the FastMCP class
        mock_fastmcp = MagicMock()
        mock_fastmcp.initialize = AsyncMock()
        mock_fastmcp.run_stdio_async = AsyncMock()
        mock_fastmcp.shutdown = AsyncMock()

        with patch("chemist_server.mcp_core.app.FastMCP", return_value=mock_fastmcp):
            # Get the app
            app = get_fastmcp_app(mock_config)

            # Run the app
            try:
                # Create a task to run the app
                task = asyncio.create_task(app.run_stdio_async())

                # Allow some time for the app to start
                await asyncio.sleep(0.1)

                # Cancel the task to simulate shutdown
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            finally:
                # Verify the app was started and potentially shut down
                mock_fastmcp.run_stdio_async.assert_called_once()

    async def test_app_sse_transport_lifecycle(self, mock_config):
        """Test app lifecycle with SSE transport."""
        # Set the transport to SSE
        mock_config.transport = "sse"

        # Mock the FastMCP class
        mock_fastmcp = MagicMock()
        mock_fastmcp.initialize = AsyncMock()
        mock_fastmcp.run_sse_async = AsyncMock()
        mock_fastmcp.shutdown = AsyncMock()

        with patch("chemist_server.mcp_core.app.FastMCP", return_value=mock_fastmcp):
            # Get the app
            app = get_fastmcp_app(mock_config)

            # Run the app
            try:
                # Create a task to run the app
                task = asyncio.create_task(app.run_sse_async())

                # Allow some time for the app to start
                await asyncio.sleep(0.1)

                # Cancel the task to simulate shutdown
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            finally:
                # Verify the app was started and potentially shut down
                mock_fastmcp.run_sse_async.assert_called_once()


class TestToolRegistration:
    """Test cases for tool registration and management."""

    async def test_core_tools_registration(self, mock_config):
        """Test registration of core tools."""
        # Mock the FastMCP class
        mock_fastmcp = MagicMock()
        mock_fastmcp.initialize = AsyncMock()
        mock_fastmcp.register_tool = MagicMock()

        # Get the list of core tools to verify registration
        with (
            patch("chemist_server.mcp_core.app.FastMCP", return_value=mock_fastmcp),
            patch(
                "chemist_server.mcp_core.app.register_core_tools"
            ) as mock_register_tools,
        ):
            # Call the function to get the app
            app = get_fastmcp_app(mock_config)

            # Verify core tools were registered
            mock_register_tools.assert_called_once_with(mock_fastmcp, mock_config)

    async def test_tool_registration_with_errors(self, mock_config):
        """Test handling of tool registration errors."""
        # Mock the FastMCP class
        mock_fastmcp = MagicMock()
        mock_fastmcp.initialize = AsyncMock()
        mock_fastmcp.register_tool = MagicMock(
            side_effect=ValueError("Tool registration error")
        )

        # Mock the tool registration with an error
        with (
            patch("chemist_server.mcp_core.app.FastMCP", return_value=mock_fastmcp),
            patch("chemist_server.mcp_core.app.logger") as mock_logger,
            patch(
                "chemist_server.mcp_core.app.register_core_tools",
                side_effect=ValueError("Tool registration error"),
            ),
        ):
            # Call the function to get the app, which should handle the error
            app = get_fastmcp_app(mock_config)

            # Verify the error was logged
            mock_logger.error.assert_called()
            # App should still be returned despite errors
            assert app == mock_fastmcp
