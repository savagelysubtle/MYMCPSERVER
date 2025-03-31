---
created: 2025-03-28
updated: 2025-03-30
tags: [documentation, organization, linking]
parent: [[Documentation Structure Guide]]
up: [[_index]]
siblings: [[Metadata and Linking Guide]], [[Creating a New Note]]
---

# Linking Strategy

## Overview

This guide defines how notes are connected to create a robust and useful knowledge graph in our documentation system. Proper linking is essential for maintaining relationships between MCP concepts, implementation details, and development guides.

## Key Points

- Hierarchical navigation uses the `up` link to parent \_index.md files
- Semantic relationships are expressed using typed links
- Links should be meaningful and placed in context
- The typed link format encodes the relationship type

## Link Types

### 1. Hierarchical Directory Links

Connect notes within their organizational hierarchy using \_index.md files:

```markdown
# Standard up link in frontmatter

up: [[../_index]]

# Navigation within content

See the [[../_index|Parent Directory]] for more context.
```

### 2. Typed Relationship Links

Express semantic relationships with typed links in the format `[[Target]](relationship_type)`:

```markdown
# Core relationships

This component [[Authentication System]](implements) the design specification.
This approach [[Base Pattern]](extends) with additional features.
See [[Technical Reference]](references) for more details.

# Decision relationships

We chose this approach based on [[Architecture Decision Record]](based_on_decision).
These requirements are [[Research Findings]](informed_by_research).

# Compositional relationships

This service is [[Overall System]](part_of) the architecture.
The system [[Authentication Service]](contains) as a critical component.

# Sequential relationships

After this, proceed to [[Next Step]](next) in the process.
Return to [[Previous Step]](previous) if needed.
```

### 3. Contextual Placement

Put typed links where they make sense in the document:

```markdown
## Implementation

We designed this component to [[Security Requirements]](implements) while maintaining high performance.

## Dependencies

This module [[Database Service]](depends_on) and requires [[Configuration Manager]](depends_on) to be running.

## Relationships / Links

- [[System Architecture]](part_of) - This component is part of the overall system
- [[Authentication Protocol]](references) - Protocol specifications
```

## Best Practices

### 1. Hierarchical Navigation

- **Always** include the `up` link in frontmatter pointing to parent directory's \_index.md
- Use `parent` to link to the logical parent (which may be different from the directory parent)
- Include key siblings in frontmatter for lateral navigation

### 2. Typed Links in Content

- Use typed links directly in the content where they make contextual sense
- Choose the most specific relationship type from the standardized list
- Provide brief explanation after the typed link for clarity
- Maintain bidirectional relationships for important connections

### 3. Directory Structure Navigation

The repository uses a hierarchical structure with \_index.md files for navigation:

```
docs-obsidian/
├── _index.md
├── mcpKnowledge/
│   ├── _index.md
│   └── core/
│       ├── _index.md
│       └── MCP Architecture.md
└── projects/
    └── myMcpServer/
        ├── _index.md
        └── implementation/
            ├── _index.md
            └── Setup Guide.md
```

- Every note's `up` link must point to its directory's \_index.md
- Each \_index.md file's `up` link points to its parent directory's \_index.md
- This creates an unbroken hierarchical navigation chain

### 4. Relationship Documentation

Include a "Relationships / Links" section in documents with important connections:

```markdown
## Relationships / Links

- [[System Architecture]](part_of) - This component is part of the overall system
- [[Authentication Protocol]](references) - Protocol specifications used
- [[Implementation Phase 2]](next) - Next step in the development process
```

## Official Relationship Types

For a complete list of standardized relationship types and their usage, see the [[Metadata and Linking Guide#Official Typed Link Relationships|Official Typed Link Relationships]] section in the Metadata and Linking Guide.

## Related Documentation

- [[Documentation Structure Guide]] - Overall documentation structure
- [[Metadata and Linking Guide]] - Comprehensive metadata and linking standards
- [[Creating a New Note]] - Step-by-step guide for creating properly linked notes

---

[[_index|← Back to Documentation Guide]]
