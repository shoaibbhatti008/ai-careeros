"""
AgentLogger: structured logger wrapper.

Emits both a Python log record and a structured Event.
Never raises.
"""

import json
import logging
from typing import Any

from agents.observability.events import Event, EventType, emit_event


class AgentLogger:
    """
    Structured logger for agents.

    Usage:
        log = AgentLogger("resume_agent")
        log.info("started", trace_id="...", user_id="...")
    """

    def __init__(self, name: str, *, level: int = logging.INFO) -> None:
        self.name = name
        self._logger = logging.getLogger(f"agents.{name}")
        self._logger.setLevel(level)

    def _log(
        self,
        level: int,
        event_type: EventType,
        message: str,
        **fields: Any,
    ) -> None:
        try:
            event = Event(
                type=event_type,
                agent_name=self.name,
                trace_id=fields.pop("trace_id", ""),
                span_id=fields.pop("span_id", ""),
                tool_name=fields.pop("tool_name", ""),
                user_id=fields.pop("user_id", ""),
                duration_ms=fields.pop("duration_ms", 0),
                data={"message": message, **fields},
                error=fields.pop("error", ""),
            )
            emit_event(event)
            self._logger.log(level, self._format(event))
        except Exception:
            # Logging must never break the caller
            pass

    @staticmethod
    def _format(event: Event) -> str:
        try:
            return json.dumps(event.to_dict(), default=str)
        except Exception:
            return f"[{event.type.value}] {event.agent_name}"

    def debug(self, message: str, **fields: Any) -> None:
        self._log(logging.DEBUG, EventType.CUSTOM, message, **fields)

    def info(self, message: str, **fields: Any) -> None:
        self._log(logging.INFO, EventType.CUSTOM, message, **fields)

    def warning(self, message: str, **fields: Any) -> None:
        self._log(logging.WARNING, EventType.CUSTOM, message, **fields)

    def error(self, message: str, **fields: Any) -> None:
        self._log(logging.ERROR, EventType.CUSTOM, message, **fields)
