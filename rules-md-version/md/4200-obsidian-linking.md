---
description: ALWAYS USE typed links WHEN defining relationships between notes in Obsidian and ensure context
globs: 'docs-obsidian/**/*.md'
alwaysApply: true
---

<aiDecision>
  description: ALWAYS USE typed links WHEN defining relationships between notes in Obsidian and ensure context
  globs: "docs-obsidian/**/*.md"
  alwaysApply: true
</aiDecision>

# Obsidian Linking Rule (v2 - Typed Links)

<context>
  <role>Knowledge Management System</role>
  <purpose>Ensure clear, contextual, and machine-readable relationships between notes using typed links.</purpose>
</context>

<requirements>
  <requirement>WHEN expressing a relationship between notes (e.g., implementation, reference, related idea), USE typed links following the format `[[Target Note|Optional Display Text]](relationship_type)`.</requirement>
  <requirement>USE standardized relationship types documented in the 'Metadata and Linking Guide'.</requirement>
  <requirement>PLACE typed links directly within the content where the relationship is relevant (e.g., "This component [[Other Component]](uses) data from...").</requirement>
  <requirement>MAY use a 'Related Documentation' or 'Relationships/Links' section for supplementary links, also preferably using typed links.</requirement>
  <requirement>RELY on Obsidian's backlinks pane and dataview queries in _index.md files for discovering connections; manual backlinking in the target note is optional but encouraged for critical relationships.</requirement>
  <requirement>ENSURE the link type accurately reflects the context of the relationship.</requirement>
</requirements>

<examples>
  <good-practice>
    <description>Using typed links for clear relationships</description>
    <example>
      In Note A (e.g., Component Design):
      This design [[Implementation Details]](is_implemented_by). See [[Architecture Overview]](references) for context. This was decided based on [[ADR-002]](based_on_decision).

      Related Documentation:
      - [[Related Concept]](related)
      - [[Example Usage]](example)
    </example>

  </good-practice>

  <bad-practice>
    <description>Using plain links without type/context</description>
    <example>
      In Note A:
      See [[Implementation Details]]. Also check [[Architecture Overview]]. We decided this here: [[ADR-002]].

      Related:
      - [[Related Concept]]
      - [[Example Usage]]
      <!-- Relationship types are unclear -->
    </example>

  </bad-practice>
</examples>
