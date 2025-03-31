---
graph-presets-plugin: basic
---

---

```yaml:graph-preset
collapse-filter: false
search: -file:_index
showTags: true
showAttachments: false
hideUnresolved: false
showOrphans: false
collapse-color-groups: false
colorGroups:
  - query: path:mcpKnowledge/core -file:_index
    color:
      rgb: 16711680  # Red
      a: 1
  - query: path:mcpKnowledge/pythonSDK -file:_index
    color:
      rgb: 16748288  # Orange
      a: 1
  - query: path:mcpKnowledge/typeScriptSDK -file:_index
    color:
      rgb: 16776960  # Yellow
      a: 1
  - query: path:projects/myMcpServer/architecture -file:_index
    color:
      rgb: 65535  # Blue
      a: 1
  - query: path:projects/myMcpServer/implementation -file:_index
    color:
      rgb: 8388736  # Purple
      a: 1
  - query: path:projects/myMcpServer/api -file:_index
    color:
      rgb: 16716947  # Pink
      a: 1
  - query: path:languages/python -file:_index
    color:
      rgb: 43775  # Light Blue
      a: 1
  - query: path:languages/typescript -file:_index
    color:
      rgb: 5308240  # Light Green
      a: 1
collapse-display: false
showArrow: true
textFadeMultiplier: -0.7
nodeSizeMultiplier: 1.3
lineSizeMultiplier: 1.5
collapse-forces: false
centerStrength: 0.5
repelStrength: 12
linkStrength: 0.8
linkDistance: 230
scale: 0.2588386562181636
close: false
```
