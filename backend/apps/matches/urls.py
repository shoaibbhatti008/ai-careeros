"""URL routing for matches app."""

from django.urls import path

from .views import (
    JobMatchComputeView,
    JobMatchDetailView,
    JobMatchListCreateView,
    SkillGapDetailView,
    SkillGapListCreateView,
)

app_name = "matches"

urlpatterns = [
    path("", JobMatchListCreateView.as_view(), name="list"),
    path("compute/", JobMatchComputeView.as_view(), name="compute"),
    path("<uuid:pk>/", JobMatchDetailView.as_view(), name="detail"),
    path("skill-gaps/", SkillGapListCreateView.as_view(), name="skill-gaps-list-create"),
    path(
        "skill-gaps/<uuid:pk>/",
        SkillGapDetailView.as_view(),
        name="skill-gap-detail",
    ),
]
