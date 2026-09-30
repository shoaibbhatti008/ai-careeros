from django.contrib import admin

from .models import Document, DocumentChunk


class DocumentChunkInline(admin.TabularInline):
    model = DocumentChunk
    extra = 0
    readonly_fields = ("chunk_index", "token_count", "char_count", "embedding_dim")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "doc_type", "status", "file_size", "created_at")
    list_filter = ("doc_type", "status")
    search_fields = ("title", "user__email")
    inlines = [DocumentChunkInline]


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("document", "chunk_index", "token_count", "char_count")
    search_fields = ("document__title", "text")
