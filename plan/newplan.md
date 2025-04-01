# Plan to Fix Ruff Errors

This plan outlines the steps to resolve the Ruff linting and formatting errors identified in the MYMCPSERVER project.

**Error Summary (Based on previous analysis):**

- **Blocker:** Syntax Error in `tests/unit/test_health.py`
- Potential Bugs / Bad Practices (`Bxxx`, `RUFxxx`)
- Unused Variables/Arguments/Imports (`ARGxxx`, `F841`, `F401`)
- Style/Refactoring Suggestions (`SIMxxx`, `UPxxx`)
- Import Style (`TIDxxx`, `E402`)
- Naming Conventions (`Nxxx`)
- Complexity (`C901`)
- Testing Specific (`PTxxx`)
- Obsolete Configuration (`ANN101`, `ANN102` in ignore list)

---

## Guiding Principle for Manual Fixes

**CRITICAL:** Before applying any _manual_ fix suggested by Ruff (especially in Phases 2 and 3), **always read the surrounding code context**. Ask:

1.  **Why was the code written this way originally?** Is there a subtle reason?
2.  **Is the Ruff suggestion the _best_ fix in this specific context?** Does it improve clarity and maintainability, or just satisfy the linter?
3.  **Should this specific instance be ignored?** If the code is correct and clearer as-is, consider using a `# noqa: RULE_CODE` comment on that line.
4.  **Should the rule be ignored globally or for this file?** If a rule consistently flags valid patterns in your project, consider adjusting the `pyproject.toml` configuration.

**Prioritize correctness and maintainability over blind adherence to linting rules.**

---

## Phased Approach

**Phase 1: Unblock and Easy Fixes**

1.  **Goal:** Resolve the critical syntax error and apply all straightforward, automatic fixes provided by Ruff. (Manual judgment is less critical here as these are often unambiguous fixes).
2.  **Steps:**
    - **Fix Syntax Error:** Manually edit `tests/unit/test_health.py` and remove or correct the invalid ``` characters at or near line 315. Ensure the file ends with valid Python syntax.
    - **Remove Obsolete Ignores:** Edit `pyproject.toml`. In the `[tool.ruff.lint]` section, remove `"ANN101"` and `"ANN102"` from the `ignore` list.
    - **Run Initial Format:** Execute `ruff format .` in the terminal from the project root.
    - **Run Autofixes:** Execute `ruff check --fix .` in the terminal. Review the output to see which errors were fixed.
    - **Run Final Format:** Execute `ruff format .` again to clean up any formatting changes resulting from fixes.
3.  **Verification:** Run `ruff check .` again. The syntax error should be gone, and the count of remaining errors significantly reduced.

**Phase 2: Manual Style and Refactoring**

1.  **Goal:** Address errors requiring manual code changes, focusing on style, naming, and minor refactorings suggested by Ruff that weren't automatically fixable.
2.  **Steps (Address in any order, applying the "Guiding Principle for Manual Fixes" above for each item):**
    - **`SIM101` (Merge `isinstance`):** Review `aichemist_mcp_hub_new.py:558`. If appropriate, refactor to use `isinstance(v, (httpx.Client, httpx.AsyncClient))`.
    - **`SIM102` (Combine nested `if`):** Review `cli_tools.py:537`, `conftest.py:129`, `aichemist_mcp_hub_new.py:558`, `aichemist_mcp_hub_new.py:3258`. If combining improves clarity without obscuring logic, combine the nested `if` conditions using `and`.
    - **`N999` (Invalid module name):** Review imports related to `cliTool`. If renaming is safe, rename the directory `src/chemist_server/tool_servers/python_tool_server/cliTool` to `src/chemist_server/tool_servers/python_tool_server/cli_tool` and update imports.
    - **`N802` (Invalid function name):** Review `visit_ClassDef`, `visit_FunctionDef`, `visit_AnnAssign` in `aichemist_mcp_hub_new.py`. _Decision:_ These are standard `ast.NodeVisitor` methods. Renaming would break the pattern. Add `# noqa: N802` to the end of the definition lines for these specific methods.
    - **`B023` (Lambda variable binding):** Review the lambdas (`stdio.py:224`, tests). _Decision:_ For test `side_effect` lambdas, this is likely acceptable. For `stdio.py:224`, analyze if late binding is a risk; if so, refactor using default arguments (`lambda s=stream, js=json_str: s.write(js + "\n")`) or a helper function.
    - **`B904` (Raise from exception context):** Review `command_tools.py`. _Decision:_ This improves debugging. Modify the `raise` statements inside `except` blocks to `raise ... from e` (or `from None` if the context isn't useful).
    - **`B018` (Useless expression):** Review `test_logger.py:244`. _Decision:_ This looks like leftover test code. Remove the `1 / 0` line.
    - **`PT011` (`pytest.raises` too broad):** Review `test_validation.py:312`. _Decision:_ Making this more specific improves test quality. Update to use `pytest.raises(ValueError, match="substring of expected error")`. Determine the expected error message substring.
    - **`RUF006` (Store `asyncio.create_task`):** Review `stdio.py:122` and `websocket.py:55`. _Decision:_ Determine if these background tasks need to be managed (e.g., cancelled on shutdown). If yes, assign `self.read_task = asyncio.create_task(...)` and add cancellation logic. If they are truly fire-and-forget (less common for servers), consider adding `# noqa: RUF006`.
3.  **Verification:** Run `ruff check .` again. These specific errors should now be resolved or appropriately ignored.

**Phase 3: Address Complexity (`C901`)**

1.  **Goal:** Refactor functions/methods identified as overly complex to improve readability and maintainability, applying judgment about the necessity and nature of the refactoring.
2.  **Steps:**
    - Identify all functions/methods flagged with `C901`.
    - For each function (prioritizing the most complex):
      - **Read and Understand:** Fully grasp the function's current logic and purpose.
      - **Analyze Complexity:** Determine _why_ Ruff flags it as complex (e.g., too many branches, deep nesting, too long).
      - **Evaluate Refactoring:** Decide if refactoring genuinely improves readability and maintainability or if the complexity is inherent and well-managed. Can logical units be extracted into helper functions?
      - **Execute Refactoring (If beneficial):** Extract sub-tasks into clearly named private helper functions/methods. Update the original function to call the helpers. Ensure tests still pass.
      - **Consider Ignoring (If complexity is justified):** If the function is complex but clear and breaking it down would obscure the logic, consider adding `# noqa: C901` to the function definition line with a brief comment explaining why.
3.  **Verification:** Run `ruff check .` periodically. `C901` errors should decrease or be explicitly ignored. Run `pytest` frequently to catch regressions.

**Phase 4: Final Verification and Cleanup**

1.  **Goal:** Ensure all Ruff errors are addressed (either fixed or consciously ignored) and the codebase is clean and functional.
2.  **Steps:**
    - Run `ruff check .` one last time. Address any remaining errors.
    - Run `ruff format . --check`. Ensure there are no formatting issues.
    - Run the full test suite (`pytest`). Ensure all tests pass.
    - Manually review changes, especially `# noqa` additions and complexity refactoring, for clarity and correctness.
3.  **Outcome:** A codebase compliant with the configured Ruff rules, with conscious decisions made about rule application.

---
