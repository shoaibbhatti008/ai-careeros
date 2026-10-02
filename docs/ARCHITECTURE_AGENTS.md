# Agent Architecture Deep-Dive

This document explains the design decisions behind the agent framework.

## Why multi-agent?

A single monolithic LLM prompt cannot reliably handle diverse career
tasks. Specialized agents:

- Have focused responsibilities
- Can be composed via the orchestrator
- Have explicit tool allowlists
- Are independently observable and verifiable

## Layered design

The agent layer is pure Python — it does NOT import Django. This makes it:

- Easier to test (no DB needed)
- Reusable in other contexts
- Portable across deployments

## Permission model (4 layers)

Every tool call is checked at 4 layers:

1. Tool registered?
2. Agent allowlist?
3. Context allowlist?
4. Tool's agent allowlist?

All four must pass. This is defense in depth.

## Budget model

Budgets are enforced at multiple levels:

| Level | Enforced by | Purpose |
|-------|-------------|---------|
| Steps | AgentContext | Prevent infinite loops |
| Tool calls | AgentContext | Cap external calls |
| Tokens | AgentContext / Budget | Cap LLM usage |
| Cost (USD) | Budget | Cap spend |
| Duration | Budget | Cap wall-clock time |

Failures are fail-closed: exceptions propagate to AgentResult.failed.

## Why agents return AgentResult, not exceptions

Exceptions are hard to test, easy to leak, and hard to serialize.
AgentResult is a plain dataclass (JSON-serializable) with explicit
status (COMPLETED, FAILED, AWAITING_APPROVAL, ...).

## Why tools return dicts, not models

Tools are stateless. Returning dicts keeps them portable, simple to
mock, and easy to log.

## Why LLM providers are injected

Agents never access LLM providers globally. The caller injects the
provider via ToolContext.metadata. This makes provider swapping
trivial.

## Why verification is separate

Verification is deterministic and lives outside the LLM: schema
validation, required-field checks, placeholder detection, PII
detection, confidence range checks.

## Why approval is separate

Approval is a policy decision, not an LLM decision:

1. The agent proposes an action
2. The system creates an ApprovalRequest
3. The user decides
4. Only then is the action executed

This is the "propose is not execute" principle.

## Testing philosophy

Every agent has tests for:
- Happy path
- Empty input
- Budget exhaustion
- Allowlist violations
- Ownership isolation
- Output shape

Total agent tests: ~322. Combined with backend: ~400 tests.

## Extensibility

Adding a new agent or tool requires zero changes to the framework.
Register via @register_agent or @register_tool and declare tools in
allowed_tools. The framework handles budgets, permissions, tracing,
metrics, verification, approval automatically.