---
created: 2025-03-28
updated: 2025-03-30
tags: [documentation, organization, linking]
parent: [[Documentation Structure Guide]]
---

# Linking Strategy

## Overview

This guide defines how notes are connected to create a robust and useful knowledge graph in our documentation system. Proper linking is essential for maintaining relationships between MCP concepts, implementation details, and development guides.

## Key Points

- Effective linking creates a discoverable knowledge network
- Links should be meaningful and contextual
- Different types of links serve different purposes
- Bidirectional linking ensures connections work both ways

## Link Types

### 1. Hierarchical Links

Connect notes within their organizational hierarchy:

```markdown
# Within mcpKnowledge
[[../core/MCP Architecture]]
[[../pythonSDK/Python SDK Overview]]

# Within projects
[[../architecture/System Overview]]
[[../implementation/Setup Guide]]
```

### 2. Cross-Category Links

Connect related content across different categories:

```markdown
# From project to MCP knowledge
[[../../mcpKnowledge/core/MCP Architecture]]

# From language to project
[[../../projects/myMcpServer/implementation/Setup Guide]]
```

### 3. MOC Links

Maps of Content serve as navigation hubs:

```markdown
# Main MOCs
[[mcpKnowledge/MCP Knowledge MOC]]
[[projects/myMcpServer/Project MOC]]
[[languages/python/Python MOC]]
```

## Best Practices

### 1. Link Text

Use descriptive link text:

```markdown
[[MCP Architecture|Core Architectural Principles]]
[[Python MOC|Python Development Guide]]
```

### 2. Relative vs. Absolute Paths

- Use relative paths within the same category
- Use absolute paths for cross-category links
- Keep paths as short as possible

### 3. Backlinks

- Add "Related Content" sections
- Use dataview queries for automatic link collection
- Maintain bidirectional links where appropriate

### 4. Link Maintenance

- Update links when moving files
- Check for broken links regularly
- Use consistent linking patterns

## Directory Structure

### Base Directories

```
docs-obsidian/
├── mcpKnowledge/    # MCP-specific knowledge
├── projects/        # Project implementations
├── languages/       # Language-specific knowledge
└── docsGuide/      # Documentation guidelines
```

### Link Examples

1. **MCP Knowledge**

   ```
   mcpKnowledge/
   ├── core/
   ├── pythonSDK/
   ├── typeScriptSDK/
   └── integration/
   ```

2. **Project Documentation**

   ```
   projects/myMcpServer/
   ├── architecture/
   ├── implementation/
   └── mcpPlanning/
   ```

3. **Language Documentation**

   ```
   languages/
   ├── python/
   └── typescript/
   ```

## Content Organization

### 1. Related Content Sections

Organize links by relevance:

```markdown
## Related Concepts
- [[Concept A]]
- [[Concept B]]

## Implementation
- [[Guide A]]
- [[Guide B]]
```

### 2. Navigation Links

Include navigation aids:

```markdown
[[Parent MOC|← Back to Parent]]
[[Home|← Back to Home]]
```

## Related Documentation

- [[Documentation Structure Guide]] - Overall documentation structure
- [[Knowledge Graph]] - Understanding the knowledge graph
- [[MOC Concept]] - Maps of Content organization

## References

- [Obsidian Linking](https://help.obsidian.md/How+to/Internal+link)
- [Zettelkasten Method](https://zettelkasten.de/posts/overview/)

---

[[Documentation Structure Guide|← Back to Documentation Guide]]
