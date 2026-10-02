"""
Instrumentation helpers.

Wraps agent and tool execution with tracing + metrics + events.
Does NOT modify agent code — used by callers.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from agents.observability.events import EventType, emit_event
from agents.observability.metrics import get_metrics
from agents.observability.tracer import Tracer


@contextmanager
def trace_agent(
    agent_name: str,
    *,
    trace_id: str = "",
    user_id: str = "",
    tracer: Tracer | None = None,
    **attributes: Any,
) -> Iterator[dict[str, Any]]:
    """
    Context manager that traces an agent execution.

    Emits: agent.start, agent.end (or agent.error).
    Records: agent.runs, agent.duration_ms.

    Yields a dict with span info.
    """
    tracer = tracer or _default_tracer()
    metrics = get_metrics()

    with tracer.span(
        f"agent.{agent_name}", trace_id=trace_id, user_id=user_id, **attributes
    ) as span:
        emit_event(
            EventType.AGENT_START,
            trace_id=span.trace_id,
            span_id=span.span_id,
            agent_name=agent_name,
            user_id=user_id,
            data=dict(attributes),
        )
        metrics.counter("agent.runs", agent=agent_name).inc()

        try:
            yield {"trace_id": span.trace_id, "span_id": span.span_id}
            emit_event(
                EventType.AGENT_END,
                trace_id=span.trace_id,
                span_id=span.span_id,
                agent_name=agent_name,
                user_id=user_id,
                duration_ms=span.duration_ms,
            )
            metrics.histogram("agent.duration_ms", agent=agent_name).observe(span.duration_ms)
        except Exception as exc:
            emit_event(
                EventType.AGENT_ERROR,
                trace_id=span.trace_id,
                span_id=span.span_id,
                agent_name=agent_name,
                user_id=user_id,
                duration_ms=span.duration_ms,
                error=str(exc),
            )
            metrics.counter("agent.errors", agent=agent_name).inc()
            raise


@contextmanager
def trace_tool(
    tool_name: str,
    *,
    agent_name: str = "",
    trace_id: str = "",
    span_id: str = "",
    tracer: Tracer | None = None,
    **attributes: Any,
) -> Iterator[dict[str, Any]]:
    """
    Context manager that traces a tool call.

    Emits: tool.start, tool.end (or tool.error).
    Records: tool.calls, tool.duration_ms.
    """
    tracer = tracer or _default_tracer()
    metrics = get_metrics()

    with tracer.span(
        f"tool.{tool_name}",
        trace_id=trace_id,
        agent_name=agent_name,
        **attributes,
    ) as span:
        emit_event(
            EventType.TOOL_START,
            trace_id=span.trace_id,
            span_id=span.span_id,
            tool_name=tool_name,
            agent_name=agent_name,
            data=dict(attributes),
        )
        metrics.counter("tool.calls", tool=tool_name).inc()

        try:
            yield {"trace_id": span.trace_id, "span_id": span.span_id}
            emit_event(
                EventType.TOOL_END,
                trace_id=span.trace_id,
                span_id=span.span_id,
                tool_name=tool_name,
                agent_name=agent_name,
                duration_ms=span.duration_ms,
            )
            metrics.histogram("tool.duration_ms", tool=tool_name).observe(span.duration_ms)
        except Exception as exc:
            emit_event(
                EventType.TOOL_ERROR,
                trace_id=span.trace_id,
                span_id=span.span_id,
                tool_name=tool_name,
                agent_name=agent_name,
                duration_ms=span.duration_ms,
                error=str(exc),
            )
            metrics.counter("tool.errors", tool=tool_name).inc()
            raise


# ==========================================================
# Default tracer
# ==========================================================

_DEFAULT_TRACER = Tracer()


def _default_tracer() -> Tracer:
    return _DEFAULT_TRACER


def get_tracer() -> Tracer:
    """Return the default global tracer."""
    return _DEFAULT_TRACER
