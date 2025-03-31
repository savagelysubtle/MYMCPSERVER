---
created: 2025-03-30
updated: 2025-03-30
tags: [folder-note, mcp, knowledge-base]
parent: [[../_index]]
up: [[../_index]]
contains:
  [
    [[core/_index]],
    [[pythonSDK/_index]],
    [[typeScriptSDK/_index]],
    [[development/_index]],
    [[integration/_index]],
    [[reference/_index]],
  ]
lists:
  [
    {
      'name': 'Core Concepts',
      'items':
        [
          '[[core/_index|Core Concepts]]',
          '[[core/MCP Architecture]]',
          '[[core/MCP Central Hub]]',
          '[[core/Tool Management]]',
        ],
    },
    {
      'name': 'SDK Documentation',
      'items':
        [
          '[[pythonSDK/_index|Python SDK]]',
          '[[typeScriptSDK/_index|TypeScript SDK]]',
        ],
    },
  ]
---

# MCP Knowledge Directory

This directory contains all MCP-related knowledge and documentation, organized into distinct categories.

## Directory Structure

```
mcpKnowledge/
├── _index.md       # This directory index
├── core/           # Core MCP concepts
├── pythonSDK/      # Python SDK documentation
├── typeScriptSDK/  # TypeScript SDK documentation
├── development/    # Development guides
├── integration/    # Integration documentation
└── reference/      # Reference materials
```

## Content Categories

### Core Knowledge

- Architecture and design principles
- Central hub functionality
- Tool management system

### SDK Documentation

- Python implementation guides
- TypeScript implementation guides
- SDK usage examples

### Development Resources

- Implementation guides
- Configuration examples
- Debugging information

### Integration Guides

- Cursor integration
- IDE integration
- API integration

### Reference Materials

- Technical specifications
- API documentation
- Configuration references

## Navigation

### Parent Directory

- Parent: [[../_index|Home]]

### Child Directories

- [[core/_index|Core Concepts]]
- [[pythonSDK/_index|Python SDK]]
- [[typeScriptSDK/_index|TypeScript SDK]]
- [[development/_index|Development]]
- [[integration/_index|Integration]]
- [[reference/_index|Reference]]

### Related Directories

- [[../projects/_index|Projects]](related)
- [[../projects/myMcpServer/_index|MCP Server Project]](implements)
- [[../languages/_index|Language Knowledge]](related)

## Tag Groups

### By Topic

- #mcp-architecture
- #mcp-implementation
- #mcp-integration

### By Type

- #concept
- #guide
- #reference

### By Status

- #stable
- #draft
- #deprecated

## Relationships

- This directory [[../projects/myMcpServer/_index]](informs) the MCP Server implementation
- The [[core/_index]](defines) core MCP architecture concepts
- [[pythonSDK/_index]](implements) and [[typeScriptSDK/_index]](implements) provide language-specific API implementations

## Contained Documentation

```dataview
LIST
FROM "docs-obsidian/mcpKnowledge"
WHERE file.name != "_index"
SORT file.name ASC
```

## Subdirectories

```dataview
LIST
FROM "docs-obsidian/mcpKnowledge" AND #folder-note
SORT file.path ASC
```

---

_This directory index provides navigation and organization for the MCP Knowledge directory._
