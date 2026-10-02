"""URL routing for resumes app."""

from django.urls import path

from .analyze_views import ResumeAnalyzeView
from .views import (
    ResumeDetailView,
    ResumeListCreateView,
    ResumeVersionDetailView,
    ResumeVersionListView,
    SkillListView,
)

app_name = "resumes"

urlpatterns = [
    path("", ResumeListCreateView.as_view(), name="list-create"),
    path("skills/", SkillListView.as_view(), name="skills-list"),
    path("<uuid:pk>/", ResumeDetailView.as_view(), name="detail"),
    path(
        "<uuid:pk>/analyze/",
        ResumeAnalyzeView.as_view(),
        name="analyze",
    ),
    path(
        "<uuid:resume_id>/versions/",
        ResumeVersionListView.as_view(),
        name="versions-list-create",
    ),
    path(
        "<uuid:resume_id>/versions/<uuid:pk>/",
        ResumeVersionDetailView.as_view(),
        name="version-detail",
    ),
]
