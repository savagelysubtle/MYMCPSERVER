"""Tests for the CLI Tool server implementation."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# Import conftest first to ensure mocks are in place
import conftest  # noqa
import pytest

# Now import the CLI tool modules - mcp_core should be mocked by conftest
from src.chemist_server.tool_servers.python_tool_server.cliTool.cli_tools import (
    preprocess_command,
    run_command,
    show_security_rules,
)
from src.chemist_server.tool_servers.python_tool_server.cliTool.command_tools import (
    CommandConfig,
    CommandExecutor,
    CommandSecurityError,
    CommandTimeoutError,
)


class TestCommandPreprocessor:
    """Test suite for the command preprocessor functionality."""

    def test_preprocess_empty_command(self):
        """Test preprocessing an empty command."""
        cmd, changes = preprocess_command("")
        assert cmd == ""
        assert "Empty command" in changes["warnings"]

    def test_preprocess_unix_to_windows_commands(self):
        """Test converting Unix commands to Windows equivalents."""
        test_cases = [
            ("ls", "dir"),
            ("ls -l", "dir /a"),
            ("cat file.txt", "type file.txt"),
            ("grep pattern file.txt", "findstr pattern file.txt"),
            ("mkdir new_dir", "md new_dir"),
            ("rm file.txt", "del file.txt"),
        ]

        for unix_cmd, expected_win_cmd in test_cases:
            processed, changes = preprocess_command(unix_cmd)
            assert processed == expected_win_cmd
            assert changes["modifications"]
            assert "Converted Unix command" in changes["modifications"][0]

    def test_preprocess_flag_conversion(self):
        """Test converting Unix-style flags to Windows equivalents."""
        test_cases = [
            ("dir -l", "dir /a"),
            ("findstr -i pattern file.txt", "findstr /i pattern file.txt"),
            ("dir -a", "dir /a"),
        ]

        for cmd_with_unix_flags, expected_cmd in test_cases:
            processed, changes = preprocess_command(cmd_with_unix_flags)
            assert processed == expected_cmd
            assert changes["modifications"]

    def test_preprocess_path_normalization(self):
        """Test normalizing paths in commands."""
        test_cases = [
            # Forward slash to backslash conversion
            ("type folder/file.txt", "type folder\\file.txt"),
            # Remove ./ prefix
            ("type ./file.txt", "type file.txt"),
            # Normalize double backslashes
            ("type folder\\\\file.txt", "type folder\\file.txt"),
        ]

        for cmd_with_path, expected_cmd in test_cases:
            processed, changes = preprocess_command(cmd_with_path)
            assert processed == expected_cmd
            assert changes["modifications"]

    def test_preprocess_quote_handling(self):
        """Test handling of quotes in commands."""
        test_cases = [
            ('echo "Hello World"', "echo Hello World"),
            ("echo 'Hello World'", "echo Hello World"),
        ]

        for cmd_with_quotes, expected_cmd in test_cases:
            processed, changes = preprocess_command(cmd_with_quotes)
            assert processed == expected_cmd
            assert changes["modifications"]

    def test_preprocess_complex_command_warnings(self):
        """Test warnings for complex commands."""
        test_cases = [
            "dir && type file.txt",
            "dir | findstr pattern",
            "echo test; echo more",
        ]

        for complex_cmd in test_cases:
            processed, changes = preprocess_command(complex_cmd)
            assert "Command contains operators" in changes["warnings"][0]

    def test_preprocess_combined_transformations(self):
        """Test multiple transformations in a single command."""
        cmd = "ls -la ./folder/file.txt"
        expected = "dir /a folder\\file.txt"

        processed, changes = preprocess_command(cmd)
        assert processed == expected
        assert len(changes["modifications"]) >= 2  # At least 2 transformations


class TestCommandTools:
    """Test suite for the low-level command tools."""

    @pytest.fixture
    def temp_test_dir(self):
        """Create a temporary directory for testing file operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files in the temp directory
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("This is a test file.")

            # Create a subdirectory
            subdir = Path(temp_dir) / "subdir"
            subdir.mkdir()
            subdir_file = subdir / "subfile.txt"
            subdir_file.write_text("This is a file in a subdirectory.")

            yield temp_dir

    @pytest.fixture
    def command_executor(self, temp_test_dir):
        """Create a command executor with a test configuration."""
        # Use Windows-friendly commands for compatibility
        config = CommandConfig(
            allowed_dir=temp_test_dir,
            allowed_commands=["dir", "type", "echo", "cd", "where", "findstr"],
            allowed_flags=["/a", "/b", "/c", "/q", "-h", "--help"],
            max_command_length=1024,
            command_timeout=5,
        )
        return CommandExecutor(config)

    @pytest.mark.asyncio
    async def test_valid_command_execution(self, command_executor):
        """Test executing a valid command."""
        result = await command_executor.run_command("dir /a")
        assert result["exit_code"] == 0
        assert "test.txt" in result["stdout"] or "subdir" in result["stdout"]

    @pytest.mark.asyncio
    async def test_command_with_output(self, command_executor):
        """Test command that produces output."""
        result = await command_executor.run_command("echo Hello, world!")
        assert result["exit_code"] == 0
        assert "Hello, world!" in result["stdout"]

    @pytest.mark.asyncio
    async def test_command_not_allowed(self, command_executor):
        """Test executing a command that is not allowed."""
        with pytest.raises(CommandSecurityError) as exc_info:
            await command_executor.run_command("del /q *")
        assert "Command 'del' is not allowed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_flag_not_allowed(self, command_executor):
        """Test executing a command with a flag that is not allowed."""
        with pytest.raises(CommandSecurityError) as exc_info:
            await command_executor.run_command("dir /s")
        assert "Flag '/s' is not allowed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_shell_operator_not_allowed(self, command_executor):
        """Test command with shell operators."""
        with pytest.raises(CommandSecurityError) as exc_info:
            await command_executor.run_command("dir && echo Dangerous")
        assert "Shell operator '&&' is not allowed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_path_traversal_prevention(self, command_executor, temp_test_dir):
        """Test path traversal prevention."""
        # Attempt to access a file outside the allowed directory
        parent_dir = str(Path(temp_test_dir).parent)
        with pytest.raises(CommandSecurityError) as exc_info:
            await command_executor.run_command(
                f"type ..\\{os.path.basename(parent_dir)}\\some_file.txt"
            )
        assert "outside the allowed directory" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_command_timeout(self, command_executor):
        """Test command execution timeout."""
        # Modify the timeout to a very small value for testing
        command_executor.config.command_timeout = 0.1

        with pytest.raises(CommandTimeoutError) as exc_info:
            # A command that will run longer than the timeout (using ping as a delay mechanism)
            await command_executor.run_command("ping -n 5 127.0.0.1")
        assert "timed out" in str(exc_info.value)

    def test_security_rules(self, command_executor):
        """Test getting security rules."""
        rules = command_executor.get_security_rules()
        assert rules["working_directory"] == command_executor.allowed_dir
        assert rules["allowed_commands"] == command_executor.config.allowed_commands
        assert rules["allowed_flags"] == command_executor.config.allowed_flags
        assert rules["max_command_length"] == command_executor.config.max_command_length
        assert rules["command_timeout"] == command_executor.config.command_timeout


