"""
Structured events emitted by agents and tools.

Events are the audit trail for the agent system. Every agent execution
produces at least:
- agent.start
- agent.end (or agent.error)

Every tool call produces:
- tool.start
- tool.end (or tool.error)

Events are dataclasses. They serialize to JSON for logging.
"""

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class EventType(str, Enum):
    """Well-known event types."""

    AGENT_START = "agent.start"
    AGENT_END = "agent.end"
    AGENT_ERROR = "agent.error"
    TOOL_START = "tool.start"
    TOOL_END = "tool.end"
    TOOL_ERROR = "tool.error"
    TOOL_BLOCKED = "tool.blocked"
    ORCHESTRATOR_START = "orchestrator.start"
    ORCHESTRATOR_END = "orchestrator.end"
    VERIFICATION_PASSED = "verification.passed"
    VERIFICATION_FAILED = "verification.failed"
    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_DECIDED = "approval.decided"
    BUDGET_EXCEEDED = "budget.exceeded"
    CUSTOM = "custom"


@dataclass
class Event:
    """A structured event."""

    type: EventType
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    trace_id: str = ""
    span_id: str = ""
    agent_name: str = ""
    tool_name: str = ""
    user_id: str = ""
    duration_ms: int = 0
    data: dict[str, Any] = field(default_factory=dict)
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dict."""
        d = asdict(self)
        d["type"] = self.type.value
        d["timestamp"] = self.timestamp.isoformat()
        return d


# ==========================================================
# In-memory event sink (default)
# ==========================================================

_EVENTS: list[Event] = []
_MAX_EVENTS = 10_000  # cap to avoid memory leaks
_ENABLED = True


def emit_event(
    event_or_type: "Event | EventType",
    **kwargs: Any,
) -> None:
    """
    Emit an event to the default sink.

    Accepts either:
    - An Event instance: emit_event(Event(...))
    - An EventType + kwargs: emit_event(EventType.CUSTOM, trace_id="...")
    """
    if not _ENABLED:
        return
    try:
        if isinstance(event_or_type, Event):
            event = event_or_type
        else:
            # Allow only valid kwargs that Event accepts
            allowed = {
                "trace_id",
                "span_id",
                "agent_name",
                "tool_name",
                "user_id",
                "duration_ms",
                "data",
                "error",
            }
            clean = {k: v for k, v in kwargs.items() if k in allowed}
            event = Event(type=event_or_type, **clean)

        _EVENTS.append(event)
        if len(_EVENTS) > _MAX_EVENTS:
            del _EVENTS[: len(_EVENTS) - _MAX_EVENTS]
    except Exception:
        pass


def get_events(
    *,
    trace_id: str | None = None,
    event_type: EventType | None = None,
) -> list[Event]:
    """Return recorded events (optionally filtered)."""
    result = list(_EVENTS)
    if trace_id is not None:
        result = [e for e in result if e.trace_id == trace_id]
    if event_type is not None:
        result = [e for e in result if e.type == event_type]
    return result


def clear_events() -> None:
    """Clear the event buffer (used in tests)."""
    _EVENTS.clear()


def set_enabled(enabled: bool) -> None:
    """Enable/disable event emission (used in tests)."""
    global _ENABLED
    _ENABLED = enabled
