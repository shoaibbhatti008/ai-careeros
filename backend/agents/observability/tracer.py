"""
Tracer: trace IDs and spans.

A trace represents one logical operation (e.g. a user request).
A span represents one unit of work within a trace (e.g. an agent run).

Traces and spans are kept in memory for inspection and testing.
In production, replace with OpenTelemetry.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from agents.observability.events import EventType, emit_event


@dataclass
class Span:
    """A span of work within a trace."""

    span_id: str
    trace_id: str
    name: str
    started_at: datetime
    ended_at: datetime | None = None
    duration_ms: int = 0
    status: str = "running"  # running | ok | error
    attributes: dict[str, Any] = field(default_factory=dict)

    def finish(self, *, status: str = "ok") -> None:
        self.ended_at = datetime.now(UTC)
        self.status = status
        self.duration_ms = int((self.ended_at - self.started_at).total_seconds() * 1000)


class Tracer:
    """
    In-memory tracer.

    Usage:
        tracer = Tracer()
        trace_id = tracer.new_trace()
        with tracer.span("my_agent", trace_id=trace_id) as span:
            ...
    """

    def __init__(self) -> None:
        self._traces: dict[str, list[Span]] = {}

    # ==========================================================
    # Trace management
    # ==========================================================

    def new_trace(self) -> str:
        """Create a new trace and return its ID."""
        trace_id = str(uuid4())
        self._traces[trace_id] = []
        return trace_id

    def get_spans(self, trace_id: str) -> list[Span]:
        """Return all spans for a trace."""
        return list(self._traces.get(trace_id, []))

    def clear(self) -> None:
        """Clear all traces (used in tests)."""
        self._traces.clear()

    # ==========================================================
    # Span management
    # ==========================================================

    @contextmanager
    def span(
        self,
        name: str,
        *,
        trace_id: str = "",
        **attributes: Any,
    ) -> Iterator[Span]:
        """
        Context manager for a span.

        Always finishes the span, even on exception.
        Emits start/end events.
        """
        if not trace_id:
            trace_id = self.new_trace()

        span = Span(
            span_id=str(uuid4()),
            trace_id=trace_id,
            name=name,
            started_at=datetime.now(UTC),
            attributes=dict(attributes),
        )
        self._traces.setdefault(trace_id, []).append(span)

        emit_event(
            EventType.CUSTOM,
            trace_id=trace_id,
            span_id=span.span_id,
            data={"event": "span.start", "name": name, "attributes": attributes},
        )

        try:
            yield span
            span.finish(status="ok")
        except Exception as exc:
            span.finish(status="error")
            span.attributes["error"] = str(exc)
            emit_event(
                EventType.CUSTOM,
                trace_id=trace_id,
                span_id=span.span_id,
                data={"event": "span.error", "name": name},
                error=str(exc),
            )
            raise
        finally:
            emit_event(
                EventType.CUSTOM,
                trace_id=trace_id,
                span_id=span.span_id,
                duration_ms=span.duration_ms,
                data={"event": "span.end", "name": name, "status": span.status},
            )
