"""
Scripts package for utility scripts.

This package contains various utility scripts for the MCP server project.
"""

__version__ = "0.1.0"

from scripts.renamer.renamer import main  # Re-export main function

# Make the main function available when importing the package
__all__ = ["main"]
