"""Observability layer for AI CareerOS agents.

Provides:
- Structured events (agent_start, agent_end, tool_call, error)
- Tracer with trace_id + spans
- Metrics collector (counters, histograms, gauges)
- Logger wrapper

Design:
- Zero external dependencies (in-memory by default)
- Pluggable backends (in-memory, JSONL, Prometheus, OpenTelemetry later)
- Never raises; failures in observability MUST NOT break agents
"""

from agents.observability.events import (
    Event,
    EventType,
    emit_event,
)
from agents.observability.logger import AgentLogger
from agents.observability.metrics import (
    Counter,
    Histogram,
    MetricsCollector,
)
from agents.observability.tracer import Span, Tracer

__all__ = [
    "Event",
    "EventType",
    "emit_event",
    "AgentLogger",
    "Counter",
    "Histogram",
    "MetricsCollector",
    "Span",
    "Tracer",
]
