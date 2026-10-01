"""Serializers for agents app."""

from rest_framework import serializers

from .models import AgentExecution, AgentTask, ApprovalRequest, ToolExecution


class AgentExecutionSerializer(serializers.ModelSerializer):
    """Serializer for agent executions."""

    class Meta:
        model = AgentExecution
        fields = [
            "id",
            "status",
            "step_count",
            "tool_call_count",
            "model_name",
            "provider",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "started_at",
            "completed_at",
            "duration_ms",
            "output_data",
            "error_message",
            "trace_id",
        ]
        read_only_fields = fields


class ToolExecutionSerializer(serializers.ModelSerializer):
    """Serializer for tool executions."""

    class Meta:
        model = ToolExecution
        fields = [
            "id",
            "tool_name",
            "agent_name",
            "status",
            "risk_level",
            "input_data",
            "output_data",
            "error_message",
            "started_at",
            "completed_at",
            "duration_ms",
        ]
        read_only_fields = fields


class AgentTaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing agent tasks."""

    class Meta:
        model = AgentTask
        fields = [
            "id",
            "agent_name",
            "task_type",
            "status",
            "priority",
            "created_at",
            "started_at",
            "completed_at",
        ]
        read_only_fields = fields


class AgentTaskDetailSerializer(serializers.ModelSerializer):
    """Full serializer for an agent task."""

    executions = AgentExecutionSerializer(many=True, read_only=True)
    approval_requests = serializers.SerializerMethodField()

    class Meta:
        model = AgentTask
        fields = [
            "id",
            "agent_name",
            "task_type",
            "status",
            "priority",
            "conversation",
            "input_data",
            "output_data",
            "error_message",
            "max_steps",
            "max_tool_calls",
            "timeout_seconds",
            "started_at",
            "completed_at",
            "executions",
            "approval_requests",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "output_data",
            "error_message",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]

    def get_approval_requests(self, obj: AgentTask):
        reqs = obj.approval_requests.all()
        return ApprovalRequestSerializer(reqs, many=True).data


class ApprovalRequestSerializer(serializers.ModelSerializer):
    """Serializer for approval requests."""

    class Meta:
        model = ApprovalRequest
        fields = [
            "id",
            "task",
            "agent_name",
            "action_type",
            "title",
            "description",
            "proposed_payload",
            "status",
            "decided_at",
            "decision_note",
            "expires_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "task",
            "agent_name",
            "action_type",
            "title",
            "description",
            "proposed_payload",
            "decided_at",
            "created_at",
            "updated_at",
        ]


class ApprovalDecisionSerializer(serializers.Serializer):
    """Serializer for approving or rejecting a request."""

    decision = serializers.ChoiceField(choices=["approved", "rejected"])
    note = serializers.CharField(required=False, allow_blank=True)


class AgentTaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an agent task."""

    class Meta:
        model = AgentTask
        fields = [
            "id",
            "agent_name",
            "task_type",
            "priority",
            "conversation",
            "input_data",
            "max_steps",
            "max_tool_calls",
            "timeout_seconds",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data: dict) -> AgentTask:
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
