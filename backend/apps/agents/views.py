"""Views for agents app."""

from apps.users.permissions import IsOwner
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AgentTask, ApprovalRequest, ToolExecution
from .serializers import (
    AgentTaskCreateSerializer,
    AgentTaskDetailSerializer,
    AgentTaskListSerializer,
    ApprovalDecisionSerializer,
    ApprovalRequestSerializer,
    ToolExecutionSerializer,
)


class AgentTaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/agents/tasks/  — list current user's agent tasks
    POST /api/agents/tasks/  — create a new agent task
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = AgentTask.objects.filter(user=self.request.user)
        params = self.request.query_params

        if status_param := params.get("status"):
            qs = qs.filter(status=status_param)

        if agent_name := params.get("agent_name"):
            qs = qs.filter(agent_name=agent_name)

        return qs.order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AgentTaskCreateSerializer
        return AgentTaskListSerializer


class AgentTaskDetailView(generics.RetrieveAPIView):
    """
    GET /api/agents/tasks/<id>/  — retrieve agent task with executions
    """

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = AgentTaskDetailSerializer

    def get_queryset(self):
        return AgentTask.objects.filter(user=self.request.user)


class ToolExecutionListView(generics.ListAPIView):
    """
    GET /api/agents/tasks/<task_id>/tools/  — list tool executions for a task
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ToolExecutionSerializer

    def get_queryset(self):
        return ToolExecution.objects.filter(
            execution__task_id=self.kwargs["task_id"],
            execution__task__user=self.request.user,
        ).order_by("-started_at")


class ApprovalRequestListView(generics.ListAPIView):
    """
    GET /api/agents/approvals/  — list current user's approval requests

    Query params:
    - status: pending | approved | rejected | expired | cancelled
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalRequestSerializer

    def get_queryset(self):
        qs = ApprovalRequest.objects.filter(user=self.request.user)
        params = self.request.query_params

        if status_param := params.get("status"):
            qs = qs.filter(status=status_param)

        return qs.order_by("-created_at")


class ApprovalRequestDetailView(generics.RetrieveAPIView):
    """
    GET /api/agents/approvals/<id>/  — retrieve an approval request
    """

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = ApprovalRequestSerializer

    def get_queryset(self):
        return ApprovalRequest.objects.filter(user=self.request.user)


class ApprovalDecisionView(APIView):
    """
    POST /api/agents/approvals/<id>/decide/

    Approve or reject a pending approval request.

    Body:
        { "decision": "approved" | "rejected", "note": "optional" }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            approval = ApprovalRequest.objects.get(pk=pk, user=request.user)
        except ApprovalRequest.DoesNotExist:
            return Response(
                {"detail": "Approval request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if approval.status != ApprovalRequest.Status.PENDING:
            return Response(
                {"detail": f"Request already {approval.status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ApprovalDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        decision = serializer.validated_data["decision"]
        note = serializer.validated_data.get("note", "")

        approval.status = (
            ApprovalRequest.Status.APPROVED
            if decision == "approved"
            else ApprovalRequest.Status.REJECTED
        )
        approval.decided_at = timezone.now()
        approval.decision_note = note
        approval.save(update_fields=["status", "decided_at", "decision_note"])

        return Response(ApprovalRequestSerializer(approval).data)
