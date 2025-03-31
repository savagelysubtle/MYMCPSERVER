---
created: 2025-03-30
updated: 2025-03-30
tags: [folder-note, project, myMcpServer]
parent: [[../_index]]
up: [[../_index]]
contains: [[[architecture/_index]], [[implementation/_index]], [[api/_index]]]
lists:
  [
    {
      'name': 'Key Components',
      'items':
        [
          '[[architecture/_index|Architecture]]',
          '[[implementation/_index|Implementation]]',
          '[[api/_index|API]]',
        ],
    },
  ]
---

# MyMcpServer Project Directory Index

This directory contains documentation related to the MyMcpServer project implementation, a modular and extensible MCP (Machine Comprehension Platform) system that connects AI clients with specialized tool servers.

## Directory Structure

```
myMcpServer/
├── _index.md                 # This directory index
├── architecture/             # Architecture documentation
│   ├── _index.md             # Architecture directory index
│   ├── System Overview.md    # High-level system architecture
│   ├── Component Design.md   # Component architecture details
│   └── logging-centralization.md # Logging design
├── implementation/           # Implementation documentation
│   ├── _index.md             # Implementation directory index
│   ├── core/                 # Core implementation details
│   ├── transport/            # Transport layer details
│   ├── adapter/              # Adapter implementation
│   └── Server Configuration.md # Server configuration guide
└── api/                      # API documentation
    ├── _index.md             # API directory index
    ├── core_api.md           # Core API reference
    └── tool_api.md           # Tool API reference
```

## Key Components

- [[architecture/_index|Architecture]](defines) - System architecture and design documentation

  - [[architecture/System Overview]](defines) - Overall system structure
  - [[architecture/Component Design]](extends) - Component architecture details
  - [[architecture/logging-centralization]](implements) - Logging system design

- [[implementation/_index|Implementation]](implements) - Implementation details organized by component layers

  - [[implementation/core/_index]](implements) - Core system implementation
  - [[implementation/transport/_index]](implements) - Communication layer implementation
  - [[implementation/adapter/_index]](implements) - Tool adapter implementation
  - [[implementation/Server Configuration]](documents) - Server configuration guide

- [[api/_index|API]](defines) - API documentation and specifications
  - [[api/core_api]](defines) - Core API specifications
  - [[api/tool_api]](defines) - Tool API specifications

## Relationships

- This project [[../../mcpKnowledge/core/_index]](implements) the MCP architecture
- The implementation is [[../../mcpKnowledge/pythonSDK/_index]](based_on) the Python SDK
- [[architecture/_index]](defines) the structure that [[implementation/_index]](implements)
- [[api/_index]](defines) interfaces that [[implementation/_index]](exposes)

## Navigation

- Parent: [[../_index|Projects]]
- Siblings: [[../aiChemist/_index|AI Chemist]]
- Related Knowledge:
  - [[../../mcpKnowledge/core/_index|MCP Core Concepts]](based_on)
  - [[../../mcpKnowledge/development/_index|MCP Development]](informed_by)
  - [[../../languages/python/_index|Python Development]](uses)

## Subdirectories

```dataview
LIST
FROM "docs-obsidian/projects/myMcpServer" AND #folder-note
SORT file.path ASC
```

## Contained Notes (Dataview)

```dataview
LIST
FROM "docs-obsidian/projects/myMcpServer"
WHERE file.name != "_index"
SORT file.name ASC
```

---

_This directory index provides navigation and organization for the MyMcpServer project documentation._
