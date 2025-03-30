"""Metrics exporters for MCP Core."""

import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..logger import logger
from .collectors import Counter, Gauge, Histogram, Metric, MetricsCollector


class MetricsExporter(ABC):
    """Base class for metrics exporters."""

    def __init__(self, collectors: List[MetricsCollector]):
        """Initialize metrics exporter.

        Args:
            collectors: List of metrics collectors
        """
        self.collectors = collectors
        logger.info(
            f"Initialized {self.__class__.__name__}",
            collectors=[collector.namespace for collector in collectors],
        )

    def collect_all(self) -> List[Metric]:
        """Collect metrics from all collectors.

        Returns:
            List[Metric]: All collected metrics
        """
        # Trigger collection in all collectors
        for collector in self.collectors:
            collector.collect()

        # Get all metrics
        metrics = []
        for collector in self.collectors:
            metrics.extend(collector.get_all_metrics())

        return metrics

    @abstractmethod
    async def export(self) -> Any:
        """Export metrics.

        Returns:
            Any: Export result
        """
        pass


class PrometheusExporter(MetricsExporter):
    """Exporter for Prometheus metrics format."""

    def __init__(self, collectors: List[MetricsCollector], prefix: str = "mcp"):
        """Initialize Prometheus exporter.

        Args:
            collectors: List of metrics collectors
            prefix: Metrics prefix
        """
        super().__init__(collectors)
        self.prefix = prefix

    async def export(self) -> str:
        """Export metrics in Prometheus format.

        Returns:
            str: Metrics in Prometheus format
        """
        metrics = self.collect_all()
        output = []

        for metric in metrics:
            # Add metric header with description
            metric_name = (
                f"{self.prefix}_{metric.name}"
                if not metric.name.startswith(f"{self.prefix}_")
                else metric.name
            )
            output.append(f"# HELP {metric_name} {metric.description}")

            # Add type information
            if isinstance(metric, Counter):
                output.append(f"# TYPE {metric_name} counter")
                self._format_counter(output, metric_name, metric)
            elif isinstance(metric, Gauge):
                output.append(f"# TYPE {metric_name} gauge")
                self._format_gauge(output, metric_name, metric)
            elif isinstance(metric, Histogram):
                output.append(f"# TYPE {metric_name} histogram")
                self._format_histogram(output, metric_name, metric)

        return "\n".join(output)

    def _format_counter(self, output: List[str], name: str, counter: Counter) -> None:
        """Format counter for Prometheus.

        Args:
            output: Output lines
            name: Metric name
            counter: Counter metric
        """
        labels_str = self._format_labels(counter.labels)
        output.append(f"{name}{labels_str} {counter.value}")

    def _format_gauge(self, output: List[str], name: str, gauge: Gauge) -> None:
        """Format gauge for Prometheus.

        Args:
            output: Output lines
            name: Metric name
            gauge: Gauge metric
        """
        labels_str = self._format_labels(gauge.labels)
        output.append(f"{name}{labels_str} {gauge.value}")

    def _format_histogram(
        self, output: List[str], name: str, histogram: Histogram
    ) -> None:
        """Format histogram for Prometheus.

        Args:
            output: Output lines
            name: Metric name
            histogram: Histogram metric
        """
        base_labels = histogram.labels.copy()

        # Add bucket samples
        for bucket, count in histogram.bucket_values.items():
            labels = base_labels.copy()
            labels["le"] = str(bucket) if bucket != float("inf") else "+Inf"
            labels_str = self._format_labels(labels)
            output.append(f"{name}_bucket{labels_str} {count}")

        # Add sum and count
        labels_str = self._format_labels(base_labels)
        output.append(f"{name}_sum{labels_str} {histogram.sum}")
        output.append(f"{name}_count{labels_str} {histogram.count}")

    def _format_labels(self, labels: Dict[str, str]) -> str:
        """Format labels for Prometheus.

        Args:
            labels: Label dictionary

        Returns:
            str: Formatted labels string
        """
        if not labels:
            return ""

        label_parts = [f'{k}="{v}"' for k, v in sorted(labels.items())]
        return "{" + ",".join(label_parts) + "}"


class JsonFileExporter(MetricsExporter):
    """Exporter for metrics to JSON file."""

    def __init__(
        self, collectors: List[MetricsCollector], file_path: str, append: bool = False
    ):
        """Initialize JSON file exporter.

        Args:
            collectors: List of metrics collectors
            file_path: Path to output file
            append: Whether to append to file
        """
        super().__init__(collectors)
        self.file_path = file_path
        self.append = append

    async def export(self) -> None:
        """Export metrics to JSON file."""
        metrics = self.collect_all()
        timestamp = time.time()

        # Convert metrics to serializable format
        data = {"timestamp": timestamp, "metrics": {}}

        for metric in metrics:
            if isinstance(metric, Counter):
                data["metrics"][metric.name] = {
                    "type": "counter",
                    "value": metric.value,
                    "labels": metric.labels,
                }
            elif isinstance(metric, Gauge):
                data["metrics"][metric.name] = {
                    "type": "gauge",
                    "value": metric.value,
                    "labels": metric.labels,
                }
            elif isinstance(metric, Histogram):
                data["metrics"][metric.name] = {
                    "type": "histogram",
                    "buckets": {str(k): v for k, v in histogram.bucket_values.items()},
                    "sum": metric.sum,
                    "count": metric.count,
                    "labels": metric.labels,
                }

        # Write to file
        mode = "a" if self.append else "w"
        with open(self.file_path, mode) as f:
            json.dump(data, f)
            f.write("\n")

        logger.info(f"Exported metrics to {self.file_path}", metric_count=len(metrics))
