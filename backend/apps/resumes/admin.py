from django.contrib import admin

from .models import Resume, ResumeVersion, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "slug")
    list_filter = ("category",)
    search_fields = ("name", "aliases")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "status", "is_primary", "created_at")
    list_filter = ("status", "is_primary")
    search_fields = ("title", "user__email")


@admin.register(ResumeVersion)
class ResumeVersionAdmin(admin.ModelAdmin):
    list_display = ("resume", "version_number", "source", "is_current", "created_at")
    list_filter = ("source", "is_current")
    search_fields = ("resume__title", "resume__user__email")
