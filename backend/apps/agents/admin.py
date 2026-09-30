from django.contrib import admin

from .models import AgentExecution, AgentTask, ApprovalRequest, ToolExecution


class AgentExecutionInline(admin.TabularInline):
    model = AgentExecution
    extra = 0
    readonly_fields = ("status", "step_count", "tool_call_count", "total_tokens", "started_at")


class ApprovalRequestInline(admin.TabularInline):
    model = ApprovalRequest
    extra = 0
    readonly_fields = ("action_type", "status", "created_at")


@admin.register(AgentTask)
class AgentTaskAdmin(admin.ModelAdmin):
    list_display = ("agent_name", "task_type", "status", "user", "priority", "created_at")
    list_filter = ("status", "agent_name", "priority")
    search_fields = ("agent_name", "task_type", "user__email")
    readonly_fields = ("started_at", "completed_at")
    inlines = [AgentExecutionInline, ApprovalRequestInline]


@admin.register(AgentExecution)
class AgentExecutionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task",
        "status",
        "step_count",
        "tool_call_count",
        "total_tokens",
        "duration_ms",
    )
    list_filter = ("status",)
    search_fields = ("task__task_type", "trace_id")
    readonly_fields = ("started_at", "completed_at")


@admin.register(ToolExecution)
class ToolExecutionAdmin(admin.ModelAdmin):
    list_display = ("tool_name", "agent_name", "status", "risk_level", "duration_ms", "started_at")
    list_filter = ("status", "risk_level", "agent_name")
    search_fields = ("tool_name", "agent_name")
    readonly_fields = ("started_at", "completed_at")


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "action_type", "status", "user", "created_at", "decided_at")
    list_filter = ("status", "action_type")
    search_fields = ("title", "user__email", "agent_name")
    readonly_fields = ("created_at", "updated_at", "decided_at")
