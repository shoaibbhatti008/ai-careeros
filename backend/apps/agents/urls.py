"""URL routing for agents app."""

from django.urls import path

from .views import (
    AgentTaskDetailView,
    AgentTaskListCreateView,
    ApprovalDecisionView,
    ApprovalRequestDetailView,
    ApprovalRequestListView,
    ToolExecutionListView,
)

app_name = "agents"

urlpatterns = [
    path("tasks/", AgentTaskListCreateView.as_view(), name="tasks-list-create"),
    path("tasks/<uuid:pk>/", AgentTaskDetailView.as_view(), name="task-detail"),
    path(
        "tasks/<uuid:task_id>/tools/",
        ToolExecutionListView.as_view(),
        name="task-tools",
    ),
    path("approvals/", ApprovalRequestListView.as_view(), name="approvals-list"),
    path(
        "approvals/<uuid:pk>/",
        ApprovalRequestDetailView.as_view(),
        name="approval-detail",
    ),
    path(
        "approvals/<uuid:pk>/decide/",
        ApprovalDecisionView.as_view(),
        name="approval-decide",
    ),
]
