# MYMCPSERVER

A MCP server implementation for Obsidian integration that provides tools for managing and interacting with Obsidian vaults through the Model Context Protocol (MCP).

## Features

- Note management (create, read, update)
- Note searching and listing
- Template support
- Backlink tracking
- Frontmatter handling
- Async operations

## Requirements

- Python >= 3.13 as it uses AIChemistCodex and that relies on the latest version of Python
- MCP >= 0.1.0
- PyYAML >= 6.0.1

## Installation

```bash
uv add PyYAML
```

## Usage

Run the server:

```bash
python -m mymcpserver
```
