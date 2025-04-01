# Expansion Guide: Enhancing MYMCPSERVER Beyond MVP

## 1. Introduction

This guide outlines potential enhancements and expansion paths for the MYMCPSERVER project, building upon the stable foundation established by the MVP (Minimum Viable Product). These suggestions aim to add features, improve robustness, and leverage more advanced MCP capabilities.

## 2. Building on the MVP Architecture

The MVP provides a solid base:

- **Configurable Core**: @src/chemist_server/config.py allows easy adjustments.
- **Structured Logging**: Provides observability (@src/chemist_server/mcp_core/logger.py).
- **Tool Registration**: @src/chemist_server/mcp_core/app.py directly registers tools.
- **Basic CLI Tools**: @src/chemist_server/tool_servers/python_tool_server/cliTool/ offers secure command execution.

## 3. Potential Expansion Areas

### 3.1. Advanced Tooling & Resources

- **Implement MCP Resources**: Beyond tools (actions), add MCP resources (data sources). Use `@app.resource_template()` from `FastMCP` (requires v0.4.0+).

  - **Example**: Expose files from the `@docs-obsidian` vault.

    ```python
    # In @src/chemist_server/mcp_core/app.py or a dedicated resource module
    from mcp.server.fastmcp import FileResource
    from mcp.server.fastmcp.resource_types import ResourceNotFoundError
    import os
    import aiofiles # Add 'aiofiles' to dependencies

    # Helper to get vault path from config (assuming it's added to CoreLifespanContext)
    def get_vault_path(ctx: Context) -> Path:
        # Assumes vault_path is accessible via ctx.lifespan.config
        # Requires CoreLifespanContext in @src/chemist_server/mcp_core/app.py to hold AppConfig
        return ctx.lifespan.config.vault_path

    @app.resource_template("obsidian://vault/{file_path:path}")
    async def get_obsidian_note(
        ctx: Context[ServerSession, CoreLifespanContext],
        file_path: str
    ) -> FileResource:
        """Provides access to notes within the Obsidian vault."""
        vault_path = get_vault_path(ctx)
        full_path = vault_path / file_path

        logger.info(f"Attempting to access resource: {full_path}")

        # Basic security check: Ensure path is within the vault
        if not full_path.is_file() or not str(full_path.resolve()).startswith(str(vault_path.resolve())):
             logger.warning(f"Resource not found or access denied: {file_path}")
             raise ResourceNotFoundError(f"Note not found: {file_path}")

        async with aiofiles.open(full_path, mode='r', encoding='utf-8') as f:
            content = await f.read()

        # Determine mime type (basic example)
        mime_type = "text/markdown" if file_path.endswith(".md") else "text/plain"

        return FileResource(
            content=content,
            mime_type=mime_type,
            metadata={"vault_path": file_path}
        )
    ```

- **Develop More Sophisticated Tools**: Create tools that interact with external APIs (e.g., search, knowledge bases) or perform complex local tasks (code analysis, refactoring). Remember to handle dependencies and potential failures.
- **Utilize Typed Messages**: For tools returning complex data, use Pydantic models and `mcp.server.fastmcp.types.TypedMsg` for structured responses instead of basic `dict`.

### 3.2. Dynamic Tool Discovery & Management

