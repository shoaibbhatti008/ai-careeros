from django.contrib import admin

from .models import InterviewAnswer, InterviewQuestion, InterviewSession


class InterviewQuestionInline(admin.TabularInline):
    model = InterviewQuestion
    extra = 0


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "interview_type", "status", "overall_score", "created_at")
    list_filter = ("interview_type", "status")
    search_fields = ("title", "user__email")
    inlines = [InterviewQuestionInline]


@admin.register(InterviewAnswer)
class InterviewAnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "user", "ai_score", "created_at")
    search_fields = ("question__text", "user__email")
