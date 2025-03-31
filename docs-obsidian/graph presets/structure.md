---
graph-presets-plugin: basic
---

---

```yaml:graph-preset
collapse-filter: false
search: file:_index
showTags: true
showAttachments: false
hideUnresolved: false
showOrphans: false
collapse-color-groups: false
colorGroups:
  - query: path:_index
    color:
      rgb: 16711680  # Red
      a: 1
  - query: path:mcpKnowledge path:_index
    color:
      rgb: 16748288  # Orange
      a: 1
  - query: path:projects path:_index
    color:
      rgb: 16776960  # Yellow
      a: 1
  - query: path:languages path:_index
    color:
      rgb: 65535  # Blue
      a: 1
  - query: path:docsGuide path:_index
    color:
      rgb: 8388736  # Purple
      a: 1
  - query: path:generalKnowledge path:_index
    color:
      rgb: 16716947  # Pink
      a: 1
collapse-display: false
showArrow: true
textFadeMultiplier: 0
nodeSizeMultiplier: 1.5
lineSizeMultiplier: 1.5
collapse-forces: false
centerStrength: 0.7
repelStrength: 8
linkStrength: 1
linkDistance: 150
scale: 0.2588386562181636
close: false
```
