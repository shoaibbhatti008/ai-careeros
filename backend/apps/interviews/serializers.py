"""Serializers for interviews app."""

from rest_framework import serializers

from .models import InterviewAnswer, InterviewQuestion, InterviewSession


class InterviewQuestionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for interview questions."""

    has_answer = serializers.SerializerMethodField()

    class Meta:
        model = InterviewQuestion
        fields = [
            "id",
            "order",
            "text",
            "question_type",
            "expected_topics",
            "ai_hint",
            "has_answer",
            "created_at",
        ]
        read_only_fields = fields

    def get_has_answer(self, obj: InterviewQuestion) -> bool:
        return hasattr(obj, "answer")


class InterviewAnswerSerializer(serializers.ModelSerializer):
    """Serializer for interview answers."""

    class Meta:
        model = InterviewAnswer
        fields = [
            "id",
            "question",
            "text",
            "audio_file",
            "duration_seconds",
            "ai_score",
            "ai_feedback",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "ai_score", "ai_feedback", "created_at", "updated_at"]


class InterviewSessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing interview sessions."""

    questions_count = serializers.IntegerField(source="questions.count", read_only=True)

    class Meta:
        model = InterviewSession
        fields = [
            "id",
            "title",
            "interview_type",
            "status",
            "overall_score",
            "questions_count",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class InterviewSessionDetailSerializer(serializers.ModelSerializer):
    """Full serializer for an interview session with questions."""

    questions = InterviewQuestionListSerializer(many=True, read_only=True)

    class Meta:
        model = InterviewSession
        fields = [
            "id",
            "title",
            "job",
            "resume",
            "interview_type",
            "status",
            "overall_score",
            "feedback",
            "questions",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "overall_score",
            "feedback",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]


class InterviewSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an interview session."""

    class Meta:
        model = InterviewSession
        fields = ["id", "title", "job", "resume", "interview_type"]
        read_only_fields = ["id"]

    def create(self, validated_data: dict) -> InterviewSession:
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class InterviewSessionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating an interview session."""

    class Meta:
        model = InterviewSession
        fields = ["title", "status", "overall_score", "feedback", "started_at", "completed_at"]


class InterviewQuestionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an interview question."""

    class Meta:
        model = InterviewQuestion
        fields = ["id", "order", "text", "question_type", "expected_topics", "ai_hint"]
        read_only_fields = ["id"]

    def create(self, validated_data: dict) -> InterviewQuestion:
        session = self.context["session"]
        user = self.context["request"].user
        return InterviewQuestion.objects.create(user=user, session=session, **validated_data)


class InterviewAnswerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an interview answer."""

    class Meta:
        model = InterviewAnswer
        fields = ["id", "text", "audio_file", "duration_seconds"]
        read_only_fields = ["id"]

    def create(self, validated_data: dict) -> InterviewAnswer:
        question = self.context["question"]
        user = self.context["request"].user

        # OneToOne: use update_or_create
        answer, _ = InterviewAnswer.objects.update_or_create(
            question=question,
            defaults={
                "user": user,
                **validated_data,
            },
        )
        return answer
