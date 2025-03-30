---
created: 2025-03-30
tags: process, implementation-plan, phase-4
parent: [[Implementation Plan MOC]]
---

# Phase 4: Python Tool Server and SDK

**Goal:** Implement the Python Tool Server and define/integrate actual Python tools (like Obsidian, AIChemist) using the MCP Python SDK.

## 📚 Prerequisite Reading

- [[final/python/tool-server.md]] - Primary technical document for this phase.
- [[final/filetree.md]] - Locate the `src/tool_servers/python_tool_server/` directory.
- MCP Python SDK Documentation (@mcpPythSDK) - Consult the official SDK docs for `create_server`, `@tool` decorator, `ToolContext`, `ToolResponse`, transport options, etc.
- [[final/adapter/technical-v2.md]] - Review the `PythonToolAdapter` requirements for communication (e.g., host/port, expected request/response format if not using a standard SDK transport).

## ✅ Checklist

- [x] **Tool Server Structure:** Create the `src/tool_servers/python_tool_server/` directory and initial files: `server.py`, `__init__.py`, `requirements.txt`. Also create subdirectories for tools like `n1/` (Obsidian) and `n2/` (AIChemist).
- [x] **Dependencies:** Add the MCP Python SDK (`uv add mcp-sdk` or equivalent) and any tool-specific dependencies to `python_tool_server/requirements.txt`.
- [x] **Basic Server Setup:** In `python_tool_server/server.py`, use `mcp.create_server` from the SDK to initialize a basic server instance as shown in [[final/python/tool-server.md]].
- [x] **Tool Implementation (Example):**
  - In `python_tool_server/n1/tool.py`, implement a basic Obsidian tool (e.g., `list_notes`) using the `@tool` decorator. Define input parameters using Pydantic models or schema dictionaries.
  - Ensure the tool function accepts `context: ToolContext` and returns a `ToolResponse`.
- [x] **Tool Registration:** In `python_tool_server/server.py`, import and register the implemented tool(s) with the server instance (`server.register_tool(...)`).
- [x] **Transport Configuration:** Configure the Python Tool Server to use a specific transport mechanism that the `PythonToolAdapter` in the Core layer will communicate with. (e.g., HTTP with `uvicorn`, or potentially a custom RPC/messaging queue if needed). Update `PythonToolAdapter` accordingly.
- [x] **Runner Integration:** Update [[../src/run_server.py]] to start the Python Tool Server process when `--mode tool --tool-server python` or `--mode full` is specified. Ensure it uses the correct host/port configuration.
- [x] **Core Adapter Update:** Update `mcp_core/adapters/python_adapter.py` to communicate with the actual running Python Tool Server (e.g., make HTTP requests if using HTTP transport). Implement the `route_request` and `health_check` methods properly.
- [x] **End-to-End Test (Manual):** Manually test the flow: Send a request via the Proxy -> Core Layer -> Adapter Registry -> Python Tool Adapter -> Python Tool Server -> Tool -> Response back through the layers.

## 🛑 Pause Point & Collaboration

- **Review:** Let's verify the Python Tool Server setup, tool definition/registration, the communication between the `PythonToolAdapter` and the tool server, and the `run_server.py` integration.
- **Claude Thinking:** We can discuss the best transport mechanism between the Core and the Python Tool Server (HTTP, gRPC, etc.) and refine the tool implementation, focusing on error handling and context usage (`ToolContext`). We should also consult the @mcpPythSDK docs together for any specific SDK features we want to leverage.

## Next Phase

➡️ [[05 - TypeScript Tool Server and SDK]]

---

_This note belongs to the [[Implementation Plan MOC]]_
