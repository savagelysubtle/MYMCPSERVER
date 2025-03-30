---
created: 2025-03-30
tags: [documentation, guide, structure]
up: [[Home]]
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
  - pythonSDK/ - Python SDK documentation
  - typeScriptSDK/ - TypeScript SDK documentation
  - core/ - Core MCP concepts and architecture

### 2. projects/

- Project-specific documentation
- Currently includes:
  - myMcpServer/ - MCP server implementation details
  - aiChemist/ - Reserved for future AI chemist project

### 3. languages/

- Language-specific knowledge shared across projects
- Contains:
  - python/ - Python best practices, patterns, and guides
  - typeScript/ - TypeScript best practices, patterns, and guides

### 4. docsGuide/

- Documentation about the documentation
- Guides for maintaining and organizing content
- Style guides and templates

### Special Directories

#### Organization Directories

- tags/ - Tag-based navigation and organization
- lists/ - List-based relationships and sequences
- _index.md files - Directory organization and navigation

#### System Directories

- Excalidraw/ - Obsidian drawing plugin files
- graph presets/ - Obsidian graph visualization settings

### 5. userDump/

- Temporary storage for future content to be indexed
- Content here should be reviewed and moved to appropriate locations

## Organization Methods

### 1. Folder Notes

Each significant directory should have a `_index.md` file that:

```yaml
---
created: [date]
updated: [date]
tags: [folder-note, category]
parent: [[parent-directory/_index]]
up: [[parent-directory/_index]]
contains: [
  [[file1]],
  [[file2]]
]
---
```

Key components:

- Directory structure explanation
- Content categories
- Navigation paths
- Relationship definitions

### 2. Tag Notes

Tag-based organization in tags/_index.md:

```yaml
---
tags: [tag-note, organization]
parent: [[Home]]
up: [[Home]]
---
```

Key features:

- Tag hierarchies
- Content collections
- Tag relationships
- Usage guidelines

### 3. List Notes

List-based organization in lists/_index.md:

```yaml
---
tags: [list-note, organization]
parent: [[Home]]
up: [[Home]]
---
```

Types of lists:

- Implementation sequences
- Component hierarchies
- Dependency relationships
- Navigation paths

## File Organization Guidelines

### YAML Frontmatter

All notes should include:

```yaml
---
created: [date]
updated: [date]
tags: [relevant-tags]
parent: [[parent-MOC]]
up: [[parent-document]]
siblings: [[doc1]], [[doc2]]
implements: [[concept]]  # Optional
extends: [[base]]       # Optional
related: [[doc3]]       # Optional
next: [[next-doc]]      # Optional
previous: [[prev-doc]]  # Optional
---
```

### Linking Strategy

- Use relative links within same category
- Use full paths when linking across categories
- Include relationship type in links
- Example: `[[Design Doc|Design]] (implements)`

### MOC (Map of Content) Files

Each major section should have an MOC file that:

- Lists all relevant content
- Provides navigation structure
- Defines relationship hierarchies
- Uses dataview queries for automatic collection
- Maintains explicit relationships

## Maintenance Procedures

1. New Content
   - Place in appropriate category directory
   - Update relevant MOC files
   - Add proper frontmatter with relationships
   - Create necessary backlinks
   - Update folder notes

2. Moving Content
   - Update all backlinks
   - Update MOC references
   - Maintain file history
   - Update folder notes
   - Preserve relationships

3. Deprecating Content
   - Add deprecation notice in frontmatter
   - Update or remove backlinks
   - Document replacement
   - Update folder notes
   - Update relationship references

## Best Practices

1. File Naming
   - Use PascalCase for file names
   - Be descriptive but concise
   - Include category prefixes when helpful

2. Content Organization
   - Keep related content together
   - Use subdirectories for complex topics
   - Maintain clear hierarchies
   - Group by relationship types

3. Linking
   - Create meaningful connections
   - Use bidirectional links
   - Keep link paths relative when possible
   - Use typed links appropriately

4. Metadata
   - Use consistent tags
   - Include creation/update dates
   - Add relevant categories
   - Maintain relationship metadata

5. Navigation
   - Maintain clear breadcrumb trails
   - Keep navigation paths current
   - Update relationship links
   - Review navigation periodically

6. Relationships
   - Use appropriate relationship types
   - Keep relationships bidirectional
   - Document relationship context
   - Review relationships regularly

## Related Documentation

### Guides

- [[Metadata and Linking Guide]] - Detailed metadata guidelines
- [[MOC Concept]] - Understanding Maps of Content
- [[Knowledge Graph]] - Knowledge graph structure

### Templates

- [[templates/MOC Template|MOC Template]] - Template for Maps of Content
- [[templates/Note Template|Note Template]] - Template for new notes

### Examples

- [[Linking Strategy]] - Link types and usage
- [[Creating a New Note]] - Step-by-step guide

---

_This guide should be updated as the documentation structure evolves._
