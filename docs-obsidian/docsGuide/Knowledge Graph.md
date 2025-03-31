---
created: 2025-03-28
updated: 2025-03-30
tags: [documentation, organization, knowledge-graph]
parent: [[../_index]]
up: [[../_index]]
siblings: [[Documentation Structure Guide]], [[Linking Strategy]], [[Metadata and Linking Guide]]
implements: []
references: [[Linking Strategy]], [[Metadata and Linking Guide]]
related: []
---

# Knowledge Graph

## Overview

A knowledge graph is a network of interlinked descriptions of concepts, entities, relationships and events that gives context and meaning to information. In our documentation system, it represents the connections between different pieces of knowledge across MCP concepts, implementation details, and development guides, with semantically typed relationships between notes.

## Key Points

- Knowledge graphs represent information as nodes (notes) and edges (typed links)
- They enable powerful connections between ideas with semantic meaning
- In Obsidian, the graph view visualizes your knowledge graph
- Typed bi-directional linking forms the foundation of our knowledge graph
- Directory hierarchy with `_index.md` files provides structural organization

## Implementation

### Directory Structure

Our knowledge graph is organized into main categories, each with an `_index.md` file as its entry point:

1. **MCP Knowledge** ([[../mcpKnowledge/_index|MCP Knowledge]](defines))

   - Core concepts and architecture
   - SDK documentation
   - Integration guides

2. **Project Documentation** ([[../projects/myMcpServer/_index|MyMcpServer]](implements))

   - Implementation details
   - Architecture documents
   - API documentation

3. **Language Knowledge** ([[../languages/_index|Languages]](implements))
   - Python development
   - TypeScript development

### Connection Types

1. **Hierarchical**

   - Directory structure with `_index.md` files
   - Parent-child relationships using the `up` link
   - Category organization through directory structure

2. **Semantic**

   - Typed relationships like `implements`, `extends`, `references`
   - Explicit meaning assigned to connections
   - Context-aware linking

3. **Contextual**
   - Use cases and examples
   - Implementation relationships
   - Decision-based connections

## Best Practices

### Creating Connections

1. **Typed Links**

   - Use the format `[[Target Note]](relationship_type)`
   - Choose the appropriate relationship type
   - Place links within their relevant context in the content

2. **Organization**

   - Use `_index.md` files as directory entry points
   - Maintain consistent `up` links for navigation
   - Create clear paths through the hierarchy

3. **Maintenance**
   - Review connections regularly
   - Update links when content changes
   - Add new relationships as the knowledge base evolves

## Visualization

The Obsidian graph view provides a visual representation of your knowledge graph:

1. **Global Graph**

   - Shows all connections between notes
   - Can be filtered by tags or paths
   - Reveals clusters and central nodes

2. **Local Graph**

   - Shows connections for the current note
   - Reveals immediate relationships
   - Helps identify missing connections

3. **Hierarchical Navigation**
   - The Breadcrumbs plugin follows `up` links
   - Provides consistent navigation
   - Shows the current location in the hierarchy

## Related Documentation

- [[Linking Strategy]](implements) - Best practices for creating typed links
- [[Metadata and Linking Guide]](implements) - Standards for frontmatter and relationships
- [[Documentation Structure Guide]](references) - Overall documentation organization

## References

- [Obsidian Graph View](https://help.obsidian.md/Plugins/Graph+view)
- [Knowledge Graph Theory](https://en.wikipedia.org/wiki/Knowledge_graph)

---

_This document is part of the [[../_index|Documentation Guide]]._
