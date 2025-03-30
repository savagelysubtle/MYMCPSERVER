---
created: 2025-03-30
updated: 2025-03-30
tags: [folder-note, tags, organization]
parent: [[../Home]]
up: [[../Home]]
---

# Tag Organization

This directory organizes content by tags, providing alternative navigation paths through the documentation.

## Primary Tag Groups

### Knowledge Areas

#### MCP Knowledge

- #mcp-architecture - Core architectural concepts
- #mcp-implementation - Implementation details
- #mcp-integration - Integration guides
- #mcp-sdk - SDK documentation
- #mcp-tools - Tool-related content

#### Technical Knowledge

- #architecture - System architecture
- #design-patterns - Design patterns
- #best-practices - Best practices
- #security - Security-related
- #performance - Performance topics

#### Project Knowledge

- #project-architecture - Project architecture
- #project-implementation - Implementation details
- #project-deployment - Deployment guides
- #project-operations - Operations guides

### Content Types

#### Documentation Types

- #guide - How-to guides
- #reference - Reference documentation
- #concept - Conceptual documentation
- #tutorial - Step-by-step tutorials
- #example - Code examples

#### Organization Types

- #moc - Maps of Content
- #folder-note - Directory organization
- #list-note - List-based organization
- #tag-note - Tag-based organization

### Status Tags

#### Development Status

- #stable - Stable content
- #draft - Work in progress
- #deprecated - Deprecated content
- #needs-review - Needs review
- #updated - Recently updated

## Tag Collections

### Architecture Collection

```dataview
list from #architecture or #mcp-architecture or #project-architecture
```

### Implementation Collection

```dataview
list from #mcp-implementation or #project-implementation
```

### Documentation Collection

```dataview
list from #guide or #reference or #concept or #tutorial
```

### Organization Collection

```dataview
list from #moc or #folder-note or #list-note or #tag-note
```

## Tag Relationships

### Parent Tags

- #mcp → Contains all MCP-related tags
- #tech → Contains all technical tags
- #project → Contains all project-specific tags
- #docs → Contains all documentation type tags

### Tag Hierarchies

1. MCP Knowledge
   - #mcp
     - #mcp-architecture
     - #mcp-implementation
     - #mcp-integration

2. Technical Knowledge
   - #tech
     - #architecture
     - #design-patterns
     - #best-practices

3. Project Knowledge
   - #project
     - #project-architecture
     - #project-implementation
     - #project-operations

4. Documentation Types
   - #docs
     - #guide
     - #reference
     - #concept

## Tag Usage

### Creating New Content

1. Use appropriate knowledge area tags
2. Add relevant content type tags
3. Include status tags
4. Add organization tags if applicable

### Updating Content

1. Update status tags
2. Review and update topic tags
3. Ensure proper tag hierarchy

### Deprecating Content

1. Add #deprecated tag
2. Remove active status tags
3. Update related content tags

## Navigation

### By Knowledge Area

- [[../mcpKnowledge/_index|MCP Knowledge]]
- [[../projects/myMcpServer/_index|Project Knowledge]]
- [[../languages/_index|Language Knowledge]]

### By Organization

- [[../Home|Home]]
- [[../MCP MOC|MCP MOC]]
- [[../Tech MOC|Tech MOC]]
- [[../Project MOC|Project MOC]]

## Tag Statistics

### Most Used Tags

```dataview
TABLE length(rows) as "Count"
FROM #mcp or #tech or #project or #docs
GROUP BY file.tags
SORT length(rows) DESC
```

### Recently Tagged

```dataview
TABLE file.tags as "Tags"
FROM ""
WHERE file.mtime >= date(today) - dur(7 days)
SORT file.mtime DESC
```

---

_This tag note provides organization and navigation through the documentation's tag system._
