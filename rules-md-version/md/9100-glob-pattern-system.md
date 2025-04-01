---
description: WHEN creating rule files ENSURE using precise aidecision tags with action-oriented descriptions and efficient glob patterns
globs: '**/*.mdc, .cursor/rules/**/*'
alwaysApply: true
---

<aiDecision>
  description: WHEN creating rule files ENSURE using precise aidecision tags with action-oriented descriptions and efficient glob patterns
  globs: **/*.md rules-md-version/**/*.md
  alwaysApply: true
</aiDecision>

> **TL;DR:** Define rule files with proper aidecision tags containing action-oriented descriptions and specific, targeted glob patterns to optimize rule performance, improve clarity, and avoid unnecessary processing.

<version>1.1.0</version>

<context>
  This rule provides guidance for creating effective rule files with proper aidecision tags and efficient glob patterns. Well-structured aidecision tags and specific glob patterns ensure rules are applied precisely to the intended files while improving clarity and minimizing processing overhead.
</context>

<requirements>
  <requirement>Structure aidecision tags with description, globs, and applyAlways fields</requirement>
  <requirement>Write descriptions using the ACTION TRIGGER OUTCOME format (e.g., WHEN X ENSURE Y)</requirement>
  <requirement>Use specific glob patterns targeting only relevant file types and directories</requirement>
  <requirement>Include exclusion patterns to avoid processing unnecessary files</requirement>
  <requirement>Structure patterns hierarchically for complex file targeting</requirement>
  <requirement>Use proper syntax with quotes and arrays for multiple patterns</requirement>
  <requirement>Consider performance implications when designing glob patterns</requirement>
  <requirement>For rule files, always use [**/*.mdc, .cursor/rules/**/*]</requirement>
</requirements>

<details>
  <section-name>AIDECISION TAG STRUCTURE</section-name>
  <content>
    Every rule file must begin with aidecision tags:

    ```
    <aidecision>
      description= "WHEN doing X ENSURE Y"
      globs= "pattern1, pattern2"
      applyAlways= "true|false"
    </aidecision>
    ```

    ### Required Fields

    - **description**: A clear, action-oriented statement of what the rule does
    - **globs**: Patterns that determine which files the rule applies to
    - **applyAlways**: Boolean indicating whether the rule should always be applied

    ### Action-Oriented Descriptions

    Use the ACTION TRIGGER OUTCOME format for descriptions:

    - Format: `WHEN [trigger condition] ENSURE [required outcome]`
    - Example: `WHEN writing React components ENSURE following component architecture best practices`
    - Example: `WHEN implementing API endpoints ENSURE proper error handling and validation`

    This format clearly communicates:
    1. When the rule should be applied (trigger)
    2. What must be done when the rule is triggered (outcome)

    ### Benefits of Action-Oriented Descriptions

    - Makes rule intent immediately clear
    - Provides deterministic guidance
    - Avoids ambiguity about when/how the rule applies
    - Improves overall rule discoverability and effectiveness

  </content>
</details>

<examples>
  <!-- Add examples here if applicable -->
</examples>
