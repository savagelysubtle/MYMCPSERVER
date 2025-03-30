"""Python adapter for MCP tools."""

import asyncio
import importlib
import inspect
from typing import Any, Dict, Optional

from ..errors import AdapterError
from ..logger import logger
from .base_adapter import BaseAdapter


class PythonAdapter(BaseAdapter):
    """Adapter for Python-based tools."""

    def __init__(self, module_path: str, function_name: str, load_module: bool = True):
        """Initialize Python adapter.

        Args:
            module_path: Import path to the Python module
            function_name: Name of the function to execute
            load_module: Whether to load the module immediately
        """
        self.module_path = module_path
        self.function_name = function_name
        self.module = None
        self.function = None

        if load_module:
            try:
                self._load_module()
            except Exception as e:
                logger.error(
                    f"Failed to load module {module_path}",
                    module=module_path,
                    error=str(e),
                )

    def _load_module(self) -> None:
        """Load the Python module.

        Raises:
            AdapterError: If module or function cannot be loaded
        """
        try:
            self.module = importlib.import_module(self.module_path)
            self.function = getattr(self.module, self.function_name, None)

            if self.function is None:
                raise AdapterError(
                    f"Function {self.function_name} not found in module {self.module_path}"
                )

            logger.info(
                f"Loaded module {self.module_path} function {self.function_name}",
                module=self.module_path,
                function=self.function_name,
            )
        except ImportError as e:
            raise AdapterError(
                f"Failed to import module {self.module_path}: {str(e)}"
            ) from e
        except AttributeError as e:
            raise AdapterError(
                f"Failed to get function {self.function_name} from module {self.module_path}: {str(e)}"
            ) from e

    async def execute(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute the Python function.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            context: Optional execution context

        Returns:
            Dict[str, Any]: Function execution result

        Raises:
            AdapterError: If execution fails
        """
        if self.function is None:
            try:
                self._load_module()
            except Exception as e:
                raise AdapterError(f"Failed to load module: {str(e)}") from e

        try:
            # Check if the function is async
            if inspect.iscoroutinefunction(self.function):
                result = await self.function(**parameters)
            else:
                # Run in executor if not async
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, lambda: self.function(**parameters)
                )

            # Ensure result is a dict
            if not isinstance(result, dict):
                result = {"result": result}

            return result
        except Exception as e:
            logger.error(
                f"Error executing {tool_name}",
                tool=tool_name,
                function=self.function_name,
                error=str(e),
            )
            raise AdapterError(f"Error executing {tool_name}: {str(e)}") from e

    async def health_check(self) -> Dict[str, Any]:
        """Check adapter health.

        Returns:
            Dict[str, Any]: Health check result

        Raises:
            AdapterError: If health check fails
        """
        try:
            if self.module is None:
                self._load_module()

            return {
                "status": "healthy",
                "module": self.module_path,
                "function": self.function_name,
                "loaded": self.module is not None and self.function is not None,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "module": self.module_path,
                "function": self.function_name,
                "error": str(e),
            }

    async def initialize(self) -> None:
        """Initialize the adapter.

        Raises:
            AdapterError: If initialization fails
        """
        try:
            if self.module is None:
                self._load_module()
        except Exception as e:
            raise AdapterError(f"Failed to initialize adapter: {str(e)}") from e

    async def shutdown(self) -> None:
        """Shutdown the adapter.

        Raises:
            AdapterError: If shutdown fails
        """
        # Nothing to do for Python adapter
        pass
