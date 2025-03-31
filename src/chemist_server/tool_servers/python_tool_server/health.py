"""Tool server health monitoring."""

# Use explicit imports instead of relative imports
from src.chemist_server.mcp_core import HealthCheck, HealthStatus, logger


class ToolHealth(HealthCheck):
    """Tool server health check implementation."""

    def __init__(self):
        self.tools = {}

    async def check_health(self) -> dict:
        """Check tool server health."""
        try:
            # Check tool availability
            tools = await self.check_tools()

            return {
                "status": HealthStatus.HEALTHY,
                "details": {"active_tools": len(tools), "tools": tools},
            }
        except Exception as e:
            logger.error("Tool health check failed", error=str(e))
            return {"status": HealthStatus.UNHEALTHY, "error": str(e)}

    async def check_tools(self) -> list[str]:
        """Check available tools."""
        return list(self.tools.keys())

    def register_tool(self, name: str):
        """Register a tool for health monitoring."""
        self.tools[name] = {"status": "registered", "last_check": None}
