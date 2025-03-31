"""Direct module entry point for the MCP server."""

import os
import sys
from pathlib import Path

# Ensure our parent directory is in the path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

if __name__ == "__main__":
    # Write to a file before anything else to confirm we got here
    try:
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        with open("logs/main_executed.log", "w") as f:
            f.write(f"Main module executed at {os.path.dirname(__file__)}\n")
            f.write(f"Python path: {sys.path}\n")
            f.write(f"Current directory: {os.getcwd()}\n")
    except Exception as e:
        print(f"Error writing startup log: {e}", file=sys.stderr)

    # Import and run the main function
    try:
        from chemist_server.server import main

        sys.exit(main())
    except Exception as e:
        # Try to log to a file directly
        try:
            with open("logs/main_error.log", "w") as f:
                f.write(f"Failed to run main: {e}\n")
                import traceback

                f.write(traceback.format_exc())
        except Exception:
            pass  # Can't do much if this fails too

        print(f"FATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)
