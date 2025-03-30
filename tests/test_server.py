"""Test script to verify the MCP server package."""

import sys

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    import mymcpserver

    print(f"Successfully imported mymcpserver version {mymcpserver.__version__}")
    print("Package is correctly installed and can be imported!")
except ImportError as e:
    print(f"Failed to import mymcpserver: {e}")
    sys.exit(1)

print("All tests passed!")
