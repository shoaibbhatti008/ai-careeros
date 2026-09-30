"""Serializers for jobs app."""

from apps.resumes.serializers import SkillSerializer
from rest_framework import serializers

from .models import Job, JobSource


class JobSourceSerializer(serializers.ModelSerializer):
    """Read-only serializer for JobSource."""

    class Meta:
        model = JobSource
        fields = ["id", "name", "slug", "source_type", "base_url", "is_active", "is_approved"]
        read_only_fields = fields


class JobListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing jobs."""

    source = JobSourceSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company",
            "location",
            "employment_type",
            "remote_policy",
            "seniority",
            "salary_min",
            "salary_max",
            "currency",
            "status",
            "source",
            "skills",
            "posted_at",
            "created_at",
        ]
        read_only_fields = fields


class JobDetailSerializer(serializers.ModelSerializer):
    """Full serializer for a single job."""

    source = JobSourceSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "external_id",
            "title",
            "company",
            "location",
            "description",
            "requirements",
            "responsibilities",
            "employment_type",
            "remote_policy",
            "seniority",
            "salary_min",
            "salary_max",
            "currency",
            "status",
            "source",
            "source_url",
            "skills",
            "tags",
            "posted_at",
            "expires_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class JobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating jobs (admin / manual entry)."""

    skill_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company",
            "location",
            "description",
            "requirements",
            "responsibilities",
            "employment_type",
            "remote_policy",
            "seniority",
            "salary_min",
            "salary_max",
            "currency",
            "status",
            "source_url",
            "skill_ids",
            "tags",
            "posted_at",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data: dict) -> Job:
        skill_ids = validated_data.pop("skill_ids", [])
        job = Job.objects.create(**validated_data)
        if skill_ids:
            job.skills.set(skill_ids)
        return job
