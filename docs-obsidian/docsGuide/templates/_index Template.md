---
created: { { date:YYYY-MM-DD } }
updated: { { date:YYYY-MM-DD } }
tags: [folder-note] # Add specific category tags, e.g., project, python, core-concept
parent: [[../Parent/_index]] # Link to the logical parent (often same as up)
up: [[../Parent/_index]] # CRUCIAL: Link to parent directory's _index.md
contains: [] # Optional: Manually list key child notes/indices [[Child1]], [[Child2/_index]]
lists: [] # Optional: Define structured lists, e.g., { "name": "Core Files", "items": ["[[FileA]]", "[[FileB]]"] }
---

# {{title}} Directory Index

<!-- Brief description of the directory's purpose and content -->

## Structure / Key Contents

<!-- Optional: Describe subdirectories or list key files. -->
<!-- Use standard [[links]] or [[Folder/_index|Display Text]] -->

## Relationships

<!-- Optional: Add typed links to show semantic relationships -->
<!-- Example: This directory [[Another Directory/_index]](extends) the concepts in... -->

## Navigation

<!-- Optional: Add explicit links to important related areas -->

- Parent: [[../Parent/_index|Parent Directory]]
- Siblings: [[../Sibling1/_index|Sibling1]], [[../Sibling2/_index|Sibling2]]

## Contained Notes (Dataview)

<!-- Optional: Use Dataview to list notes in this folder -->

```dataview
LIST
FROM "{{folder}}"
WHERE file.name != "_index"
SORT file.name ASC
```

---

_Instructions: Replace {{title}} and {{folder}} with actual values. Update `parent` and `up` links accurately. Add relevant tags. Fill in the description and structure sections. Add typed links in the Relationships section. Adjust or remove Dataview query as needed. Add key items to `contains` or `lists` in the frontmatter if needed. Remove these instructions._
