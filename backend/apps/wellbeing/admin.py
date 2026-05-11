from django.contrib import admin
from .models import WellbeingConsent, WellbeingCheckIn, WellbeingAuditLog

@admin.register(WellbeingConsent)
class WellbeingConsentAdmin(admin.ModelAdmin):
    list_display = ("student", "is_enabled", "consented_at", "updated_at")
    list_filter = ("is_enabled",)
    search_fields = ("student__student_number", "student__user__full_name")

@admin.register(WellbeingCheckIn)
class WellbeingCheckInAdmin(admin.ModelAdmin):
    list_display = ("student", "mood_rating", "triage_class", "created_at", "is_deleted_by_student")
    list_filter = ("triage_class", "is_deleted_by_student")
    search_fields = ("student__student_number", "student__user__full_name")

@admin.register(WellbeingAuditLog)
class WellbeingAuditLogAdmin(admin.ModelAdmin):
    list_display = ("student", "triage_class", "notification_sent", "created_at")
    list_filter = ("triage_class", "notification_sent")
    search_fields = ("student__student_number", "student__user__full_name")