class TestCliTools:
    """Test suite for the CLI tool functions exposed to the MCP server."""

    @pytest.fixture
    def mock_executor(self):
        """Create a mock command executor."""
        mock = MagicMock()
        mock.run_command = MagicMock(
            return_value={"stdout": "mocked output", "stderr": "", "exit_code": 0}
        )
        mock.get_security_rules = MagicMock(
            return_value={
                "working_directory": "C:\\mock\\dir",
                "allowed_commands": ["dir", "type", "echo"],
                "allowed_flags": ["/a", "/b", "/q"],
                "max_command_length": 1024,
                "command_timeout": 30,
            }
        )
        mock.allowed_dir = "C:\\mock\\dir"
        mock.config = MagicMock()
        mock.config.command_timeout = 30
        return mock

    @pytest.fixture
    def mock_ctx(self):
        """Create a mock context for tool functions."""
        return MagicMock(params={"command": "dir /a"})

    @pytest.mark.asyncio
    @patch(
        "src.chemist_server.tool_servers.python_tool_server.cliTool.cli_tools.executor"
    )
    async def test_run_command_success(
        self, mock_executor_module, mock_executor, mock_ctx
    ):
        """Test successful command execution."""
        mock_executor_module.run_command = mock_executor.run_command

        result = await run_command(mock_ctx, "dir /a")

        mock_executor.run_command.assert_called_once_with("dir /a")
        assert result["stdout"] == "mocked output"
        assert result["success"] is True
        assert result["command"] == "dir /a"
        assert result["working_directory"] == "C:\\mock\\dir"

    @pytest.mark.asyncio
    @patch(
        "src.chemist_server.tool_servers.python_tool_server.cliTool.cli_tools.executor"
    )
    async def test_run_command_with_unix_conversion(
        self, mock_executor_module, mock_executor, mock_ctx
    ):
        """Test command execution with Unix to Windows conversion."""
        mock_executor_module.run_command = mock_executor.run_command

        result = await run_command(mock_ctx, "ls -l")

        # The run_command should have converted ls -l to dir /a
        mock_executor.run_command.assert_called_once_with("dir /a")
        assert result["original_command"] == "ls -l"
        assert result["command"] == "dir /a"
        assert "command_modifications" in result
        assert result["command_modifications"] is not None

    @pytest.mark.asyncio
    @patch(
        "src.chemist_server.tool_servers.python_tool_server.cliTool.cli_tools.executor"
    )
    async def test_run_command_failure(
        self, mock_executor_module, mock_executor, mock_ctx
    ):
        """Test command execution failure."""
        mock_executor.run_command.side_effect = CommandSecurityError(
            "Security violation"
        )
        mock_executor_module.run_command = mock_executor.run_command

        result = await run_command(mock_ctx, "del /q *")

        assert result["success"] is False
        assert "Security violation" in result["error"]
        assert result["type"] == "SecurityViolation"
        assert result["command"] == "del /q *"

    @pytest.mark.asyncio
    @patch(
        "src.chemist_server.tool_servers.python_tool_server.cliTool.cli_tools.executor"
    )
    async def test_run_command_timeout(
        self, mock_executor_module, mock_executor, mock_ctx
    ):
        """Test command timeout handling."""
        mock_executor.run_command.side_effect = CommandTimeoutError(
            "Command timed out after 30 seconds"
        )
        mock_executor_module.run_command = mock_executor.run_command

        result = await run_command(mock_ctx, "ping -n 60 127.0.0.1")

        assert result["success"] is False
        assert "timed out" in result["error"]
        assert result["type"] == "CommandTimeout"
        assert result["command"] == "ping -n 60 127.0.0.1"

    @pytest.mark.asyncio
    @patch(
        "src.chemist_server.tool_servers.python_tool_server.cliTool.cli_tools.executor"
    )
    async def test_command_from_context(self, mock_executor_module, mock_executor):
        """Test getting command from context if not explicitly provided."""
        mock_executor_module.run_command = mock_executor.run_command

        # Create context with command parameter
        ctx = MagicMock(params={"command": "dir /a"})

        # Don't provide the command explicitly - use empty string instead of None
        result = await run_command(ctx, "")

        # Should still execute the command from context
        mock_executor.run_command.assert_called_once_with("dir /a")
        assert result["success"] is True

    @pytest.mark.asyncio
    @patch(
        "src.chemist_server.tool_servers.python_tool_server.cliTool.cli_tools.executor"
    )
    async def test_show_security_rules(
        self, mock_executor_module, mock_executor, mock_ctx
    ):
        """Test getting security rules."""
        mock_executor_module.get_security_rules = mock_executor.get_security_rules

        result = await show_security_rules(mock_ctx)

        mock_executor.get_security_rules.assert_called_once()
        assert result["success"] is True
        assert "working_directory" in result["security_rules"]
        assert result["security_rules"]["allowed_commands"] == ["dir", "type", "echo"]
        assert "platform_specific" in result
        assert "is_windows" in result["platform_specific"]
        assert "command_preprocessing" in result["platform_specific"]
        assert (
            "unix_to_windows_commands"
            in result["platform_specific"]["command_preprocessing"]
        )


