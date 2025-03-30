---
created: 2025-03-30
tags: process, implementation-plan, phase-2
parent: [[Implementation Plan MOC]]
---

# Phase 2: Transport Layer (stdio)

**Goal:** Implement the Proxy Connection Server focusing initially on stdio communication between the Proxy and the Core Layer.

## 📚 Prerequisite Reading

- [[final/transport/overview-v2.md]] - Understand the Transport Layer's role and components.
- [[final/transport/technical-v2.md]] - Review the technical design for the Transport Layer, focusing on the `StdioHandler` and `MessageRouter`.
- [[final/core/technical-v2.md]] - Remind yourself how the Core Layer expects to receive requests (e.g., the `handle_request` method).
- [[../src/mymcpserver/server.py]] - Note the existing transport handling logic which might be refactored or replaced.

## ✅ Checklist

- [x] **Proxy Structure:** Create the directory structure for `src/mcp_proxy/` including `transports/` as per [[final/filetree.md]].
- [x] **stdio Handler:** Implement the `StdioHandler` class in `mcp_proxy/transports/stdio.py` based on [[final/transport/technical-v2.md]]. Focus on spawning a process (the Core Layer) and reading/writing from its stdin/stdout.
- [x] **Message Router:** Implement a basic `MessageRouter` (or similar queue-based mechanism) in `mcp_proxy/router.py` (or equivalent) to pass messages between the eventual SSE/WebSocket side and the stdio side, based on [[final/transport/technical-v2.md]].
- [x] **Proxy Server Core:** Implement the main `ProxyServer` class in `mcp_proxy/proxy_server.py`. This class should initialize the `StdioHandler` and the `MessageRouter`.
- [x] **Proxy Entry Point:** Create `mcp_proxy/__main__.py`. This script should initialize and start the `ProxyServer`.
- [x] **Runner Integration:** Update [[../src/run_server.py]] to:
  - Spawn the `mcp_core` process when `--mode proxy` or `--mode full` is selected.
  - Spawn the `mcp_proxy` process using `asyncio.create_subprocess_exec` or similar, connecting its stdin/stdout to the Core Layer process, when `--mode proxy` or `--mode full` is selected.
- [x] **Basic Communication:** Ensure a simple message sent to the Proxy's stdin (simulating an external client for now) gets forwarded to the Core Layer's stdin via the `StdioHandler`, and a response from the Core's stdout is read back.

## 🛑 Pause Point & Collaboration

- **Review:** The implementation successfully establishes the process spawning logic and basic communication flow between the Proxy and Core via the StdioHandler.
- **Implementation Summary:** We have:
  - Created a robust MessageRouter for routing messages between different transports
  - Implemented the StdioHandler that can spawn and communicate with the Core Layer
  - Updated the ProxyServer to use both components effectively
  - Modified the run_server.py to handle different modes and transports properly
  - Ensured proper message passing between components

## Next Phase

➡️ [[03 - Adapter and Registry Layer]]

---

_This note belongs to the [[Implementation Plan MOC]]_
