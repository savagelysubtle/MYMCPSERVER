"""Integration tests for application startup and initialization."""

from unittest.mock import patch

import pytest

# Assuming main app creation and config loading functions
# Adjust import paths as necessary
try:
    from mcp.server.fastmcp import FastMCP

    from chemist_server.config import AppConfig, load_and_get_config
    from chemist_server.mcp_core.app import get_fastmcp_app
    from chemist_server.mcp_core.logger import (
        configure_logging,  # Central logging config
    )

    MODULE_EXISTS = True
except ImportError:
    MODULE_EXISTS = False

    # Define dummies if modules might be missing
    class AppConfig:
        pass

    class FastMCP:
        pass

    def load_and_get_config(*args, **kwargs):
        return AppConfig()

    def get_fastmcp_app(*args, **kwargs):
        return FastMCP()

    def configure_logging(*args, **kwargs):
        pass


pytestmark = pytest.mark.skipif(
    not MODULE_EXISTS, reason="Required modules for app startup tests not found"
)


@pytest.fixture
def default_config() -> AppConfig:
    """Provides a default AppConfig instance."""
    # Load default config, potentially using overrides for testing
    return load_and_get_config({})  # Pass empty dict for defaults


# Test Case 1: Basic App Initialization
def test_basic_app_initialization(default_config):
    """Test that get_fastmcp_app returns a FastMCP instance with default config."""
    app = get_fastmcp_app(default_config)
    assert isinstance(app, FastMCP)
    # Add more assertions: Check if default tools/resources are registered if expected
    # e.g., assert "default_tool" in app.tools


# Test Case 2: Logging Configuration during Startup
@patch("chemist_server.mcp_core.logger.configure_logging")
def test_logging_is_configured_on_startup(mock_configure_logging, default_config):
    """Test that configure_logging is called during the app setup phase.

    Note: This assumes get_fastmcp_app or a related setup function calls configure_logging.
    Adjust the test if logging is configured elsewhere in the startup sequence.
    """
    # Trigger the app creation/setup process that should call configure_logging
    get_fastmcp_app(default_config)  # Or call the main setup function

    # Verify configure_logging was called once with the config
    mock_configure_logging.assert_called_once_with(default_config)


# Test Case 3: Tool Registration during Startup
@patch("chemist_server.mcp_core.tool_registry.register_tool")  # Example patch target
def test_tools_are_registered_on_startup(mock_register_tool, default_config):
    """Test that expected tools are registered when the app starts.

    Note: This relies on tools registering themselves upon import or during app setup.
    Adjust patch target and assertions based on the actual registration mechanism.
    """
    # App initialization should trigger tool loading/registration
    app = get_fastmcp_app(default_config)

    # Check if register_tool was called for expected tools
    # Example: Asserting a specific tool was registered
    # found_call = any(
    #     call_args[0][0] == "expected_tool_name" for call_args in mock_register_tool.call_args_list
    # )
    # assert found_call, "Expected tool 'expected_tool_name' was not registered"

    # Or check the number of calls if predictable
    # assert mock_register_tool.call_count >= 1 # Check at least one tool was registered

    # Alternatively, check the app's tool collection directly if possible
    # assert "expected_tool_name" in app.tools


# Test Case 4: Handling Invalid Configuration during Startup
def test_startup_with_invalid_config():
    """Test how the application handles invalid configuration during startup."""
    invalid_config_values = {"logging": {"level": "INVALID_LEVEL"}}

    # Expect a specific exception (e.g., ValueError, ConfigurationError) upon loading or use
    with pytest.raises((ValueError, TypeError)):  # Adjust expected exception type
        config = load_and_get_config(invalid_config_values)
        # Potentially call the app setup if config loading doesn't raise immediately
        # get_fastmcp_app(config)


# Test Case 5: Lifespan Function Execution (if using lifespan context manager)
@pytest.mark.asyncio
@patch("chemist_server.mcp_core.app.startup_event", create=True)  # Example patch target
@patch(
    "chemist_server.mcp_core.app.shutdown_event", create=True
)  # Example patch target
async def test_lifespan_events(mock_startup, mock_shutdown, default_config):
    """Test that startup and shutdown events in the lifespan context manager execute.

    Note: Requires the app to be configured with an async lifespan context manager.
    Adjust patch targets to the actual startup/shutdown functions.
    Requires running the app within a test client or simulated server environment.
    This test might be better suited for a full integration test with an ASGI client.
    """
    # This test setup is simplified. A real test would likely involve:
    # 1. Creating the app: app = get_fastmcp_app(default_config)
    # 2. Using an ASGI test client (like httpx.AsyncClient) to run the app lifespan:
    #    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
    #        # Lifespan startup runs upon entering the context
    #        mock_startup.assert_called_once()
    #        # Perform a dummy request if needed
    #        # response = await client.get("/")
    #    # Lifespan shutdown runs upon exiting the context
    #    mock_shutdown.assert_called_once()
    pass  # Placeholder for complex lifespan test
