"""Serializers for resumes app."""

from rest_framework import serializers

from .models import Resume, ResumeVersion, Skill


class SkillSerializer(serializers.ModelSerializer):
    """Read-only skill serializer."""

    class Meta:
        model = Skill
        fields = ["id", "name", "slug", "category", "description"]
        read_only_fields = fields


class SkillCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating skills (admin use)."""

    class Meta:
        model = Skill
        fields = ["id", "name", "slug", "category", "aliases", "description"]

    def validate_slug(self, value: str) -> str:
        if Skill.objects.filter(slug=value).exists():
            raise serializers.ValidationError("A skill with this slug already exists.")
        return value


class ResumeVersionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing resume versions."""

    skills = SkillSerializer(source="extracted_skills", many=True, read_only=True)

    class Meta:
        model = ResumeVersion
        fields = [
            "id",
            "version_number",
            "source",
            "is_current",
            "file_size",
            "file_hash",
            "skills",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ResumeVersionDetailSerializer(serializers.ModelSerializer):
    """Full serializer for a single resume version."""

    skills = SkillSerializer(source="extracted_skills", many=True, read_only=True)

    class Meta:
        model = ResumeVersion
        fields = [
            "id",
            "version_number",
            "source",
            "is_current",
            "raw_text",
            "parsed_data",
            "analysis",
            "file",
            "file_size",
            "file_hash",
            "skills",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "version_number",
            "file_size",
            "file_hash",
            "analysis",
            "created_at",
            "updated_at",
        ]


class ResumeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing resumes."""

    versions_count = serializers.IntegerField(source="versions.count", read_only=True)

    class Meta:
        model = Resume
        fields = [
            "id",
            "title",
            "status",
            "is_primary",
            "language",
            "versions_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "versions_count", "created_at", "updated_at"]


class ResumeDetailSerializer(serializers.ModelSerializer):
    """Full serializer for a resume with versions."""

    versions = ResumeVersionListSerializer(many=True, read_only=True)
    current_version = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = [
            "id",
            "title",
            "status",
            "is_primary",
            "language",
            "versions",
            "current_version",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_current_version(self, obj: Resume):
        current = obj.versions.filter(is_current=True).first()
        if current is None:
            return None
        return ResumeVersionListSerializer(current).data


class ResumeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a resume (with optional first version)."""

    raw_text = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Resume
        fields = ["id", "title", "status", "is_primary", "language", "raw_text"]
        read_only_fields = ["id"]

    def create(self, validated_data: dict) -> Resume:
        raw_text = validated_data.pop("raw_text", "")
        user = self.context["request"].user

        # If this resume is marked primary, unset other primaries
        if validated_data.get("is_primary"):
            Resume.objects.filter(user=user, is_primary=True).update(is_primary=False)

        resume = Resume.objects.create(user=user, **validated_data)

        # Create first version if raw_text provided
        if raw_text:
            ResumeVersion.objects.create(
                user=user,
                resume=resume,
                version_number=1,
                source=ResumeVersion.Source.MANUAL,
                raw_text=raw_text,
                is_current=True,
            )

        return resume


class ResumeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a resume."""

    class Meta:
        model = Resume
        fields = ["title", "status", "is_primary", "language"]

    def update(self, instance: Resume, validated_data: dict) -> Resume:
        # If setting is_primary=True, unset others
        if validated_data.get("is_primary") is True:
            Resume.objects.filter(user=instance.user, is_primary=True).exclude(
                pk=instance.pk
            ).update(is_primary=False)
        return super().update(instance, validated_data)


class ResumeVersionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new version of an existing resume."""

    class Meta:
        model = ResumeVersion
        fields = [
            "id",
            "version_number",
            "source",
            "raw_text",
            "notes",
            "is_current",
            "created_at",
        ]
        read_only_fields = ["id", "version_number", "is_current", "created_at"]

    def create(self, validated_data: dict) -> ResumeVersion:
        resume = self.context["resume"]
        user = self.context["request"].user

        # Compute next version number
        last = resume.versions.order_by("-version_number").first()
        next_number = (last.version_number + 1) if last else 1

        # Unset current on previous versions
        resume.versions.filter(is_current=True).update(is_current=False)

        return ResumeVersion.objects.create(
            user=user,
            resume=resume,
            version_number=next_number,
            is_current=True,
            **validated_data,
        )
