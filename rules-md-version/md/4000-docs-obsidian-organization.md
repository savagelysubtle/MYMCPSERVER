---
description: IMPORTANT MAINTAIN hierarchical folder structure using _index.md WHEN working with docs-obsidian content
globs: 'docs-obsidian/**/*.md'
alwaysApply: true
---

 <aiDecision>
  description: IMPORTANT MAINTAIN hierarchical folder structure using _index.md WHEN working with docs-obsidian content
  globs: "docs-obsidian/**/*.md"
  alwaysApply: true
</aiDecision>

# Obsidian Documentation Organization Rule (v2 - Hierarchical)

<context>
  <role>Documentation System</role>
  <purpose>Maintain consistent hierarchical folder structure and organization using _index.md files for navigation.</purpose>
</context>

<requirements>
  <requirement>USE dedicated top-level folders for distinct knowledge areas: docsGuide/, generalKnowledge/, languages/, mcpKnowledge/, projects/.</requirement>
  <requirement>PLACE meta-documentation (guides, templates) within the docsGuide/ folder.</requirement>
  <requirement>PLACE shared language-specific knowledge in languages/{language}/{category}/ folders (e.g., languages/python/patterns/).</requirement>
  <requirement>PLACE general MCP concepts and SDK overviews in the mcpKnowledge/ folder and its subdirectories.</requirement>
  <requirement>PLACE project-specific documentation within projects/{projectName}/, further organized by component/layer (e.g., projects/myMcpServer/implementation/core/).</requirement>
  <requirement>CREATE an _index.md file within EACH significant directory to serve as the entry point and navigation hub for that directory.</requirement>
  <requirement>ENSURE each _index.md file contains appropriate frontmatter, including an 'up' link to the parent directory's _index.md.</requirement>
  <requirement>AVOID using top-level MOC files for primary directory organization; use _index.md instead.</requirement>
  <requirement>USE the Fleeting MOC.md or a dedicated Fleeting/ folder as an inbox for temporary notes.</requirement>
</requirements>

<structure>
  <description>Example of the target hierarchical structure.</description>
  <folder name="docs-obsidian">
    <file>_index.md</file> <!-- Root Index -->
    <folder name="docsGuide">
      <file>_index.md</file>
      <folder name="templates">
         <file>_index.md</file>
         <file>Note Template.md</file>
         <file>_index Template.md</file>
      </folder>
      <file>Documentation Structure Guide.md</file>
      <!-- other guides -->
    </folder>
    <folder name="generalKnowledge">
      <file>_index.md</file>
      <!-- other general notes -->
    </folder>
    <folder name="languages">
      <file>_index.md</file>
      <folder name="python">
        <file>_index.md</file>
        <folder name="core">
           <file>_index.md</file>
        </folder>
        <!-- other categories -->
      </folder>
      <folder name="typescript">
         <file>_index.md</file>
         <!-- categories -->
      </folder>
    </folder>
    <folder name="mcpKnowledge">
       <file>_index.md</file>
       <folder name="core">
          <file>_index.md</file>
          <!-- core concept notes -->
       </folder>
       <!-- other mcp categories -->
    </folder>
    <folder name="projects">
       <file>_index.md</file>
       <folder name="myMcpServer">
          <file>_index.md</file> <!-- Project Index -->
          <folder name="architecture">
             <file>_index.md</file>
             <file>System Overview.md</file>
          </folder>
          <folder name="implementation">
             <file>_index.md</file>
             <folder name="core">
                <file>_index.md</file>
                <file>technical-v2.md</file>
             </folder>
             <!-- other implementation layers -->
          </folder>
          <!-- other project sections like api -->
       </folder>
       <!-- other projects -->
    </folder>
    <file>Fleeting MOC.md</file> <!-- Optional Inbox -->
  </folder>
</structure>

<examples>
  <!-- Add examples here if applicable -->
</examples>
