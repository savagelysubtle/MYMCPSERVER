"""Metrics collectors for MCP Core."""

import time
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field

from ..logger import logger


@dataclass
class Metric:
    """Base class for metrics."""

    name: str
    description: str
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class Counter(Metric):
    """Counter metric type."""

    value: int = 0

    def increment(self, amount: int = 1) -> None:
        """Increment counter.

        Args:
            amount: Amount to increment by
        """
        self.value += amount


@dataclass
class Gauge(Metric):
    """Gauge metric type."""

    value: float = 0.0

    def set(self, value: float) -> None:
        """Set gauge value.

        Args:
            value: Value to set
        """
        self.value = value

    def increment(self, amount: float = 1.0) -> None:
        """Increment gauge.

        Args:
            amount: Amount to increment by
        """
        self.value += amount

    def decrement(self, amount: float = 1.0) -> None:
        """Decrement gauge.

        Args:
            amount: Amount to decrement by
        """
        self.value -= amount


@dataclass
class Histogram(Metric):
    """Histogram metric type."""

    buckets: list[float] = field(
        default_factory=lambda: [
            0.005,
            0.01,
            0.025,
            0.05,
            0.1,
            0.25,
            0.5,
            1,
            2.5,
            5,
            10,
        ]
    )
    bucket_values: dict[float, int] = field(default_factory=dict)
    sum: float = 0.0
    count: int = 0

    def __post_init__(self) -> None:
        """Initialize bucket values."""
        self.bucket_values = dict.fromkeys(self.buckets, 0)
        # Add Inf bucket
        self.bucket_values[float("inf")] = 0

    def observe(self, value: float) -> None:
        """Record an observation.

        Args:
            value: Value to observe
        """
        self.sum += value
        self.count += 1

        # Update buckets
        for bucket in self.buckets + [float("inf")]:
            if value <= bucket:
                self.bucket_values[bucket] += 1


class MetricsCollector(ABC):
    """Base class for metrics collectors."""

    def __init__(self, namespace: str) -> None:
        """Initialize metrics collector.

        Args:
            namespace: Metrics namespace
        """
        self.namespace = namespace
        self.counters: dict[str, Counter] = {}
        self.gauges: dict[str, Gauge] = {}
        self.histograms: dict[str, Histogram] = {}

    def create_counter(
        self, name: str, description: str, labels: dict[str, str] | None = None
    ) -> Counter:
        """Create a counter metric.

        Args:
            name: Metric name
            description: Metric description
            labels: Metric labels

        Returns:
            Counter: New counter metric
        """
        full_name = f"{self.namespace}_{name}"
        counter = Counter(full_name, description, labels or {})
        self.counters[full_name] = counter
        return counter

    def create_gauge(
        self, name: str, description: str, labels: dict[str, str] | None = None
    ) -> Gauge:
        """Create a gauge metric.

        Args:
            name: Metric name
            description: Metric description
            labels: Metric labels

        Returns:
            Gauge: New gauge metric
        """
        full_name = f"{self.namespace}_{name}"
        gauge = Gauge(full_name, description, labels or {})
        self.gauges[full_name] = gauge
        return gauge

    def create_histogram(
        self,
        name: str,
        description: str,
        buckets: list[float] | None = None,
        labels: dict[str, str] | None = None,
    ) -> Histogram:
        """Create a histogram metric.

        Args:
            name: Metric name
            description: Metric description
            buckets: Histogram buckets
            labels: Metric labels

        Returns:
            Histogram: New histogram metric
        """
        full_name = f"{self.namespace}_{name}"
        histogram = Histogram(full_name, description, labels or {}, buckets or [])
        self.histograms[full_name] = histogram
        return histogram

    def get_all_metrics(self) -> Sequence[Metric]:
        """Get all metrics.

        Returns:
            Sequence[Metric]: All metrics
        """
        return (
            list(self.counters.values())
            + list(self.gauges.values())
            + list(self.histograms.values())
        )

    @abstractmethod
    def collect(self) -> None:
        """Collect metrics."""
        pass


class RequestMetricsCollector(MetricsCollector):
    """Collector for request-related metrics."""

    def __init__(self) -> None:
        """Initialize request metrics collector."""
        super().__init__("mcp_request")

        # Define metrics
        self.request_count = self.create_counter(
            "total", "Total number of requests processed"
        )

        self.request_success_count = self.create_counter(
            "success_total", "Total number of successful requests"
        )

        self.request_error_count = self.create_counter(
            "error_total", "Total number of failed requests"
        )

        self.request_duration = self.create_histogram(
            "duration_seconds", "Request duration in seconds"
        )

        self.request_active = self.create_gauge("active", "Number of active requests")

        logger.info("Request metrics collector initialized")

    def collect(self) -> None:
        """Collect metrics."""
        # This collector is updated in real-time, so no collection needed
        pass

    def record_request_start(self) -> float:
        """Record the start of a request.

        Returns:
            float: Start timestamp
        """
        self.request_count.increment()
        self.request_active.increment()
        return time.time()

    def record_request_end(self, start_time: float, success: bool = True) -> float:
        """Record the end of a request.

        Args:
            start_time: Request start timestamp
            success: Whether request was successful

        Returns:
            float: Request duration in seconds
        """
        duration = time.time() - start_time
        self.request_duration.observe(duration)
        self.request_active.decrement()

        if success:
            self.request_success_count.increment()
        else:
            self.request_error_count.increment()

        return duration


