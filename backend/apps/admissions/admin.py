from django.contrib import admin

from apps.admissions.models import ApplicantDocument, ApplicantProfile


class ApplicantDocumentInline(admin.TabularInline):
    model = ApplicantDocument
    extra = 0


@admin.register(ApplicantProfile)
class ApplicantProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "application_status", "programme_applied", "created_at"]
    list_filter = ["application_status"]
    search_fields = ["full_name", "email", "national_id"]
    inlines = [ApplicantDocumentInline]
