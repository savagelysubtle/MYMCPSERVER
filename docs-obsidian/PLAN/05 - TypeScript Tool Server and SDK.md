---
created: 2025-03-30
tags: process, implementation-plan, phase-5
parent: [[Implementation Plan MOC]]
---

# Phase 5: TypeScript Tool Server and SDK

**Goal:** Implement the TypeScript Tool Server and define/integrate TypeScript tools (like Thinking, Another Tool) using the MCP TypeScript SDK.

## 📚 Prerequisite Reading

- [[final/typescript/tool-server.md]] - Primary technical document for this phase.
- [[final/filetree.md]] - Locate the `src/tool_servers/typescript_tool_server/` directory.
- MCP TypeScript SDK Documentation (@mcpTSDK) - Consult the official SDK docs for `McpServer`, `server.tool()`, `ToolContext`, transport options (stdio, SSE, WebSocket), Zod schema integration, etc.
- [[final/adapter/technical-v2.md]] - Review the `TypeScriptToolAdapter` requirements for communication.

## ✅ Checklist

- [ ] **Tool Server Structure:** Create the `src/tool_servers/typescript_tool_server/` directory. Initialize a Node.js project (`npm init -y` or `yarn init -y`). Set up TypeScript (`npm install --save-dev typescript @types/node` or yarn equivalent, `npx tsc --init`). Create `src/` dir and initial files like `src/index.ts`, `src/n3/index.ts` (Thinking Tool), `src/n4/index.ts` (Another Tool).
- [ ] **Dependencies:** Add the MCP TypeScript SDK (`npm install @modelcontextprotocol/sdk` or yarn equivalent) and Zod (`npm install zod`).
- [ ] **Basic Server Setup:** In `src/index.ts`, instantiate `McpServer` from the SDK as shown in [[final/typescript/tool-server.md]].
- [ ] **Tool Implementation (Example):**
  - In `src/n3/index.ts`, implement a basic Thinking tool using `server.tool()`. Define the input parameter schema using Zod.
  - Ensure the tool function accepts `context: ToolContext` and typed parameters, returning a promise resolving to the tool response structure.
- [ ] **Tool Registration:** In `src/index.ts`, import and register the implemented tool(s).
- [ ] **Transport Configuration:** Configure the TS Tool Server to use a transport mechanism compatible with the `TypeScriptToolAdapter` (e.g., HTTP via Express/Fastify, or stdio/SSE/WebSocket directly using SDK transports). Update `TypeScriptToolAdapter` accordingly.
- [ ] **Build Process:** Configure `tsconfig.json` and add build/start scripts to `package.json` (e.g., `"build": "tsc"`, `"start": "node dist/index.js"`).
- [ ] **Runner Integration:** Update [[../src/run_server.py]] to build (if necessary) and start the TypeScript Tool Server process (e.g., `node dist/index.js`) when `--mode tool --tool-server typescript` or `--mode full` is specified.
- [ ] **Core Adapter Update:** Update `mcp_core/adapters/ts_adapter.py` to communicate with the running TypeScript Tool Server. Implement `route_request` and `health_check`.
- [ ] **End-to-End Test (Manual):** Test the flow for a TypeScript tool request through all layers.

## 🛑 Pause Point & Collaboration

- **Review:** Let's check the TypeScript Tool Server setup, tool definition/registration (especially Zod schema usage), the communication between the `TypeScriptToolAdapter` and the TS server, and the `run_server.py` integration including the build step.
- **Claude Thinking:** We can explore the different transport options provided by the @mcpTSDK (stdio, SSE, WebSocket) and decide which is most suitable for communication with the Core Layer's adapter. We can also refine error handling within the TypeScript tools.

## Next Phase

➡️ [[06 - Integration, Testing, and Running]]

---

_This note belongs to the [[Implementation Plan MOC]]_
