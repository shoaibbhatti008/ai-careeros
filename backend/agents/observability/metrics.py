"""
Metrics: counters, histograms, gauges.

In-memory by default. Pluggable backends later (Prometheus, StatsD).
"""

from dataclasses import dataclass, field
from statistics import mean
from threading import Lock


@dataclass
class Counter:
    """A monotonically increasing counter."""

    name: str
    value: int = 0
    labels: dict[str, str] = field(default_factory=dict)

    def inc(self, amount: int = 1) -> None:
        self.value += amount


@dataclass
class Histogram:
    """A histogram that stores all observations in memory."""

    name: str
    observations: list[float] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)

    def observe(self, value: float) -> None:
        self.observations.append(value)

    @property
    def count(self) -> int:
        return len(self.observations)

    @property
    def sum(self) -> float:
        return sum(self.observations)

    @property
    def mean(self) -> float:
        return mean(self.observations) if self.observations else 0.0

    def percentile(self, p: float) -> float:
        """Compute the p-th percentile (0.0–1.0)."""
        if not self.observations:
            return 0.0
        sorted_obs = sorted(self.observations)
        idx = int(len(sorted_obs) * p)
        idx = min(idx, len(sorted_obs) - 1)
        return sorted_obs[idx]


class MetricsCollector:
    """
    Central metrics collector.

    Usage:
        metrics = MetricsCollector()
        metrics.counter("agent.runs", agent="resume_agent").inc()
        metrics.histogram("agent.duration_ms").observe(42)
    """

    def __init__(self) -> None:
        self._counters: dict[tuple[str, tuple], Counter] = {}
        self._histograms: dict[tuple[str, tuple], Histogram] = {}
        self._lock = Lock()

    # ==========================================================
    # Accessors
    # ==========================================================

    def counter(self, name: str, **labels: str) -> Counter:
        key = (name, tuple(sorted(labels.items())))
        with self._lock:
            if key not in self._counters:
                self._counters[key] = Counter(name=name, labels=dict(labels))
            return self._counters[key]

    def histogram(self, name: str, **labels: str) -> Histogram:
        key = (name, tuple(sorted(labels.items())))
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = Histogram(name=name, labels=dict(labels))
            return self._histograms[key]

    def snapshot(self) -> dict:
        """Return a JSON-safe snapshot of all metrics."""
        with self._lock:
            return {
                "counters": {self._key_to_str(k): c.value for k, c in self._counters.items()},
                "histograms": {
                    self._key_to_str(k): {
                        "count": h.count,
                        "sum": h.sum,
                        "mean": h.mean,
                        "p50": h.percentile(0.5),
                        "p95": h.percentile(0.95),
                        "p99": h.percentile(0.99),
                    }
                    for k, h in self._histograms.items()
                },
            }

    def reset(self) -> None:
        """Clear all metrics (used in tests)."""
        with self._lock:
            self._counters.clear()
            self._histograms.clear()

    @staticmethod
    def _key_to_str(key: tuple[str, tuple]) -> str:
        name, labels = key
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in labels)
        return f"{name}{{{label_str}}}"


# ==========================================================
# Global metrics (used by instrumentation)
# ==========================================================

_GLOBAL_METRICS = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """Return the global metrics collector."""
    return _GLOBAL_METRICS


def reset_metrics() -> None:
    """Reset the global metrics collector."""
    _GLOBAL_METRICS.reset()