- **Refactor Tool Registration**: Move tool definitions out of @src/chemist_server/mcp_core/app.py into separate modules within `tool_servers/` (e.g., @src/chemist_server/tool_servers/python_tool_server/git_tools.py, `tool_servers/python_tool_server/file_tools.py`).
- **Implement Discovery**: Create a function (e.g., in @src/chemist_server/mcp_core/registry.py or @src/chemist_server/mcp_core/app.py) that dynamically imports modules from `@src/chemist_server/tool_servers/` and calls a convention-based registration function within each (e.g., `register_tools(app: FastMCP)`).

  ```python
  # Example in @src/chemist_server/mcp_core/app.py lifespan or a dedicated function
  import pkgutil
  import importlib
  import chemist_server.tool_servers.python_tool_server as tool_pkg # Adjust import as needed

  async def discover_and_register_tools(app: FastMCP):
      package = tool_pkg
      package_path = package.__path__
      prefix = package.__name__ + "."

      logger.info(f"Discovering tools in {package_path}")
      for _, module_name, _ in pkgutil.walk_packages(package_path, prefix):
          if "__pycache__" in module_name: # Skip cache directories
              continue
          try:
              logger.debug(f"Importing module: {module_name}")
              module = importlib.import_module(module_name)
              if hasattr(module, "register_tools") and callable(module.register_tools):
                  logger.info(f"Registering tools from {module_name}")
                  # Decide if register_tools should be async or sync
                  if asyncio.iscoroutinefunction(module.register_tools):
                      await module.register_tools(app)
                  else:
                      module.register_tools(app)
              else:
                  logger.debug(f"No register_tools function found in {module_name}")
          except Exception as e:
              logger.error(f"Failed to load or register tools from {module_name}: {e}", exc_info=True)

  # Call this during app startup (e.g., within core_lifespan in @src/chemist_server/mcp_core/app.py)
  # Example: async with core_lifespan(app) as lifespan_ctx:
  #             await discover_and_register_tools(app)
  #             yield lifespan_ctx
  ```

- **Tool Versioning**: Enhance @src/chemist_server/mcp_core/registry.py (`ToolRegistry`) to handle multiple versions of the same tool if needed.

### 3.3. Enhanced Configuration & Security

- **Tool-Specific Configuration**: Allow individual tools or toolsets to have their own configuration sections within @src/chemist_server/config.py or separate config files.
- **Authentication/Authorization**: Implement robust authentication (e.g., bearer tokens checked in middleware or via MCP context) and authorization (checking permissions before executing tools).
- **Secrets Management**: Integrate with a proper secrets management solution (like HashiCorp Vault or cloud provider secrets managers) instead of relying solely on environment variables for sensitive data.

### 3.4. Improved Observability

- **Metrics**: Add metrics collection (e.g., using Prometheus client libraries) to track tool usage frequency, execution time, success/failure rates, and resource consumption. Expose a metrics endpoint (might require adding a small HTTP server component if using stdio).
- **Tracing**: Implement distributed tracing (e.g., using OpenTelemetry) to follow requests across different components, especially if integrating with external services.

### 3.5. Asynchronous Task Handling

- **Background Tasks**: For long-running tools, consider using a background task queue (e.g., Celery, ARQ) managed by `anyio` (@src/chemist_server/server.py) or a separate process. The tool could immediately return a task ID, and the client could poll for results or receive a notification.

### 3.6. Advanced MCP Features

- **MCP Prompts**: Define reusable prompt templates using `@app.prompt()` in @src/chemist_server/mcp_core/app.py.
- **MCP Completions**: Implement completion providers (`@app.completion()`) in @src/chemist_server/mcp_core/app.py to assist users with tool parameters or resource URIs.
- **Client Callbacks (Sampling/Roots)**: If needed, allow the server to request information or actions from the client (requires client support and changes to server logic).

## 4. Refactoring and Code Structure

- **Modularize `mcp_core`**: Break down @src/chemist_server/mcp_core/app.py further. Tool registration logic should move out. Consider dedicated modules for request handling, response formatting, etc.
- **Service Layer**: Introduce a service layer between the MCP handlers (@src/chemist_server/mcp_core/app.py) and the core logic (@src/chemist_server/tool_servers/python_tool_server/cliTool/, etc.) to decouple the MCP interface from the business logic.
- **Dependency Injection**: Explore using a dependency injection framework to manage dependencies like the `ToolRegistry`, `Config`, and `CommandExecutor` more explicitly.

## 5. Conclusion

The MVP provides a launchpad. By incrementally adding features like resources, dynamic discovery, enhanced security, and better observability, MYMCPSERVER can evolve into a highly capable and robust MCP integration point.
