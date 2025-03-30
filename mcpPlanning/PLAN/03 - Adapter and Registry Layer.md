---
created: 2025-03-30
tags: process, implementation-plan, phase-3
parent: [[Implementation Plan MOC]]
---

# Phase 3: Adapter and Registry Layer

**Goal:** Implement the core logic within the MCP Core Layer for routing requests to different tool servers, managing versions, and monitoring health using circuit breakers.

## 📚 Prerequisite Reading

- [[final/adapter/technical-v2.md]] - This is the primary technical specification for this phase.
- [[final/core/technical-v2.md]] - Understand how the Core Layer's `Router` component interacts with the Registry.
- [[final/filetree.md]] - Locate the `src/mcp_core/adapters/` directory.

## ✅ Checklist

- [x] **Adapter Structure:** Create the directory `src/mcp_core/adapters/` and the initial files: `__init__.py`, `base_adapter.py`, `registry.py`, `circuit_breaker.py`, `errors.py` (can reuse/extend core errors if appropriate).
- [x] **Base Adapter:** Define the `BaseAdapter` abstract class in `base_adapter.py` as per the spec.
- [x] **Circuit Breaker:** Implement the `CircuitState` enum and `CircuitBreaker` class in `circuit_breaker.py` based on the spec.
- [x] **Adapter Registry:** Implement the `AdapterRegistry` class in `registry.py`. Include methods for `register_adapter`, `get_adapter`, and the background health monitoring task (`_monitor_adapter_health`).
- [x] **Adapter Errors:** Define specific errors like `AdapterNotFoundError`, `VersionNotFoundError`, `CircuitBreakerOpenError` in `adapters/errors.py` or the main `mcp_core/errors.py`.
- [x] **Core Integration:** Modify the `Router` class within `mcp_core/app.py` (or wherever it's defined based on Phase 1) to:
  - Initialize the `AdapterRegistry`.
  - Use `registry.get_adapter()` to find the appropriate adapter based on the request.
  - Use the adapter's associated `circuit_breaker.execute()` method to wrap the call to `adapter.route_request()`.
- [x] **Dummy Adapters:** Create basic `PythonToolAdapter` and `TypeScriptToolAdapter` classes in `python_adapter.py` and `ts_adapter.py` respectively. For now, their `route_request` can just log the call and return a dummy success response, and `health_check` can return a static healthy status.
- [x] **Registration in Core:** In the main `MCPCore` application setup (`mcp_core/app.py`), instantiate and register these dummy adapters with the `AdapterRegistry` upon startup.

## 🛑 Pause Point & Collaboration

- **Review:** The implementation of the `AdapterRegistry` (implemented as `ToolRegistry`), the `CircuitBreaker`, and their integration into the Core Layer's `Router` is now complete. The dummy adapters for Python and TypeScript are registered correctly, and the Router provides the necessary methods to interact with them.
- **Implementation Summary:** We have:
  - Created a `Router` class that integrates with the existing `ToolRegistry`
  - Implemented API routes for tool execution and information retrieval
  - Registered dummy adapters for testing
  - Added proper error handling and circuit breaking for fault tolerance
  - Set up health checking for adapters

## Next Phase

➡️ [[04 - Python Tool Server and SDK]]

---

_This note belongs to the [[Implementation Plan MOC]]_
