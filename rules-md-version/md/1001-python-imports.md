---
description: Organize Python imports in the recommended order with proper grouping and formatting
globs: 'src/**/*.py'
alwaysApply: true
---

<aiDecision>
  description: Organize Python imports in the recommended order with proper grouping and formatting
  globs: "src/**/*.py"
  alwaysApply: true
</aiDecision>

# Python Import Organization

<context>
  Use when importing modules in Python files to maintain consistent organization
</context>

<requirements>
  <requirement>Group imports into sections: standard library, third-party, application-specific</requirement>
  <requirement>Sort imports alphabetically within each section</requirement>
  <requirement>Use absolute imports for cross-domain boundaries</requirement>
  <requirement>Use relative imports only for closely related modules within same domain</requirement>
  <requirement>Avoid wildcard imports (from module import *)</requirement>
  <requirement>Include type hints when importing types</requirement>
  <requirement>Avoid circular dependencies between modules</requirement>
  <requirement>Place imports after docstrings but before module-level code</requirement>
</requirements>

<examples>
  <good-example>
    <title>Properly Organized Imports with Type Hints</title>
    <code>
"""Module for handling file metadata extraction and analysis.

This module provides utilities to extract and analyze metadata from different
file types in the Aichemist Codex system.
"""

from **future** import annotations

**all** = ['MetadataExtractor', 'FileTypeDetector']
**version** = '0.1.0'

# Standard library imports

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Set, Tuple, Union, TypeVar, cast

# Third-party imports

import magic
import yaml
from pydantic import BaseModel, Field, validator

# Application imports (absolute)

from the_aichemist_codex.backend.domain.models.file import File, FileType
from the_aichemist_codex.backend.domain.repositories.metadata_repository import MetadataRepository

# Local/related imports (relative)

from .analyzers import ContentAnalyzer
from ..common.utils import generate_hash, safe_read_file
</code>
</good-example>

  <bad-example>
    <title>Problematic Import Organization</title>
    <code>

import json, yaml, os, sys # Imports on same line
from pathlib import Path
import logging
from .utils import \* # Wildcard import
from the_aichemist_codex.backend.file_manager import FileMover
import magic # Third-party mixed with standard library

# Circular dependency

from .other_module import process_file # other_module imports from this file
</code>
</bad-example>
</examples>

<guidance>
  <step>Start with any __future__ imports</step>
  <step>Add any module-level dunder attributes (__all__, __version__, etc.)</step>
  <step>Group standard library imports alphabetically</step>
  <step>Add a blank line, then group third-party library imports alphabetically</step>
  <step>Add a blank line, then add application imports (absolute paths)</step>
  <step>Add a blank line, then add local/related imports (relative paths)</step>
  <step>Use type hints in imports when importing for type annotations</step>
  <step>Ensure no circular dependencies exist between modules</step>
</guidance>

<rationale>
  <point>Consistent import organization improves readability and maintainability</point>
  <point>Proper import structure helps prevent circular dependencies</point>
  <point>Type hints in imports improve static type checking</point>
  <point>Explicit imports make dependencies clear and aid tooling</point>
  <point>Following PEP 8 standards ensures code consistency</point>
</rationale>
