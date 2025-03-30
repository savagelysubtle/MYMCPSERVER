---
created: 2025-03-30
tags: [documentation, guide, metadata, linking]
parent: [[Documentation Structure Guide]]
up: [[Documentation Structure Guide]]
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
parent: [[parent-MOC]]
up: [[parent-document]]
siblings: [[related-doc-1]], [[related-doc-2]]
---
```

### Breadcrumb Fields

1. **Hierarchical Navigation**
   - `parent` - Direct parent document (usually an MOC)
   - `up` - Upward navigation (can be different from parent)
   - `siblings` - Related documents at the same level

2. **Relationship Types**
   - `implements` - Implementation of a concept
   - `extends` - Extension or enhancement of another document
   - `related` - General relationship to other documents
   - `next` - Next document in a sequence
   - `previous` - Previous document in a sequence

Example with relationships:

```yaml
---
created: 2025-03-30
tags: [implementation, python]
parent: [[Python MOC]]
up: [[Development Guide]]
siblings: [[Testing Guide]], [[Deployment Guide]]
implements: [[Design Specification]]
next: [[Implementation Phase 2]]
previous: [[Requirements Document]]
---
```

### Tag Categories

1. Content Type Tags
   - mcp
   - python
   - typescript
   - project
   - guide
   - documentation

2. Topic Tags
   - architecture
   - implementation
   - development
   - testing
   - deployment

3. Status Tags
   - draft
   - review
   - deprecated
   - current

## Linking Conventions

### Relative vs. Absolute Paths

1. Within Same Category

   ```markdown
   [[Tool Management]] - Same directory
   [[../core/MCP Architecture]] - Parent directory
   [[./implementation/Setup Guide]] - Child directory
   ```

2. Across Categories

   ```markdown
   [[../../mcpKnowledge/core/MCP Architecture]]
   [[../../languages/python/Python MOC]]
   [[../../projects/myMcpServer/Project MOC]]
   ```

### Link Text

Use descriptive link text:

```markdown
[[MCP Architecture|Core MCP Architectural Principles]]
[[Python MOC|Python Development Guide]]
```

### Typed Links

Use typed links to indicate relationship types:

```markdown
[[Design Specification|Design]] (implements)
[[Core Concept|Concept]] (extends)
[[Related Topic|Topic]] (related)
```

## Directory Structure Navigation

### MCP Knowledge

```
mcpKnowledge/
├── core/
├── pythonSDK/
├── typeScriptSDK/
└── integration/
```

### Project Documentation

```
projects/
└── myMcpServer/
    ├── architecture/
    ├── implementation/
    └── mcpPlanning/
```

### Language Knowledge

```
languages/
├── python/
│   ├── core/
│   └── testing/
└── typescript/
    ├── core/
    └── testing/
```

## Navigation Management

### 1. Breadcrumb Navigation

Use frontmatter fields to create explicit navigation paths:

```yaml
up: Navigate to parent/higher level
siblings: Navigate laterally
next/previous: Navigate sequentially
```

### 2. Relationship Navigation

Use typed relationships to create semantic connections:

```yaml
implements: Connect to specifications
extends: Connect to base concepts
related: Connect to relevant content
```

### 3. Automatic Collection

Use dataview queries to collect related notes:

```markdown
Notes linking to this document:
```dataview
list from [[Metadata and Linking Guide]] and !outgoing([[Metadata and Linking Guide]])
```

```

### 4. Manual References

Add "Related Content" sections:
```markdown
## Related Content
- [[Other Guide]] - Brief description
- [[Another Document]] - Brief description
```

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
   - Link to relevant MOCs
   - Use consistent headings
   - Include navigation links
   - Maintain clear hierarchies

5. **Relationship Management**
   - Use appropriate relationship types
   - Keep relationships bidirectional
   - Document relationship context
   - Review relationships periodically

## Related Guides

- [[Documentation Structure Guide]] - Overall documentation structure
- [[MOC Template]] - Template for Maps of Content
- [[Note Template]] - Template for new notes
- [[Knowledge Graph]] - Understanding the knowledge graph

---

[[Documentation Structure Guide|← Back to Documentation Guide]]
