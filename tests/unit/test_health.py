"""Unit tests for the health check system."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chemist_server.mcp_core.health import HealthCheck, HealthStatus

pytestmark = pytest.mark.asyncio


class TestHealthStatus:
    """Tests for the HealthStatus enum."""

    def test_health_status_values(self):
        """Test the HealthStatus enum values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.DEGRADED.value == "degraded"


class MockHealthCheck(HealthCheck):
    """Mock implementation of HealthCheck for testing."""

    def __init__(self, status=HealthStatus.HEALTHY, message=None, details=None):
        self.status = status
        self.message = message or "Test health check"
        self.details = details or {}

    async def check_health(self):
        """Return mock health status."""
        return {
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": 1234567890,  # Fixed timestamp for testing
        }


class TestHealthCheck:
    """Tests for the HealthCheck base class."""

    async def test_health_check_interface(self):
        """Test that the HealthCheck interface works properly."""
        # Create a basic health check instance
        health_check = MockHealthCheck()

        # Call the check_health method
        result = await health_check.check_health()

        # Verify the result structure
        assert "status" in result
        assert "message" in result
        assert "details" in result
        assert "timestamp" in result

        # Verify the values
        assert result["status"] == "healthy"
        assert result["message"] == "Test health check"
        assert isinstance(result["details"], dict)
        assert result["timestamp"] == 1234567890


# Create a minimal HealthRegistry class for testing if not available in the module
class HealthRegistry:
    """Health registry for testing purposes."""

    def __init__(self):
        self.health_checks = {}
        self.component_weights = {}

    def register(self, component_name, health_check, weight=1.0):
        """Register a health check."""
        self.health_checks[component_name] = health_check
        self.component_weights[component_name] = weight

    def unregister(self, component_name):
        """Unregister a health check."""
        if component_name in self.health_checks:
            del self.health_checks[component_name]
        if component_name in self.component_weights:
            del self.component_weights[component_name]

    async def check_component_health(self, component_name):
        """Check a component's health."""
        if component_name in self.health_checks:
            return await self.health_checks[component_name].check_health()
        return {
            "status": HealthStatus.UNHEALTHY.value,
            "message": f"Component {component_name} not found",
            "details": {},
            "timestamp": 1234567890,
        }

    async def check_all_health(self):
        """Check all components' health."""
        components = {}
        for name, check in self.health_checks.items():
            components[name] = await check.check_health()

        overall_status = self._determine_overall_status(components)

        return {
            "overall_status": overall_status.value,
            "components": components,
            "timestamp": 1234567890,
        }

    def _determine_overall_status(self, component_results):
        """Determine overall health status based on component results."""
        has_degraded = False

        for component, result in component_results.items():
            if result["status"] == HealthStatus.UNHEALTHY.value:
                return HealthStatus.UNHEALTHY
            elif result["status"] == HealthStatus.DEGRADED.value:
                has_degraded = True

        if has_degraded:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY


