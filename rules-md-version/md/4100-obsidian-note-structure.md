---
description: CRITICAL STRUCTURE all notes WHEN creating content in Obsidian to follow template format with mandatory frontmatter including 'up' link
globs: 'docs-obsidian/**/*.md'
alwaysApply: true
---

<aiDecision>
  description: CRITICAL STRUCTURE all notes WHEN creating content in Obsidian to follow template format with mandatory frontmatter including 'up' link
  globs: "docs-obsidian/**/*.md"
  alwaysApply: true
</aiDecision>

# Obsidian Note Structure Rule (v2 - Hierarchical)

<context>
  <role>Knowledge Management System</role>
  <purpose>Ensure consistent structure and essential metadata across all notes for navigation and relationships.</purpose>
</context>

<requirements>
  <requirement>ALWAYS BEGIN notes with YAML frontmatter containing mandatory fields: created, updated, tags, parent, up, siblings.</requirement>
  <requirement>CRITICAL: ENSURE the 'up' frontmatter field contains a valid Wikilink to the _index.md file of the immediate parent directory (e.g., `up: [[../_index]]`).</requirement>
  <requirement>INCLUDE placeholder relationship fields in frontmatter (e.g., implements, references, related, based_on_decision) even if initially empty.</requirement>
  <requirement>USE the 'parent' frontmatter field to link to the main conceptual MOC or Index file for the topic (may be the same as 'up').</requirement>
  <requirement>SHOULD include standard sections like Overview, Key Points, Details, Relationships/Links, Related Documentation, following the Note Template.</requirement>
  <requirement>USE typed links (e.g., `[[Target]](relationship_type)`) within the content, especially in a 'Relationships/Links' section, to define semantic connections.</requirement>
</requirements>

<examples>
  <good-practice>
    <description>Properly structured note with mandatory frontmatter</description>
    <example>
      ---
      created: 2025-03-30
      updated: 2025-03-30
      tags: [architecture, component-design, myMcpServer]
      parent: [[../_index]] # Project Index
      up: [[../_index]] # Link to parent dir's index.md (architecture/_index.md)
      siblings: [[System Overview]]
      implements: []
      references: [[../implementation/core/technical-v2]]
      related: []
      based_on_decision: [[../_decisions/ADR-001]] # Example
      informed_by_research: []
      next: []
      previous: [[System Overview]]
      ---

      # Component Design

      ## Overview
      Describes the design of individual components.

      ## Key Points
      - Point A
      - Point B

      ## Details
      Detailed design information... This component [[../implementation/core/technical-v2]](implements) the core logic...

      ## Relationships / Links
      - References: [[../implementation/core/technical-v2]]
      - Based on: [[../_decisions/ADR-001]](based_on_decision)

      ## Related Documentation
      - [[System Overview]]

      ---
      <!-- Optional footer link -->
      *Part of [[../_index|Architecture Documentation]]*
    </example>

  </good-practice>
</examples>
