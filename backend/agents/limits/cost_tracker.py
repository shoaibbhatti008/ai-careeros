"""
CostTracker: tracks token usage and costs per user/model/agent.

In-memory by default. Plug into a database or Prometheus later.

Pricing is per-million-tokens (input/output).
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock


@dataclass(frozen=True)
class ModelPricing:
    """Pricing for a model, per 1M tokens (in USD)."""

    name: str
    input_per_million: float
    output_per_million: float


# Curated pricing table (update as needed)
DEFAULT_PRICING: dict[str, ModelPricing] = {
    "gpt-4o": ModelPricing("gpt-4o", 2.50, 10.00),
    "gpt-4o-mini": ModelPricing("gpt-4o-mini", 0.15, 0.60),
    "gpt-4-turbo": ModelPricing("gpt-4-turbo", 10.00, 30.00),
    "claude-3-5-sonnet": ModelPricing("claude-3-5-sonnet", 3.00, 15.00),
    "claude-3-5-haiku": ModelPricing("claude-3-5-haiku", 0.80, 4.00),
    "mock": ModelPricing("mock", 0.0, 0.0),
}


@dataclass
class UsageRecord:
    """A single usage record."""

    user_id: str
    agent_name: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class CostTracker:
    """
    Tracks token usage and cost.

    Usage:
        tracker = CostTracker()
        tracker.record(
            user_id="u1", agent_name="resume_agent",
            model="gpt-4o-mini", prompt_tokens=500, completion_tokens=200,
        )
        total = tracker.user_total("u1")
    """

    def __init__(self, pricing: dict[str, ModelPricing] | None = None) -> None:
        self._pricing = dict(pricing or DEFAULT_PRICING)
        self._records: list[UsageRecord] = []
        self._lock = Lock()

    # ==========================================================
    # Recording
    # ==========================================================

    def record(
        self,
        *,
        user_id: str,
        agent_name: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> UsageRecord:
        """Record a usage event and return the UsageRecord."""
        cost = self._compute_cost(model, prompt_tokens, completion_tokens)
        record = UsageRecord(
            user_id=user_id,
            agent_name=agent_name,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost,
        )
        with self._lock:
            self._records.append(record)
        return record

    # ==========================================================
    # Queries
    # ==========================================================

    def user_total(self, user_id: str) -> float:
        """Total cost for a user."""
        with self._lock:
            return sum(r.cost_usd for r in self._records if r.user_id == user_id)

    def user_total_tokens(self, user_id: str) -> int:
        """Total tokens used by a user."""
        with self._lock:
            return sum(
                r.prompt_tokens + r.completion_tokens for r in self._records if r.user_id == user_id
            )

    def agent_total(self, agent_name: str) -> float:
        """Total cost for an agent across all users."""
        with self._lock:
            return sum(r.cost_usd for r in self._records if r.agent_name == agent_name)

    def model_total(self, model: str) -> float:
        """Total cost for a model."""
        with self._lock:
            return sum(r.cost_usd for r in self._records if r.model == model)

    def all_records(self) -> list[UsageRecord]:
        """Return a copy of all records."""
        with self._lock:
            return list(self._records)

    def reset(self) -> None:
        """Clear all records (used in tests)."""
        with self._lock:
            self._records.clear()

    # ==========================================================
    # Pricing
    # ==========================================================

    def _compute_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        pricing = self._pricing.get(model)
        if pricing is None:
            # Unknown model → cost = 0 (do not invent pricing)
            return 0.0
        input_cost = (prompt_tokens / 1_000_000) * pricing.input_per_million
        output_cost = (completion_tokens / 1_000_000) * pricing.output_per_million
        return round(input_cost + output_cost, 6)
