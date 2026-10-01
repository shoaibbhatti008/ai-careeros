"""Serializers for documents app."""

from rest_framework import serializers

from .models import Document, DocumentChunk


class DocumentChunkSerializer(serializers.ModelSerializer):
    """Serializer for document chunks."""

    class Meta:
        model = DocumentChunk
        fields = [
            "id",
            "chunk_index",
            "text",
            "token_count",
            "char_count",
            "embedding_model",
            "embedding_dim",
            "page_number",
            "section",
            "created_at",
        ]
        read_only_fields = fields


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing documents."""

    chunks_count = serializers.IntegerField(source="chunks.count", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "doc_type",
            "status",
            "file_size",
            "mime_type",
            "page_count",
            "word_count",
            "chunks_count",
            "processed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class DocumentDetailSerializer(serializers.ModelSerializer):
    """Full serializer for a single document."""

    chunks_count = serializers.IntegerField(source="chunks.count", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "doc_type",
            "status",
            "file",
            "file_size",
            "file_hash",
            "mime_type",
            "extracted_text",
            "page_count",
            "word_count",
            "metadata",
            "error_message",
            "chunks_count",
            "processed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "file_size",
            "file_hash",
            "mime_type",
            "extracted_text",
            "page_count",
            "word_count",
            "error_message",
            "chunks_count",
            "processed_at",
            "created_at",
            "updated_at",
        ]


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading a document."""

    class Meta:
        model = Document
        fields = ["id", "title", "doc_type", "file"]
        read_only_fields = ["id"]

    def validate_file(self, value):
        # Size limit: 10 MB
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size must be under {max_size // (1024 * 1024)} MB."
            )

        # Allowed extensions
        allowed = (".pdf", ".docx", ".txt", ".md")
        name = value.name.lower()
        if not name.endswith(allowed):
            raise serializers.ValidationError(
                f"Unsupported file type. Allowed: {', '.join(allowed)}"
            )

        return value

    def create(self, validated_data: dict) -> Document:
        user = self.context["request"].user
        file = validated_data.get("file")

        doc = Document.objects.create(
            user=user,
            file_size=file.size if file else 0,
            mime_type=getattr(file, "content_type", "") or "",
            **validated_data,
        )
        return doc
