---
created: 2025-03-30
updated: 2025-03-30
tags: [architecture, logging, implementation, myMcpServer]
parent: [[../Project MOC]]
---

# Logging Centralization Strategy

## Context

The MCP system currently has two separate logging configurations:

1. `src/mcp_core/logger/config.py` with a `LogConfig` class
2. `src/config.py` with a `LoggingConfig` class

This dual configuration can lead to confusion and potential inconsistencies in logging behavior across the system.

## Decision

We will centralize logging configuration and management with the following approach:

### 1. Configuration Consolidation

- Use `LoggingConfig` from `src/config.py` as the single source of truth
- Deprecate and remove the separate `LogConfig` in `mcp_core/logger/config.py`
- Maintain the existing directory structure:

  ```
  logs/
  ├── core/     # Core service logs
  ├── proxy/    # Proxy service logs
  ├── server/   # Server-wide logs
  └── tools/    # Tool server logs
  ```

### 2. Logging Architecture

- Each service gets its own subdirectory under logs/
- Log files follow the pattern: `{service}.{date}.log`
- Rotation policies:
  - Max file size: 10MB
  - Keep 5 backup files
- Support both JSON and text formats
- Optional stdout logging for development

### 3. Service-to-Directory Mapping

```python
Service Name Pattern -> Log Directory
mcp_core.*          -> logs/core/
tool_servers.*      -> logs/tools/{server-name}/
mcp_proxy.*         -> logs/proxy/
other               -> logs/misc/
```

### 4. Implementation Strategy

1. Update `server.py` to initialize logging before any service starts
2. Ensure log directories exist during startup
3. Configure global logging parameters
4. Set up service-specific log handlers

## Consequences

### Positive

- Single source of truth for logging configuration
- Consistent logging behavior across all services
- Clear directory structure for log organization
- Easier log management and rotation

### Negative

- Need to migrate any services using the old configuration
- Brief one-time refactoring effort required

## Implementation Notes

### Code Changes Required

1. Remove `src/mcp_core/logger/config.py`
2. Update `src/server.py` to properly initialize logging
3. Update any services using old config to use AppConfig.logging

### Migration Path

1. Keep both configurations temporarily
2. Add deprecation warnings to old config
3. Migrate services to new config
4. Remove old config after all services migrated

## Validation

- Ensure all services log to correct directories
- Verify log rotation works as expected
- Confirm JSON/text formatting options
- Test stdout logging configuration

## Future Considerations

- Consider adding log aggregation
- Add log analysis tools
- Implement log level override per service
- Add structured logging validation

## Related Documentation

### Project Documentation

- [[../mcpPlanning/final/core/overview-v2|Core Implementation Overview]]
- [[../mcpPlanning/final/core/technical-v2|Technical Implementation]]

### MCP Knowledge

- [[../../../mcpKnowledge/core/MCP Server Architecture|MCP Architecture]]
- [[../../../mcpKnowledge/core/MCP Central Hub|MCP Central Hub]]

### Implementation Examples

- [[../../../mcpKnowledge/development/MCP Hub Implementation|Hub Implementation Guide]]
- [[../../../mcpKnowledge/development/Configuration Examples|Configuration Examples]]

---

[[../Project MOC|← Back to Project MOC]]
