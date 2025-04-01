#!/usr/bin/env python3

import json
import os
import sys

# File to store the last used directory
CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "rename_mdc_config.json"
)


def save_directory(directory: str) -> None:
    """
    Save the directory path to a config file for future use.

    Args:
        directory (str): The directory path to save
    """
    config = {"last_directory": directory}
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        print("Directory location saved for future use.")
    except Exception as e:
        print(f"Warning: Could not save directory location: {e}")


def get_saved_directory() -> str | None:
    """
    Get the previously saved directory path from the config file.

    Returns:
        Optional[str]: The saved directory path, or None if not found
    """
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                return config.get("last_directory")
    except Exception as e:
        print(f"Warning: Could not read saved directory location: {e}")
    return None


def get_directory_from_user(saved_directory: str | None = None) -> str:
    """
    Prompt the user for a directory path, with option to use a saved path.

    Args:
        saved_directory (Optional[str], optional): Previously saved directory path

    Returns:
        str: Directory path to use
    """
    if saved_directory:
        use_saved = input(
            f"Use saved directory location: {saved_directory}? (y/n): "
        ).lower()
        if use_saved == "y" or use_saved == "":
            return saved_directory

    # Ask for a new directory path
    while True:
        directory = input("Enter the directory path containing .mdc files: ").strip()

        # Convert to absolute path
        abs_directory = os.path.abspath(directory)

        # Check if the directory exists
        if not os.path.isdir(abs_directory):
            print(f"Directory not found: {abs_directory}")
            continue

        # Save this directory for future use
        save_choice = input("Save this directory for future use? (y/n): ").lower()
        if save_choice == "y" or save_choice == "":
            save_directory(abs_directory)

        return abs_directory


def rename_mdc_to_md(directory: str) -> None:
    """
    Rename all .mdc files to .md files in the specified directory.
    Only processes files in the immediate directory (not subdirectories).

    Args:
        directory (str): Directory containing .mdc files to rename
    """
    # Get the absolute path of the directory
    abs_directory = os.path.abspath(directory)
    print(f"Scanning directory: {abs_directory}")

    # Count for statistics
    files_processed = 0

    # List all files in the directory (non-recursive)
    for filename in os.listdir(abs_directory):
        # Get the full path
        full_path = os.path.join(abs_directory, filename)

        # Skip directories and only process files
        if os.path.isfile(full_path) and filename.lower().endswith(".mdc"):
            # Create the new filename by replacing .mdc with .md
            new_filename = filename[:-4] + ".md"  # Remove .mdc and add .md
            new_full_path = os.path.join(abs_directory, new_filename)

            # Rename the file
            try:
                print(f"Renaming: {filename} -> {new_filename}")
                os.rename(full_path, new_full_path)
                files_processed += 1
            except Exception as e:
                print(f"Error renaming {filename}: {e}")

    print(f"\nConversion complete. {files_processed} files renamed from .mdc to .md")


def main() -> None:
    """
    Main entry point for the renamer script.
    Handles command line arguments and calls the rename function.
    """
    # Check if directory provided as command-line argument
    if len(sys.argv) > 1:
        directory = sys.argv[1]
        print(f"Using command-line specified directory: {directory}")
    else:
        # Try to get saved directory
        saved_directory = get_saved_directory()

        # Get directory from user input
        directory = get_directory_from_user(saved_directory)

    # Run the renaming function
    rename_mdc_to_md(directory)


if __name__ == "__main__":
    main()
