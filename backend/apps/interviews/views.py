"""Views for interviews app."""

from apps.users.permissions import IsOwner
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import InterviewAnswer, InterviewQuestion, InterviewSession
from .serializers import (
    InterviewAnswerCreateSerializer,
    InterviewAnswerSerializer,
    InterviewQuestionCreateSerializer,
    InterviewQuestionListSerializer,
    InterviewSessionCreateSerializer,
    InterviewSessionDetailSerializer,
    InterviewSessionListSerializer,
    InterviewSessionUpdateSerializer,
)


class InterviewSessionListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/interviews/  — list current user's interview sessions
    POST /api/interviews/  — create a new session
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = InterviewSession.objects.filter(user=self.request.user)
        params = self.request.query_params

        if status := params.get("status"):
            qs = qs.filter(status=status)

        if interview_type := params.get("interview_type"):
            qs = qs.filter(interview_type=interview_type)

        return qs.order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return InterviewSessionCreateSerializer
        return InterviewSessionListSerializer


class InterviewSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/interviews/<id>/  — retrieve session with questions
    PATCH  /api/interviews/<id>/  — update session
    DELETE /api/interviews/<id>/  — delete session
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return InterviewSession.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return InterviewSessionUpdateSerializer
        return InterviewSessionDetailSerializer


class InterviewQuestionListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/interviews/<session_id>/questions/  — list questions
    POST /api/interviews/<session_id>/questions/  — add a question
    """

    permission_classes = [IsAuthenticated]

    def get_session(self) -> InterviewSession:
        return get_object_or_404(
            InterviewSession,
            pk=self.kwargs["session_id"],
            user=self.request.user,
        )

    def get_queryset(self):
        return self.get_session().questions.order_by("order")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return InterviewQuestionCreateSerializer
        return InterviewQuestionListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["session"] = self.get_session()
        return ctx


class InterviewAnswerCreateView(generics.CreateAPIView):
    """
    POST /api/interviews/questions/<question_id>/answer/  — submit answer
    """

    permission_classes = [IsAuthenticated]
    serializer_class = InterviewAnswerCreateSerializer

    def get_question(self) -> InterviewQuestion:
        return get_object_or_404(
            InterviewQuestion,
            pk=self.kwargs["question_id"],
            user=self.request.user,
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["question"] = self.get_question()
        return ctx


class InterviewAnswerDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/interviews/questions/<question_id>/answer/  — retrieve answer
    PATCH /api/interviews/questions/<question_id>/answer/  — update answer
    """

    permission_classes = [IsAuthenticated]
    serializer_class = InterviewAnswerSerializer

    def get_queryset(self):
        return InterviewAnswer.objects.filter(
            question_id=self.kwargs["question_id"],
            user=self.request.user,
        )
