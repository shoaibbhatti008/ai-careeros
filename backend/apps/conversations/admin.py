from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("role", "content", "tokens_used", "created_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "message_count", "is_archived", "created_at")
    list_filter = ("is_archived", "is_pinned")
    search_fields = ("title", "user__email")
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "role", "tokens_used", "created_at")
    list_filter = ("role",)
    search_fields = ("content",)
