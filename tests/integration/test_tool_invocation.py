"""Integration tests for invoking registered tools on the MCP server."""

import pytest

# Assuming the fixture from conftest provides app and client session
# Ensure conftest.py is correctly set up and imports necessary components

# --- Test Cases for Tool Invocation ---

pytestmark = pytest.mark.asyncio


async def test_invoke_existing_tool_success(create_connected_server_and_client_session):
    """Test invoking a known, registered tool successfully via the client session."""
    app, client_session = await create_connected_server_and_client_session

    # Assume a tool named 'echo_tool' is registered and simply returns its input
    tool_name = "echo_tool"  # Replace with an actual registered tool name
    tool_params = {"message": "Hello, MCP!"}

    # Mock the actual implementation of the tool if needed to isolate invocation
    # Patch target depends on how tools are structured and registered
    # Example: @patch("chemist_server.mcp_core.tools.echo_tool.EchoTool.__call__")
    # async with patch_target as mock_tool_call:
    #    mock_tool_call.return_value = {"response": "Mocked Hello, MCP!"}
    #    result = await client_session.invoke_tool(tool_name, **tool_params)

    # If testing the real tool implementation via the mock client:
    try:
        # Ensure the tool actually exists on the app instance from the fixture
        if tool_name not in app.tools:
            pytest.skip(f"Tool '{tool_name}' not registered on the app instance.")

        result = await client_session.invoke_tool(tool_name, **tool_params)

        # Assert based on the expected return value of the REAL 'echo_tool'
        # This depends heavily on the actual tool's implementation
        assert isinstance(result, dict), "Tool result should be a dictionary"
        assert result.get("response") == "Hello, MCP!"  # Example assertion

    except ValueError as e:
        # Handle case where invoke_tool raises error (e.g., tool not found in mock)
        pytest.fail(f"Invoking tool '{tool_name}' failed: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error during tool invocation: {e}")


async def test_invoke_nonexistent_tool(create_connected_server_and_client_session):
    """Test invoking a tool that is not registered."""
    app, client_session = await create_connected_server_and_client_session
    tool_name = "non_existent_tool_xyz"

    # Expect invoke_tool to raise an error (e.g., ValueError or a specific MCP error)
    with pytest.raises(ValueError, match=f"Tool {tool_name} not found"):
        await client_session.invoke_tool(tool_name, param1="value1")


async def test_invoke_tool_with_missing_required_param(
    create_connected_server_and_client_session,
):
    """Test invoking a tool with missing required parameters."""
    app, client_session = await create_connected_server_and_client_session
    # Assume 'calculator_tool' requires 'a' and 'b'
    tool_name = "calculator_tool"  # Replace with an actual tool name
    tool_params = {"a": 5}  # Missing 'b'

    if tool_name not in app.tools:
        pytest.skip(f"Tool '{tool_name}' not registered on the app instance.")

    # The behavior depends on FastMCP/Pydantic validation
    # It might raise TypeError, ValueError, or a Pydantic ValidationError
    with pytest.raises((TypeError, ValueError)):  # Adjust expected exception
        await client_session.invoke_tool(tool_name, **tool_params)


async def test_invoke_tool_with_incorrect_param_type(
    create_connected_server_and_client_session,
):
    """Test invoking a tool with incorrect parameter types."""
    app, client_session = await create_connected_server_and_client_session
    tool_name = "calculator_tool"  # Requires int/float for a, b
    tool_params = {"a": "five", "b": 3}  # 'a' is incorrect type

    if tool_name not in app.tools:
        pytest.skip(f"Tool '{tool_name}' not registered on the app instance.")

    # Expect validation error (likely Pydantic ValidationError or TypeError)
    with pytest.raises((TypeError, ValueError)):  # Adjust expected exception
        await client_session.invoke_tool(tool_name, **tool_params)


# Add more tests:
# - Test tools that interact with external systems (mock the external calls)
# - Test tools that modify state (check state before and after)
# - Test tools with different return types
# - Test tools requiring specific context information (mock context attributes)
