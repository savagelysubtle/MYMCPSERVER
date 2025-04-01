"""Integration tests for end-to-end CLI command execution."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Assuming the main entry point script or module
# Adjust this based on your project structure (e.g., src/chemist_server/__main__.py)
MAIN_SCRIPT_PATH = (
    Path(__file__).parent.parent.parent / "src" / "chemist_server" / "__main__.py"
)
PYTHON_EXECUTABLE = sys.executable


# Helper function to run the main script as a subprocess
def run_main_script(args: list[str]) -> subprocess.CompletedProcess:
    """Runs the main chemist_server script with given arguments."""
    command = [PYTHON_EXECUTABLE, str(MAIN_SCRIPT_PATH)] + args
    # Ensure the script path exists
    if not MAIN_SCRIPT_PATH.exists():
        pytest.skip(f"Main script not found at {MAIN_SCRIPT_PATH}")

    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,  # Don't raise exception on non-zero exit
        timeout=30,  # Add a reasonable timeout
        cwd=MAIN_SCRIPT_PATH.parent.parent.parent,  # Run from project root
    )


def test_cli_help_command():
    """Test running the CLI with --help argument."""
    result = run_main_script(["--help"])

    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert "--help" in result.stdout
    # Add more specific checks based on expected help output
    assert "--config" in result.stdout  # Example: check for config option


def test_cli_invalid_option():
    """Test running the CLI with an invalid option."""
    result = run_main_script(["--invalid-option-xyz"])

    assert result.returncode != 0  # Should fail
    assert "error: unrecognized arguments" in result.stderr.lower()


@patch("chemist_server.server.anyio.run")  # Patch the main execution function
def test_cli_basic_run_starts_services(mock_anyio_run):
    """Test that a basic CLI invocation attempts to start services."""
    # Example: Run without specific commands, assuming it starts the server
    result = run_main_script([])

    # Check if the script tried to run the main service loop
    mock_anyio_run.assert_called_once()
    # Check the return code (might be 0 if anyio.run was mocked successfully)
    # or non-zero if startup failed before the mock
    # assert result.returncode == 0


@patch("chemist_server.config.load_and_get_config")
def test_cli_config_option(mock_load_config):
    """Test passing a custom config file via CLI."""
    mock_load_config.return_value = MagicMock()  # Mock the config object
    custom_config_path = "/path/to/dummy/config.yaml"

    result = run_main_script(["--config", custom_config_path])

    # Check if load_and_get_config was called with the custom path
    # This depends on how CLI args are parsed and passed to load_and_get_config
    # Example: Assuming args are passed as a dict
    args_dict = mock_load_config.call_args[0][0]
    assert args_dict.get("config") == custom_config_path
    # assert result.returncode == 0 # If mocking prevents actual run


# Add more tests for specific CLI subcommands or arguments:
# - Test running with a specific tool server mode
# - Test passing logging level overrides
# - Test behavior with missing required arguments

# Assuming MagicMock is imported from unittest.mock
from unittest.mock import MagicMock

# Assuming the rest of the file is unchanged
# ...
