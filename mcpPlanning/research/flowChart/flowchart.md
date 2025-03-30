---
config:
  theme: neo-dark
  layout: dagre
---

flowchart TD
A["MCP Client
Cursor"] <-- SSE --> B["Proxy Connection Server
stdio ⇄ SSE"]
B <-- stdio --> C["MCP Core Layer
Python"]
C -- Dispatch Request --> D["Adapter/Registry Layer"]
D -- Route Request --> E1["Python Tool Server - Python SDK"] & E2["TypeScript Tool Server:"]
E1 -- Response --> D
E2 -- Response --> D
E1 -- Route Request --> n1["Obsidian Tool"] & n2["AIChemist Tool"]
E2 -- Route Request --> n3["Thinking Tool"] & n4["Another Tool"]
n1 -- Response --> E1
n2 -- Response --> E1
n3 -- Response --> E2
n4 -- Response --> E2
