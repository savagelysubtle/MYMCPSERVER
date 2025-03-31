---
created: 2025-03-30
updated: 2025-03-30
tags: [documentation, guide, metadata, linking]
parent: [[Documentation Structure Guide]]
up: [[_index]]
siblings: [[Creating a New Note]], [[Knowledge Graph]], [[Linking Strategy]]
---

# Metadata and Linking Guide

## Frontmatter Standards

### Required Metadata

Every note should include the following frontmatter:

```yaml
---
created: [creation-date]
updated: [last-update-date]
tags: [relevant-tags]
parent: [[Parent MOC or Index]] # Link to the logical parent
up: [[Path/To/Parent/_index]] # CRUCIAL: Link to parent directory's _index.md
siblings: [[related-doc-1]], [[related-doc-2]]
---
```

### Breadcrumb Fields

1. **Hierarchical Navigation**

   - `parent` - Link to the logical parent document (usually an \_index.md or related conceptual parent)
   - `up` - Upward navigation (always points to parent directory's \_index.md)
   - `siblings` - Related documents at the same level

2. **Relationship Types**
   All relationship fields should use the standardized typed link format within the content: `[[Target Note|Optional Display Text]](relationship_type)`

## Official Typed Link Relationships

### Core Relationships

- `implements` - Indicates this document describes an implementation of a concept or design specified in the target document

  - Example: A code documentation [[Design Specification]](implements) because it realizes the design

- `extends` - Indicates this document extends or enhances concepts from the target document

  - Example: This pattern [[Base Pattern]](extends) with additional features

- `references` - Indicates this document references or relies on information in the target document

  - Example: See [[Technical Specification]](references) for more details

- `related` - Indicates a general relationship to another document without a more specific type
  - Example: Also check [[Related Topic]](related) for complementary information

### Decision-based Relationships

- `based_on_decision` - Indicates this document is based on a decision documented in the target document

  - Example: This approach follows [[Architecture Decision Record 12]](based_on_decision)

- `informed_by_research` - Indicates this document is informed by research in the target document
  - Example: These requirements were [[Research Findings]](informed_by_research)

### Compositional Relationships

- `part_of` - Indicates this document is a component or part of a larger system documented in the target

  - Example: This component is [[System Architecture]](part_of)

- `contains` - Indicates this document contains or includes the target document
  - Example: This system [[Component X]](contains) as a critical element

### Sequential Relationships

- `next` - Indicates the target document is the next in a sequence

  - Example: Proceed to [[Implementation Phase 2]](next)

- `previous` - Indicates the target document is the previous in a sequence
  - Example: Return to [[Requirements Document]](previous)

### Dependency Relationships

- `depends_on` - Indicates this document depends on content in the target document

  - Example: This component [[Authentication Service]](depends_on)

- `prerequisite_for` - Indicates this document is a prerequisite for the target document
  - Example: This setup is [[Advanced Configuration]](prerequisite_for)

### Semantic Relationships

- `example_of` - Indicates this document provides an example of the target document

  - Example: This code is an [[Design Pattern]](example_of)

- `contradicts` - Indicates this document contradicts or provides an alternative to the target
  - Example: This approach [[Alternative Method]](contradicts) for specific cases

## Using Typed Links

### Syntax

Use the following format for typed links:

```markdown
[[Target Note|Optional Display Text]](relationship_type)
```

### Context

1. Place typed links directly in the content where the relationship is contextually relevant
2. Use the "Relationships / Links" section for additional explicit connections
3. Always ensure the relationship type accurately reflects the actual relationship

### Examples

```markdown
## Implementation Details

This component [[Authentication System]](implements) the security requirements and [[Logging Framework]](depends_on) for audit trails.

## Relationships / Links

- [[System Architecture]](part_of) - This component is part of the overall system
- [[Security Requirements]](references) - Referenced security standards
- [[Component Interface]](next) - Next document in the implementation guide
```

## Directory Structure Navigation

### Hierarchical Structure with \_index.md

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
    ├── _index.md
    └── myMcpServer/
        ├── _index.md
        └── architecture/
            ├── _index.md
            └── System Overview.md
```

## Navigation Management

### 1. Breadcrumb Navigation

Use frontmatter fields to create explicit navigation paths:

```yaml
up: [[../_index]] # Always point to parent directory's _index.md
siblings: [[File1]], [[File2]] # Related files at same level
```

### 2. Relationship Navigation

Use typed relationships to create semantic connections:

```markdown
This component [[Design Doc]](implements) the specification.
```

### 3. Automatic Collection

Use dataview queries to collect related notes:

````markdown
Notes linking to this document:

```dataview
list from [[Metadata and Linking Guide]] and !outgoing([[Metadata and Linking Guide]])
```
````

## Best Practices

1. **Consistent Naming**

   - Use PascalCase for file names
   - Be descriptive but concise
   - Include category prefixes when helpful

2. **Link Maintenance**

   - Update links when moving files
   - Check for broken links regularly
   - Use relative paths when possible

3. **Metadata Updates**

   - Keep creation dates accurate
   - Update modification dates
   - Maintain relevant tags
   - Keep breadcrumbs current

4. **Content Organization**

   - Link to relevant \_index.md files
   - Use consistent headings
   - Include navigation links
   - Maintain clear hierarchies

5. **Relationship Management**
   - Use appropriate relationship types from the official list
   - Keep relationships bidirectional when possible
   - Document relationship context
   - Review relationships periodically

## Related Guides

- [[Documentation Structure Guide]] - Overall documentation structure
- [[templates/_index Template|_index Template]] - Template for directory index files
- [[templates/Note Template|Note Template]] - Template for new notes
- [[Knowledge Graph]] - Understanding the knowledge graph

---

[[_index|← Back to Documentation Guide]]
