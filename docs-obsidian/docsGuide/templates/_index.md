---
created: 2025-03-30
updated: 2025-03-30
tags: [folder-note, templates, documentation]
parent: [[../_index]]
up: [[../_index]]
contains: [[[_index Template]], [[Note Template]]]
lists:
  [
    {
      'name': 'Template Types',
      'items': ['[[_index Template]]', '[[Note Template]]'],
    },
  ]
---

# Documentation Templates

## Overview

This directory contains templates for creating new documentation files. These templates ensure consistency across the documentation and make it easier to create well-structured notes that follow our established standards.

## Available Templates

### 1. \_index Template

[[_index Template|Directory Index Template]]

- Used for creating new directory index files (\_index.md)
- Provides structure for organizing directory-level documentation
- Includes sections for:
  - Directory overview
  - Contents listing
  - Navigation links
  - Relationship definitions
  - Dataview queries

### 2. Note Template

[[Note Template|Standard Note Template]]

- Used for creating new documentation notes
- Provides standard structure for:
  - Overview
  - Key points
  - Details
  - Implementation (if applicable)
  - Related documentation with typed links
  - External references

## Usage Guidelines

### Creating New Directory Indexes

1. Use the \_index template when:

   - Creating a new directory in the documentation
   - Setting up navigation for a collection of related notes
   - Organizing a knowledge domain

2. Customization:
   - Replace placeholder content with actual directory information
   - Add relevant contained files
   - Include appropriate typed links
   - Update parent and up links to establish hierarchy

### Creating New Notes

1. Use the Note template when:

   - Adding new documentation
   - Creating implementation guides
   - Documenting concepts or features

2. Customization:
   - Replace placeholder content with actual note information
   - Add appropriate tags
   - Update up link to parent directory index
   - Include relevant typed links
   - Remove unnecessary sections

## Template Maintenance

### Updates

- Templates should be reviewed regularly
- Update structure as documentation needs evolve
- Maintain consistency with documentation standards
- Keep typed link examples current

### Best Practices

1. **Frontmatter**

   - Always include creation and update dates
   - Use appropriate tags
   - Specify up link for navigation
   - Include contains/lists for directory indexes

2. **Structure**

   - Maintain consistent headings
   - Use clear section organization
   - Include navigation hierarchy
   - Add proper typed links

3. **Content**
   - Provide clear instructions
   - Include helpful examples
   - Use typed links for relationships
   - Remove placeholder text

## Related Documentation

- [[../Documentation Structure Guide]](implements) - Structure guidelines
- [[../Metadata and Linking Guide]](extends) - Metadata standards
- [[../Linking Strategy]](implements) - Linking guidelines

## Directory Contents

```dataview
LIST
FROM "docs-obsidian/docsGuide/templates"
WHERE file.name != "_index"
SORT file.name ASC
```

---

_This directory index provides templates for creating consistent documentation._
