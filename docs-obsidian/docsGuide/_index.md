---
created: 2025-03-30
updated: 2025-03-30
tags: [folder-note, documentation, guide]
parent: [[../_index]]
up: [[../_index]]
contains:
  [
    [[Documentation Structure Guide]],
    [[Creating a New Note]],
    [[Knowledge Graph]],
    [[Linking Strategy]],
    [[Metadata and Linking Guide]],
    [[templates/_index]],
  ]
lists:
  [
    {
      'name': 'Core Guides',
      'items':
        ['[[Documentation Structure Guide]]', '[[Metadata and Linking Guide]]'],
    },
    {
      'name': 'Process Guides',
      'items': ['[[Creating a New Note]]', '[[Linking Strategy]]'],
    },
  ]
---

# Documentation Guide Directory

This directory contains guides and templates for maintaining the documentation system, including structure, organization, and best practices.

## Directory Structure

```
docsGuide/
├── _index.md                       # This directory index
├── Documentation Structure Guide.md # Overall structure
├── Creating a New Note.md           # Note creation process
├── Knowledge Graph.md               # Graph organization
├── Linking Strategy.md             # Linking guidelines
├── Metadata and Linking Guide.md   # Metadata standards
└── templates/                      # Document templates
    ├── _index.md                   # Templates directory index
    ├── _index Template.md          # Directory index template
    └── Note Template.md            # Standard note template
```

## Documentation Components

### Core Documentation

1. Structure and Organization

   - [[Documentation Structure Guide]] (implements) - Overall documentation structure
   - [[Knowledge Graph]] (references) - Knowledge graph structure

2. Metadata and Relationships

   - [[Metadata and Linking Guide]] (implements) - Metadata standards
   - [[Linking Strategy]] (implements) - Linking guidelines

3. Process Guides
   - [[Creating a New Note]] (implements) - Note creation workflow
   - [[templates/_index]] (contains) - Document templates

## Organization Methods

### 1. Directory Index Files

- Purpose: Directory organization and navigation
- Implementation: \_index.md files in each significant directory
- Navigation: Hierarchical with `up` links to parent \_index.md files
- Example: This file is the directory index for docsGuide/

### 2. Typed Relationships

- Purpose: Semantic organization
- Implementation: Typed links like [[Metadata and Linking Guide]](implements)
- Categories: Implements, extends, references, etc.
- Usage: Content discovery and semantic relationships

## Navigation

### Parent Directory

- Parent: [[../_index|Home]]

### Child Directories

- [[templates/_index|Templates]]

### Related Directories

- [[../mcpKnowledge/_index|MCP Knowledge]]
- [[../projects/_index|Projects]]

## Tag Groups

### By Purpose

- #guide
- #template
- #process

### By Topic

- #structure
- #metadata
- #organization

### By Type

- #folder-note
- #documentation

## Relationships

### Implements

The documentation guides implement best practices for:

- [[../mcpKnowledge/_index|MCP Documentation]] (used_by)
- [[../projects/_index|Project Documentation]] (used_by)
- [[../languages/_index|Language Documentation]] (used_by)

## Usage Guidelines

### Creating Documentation

1. Choose appropriate template from [[templates/_index|Templates]]
2. Follow structure guidelines in [[Documentation Structure Guide]]
3. Add proper metadata as specified in [[Metadata and Linking Guide]]
4. Create typed relationships following [[Linking Strategy]]

### Maintaining Documentation

1. Update relationships using typed links
2. Review organization via \_index.md files
3. Maintain the hierarchical `up` link navigation
4. Verify metadata matches the current standards

## Contained Notes (Dataview)

```dataview
LIST
FROM "docs-obsidian/docsGuide"
WHERE file.name != "_index"
SORT file.name ASC
```

---

_This directory index provides organization and guidance for the documentation system._
