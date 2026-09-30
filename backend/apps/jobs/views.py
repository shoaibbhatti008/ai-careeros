"""Views for jobs app."""

from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Job, JobSource
from .serializers import (
    JobCreateSerializer,
    JobDetailSerializer,
    JobListSerializer,
    JobSourceSerializer,
)


class JobSourceListView(generics.ListAPIView):
    """GET /api/jobs/sources/ — list approved job sources."""

    queryset = JobSource.objects.filter(is_active=True)
    serializer_class = JobSourceSerializer
    permission_classes = [IsAuthenticated]


class JobListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/jobs/  — list jobs with filters
    POST /api/jobs/  — create a job (manual entry)

    Query params:
    - search: search in title/company/location
    - company: filter by company
    - location: filter by location
    - remote_policy: onsite | hybrid | remote
    - employment_type: full_time | part_time | contract | internship | freelance
    - status: open | closed | unknown
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Job.objects.select_related("source").prefetch_related("skills")
        params = self.request.query_params

        search = params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(company__icontains=search)
                | Q(location__icontains=search)
            )

        if company := params.get("company"):
            qs = qs.filter(company__icontains=company)

        if location := params.get("location"):
            qs = qs.filter(location__icontains=location)

        if remote_policy := params.get("remote_policy"):
            qs = qs.filter(remote_policy=remote_policy)

        if employment_type := params.get("employment_type"):
            qs = qs.filter(employment_type=employment_type)

        if status := params.get("status"):
            qs = qs.filter(status=status)

        return qs.order_by("-posted_at", "-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return JobCreateSerializer
        return JobListSerializer


class JobDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/jobs/<id>/  — retrieve a job
    PATCH /api/jobs/<id>/  — update a job (admin only in future)
    """

    queryset = Job.objects.select_related("source").prefetch_related("skills")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return JobCreateSerializer
        return JobDetailSerializer
