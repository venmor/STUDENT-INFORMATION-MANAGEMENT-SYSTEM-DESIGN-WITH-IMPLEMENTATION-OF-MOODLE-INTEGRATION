from django.contrib import admin

from .models import AdvisorAssignment, AdvisingNote, FinancialFlag, StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "student_number",
        "user",
        "programme",
        "year_of_study",
        "academic_standing",
        "is_active",
    )
    list_filter = ("academic_standing", "programme", "is_active")
    search_fields = ("student_number", "national_id", "user__username", "user__full_name")


@admin.register(AdvisorAssignment)
class AdvisorAssignmentAdmin(admin.ModelAdmin):
    list_display = ("student", "advisor_user", "effective_from", "effective_to", "is_current")
    list_filter = ("is_current", "effective_from")
    search_fields = ("student__student_number", "advisor_user__username", "advisor_user__full_name")


@admin.register(FinancialFlag)
class FinancialFlagAdmin(admin.ModelAdmin):
    list_display = ("student", "flag_type", "effective_date", "cleared_date", "created_by_user")
    list_filter = ("flag_type", "effective_date", "cleared_date")
    search_fields = ("student__student_number", "reason")


@admin.register(AdvisingNote)
class AdvisingNoteAdmin(admin.ModelAdmin):
    list_display = ("student", "status", "created_by_user", "approved_by_user", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("student__student_number", "note_text")