class ToolMetricsCollector(MetricsCollector):
    """Collector for tool-related metrics."""

    def __init__(self) -> None:
        """Initialize tool metrics collector."""
        super().__init__("mcp_tool")

        # Define metrics
        self.tool_call_count = self.create_counter(
            "calls_total", "Total number of tool calls"
        )

        self.tool_success_count = self.create_counter(
            "success_total", "Total number of successful tool calls"
        )

        self.tool_error_count = self.create_counter(
            "error_total", "Total number of failed tool calls"
        )

        self.tool_duration = self.create_histogram(
            "duration_seconds", "Tool call duration in seconds"
        )

        # Track tool-specific metrics
        self.tool_specific_calls: dict[str, Counter] = {}
        self.tool_specific_errors: dict[str, Counter] = {}
        self.tool_specific_durations: dict[str, Histogram] = {}

        logger.info("Tool metrics collector initialized")

    def collect(self) -> None:
        """Collect metrics."""
        # This collector is updated in real-time, so no collection needed
        pass

    def register_tool(self, tool_name: str, tool_version: str) -> None:
        """Register a tool for metrics collection.

        Args:
            tool_name: Name of the tool
            tool_version: Version of the tool
        """
        tool_id = f"{tool_name}_{tool_version}"

        # Create tool-specific metrics if not already created
        if tool_id not in self.tool_specific_calls:
            self.tool_specific_calls[tool_id] = self.create_counter(
                f"calls_total_{tool_id}",
                f"Total calls for tool {tool_name} v{tool_version}",
                {"tool": tool_name, "version": tool_version},
            )

            self.tool_specific_errors[tool_id] = self.create_counter(
                f"errors_total_{tool_id}",
                f"Total errors for tool {tool_name} v{tool_version}",
                {"tool": tool_name, "version": tool_version},
            )

            self.tool_specific_durations[tool_id] = self.create_histogram(
                f"duration_seconds_{tool_id}",
                f"Call duration for tool {tool_name} v{tool_version}",
                labels={"tool": tool_name, "version": tool_version},
            )

            logger.info(
                f"Registered metrics for tool {tool_name} v{tool_version}",
                tool=tool_name,
                version=tool_version,
            )

    def record_tool_call_start(self, tool_name: str, tool_version: str) -> float:
        """Record the start of a tool call.

        Args:
            tool_name: Name of the tool
            tool_version: Version of the tool

        Returns:
            float: Start timestamp
        """
        self.tool_call_count.increment()

        # Update tool-specific metrics
        tool_id = f"{tool_name}_{tool_version}"
        if tool_id in self.tool_specific_calls:
            self.tool_specific_calls[tool_id].increment()

        return time.time()

    def record_tool_call_end(
        self, start_time: float, tool_name: str, tool_version: str, success: bool = True
    ) -> float:
        """Record the end of a tool call.

        Args:
            start_time: Call start timestamp
            tool_name: Name of the tool
            tool_version: Version of the tool
            success: Whether call was successful

        Returns:
            float: Call duration in seconds
        """
        duration = time.time() - start_time
        self.tool_duration.observe(duration)

        if success:
            self.tool_success_count.increment()
        else:
            self.tool_error_count.increment()

        # Update tool-specific metrics
        tool_id = f"{tool_name}_{tool_version}"
        if tool_id in self.tool_specific_durations:
            self.tool_specific_durations[tool_id].observe(duration)

        if not success and tool_id in self.tool_specific_errors:
            self.tool_specific_errors[tool_id].increment()

        return duration


class SystemMetricsCollector(MetricsCollector):
    """Collector for system-related metrics."""

    def __init__(self) -> None:
        """Initialize system metrics collector."""
        super().__init__("mcp_system")

        # Define metrics
        self.uptime = self.create_gauge("uptime_seconds", "MCP Core uptime in seconds")

        self.memory_usage = self.create_gauge("memory_bytes", "Memory usage in bytes")

        self.cpu_usage = self.create_gauge("cpu_percent", "CPU usage percentage")

        self.thread_count = self.create_gauge("thread_count", "Number of threads")

        self.gc_collections = self.create_counter(
            "gc_collections_total", "Total number of garbage collections"
        )

        self.start_time = time.time()
        logger.info("System metrics collector initialized")

    def collect(self) -> None:
        """Collect system metrics."""
        # Update uptime
        self.uptime.set(time.time() - self.start_time)

        # Other metrics would typically be updated here
        # This is just a placeholder - in a real implementation you would
        # use psutil or similar to get actual system metrics

        logger.debug("System metrics collected")
