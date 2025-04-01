#!/usr/bin/env python3
"""
Entry point for the renamer script.
This allows direct execution with: uv run scripts/renamer_run.py
"""

from scripts.renamer.renamer import main as renamer_main


def main():
    """Entry point for the renamer script."""
    renamer_main()


if __name__ == "__main__":
    main()
