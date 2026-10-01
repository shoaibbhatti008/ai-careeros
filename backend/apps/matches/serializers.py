"""Serializers for matches app."""

from apps.jobs.serializers import JobListSerializer
from apps.resumes.models import Resume, Skill
from apps.resumes.serializers import SkillSerializer
from rest_framework import serializers

from .models import JobMatch, SkillGap


class JobMatchListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing job matches."""

    job = JobListSerializer(read_only=True)

    class Meta:
        model = JobMatch
        fields = [
            "id",
            "job",
            "score",
            "is_saved",
            "is_dismissed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class JobMatchDetailSerializer(serializers.ModelSerializer):
    """Full serializer for a single job match."""

    job = JobListSerializer(read_only=True)
    match_reasons = serializers.JSONField()
    missing_skills = serializers.JSONField()
    extra_skills = serializers.JSONField()

    class Meta:
        model = JobMatch
        fields = [
            "id",
            "resume",
            "job",
            "score",
            "match_reasons",
            "missing_skills",
            "extra_skills",
            "is_saved",
            "is_dismissed",
            "user_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "resume",
            "job",
            "score",
            "match_reasons",
            "missing_skills",
            "extra_skills",
            "created_at",
            "updated_at",
        ]


class JobMatchUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a match (save/dismiss/notes)."""

    class Meta:
        model = JobMatch
        fields = ["is_saved", "is_dismissed", "user_notes"]


class SkillGapListSerializer(serializers.ModelSerializer):
    """Serializer for listing skill gaps."""

    skill = SkillSerializer(read_only=True)

    class Meta:
        model = SkillGap
        fields = [
            "id",
            "skill",
            "target_role",
            "priority",
            "importance",
            "is_resolved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class SkillGapDetailSerializer(serializers.ModelSerializer):
    """Full serializer for a skill gap."""

    skill = SkillSerializer(read_only=True)

    class Meta:
        model = SkillGap
        fields = [
            "id",
            "resume",
            "skill",
            "target_role",
            "priority",
            "importance",
            "learning_resources",
            "is_resolved",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "resume", "created_at", "updated_at"]


class SkillGapCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a skill gap."""

    skill_id = serializers.UUIDField(write_only=True)
    resume_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = SkillGap
        fields = [
            "id",
            "resume_id",
            "skill_id",
            "target_role",
            "priority",
            "importance",
            "learning_resources",
            "notes",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs: dict) -> dict:
        user = self.context["request"].user
        resume_id = attrs.pop("resume_id")
        skill_id = attrs.pop("skill_id")

        # Ownership: resume must belong to user
        try:
            resume = Resume.objects.get(pk=resume_id, user=user)
        except Resume.DoesNotExist as exc:
            raise serializers.ValidationError({"resume_id": "Resume not found."}) from exc

        # Skill must exist
        try:
            skill = Skill.objects.get(pk=skill_id)
        except Skill.DoesNotExist as exc:
            raise serializers.ValidationError({"skill_id": "Skill not found."}) from exc

        attrs["resume"] = resume
        attrs["skill"] = skill
        return attrs

    def create(self, validated_data: dict) -> SkillGap:
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class JobMatchComputeSerializer(serializers.Serializer):
    """Serializer for computing a job match (simple stub for now).

    Real scoring will be added in Phase 11 (Skill Gap Agent).
    """

    resume_id = serializers.UUIDField()
    job_id = serializers.UUIDField()
