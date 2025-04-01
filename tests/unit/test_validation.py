"""Unit tests for the MCP protocol validation components."""

import pytest

# Import from conftest instead of trying to import directly
from tests.conftest import (
    mock_validate_jsonrpc_message,
    mock_validate_tool_parameters,
    mock_validate_tool_result,
)

# Sample schemas for testing
ECHO_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {"type": "string"},
        "repeat": {"type": "integer", "minimum": 1, "maximum": 10},
    },
    "required": ["message"],
}

CALCULATOR_SCHEMA = {
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
}

NESTED_SCHEMA = {
    "type": "object",
    "properties": {
        "user": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0},
                "email": {"type": "string", "format": "email"},
            },
            "required": ["name", "email"],
        },
        "settings": {
            "type": "object",
            "properties": {
                "theme": {"type": "string", "enum": ["light", "dark", "system"]},
                "notifications": {"type": "boolean"},
            },
        },
    },
    "required": ["user"],
}


class TestParameterValidation:
    """Tests for parameter validation."""

    def test_valid_simple_parameters(self):
        """Test validation of valid simple parameters."""
        # Test with echo schema
        params = {"message": "Hello, world!"}
        result = mock_validate_tool_parameters(params, ECHO_SCHEMA)
        assert result is True

        # Test with optional parameter
        params = {"message": "Hello, world!", "repeat": 3}
        result = mock_validate_tool_parameters(params, ECHO_SCHEMA)
        assert result is True

    def test_invalid_simple_parameters(self):
        """Test validation of invalid simple parameters."""
        # Missing required parameter
        params = {}
        with pytest.raises(ValueError, match="Required .*'message'"):
            mock_validate_tool_parameters(params, ECHO_SCHEMA)

        # Invalid type
        params = {"message": 123}  # Number instead of string
        with pytest.raises(ValueError, match="should be a string"):
            mock_validate_tool_parameters(params, ECHO_SCHEMA)

        # Value out of range
        params = {"message": "Hello", "repeat": 20}  # Outside maximum of 10
        with pytest.raises(ValueError, match="exceeds maximum value"):
            mock_validate_tool_parameters(params, ECHO_SCHEMA)

    def test_valid_complex_parameters(self):
        """Test validation of valid complex parameters."""
        # Test with calculator schema
        params = {"operation": "add", "a": 5, "b": 3}
        result = mock_validate_tool_parameters(params, CALCULATOR_SCHEMA)
        assert result is True

        # Test with floating point numbers
        params = {"operation": "multiply", "a": 2.5, "b": 1.5}
        result = mock_validate_tool_parameters(params, CALCULATOR_SCHEMA)
        assert result is True

    def test_invalid_complex_parameters(self):
        """Test validation of invalid complex parameters."""
        # Invalid enum value
        params = {
            "operation": "power",
            "a": 2,
            "b": 3,
        }  # 'power' not in allowed operations
        with pytest.raises(ValueError, match="must be one of"):
            mock_validate_tool_parameters(params, CALCULATOR_SCHEMA)

        # Missing required parameter
        params = {"operation": "add", "a": 5}  # Missing 'b'
        with pytest.raises(ValueError, match="Required .*'b'"):
            mock_validate_tool_parameters(params, CALCULATOR_SCHEMA)

    def test_valid_nested_parameters(self):
        """Test validation of valid nested parameters."""
        params = {
            "user": {"name": "John Doe", "email": "john@example.com", "age": 30},
            "settings": {"theme": "dark", "notifications": True},
        }
        result = mock_validate_tool_parameters(params, NESTED_SCHEMA)
        assert result is True

        # Test with minimal required fields
        params = {"user": {"name": "John Doe", "email": "john@example.com"}}
        result = mock_validate_tool_parameters(params, NESTED_SCHEMA)
        assert result is True


