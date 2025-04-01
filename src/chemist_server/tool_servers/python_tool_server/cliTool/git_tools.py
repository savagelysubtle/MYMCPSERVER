"""Git-related tools for the Python Tool Server."""

# Standard library imports
import os
from pathlib import Path
from typing import Any

# Third-party imports
import git

# Application imports - simplified
from chemist_server.config import get_config_instance
from chemist_server.mcp_core.logger import StructuredLogger

# Get configuration instance
config = get_config_instance()

# Configure logger using StructuredLogger
logger = StructuredLogger("chemist_server.tool_servers.cliTool.git_tools")

# Determine workspace/project root - using multiple methods to ensure robustness
WORKSPACE_ROOT = os.environ.get("WORKSPACE_FOLDER")

if WORKSPACE_ROOT and Path(WORKSPACE_ROOT).exists():
    # Use environment variable if available (highest priority)
    PROJECT_ROOT = Path(WORKSPACE_ROOT)
    logger.info(
        f"Using WORKSPACE_FOLDER environment variable for project root: {PROJECT_ROOT}"
    )
elif hasattr(config, "vault_path") and config.vault_path.exists():
    # Use vault_path parent if it exists
    PROJECT_ROOT = config.vault_path.parent
    logger.info(f"Using vault_path parent for project root: {PROJECT_ROOT}")
else:
    # Fall back to current working directory
    PROJECT_ROOT = Path.cwd().resolve()
    logger.info(f"Using current working directory for project root: {PROJECT_ROOT}")

# Initialize Git repository object
try:
    repo = git.Repo(PROJECT_ROOT)
    logger.info(f"Successfully initialized Git repository at {PROJECT_ROOT}")
except git.InvalidGitRepositoryError:
    repo = None
    logger.warning(
        f"Warning: {PROJECT_ROOT} is not a Git repository. Git operations will be unavailable."
    )


async def get_git_status() -> dict[str, Any]:
    """
    Get Git repository status.

    Returns:
        Dictionary with Git status information
    """
    if repo is None:
        logger.warning("Attempted to get git status but no Git repository available")
        return {"error": "Not a Git repository"}

    try:
        # Use GitPython instead of subprocess
        changes = []
        for item in repo.index.diff(None):  # Unstaged changes
            changes.append({"status": "M ", "file": item.a_path})

        for item in repo.index.diff("HEAD"):  # Staged changes
            changes.append({"status": " M", "file": item.a_path})

        for item in repo.untracked_files:  # Untracked files
            changes.append({"status": "??", "file": item})

        # Get current branch
        current_branch = repo.active_branch.name

        result = {
            "current_branch": current_branch,
            "changes": changes,
            "has_changes": len(changes) > 0,
        }

        logger.debug(
            f"Git status retrieved: {current_branch} with {len(changes)} changes"
        )
        return result
    except Exception as e:
        logger.error(f"Git operation failed: {e!s}")
        raise Exception(f"Git operation failed: {e!s}") from e


async def list_branches() -> dict[str, Any]:
    """
    List branches in the Git repository.

    Returns:
        Dictionary with branch information including names and current status
    """
    if repo is None:
        logger.warning("Attempted to list branches but no Git repository available")
        return {"error": "Not a Git repository"}

    try:
        # Use GitPython instead of subprocess
        branches = []
        current_branch_name = repo.active_branch.name

        # Local branches
        for branch in repo.branches:
            branches.append(
                {"name": branch.name, "is_current": branch.name == current_branch_name}
            )

        # Remote branches - check if remotes exist
        if hasattr(repo, "remotes") and repo.remotes:
            try:
                # Origin is the standard remote name, but we should check if it exists
                origin = repo.remotes.origin
                for ref in origin.refs:
                    # Skip HEAD reference
                    if ref.name == "origin/HEAD":
                        continue

                    # Format remote branch name
                    branches.append(
                        {"name": f"remotes/{ref.name}", "is_current": False}
                    )
            except (AttributeError, IndexError):
                # Handle case where origin remote doesn't exist
                logger.warning(
                    "No origin remote found or unable to access remote references"
                )

        logger.debug(f"Retrieved {len(branches)} branches from repository")
        return {"branches": branches, "count": len(branches)}
    except Exception as e:
        logger.error(f"Git operation failed: {e!s}")
        raise Exception(f"Git operation failed: {e!s}") from e


async def search_codebase(
    query: str, file_patterns: list[str] | None = None
) -> dict[str, Any]:
    """
    Search the codebase for the given query.

    Args:
        query: The search query
        file_patterns: Optional list of glob patterns to filter files

    Returns:
        Dictionary with matching files and snippets
    """
    logger.info(f"Searching codebase for: {query}")
    patterns = file_patterns or ["**/*.py", "**/*.md", "**/*.mdc"]
    matches = []

    for pattern in patterns:
        logger.debug(f"Searching with pattern: {pattern}")
        for file_path in PROJECT_ROOT.glob(pattern):
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if query.lower() in content.lower():
                        # Find the matching lines and include some context
                        lines = content.split("\n")
                        line_matches = []

                        for i, line in enumerate(lines):
                            if query.lower() in line.lower():
                                start = max(0, i - 2)
                                end = min(len(lines), i + 3)
                                context = "\n".join(
                                    [f"{j + 1}: {lines[j]}" for j in range(start, end)]
                                )
                                line_matches.append(
                                    {"line_number": i + 1, "context": context}
                                )

                        if line_matches:
                            matches.append(
                                {
                                    "file": str(file_path.relative_to(PROJECT_ROOT)),
                                    "matches": line_matches,
                                }
                            )
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {e}")

    logger.info(f"Found {len(matches)} files containing '{query}'")
    return {"query": query, "match_count": len(matches), "matches": matches}
