"""Configuration for pytest with mocks for MCP components."""

import sys
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from typing import Any, TypeVar, cast
from unittest.mock import MagicMock, patch

import pytest

# Mark the whole file as async to avoid warnings
pytestmark = pytest.mark.asyncio


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


# Validation mocks
def mock_validate_tool_parameters(
    parameters: dict[str, Any], schema: dict[str, Any]
) -> bool:
    """Mock validation for tool parameters."""
    # Simple validation logic for testing
    if "required" in schema:
        for field in schema["required"]:
            if field not in parameters:
                raise ValueError(f"Required field '{field}' is missing")

    # Check type validation for string fields
    if "properties" in schema:
        for field, field_schema in schema["properties"].items():
            if field in parameters:
                # String validation
                if field_schema.get("type") == "string" and not isinstance(
                    parameters[field], str
                ):
                    raise ValueError(f"Field '{field}' should be a string")

                # Number validation
                if field_schema.get("type") == "number" and not isinstance(
                    parameters[field], (int, float)
                ):
                    raise ValueError(f"Field '{field}' should be a number")

                # Integer validation
                if field_schema.get("type") == "integer":
                    if not isinstance(parameters[field], int):
                        raise ValueError(f"Field '{field}' should be an integer")

                    # Range validation
                    if (
                        "minimum" in field_schema
                        and parameters[field] < field_schema["minimum"]
                    ):
                        raise ValueError(
                            f"Field '{field}' is below minimum value {field_schema['minimum']}"
                        )
                    if (
                        "maximum" in field_schema
                        and parameters[field] > field_schema["maximum"]
                    ):
                        raise ValueError(
                            f"Field '{field}' exceeds maximum value {field_schema['maximum']}"
                        )

                # Enum validation
                if (
                    "enum" in field_schema
                    and parameters[field] not in field_schema["enum"]
                ):
                    raise ValueError(
                        f"Field '{field}' must be one of {field_schema['enum']}"
                    )

    return True


def mock_validate_jsonrpc_message(message: dict[str, Any]) -> bool:
    """Mock validation for JSON-RPC messages."""
    # Basic validation logic
    if "jsonrpc" not in message:
        raise ValueError("Missing 'jsonrpc' field")

    if message["jsonrpc"] != "2.0":
        raise ValueError("Invalid JSON-RPC version (must be '2.0')")

    # Request validation
    if "method" in message:
        if "/" not in message["method"]:
            raise ValueError("Method must follow namespace/method format")
    # Response validation
    elif "id" in message:
        if "result" not in message and "error" not in message:
            raise ValueError("Response must contain either 'result' or 'error'")

    return True


def mock_validate_tool_result(result: dict[str, Any]) -> bool:
    """Mock validation for tool results."""
    # Basic validation
    if "content" not in result:
        raise ValueError("Missing 'content' field")

    if not result["content"]:
        raise ValueError("Content array cannot be empty")

    if "isError" not in result:
        raise ValueError("Missing 'isError' field")

    if "isPartial" not in result:
        raise ValueError("Missing 'isPartial' field")

    # Content item validation
    for item in result["content"]:
        if "type" not in item:
            raise ValueError("Content item missing 'type' field")

        if item["type"] == "text" and "text" not in item:
            raise ValueError("Text content item missing 'text' field")

    return True


# Create module mocks
mock_mcp_core = MagicMock()
mock_mcp_core.HealthCheck = MockHealthCheck
mock_mcp_core.HealthStatus = MockHealthStatus
mock_mcp_core.logger = MockLogger()

# Add validation mocks
mock_mcp_core.validation = MagicMock()
mock_mcp_core.validation.validate_tool_parameters = mock_validate_tool_parameters
mock_mcp_core.validation.validate_jsonrpc_message = mock_validate_jsonrpc_message
mock_mcp_core.validation.validate_tool_result = mock_validate_tool_result

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
sys.modules["chemist_server.mcp_core.validation"] = mock_mcp_core.validation


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


@pytest.fixture
def mock_validation_components():
    """Fixture to provide access to mock validation components."""
    return {
        "validate_tool_parameters": mock_validate_tool_parameters,
        "validate_jsonrpc_message": mock_validate_jsonrpc_message,
        "validate_tool_result": mock_validate_tool_result,
    }


class MockClientSession:
    """Mock client session for testing."""

    def __init__(self, app):
        self.app = app
        self.request_id = "test-request-id"

    async def invoke_tool(self, tool_name: str, **kwargs) -> Any:
        """Invoke a tool on the app."""
        tool_func = self.app.get_tool(tool_name)
        if not tool_func:
            raise ValueError(f"Tool {tool_name} not found")

        # Create a mock context with a mock session
        session = MagicMock()
        from mcp.server.fastmcp import Context

        ctx = Context(session=session, request_id=self.request_id)

        # Call the tool function with the context and parameters
        return await tool_func(ctx, **kwargs)


