"""Unit tests for the secure CommandExecutor."""

import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# Import components to be tested
from chemist_server.tool_servers.python_tool_server.cliTool.command_tools import (
    CommandConfig,
    CommandExecutionError,
    CommandExecutor,
    CommandSecurityError,
    CommandTimeoutError,
)

# --- Fixtures ---


@pytest.fixture
def default_command_config(tmp_path: Path) -> CommandConfig:
    """Provides a default CommandConfig pointing to a safe temp directory."""
    # Ensure the temp directory exists for the validator
    allowed_dir = tmp_path / "allowed_exec_dir"
    allowed_dir.mkdir()
    return CommandConfig(
        allowed_dir=str(allowed_dir),
        allowed_commands=None,  # Allow defaults initially for simpler tests
        allowed_flags=None,
        max_command_length=512,
        command_timeout=10,
    )


@pytest.fixture
def restricted_command_config(tmp_path: Path) -> CommandConfig:
    """Provides a CommandConfig with restricted commands/flags."""
    allowed_dir = tmp_path / "restricted_exec_dir"
    allowed_dir.mkdir()
    return CommandConfig(
        allowed_dir=str(allowed_dir),
        allowed_commands=["echo", "dir"],  # Only allow echo and dir
        allowed_flags=["/b", "--version"],  # Only allow /b and --version
    )


@pytest.fixture
def command_executor(default_command_config: CommandConfig) -> CommandExecutor:
    """Provides a CommandExecutor instance with default config."""
    return CommandExecutor(default_command_config)


@pytest.fixture
def restricted_executor(restricted_command_config: CommandConfig) -> CommandExecutor:
    """Provides a CommandExecutor instance with restricted config."""
    return CommandExecutor(restricted_command_config)


# --- Test Cases for CommandConfig ---


def test_command_config_defaults():
    """Test CommandConfig default command and flag initialization."""
    config = CommandConfig(allowed_dir="./dummy")
    assert config.allowed_commands == ["dir", "type", "cd", "echo", "where", "whoami"]
    assert "/q" in config.allowed_flags  # Check a few defaults
    assert "--help" in config.allowed_flags


def test_command_config_all_override():
    """Test 'all' override for commands and flags."""
    config = CommandConfig(
        allowed_dir="./dummy", allowed_commands=["all"], allowed_flags=["all"]
    )
    assert config.allowed_commands is None
    assert config.allowed_flags is None


# --- Test Cases for CommandExecutor Initialization ---


def test_command_executor_init_success(default_command_config: CommandConfig):
    """Test successful initialization of CommandExecutor."""
    executor = CommandExecutor(default_command_config)
    assert executor.config == default_command_config
    assert os.path.isabs(executor.allowed_dir)
    assert executor.allowed_dir == os.path.abspath(default_command_config.allowed_dir)


def test_command_executor_init_dir_not_exist(tmp_path: Path):
    """Test initialization fails if allowed_dir doesn't exist."""
    non_existent_dir = tmp_path / "i_do_not_exist"
    config = CommandConfig(allowed_dir=str(non_existent_dir))
    with pytest.raises(ValueError, match="Allowed directory does not exist"):
        CommandExecutor(config)


# --- Test Cases for CommandExecutor Validation Methods ---


def test_validate_command_length_success(command_executor: CommandExecutor):
    """Test validation passes for command within length limit."""
    command_executor._validate_command_length("echo hello")  # Should not raise


def test_validate_command_length_failure(command_executor: CommandExecutor):
    """Test validation fails for command exceeding length limit."""
    long_command = "a" * (command_executor.config.max_command_length + 1)
    with pytest.raises(CommandSecurityError, match="exceeds maximum length"):
        command_executor._validate_command_length(long_command)


def test_validate_command_allowed(restricted_executor: CommandExecutor):
    """Test command validation with restrictions."""
    restricted_executor._validate_command("echo test")  # Allowed
    restricted_executor._validate_command("dir /b")  # Allowed command and flag

    with pytest.raises(CommandSecurityError, match="Command 'type' is not allowed"):
        restricted_executor._validate_command(
            "type somefile.txt"
        )  # Command not allowed

    with pytest.raises(CommandSecurityError, match="Flag '/a' is not allowed"):
        restricted_executor._validate_command("dir /a")  # Flag not allowed


def test_validate_command_shell_operators(command_executor: CommandExecutor):
    """Test validation fails for commands with shell operators."""
    operators = [";", "&&", "||", "|", ">", ">>", "<", "%"]
    for op in operators:
        cmd = f"echo hello {op} echo world"
        with pytest.raises(
            CommandSecurityError, match=f"Shell operator '{op}' is not allowed"
        ):
            command_executor._validate_command(cmd)


