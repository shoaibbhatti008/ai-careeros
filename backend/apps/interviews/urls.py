"""URL routing for interviews app."""

from django.urls import path

from .views import (
    InterviewAnswerCreateView,
    InterviewAnswerDetailView,
    InterviewQuestionListCreateView,
    InterviewSessionDetailView,
    InterviewSessionListCreateView,
)

app_name = "interviews"

urlpatterns = [
    path("", InterviewSessionListCreateView.as_view(), name="list-create"),
    path("<uuid:pk>/", InterviewSessionDetailView.as_view(), name="detail"),
    path(
        "<uuid:session_id>/questions/",
        InterviewQuestionListCreateView.as_view(),
        name="questions-list-create",
    ),
    path(
        "questions/<uuid:question_id>/answer/",
        InterviewAnswerCreateView.as_view(),
        name="answer-create",
    ),
    path(
        "questions/<uuid:question_id>/answer/detail/",
        InterviewAnswerDetailView.as_view(),
        name="answer-detail",
    ),
]
