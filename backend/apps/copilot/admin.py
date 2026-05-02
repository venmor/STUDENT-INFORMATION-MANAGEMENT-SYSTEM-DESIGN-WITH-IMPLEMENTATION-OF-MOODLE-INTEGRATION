from django.contrib import admin

from .models import AIAuditLog, CopilotFeedback, CopilotMessage, CopilotSession


@admin.register(CopilotSession)
class CopilotSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "student", "title", "status", "last_message_at", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "user__username", "student__student_number")
    readonly_fields = ("id", "created_at", "updated_at", "last_message_at")


@admin.register(CopilotMessage)
class CopilotMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "role", "confidence", "provider", "retrieved_chunk_count", "created_at")
    list_filter = ("role", "confidence", "provider", "created_at")
    search_fields = ("content", "session__title", "session__user__username")
    readonly_fields = ("id", "created_at")


@admin.register(AIAuditLog)
class AIAuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "action", "user", "student", "confidence", "provider", "source_count", "created_at")
    list_filter = ("action", "confidence", "provider", "created_at")
    search_fields = ("input_text", "output_text", "user__username", "student__student_number")
    readonly_fields = ("id", "created_at")


@admin.register(CopilotFeedback)
class CopilotFeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("comment", "user__username", "message__content")
    readonly_fields = ("id", "created_at", "updated_at")
