"""MCP Server module wrapper.

This file serves as a wrapper to import the main server functionality.
"""

import sys
from pathlib import Path

# Get project root directory
project_root = Path(__file__).resolve().parent.parent.parent
src_dir = project_root / "src"

# Add project root and src to Python path if not already there
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import the main server functions
from server import main, parse_args, run_services

__all__ = ["main", "parse_args", "run_services"]
