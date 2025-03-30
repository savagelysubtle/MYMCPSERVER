---
created: 2025-03-30
updated: 2025-03-30
tags: [MOC, fleeting, temporary]
parent: [[Home]]
up: [[Home]]
siblings: []
transitions_to: [
  [[MCP MOC]],
  [[Tech MOC]],
  [[Processes MOC]],
  [[Reference MOC]]
]
---

# Fleeting MOC

This is your collection point for new, unprocessed notes that haven't been fully organized yet. Notes here are temporary and will transition to permanent locations in other MOCs.

## Navigation

### Breadcrumb Trail

1. [[Home|Home]]
2. Current: Fleeting Notes

### Destination MOCs

_Notes from here will be organized into:_

- [[MCP MOC]] - For MCP-specific concepts
- [[Tech MOC]] - For technical knowledge
- [[Processes MOC]] - For procedures and workflows
- [[Reference MOC]] - For technical references

## Note Status

### Unprocessed Notes

_Notes awaiting organization:_

```dataview
list from [[Fleeting MOC]]
where !contains(file.outlinks, this.transitions_to)
```

### In Progress

_Notes being processed:_

```dataview
list from [[Fleeting MOC]]
where contains(file.outlinks, this.transitions_to)
```

### Recently Processed Notes

_Notes that have been organized from the Fleeting collection:_

```dataview
list from [[Fleeting MOC]]
where processed = true
sort date desc
limit 5
```

## Organization Guidelines

### 1. Note Creation

When creating new fleeting notes:

- Link them to this MOC
- Add appropriate tags
- Mark as `status: unprocessed`

### 2. Processing

When processing notes:

- Review content
- Identify permanent location
- Update metadata
- Mark as `status: in_progress`

### 3. Organization

When organizing notes:

- Move to appropriate MOC
- Update relationships
- Remove fleeting link
- Mark as `status: processed`

### 4. Transition Paths

- MCP concepts → [[MCP MOC]]
- Technical knowledge → [[Tech MOC]]
- Procedures → [[Processes MOC]]
- References → [[Reference MOC]]

---

_This MOC serves as a temporary collection point. Notes should be processed and moved to their permanent locations regularly._

## Automatically Linked Notes

_Notes currently linked to this MOC:_

```dataview
list from [[Fleeting MOC]] and !outgoing([[Fleeting MOC]])
```

---

[[Home|← Back to Home]]
