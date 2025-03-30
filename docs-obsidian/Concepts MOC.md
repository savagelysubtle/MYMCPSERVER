---
created: 2025-03-28
tags: MOC, deprecated
---

# Concepts MOC (Deprecated)

> **Note**: This MOC has been reorganized into a new structure for better organization:
>
> - [[mcpKnowledge/MCP Knowledge MOC|MCP Knowledge]] - MCP concepts and standards
> - [[projects/myMcpServer/Project MOC|MyMcpServer Project]] - Project implementation
> - [[languages/python/Python MOC|Python Knowledge]] - Python development
> - [[languages/typescript/TypeScript MOC|TypeScript Knowledge]] - TypeScript development
>
> Please update your links to point to the appropriate new MOC.

## New Structure

### MCP Knowledge

All MCP-related content has moved to [[mcpKnowledge/MCP Knowledge MOC|MCP Knowledge MOC]], including:

- [[mcpKnowledge/core/MCP Server Architecture|MCP Architecture]]
- [[mcpKnowledge/core/MCP Central Hub|MCP Central Hub]]
- [[mcpKnowledge/core/Tool Management|Tool Management]]

### Project Documentation

Project-specific documentation has moved to [[projects/myMcpServer/Project MOC|MyMcpServer Project MOC]], including:

- [[projects/myMcpServer/architecture/System Overview|System Overview]]
- [[projects/myMcpServer/implementation/Setup Guide|Setup Guide]]
- [[projects/myMcpServer/implementation/Deployment|Deployment Guide]]

### Language-Specific Knowledge

Programming language content has been organized into:

- [[languages/python/Python MOC|Python MOC]] - Python development knowledge
- [[languages/typescript/TypeScript MOC|TypeScript MOC]] - TypeScript development knowledge

## Migration Guide

### For Content Creators

1. Place new content in the appropriate directory:
   - MCP-related → `mcpKnowledge/`
   - Project-specific → `projects/myMcpServer/`
   - Language-specific → `languages/python/` or `languages/typescript/`

2. Follow the new linking convention:
   - Use relative paths when linking within the same category
   - Use full paths when linking across categories
   - Example: `[[../../mcpKnowledge/core/MCP Architecture]]`

3. Include proper frontmatter:

   ```yaml
   ---
   created: [date]
   updated: [date]
   tags: [relevant-tags]
   parent: [[appropriate MOC]]
   ---
   ```

### For Content Consumers

1. Start from the [[Home]] page for main navigation
2. Use the appropriate MOC based on content type:
   - MCP concepts → [[mcpKnowledge/MCP Knowledge MOC|MCP Knowledge]]
   - Project details → [[projects/myMcpServer/Project MOC|MyMcpServer Project]]
   - Language guides → [[languages/python/Python MOC|Python]] or [[languages/typescript/TypeScript MOC|TypeScript]]

3. Check the [[docsGuide/Documentation Structure Guide|Documentation Guide]] for detailed organization

### Documentation Standards

For information about maintaining the documentation, see:

- [[docsGuide/Documentation Structure Guide|Documentation Structure Guide]]
- [[templates/Note Template|Note Template]]
- [[templates/MOC Template|MOC Template]]

---

[[Home|← Back to Home]]