class TestJsonRpcValidation:
    """Tests for JSON-RPC message validation."""

    def test_valid_jsonrpc_request(self):
        """Test validation of a valid JSON-RPC request."""
        message = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "echo", "parameters": {"message": "Hello"}},
            "id": "request-123",
        }
        result = mock_validate_jsonrpc_message(message)
        assert result is True

    def test_valid_jsonrpc_notification(self):
        """Test validation of a valid JSON-RPC notification."""
        message = {
            "jsonrpc": "2.0",
            "method": "notifications/status",
            "params": {"status": "ready"},
        }
        result = mock_validate_jsonrpc_message(message)
        assert result is True

    def test_valid_jsonrpc_response(self):
        """Test validation of a valid JSON-RPC response."""
        message = {
            "jsonrpc": "2.0",
            "id": "request-123",
            "result": {
                "content": [{"type": "text", "text": "Hello, world!"}],
                "isError": False,
                "isPartial": False,
            },
        }
        result = mock_validate_jsonrpc_message(message)
        assert result is True

    def test_valid_jsonrpc_error_response(self):
        """Test validation of a valid JSON-RPC error response."""
        message = {
            "jsonrpc": "2.0",
            "id": "request-123",
            "error": {
                "code": -32600,
                "message": "Invalid Request",
                "data": {"details": "Missing required field"},
            },
        }
        result = mock_validate_jsonrpc_message(message)
        assert result is True

    def test_invalid_jsonrpc_version(self):
        """Test validation with an invalid JSON-RPC version."""
        message = {
            "jsonrpc": "1.0",  # Invalid version, should be "2.0"
            "method": "tools/call",
            "params": {"name": "echo"},
            "id": "request-123",
        }
        with pytest.raises(ValueError, match="Invalid JSON-RPC version"):
            mock_validate_jsonrpc_message(message)

    def test_missing_jsonrpc_field(self):
        """Test validation with missing required JSON-RPC fields."""
        # Missing jsonrpc field
        message = {
            "method": "tools/call",
            "params": {"name": "echo"},
            "id": "request-123",
        }
        with pytest.raises(ValueError, match="Missing 'jsonrpc' field"):
            mock_validate_jsonrpc_message(message)

        # Request missing method
        message = {"jsonrpc": "2.0", "params": {"name": "echo"}, "id": "request-123"}
        with pytest.raises(ValueError, match="method"):
            mock_validate_jsonrpc_message(message)

        # Response missing both result and error
        message = {"jsonrpc": "2.0", "id": "request-123"}
        with pytest.raises(ValueError, match="must contain either 'result' or 'error'"):
            mock_validate_jsonrpc_message(message)

    def test_invalid_method_format(self):
        """Test validation with an invalid method format."""
        message = {
            "jsonrpc": "2.0",
            "method": "invalid_method",  # Should follow namespace/method format
            "params": {"name": "echo"},
            "id": "request-123",
        }
        with pytest.raises(
            ValueError, match="Method must follow namespace/method format"
        ):
            mock_validate_jsonrpc_message(message)


class TestToolResultValidation:
    """Tests for tool result validation."""

    def test_valid_tool_result(self):
        """Test validation of a valid tool result."""
        # Simple text content
        result = {
            "content": [{"type": "text", "text": "Hello, world!"}],
            "isError": False,
            "isPartial": False,
        }
        assert mock_validate_tool_result(result) is True

        # Multiple content items
        result = {
            "content": [
                {"type": "text", "text": "Result: "},
                {"type": "text", "text": "42"},
            ],
            "isError": False,
            "isPartial": False,
        }
        assert mock_validate_tool_result(result) is True

        # Error result
        result = {
            "content": [{"type": "text", "text": "An error occurred: File not found"}],
            "isError": True,
            "isPartial": False,
        }
        assert mock_validate_tool_result(result) is True

        # Partial result
        result = {
            "content": [{"type": "text", "text": "Processing... 50% complete"}],
            "isError": False,
            "isPartial": True,
        }
        assert mock_validate_tool_result(result) is True

    def test_invalid_tool_result_structure(self):
        """Test validation with invalid tool result structure."""
        # Missing content field
        result = {"isError": False, "isPartial": False}
        with pytest.raises(ValueError, match="Missing 'content' field"):
            mock_validate_tool_result(result)

        # Empty content array
        result = {"content": [], "isError": False, "isPartial": False}
        with pytest.raises(ValueError, match="Content array cannot be empty"):
            mock_validate_tool_result(result)

        # Missing isError field
        result = {"content": [{"type": "text", "text": "Hello"}], "isPartial": False}
        with pytest.raises(ValueError, match="Missing 'isError' field"):
            mock_validate_tool_result(result)

        # Missing isPartial field
        result = {"content": [{"type": "text", "text": "Hello"}], "isError": False}
        with pytest.raises(ValueError, match="Missing 'isPartial' field"):
            mock_validate_tool_result(result)

    def test_invalid_content_items(self):
        """Test validation with invalid content items."""
        # Missing type in content item
        result = {"content": [{"text": "Hello"}], "isError": False, "isPartial": False}
        with pytest.raises(ValueError, match="Content item missing 'type' field"):
            mock_validate_tool_result(result)

        # Missing text in text-type content
        result = {"content": [{"type": "text"}], "isError": False, "isPartial": False}
        with pytest.raises(ValueError, match="Text content item missing 'text' field"):
            mock_validate_tool_result(result)

        # Unsupported content type
        result = {
            "content": [{"type": "unsupported", "data": "something"}],
            "isError": False,
            "isPartial": False,
        }
        with pytest.raises(ValueError):
            mock_validate_tool_result(result)

    def test_valid_mixed_content_types(self):
        """Test validation with valid mixed content types."""
        result = {
            "content": [
                {"type": "text", "text": "Here's an image: "},
                {
                    "type": "image",
                    "url": "https://example.com/image.jpg",
                    "alt": "Example image",
                },
            ],
            "isError": False,
            "isPartial": False,
        }
        assert mock_validate_tool_result(result) is True


@pytest.fixture
def mock_validation_functions(mock_validation_components):
    """Fixture to provide validation functions for testing."""
    return mock_validation_components
