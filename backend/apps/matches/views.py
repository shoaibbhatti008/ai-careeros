"""Views for matches app."""

from apps.jobs.models import Job
from apps.resumes.models import Resume
from apps.users.permissions import IsOwner
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import JobMatch, SkillGap
from .serializers import (
    JobMatchComputeSerializer,
    JobMatchDetailSerializer,
    JobMatchListSerializer,
    JobMatchUpdateSerializer,
    SkillGapCreateSerializer,
    SkillGapDetailSerializer,
    SkillGapListSerializer,
)


class JobMatchListCreateView(generics.ListAPIView):
    """
    GET /api/matches/  — list current user's job matches

    Query params:
    - saved: true | false
    - dismissed: true | false
    - min_score: float
    """

    serializer_class = JobMatchListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = JobMatch.objects.filter(user=self.request.user).select_related("job")
        params = self.request.query_params

        if (saved := params.get("saved")) is not None:
            qs = qs.filter(is_saved=saved.lower() == "true")

        if (dismissed := params.get("dismissed")) is not None:
            qs = qs.filter(is_dismissed=dismissed.lower() == "true")
        else:
            # By default, hide dismissed matches
            qs = qs.filter(is_dismissed=False)

        if min_score := params.get("min_score"):
            try:
                qs = qs.filter(score__gte=float(min_score))
            except ValueError:
                pass

        return qs.order_by("-score", "-created_at")


class JobMatchDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/matches/<id>/  — retrieve a match
    PATCH  /api/matches/<id>/  — update (save/dismiss/notes)
    DELETE /api/matches/<id>/  — delete a match
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return JobMatch.objects.filter(user=self.request.user).select_related("job")

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return JobMatchUpdateSerializer
        return JobMatchDetailSerializer


class JobMatchComputeView(APIView):
    """
    POST /api/matches/compute/

    Compute a simple job match between a resume and a job.

    NOTE: This is a placeholder scoring algorithm. Real skill-based
    scoring will be implemented in Phase 11 (Skill Gap Agent).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = JobMatchComputeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Ownership: resume must belong to user
        resume = get_object_or_404(
            Resume,
            pk=serializer.validated_data["resume_id"],
            user=request.user,
        )
        job = get_object_or_404(Job, pk=serializer.validated_data["job_id"])

        # Simple placeholder score: based on title/company/location overlap
        # (Real implementation will use skill matching + embeddings.)
        score = 0.5
        reasons = ["Placeholder score — real scoring in Phase 11."]

        match, created = JobMatch.objects.update_or_create(
            user=request.user,
            resume=resume,
            job=job,
            defaults={
                "score": score,
                "match_reasons": reasons,
            },
        )

        return Response(
            JobMatchDetailSerializer(match).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class SkillGapListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/matches/skill-gaps/  — list current user's skill gaps
    POST /api/matches/skill-gaps/  — create a skill gap
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = SkillGap.objects.filter(user=self.request.user).select_related("skill")
        params = self.request.query_params

        if (resolved := params.get("resolved")) is not None:
            qs = qs.filter(is_resolved=resolved.lower() == "true")

        if priority := params.get("priority"):
            qs = qs.filter(priority=priority)

        if target_role := params.get("target_role"):
            qs = qs.filter(target_role__icontains=target_role)

        return qs.order_by("-importance", "-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SkillGapCreateSerializer
        return SkillGapListSerializer


class SkillGapDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/matches/skill-gaps/<id>/  — retrieve a skill gap
    PATCH  /api/matches/skill-gaps/<id>/  — update (resolve, priority)
    DELETE /api/matches/skill-gaps/<id>/  — delete a skill gap
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return SkillGap.objects.filter(user=self.request.user).select_related("skill")

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return SkillGapDetailSerializer
        return SkillGapDetailSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs["partial"] = True
        return super().get_serializer(*args, **kwargs)
