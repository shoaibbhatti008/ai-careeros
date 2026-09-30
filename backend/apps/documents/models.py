"""Document and DocumentChunk models for RAG."""

from apps.common.models import OwnedModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class Document(OwnedModel):
    """
    A user-owned document for RAG.

    Supported types: PDF, DOCX, TXT, MD.
    """

    class DocType(models.TextChoices):
        RESUME = "resume", _("Resume")
        JOB_DESCRIPTION = "job_description", _("Job description")
        COVER_LETTER = "cover_letter", _("Cover letter")
        ARTICLE = "article", _("Article")
        NOTES = "notes", _("Notes")
        OTHER = "other", _("Other")

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")
        READY = "ready", _("Ready")
        FAILED = "failed", _("Failed")

    title = models.CharField(max_length=300, db_index=True)
    doc_type = models.CharField(
        max_length=30, choices=DocType.choices, default=DocType.OTHER, db_index=True
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )

    file = models.FileField(upload_to="documents/%Y/%m/")
    file_size = models.PositiveIntegerField(default=0)
    file_hash = models.CharField(max_length=64, blank=True, db_index=True)
    mime_type = models.CharField(max_length=100, blank=True)

    extracted_text = models.TextField(blank=True)
    page_count = models.PositiveIntegerField(null=True, blank=True)
    word_count = models.PositiveIntegerField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta(OwnedModel.Meta):
        verbose_name = _("document")
        verbose_name_plural = _("documents")
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "doc_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.status})"


class DocumentChunk(OwnedModel):
    """
    A chunk of a document with its embedding for RAG.

    Ownership is enforced at the query layer:
        DocumentChunk.objects.filter(user=request.user)
    """

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    chunk_index = models.PositiveIntegerField()
    text = models.TextField()
    token_count = models.PositiveIntegerField(default=0)
    char_count = models.PositiveIntegerField(default=0)

    # Vector embedding stored as JSON for portability.
    # In production this can be moved to pgvector.
    embedding = models.JSONField(default=list, blank=True)
    embedding_model = models.CharField(max_length=100, blank=True)
    embedding_dim = models.PositiveIntegerField(null=True, blank=True)

    # Source metadata for citations
    page_number = models.PositiveIntegerField(null=True, blank=True)
    section = models.CharField(max_length=200, blank=True)

    class Meta(OwnedModel.Meta):
        verbose_name = _("document chunk")
        verbose_name_plural = _("document chunks")
        ordering = ["document", "chunk_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["document", "chunk_index"],
                name="unique_document_chunk_index",
            ),
        ]
        indexes = [
            models.Index(fields=["document", "chunk_index"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self) -> str:
        return f"Chunk {self.chunk_index} of {self.document.title}"
