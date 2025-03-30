---
config:
  theme: neo-dark
  layout: dagre
---

flowchart TD
subgraph Client["MCP Client Layer"]
A["MCP Client\nCursor"]
end

    subgraph Transport["Transport Layer"]
        B["Proxy Connection Server\nstdio ⇄ SSE/WebSocket"]
        B1["Transport Manager"]
        B2["Protocol Adapters"]
    end

    subgraph Core["Core Processing Layer"]
        C["MCP Core Layer\nPython"]
        C1["Request Validator"]
        C2["Metrics Collector"]
        C3["Config Manager"]
    end

    subgraph Registry["Registry Layer"]
        D["Adapter/Registry Layer"]
        D1["Version Manager"]
        D2["Circuit Breaker"]
        D3["Health Monitor"]
    end

    subgraph Servers["Tool Servers"]
        E1["Python Tool Server\nPython SDK"]
        E2["TypeScript Tool Server"]
    end

    subgraph Tools["Tool Layer"]
        n1["Obsidian Tool"]
        n2["AIChemist Tool"]
        n3["Thinking Tool"]
        n4["Another Tool"]
    end

    A <--> B
    B <--> B1
    B1 <--> B2
    B2 <--> C

    C --> C1
    C1 --> C2
    C2 --> C3
    C3 --> D

    D --> D1
    D1 --> D2
    D2 --> D3

    D3 --> E1 & E2
    E1 --> n1 & n2
    E2 --> n3 & n4

    n1 & n2 --> E1
    n3 & n4 --> E2
    E1 & E2 --> D3
    D3 --> D2
    D2 --> D1
    D1 --> D
    D --> C
    C --> B2
    B2 --> B1
    B1 --> B
    B --> A