# Define a type variable for the config type to help with type annotations
ConfigT = TypeVar("ConfigT")


# Handling AppConfig and load_and_get_config to avoid type issues
# Create a dummy base class for app config
class TestAppConfigBase:
    """Base app config class to avoid type conflicts."""


# Try to import real config, or create a stub version
try:
    # Import the real config classes but with different names to avoid shadowing
    from chemist_server.config import AppConfig as RealAppConfig
    from chemist_server.config import load_and_get_config as real_load_and_get_config

    # Create our test version that extends the real one
    class TestAppConfig(RealAppConfig, TestAppConfigBase):
        """Test app config class that combines real config with our base class."""

    # Wrapper function with proper typing
    def test_load_and_get_config(
        cli_args: dict[str, Any] | None = None, **kwargs
    ) -> TestAppConfig:
        """Wrapper to ensure consistent typing."""
        config = real_load_and_get_config(cli_args, **kwargs)
        # This cast helps with type checking
        return cast("TestAppConfig", config)

    CONFIG_MODULE_EXISTS = True

except ImportError:
    # Create a stub AppConfig class
    class TestAppConfig(TestAppConfigBase):
        """Stub app config class for when the real one is unavailable."""

        def __init__(self):
            self.transport = "stdio"
            self.logs_path = "/tmp/test_logs"
            self.components = "all"
            self.debug = True
            self.tool_servers = {
                "python": {
                    "enabled": True,
                    "host": "localhost",
                    "port": 8001,
                    "path": "/tools/python",
                }
            }
            self.core = {
                "host": "localhost",
                "port": 8000,
                "debug": True,
                "auth_token": "test_token",
            }

        def get_core_host(self):
            """Return the core host."""
            return self.core["host"]

        def get_core_port(self):
            """Return the core port."""
            return self.core["port"]

    def test_load_and_get_config(
        cli_args: dict[str, Any] | None = None, **kwargs
    ) -> TestAppConfig:
        """Stub function that returns our dummy config."""
        return TestAppConfig()

    CONFIG_MODULE_EXISTS = False


# --- Enhanced/New Fixtures for MVP ---


@pytest.fixture(scope="session")
def session_default_config() -> TestAppConfig:
    """Provides a default AppConfig instance loaded once per session."""
    if not CONFIG_MODULE_EXISTS:
        pytest.skip("Config module not found, using stub config for testing.")
    # Load default config using an empty dict for CLI args
    # You might add specific overrides here for testing defaults
    config = test_load_and_get_config(
        {}, skip_env_files=True
    )  # Skip .env for session scope
    return config


@pytest.fixture
def function_default_config() -> TestAppConfig:
    """Provides a default AppConfig instance loaded per function (allows modification)."""
    if not CONFIG_MODULE_EXISTS:
        pytest.skip("Config module not found, using stub config for testing.")
    # Load default config, potentially allowing modification via CLI dict mock
    config = test_load_and_get_config(
        {}, skip_env_files=True
    )  # Skip .env for isolation
    # Deep copy might be needed if tests modify config object: import copy; return copy.deepcopy(config)
    return config


@pytest.fixture
def temp_directory(tmp_path: Path) -> Path:
    """Provides a temporary directory unique to each test function using pytest's tmp_path."""
    return tmp_path


@pytest.fixture
def mock_subprocess_run() -> Generator[MagicMock]:
    """Provides a patch for subprocess.run for the duration of a test."""
    with patch("subprocess.run") as mock_run:
        # Configure default mock behavior if desired
        mock_run.return_value = MagicMock(stdout=b"", stderr=b"", returncode=0)
        yield mock_run


# --- Existing Fixture (Modified for compatibility with test config) ---


@pytest.fixture
async def create_connected_server_and_client_session(
    function_default_config: TestAppConfig,
) -> AsyncGenerator[tuple[Any, Any]]:
    """Fixture that creates a FastMCP server and client session for integration testing.

    Uses the function-scoped default config by default. Initializes the app
    and yields the app instance and a mock client session.

    Yields:
        Tuple[FastMCP, MockClientSession]: A tuple of (FastMCP app, mock client session)

    """
    # Check if necessary modules exist before proceeding
    try:
        from mcp.server.fastmcp import FastMCP

        from chemist_server.mcp_core.app import get_fastmcp_app
    except ImportError:
        pytest.skip(
            "Required app modules (get_fastmcp_app, FastMCP) not found for integration fixture."
        )

    # Use the injected config fixture
    config = function_default_config

    # Initialize the FastMCP app - use Any to bypass type checking which is complex here
    try:
        app = get_fastmcp_app(cast("Any", config))
    except Exception as e:
        pytest.fail(f"Failed to initialize FastMCP app in fixture: {e}")

    # Create a mock client session
    client = MockClientSession(app)

    # Yield the app and client
    return app, client

    # Add any necessary cleanup here if required after tests using the fixture
