# AI CareerOS — Agent Framework

> Production-ready multi-agent framework with safety-first design.

## Overview

AI CareerOS uses a **multi-agent architecture** where specialized agents
collaborate to solve career-related tasks.

- **Pure Python** — no Django dependency in the agent layer
- **Provider-agnostic** — works with OpenAI, Anthropic, or mock providers
- **Permission-aware** — every tool call is checked at 4 layers
- **Budget-enforced** — hard limits on steps, tools, time, tokens, cost
- **Observable** — every execution is traced, metered, and audited
- **Verifiable** — outputs are validated before use
- **Human-in-the-loop** — sensitive actions require explicit approval

## Core Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `BaseAgent` | Abstract agent base | `agents/base.py` |
| `AgentContext` | Per-execution context | `agents/context.py` |
| `AgentResult` | Structured output | `agents/result.py` |
| `AgentRegistry` | Agent discovery | `agents/registry.py` |
| `Orchestrator` | Multi-agent workflows | `agents/orchestrator.py` |
| `BaseTool` | Abstract tool base | `agents/tools/base.py` |
| `ToolRegistry` | Central tool registry | `agents/tools/registry.py` |
| `LLMProvider` | Provider-agnostic LLM | `agents/llm/provider.py` |
| `Retriever` | Ownership-enforced search | `agents/rag/retriever.py` |
| `Verifier` | Output verification | `agents/verification/verifier.py` |
| `ApprovalService` | Human approval | `agents/approval/service.py` |
| `Tracer` | Traces and spans | `agents/observability/tracer.py` |
| `RateLimiter` | Token-bucket limiting | `agents/limits/rate_limiter.py` |

## Available Agents

| Agent | Purpose | Tools |
|-------|---------|-------|
| `resume_agent` | Resume analysis (heuristic) | `resume_reader`, `skill_extractor` |
| `resume_agent_llm` | Resume analysis (LLM) | `llm_analyzer` |
| `job_agent` | Job parsing + matching | `job_parser`, `skill_extractor`, `skill_matcher` |
| `skill_gap_agent` | Skill gap analysis | `skill_gap_analyzer`, `skill_extractor` |
| `interview_agent` | Mock interviews | `question_generator`, `answer_analyzer` |
| `rag_agent` | Document Q&A | `document_search` |
| `verification_agent` | Output verification | `verify_output` |
| `approval_agent` | Human approval | `request_approval` |

## Available Tools

| Tool | Risk | Purpose |
|------|------|---------|
| `echo` | LOW | Returns input (testing) |
| `text_length` | LOW | Character/word count |
| `text_normalize` | LOW | Whitespace normalization |
| `resume_reader` | LOW | Resume text parsing |
| `skill_extractor` | LOW | Skill matching from catalog |
| `job_parser` | LOW | Job description parsing |
| `skill_matcher` | LOW | Skill set comparison |
| `skill_gap_analyzer` | LOW | Prioritized gap analysis |
| `question_generator` | LOW | Interview questions |
| `answer_analyzer` | LOW | Answer quality analysis |
| `document_search` | MEDIUM | User's own documents (RAG) |
| `llm_analyzer` | MEDIUM | LLM call with prompt template |
| `verify_output` | LOW | Deterministic verification |
| `request_approval` | LOW | Create approval request |

## Safety Guarantees

1. **No arbitrary code execution** — agents cannot run shell, Python, or JS
2. **No filesystem access** — all I/O goes through registered tools
3. **No env var access** — secrets never reach agent code
4. **Ownership enforced** — every query filters by `user_id`
5. **Budgets enforced** — steps, tools, time, tokens, cost
6. **Human approval** — sensitive actions require explicit consent
7. **Output verification** — schema, PII, placeholders checked
8. **Audit trail** — every agent/tool call is logged

## Quick Example

```python
from uuid import uuid4
from agents.context import AgentContext
from agents.implementations.resume_agent import ResumeAgent

ctx = AgentContext(
    user_id=uuid4(),
    allowed_tools=frozenset({"resume_reader", "skill_extractor"}),
    tool_executor=my_tool_executor,
)

agent = ResumeAgent(ctx)
result = agent.execute({"resume_text": "John Doe, Python developer..."})