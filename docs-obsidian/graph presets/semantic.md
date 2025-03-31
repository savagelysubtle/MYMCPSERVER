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
  - query: (implements)
    color:
      rgb: 16711680  # Red
      a: 1
  - query: (extends)
    color:
      rgb: 16748288  # Orange
      a: 1
  - query: (references)
    color:
      rgb: 16776960  # Yellow
      a: 1
  - query: (related)
    color:
      rgb: 65535  # Blue
      a: 1
  - query: (based_on_decision)
    color:
      rgb: 8388736  # Purple
      a: 1
  - query: (informed_by_research)
    color:
      rgb: 16716947  # Pink
      a: 1
  - query: (next) OR (previous)
    color:
      rgb: 43775  # Light Blue
      a: 1
  - query: -file:_index -((implements) OR (extends) OR (references) OR (related) OR (based_on_decision) OR (informed_by_research) OR (next) OR (previous))
    color:
      rgb: 8421504  # Gray
      a: 1
collapse-display: false
showArrow: true
textFadeMultiplier: -0.7
nodeSizeMultiplier: 1.3
lineSizeMultiplier: 1.5
collapse-forces: false
centerStrength: 0.5
repelStrength: 12
linkStrength: 1
linkDistance: 200
scale: 0.2588386562181636
close: false
```