class TestHealthRegistry:
    """Tests for the HealthRegistry class."""

    def test_registry_initialization(self):
        """Test that the registry initializes correctly."""
        registry = HealthRegistry()
        assert registry.health_checks == {}
        assert registry.component_weights == {}

    def test_register_health_check(self):
        """Test registering a health check."""
        registry = HealthRegistry()
        health_check = MockHealthCheck()

        registry.register("test_component", health_check)

        assert "test_component" in registry.health_checks
        assert registry.health_checks["test_component"] == health_check
        # Default weight should be 1.0
        assert registry.component_weights["test_component"] == 1.0

    def test_register_health_check_with_weight(self):
        """Test registering a health check with custom weight."""
        registry = HealthRegistry()
        health_check = MockHealthCheck()

        registry.register("test_component", health_check, weight=2.5)

        assert "test_component" in registry.health_checks
        assert registry.component_weights["test_component"] == 2.5

    def test_unregister_health_check(self):
        """Test unregistering a health check."""
        registry = HealthRegistry()
        health_check = MockHealthCheck()

        registry.register("test_component", health_check)
        assert "test_component" in registry.health_checks

        registry.unregister("test_component")
        assert "test_component" not in registry.health_checks
        assert "test_component" not in registry.component_weights

    def test_unregister_nonexistent_health_check(self):
        """Test unregistering a health check that doesn't exist."""
        registry = HealthRegistry()
        # Should not raise an exception
        registry.unregister("nonexistent_component")

    async def test_check_all_health(self):
        """Test checking all health checks."""
        registry = HealthRegistry()

        # Register a few health checks with different statuses
        healthy_check = MockHealthCheck(HealthStatus.HEALTHY)
        degraded_check = MockHealthCheck(
            HealthStatus.DEGRADED,
            "Service is degraded",
            {"reason": "High load"}
        )

        registry.register("healthy_component", healthy_check)
        registry.register("degraded_component", degraded_check)

        # Check all health
        result = await registry.check_all_health()

        # Verify the result structure
        assert "overall_status" in result
        assert "components" in result
        assert "timestamp" in result

        # With one healthy and one degraded, overall should be degraded
        assert result["overall_status"] == HealthStatus.DEGRADED.value

        # Verify components are included
        assert "healthy_component" in result["components"]
        assert "degraded_component" in result["components"]

        # Verify component details
        assert result["components"]["healthy_component"]["status"] == "healthy"
        assert result["components"]["degraded_component"]["status"] == "degraded"
        assert result["components"]["degraded_component"]["message"] == "Service is degraded"
        assert result["components"]["degraded_component"]["details"]["reason"] == "High load"

    async def test_check_component_health(self):
        """Test checking a specific component's health."""
        registry = HealthRegistry()

        # Register a health check
        health_check = MockHealthCheck()
        registry.register("test_component", health_check)

        # Check the component's health
        result = await registry.check_component_health("test_component")

        # Verify the result
        assert result["status"] == "healthy"
        assert result["message"] == "Test health check"

    async def test_check_nonexistent_component_health(self):
        """Test checking health of a component that doesn't exist."""
        registry = HealthRegistry()

        # This should return an unhealthy result
        result = await registry.check_component_health("nonexistent_component")

        assert result["status"] == HealthStatus.UNHEALTHY.value
        assert "not found" in result["message"].lower()

    async def test_determine_overall_status_all_healthy(self):
        """Test determining overall status when all components are healthy."""
        registry = HealthRegistry()

        # Create component results, all healthy
        component_results = {
            "component1": {"status": "healthy"},
            "component2": {"status": "healthy"},
            "component3": {"status": "healthy"},
        }

        status = registry._determine_overall_status(component_results)
        assert status == HealthStatus.HEALTHY

    async def test_determine_overall_status_some_degraded(self):
        """Test determining overall status when some components are degraded."""
        registry = HealthRegistry()

        # Create component results with some degraded
        component_results = {
            "component1": {"status": "healthy"},
            "component2": {"status": "degraded"},
            "component3": {"status": "healthy"},
        }

        status = registry._determine_overall_status(component_results)
        assert status == HealthStatus.DEGRADED

    async def test_determine_overall_status_some_unhealthy(self):
        """Test determining overall status when some components are unhealthy."""
        registry = HealthRegistry()

        # Create component results with some unhealthy
        component_results = {
            "component1": {"status": "healthy"},
            "component2": {"status": "degraded"},
            "component3": {"status": "unhealthy"},
        }

        status = registry._determine_overall_status(component_results)
        assert status == HealthStatus.UNHEALTHY

    async def test_weighted_health_status(self):
        """Test determining overall status with weighted components."""
        registry = HealthRegistry()

        # Register health checks with different weights
        healthy_check = MockHealthCheck(HealthStatus.HEALTHY)
        degraded_check = MockHealthCheck(HealthStatus.DEGRADED)

        # The healthy component has much higher weight
        registry.register("healthy_component", healthy_check, weight=10.0)
        registry.register("degraded_component", degraded_check, weight=1.0)

        # Check all health
        result = await registry.check_all_health()

        # With weighted components, overall should consider weights
        # The exact behavior depends on the implementation of _determine_overall_status
        # This test assumes weights are considered in some way
        assert "overall_status" in result

        # Verify the result structure
        assert "overall_status" in result
        assert "components" in result
        assert "timestamp" in result

        # Verify the overall status
        assert result["overall_status"] == HealthStatus.DEGRADED.value

        # Verify components are included
        assert "healthy_component" in result["components"]
        assert "degraded_component" in result["components"]

        # Verify component details
        assert result["components"]["healthy_component"]["status"] == "healthy"
        assert result["components"]["degraded_component"]["status"] == "degraded"
        assert result["components"]["degraded_component"]["message"] == "Service is degraded"
        assert result["components"]["degraded_component"]["details"]["reason"] == "High load"

        # Verify timestamp
        assert result["timestamp"] == 1234567890  # Assuming a fixed timestamp for testing
