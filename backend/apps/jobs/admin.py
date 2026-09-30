from django.contrib import admin

from .models import Job, JobSource


@admin.register(JobSource)
class JobSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "source_type", "is_active", "is_approved")
    list_filter = ("source_type", "is_active", "is_approved")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "status", "posted_at")
    list_filter = ("status", "employment_type", "remote_policy")
    search_fields = ("title", "company", "location")
    filter_horizontal = ("skills",)
