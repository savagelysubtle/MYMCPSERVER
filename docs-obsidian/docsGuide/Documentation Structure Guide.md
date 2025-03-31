---
created: 2025-03-30
updated: 2025-03-30
tags: [documentation, guide, structure]
parent: [[../_index]]
up: [[_index]]
siblings: [[Creating a New Note]], [[Knowledge Graph]], [[Linking Strategy]]
---

# Documentation Structure Guide

## Overview

This guide explains the organization of the documentation repository and provides guidelines for maintaining it, including navigation and relationships between documents.

## Directory Structure

The documentation is organized into the following main directories:

### 1. mcpKnowledge/

- Contains all MCP-related research and knowledge
- Includes SDK documentation for both Python and TypeScript
- Structure:
  - core/ - Core MCP concepts and architecture
  - pythonSDK/ - Python SDK documentation
  - typeScriptSDK/ - TypeScript SDK documentation
  - development/ - Development guides and documentation
  - integration/ - Integration documentation
  - reference/ - Reference materials

### 2. projects/

- Project-specific documentation
- Currently includes:
  - myMcpServer/ - MCP server implementation details
    - architecture/ - System design and architecture
    - implementation/ - Implementation details
    - api/ - API documentation

### 3. languages/

- Language-specific knowledge shared across projects
- Contains:
  - python/ - Python best practices, patterns, and guides
    - core-concepts/ - Core Python concepts
    - best-practices/ - Python best practices
    - libraries-frameworks/ - Libraries and frameworks
    - testing/ - Testing methodologies
    - common-error-fixing/ - Common error solutions
    - tools/ - Python tools and utilities
  - typescript/ - TypeScript best practices, patterns, and guides
    - Similar structure to Python

### 4. docsGuide/

- Documentation about the documentation
- Guides for maintaining and organizing content
- Style guides and templates

### Special Directories

#### Organization Directories

- \_index.md files - Directory organization and navigation files present in each significant directory

#### System Directories

- .obsidian/ - Obsidian configuration files
- graph presets/ - Obsidian graph visualization settings

## Hierarchical Organization with \_index.md Files

### 1. Directory Index Files (\_index.md)

Each significant directory must have an `_index.md` file that:

```yaml
---
created: [date]
updated: [date]
tags: [folder-note, category-tag]
parent: [[_index]] # Logical parent (can be higher in hierarchy)
up: [[../_index]] # CRITICAL: Always points to parent directory's _index.md
contains: [] # List of key files in this directory
lists: [] # Optional structured lists of content
---
```

Key components of an \_index.md file:

- Directory description and purpose
- Structure and key contents listing
- Dataview query for listing contained notes
- Navigation links to parent and related directories

### Example Structure with \_index.md

```
docs-obsidian/
├── _index.md
├── mcpKnowledge/
│   ├── _index.md
│   ├── core/
│   │   ├── _index.md
│   │   └── MCP Architecture.md
│   └── pythonSDK/
│       ├── _index.md
│       └── Python SDK Overview.md
└── projects/
    └── myMcpServer/
        ├── _index.md
        └── implementation/
            ├── _index.md
            └── Setup Guide.md
```

This structure provides clear hierarchical navigation through the `up` links in each \_index.md file.

## File Organization Guidelines

### YAML Frontmatter

All notes should include:

```yaml
---
created: [date]
updated: [date]
tags: [relevant-tags]
parent: [[Parent Document]] # Link to the logical parent (can be higher level)
up: [[../_index]] # CRUCIAL: Always link to parent directory's _index.md
siblings: [[doc1]], [[doc2]]
implements: [] # Using typed links in content is preferred to listing here
extends: [] # Using typed links in content is preferred to listing here
references: [] # Using typed links in content is preferred to listing here
related: [] # Using typed links in content is preferred to listing here
---
```

### Linking Strategy

- Use typed links to indicate relationships between documents
- Follow the format: `[[Target Note|Optional Display Text]](relationship_type)`
- Use the standardized relationship types from the Metadata and Linking Guide
- Example: `This component [[Authentication System]](implements) the security requirements`

### Directory Index (\_index.md) Files

Each directory should have an \_index.md file that:

- Describes the purpose of the directory
- Lists key files and subdirectories
- Provides navigation links to parent and related directories
- Includes a dataview query to show contained notes

## Maintenance Procedures

1. New Content

   - Place in appropriate category directory
   - Ensure the directory has an \_index.md file
   - Add proper frontmatter with up link to parent \_index.md
   - Create necessary typed links for relationships
   - Update parent \_index.md if significant content

2. Moving Content

   - Update all links to the content
   - Update the up link to point to new parent \_index.md
   - Maintain relationship links
   - Update parent \_index.md files

3. Deprecating Content
   - Add deprecation notice in frontmatter
   - Update or remove links to the content
   - Document replacement
   - Update parent \_index.md file

## Best Practices

1. File Naming

   - Use PascalCase for file names
   - Be descriptive but concise
   - Use consistent naming patterns

2. Content Organization

   - Keep related content in the same directory
   - Use subdirectories for complex topics
   - Maintain clear hierarchies through \_index.md files
   - Group by logical relationships

3. Linking

   - Always include the up link in frontmatter
   - Use typed links for semantic relationships
   - Keep link paths relative when possible
   - Use the standardized relationship types

4. Metadata

   - Use consistent tags
   - Include creation/update dates
   - Add relevant categories
   - Maintain correct up and parent links

5. Navigation

   - Maintain clear breadcrumb trails through \_index.md files
   - Keep navigation paths current
   - Ensure the up link always points to parent directory's \_index.md
   - Review navigation periodically

6. Relationships
   - Use typed links with standardized relationship types
   - Place typed links where contextually relevant
   - Include Relationships/Links section for explicit connections
   - Ensure bidirectional relationships where appropriate

## Related Documentation

### Guides

- [[Metadata and Linking Guide]] - Detailed metadata and relationship guidelines
- [[Linking Strategy]] - Link types and usage
- [[Creating a New Note]] - Step-by-step guide

### Templates

- [[templates/_index Template|_index Template]] - Template for directory index files
- [[templates/Note Template|Note Template]] - Template for new notes

---

[[_index|← Back to Documentation Guide]]