class TestCliToolIntegration:
    """Integration tests for the CLI tool."""

    @pytest.fixture
    def temp_test_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Integration test file content")
            yield temp_dir

    @pytest.fixture
    def mock_ctx(self):
        """Create a mock context for tool functions."""
        return MagicMock(params={})

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"ALLOWED_DIR": "PLACEHOLDER"})
    async def test_cli_tool_integration(self, temp_test_dir, mock_ctx):
        """Test CLI tool integration with actual command execution."""
        # Update the ALLOWED_DIR environment variable with the actual temp directory
        os.environ["ALLOWED_DIR"] = temp_test_dir

        # Import here to ensure environment variable is set before module initialization
        from src.chemist_server.tool_servers.python_tool_server.cliTool.cli_tools import (
            run_command,
        )

        # Test file listing
        mock_ctx.command = "dir"
        dir_result = await run_command(mock_ctx, "dir")
        assert dir_result["success"] is True
        assert "test.txt" in dir_result["stdout"]

        # Test file content reading
        mock_ctx.command = "type test.txt"
        cat_result = await run_command(mock_ctx, "type test.txt")
        assert cat_result["success"] is True
        assert "Integration test file content" in cat_result["stdout"]

        # Test file content reading with Unix command (should be auto-converted)
        mock_ctx.command = "cat test.txt"
        unix_cat_result = await run_command(mock_ctx, "cat test.txt")
        assert unix_cat_result["success"] is True
        assert "Integration test file content" in unix_cat_result["stdout"]
        assert unix_cat_result["original_command"] == "cat test.txt"
        assert unix_cat_result["command"] == "type test.txt"
        assert unix_cat_result["command_modifications"] is not None

        # Test disallowed command
        mock_ctx.command = "del test.txt"
        invalid_result = await run_command(mock_ctx, "del test.txt")
        assert invalid_result["success"] is False
        assert "not allowed" in invalid_result["error"]
