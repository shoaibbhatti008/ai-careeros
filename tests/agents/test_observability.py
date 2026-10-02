"""Tests for the observability layer."""

import pytest

from agents.observability.events import (
    Event,
    EventType,
    clear_events,
    emit_event,
    get_events,
    set_enabled,
)
from agents.observability.logger import AgentLogger
from agents.observability.metrics import (
    Counter,
    Histogram,
    MetricsCollector,
    get_metrics,
    reset_metrics,
)
from agents.observability.tracer import Span, Tracer


# ==========================================================
# Fixtures
# ==========================================================


@pytest.fixture(autouse=True)
def _reset():
    clear_events()
    reset_metrics()
    set_enabled(True)
    yield
    clear_events()
    reset_metrics()


# ==========================================================
# Event tests
# ==========================================================


class TestEvents:
    def test_emit_and_get(self):
        event = Event(type=EventType.AGENT_START, agent_name="test")
        emit_event(event)
        events = get_events()
        assert len(events) == 1
        assert events[0].agent_name == "test"

    def test_filter_by_trace_id(self):
        emit_event(Event(type=EventType.AGENT_START, trace_id="A"))
        emit_event(Event(type=EventType.AGENT_START, trace_id="B"))
        assert len(get_events(trace_id="A")) == 1
        assert len(get_events(trace_id="B")) == 1

    def test_filter_by_type(self):
        emit_event(Event(type=EventType.AGENT_START))
        emit_event(Event(type=EventType.AGENT_END))
        assert len(get_events(event_type=EventType.AGENT_START)) == 1

    def test_to_dict_is_json_safe(self):
        event = Event(type=EventType.CUSTOM, data={"k": "v"})
        d = event.to_dict()
        assert d["type"] == "custom"
        assert isinstance(d["timestamp"], str)

    def test_clear(self):
        emit_event(Event(type=EventType.CUSTOM))
        clear_events()
        assert get_events() == []

    def test_disabled_does_not_emit(self):
        set_enabled(False)
        emit_event(Event(type=EventType.CUSTOM))
        assert get_events() == []


# ==========================================================
# Tracer tests
# ==========================================================


class TestTracer:
    def test_new_trace(self):
        t = Tracer()
        tid = t.new_trace()
        assert tid
        assert t.get_spans(tid) == []

    def test_span_records(self):
        t = Tracer()
        tid = t.new_trace()
        with t.span("test", trace_id=tid):
            pass
        spans = t.get_spans(tid)
        assert len(spans) == 1
        assert spans[0].name == "test"
        assert spans[0].status == "ok"

    def test_span_on_error(self):
        t = Tracer()
        tid = t.new_trace()
        with pytest.raises(ValueError):
            with t.span("failing", trace_id=tid):
                raise ValueError("boom")
        spans = t.get_spans(tid)
        assert spans[0].status == "error"
        assert "boom" in spans[0].attributes.get("error", "")

    def test_span_has_duration(self):
        t = Tracer()
        with t.span("duration"):
            pass
        spans = t.get_spans(list(t._traces.keys())[0])
        assert spans[0].duration_ms >= 0

    def test_clear(self):
        t = Tracer()
        t.new_trace()
        t.clear()
        assert t._traces == {}


# ==========================================================
# Metrics tests
# ==========================================================


class TestMetrics:
    def test_counter(self):
        c = Counter(name="test")
        c.inc()
        c.inc(3)
        assert c.value == 4

    def test_histogram_observe(self):
        h = Histogram(name="test")
        h.observe(1.0)
        h.observe(3.0)
        assert h.count == 2
        assert h.sum == 4.0
        assert h.mean == 2.0

    def test_histogram_percentile(self):
        h = Histogram(name="test")
        for i in range(1, 101):
            h.observe(float(i))
        assert 50 <= h.percentile(0.5) <= 51
        assert 95 <= h.percentile(0.95) <= 96

    def test_collector_counter_reuse(self):
        m = MetricsCollector()
        c1 = m.counter("x", agent="a")
        c2 = m.counter("x", agent="a")
        assert c1 is c2

    def test_collector_labels_isolated(self):
        m = MetricsCollector()
        c1 = m.counter("x", agent="a")
        c2 = m.counter("x", agent="b")
        c1.inc(5)
        assert c2.value == 0

    def test_collector_snapshot(self):
        m = MetricsCollector()
        m.counter("hits", agent="a").inc(3)
        m.histogram("lat", agent="a").observe(42.0)
        snap = m.snapshot()
        assert "hits{agent=a}" in snap["counters"]
        assert snap["counters"]["hits{agent=a}"] == 3
        assert "lat{agent=a}" in snap["histograms"]

    def test_global_metrics(self):
        m = get_metrics()
        m.counter("global_test").inc()
        assert m.counter("global_test").value == 1


# ==========================================================
# Logger tests
# ==========================================================


class TestAgentLogger:
    def test_info_emits_event(self):
        log = AgentLogger("test_agent")
        log.info("hello", trace_id="t1", user_id="u1")
        events = get_events()
        assert len(events) == 1
        assert events[0].agent_name == "test_agent"
        assert events[0].data["message"] == "hello"

    def test_error_emits_event(self):
        log = AgentLogger("test_agent")
        log.error("boom")
        events = get_events()
        assert len(events) == 1
        assert events[0].data["message"] == "boom"


# ==========================================================
# Instrumentation tests
# ==========================================================


class TestInstrumentation:
    def test_trace_agent_emits_start_and_end(self):
        from agents.observability.instrumentation import trace_agent

        with trace_agent("resume_agent", user_id="u1"):
            pass

        events = get_events()
        types = [e.type for e in events]
        assert EventType.AGENT_START in types
        assert EventType.AGENT_END in types

    def test_trace_agent_records_metrics(self):
        from agents.observability.instrumentation import trace_agent

        with trace_agent("resume_agent"):
            pass

        m = get_metrics()
        assert m.counter("agent.runs", agent="resume_agent").value == 1
        assert m.histogram("agent.duration_ms", agent="resume_agent").count == 1

    def test_trace_agent_on_error(self):
        from agents.observability.instrumentation import trace_agent

        with pytest.raises(RuntimeError):
            with trace_agent("crashing_agent"):
                raise RuntimeError("boom")

        events = get_events()
        types = [e.type for e in events]
        assert EventType.AGENT_ERROR in types
        assert get_metrics().counter("agent.errors", agent="crashing_agent").value == 1

    def test_trace_tool(self):
        from agents.observability.instrumentation import trace_tool

        with trace_tool("document_search", agent_name="rag_agent"):
            pass

        events = get_events()
        types = [e.type for e in events]
        assert EventType.TOOL_START in types
        assert EventType.TOOL_END in types
        assert get_metrics().counter("tool.calls", tool="document_search").value == 1

    def test_trace_tool_on_error(self):
        from agents.observability.instrumentation import trace_tool

        with pytest.raises(ValueError):
            with trace_tool("bad_tool"):
                raise ValueError("nope")

        assert get_metrics().counter("tool.errors", tool="bad_tool").value == 1

    def test_trace_agent_span_records_duration(self):
        from agents.observability.instrumentation import get_tracer, trace_agent

        tracer = get_tracer()
        tracer.clear()
        with trace_agent("agent", tracer=tracer) as info:
            trace_id = info["trace_id"]
        spans = tracer.get_spans(trace_id)
        assert len(spans) >= 1
        assert spans[0].duration_ms >= 0

    def test_default_tracer_reused(self):
        from agents.observability.instrumentation import get_tracer

        t1 = get_tracer()
        t2 = get_tracer()
        assert t1 is t2