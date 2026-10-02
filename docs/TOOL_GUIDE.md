# Building a Tool

Tools are the ONLY way agents can affect the outside world. This guide
shows you how to build one safely.

## Tool responsibilities

A tool should:

1. Do **one thing** and do it well
2. Have a **declared input schema**
3. Have a **declared output schema** (always a dict)
4. Declare its **risk level**
5. Declare which **agents** may use it
6. Declare a **timeout** and **rate limit**
7. NEVER access the filesystem, env vars, or network directly
8. NEVER execute arbitrary code

## Risk levels

| Level | Meaning | Examples |
|-------|---------|----------|
| `LOW` | Pure computation | text_length, echo |
| `MEDIUM` | External call, no side effects | llm_analyzer, web_research |
| `HIGH` | Writes to external systems | send_email, submit_application |
| `CRITICAL` | Destructive/irreversible | delete_user_data |

**Rule:** HIGH and CRITICAL tools should set `requires_approval = True`.

## Step 1 — Create the tool file

**File:** `backend/agents/tools/career/my_tool.py`

```python
"""MyTool: one-line description."""

from typing import Any, ClassVar

from agents.tools.base import BaseTool, RiskLevel


class MyTool(BaseTool):
    """One-line description."""

    # ---- Required metadata ----
    name = "my_tool"
    description = "Does X and returns Y."
    risk_level: ClassVar[RiskLevel] = RiskLevel.LOW
    allowed_agents: ClassVar[frozenset[str]] = frozenset({"my_agent"})

    # ---- Schemas ----
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
        },
        "required": ["text"],
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "length": {"type": "integer"},
        },
    }

    # ---- Limits ----
    timeout_seconds = 5
    rate_limit_per_minute = 300
    requires_approval = False

    # ---- Logic ----
    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        text = input_data["text"]
        return {"length": len(text)}