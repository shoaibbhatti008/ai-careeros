from django.contrib import admin

from .models import JobMatch, SkillGap


@admin.register(JobMatch)
class JobMatchAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "score", "is_saved", "created_at")
    list_filter = ("is_saved", "is_dismissed")
    search_fields = ("user__email", "job__title", "job__company")


@admin.register(SkillGap)
class SkillGapAdmin(admin.ModelAdmin):
    list_display = ("user", "skill", "priority", "is_resolved", "created_at")
    list_filter = ("priority", "is_resolved")
    search_fields = ("user__email", "skill__name", "target_role")
