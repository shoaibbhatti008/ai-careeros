"""Views for resumes app."""

from apps.users.permissions import IsOwner
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Resume, ResumeVersion, Skill
from .serializers import (
    ResumeCreateSerializer,
    ResumeDetailSerializer,
    ResumeListSerializer,
    ResumeUpdateSerializer,
    ResumeVersionCreateSerializer,
    ResumeVersionDetailSerializer,
    ResumeVersionListSerializer,
    SkillSerializer,
)


class SkillListView(generics.ListAPIView):
    """GET /api/resumes/skills/ — list all skills in the catalog."""

    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get("category")
        search = self.request.query_params.get("search")
        if category:
            qs = qs.filter(category=category)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs


class ResumeListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/resumes/        — list current user's resumes
    POST /api/resumes/        — create a new resume
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ownership filter — non-negotiable
        return Resume.objects.filter(user=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ResumeCreateSerializer
        return ResumeListSerializer


class ResumeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/resumes/<id>/  — retrieve resume with versions
    PATCH  /api/resumes/<id>/  — update resume metadata
    DELETE /api/resumes/<id>/  — delete resume (cascades to versions)
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return ResumeUpdateSerializer
        return ResumeDetailSerializer


class ResumeVersionListView(generics.ListCreateAPIView):
    """
    GET  /api/resumes/<resume_id>/versions/  — list versions
    POST /api/resumes/<resume_id>/versions/  — create a new version
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get_resume(self) -> Resume:
        return get_object_or_404(
            Resume,
            pk=self.kwargs["resume_id"],
            user=self.request.user,
        )

    def get_queryset(self):
        resume = self.get_resume()
        return resume.versions.order_by("-version_number")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ResumeVersionCreateSerializer
        return ResumeVersionListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["resume"] = self.get_resume()
        return ctx


class ResumeVersionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/resumes/<resume_id>/versions/<id>/  — retrieve version
    PATCH  /api/resumes/<resume_id>/versions/<id>/  — update version
    DELETE /api/resumes/<resume_id>/versions/<id>/  — delete version
    """

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = ResumeVersionDetailSerializer

    def get_queryset(self):
        return ResumeVersion.objects.filter(
            resume_id=self.kwargs["resume_id"],
            user=self.request.user,
        )
