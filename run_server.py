#!/usr/bin/env python
"""Run script for MCP Server.

This script sets up the correct Python path and runs the server.
"""

import sys
from pathlib import Path

# Set up the correct Python path
project_root = Path(__file__).resolve().parent
src_path = project_root / "src"

# Add src to path if not already there
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import and run the server
from src.server import main

if __name__ == "__main__":
    # Run the server
    sys.exit(main())
