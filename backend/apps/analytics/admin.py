from django.contrib import admin

from .models import AnalyticsETLRun, StudentAnalyticsSnapshot


@admin.register(AnalyticsETLRun)
class AnalyticsETLRunAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "dry_run", "students_processed", "failure_count", "started_at", "completed_at")
    list_filter = ("status", "dry_run")
    search_fields = ("id", "last_error")


@admin.register(StudentAnalyticsSnapshot)
class StudentAnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ("student", "academic_year", "semester", "programme", "active_enrollment_count", "updated_at")
    list_filter = ("academic_year", "semester", "programme", "academic_standing")
    search_fields = ("student__student_number", "student__user__full_name", "student__user__username", "programme")
