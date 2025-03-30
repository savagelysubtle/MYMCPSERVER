---
created: 2025-03-30
updated: { { date } }
tags: [template, moc, documentation]
parent: [[../Documentation Structure Guide]]
up: [[../../Home]]
siblings: []
contains: []
related_mocs: []
---

# {{title}} MOC

This Map of Content organizes information about {{title}}. Use this as a starting point when looking for information on this topic.

## Overview

<!-- Brief overview of what this MOC covers -->

## Navigation Structure

### Hierarchical Organization

_Documents contained in this MOC:_

```dataview
list from #{{title-tag}}
where contains(file.outlinks, this.file.link)
```

### Related MOCs

_Connected knowledge areas:_

- (Add related MOCs with relationship types)
- Example: [[Python MOC]] (implements)
- Example: [[Core MOC]] (extends)

## Key Topics

_Main subtopics in this area:_

### Core Concepts

- (Add core concepts)
- Example: [[Concept A]] (foundational)
- Example: [[Concept B]] (advanced)

### Implementation

- (Add implementation topics)
- Example: [[Guide A]] (step 1)
- Example: [[Guide B]] (step 2)

### Reference

- (Add reference materials)
- Example: [[Reference A]] (specification)
- Example: [[Reference B]] (examples)

## Topic Relationships

### Dependencies

_Documents that this knowledge depends on:_

- (Add dependency relationships)
- Example: [[Prerequisite A]] (required)
- Example: [[Prerequisite B]] (recommended)

### Extensions

_Documents that build upon this knowledge:_

- (Add extension relationships)
- Example: [[Extension A]] (implements)
- Example: [[Extension B]] (enhances)

## Important Notes

_Essential notes on this topic:_

- (Add important notes with relationship context)
- Example: Note about relationship to other concepts
- Example: Note about implementation patterns

## Resources

_Helpful resources on this topic:_

### Documentation

- (Add documentation links with relationship types)
- Example: [[Doc A]] (reference)
- Example: [[Doc B]] (tutorial)

### External Resources

- (Add external resources with context)
- Example: [Resource A](url) (specification)
- Example: [Resource B](url) (examples)

## Navigation Aids

### Breadcrumb Trail

1. [[../../Home|Home]]
2. [[../Documentation Structure Guide|Documentation Guide]]
3. Current: {{title}} MOC

### Related Content

_Content with explicit relationships to this MOC:_

```dataview
table type, file.path
from [[{{title}} MOC]]
where type = "implements" or type = "extends" or type = "related"
```

## Automatically Linked Notes

_Notes that link to this MOC:_

```dataview
list from [[{{title}} MOC]] and !outgoing([[{{title}} MOC]])
```

---

Note: When creating a new MOC:

1. Update Frontmatter

   - Set creation and update dates
   - Add appropriate tags
   - Set parent MOC
   - Define up/siblings navigation
   - List contained documents
   - Link related MOCs

2. Relationship Management

   - Define clear hierarchies
   - Establish typed relationships
   - Maintain bidirectional links
   - Document relationship context

3. Navigation Structure

   - Create clear navigation paths
   - Define topic relationships
   - Maintain breadcrumb trails
   - Link related content

4. Remove these instructions

---

[[../Documentation Structure Guide|← Back to Documentation Guide]]
