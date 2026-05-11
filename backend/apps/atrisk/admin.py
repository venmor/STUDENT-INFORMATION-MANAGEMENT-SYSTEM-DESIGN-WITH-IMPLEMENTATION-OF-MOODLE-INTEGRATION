from django.contrib import admin

from .models import AtRiskAlert


@admin.register(AtRiskAlert)
class AtRiskAlertAdmin(admin.ModelAdmin):
    list_display = ["student", "severity", "is_acknowledged", "is_closed", "created_at"]
    list_filter = ["severity", "is_acknowledged", "is_closed"]
    search_fields = ["student__student_number"]
    readonly_fields = ["id", "created_at", "updated_at"]
