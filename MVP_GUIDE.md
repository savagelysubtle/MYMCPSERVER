# MVP Guide: Solidifying the MYMCPSERVER Implementation

## 1. Introduction

This guide focuses on the steps required to bring the current MYMCPSERVER implementation in the `src/` directory to a Minimum Viable Product (MVP) state. The goal is a stable, well-tested, and documented server that correctly implements the core requirements using the MCP Python SDK. This guide **does not** introduce new features but focuses on refining the existing codebase.

## 2. Current Implementation Overview (`@src/chemist_server/`)

The existing implementation consists of:

- **@src/chemist_server/server.py**: Main application runner using `anyio` for managing services.
- **@src/chemist_server/config.py**: Pydantic-based configuration (`AppConfig`, `LoggingConfig`, etc.) loading from environment variables and `.env.local`.
- **@src/chemist_server/**main**.py**: Entry point ensuring the package context is set up correctly.
- **`@src/chemist_server/mcp_core/`**:
  - **@src/chemist_server/mcp_core/app.py**: Defines the `FastMCP` application (`get_fastmcp_app`), registers tools directly, and manages the application lifespan (`core_lifespan`). It uses `Context` for request handling.
  - **@src/chemist_server/mcp_core/logger.py**: Implements `StructuredLogger` based on `structlog`.
  - **@src/chemist_server/mcp_core/registry.py**: Defines `ToolRegistry` for managing tool adapters and metadata, including `CircuitBreaker`.
  - **@src/chemist_server/mcp_core/router.py**: Basic routing logic (though current tools are registered directly in `app.py`).
  - **@src/chemist_server/mcp_core/errors.py**: Defines custom error classes.
  - **@src/chemist_server/mcp_core/health.py**: Basic health checking capabilities.
- **`@src/chemist_server/tool_servers/python_tool_server/cliTool/`**:
  - **@src/chemist_server/tool_servers/python_tool_server/cliTool/cli_tools.py**: Implements the core command execution logic (`run_command`), including security checks, Windows/UV adaptations, and command sanitization. Uses `CommandExecutor`.
  - **@src/chemist_server/tool_servers/python_tool_server/cliTool/git_tools.py**: Implements Git-specific commands (`get_git_status`, etc.).
  - **@src/chemist_server/tool_servers/python_tool_server/cliTool/command_tools.py**: Provides the underlying `CommandExecutor` and configuration.

## 3. SDK Alignment and Verification

The current code aligns with the MCP SDK in several ways:

- **Uses `FastMCP`**: Leverages the simplified `FastMCP` interface (`mcp.server.fastmcp`) as recommended for easier server creation (see @src/chemist_server/mcp_core/app.py).
- **Decorator Pattern**: Uses the `@app.tool()` decorator for registering tools (@src/chemist_server/mcp_core/app.py), matching the SDK examples.
- **Context Object**: Tool signatures correctly use the `Context` object (`mcp.server.fastmcp.Context`) for accessing request and lifespan state.
- **Transport Support**: @src/chemist_server/server.py correctly handles `stdio` and `sse`/`http` transport mechanisms based on configuration.
- **Structured Logging**: Implements robust logging (@src/chemist_server/mcp_core/logger.py), a good practice for server applications.

**MVP Action:**

- **Verify Dependency Versions**: Run `uv pip list` to confirm the installed versions of `mcp` and `fastmcp`. Ensure they are compatible (ideally `0.4.0+` for latest features, but verify based on current usage). Update `@pyproject.toml` to reflect the working versions used for the MVP.
  ```bash
  # Check installed versions
  uv pip list | grep mcp
  ```
- **Confirm Imports**: Double-check that imports like `Context`, `FastMCP`, `ServerSession` in @src/chemist_server/mcp_core/app.py align with the structure of the installed SDK version.

## 4. Essential Testing for MVP

Solid testing is crucial for MVP. Focus on testing the _existing_ functionality:

**MVP Actions:**

- **Create `tests/` directory**: Structure it as suggested previously (`unit/`, `integration/`, `fixtures/`) within `@src/`.
- **Unit Tests (`@src/tests/unit/`)**:
  - **`test_config.py`**: Test `AppConfig` (@src/chemist*server/config.py) loading from defaults, `.env.local`, environment variables, and CLI overrides. Test the `get_effective*\*` methods.
  - **`test_logger.py`**: Test `StructuredLogger` initialization (@src/chemist_server/mcp_core/logger.py) and basic message formatting (if custom logic exists beyond `structlog`).
  - **`test_registry.py`**: Test `ToolRegistry` (@src/chemist_server/mcp_core/registry.py) `register_tool`, `get_tool`, `get_metadata`, and `CircuitBreaker` interaction (mocking `BaseAdapter`).
  - **`test_command_tools.py`**: Test `CommandExecutor` (@src/chemist_server/tool_servers/python_tool_server/cliTool/command_tools.py) security checks (allowed commands/flags, path validation, restricted patterns) using various safe and unsafe command inputs. Test command sanitization/translation logic.
  - **`test_cli_tools.py`**: Test the main `run_command` function's (@src/chemist_server/tool_servers/python_tool_server/cliTool/cli_tools.py) argument parsing and interaction with `CommandExecutor`. Mock `CommandExecutor.execute`.
  - **`test_git_tools.py`**: Test the Git command functions (@src/chemist_server/tool_servers/python_tool_server/cliTool/git_tools.py). Mock the underlying `run_command` call to avoid actual Git operations in unit tests.
- **Integration Tests (`@src/tests/integration/`)**:
  - **`test_cli_execution.py`**: Test the _actual_ execution of safe `run_command` operations (e.g., `dir`, `echo`, `uv --version`) within the allowed directory.
  - **`test_app_startup.py`**: Test that the `FastMCP` app (@src/chemist_server/mcp_core/app.py) initializes correctly via `get_fastmcp_app` and the lifespan manager runs without errors.
  - **`test_tool_invocation.py`**: (More complex) If possible, simulate an MCP client call (or use test utilities if FastMCP provides them) to invoke a registered tool like `run_command` through the `FastMCP` app and verify the response.
- **Fixtures (`@src/tests/fixtures/`)**:
  - Create pytest fixtures for `AppConfig` instances with different settings.
  - Create fixtures for initializing `ToolRegistry` or `CommandExecutor`.
  - Create mock `Context` objects.

## 5. Code Style and Documentation for MVP

Consistent style and clear documentation improve maintainability.

**MVP Actions:**

- **Linter/Formatter**: Run `ruff check --fix .` and `black .` within the `@src/` directory to enforce consistent style. Configure these tools in `@pyproject.toml`.
- **Docstrings**: Add/improve docstrings for all public classes and functions in `@src/chemist_server/`, explaining their purpose, arguments, and return values. Use a standard format (e.g., Google style).

  ```python
  # Example for @src/chemist_server/config.py
  class AppConfig(BaseSettings):
      """Unified application configuration model.

      Loads settings from environment variables (prefixed with MCP_), .env.local,
      and applies command-line overrides. Provides access to nested configurations
      for logging, core server, etc., and helper methods for effective values.

      Attributes:
          vault_path: Resolved path to the Obsidian vault.
          logs_path: Resolved path for storing log files.
          components: Which components to run ('all', 'core', 'tool').
          transport: Transport mechanism ('stdio', 'sse', 'http').
          logging: Nested LoggingConfig object.
          core: Nested CoreConfig object.
          # ... other attributes
      """
      # ... rest of the class
  ```

- **README Update**: Ensure the main project `@README.md` includes clear instructions on how to set up the environment (`uv sync`), configure (`.env.local`), and run the MVP server (`python -m chemist_server`).

## 6. MVP Definition

Completing the actions above (SDK verification, comprehensive testing of existing features, code styling, and essential documentation) will result in a stable, reliable, and maintainable MVP of the MYMCPSERVER project.
