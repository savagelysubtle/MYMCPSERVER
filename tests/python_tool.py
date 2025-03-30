"""Example Python tool for testing the adapter."""

import time
from typing import Any


async def execute_tool(**kwargs: Any) -> dict[str, Any]:
    """Execute the example Python tool.

    Args:
        **kwargs: Tool parameters

    Returns:
        Dict[str, Any]: Tool execution result
    """
    # Simulate some processing
    time.sleep(0.1)

    # Return a sample result
    return {
        "tool": "python-example",
        "executed_at": time.time(),
        "received_parameters": kwargs,
        "sample_result": "This is a test result from the Python tool",
    }
