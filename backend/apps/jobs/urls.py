"""URL routing for jobs app."""

from django.urls import path

from .views import JobDetailView, JobListCreateView, JobSourceListView

app_name = "jobs"

urlpatterns = [
    path("", JobListCreateView.as_view(), name="list-create"),
    path("sources/", JobSourceListView.as_view(), name="sources-list"),
    path("<uuid:pk>/", JobDetailView.as_view(), name="detail"),
]
