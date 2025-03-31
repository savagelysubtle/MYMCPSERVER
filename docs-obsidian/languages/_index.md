---
created: 2025-03-30
updated: 2025-03-30
tags: [folder-note, languages, development]
parent: [[../_index]]
up: [[../_index]]
contains: [[[python/_index]], [[typescript/_index]]]
lists:
  [
    {
      'name': 'Language Guides',
      'items':
        [
          '[[python/_index|Python Development]]',
          '[[typescript/_index|TypeScript Development]]',
        ],
    },
  ]
---

# Languages Directory

This directory contains language-specific knowledge and best practices that are shared across different projects.

## Directory Structure

```
languages/
├── _index.md         # This directory index
├── python/           # Python development knowledge
│   ├── _index.md     # Python directory index
│   ├── core/         # Core concepts and patterns
│   └── tools/        # Development tools
└── typescript/       # TypeScript development knowledge
    ├── _index.md     # TypeScript directory index
    ├── core/         # Core concepts and patterns
    └── tools/        # Development tools
```

## Language Documentation

### Python Development

- [[python/_index|Python Knowledge Base]](defines) - Python-specific development knowledge
- Core concepts and design patterns
- Development tools and best practices
- Testing strategies and methodologies

### TypeScript Development

- [[typescript/_index|TypeScript Knowledge Base]](defines) - TypeScript-specific development knowledge
- Core concepts and design patterns
- Development tools and best practices
- Testing strategies and methodologies

## Knowledge Organization

### Core Knowledge

Each language section includes:

1. Design Patterns

   - Common patterns and idioms
   - Implementation examples with code
   - Best practices and anti-patterns

2. Development Practices

   - Coding standards and style guides
   - Testing approaches and methodologies
   - Documentation standards

3. Tool Usage
   - Development environments and IDEs
   - Testing frameworks and libraries
   - Build systems and package management

## Relationships

- This directory [[../projects/_index]](informs) implementation projects
- The [[python/_index]](supports) and [[typescript/_index]](supports) the [[../mcpKnowledge/_index]](defines) implementation
- Language knowledge [[../projects/myMcpServer/_index]](used_by) for project development

## Navigation

- Parent: [[../_index|Home]]
- Siblings: [[../mcpKnowledge/_index|MCP Knowledge]], [[../projects/_index|Projects]]

## Child Directories

- [[python/_index|Python Knowledge]]
- [[typescript/_index|TypeScript Knowledge]]

## Tag Groups

### By Language

- #python
- #typescript

### By Topic

- #design-patterns
- #best-practices
- #testing
- #tools

### By Type

- #guide
- #reference
- #example

## Python Resources

- Core: [[python/core/_index|Python Core Concepts]](defines)
- Tools: [[python/tools/_index|Python Development Tools]](implements)
- Testing: [[python/testing/_index|Python Testing]](implements)

## TypeScript Resources

- Core: [[typescript/core/_index|TypeScript Core Concepts]](defines)
- Tools: [[typescript/tools/_index|TypeScript Development Tools]](implements)
- Testing: [[typescript/testing/_index|TypeScript Testing]](implements)

## Subdirectories

```dataview
LIST
FROM "docs-obsidian/languages" AND #folder-note
SORT file.path ASC
```

## Contained Notes (Dataview)

```dataview
LIST
FROM "docs-obsidian/languages"
WHERE file.name != "_index"
SORT file.name ASC
```

---

_This directory index provides organization and navigation for language-specific knowledge._
