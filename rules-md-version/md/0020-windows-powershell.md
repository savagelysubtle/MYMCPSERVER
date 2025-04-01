---
description: CRITICAL: USER is on WINDOWS ALL TOOL CALLS to reflect
globs: "**/*"
alwaysApply: true
---

<aiDecision>
  description: CRITICAL: USER is on WINDOWS ALL TOOL CALLS to reflect
  globs: "**/*"
  alwaysApply: true
</aiDecision>

# USER SYSTEM WINDOWS TOOL CALLS REFLECT

<context>
  <role>AGENT TOOL CALL</role>
  <purpose>When using tools for file handling calling or terminal use all Calls are for windows & powershell</purpose>
</context>

<requirements>
  <requirement>Always Use WINDOWS Tool Calls</requirement>
  <requirement>This is TOOL CALLS ONLY writing code may be different</requirement>
</requirements>

<examples>
  <example>
    ```powershell
    # Example tool call for Windows PowerShell
    # list directory contents
    Get-ChildItem -Path ".\src"

    # Example file path
    $filePath = "C:\Users\User\Documents\file.txt"
    ```

  </example>
</examples>
