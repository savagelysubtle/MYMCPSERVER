---
created: 2025-03-30
updated: 2025-03-30
tags: [folder-note, projects]
parent: [[../_index]]
up: [[../_index]]
contains: [[[myMcpServer/_index]], [[aiChemist/_index]]]
lists:
  [
    {
      'name': 'Active Projects',
      'items':
        [
          '[[myMcpServer/_index|MyMcpServer]]',
          '[[aiChemist/_index|AI Chemist]]',
        ],
    },
  ]
---

# Projects Directory Index

This directory contains documentation related to specific project implementations, each in its own subdirectory.

## Directory Structure

```
projects/
├── _index.md              # This directory index
├── myMcpServer/           # MCP Server implementation
│   └── _index.md          # MCP Server project index
└── aiChemist/             # AI Chemist project
    └── _index.md          # AI Chemist project index
```

## Key Projects

- [[myMcpServer/_index|MyMcpServer]](implements) - MCP Server implementation project
- [[aiChemist/_index|AI Chemist]](implements) - AI Chemist project

## Relationships

- Projects in this directory [[../mcpKnowledge/_index]](implement) the MCP knowledge base concepts
- The [[myMcpServer/_index]](based_on) [[../mcpKnowledge/core/_index]](defines) architecture principles

## Navigation

- Parent: [[../_index|Documentation Root]]
- Siblings: [[../mcpKnowledge/_index|MCP Knowledge]], [[../languages/_index|Languages]]

## Subdirectories

```dataview
LIST
FROM "docs-obsidian/projects" AND #folder-note
SORT file.path ASC
```

## Contained Notes (Dataview)

```dataview
LIST
FROM "docs-obsidian/projects"
WHERE file.name != "_index"
SORT file.name ASC
```

---

_This directory index provides navigation and organization for implementation projects._
