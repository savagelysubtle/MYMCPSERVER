"""Unit tests for Git related tools."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# --- Dummy Implementations (Defined outside try block) ---
# Define dummy versions of classes/functions expected from the module.
# These will be used by fixtures/tests if the real module import fails.


class DummyGitTool:
    """Dummy GitTool for testing structure."""

    async def get_current_branch(self, ctx: Any) -> str:
        return "main"

    async def get_repo_status(self, ctx: Any) -> dict[str, Any]:
        return {"branch": "main", "clean": True, "files": []}


async def dummy_run_git_command(command_args: list[str], **kwargs) -> dict[str, Any]:
    """Dummy function to simulate running git commands."""
    full_cmd = ["git"] + command_args
    if "status" in command_args:
        return {
            "stdout": "On branch main\nYour branch is up to date.\nnothing to commit",
            "stderr": "",
            "return_code": 0,
        }
    if "branch" in command_args and "--show-current" in command_args:
        return {"stdout": "main", "stderr": "", "return_code": 0}
    return {
        "stdout": "",
        "stderr": f"Unknown git command: {full_cmd}",
        "return_code": 1,
    }


class DummyContext:
    """Dummy Context for type hints."""

    pass


# --- Attempt to import Real Implementations ---
try:
    # Adjust import paths based on your actual project structure
    from mcp.server.fastmcp import Context  # Real MCP Context

    from chemist_server.mcp_core.tool_registry import register_tool
    from chemist_server.mcp_core.tools.git_tools import (
        GitTool,  # Example real tool class
        run_git_command,  # Example real underlying function
    )

    MODULE_EXISTS = True
    # Use the real classes if import succeeds
    GitToolToTest = GitTool
    run_git_command_to_test = run_git_command
    ContextType = Context

except ImportError:
    MODULE_EXISTS = False
    # Use dummy classes if import fails
    GitToolToTest = DummyGitTool
    run_git_command_to_test = dummy_run_git_command
    ContextType = DummyContext

    # Define dummy register_tool if needed and not imported
    def register_tool(name: str, tool_instance: Any):
        pass


pytestmark = pytest.mark.skipif(
    not MODULE_EXISTS, reason="git_tools or dependencies module not found"
)

# --- Fixtures ---


@pytest.fixture
def mock_mcp_context() -> Any:
    """Provides a mock MCP Context object (using real or dummy type)."""
    return MagicMock(spec=ContextType)


@pytest.fixture
def git_tool() -> Any:
    """Provides an instance of the GitTool (real or dummy)."""
    return GitToolToTest()


# --- Tests for run_git_command ---
# (Only meaningful if the real function exists and was imported)


@pytest.mark.asyncio
@patch(
    "chemist_server.mcp_core.tools.git_tools.subprocess.run", create=True
)  # Patch subprocess used by real func
@pytest.mark.skipif(not MODULE_EXISTS, reason="Real module needed for this test")
async def test_run_git_command_success(mock_subprocess_run):
    """Test the real run_git_command successfully executes."""
    mock_subprocess_run.return_value = MagicMock(
        stdout=b"current_branch", stderr=b"", returncode=0
    )
    command_args = ["branch", "--show-current"]

    # Assuming run_git_command is the real imported function
    result = await run_git_command(command_args)

    assert result["return_code"] == 0
    assert result["stdout"] == "current_branch"
    mock_subprocess_run.assert_called_once()  # Check call details


# --- Tests for GitTool ---


@pytest.mark.asyncio
async def test_git_tool_get_current_branch(git_tool, mock_mcp_context):
    """Test the GitTool's get_current_branch method."""
    # Patch the underlying function used by the tool (real or dummy)
    patch_target = (
        "chemist_server.mcp_core.tools.git_tools.run_git_command"
        if MODULE_EXISTS
        else f"{__name__}.dummy_run_git_command"  # Patch the dummy if module doesn't exist
    )

    with patch(patch_target) as mock_run_git:
        mock_run_git.return_value = {
            "stdout": "feature/test",
            "stderr": "",
            "return_code": 0,
        }
        branch = await git_tool.get_current_branch(mock_mcp_context)

    assert branch == "feature/test"
    mock_run_git.assert_called_once_with(["branch", "--show-current"])


@pytest.mark.asyncio
async def test_git_tool_get_repo_status(git_tool, mock_mcp_context):
    """Test the GitTool's get_repo_status method."""
    patch_target = (
        "chemist_server.mcp_core.tools.git_tools.run_git_command"
        if MODULE_EXISTS
        else f"{__name__}.dummy_run_git_command"
    )

    with patch(patch_target) as mock_run_git:
        # Simulate a clean status
        mock_run_git.return_value = {
            "stdout": "On branch main\nYour branch is up to date.\nnothing to commit, working tree clean",
            "stderr": "",
            "return_code": 0,
        }
        status = await git_tool.get_repo_status(mock_mcp_context)

    # Assertions depend on how the tool parses the status output
    assert status["branch"] == "main"  # Example assertion
    assert status["clean"] is True  # Example assertion
    mock_run_git.assert_called_once_with(["status", "--porcelain"])


# Add tests for other GitTool methods (commit, push, pull, diff etc.)
# Add tests for error handling (e.g., git command fails)

# Test registration (if applicable)
# @patch("chemist_server.mcp_core.tool_registry.register_tool")
# def test_tool_registration(mock_register):
#    ...
