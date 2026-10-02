# Observability

The observability layer provides tracing, metrics, and structured events
for every agent execution.

## Design principles

1. Never raise — observability must not break the agent
2. Zero external dependencies — in-memory by default
3. Pluggable backends — swap to OpenTelemetry, Prometheus later
4. Ring buffer cap — prevents memory leaks
5. Fail-safe — exceptions in observability are swallowed

## Components

| Component | Purpose |
|-----------|---------|
| Event / EventType | Structured events |
| Tracer / Span | Trace IDs, spans, durations |
| MetricsCollector | Counters, histograms |
| AgentLogger | Structured JSON logger |
| trace_agent / trace_tool | Context managers |

## Using traces

    from agents.observability.instrumentation import trace_agent

    with trace_agent("resume_agent", user_id="u1") as info:
        ...
        print(info["trace_id"])

## Using metrics

    from agents.observability.metrics import get_metrics

    metrics = get_metrics()
    metrics.counter("resume_analyses").inc()
    metrics.histogram("analysis_duration_ms").observe(42.0)

    snapshot = metrics.snapshot()

## Reading events

    from agents.observability.events import get_events, EventType

    events = get_events(trace_id="abc-123")
    starts = get_events(event_type=EventType.AGENT_START)

## Structured logging

    from agents.observability.logger import AgentLogger

    log = AgentLogger("resume_agent")
    log.info("analysis_started", trace_id="abc", user_id="u1")
    log.error("analysis_failed", trace_id="abc", error="timeout")

## Event types

| Event | When emitted |
|-------|--------------|
| agent.start | Before agent runs |
| agent.end | After successful run |
| agent.error | On exception |
| tool.start | Before tool executes |
| tool.end | After successful tool run |
| tool.error | On tool failure |
| orchestrator.start | Workflow planning begins |
| orchestrator.end | Workflow finished |
| verification.passed | Output verified |
| verification.failed | Verification failed |
| approval.requested | Approval request created |
| approval.decided | Approval approved/rejected |
| budget.exceeded | Hard limit hit |

## Production integration

Replace the in-memory sink with a real one that ships events to
stdout (JSON) or a log aggregator like OpenTelemetry.

## Metrics collected by default

| Metric | Type | Labels |
|--------|------|--------|
| agent.runs | Counter | agent |
| agent.errors | Counter | agent |
| agent.duration_ms | Histogram | agent |
| tool.calls | Counter | tool |
| tool.errors | Counter | tool |
| tool.duration_ms | Histogram | tool |