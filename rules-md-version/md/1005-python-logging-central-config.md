---
description: IMPORTANT ENSURE logging is configured centrally via configure_logging before use; AVOID ad-hoc logging setup
globs: 'src/chemist_server/server.py, src/chemist_server/tool_servers/python_tool_server/server.py, src/chemist_server/__main__.py'
alwaysApply: true
---

<aiDecision>
  description: IMPORTANT ENSURE logging is configured centrally via configure_logging before use; AVOID ad-hoc logging setup
  globs: "src/chemist_server/server.py, src/chemist_server/tool_servers/python_tool_server/server.py, src/chemist_server/__main__.py"
  alwaysApply: true
</aiDecision>

# Python Logging Standard: Central Configuration

<context>
  <role>Code Quality Agent</role>
  <purpose>Ensure logging is configured consistently from a single point using the project's configuration system.</purpose>
  <version>1.0.0</version>
</context>

<requirements>
  <requirement>MUST ensure `configure_logging(config)` from `chemist_server.mcp_core.logger.logger` is called exactly once, early in the main application entry point (`src/chemist_server/server.py`'s `main` function, after loading `AppConfig`).</requirement>
  <requirement>MUST remove any calls to `logging.basicConfig()` from other modules (like `tool_servers/python_tool_server/server.py`).</requirement>
  <requirement>MUST obtain logger instances using `logger = StructuredLogger(__name__)` in modules where logging is needed.</requirement>
  <requirement>MUST NOT add handlers directly to the root logger or individual loggers outside of the `configure_logging` function.</requirement>
  <requirement>ENSURE the `AppConfig` object passed to `configure_logging` is fully loaded, including any CLI overrides.</requirement>
</requirements>

<examples>
  <good-practice>
    <description>Correct central logging configuration in main entry point</description>
    <example>
      ```python
      # src/chemist_server/server.py (or __main__.py)

      from chemist_server.config import load_and_get_config
      from chemist_server.mcp_core.logger.logger import configure_logging, StructuredLogger
      import anyio
      # ... other imports ...

      def main() -> int:
          bootstrap_logger = logging.getLogger("bootstrap") # Basic logger for startup
          try:
              # ... parse args ...
              config = load_and_get_config(vars(args))

              # *** Configure logging centrally AFTER config is loaded ***
              configure_logging(config)

              # Now use structured logger
              main_logger = StructuredLogger("mymcpserver.runner")
              main_logger.info("Logging configured, starting services...")

              anyio.run(run_services, config)
              return 0
          except Exception as e:
              # Use bootstrap logger for critical failure before structured logging is ready
              bootstrap_logger.critical(f"Setup failed: {e}", exc_info=True)
              return 1

      if __name__ == "__main__":
          sys.exit(main())
      ```
    </example>

  </good-practice>

  <bad-practice>
    <description>Incorrect ad-hoc logging setup</description>
    <example>
      ```python
      # src/chemist_server/tool_servers/python_tool_server/server.py

      import logging # Should use StructuredLogger

      # BAD PRACTICE: Sets up basicConfig locally, ignoring central config
      logging.basicConfig(level=logging.DEBUG)

      def start_server():
          # ... server logic ...
          logging.info("Tool server started") # Uses root logger directly
      ```
    </example>

  </bad-practice>
</examples>

<rationale>
  Centralized logging configuration ensures all parts of the application adhere to the same logging level, format, and output destinations defined in the main `AppConfig`. Ad-hoc configuration leads to inconsistent logs and makes it difficult to manage logging behavior globally.
</rationale>
