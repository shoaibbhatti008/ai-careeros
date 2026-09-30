"""
AgentTask, AgentExecution, ToolExecution, ApprovalRequest models.

These models form the backbone of the multi-agent system:
- AgentTask: high-level task assigned to an agent
- AgentExecution: one attempt/run of an agent on a task
- ToolExecution: one tool call made during an execution
- ApprovalRequest: human-in-the-loop approval for sensitive actions
"""

from apps.common.models import OwnedModel, TimeStampedModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class AgentTask(OwnedModel):
    """
    A high-level task assigned to an agent by the orchestrator.

    Example task types:
    - analyze_resume
    - find_jobs
    - compute_skill_gap
    - run_mock_interview
    - answer_from_documents
    """

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        RUNNING = "running", _("Running")
        COMPLETED = "completed", _("Completed")
        FAILED = "failed", _("Failed")
        AWAITING_APPROVAL = "awaiting_approval", _("Awaiting approval")
        CANCELLED = "cancelled", _("Cancelled")

    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        NORMAL = "normal", _("Normal")
        HIGH = "high", _("High")
        URGENT = "urgent", _("Urgent")

    # Identity
    agent_name = models.CharField(max_length=100, db_index=True)
    task_type = models.CharField(max_length=100, db_index=True)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True,
    )

    # Optional linkage to a conversation
    conversation = models.ForeignKey(
        "conversations.Conversation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agent_tasks",
    )

    # Inputs / outputs (JSON)
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    # Safety budgets
    max_steps = models.PositiveIntegerField(default=12)
    max_tool_calls = models.PositiveIntegerField(default=20)
    timeout_seconds = models.PositiveIntegerField(default=120)

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta(OwnedModel.Meta):
        verbose_name = _("agent task")
        verbose_name_plural = _("agent tasks")
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["agent_name", "status"]),
            models.Index(fields=["task_type"]),
        ]

    def __str__(self) -> str:
        return f"[{self.agent_name}] {self.task_type} ({self.status})"


class AgentExecution(TimeStampedModel):
    """
    One execution attempt of an agent on a task.

    An AgentTask may have multiple executions (retries, re-runs).
    """

    class Status(models.TextChoices):
        STARTED = "started", _("Started")
        COMPLETED = "completed", _("Completed")
        FAILED = "failed", _("Failed")
        TIMEOUT = "timeout", _("Timeout")
        CANCELLED = "cancelled", _("Cancelled")
        MAX_STEPS_REACHED = "max_steps_reached", _("Max steps reached")

    task = models.ForeignKey(
        AgentTask,
        on_delete=models.CASCADE,
        related_name="executions",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.STARTED,
        db_index=True,
    )

    # Step tracking
    step_count = models.PositiveIntegerField(default=0)
    tool_call_count = models.PositiveIntegerField(default=0)

    # Model info
    model_name = models.CharField(max_length=100, blank=True)
    provider = models.CharField(max_length=50, blank=True)

    # Token usage
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(default=0)

    # Result
    output_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    trace_id = models.CharField(max_length=100, blank=True, db_index=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = _("agent execution")
        verbose_name_plural = _("agent executions")
        indexes = [
            models.Index(fields=["task", "-started_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"Execution #{self.id} of {self.task.task_type} — {self.status}"


class ToolExecution(TimeStampedModel):
    """
    One tool call made during an agent execution.

    Every tool call is logged here for auditability and safety analysis.
    """

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        SUCCESS = "success", _("Success")
        FAILED = "failed", _("Failed")
        BLOCKED = "blocked", _("Blocked by permission")
        TIMEOUT = "timeout", _("Timeout")
        RATE_LIMITED = "rate_limited", _("Rate limited")

    class RiskLevel(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")
        CRITICAL = "critical", _("Critical")

    execution = models.ForeignKey(
        AgentExecution,
        on_delete=models.CASCADE,
        related_name="tool_executions",
    )
    tool_name = models.CharField(max_length=100, db_index=True)
    agent_name = models.CharField(max_length=100, db_index=True)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
        db_index=True,
    )

    # Inputs / outputs (redacted where necessary)
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(default=0)

    class Meta(TimeStampedModel.Meta):
        verbose_name = _("tool execution")
        verbose_name_plural = _("tool executions")
        indexes = [
            models.Index(fields=["execution", "started_at"]),
            models.Index(fields=["tool_name", "status"]),
            models.Index(fields=["risk_level"]),
        ]

    def __str__(self) -> str:
        return f"{self.tool_name} ({self.status}) by {self.agent_name}"


class ApprovalRequest(OwnedModel):
    """
    Human-in-the-loop approval for sensitive actions.

    Agents MUST create an ApprovalRequest for any action that is:
    - Irreversible
    - External-facing (sending emails, submitting applications)
    - High-risk (per security policy)

    The action is only executed after the user approves.
    """

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")
        EXPIRED = "expired", _("Expired")
        CANCELLED = "cancelled", _("Cancelled")

    class ActionType(models.TextChoices):
        SEND_EMAIL = "send_email", _("Send email")
        SUBMIT_APPLICATION = "submit_application", _("Submit job application")
        EXPORT_DATA = "export_data", _("Export user data")
        DELETE_DATA = "delete_data", _("Delete data")
        EXTERNAL_API_CALL = "external_api_call", _("External API call")
        OTHER = "other", _("Other")

    # Linkage
    task = models.ForeignKey(
        AgentTask,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="approval_requests",
    )
    agent_name = models.CharField(max_length=100, blank=True, db_index=True)

    # What is being requested
    action_type = models.CharField(
        max_length=50,
        choices=ActionType.choices,
        default=ActionType.OTHER,
        db_index=True,
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    proposed_payload = models.JSONField(default=dict, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # Decision
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_note = models.TextField(blank=True)

    # Expiry (auto-reject after this time)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Audit
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)

    class Meta(OwnedModel.Meta):
        verbose_name = _("approval request")
        verbose_name_plural = _("approval requests")
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"[{self.status}] {self.action_type} — {self.title}"