def test_validate_path_safety_allowed(
    command_executor: CommandExecutor, tmp_path: Path
):
    """Test path safety validation for paths within the allowed directory."""
    allowed_dir = Path(command_executor.allowed_dir)
    file_in_dir = allowed_dir / "test.txt"
    file_in_subdir = allowed_dir / "subdir" / "test.txt"

    # Create the file/dir for path resolution to work
    file_in_dir.touch()
    (allowed_dir / "subdir").mkdir()
    file_in_subdir.touch()

    command_executor._validate_path_safety(
        f"type {file_in_dir.name}"
    )  # Relative path inside
    command_executor._validate_path_safety(
        f"type subdir\\{file_in_subdir.name}"
    )  # Relative sub-path
    command_executor._validate_path_safety(
        f'type "{file_in_dir}"'
    )  # Absolute path inside
    command_executor._validate_path_safety(
        f'type "{file_in_subdir}"'
    )  # Absolute sub-path


def test_validate_path_safety_outside(
    command_executor: CommandExecutor, tmp_path: Path
):
    """Test path safety validation fails for paths outside the allowed directory."""
    # Path outside the allowed directory (e.g., parent directory)
    outside_path = Path(command_executor.allowed_dir).parent / "outside.txt"

    with pytest.raises(CommandSecurityError, match="outside the allowed directory"):
        command_executor._validate_path_safety(f"type ..\\{outside_path.name}")

    with pytest.raises(CommandSecurityError, match="outside the allowed directory"):
        command_executor._validate_path_safety(f'type "{outside_path}"')


# --- Test Cases for CommandExecutor.run_command ---


@pytest.mark.asyncio
@patch("asyncio.create_subprocess_shell")
async def test_run_command_success(
    mock_create_subprocess, command_executor: CommandExecutor
):
    """Test successful command execution via run_command."""
    command = "echo Test Output"

    # Mock the subprocess
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b"Test Output\r\n", b"")
    mock_process.returncode = 0
    mock_create_subprocess.return_value = mock_process

    result = await command_executor.run_command(command)

    assert result == {"stdout": "Test Output\r\n", "stderr": "", "exit_code": 0}
    mock_create_subprocess.assert_called_once_with(
        f"cmd.exe /c {command}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=command_executor.allowed_dir,
    )
    mock_process.communicate.assert_called_once()


@pytest.mark.asyncio
@patch("asyncio.create_subprocess_shell")
async def test_run_command_failure_exit_code(
    mock_create_subprocess, command_executor: CommandExecutor
):
    """Test command execution failure with non-zero exit code."""
    command = "dir non_existent_file"

    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b"", b"File Not Found\r\n")
    mock_process.returncode = 1
    mock_create_subprocess.return_value = mock_process

    result = await command_executor.run_command(command)

    assert result == {"stdout": "", "stderr": "File Not Found\r\n", "exit_code": 1}
    mock_create_subprocess.assert_called_once()
    mock_process.communicate.assert_called_once()


@pytest.mark.asyncio
@patch("asyncio.create_subprocess_shell")
async def test_run_command_timeout(
    mock_create_subprocess, command_executor: CommandExecutor
):
    """Test command execution timeout."""
    command = "timeout 5"
    command_executor.config.command_timeout = 1  # Set short timeout for test

    mock_process = AsyncMock()
    mock_process.communicate.side_effect = asyncio.TimeoutError  # Simulate timeout
    mock_create_subprocess.return_value = mock_process

    with pytest.raises(CommandTimeoutError, match="timed out after 1 seconds"):
        await command_executor.run_command(command)

    mock_create_subprocess.assert_called_once()
    mock_process.communicate.assert_called_once()
    mock_process.kill.assert_called_once()  # Check if process kill was attempted


@pytest.mark.asyncio
async def test_run_command_security_validation_failure(
    restricted_executor: CommandExecutor,
):
    """Test that run_command fails if security validation fails."""
    command = "type secret.txt"  # Assume 'type' is not allowed

    with pytest.raises(CommandSecurityError, match="Command 'type' is not allowed"):
        await restricted_executor.run_command(command)


@pytest.mark.asyncio
@patch("asyncio.create_subprocess_shell", side_effect=OSError("Subprocess error"))
async def test_run_command_subprocess_exception(
    mock_create_subprocess, command_executor: CommandExecutor
):
    """Test handling of unexpected exceptions during subprocess creation/execution."""
    command = "echo hello"

    with pytest.raises(
        CommandExecutionError, match="Command execution failed: Subprocess error"
    ):
        await command_executor.run_command(command)

    mock_create_subprocess.assert_called_once()


# --- Test Cases for get_security_rules ---


def test_get_security_rules(restricted_executor: CommandExecutor):
    """Test retrieving security rules configuration."""
    rules = restricted_executor.get_security_rules()

    assert rules["allowed_directory"] == restricted_executor.allowed_dir
    assert rules["allowed_commands"] == ["echo", "dir"]
    assert rules["allowed_flags"] == ["/b", "--version"]
    assert rules["max_command_length"] == restricted_executor.config.max_command_length
    assert rules["command_timeout"] == restricted_executor.config.command_timeout
